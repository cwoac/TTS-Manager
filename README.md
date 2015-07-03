# TTS-Manager
Import/Export Mods from Tabletop Simulator, including all assets.

## Status

Currently this code is rather alpha quality; there is no failure recovery or pretty printing of error messages. It has also only been tested on a limited number of mods and machines. If you find a configuration / mod that doesn't work, please let me know.

Listing, export and import all should work. Note that old-style mods (`.cjc` files) are *not* supported.

Currently the code is command line only, the gui version is under development.

To export a mod, you must have downloaded *all* assets. Opening a mod in Tabletop Simulator is usually enough, but make sure you have taken something out of every bag in the mod. If anything is missing, then the tool will tell you.

## Quickstart

download `tts_cli.exe` from the [releases](https://github.com/cwoac/TTS-Manager/releases) and run it from a command window. Use `tts_cli list` to find the id number of the mod to export then `tts_cli export id` to create a `.pak` file. You can then import this into an install using `tts_cli import path/to/pakfile`. The commands have further options, use `-h` to find out.

## Requirements
Either download a compiled exe, or run using python.

## TODO
- Gui.
- Downloading of missing data items.
- Some form of verification of pak contents.
- Error handling.
- LOTS MORE TESTING.
