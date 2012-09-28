
# This file dictates which colours are used for syntax highlighting.
# I advise using the <Preferences> dialog, but edit away here if you prefer.

# To edit colours, change the '#0000FF' variables.
# To edit the fonts, change the 'monospace' entry.

from pango import UNDERLINE_SINGLE
from pango import WEIGHT_BOLD


DEFAULT_STYLES = {
	'DEFAULT':      {'font'      : 'monospace'},
	'comment':      {'foreground': '#0000FF'},
	'preprocessor': {'foreground': '#A020F0'},
	'keyword':      {'foreground': '#DC0000',
					 'weight'    :  WEIGHT_BOLD},
	'special':      {'foreground': 'turquoise'},
	'mark1':        {'foreground': '#008B8B'},
	'mark2':        {'foreground': '#6A5ACD'},
	'string':       {'foreground': '#FF00FF'},
	'number':       {'foreground': '#FF00FF'},
	'datatype':     {'foreground': '#0000B6',
					 'weight'    :  WEIGHT_BOLD},
	'function':     {'foreground': '#008A8C'},

	'link':         {'foreground': '#0000FF',
					 'underline' :  UNDERLINE_SINGLE} }

