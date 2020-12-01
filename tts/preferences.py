import tkinter as Tk
import tkinter.ttk as ttk
import tkinter.simpledialog as simpledialog
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import tts
import platform
import os

if platform.system() == 'Windows':
  import winreg
else:
  import xdgappdirs
  import configparser

class Preferences(object):
  def __new__(cls):
    """Select the correct platform class."""
    if platform.system() == 'Windows':
      new_cls = PreferencesWin
    else:
      new_cls = PreferencesLinux
    instance = super(Preferences, new_cls).__new__(new_cls)
    if not issubclass(new_cls, cls) and new_cls != cls:
      instance.__init__(n)
    return instance

  def __init__(self):
    self.changed=False
    self._locationIsUser = True
    self._TTSLocation = ''
    self._defaultSaveLocation = ''
    self._firstRun = False
    #child class must initialize these properly (load from disk or assign defaults)

  @property
  def locationIsUser(self):
    return self._locationIsUser

  @locationIsUser.setter
  def locationIsUser(self,value):
    if self._locationIsUser==bool(value):
      return
    self._locationIsUser=bool(value)
    self.changed=True

  @property
  def TTSLocation(self):
    return self._TTSLocation

  @TTSLocation.setter
  def TTSLocation(self,value):
    value = os.path.normpath(value)
    if self._TTSLocation==value:
      return
    self._TTSLocation=value
    self.changed=True

  @property
  def defaultSaveLocation(self):
    return self._defaultSaveLocation

  @defaultSaveLocation.setter
  def defaultSaveLocation(self,value):
    if self._defaultSaveLocation==value:
      return
    self._defaultSaveLocation=value
    self.changed=True

  @property
  def firstRun(self):
    return self._firstRun

  @firstRun.setter
  def firstRun(self,value):
    if self._firstRun==bool(value):
      return
    self._firstRun=bool(value)
    self.changed=True

  def reset(self):
    self._locationIsUser=True
    self._firstRun=1
    self._defaultSaveLocation=""
    self._TTSLocation=""
    #child class must delete values from disk storage

  def save(self):
    # No longer first run.
    self.firstRun=0
    #Child class must save all 4 values to disk storage

  def validate(self):
    return self.get_filesystem().check_dirs()

  def get_filesystem(self):
    if self.locationIsUser:
      return tts.get_default_fs()
    return tts.filesystem.FileSystem(tts_install_path=self.TTSLocation)

  def __str__(self):
    return f"""Preferences:
locationIsUser: {self.locationIsUser}
TTSLocation: {self.TTSLocation}
DefaultSaveLocation: {self.defaultSaveLocation}
firstRun: {self.firstRun}"""


class PreferencesWin(Preferences):

  def __init__(self):
    super().__init__()
    self._connection=winreg.ConnectRegistry(None,winreg.HKEY_CURRENT_USER)
    self._registry=winreg.CreateKeyEx( self._connection, "Software\TTS Manager",0,winreg.KEY_ALL_ACCESS )
    try:
      self._locationIsUser="True"==winreg.QueryValueEx(self._registry,"locationIsUser")[0]
    except FileNotFoundError as e:
      self._locationIsUser=True
    try:
      self._TTSLocation=os.path.normpath( winreg.QueryValueEx(self._registry,"TTSLocation")[0] )
    except FileNotFoundError as e:
      self._TTSLocation=""
    try:
      self._defaultSaveLocation=winreg.QueryValueEx(self._registry,"defaultSaveLocation")[0]
    except FileNotFoundError as e:
      self._defaultSaveLocation=""
    try:
      self._firstRun="True"==winreg.QueryValueEx(self._registry,"firstRun")[0]
    except FileNotFoundError as e:
      self._firstRun=True

  def reset(self):
    super().reset()
    winreg.DeleteValue(self._registry,"locationIsUser")
    winreg.DeleteValue(self._registry,"TTSLocation")
    winreg.DeleteValue(self._registry,"defaultSaveLocation")
    winreg.DeleteValue(self._registry,"firstRun")

  def save(self):
    super().save()
    # Make sure all values have been createds
    winreg.SetValueEx(self._registry,"locationIsUser",0,winreg.REG_SZ,str(self.locationIsUser))
    winreg.SetValueEx(self._registry,"TTSLocation",0,winreg.REG_SZ,str(self.TTSLocation))
    winreg.SetValueEx(self._registry,"defaultSaveLocation",0,winreg.REG_SZ,str(self.defaultSaveLocation))
    winreg.SetValueEx(self._registry,"firstRun",0,winreg.REG_SZ,str(self._firstRun))


