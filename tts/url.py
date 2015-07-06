class Url:
  def __init__(self,parameter,url,path):
    self.url = url
    self.path = path
    self.parameter = parameter
    self._isImage=None
    self._looked_for_location=False
    self._location=None

  def examine_filesystem(self):
    if not self._looked_for_location:
      self._location,self._isImage=self.path.find_details(self.url)
      self._looked_for_location=True

  @property
  def exists(self):
    """Does the url exist on disk already?"""
    return self.location != None

  @property
  def isImage(self):
    """Do we think this is an image?"""
    self.examine_filesystem()
    return self._isImage

  @property
  def location(self):
    """Return the location of the file on disk for this url, if it exists."""
    self.examine_filesystem()
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

