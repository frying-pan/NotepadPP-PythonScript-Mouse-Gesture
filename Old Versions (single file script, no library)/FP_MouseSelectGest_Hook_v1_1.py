# PythonScript which hooks mouse clicks (WndProc HOOK on Scintilla windows)
# Tested on Notepad++ 64 bits (NOT tested on 32 Bits but could be compatible) /!\ this file uses TABS for indent /!\
	# SHIFT + double-left-click			: select from clicked point the whole variable name : alphanumeric with _ and . (dot)
	# CTRL + SHIFT + double-left-click	: select from clicked point the whole bracket content : () [] {}, from left in case of mismatch
	# ALT + SHIFT + double-left-click	: select from clicked point the whole quote content : "" '', from left in case of mismatch
	# ALT + right-click					: select from clicked point until space/space-like characters are met : space/tab/cr/lf/formfeed/vtab etc...
	# right-click						: prevent right-click from moving the caret and losing current text selection
# re-run the script to de-activate/re-activate the whole hook (re-running the script will also apply new *options values*)
# change the *options values* (just below) to choose which mouse hooks will be active

# *options values* : set value to INTEGER 1 to have the feature enabled (any OTHER INTEGER value will DISABLE it)
i_feature_shift_double_left_click			= 1
i_feature_control_shift_double_left_click	= 1
i_feature_alt_shift_double_left_click		= 1
i_feature_alt_right_click					= 1
i_feature_right_click						= 1
i_message_box_warnings						= 1	# if disabled, no message box will pop on registering hook error,
												# or when toggling the hook (console messages will still occur)
# end of *options values*

from Npp import *

import platform
import ctypes
from ctypes import wintypes
import datetime
from datetime import datetime

s_script_name	= "Perso_ScintWndProc_Hook"
s_hook_name		= "Scint_Mouse_Click_Hook"

s_editorprop_regdone		= "SCINTWNDPROC_HOOK_DONE"
s_editorprop_active			= "SCINTWNDPROC_HOOK_ACTIVE"
s_editorprop_sdlc_active	= "SCINTWNDPROC_SDLC_ACTIVE"
s_editorprop_csdlc_active	= "SCINTWNDPROC_CSDLC_ACTIVE"
s_editorprop_asdlc_active	= "SCINTWNDPROC_ASDLC_ACTIVE"
s_editorprop_arc_active		= "SCINTWNDPROC_ARC_ACTIVE"
s_editorprop_rc_active		= "SCINTWNDPROC_RC_ACTIVE"
s_true						= "TRUE"

s_reruntogglehook	= "Re-run the script to toggle the whole hook"
s_willapplynewopt	= "This will also apply new *options values* saved in the script file"
s_feature_sdlc_off	= "* Feature SHIFT + double-left-click is DISABLED by script option"
s_feature_csdlc_off	= "* Feature CTRL + SHIFT + double-left-click is DISABLED by script option"
s_feature_asdlc_off	= "* Feature ALT + SHIFT + double-left-click is DISABLED by script option"
s_feature_arc_off	= "* Feature ALT + right-click is DISABLED by script option"
s_feature_rc_off	= "* Feature right-click is DISABLED by script option"

GWL_WNDPROC = -4				# used to set a new address for the windows procedure
I_VK_SHIFT		= 0x10			# SHIFT virtual key code
I_VK_CONTROL	= 0x11			# CONTROL virtual key code
I_VK_ALT		= 0x12			# ALT virtual key code
KSTATE_ISDOWN = 0x8000			# key pressed
WM_LBUTTONDBLCLK	= 0x0203	# mouse double-left-click window message
WM_RBUTTONDOWN		= 0x0204	# mouse right-click down window message
WM_RBUTTONUP		= 0x0205	# mouse right-click up window message

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

EnumWindowsProc				= ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
EnumWindows					= ctypes.windll.user32.EnumWindows
EnumChildWindows			= ctypes.windll.user32.EnumChildWindows
GetAsyncKeyState			= ctypes.windll.user32.GetAsyncKeyState
RealGetWindowClass			= ctypes.windll.user32.RealGetWindowClassW
GetWindowThreadProcessId	= ctypes.windll.user32.GetWindowThreadProcessId
GetCurrentProcessId			= ctypes.windll.kernel32.GetCurrentProcessId
SetLastError				= ctypes.windll.kernel32.SetLastError
GetLastError				= ctypes.windll.kernel32.GetLastError

