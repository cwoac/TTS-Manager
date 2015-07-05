import tts
import tkinter as Tk
import tkinter.ttk as ttk
import tkinter.scrolledtext as ScrolledText
import os.path

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
    save=tts.Save(data)
    self.poll_command(save)



class TTS_GUI:
  def update_details(self,savedata):
    self.details_list.config(state=Tk.NORMAL)
    self.details_list.delete(1.0,Tk.END)
    self.details_list.insert(Tk.END,savedata)
    self.details_list.config(state=Tk.DISABLED)

  def populate_list(self,frame):
    self.sb=SaveBrowser(frame,self.update_details)
    self.file_list_current = None
    ttk.Label(frame,text="Details:").pack()
    self.details_list=ScrolledText.ScrolledText(master=frame,height=5)
    self.details_list.config(state=Tk.DISABLED)
    self.details_list.pack(fill=Tk.BOTH, expand=Tk.Y)
    self.sb.list_command()


  def __init__(self,root):
    self.root=root
    mode_notebook = ttk.Notebook(root)
    list_frame = ttk.Frame(mode_notebook)
    self.populate_list(list_frame)
    export_frame = ttk.Frame(mode_notebook)
    import_frame = ttk.Frame(mode_notebook)

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