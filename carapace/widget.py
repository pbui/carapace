#!/usr/bin/env python

#-------------------------------------------------------------------------------
# widget.py: carapace widget module
#-------------------------------------------------------------------------------

# Copyright (c) 2008 Peter Bui. All Rights Reserved.

# This software is provided 'as-is', without any express or implied warranty.
# In no event will the authors be held liable for any damages arising from the
# use of this software.

# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:

# 1. The origin of this software must not be misrepresented; you must not claim
# that you wrote the original software. If you use this software in a product,
# an acknowledgment in the product documentation would be appreciated but is
# not required.

# 2. Altered source versions must be plainly marked as such, and must not be
# misrepresented as being the original software.  

# 3. This notice may not be removed or altered from any source distribution.

# Peter Bui <peter.j.bui@gmail.com>

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------

import curses
import os

import carapace

#-------------------------------------------------------------------------------
# Classes
#-------------------------------------------------------------------------------

class	Widget:
    """	Turtle base widget
    """

    def	__init__(self, height=None, auto_height=None):
	"""Create widget"""
	self.height = height
	self.auto_height = auto_height

    def	__del__(self):
	"""Delete widget"""

    def draw(self):
	"""Draw widget"""
    
    def	highlight(self, attribute_mod=curses.A_REVERSE):
	self.attribute_mod = attribute_mod
    
    def	unhighlight(self):
	self.attribute_mod = curses.A_NORMAL

#-------------------------------------------------------------------------------

class	Text(Widget):
    """	Turtle text widget
    """

    def	__init__(self, value=None, color_pair=0, attribute=0):
	Widget.__init__(self, 1)
	self.value	   = value
	self.attribute	   = attribute
	self.attribute_mod = 0
	self.color_pair	   = color_pair

    def draw(self, screen, row):
	if self.value:
	    value      = self.value.ljust(curses.COLS, ' ')
	    attribute  = self.attribute | curses.color_pair(self.color_pair)
	    attribute |= self.attribute_mod
	    try:
		screen.addstr(row, 0, value, attribute)
	    except curses.error:
		pass
		
	    try:
		screen.move(row, 0)
	    except curses.error:
		pass
    
    def get_value(self):
	return self.value
    
    def set_value(self, value):
	self.value = value

#-------------------------------------------------------------------------------

