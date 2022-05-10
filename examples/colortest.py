#!/usr/bin/env python

#-------------------------------------------------------------------------------
# colortest.py: carapace color test
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
import time
import sys 

sys.path.insert(0, '../' )

import carapace

from carapace.colormap import Colors
from carapace.event    import KeyboardGenerator
from carapace.shell    import Shell
from carapace.widget   import Text, List

#-------------------------------------------------------------------------------
# Class
#-------------------------------------------------------------------------------
  
class	TestShell(Shell):
    def	__init__(self):
	Shell.__init__(self)

	self.title_text	 = Text('TestShell', 0, curses.A_REVERSE)
	self.color_list	 = List()
	self.menu_text	 = Text('j:down k:up', 0, curses.A_REVERSE)
	self.status_text = Text(' ')

	self.add_widget(self.title_text)
	self.add_widget(self.color_list)
	self.add_widget(self.menu_text)
	self.add_widget(self.status_text)

	self.add_event_generator(KeyboardGenerator())
	
	self.add_event_handler('cmd-select-down', 
	    lambda shell, event, data:	shell.color_list.select_down())
	self.add_event_handler('cmd-select-up',
	    lambda shell, event, data:	shell.color_list.select_up())
	
	self.add_event_handler('cmd-select-page-down',
	    lambda shell, event, data:	shell.color_list.select_page_down())
	self.add_event_handler('cmd-select-page-up',
	    lambda shell, event, data:	shell.color_list.select_page_up())
	self.add_event_handler('cmd-quit', 
	    lambda shell, event, data: shell.exit(0))
	
	self.add_event_handler('cmd-any-key-press', self.cmd_any_key_press)
	
	for i in xrange(1, 64):
	    self.color_list.add_widget(
		Text(str(i) + ' ' + Colors[i%8] + '/' + Colors[i/8], i))
	
	self.draw_widgets()
    
    #---------------------------------------------------------------------------

    def	cmd_any_key_press(self, shell, event, data):
	color_list = self.color_list
	color_list_size = len(color_list.widgets)

	self.status_text.value  = 'Color: '
	self.status_text.value += str(color_list.selected_widget_index())
	self.status_text.value += '/' + str(color_list_size)

	self.set_refresh_screen(True)

    #---------------------------------------------------------------------------

    def	run(self):
	self.do_loop()

#-------------------------------------------------------------------------------
# Main Execution
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    ts = TestShell()
    ts.run()

#-------------------------------------------------------------------------------
# vim: sts=4 sw=4 ts=8 ft=python
#-------------------------------------------------------------------------------
