import tkinter as Tk
import tkinter.ttk as ttk
import tkinter.simpledialog as simpledialog
import winreg
import tts

class Preferences(simpledialog.Dialog):
  def body(self,master):
    self.connection=winreg.ConnectRegistry(None,winreg.HKEY_CURRENT_USER)
    self.registry=winreg.OpenKey( self.connection, "Software\TTS Manager",0,winreg.KEY_ALL_ACCESS )
    locationFrame=ttk.Frame(master)
    locationFrame.pack()
    ttk.Label(locationFrame,text="Mod Save Location:").pack()
    self.locationIsUser=Tk.BooleanVar()
    self.locationIsUser.set(True)
    try:
      self.locationIsUser.set(winreg.QueryValueEx(self.registry,"locationIsUser")[0])
    except FileNotFoundError as e:
      pass

    ttk.Radiobutton(locationFrame,
                    text="Documents",
                    variable=self.locationIsUser,
                    value=True).pack(side=Tk.LEFT)
    ttk.Radiobutton(locationFrame,
                    text="Game Data",
                    variable=self.locationIsUser,
                    value=False).pack(side=Tk.LEFT)

    ttsFrame=ttk.Frame(master)
    ttsFrame.pack()
    ttk.Label(ttsFrame,text="TTS Install location:")
    self.TTSLocation=Tk.StringVar()
    self.TTSLocation.set("")
    try:
      self.TTSLocation.set(winreg.QueryValueEx(self.registry,"TTSLocation")[0])
    except FileNotFoundError as e:
      pass

  def apply(self):
    winreg.SetValueEx(self.registry,"locationIsUser",0,winreg.REG_SZ,str(self.locationIsUser.get()))
    self.changed=True

