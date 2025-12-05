import wx                    # Imports wxPython GUI library for all widgets (windows, buttons, sliders, panels) [web:2]
import wx.media              # Imports MediaCtrl for audio/video playback functionality [web:2][web:4]
import os                    # Imports OS module for file path operations (basename extraction) [web:1]

class MusicPlayer(wx.Frame): # Main window class inheriting from wx.Frame [web:2]
    def __init__(self):      # Constructor - runs when MusicPlayer() called [web:1]
        super().__init__(None, title="Music Player", size=(600, 400))  # Creates 600x400 window [web:2]
        panel = wx.Panel(self) # Container panel for all child widgets [web:2]

        # Data storage for tracks (Model)
        self.tracks = []       # List of full file paths (e.g., ['/music/song1.mp3', '/music/song2.mp3']) [web:1]
        self.display_names = []# Names shown in filtered playlist view [web:1]
        self.current_index = -1# -1 = no track selected/playing, 0+ = track index [web:1]

        # Core media player control
        self.mc = wx.media.MediaCtrl(panel, style=wx.SIMPLE_BORDER)  # Audio player engine [web:2][web:4]

        # Search bar for filtering songs
        self.search_ctrl = wx.SearchCtrl(panel, style=wx.TE_PROCESS_ENTER)  # Live search with Enter support [web:1]

        # Playlist display
        self.playlist = wx.ListBox(panel)  # Scrollable song list (double-click to play) [web:1]

        # Control buttons (local variables - only needed for binding)
        btn_load = wx.Button(panel, label="Load songs")     # File dialog trigger [web:2]
        btn_prev = wx.Button(panel, label="<< Prev")        # Previous track (wrap-around) [web:1]
        btn_play = wx.Button(panel, label="Play/Pause")     # Toggle playback [web:2]
        btn_next = wx.Button(panel, label="Next >>")        # Next track (wrap-around) [web:1]

        # Volume control (needs self. for event handling)
        self.vol_slider = wx.Slider(panel, value=50, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL)  # 50% default [web:2][web:6]
        vol_label = wx.StaticText(panel, label="Volume")    # Static text label [web:1]

        # Progress/seek slider (dual purpose)
        self.pos_slider = wx.Slider(panel, value=0, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL)  # Progress + seek [web:2]

        # Layout system (sizers) - automatic positioning/resizing
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)     # Left-right split (1:2 ratio) [web:2]
        left_sizer = wx.BoxSizer(wx.VERTICAL)       # Left column: search+playlist (1/3 width) [web:2]
        right_sizer = wx.BoxSizer(wx.VERTICAL)      # Right column: player+controls (2/3 width) [web:2]
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)      # Horizontal button row [web:2]
        vol_sizer = wx.BoxSizer(wx.HORIZONTAL)      # Label+slider row [web:2]

        # Left panel layout (search + playlist)
        left_sizer.Add(self.search_ctrl, 0, wx.EXPAND | wx.ALL, 5)    # Fixed height, expands width [web:2]
        left_sizer.Add(self.playlist, 1, wx.EXPAND | wx.ALL, 5)      # Grows to fill remaining height [web:2]

        # Button row layout
        btn_sizer.Add(btn_load, 0, wx.ALL, 5)      # Load | Prev | Play | Next (equal width) [web:2]
        btn_sizer.Add(btn_prev, 0, wx.ALL, 5)
        btn_sizer.Add(btn_play, 0, wx.ALL, 5)
        btn_sizer.Add(btn_next, 0, wx.ALL, 5)

        # Volume row layout
        vol_sizer.Add(vol_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)  # Label fixed height [web:2]
        vol_sizer.Add(self.vol_slider, 1, wx.EXPAND)  # Slider fills remaining width [web:2]

        # Right panel assembly
        right_sizer.Add(self.mc, 0, wx.EXPAND | wx.ALL, 5)             # Media visualization area [web:2]
        right_sizer.Add(self.pos_slider, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)  # Progress bar [web:2]
        right_sizer.Add(btn_sizer, 0, wx.CENTER)                       # Buttons centered [web:2]
        right_sizer.Add(vol_sizer, 0, wx.EXPAND | wx.ALL, 5)           # Volume bottom row [web:2]

        # Main layout assembly & activation
        main_sizer.Add(left_sizer, 1, wx.EXPAND)   # Left: 1/3 width [web:2]
        main_sizer.Add(right_sizer, 2, wx.EXPAND)  # Right: 2/3 width [web:2]
        panel.SetSizer(main_sizer)                 # Activate complete layout [web:2]

        # Timer for progress updates (5x/second during playback)
        self.timer = wx.Timer(self)                # Fires every 200ms during playback [web:2][web:4]
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)  # Connects timer → on_timer() [web:2]

        # Event bindings (Controller layer)
        btn_load.Bind(wx.EVT_BUTTON, self.on_load)         # Click → on_load() [web:2]
        btn_prev.Bind(wx.EVT_BUTTON, self.on_prev)         # Previous track
        btn_play.Bind(wx.EVT_BUTTON, self.on_play_pause)   # Play/pause toggle
        btn_next.Bind(wx.EVT_BUTTON, self.on_next)         # Next track

        self.playlist.Bind(wx.EVT_LISTBOX_DCLICK, self.on_playlist_dclick)  # Double-click playlist [web:1]
        self.vol_slider.Bind(wx.EVT_SLIDER, self.on_volume_change)         # Volume slider [web:2]
        self.pos_slider.Bind(wx.EVT_SLIDER, self.on_seek)                  # Seek position [web:2]
        self.search_ctrl.Bind(wx.EVT_TEXT, self.on_search)                 # Live search typing [web:1]
        self.search_ctrl.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.on_search_cancel)  # Clear search [web:1]

        # Initialize and show window
        self.update_playlist_display()  # Initialize empty playlist [web:1]
        self.Show()                    # Display window [web:2]

    # HELPER: Rebuild playlist with filter (live search)
    def update_playlist_display(self, filter_text=""):     # Rebuilds visible playlist listbox [web:1]
        self.playlist.Clear()      # Clear current list
        self.display_names = []    # Reset display names
        filter_text = filter_text.lower()  # Case insensitive search
        for full_path in self.tracks:      # Loop through all tracks
            name = os.path.basename(full_path)  # Get filename only
            if not filter_text or filter_text in name.lower():  # Match filter
                self.display_names.append(name)  # Add to display list
                self.playlist.Append(name)       # Add to visible list

    # HELPER: Load and play specific track (handles async duration loading)
    def load_track(self, index):                           # Loads specific track by index [web:2][web:4]
        if index < 0 or index >= len(self.tracks):  # Check valid index
            return
        self.mc.Stop()         # Stop current playback
        self.timer.Stop()      # Stop progress timer
        path = self.tracks[index]  # Get track path
        if self.mc.Load(path):     # Try to load file
            self.current_index = index  # Update current track
            # Async setup for slider (wait for length to load)
            def setup_slider():
                length = self.mc.Length()  # Get track duration in ms
                if length > 0:             # Length available
                    self.pos_slider.SetRange(0, length)  # Set slider max
                    self.pos_slider.SetValue(0)          # Reset to start
                    self.mc.Play()             # Start playback
                    self.timer.Start(200)      # Start progress updates
                else:                      # Length not ready, retry
                    wx.CallLater(100, setup_slider)
            setup_slider()
        else:                      # Load failed
            wx.MessageBox(f"Unable to load {path}", "Error", wx.OK | wx.ICON_ERROR)

    # EVENT: Load songs from file dialog (multiple selection)
    def on_load(self, event):                              # Multi-file dialog → add tracks → auto-play first [web:2]
        dlg = wx.FileDialog(self, message="Choose audio files",
            wildcard="Audio files (*.mp3;*.wav;*.ogg)|*.mp3;*.wav;*.ogg|All files (*.*)|*.*",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE)  # Multiple file selection
        if dlg.ShowModal() == wx.ID_OK:  # User clicked OK
            paths = dlg.GetPaths()     # Get selected file paths
            for p in paths:            # Add each file
                self.tracks.append(p)
            self.update_playlist_display(self.search_ctrl.GetValue())  # Refresh with current filter
            if self.current_index == -1 and self.tracks:  # No current track and have songs
                self.playlist.SetSelection(0)  # Select first
                self.load_track(0)             # Auto-play first
        dlg.Destroy()          # Clean up dialog

    # EVENT: Previous track (wrap-around playlist)
    def on_prev(self, event):                              # (current - 1) % len(tracks) for wrap-around [web:1]
        if not self.tracks: return  # No tracks loaded
        new_index = (self.current_index - 1) % len(self.tracks)  # Previous with wrap
        self.current_index = new_index
        name = os.path.basename(self.tracks[new_index])  # Get display name
        idx = self.playlist.FindString(name)             # Find in filtered list
        if idx != wx.NOT_FOUND: self.playlist.SetSelection(idx)  # Select if visible
        self.load_track(new_index)                       # Load and play

    # EVENT: Next track (wrap-around playlist)
    def on_next(self, event):                              # (current + 1) % len(tracks) for wrap-around [web:1]
        if not self.tracks: return
        new_index = (self.current_index + 1) % len(self.tracks)
        self.current_index = new_index
        name = os.path.basename(self.tracks[new_index])
        idx = self.playlist.FindString(name)
        if idx != wx.NOT_FOUND: self.playlist.SetSelection(idx)
        self.load_track(new_index)

    # EVENT: Play/pause toggle
    def on_play_pause(self, event):                        # Toggle based on mc.GetState() [web:2]
        if self.mc.GetState() != wx.media.MEDIASTATE_PLAYING:  # Not playing
            self.mc.Play()     # Resume
            self.timer.Start(200)  # Restart timer
        else:                  # Playing
            self.mc.Pause()    # Pause
            self.timer.Stop()  # Stop timer

    # EVENT: Double-click playlist item
    def on_playlist_dclick(self, event):                   # Play selected song from filtered list [web:1]
        sel = self.playlist.GetSelection()  # Get selected item
        if sel == wx.NOT_FOUND: return
        name = self.playlist.GetString(sel)  # Get song name
        for i, p in enumerate(self.tracks):  # Find matching full path
            if os.path.basename(p) == name:
                self.load_track(i)     # Play it
                self.current_index = i
                break

    # EVENT: Volume slider changed
    def on_volume_change(self, event):                     # Convert 0-100 to 0.0-1.0 for MediaCtrl [web:2]
        volume = self.vol_slider.GetValue() / 100  # Convert 0-100 to 0.0-1.0
        self.mc.SetVolume(volume)

    # EVENT: Position slider seek
    def on_seek(self, event):                              # Jump to slider position (clamped) [web:2]
        length = self.mc.Length()
        if length > 0:
            pos = self.pos_slider.GetValue()
            if pos < 0: pos = 0
            elif pos > length: pos = length
            self.mc.Seek(pos)  # Jump to position

    # EVENT: Timer tick (200ms during playback)
    def on_timer(self, event):                             # Updates slider + auto-next at end [web:2]
        if self.mc.GetState() == wx.media.MEDIASTATE_PLAYING:  # Still playing
            length = self.mc.Length()
            if length > 0:
                pos = self.mc.Tell()  # Current position
                if pos < 0: pos = 0
                elif pos > length: pos = length
                self.pos_slider.SetRange(0, length)  # Update range
                self.pos_slider.SetValue(pos)        # Update slider
                # Auto-next near end (500ms tolerance)
                if pos >= length - 500 and self.current_index is not None:
                    self.on_next(None)
        else:
            self.timer.Stop()  # Stop if paused/stopped

    # EVENT: Live search typing
    def on_search(self, event):                            # Live filtering as user types [web:1]
        term = self.search_ctrl.GetValue()  # Get search text
        self.update_playlist_display(term)  # Filter playlist

    # EVENT: Search cancel (X button)
    def on_search_cancel(self, event):                     # Clear search and show all songs [web:1]
        self.search_ctrl.SetValue("")      # Clear search box
        self.update_playlist_display("")   # Show all songs

# PROGRAM ENTRY POINT (Standard wxPython structure)
if __name__ == "__main__":
    app = wx.App(False)        # wxPython requires 1 App instance [web:2][web:11]
    MusicPlayer()              # Creates/shows window
    app.MainLoop()             # Event loop (runs forever, waits for user events) [web:2]
