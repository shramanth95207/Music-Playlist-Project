import wx  # Import the wxPython GUI toolkit module for building windows and widgets
import wx.media  # Import the media submodule to handle audio/video playback controls
import os  # Import the os module to work with filesystem paths and check file existence


class MusicPlayer(wx.Frame):  # Define a MusicPlayer class that inherits from wx.Frame (a top-level window)
    def __init__(self):  # Constructor for the MusicPlayer class
        # Create main window with black background theme
        super().__init__(None, title="Music Player", size=(900, 600))  # Initialize base wx.Frame with title and size
        self.SetBackgroundColour(wx.Colour(10, 10, 10))  # Very dark black background color for the frame

        panel = wx.Panel(self)  # Create a panel inside the frame to place other widgets on
        panel.SetBackgroundColour(wx.Colour(10, 10, 10))  # Dark black background for the panel

        # --- Data ---
        self.tracks = []  # List to hold file paths of loaded tracks
        self.display_names = []  # List to hold display names (base filenames) shown in the playlist UI
        self.current_index = -1  # Index of the currently loaded/playing track (-1 means none loaded)
        self.is_dragging = False  # Flag to track whether the user is currently dragging the progress slider

        # Flag to avoid handling slider events caused by programmatic updates
        self.updating_slider = False  # When True, slider events caused by program (not user) should be ignored

        # --- Search bar ---
        self.search_ctrl = wx.SearchCtrl(panel, style=wx.TE_PROCESS_ENTER)  # Search control for filtering playlist
        self.search_ctrl.SetBackgroundColour(wx.Colour(20, 20, 20))  # Very dark gray background for search box
        self.search_ctrl.SetForegroundColour(wx.Colour(0, 255, 100))  # Light green text color

        # --- Playlist ---
        self.playlist = wx.ListBox(panel)  # ListBox widget to display the playlist entries
        self.playlist.SetBackgroundColour(wx.Colour(15, 15, 15))  # Almost black background for playlist
        self.playlist.SetForegroundColour(wx.Colour(50, 255, 100))  # Bright light green text for playlist entries

        # --- Now Playing Label ---
        now_playing_label = wx.StaticText(panel, label=">> NOW PLAYING")  # Static label indicating now playing section
        font_title = now_playing_label.GetFont()  # Get the default font to modify it
        font_title.PointSize = 15  # Increase font size for the title
        font_title = font_title.Bold()  # Make the font bold
        now_playing_label.SetFont(font_title)  # Apply the modified font to the label
        now_playing_label.SetForegroundColour(wx.Colour(0, 255, 100))  # Light green color for the label

        self.now_playing = wx.StaticText(panel, label="No track loaded")  # Label that shows the current track name
        self.now_playing.SetFont(font_title)  # Use the same font as the title for consistent styling
        self.now_playing.SetForegroundColour(wx.Colour(100, 255, 150))  # Lighter green color for the now playing text

        # --- Video Display Panel (MP4 GIF-like animation) ---
        display_panel = wx.Panel(panel)  # Panel to contain the video/animation area
        display_panel.SetBackgroundColour(wx.Colour(10, 10, 10))  # Match main background color
        display_sizer = wx.BoxSizer(wx.VERTICAL)  # Vertical sizer to layout items inside the display panel

        # Create media control for video playback
        self.video_player = wx.media.MediaCtrl(
            display_panel,
            style=wx.SIMPLE_BORDER
        )  # MediaCtrl used to show video content inside the display panel

        try:
            # Load MP4 video file (like animated GIF)
            video_path = r"e:\Python\Lib\py\animation.mp4"  # Hard-coded path to an MP4 animation file

            if os.path.exists(video_path):  # Check if the given video file actually exists on disk
                # Check if file exists
                if self.video_player.Load(video_path):  # Attempt to load the video into the media control
                    # Successfully loaded video
                    # Remove controls (play/pause buttons, slider, etc.)
                    self.video_player.ShowPlayerControls(0)  # Hide the built-in media player controls

                    # Start playing
                    self.video_player.Play()  # Begin playback of the video

                    # Create timer to loop the video
                    self.video_timer = wx.Timer(self, wx.ID_ANY)  # Timer used to periodically check video state
                    self.Bind(wx.EVT_TIMER, self.on_video_timer, self.video_timer)  # Bind timer events to handler
                    self.video_timer.Start(100)  # Check every 100ms whether the video finished to loop it

                else:
                    # Video failed to load
                    error_text = wx.StaticText(display_panel, label="[VIDEO ERROR]")  # Show an error label
                    error_text.SetForegroundColour(wx.Colour(255, 0, 0))  # Red color to indicate error
                    display_sizer.Add(error_text, 1, wx.ALIGN_CENTER | wx.ALL, 20)  # Add the error message to the layout

            else:
                # File doesn't exist
                no_file_text = wx.StaticText(
                    display_panel,
                    label=f"[FILE NOT FOUND]\n{video_path}"
                )  # Show a message when the video file is missing
                no_file_text.SetForegroundColour(wx.Colour(255, 100, 0))  # Orange color as a warning
                display_sizer.Add(no_file_text, 1, wx.ALIGN_CENTER | wx.ALL, 20)  # Add the warning to the layout

        except Exception as e:  # Catch-all to avoid crashing the UI if video loading throws an exception
            # Catch any errors
            print(f"Error loading video: {e}")  # Print the exception to console for debugging
            error_text = wx.StaticText(display_panel, label=f"[ERROR]\n{str(e)}")  # Show the error text in the UI
            error_text.SetForegroundColour(wx.Colour(255, 0, 0))  # Red color for error
            display_sizer.Add(error_text, 1, wx.ALIGN_CENTER | wx.ALL, 20)  # Add to display panel layout

        # Add video player with expansion to fill all available space
        display_sizer.Add(self.video_player, 1, wx.EXPAND | wx.ALL, 0)  # Place the video player into the sizer
        display_panel.SetSizer(display_sizer)  # Apply the sizer to the display panel

        # --- Media control for audio (hidden) ---
        self.mc = wx.media.MediaCtrl(panel, style=wx.SIMPLE_BORDER)  # MediaCtrl instance used for audio playback
        self.mc.Hide()  # Hide the control widget (we control playback programmatically)

        # --- Buttons ---
        btn_load = wx.Button(panel, label="LOAD SONGS")  # Button to open file dialog and load songs
        btn_prev = wx.Button(panel, label="<< Prev")  # Button to go to previous track
        btn_play = wx.Button(panel, label="PLAY/PAUSE")  # Button to toggle play/pause
        btn_next = wx.Button(panel, label="NEXT >>")  # Button to go to next track

        # Style buttons with black and light green theme
        for btn in [btn_load, btn_prev, btn_play, btn_next]:
            btn.SetBackgroundColour(wx.Colour(0, 150, 75))  # Dark green background for buttons
            btn.SetForegroundColour(wx.WHITE)  # White text color on buttons
            font = btn.GetFont()  # Retrieve the current font of the button
            font.PointSize = 10  # Set a slightly larger size for button text
            btn.SetFont(font)  # Apply the modified font to the button

        # --- Volume slider ---
        vol_label = wx.StaticText(panel, label="VOLUME")  # Label shown next to volume slider
        vol_label.SetForegroundColour(wx.Colour(0, 255, 100))  # Light green color for label
        self.vol_slider = wx.Slider(
            panel, value=70, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL
        )  # Slider to control volume, default value 70
        self.vol_slider.SetBackgroundColour(wx.Colour(20, 20, 20))  # Dark gray background for the slider

        # --- Progress slider ---
        prog_label = wx.StaticText(panel, label="PROGRESS")  # Label for the playback progress slider
        prog_label.SetForegroundColour(wx.Colour(0, 255, 100))  # Light green color for the label
        self.pos_slider = wx.Slider(
            panel, value=0, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL
        )  # Slider to show and control playback position (range will be updated dynamically)
        self.pos_slider.SetBackgroundColour(wx.Colour(20, 20, 20))  # Dark gray background for position slider

        # time label
        self.time_label = wx.StaticText(panel, label="00:00 / 00:00")  # Label to show current time / total time
        font_time = self.time_label.GetFont()  # Get current font to adjust size
        font_time.PointSize = 11  # Slightly larger font for the time display
        self.time_label.SetFont(font_time)  # Set modified font on the label
        self.time_label.SetForegroundColour(wx.Colour(50, 255, 150))  # Bright light green color for time text

        # --- Layout ---
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)  # Main horizontal sizer: left (playlist) + right (player)
        left_sizer = wx.BoxSizer(wx.VERTICAL)  # Left column sizer for playlist components
        right_sizer = wx.BoxSizer(wx.VERTICAL)  # Right column sizer for player components
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)  # Sizer to layout control buttons horizontally
        vol_sizer = wx.BoxSizer(wx.HORIZONTAL)  # Sizer for volume label + slider in a row
        prog_sizer = wx.BoxSizer(wx.VERTICAL)  # Sizer for progress label, slider and time vertically

        # left: playlist title + search + playlist
        playlist_title = wx.StaticText(panel, label="PLAYLIST")  # Title label for the playlist section
        font_pl = playlist_title.GetFont()  # Get its font to modify
        font_pl.PointSize = 12  # Increase size for playlist title
        font_pl = font_pl.Bold()  # Make it bold
        playlist_title.SetFont(font_pl)  # Apply the modified font to the playlist title
        playlist_title.SetForegroundColour(wx.Colour(0, 255, 100))  # Light green color for the title

        left_sizer.Add(playlist_title, 0, wx.ALL, 8)  # Add playlist title to left sizer with padding
        left_sizer.Add(self.search_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)  # Add search control
        left_sizer.Add(self.playlist, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)  # Add playlist listbox and let it expand

        # buttons
        btn_sizer.Add(btn_load, 0, wx.ALL, 5)  # Add load button to the button sizer
        btn_sizer.Add(btn_prev, 0, wx.ALL, 5)  # Add previous button
        btn_sizer.Add(btn_play, 0, wx.ALL, 5)  # Add play/pause button
        btn_sizer.Add(btn_next, 0, wx.ALL, 5)  # Add next button

        # volume row
        vol_sizer.Add(vol_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)  # Put the "VOLUME" label with right margin
        vol_sizer.Add(self.vol_slider, 1, wx.EXPAND)  # Put volume slider and allow it to expand horizontally

        # progress row
        prog_sizer.Add(prog_label, 0, wx.LEFT | wx.TOP, 5)  # Add "PROGRESS" label with left/top padding
        prog_sizer.Add(self.pos_slider, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)  # Add progress slider
        prog_sizer.Add(self.time_label, 0, wx.ALIGN_CENTER | wx.ALL, 5)  # Add time label centered with padding

        # right side
        right_sizer.Add(now_playing_label, 0, wx.ALL, 8)  # Add "NOW PLAYING" title to right column
        right_sizer.Add(self.now_playing, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)  # Add current track label
        right_sizer.Add(display_panel, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 0)  # Add the video/animation panel
        right_sizer.Add(prog_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)  # Add progress controls to right column
        right_sizer.Add(btn_sizer, 0, wx.CENTER | wx.ALL, 5)  # Add control buttons centered in right column
        right_sizer.Add(vol_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)  # Add volume controls

        main_sizer.Add(left_sizer, 1, wx.EXPAND | wx.ALL, 5)  # Add left column to main layout with proportion 1
        main_sizer.Add(right_sizer, 2, wx.EXPAND | wx.ALL, 5)  # Add right column with proportion 2 (wider)

        panel.SetSizer(main_sizer)  # Apply the main sizer to the panel so layout takes effect

        # --- Timer for audio ---
        self.timer = wx.Timer(self)  # Timer used to periodically update playback position UI
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)  # Bind timer events to the on_timer handler

        # --- Bindings ---
        btn_load.Bind(wx.EVT_BUTTON, self.on_load)  # Bind load button click to on_load method
        btn_prev.Bind(wx.EVT_BUTTON, self.on_prev)  # Bind prev button to on_prev
        btn_play.Bind(wx.EVT_BUTTON, self.on_play_pause)  # Bind play/pause button to on_play_pause
        btn_next.Bind(wx.EVT_BUTTON, self.on_next)  # Bind next button to on_next

        self.playlist.Bind(wx.EVT_LISTBOX_DCLICK, self.on_playlist_dclick)  # Double-click on playlist item loads it
        self.vol_slider.Bind(wx.EVT_SLIDER, self.on_volume_change)  # Volume slider changes call on_volume_change

        # For progress slider:
        # - EVT_SLIDER will be used to seek when the user moves the slider
        # - EVT_LEFT_DOWN / EVT_LEFT_UP change dragging state but MUST call event.Skip()
        #   so the slider can still handle the mouse and move its thumb.
        self.pos_slider.Bind(wx.EVT_LEFT_DOWN, self.on_slider_down)  # Mouse down on slider: set dragging state
        self.pos_slider.Bind(wx.EVT_LEFT_UP, self.on_slider_up)  # Mouse up on slider: finalize seek and resume timer
        self.pos_slider.Bind(wx.EVT_SLIDER, self.on_seek)  # Slider move events trigger seeking while dragging

        self.search_ctrl.Bind(wx.EVT_TEXT, self.on_search)  # Typing in search control filters the playlist in real time
        self.search_ctrl.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.on_search_cancel)  # Canceling search clears filter

        self.update_playlist_display()  # Initial refresh of the playlist UI (empty at start)
        self.mc.SetVolume(self.vol_slider.GetValue() / 100)  # Set initial audio volume from slider (convert to 0..1)

        self.Show()  # Show the main frame window

    # -------------- helpers -----------------

    def update_playlist_display(self, filter_text=""):  # Rebuild playlist display optionally using a filter string
        """Rebuild the playlist listbox based on the filter text."""
        self.playlist.Clear()  # Clear all entries from the displayed listbox
        self.display_names = []  # Reset the display names list

        filter_text = filter_text.lower()  # Normalize filter text to lowercase for case-insensitive matching
        for full_path in self.tracks:  # Iterate over all loaded track file paths
            name = os.path.basename(full_path)  # Extract just the filename portion for display
            if not filter_text or filter_text in name.lower():  # If no filter or name contains the filter text
                self.display_names.append(name)  # Add name to internal display list
                self.playlist.Append(name)  # Append the name to the ListBox control so it appears in the UI

    def load_track(self, index):  # Load and start playing the track at the given index
        if index < 0 or index >= len(self.tracks):  # Guard: invalid index
            return  # Do nothing if index is out of range

        try:
            self.mc.Stop()  # Try stopping any currently playing audio before loading a new one
        except Exception:
            pass  # Ignore exceptions from Stop (e.g., if nothing is loaded)
        self.timer.Stop()  # Stop the position update timer while we load and prepare the new file

        path = self.tracks[index]  # Get the file path for the requested index
        if self.mc.Load(path):  # Attempt to load the audio file into the media control
            self.current_index = index  # Update the current index to the loaded track
            self.now_playing.SetLabel(os.path.basename(path))  # Update the now playing label with the filename

            def setup_slider():  # Nested helper to set up slider once media length is available
                length = self.mc.Length()  # Query media length (in milliseconds)
                if length and length > 0:  # If length is a valid positive number
                    # protect against generating slider events we should ignore
                    self.updating_slider = True  # Set flag so programmatic slider updates won't trigger seek handling
                    try:
                        self.pos_slider.SetRange(0, length)  # Set the slider range to the media length
                        self.pos_slider.SetValue(0)  # Reset slider to start position
                    finally:
                        self.updating_slider = False  # Clear the flag after updating the slider

                    self.time_label.SetLabel(f"{self.ms_to_time(0)} / {self.ms_to_time(length)}")  # Update time display
                    self.mc.Play()  # Start playback
                    self.timer.Start(250)  # Start timer to update UI every 250ms
                else:
                    wx.CallLater(100, setup_slider)  # If length isn't ready, try again shortly (asynchronous load)

            setup_slider()  # Call nested helper to initialize slider and start playback
        else:
            wx.MessageBox(f"Unable to load {path}", "Error", wx.OK | wx.ICON_ERROR)  # Show error if load failed

    def on_video_timer(self, event):  # Timer handler used to loop the video playback
        """Loop video when it finishes - checks every 100ms"""
        try:
            # Check if video has stopped (finished playing)
            if self.video_player.GetState() == wx.media.MEDIASTATE_STOPPED:
                # Seek to beginning (position 0)
                self.video_player.Seek(0)  # Reset video position to the start
                # Start playing again
                self.video_player.Play()  # Play video again to create a looping effect
        except Exception:
            pass  # Silently ignore any errors interacting with video player (keeps UI stable)

    # -------------- events -------------------

    def on_load(self, event):  # Handler for the "LOAD SONGS" button
        dlg = wx.FileDialog(
            self,
            message="Choose audio files",
            wildcard="Audio files (*.mp3;*.wav;*.ogg;*.flac)|*.mp3;*.wav;*.ogg;*.flac|All files (*.*)|*.*",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE,
        )  # File dialog configured to allow multiple audio files selection
        if dlg.ShowModal() == wx.ID_OK:  # If the user pressed OK and selected files
            paths = dlg.GetPaths()  # Get the selected file paths as a list
            for p in paths:
                self.tracks.append(p)  # Append each selected path to the tracks list
            self.update_playlist_display(self.search_ctrl.GetValue())  # Rebuild the displayed playlist using current filter
            if self.current_index == -1 and self.tracks:  # If no track was loaded previously but now we have tracks
                self.playlist.SetSelection(0)  # Select the first item in the playlist UI
                self.load_track(0)  # Load and start playing the first track
        dlg.Destroy()  # Destroy the dialog to free resources

    def on_prev(self, event):  # Handler for the "Prev" button
        if not self.tracks:  # If there are no tracks loaded, do nothing
            return
        new_index = (self.current_index - 1) % len(self.tracks)  # Calculate previous index with wrap-around
        self.current_index = new_index  # Update current index
        name = os.path.basename(self.tracks[new_index])  # Extract filename for finding it in the listbox
        idx = self.playlist.FindString(name)  # Find the display index in the ListBox that matches the filename
        if idx != wx.NOT_FOUND:
            self.playlist.SetSelection(idx)  # Select it in the UI if found
        self.load_track(new_index)  # Load the track at the new index

    def on_next(self, event):  # Handler for the "Next" button
        if not self.tracks:  # If no tracks loaded, do nothing
            return
        new_index = (self.current_index + 1) % len(self.tracks)  # Next index with wrap-around
        self.current_index = new_index  # Update current index
        name = os.path.basename(self.tracks[new_index])  # Get filename for UI selection
        idx = self.playlist.FindString(name)  # Find the entry in the ListBox
        if idx != wx.NOT_FOUND:
            self.playlist.SetSelection(idx)  # Select entry if present
        self.load_track(new_index)  # Load and play the next track

    def on_play_pause(self, event):  # Handler for the play/pause button
        if self.mc.GetState() != wx.media.MEDIASTATE_PLAYING:  # If not currently playing
            self.mc.Play()  # Start playback
            self.timer.Start(250)  # Start the UI update timer
        else:
            self.mc.Pause()  # Pause playback
            self.timer.Stop()  # Stop the periodic UI updates

    def on_playlist_dclick(self, event):  # Handler for double-clicking an item in the playlist
        sel = self.playlist.GetSelection()  # Get the selected index from the ListBox
        if sel == wx.NOT_FOUND:
            return  # Do nothing if nothing is selected
        name = self.playlist.GetString(sel)  # Get the display name string for the selected entry
        for i, p in enumerate(self.tracks):  # Find the corresponding track path by matching filenames
            if os.path.basename(p) == name:
                self.load_track(i)  # Load the matching track
                self.current_index = i  # Update current index
                break  # Exit loop after loading the selected track

    def on_volume_change(self, event):  # Handler for volume slider changes
        volume = self.vol_slider.GetValue() / 100  # Convert slider value (0-100) to 0.0-1.0 range
        try:
            self.mc.SetVolume(volume)  # Try to set the media control volume
        except Exception:
            pass  # Ignore any errors (some backends may not support SetVolume)
        # allow default processing as well
        event.Skip()  # Call Skip to allow default slider behavior/events to continue

    def on_slider_down(self, event):  # Handler for mouse down on the position slider
        # When user presses the mouse on the slider, stop the regular update timer
        self.is_dragging = True  # Mark that the user has started dragging the slider
        try:
            self.timer.Stop()  # Stop the periodic updates while dragging to avoid conflicts
        except Exception:
            pass  # Ignore errors if timer cannot be stopped
        # MUST call Skip so the slider gets the mouse event and moves its thumb
        event.Skip()  # Allow the slider to process the mouse-down event normally

    def on_slider_up(self, event):  # Handler for mouse up on the position slider
        # User released the mouse; perform final seek and resume timer if playing
        self.is_dragging = False  # Clear dragging state
        try:
            pos = self.pos_slider.GetValue()  # Get the final slider value (int)
            if self.mc.Length() > 0:  # If media length is known and positive
                try:
                    self.mc.Seek(pos)  # Seek audio to the selected position in milliseconds
                except Exception:
                    pass  # Ignore any exceptions seeking (backend limitations)
                self.time_label.SetLabel(f"{self.ms_to_time(pos)} / {self.ms_to_time(self.mc.Length())}")  # Update time display
        except Exception:
            pass  # Ignore unexpected exceptions while reading slider value

        if self.mc.GetState() == wx.media.MEDIASTATE_PLAYING:  # If playback was active before drag
            try:
                self.timer.Start(250)  # Resume the timer to update position periodically
            except Exception:
                pass  # Ignore errors restarting the timer

        # Allow the slider to also process the left-up event
        event.Skip()  # Allow default handling for the mouse-up event to continue

    def on_seek(self, event):  # Handler for slider movement / seeking events
        # Ignore events caused by programmatic updates
        if self.updating_slider:
            return  # If we set the slider value programmatically, ignore the event to avoid feedback

        # event.GetInt() provides the slider value for EVT_SLIDER
        try:
            pos = event.GetInt()  # Get the integer value from the event if possible
        except Exception:
            pos = self.pos_slider.GetValue()  # Fallback to reading slider value directly

        length = self.mc.Length()  # Query current media length
        if length > 0:
            pos = max(0, min(pos, length))  # Clamp pos between 0 and length
            try:
                # Seek to position as the user drags/clicks
                self.mc.Seek(pos)  # Perform seek to requested position
            except Exception:
                pass  # Ignore backend-related seek errors
            self.time_label.SetLabel(f"{self.ms_to_time(pos)} / {self.ms_to_time(length)}")  # Update the displayed time

        # let other handlers run if needed
        event.Skip()  # Allow default handlers to also process the slider event

    def on_timer(self, event):  # Periodic timer handler to update UI while playing
        if self.mc.GetState() == wx.media.MEDIASTATE_PLAYING:  # Only update when media is playing
            length = self.mc.Length()  # Get total length in milliseconds
            if length > 0:
                pos = self.mc.Tell()  # Get current playback position in milliseconds
                if pos < 0:
                    pos = 0  # Guard against negative positions from backends
                elif pos > length:
                    pos = length  # Clamp to length if Tell overshoots
                if not self.is_dragging:  # Only update slider if the user is not currently dragging it
                    # protect against generating slider events we should ignore
                    self.updating_slider = True  # Set flag to prevent on_seek handling from reacting
                    try:
                        self.pos_slider.SetRange(0, length)  # Ensure slider range matches media length
                        self.pos_slider.SetValue(pos)  # Move slider thumb to current playback position
                    finally:
                        self.updating_slider = False  # Clear the flag after programmatic update
                self.time_label.SetLabel(f"{self.ms_to_time(pos)} / {self.ms_to_time(length)}")  # Update time display

                # if near end, go to next
                if pos >= length - 500 and self.current_index is not None:  # If playback is within 500ms of end
                    self.on_next(None)  # Advance to the next track automatically
        else:
            try:
                self.timer.Stop()  # If not playing, stop the timer to save resources
            except Exception:
                pass  # Ignore any errors stopping the timer

    def ms_to_time(self, ms):  # Utility to format milliseconds into "MM:SS"
        """Convert milliseconds to MM:SS"""
        try:
            ms = int(ms)  # Ensure ms is integer
            if ms <= 0:
                return "00:00"  # Return zero time for non-positive values
            s = ms // 1000  # Convert milliseconds to total seconds
            m = s // 60  # Compute minutes
            s = s % 60  # Remaining seconds after removing minutes
            return f"{m:02d}:{s:02d}"  # Format as two-digit minutes and seconds
        except Exception:
            return "00:00"  # On error, return safe default time string

    def on_search(self, event):  # Handler called when search text changes
        term = self.search_ctrl.GetValue()  # Read current search text
        self.update_playlist_display(term)  # Rebuild playlist display filtered by search term

    def on_search_cancel(self, event):  # Handler for cancel button in search control
        self.search_ctrl.SetValue("")  # Clear the search text
        self.update_playlist_display("")  # Refresh the playlist with no filter


if __name__ == "__main__":  # If this script is run directly (not imported), start the application
    app = wx.App(False)  # Create a wx App object; False means do not redirect stdout/stderr to a window
    MusicPlayer()  # Instantiate the MusicPlayer frame (constructor shows the window)
    app.MainLoop()  # Enter the wx event loop to start handling GUI events and keep the app running
