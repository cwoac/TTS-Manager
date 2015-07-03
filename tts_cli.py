#!/usr/bin/env python2.7
import tts
import argparse
import os.path
import sys
import codecs
import locale
import zipfile

def list_saves():
  print("Saved games:")
  for (name,id) in tts.describe_save_files():
    print("%s (%s)" % (name,id) )


def list_installed():
  print("Installed workshop files:")
  for (name,id) in tts.describe_workshop_files():
    print("%s (%s)" % (name,id) )

def list_item(data):
  if not data:
    list_installed()
    return
  save=tts.Save(data)
  print save

def do_list(args):
  if not args.id:
    if args.saves:
      list_saves()
    else:
      list_installed()
  else:
    data=None
    if args.saves:
      data=tts.load_save_file(args.id)
    else:
      data=tts.load_workshop_file(args.id)
    list_item(data)

def do_export(args):
  filename=None
  if args.output:
    if os.path.isdir(args.output):
      filename=os.path.join(args.output,args.id+".pak")
    else:
      filename=args.output
  else:
    filename=args.id+".pak"

  data=tts.load_workshop_file(args.id)
  if not data:
    print("Unable to load data for workshop save file %s" % args.id)
    return
  save=tts.Save(data)
  if not save.isInstalled:
    print("Unable to find all urls required by %s" % args.id)
    print(save)
    return
  if os.path.isfile(filename) and not args.force:
    print("%s already exists. Please specify another file or use '-f'" % filename)
    return
  print("Exporting workshop save file %s to %s" % (args.id,filename))
  with zipfile.ZipFile(filename,'w') as zf:
    savefile=tts.get_workshop_filename(args.id)
    zf.write(savefile,os.path.join("Mods","Workshop",os.path.basename(savefile)))
    for url in save.models:
      zf.write(url.location,os.path.join("Mods","Models",os.path.basename(url.location)))
    for url in save.images:
      zf.write(url.location,os.path.join("Mods","Images",os.path.basename(url.location)))
  # TODO: exception handling
  print("Done")
  return

def do_import(args):
  if not os.path.isfile(args.file):
    print("Unable to find mod pak %s" % args.file)
    return
  with zipfile.ZipFile(args.file,'r') as zf:
    # TODO: handle exceptions
    # TODO: Figure out a way to check this is a pack file.
    zf.extractall(tts.get_tts_dir())
  print("Done")
  return

def main():
  parser = argparse.ArgumentParser(description="Manipulate Tabletop Simulator files")
  subparsers = parser.add_subparsers(title='command',description='Valid commands.')

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
  parser_export.add_argument("id",help="ID of mod to export")
  parser_export.add_argument("-o","--output",help="Location/file to export to.")
  parser_export.add_argument("-f","--force",action="store_true",help="Force creation of export file.")
  parser_export.set_defaults(func=do_export)

  # import command
  parser_import = subparsers.add_parser('import',help="Import a mod.",description="Import an previously exported mod.")
  parser_import.add_argument("file",help="Mod pak file to import.")
  parser_import.set_defaults(func=do_import)


  args = parser.parse_args()
  args.func(args)

if __name__ == "__main__":
  # fix windows' poor unicode support
  sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
  main()