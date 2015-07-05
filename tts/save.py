from .tts import *
from .url import Url

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
        urls.add((key,data[key]))
        continue
      protocols=data[key].split('://')
      if len(protocols)==1:
        # not an url
        continue
      if protocols[0] in ['http','https','ftp']:
        # belt + braces.
        urls.add((key,data[key]))
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
  def __init__(self,savedata,ident=None,isWorkshop=True):
    self.data = savedata
    self.ident=ident
    self.isWorkshop=isWorkshop
    self.urls = [ Url(a,b) for (a,b) in get_save_urls(savedata) ]
    self.models=[ x for x in self.urls if not x.isImage ]
    self.images=[ x for x in self.urls if x.isImage ]


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