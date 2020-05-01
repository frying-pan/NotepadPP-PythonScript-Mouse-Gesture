# ##################################################################################################
# Perso Library : Edit
# ##################################################################################################
from Npp import *

class C_Extend_Sel_From_Caret():
	class C_FindSearch():
		# class constructor
		def __init__(self):
			dummy = None

		def FindBordersOutRange(self, i_start, i_end, s_pattern):
			if i_start > i_end:
				return None

			i_text_len = editor.getTextLength()
			t_search = editor.findText(FINDOPTION.REGEXP, i_start, 0, s_pattern)
			if t_search is None:
				i_left = -1
			else:
				i_left = t_search[0]
			t_search = editor.findText(FINDOPTION.REGEXP, i_end, i_text_len, s_pattern)
			if t_search is None:
				i_right = i_text_len
			else:
				i_right = t_search[0]
			return (i_left, i_right)

		def FindMatchingQuotesOutRange(self, i_start, i_end):
			if i_start > i_end:
				return None

			i_text_len = editor.getTextLength()
			t_search_prev_single = editor.findText(0, i_start, 0, "'")
			t_search_next_single = editor.findText(0, i_end, i_text_len, "'")
			t_search_prev_double = editor.findText(0, i_start, 0, chr(34))
			t_search_next_double = editor.findText(0, i_end, i_text_len, chr(34))

			i_left	= None
			i_right	= None
			if ((t_search_prev_single is None) or (t_search_next_single is None)):
				if (not(t_search_prev_double is None) and not(t_search_next_double is None)):
					i_left	= t_search_prev_double[0]
					i_right	= t_search_next_double[0]
			elif ((t_search_prev_double is None) or (t_search_next_double is None)):
				if (not(t_search_prev_single is None) and not(t_search_next_single is None)):
					i_left	= t_search_prev_single[0]
					i_right	= t_search_next_single[0]
			elif t_search_prev_single[0] < t_search_prev_double[0]:
					i_left	= t_search_prev_double[0]
					i_right	= t_search_next_double[0]
			elif t_search_prev_double[0] < t_search_prev_single[0]:
					i_left	= t_search_prev_single[0]
					i_right	= t_search_next_single[0]
			if ((i_left is None) or (i_right is None)):
				return None
			return (i_left, i_right)

		def SearchOrphanBiDir(self, i_from, i_to, s_pattern_brackets):
			if i_from == i_to:
				return None

			if i_from < i_to: b_forward = True
			else: b_forward = False

			i_par = 0; i_sqr = 0; i_cur = 0
			i_pos = i_from
			while True:
				t_search = editor.findText(FINDOPTION.REGEXP, i_pos, i_to, s_pattern_brackets)
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
	# end of class

	# class constructor
	def __init__(self):
		self.o_findsearch = self.C_FindSearch()

	def ExtendSel_To_SpacesSpacesLike(self, i_sel_start, i_sel_end, b_clp_copy, b_con_copy):
		self.ExtendSel_To_Pattern(i_sel_start, i_sel_end, b_clp_copy, b_con_copy, "\s")
	def ExtendSel_AlphaNumUnderscoreDot(self, i_sel_start, i_sel_end, b_clp_copy, b_con_copy):
		self.ExtendSel_To_Pattern(i_sel_start, i_sel_end, b_clp_copy, b_con_copy, "[^\w_.]")
	def ExtendSel_To_Pattern(self, i_sel_start, i_sel_end, b_clp_copy, b_con_copy, s_pattern):
		t_borders = self.o_findsearch.FindBordersOutRange(i_sel_start, i_sel_end, s_pattern)
		if not(t_borders is None):
			i_left	= t_borders[0] + 1
			i_right	= t_borders[1]

			editor.setSel(i_left, i_right)
			if (b_clp_copy or b_con_copy): self.copy_non_empty(i_left, i_right, b_clp_copy, b_con_copy)
		else:
			editor.setSel(i_sel_start, i_sel_end)

	def ExtendSel_To_Quotes(self, b_get_quotes, i_sel_start, i_sel_end, b_clp_copy, b_con_copy):
		# only add touching quotes to selection
		s_char_left		= editor.getTextRange(i_sel_start - 1, i_sel_start)
		s_char_right	= editor.getTextRange(i_sel_end, i_sel_end + 1)
		if (	(s_char_left == chr(34) and s_char_right == chr(34)) or \
				(s_char_left == "'" and s_char_right == "'")):
			editor.setSel(i_sel_start - 1, i_sel_end + 1)
			if (b_clp_copy or b_con_copy): self.copy_non_empty(i_sel_start - 1, i_sel_end + 1, b_clp_copy, b_con_copy)
			return

		t_quotes = self.o_findsearch.FindMatchingQuotesOutRange(i_sel_start, i_sel_end)
		if not(t_quotes is None):
			i_left	= t_quotes[0] + 1
			i_right	= t_quotes[1]
			i_extend_chars = 1 if b_get_quotes else 0
			i_left	= i_left - i_extend_chars
			i_right	= i_right + i_extend_chars

			editor.setSel(i_left, i_right)
			if (b_clp_copy or b_con_copy): self.copy_non_empty(i_left, i_right, b_clp_copy, b_con_copy)
		else:
			editor.setSel(i_sel_start, i_sel_end)

	def ExtendSel_To_Brackets(self, b_get_brackets, i_sel_start, i_sel_end, b_clp_copy, b_con_copy):
		s_pattern_par = "\(\)"
		s_pattern_sqr = "\[\]"
		s_pattern_cur = "\{\}"
		s_pattern_brackets = "[" + s_pattern_par + s_pattern_sqr + s_pattern_cur + "]"

		# only add touching brackets to selection
		s_char_left		= editor.getTextRange(i_sel_start - 1, i_sel_start)
		s_char_right	= editor.getTextRange(i_sel_end, i_sel_end + 1)
		if (	(s_char_left == "(" and s_char_right == ")") or \
				(s_char_left == "[" and s_char_right == "]") or \
				(s_char_left == "{" and s_char_right == "}")):
			editor.setSel(i_sel_start - 1, i_sel_end + 1)
			if (b_clp_copy or b_con_copy): self.copy_non_empty(i_sel_start - 1, i_sel_end + 1, b_clp_copy, b_con_copy)
			return

		i_text_len = editor.getTextLength()
		i_left	= None
		i_right	= None
		while True:
			t_orphan_back = self.o_findsearch.SearchOrphanBiDir(i_sel_start, 0, s_pattern_brackets)
			if t_orphan_back is None: break

			s_char = t_orphan_back[1]
			if		s_char == "(": s_pattern = "[" + s_pattern_par + "]"
			elif	s_char == "[": s_pattern = "[" + s_pattern_sqr + "]"
			elif	s_char == "{": s_pattern = "[" + s_pattern_cur + "]"
			t_orphan_forward = self.o_findsearch.SearchOrphanBiDir(i_sel_end, i_text_len, s_pattern)
			if not(t_orphan_forward is None):
				i_left	= t_orphan_back[0] + 1
				i_right	= t_orphan_forward[0]
				break

			if		s_char == "(": s_pattern_brackets = s_pattern_brackets.replace(s_pattern_par, "")
			elif	s_char == "[": s_pattern_brackets = s_pattern_brackets.replace(s_pattern_sqr, "")
			elif	s_char == "{": s_pattern_brackets = s_pattern_brackets.replace(s_pattern_cur, "")
			if s_pattern_brackets == "[]": break
		if (not(i_left is None) and not(i_right is None)):
			i_extend_chars = 1 if b_get_brackets else 0
			i_left	= i_left - i_extend_chars
			i_right	= i_right + i_extend_chars

			editor.setSel(i_left, i_right)
			if (b_clp_copy or b_con_copy): self.copy_non_empty(i_left, i_right, b_clp_copy, b_con_copy)
		else:
			editor.setSel(i_sel_start, i_sel_end)

	def copy_non_empty(self, i_start, i_end, b_clp_copy, b_con_copy):
		if i_start == i_end:
			return
		s_text = editor.getTextRange(i_start, i_end)
		if b_clp_copy: editor.copyText(s_text)
		if b_con_copy: print s_text
# end of class
