#!/usr/bin/env python

#-------------------------------------------------------------------------------
# event.py: carapace event module
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
import select
import sys
import time

import carapace
import carapace.keys as keys

#-------------------------------------------------------------------------------
# Classes
#-------------------------------------------------------------------------------

class	Generator():

    def	__init__(self, event):
	self.event = event

    def	generate(self):
	""" Generate Event """

#-------------------------------------------------------------------------------

class	TimerGenerator(Generator):

    def	__init__(self, event, delay=0.25):
	Generator.__init__(self, event)
	self.delay	= delay
	self.start_time	= None
    
    def	generate(self, shell):
	if self.start_time is None:
	    self.start_time = time.time()
   
	delay	    = self.delay
	start_time  = self.start_time
	end_time    = time.time()

	if (end_time - start_time) > delay:
	    shell.queue_event(self.event)
	    self.start_time = time.time()

#-------------------------------------------------------------------------------

class	KeyboardGenerator(Generator):
    DEFAULT_ANY_KEY_EVENT     = 'any-key-press'
    DEFAULT_UNKNOWN_KEY_EVENT = 'unknown-key-press'
    
    #---------------------------------------------------------------------------

    def	__init__(self, timeout=1.0, modes=None, any_key_event=None, 
		 unknown_key_event=None):
	Generator.__init__(self, 'kbd-press-event')
	self.timeout = timeout
	self.modes   = modes or [DefaultCommandMode, DefaultEditorMode]
	self.mode_index = 0

	from carapace.event import KeyboardGenerator as KG

	self.any_key_event     = any_key_event or KG.DEFAULT_ANY_KEY_EVENT
	self.unknown_key_event = unknown_key_event or \
	    KG.DEFAULT_UNKNOWN_KEY_EVENT
    
    #---------------------------------------------------------------------------
    
    def	generate(self, shell):
	input   = []
	timeout = self.timeout

	try:
	    input, output, exc = select.select([sys.stdin], [], [], timeout)
	except select.error, e:
	    if e[0] != 4: raise	# EINTR = 4

	if len(input) > 0:
	    data = shell.screen.getch()

	    keymap = self.get_mode().keymap
	    prefix = self.get_mode().prefix

	    if keymap.has_key(data):
		shell.queue_event(prefix + '-' + keymap[data], data)
	    else:
		shell.queue_event(prefix + '-' + self.unknown_key_event, data)
	    
	    shell.queue_event(prefix + '-' + self.any_key_event, data)
    
    #---------------------------------------------------------------------------
   
    def auto_register_handlers(self, shell, prefixes):
	if isinstance(prefixes, str): prefixes = [prefixes]

	for p in prefixes:
	    for f in dir(shell):
		if f.startswith(p + '_'):
		    event = f.replace('_', '-')
		    handler = getattr(shell, f)
		    shell.add_event_handler(event, handler)
    
    #---------------------------------------------------------------------------
    
    def get_mode(self, prefix=None):
	if prefix is None:
	    return self.modes[self.mode_index]
	else:
	    for m in self.modes:
		if m.prefix == prefix:
		    return m
	    return None
    
    def set_mode(self, prefix):
	for i, m in enumerate(self.modes):
	    if m.prefix == prefix:
		self.mode_index = i
		return

    def get_mode_index(self):
	return self.mode_index
    
    def set_mode_index(self, index):
	self.mode_index = index

    def rotate_to_next_mode(self):
	self.mode_index = (self.mode_index + 1) % len(self.modes)
    
    def rotate_to_prev_mode(self):
	self.mode_index = self.mode_index - 1
	if self.mode_index < 0: self.mode_index = len(self.modes) - 1

#-------------------------------------------------------------------------------

class	KeyboardMode:
    def	__init__(self, prefix=None, keymap=None):
	self.prefix = prefix or ''
	self.keymap = keymap or {} 
    
    #---------------------------------------------------------------------------

    def get_keymap(self):
	return self.keymap
    
    def set_keymap(self, keymap):
	self.keymap = keymap

    def append_keymap(self, keymap):
	self.keymap.update(keymap)
    
    def clear_keymap(self):
	self.keymap = {}
    
    #---------------------------------------------------------------------------

    def get_prefix(self):
	return self.prefix
    
    def set_prefix(self, prefix):
	self.prefix = prefix

#-------------------------------------------------------------------------------
# Global Variables
#-------------------------------------------------------------------------------

DefaultCommandMode = KeyboardMode(
    'cmd',
    { keys.KEY_ENTER   : 'enter',
      ord('j')         : 'select-down',
      curses.KEY_DOWN  : 'select-down',
      ord('k')         : 'select-up',
      curses.KEY_UP    : 'select-up',
      curses.KEY_NPAGE : 'select-page-down',
      curses.KEY_PPAGE : 'select-page-up',
      keys.KEY_ESC     : 'toggle-mode',
      ord('q')         : 'quit',
    })

#-------------------------------------------------------------------------------

DefaultEditorMode = KeyboardMode(
    'edt' ,
    { keys.KEY_BKSP  : 'backspace',
      keys.KEY_ENTER : 'enter',
      keys.KEY_ESC   : 'toggle-mode',
    })

#-------------------------------------------------------------------------------
# vim: sts=4 sw=4 ts=8 ft=python
#-------------------------------------------------------------------------------
