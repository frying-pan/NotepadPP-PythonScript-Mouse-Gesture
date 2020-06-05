# PythonScript that adds keyboard modifiers + mouse clicks for text selection (WndProc HOOK on Scintilla windows)

# Tested with Notepad++ 7.8.2 64 bits, on Windows 8.1 64 bits (NOT tested with Notepad++ 32 Bits but should be compatible)
# using PythonScript plugin 1.5.2 from https://github.com/bruderstein/PythonScript/releases/ (based on python 2.7)
# /!\ this file uses TABS for indent /!\ (better read as 4 chars wide tabs)

# features : add keyboard + mouse click to Notepad++ when the script is run from Notepad++ (with PythonScript plugin installed)
	# SHIFT + double-left-click			: select from clicked point/selection the whole word, with custom special characters
	# CTRL + SHIFT + double-left-click	: select from clicked point/selection the whole bracket : () [] {} <>, left-most pair in case of mismatch
	# ALT + SHIFT + double-left-click	: select from clicked point/selection the whole quote : "" '', left-most pair in case of mismatch
	# ALT + right-click					: select from clicked point/selection until space/space-like chars are met : space/tab/cr/lf etc...
	# right-click						: prevent right-click from losing current text selection and moving the cursor
# an already existing selection can also be expanded by executing one of those selection gesture inside it
# if option *get_brackets* or *get_quotes* is disabled a second selection inside the selection will however select them

# (i) successive double-clicks : when expanding the selection of [aa[XXX]bb] by successive CTRL + SHIFT + double-left-click on the XXX,
# successive double-clicks can't be too close or they will be interpreted as triple-clicks(line selection) + one click by Notepad++,
# the needed interval between two successive double-clicks seems to be linked to the system-wide double-click speed
# (set up within the Mouse applet from the Config Panel)

# re-run the script to de-activate/re-activate the whole hook (re-running the script will also apply new *options values*)
# change the *options values* (just below) to choose which mouse shortcuts will be enabled when the hook is active

# *options values* *********************************************************************************
# set options to INTEGER 1 to have them enabled (OTHER values will DISABLE them)
i_option_shift_double_left_click			= 1 # select word : alphanumeric with _ and custom special characters
i_option_control_shift_double_left_click	= 1 # select () [] {} <> content, possibly including the brackets (see i_option_get_brackets)
i_option_alt_shift_double_left_click		= 1 # select "" '' content, possibly including the quotes (see i_option_get_quotes)
i_option_alt_right_click					= 1 # select until space/space-like chars
i_option_right_click						= 1 # right-click keeps current selection and cursor position
i_option_angle							= 1 # also select <> angle brackets (in addition to () [] {})
i_option_get_brackets					= 0 # also select surrounding brackets () [] {} <> with content at first double-left-click
i_option_get_quotes						= 0 # also select surrounding quotes "" '' with content at first double-left-click
i_option_copy_selection_to_clipboard	= 0 # copy the new selection to the clipboard
i_option_copy_selection_to_console		= 1 # copy the new selection to the console
i_option_toggle_msgbox					= 1 # show a message box when toggling the hook (console messages always occur)
# set option to raw r-STRING (a single \ at the end would still need to be doubled \\)
s_option_word_special_chars = r"@.-" # add custom special characters for word selection (in addition to alphanumeric and _)

# script declarations ******************************************************************************
from Npp import *

s_script_name	= "Mouse Select Gesture"
s_hook_name		= "MouseGesture Hook"

s_controleditscript	= "(hold CTRL while starting the script to edit its options in Notepad++)"
s_reruntogglehook	= "Re-run the script to toggle the whole hook"
s_willapplynewopt	= "This will also apply new *options values* saved in the script file"
s_disabledopt		= "* DISABLED option : "

s_editorprop_prefix		= "SCINTWNDPROCHK_"
s_editorprop_hook_reg	= s_editorprop_prefix + "HOOK_REGISTERED"
s_editorprop_hook_on	= s_editorprop_prefix + "HOOK_ON"

t_option_key = ("SDLC", "CSDLC", "ASDLC", "ARC", "RC", "ANGLE", "GBR", "GQT", "CLPCOPY", "CONCOPY", "TOGMBOX", "WORDCHR")
s_option_word_special_chars = "".join(set(s_option_word_special_chars)) # remove duplicates
t_option_value = (
	i_option_shift_double_left_click, i_option_control_shift_double_left_click, i_option_alt_shift_double_left_click, \
	i_option_alt_right_click, i_option_right_click, \
	i_option_angle, i_option_get_brackets, i_option_get_quotes, \
	i_option_copy_selection_to_clipboard, i_option_copy_selection_to_console, \
	i_option_toggle_msgbox, s_option_word_special_chars)
