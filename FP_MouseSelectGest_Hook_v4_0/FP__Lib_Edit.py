# ##################################################################################################
# FP Library : Edit
# ##################################################################################################
from Npp import *

class C_Find_OutRange():
	def __init__(self):
		# class const
		self.INVALID_POSITION = -1 # Scintilla character position constant

	def FindText_Borders_OutRange(self, curedit, i_start, i_end, s_pattern):
		if i_start > i_end:
			return None

		i_text_len = curedit.getTextLength()
		t_findtext = curedit.findText(FINDOPTION.REGEXP, i_start, 0, s_pattern)
		if t_findtext is None:
			i_left = -1
		else:
			i_left = t_findtext[0]
		t_findtext = curedit.findText(FINDOPTION.REGEXP, i_end, i_text_len, s_pattern)
		if t_findtext is None:
			i_right = i_text_len
		else:
			i_right = t_findtext[0]
		if (i_left + 1 == i_start and i_right == i_end):
			return None
		return (i_left, i_right)

	def FindText_MatchingQuotes_OutRange(self, curedit, i_start, i_end):
		if i_start > i_end:
			return None

		i_text_len = curedit.getTextLength()
		t_findtext_prev_single = curedit.findText(0, i_start, 0, "'")
		t_findtext_next_single = None if (t_findtext_prev_single is None) else curedit.findText(0, i_end, i_text_len, "'")
		t_findtext_prev_double = curedit.findText(0, i_start, 0, chr(34))
		t_findtext_next_double = None if (t_findtext_prev_double is None) else curedit.findText(0, i_end, i_text_len, chr(34))

		i_left	= None
		i_right	= None
		if t_findtext_next_double is None:
			if not(t_findtext_next_single is None):
				i_left	= t_findtext_prev_single[0]
				i_right	= t_findtext_next_single[0]
		elif t_findtext_next_single is None:
			if not(t_findtext_next_double is None):
				i_left	= t_findtext_prev_double[0]
				i_right	= t_findtext_next_double[0]
		elif t_findtext_next_single[0] < t_findtext_next_double[0]:
				i_left	= t_findtext_prev_single[0]
				i_right	= t_findtext_next_single[0]
		elif t_findtext_next_double[0] < t_findtext_next_single[0]:
				i_left	= t_findtext_prev_double[0]
				i_right	= t_findtext_next_double[0]
		if ((i_left is None) or (i_right is None)):
			return None
		return (i_left, i_right)

	def FindText_MatchingBrackets_OutRange(self, curedit, i_start, i_end, b_angle, b_sl_angle):
		s_pattern_newline = "[\r\n]"
		s_pattern_close_brackets = "\)\]\}"
		if b_angle: s_pattern_close_brackets = s_pattern_close_brackets + "\>"
		s_pattern_close_brackets = "[" + s_pattern_close_brackets + "]"

		i_left	= None
		i_right	= None
		i_text_len = curedit.getTextLength()
		i_search_start = i_end
		while True:
			t_findtext = curedit.findText(FINDOPTION.REGEXP, i_search_start, i_text_len, s_pattern_close_brackets)
			if t_findtext is None: break

			i_pos_close	= t_findtext[0]
			i_pos_open	= curedit.braceMatch(i_pos_close, 0)
			if (i_pos_open != self.INVALID_POSITION and i_pos_open < i_start):
				b_ignore = False
				if (b_angle and b_sl_angle):
					if curedit.getTextRange(i_pos_close, i_pos_close + 1) == ">":
						if not(curedit.findText(FINDOPTION.REGEXP, i_pos_open + 1, i_pos_close, s_pattern_newline) is None):
							b_ignore = True
				if not(b_ignore):
					i_left	= i_pos_open
					i_right	= i_pos_close
					break
			i_search_start = i_pos_close + 1
		if ((i_left is None) or (i_right is None)):
			return None
		return (i_left, i_right)
# end of class