class	List(Widget):
    """ Turtle list widget
	
	As of right now, scrolling and selecting don't handle widgets with
	height > 1 properly.
    """

    def	__init__(self, background_widget=Text(' ', 0), enable_highlight=True,
		 enable_embolden=False):
	Widget.__init__(self, 0, True)
	
	self.clear_widgets()

	self.enable_highlight  = enable_highlight
	self.enable_embolden   = enable_embolden
	self.background_widget = background_widget
	self.color_pair	= 0
	self.attribute	= 0
	self.highlight_mod = curses.A_REVERSE | curses.A_BOLD
	self.embolden_mod  = curses.A_BOLD
    
    #--------------------------------------------------------------------------
    
    def	add_widget(self, widget):
	self.widgets.append(widget)
    
    def	delete_widget(self, widget):
	self.widgets.remove(widget)

    def	clear_widgets(self):
	self.widgets	   = []
	self.select_index  = 0
	self.scroll_index  = 0
	self.embolden_list = []

    def	get_selected_widget(self):
	if self.select_index < 0 or self.select_index == len(self.widgets):
	    return None
	else:
	    return self.widgets[self.get_selected_widget_index()]
    
    def get_selected_widget_index(self):
	return self.select_index + self.scroll_index

    def	get_widget_index(self, widget):
	if isinstance(widget, int):
	    return widget
	else:
	    for i, w in enumerate(self.widgets):
		if w is widget: return i
	    return -1
    
    #--------------------------------------------------------------------------
  
    def move_widget_up(self, widget):
	widget_index = self.get_widget_index(widget)
	self.swap_widgets(widget_index, widget_index - 1)
    
    def move_widget_down(self, widget):
	widget_index = self.get_widget_index(widget)
	self.swap_widgets(widget_index, widget_index + 1)

    def swap_widgets(self, widget1, widget2):
	widget1_index = self.get_widget_index(widget1)
	widget2_index = self.get_widget_index(widget2)

	if widget1_index < 0 or widget1_index >= len(self.widgets) or \
	   widget2_index < 0 or widget2_index >= len(self.widgets): 
	    return False

	tmp_widget = self.widgets[widget2_index]
	self.widgets[widget2_index] = self.widgets[widget1_index]
	self.widgets[widget1_index] = tmp_widget

	return True
    
    #--------------------------------------------------------------------------

    def draw(self, screen, row):
	orig_row     = row
	widget_index = 0
	
	select_index = self.select_index
	scroll_index = self.scroll_index

	height = self.height

	for widget in self.widgets[scroll_index:(scroll_index + height)]:
	    if self.enable_embolden:
		try:
		    self.embolden_list.index(scroll_index + widget_index)
		    widget.highlight(self.embolden_mod)
		except ValueError:
		    widget.unhighlight()
		    pass
	    else:
		widget.unhighlight()

	    if self.enable_highlight:
		if widget_index == select_index:
		    widget.highlight(self.highlight_mod)

	    widget.draw(screen, row)

	    widget_index += 1
	    row		 += widget.height

	for i in xrange(0, height - (row - orig_row)):
	    self.background_widget.draw(screen, row + i)
    
    #--------------------------------------------------------------------------

    def	select_down(self, rows=1):
	self.select_index += rows
	if self.select_index >= self.height:
	    self.select_index = self.height - 1
	    self.scroll_down(rows)
	elif self.select_index >= (len(self.widgets) - self.scroll_index):
	    self.select_index = len(self.widgets) - self.scroll_index - 1
    
    def	select_up(self, rows=1):
	self.select_index -= rows
	if self.select_index < 0:
	    self.select_index = 0 
	    self.scroll_up(rows)
    
    def	select_page_down(self):
	adjusted_height = self.height - 1
	if self.select_index == adjusted_height:
	    self.scroll_down(adjusted_height)
	else:
	    while adjusted_height >= (len(self.widgets) - self.scroll_index):
		adjusted_height -= 1 
	    self.select_index = adjusted_height
    
    def	select_page_up(self):
	adjusted_height = self.height - 1
	if self.select_index == 0:
	    self.scroll_up(adjusted_height)
	self.select_index = 0
    
    def	scroll_down(self, rows=1):
	self.scroll_index += rows
	
	if self.scroll_index > 0:
	    while (len(self.widgets) - self.scroll_index < self.height):
		self.scroll_index -= 1
		self.select_index += 1
	
	if self.select_index > self.height - 1:
	    self.select_index = self.height - 1
    
    def	scroll_up(self, rows=1):
	self.scroll_index -= rows
	if self.scroll_index < 0:
	    self.scroll_index = 0

    def	select_widget_at_index(self, index):
	if index > len(self.widgets):
	    index = len(self.widgets) - 1
	elif index < 0:
	    index = 0

	self.scroll_index = (index / self.height) * self.height
	self.select_index = index % self.height
	self.scroll_down(0)

    #--------------------------------------------------------------------------
    
    def search(self, query, ranges, filter=None):
	f = filter or (lambda x, y: x in y)

	if len(self.widgets) == 0: return

	for r in ranges:
	    for i in r:
		if not (i < len(self.widgets)):
		    continue
		if f(query, self.widgets[i].value):
		    self.select_widget_at_index(i)
		    return

    def search_prev(self, query, filter=None):
	file_index = self.scroll_index + self.select_index
	ranges = [xrange(0, file_index), xrange(file_index, len(self.widgets))]
	ranges = [reversed(r) for r in ranges]

	self.search(query, ranges, filter)

    def search_next(self, query, filter=None):
	file_index = self.scroll_index + self.select_index + 1
	ranges = [xrange(file_index, len(self.widgets)), xrange(0, file_index)]
	
	self.search(query, ranges, filter)

#-------------------------------------------------------------------------------

