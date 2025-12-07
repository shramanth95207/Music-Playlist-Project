import wx
import wx.media
import os

class MusicPlayer(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Music Player", size=(700, 420))
        panel = wx.Panel(self)

        # Color palette
        main_bg = wx.Colour(0x6F, 0xC5, 0xC5)
        card_bg = wx.Colour(0xF5, 0xFE, 0xFE)
        left_bg = wx.Colour(0x08, 0x37, 0x39)
        text_col = wx.Colour(0x08, 0x37, 0x39)
        button_bg = wx.Colour(0x00, 0x7A, 0xCC)
        button_fg = wx.Colour(255, 255, 255)

        self.SetBackgroundColour(main_bg)
        panel.SetBackgroundColour(main_bg)

        # Player state
        self.tracks = []
        self.display_names = []
        self.current_index = -1

        # Left panel (playlist)
        left_panel = wx.Panel(panel)
        left_panel.SetBackgroundColour(left_bg)
        
        self.search_ctrl = wx.SearchCtrl(left_panel, style=wx.TE_PROCESS_ENTER)
        self.playlist = wx.ListBox(left_panel)
        
        self.search_ctrl.SetMinSize((220, -1))
        self.search_ctrl.SetBackgroundColour(wx.WHITE)
        self.playlist.SetBackgroundColour(left_bg)
        self.playlist.SetForegroundColour(wx.Colour(230, 245, 245))

        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(self.search_ctrl, 0, wx.EXPAND | wx.ALL, 8)
        left_sizer.Add(self.playlist, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        left_panel.SetSizer(left_sizer)

        # Right panel (controls)
        card_panel = wx.Panel(panel)
        card_panel.SetBackgroundColour(card_bg)

        self.mc = wx.media.MediaCtrl(card_panel, style=wx.SIMPLE_BORDER)
        self.pos_slider = wx.Slider(card_panel, value=0, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL)
        self.time_label = wx.StaticText(card_panel, label="00:00 / 00:00")

        btn_load = wx.Button(card_panel, label="Load songs")
        btn_prev = wx.Button(card_panel, label="<< Prev")
        btn_play = wx.Button(card_panel, label="Play/Pause")
        btn_next = wx.Button(card_panel, label="Next >>")

        self.vol_slider = wx.Slider(card_panel, value=70, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL)

        # Fonts
        try:
            ui_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Comfortaa")
        except:
            ui_font = self.GetFont()

        for w in (self.search_ctrl, self.playlist, self.time_label, btn_load, btn_prev, btn_play, btn_next):
            w.SetFont(ui_font)

        # Colors
        self.mc.SetBackgroundColour(card_bg)
        self.time_label.SetForegroundColour(text_col)
        for b in (btn_load, btn_prev, btn_play, btn_next):
            b.SetBackgroundColour(button_bg)
            b.SetForegroundColour(button_fg)

        # Card layout
        card_sizer = wx.BoxSizer(wx.VERTICAL)
        card_sizer.Add(self.mc, 0, wx.EXPAND | wx.ALL, 5)
        card_sizer.Add(self.pos_slider, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        card_sizer.Add(self.time_label, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)

        controls_row = wx.BoxSizer(wx.HORIZONTAL)
        controls_row.Add(btn_prev, 0, wx.ALL, 6)
        controls_row.Add(btn_play, 0, wx.ALL, 6)
        controls_row.Add(btn_next, 0, wx.ALL, 6)
        card_sizer.Add(controls_row, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)

        load_row = wx.BoxSizer(wx.HORIZONTAL)
        load_row.Add(btn_load, 0, wx.ALL, 5)
        card_sizer.Add(load_row, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        vol_row = wx.BoxSizer(wx.HORIZONTAL)
        vol_text = wx.StaticText(card_panel, label="Volume")
        vol_text.SetForegroundColour(text_col)
        vol_row.Add(vol_text, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        vol_row.Add(self.vol_slider, 1, wx.EXPAND)
        card_sizer.Add(vol_row, 0, wx.EXPAND | wx.ALL, 10)
        card_sizer.AddStretchSpacer()
        card_panel.SetSizer(card_sizer)

        # Main layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(left_panel, 0, wx.EXPAND)
        main_sizer.Add(card_panel, 1, wx.EXPAND | wx.ALL, 12)
        panel.SetSizer(main_sizer)

        # Timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)

        # Event bindings
        btn_load.Bind(wx.EVT_BUTTON, self.on_load)
        btn_prev.Bind(wx.EVT_BUTTON, self.on_prev)
        btn_play.Bind(wx.EVT_BUTTON, self.on_play_pause)
        btn_next.Bind(wx.EVT_BUTTON, self.on_next)

        self.playlist.Bind(wx.EVT_LISTBOX_DCLICK, self.on_playlist_dclick)
        self.vol_slider.Bind(wx.EVT_SLIDER, self.on_volume_change)
        self.pos_slider.Bind(wx.EVT_SLIDER, self.on_seek)
        self.search_ctrl.Bind(wx.EVT_TEXT, self.on_search)
        self.search_ctrl.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.on_search_cancel)

        self.update_playlist_display()
        self.mc.SetVolume(self.vol_slider.GetValue() / 100)
        self.Show()

    def update_playlist_display(self, filter_text=""):
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
        try:
            self.mc.Stop()
        except:
            pass
        self.timer.Stop()

        path = self.tracks[index]
        if self.mc.Load(path):
            self.current_index = index
            def setup_slider():
                length = self.mc.Length()
                if length and length > 0:
                    self.pos_slider.SetRange(0, length)
                    self.pos_slider.SetValue(0)
                    self.time_label.SetLabel(f"{self.ms_to_time(0)} / {self.ms_to_time(length)}")
                    self.mc.Play()
                    self.timer.Start(250)
                else:
                    wx.CallLater(100, setup_slider)
            setup_slider()
        else:
            wx.MessageBox(f"Unable to load {path}", "Error", wx.OK | wx.ICON_ERROR)

    def on_load(self, event):
        dlg = wx.FileDialog(
            self, "Choose audio files",
            wildcard="Audio files (*.mp3;*.wav;*.ogg;*.flac)|*.mp3;*.wav;*.ogg;*.flac|All files (*.*)|*.*",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE,
        )
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            for p in paths:
                self.tracks.append(p)
            self.update_playlist_display(self.search_ctrl.GetValue())
            if self.current_index == -1 and self.tracks:
                self.playlist.SetSelection(0)
                self.load_track(0)
        dlg.Destroy()

    def on_prev(self, event):
        if not self.tracks: return
        new_index = (self.current_index - 1) % len(self.tracks)
        self.current_index = new_index
        name = os.path.basename(self.tracks[new_index])
        idx = self.playlist.FindString(name)
        if idx != wx.NOT_FOUND:
            self.playlist.SetSelection(idx)
        self.load_track(new_index)

    def on_next(self, event):
        if not self.tracks: return
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
            self.timer.Start(250)
        else:
            self.mc.Pause()
            self.timer.Stop()

    def on_playlist_dclick(self, event):
        sel = self.playlist.GetSelection()
        if sel == wx.NOT_FOUND: return
        name = self.playlist.GetString(sel)
        for i, p in enumerate(self.tracks):
            if os.path.basename(p) == name:
                self.load_track(i)
                self.current_index = i
                break

    def on_volume_change(self, event):
        volume = self.vol_slider.GetValue() / 100
        try:
            self.mc.SetVolume(volume)
        except: pass

    def on_seek(self, event):
        length = self.mc.Length()
        if length > 0:
            pos = self.pos_slider.GetValue()
            pos = max(0, min(pos, length))
            try:
                self.mc.Seek(pos)
            except: pass
            self.time_label.SetLabel(f"{self.ms_to_time(pos)} / {self.ms_to_time(length)}")

    def on_timer(self, event):
        if self.mc.GetState() == wx.media.MEDIASTATE_PLAYING:
            length = self.mc.Length()
            if length > 0:
                pos = self.mc.Tell()
                pos = max(0, min(pos, length))
                self.pos_slider.SetRange(0, length)
                self.pos_slider.SetValue(pos)
                self.time_label.SetLabel(f"{self.ms_to_time(pos)} / {self.ms_to_time(length)}")
                if pos >= length - 500 and self.current_index is not None:
                    self.on_next(None)
        else:
            self.timer.Stop()

    def ms_to_time(self, ms):
        try:
            ms = int(ms)
            if ms <= 0: return "00:00"
            s = ms // 1000
            m = s // 60
            s = s % 60
            return f"{m:02d}:{s:02d}"
        except: return "00:00"

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
