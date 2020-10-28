import urllib.request
import urllib.error
import http.client
import imghdr
import tts

# fix jpeg detection
def test_jpg(h,f):
  """binary jpg"""
  if h[:3]==b'\xff\xd8\xff':
    return 'jpg'

imghdr.tests.append(test_jpg)

class Url:
  def __init__(self,url,filesystem):
    self.url = url
    self.stripped_url=tts.strip_filename(url)
    self.filesystem = filesystem
    self._isImage=None
    self._looked_for_location=False
    self._location=None

  def examine_filesystem(self):
    if not self._looked_for_location:
      self._location,self._isImage=self.filesystem.find_details(self.url)
      self._looked_for_location=True

  def download(self):
    log=tts.logger()
    if self.exists:
      return True
    url=self.url
    protocols=url.split('://')
    if len(protocols)==1:
      log.warn("Missing protocol for {}. Assuming http://.".format(url))
      url = "http://" + url
    log.info("Downloading data for %s." % url)
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = { 'User-Agent' : user_agent }
    request=urllib.request.Request(url,headers=headers)
    try:
      response=urllib.request.urlopen(request)
    except urllib.error.URLError as e:
      log.error("Error downloading %s (%s)" % (url,e))
      return False
    try:
      data=response.read()
    except http.client.IncompleteRead as e:
      #This error is the http server did not return the whole file
      log.error("Error downloading %s (%s)" % (url,e))
      return False
    imagetype=imghdr.what('',data)
    filename=None
    if imagetype==None:
      filename=self.filesystem.get_model_path(self.stripped_url+'.obj')
      log.debug("File is OBJ")
    else:
      if imagetype=='jpeg':
        imagetype='jpg'
      log.debug("File is %s" % imagetype)
      filename=self.filesystem.get_image_path(self.stripped_url+'.'+imagetype)
    try:
      fh=open(filename,'wb')
      fh.write(data)
      fh.close()
    except IOError as e:
      log.error("Error writing file %s (%s)" % (filename,e))
      return False
    self._looked_for_location=False
    return True

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
    if self.exists:
      return "%s: %s (%s)" % ( \
             "Image" if self.isImage else "Model", \
             self.url, \
             self.location)
    else:
      return "%s (Not Found)" % self.url

  def __str__(self):
    if self.exists:
      return "%s: %s" % ( \
             "Image" if self.isImage else "Model", \
             self.url)
    else:
      return "%s (Not Found)" % self.url


