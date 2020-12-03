import os
import os.path
import platform
from typing import Tuple

import tts
import tts.util
from tts.filetype import FileType

if platform.system() == 'Linux':
    import xdgappdirs


def get_json_filename_from(basename, paths):
    result = None
    for pth in paths:
        filename = os.path.join(pth, basename + '.json')
        if os.path.isfile(filename):
            result = filename
            break
    # TODO: error handling here
    return result


def get_filenames_in(search_path):
    if not os.path.isdir(search_path):
        tts.logger().warn("Tried to search non-existent path {}.".format(search_path))
        return []
    return [os.path.splitext(file)[0] for file in os.listdir(search_path) if
            os.path.splitext(file)[1].lower() == '.json']


def standard_basepath():
    if platform.system() == 'Windows':
        basepath = os.path.join(os.path.expanduser("~"), "Documents", "My Games", "Tabletop Simulator")
    elif platform.system() == 'Linux':
        basepath = os.path.join(xdgappdirs.user_data_dir(), "Tabletop Simulator")
    else:
        basepath = os.path.join(os.path.expanduser("~"), "Library", "Tabletop Simulator")
    return basepath


class FileSystem:
    def __init__(self, base_path=None, tts_install_path=None):
        if base_path is not None:
            self.basepath = base_path
        else:
            self.basepath = standard_basepath()
        if tts_install_path is not None:
            self.modpath = os.path.join(tts_install_path, "Tabletop Simulator_Data")
        else:
            self.modpath = self.basepath
        self._saves = os.path.join(self.basepath, "Saves")
        self._chest = os.path.join(self._saves, "Chest")
        self._mods = os.path.join(self.modpath, "Mods")
        self._images = os.path.join(self._mods, "Images")
        self._models = os.path.join(self._mods, "Models")
        self._workshop = os.path.join(self._mods, "Workshop")

    def get_dir_by_type(self, save_type):
        st = {
            tts.SaveType.workshop: self._workshop,
            tts.SaveType.save: self._saves,
            tts.SaveType.chest: self._chest
        }
        return st[save_type]

    def check_dirs(self):
        """Do all the directories exist?"""
        for dir in [self._saves, self._mods, self._images, self._models, self._workshop]:
            if not os.path.isdir(dir):
                tts.logger().error("TTS Dir missing: {}".format(dir))
                return False
        # These directories don't always exist, and that's OK
        for dir in [self._chest]:
            if not os.path.isdir(dir):
                tts.logger().warn("TTS Dir missing: {}".format(dir))
        return True

    def create_dirs(self):
        """Attempt to create any missing directories."""
        for dir in [self._saves, self._chest, self._mods, self._images, self._models, self._workshop]:
            os.makedirs(dir, exist_ok=True)

    @property
    def saves_dir(self):
        return self._saves

    @property
    def images_dir(self):
        return self._images

    def get_dir(self, type: FileType) -> str:
        return os.path.join(self._mods, type.value)

    def get_file_path(self, file_name: str, file_type: FileType) -> str:
        return os.path.join(self.get_dir(file_type), file_name)

    def get_path_by_save_type(self, filename, save_type):
        return os.path.join(self.get_dir_by_type(save_type), filename)

    def check_for_file_location(self, basename: str, type: FileType) -> Tuple[str, str]:
        if type is FileType.IMAGE:
            return self.find_image(basename)
        if type is FileType.NONE:
            return None
        extension = type.get_extension(None)
        filename = os.path.join(self.get_dir(type),
                                f"{tts.util.strip_filename(basename)}{extension}")
        return (filename, extension) if os.path.isfile(filename) else None

    def find_image(self, basename: str) -> str:
        result = None
        stripname = tts.util.strip_filename(basename)
        for image_format in ['.png', '.jpg', '.bmp']:
            filename = os.path.join(self._images, stripname + image_format)
            if os.path.isfile(filename):
                result = filename, image_format
                break
        return result

    def get_save_filenames(self):
        files = get_filenames_in(self._saves)
        if files and 'SaveFileInfos' in files:
            files.remove('SaveFileInfos')
        return files

    def get_workshop_filenames(self):
        files = get_filenames_in(self._workshop)
        if files and 'WorkshopFileInfos' in files:
            files.remove('WorkshopFileInfos')
        return files

    def get_chest_filenames(self):
        return get_filenames_in(self._chest)

    def get_filenames_by_type(self, save_type):
        if save_type == tts.SaveType.workshop:
            return self.get_workshop_filenames()
        if save_type == tts.SaveType.save:
            return self.get_save_filenames()
        if save_type == tts.SaveType.chest:
            return self.get_chest_filenames()
        # TODO: error handling here
        return None

    def get_json_filename(self, basename):
        return get_json_filename_from(basename, [self._workshop, self._saves, self._chest])

    def get_json_filename_for_type(self, basename, save_type):
        return get_json_filename_from(basename, [self.get_dir_by_type(save_type)])

    def get_json_filename_type(self, basename):
        if os.path.isfile(os.path.join(self._workshop, basename + '.json')):
            return tts.SaveType.workshop
        if os.path.isfile(os.path.join(self._saves, basename + '.json')):
            return tts.SaveType.save
        if os.path.isfile(os.path.join(self._chest, basename + '.json')):
            return tts.SaveType.chest
        # TODO: error handling here
        return None

    def __str__(self):
        return "Saves: {} Mods: {}".format(self.basepath, self.modpath)
