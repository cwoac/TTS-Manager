import os.path
import string
import json

def get_tts_dir():
  # TODO: handle non-user save option
  return os.path.join(os.path.expanduser("~"),"Documents","My Games","Tabletop Simulator")

def get_saves_dir():
  return os.path.join(get_tts_dir(),"Saves")

def get_chest_dir():
  return os.path.join(get_tts_dir(),"Saves","Chest")

def get_image_dir():
  return os.path.join(get_tts_dir(),"Mods","Images")

def get_model_dir():
  return os.path.join(get_tts_dir(),"Mods","Models")

def get_workshop_dir():
  return os.path.join(get_tts_dir(),"Mods","Workshop")

def get_save_filenames():
  files=[os.path.splitext(file)[0] for file in os.listdir(get_saves_dir()) if os.path.splitext(file)[1].lower()=='.json']
  files.remove('SaveFileInfos')
  return files

def get_save_filename(savename):
  return os.path.join(get_saves_dir(),savename+'.json')


def get_workshop_filenames():
  files=[os.path.splitext(file)[0] for file in os.listdir(get_workshop_dir()) if os.path.splitext(file)[1].lower()=='.json']
  files.remove('WorkshopFileInfos')
  return files

def strip_filename(filename):
  # Convert a filename to TTS format.
  valid_chars = "%s%s" % (string.ascii_letters, string.digits)
  return ''.join(c for c in filename if c in valid_chars)

def get_workshop_filename(id):
  return os.path.join(get_workshop_dir(),id+'.json')

def load_json_file(filename):
  if not os.path.isfile(filename):
    print("Unable to find mod file #%s" %id)
    return None
  data=open(filename,'r').read()
  j_data=json.loads(data)
  return j_data

def load_workshop_file(id):
  filename=get_workshop_filename(id)
  return load_json_file(filename)

def load_save_file(savename):
  filename=get_save_filename(savename)
  return load_json_file(filename)

def describe_workshop_files():
  output=[]
  for id in get_workshop_filenames():
    json=load_workshop_file(id)
    name=json['SaveName']
    output.append((name,id))
  return output

def describe_save_files():
  output=[]
  for savefile in get_save_filenames():
    json=load_save_file(savefile)
    name=json['SaveName']
    output.append((name,savefile))
  return output