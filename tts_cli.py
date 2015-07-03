#!/usr/bin/env python2.7
import tts
import argparse
import os.path
import sys
import codecs
import locale


def list_installed(_):
  for (name,id) in tts.describe_workshop_files():
    print("%s (%s)" % (name,id) )


def main():
    parser = argparse.ArgumentParser(description="Manipulate Tabletop Simulator files")
    subparsers = parser.add_subparsers(title='command',description='Valid commands.')

    # add list command
    parser_list = subparsers.add_parser('list',help="List installed mods.",description="List installed mods.")
    parser_list.set_defaults(func=list_installed)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
  # fix windows' poor unicode support
  sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
  main()