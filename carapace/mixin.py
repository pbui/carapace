#!/usr/bin/env python

#-------------------------------------------------------------------------------
# mixin.py: carapace mixin module
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

import carapace

#-------------------------------------------------------------------------------
# Classes
#-------------------------------------------------------------------------------

class	NotebookMixIn:
    def	__init__(self, current_tab_id=0, tab_widget_index = 0, tabs=None):
	self.tabs = tabs or []
	self.tab_widget_index = tab_widget_index
	self.current_tab_id = current_tab_id

	self.switch_to_tab(self.current_tab_id)
	
    #---------------------------------------------------------------------------

    def add_tabs(self, tabs):
	self.tabs.extend(tabs)
	for i, t in enumerate(self.tabs): t.set_id(i)

    def get_current_tab(self):
	return self.tabs[self.current_tab_id]
    
    def get_current_tab_id(self):
	return self.current_tab_id

    def set_tab_widget_index(self, index):
	self.tab_widget_index = index
    
    #---------------------------------------------------------------------------

    def rotate_to_next_tab(self):
	self.switch_to_tab((self.current_tab_id + 1) % len(self.tabs))
    
    def rotate_to_prev_tab(self):
	new_index = self.current_tab_id - 1
	
	if new_index < 0: 
	    new_index = len(self.tabs) - 1

	self.switch_to_tab(new_index)
    
    def switch_to_tab(self, index, normalize=False):
	if normalize: index += 1

	if 0 <= index and index < len(self.tabs) and hasattr(self, 'widgets'):
	    self.current_tab_id = index
	    self.widgets[self.tab_widget_index] = self.tabs[index]

#-------------------------------------------------------------------------------

class	TabMixIn:
    def __init__(self, id=0, name=None, message=None):
	self.id = id
	self.name = name or ''
	self.message = message or ''
	
    def get_title(self):
	return "[%d] %s: %s" % (self.id + 1, self.name, self.message)

    def set_id(self, id):
	self.id = id
    
    def set_name(self, name):
	self.name = name
    
    def set_message(self, message):
	self.message = message

#-------------------------------------------------------------------------------
# vim: sts=4 sw=4 ts=8 ft=python
#-------------------------------------------------------------------------------
