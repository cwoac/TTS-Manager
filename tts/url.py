import http.client
import os
import urllib.error
import urllib.request

import tts.util
from tts.filetype import FileType


class Url:
    def __init__(self, url: str, type: FileType, filesystem: "FileSystem"):
        self.url = url
        self.stripped_url = tts.util.strip_filename(url)
        self.filesystem = filesystem
        self._type = type
        self._looked_for_location = False
        self._location = None
        self._extension = None

    def examine_filesystem(self):
        if not self._looked_for_location:
            result = self.filesystem.check_for_file_location(self.url, self._type)
            if result:
                # It seems I can't return a tuple of (None, None), so...
                self._location, self._extension = result
            self._looked_for_location = True

    def is_unavailiable(self):
        """ Check whether this url can be reached.
        """
        log = tts.logger()
        url = self.url
        protocols = url.split('://')
        if len(protocols) == 1:
            log.warn(f"Missing protocol for {url}. Assuming http://.")
            url = "http://" + url
        log.info(f"Downloading data for {url}")
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = {'User-Agent': user_agent}
        request = urllib.request.Request(url, headers=headers)
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.URLError:
            return True
        # In theory it might still not be downloadable at this point as the server
        # might only have a partial copy. Going to assume that is unlikely enough we can ignore it.
        return response.status >= 400

    def download(self):
        log = tts.logger()
        if self.exists:
            return True
        if self._type is FileType.NONE:
            log.info("Skipping none type file")
            return True
        url = self.url
        protocols = url.split('://')
        if len(protocols) == 1:
            log.warn("Missing protocol for {}. Assuming http://.".format(url))
            url = "http://" + url
        log.info("Downloading data for %s." % url)
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = {'User-Agent': user_agent}
        request = urllib.request.Request(url, headers=headers)
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.URLError as e:
            log.error("Error downloading %s (%s)" % (url, e))
            return False
        try:
            data = response.read()
        except http.client.IncompleteRead as e:
            # This error is the http server did not return the whole file
            log.error("Error downloading %s (%s)" % (url, e))
            return False

        self._extension = self._type.get_extension(data)

        filename = os.path.join(
            self.filesystem.get_dir(self._type),
            f"{self.stripped_url}{self._extension}"
        )
        log.info(f"Writing file to {filename}")
        try:
            fh = open(filename, 'wb')
            fh.write(data)
            fh.close()
        except IOError as e:
            log.error("Error writing file %s (%s)" % (filename, e))
            return False
        self._looked_for_location = False
        return True

    @property
    def exists(self):
        """Does the url exist on disk already?"""
        return self.location is not None

    @property
    def type(self):
        return self._type

    @property
    def isImage(self):
        """Do we think this is an image?"""
        return self._type == FileType.IMAGE

    @property
    def location(self):
        """Return the location of the file on disk for this url, if it exists."""
        self.examine_filesystem()
        return self._location

    def __repr__(self):
        if self.exists:
            return "%s: %s (%s)" % (
                "Image" if self.isImage else "Model",
                self.url,
                self.location)
        else:
            return "%s (Not Found)" % self.url

    def __str__(self):
        if self.exists:
            return "%s: %s" % (
                "Image" if self.isImage else "Model",
                self.url)
        else:
            return "%s (Not Found)" % self.url
