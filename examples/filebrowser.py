#!/usr/bin/env python

#-------------------------------------------------------------------------------
# filebrowser.py: simple filebrowser
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
import time
import re
import sys 

sys.path.insert(0, '../')

import carapace

from carapace.colormap import ColorMap
from carapace.event    import KeyboardGenerator
from carapace.shell    import Shell
from carapace.widget   import Text, FileList, FileText, EditText

#-------------------------------------------------------------------------------
# Classes
#-------------------------------------------------------------------------------
  
class	FileBrowser(Shell):

    def	__init__(self):
	Shell.__init__(self)
	
	self.title_text	 = Text(
	    'File Browser: .', ColorMap['WHITE/BLUE'], curses.A_BOLD)
	self.file_list	 = FileList()
	self.menu_text	 = Text(
	    'j:down k:up q:quit', ColorMap['WHITE/BLUE'], curses.A_BOLD)
	self.status_text = Text(' ')
	self.edit_text	 = EditText('> ')

	self.add_widget(self.title_text)
	self.add_widget(self.file_list)
	self.add_widget(self.menu_text)
	self.add_widget(self.status_text)

	self.kbd_gen = KeyboardGenerator()
	self.kbd_gen.get_mode('cmd').append_keymap({
	    ord('e')	: 'edit-selected',
	    ord('J')	: 'move-selected-item-down',
	    ord('K')	: 'move-selected-item-up',
	    })

	self.add_event_generator(self.kbd_gen)

	self.kbd_gen.auto_register_handlers(self, ['cmd', 'edt'])
	
	self.file_list.change_directory(os.environ['PWD'])
	self.status_text.set_value(self.file_list.pwd)
	
	self.draw_widgets()
    
    #---------------------------------------------------------------------------
   
    # Command Mode Handlers
    
    def	cmd_any_key_press(self, shell, event, data):
	self.status_text.set_value(self.file_list.get_selected_widget().value)
	self.set_refresh_screen(True)
    
    def	cmd_unknown_key_press(self, shell, event, data):
	self.status_text.set_value('Unknown key: ' + str(data))
	self.set_refresh_screen(True)

    def cmd_select_down(self, shell, event, data):
	self.file_list.select_down()
    
    def cmd_select_up(self, shell, event, data):
	self.file_list.select_up()
    
    def cmd_select_page_down(self, shell, event, data):
	self.file_list.select_page_down()
    
    def cmd_select_page_up(self, shell, event, data):
	self.file_list.select_page_up()

    def cmd_edit_selected(self, shell, event, data):
	value = self.file_list.get_selected_widget().value
	if (os.path.isfile(value)):
	    os.system('$EDITOR "' + value + '"')
	    self.refresh_widgets()
    
    def cmd_enter(self, shell, event, data):
	value = self.file_list.get_selected_widget().value
	if (os.path.isfile(value)):
	    os.system('$PAGER "' + value + '"')
	    self.refresh_widgets()
	else:
	    self.file_list.change_directory(value)
	    self.title_text.set_value('File Browser: ' + self.file_list.pwd)
    
    def cmd_move_selected_item_down(self, shell, event, data):
	self.file_list.move_widget_down(self.file_list.get_selected_widget_index())
	self.file_list.select_down()
    
    def cmd_move_selected_item_up(self, shell, event, data):
	self.file_list.move_widget_up(self.file_list.get_selected_widget_index())
	self.file_list.select_up()
    
    def cmd_toggle_mode(self, shell, event, data):
	self.kbd_gen.set_mode('edt')
	self.widgets[3]	= self.edit_text

    def cmd_quit(self, shell, event, data):
	self.exit(0)
    
    #---------------------------------------------------------------------------
   
    # Edit Mode Handlers
    
    def	edt_any_key_press(self, shell, event, data):
	if re.compile('[-_./a-zA-Z0-9]').match(curses.keyname(data)):
	    self.edit_text.buffer += curses.keyname(data)
	self.set_refresh_screen(True)
    
    def	edt_backspace(self, shell, event, data):
	self.edit_text.buffer = self.edit_text.buffer[:-1]
    
    def	edt_enter(self, shell, event, data):
	self.file_list.change_directory(self.edit_text.value)
	self.edt_toggle_mode(shell, event, data)
    
    def	edt_toggle_mode(self, shell, event, data):
	self.widgets[3]	= self.status_text
	self.kbd_gen.set_mode('cmd')

    #---------------------------------------------------------------------------

    def	run			(self):
	self.do_loop()

#-------------------------------------------------------------------------------
# Main Execution
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    fb = FileBrowser()
    fb.run()

#-------------------------------------------------------------------------------
# vim: sts=4 sw=4 ts=8 ft=python
#-------------------------------------------------------------------------------
