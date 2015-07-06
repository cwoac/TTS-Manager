import os.path
import string
import json
from .filesystem import FileSystem,standard_basepath

def get_default_fs():
  return FileSystem(standard_basepath())

def strip_filename(filename):
  # Convert a filename to TTS format.
  valid_chars = "%s%s" % (string.ascii_letters, string.digits)
  return ''.join(c for c in filename if c in valid_chars)


def load_json_file(filename):
  if not os.path.isfile(filename):
    print("Unable to find mod file %s" % filename)
    return None
  data=open(filename,'r').read()
  j_data=json.loads(data)
  return j_data

def load_file(ident,filesystem=get_default_fs(),prefer_workshop=True):
  return load_json_file(filesystem.get_json_filename(ident,prefer_workshop))

def describe_workshop_files(filesystem=get_default_fs()):
  output=[]
  for id in filesystem.get_workshop_filenames():
    json=load_workshop_file(id)
    name=json['SaveName']
    output.append((name,id))
  return output

def describe_save_files(filesystem=get_default_fs()):
  output=[]
  for savefile in filesystem.get_save_filenames():
    json=load_save_file(savefile)
    name=json['SaveName']
    output.append((name,savefile))
  return output
