from .tts import *
from .url import Url
import tts
import zipfile
import json
import urllib.error

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
    # TODO: handle mixed location saves
    zf.extractall(filesystem.basepath)
  return 0,"Imported %s" % filename

def get_save_urls(savedata):
  '''
  Iterate over all the values in the json file, building a (key,value) set of
  all the values whose key ends in "URL"
  '''
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
    if self.data['SaveName']:
      self.save_name=self.data['SaveName']
    else:
      self.save_name=self.ident
    self.save_type=save_type
    self.filesystem = filesystem
    self.filename=filename
    self.urls = [ Url(url,self.filesystem) for url in get_save_urls(savedata) ]
    self.missing = [ x for x in self.urls if not x.exists ]
    self.models=[ x for x in self.urls if x.exists and x.isImage ]
    self.images=[ x for x in self.urls if x.exists and not x.isImage ]

  def export(self,export_filename):
    log=tts.logger()
    log.info("About to export %s to %s" % (self.ident,export_filename))
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
    log.info("File exported.")

  @property
  def isInstalled(self):
    """Is every url referenced by this save installed?"""
    return len(self.missing)==0

  def download(self):
    log=tts.logger()
    log.warn("About to download files for %s" % self.save_name)
    if self.isInstalled==True:
      log.info("All files already downloaded.")
      return True

    successful=True
    url_counter=1
    for url in self.missing:
      log.warn("Downloading file {} of {} for {}".format(url_counter,len(self.missing),self.save_name))
      result = url.download()
      if not result:
        successful=False
      url_counter+=1

    #TODO:: remove items from missing list.
    return successful


    log.info("All files downloaded.")
    return True

  def __str__(self):
    result = "Save: %s\n" % self.data['SaveName']
    if len(self.missing)>0:
      result += "Missing:\n"
      for x in self.missing:
        result += str(x)+"\n"
    if len(self.images)>0:
      result += "Images:\n"
      for x in self.images:
        result += str(x)+"\n"
    if len(self.models)>0:
      result += "Models:\n"
      for x in self.models:
        result += str(x)+"\n"
    return result
__all__ = [ 'Save' ]
