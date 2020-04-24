# NotepadPP-PythonScript-Mouse-Gesture

Add keyboard + mouse gestures to Notepad++ when the script is run from Notepad++ (with PythonScript plugin installed)

via a window procedure hook on Notepad++ Scintilla child windows

Tested with Notepad++ 7.8.2 64 bits, with PythonScript plugin 1.5.2

on Windows 8.1 64 bits (NOT tested with Notepad++ 32 Bits but could be compatible)

Features :
  * SHIFT + double-left-click        : select from clicked point the whole variable name : alphanumeric with _ and . (dot)
  * CTRL + SHIFT + double-left-click : select from clicked point the whole bracket content : () [] {}, from left in case of mismatch
  * ALT + SHIFT + double-left-click  : select from clicked point the whole quote content : "" '', from left in case of mismatch
  * ALT + right-click                : select from clicked point until space/space-like characters are met : space/tab/cr/lf/formfeed/vtab etc...
  * right-click                      : prevent right-click from moving the caret and losing current text selection

# Versions :

Perso_ScintWndProc_Hook.v1.py
is somewhat more tested.

Perso_ScintWndProc_Hook.v2.0.py
changes :
* code reorganized/cleaned
* more object oriented

This script can be run at Notepad++ startup :

* copy the .py script file in

C:\Users\[username]\AppData\Roaming\Notepad++\plugins\config\PythonScript\scripts

* add "import [py script file name without extension]"

to the startup.py file located, for me, under the Notepad++ install folder

C:\Program Files\Notepad++\plugins\PythonScript\scripts

(I think I had to take ownership of startup.py before being able to write into it)

