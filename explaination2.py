import wx              # Main wxPython GUI library - handles windows, buttons, layouts, events
import wx.media        # MediaCtrl for playing audio/video - the actual audio engine
import os              # For working with file paths (os.path.basename etc.) - extracts filenames

class MusicPlayer(wx.Frame):
    def __init__(self):
        """
        CONSTRUCTOR: Creates the entire music player GUI in one massive setup method.
        wx.Frame is the main window container - everything lives inside this.
        """
        # STEP 1: Create main window frame with title and fixed size
        # None = parent (top-level window), title="Music Player", size=(700,420) pixels
        super().__init__(None, title="Music Player", size=(700, 420))

        # STEP 2: Create root panel - ALL widgets live inside this panel
        # Panel is a container that can have its own background color and sizers
        panel = wx.Panel(self)

        # ----------------- STEP 3: COLOR PALETTE DEFINITION -----------------
        # These are RGB values (0-255) defining the app's visual theme
        # HEX colors converted to wx.Colour format for wxPython compatibility
        main_bg   = wx.Colour(0x6F, 0xC5, 0xC5)  # Teal background for main window
        card_bg   = wx.Colour(0xF5, 0xFE, 0xFE)  # Near-white for right "card" area
        left_bg   = wx.Colour(0x08, 0x37, 0x39)  # Dark teal for left playlist panel
        text_col  = wx.Colour(0x08, 0x37, 0x39)  # Dark teal for text labels
        button_bg = wx.Colour(0x00, 0x7A, 0xCC)  # Blue for button backgrounds
        button_fg = wx.Colour(255, 255, 255)     # Pure white text on buttons

        # Apply theme colors to main containers
        self.SetBackgroundColour(main_bg)  # Frame background
        panel.SetBackgroundColour(main_bg) # Root panel background

        # ----------------- STEP 4: PLAYER STATE VARIABLES -----------------
        # These instance variables track the app's internal state across methods
        self.tracks = []          # List of FULL file paths (e.g., "/home/song.mp3")
        self.display_names = []   # Names shown in playlist (filtered version of tracks)
        self.current_index = -1   # Index of currently playing track (-1 = nothing playing)

        # ----------------- STEP 5: LEFT PANEL SETUP (PLAYLIST SIDE) -----------------
        # Dark-themed panel containing search + playlist listbox
        left_panel = wx.Panel(panel)
        left_panel.SetBackgroundColour(left_bg)  # Apply dark teal background

        # Search control - wx.SearchCtrl has built-in magnifying glass + cancel button
        self.search_ctrl = wx.SearchCtrl(left_panel, style=wx.TE_PROCESS_ENTER)
        # wx.TE_PROCESS_ENTER = capture Enter key presses for search

        # Playlist display - wx.ListBox shows selectable list of track names
        self.playlist = wx.ListBox(left_panel)

        # Force minimum width on search bar + make it white (overrides dark theme)
        self.search_ctrl.SetMinSize((220, -1))  # 220px wide, auto height
        self.search_ctrl.SetBackgroundColour(wx.WHITE)

        # Style playlist to match dark theme
        self.playlist.SetBackgroundColour(left_bg)           # Dark background
        self.playlist.SetForegroundColour(wx.Colour(230, 245, 245))  # Light text

        # VERTICAL LAYOUT FOR LEFT PANEL: Search on top, playlist fills remaining space
        left_sizer = wx.BoxSizer(wx.VERTICAL)  # Stacks widgets top-to-bottom
        # Search bar: 0=preferred size, wx.EXPAND=full width, wx.ALL=8px margin all sides
        left_sizer.Add(self.search_ctrl, 0, wx.EXPAND | wx.ALL, 8)
        # Playlist: 1=expand to fill remaining vertical space, margins on 3 sides
        left_sizer.Add(self.playlist, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        # Tell left_panel to use this sizer for automatic layout
        left_panel.SetSizer(left_sizer)

        # ----------------- STEP 6: RIGHT CARD PANEL SETUP (PLAYER CONTROLS) -----------------
        # Light-themed "card" containing media player + controls
        card_panel = wx.Panel(panel)
        card_panel.SetBackgroundColour(card_bg)  # Near-white background

        # CORE MEDIA WIDGET - This actually plays audio files
        # wx.media.MediaCtrl handles MP3/WAV/OGG/FLAC playback
        self.mc = wx.media.MediaCtrl(card_panel, style=wx.SIMPLE_BORDER)

        # PROGRESS SLIDER - Shows current position (initially 0-100 range)
        self.pos_slider = wx.Slider(card_panel, value=0, minValue=0,
                                    maxValue=100, style=wx.SL_HORIZONTAL)

        # TIME DISPLAY - Shows "00:00 / 03:45" format
        self.time_label = wx.StaticText(card_panel, label="00:00 / 00:00")

        # CONTROL BUTTONS - User interaction points
        btn_load = wx.Button(card_panel, label="Load songs")      # Open file dialog
        btn_prev = wx.Button(card_panel, label="<< Prev")         # Previous track
        btn_play = wx.Button(card_panel, label="Play/Pause")      # Toggle play/pause
        btn_next = wx.Button(card_panel, label="Next >>")         # Next track

        # VOLUME SLIDER - 0-100% volume control (starts at 70%)
        self.vol_slider = wx.Slider(card_panel, value=70, minValue=0,
                                    maxValue=100, style=wx.SL_HORIZONTAL)

        # ----------------- STEP 7: CUSTOM FONT SETUP -----------------
        # Attempt to load "Comfortaa" font (modern rounded font)
        # Graceful fallback if font not installed on user's system
        try:
            ui_font = wx.Font(
                10,                      # 10pt size
                wx.FONTFAMILY_DEFAULT,   # Let system choose similar font family
                wx.FONTSTYLE_NORMAL,     # Not italic
                wx.FONTWEIGHT_NORMAL,    # Normal thickness
                False,                   # No underline
                "Comfortaa"              # Exact font name to try
            )
        except Exception:
            # Font failed to load → use default system font
            ui_font = self.GetFont()

        # Apply custom font to ALL text widgets for consistent look
        for w in (self.search_ctrl, self.playlist, self.time_label,
                  btn_load, btn_prev, btn_play, btn_next):
            w.SetFont(ui_font)

        # ----------------- STEP 8: APPLY COLORS TO RIGHT PANEL WIDGETS -----------------
        self.mc.SetBackgroundColour(card_bg)        # MediaCtrl matches card background
        self.time_label.SetForegroundColour(text_col)  # Dark text on light background

        # Style all buttons with blue background + white text
        for b in (btn_load, btn_prev, btn_play, btn_next):
            b.SetBackgroundColour(button_bg)
            b.SetForegroundColour(button_fg)

        # ----------------- STEP 9: LAYOUT INSIDE RIGHT CARD PANEL -----------------
        card_sizer = wx.BoxSizer(wx.VERTICAL)  # Top-to-bottom layout

        # MediaCtrl visualization area (shows album art if available)
        card_sizer.Add(self.mc, 0, wx.EXPAND | wx.ALL, 5)

        # Progress slider below media area - full width
        card_sizer.Add(self.pos_slider, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Centered time label below slider
        card_sizer.Add(self.time_label, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)

        # HORIZONTAL ROW: Prev + Play + Next buttons
        controls_row = wx.BoxSizer(wx.HORIZONTAL)
        controls_row.Add(btn_prev, 0, wx.ALL, 6)  # 6px margin around each
        controls_row.Add(btn_play, 0, wx.ALL, 6)
        controls_row.Add(btn_next, 0, wx.ALL, 6)
        # Center the entire button row
        card_sizer.Add(controls_row, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)

        # SINGLE "Load songs" button row (centered)
        load_row = wx.BoxSizer(wx.HORIZONTAL)
        load_row.Add(btn_load, 0, wx.ALL, 5)
        card_sizer.Add(load_row, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        # BOTTOM VOLUME ROW: "Volume" label + slider
        vol_row = wx.BoxSizer(wx.HORIZONTAL)
        vol_text = wx.StaticText(card_panel, label="Volume")
        vol_text.SetForegroundColour(text_col)  # Dark text
        # Label vertically centered + 5px right margin
        vol_row.Add(vol_text, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        # Slider takes remaining horizontal space
        vol_row.Add(self.vol_slider, 1, wx.EXPAND)
        card_sizer.Add(vol_row, 0, wx.EXPAND | wx.ALL, 10)

        # Invisible spacer pushes content to top if window resized larger
        card_sizer.AddStretchSpacer()

        # Apply sizer to card_panel → automatic responsive layout
        card_panel.SetSizer(card_sizer)

        # ----------------- STEP 10: MAIN HORIZONTAL LAYOUT -----------------
        # SPLIT WINDOW: Left panel (fixed width) + Right panel (expands)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(left_panel, 0, wx.EXPAND)           # Left: natural width
        main_sizer.Add(card_panel, 1, wx.EXPAND | wx.ALL, 12)  # Right: grows + 12px margins
        panel.SetSizer(main_sizer)  # Root panel uses main sizer

        # ----------------- STEP 11: UPDATE TIMER SETUP -----------------
        # wx.Timer calls on_timer() every 250ms during playback to update progress
        self.timer = wx.Timer(self)
        # Bind timer event to our update method
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)

        # ----------------- STEP 12: EVENT BINDINGS (THE BRAIN) -----------------
        # Connect button clicks to handler methods
        btn_load.Bind(wx.EVT_BUTTON, self.on_load)           # File dialog
        btn_prev.Bind(wx.EVT_BUTTON, self.on_prev)           # Previous track
        btn_play.Bind(wx.EVT_BUTTON, self.on_play_pause)     # Play/pause toggle
        btn_next.Bind(wx.EVT_BUTTON, self.on_next)           # Next track

        # Playlist double-click → play that track
        self.playlist.Bind(wx.EVT_LISTBOX_DCLICK, self.on_playlist_dclick)
        # Volume slider drag → update volume
        self.vol_slider.Bind(wx.EVT_SLIDER, self.on_volume_change)
        # Progress slider drag → seek to position
        self.pos_slider.Bind(wx.EVT_SLIDER, self.on_seek)

        # Search box typing → live filter playlist
        self.search_ctrl.Bind(wx.EVT_TEXT, self.on_search)
        # Search cancel button (X) → clear filter
        self.search_ctrl.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.on_search_cancel)

        # ----------------- STEP 13: INITIALIZATION -----------------
        # Show empty playlist + set initial volume
        self.update_playlist_display()
        self.mc.SetVolume(self.vol_slider.GetValue() / 100)  # 70% default

        # FINALLY: Make window visible to user
        self.Show()

    # ================== HELPER METHODS ==================

    def update_playlist_display(self, filter_text=""):
        """
        REBUILDS PLAYLIST VISUALLY based on search filter.
        Called whenever tracks change OR search text changes.
        """
        self.playlist.Clear()  # Wipe current list
        self.display_names = []  # Reset filtered names

        filter_text = filter_text.lower()  # Case-insensitive search
        for full_path in self.tracks:  # Loop through ALL loaded tracks
            name = os.path.basename(full_path)  # "C:\music\song.mp3" → "song.mp3"
            if not filter_text or filter_text in name.lower():  # Match?
                self.display_names.append(name)  # Add to filtered list
                self.playlist.Append(name)       # Add to visual listbox

    def load_track(self, index):
        """
        LOADS AND PLAYS track at given index with retry logic for media readiness.
        Complex because MediaCtrl.Length() isn't immediately available after Load().
        """
        if index < 0 or index >= len(self.tracks):  # Invalid index?
            return

        # STOP current playback safely (ignore errors)
        try:
            self.mc.Stop()
        except Exception:
            pass
        self.timer.Stop()  # Stop progress updates

        path = self.tracks[index]
        if self.mc.Load(path):  # Try to load file
            self.current_index = index  # Track current playing index

            # NESTED FUNCTION: Wait for MediaCtrl to be ready, then play
            def setup_slider():
                length = self.mc.Length()  # Total duration in milliseconds
                if length and length > 0:  # Ready!
                    # Resize slider to match track length
                    self.pos_slider.SetRange(0, length)
                    self.pos_slider.SetValue(0)  # Start at beginning
                    # Update time display: current / total
                    self.time_label.SetLabel(
                        f"{self.ms_to_time(0)} / {self.ms_to_time(length)}"
                    )
                    # START PLAYBACK + progress timer
                    self.mc.Play()
                    self.timer.Start(250)  # Update every 250ms
                else:
                    # Length not ready yet → retry in 100ms
                    wx.CallLater(100, setup_slider)

            setup_slider()  # Kick off the readiness check
        else:
            # File failed to load → show error dialog
            wx.MessageBox(f"Unable to load {path}", "Error",
                          wx.OK | wx.ICON_ERROR)

    # ================== EVENT HANDLERS ==================

    def on_load(self, event):
        """
        FILE DIALOG: User selects multiple audio files → add to playlist.
        Supports MP3/WAV/OGG/FLAC with wildcard filtering.
        """
        dlg = wx.FileDialog(
            self,                                    # Parent window
            message="Choose audio files",            # Dialog title
            wildcard=(
                "Audio files (*.mp3;*.wav;*.ogg;*.flac)"
                "|*.mp3;*.wav;*.ogg;*.flac|All files (*.*)|*.*"
            ),  # File type filter
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE,  # Multi-select
        )
        if dlg.ShowModal() == wx.ID_OK:  # User clicked OK
            paths = dlg.GetPaths()  # Get list of selected file paths
            for p in paths:
                self.tracks.append(p)  # Add each to master track list
            # Refresh display (respects current search filter)
            self.update_playlist_display(self.search_ctrl.GetValue())
            # Auto-play first track if nothing was playing
            if self.current_index == -1 and self.tracks:
                self.playlist.SetSelection(0)  # Highlight first item
                self.load_track(0)
        dlg.Destroy()  # Clean up dialog

    def on_prev(self, event):
        """PLAY PREVIOUS TRACK with wrap-around (last → first)."""
        if not self.tracks:  # No tracks loaded
            return
        # Modulo (%) creates wrap-around: (n-1) % len = last when at first
        new_index = (self.current_index - 1) % len(self.tracks)
        self.current_index = new_index
        name = os.path.basename(self.tracks[new_index])
        idx = self.playlist.FindString(name)  # Find in filtered list
        if idx != wx.NOT_FOUND:
            self.playlist.SetSelection(idx)  # Highlight in playlist
        self.load_track(new_index)

    def on_next(self, event):
        """PLAY NEXT TRACK with wrap-around (last → first)."""
        if not self.tracks:
            return
        new_index = (self.current_index + 1) % len(self.tracks)
        self.current_index = new_index
        name = os.path.basename(self.tracks[new_index])
        idx = self.playlist.FindString(name)
        if idx != wx.NOT_FOUND:
            self.playlist.SetSelection(idx)
        self.load_track(new_index)

    def on_play_pause(self, event):
        """TOGGLE play/pause of current track."""
        if self.mc.GetState() != wx.media.MEDIASTATE_PLAYING:
            # Not playing → start playback + timer
            self.mc.Play()
            self.timer.Start(250)
        else:
            # Playing → pause + stop timer
            self.mc.Pause()
            self.timer.Stop()

    def on_playlist_dclick(self, event):
        """DOUBLE-CLICK playlist item → play that track."""
        sel = self.playlist.GetSelection()  # Get selected index
        if sel == wx.NOT_FOUND:
            return
        name = self.playlist.GetString(sel)  # Get display name
        # Search master tracks list for matching filename
        for i, p in enumerate(self.tracks):
            if os.path.basename(p) == name:
                self.load_track(i)
                self.current_index = i
                break

    def on_volume_change(self, event):
        """VOLUME SLIDER: Update MediaCtrl volume (0.0-1.0 range)."""
        volume = self.vol_slider.GetValue() / 100  # Convert 0-100 → 0.0-1.0
        try:
            self.mc.SetVolume(volume)
        except Exception:
            pass  # Ignore volume change errors

    def on_seek(self, event):
        """PROGRESS SLIDER: Jump to new position in track."""
        length = self.mc.Length()
        if length > 0:
            pos = self.pos_slider.GetValue()  # New position in ms
            # Clamp to valid range [0, length]
            pos = max(0, min(pos, length))
            try:
                self.mc.Seek(pos)
            except Exception:
                pass
            # Update time display immediately
            self.time_label.SetLabel(
                f"{self.ms_to_time(pos)} / {self.ms_to_time(length)}"
            )

    def on_timer(self, event):
        """
        PROGRESS UPDATER: Called every 250ms during playback.
        Syncs slider position + time display with current playback position.
        Auto-advances to next track near end.
        """
        if self.mc.GetState() == wx.media.MEDIASTATE_PLAYING:
            length = self.mc.Length()
            if length > 0:
                pos = self.mc.Tell()  # Current position in milliseconds
                pos = max(0, min(pos, length))  # Clamp to valid range

                # SYNC UI with current position
                self.pos_slider.SetRange(0, length)
                self.pos_slider.SetValue(pos)
                self.time_label.SetLabel(
                    f"{self.ms_to_time(pos)} / {self.ms_to_time(length)}"
                )

                # AUTO-NEXT: Advance when within 500ms of end
                if pos >= length - 500 and self.current_index is not None:
                    self.on_next(None)
        else:
            # Not playing → stop timer to save CPU
            self.timer.Stop()

    def ms_to_time(self, ms):
        """UTILITY: Convert milliseconds → "MM:SS" format."""
        try:
            ms = int(ms)
            if ms <= 0:
                return "00:00"
            s = ms // 1000  # Total seconds
            m = s // 60     # Minutes
            s = s % 60      # Remaining seconds
            return f"{m:02d}:{s:02d}"  # Zero-pad to 2 digits
        except Exception:
            return "00:00"

    # --------- SEARCH HANDLERS ----------

    def on_search(self, event):
        """LIVE SEARCH: Filter playlist as user types."""
        term = self.search_ctrl.GetValue()  # Current search text
        self.update_playlist_display(term)

    def on_search_cancel(self, event):
        """SEARCH CANCEL (X button): Show full unfiltered playlist."""
        self.search_ctrl.SetValue("")
        self.update_playlist_display("")

# ================== MAIN ENTRY POINT ==================
if __name__ == "__main__":
    """
    STANDARD PYTHON GUI BOILERPLATE:
    1. Create wx.App() - the application event loop
    2. Create MusicPlayer() window
    3. app.MainLoop() - start processing events forever
    """
    app = wx.App(False)  # False = no default error dialog on crashes
    MusicPlayer()        # Create and show the player
    app.MainLoop()       # Enter infinite event loop - handles all user interactions