class	FileList(List):
    def change_directory(self, directory):
	directory = os.path.abspath(directory)
	
	try:
	    os.chdir(directory)
	except:
	    return None

	self.pwd = directory
	self.clear_widgets()

	self.add_widget(FileText('..', 'dir', self.color_pair, self.attribute))
	for f in sorted(os.listdir(self.pwd)):
	    f = os.path.abspath(f)
	    if os.path.islink(f):
		self.add_widget(
		    FileText(f, 'link', self.color_pair, self.attribute))
	    elif os.path.isdir(f):
		self.add_widget(
		    FileText(f, 'dir', self.color_pair, self.attribute))
	    else:
		self.add_widget(
		    FileText(f, 'file', self.color_pair, self.attribute))
    
    def search(self, query, ranges, filter=None):
	List.search(self, query, ranges, lambda x, y: x in os.path.basename(y))
    
#-------------------------------------------------------------------------------
  
class	FileText(Text):
    def	__init__(self, file_path=None, file_type=None, color_pair=0,
		 attribute=0):
	Text.__init__(self, file_path, color_pair, attribute)
	self.file_path = file_path
	self.file_type = file_type

    def	draw(self, screen, row):
	self.value = os.path.basename(self.file_path)
	if self.file_type == 'link':
	    self.value += '@'
	elif self.file_type == 'dir':
	    self.value += '/'
	
	Text.draw(self, screen, row)
	self.value = self.file_path

#-------------------------------------------------------------------------------

class	Seperator(Text):
    def	__init__(self, color_pair=0, attribute=0):
	Text.__init__(self, '', color_pair, attribute)
    
    def	draw(self, screen, row):
	for i in xrange(0, curses.COLS):
	    try:
		screen.addch(row, i, curses.ACS_HLINE)
	    except curses.error:
		pass

#-------------------------------------------------------------------------------

class	ProgressBar(Text):
    def	__init__(self, use_percent=False,  color_pair=0, attribute=0):
	Text.__init__(self, '', color_pair, attribute)
	self.use_percent = use_percent
	self.percent_pos = 0
	self.time_length = 0
	self.time_pos	 = 0

    def	set_percent_pos(self, pos):
	self.percent_pos = pos
    
    def	set_time_length(self, length):
	self.time_length = length
    
    def	set_time_pos (self, pos):
	self.time_pos = pos 
    
    def	draw(self, screen, row):
	attribute = self.color_pair | self.attribute

	if self.use_percent:
	    percent_pos_text= "[%02d%%]" % self.percent_pos
	else:
	    pos_min, pos_sec  = (self.time_pos / 60, self.time_pos % 60)
	    len_min, len_sec  = (self.time_length / 60, self.time_length % 60)
	    percent_pos_text  = "[%d:%02d" % (pos_min, pos_sec)
	    percent_pos_text += "/%d:%02d]" % (len_min, len_sec)
	    if self.time_length:
		self.percent_pos = self.time_pos * 100 / self.time_length
	    else:
		self.percent_pos= 0

	progress_length = curses.COLS - len(percent_pos_text)
	percent_length  = int(progress_length * self.percent_pos / 100)

	for i in xrange(0, percent_length):
	    try:
		if i == (percent_length - 1):
		    screen.addch(row, i, 'O')
		else:
		    screen.addch(row, i, '=')
	    except curses.error:
		pass
	
	for i in xrange(percent_length, progress_length):
	    try:
		screen.addch(row, i, curses.ACS_HLINE)
	    except curses.error:
		pass

	try:
	    screen.addstr(row, progress_length, percent_pos_text, attribute) 
	except curses.error:
	    pass

#-------------------------------------------------------------------------------

class	EditText(Text):
    def	__init__(self, prompt, color_pair=0, attribute=0):
	Text.__init__(self, '', color_pair, attribute)
	self.prompt = prompt
	self.clear_buffer()

    def	draw(self, screen, row):
	buffer   = self.buffer
	a_length = (curses.COLS - len(self.prompt))

	if len(buffer) > a_length:
	    buffer = buffer[-a_length:]

	self.value = self.prompt + buffer
	Text.draw(self, screen, row)
	self.value = self.buffer
    
    def clear_buffer(self):
	self.buffer = ''

#-------------------------------------------------------------------------------
# vim: sts=4 sw=4 ts=8 ft=python
#-------------------------------------------------------------------------------
