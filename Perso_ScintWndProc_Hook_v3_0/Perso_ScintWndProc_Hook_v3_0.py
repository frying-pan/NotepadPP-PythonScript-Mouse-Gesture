# PythonScript that hooks Notepad++ mouse clicks (WndProc HOOK on Scintilla windows)
# Tested with Notepad++ 7.8.2 64 bits, with PythonScript plugin 1.5.2
# on Windows 8.1 64 bits (NOT tested with Notepad++ 32 Bits but could be compatible)
# /!\ this file uses TABS for indent /!\ (better read as 4 chars wide tabs)

# features : add keyboard + mouse action to Notepad++ when the script is run from Notepad++ (with PythonScript plugin installed)
	# SHIFT + double-left-click			: select from clicked point/selection the whole variable name : alphanumeric with _ and . (dot)
	# CTRL + SHIFT + double-left-click	: select from clicked point/selection the whole bracket : () [] {}, from left in case of mismatch
	# ALT + SHIFT + double-left-click	: select from clicked point/selection the whole quote : "" '', from left in case of mismatch
	# ALT + right-click					: select from clicked point/selection until space/space-like chars are met : space/tab/cr/lf etc...
	# right-click						: prevent right-click from losing current text selection and moving the caret
# an already existing selection can also be expanded by executing one of those selection gesture inside it
# if feature *get_brackets* or *get_quotes* is disabled a second selection inside the selection will select them

# (i) successive double-clicks : for expanding the selection of [aa[XXX]bb] by successive CTRL + SHIFT + double-left-click on the XXX
# successive double-clicks can't be too close or they will be interpreted as triple-clicks(line selection) + one click by Notepad++
# the needed interval between two successive double-clicks seems to be linked to the system-wide double-click speed
# (set up within the Mouse applet from the Config Panel)

# re-run the script to de-activate/re-activate the whole hook (re-running the script will also apply new *options values*)
# change the *options values* (just below) to choose which mouse shortcuts will be enabled when the hook is active

# *options values* : set value to 1 to have the feature enabled (any OTHER value will DISABLE it)
i_feature_shift_double_left_click			= 1 # select word with _ and . (dot)
i_feature_control_shift_double_left_click	= 1 # select () [] {} content, possibly including the brackets (see i_feature_get_brackets)
i_feature_alt_shift_double_left_click		= 1 # select "" '' content, possibly including the quotes (see i_feature_get_quotes)
i_feature_alt_right_click					= 1 # select until space/space-like chars
i_feature_right_click						= 1 # right-click keeps current selection and caret position
i_feature_get_brackets						= 0 # also select surrounding brackets/quotes () [] {} with content at first click
i_feature_get_quotes						= 0 # also select surrounding brackets/quotes "" '' with content at first click
i_feature_copy_selection_to_clipboard		= 1 # copy any (non-empty) new selection to the clipboard
i_feature_copy_selection_to_console			= 1 # copy any (non-empty) new selection to the console
i_feature_msgbox							= 1	# if disabled, no message box will pop when toggling the hook,
												# or on registering hook error (console messages will still occur)
# end of *options values*

# general declarations *****************************************************************************
from Npp import *

import platform
import ctypes
from ctypes import wintypes
import time, datetime
from datetime import datetime

GWL_WNDPROC = -4				# used to set a new address for a window procedure
WM_NONE				= 0x0000	# null window message
WM_LBUTTONDOWN		= 0x0201	# mouse left-click-down window message
WM_LBUTTONDBLCLK	= 0x0203	# mouse double-left-click window message
WM_RBUTTONDOWN		= 0x0204	# mouse right-click down window message
WM_RBUTTONUP		= 0x0205	# mouse right-click up window message
I_VK_SHIFT		= 0x10			# SHIFT virtual key code
I_VK_CONTROL	= 0x11			# CONTROL virtual key code
I_VK_ALT		= 0x12			# ALT virtual key code
KSTATE_ISDOWN = 0x8000			# key pressed

