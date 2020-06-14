# PythonScript that adds keyboard modifiers + mouse clicks for text selection (WndProc HOOK on Scintilla windows)

# Tested with Notepad++ 7.8.2 64 bits, on Windows 8.1 64 bits (NOT tested with Notepad++ 32 Bits but should be compatible)
# using PythonScript plugin 1.5.2 from https://github.com/bruderstein/PythonScript/releases/ (based on python 2.7)
# /!\ this file uses TABS for indent /!\ (better read as 4 chars wide tabs)
# check update at https://github.com/frying-pan

# features : add keyboard + mouse click to Notepad++ when the script is run from Notepad++ (with PythonScript plugin installed)
	# CTRL + SHIFT + double-left-click	: select from clicked point/sel. the bracket content : () [] {} + <>, left-most pair in case of mismatch
	# ALT  + SHIFT + double-left-click	: select from clicked point/sel. the quote content : "" '', left-most pair in case of mismatch
	# CTRL + right-click				: select from clicked point/sel. the whole word, with custom special characters
	# ALT  + right-click				: select from clicked point/sel. until space/space-like chars are met : space/tab/cr/lf etc...
	# [same modifiers] + middle-click	: same actions as above (can, as an option, move the caret)
	# [NO modifier] + right-click		: prevent simple right-click from losing current text selection and moving the caret
	# optional auto-copy new selection to clipboard and/or console
# an already existing selection can also be expanded by executing one of those selection gestures inside it
# if option 'get_brackets' or 'get_quotes' is disabled a second selection inside the selection will however select them

# (i) successive double-clicks : when expanding the selection of [aa[XXX]bb] by successive CTRL + SHIFT + double-left-click on the XXX,
# successive double-clicks can't be too close or they will be interpreted as triple-clicks(line selection) + one click by Notepad++,
# the needed interval between two successive double-clicks may be linked to the system-wide double-click speed
# (set up within the Mouse applet from the Config Panel)

# re-run the script to de-activate/re-activate the whole hook (re-running the script will also apply new *options values*)
# change the *options values* (just below) to choose which mouse shortcuts will be enabled when the hook is active

# *options values* *********************************************************************************
# set to INTEGER 1 to enable an option (OTHER values will DISABLE it)
# selection type
i_option_control_shift_double_left_click	= 1 # select () [] {} + <> content, possibly including the brackets (see i_option_get_brackets)
i_option_control_shift_middle_click			= 1 # same as previous
i_option_alt_shift_double_left_click		= 1 # select "" '' content, possibly including the quotes (see i_option_get_quotes)
i_option_alt_shift_middle_click				= 1 # same as previous
i_option_control_right_click				= 1 # select word : alphanumeric with _ and custom special characters
i_option_control_middle_click				= 1 # same as previous
i_option_alt_right_click					= 1 # select until space/space-like chars
i_option_alt_middle_click					= 1 # same as previous
# click moves/keeps caret
i_option_middle_click_move_caret	= 0 # [modifier] + middle-click MOVES the caret
i_option_right_click_keep_selection	= 1 # [NO modifier] + right-click KEEPS current selection and caret position
# miscellaneous options
i_option_angle							= 1 # also select <> angle brackets content (in addition to () [] {})
i_option_single_line_angle				= 1 # only select <> angle brackets content when both are on the same line
i_option_get_brackets					= 0 # also select surrounding brackets () [] {} + <> with content at first double-left/middle-click
i_option_get_quotes						= 0 # also select surrounding quotes "" '' with content at first double-left/middle-click
i_option_copy_selection_to_clipboard	= 0 # copy the selection done by the mouse gesture to the clipboard
i_option_copy_selection_to_console		= 1 # copy the selection done by the mouse gesture to the console
i_option_toggle_msgbox					= 1 # show a message box when toggling the hook (console messages always occur)
# set option to raw r-STRING (a single \ at the end would still need to be doubled \\, " could be added after the r-string with : + chr(34))
s_option_word_special_chars = r"@.-"		# add custom special characters for word selection (in addition to alphanumeric and _)

# script declarations ******************************************************************************
from Npp import *

s_script_name	= "Mouse Select Gesture"
s_hook_name		= "MouseGesture Hook"

