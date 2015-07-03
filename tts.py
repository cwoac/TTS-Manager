#!/usr/bin/env python27

import os
import os.path
import json
import string

class TTS_URL:
  def __init__(self,parameter,url):
    self.url = url
    self.parameter = parameter
    # TODO: Are there others model types?
    self.isImage = parameter not in ['MeshURL' , 'ColliderURL']

  def get_location(self):
    if self.isImage:
      for image_format in ['.png','.jpg','.bmp']:
        # TODO: Is this all the supported formats?
        filename=os.path.join(get_image_dir(),strip_filename(self.url)+image_format)
        if os.path.isfile(filename):
          return filename
      print("Unable to find image from url %s",self.url)
      return None
    # got here, must be a model
    for model_format in ['.obj']:
      filename=os.path.join(get_model_dir(),strip_filename(self.url)+model_format)
      if os.path.isfile(filename):
        return filename
    print("Unable to find image from url %s",self.url)
    return None

def get_tts_dir():
  # TODO: handle non-user save option
  return os.path.join(os.path.expanduser("~"),"Documents","My Games","Tabletop Simulator")

def get_chest_dir():
  return os.path.join(get_tts_dir(),"Saves","Chest")

def get_image_dir():
  return os.path.join(get_tts_dir(),"Mods","Images")

def get_model_dir():
  return os.path.join(get_tts_dir(),"Mods","Models")

def get_workshop_dir():
  return os.path.join(get_tts_dir(),"Mods","Workshop")

def get_workshop_filenames():
  files=[os.path.splitext(file)[0] for file in os.listdir(get_workshop_dir()) if os.path.splitext(file)[1].lower()=='.json']
  files.remove('WorkshopFileInfos')
  return files

def strip_filename(filename):
  # Convert a filename to TTS format.
  valid_chars = "%s%s" % (string.ascii_letters, string.digits)
  return ''.join(c for c in filename if c in valid_chars)

def load_workshop_file(id):
  filename=os.path.join(get_workshop_dir(),id+'.json')
  data=open(filename,'r').read()
  j_data=json.loads(data)
  return j_data

def describe_workshop_files():
  output=[]
  for id in get_workshop_filenames():
    json=load_workshop_file(id)
    name=json['SaveName']
    output.append((name,id))
  return output
def get_save_urls(savedata):
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
      if key.endswith('URL') and data[key]!='':
        urls.add(TTS_URL(key,data[key]))
    for item in data.values():
      urls |= get_save_urls(item)
    return urls

  if type(savedata) is list:
    return parse_list(savedata)
  if type(savedata) is dict:
    return parse_dict(savedata)
  return set()
