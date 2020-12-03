import zipfile
from typing import Tuple, Set

import tts
from tts.filetype import FileType
from .tts import *
from .url import Url

PAK_VER = 3


def import_pak(filesystem, filename):
    log = tts.logger()
    log.debug("About to import {} into {}.".format(filename, filesystem))
    if not os.path.isfile(filename):
        log.error("Unable to find mod pak {}".format(filename))
        return False
    if not zipfile.is_zipfile(filename):
        log.error("Mod pak {} format appears corrupt.".format(filename))
        return False
    try:
        with zipfile.ZipFile(filename, 'r') as zf:
            bad_file = zf.testzip()
            if bad_file:
                log.error("At least one corrupt file found in {} - {}".format(filename, bad_file))
                return False
            if not zf.comment:
                # TODO: allow overrider
                log.error("Missing pak header comment in {}. Aborting import.".format(filename))
                return False
            metadata = json.loads(zf.comment.decode('utf-8'))
            if not tts.validate_metadata(metadata, PAK_VER):
                log.error(f"Invalid pak header '{metadata}' in {filename}. Aborting import.")
                return False
            log.info(f"Extracting {metadata['Type']} pak for id {metadata['Id']} (pak version {metadata['Ver']})")

            # select the thumbnail which matches the metadata id, else anything
            names = zf.namelist()
            thumbnails = [name for name in names if '/Thumbnails/' in name]
            thumbnail = None
            for thumbnail in thumbnails:
                if metadata['Id'] in os.path.basename(thumbnail):
                    break

            outname = None
            for name in names:
                # Note that zips always use '/' as the seperator it seems.
                splitname = name.split('/')
                if len(splitname) > 2 and splitname[2] == 'Thumbnails':
                    if name == thumbnail:
                        # remove "Thumbnails" from the path
                        outname = '/'.join(splitname[0:2] + [os.path.extsep.join([metadata['Id'], 'png'])])
                    else:
                        outname = None
                        continue

                start = splitname[0]
                if start == 'Saves':
                    modpath = filesystem.basepath
                else:
                    modpath = filesystem.modpath
                target_base_name = outname if outname else name
                target_file_name = os.path.join(modpath, target_base_name)
                if os.path.isfile(target_file_name):
                    log.warn(f"Not extracting existing file {target_file_name}")
                    continue
                log.debug(f"Extracting {name} to {modpath}")
                zf.extract(name, modpath)
                if outname:
                    log.debug(f"Renaming {name} to {outname}")
                    os.rename(os.path.join(modpath, name), os.path.join(modpath, outname))
                    try:
                        outdir = os.path.dirname(os.path.join(modpath, name))
                        os.rmdir(outdir)
                    except OSError:
                        log.debug(f"Can't remove dir {outdir}")

    except zipfile.BadZipFile as e:
        log.error("Mod pak {} format appears corrupt - {}.".format(filename, e))
    except zipfile.LargeZipFile as e:
        log.error("Mod pak {} requires large zip capability - {}.\nThis shouldn't happen - please raise a bug.".format(
            filename, e))
    log.info("Imported {} successfully.".format(filename))
    return True


def get_save_urls(save_data) -> Set[Tuple[str, FileType]]:
    """
    Iterate over all the values in the json file, building a (key,value) set of
    all the values whose key ends in "URL"
    """
    log = tts.logger()

    def parse_list(data):
        urls = set()
        for item in data:
            urls |= get_save_urls(item)
        return urls

    def parse_dict(data):
        urls = set()
        if not data:
            return urls
        for key in data:
            key_type = FileType.identify_type(key)

            if not key_type or key_type is FileType.NONE:
                # If it isn't a string, it can't be an url.
                # Also don't save tablet state / rulebooks
                continue
            if data[key] != '':
                log.debug(f"Found {key_type}: {key}:{data[key]}")
                urls.add((data[key], key_type))
                continue
        for item in data.values():
            urls |= get_save_urls(item)
        return urls

    if type(save_data) is list:
        return parse_list(save_data)
    if type(save_data) is dict:
        return parse_dict(save_data)
    return set()