s_controleditscript	= "(hold CTRL while starting the script to edit its options in Notepad++)"
s_reruntogglehook	= "Re-run the script to toggle the whole hook"
s_willapplynewopt	= "This will also apply new *options values* saved in the script file"

s_editorprop_prefix		= "SCINTWNDPROCHK_"
s_editorprop_hook_reg	= s_editorprop_prefix + "HOOK_REGISTERED"
s_editorprop_hook_on	= s_editorprop_prefix + "HOOK_ON"

i_true	= 1
i_false	= 0

s_option_word_special_chars = "".join(set(s_option_word_special_chars)) # remove duplicates
s_opt_info_wordchr	= " and '" + s_option_word_special_chars + "'" if s_option_word_special_chars != "" else ""
s_opt_info_angle	= ""
if str(i_option_angle) == str(i_true):
	s_opt_info_angle = s_opt_info_angle + " <>"
	if str(i_option_single_line_angle) == str(i_true):
		s_opt_info_angle = s_opt_info_angle + " (single line <>)"
	else:
		s_opt_info_angle = s_opt_info_angle + " (multi-line <>)"

t_option_key = ("CSDLC", "CSMC", "ASDLC", "ASMC", "CRC", "CMC", "ARC", "AMC", "MC_MOVE", "RC_KEEP", \
	"ANGLE", "SL_ANGLE", "GET_BR", "GET_QT", "CLPCOPY", "CONCOPY", "TOGMBOX", "WORDCHR")
t_option_value = (
	i_option_control_shift_double_left_click, i_option_control_shift_middle_click, \
	i_option_alt_shift_double_left_click, i_option_alt_shift_middle_click, \
	i_option_control_right_click, i_option_control_middle_click, i_option_alt_right_click, i_option_alt_middle_click, \
	i_option_middle_click_move_caret, i_option_right_click_keep_selection, \
	i_option_angle, i_option_single_line_angle, i_option_get_brackets, i_option_get_quotes, \
	i_option_copy_selection_to_clipboard, i_option_copy_selection_to_console, \
	i_option_toggle_msgbox, s_option_word_special_chars)
t_option_initdes = (
	"", "", "", "", "", "", "", "", "", "", \
	"<> Brackets", "Single Line <>", "also select the brackets", "also select the quotes", \
	"copy sel. to clipboard", "copy sel. to console", "toggle message box", "word chars")
t_option_verbdes = (
	"CTRL + SHIFT + double-left-click"	+ "\t"			+ ": select the bracket content : () [] {}" + s_opt_info_angle, \
	"CTRL + SHIFT + middle-click"		+ "\t\t"		+ ": same as previous", \
	"ALT  + SHIFT + double-left-click"	+ "\t"			+ ": select the quote content : " + chr(34) + chr(34) + " ''", \
	"ALT  + SHIFT + middle-click"		+ "\t\t"		+ ": same as previous", \
	"CTRL + right-click"				+ "\t\t\t\t"	+ ": select the whole word : alphanumeric with '_'" + s_opt_info_wordchr, \
	"CTRL + middle-click"				+ "\t\t\t\t"	+ ": same as previous", \
	"ALT  + right-click"				+ "\t\t\t\t"	+ ": select until space/space-like chars are met : space/tab/cr/lf etc...", \
	"ALT  + middle-click"				+ "\t\t\t\t"	+ ": same as previous", \
	"[modifier] + middle-click"			+ "\t" + ": moves the caret", \
	"[NO modifier] + right-click"		+ "\t" + ": keeps current selection and caret position", \
	"", "", "", "", "", "", "", "")