t_option_offdes = (
	"SHIFT + double-left-click", "CTRL + SHIFT + double-left-click", "ALT + SHIFT + double-left-click", \
	"ALT + right-click", "right-click", \
	"select <> Brackets", "select surrounding brackets", "select surrounding quotes", \
	"copy selection to clipboard", "copy selection to console", \
	"toggle message box", "")
t_option_initdes = (
	"SHIFT + double-left-click        : select the whole word : alphanumeric with _ and " + s_option_word_special_chars, \
	"CTRL + SHIFT + double-left-click : select the whole bracket : () [] {} <>", \
	"ALT + SHIFT + double-left-click  : select the whole quote : " + chr(34) + chr(34) + " ''", \
	"ALT + right-click                : select until space/space-like chars are met : space/tab/cr/lf etc...", \
	"right-click                      : right-click keeps current selection and cursor position", \
	"", "", "", "", "", "", "")

i_true	= 1
i_false	= 0

class C_Scint_Mouse_Click_Hook():
	# class constructor
	def __init__(self, s_script_name, s_hook_name, i_option_on, s_editorprop_hook_on, dic_editorprop):
		import platform
		import ctypes
		from ctypes import wintypes
		import time
		self.time = time

		s_plat_arch_x86 = "32bit"
		self.GWL_WNDPROC = -4				# used to set a new address for a window procedure
		self.WM_NONE			= 0x0000	# null window message
		self.WM_LBUTTONDOWN		= 0x0201	# mouse left-click-down window message
		self.WM_LBUTTONDBLCLK	= 0x0203	# mouse double-left-click window message
		self.WM_RBUTTONDOWN		= 0x0204	# mouse right-click down window message
		self.WM_RBUTTONUP		= 0x0205	# mouse right-click up window message
		self.I_VK_SHIFT		= 0x10			# SHIFT virtual key code
		self.I_VK_CONTROL	= 0x11			# CONTROL virtual key code
		self.I_VK_ALT		= 0x12			# ALT virtual key code
		self.KSTATE_ISDOWN = 0x8000			# key pressed

		LRESULT = wintypes.LPARAM
		self.WndProcType = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

		# window message hook functions
		self.CallWindowProc = ctypes.windll.user32.CallWindowProcW
		self.CallWindowProc.restype = LRESULT
		self.CallWindowProc.argtypes = [self.WndProcType, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]

		b_x86 = (platform.architecture()[0].lower() == s_plat_arch_x86.lower())
		if b_x86:
			self.SetWindowLong = ctypes.windll.user32.SetWindowLongW
		else:
			self.SetWindowLong = ctypes.windll.user32.SetWindowLongPtrW
		self.SetWindowLong.restype = self.WndProcType
		self.SetWindowLong.argtypes = [wintypes.HWND, wintypes.INT, self.WndProcType]
		# end of window message hook functions

		self.GetDoubleClickTime	= ctypes.windll.user32.GetDoubleClickTime
		self.GetAsyncKeyState	= ctypes.windll.user32.GetAsyncKeyState
		self.SetLastError		= ctypes.windll.kernel32.SetLastError
		self.GetLastError		= ctypes.windll.kernel32.GetLastError

		from FP__Lib_Window	import C_Get_NPPScintilla_Wins
		from FP__Lib_Edit	import C_Extend_Sel_From_Caret
		self.o_get_nppscintilla_wins	= C_Get_NPPScintilla_Wins()
		self.o_extend_sel_from_caret	= C_Extend_Sel_From_Caret()

		# local const
		self.i_num_editor = 2 # required number of NPP views/editors window
		# script params
		self.script_name	= s_script_name
		self.hook_name		= s_hook_name
		self.option_on		= i_option_on
		self.editorprop_hook_on		= s_editorprop_hook_on
		self.editorprop_sdlc_on		= dic_editorprop["SDLC"]
		self.editorprop_csdlc_on	= dic_editorprop["CSDLC"]
		self.editorprop_asdlc_on	= dic_editorprop["ASDLC"]
		self.editorprop_arc_on		= dic_editorprop["ARC"]
		self.editorprop_rc_on		= dic_editorprop["RC"]
		self.editorprop_angle_on	= dic_editorprop["ANGLE"]
		self.editorprop_gbr_on		= dic_editorprop["GBR"]
		self.editorprop_gqt_on		= dic_editorprop["GQT"]
		self.editorprop_clpcopy_on	= dic_editorprop["CLPCOPY"]
		self.editorprop_concopy_on	= dic_editorprop["CONCOPY"]
		self.editorprop_wordchr		= dic_editorprop["WORDCHR"]
		# instance state datas
		self.hook_done		= False
		self.last_down_time	= time.time()
		self.lastsel_start	= 0
		self.lastsel_end	= 0

	# function to register the hook on Scintilla editors window
	def RegHook(self):
		# our own WndProc function that receives hooked windows messages
		def HOOK_MyWndProc(hwnd, msg, wparam, lparam):
			# window messages may be processed slower than actual double-left-click
			f_s_dblclick_processing_bonus = float(0.1)

			oldwndproc = None
			for i in range(0, len(self.lst_scint_hwnd)):
				# target hwnd found at index i in lst_scint_hwnd
				if self.lst_scint_hwnd[i] == hwnd:
					# corresponding oldwndproc is picked in lst_scint_oldwndproc
					oldwndproc = self.lst_scint_oldwndproc[i]
					break
			if oldwndproc is None:
				print "\t" + self.hook_name + " Fatal error ! Hooked WndProc NOT found !"
				notepad.messageBox(self.hook_name + " Fatal error ! Hooked WndProc NOT found !", \
					self.script_name, MESSAGEBOXFLAGS.ICONSTOP)
				return 0																	# -> FATAL ERROR ! you are f...ed...

			if (msg != self.WM_LBUTTONDOWN and msg != self.WM_LBUTTONDBLCLK and \
				msg != self.WM_RBUTTONDOWN and msg != self.WM_RBUTTONUP):					# if NOT in mouse hooked messages : abort
				return self.CallWindowProc(oldwndproc, hwnd, msg, wparam, lparam)			# -> IMPORTANT : pass msg, otherwise will block NPP
			if console.editor.getProperty(self.editorprop_hook_on) != str(self.option_on):	# if hook de-activated : abort
				return self.CallWindowProc(oldwndproc, hwnd, msg, wparam, lparam)			# -> IMPORTANT : pass msg, otherwise will block NPP

			# identify which editor will receive the click before it has been activated
			if hwnd == self.lst_scint_hwnd[0]:
				curedit = editor1
			elif hwnd == self.lst_scint_hwnd[1]:
				curedit = editor2
			else:																			# if NOT editor1 or editor2 : abort
				return self.CallWindowProc(oldwndproc, hwnd, msg, wparam, lparam)			# -> IMPORTANT : pass msg, otherwise will block NPP

			if msg == self.WM_LBUTTONDOWN:
				f_s_dblclick = (float(self.GetDoubleClickTime()) / float(1000)) + f_s_dblclick_processing_bonus
				cur_time = self.time.time()
				# save current selection before the first left-click down of a double-left-click loose this selection
				if ((cur_time - self.last_down_time) > f_s_dblclick):
					self.lastsel_start	= curedit.getSelectionStart()
					self.lastsel_end	= curedit.getSelectionEnd()
				# if second left-click down is out of the last selection, collapse this last selection to caret position
				elif (curedit.getCurrentPos() < self.lastsel_start or curedit.getCurrentPos() > self.lastsel_end):
					self.lastsel_start	= curedit.getCurrentPos()
					self.lastsel_end	= curedit.getCurrentPos()
				self.last_down_time = cur_time
				return self.CallWindowProc(oldwndproc, hwnd, msg, wparam, lparam)			# -> IMPORTANT : pass msg, otherwise will block NPP

			b_shift_down	= ((self.GetAsyncKeyState(self.I_VK_SHIFT)		& self.KSTATE_ISDOWN) == self.KSTATE_ISDOWN)
			b_ctrl_down		= ((self.GetAsyncKeyState(self.I_VK_CONTROL)	& self.KSTATE_ISDOWN) == self.KSTATE_ISDOWN)
			b_alt_down		= ((self.GetAsyncKeyState(self.I_VK_ALT)		& self.KSTATE_ISDOWN) == self.KSTATE_ISDOWN)

			b_clp_copy	= (console.editor.getProperty(self.editorprop_clpcopy_on) == str(self.option_on))
			b_con_copy	= (console.editor.getProperty(self.editorprop_concopy_on) == str(self.option_on))
			# select from clicked point the whole word
			if (msg == self.WM_LBUTTONDBLCLK and b_shift_down and not(b_ctrl_down) and not(b_alt_down) and \
					(console.editor.getProperty(self.editorprop_sdlc_on)	== str(self.option_on))):
				s_specchars = console.editor.getProperty(self.editorprop_wordchr)
				self.o_extend_sel_from_caret.ExtendSel_WordWSpecialChars( \
					curedit, self.lastsel_start, self.lastsel_end, s_specchars, b_clp_copy, b_con_copy)
			# select from clicked point the whole bracket [content]
			elif (msg == self.WM_LBUTTONDBLCLK and b_shift_down and b_ctrl_down and not(b_alt_down) and \
					(console.editor.getProperty(self.editorprop_csdlc_on)	== str(self.option_on))):
				b_angle			= (console.editor.getProperty(self.editorprop_angle_on)	== str(self.option_on))
				b_get_brackets	= (console.editor.getProperty(self.editorprop_gbr_on)	== str(self.option_on))
				self.o_extend_sel_from_caret.ExtendSel_To_Brackets( \
					curedit, self.lastsel_start, self.lastsel_end, b_angle, b_get_brackets, b_clp_copy, b_con_copy)
			# select from clicked point the whole quote [content]
			elif (msg == self.WM_LBUTTONDBLCLK and b_shift_down and not(b_ctrl_down) and b_alt_down and \
					(console.editor.getProperty(self.editorprop_asdlc_on)	== str(self.option_on))):
				b_get_quotes = (console.editor.getProperty(self.editorprop_gqt_on) == str(self.option_on))
				self.o_extend_sel_from_caret.ExtendSel_To_Quotes( \
					curedit, b_get_quotes, self.lastsel_start, self.lastsel_end, b_clp_copy, b_con_copy)
			# select from clicked point until space/space-like chars
			elif (msg == self.WM_RBUTTONUP and not(b_shift_down) and not(b_ctrl_down) and b_alt_down and \
					(console.editor.getProperty(self.editorprop_arc_on)		== str(self.option_on))):
				self.o_extend_sel_from_caret.ExtendSel_To_SpacesSpacesLike( \
					curedit, curedit.getSelectionStart(), curedit.getSelectionEnd(), b_clp_copy, b_con_copy)
			# do nothing, keep the selection
			elif (msg == self.WM_RBUTTONDOWN and not(b_shift_down) and not(b_ctrl_down) and not(b_alt_down) and \
					(console.editor.getProperty(self.editorprop_rc_on)		== str(self.option_on))):
				pass
			else:
				return self.CallWindowProc(oldwndproc, hwnd, msg, wparam, lparam)			# -> IMPORTANT : pass msg, otherwise will block NPP

			#s_debug = "DEBUG : " + s_hook_name + " got Msg = " + hex(msg) + ", to Hwnd = " + hex(hwnd)
			#s_debug = s_debug + ", oldWndProc = " + str(oldwndproc)
			#s_debug = s_debug + " (Edit1_Hwnd = " + hex(self.lst_scint_hwnd[0]) + ", Edit2_Hwnd = " + hex(self.lst_scint_hwnd[1]) + ")"
			#s_debug = s_debug + " At " + str(self.time.time())
			#print s_debug

			return self.CallWindowProc(oldwndproc, hwnd, self.WM_NONE, 0, 0)				# -> NULLIFY the mouse hooked messages
		# end of hook

		if self.hook_done:
			return False

		self.lst_scint_hwnd			= []
		self.lst_scint_oldwndproc	= []

		npp_win_hwnd, self.lst_scint_hwnd, s_npp_class, s_scint_class = self.o_get_nppscintilla_wins.GetWinsInfos(self.i_num_editor)

		if npp_win_hwnd is None:
			print "\t" + s_npp_class + " main window NOT found ! NO hook !"
			return False
		if len(self.lst_scint_hwnd) != self.i_num_editor:
			print "\t" + "Required " + self.i_num_editor + " " + s_scint_class + " editors window NOT found ! NO hook !"
			return False
		print "\t" + "Found " + str(len(self.lst_scint_hwnd)) + " " + s_scint_class + " editors window"

		# get the address of our own WndProc
		self.newWndProc = self.WndProcType(HOOK_MyWndProc)

		# register the hook for each window present in lst_scint_hwnd, number must be i_num_editor
		s_hookreport = ""
		i_index = 0
		while i_index < len(self.lst_scint_hwnd):
			win_hwnd = self.lst_scint_hwnd[i_index]
			# register hooks and store oldwndproc addresses in lst_scint_oldwndproc
			self.SetLastError(0)
			oldwndproc = self.SetWindowLong(win_hwnd, self.GWL_WNDPROC, self.newWndProc)
			i_apierr = self.GetLastError()
			if i_apierr == 0:
				self.lst_scint_oldwndproc.append(oldwndproc)
				#s_hookreport = s_hookreport + "\t\t" + "DEBUG : " + hex(win_hwnd) + " / " + str(oldwndproc) + " WindowProc OK" + "\n"
				i_index = i_index + 1
			else:
				del self.lst_scint_hwnd[i_index]
				s_hookreport = s_hookreport + "\t\t" + hex(win_hwnd) + " / " + "NO WindowProc ! NOT hooked !" + "\n"
		if s_hookreport != "":
			s_hookreport = s_hookreport[:-1]
			print s_hookreport
		if len(self.lst_scint_hwnd) != self.i_num_editor:
			for i in range(0, len(self.lst_scint_hwnd)):
				# un-register hooks that were successfull since the whole hook is canceled
				self.SetWindowLong(self.lst_scint_hwnd[i], self.GWL_WNDPROC, self.lst_scint_oldwndproc[i])
			print "\t" + "Required " + self.i_num_editor + " " + s_scint_class + " editors WindowProc NOT found ! NO hook !"
			return False

		self.hook_done = True
		return True
