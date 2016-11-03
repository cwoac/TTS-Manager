import tkinter as Tk
import tkinter.ttk as ttk
import tkinter.simpledialog as simpledialog
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import winreg
import tts

class Preferences():
  def __init__(self):
    self.connection=winreg.ConnectRegistry(None,winreg.HKEY_CURRENT_USER)
    self.registry=winreg.CreateKey( self.connection, "Software\TTS Manager")
    self.changed=False
    try:
      self._locationIsUser="True"==winreg.QueryValueEx(self.registry,"locationIsUser")[0]
    except FileNotFoundError as e:
      self._locationIsUser=True
    try:
      self._TTSLocation=winreg.QueryValueEx(self.registry,"TTSLocation")[0]
    except FileNotFoundError as e:
      self._TTSLocation=""
    try:
      self._defaultSaveLocation=winreg.QueryValueEx(self.registry,"defaultSaveLocation")[0]
    except FileNotFoundError as e:
      self._defaultSaveLocation=""
    try:
      self._firstRun="True"==winreg.QueryValueEx(self.registry,"firstRun")[0]
    except FileNotFoundError as e:
      self._firstRun=True

  @property
  def locationIsUser(self):
    return self._locationIsUser

  @locationIsUser.setter
  def locationIsUser(self,value):
    if self._locationIsUser==(value==1):
      return
    self._locationIsUser=(value==1)
    self.changed=True

  @property
  def TTSLocation(self):
    return self._TTSLocation

  @TTSLocation.setter
  def TTSLocation(self,value):
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
    if self._firstRun==(value==1):
      return
    self._firstRun=(value==1)
    self.changed=True

  def reset(self):
    self._locationIsUser=True
    self._firstRun=1
    self._defaultSaveLocation=""
    self._TTSLocation=""
    winreg.DeleteValue(self.registry,"locationIsUser")
    winreg.DeleteValue(self.registry,"TTSLocation")
    winreg.DeleteValue(self.registry,"defaultSaveLocation")
    winreg.DeleteValue(self.registry,"firstRun")

  def save(self):
    # No longer first run.
    self.firstRun=0
    # Make sure all values have been createds
    winreg.SetValueEx(self.registry,"locationIsUser",0,winreg.REG_SZ,str(self.locationIsUser))
    winreg.SetValueEx(self.registry,"TTSLocation",0,winreg.REG_SZ,str(self.TTSLocation))
    winreg.SetValueEx(self.registry,"defaultSaveLocation",0,winreg.REG_SZ,str(self.defaultSaveLocation))
    winreg.SetValueEx(self.registry,"firstRun",0,winreg.REG_SZ,str(self._firstRun))

  def validate(self):
    return self.get_filesystem().check_dirs()

  def get_filesystem(self):
    if self.locationIsUser:
      return tts.get_default_fs()
    return tts.filesystem.FileSystem(tts_install_path=self.TTSLocation)

  def __str__(self):
    return """Preferences:
locationIsUser: {}
TTSLocation: {}
DefaultSaveLocation: {}
firstRun: {}""".format(self.locationIsUser,self.TTSLocation,self.defaultSaveLocation,self.firstRun)



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