LRESULT = wintypes.LPARAM
WndProcType = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

# window message hook functions
CallWindowProc = ctypes.windll.user32.CallWindowProcW
CallWindowProc.restype = LRESULT
CallWindowProc.argtypes = [WndProcType, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]

x86 = platform.architecture()[0] == "32bit"
if x86:
	SetWindowLong = ctypes.windll.user32.SetWindowLongW
else:
	SetWindowLong = ctypes.windll.user32.SetWindowLongPtrW
SetWindowLong.restype = WndProcType
SetWindowLong.argtypes = [wintypes.HWND, wintypes.INT, WndProcType]
# end of window message hook functions

GetDoubleClickTime	= ctypes.windll.user32.GetDoubleClickTime
GetAsyncKeyState	= ctypes.windll.user32.GetAsyncKeyState
SetLastError		= ctypes.windll.kernel32.SetLastError
GetLastError		= ctypes.windll.kernel32.GetLastError

# script declarations ******************************************************************************
from Perso__Lib_Window import C_Get_NPPScintilla_Wins
from Perso__Lib_Edit import C_Extend_Sel_From_Caret

s_script_name	= "Scintilla Mouse Gesture"
s_hook_name		= "Scint_Mouse_Click Hook"

s_reruntogglehook	= "Re-run the script to toggle the whole hook"
s_willapplynewopt	= "This will also apply new *options values* saved in the script file"
s_feature_disbyopt	= "* Feature DISABLED by script option : "

i_true	= 1
i_false	= 0

s_editorprop_prefix		= "SCINTWNDPROC_"
s_editorprop_hook_reg	= s_editorprop_prefix + "HOOK_REGISTERED"
s_editorprop_hook_on	= s_editorprop_prefix + "HOOK_ON"

t_features_key = ("SDLC", "CSDLC", "ASDLC", "ARC", "RC", "GBR", "GQT", "CLPCOPY", "CONCOPY", "MBOX")
t_feature_value = (
	i_feature_shift_double_left_click, i_feature_control_shift_double_left_click, i_feature_alt_shift_double_left_click, \
	i_feature_alt_right_click, i_feature_right_click, \
	i_feature_get_brackets, i_feature_get_quotes, \
	i_feature_copy_selection_to_clipboard, i_feature_copy_selection_to_console, \
	i_feature_msgbox)
t_feature_offdes = (
	"SHIFT + double-left-click", "CTRL + SHIFT + double-left-click", "ALT + SHIFT + double-left-click", \
	"ALT + right-click", "right-click", \
	"select surrounding brackets", "select surrounding quotes", \
	"copy selection to clipboard", "copy selection to console", \
	"message box warnings")
t_feature_initdes = (
	"SHIFT + double-left-click        : select the whole variable name : alphanumeric with _ and . (dot)", \
	"CTRL + SHIFT + double-left-click : select the whole bracket : () [] {}, from left in case of mismatch", \
	"ALT + SHIFT + double-left-click  : select the whole quote : " + chr(34) + chr(34) + " '', from left in case of mismatch", \
	"ALT + right-click                : select until space/space-like chars are met : space/tab/cr/lf etc...", \
	"right-click                      : right-click keeps current selection and caret position")