class C_Scint_Mouse_Click_Hook():
	# class constructor
	def __init__(self):
		self.arr_scint_hwnd = []
		self.arr_scint_oldwndproc = []

	# function to register the hook on all found Scintilla windows
	def RegHook(self):
		def Enum_Window_Hwnd(hwnd, lparam):
			arr_enum_window_hwnd.append(hwnd)
			return True

		s_npp_class		= u"Notepad++"
		s_scint_class	= u"Scintilla"

		i_cur_pid = GetCurrentProcessId()
		npp_win_hwnd = None

		arr_enum_window_hwnd = []
		EnumWindows(EnumWindowsProc(Enum_Window_Hwnd), 0)
		# get all class="Notepad++" top_level NPP windows handle
		buff = ctypes.create_unicode_buffer(len(s_npp_class) + 1 + 1)
		for win_hwnd in arr_enum_window_hwnd:
			RealGetWindowClass(win_hwnd, buff, len(s_npp_class) + 1 + 1)
			if buff.value == s_npp_class:
				# check if each NPP window handle is owned by current process, stop at the first found
				ci_win_pid = wintypes.DWORD(0)
				GetWindowThreadProcessId(win_hwnd, ctypes.pointer(ci_win_pid))
				if i_cur_pid == ci_win_pid.value:
					npp_win_hwnd = win_hwnd
					break
		if npp_win_hwnd is None:
			print "\t" + s_npp_class + " window NOT found ! NO hook !"
			return False
		print "\t" + s_npp_class + " Handle = " + hex(npp_win_hwnd)

		del arr_enum_window_hwnd[:]
		EnumChildWindows(npp_win_hwnd, EnumWindowsProc(Enum_Window_Hwnd), 0)
		# get all class="Scintilla" windows handle, childs of NPP window, in arr_scint_hwnd
		# (at least all existing Scintilla windows at that time, should include primary and secondary views)
		buff = ctypes.create_unicode_buffer(len(s_scint_class) + 1 + 1)
		for win_hwnd in arr_enum_window_hwnd:
			RealGetWindowClass(win_hwnd, buff, len(s_scint_class) + 1 + 1)
			if buff.value == s_scint_class:
				self.arr_scint_hwnd.append(win_hwnd)

		# get the address of our own WndProc
		self.newWndProc = WndProcType(self.MyWndProc)

		# register the hook for each window present in arr_scint_hwnd
		s_list = "\t" + "Found " + str(len(self.arr_scint_hwnd)) + " " + s_scint_class + " Handle / WindowProc"
		i_index = 0
		while i_index < len(self.arr_scint_hwnd):
			win_hwnd = self.arr_scint_hwnd[i_index]
			# register hook and store oldwndproc addresses in arr_scint_oldwndproc
			SetLastError(0)
			oldwndproc = SetWindowLong(win_hwnd, GWL_WNDPROC, self.newWndProc)
			i_apierr = GetLastError()
			if i_apierr == 0:
				self.arr_scint_oldwndproc.append(oldwndproc)
				s_list = s_list + "\n" + "\t\t" + hex(win_hwnd) + " / " + str(oldwndproc)
				i_index = i_index + 1
			else:
				del self.arr_scint_hwnd[i_index]
				s_list = s_list + "\n" + "\t\t" + hex(win_hwnd) + " / " + "NO WindowProc ! NOT hooked !"
		print s_list
		if len(self.arr_scint_hwnd) == 0:
			print "\t" + s_scint_class + " window(s) or WindowProc(s) NOT found ! NO hook !"
			return False
		return True

	def MyWndProc(self, hwnd, msg, wparam, lparam):							# our own WndProc function receives windows messages
		oldwndproc = None
		for i in range(0, len(self.arr_scint_hwnd)):
			if self.arr_scint_hwnd[i] == hwnd:								# target hwnd found at index i in arr_scint_hwnd
				oldwndproc = self.arr_scint_oldwndproc[i]					# corresponding oldwndproc is picked in arr_scint_oldwndproc
				break
		if oldwndproc is None:												# fatal error ! should not happen...
			print "\t" + s_hook_name + " Fatal error ! Hooked WndProc NOT found !"
			notepad.messageBox(s_hook_name + " Fatal error ! Hooked WndProc NOT found !", s_script_name, MESSAGEBOXFLAGS.ICONEXCLAMATION)
			return 0

		if (msg != WM_LBUTTONDBLCLK and msg != WM_RBUTTONDOWN and msg != WM_RBUTTONUP): # if NOT in mouse hooked messages : abort
			return CallWindowProc(oldwndproc, hwnd, msg, wparam, lparam)	# -> IMPORTANT pass other msg to NPP, otherwise will block NPP
		if console.editor.getProperty(s_editorprop_active) != s_true:		# if hook de-activated : abort
			return CallWindowProc(oldwndproc, hwnd, msg, wparam, lparam)	# -> IMPORTANT pass other msg to NPP, otherwise will block NPP

		b_shift_down	= ((GetAsyncKeyState(I_VK_SHIFT)	& KSTATE_ISDOWN) == KSTATE_ISDOWN)
		b_ctrl_down		= ((GetAsyncKeyState(I_VK_CONTROL)	& KSTATE_ISDOWN) == KSTATE_ISDOWN)
		b_alt_down		= ((GetAsyncKeyState(I_VK_ALT)		& KSTATE_ISDOWN) == KSTATE_ISDOWN)

		if (console.editor.getProperty(s_editorprop_sdlc_active) == "1" and \
				msg == WM_LBUTTONDBLCLK and b_shift_down and not(b_ctrl_down) and not(b_alt_down)):
			self.ExtendSel_AlphaNumUnderscoreDot()							# select from clicked point the whole variable name
		elif (console.editor.getProperty(s_editorprop_csdlc_active) == "1" and \
				msg == WM_LBUTTONDBLCLK and b_shift_down and b_ctrl_down and not(b_alt_down)):
			self.ExtendSel_BracketContent()									# select from clicked point the whole bracket content
		elif (console.editor.getProperty(s_editorprop_asdlc_active) == "1" and \
				msg == WM_LBUTTONDBLCLK and b_shift_down and not(b_ctrl_down) and b_alt_down):
			self.ExtendSel_Quotes()											# select from clicked point the whole quote content
		elif (console.editor.getProperty(s_editorprop_arc_active) == "1" and \
				msg == WM_RBUTTONUP and not(b_shift_down) and not(b_ctrl_down) and b_alt_down):
			self.ExtendSel_SpaceSpaceLike()
		elif (console.editor.getProperty(s_editorprop_rc_active) == "1" and \
				msg == WM_RBUTTONDOWN and not(b_shift_down) and not(b_ctrl_down) and not(b_alt_down)):
			dummy = 0														# do nothing
		else:
			return CallWindowProc(oldwndproc, hwnd, msg, wparam, lparam)	# -> IMPORTANT pass other msg to NPP, otherwise will block NPP

		#res = "DEBUG " + s_hook_name
		#res = res + " Message = " + hex(msg) + " to hwnd = " + hex(hwnd)
		#res = res + " Forwarded To oldwndproc = " + str(oldwndproc)
		#print res + " At " + str(datetime.now())
		return CallWindowProc(oldwndproc, hwnd, 0, 0, 0)					# nullify the mouse hooked messages

	def FindBorderBiDir(self, i_start, s_pattern):
		i_text_len = editor.getTextLength()
		t_search = editor.findText(FINDOPTION.REGEXP, i_start, 0, s_pattern)
		if t_search is None:
			i_left = -1
		else:
			i_left = t_search[0]
		t_search = editor.findText(FINDOPTION.REGEXP, i_start, i_text_len, s_pattern)
		if t_search is None:
			i_right = i_text_len
		else:
			i_right = t_search[0]
		return (i_left, i_right)

	def ExtendSel_SpaceSpaceLike(self):
		s_pattern = "\s"

		i_caret_pos = editor.getCurrentPos()
		i_start	= editor.getSelectionStart()
		i_end	= editor.getSelectionEnd()

		t_border = self.FindBorderBiDir(i_caret_pos, s_pattern)
		i_left	= t_border[0] + 1
		i_right	= t_border[1]
		if i_left < i_right:
			editor.setSel(i_left, i_right)
		else:
			editor.setSel(i_start, i_end)

	def ExtendSel_AlphaNumUnderscoreDot(self):
		s_pattern = "[^\w_.]"

		i_caret_pos = editor.getCurrentPos()
		i_start	= editor.getSelectionStart()
		i_end	= editor.getSelectionEnd()

		t_border = self.FindBorderBiDir(i_caret_pos, s_pattern)
		i_left	= t_border[0] + 1
		i_right	= t_border[1]
		if i_left < i_right:
			editor.setSel(i_left, i_right)
		else:
			editor.setSel(i_start, i_end)

	def ExtendSel_Quotes(self):
		i_text_len = editor.getTextLength()
		i_caret_pos = editor.getCurrentPos()
		i_start	= editor.getSelectionStart()
		i_end	= editor.getSelectionEnd()

		t_search_prev_single = editor.findText(0, i_caret_pos, 0, "'")
		t_search_next_single = editor.findText(0, i_caret_pos, i_text_len, "'")
		t_search_prev_double = editor.findText(0, i_caret_pos, 0, chr(34))
		t_search_next_double = editor.findText(0, i_caret_pos, i_text_len, chr(34))

		i_left	= None
		i_right	= None
		if ((t_search_prev_single is None) or (t_search_next_single is None)):
			if (not(t_search_prev_double is None) and not(t_search_next_double is None)):
				i_left	= t_search_prev_double[0] + 1
				i_right	= t_search_next_double[0]
		elif ((t_search_prev_double is None) or (t_search_next_double is None)):
			if (not(t_search_prev_single is None) and not(t_search_next_single is None)):
				i_left	= t_search_prev_single[0] + 1
				i_right	= t_search_next_single[0]
		elif t_search_prev_single[0] < t_search_prev_double[0]:
				i_left	= t_search_prev_double[0] + 1
				i_right	= t_search_next_double[0]
		elif t_search_prev_double[0] < t_search_prev_single[0]:
				i_left	= t_search_prev_single[0] + 1
				i_right	= t_search_next_single[0]
		if (not(i_left is None) and not(i_right is None)):
			editor.setSel(i_left, i_right)
		else:
			editor.setSel(i_start, i_end)

	def ExtendSel_BracketContent(self):
		def SearchOrphan(i_start, i_end, s_pattern_brackets):
			if i_start == i_end:
				return None

			if i_start < i_end: b_forward = True
			else: b_forward = False

			i_par = 0; i_sqr = 0; i_cur = 0
			i_pos = i_start
			while True:
				t_search = editor.findText(FINDOPTION.REGEXP, i_pos, i_end, s_pattern_brackets)
				if t_search is None:
					return None

				i_pos = t_search[0]
				s_char = editor.getTextRange(i_pos, i_pos + 1)
				if		s_char == "(": i_par += 1
				elif	s_char == ")": i_par -= 1
				elif	s_char == "[": i_sqr += 1
				elif	s_char == "]": i_sqr -= 1
				elif	s_char == "{": i_cur += 1
				elif	s_char == "}": i_cur -= 1

				if b_forward:
					if (i_par < 0 or i_sqr < 0 or i_cur < 0): break
				else:
					if (i_par > 0 or i_sqr > 0 or i_cur > 0): break
				if b_forward: i_pos = i_pos + 1
			return (i_pos, s_char)

		i_text_len = editor.getTextLength()
		i_caret_pos = editor.getCurrentPos()
		i_start	= editor.getSelectionStart()
		i_end	= editor.getSelectionEnd()

		s_pattern_par = "\(\)"
		s_pattern_sqr = "\[\]"
		s_pattern_cur = "\{\}"
		s_pattern_brackets = "[" + s_pattern_par + s_pattern_sqr + s_pattern_cur + "]"

		i_left	= None
		i_right	= None
		while True:
			t_orphan_back = SearchOrphan(i_caret_pos, 0, s_pattern_brackets)
			if t_orphan_back is None: break

			s_char = t_orphan_back[1]
			if		s_char == "(": s_pattern = "[" + s_pattern_par + "]"
			elif	s_char == "[": s_pattern = "[" + s_pattern_sqr + "]"
			elif	s_char == "{": s_pattern = "[" + s_pattern_cur + "]"
			t_orphan_forward = SearchOrphan(i_caret_pos, i_text_len, s_pattern)
			if not(t_orphan_forward is None):
				i_left	= t_orphan_back[0] + 1
				i_right	= t_orphan_forward[0]
				break

			if		s_char == "(": s_pattern_brackets = s_pattern_brackets.replace(s_pattern_par, "")
			elif	s_char == "[": s_pattern_brackets = s_pattern_brackets.replace(s_pattern_sqr, "")
			elif	s_char == "{": s_pattern_brackets = s_pattern_brackets.replace(s_pattern_cur, "")
			if s_pattern_brackets == "[]": break
		if (not(i_left is None) and not(i_right is None)):
			editor.setSel(i_left, i_right)
		else:
			editor.setSel(i_start, i_end)
	# end of class

