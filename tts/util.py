import string
import imghdr


# fix jpeg detection
def test_jpg(h, f):
    """binary jpg"""
    if h[:3] == b'\xff\xd8\xff':
        return 'jpg'


imghdr.tests.append(test_jpg)

def strip_filename(filename):
  # Convert a filename to TTS format.
  valid_chars = "%s%s" % (string.ascii_letters, string.digits)
  return ''.join(c for c in filename if c in valid_chars)


def identify_image_extension(data) -> str:
    image_type = imghdr.what("", data)
    if image_type == 'jpeg':
        image_type = 'jpg'
    if image_type:
        return "." + image_type
    return None