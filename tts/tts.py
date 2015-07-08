import os.path
import string
import json
from enum import IntEnum
from .filesystem import FileSystem,standard_basepath

class SaveType(IntEnum):
  workshop = 1
  save = 2
  chest = 3

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

def load_file_by_type(ident,filesystem,save_type):
  filename=filesystem.get_json_filename_for_type(ident,save_type)
  return load_json_file(filename)

def describe_files_by_type(filesystem,save_type):
  output=[]
  for filename in filesystem.get_filenames_by_type(save_type):
    json=load_file_by_type(filename,filesystem,save_type)
    name=json['SaveName']
    output.append((name,filename))
  return output
