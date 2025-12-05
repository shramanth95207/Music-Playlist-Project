import wx
import wx.media
import os


class MusicPlayer(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Music Player", size=(600, 400))
        panel = wx.Panel(self)

        # --- Data ---
        self.tracks = []          # full paths
        self.display_names = []   # names currently shown in playlist
        self.current_index = -1

        # --- Media control ---
        self.mc = wx.media.MediaCtrl(panel, style=wx.SIMPLE_BORDER)

        # --- Search bar ---
        self.search_ctrl = wx.SearchCtrl(panel, style=wx.TE_PROCESS_ENTER)

        # --- Playlist ---
        self.playlist = wx.ListBox(panel)

        # --- Buttons ---
        btn_load = wx.Button(panel, label="Load songs")
        btn_prev = wx.Button(panel, label="<< Prev")
        btn_play = wx.Button(panel, label="Play/Pause")
        btn_next = wx.Button(panel, label="Next >>")

        # --- Volume slider ---
        self.vol_slider = wx.Slider(
            panel, value=50, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL
        )
        vol_label = wx.StaticText(panel, label="Volume")

        # --- Progress slider (seek + progress bar) ---
        self.pos_slider = wx.Slider(
            panel, value=0, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL
        )

        # --- Layout ---
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        vol_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # left: search + playlist
        left_sizer.Add(self.search_ctrl, 0, wx.EXPAND | wx.ALL, 5)
        left_sizer.Add(self.playlist, 1, wx.EXPAND | wx.ALL, 5)

        # buttons
        btn_sizer.Add(btn_load, 0, wx.ALL, 5)
        btn_sizer.Add(btn_prev, 0, wx.ALL, 5)
        btn_sizer.Add(btn_play, 0, wx.ALL, 5)
        btn_sizer.Add(btn_next, 0, wx.ALL, 5)

        # volume row
        vol_sizer.Add(vol_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        vol_sizer.Add(self.vol_slider, 1, wx.EXPAND)

        # right side: media, position slider, buttons, volume
        right_sizer.Add(self.mc, 0, wx.EXPAND | wx.ALL, 5)
        right_sizer.Add(
            self.pos_slider, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5
        )
        right_sizer.Add(btn_sizer, 0, wx.CENTER)
        right_sizer.Add(vol_sizer, 0, wx.EXPAND | wx.ALL, 5)

        main_sizer.Add(left_sizer, 1, wx.EXPAND)
        main_sizer.Add(right_sizer, 2, wx.EXPAND)

        panel.SetSizer(main_sizer)

        # --- Timer for progress updates ---
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)

        # --- Bindings ---
        btn_load.Bind(wx.EVT_BUTTON, self.on_load)
        btn_prev.Bind(wx.EVT_BUTTON, self.on_prev)
        btn_play.Bind(wx.EVT_BUTTON, self.on_play_pause)
        btn_next.Bind(wx.EVT_BUTTON, self.on_next)

        self.playlist.Bind(wx.EVT_LISTBOX_DCLICK, self.on_playlist_dclick)
        self.vol_slider.Bind(wx.EVT_SLIDER, self.on_volume_change)
        self.pos_slider.Bind(wx.EVT_SLIDER, self.on_seek)

        # search events (live filter + clear button)
        self.search_ctrl.Bind(wx.EVT_TEXT, self.on_search)
        self.search_ctrl.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.on_search_cancel)

        # initial empty display
        self.update_playlist_display()

        self.Show()

    # -------------- helpers -----------------

    def update_playlist_display(self, filter_text=""):
        """Rebuild the playlist listbox based on the filter text."""
        self.playlist.Clear()
        self.display_names = []

        filter_text = filter_text.lower()
        for full_path in self.tracks:
            name = os.path.basename(full_path)
            if not filter_text or filter_text in name.lower():
                self.display_names.append(name)
                self.playlist.Append(name)

    def load_track(self, index):
        if index < 0 or index >= len(self.tracks):
            return
        
        # Stop current playback and timer first
        self.mc.Stop()
        self.timer.Stop()
        
        path = self.tracks[index]
        if self.mc.Load(path):
            self.current_index = index
            
            # Wait briefly for Length() to be available, then set up slider
            def setup_slider():
                length = self.mc.Length()
                if length > 0:
                    self.pos_slider.SetRange(0, length)
                    self.pos_slider.SetValue(0)  # ✅ RESET TO ZERO
                    self.mc.Play()
                    self.timer.Start(200)
                else:
                    # Retry if length not ready yet
                    wx.CallLater(100, setup_slider)
            
            setup_slider()
        else:
            wx.MessageBox(
                f"Unable to load {path}", "Error", wx.OK | wx.ICON_ERROR
            )

    # -------------- events -------------------

    def on_load(self, event):
        dlg = wx.FileDialog(
            self,
            message="Choose audio files",
            wildcard="Audio files (*.mp3;*.wav;*.ogg)|*.mp3;*.wav;*.ogg|All files (*.*)|*.*",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE,
        )
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            for p in paths:
                self.tracks.append(p)
            # refresh list with current filter text
            self.update_playlist_display(self.search_ctrl.GetValue())
            if self.current_index == -1 and self.tracks:
                self.playlist.SetSelection(0)
                self.load_track(0)
        dlg.Destroy()

    def on_prev(self, event):
        if not self.tracks:
            return
        new_index = (self.current_index - 1) % len(self.tracks)
        self.current_index = new_index
        # update visible selection if this track is in the filtered list
        name = os.path.basename(self.tracks[new_index])
        idx = self.playlist.FindString(name)
        if idx != wx.NOT_FOUND:
            self.playlist.SetSelection(idx)
        self.load_track(new_index)

    def on_next(self, event):
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
        if self.mc.GetState() != wx.media.MEDIASTATE_PLAYING:
            self.mc.Play()
            self.timer.Start(200)
        else:
            self.mc.Pause()
            self.timer.Stop()

    def on_playlist_dclick(self, event):
        sel = self.playlist.GetSelection()
        if sel == wx.NOT_FOUND:
            return
        name = self.playlist.GetString(sel)
        # find the real index in self.tracks
        for i, p in enumerate(self.tracks):
            if os.path.basename(p) == name:
                self.load_track(i)
                self.current_index = i
                break

    def on_volume_change(self, event):
        volume = self.vol_slider.GetValue() / 100
        self.mc.SetVolume(volume)

    def on_seek(self, event):
        length = self.mc.Length()
        if length > 0:
            pos = self.pos_slider.GetValue()
            if pos < 0:
                pos = 0
            elif pos > length:
                pos = length
            self.mc.Seek(pos)

    def on_timer(self, event):
        if self.mc.GetState() == wx.media.MEDIASTATE_PLAYING:
            length = self.mc.Length()
            if length > 0:
                pos = self.mc.Tell()
                if pos < 0:
                    pos = 0
                elif pos > length:
                    pos = length
                self.pos_slider.SetRange(0, length)
                self.pos_slider.SetValue(pos)
                
                # Auto-next when song ends
                if pos >= length - 500 and self.current_index is not None:
                    self.on_next(None)
        else:
            self.timer.Stop()

    # --------- search handlers ----------

    def on_search(self, event):
        term = self.search_ctrl.GetValue()
        self.update_playlist_display(term)

    def on_search_cancel(self, event):
        self.search_ctrl.SetValue("")
        self.update_playlist_display("")


if __name__ == "__main__":
    app = wx.App(False)
    MusicPlayer()
    app.MainLoop()
