#!/usr/bin/env python2.7
import tts
import argparse
import os.path
import sys
import codecs
import locale
import zipfile
import _io

def list_saves():
  result="Saved games:"
  for (name,id) in tts.describe_save_files():
    result+="\n%s (%s)" % (name,id)
  return 0,result


def list_installed():
  result="Installed workshop files:"
  for (name,id) in tts.describe_workshop_files():
    result += "\n%s (%s)" % (name,id)
  return 0,result

def list_item(data):
  if not data:
    list_installed()
    return
  save=tts.Save(data)
  return 0,save


def do_list(args):
  rc=0
  result=None
  if not args.id:
    if args.saves:
      rc,result=list_saves()
    else:
      rc,result=list_installed()
  else:
    data=None
    if args.saves:
      data=tts.load_save_file(args.id)
    else:
      data=tts.load_workshop_file(args.id)
    rc,result=list_item(data)
  return rc,result

def do_export(args):
  filename=None
  if args.output:
    if os.path.isdir(args.output):
      filename=os.path.join(args.output,args.id+".pak")
    else:
      filename=args.output
  else:
    filename=args.id+".pak"

  data=None
  if args.workshop or (args.id[0].isdigit() and not args.save):
    data=tts.load_workshop_file(args.id)
  if args.save or (args.id.startswith('TS_') and not args.workshop):
    data=tts.load_save_file(args.id)
  if not data:
    return 1, "Unable to load data for file %s (perhaps specify type with -s/-w)" % args.id

  save=tts.Save(data)
  if not save.isInstalled:
    return 1, "Unable to find all urls required by %s\n%s" % (args.id,save)
  if os.path.isfile(filename) and not args.force:
    return 1,"%s already exists. Please specify another file or use '-f'" % filename
  print("Exporting workshop save file %s to %s" % (args.id,filename))
  with zipfile.ZipFile(filename,'w') as zf:
    savefile=tts.get_workshop_filename(args.id)
    zf.write(savefile,os.path.join("Mods","Workshop",os.path.basename(savefile)))
    for url in save.models:
      zf.write(url.location,os.path.join("Mods","Models",os.path.basename(url.location)))
    for url in save.images:
      zf.write(url.location,os.path.join("Mods","Images",os.path.basename(url.location)))
  # TODO: exception handling
  return 0,"Exported %s to %s" % (args.id,filename)

def do_import(args):
  if not os.path.isfile(args.file):
    print("Unable to find mod pak %s" % args.file)
    return
  with zipfile.ZipFile(args.file,'r') as zf:
    # TODO: handle exceptions
    # TODO: Figure out a way to check this is a pack file.
    zf.extractall(tts.get_tts_dir())
  return 0,"Imported %s" % args.file

def main():
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
  parser_list.set_defaults(func=do_list)

  # export command
  parser_export = subparsers.add_parser('export',help="Export a mod.",description='Export a mod in a format suitible for later import.')
  group_export=parser_export.add_mutually_exclusive_group()
  group_export.add_argument("-w","--workshop",action="store_true",help="ID is of workshop file.")
  group_export.add_argument("-s","--save",action="store_true",help="ID is of savegame file.")
  parser_export.add_argument("id",help="ID of mod/name of savegame to export.")
  parser_export.add_argument("-o","--output",help="Location/file to export to.")
  parser_export.add_argument("-f","--force",action="store_true",help="Force creation of export file.")
  parser_export.set_defaults(func=do_export)

  # import command
  parser_import = subparsers.add_parser('import',help="Import a mod.",description="Import an previously exported mod.")
  parser_import.add_argument("file",help="Mod pak file to import.")
  parser_import.set_defaults(func=do_import)


  args = parser.parse_args()
  rc,message = args.func(args)
  if message:
    print(message)
  sys.exit(rc)

if __name__ == "__main__":
  # fix windows' poor unicode support
  sys.stdout=_io.TextIOWrapper(sys.stdout.buffer,sys.stdout.encoding,'replace',sys.stdout.newlines,sys.stdout.line_buffering)

  main()