import logging
import tkinter as Tk
import tkinter.ttk as ttk
import tkinter.scrolledtext as scrolledtext


class TTS_LOGGER:
  def __init__(self,root):
    self.log_window=Tk.Toplevel(root)
    self.log_window.protocol("WM_DELETE_WINDOW",self.log_window.withdraw)
    Tk.Grid.rowconfigure(self.log_window,0,weight=1)
    Tk.Grid.columnconfigure(self.log_window,0,weight=1)
    self.log_window.title("TTS Manager Log")
    frame=ttk.Frame(self.log_window)
    frame.grid(sticky=Tk.N+Tk.S+Tk.E+Tk.W)
    ttk.Label(frame,text="Log:").grid()
    self.log_window.withdraw()
    self.loggerLevel=ttk.Combobox(frame,state="readonly",value=['debug','infomation','warning','error'])
    self.loggerLevel.bind("<<ComboboxSelected>>",self.change_log_level)
    self.loggerLevel.current(2)
    self.loggerLevel.grid(row=0,column=1,sticky=Tk.W+Tk.E)
    logger=scrolledtext.ScrolledText(frame,state=Tk.DISABLED,height=5)
    logger.grid(row=1,columnspan=2,sticky=Tk.N+Tk.S+Tk.E+Tk.W)
    setLoggerConsole(logger)

    # Enable resizing
    for x in range(2):
      Tk.Grid.columnconfigure(frame,x,weight=1)
    Tk.Grid.rowconfigure(frame,1,weight=1)

  def toggle(self):
    if self.log_window.state()=="withdrawn":
      self.log_window.deiconify()
    else:
      self.log_window.withdraw()

  def change_log_level(self,event):
    levels=[logging.DEBUG,logging.INFO,logging.WARN,logging.ERROR]
    tts.logger().info("Setting log level to %s" % levels[self.loggerLevel.current()])
    tts.logger().setLevel(levels[self.loggerLevel.current()])


class TKHandler(logging.Handler):
  def __init__(self,console=None):
    logging.Handler.__init__(self)
    self.console = console # must be a text widget of some kind.

  def emit(self,message):
    formattedMessage = self.format(message)

    if self.console:
      self.console.configure(state=Tk.NORMAL)
      self.console.insert(Tk.END, formattedMessage+'\n')
      self.console.configure(state=Tk.DISABLED)
      self.console.see(Tk.END)
      self.console.update()
    print(formattedMessage)


_logger  = logging.getLogger("TTS Logger")
_handler = TKHandler()
_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
_handler.setFormatter(_formatter)
_logger.addHandler(_handler)
_handler.setLevel(logging.DEBUG)
_logger.setLevel(logging.DEBUG)

def logger():
  return _logger

def setLoggerConsole(console):
  _handler.console=console
