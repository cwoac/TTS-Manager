import tts
import tkinter as Tk
import tkinter.ttk as ttk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import tkinter.scrolledtext as ScrolledText
import os.path
import zipfile

class SaveBrowser():
  def __init__(self,master,poll_command):
    self.master=master
    srcFrame=ttk.Frame(master)
    srcFrame.pack()
    ttk.Label(srcFrame,text="Select list source:").pack()
    self.isSaves=Tk.BooleanVar()
    ttk.Radiobutton(srcFrame,
                   text="Workshop",
                   variable=self.isSaves,
                   value=False,
                   command=self.list_command).pack(side=Tk.LEFT)
    ttk.Radiobutton(srcFrame,
                   text="Save",
                   variable=self.isSaves,
                   value=True,
                   command=self.list_command).pack(side=Tk.LEFT)
    scrollFrame=ttk.Frame(master)
    scrollFrame.pack(expand=1,fill=Tk.BOTH)
    ttk.Label(scrollFrame,text="Files found:").pack()
    foundBar=ttk.Scrollbar(scrollFrame,orient=Tk.VERTICAL)
    self.file_list=Tk.Listbox(scrollFrame,yscrollcommand=foundBar.set)
    foundBar.config(command=self.file_list.yview)
    foundBar.pack(side=Tk.RIGHT,fill=Tk.Y)
    self.file_list.pack(side=Tk.LEFT,fill=Tk.BOTH,expand=1)
    self.poll_command=poll_command
    self.file_list_current = None
    self.poll_file_list()

  def list_command(self):
    """ Populates the list box"""
    data=None
    if self.isSaves.get():
      data=tts.describe_save_files()
    else:
      data=tts.describe_workshop_files()
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
    data=None
    if self.isSaves.get():
      data=tts.load_save_file(ident)
    else:
      data=tts.load_workshop_file(ident)
    # TODO: error handling
    save=tts.Save(data,ident,not self.isSaves.get())
    self.poll_command(save)


class TTS_GUI:
  def update_list_frame_details(self,savedata):
    self.details_list.config(state=Tk.NORMAL)
    self.details_list.delete(1.0,Tk.END)
    self.details_list.insert(Tk.END,savedata)
    self.details_list.config(state=Tk.DISABLED)

  def populate_list_frame(self,frame):
    self.list_sb=SaveBrowser(frame,self.update_list_frame_details)
    ttk.Label(frame,text="Details:").pack()
    self.details_list=ScrolledText.ScrolledText(master=frame,height=5)
    self.details_list.config(state=Tk.DISABLED)
    self.details_list.pack(fill=Tk.BOTH, expand=Tk.Y)
    self.list_sb.list_command()

  def update_export_frame_details(self,savedata):
    if savedata.isInstalled:
      self.statusLabel.config(text="All cache files found. OK to export.")
      self.exportButton.config(state=Tk.NORMAL)
      self.targetEntry.delete(0,Tk.END)
      self.export_filename=os.path.join(os.path.expanduser("~"),"Downloads",savedata.ident+'.pak')
      self.targetEntry.insert(0,self.export_filename)
      self.export_savedata=savedata
    else:
      self.statusLabel.config(text="Some cache files missing - check details on list page.")
      self.exportButton.config(state=Tk.DISABLED)
      self.export_filename=None
      self.targetEntry.delete(0,Tk.END)
      self.export_savedata=None

  def pickExportTarget(self):
    self.export_filename = filedialog.asksaveasfilename(
      parent=self.root,
      initialdir=os.path.join(os.path.expanduser("~"),"Downloads"),
      filetypes=[('PAK files','*.pak')],
      defaultextension='pak',
      title='Choose export target')
    self.targetEntry.delete(0,Tk.END)
    self.targetEntry.insert(0,self.export_filename)

  def export(self):
    with zipfile.ZipFile(self.export_filename,'w') as zf:
      if self.export_savedata.isWorkshop:
        savefile=tts.get_workshop_filename(self.export_savedata.ident)
        zf.write(savefile,os.path.join("Mods","Workshop",os.path.basename(savefile)))
      else:
        savefile=tts.get_save_filename(self.export_savedata.ident)
        zf.write(savefile,os.path.join("Saves",os.path.basename(savefile)))
      for url in self.export_savedata.models:
        zf.write(url.location,os.path.join("Mods","Models",os.path.basename(url.location)))
      for url in self.export_savedata.images:
        zf.write(url.location,os.path.join("Mods","Images",os.path.basename(url.location)))
    # TODO: Error handling.
    messagebox.showinfo("TTS Manager","Export Done.")

  def populate_export_frame(self,frame):
    self.export_sb=SaveBrowser(frame,self.update_export_frame_details)
    targetFrame=ttk.Frame(frame)
    targetFrame.pack(expand=1,fill="both")
    ttk.Label(targetFrame,text="Select output file").pack()
    self.targetEntry=ttk.Entry(targetFrame)
    self.targetEntry.pack(side=Tk.LEFT,expand=Tk.Y,fill=Tk.X)
    targetButton=ttk.Button(targetFrame,text="Browse",command=self.pickExportTarget).pack(side=Tk.LEFT)

    exportFrame=ttk.Frame(frame)
    exportFrame.pack(expand=Tk.Y,fill=Tk.BOTH)
    self.export_filename=None
    self.export_savedata=None
    self.statusLabel=ttk.Label(exportFrame,text="")
    self.statusLabel.pack()
    self.exportButton=ttk.Button(exportFrame,text="Export",command=self.export,state=Tk.DISABLED)
    self.exportButton.pack()

    self.export_sb.list_command()


  def populate_import_frame(self,frame):
    pass


  def __init__(self,root):
    self.root=root
    mode_notebook = ttk.Notebook(root)
    list_frame = ttk.Frame(mode_notebook)
    self.populate_list_frame(list_frame)
    export_frame = ttk.Frame(mode_notebook)
    self.populate_export_frame(export_frame)
    import_frame = ttk.Frame(mode_notebook)
    self.populate_import_frame(import_frame)

    mode_notebook.add(list_frame,text="List")
    mode_notebook.add(export_frame,text="Export")
    mode_notebook.add(import_frame,text="Import")
    mode_notebook.pack(expand=1,fill="both")

def main():
  root = Tk.Tk()
  root.wm_title("TTS Manager")
  tts_gui=TTS_GUI(root)
  root.mainloop()

if __name__ == "__main__":
  main()