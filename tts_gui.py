import tts
import tkinter as Tk
import tkinter.ttk as ttk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import tkinter.scrolledtext as ScrolledText
import os.path
import logging

class SaveBrowser():
  def __init__(self,master,filesystem):
    self.filesystem = filesystem
    self.master=master
    srcFrame=ttk.Frame(master)
    srcFrame.pack()
    ttk.Label(srcFrame,text="Select list source:").pack()
    self.save_type=Tk.IntVar()
    self.save_type.set(int(tts.SaveType.workshop))
    ttk.Radiobutton(srcFrame,
                   text="Workshop",
                   variable=self.save_type,
                   value=int(tts.SaveType.workshop),
                   command=self.list_command).pack(side=Tk.LEFT)
    ttk.Radiobutton(srcFrame,
                   text="Save",
                   variable=self.save_type,
                   value=int(tts.SaveType.save),
                   command=self.list_command).pack(side=Tk.LEFT)
    ttk.Radiobutton(srcFrame,
                   text="Chest",
                   variable=self.save_type,
                   value=int(tts.SaveType.chest),
                   command=self.list_command).pack(side=Tk.LEFT)
    scrollFrame=ttk.Frame(master)
    scrollFrame.pack(expand=1,fill=Tk.BOTH)
    ttk.Label(scrollFrame,text="Files found:").pack()
    foundBar=ttk.Scrollbar(scrollFrame,orient=Tk.VERTICAL)
    self.file_list=Tk.Listbox(scrollFrame,yscrollcommand=foundBar.set)
    foundBar.config(command=self.file_list.yview)
    foundBar.pack(side=Tk.RIGHT,fill=Tk.Y)
    self.file_list.pack(side=Tk.LEFT,fill=Tk.BOTH,expand=Tk.Y)
    statusFrame=ttk.Frame(master)
    statusFrame.pack(expand=Tk.Y,fill=Tk.BOTH)
    self.status_label=ttk.Label(statusFrame)
    self.status_label.pack(fill=Tk.BOTH,expand=Tk.Y)
    self.file_list_current = None
    self.poll_file_list()

  def bind(self,event,function):
    self.file_list.bind(event,function)

  def list_command(self):
    """ Populates the list box"""
    data=tts.describe_files_by_type(self.filesystem,self.save_type.get())
    self.file_list.delete(0,Tk.END)
    self.file_store={}
    i=0
    for (name,number) in data:
      self.file_list.insert(Tk.END,"%s (%s)" % (name,number))
      self.file_store[i]=number
      i+=1


  def poll_file_list(self):
    now = self.file_list.curselection()
    if now != self.file_list_current:
      self.file_list_has_changed(now)
      self.file_list_current=now
    self.master.after(250,self.poll_file_list)

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
      self.status_label.config(text="All files found.")
    else:
      self.status_label.config(text="Some cache files missing - check details on list page.")
    self.file_list.event_generate("<<SelectionChange>>")


