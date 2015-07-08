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

  def get_dir_by_type(self,save_type):
    st={
      tts.SaveType.workshop:self._workshop,
      tts.SaveType.save:self._saves,
      tts.SaveType.chest:self._chest
    }
    return st[save_type]

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

  def get_chest_path(self,filename):
    return os.path.join(self._chest,filename)

  def get_path_by_type(self,filename,save_type):
    return os.path.join(self.get_dir_by_type(save_type),filename)

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

  def get_filenames_in(self,search_path):
    return [os.path.splitext(file)[0] for file in os.listdir(search_path) if os.path.splitext(file)[1].lower()=='.json']

  def get_save_filenames(self):
    files=self.get_filenames_in(self._saves)
    files.remove('SaveFileInfos')
    return files

  def get_workshop_filenames(self):
    files=self.get_filenames_in(self._workshop)
    files.remove('WorkshopFileInfos')
    return files

  def get_chest_filenames(self):
    return self.get_filenames_in(self._chest)

  def get_filenames_by_type(self,save_type):
    if save_type==tts.SaveType.workshop:
      return self.get_workshop_filenames()
    if save_type==tts.SaveType.save:
      return self.get_save_filenames()
    if save_type==tts.SaveType.chest:
      return self.get_chest_filenames()
    # TODO: error handling here
    return None

  def get_json_filename_from(self,basename,paths):
    result=None
    for pth in paths:
      filename=os.path.join(pth,basename+'.json')
      if os.path.isfile(filename):
        result=filename
        break
    return result

  def get_json_filename(self,basename):
    return self.get_json_filename_from(basename,[self._workshop,self._saves,self._chest])

  def get_json_filename_for_type(self,basename,save_type):
    return self.get_json_filename_from(basename,[self.get_dir_by_type(save_type)])

  def get_json_filename_type(self,basename):
    if os.path.isfile(os.path.join(self._workshop,basename+'.json')):
      return SaveType.workshop
    if os.path.isfile(os.path.join(self._saves,basename+'.json')):
      return SaveType.save
    if os.path.isfile(os.path.join(self._chest,basename+'.json')):
      return SaveType.chest
    # TODO: error handling here
    return None
