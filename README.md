# TTS-Manager
Import/Export Mods from Tabletop Simulator, including all assets.

## Status

Currently this code is rather alpha quality; there is no failure recovery or pretty printing of error messages. It has also only been tested on a limited number of mods and machines. **Do not rely on this to backup your files without checking it restores correctly on another install.** If you find a configuration / mod that doesn't work, please let me know.

Listing, export and import all should work. Note that old-style mods (`.cjc` files) are *not* supported.

To export a mod, you must have downloaded *all* assets. Opening a mod in Tabletop Simulator is usually enough, but make sure you have taken something out of every bag in the mod. If anything is missing, then the tool will tell you.

## Quickstart
### GUI
download `tts_gui.exe` from the [releases](https://github.com/cwoac/TTS-Manager/releases) and run it. Pick the action you want at the top.

### Command Line
download `tts_cli.exe` from the [releases](https://github.com/cwoac/TTS-Manager/releases) and run it from a command window. Use `tts_cli list` to find the id number of the mod to export then `tts_cli export id` to create a `.pak` file. You can then import this into an install using `tts_cli import path/to/pakfile`. The commands have further options, use `-h` to find out.

## Requirements
Either download a compiled exe, or run using python3.

## TODO
These are primarily tracked on github, but roughly:
- Downloading of missing data items.
- Uninstalling paks
- Error handling.
- LOTS MORE TESTING.
