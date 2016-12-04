#!/usr/bin/python3.5

"""
To display "The Matrix(tm)" style display of flowing green random letters.
This was coded after trying the excellent example called "cmatrix".
I was running the following version:

 CMatrix version 1.2a by Chris Allegretta (compiled 21:43:16, Sep  6 2015)
 Email: cmatrix@asty.org  Web: http://www.asty.org/cmatrix

This version is coded in Python3, using Curses to display characters at
any position in the terminal window.  I've not been coding in Python for
long so don't expect too much fancyness :-)

Author: Paul Hornsey
Email: paul@1partcarbon.co.uk
Date: 3rd December, 2016

Copyright: 1partCarbon Ltd. 2016
"""

import curses
import string
import random
import time


class MatrixEffect():
    def __init__(self):
        self.stdscr = curses.initscr()

        curses.curs_set(0)   # Hide the cursor

        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)

        self.stdscr.nodelay(1)  # To allow getch() to not pause
        curses.noecho()

        scr_size = self.stdscr.getmaxyx()
        self.width = scr_size[1]
        self.height = scr_size[0]
        self.columns = self.create_columns()
        self.effect_writters = self.create_effect_writters()

    def get_height(self):
        return self.height

    def create_columns(self):
        columns = []
        for col in range(0, self.width):
            columns.append(CharsColumn(self, col))
        return columns

    def create_effect_writters(self):
        effect_writters = []
        for col in self.columns:
            effect_writters.append(EffectWritter(col))
        return effect_writters

    def _is_lower_right_position(self, row, col):
        return row == self.height - 1 and col == self.width - 1

    def write_char_at(self, row_index, col_index, character, color_pair_index):
        if self._is_lower_right_position(row_index, col_index):
            # Insert to avoid cursor overflow
            self.stdscr.insstr(row_index, col_index, character,
                               curses.color_pair(color_pair_index))
        else:
            self.stdscr.addstr(row_index, col_index, character,
                               curses.color_pair(color_pair_index))

    def start_loop(self):
        key_press = -1
        while key_press < 0:
            key_press = self.stdscr.getch()

            if key_press == curses.KEY_RESIZE:
                # End loop if the screen is resized
                break

            for writter in self.effect_writters:
                writter.down_one_step()
                if writter.finished():
                    writter.reset()

            self.stdscr.refresh()
            time.sleep(.05)

        curses.endwin()


class CharsColumn():
    def __init__(self, screen, col_index):
        self.screen = screen
        self.screen_height = screen.get_height()
        self.col_index = col_index
        self.chars = []
        for i in range(self.screen_height):
            self.chars.append('*')

    def get_height(self):
        return self.screen_height

    def read_char(self, row_index):
        if row_index >= 0 and row_index < self.screen_height:
            return self.chars[row_index]
        else:
            return ''

    def write_char(self, row_index, character, colour_pair_index):
        if row_index >= 0 and row_index < self.screen_height:
            self.chars[row_index] = character
            self.screen.write_char_at(row_index, self.col_index, character,
                                      colour_pair_index)


class EffectWritter():
    def __init__(self, chars_column):
        self.chars_column = chars_column
        self.length = self.get_random_length()
        self.current_row = 0

    def reset(self):
        self.length = self.get_random_length()
        self.current_row = -1

    def get_random_length(self):
        return random.randint(5, self.chars_column.get_height())

    def down_one_step(self):
        self.current_row += 1
        self.blank_head()
        self.write_random_bright_char()
        self.darken_last_char()

    def finished(self):
        return self.last_char_row() > self.chars_column.get_height()

    def last_char_row(self):
        return self.current_row - self.length

    def bright_char_row(self):
        return self.last_char_row() + 1

    def blank_head(self):
        self.chars_column.write_char(self.current_row, ' ', 1)

    def random_printable(self):
        return random.choice(
                string.digits + string.ascii_letters + string.punctuation)

    def write_random_bright_char(self):
        self.chars_column.write_char(
                 self.bright_char_row(), self.random_printable(), 2)

    def darken_last_char(self):
        current_char = self.chars_column.read_char(self.last_char_row())
        self.chars_column.write_char(self.last_char_row(), current_char, 1)


if __name__ == "__main__":
    matrix_effect = MatrixEffect()
    matrix_effect.start_loop()
