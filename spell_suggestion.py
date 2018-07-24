# coding: utf-8



def generate_spell_suggestions(dic, word, directions, tables, language):
	suggestions = set()
	for d, _ in directions:
		fromDanish = (d == "fromDanish")
		for t, _ in tables:
			suggestions = suggestions.union(dic.spell_suggestions(word, fromDanish, t, language))


