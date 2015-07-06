import os
import os.path
import tts

def standard_basepath():
  return os.path.join(os.path.expanduser("~"),"Documents","My Games","Tabletop Simulator")

class FileSystem:
  def __init__(self,basepath):
    self.basepath=basepath
    self._saves = os.path.join(basepath,"Saves")
    self._chest = os.path.join(self._saves,"Chest")
    self._mods  = os.path.join(basepath,"Mods")
    self._images= os.path.join(self._mods,"Images")
    self._models= os.path.join(self._mods,"Models")
    self._workshop = os.path.join(self._mods,"Workshop")

  @property
  def saves_dir(self):
    return self._saves

  @property
  def images_dir(self):
    return self._images

  def get_image_path(self,filename):
    return os.path.join(self._images,filename)

  def get_model_path(self,filename):
    return os.path.join(self._models,filename)

  def get_workshop_path(self,filename):
    return os.path.join(self._workshop,filename)

  def get_save_path(self,filename):
    return os.path.join(self._saves,filename)

  def find_details(self,basename):
    result=self.find_image(basename)
    if result:
      return result,True
    result=self.find_model(basename)
    if result:
      return result,False
    return None,None

  def find_image(self,basename):
    result=None
    stripname = tts.strip_filename(basename)
    for image_format in ['.png','.jpg','.bmp']:
      filename=os.path.join(self._images,stripname+image_format)
      if os.path.isfile(filename):
        result=filename
        break
    return result

  def find_model(self,basename):
    result=None
    stripname = tts.strip_filename(basename)
    for model_format in ['.obj']:
      filename=os.path.join(self._models,stripname+model_format)
      if os.path.isfile(filename):
        result=filename
        break
    return result

  def get_save_filenames(self):
    files=[os.path.splitext(file)[0] for file in os.listdir(self._saves) if os.path.splitext(file)[1].lower()=='.json']
    files.remove('SaveFileInfos')
    return files

  def get_workshop_filenames(self):
    files=[os.path.splitext(file)[0] for file in os.listdir(self._workshop) if os.path.splitext(file)[1].lower()=='.json']
    files.remove('WorkshopFileInfos')
    return files

  def get_json_filename_from(self,basename,paths):
    result=None
    for pth in paths:
      filename=os.path.join(pth,basename+'.json')
      if os.path.isfile(filename):
        result=filename
        break
    return result

  def get_json_filename(self,basename):
    return self.get_json_filename_from(basename,[self._workshop,self._saves])

  def get_workshop_filename(self,basename):
    return self.get_json_filename_from(basename,[self._workshop])

  def get_save_filename(self,basename):
    return self.get_json_filename_from(basename,[self._saves])
