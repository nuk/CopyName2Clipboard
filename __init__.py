# Inspired in the version place at http://projects.kflorence.com/programming/rhythmbox
# This plugin copies the current song name to clipboard

import os
import rb
import rhythmdb
import gtk, pygtk

pygtk.require('2.0')

ui_definition = """
<ui>

    <popup name="RhythmboxIndicator">
    	<menuitem name="CopyNamePopup" action="CopyCurrentName"/>
    </popup>
    <menubar name="MenuBar">
	<menu name="ViewMenu" action="View">
	  <menuitem name="CopyNamePopup" action="CopyCurrentName"/>
	</menu>
    </menubar>
</ui>"""

STREAM_SONG_ARTIST = 'rb:stream-song-artist'
STREAM_SONG_TITLE  = 'rb:stream-song-title'
STREAM_SONG_ALBUM  = 'rb:stream-song-album'

class CopyName2Clipboard (rb.Plugin):
  def __init__(self):
    rb.Plugin.__init__(self)

  # What to do on activation
  def activate(self, shell):
    self.shell = shell
    self.db = self.shell.props.db
    self.clipboard = gtk.clipboard_get()

    # Reference the shell player
    sp = shell.props.shell_player

    manager = shell.get_player().get_property('ui-manager')
    self.__action = gtk.Action('CopyCurrentName', _('Copy Current Name...'),
                                _('Copy Current Name of the song to...'), '')
    self.__action.connect('activate', self.set_clipboard_action, shell)

    self.__action_group = gtk.ActionGroup('CopyCurrentNameActionGroup')
    self.__action_group.add_action(self.__action)
    manager.insert_action_group(self.__action_group)

    self.__ui_id = manager.add_ui_from_string(ui_definition)
    manager.ensure_update()
  
  # What to do on deactivation
  def deactivate(self, shell):    
    # Disconnect signals
    sp = shell.props.shell_player
    
    # Remove references
    del self.db
    del self.shell
    del self.current_entry
    del self.clipboard

    shell.get_ui_manager().remove_action_group(self.__action_group)
    shell.get_ui_manager().remove_ui(self.__ui_id)
    shell.get_ui_manager().ensure_update()

    del self.__action_group
    del self.__action



  # Set clipboard to current song info
  def set_clipboard_action(self, action, shell):

    self.current_entry = shell.get_player().get_playing_entry()

    db = self.shell.get_property ("db")
    self.current_artist = db.entry_get (self.current_entry, rhythmdb.PROP_ARTIST)
    self.current_title  = db.entry_get (self.current_entry, rhythmdb.PROP_TITLE)
    self.current_album  = db.entry_get (self.current_entry, rhythmdb.PROP_ALBUM)

    if self.current_entry.get_entry_type().category == rhythmdb.ENTRY_STREAM:
      self.current_artist = db.entry_request_extra_metadata (self.current_entry, STREAM_SONG_ARTIST)
      self.current_title  = db.entry_request_extra_metadata (self.current_entry, STREAM_SONG_TITLE)
      self.current_album  = db.entry_request_extra_metadata (self.current_entry, STREAM_SONG_ALBUM)
    else:
      self.current_artist = db.entry_get (self.current_entry, rhythmdb.PROP_ARTIST)
      self.current_title  = db.entry_get (self.current_entry, rhythmdb.PROP_TITLE)
      self.current_album  = db.entry_get (self.current_entry, rhythmdb.PROP_ALBUM)

    clip_text = None

    if (self.current_album and self.current_artist and self.current_title):
    	clip_text = (("%s - %s - %s")%(self.current_album, self.current_artist, self.current_title))
    elif (self.current_artist and self.current_title):
    	clip_text = (("%s - %s")%(self.current_artist, self.current_title))
    elif (self.current_title):
    	clip_text = (("%s")%(self.current_title))

    self.clipboard.set_text(clip_text)

    # make our data available to other applications
    self.clipboard.store()