s_opt_info = ""
if i_feature_shift_double_left_click			!= 1: s_opt_info = s_opt_info + "\t" + s_feature_sdlc_off + "\n"
if i_feature_control_shift_double_left_click	!= 1: s_opt_info = s_opt_info + "\t" + s_feature_csdlc_off + "\n"
if i_feature_alt_shift_double_left_click		!= 1: s_opt_info = s_opt_info + "\t" + s_feature_asdlc_off + "\n"
if i_feature_alt_right_click					!= 1: s_opt_info = s_opt_info + "\t" + s_feature_arc_off + "\n"
if i_feature_right_click						!= 1: s_opt_info = s_opt_info + "\t" + s_feature_rc_off + "\n"
if not(s_opt_info == ""): s_opt_info = s_opt_info[:-1]
console.editor.setProperty(s_editorprop_sdlc_active,	str(i_feature_shift_double_left_click))
console.editor.setProperty(s_editorprop_csdlc_active,	str(i_feature_control_shift_double_left_click))
console.editor.setProperty(s_editorprop_asdlc_active,	str(i_feature_alt_shift_double_left_click))
console.editor.setProperty(s_editorprop_arc_active,		str(i_feature_alt_right_click))
console.editor.setProperty(s_editorprop_rc_active,		str(i_feature_right_click))