# end of class

# Main() code **************************************************************************************
def Main():
	print "[" + s_script_name + " starts] " + s_controleditscript

	s_disopt_info	= ""
	s_initdes_info	= ""
	dic_editorprop = {}
	for i in range(0, len(t_option_key)):
		console.editor.setProperty(s_editorprop_prefix + t_option_key[i], str(t_option_value[i]))
		if (t_option_offdes[i] != "" and str(t_option_value[i]) != str(i_true)):
			s_disopt_info = s_disopt_info + "\t" + s_disabledopt + t_option_offdes[i] + "\n"
		if t_option_initdes[i] != "": s_initdes_info = s_initdes_info + "\t\t" + t_option_initdes[i] + "\n"
		dic_editorprop[t_option_key[i]] = s_editorprop_prefix + t_option_key[i]
	if s_initdes_info != "": s_initdes_info = s_initdes_info[:-1]
	if s_disopt_info != "": s_disopt_info = s_disopt_info[:-1]

	if console.editor.getProperty(s_editorprop_hook_reg) != str(i_true):
		# create an instance of the hook class, and populate object properties with script and Console variables
		o_scint_mouse_click_hook = C_Scint_Mouse_Click_Hook(s_script_name, s_hook_name, i_true, s_editorprop_hook_on, dic_editorprop)

		# register the hook on Scintilla editors window
		b_reg = o_scint_mouse_click_hook.RegHook()
		if not(b_reg):
			console.writeError("\t" + s_hook_name + " registering FAILED /!\\" + "\n")
			console.show()
			notepad.messageBox(s_hook_name + " registering FAILED /!\\", s_script_name, MESSAGEBOXFLAGS.ICONSTOP)
		else:
			console.editor.setProperty(s_editorprop_hook_reg, str(i_true))
			console.editor.setProperty(s_editorprop_hook_on, str(i_true))
			print "\t" + s_hook_name + " registered and activated (" + s_reruntogglehook + ". " + s_willapplynewopt + ")"
			print s_initdes_info
			if s_disopt_info != "": print s_disopt_info
		return

	if console.editor.getProperty(s_editorprop_hook_on) != str(i_true):
		console.editor.setProperty(s_editorprop_hook_on, str(i_true))
		print "\t" + s_hook_name + " re-activated (" + s_reruntogglehook + ". " + s_willapplynewopt + ")"
		if s_disopt_info != "": print s_disopt_info
		if str(i_option_toggle_msgbox) == str(i_true):
			notepad.messageBox( \
				s_hook_name + " re-activated" + "\n\n" + \
				s_reruntogglehook + "\n" + s_willapplynewopt + "\n\n" + \
				s_disopt_info.replace("\t", "") + "\n\n" + \
				s_controleditscript, \
				s_script_name, MESSAGEBOXFLAGS.ICONINFORMATION)
	else:
		console.editor.setProperty(s_editorprop_hook_on, str(i_false))
		print "\t" + s_hook_name + " DE-ACTIVATED /!\\ (" + s_reruntogglehook + ". " + s_willapplynewopt + ")"
		if s_disopt_info != "": print s_disopt_info
		if str(i_option_toggle_msgbox) == str(i_true):
			notepad.messageBox( \
				s_hook_name + " DE-ACTIVATED /!\\" + "\n\n" + \
				s_reruntogglehook + "\n" + s_willapplynewopt + "\n\n" + \
				s_disopt_info.replace("\t", "") + "\n\n" + \
				s_controleditscript, \
				s_script_name, MESSAGEBOXFLAGS.ICONEXCLAMATION)

Main()