class C_Scint_Mouse_Click_Hook():
	# class constructor
	def __init__(self, s_script_name, s_hook_name, i_option_on, s_editorprop_hook_on, dic_editorprop):
		import platform
		import ctypes
		from ctypes import wintypes
		import time, re
		self.ctypes	= ctypes
		self.time	= time
		self.re		= re

		s_plat_arch_x86 = "32bit"
		self.I_VK_SHIFT		= 0x10	# virtual key code SHIFT
		self.I_VK_CONTROL	= 0x11	# virtual key code CONTROL
		self.I_VK_ALT		= 0x12	# virtual key code ALT
		self.KSTATE_ISDOWN = 0x8000	# key is pressed
		self.GWL_WNDPROC = -4 # used to set a new address for a window procedure
		self.WM_NONE			= 0x0000	# null window message
		self.WM_LBUTTONDOWN		= 0x0201	# mouse left-click down
		# WM_LBUTTONUP			= 0x0202	# mouse left-click up
		self.WM_LBUTTONDBLCLK	= 0x0203	# mouse left-click doubled (second down)
		self.WM_RBUTTONDOWN		= 0x0204	# mouse right-click down
		self.WM_RBUTTONUP		= 0x0205	# mouse right-click up
		# WM_RBUTTONDBLCLK		= 0x0206	# mouse right-click doubled (second down)
		# WM_MBUTTONDOWN		= 0x0207	# mouse middle-click down
		self.WM_MBUTTONUP		= 0x0208	# mouse middle-click up
		# WM_MBUTTONDBLCLK		= 0x0209	# mouse middle-click doubled (second down)

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

		# custom object import
		from FP__Lib_Edit	import C_Extend_Sel_From_Sel
		from FP__Lib_Window	import C_Get_NPPScintilla_Wins
		self.o_extend_sel_from_sel		= C_Extend_Sel_From_Sel()
		self.o_get_nppscintilla_wins	= C_Get_NPPScintilla_Wins()

		# class const
		self.i_num_editor = 2 # required number of NPP views/editors window
		# script params
		self.script_name	= s_script_name
		self.hook_name		= s_hook_name
		self.option_on		= i_option_on
		self.editorprop_hook_on		= s_editorprop_hook_on
		self.editorprop_csdlc_on	= dic_editorprop["CSDLC"]
		self.editorprop_csmc_on		= dic_editorprop["CSMC"]
		self.editorprop_asdlc_on	= dic_editorprop["ASDLC"]
		self.editorprop_asmc_on		= dic_editorprop["ASMC"]
		self.editorprop_crc_on		= dic_editorprop["CRC"]
		self.editorprop_cmc_on		= dic_editorprop["CMC"]
		self.editorprop_arc_on		= dic_editorprop["ARC"]
		self.editorprop_amc_on		= dic_editorprop["AMC"]
		self.editorprop_mc_move_on	= dic_editorprop["MC_MOVE"]
		self.editorprop_rc_keep_on	= dic_editorprop["RC_KEEP"]
		self.editorprop_angle_on	= dic_editorprop["ANGLE"]
		self.editorprop_sl_angle_on	= dic_editorprop["SL_ANGLE"]
		self.editorprop_get_br_on	= dic_editorprop["GET_BR"]
		self.editorprop_get_qt_on	= dic_editorprop["GET_QT"]
		self.editorprop_clpcopy_on	= dic_editorprop["CLPCOPY"]
		self.editorprop_concopy_on	= dic_editorprop["CONCOPY"]
		self.editorprop_wordchars	= dic_editorprop["WORDCHR"]
		# instance state datas
		self.hook_done		= False
		self.fatalerror		= False
		self.last_down_time	= time.time()
		self.lastsel_start	= 0
		self.lastsel_end	= 0

	# function to register the hook on Scintilla editors window
	def RegHook(self):
		# our own WndProc function that receives hooked windows messages
		def _HOOK_MyWndProc(hwnd, msg, wparam, lparam):
			def _Set_Middle_Click_Sel(lparam, b_move):
					i_sel_start	= curedit.getSelectionStart()
					i_sel_end	= curedit.getSelectionEnd()
					if b_move:
						x = self.ctypes.c_int16(lparam	& 0x000000000000FFFF).value			# same for 32 and 64 bits
						y = self.ctypes.c_int16((lparam	& 0x00000000FFFF0000) >> 16).value	# same for 32 and 64 bits
						i_pos = curedit.positionFromPoint(x, y) # lparam and positionFromPoint are client coordinates
						if (i_pos < i_sel_start or i_pos > i_sel_end):
							i_sel_start					= i_pos
							i_sel_end					= i_pos
							editor.setSelectionStart	= i_pos
							editor.setSelectionEnd		= i_pos
					return (i_sel_start, i_sel_end)

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
				if not(self.fatalerror):
					self.fatalerror = True
					console.writeError(self.hook_name + " Fatal error ! Hooked WndProc NOT found !")
					console.show()
					notepad.messageBox(self.hook_name + " Fatal error ! Hooked WndProc NOT found !", \
						self.script_name, MESSAGEBOXFLAGS.ICONSTOP)
				return 0																	# -> FATAL ERROR ! you are f...ed...

			if (msg != self.WM_LBUTTONDOWN and msg != self.WM_LBUTTONDBLCLK and \
				msg != self.WM_MBUTTONUP and \
				msg != self.WM_RBUTTONDOWN and msg != self.WM_RBUTTONUP):					# if NOT a hooked mouse click : abort
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

			# double-click timing hack
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
			if (b_shift_down or b_ctrl_down or b_alt_down):
				b_clp_copy	= (console.editor.getProperty(self.editorprop_clpcopy_on) == str(self.option_on))
				b_con_copy	= (console.editor.getProperty(self.editorprop_concopy_on) == str(self.option_on))

			# select the bracket content (uses double-click hack)
			if (b_shift_down and b_ctrl_down and not(b_alt_down) and ( \
					(msg == self.WM_LBUTTONDBLCLK	and console.editor.getProperty(self.editorprop_csdlc_on)	== str(self.option_on)) or \
					(msg == self.WM_MBUTTONUP		and console.editor.getProperty(self.editorprop_csmc_on)		== str(self.option_on)))):
				if msg == self.WM_MBUTTONUP:
					b_move = (console.editor.getProperty(self.editorprop_mc_move_on) == str(self.option_on))
					i_sel_start, i_sel_end = _Set_Middle_Click_Sel(lparam, b_move)
				else:
					i_sel_start	= self.lastsel_start
					i_sel_end	= self.lastsel_end
				b_angle			= (console.editor.getProperty(self.editorprop_angle_on)		== str(self.option_on))
				b_sl_angle		= (console.editor.getProperty(self.editorprop_sl_angle_on)	== str(self.option_on))
				b_get_brackets	= (console.editor.getProperty(self.editorprop_get_br_on)	== str(self.option_on))
				self.o_extend_sel_from_sel.ExtendSel_To_Brackets( \
					curedit, i_sel_start, i_sel_end, b_angle, b_sl_angle, b_get_brackets, b_clp_copy, b_con_copy)
			# select the quote content (uses double-click hack)
			elif (b_shift_down and not(b_ctrl_down) and b_alt_down and ( \
					(msg == self.WM_LBUTTONDBLCLK	and console.editor.getProperty(self.editorprop_asdlc_on)	== str(self.option_on)) or \
					(msg == self.WM_MBUTTONUP		and console.editor.getProperty(self.editorprop_asmc_on)		== str(self.option_on)))):
				if msg == self.WM_MBUTTONUP:
					b_move = (console.editor.getProperty(self.editorprop_mc_move_on) == str(self.option_on))
					i_sel_start, i_sel_end = _Set_Middle_Click_Sel(lparam, b_move)
				else:
					i_sel_start	= self.lastsel_start
					i_sel_end	= self.lastsel_end
				b_get_quotes = (console.editor.getProperty(self.editorprop_get_qt_on) == str(self.option_on))
				self.o_extend_sel_from_sel.ExtendSel_To_Quotes( \
					curedit, b_get_quotes, i_sel_start, i_sel_end, b_clp_copy, b_con_copy)
			# select the whole word
			elif (not(b_shift_down) and b_ctrl_down and not(b_alt_down) and ( \
					(msg == self.WM_RBUTTONUP		and console.editor.getProperty(self.editorprop_crc_on)		== str(self.option_on)) or \
					(msg == self.WM_MBUTTONUP		and console.editor.getProperty(self.editorprop_cmc_on)		== str(self.option_on)))):
				if msg == self.WM_MBUTTONUP:
					b_move = (console.editor.getProperty(self.editorprop_mc_move_on) == str(self.option_on))
					i_sel_start, i_sel_end = _Set_Middle_Click_Sel(lparam, b_move)
				else:
					i_sel_start	= curedit.getSelectionStart()
					i_sel_end	= curedit.getSelectionEnd()
				s_escaped_wordchars = self.re.escape(console.editor.getProperty(self.editorprop_wordchars))
				self.o_extend_sel_from_sel.ExtendSel_WordWSpecialChars( \
					curedit, i_sel_start, i_sel_end, s_escaped_wordchars, b_clp_copy, b_con_copy)
			# select until space/space-like chars
			elif (not(b_shift_down) and not(b_ctrl_down) and b_alt_down and ( \
					(msg == self.WM_RBUTTONUP		and console.editor.getProperty(self.editorprop_arc_on)		== str(self.option_on)) or \
					(msg == self.WM_MBUTTONUP		and console.editor.getProperty(self.editorprop_amc_on)		== str(self.option_on)))):
				if msg == self.WM_MBUTTONUP:
					b_move = (console.editor.getProperty(self.editorprop_mc_move_on) == str(self.option_on))
					i_sel_start, i_sel_end = _Set_Middle_Click_Sel(lparam, b_move)
				else:
					i_sel_start	= curedit.getSelectionStart()
					i_sel_end	= curedit.getSelectionEnd()
				self.o_extend_sel_from_sel.ExtendSel_To_SpacesSpacesLike( \
					curedit, i_sel_start, i_sel_end, b_clp_copy, b_con_copy)
			# keep the selection/caret
			elif (not(b_shift_down) and not(b_ctrl_down) and not(b_alt_down) and \
					msg == self.WM_RBUTTONDOWN and console.editor.getProperty(self.editorprop_rc_keep_on) == str(self.option_on)):
				pass
			# normal WindowProc processing
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

		# get Scintilla windows in lst_scint_hwnd, number must be >= i_num_editor, truncate to i_num_editor
		npp_win_hwnd, self.lst_scint_hwnd, s_npp_class, s_scint_class = \
			self.o_get_nppscintilla_wins.GetNPPAndEditorsInfos()

		if npp_win_hwnd is None:
			print "\t" + s_npp_class + " main window NOT found ! NO hook !"
			return False
		if len(self.lst_scint_hwnd) < self.i_num_editor:
			print \
				"\t" + "Required " + str(self.i_num_editor) + " " + s_scint_class + " editors window : " + \
				str(len(self.lst_scint_hwnd)) + " found ! NO hook !"
			return False
		del self.lst_scint_hwnd[self.i_num_editor:]

		# get the address of our own WndProc
		self.newWndProc = self.WndProcType(_HOOK_MyWndProc)

		# register the hook for each Scintilla window present in lst_scint_hwnd, number must be i_num_editor
		s_hookreport = ""
		i_index = 0
		while i_index < len(self.lst_scint_hwnd):
			win_hwnd = self.lst_scint_hwnd[i_index]
			# register each hook and store oldwndproc addresses in lst_scint_oldwndproc
			self.SetLastError(0)
			oldwndproc = self.SetWindowLong(win_hwnd, self.GWL_WNDPROC, self.newWndProc)
			i_apierr = self.GetLastError()
			if i_apierr == 0:
				self.lst_scint_oldwndproc.append(oldwndproc)
				#s_hookreport = s_hookreport + "\t" + "-> DEBUG : " + hex(win_hwnd) + " : WindowProc OK" + " : " + str(oldwndproc) + "\n"
				i_index = i_index + 1
			else:
				del self.lst_scint_hwnd[i_index]
				s_hookreport = s_hookreport + "\t" + "-> " + hex(win_hwnd) + " : " + "NO WindowProc ! NOT hooked !" + "\n"
		if s_hookreport != "":
			s_hookreport = s_hookreport[:-1]
			print s_hookreport
		if len(self.lst_scint_hwnd) != self.i_num_editor:
			# un-register hooks that were successfull since the whole hook is canceled
			for i in range(0, len(self.lst_scint_hwnd)):
				self.SetWindowLong(self.lst_scint_hwnd[i], self.GWL_WNDPROC, self.lst_scint_oldwndproc[i])
			print "\t" + "Missing editors WindowProc ! NO hook !"
			return False

		self.hook_done = True
		return True
