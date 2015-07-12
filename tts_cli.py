#!/usr/bin/env python3
import tts
import argparse
import os.path
import sys
import codecs
import locale
import _io
import json
import zipfile
import logging

class TTS_CLI:
  def __init__(self):
    parser = argparse.ArgumentParser(description="Manipulate Tabletop Simulator files")
    parser.add_argument("-d","--directory",help="Override TTS cache directory")
    parser.add_argument("-l","--loglevel",help="Set logging level",choices=['debug','info','warn','error'])
    subparsers = parser.add_subparsers(dest='parser',title='command',description='Valid commands.')
    subparsers.required=True
    # add list command
    parser_list = subparsers.add_parser('list',help="List installed mods.",description='''
    List installed mods.
    If no id is provided, then this will return a list of all installed modules.
    If an id is provided, then this will list the contents of that modules.
    ''')
    group_list=parser_list.add_mutually_exclusive_group()
    group_list.add_argument("-w","--workshop",action="store_const",metavar='save_type',dest='save_type',const=tts.SaveType.workshop,help="List workshop files (the default).")
    group_list.add_argument("-s","--save",action="store_const",metavar='save_type',dest='save_type',const=tts.SaveType.save,help="List saves.")
    group_list.add_argument("-c","--chest",action="store_const",metavar='save_type',dest='save_type',const=tts.SaveType.chest,help="List chest files.")

    parser_list.add_argument("id",nargs='?',help="ID of specific mod to list details of.")
    parser_list.set_defaults(func=self.do_list)

    # export command
    parser_export = subparsers.add_parser('export',help="Export a mod.",description='Export a mod in a format suitible for later import.')
    group_export=parser_export.add_mutually_exclusive_group()
    group_export.add_argument("-w","--workshop",action="store_const",dest='save_type',metavar='save_type',const=tts.SaveType.workshop,help="ID is of workshop file (the default).")
    group_export.add_argument("-s","--save",action="store_const",dest='save_type',metavar='save_type',const=tts.SaveType.save,help="ID is of savegame file.")
    group_export.add_argument("-c","--chest",action="store_const",dest='save_type',metavar='save_type',const=tts.SaveType.chest,help="ID is of chest file.")
    parser_export.add_argument("id",help="ID of mod/name of savegame to export.")
    parser_export.add_argument("-o","--output",help="Location/file to export to.")
    parser_export.add_argument("-f","--force",action="store_true",help="Force creation of export file.")
    parser_export.add_argument("-d","--download",action="store_true",help="Attempt to download missing cache files. (EXPERIMENTAL)")
    parser_export.set_defaults(func=self.do_export)

    # import command
    parser_import = subparsers.add_parser('import',help="Import a mod.",description="Import an previously exported mod.")
    parser_import.add_argument("file",help="Mod pak file to import.")
    parser_import.set_defaults(func=self.do_import)

    # download command
    parser_download = subparsers.add_parser('download',help='Download mod files.',description='Attempt to download any missing files for an installed mod.')
    group_download=parser_download.add_mutually_exclusive_group()
    group_download.add_argument("-w","--workshop",action="store_const",dest='save_type',metavar='save_type',const=tts.SaveType.workshop,help="ID is of workshop file.")
    group_download.add_argument("-s","--save",action="store_const",dest='save_type',metavar='save_type',const=tts.SaveType.save,help="ID is of savegame file.")
    group_download.add_argument("-c","--chest",action="store_const",dest='save_type',metavar='save_type',const=tts.SaveType.chest,help="ID is of chest file.")
    group_download_target=parser_download.add_mutually_exclusive_group(required=True)
    group_download_target.add_argument("-a","--all",action="store_true",help="Download all.")
    group_download_target.add_argument("id",nargs='?',help="ID of mod/name of savegame to download.")
    parser_download.set_defaults(func=self.do_download)

    # cache command
    parser_cache = subparsers.add_parser('cache',help='Work with the cache')
    subparsers_cache = parser_cache.add_subparsers(dest='parser_cache',title='cache_command',description='Valid sub-commands.')
    subparsers_cache.required = True
    parser_cache_create = subparsers_cache.add_parser('create',help='(re)create cache directory')
    parser_cache_create.set_defaults(func=self.do_cache_create)

    args = parser.parse_args()

    # set logging
    if args.loglevel:
      logmap={
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warn':logging.WARN,
        'error':logging.ERROR
       }
      tts.logger().setLevel(logmap[args.loglevel])
    else:
      tts.logger().setLevel(logging.WARN)

    # load filesystem values
    if args.directory:
      self.filesystem = tts.filesystem.FileSystem(os.path.abspath(args.directory))
    else:
      self.filesystem = tts.get_default_fs()

    if (args.parser=='list' or args.parser=='export') and not args.save_type:
      # set default
      args.save_type = tts.SaveType.workshop


    rc,message = args.func(args)
    if message:
      print(message)
    sys.exit(rc)

  def do_cache_create(self,args):
    try:
      self.filesystem.create_dirs()
    except OSError as exception:
      return 1,"OS error: {0}".format(exception)
    return 0,"All directories created OK."

  def list_by_type(self,save_type):
    result=""
    for (name,id) in tts.describe_files_by_type(self.filesystem,save_type):
      result+="\n%s (%s)" % (name,id)
    return 0,result

  def list_item(self,data,filename,ident):
    if not data:
      self.list_installed()
      return
    save=tts.Save(savedata=data,ident=ident,filename=filename)
    return 0,save

  def do_download(self,args):
    successful=True
    if not args.all:
      if not args.save_type:
        args.save_type=self.filesystem.get_json_filename_type(args.id)
      if not args.save_type:
        return 1,"Unable to determine type of id %s" % args.id
      successful = tts.download_file(self.filesystem,args.id,args.save_type)
    else:
      if args.save_type:
        for ident in self.filesystem.get_filenames_by_type(args.save_type):
          if not tts.download_file(self.filesystem,ident,args.save_type):
            successful=False
            break
      else:
        for save_type in tts.SaveType:
          for ident in self.filesystem.get_filenames_by_type(save_type):
            if not tts.download_file(self.filesystem,ident,save_type):
              successful=False
              break

    if successful:
      return 0, "All files downloaded."
    else:
      return 1, "Some files failed to download."

  def do_list(self,args):
    rc=0
    result=None

    if not args.id:
      rc,result=self.list_by_type(args.save_type)
    else:
      filename=self.filesystem.get_json_filename(args.id)
      data=tts.load_json_file(filename)
      rc,result=self.list_item(data,filename,args.id)
    return rc,result

  def do_export(self,args):
    filename=None
    if args.output:
      if os.path.isdir(args.output):
        filename=os.path.join(args.output,args.id+".pak")
      else:
        filename=args.output
    else:
      filename=args.id+".pak"

    data=None
    json_filename=None
    if not args.save_type:
      args.save_type=self.filesystem.get_json_filename_type(args.id)
    if not args.save_type:
      return 1,"Unable to determine type of id %s" % args.id

    json_filename=self.filesystem.get_json_filename_for_type(args.id,args.save_type)

    if not json_filename:
      return 1, "Unable to find filename for id %s (wrong -s/-w/-c specified?)" % args.id
    data=tts.load_json_file(json_filename)
    if not data:
      return 1, "Unable to load data for file %s" % json_filename

    save=tts.Save(savedata=data,
                  filename=json_filename,
                  ident=args.id,
                  save_type=args.save_type,
                  filesystem=self.filesystem)
    if not save.isInstalled:
      if not args.download:
        return 1, "Unable to find all urls required by %s. Rerun with -d to try and download them or open it within TTS.\n%s" % (args.id,save)
      else:
        tts.logger().info("Downloading missing files...")
        successful = save.download()
        if successful:
          tts.logger().info("Files downloaded successfully.")
        else:
          return 1, "Some files failed to download"
    if os.path.isfile(filename) and not args.force:
      return 1,"%s already exists. Please specify another file or use '-f'" % filename
    tts.logger().info("Exporting json file %s to %s" % (args.id,filename))
    save.export(filename)
    # TODO: exception handling
    return 0,"Exported %s to %s" % (args.id,filename)

  def do_import(self,args):
    return tts.save.importPak(self.filesystem,args.file)

if __name__ == "__main__":
  # fix windows' poor unicode support
  sys.stdout=_io.TextIOWrapper(sys.stdout.buffer,sys.stdout.encoding,'replace',sys.stdout.newlines,sys.stdout.line_buffering)
  tts_cli=TTS_CLI()
