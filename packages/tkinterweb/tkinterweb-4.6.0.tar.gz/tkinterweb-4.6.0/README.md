# TkinterWeb 
**A fast and lightweight web browser widget for Tkinter.**

## Overview
**TkinterWeb offers bindings and extensions to a modified version of the Tkhtml3 widget from [http://tkhtml.tcl.tk](https://web.archive.org/web/20250219233338/http://tkhtml.tcl.tk/), which enables enables the display of HTML and CSS code in Tkinter applications.** 

Some of TkinterWeb's uses include:

- Displaying websites, feeds, help files, and other styled HTML
- Displaying images, including SVG images
- Designing apps using HTML templates
- Creating prettier apps, with rounded buttons and more!

All major operating systems running Python 3.2+ are supported. 

## Usage
**TkinterWeb provides a web browser frame, a label widget capable of displaying styled HTML, and an HTML-based geometry manager.**

TkinterWeb can be used in any Tkinter application. Here is an example:
```
import tkinter as tk
from tkinterweb import HtmlFrame # import the HtmlFrame widget

root = tk.Tk() # create the Tkinter window
frame = HtmlFrame(root) # create the HTML widget
frame.load_website("http://tkhtml.tcl.tk/tkhtml.html") # load a website
frame.pack(fill="both", expand=True) # attach the HtmlFrame widget to the window
root.mainloop()
```
![Output](https://raw.githubusercontent.com/Andereoo/TkinterWeb/main/images/tkinterweb-tkhtml.png)

**Refer to the [GitHub home page](https://github.com/Andereoo/TkinterWeb) or the [Read the Docs home page](https://tkinterweb.readthedocs.io/en/latest/) for more information.**
