#!/usr/bin/env python

#-------------------------------------------------------------------------------
# shell.py: carapace shell module
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
import signal
import sys
import time

import carapace

#-------------------------------------------------------------------------------
# Classes
#-------------------------------------------------------------------------------

class	Shell:
    """	Turtle shell class
	
	Event Handlers { EVENT_TYPE : [ EVENT_HANDLER_FUNC, ... ], ... }
	EVENT_HANDLER_FUNC = (self, event, data)
    """
    
    #---------------------------------------------------------------------------
    # Constructor and Initialization
    #---------------------------------------------------------------------------

    def	__init__(self, black_is_default=True):
	""" Create carapace shell"""
	self.screen	    = curses.initscr()
	self.refresh_screen = False

	self.black_is_default = black_is_default
	self._initialize_tty()
	self._initialize_colors()
	
	self.event_handlers	= {}
	self.event_generators	= []
	self.events = []

	self.widgets = []

	signal.signal(signal.SIGWINCH, 
	    lambda signum, frame: self.refresh_widgets()) 

    #---------------------------------------------------------------------------

    def _initialize_tty(self):
	""" Initialize TTY"""
	self.screen.keypad(1)
	self.screen.nodelay(1)
	curses.cbreak()
	curses.curs_set(0)
	curses.noecho()

    def _initialize_colors(self):
	if curses.has_colors():
	    curses.start_color()
	    curses.use_default_colors()
	    carapace.colormap.initialize_color_map(self.black_is_default)
    
    #---------------------------------------------------------------------------
    # Destructor, Reset, and Exit
    #---------------------------------------------------------------------------

    def	__del__(self):
	""" Delete carapace shell"""
	self._reset_tty()
    
    #---------------------------------------------------------------------------

    def _reset_tty(self):
	""" Reset TTY"""
	self.screen.keypad(0)
	self.screen.nodelay(0)
	
	curses.nocbreak()
	curses.curs_set(1)
	curses.echo()

	curses.endwin()
    
    #---------------------------------------------------------------------------

    def	exit(self, n):
	self._reset_tty()
	sys.exit(n)
    
    #---------------------------------------------------------------------------
    # Event Engine
    #---------------------------------------------------------------------------

    def add_event_handler(self, event, handler):
	if not self.event_handlers.has_key(event):
	    self.event_handlers[event] = []
	self.event_handlers[event].append(handler)
    
    #---------------------------------------------------------------------------
    
    def add_event_generator(self, generator):
	self.event_generators.append(generator)
    
    #---------------------------------------------------------------------------
   
    def generate_events(self):
	self.events = []

	for generator in self.event_generators:
	    generator.generate(self)
    
    #---------------------------------------------------------------------------
    
    def queue_event(self, event, data=None):
	if self.event_handlers.has_key(event):
	    for handler in self.event_handlers[event]:
		self.events.append((event, data, handler))
    
    #---------------------------------------------------------------------------
  
    def	process_events(self):
	for event, data, handler in self.events:
	    handler(self, event, data)

    #---------------------------------------------------------------------------
    
    def do_loop(self):
	while True:
	    self.do_one_loop()
    
    #---------------------------------------------------------------------------

    def	do_one_loop(self):
	if self.refresh_screen:
	    self.draw_widgets()

	self.refresh_screen = False

	self.generate_events()
	self.process_events()

	if self.refresh_screen:
	    self.draw_widgets()

    #---------------------------------------------------------------------------
    # Widget Manager
    #---------------------------------------------------------------------------

    def	add_widget(self, widget):
	self.widgets.append(widget)
    
    #---------------------------------------------------------------------------

    def	draw_widgets(self):
	row = 0
	for widget in self.widgets:
	    if widget.auto_height == True:
		other_heights = sum(
			[w.height for w in self.widgets if w != widget])
		widget.height	= curses.LINES - other_heights
	    
	    widget.draw(self.screen, row)
	    row += widget.height

	self.screen.refresh()
    
    #---------------------------------------------------------------------------

    def refresh_widgets(self):
	curses.endwin()
	self.screen.refresh()

	self._initialize_tty()
	
	curses.LINES, curses.COLS = self.screen.getmaxyx()
	self.draw_widgets()
    
    #---------------------------------------------------------------------------
	
    def set_refresh_screen(self, refresh_screen):
	self.refresh_screen = refresh_screen

#-------------------------------------------------------------------------------
# vim: sts=4 sw=4 ts=8 ft=python
#-------------------------------------------------------------------------------
