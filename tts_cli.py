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

class TTS_CLI:
  def __init__(self):
    self.filesystem = tts.get_default_fs()

    parser = argparse.ArgumentParser(description="Manipulate Tabletop Simulator files")
    subparsers = parser.add_subparsers(dest='parser',title='command',description='Valid commands.')
    subparsers.required=True
    # add list command
    parser_list = subparsers.add_parser('list',help="List installed mods.",description='''
    List installed mods.
    If no id is provided, then this will return a list of all installed modules.
    If an id is provided, then this will list the contents of that modules.
    ''')
    parser_list.add_argument("-s","--saves",action="store_true",help="List saves rather than workshop files.")
    parser_list.add_argument("id",nargs='?',help="ID of specific mod to list details of.")
    parser_list.set_defaults(func=self.do_list)

    # export command
    parser_export = subparsers.add_parser('export',help="Export a mod.",description='Export a mod in a format suitible for later import.')
    group_export=parser_export.add_mutually_exclusive_group()
    group_export.add_argument("-w","--workshop",action="store_true",help="ID is of workshop file.")
    group_export.add_argument("-s","--save",action="store_true",help="ID is of savegame file.")
    parser_export.add_argument("id",help="ID of mod/name of savegame to export.")
    parser_export.add_argument("-o","--output",help="Location/file to export to.")
    parser_export.add_argument("-f","--force",action="store_true",help="Force creation of export file.")
    parser_export.set_defaults(func=self.do_export)

    # import command
    parser_import = subparsers.add_parser('import',help="Import a mod.",description="Import an previously exported mod.")
    parser_import.add_argument("file",help="Mod pak file to import.")
    parser_import.set_defaults(func=self.do_import)


    args = parser.parse_args()
    rc,message = args.func(args)
    if message:
      print(message)
    sys.exit(rc)


  def list_saves(self):
    result="Saved games:"
    for (name,id) in tts.describe_save_files(self.filesystem):
      result+="\n%s (%s)" % (name,id)
    return 0,result


  def list_installed(self):
    result="Installed workshop files:"
    for (name,id) in tts.describe_workshop_files(self.filesystem):
      result += "\n%s (%s)" % (name,id)
    return 0,result

  def list_item(self,data,filename,ident):
    if not data:
      self.list_installed()
      return
    save=tts.Save(savedata=data,ident=ident,filename=filename)
    return 0,save


  def do_list(self,args):
    rc=0
    result=None
    if not args.id:
      if args.saves:
        rc,result=self.list_saves()
      else:
        rc,result=self.list_installed()
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
    isWorkshop=True
    if args.workshop or not args.save:
      json_filename=self.filesystem.get_workshop_filename(args.id)
    if not json_filename and not args.workshop:
      json_filename=self.filesystem.get_save_filename(args.id)
      isWorkshop=False

    if args.save:
      json_filename=self.filesystem.get_save_filename(args.id)


    if not json_filename:
      return 1, "Unable to find filename for id %s (wrong -s/-w specified?)" % args.id
    data=tts.load_json_file(json_filename)
    if not data:
      return 1, "Unable to load data for file %s" % json_filename

    save=tts.Save(savedata=data,
                  filename=json_filename,
                  ident=args.id,
                  isWorkshop=isWorkshop,
                  filesystem=self.filesystem)
    if not save.isInstalled:
      return 1, "Unable to find all urls required by %s\n%s" % (args.id,save)
    if os.path.isfile(filename) and not args.force:
      return 1,"%s already exists. Please specify another file or use '-f'" % filename
    print("Exporting json file %s to %s" % (args.id,filename))
    save.export(filename)
    # TODO: exception handling
    return 0,"Exported %s to %s" % (args.id,filename)

  def do_import(self,args):
    return tts.save.importPak(self.filesystem,args.file)

if __name__ == "__main__":
  # fix windows' poor unicode support
  sys.stdout=_io.TextIOWrapper(sys.stdout.buffer,sys.stdout.encoding,'replace',sys.stdout.newlines,sys.stdout.line_buffering)
  tts_cli=TTS_CLI()
