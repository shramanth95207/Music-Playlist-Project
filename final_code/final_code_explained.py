
# ===== IMPORTS =====
import wx
# Import wxPython GUI framework for creating windows and widgets

import wx.media
# Import media module for audio/video playback functionality

import os
# Import operating system module for file path operations


# ===== CLASS DEFINITION =====
class MusicPlayer(wx.Frame):
    # Define MusicPlayer class that inherits from wx.Frame (top-level window)
    # wx.Frame is the main window container
    
    def __init__(self):
        # Constructor method - runs when MusicPlayer object is created
        
        # Create main window with title and size
        super().__init__(None, title="Music Player", size=(900, 600))
        # Call parent class (wx.Frame) constructor
        # None = no parent window
        # title = window title bar text
        # size = (width=900 pixels, height=600 pixels)
        
        self.SetBackgroundColour(wx.Colour(10, 10, 10))
        # Set window background color to very dark black (RGB: 10,10,10)
        
        panel = wx.Panel(self)
        # Create panel (container) inside the frame to hold all widgets
        
        panel.SetBackgroundColour(wx.Colour(10, 10, 10))
        # Set panel background to same dark black color
        
        # ===== DATA STORAGE =====
        self.tracks = []
        # List to store full file paths of all loaded audio files
        
        self.display_names = []
        # List to store song names displayed in filtered playlist
        
        self.current_index = -1
        # Index of currently playing song (-1 means no song is playing)
        
        self.is_dragging = False
        # Boolean flag to check if user is dragging progress slider
        
        # ===== SEARCH BAR WIDGET =====
        self.search_ctrl = wx.SearchCtrl(panel, style=wx.TE_PROCESS_ENTER)
        # Create search bar widget in panel
        # wx.SearchCtrl = text input with search functionality and clear button
        # wx.TE_PROCESS_ENTER = process Enter key events
        
        self.search_ctrl.SetBackgroundColour(wx.Colour(20, 20, 20))
        # Set search bar background to dark gray (RGB: 20,20,20)
        
        self.search_ctrl.SetForegroundColour(wx.Colour(0, 255, 100))
        # Set search bar text color to light green (RGB: 0,255,100)
        
        # ===== PLAYLIST WIDGET =====
        self.playlist = wx.ListBox(panel)
        # Create listbox widget to display list of songs
        # wx.ListBox = widget that displays selectable list items
        
        self.playlist.SetBackgroundColour(wx.Colour(15, 15, 15))
        # Set playlist background to almost black (RGB: 15,15,15)
        
        self.playlist.SetForegroundColour(wx.Colour(50, 255, 100))
        # Set playlist text color to bright light green (RGB: 50,255,100)
        
        # ===== NOW PLAYING LABEL =====
        now_playing_label = wx.StaticText(panel, label=">> NOW PLAYING")
        # Create static text label (non-editable text)
        # label = text to display: ">> NOW PLAYING"
        
        font_title = now_playing_label.GetFont()
        # Get current font from label widget
        
        font_title.PointSize = 15
        # Set font size to 15 points (larger text)
        
        font_title = font_title.Bold()
        # Make font bold (thicker letters)
        
        now_playing_label.SetFont(font_title)
        # Apply the modified bold font to label
        
        now_playing_label.SetForegroundColour(wx.Colour(0, 255, 100))
        # Set label text color to light green
        
        # ===== CURRENT SONG NAME DISPLAY =====
        self.now_playing = wx.StaticText(panel, label="No track loaded")
        # Create text widget to display current song name
        # Initial text: "No track loaded" (shown when no song is playing)
        
        self.now_playing.SetFont(font_title)
        # Apply same bold font as "NOW PLAYING" label
        
        self.now_playing.SetForegroundColour(wx.Colour(100, 255, 150))
        # Set text color to lighter green (RGB: 100,255,150)
        
        # ===== MUSIC ICON DISPLAY PANEL =====
        display_panel = wx.Panel(panel)
        # Create sub-panel inside main panel to hold the music icon
        
        display_panel.SetBackgroundColour(wx.Colour(20, 20, 20))
        # Set background to dark gray (RGB: 20,20,20)
        
        display_sizer = wx.BoxSizer(wx.VERTICAL)
        # Create vertical sizer (arranges items top-to-bottom)
        
        try:
            # Try to load the music icon image
            
            icon_path = r"e:\Python\Lib\py\music_icon.png"
            # Raw string (r prefix) path to music_icon.png file
            # r prefix prevents backslashes from being escaped
            
            icon_bitmap = wx.Bitmap(icon_path, wx.BITMAP_TYPE_PNG)
            # Load PNG image file as wx.Bitmap object
            # wx.Bitmap = image data in memory
            
            if icon_bitmap.IsOk():
                # Check if image loaded successfully (not corrupted/missing)
                
                icon_image = icon_bitmap.ConvertToImage()
                # Convert bitmap to wx.Image for scaling operations
                
                icon_image = icon_image.Scale(200, 200, wx.IMAGE_QUALITY_HIGH)
                # Resize image to 200x200 pixels with high quality scaling
                
                icon_bitmap = wx.Bitmap(icon_image)
                # Convert scaled image back to bitmap
                
                icon_display = wx.StaticBitmap(display_panel, bitmap=icon_bitmap)
                # Create static bitmap widget to display the scaled icon
                # wx.StaticBitmap = widget that displays an image (can't be edited)
                
            else:
                # If image failed to load
                
                icon_display = wx.StaticText(display_panel, label="[NO IMAGE]")
                # Show text "[NO IMAGE]" instead of image
                
                icon_display.SetForegroundColour(wx.Colour(0, 255, 100))
                # Set text color to light green
                
        except Exception as e:
            # Catch any errors that occur during image loading
            
            print(f"Error loading icon: {e}")
            # Print error message to console for debugging
            
            icon_display = wx.StaticText(display_panel, label="[NO IMAGE]")
            # Show "[NO IMAGE]" text if any error occurs
            
            icon_display.SetForegroundColour(wx.Colour(0, 255, 100))
            # Set text color to light green
        
        display_sizer.Add(icon_display, 1, wx.ALIGN_CENTER | wx.ALL, 20)
        # Add icon to vertical sizer
        # 1 = proportion (take extra space if available)
        # wx.ALIGN_CENTER = center the icon
        # wx.ALL = add 20px padding on all sides
        # 20 = padding amount in pixels
        
        display_panel.SetSizer(display_sizer)
        # Apply sizer layout to display_panel
        
        # ===== MEDIA CONTROL (HIDDEN) =====
        self.mc = wx.media.MediaCtrl(panel, style=wx.SIMPLE_BORDER)
        # Create media control widget for audio playback
        # wx.media.MediaCtrl = handles audio/video playback
        # wx.SIMPLE_BORDER = simple border style
        
        self.mc.Hide()
        # Hide the media control (it's used for audio only, no visual needed)
        
        # ===== CONTROL BUTTONS =====
        btn_load = wx.Button(panel, label="LOAD SONGS")
        # Create button to load songs (opens file dialog)
        
        btn_prev = wx.Button(panel, label="<< Prev")
        # Create button to play previous song
        
        btn_play = wx.Button(panel, label="PLAY/PAUSE")
        # Create button to toggle play/pause
        
        btn_next = wx.Button(panel, label="NEXT >>")
        # Create button to play next song
        
        # ===== BUTTON STYLING =====
        for btn in [btn_load, btn_prev, btn_play, btn_next]:
            # Loop through all 4 buttons
            
            btn.SetBackgroundColour(wx.Colour(0, 150, 75))
            # Set button background to dark green (RGB: 0,150,75)
            
            btn.SetForegroundColour(wx.WHITE)
            # Set button text color to white
            
            font = btn.GetFont()
            # Get current button font
            
            font.PointSize = 10
            # Set font size to 10 points
            
            btn.SetFont(font)
            # Apply modified font to button
        
        # ===== VOLUME SLIDER =====
        vol_label = wx.StaticText(panel, label="VOLUME")
        # Create label text "VOLUME"
        
        vol_label.SetForegroundColour(wx.Colour(0, 255, 100))
        # Set label text color to light green
        
        self.vol_slider = wx.Slider(
            panel, value=70, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL
        )
        # Create horizontal slider for volume control
        # value=70 = initial position at 70%
        # minValue=0 = minimum volume 0%
        # maxValue=100 = maximum volume 100%
        # wx.SL_HORIZONTAL = slider goes left-to-right
        
        self.vol_slider.SetBackgroundColour(wx.Colour(20, 20, 20))
        # Set slider background to dark gray
        
        # ===== PROGRESS SLIDER (SEEK BAR) =====
        prog_label = wx.StaticText(panel, label="PROGRESS")
        # Create label text "PROGRESS"
        
        prog_label.SetForegroundColour(wx.Colour(0, 255, 100))
        # Set label text color to light green
        
        self.pos_slider = wx.Slider(
            panel, value=0, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL
        )
        # Create progress slider (seek bar)
        # value=0 = starts at beginning (0%)
        # minValue=0 = start of song
        # maxValue=100 = end of song (will be updated to actual length)
        
        self.pos_slider.SetBackgroundColour(wx.Colour(20, 20, 20))
        # Set slider background to dark gray
        
        # ===== TIME LABEL =====
        self.time_label = wx.StaticText(panel, label="00:00 / 00:00")
        # Create text to display current_time / total_time
        # Initial: "00:00 / 00:00" (0 seconds / 0 seconds)
        
        font_time = self.time_label.GetFont()
        # Get current font from time label
        
        font_time.PointSize = 11
        # Set font size to 11 points
        
        self.time_label.SetFont(font_time)
        # Apply modified font to time label
        
        self.time_label.SetForegroundColour(wx.Colour(50, 255, 150))
        # Set text color to bright light green
        
        # ===== LAYOUT SETUP (SIZERS) =====
        # Sizers automatically arrange widgets in rows/columns
        
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # Create main horizontal sizer (left | right layout)
        
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        # Create left vertical sizer (top-to-bottom for playlist side)
        
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        # Create right vertical sizer (top-to-bottom for player side)
        
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # Create horizontal sizer for buttons (left-to-right)
        
        vol_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # Create horizontal sizer for volume (label + slider)
        
        prog_sizer = wx.BoxSizer(wx.VERTICAL)
        # Create vertical sizer for progress (label + slider + time)
        
        # ===== LEFT SIDE LAYOUT =====
        playlist_title = wx.StaticText(panel, label="PLAYLIST")
        # Create "PLAYLIST" title text
        
        font_pl = playlist_title.GetFont()
        # Get font from playlist title
        
        font_pl.PointSize = 12
        # Set font size to 12 points
        
        font_pl = font_pl.Bold()
        # Make font bold
        
        playlist_title.SetFont(font_pl)
        # Apply bold font to title
        
        playlist_title.SetForegroundColour(wx.Colour(0, 255, 100))
        # Set text color to light green
        
        left_sizer.Add(playlist_title, 0, wx.ALL, 8)
        # Add title to left sizer
        # 0 = fixed size (no extra space)
        # wx.ALL = 8px padding on all sides
        
        left_sizer.Add(self.search_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        # Add search bar to left sizer
        # 0 = fixed height
        # wx.EXPAND = stretch horizontally
        # wx.LEFT | wx.RIGHT | wx.BOTTOM = padding on left, right, bottom (8px)
        
        left_sizer.Add(self.playlist, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        # Add playlist to left sizer
        # 1 = take remaining vertical space (grow to fill)
        # wx.EXPAND = stretch both directions
        # 8px padding on left, right, bottom
        
        # ===== BUTTON LAYOUT =====
        btn_sizer.Add(btn_load, 0, wx.ALL, 5)
        # Add LOAD button with 5px padding
        
        btn_sizer.Add(btn_prev, 0, wx.ALL, 5)
        # Add PREV button with 5px padding
        
        btn_sizer.Add(btn_play, 0, wx.ALL, 5)
        # Add PLAY/PAUSE button with 5px padding
        
        btn_sizer.Add(btn_next, 0, wx.ALL, 5)
        # Add NEXT button with 5px padding
        
        # ===== VOLUME LAYOUT =====
        vol_sizer.Add(vol_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        # Add volume label
        # 0 = fixed width
        # wx.ALIGN_CENTER_VERTICAL = center label vertically
        # wx.RIGHT = 10px padding on right
        
        vol_sizer.Add(self.vol_slider, 1, wx.EXPAND)
        # Add slider
        # 1 = take remaining horizontal space
        # wx.EXPAND = fill available space
        
        # ===== PROGRESS LAYOUT =====
        prog_sizer.Add(prog_label, 0, wx.LEFT | wx.TOP, 5)
        # Add progress label with 5px left and top padding
        
        prog_sizer.Add(self.pos_slider, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)
        # Add slider with 5px padding on left, right, top
        
        prog_sizer.Add(self.time_label, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        # Add time label (centered) with 5px padding
        
        # ===== RIGHT SIDE LAYOUT =====
        right_sizer.Add(now_playing_label, 0, wx.ALL, 8)
        # Add "NOW PLAYING" label with 8px padding
        
        right_sizer.Add(self.now_playing, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        # Add song name display with 8px padding
        
        right_sizer.Add(display_panel, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        # Add music icon display (takes remaining space)
        
        right_sizer.Add(prog_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
        # Add progress section
        
        right_sizer.Add(btn_sizer, 0, wx.CENTER | wx.ALL, 5)
        # Add buttons (centered) with 5px padding
        
        right_sizer.Add(vol_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        # Add volume section with 8px padding
        
        # ===== MAIN LAYOUT =====
        main_sizer.Add(left_sizer, 1, wx.EXPAND | wx.ALL, 5)
        # Add left side (playlist)
        # 1 = take 1 part of horizontal space
        # Expands to fill space, 5px padding
        
        main_sizer.Add(right_sizer, 2, wx.EXPAND | wx.ALL, 5)
        # Add right side (player)
        # 2 = take 2 parts of horizontal space (twice as wide as left)
        
        panel.SetSizer(main_sizer)
        # Apply main sizer layout to panel
        
        # ===== TIMER SETUP =====
        self.timer = wx.Timer(self)
        # Create timer object
        # Fires events at regular intervals (for progress bar updates)
        
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        # Connect timer events to on_timer event handler
        # When timer fires, call self.on_timer()
        
        # ===== EVENT BINDINGS =====
        # Connect button clicks to event handler functions
        
        btn_load.Bind(wx.EVT_BUTTON, self.on_load)
        # When LOAD button clicked, call self.on_load()
        
        btn_prev.Bind(wx.EVT_BUTTON, self.on_prev)
        # When PREV button clicked, call self.on_prev()
        
        btn_play.Bind(wx.EVT_BUTTON, self.on_play_pause)
        # When PLAY button clicked, call self.on_play_pause()
        
        btn_next.Bind(wx.EVT_BUTTON, self.on_next)
        # When NEXT button clicked, call self.on_next()
        
        self.playlist.Bind(wx.EVT_LISTBOX_DCLICK, self.on_playlist_dclick)
        # When song double-clicked in playlist, call self.on_playlist_dclick()
        
        self.vol_slider.Bind(wx.EVT_SLIDER, self.on_volume_change)
        # When volume slider moved, call self.on_volume_change()
        
        self.pos_slider.Bind(wx.EVT_LEFT_DOWN, self.on_slider_down)
        # When user starts dragging progress slider, call self.on_slider_down()
        
        self.pos_slider.Bind(wx.EVT_LEFT_UP, self.on_slider_up)
        # When user stops dragging progress slider, call self.on_slider_up()
        
        self.pos_slider.Bind(wx.EVT_SLIDER, self.on_seek)
        # When progress slider moves, call self.on_seek()
        
        self.search_ctrl.Bind(wx.EVT_TEXT, self.on_search)
        # When user types in search bar, call self.on_search()
        
        self.search_ctrl.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.on_search_cancel)
        # When user clicks X button in search, call self.on_search_cancel()
        
        # ===== INITIALIZATION =====
        self.update_playlist_display()
        # Refresh playlist display (empty initially)
        
        self.mc.SetVolume(self.vol_slider.GetValue() / 100)
        # Set audio volume to initial slider position (70/100 = 0.7)
        
        self.Show()
        # Make window visible to user

    # ===== HELPER FUNCTIONS =====

    def update_playlist_display(self, filter_text=""):
        """Rebuild the playlist listbox based on filter text"""
        # Function parameter: filter_text = search term (empty string by default)
        
        self.playlist.Clear()
        # Delete all items from playlist listbox
        
        self.display_names = []
        # Clear the display names list
        
        filter_text = filter_text.lower()
        # Convert search term to lowercase for case-insensitive matching
        
        for full_path in self.tracks:
            # Loop through all loaded track file paths
            
            name = os.path.basename(full_path)
            # Extract just the filename from full path
            # Example: "C:/Music/song.mp3" → "song.mp3"
            
            if not filter_text or filter_text in name.lower():
                # If no search term OR filename contains search term
                
                self.display_names.append(name)
                # Add filename to display list
                
                self.playlist.Append(name)
                # Add filename to listbox display

    def load_track(self, index):
        """Load and play a track by its index in tracks list"""
        # Function parameter: index = position in self.tracks list
        
        if index < 0 or index >= len(self.tracks):
            # If index is invalid (less than 0 OR past end of list)
            return
            # Exit function without doing anything
        
        try:
            self.mc.Stop()
            # Stop any currently playing audio
        except Exception:
            pass
            # Ignore any errors
        
        self.timer.Stop()
        # Stop progress bar updates
        
        path = self.tracks[index]
        # Get full file path of track at given index
        
        if self.mc.Load(path):
            # Try to load audio file into media control
            
            self.current_index = index
            # Update current track index
            
            self.now_playing.SetLabel(os.path.basename(path))
            # Update "now playing" text with song name
            
            def setup_slider():
                # Nested function to setup progress slider after loading
                
                length = self.mc.Length()
                # Get total song length in milliseconds
                
                if length and length > 0:
                    # If length is valid (not 0 or None)
                    
                    self.pos_slider.SetRange(0, length)
                    # Set slider range from 0 to song length
                    
                    self.pos_slider.SetValue(0)
                    # Set slider to start (position 0)
                    
                    self.time_label.SetLabel(f"{self.ms_to_time(0)} / {self.ms_to_time(length)}")
                    # Update time display: "00:00 / total_time"
                    
                    self.mc.Play()
                    # Start playback
                    
                    self.timer.Start(250)
                    # Start timer (fires every 250ms to update progress)
                    
                else:
                    # If length not ready yet
                    
                    wx.CallLater(100, setup_slider)
                    # Retry function in 100ms (wait for metadata to load)
            
            setup_slider()
            # Call setup function
            
        else:
            # If track failed to load
            
            wx.MessageBox(f"Unable to load {path}", "Error", wx.OK | wx.ICON_ERROR)
            # Show error dialog box

    # ===== EVENT HANDLERS =====

    def on_load(self, event):
        """Handle LOAD SONGS button click"""
        # Parameter: event = button click event object
        
        dlg = wx.FileDialog(
            self,
            message="Choose audio files",
            wildcard="Audio files (*.mp3;*.wav;*.ogg;*.flac)|*.mp3;*.wav;*.ogg;*.flac|All files (*.*)|*.*",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE,
        )
        # Create file picker dialog
        # self = parent window
        # message = instruction text shown in dialog
        # wildcard = file type filters (audio formats)
        # style = dialog options (OPEN = open files, MUST_EXIST = only existing files, MULTIPLE = select many files)
        
        if dlg.ShowModal() == wx.ID_OK:
            # If user clicked OK (not Cancel)
            
            paths = dlg.GetPaths()
            # Get list of selected file paths
            
            for p in paths:
                # Loop through each selected file
                
                self.tracks.append(p)
                # Add full path to tracks list
            
            self.update_playlist_display(self.search_ctrl.GetValue())
            # Refresh playlist display with current search filter
            
            if self.current_index == -1 and self.tracks:
                # If no song currently playing AND tracks were loaded
                
                self.playlist.SetSelection(0)
                # Highlight first song in list
                
                self.load_track(0)
                # Load and play first track
        
        dlg.Destroy()
        # Close and delete dialog

    def on_prev(self, event):
        """Handle PREV button click - play previous song"""
        
        if not self.tracks:
            # If no tracks loaded
            return
            # Exit function
        
        new_index = (self.current_index - 1) % len(self.tracks)
        # Calculate previous index with wraparound
        # % operator wraps: -1 % 5 = 4 (goes from end to beginning)
        
        self.current_index = new_index
        # Update current index
        
        name = os.path.basename(self.tracks[new_index])
        # Get filename of previous track
        
        idx = self.playlist.FindString(name)
        # Find position of this song in listbox display
        
        if idx != wx.NOT_FOUND:
            # If song is visible in filtered list
            
            self.playlist.SetSelection(idx)
            # Highlight it in listbox
        
        self.load_track(new_index)
        # Load and play the track

    def on_next(self, event):
        """Handle NEXT button click - play next song"""
        
        if not self.tracks:
            # If no tracks loaded
            return
            # Exit function
        
        new_index = (self.current_index + 1) % len(self.tracks)
        # Calculate next index with wraparound
        # % operator wraps: 5 % 5 = 0 (goes from end to beginning)
        
        self.current_index = new_index
        # Update current index
        
        name = os.path.basename(self.tracks[new_index])
        # Get filename of next track
        
        idx = self.playlist.FindString(name)
        # Find position of this song in listbox display
        
        if idx != wx.NOT_FOUND:
            # If song is visible in filtered list
            
            self.playlist.SetSelection(idx)
            # Highlight it in listbox
        
        self.load_track(new_index)
        # Load and play the track

    def on_play_pause(self, event):
        """Handle PLAY/PAUSE button click"""
        
        if self.mc.GetState() != wx.media.MEDIASTATE_PLAYING:
            # If not currently playing
            
            self.mc.Play()
            # Start playback
            
            self.timer.Start(250)
            # Start timer (update progress every 250ms)
            
        else:
            # If currently playing
            
            self.mc.Pause()
            # Pause playback
            
            self.timer.Stop()
            # Stop timer

    def on_playlist_dclick(self, event):
        """Handle double-click on song in playlist"""
        
        sel = self.playlist.GetSelection()
        # Get index of selected item in listbox
        
        if sel == wx.NOT_FOUND:
            # If nothing selected
            return
            # Exit function
        
        name = self.playlist.GetString(sel)
        # Get filename from selected listbox item
        
        for i, p in enumerate(self.tracks):
            # Loop through all tracks with index
            
            if os.path.basename(p) == name:
                # If this track's filename matches selected song
                
                self.load_track(i)
                # Load and play this track
                
                self.current_index = i
                # Update current index
                
                break
                # Exit loop

    def on_volume_change(self, event):
        """Handle volume slider movement"""
        
        volume = self.vol_slider.GetValue() / 100
        # Get slider value (0-100) and convert to decimal (0.0-1.0)
        # Example: 70 / 100 = 0.7 (70% volume)
        
        try:
            self.mc.SetVolume(volume)
            # Set audio volume to decimal value
        except Exception:
            pass
            # Ignore any errors

    def on_slider_down(self, event):
        """Handle when user starts dragging progress slider"""
        
        self.is_dragging = True
        # Set flag to indicate user is dragging
        
        self.timer.Stop()
        # Stop progress updates while dragging

    def on_slider_up(self, event):
        """Handle when user stops dragging progress slider"""
        
        self.is_dragging = False
        # Clear dragging flag
        
        if self.mc.GetState() == wx.media.MEDIASTATE_PLAYING:
            # If song is playing
            
            self.timer.Start(250)
            # Resume progress updates

    def on_seek(self, event):
        """Handle progress slider movement (user seeking)"""
        
        if not self.is_dragging:
            # If user is not dragging (this prevents multiple seeks during drag)
            return
            # Exit function
        
        length = self.mc.Length()
        # Get total song length (milliseconds)
        
        if length > 0:
            # If song length is valid
            
            pos = self.pos_slider.GetValue()
            # Get current slider position
            
            pos = max(0, min(pos, length))
            # Clamp position between 0 and song length
            # max(0, ...) = ensure not less than 0
            # min(..., length) = ensure not more than length
            
            try:
                self.mc.Seek(pos)
                # Jump to this position in song
            except Exception:
                pass
                # Ignore errors
            
            self.time_label.SetLabel(f"{self.ms_to_time(pos)} / {self.ms_to_time(length)}")
            # Update time display to show new position

    def on_timer(self, event):
        """Handle timer events - runs every 250ms during playback"""
        
        if self.mc.GetState() == wx.media.MEDIASTATE_PLAYING:
            # If song is currently playing
            
            length = self.mc.Length()
            # Get total song length (milliseconds)
            
            if length > 0:
                # If valid song length
                
                pos = self.mc.Tell()
                # Get current playback position (milliseconds)
                
                if pos < 0:
                    # If position is invalid (negative)
                    pos = 0
                    # Reset to 0
                    
                elif pos > length:
                    # If position past end of song
                    pos = length
                    # Cap at song length
                
                if not self.is_dragging:
                    # If user is not dragging slider
                    
                    self.pos_slider.SetRange(0, length)
                    # Ensure slider range is correct
                    
                    self.pos_slider.SetValue(pos)
                    # Update slider to current position
                
                self.time_label.SetLabel(f"{self.ms_to_time(pos)} / {self.ms_to_time(length)}")
                # Update time display (e.g., "1:23 / 3:45")
                
                if pos >= length - 500 and self.current_index is not None:
                    # If song almost finished (within 500ms of end)
                    
                    self.on_next(None)
                    # Auto-play next song
        else:
            # If not playing
            
            self.timer.Stop()
            # Stop timer

    def ms_to_time(self, ms):
        """Convert milliseconds to MM:SS format"""
        # Parameter: ms = milliseconds value
        
        try:
            ms = int(ms)
            # Convert to integer (in case it's float)
            
            if ms <= 0:
                # If zero or negative
                return "00:00"
                # Return zero time
            
            s = ms // 1000
            # Convert milliseconds to seconds using integer division
            # Example: 85000 // 1000 = 85 seconds
            
            m = s // 60
            # Get minutes from seconds
            # Example: 85 // 60 = 1 minute
            
            s = s % 60
            # Get remaining seconds after removing minutes
            # % operator gets remainder
            # Example: 85 % 60 = 25 seconds (1:25)
            
            return f"{m:02d}:{s:02d}"
            # Format as MM:SS with leading zeros
            # :02d = pad with zeros to 2 digits
            # Example: "01:25"
            
        except Exception:
            return "00:00"
            # Return "00:00" if any error occurs

    def on_search(self, event):
        """Handle search bar text changes"""
        
        term = self.search_ctrl.GetValue()
        # Get text from search box
        
        self.update_playlist_display(term)
        # Update playlist with search filter applied

    def on_search_cancel(self, event):
        """Handle clicking X button in search bar"""
        
        self.search_ctrl.SetValue("")
        # Clear search text
        
        self.update_playlist_display("")
        # Show all songs again


if __name__ == "__main__":
    """Entry point - runs when script is executed directly"""
    
    app = wx.App(False)
    # Create application object
    # False = don't show splash screen
    
    MusicPlayer()
    # Create and display main window
    
    app.MainLoop()
    # Start event loop (waits for user interaction, runs until window closes)