class PreferencesLinux(Preferences):

  def __init__(self):
    super().__init__()
    self._conffile = os.path.join(xdgappdirs.user_config_dir(),'tts_manager.ini')
    self._config = configparser.ConfigParser(allow_no_value=True)
    self._config['main'] = {'locationIsUser': 'yes',
                         'TTSLocation': '',
                         'defaultSaveLocation': '',
                         'firstRun': '0'}
    self._config.read(self._conffile, encoding='utf-8')
    self._locationIsUser = self._config['main'].getboolean('locationIsUser')
    self._TTSLocation = self._config['main']['TTSLocation']
    self._defaultSaveLocation = self._config['main']['defaultSaveLocation']
    self._firstRun = self._config['main'].getboolean('load_firstRun')

  def reset(self):
    super().reset()
    os.unlink(self._conffile)
    self.__init__()

  def save(self):
    super().save()
    # Make sure all values have been createds
    self._config['main']['locationIsUser'] = 'yes' if self._locationIsUser else 'no'
    self._config['main']['TTSLocation'] = self._TTSLocation
    self._config['main']['defaultSaveLocation'] = self._defaultSaveLocation
    self._config['main']['firstRun'] = 'yes' if self._firstRun else 'no'
    with open(self._conffile, 'w') as configfile:
      self._config.write(configfile)


class PreferencesDialog(simpledialog.Dialog):
  def applyLocationIsUser(*args):
    args[0].preferences.locationIsUser=args[0].locationIsUser.get()

  def body(self,master):
    self.master=master
    self.preferences=Preferences()
    ttk.Label(master,text="Mod Save Location:").grid(row=0)
    self.locationIsUser=Tk.BooleanVar()
    ttk.Radiobutton(master,
                    text="Documents",
                    variable=self.locationIsUser,
                    value=True).grid(row=0,column=1)
    ttk.Radiobutton(master,
                    text="Game Data",
                    variable=self.locationIsUser,
                    value=False).grid(row=0,column=2)
    self.locationIsUser.set(self.preferences.locationIsUser)
    self.locationIsUser.trace("w",self.applyLocationIsUser)
    ttk.Label(master,text="TTS Install location:").grid(row=1,columnspan=3)
    self.ttsLocationEntry=ttk.Entry(master)
    self.ttsLocationEntry.insert(0,self.preferences.TTSLocation)
    self.ttsLocationEntry.grid(row=2,sticky=Tk.E+Tk.W,columnspan=2)
    ttk.Button(master,text="Browse",command=self.pickTTSDir).grid(row=2,column=2)
    ttk.Label(master,text="If you have installed via Steam, this will be something like:\n \"C:\\Program Files (x86)\\Steam\\steamapps\\common\\Tabletop Simulator\"").grid(row=5,columnspan=2)
    ttk.Button(master,text="Validate",command=self.validate).grid(row=3,columnspan=3)

  def pickTTSDir(self):
    self.preferences.TTSLocation=filedialog.askdirectory(
            parent=self.master,
            mustexist=True
        )
    self.ttsLocationEntry.delete(0,Tk.END)
    self.ttsLocationEntry.insert(0,self.preferences.TTSLocation)

  def validate(self):
    self.preferences.TTSLocation=self.ttsLocationEntry.get()
    if not self.preferences.validate():
      messagebox.showwarning("Missing directories","Unable to find some directories - please check your settings.")
      return False
    messagebox.showinfo("TTS Manager","Preferences validated OK.")
    return True

  def apply(self):
    self.preferences.TTSLocation=self.ttsLocationEntry.get()
    self.preferences.save()
