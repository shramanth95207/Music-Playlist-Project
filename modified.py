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

        vol_row = wx
