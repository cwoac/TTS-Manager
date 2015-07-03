#!/usr/bin/env python2.7
import tts
import argparse
import os.path
import sys
import codecs
import locale


def list_installed():
  print("Installed workshop files:")
  for (name,id) in tts.describe_workshop_files():
    print("%s (%s)" % (name,id) )

def list_item(id):
  data=tts.load_workshop_file(id)
  if not data:
    list_installed()
    return
  save=tts.Save(data)
  print save

def list(args):
  if not args.id:
    list_installed()
  else:
    list_item(args.id)

def main():
    parser = argparse.ArgumentParser(description="Manipulate Tabletop Simulator files")
    subparsers = parser.add_subparsers(title='command',description='Valid commands.')

    # add list command
    parser_list = subparsers.add_parser('list',help="List installed mods.",description='''
    List installed mods.
    If no id is provided, then this will return a list of all installed modules.
    If an id is provided, then this will list the contents of that modules.
    ''')
    parser_list.add_argument("id",nargs='?',help="ID of specific mod to list details of.")
    parser_list.set_defaults(func=list)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
  # fix windows' poor unicode support
  sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
  main()