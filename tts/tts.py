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

def validate_metadata(metadata):
  # TODO: extract into new class
  if not metadata or type(metadata) is not dict:
    return False
  return 'Ver' in metadata and 'Id' in metadata and 'Type' in metadata

def load_json_file(filename):
  if not filename or not os.path.isfile(filename):
    print("Unable to find mod file %s" % filename)
    return None
  data=open(filename,'r').read()
  j_data=json.loads(data)
  return j_data

def load_workshop_file(ident,filesystem):
  filename=filesystem.get_workshop_filename(ident)
  return load_json_file(filename)


def load_save_file(ident,filesystem):
  filename=filesystem.get_save_filename(ident)
  return load_json_file(filename)

def describe_workshop_files(filesystem):
  output=[]
  for id in filesystem.get_workshop_filenames():
    json=load_workshop_file(id,filesystem)
    name=json['SaveName']
    output.append((name,id))
  return output

def describe_save_files(filesystem):
  output=[]
  for savefile in filesystem.get_save_filenames():
    json=load_save_file(savefile,filesystem)
    name=json['SaveName']
    output.append((name,savefile))
  return output