class C_Scint_Mouse_Click_Hook():
	# class constructor
	def __init__(self, s_script_name, s_hook_name, i_feature_on, s_editorprop_hook_on, dic_features):
		self.HookDone = False
		self.script_name	= s_script_name
		self.hook_name		= s_hook_name
		self.feature_on		= i_feature_on
		self.editorprop_hook_on	= s_editorprop_hook_on
		self.editorprop_sdlc_on =		dic_features["SDLC"]
		self.editorprop_csdlc_on =		dic_features["CSDLC"]
		self.editorprop_asdlc_on =		dic_features["ASDLC"]
		self.editorprop_arc_on =		dic_features["ARC"]
		self.editorprop_rc_on =			dic_features["RC"]
		self.editorprop_gbr_on =		dic_features["GBR"]
		self.editorprop_gqt_on =		dic_features["GQT"]
		self.editorprop_clpcopy_on =	dic_features["CLPCOPY"]
		self.editorprop_concopy_on =	dic_features["CONCOPY"]

		self.last_down_time = time.time()
		self.lastsel_start	= editor.getSelectionStart()
		self.lastsel_end	= editor.getSelectionEnd()

	# function to register the hook on all found Scintilla windows
	def RegHook(self):
		# our own WndProc function that receives hooked windows messages
		def HOOK_MyWndProc(hwnd, msg, wparam, lparam):
			f_s_dblclick_processing_bonus = float(0.1)

			oldwndproc = None
			for i in range(0, len(self.lst_scint_hwnd)):
				# target hwnd found at index i in lst_scint_hwnd
				if self.lst_scint_hwnd[i] == hwnd:
					# corresponding oldwndproc is picked in lst_scint_oldwndproc
					oldwndproc = self.lst_scint_oldwndproc[i]
					break
			if oldwndproc is None:															# FATAL ERROR ! you are doomed...
				print "\t" + self.hook_name + " Fatal error ! Hooked WndProc NOT found !"
				notepad.messageBox(self.hook_name + " Fatal error ! Hooked WndProc NOT found !", \
					self.script_name, MESSAGEBOXFLAGS.ICONEXCLAMATION)
				return 0

			if (msg != WM_LBUTTONDOWN and \
				msg != WM_LBUTTONDBLCLK and msg != WM_RBUTTONDOWN and msg != WM_RBUTTONUP):	# if NOT in mouse hooked messages : abort
				return CallWindowProc(oldwndproc, hwnd, msg, wparam, lparam)				# -> IMPORTANT pass other msg, otherwise will block NPP
			if console.editor.getProperty(self.editorprop_hook_on) != str(self.feature_on):	# if hook de-activated : abort
				return CallWindowProc(oldwndproc, hwnd, msg, wparam, lparam)				# -> IMPORTANT pass other msg, otherwise will block NPP

			# save selection before the first left-click down of a double-left-click loose it
			if msg == WM_LBUTTONDOWN:
				f_s_dblclick = (float(GetDoubleClickTime()) / float(1000)) + f_s_dblclick_processing_bonus
				cur_time = time.time()
				if (cur_time - self.last_down_time) > f_s_dblclick:
					self.lastsel_start	= editor.getSelectionStart()
					self.lastsel_end	= editor.getSelectionEnd()
				else:
					if (editor.getCurrentPos() < self.lastsel_start or editor.getCurrentPos() > self.lastsel_end):
						self.lastsel_start	= editor.getCurrentPos()
						self.lastsel_end	= editor.getCurrentPos()
				self.last_down_time = cur_time
				return CallWindowProc(oldwndproc, hwnd, msg, wparam, lparam)				# -> IMPORTANT pass other msg, otherwise will block NPP

			b_shift_down	= ((GetAsyncKeyState(I_VK_SHIFT)	& KSTATE_ISDOWN) == KSTATE_ISDOWN)
			b_ctrl_down		= ((GetAsyncKeyState(I_VK_CONTROL)	& KSTATE_ISDOWN) == KSTATE_ISDOWN)
			b_alt_down		= ((GetAsyncKeyState(I_VK_ALT)		& KSTATE_ISDOWN) == KSTATE_ISDOWN)

			b_clp_copy	= (console.editor.getProperty(self.editorprop_clpcopy_on) == str(self.feature_on))
			b_con_copy	= (console.editor.getProperty(self.editorprop_concopy_on) == str(self.feature_on))
			# select from clicked point the whole variable name
			if (msg == WM_LBUTTONDBLCLK and b_shift_down and not(b_ctrl_down) and not(b_alt_down) and \
					(console.editor.getProperty(self.editorprop_sdlc_on)	== str(self.feature_on))):
				self.o_extend_sel_from_caret.ExtendSel_AlphaNumUnderscoreDot( \
					self.lastsel_start, self.lastsel_end, b_clp_copy, b_con_copy)
			# select from clicked point the whole bracket [content]
			elif (msg == WM_LBUTTONDBLCLK and b_shift_down and b_ctrl_down and not(b_alt_down) and \
					(console.editor.getProperty(self.editorprop_csdlc_on)	== str(self.feature_on))):
				b_get_brackets = (console.editor.getProperty(self.editorprop_gbr_on) == str(self.feature_on))
				self.o_extend_sel_from_caret.ExtendSel_To_Brackets( \
					b_get_brackets, self.lastsel_start, self.lastsel_end, b_clp_copy, b_con_copy)
			# select from clicked point the whole quote [content]
			elif (msg == WM_LBUTTONDBLCLK and b_shift_down and not(b_ctrl_down) and b_alt_down and \
					(console.editor.getProperty(self.editorprop_asdlc_on)	== str(self.feature_on))):
				b_get_quotes = (console.editor.getProperty(self.editorprop_gqt_on) == str(self.feature_on))
				self.o_extend_sel_from_caret.ExtendSel_To_Quotes( \
					b_get_quotes, self.lastsel_start, self.lastsel_end, b_clp_copy, b_con_copy)
			# select from clicked point until space/space-like chars
			elif (msg == WM_RBUTTONUP and not(b_shift_down) and not(b_ctrl_down) and b_alt_down and \
					(console.editor.getProperty(self.editorprop_arc_on)		== str(self.feature_on))):
				self.o_extend_sel_from_caret.ExtendSel_To_SpacesSpacesLike( \
					editor.getSelectionStart(), editor.getSelectionEnd(), b_clp_copy, b_con_copy)
			# do nothing, keep the selection
			elif (msg == WM_RBUTTONDOWN and not(b_shift_down) and not(b_ctrl_down) and not(b_alt_down) and \
					(console.editor.getProperty(self.editorprop_rc_on)		== str(self.feature_on))):
				dummy = 0
			else:
				return CallWindowProc(oldwndproc, hwnd, msg, wparam, lparam)				# -> IMPORTANT pass other msg, otherwise will block NPP

			#s_debug = "DEBUG " + s_hook_name + " Message = " + hex(msg) + " to hwnd = " + hex(hwnd)
			#s_debug = s_debug + " Forwarded To oldwndproc = " + str(oldwndproc) + " At " + str(datetime.now())
			#print s_debug
			return CallWindowProc(oldwndproc, hwnd, WM_NONE, 0, 0)							# NULLIFY the mouse hooked messages

		if self.HookDone:
			return False

		self.lst_scint_hwnd = []
		self.lst_scint_oldwndproc = []

		o_get_nppscintilla_wins = C_Get_NPPScintilla_Wins()
		npp_win_hwnd, self.lst_scint_hwnd, s_npp_class, s_scint_class = o_get_nppscintilla_wins.GetWinsInfos()

		if npp_win_hwnd is None:
			print "\t" + s_npp_class + " window NOT found ! NO hook !"
			return False
		#print "\t" + s_npp_class + " Handle = " + hex(npp_win_hwnd)
		print "\t" + "Found " + str(len(self.lst_scint_hwnd)) + " " + s_scint_class + " Handle(s)"

		# get the address of our own WndProc
		self.newWndProc = WndProcType(HOOK_MyWndProc)

		# register the hook for each window present in lst_scint_hwnd
		s_errlist = ""
		i_index = 0
		while i_index < len(self.lst_scint_hwnd):
			win_hwnd = self.lst_scint_hwnd[i_index]
			# register hook and store oldwndproc addresses in lst_scint_oldwndproc
			SetLastError(0)
			oldwndproc = SetWindowLong(win_hwnd, GWL_WNDPROC, self.newWndProc)
			i_apierr = GetLastError()
			if i_apierr == 0:
				self.lst_scint_oldwndproc.append(oldwndproc)
				i_index = i_index + 1
			else:
				del self.lst_scint_hwnd[i_index]
				s_errlist = s_errlist + "\t\t" + hex(win_hwnd) + " / " + "NO WindowProc ! NOT hooked !" + "\n"
		if not(s_errlist == ""):
			s_errlist = s_errlist[:-1]
			print s_errlist
		if len(self.lst_scint_hwnd) == 0:
			print "\t" + s_scint_class + " window(s) or WindowProc(s) NOT found or NO hook !"
			return False

		self.o_extend_sel_from_caret = C_Extend_Sel_From_Caret()

		self.HookDone = True
		return True
