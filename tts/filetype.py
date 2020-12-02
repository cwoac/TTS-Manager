from enum import Enum

from tts.util import identify_image_extension


class FileType(Enum):
    ASSETBUNDLE = "Assetbundles"
    AUDIO = "Audio"
    IMAGE = "Images"
    MODEL = "Models"
    PDF = "PDF"
    TEXT = "Text"
    WORKSHOP = "Workshop"
    NONE = "unk"

    @classmethod
    def identify_type(cls, url_key: str):
        result = None
        try:
            result = _urlkeys[url_key]
        except KeyError:
            pass
        return result

    def get_extension(self, data):
        if self is FileType.IMAGE:
            image_type = identify_image_extension(data)
            if image_type:
                return image_type
            return ""
        return _url_extensions[self]


_urlkeys = {
    "AssetbundleURL": FileType.ASSETBUNDLE,
    "AssetbundleSecondaryURL": FileType.ASSETBUNDLE,
    "BackURL": FileType.IMAGE,
    "ColliderURL": FileType.MODEL,
    "CurrentAudioURL": FileType.AUDIO,
    "DiffuseURL": FileType.IMAGE,
    "FaceURL": FileType.IMAGE,
    "ImageSecondaryURL": FileType.IMAGE,
    "ImageURL": FileType.IMAGE,
    "LutURL": FileType.NONE,  # TODO:: Figure out where lookup tables go
    "MeshURL": FileType.MODEL,
    "NormalURL": FileType.IMAGE,
    "PageURL": FileType.NONE,  # Not downloading this one
    "PDFUrl": FileType.PDF,
    "SkyURL": FileType.IMAGE,
    "TableURL": FileType.IMAGE,
    "URL": FileType.IMAGE
}

# Unfortunately Images can be png or jpg. I suspect Audio may be the same,
# but all the files I have are MP3
_url_extensions = {
    FileType.ASSETBUNDLE: ".unity3d",
    FileType.AUDIO: ".MP3",
    FileType.MODEL: ".obj",
    FileType.PDF: ".pdf",
    FileType.TEXT: ".txt",
    FileType.NONE: ""
}
