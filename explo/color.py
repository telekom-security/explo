# coding: utf-8
# https://github.com/reorx/python-terminal-color/blob/master/color.py
import sys

NO_COLOR = False

def make_color(code):
    def color_func(s):
        if not sys.stdout.isatty() or NO_COLOR:
            return s

        tpl = '\x1b[{}m{}\x1b[0m'
        return tpl.format(code, s)
    return color_func

red = make_color(31)
green = make_color(32)
yellow = make_color(33)
blue = make_color(34)
magenta = make_color(35)
cyan = make_color(36)

bold = make_color(1)
underline = make_color(4)

grayscale = {(i - 232): make_color('38;5;' + str(i)) for i in range(232, 256)}
