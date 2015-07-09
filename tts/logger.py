import logging
import tkinter

class TKHandler(logging.Handler):
  def __init__(self,console=None):
    logging.Handler.__init__(self)

    self.console = console # must be a text widget of some kind.

  def emit(self,message):
    formattedMessage = self.format(message)

    if self.console:
      self.console.configure(state=tkinter.NORMAL)
      self.console.insert(tkinter.END, formattedMessage)
      self.console.configure(state=tkinter.DISABLED)
      self.console.see(tkinter.END)
    print(formattedMessage)


_logger  = logging.getLogger("TTS Logger")
_handler = TKHandler()
_handler.setLevel(logging.DEBUG)
_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
_handler.setFormatter(_formatter)
_logger.addHandler(_handler)

def logger():
  return _logger

def setConsole(console):
  _handler.console=console

