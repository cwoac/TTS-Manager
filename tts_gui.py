#!/usr/bin/env python27

import tts
import tts_cli
import Tkinter as Tk
import ttk
import ScrolledText
import tkFileDialog
import tkMessageBox
import os.path

class TTS_GUI:
  def list_command(self):
    data=None
    if self.isSaves.get():
      data=tts.describe_save_files()
    else:
      data=tts.describe_workshop_files()
    self.file_list.delete(0,Tk.END)
    for (name,number) in data:
      self.file_list.insert(Tk.END,"%s (%s)" % (name,number))

  def populate_list(self,frame):
    srcFrame=ttk.Frame(frame)
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
    listFrame=ttk.Frame(frame)
    listFrame.pack(expand=1,fill=Tk.BOTH)
    ttk.Label(listFrame,text="Files found:").pack()
    foundBar=ttk.Scrollbar(listFrame,orient=Tk.VERTICAL)
    self.file_list=Tk.Listbox(listFrame,yscrollcommand=foundBar.set)
    foundBar.config(command=self.file_list.yview)
    foundBar.pack(side=Tk.RIGHT,fill=Tk.Y)
    self.file_list.pack(side=Tk.LEFT,fill=Tk.BOTH,expand=1)
    #self.file_list=ScrolledText.ScrolledText(master=frame,height=5).pack(fill=Tk.BOTH, expand=Tk.Y)
    ttk.Label(frame,text="Details:").pack()
    self.details_list=ScrolledText.ScrolledText(master=frame,height=5).pack(fill=Tk.BOTH, expand=Tk.Y)
    self.list_command()

  def __init__(self,root):
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