class TTS_GUI:
  def update_list_frame_details(self,event):
    self.details_list.config(state=Tk.NORMAL)
    self.details_list.delete(1.0,Tk.END)
    self.details_list.insert(Tk.END,self.list_sb.save)
    self.details_list.config(state=Tk.DISABLED)

  def populate_list_frame(self,frame):
    self.list_sb=SaveBrowser(frame,self.filesystem)
    self.list_sb.bind("<<SelectionChange>>",self.update_list_frame_details)
    ttk.Label(frame,text="Details:").pack()
    self.details_list=ScrolledText.ScrolledText(master=frame,height=5)
    self.details_list.config(state=Tk.DISABLED)
    self.details_list.pack(fill=Tk.BOTH, expand=Tk.Y)
    self.list_sb.list_command()

  def update_export_frame_details(self,event):
    if self.export_sb.save.isInstalled:
      self.downloadMissingFiles.set(False)
      self.downloadMissingFilesCB.config(state=Tk.DISABLED)
      self.exportButton.config(state=Tk.NORMAL)
      self.targetEntry.delete(0,Tk.END)
      self.export_filename=os.path.join(os.path.expanduser("~"),"Downloads",self.export_sb.save.ident+'.pak')
      self.targetEntry.insert(0,self.export_filename)
    else:
      self.downloadMissingFilesCB.config(state=Tk.NORMAL)
      self.exportButton.config(state=Tk.DISABLED)
      self.export_filename=None
      self.targetEntry.delete(0,Tk.END)

  def pickExportTarget(self):
    self.export_filename = filedialog.asksaveasfilename(
      parent=self.root,
      initialdir=os.path.join(os.path.expanduser("~"),"Downloads"),
      filetypes=[('PAK files','*.pak')],
      defaultextension='pak',
      title='Choose export target')
    self.targetEntry.delete(0,Tk.END)
    self.targetEntry.insert(0,self.export_filename)

  def pickImportTarget(self):
    self.import_filename = filedialog.askopenfilename(
      parent=self.root,
      initialdir=os.path.join(os.path.expanduser("~"),"Downloads"),
      filetypes=[('PAK files','*.pak')],
      defaultextension='pak',
      title='Choose import target')
    self.importEntry.delete(0,Tk.END)
    self.importEntry.insert(0,self.import_filename)

  def exportPak(self):
    if not self.export_sb.save.isInstalled:
      successful = self.export_sb.save.download()
      if not successful:
        messagebox.showinfo("TTS Manager","Export failed (see log)")
        return
    self.export_filename=self.targetEntry.get()
    self.export_sb.save.export(self.export_filename)
    messagebox.showinfo("TTS Manager","Export Done.")

  def importPak(self):
    self.import_filename=self.importEntry.get()
    rc=tts.save.importPak(self.filesystem,self.import_filename)
    if rc:
      messagebox.showinfo("TTS Manager","Pak imported successfully.")
    else:
      messagebox.showwarning("TTS Manager","Pak import failed - see log.")

  def toggleDownloadMissing(self):
    if self.downloadMissingFiles.get():
      self.exportButton.config(state=Tk.NORMAL)
      self.targetEntry.delete(0,Tk.END)
      self.export_filename=os.path.join(os.path.expanduser("~"),"Downloads",self.export_sb.save.ident+'.pak')
      self.targetEntry.insert(0,self.export_filename)
    else:
      self.exportButton.config(state=Tk.DISABLED)
      self.export_filename=None
      self.targetEntry.delete(0,Tk.END)

  def populate_export_frame(self,frame):
    self.export_sb=SaveBrowser(frame,self.filesystem)
    self.export_sb.bind("<<SelectionChange>>",self.update_export_frame_details)
    targetFrame=ttk.Frame(frame)
    targetFrame.pack(expand=Tk.Y,fill=Tk.BOTH)
    self.downloadMissingFiles=Tk.BooleanVar()
    self.downloadMissingFiles.set(False)
    self.downloadMissingFilesCB=ttk.Checkbutton(targetFrame,
                    text="Download missing files.",
                    variable=self.downloadMissingFiles,
                    offvalue=False,
                    onvalue=True,
                    state=Tk.DISABLED,
                    command=self.toggleDownloadMissing)
    self.downloadMissingFilesCB.pack()
    ttk.Label(targetFrame,text="Select output file").pack()
    self.targetEntry=ttk.Entry(targetFrame)
    self.targetEntry.pack(side=Tk.LEFT,expand=Tk.Y,fill=Tk.X)
    ttk.Button(targetFrame,text="Browse",command=self.pickExportTarget).pack(side=Tk.LEFT)

    exportFrame=ttk.Frame(frame)
    exportFrame.pack(expand=Tk.Y,fill=Tk.BOTH)
    self.export_filename=None
    self.exportButton=ttk.Button(exportFrame,text="Export",command=self.exportPak,state=Tk.DISABLED)
    self.exportButton.pack()

    self.export_sb.list_command()

  def populate_import_frame(self,frame):
    importEntryFrame=ttk.Frame(frame)
    importEntryFrame.pack(expand=Tk.Y,fill=Tk.BOTH)
    ttk.Label(importEntryFrame,text="Select pak to import.").pack()
    self.importEntry=ttk.Entry(importEntryFrame)
    self.importEntry.pack(side=Tk.LEFT,expand=Tk.Y,fill=Tk.X)
    self.import_filename=None
    importEntryButton=ttk.Button(importEntryFrame,text="Browse",command=self.pickImportTarget).pack(side=Tk.LEFT)

    importFrame=ttk.Frame(frame)
    importFrame.pack(expand=Tk.Y,fill=Tk.BOTH)
    ttk.Button(importFrame,text="Import",command=self.importPak).pack()

  def update_download_frame_details(self,event):
    if self.download_sb.save.isInstalled:
      self.downloadButton.config(state=Tk.DISABLED)
    else:
      self.downloadButton.config(state=Tk.NORMAL)

  def download(self):
    if not self.download_sb.save:
      tts.logger().warn("Internal error: no save when attempting to download")
      messagebox.showinfo("TTS Manager","Download failed (see log).")
      return
    if self.download_sb.save.download():
      messagebox.showinfo("TTS Manager","Download done.")
    else:
      messagebox.showinfo("TTS Manager","Download failed (see log).")

  def download_all(self):
    successful=True
    save_type={1:tts.SaveType.workshop,
               2:tts.SaveType.save,
               3:tts.SaveType.chest}[self.download_sb.save_type.get()]
    for ident in self.download_sb.file_store.values():
      successful = tts.download_file(self.filesystem,ident,save_type)
      if not successful:
        break
    if successful:
      messagebox.showinfo("TTS Manager","All files downloaded successfully.")
    else:
      messagebox.showinfo("TTS Manager","Some downloads failed (see log).")

  def populate_download_frame(self,frame):
    self.download_sb=SaveBrowser(frame,self.filesystem)
    self.download_sb.bind("<<SelectionChange>>",self.update_download_frame_details)
    self.downloadButton=ttk.Button(frame,text="Download",command=self.download)
    self.downloadButton.pack()
    downloadAllButton=ttk.Button(frame,text="Download All",command=self.download_all).pack()
    self.download_sb.list_command()

  def change_log_level(self,event):
    levels=[logging.DEBUG,logging.INFO,logging.WARN,logging.ERROR]
    tts.logger().info("Setting log level to %s" % levels[self.loggerLevel.current()])
    tts.logger().setLevel(levels[self.loggerLevel.current()])

  def showPreferences(self):
    preferences_dialog=tts.preferences.PreferencesDialog(self.root)
    self.log.debug(preferences_dialog.preferences)
    self.preferences=preferences_dialog.preferences
    self.reload_filesystem()

  def reload_filesystem(self):
    if self.preferences.locationIsUser:
      self.filesystem=tts.get_default_fs()
    else:
      self.filesystem=tts.filesystem.FileSystem(tts_install_path=self.preferences.TTSLocation)

  def __init__(self,root):
    self.log=tts.logger()
    self.log.setLevel(logging.WARN)
    self.preferences=tts.preferences.Preferences()
    self.root=root

    if self.preferences.firstRun:
      messagebox.showinfo("TTS Manager","First run detected.\nOpening preferences pane.")
      self.showPreferences()

    if not self.preferences.validate():
      messagebox.showwarning("TTS Manager","Invalid preferences detected.\nOpening preferences pane.")
      self.showPreferences()

    self.reload_filesystem()
    mode_notebook = ttk.Notebook(root)
    list_frame = ttk.Frame(mode_notebook)
    self.populate_list_frame(list_frame)
    export_frame = ttk.Frame(mode_notebook)
    self.populate_export_frame(export_frame)
    import_frame = ttk.Frame(mode_notebook)
    self.populate_import_frame(import_frame)
    download_frame = ttk.Frame(mode_notebook)
    self.populate_download_frame(download_frame)

    mode_notebook.add(list_frame,text="List")
    mode_notebook.add(export_frame,text="Export")
    mode_notebook.add(import_frame,text="Import")
    mode_notebook.add(download_frame,text="Download")
    mode_notebook.pack(expand=1,fill="both")

    logger_frame=ttk.Frame(root)
    logger_frame.pack(fill=Tk.X,expand=Tk.Y)
    ttk.Label(logger_frame,text="Log:").pack(side=Tk.LEFT)
    self.loggerLevel=ttk.Combobox(logger_frame,state="readonly",value=['debug','infomation','warning','error'])
    self.loggerLevel.bind("<<ComboboxSelected>>",self.change_log_level)
    self.loggerLevel.current(2)
    self.loggerLevel.pack(side=Tk.LEFT)
    log_frame=ttk.Frame(root)
    log_frame.pack(fill=Tk.X,expand=Tk.Y)
    logger=ScrolledText.ScrolledText(log_frame,state=Tk.DISABLED,height=5,)
    logger.pack(fill=Tk.BOTH,expand=Tk.Y,side=Tk.BOTTOM)
    tts.setLoggerConsole(logger)
    pref_frame=ttk.Frame(root)
    pref_frame.pack(fill=Tk.X,expand=Tk.Y)
    ttk.Button(pref_frame,text="Preferences",command=self.showPreferences).pack()

def main():
  root = Tk.Tk()
  root.wm_title("TTS Manager")
  tts_gui=TTS_GUI(root)
  root.mainloop()

if __name__ == "__main__":
  main()
