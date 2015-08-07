import tts
import tkinter as Tk
import tkinter.ttk as ttk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import tkinter.scrolledtext as scrolledtext
import os.path
import logging

class TTS_MANAGER:
  def __init__(self,root):
    self.log=tts.logger()
    self.log.setLevel(logging.WARN)
    self.preferences=tts.preferences.Preferences()
    self.root=root
    Tk.Grid.rowconfigure(self.root,0,weight=1)
    Tk.Grid.columnconfigure(self.root,0,weight=1)
    self.log_window=tts.TTS_LOGGER(root)

    if self.preferences.firstRun:
      messagebox.showinfo("TTS Manager","First run detected.\nOpening preferences pane.")
      self.showPreferences()

    if not self.preferences.validate():
      messagebox.showwarning("TTS Manager","Invalid preferences detected.\nOpening preferences pane.")
      self.showPreferences()

    self.filesystem=self.preferences.get_filesystem()
    self.populate_manage_frame(root)

  def reload_filesystem(self):
    self.filesystem=self.preferences.get_filesystem()
    self.file_list_current=None
    self.file_list_box.selection_clear(0,Tk.END)

  def populate_manage_frame(self,frame):
    ttk.Label(frame,text="Select list source:").grid(row=0,sticky=Tk.W)
    self.save_type=Tk.IntVar()
    self.save_type.set(int(tts.SaveType.workshop))
    ttk.Radiobutton(frame,
                   text="Workshop",
                   variable=self.save_type,
                   value=int(tts.SaveType.workshop),
                   command=self.list_command).grid(row=0,column=1)
    ttk.Radiobutton(frame,
                   text="Save",
                   variable=self.save_type,
                   value=int(tts.SaveType.save),
                   command=self.list_command).grid(row=0,column=2)
    ttk.Radiobutton(frame,
                   text="Chest",
                   variable=self.save_type,
                   value=int(tts.SaveType.chest),
                   command=self.list_command).grid(row=0,column=3)
    fl_frame=ttk.Frame(frame)
    fl_frame.grid(row=1,columnspan=4,sticky=Tk.N+Tk.S+Tk.E+Tk.W)
    ttk.Label(fl_frame,text="Files found:").pack()
    foundBar=ttk.Scrollbar(fl_frame,orient=Tk.VERTICAL)
    self.file_list_box=Tk.Listbox(fl_frame,yscrollcommand=foundBar.set)
    foundBar.config(command=self.file_list_box.yview)
    foundBar.pack(side=Tk.RIGHT,fill=Tk.Y)
    self.file_list_box.pack(side=Tk.LEFT,fill=Tk.BOTH,expand=Tk.Y)
    self.file_list_box.config(state=Tk.DISABLED)

    self.downloadButton=ttk.Button(frame,
                                   text="Download",
                                   command=self.download,
                                   state=Tk.DISABLED)
    self.downloadButton.grid(row=2,column=0)
    self.exportButton=ttk.Button(frame,
                                 text="Export",
                                 command=self.export,
                                 state=Tk.DISABLED)
    self.exportButton.grid(row=2,column=1)

    ttk.Button(frame,text="Preferences",command=self.showPreferences).grid(row=3)
    ttk.Button(frame,text="Log",command=self.log_window.toggle).grid(row=3,column=1)

    # Enable resizing
    for x in range(4):
      Tk.Grid.columnconfigure(frame,x,weight=1)
    for y in range(3):
      Tk.Grid.rowconfigure(frame,y,weight=1)

    self.file_list_current=None
    self.list_command()
    self.poll_file_list()

  def download(self):
    if not self.save:
      tts.logger().warn("Internal error: self.save NULL when attempting to download")
      messagebox.showinfo("TTS Manager","Download failed (see log).")
      return
    if self.save.download():
      messagebox.showinfo("TTS Manager","Download done.")
    else:
      messagebox.showinfo("TTS Manager","Download failed (see log).")
    self.file_list_has_changed(self.file_list_current)

  def export(self):
    pass

  def poll_file_list(self):
    now = self.file_list_box.curselection()
    if now != self.file_list_current:
      self.file_list_has_changed(now)
      self.file_list_current=now
    self.root.after(250,self.poll_file_list)

  def file_list_has_changed(self,now):
    if not now:
      return
    ident=self.file_store[now[0]]
    filename=self.filesystem.get_json_filename_for_type(ident,self.save_type.get())
    data=tts.load_json_file(filename)
    # TODO: error handling
    self.save=tts.Save(savedata=data,
                       ident=ident,
                       filename=filename,
                       save_type=tts.SaveType(self.save_type.get()),
                       filesystem=self.filesystem)
    if self.save.isInstalled:
      self.downloadButton.configure(text="All files Downloaded",
                                    state=Tk.DISABLED)
      self.exportButton.configure(text="Export",state=Tk.NORMAL)
    else:
      self.downloadButton.configure(text="Download missing files",
                                    state=Tk.NORMAL)
      self.exportButton.configure(text="Download and Export",
                                  state=Tk.NORMAL)

  def list_command(self):
    """ Populates the list box"""
    data=tts.describe_files_by_type(self.filesystem,self.save_type.get())
    self.file_list_box.config(state=Tk.NORMAL)
    self.file_list_box.delete(0,Tk.END)
    self.file_store={}
    i=0
    for (name,number) in data:
      self.file_list_box.insert(Tk.END,"%s (%s)\n" % (name,number))
      self.file_store[i]=number
      i+=1

  def showPreferences(self):
    preferences_dialog=tts.preferences.PreferencesDialog(self.root)
    self.log.debug(preferences_dialog.preferences)
    self.preferences=preferences_dialog.preferences
    self.reload_filesystem()

def main():
  root = Tk.Tk()
  root.wm_title("TTS Manager")
  x=TTS_MANAGER(root)
  root.mainloop()

if __name__ == "__main__":
  main()
