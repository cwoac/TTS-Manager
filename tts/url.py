import os.path
from .tts import get_image_dir,strip_filename,get_model_dir

class Url:
  def __init__(self,parameter,url):
    self.url = url
    self.parameter = parameter
    # TODO: Are there others model types?
    self.isImage = parameter not in ['MeshURL' , 'ColliderURL']
    self._looked_for_location=False
    self._location=None

  @property
  def exists(self):
    """Does the url exist on disk already?"""
    return self.location != None

  @property
  def location(self):
    """Return the location of the file on disk for this url, if it exists."""
    if not self._looked_for_location:
      if self.isImage:
        for image_format in ['.png','.jpg','.bmp']:
          # TODO: Is this all the supported formats?
          filename=os.path.join(get_image_dir(),strip_filename(self.url)+image_format)
          if os.path.isfile(filename):
            self._location=filename
            break
      # got here, must be a model
      for model_format in ['.obj']:
        filename=os.path.join(get_model_dir(),strip_filename(self.url)+model_format)
        if os.path.isfile(filename):
            self._location=filename
            break
      self._looked_for_location=True

    return self._location

  def __repr__(self):
    return "%s: %s (%s)" % ( \
           "Image" if self.isImage else "Model", \
           self.url, \
           self.location if self.exists else "Not Found")

  def __str__(self):
    return "%s: %s (%s)" % ( \
           "Image" if self.isImage else "Model", \
           self.url, \
           "Found" if self.exists else "Not Found")