# end of class

print "[" + s_script_name + " starts]"

s_disopt_info	= ""
s_initdes_info	= ""
dic_features = {}
for i in range(0, len(t_features_key)):
	console.editor.setProperty(s_editorprop_prefix + t_features_key[i], str(t_feature_value[i]))
	if str(t_feature_value[i]) != str(i_true): s_disopt_info = s_disopt_info + "\t" + s_feature_disbyopt + t_feature_offdes[i] + "\n"
	if i < len(t_feature_initdes): s_initdes_info = s_initdes_info + "\t\t" + t_feature_initdes[i] + "\n"
	dic_features[t_features_key[i]] = s_editorprop_prefix + t_features_key[i]
if not(s_initdes_info == ""): s_initdes_info = s_initdes_info[:-1]
if not(s_disopt_info == ""): s_disopt_info = s_disopt_info[:-1]

if console.editor.getProperty(s_editorprop_hook_reg) != str(i_true):
	# create an instance of the hook class, and populate object properties with variables which are also needed globally
	o_scint_mouse_click_hook = C_Scint_Mouse_Click_Hook(s_script_name, s_hook_name, i_true, s_editorprop_hook_on, dic_features)

	# register the hook on all found Scintilla windows
	b_reg = o_scint_mouse_click_hook.RegHook()
	if b_reg:
		console.editor.setProperty(s_editorprop_hook_reg, str(i_true))
		console.editor.setProperty(s_editorprop_hook_on, str(i_true))
		print "\t" + s_hook_name + " registered and activated (" + s_reruntogglehook + ". " + s_willapplynewopt + ")"
		print s_initdes_info
		if not(s_disopt_info == ""): print s_disopt_info
	else:
		print "\t" + s_hook_name + " registering failed"
		if str(i_feature_msgbox) == str(i_true):
			notepad.messageBox(s_hook_name + " registering failed", \
				s_script_name, MESSAGEBOXFLAGS.ICONSTOP)
