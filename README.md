# Mouse_Select_Gesture

PythonScript that adds keyboard modifiers + mouse clicks for text selection (WndProc HOOK on Scintilla windows).

Tested with Notepad++ 7.8.2 64 bits, on Windows 8.1 64 bits (NOT tested with Notepad++ 32 Bits but should be compatible)

using PythonScript plugin 1.5.2 from https://github.com/bruderstein/PythonScript/releases/ (based on python 2.7).


Features :
  * CTRL + SHIFT + double-left-click	: select from clicked point/sel. the bracket content : () [] {} + <>, left-most pair in case of mismatch
  * ALT  + SHIFT + double-left-click	: select from clicked point/sel. the quote content : "" '', left-most pair in case of mismatch
  * CTRL + right-click				: select from clicked point/sel. the whole word, with custom special characters
  * ALT  + right-click				: select from clicked point/sel. until space/space-like chars are met : space/tab/cr/lf etc...
  * [same modifiers] + middle-click	: same actions as above (can, as an option, move the caret)
  * [NO modifier] + right-click		: prevent simple right-click from losing current text selection and moving the caret
  * optional auto-copy new selection to clipboard and/or console



# Install :

This script can be run at Notepad++ startup (folders below are those of a local installation) : 

* copy the main FP_MouseSelectGest_Hook .py script file (and starting from v3_0 the needed libraries files) in :

C:\Users\[username]\AppData\Roaming\Notepad++\plugins\config\PythonScript\scripts

* add "import [FP_MouseSelectGest_Hook (py) script file name without extension]"

to the startup.py file located, for me, under the Notepad++ install folder :

C:\Program Files\Notepad++\plugins\PythonScript\scripts

(I think I had to take ownership of startup.py before being able to write into it)


# Versions :

FP_MouseSelectGest_Hook_v1_0.py, (updated to FP_MouseSelectGest_Hook_v1_1.py for a small bug)

FP_MouseSelectGest_Hook_v2_0.py, (updated to FP_MouseSelectGest_Hook_v2_1.py for the same small bug as v1_0)
changes :
  * code reorganized/cleaned
  * more object oriented

FP_MouseSelectGest_Hook_v3_0.py
changes :
  * now requires the two libraries : FP__Lib_Edit.py, FP__Lib_Window.py included in the same folder
  * new option to select brackets, quotes with content
  * new option to auto-copy selection to clipboard, console
  * capability to expand selection from a previous selection
  * code reorganized/cleaned/optimized

FP_MouseSelectGest_Hook_v3_1.py
changes :
  * better handling of both Notepad++ views
  * should only hook the 2 required Scintilla editors window
  * code optimization

FP_MouseSelectGest_Hook_v3_2.py
changes :
  * minor update

FP_MouseSelectGest_Hook_v3_3.py
changes :
  * script name changed from Perso_ScintWndProc_Hook to FP_MouseSelectGest_Hook for easier identification
  * follow Scintilla bracket matching rule
  * custom special characters for word selection

FP_MouseSelectGest_Hook_v3_4.py
changes :
  * added <> angle brackets highlight as an option

FP_MouseSelectGest_Hook_v3_5.py
changes :
  * changed keyboard + right-click combos : word selection, and selection until space/space-like chars are met
  * added option : only select <> angle brackets when they are on the same line

FP_MouseSelectGest_Hook_v4_0.py
changes :
  * debugged and hardened editors window detection
  * added feature : middle-click alternative to the double-click and right-click shortcuts

FP_MouseSelectGest_Hook_v4_1.py
changes :
  * quotes "" '' content selection now requires that both quotes and their content have the same style
