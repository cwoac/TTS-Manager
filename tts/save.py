from .tts import *
from .url import Url
import tts
import zipfile
import json

def importPak(filesystem,filename):
  if not os.path.isfile(filename):
    return 1, "Unable to find mod pak %s" % filename
  if not zipfile.is_zipfile(filename):
    return 1, "Mod pak %s format appears corrupt." % filename
  with zipfile.ZipFile(filename,'r') as zf:
    if not zf.comment:
      return 1, "Missing pak header comment in %s." % filename
    metadata=json.loads(zf.comment.decode('utf-8'))
    if not tts.validate_metadata(metadata):
      return 1, "Unable to read pak header comment in %s." % filename
    print("Extracting %s pak for id %s (pak version %s)" % (metadata['Type'],metadata['Id'],metadata['Ver']))
    # TODO: handle exceptions
    zf.extractall(filesystem.basepath)
  return 0,"Imported %s" % filename

def get_save_urls(savedata):
  '''
  Iterate over all the values in the json file, building a (key,value) set of
  all the values whose key ends in "URL"
  '''
  # TODO: handle duplicate list ids
  def parse_list(data):
    urls=set()
    for item in data:
      urls |= get_save_urls(item)
    return urls
  def parse_dict(data):
    urls=set()
    if not data:
      return urls
    for key in data:
      if type(data[key]) is not str or key=='PageURL':
        # If it isn't a string, it can't be an url.
        # Also don't save tablet state.
        continue
      if key.endswith('URL') and data[key]!='':
        urls.add(data[key])
        continue
      protocols=data[key].split('://')
      if len(protocols)==1:
        # not an url
        continue
      if protocols[0] in ['http','https','ftp']:
        # belt + braces.
        urls.add(data[key])
        continue
    for item in data.values():
      urls |= get_save_urls(item)
    return urls

  if type(savedata) is list:
    return parse_list(savedata)
  if type(savedata) is dict:
    return parse_dict(savedata)
  return set()


class Save:
  def __init__(self,savedata,filename,ident,save_type=SaveType.workshop,filesystem=get_default_fs()):
    self.data = savedata
    self.ident=ident
    self.save_type=save_type
    self.filesystem = filesystem
    self.filename=filename
    self.urls = [ Url(url,self.filesystem) for url in get_save_urls(savedata) ]
    self.models=[ x for x in self.urls if not x.isImage ]
    self.images=[ x for x in self.urls if x.isImage ]

  def export(self,export_filename):
    zfs = tts.filesystem.FileSystem("")
    zipComment = {
      "Ver":1,
      "Id":self.ident,
      "Type":self.save_type.name
    }

    # TODO: error checking.
    with zipfile.ZipFile(export_filename,'w') as zf:
      zf.comment=json.dumps(zipComment).encode('utf-8')
      zf.write(self.filename,zfs.get_path_by_type(os.path.basename(self.filename),self.save_type))
      for url in self.models:
        zf.write(url.location,zfs.get_model_path(os.path.basename(url.location)))
      for url in self.images:
        zf.write(url.location,zfs.get_image_path(os.path.basename(url.location)))


  @property
  def isInstalled(self):
    """Is every url referenced by this save installed?"""
    for url in self.urls:
      if not url.exists:
        return False
    return True

  def __str__(self):
    result = "Save: %s\n" % self.data['SaveName']
    result += "Images:\n"
    for x in self.images:
      result += str(x)+"\n"
    result += "Models:\n"
    for x in self.models:
      result += str(x)+"\n"
    return result
__all__ = [ 'Save' ]
