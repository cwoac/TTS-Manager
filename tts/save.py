from .tts import *
from .url import Url
import tts
import zipfile
import json
import urllib.error

PAK_VER=2

def importPak(filesystem,filename):
  log=tts.logger()
  log.debug("About to import {} into {}.".format(filename,filesystem))
  if not os.path.isfile(filename):
    log.error("Unable to find mod pak {}".format(filename))
    return False
  if not zipfile.is_zipfile(filename):
    log.error("Mod pak {} format appears corrupt.".format(filename))
    return False
  try:
    with zipfile.ZipFile(filename,'r') as zf:
      bad_file=zf.testzip()
      if bad_file:
        log.error("At least one corrupt file found in {} - {}".format(filename,bad_file))
        return False
      if not zf.comment:
        # TODO: allow overrider
        log.error("Missing pak header comment in {}. Aborting import.".format(filename))
        return False
      metadata=json.loads(zf.comment.decode('utf-8'))
      if not tts.validate_metadata(metadata, PAK_VER):
        log.error(f"Invalid pak header '{metadata}' in {filename}. Aborting import.")
        return False
      log.info(f"Extracting {metadata['Type']} pak for id {metadata['Id']} (pak version {metadata['Ver']})")

      #select the thumbnail which matches the metadata id, else anything
      names = zf.namelist()
      thumbnails = [name for name in names if '/Thumbnails/' in name]
      thumbnail = None
      for thumbnail in thumbnails:
        if metadata['Id'] in os.path.basename(thumbnail):
          break

      outname=None
      for name in names:
        # Note that zips always use '/' as the seperator it seems.
        splitname = name.split('/')
        if len(splitname) > 2 and splitname[2] == 'Thumbnails':
          if name == thumbnail:
            #remove "Thumbnails" from the path
            outname='/'.join(splitname[0:2] + [os.path.extsep.join([metadata['Id'],'png'])])
          else:
            outname=None
            continue

        start=splitname[0]
        if start=='Saves':
          modpath=filesystem.basepath
        else:
          modpath=filesystem.modpath
        log.debug(f"Extracting {name} to {modpath}")
        zf.extract(name,modpath)
        if outname:
          log.debug(f"Renaming {name} to {outname}")
          os.rename(os.path.join(modpath,name), os.path.join(modpath,outname))
          try:
            outdir = os.path.dirname(os.path.join(modpath,name))
            os.rmdir(outdir)
          except OSError:
            log.debug(f"Can't remove dir {outdir}")

  except zipfile.BadZipFile as e:
    log.error("Mod pak {} format appears corrupt - {}.".format(filename,e))
  except zipfile.LargeZipFile as e:
    log.error("Mod pak {} requires large zip capability - {}.\nThis shouldn't happen - please raise a bug.".format(filename,e))
  log.info("Imported {} successfully.".format(filename))
  return True

def get_save_urls(savedata):
  '''
  Iterate over all the values in the json file, building a (key,value) set of
  all the values whose key ends in "URL"
  '''
  log=tts.logger()
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
      if type(data[key]) is not str or key=='PageURL' or key=='Rules':
        # If it isn't a string, it can't be an url.
        # Also don't save tablet state / rulebooks
        continue
      if key.endswith('URL') and data[key]!='':
        log.debug("Found {}:{}".format(key,data[key]))
        urls.add(data[key])
        continue
      protocols=data[key].split('://')
      if len(protocols)==1:
        # not an url
        continue
      if protocols[0] in ['http','https','ftp']:
        # belt + braces.
        urls.add(data[key])
        log.debug("Found {}:{}".format(key,data[key]))
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
  def __init__(self,savedata,filename,ident,filesystem,save_type=SaveType.workshop):
    log=tts.logger()
    self.data = savedata
    self.ident=ident
    if self.data['SaveName']:
      self.save_name=self.data['SaveName']
    else:
      self.save_name=self.ident
    self.save_type=save_type
    self.filesystem = filesystem
    self.filename=filename
    thumbnail = os.path.extsep.join(filename.split(os.path.extsep)[0:-1] + ['png']) #Known issue: this fails if filename doesn't contain an extsep
    if os.path.isfile(thumbnail):
        self.thumbnail = thumbnail
    else:
        self.thumbnail = None
    self.thumb=os.path.isfile(os.path.extsep.join([filename.split(os.path.extsep)[0],'png']))
    #strip the local part off.
    fileparts=self.filename.split(os.path.sep)
    while fileparts[0]!='Saves' and fileparts[0]!='Mods':
      fileparts=fileparts[1:]
    self.basename=os.path.join(*fileparts)
    log.debug("filename: {},save_name: {}, basename: {}".format(self.filename,self.save_name,self.basename))
    self.urls = [ Url(url,self.filesystem) for url in get_save_urls(savedata) ]
    self.missing = [ x for x in self.urls if not x.exists ]
    self.images=[ x for x in self.urls if x.exists and x.isImage ]
    self.models=[ x for x in self.urls if x.exists and not x.isImage ]
    log.debug("Urls found {}:{} missing, {} models, {} images".format(len(self.urls),len(self.missing),len(self.models),len(self.images)))

  def export(self,export_filename):
    log=tts.logger()
    log.info("About to export %s to %s" % (self.ident,export_filename))
    zfs = tts.filesystem.FileSystem(base_path="")
    zipComment = {
      "Ver":PAK_VER,
      "Id":self.ident,
      "Type":self.save_type.name
    }

    # TODO: error checking.
    with zipfile.ZipFile(export_filename,'w') as zf:
      zf.comment=json.dumps(zipComment).encode('utf-8')
      log.debug("Writing {} (base {}) to {}".format(self.filename,os.path.basename(self.filename),zfs.get_path_by_type(os.path.basename(self.filename),self.save_type)))
      zf.write(self.filename,zfs.get_path_by_type(os.path.basename(self.filename),self.save_type))
      if self.thumbnail:
          filepath=zfs.get_path_by_type(os.path.basename(self.thumbnail),self.save_type)
          arcname=os.path.join(os.path.dirname(filepath), 'Thumbnails', os.path.basename(filepath))
          zf.write(self.filename,arcname=arcname)
      for url in self.models:
        log.debug("Writing {} to {}".format(url.location,zfs.get_model_path(os.path.basename(url.location))))
        zf.write(url.location,zfs.get_model_path(os.path.basename(url.location)))
      for url in self.images:
        log.debug("Writing {} to {}".format(url.location,zfs.get_model_path(os.path.basename(url.location))))
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
