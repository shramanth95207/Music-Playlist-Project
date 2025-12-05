import wx
import wx.media
import os

# Import libraries:
# wx - GUI framework for building graphical interfaces
# wx.media - Media playback module (audio/video)
# os - Operating system module for file path operations


class MusicPlayer(wx.Frame):
    """Main Music Player window class that inherits from wx.Frame (top-level window)"""
    
    def __init__(self):
        """Constructor - initializes the Music Player window and all components"""
        
        # Create main window: title = "Music Player", size = 700x420 pixels
        super().__init__(None, title="Music Player", size=(700, 420))
        
        # Create a panel (container) inside the frame to hold all widgets
        panel = wx.Panel(self)

        # --- Data Storage ---
        self.tracks = []          # List to store full file paths of all loaded songs
        self.display_names = []   # List to store song names displayed in filtered playlist
        self.current_index = -1   # Index of currently playing song (-1 = no song playing)

        # --- Media Control Widget ---
        # wx.media.MediaCtrl: Core widget that handles audio playback
        self.mc = wx.media.MediaCtrl(panel, style=wx.SIMPLE_BORDER)

        # --- Search Bar Widget ---
        # wx.SearchCtrl: Text input field with search functionality and clear button
        self.search_ctrl = wx.SearchCtrl(panel, style=wx.TE_PROCESS_ENTER)

        # --- Playlist Widget ---
        # wx.ListBox: Displays list of song names that user can click/double-click
        self.playlist = wx.ListBox(panel)

        # --- Control Buttons ---
        btn_load = wx.Button(panel, label="Load songs")      # Opens file dialog to add songs
        btn_prev = wx.Button(panel, label="<< Prev")         # Goes to previous song
        btn_play = wx.Button(panel, label="Play/Pause")      # Toggles play/pause state
        btn_next = wx.Button(panel, label="Next >>")         # Goes to next song

        # --- Volume Slider ---
        # Controls audio volume (0-100)
        self.vol_slider = wx.Slider(
            panel, value=70, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL
        )
        vol_label = wx.StaticText(panel, label="Volume")     # Label for volume slider

        # --- Progress Slider (Seek Bar) ---
        # Allows user to jump to specific position in song (0-100% or 0-length in ms)
        self.pos_slider = wx.Slider(
            panel, value=0, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL
        )
        
        # Time label displays current time and total duration (e.g., "1:23 / 3:45")
        self.time_label = wx.StaticText(panel, label="00:00 / 00:00")

        # --- Layout Management (Sizers) ---
        # Sizers automatically arrange widgets in rows/columns
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)    # Main horizontal layout (left + right)
        left_sizer = wx.BoxSizer(wx.VERTICAL)      # Left side: search + playlist (vertical)
        right_sizer = wx.BoxSizer(wx.VERTICAL)     # Right side: player controls (vertical)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)     # Button row: 4 buttons in a line
        vol_sizer = wx.BoxSizer(wx.HORIZONTAL)     # Volume row: label + slider

        # LEFT SIDE: Add search bar and playlist to left_sizer
        left_sizer.Add(self.search_ctrl, 0, wx.EXPAND | wx.ALL, 5)
        # Add with 5 pixels padding (wx.ALL) and expand horizontally (wx.EXPAND)
        # Proportion = 0 (fixed height)
        
        left_sizer.Add(self.playlist, 1, wx.EXPAND | wx.ALL, 5)
        # Proportion = 1 means take remaining space vertically
        # This makes the playlist grow to fill available space

        # BUTTON ROW: Add 4 control buttons horizontally
        btn_sizer.Add(btn_load, 0, wx.ALL, 5)
        btn_sizer.Add(btn_prev, 0, wx.ALL, 5)
        btn_sizer.Add(btn_play, 0, wx.ALL, 5)
        btn_sizer.Add(btn_next, 0, wx.ALL, 5)

        # VOLUME ROW: Add volume label and slider
        vol_sizer.Add(vol_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        # vol_label: fixed width, centered vertically, 5px right margin
        
        vol_sizer.Add(self.vol_slider, 1, wx.EXPAND)
        # vol_slider: takes remaining horizontal space, expands to fill

        # RIGHT SIDE: Add all components vertically
        right_sizer.Add(self.mc, 0, wx.EXPAND | wx.ALL, 5)
        # Media player display area
        
        right_sizer.Add(self.pos_slider, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        # Progress slider (seek bar)
        
        right_sizer.Add(self.time_label, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        # Time display (centered)
        
        right_sizer.Add(btn_sizer, 0, wx.CENTER)
        # Button row (centered horizontally)
        
        right_sizer.Add(vol_sizer, 0, wx.EXPAND | wx.ALL, 5)
        # Volume row (expanded horizontally)

        # MAIN LAYOUT: Combine left and right sides
        main_sizer.Add(left_sizer, 1, wx.EXPAND)    # Left takes 1/3 of width
        main_sizer.Add(right_sizer, 2, wx.EXPAND)   # Right takes 2/3 of width

        # Apply the main layout to the panel
        panel.SetSizer(main_sizer)

        # --- Timer for Progress Updates ---
        # Timer fires every 250ms to update progress bar and time display during playback
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)

        # --- Event Bindings (Connections) ---
        # Connect button clicks to event handler functions
        btn_load.Bind(wx.EVT_BUTTON, self.on_load)
        btn_prev.Bind(wx.EVT_BUTTON, self.on_prev)
        btn_play.Bind(wx.EVT_BUTTON, self.on_play_pause)
        btn_next.Bind(wx.EVT_BUTTON, self.on_next)

        # Playlist double-click loads that song
        self.playlist.Bind(wx.EVT_LISTBOX_DCLICK, self.on_playlist_dclick)
        
        # Slider movements trigger seek updates
        self.vol_slider.Bind(wx.EVT_SLIDER, self.on_volume_change)
        self.pos_slider.Bind(wx.EVT_SLIDER, self.on_seek)

        # Search bar events: text changes filter list, cancel button clears search
        self.search_ctrl.Bind(wx.EVT_TEXT, self.on_search)
        self.search_ctrl.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.on_search_cancel)

        # Initialize display
        self.update_playlist_display()

        # Set initial volume to 70%
        self.mc.SetVolume(self.vol_slider.GetValue() / 100)

        # Display the window
        self.Show()

    # -------------- HELPER FUNCTIONS -----------------

    def update_playlist_display(self, filter_text=""):
        """
        Rebuilds the playlist display with optional text filter
        - Clears current list
        - Loops through all tracks and adds matching songs
        - filter_text: search term to filter songs (case-insensitive)
        """
        self.playlist.Clear()  # Clear all items from listbox
        self.display_names = []  # Reset display names list

        filter_text = filter_text.lower()  # Convert search to lowercase for case-insensitive matching
        
        for full_path in self.tracks:  # Loop through all loaded tracks
            name = os.path.basename(full_path)  # Extract filename from full path
            
            # If no filter OR filename contains filter text, add to display
            if not filter_text or filter_text in name.lower():
                self.display_names.append(name)
                self.playlist.Append(name)  # Add to listbox

    def load_track(self, index):
        """
        Loads and plays a track by index
        - Validates index
        - Stops current playback
        - Loads new track using MediaCtrl
        - Sets up progress slider range
        - Starts playback
        """
        # Check if index is valid (0 to end of tracks list)
        if index < 0 or index >= len(self.tracks):
            return

        # Stop any currently playing audio
        try:
            self.mc.Stop()
        except Exception:
            pass
        
        # Stop the timer (progress updates)
        self.timer.Stop()

        path = self.tracks[index]  # Get full path of track to load
        
        # Try to load the track into MediaCtrl
        if self.mc.Load(path):
            self.current_index = index  # Update current track index

            # Setup slider function (delayed to wait for track info)
            def setup_slider():
                length = self.mc.Length()  # Get track duration in milliseconds
                
                # If length is available and > 0
                if length and length > 0:
                    self.pos_slider.SetRange(0, length)  # Set slider max to track length
                    self.pos_slider.SetValue(0)  # Set slider to start (0)
                    # Update time label to show "00:00 / total_time"
                    self.time_label.SetLabel(f"{self.ms_to_time(0)} / {self.ms_to_time(length)}")
                    self.mc.Play()  # Start playback
                    self.timer.Start(250)  # Start timer to update every 250ms
                else:
                    # If length not ready, try again in 100ms
                    wx.CallLater(100, setup_slider)

            setup_slider()  # Call setup function
        else:
            # Show error if track failed to load
            wx.MessageBox(f"Unable to load {path}", "Error", wx.OK | wx.ICON_ERROR)

    # -------------- EVENT HANDLERS -------------------

    def on_load(self, event):
        """
        Opens file dialog to select and load multiple audio files
        - Creates file dialog for audio formats (mp3, wav, ogg, flac)
        - Adds selected files to tracks list
        - Refreshes playlist display
        - Auto-plays first song if none was playing
        """
        # Create file selection dialog
        dlg = wx.FileDialog(
            self,
            message="Choose audio files",
            wildcard="Audio files (*.mp3;*.wav;*.ogg;*.flac)|*.mp3;*.wav;*.ogg;*.flac|All files (*.*)|*.*",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE,
        )
        
        # If user clicked OK (not Cancel)
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()  # Get list of selected file paths
            
            # Add each selected file to tracks list
            for p in paths:
                self.tracks.append(p)
            
            # Refresh playlist display with current search filter
            self.update_playlist_display(self.search_ctrl.GetValue())
            
            # If no song is currently playing, auto-select and play first track
            if self.current_index == -1 and self.tracks:
                self.playlist.SetSelection(0)  # Highlight first song in list
                self.load_track(0)  # Load and play it
        
        dlg.Destroy()  # Close dialog

    def on_prev(self, event):
        """
        Plays previous song in playlist (wraps around to end if at start)
        """
        if not self.tracks:
            return  # Do nothing if no tracks loaded
        
        # Calculate previous index with wraparound
        new_index = (self.current_index - 1) % len(self.tracks)
        self.current_index = new_index
        
        # Update visible selection in listbox if song is visible
        name = os.path.basename(self.tracks[new_index])
        idx = self.playlist.FindString(name)
        if idx != wx.NOT_FOUND:
            self.playlist.SetSelection(idx)
        
        self.load_track(new_index)  # Load and play the song

    def on_next(self, event):
        """
        Plays next song in playlist (wraps around to start if at end)
        """
        if not self.tracks:
            return  # Do nothing if no tracks loaded
        
        # Calculate next index with wraparound
        new_index = (self.current_index + 1) % len(self.tracks)
        self.current_index = new_index
        
        # Update visible selection in listbox if song is visible
        name = os.path.basename(self.tracks[new_index])
        idx = self.playlist.FindString(name)
        if idx != wx.NOT_FOUND:
            self.playlist.SetSelection(idx)
        
        self.load_track(new_index)  # Load and play the song

    def on_play_pause(self, event):
        """
        Toggles between play and pause states
        - If not playing: start playback and timer
        - If playing: pause playback and stop timer
        """
        # Check if currently playing
        if self.mc.GetState() != wx.media.MEDIASTATE_PLAYING:
            self.mc.Play()  # Start playback
            self.timer.Start(250)  # Start progress update timer
        else:
            self.mc.Pause()  # Pause playback
            self.timer.Stop()  # Stop progress updates

    def on_playlist_dclick(self, event):
        """
        Event handler for double-clicking a song in the playlist
        - Gets selected song name from listbox
        - Finds corresponding full path in tracks list
        - Loads and plays that track
        """
        sel = self.playlist.GetSelection()  # Get index of selected item
        if sel == wx.NOT_FOUND:
            return  # No selection
        
        name = self.playlist.GetString(sel)  # Get song name from listbox
        
        # Find the full path matching this song name in tracks list
        for i, p in enumerate(self.tracks):
            if os.path.basename(p) == name:
                self.load_track(i)  # Load and play
                self.current_index = i
                break

    def on_volume_change(self, event):
        """
        Updates audio volume when slider moves
        - Gets slider value (0-100)
        - Converts to decimal (0.0-1.0)
        - Sets MediaCtrl volume
        """
        volume = self.vol_slider.GetValue() / 100  # Convert 0-100 to 0.0-1.0
        try:
            self.mc.SetVolume(volume)  # Set audio volume
        except Exception:
            pass  # Ignore errors

    def on_seek(self, event):
        """
        Handles progress slider movement (user seeking to new position)
        - Gets new position from slider
        - Clamps value between 0 and track length
        - Seeks to that position in track
        - Updates time label
        """
        length = self.mc.Length()  # Get track length in ms
        
        if length > 0:
            pos = self.pos_slider.GetValue()  # Get slider position
            pos = max(0, min(pos, length))  # Ensure pos is between 0 and length
            
            try:
                self.mc.Seek(pos)  # Jump to this position in track
            except Exception:
                pass
            
            # Update time label to show new position
            self.time_label.SetLabel(f"{self.ms_to_time(pos)} / {self.ms_to_time(length)}")

    def on_timer(self, event):
        """
        Timer event handler - fires every 250ms during playback
        - Updates progress slider to current position
        - Updates time label
        - Auto-plays next song when current song ends
        """
        # Check if currently playing
        if self.mc.GetState() == wx.media.MEDIASTATE_PLAYING:
            length = self.mc.Length()  # Total track length (ms)
            
            if length > 0:
                pos = self.mc.Tell()  # Current playback position (ms)
                
                # Clamp position between 0 and length
                if pos < 0:
                    pos = 0
                elif pos > length:
                    pos = length
                
                # Update slider to show current position
                self.pos_slider.SetRange(0, length)
                self.pos_slider.SetValue(pos)
                
                # Update time label (e.g., "1:23 / 3:45")
                self.time_label.SetLabel(f"{self.ms_to_time(pos)} / {self.ms_to_time(length)}")

                # If song is almost finished (within 500ms of end), play next
                if pos >= length - 500 and self.current_index is not None:
                    self.on_next(None)  # Auto-play next track
        else:
            self.timer.Stop()  # Stop timer if not playing

    def ms_to_time(self, ms):
        """
        Converts milliseconds to MM:SS format
        - Input: milliseconds (e.g., 85000)
        - Output: "1:25" (1 minute 25 seconds)
        - Handles errors gracefully, returns "00:00" if invalid
        """
        try:
            ms = int(ms)  # Convert to integer
            if ms <= 0:
                return "00:00"
            
            s = ms // 1000  # Convert ms to seconds
            m = s // 60     # Get minutes (integer division)
            s = s % 60      # Get remaining seconds (modulo)
            
            # Format as MM:SS (e.g., "01:25")
            return f"{m:02d}:{s:02d}"
        except Exception:
            return "00:00"  # Return default if error

    # --------- SEARCH EVENT HANDLERS ----------

    def on_search(self, event):
        """
        Live search filter - called when user types in search bar
        - Gets search term from input field
        - Filters playlist to show only matching songs
        """
        term = self.search_ctrl.GetValue()  # Get text from search box
        self.update_playlist_display(term)  # Update playlist with filter

    def on_search_cancel(self, event):
        """
        Clear search - called when user clicks X button in search bar
        - Clears search text
        - Shows all songs again
        """
        self.search_ctrl.SetValue("")  # Clear search text
        self.update_playlist_display("")  # Reset to show all songs


if __name__ == "__main__":
    """
    Entry point of program
    - Creates wx.App (application object)
    - Creates MusicPlayer instance (window)
    - Starts event loop (MainLoop waits for user interaction)
    """
    app = wx.App(False)  # Create application (False = don't show splash screen)
    MusicPlayer()  # Create and display main window
    app.MainLoop()  # Start event loop (runs until window closes)