class Save:
    def __init__(self, savedata, filename, ident, filesystem, save_type=SaveType.workshop):
        log = tts.logger()
        self.data = savedata
        self.ident = ident
        if self.data['SaveName']:
            self.save_name = self.data['SaveName']
        else:
            self.save_name = self.ident
        self.save_type = save_type
        self.filesystem = filesystem
        self.filename = filename
        thumbnail = os.path.extsep.join(filename.split(os.path.extsep)[0:-1] + [
            'png'])  # Known issue: this fails if filename doesn't contain an extsep
        if os.path.isfile(thumbnail):
            self.thumbnail = thumbnail
        else:
            self.thumbnail = None
        self.thumb = os.path.isfile(os.path.extsep.join([filename.split(os.path.extsep)[0], 'png']))
        # strip the local part off.
        fileparts = self.filename.split(os.path.sep)
        while fileparts[0] != 'Saves' and fileparts[0] != 'Mods':
            fileparts = fileparts[1:]
        self.basename = os.path.join(*fileparts)
        log.debug("filename: {},save_name: {}, basename: {}".format(self.filename, self.save_name, self.basename))
        self.urls = [Url(url, type, self.filesystem) for url, type in get_save_urls(savedata)]
        self.missing = [x for x in self.urls if not x.exists]
        self.present_files = {}
        for url in [u for u in self.urls if u.exists]:
            try:
                self.present_files[url.type].append(url)
            except KeyError:
                self.present_files[url.type] = [url]
        log.debug(f"Urls found {len(self.urls)} ({len(self.missing)} missing)")

    def export(self, export_filename):
        log = tts.logger()
        log.info("About to export %s to %s" % (self.ident, export_filename))
        zfs = tts.filesystem.FileSystem(base_path="")
        zip_comment = {
            "Ver": PAK_VER,
            "Id": self.ident,
            "Type": self.save_type.name
        }

        # TODO: error checking.
        with zipfile.ZipFile(export_filename, 'w') as zf:
            zf.comment = json.dumps(zip_comment).encode('utf-8')
            log.debug("Writing {} (base {}) to {}".format(self.filename, os.path.basename(self.filename),
                                                          zfs.get_path_by_save_type(os.path.basename(self.filename),
                                                                                    self.save_type)))
            zf.write(self.filename, zfs.get_path_by_save_type(os.path.basename(self.filename), self.save_type))
            if self.thumbnail:
                filepath = zfs.get_path_by_save_type(os.path.basename(self.thumbnail), self.save_type)
                arcname = os.path.join(os.path.dirname(filepath), 'Thumbnails', os.path.basename(filepath))
                zf.write(self.thumbnail, arcname=arcname)
                log.debug(f"Writing {self.thumbnail} to {arcname}")
            for file_type in self.present_files:
                log.info(f"Writing {file_type} files")
                for url in self.present_files[file_type]:
                    target_file = zfs.get_file_path(os.path.basename(url.location), url.type)
                    log.debug(f"Writing {url.location} to {target_file}")
                    zf.write(url.location, target_file)
        log.info("File exported.")

    def export_missing(self, export_filename):
        """ Create a partial pak containing only those files currently unavailiable
        """
        # TODO:: I don't like the amount of code duplication here.
        # Possible options:
        # 1. pass a filter function to an inner export function
        # 2. Create a filtered Save subclass and use the normal export function?
        log = tts.logger()
        log.info(f"About to partial export {self.ident} to {export_filename}")
        zfs = tts.filesystem.FileSystem(base_path="")
        zip_comment = {
            "Ver": PAK_VER,
            "Id": self.ident,
            "Type": self.save_type.name
        }

        # TODO: error checking.
        with zipfile.ZipFile(export_filename, 'w') as zf:
            # Always write base file and thumbnail. They should be pretty small anyway.
            zf.comment = json.dumps(zip_comment).encode('utf-8')
            log.debug(
                f"Writing {self.filename} (base {os.path.basename(self.filename)}) to {zfs.get_path_by_save_type(os.path.basename(self.filename), self.save_type)}")
            zf.write(self.filename, zfs.get_path_by_save_type(os.path.basename(self.filename), self.save_type))
            if self.thumbnail:
                filepath = zfs.get_path_by_save_type(os.path.basename(self.thumbnail), self.save_type)
                arcname = os.path.join(os.path.dirname(filepath), 'Thumbnails', os.path.basename(filepath))
                log.debug(f"Writing {self.thumbnail} to {arcname}")
                zf.write(self.thumbnail, arcname=arcname)
            for file_type in self.present_files:
                log.info(f"Writing {file_type} files")
                for url in self.present_files[file_type]:
                    target_file = zfs.get_file_path(os.path.basename(url.location), url.type)
                    log.debug(f"Writing {url.location} to {target_file}")
                    zf.write(url.location, target_file)
            log.info("File exported.")

    @property
    def is_installed(self):
        """Is every url referenced by this save installed?"""
        return len(self.missing) == 0

    def download(self):
        log = tts.logger()
        log.warn("About to download files for %s" % self.save_name)
        if self.is_installed:
            log.info("All files already downloaded.")
            return True

        successful = True
        url_counter = 1
        for url in self.missing:
            log.warn("Downloading file {} of {} for {}".format(url_counter, len(self.missing), self.save_name))
            result = url.download()
            if not result:
                successful = False
            url_counter += 1

        # TODO:: remove items from missing list.
        return successful

    def __str__(self):
        result = "Save: %s\n" % self.data['SaveName']
        if len(self.missing) > 0:
            result += "Missing:\n"
            for x in self.missing:
                result += str(x) + "\n"
        for file_type in self.present_files:
            result += f"{file_type}:\n"
            for url in self.present_files[file_type]:
                result += str(x) + "\n"
        return result


__all__ = ['Save']
