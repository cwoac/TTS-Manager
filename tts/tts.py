import os.path
import string
import json
import tts.logger
import tts.save
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

def download_file(filesystem,ident,save_type):
  """Attempt to download all files for a given savefile"""
  log=tts.logger()
  log.info("Downloading %s file %s (from %s)" % (save_type.name,ident,filesystem))
  filename=filesystem.get_json_filename_for_type(ident,save_type)
  if not filename:
    log.error("Unable to find data file.")
    return False
  try:
    data=load_json_file(filename)
  except IOError as e:
    log.error("Unable to read data file %s (%s)" % (filename,e))
    return False
  if not data:
    log.error("Unable to read data file %s" % filename)
    return False

  save=tts.Save(savedata=data,
            filename=filename,
            ident=ident,
            save_type=save_type,
            filesystem=filesystem)

  if save.isInstalled:
    log.info("All files already downloaded.")
    return True

  successful = save.download()
  if successful:
    log.info("All files downloaded.")
  else:
    log.info("Some files failed to download.")
  return successful