print "[" + s_script_name + " starts]"
if console.editor.getProperty(s_editorprop_regdone) != s_true:
	console.editor.setProperty(s_editorprop_active, s_true)
	o_scint_mouse_click_hook = C_Scint_Mouse_Click_Hook()	# create an instance of the hook class
	b_reg = o_scint_mouse_click_hook.RegHook()				# register the hook on all found Scintilla windows
	if b_reg:
		console.editor.setProperty(s_editorprop_regdone, s_true)
		print "\t" + s_hook_name + " registered and activated (" + s_reruntogglehook + ")"
		if not(s_opt_info == ""): print s_opt_info
	else:
		if not(s_opt_info == ""): print s_opt_info
		print "\t" + s_hook_name + " registering failed"
		if i_message_box_warnings == 1:
			notepad.messageBox(s_hook_name + " registering failed", s_script_name, MESSAGEBOXFLAGS.ICONSTOP)
else:
	if console.editor.getProperty(s_editorprop_active) != s_true:
		console.editor.setProperty(s_editorprop_active, s_true)
		print "\t" + s_hook_name + " re-activated (" + s_reruntogglehook + ")"
		if not(s_opt_info == ""): print s_opt_info
		if i_message_box_warnings == 1:
			notepad.messageBox( \
				s_hook_name + " re-activated\n\n" + s_reruntogglehook + "\n" + s_willapplynewopt + "\n" + s_opt_info, \
				s_script_name, MESSAGEBOXFLAGS.ICONINFORMATION)
	else:
		console.editor.setProperty(s_editorprop_active, "")
		print "\t" + s_hook_name + " DE-ACTIVATED (" + s_reruntogglehook + ")"
		if not(s_opt_info == ""): print s_opt_info
		if i_message_box_warnings == 1:
			notepad.messageBox( \
				s_hook_name + " DE-ACTIVATED\n\n" + s_reruntogglehook + "\n" + s_willapplynewopt + "\n" + s_opt_info, \
				s_script_name, MESSAGEBOXFLAGS.ICONEXCLAMATION)
