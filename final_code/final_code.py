import wx
import wx.media
import os


class MusicPlayer(wx.Frame):
    def __init__(self):
       
        super().__init__(None, title="Music Player", size=(900, 600))
        self.SetBackgroundColour(wx.Colour(10, 10, 10))  

        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(10, 10, 10))

        # --- Data ---
        self.tracks = []
        self.display_names = []
        self.current_index = -1
        self.is_dragging = False

       
        self.updating_slider = False

        # --- Search bar ---
        self.search_ctrl = wx.SearchCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.search_ctrl.SetBackgroundColour(wx.Colour(20, 20, 20))  
        self.search_ctrl.SetForegroundColour(wx.Colour(0, 255, 100)) 

        # --- Playlist ---
        self.playlist = wx.ListBox(panel)
        self.playlist.SetBackgroundColour(wx.Colour(15, 15, 15))  
        self.playlist.SetForegroundColour(wx.Colour(50, 255, 100))  

        # --- Now Playing Label ---
        now_playing_label = wx.StaticText(panel, label=">> NOW PLAYING")
        font_title = now_playing_label.GetFont()
        font_title.PointSize = 15
        font_title = font_title.Bold()
        now_playing_label.SetFont(font_title)
        now_playing_label.SetForegroundColour(wx.Colour(0, 255, 100))  

        self.now_playing = wx.StaticText(panel, label="No track loaded")
        self.now_playing.SetFont(font_title)
        self.now_playing.SetForegroundColour(wx.Colour(100, 255, 150))  

       
        display_panel = wx.Panel(panel)
        display_panel.SetBackgroundColour(wx.Colour(10, 10, 10))  
        display_sizer = wx.BoxSizer(wx.VERTICAL)

        
        self.video_player = wx.media.MediaCtrl(
            display_panel,
            style=wx.SIMPLE_BORDER
        )

        try:
         
            video_path = r"e:\Python\Lib\py\animation.mp4"

            if os.path.exists(video_path):
                
                if self.video_player.Load(video_path):
                 
                    self.video_player.ShowPlayerControls(0)

               
                    self.video_player.Play()

                    
                    self.video_timer = wx.Timer(self, wx.ID_ANY)
                    self.Bind(wx.EVT_TIMER, self.on_video_timer, self.video_timer)
                    self.video_timer.Start(100)  

                else:
                  
                    error_text = wx.StaticText(display_panel, label="[VIDEO ERROR]")
                    error_text.SetForegroundColour(wx.Colour(255, 0, 0))  
                    display_sizer.Add(error_text, 1, wx.ALIGN_CENTER | wx.ALL, 20)

            else:
                
                no_file_text = wx.StaticText(
                    display_panel,
                    label=f"[FILE NOT FOUND]\n{video_path}"
                )
                no_file_text.SetForegroundColour(wx.Colour(255, 100, 0)) 
                display_sizer.Add(no_file_text, 1, wx.ALIGN_CENTER | wx.ALL, 20)

        except Exception as e:
          
            print(f"Error loading video: {e}")
            error_text = wx.StaticText(display_panel, label=f"[ERROR]\n{str(e)}")
            error_text.SetForegroundColour(wx.Colour(255, 0, 0))  
            display_sizer.Add(error_text, 1, wx.ALIGN_CENTER | wx.ALL, 20)

        
        display_sizer.Add(self.video_player, 1, wx.EXPAND | wx.ALL, 0)
        display_panel.SetSizer(display_sizer)

      
        self.mc = wx.media.MediaCtrl(panel, style=wx.SIMPLE_BORDER)
        self.mc.Hide()

        
        btn_load = wx.Button(panel, label="LOAD SONGS")
        btn_prev = wx.Button(panel, label="<< Prev")
        btn_play = wx.Button(panel, label="PLAY/PAUSE")
        btn_next = wx.Button(panel, label="NEXT >>")

     
        for btn in [btn_load, btn_prev, btn_play, btn_next]:
            btn.SetBackgroundColour(wx.Colour(0, 150, 75))  
            btn.SetForegroundColour(wx.WHITE)  
            font = btn.GetFont()
            font.PointSize = 10
            btn.SetFont(font)

        # --- Volume slider ---
        vol_label = wx.StaticText(panel, label="VOLUME")
        vol_label.SetForegroundColour(wx.Colour(0, 255, 100)) 
        self.vol_slider = wx.Slider(
            panel, value=70, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL
        )
        self.vol_slider.SetBackgroundColour(wx.Colour(20, 20, 20))  

        # --- Progress slider ---
        prog_label = wx.StaticText(panel, label="PROGRESS")
        prog_label.SetForegroundColour(wx.Colour(0, 255, 100))  
        self.pos_slider = wx.Slider(
            panel, value=0, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL
        )
        self.pos_slider.SetBackgroundColour(wx.Colour(20, 20, 20))  

        # time label
        self.time_label = wx.StaticText(panel, label="00:00 / 00:00")
        font_time = self.time_label.GetFont()
        font_time.PointSize = 11
        self.time_label.SetFont(font_time)
        self.time_label.SetForegroundColour(wx.Colour(50, 255, 150))

        # --- Layout ---
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        vol_sizer = wx.BoxSizer(wx.HORIZONTAL)
        prog_sizer = wx.BoxSizer(wx.VERTICAL)

        # left: playlist title + search + playlist
        playlist_title = wx.StaticText(panel, label="PLAYLIST")
        font_pl = playlist_title.GetFont()
        font_pl.PointSize = 12
        font_pl = font_pl.Bold()
        playlist_title.SetFont(font_pl)
        playlist_title.SetForegroundColour(wx.Colour(0, 255, 100)) 

        left_sizer.Add(playlist_title, 0, wx.ALL, 8)
        left_sizer.Add(self.search_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        left_sizer.Add(self.playlist, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        # buttons
        btn_sizer.Add(btn_load, 0, wx.ALL, 5)
        btn_sizer.Add(btn_prev, 0, wx.ALL, 5)
        btn_sizer.Add(btn_play, 0, wx.ALL, 5)
        btn_sizer.Add(btn_next, 0, wx.ALL, 5)

        # volume row
        vol_sizer.Add(vol_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        vol_sizer.Add(self.vol_slider, 1, wx.EXPAND)

        # progress row
        prog_sizer.Add(prog_label, 0, wx.LEFT | wx.TOP, 5)
        prog_sizer.Add(self.pos_slider, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)
        prog_sizer.Add(self.time_label, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # right side
        right_sizer.Add(now_playing_label, 0, wx.ALL, 8)
        right_sizer.Add(self.now_playing, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        right_sizer.Add(display_panel, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 0)
        right_sizer.Add(prog_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
        right_sizer.Add(btn_sizer, 0, wx.CENTER | wx.ALL, 5)
        right_sizer.Add(vol_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        main_sizer.Add(left_sizer, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(right_sizer, 2, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(main_sizer)

        # --- Timer for audio ---
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)

        # --- Bindings ---
        btn_load.Bind(wx.EVT_BUTTON, self.on_load)
        btn_prev.Bind(wx.EVT_BUTTON, self.on_prev)
        btn_play.Bind(wx.EVT_BUTTON, self.on_play_pause)
        btn_next.Bind(wx.EVT_BUTTON, self.on_next)

        self.playlist.Bind(wx.EVT_LISTBOX_DCLICK, self.on_playlist_dclick)
        self.vol_slider.Bind(wx.EVT_SLIDER, self.on_volume_change)

        # For progress slider:
        
        self.pos_slider.Bind(wx.EVT_LEFT_DOWN, self.on_slider_down)
        self.pos_slider.Bind(wx.EVT_LEFT_UP, self.on_slider_up)
        self.pos_slider.Bind(wx.EVT_SLIDER, self.on_seek)

        self.search_ctrl.Bind(wx.EVT_TEXT, self.on_search)
        self.search_ctrl.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.on_search_cancel)

        self.update_playlist_display()
        self.mc.SetVolume(self.vol_slider.GetValue() / 100)

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

        try:
            self.mc.Stop()
        except Exception:
            pass
        self.timer.Stop()

        path = self.tracks[index]
        if self.mc.Load(path):
            self.current_index = index
            self.now_playing.SetLabel(os.path.basename(path))

            def setup_slider():
                length = self.mc.Length()
                if length and length > 0:
              
                    self.updating_slider = True
                    try:
                        self.pos_slider.SetRange(0, length)
                        self.pos_slider.SetValue(0)
                    finally:
                        self.updating_slider = False

                    self.time_label.SetLabel(f"{self.ms_to_time(0)} / {self.ms_to_time(length)}")
                    self.mc.Play()
                    self.timer.Start(250)
                else:
                    wx.CallLater(100, setup_slider)

            setup_slider()
        else:
            wx.MessageBox(f"Unable to load {path}", "Error", wx.OK | wx.ICON_ERROR)

    def on_video_timer(self, event):
        """Loop video when it finishes - checks every 100ms"""
        try:
          
            if self.video_player.GetState() == wx.media.MEDIASTATE_STOPPED:
              
                self.video_player.Seek(0)
                
                self.video_player.Play()
        except Exception:
            pass

    # -------------- events -------------------

    def on_load(self, event):
        dlg = wx.FileDialog(
            self,
            message="Choose audio files",
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
        if not self.tracks:
            return
        new_index = (self.current_index - 1) % len(self.tracks)
        self.current_index = new_index
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
            self.timer.Start(250)
        else:
            self.mc.Pause()
            self.timer.Stop()

    def on_playlist_dclick(self, event):
        sel = self.playlist.GetSelection()
        if sel == wx.NOT_FOUND:
            return
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
        except Exception:
            pass
        # allow default processing as well
        event.Skip()

    def on_slider_down(self, event):

        self.is_dragging = True
        try:
            self.timer.Stop()
        except Exception:
            pass
        
        event.Skip()

    def on_slider_up(self, event):
     
        self.is_dragging = False
        try:
            pos = self.pos_slider.GetValue()
            if self.mc.Length() > 0:
                try:
                    self.mc.Seek(pos)
                except Exception:
                    pass
                self.time_label.SetLabel(f"{self.ms_to_time(pos)} / {self.ms_to_time(self.mc.Length())}")
        except Exception:
            pass

        if self.mc.GetState() == wx.media.MEDIASTATE_PLAYING:
            try:
                self.timer.Start(250)
            except Exception:
                pass

     
        event.Skip()

    def on_seek(self, event):
   
        if self.updating_slider:
            return

        try:
            pos = event.GetInt()
        except Exception:
            pos = self.pos_slider.GetValue()

        length = self.mc.Length()
        if length > 0:
            pos = max(0, min(pos, length))
            try:
                
                self.mc.Seek(pos)
            except Exception:
                pass
            self.time_label.SetLabel(f"{self.ms_to_time(pos)} / {self.ms_to_time(length)}")

       
        event.Skip()

    def on_timer(self, event):
        if self.mc.GetState() == wx.media.MEDIASTATE_PLAYING:
            length = self.mc.Length()
            if length > 0:
                pos = self.mc.Tell()
                if pos < 0:
                    pos = 0
                elif pos > length:
                    pos = length
                if not self.is_dragging:
                   
                    self.updating_slider = True
                    try:
                        self.pos_slider.SetRange(0, length)
                        self.pos_slider.SetValue(pos)
                    finally:
                        self.updating_slider = False
                self.time_label.SetLabel(f"{self.ms_to_time(pos)} / {self.ms_to_time(length)}")

              
                if pos >= length - 500 and self.current_index is not None:
                    self.on_next(None)
        else:
            try:
                self.timer.Stop()
            except Exception:
                pass

    def ms_to_time(self, ms):
        """Convert milliseconds to MM:SS"""
        try:
            ms = int(ms)
            if ms <= 0:
                return "00:00"
            s = ms // 1000
            m = s // 60
            s = s % 60
            return f"{m:02d}:{s:02d}"
        except Exception:
            return "00:00"

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