else:
	if console.editor.getProperty(s_editorprop_hook_on) != str(i_true):
		console.editor.setProperty(s_editorprop_hook_on, str(i_true))
		print "\t" + s_hook_name + " re-activated (" + s_reruntogglehook + ". " + s_willapplynewopt + ")"
		if not(s_disopt_info == ""): print s_disopt_info
		if str(i_feature_msgbox) == str(i_true):
			notepad.messageBox( \
				s_hook_name + " re-activated" + "\n\n" + \
				s_reruntogglehook + "\n" + s_willapplynewopt + "\n\n" + \
				s_disopt_info.replace("\t", ""), \
				s_script_name, MESSAGEBOXFLAGS.ICONINFORMATION)
	else:
		console.editor.setProperty(s_editorprop_hook_on, str(i_false))
		print "\t" + s_hook_name + " DE-ACTIVATED /!\\ (" + s_reruntogglehook + ". " + s_willapplynewopt + ")"
		if not(s_disopt_info == ""): print s_disopt_info
		if str(i_feature_msgbox) == str(i_true):
			notepad.messageBox( \
				s_hook_name + " DE-ACTIVATED /!\\" + "\n\n" + \
				s_reruntogglehook + "\n" + s_willapplynewopt + "\n\n" + \
				s_disopt_info.replace("\t", ""), \
				s_script_name, MESSAGEBOXFLAGS.ICONEXCLAMATION)
