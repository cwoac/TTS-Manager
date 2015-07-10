from distutils.core import setup
import py2exe,sys,os

sys.argv.append("py2exe")



setup(
  options = {'py2exe': {'optimize':2,
                        'bundle_files':2,
                        'compressed':True,
                        'excludes':['doctest','pdb','unittest','inspect','difflib']}},
  zipfile=None,

  console=['tts_cli.py']
)

setup(
  options = {'py2exe': {'optimize':2,
                        'bundle_files':2,
                        'compressed':True,
                        'excludes':['doctest','pdb','unittest','inspect','difflib']}},
  zipfile=None,
  windows=[{'script':'tts_gui.py'}]
)