class C_Extend_Sel_From_Sel():
	# class constructor
	def __init__(self):
		# custom object import
		self.o_find_outrange = C_Find_OutRange()

	def ExtendSel_To_SpacesSpacesLike(self, curedit, i_sel_start, i_sel_end, b_clp_copy, b_con_copy):
		self.ExtendSel_To_Pattern(curedit, i_sel_start, i_sel_end, b_clp_copy, b_con_copy, "\s")
	def ExtendSel_WordWSpecialChars(self, curedit, i_sel_start, i_sel_end, s_escaped_wordchars, b_clp_copy, b_con_copy):
		self.ExtendSel_To_Pattern(curedit, i_sel_start, i_sel_end, b_clp_copy, b_con_copy, "[^\w" + s_escaped_wordchars + "]")
	def ExtendSel_To_Pattern(self, curedit, i_sel_start, i_sel_end, b_clp_copy, b_con_copy, s_pattern):
		t_borders = self.o_find_outrange.FindText_Borders_OutRange(curedit, i_sel_start, i_sel_end, s_pattern)
		if not(t_borders is None):
			i_sel_start	= t_borders[0] + 1
			i_sel_end	= t_borders[1]
			if (b_clp_copy or b_con_copy): self.Copy_Range(curedit, i_sel_start, i_sel_end, b_clp_copy, b_con_copy)
		curedit.setSel(i_sel_start, i_sel_end)

	def ExtendSel_To_Quotes(self, curedit, b_get_quotes, i_sel_start, i_sel_end, b_clp_copy, b_con_copy):
		# only add quotes touching the selection
		s_char_left		= curedit.getTextRange(i_sel_start - 1, i_sel_start)
		s_char_right	= curedit.getTextRange(i_sel_end, i_sel_end + 1)
		if (	(s_char_left == chr(34) and s_char_right == chr(34)) or \
				(s_char_left == "'" and s_char_right == "'")):
			curedit.setSel(i_sel_start - 1, i_sel_end + 1)
			if (b_clp_copy or b_con_copy): self.Copy_Range(curedit, i_sel_start - 1, i_sel_end + 1, b_clp_copy, b_con_copy)
			return

		t_quotes = self.o_find_outrange.FindText_MatchingQuotes_OutRange(curedit, i_sel_start, i_sel_end)
		if not(t_quotes is None):
			i_extend_chars = 1 if b_get_quotes else 0
			i_sel_start	= t_quotes[0] + 1 - i_extend_chars
			i_sel_end	= t_quotes[1] + i_extend_chars
			if (b_clp_copy or b_con_copy): self.Copy_Range(curedit, i_sel_start, i_sel_end, b_clp_copy, b_con_copy)
		curedit.setSel(i_sel_start, i_sel_end)

	def ExtendSel_To_Brackets(self, curedit, i_sel_start, i_sel_end, b_angle, b_sl_angle, b_get_brackets, b_clp_copy, b_con_copy):
		# only add brackets touching the selection
		s_char_left		= curedit.getTextRange(i_sel_start - 1, i_sel_start)
		s_char_right	= curedit.getTextRange(i_sel_end, i_sel_end + 1)
		if (	(s_char_left == "(" and s_char_right == ")") or \
				(s_char_left == "[" and s_char_right == "]") or \
				(s_char_left == "{" and s_char_right == "}") or \
				(s_char_left == "<" and s_char_right == ">" and b_angle)):
			curedit.setSel(i_sel_start - 1, i_sel_end + 1)
			if (b_clp_copy or b_con_copy): self.Copy_Range(curedit, i_sel_start - 1, i_sel_end + 1, b_clp_copy, b_con_copy)
			return

		t_brackets = self.o_find_outrange.FindText_MatchingBrackets_OutRange(curedit, i_sel_start, i_sel_end, b_angle, b_sl_angle)
		if not(t_brackets is None):
			i_extend_chars = 1 if b_get_brackets else 0
			i_sel_start	= t_brackets[0] + 1 - i_extend_chars
			i_sel_end	= t_brackets[1] + i_extend_chars
			if (b_clp_copy or b_con_copy): self.Copy_Range(curedit, i_sel_start, i_sel_end, b_clp_copy, b_con_copy)
		curedit.setSel(i_sel_start, i_sel_end)

	def Copy_Range(self, curedit, i_start, i_end, b_clp_copy, b_con_copy):
		if i_start == i_end:
			return
		s_text = curedit.getTextRange(i_start, i_end)
		if b_clp_copy: curedit.copyText(s_text)
		if b_con_copy: print s_text
# end of class