# end of class

# Main() code **************************************************************************************
def Main():
	print "[" + s_script_name + " starts] " + s_controleditscript

	# options formatting
	s_opt_info = ""
	s_opt_verb = ""
	dic_editorprop = {}
	for i in range(0, len(t_option_key)):
		console.editor.setProperty(s_editorprop_prefix + t_option_key[i], str(t_option_value[i]))
		if t_option_verbdes[i] == "":
			v_opt_value = t_option_value[i]
			if type(v_opt_value) == type(""):
				v_opt_value = "'" + v_opt_value + "'"
			else:
				v_opt_value = str(v_opt_value)
			s_opt_info = s_opt_info + t_option_initdes[i] + "=" + v_opt_value + ", "
		else:
			if str(t_option_value[i]) == str(i_true):
				s_opt_verb = s_opt_verb + "\t" + "* Enabled  : " + t_option_verbdes[i] + "\n"
			else:
				s_opt_verb = s_opt_verb + "\t" + "* DISABLED : " + t_option_verbdes[i] + "\n"
		dic_editorprop[t_option_key[i]] = s_editorprop_prefix + t_option_key[i]
	s_opt_info = s_opt_info[:-2]
	s_opt_verb = s_opt_verb[:-1]

	if console.editor.getProperty(s_editorprop_hook_reg) != str(i_true):
		# create an instance of the hook class, and populate object properties with script and Console variables
		o_scint_mouse_click_hook = C_Scint_Mouse_Click_Hook(s_script_name, s_hook_name, i_true, s_editorprop_hook_on, dic_editorprop)
		# register the WindowProc hook on Scintilla editors window
		b_reg = o_scint_mouse_click_hook.RegHook()
		if not(b_reg):
			console.writeError("\t" + s_hook_name + " registering FAILED /!\\" + "\n")
			console.show()
			notepad.messageBox(s_hook_name + " registering FAILED /!\\", s_script_name, MESSAGEBOXFLAGS.ICONSTOP)
		else:
			console.editor.setProperty(s_editorprop_hook_reg, str(i_true))
			console.editor.setProperty(s_editorprop_hook_on, str(i_true))
			print \
				"\t" + s_hook_name + " registered and activated" + \
				" [" + str(o_scint_mouse_click_hook.i_num_editor) + " editors window found]" + \
				" (" + s_reruntogglehook + ". " + s_willapplynewopt + ")"
			print "\t" + s_opt_info
			print s_opt_verb
		return

	if console.editor.getProperty(s_editorprop_hook_on) != str(i_true):
		console.editor.setProperty(s_editorprop_hook_on, str(i_true))

		print "\t" + s_hook_name + " re-activated (" + s_reruntogglehook + ". " + s_willapplynewopt + ")"
		print "\t" + s_opt_info
		print s_opt_verb
		if str(i_option_toggle_msgbox) == str(i_true):
			notepad.messageBox( \
				s_hook_name + " re-activated" + "\n\n" + \
				s_reruntogglehook + "\n" + s_willapplynewopt + "\n\n" + \
				s_opt_info.replace(", ", "\n") + "\n\n" + \
				s_opt_verb.replace("  ", " ").replace("\t: ", "\n   ").replace("\t", "") + "\n\n" + \
				s_controleditscript, \
				s_script_name, MESSAGEBOXFLAGS.ICONINFORMATION)
	else:
		console.editor.setProperty(s_editorprop_hook_on, str(i_false))

		print "\t" + s_hook_name + " DE-ACTIVATED /!\\ (" + s_reruntogglehook + ". " + s_willapplynewopt + ")"
		print "\t" + s_opt_info
		print s_opt_verb
		if str(i_option_toggle_msgbox) == str(i_true):
			notepad.messageBox( \
				s_hook_name + " DE-ACTIVATED /!\\" + "\n\n" + \
				s_reruntogglehook + "\n" + s_willapplynewopt + "\n\n" + \
				s_opt_info.replace(", ", "\n") + "\n\n" + 
				s_opt_verb.replace("  ", " ").replace("\t: ", "\n   ").replace("\t", "") + "\n\n" + \
				s_controleditscript, \
				s_script_name, MESSAGEBOXFLAGS.ICONEXCLAMATION)

Main()
