# -*- coding:utf-8 -*-
'''
#TODO streamplot() 流線圖 多顏色
'''
#try:
if True:
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from pathlib import Path
    import warnings
    import matplotlib.font_manager as fm
    import matplotlib.tri as tri
    import matplotlib.gridspec as gridspec
    from matplotlib.colors import LinearSegmentedColormap
    from mpl_toolkits.basemap import Basemap
    from mpl_toolkits.mplot3d.axes3d import Axes3D
    import seaborn as sns
    import numpy as np
    import os
    import imageio, glob
    import cartopy
    import cartopy.feature as cfeature
    import cartopy.crs as ccrs
    from windrose import WindroseAxes
    
    
    #from cmapdict import cmaplist
    #from richTable import printTable, getTableTime
    #from configure import ConfigManager
    
    from pymeili.cmapdict import cmaplist
    from pymeili.richTable import printTable, getTableTime
    from pymeili.configure import ConfigManager
    

    # global variables
    global production_name, production_time
    production_name = []
    production_time = []
    
    _fig_ = None
    _axes_ = None
    _ax_ = None
    _last_mappable_ = None


    
    # ignore specific warnings
    warnings.filterwarnings(
        "ignore",
        message=r".*facecolor will have no effect.*",
        category=UserWarning
    )
    # 忽略 tight_layout 無法處理 GeoAxes 的警告
    warnings.filterwarnings(
        "ignore",
        message=r".*Axes that are not compatible with tight_layout.*",
        category=UserWarning
    )
    
    
    # Fundamental Config
    CURRENT_FILE = Path(__file__).resolve()
    MOTHER_PATH = CURRENT_FILE.parent
    CONFIG_PATH = MOTHER_PATH / "pymeili_resource" / "config.ini"

    # 初始化設定管理器 (不存在時會自動建立 config.ini)
    config = ConfigManager(CONFIG_PATH)

    # 讀取配置函數路徑
    def inspect_resource():
        """印出資源資料夾路徑"""
        resource_path = MOTHER_PATH / "pymeili_resource"
        print(f"\033[44m[pymeili Info]\033[0m Resource path: {resource_path}")
        
    # 重設配置檔案
    def default():
        config._create_default_config()
        if not config.get("General", "MuteInfo", bool):
            print("\033[44m[pymeili Info]\033[0m All Configs are set to default.")
        return None

    class Mute:
        def __init__(self, config: ConfigManager = None):
            self.config = config if config else globals()['config']  # 使用全域的 config
            self.info = self.config.get("General", "MuteInfo", bool)
            self.warning = self.config.get("General", "MuteWarning", bool)

        def __get__(self):
            return self

        def change(self, info=None, warning=None):
            """修改靜音設定"""
            if info is not None:
                self.info = bool(info)
                self.config.set("General", "MuteInfo", self.info)
            if warning is not None:
                self.warning = bool(warning)
                self.config.set("General", "MuteWarning", self.warning)
            self.config.save()

        def inspect(self):
            """檢查目前靜音狀態"""
            print("\033[44m[pymeili Info]\033[0m Mute Config:")
            print(f"\tMute.info:\t\t{self.config.get('General', 'MuteInfo', bool)}")
            print(f"\tMute.warning:\t\t{self.config.get('General', 'MuteWarning', bool)}")

        def default(self):
            """重設為預設值 (全部 False)"""
            self.info = False
            self.warning = False
            self.config.set("General", "MuteInfo", False)
            self.config.set("General", "MuteWarning", False)
            self.config.save()

        def get(self, key):
            """取得單一設定"""
            if key == "info":
                return self.config.get("General", "MuteInfo", bool)
            elif key == "warning":
                return self.config.get("General", "MuteWarning", bool)
            else:
                raise TypeError(f"\033[41m[pymeili Error]\033[0m Mute.get() got an unexpected keyword argument: '{key}'")


    class FontSize:
        def __init__(self, config: ConfigManager = None):
            self.config = config if config else globals()['config']  # 使用全域的 config
            # 對應原本 title/subtitle/... 的字級到 H1~H6
            self.title = self.config.get("FontSize", "H1", int)
            self.subtitle = self.config.get("FontSize", "H2", int)
            self.label = self.config.get("FontSize", "H3", int)
            self.ticklabel = self.config.get("FontSize", "H4", int)
            self.clabel = self.config.get("FontSize", "H5", int)
            self.legend = self.config.get("FontSize", "H3", int)   # legend 沿用 H3
            self.text = self.config.get("FontSize", "H3", int)     # text 也沿用 H3

        def __getitem__(self):
            return self

        def change(self, title=None, subtitle=None, label=None, ticklabel=None, clabel=None, legend=None, text=None):
            if title is not None:
                self.title = int(title)
                self.config.set("FontSize", "H1", self.title)
            if subtitle is not None:
                self.subtitle = int(subtitle)
                self.config.set("FontSize", "H2", self.subtitle)
            if label is not None:
                self.label = int(label)
                self.config.set("FontSize", "H3", self.label)
            if ticklabel is not None:
                self.ticklabel = int(ticklabel)
                self.config.set("FontSize", "H4", self.ticklabel)
            if clabel is not None:
                self.clabel = int(clabel)
                self.config.set("FontSize", "H3", self.clabel)
            if legend is not None:
                self.legend = int(legend)
                self.config.set("FontSize", "H5", self.legend)
            if text is not None:
                self.text = int(text)
                self.config.set("FontSize", "H6", self.text)
            self.config.save()

        def default(self):
            defaults = {"H1": 30, "H2": 24, "H3": 20, "H4": 18, "H5": 15, "H6": 12}
            for k, v in defaults.items():
                self.config.set("FontSize", k, v)
            self.config.save()
            # 更新屬性
            self.__init__(self.config)

        def get(self, key):
            mapping = {
                "title": ("FontSize", "H1"),
                "subtitle": ("FontSize", "H2"),
                "label": ("FontSize", "H3"),
                "ticklabel": ("FontSize", "H4"),
                "clabel": ("FontSize", "H3"),
                "legend": ("FontSize", "H5"),
                "text": ("FontSize", "H6"),
            }
            if key not in mapping:
                raise TypeError(f"\033[41m[pymeili Error]\033[0m FontSize.get() got an unexpected keyword argument: '{key}'")
            section, option = mapping[key]
            return self.config.get(section, option, int)

        def inspect(self):
            print("\033[44m[pymeili Info]\033[0m Font Size Config:")
            print(f"\tFontSize.title:\t\t{self.get('title')}")
            print(f"\tFontSize.subtitle:\t{self.get('subtitle')}")
            print(f"\tFontSize.label:\t\t{self.get('label')}")
            print(f"\tFontSize.ticklabel:\t{self.get('ticklabel')}")
            print(f"\tFontSize.clabel:\t{self.get('clabel')}")
            print(f"\tFontSize.legend:\t{self.get('legend')}")
            print(f"\tFontSize.text:\t\t{self.get('text')}")


    class FontScale:
        def __init__(self, config: ConfigManager = None):
            self.config = config if config else globals()['config']  # 使用全域的 config
            self.scale = self.config.get("General", "FontScale", float)

        def __getitem__(self):
            return self

        def default(self):
            self.scale = 1.0
            self.config.set("General", "FontScale", self.scale)
            self.config.save()

        def change(self, scale):
            self.scale = float(scale)
            self.config.set("General", "FontScale", self.scale)
            self.config.save()

        def get(self):
            return self.config.get("General", "FontScale", float)

        def inspect(self):
            print(f"\033[44m[pymeili Info]\033[0m Font Scale Config: {self.get()}")


    # True Fontsize = Fontsize * Fontscale
    def _GetFontSize_(key):
        if key in ["title", "subtitle", "label", "ticklabel", "clabel", "legend", "text"]:
            return FontSize().get(key) * FontScale().get()
        else: raise TypeError(f"\033[45m[pymeili inner Error]\033[0m GetFontSize() got an unexpected keyword argument: '{key}'")
    
    # FontFamily Config
    class FontFamily:
        def __init__(self, config: ConfigManager = None):
            self.config = config if config else globals()['config']  # 使用全域的 config
            self.resource_path = Path(__file__).resolve().parent / "pymeili_resource"

            # 載入字型路徑
            self.fontpath_default = self._resolve_font("default")
            self.fontpath_bold = self._resolve_font("bold")
            self.fontpath_black = self._resolve_font("black")
            self.fontpath_ocr = self._resolve_font("ocr")
            self.fontpath_kl = self._resolve_font("kl")
            self.fontpath_zh = self._resolve_font("zh")
            self.fontpath_zh_bold = self._resolve_font("zh_bold")

        def __getitem__(self):
            return self

        def _resolve_font(self, key: str) -> Path:
            """取得 matplotlib 可用的字型完整路徑"""
            font_file = self.config.get("FontFamily", key)
            return Path(mpl.get_data_path(), self.resource_path / font_file)

        def default(self):
            """回復預設字型設定"""
            defaults = {
                "default": "futura_default_bt.ttf",
                "bold": "Futura_Heavy_font.ttf",
                "black": "Futura_Extra_Black_font.ttf",
                "ocr": "OCR-A_Regular.ttf",
                "kl": "KleinCondensed-Medium.ttf",
                "zh": "HarmonyOS_Sans_TC_Regular.ttf",
                "zh_bold": "HarmonyOS_Sans_TC_Bold.ttf"
            }
            for k, v in defaults.items():
                self.config.set("FontFamily", k, v)
            self.config.save()
            self.__init__(self.config)  # 重新載入

        def get(self, key="default") -> Path:
            """依 key 取得字型路徑"""
            valid_keys = ["default", "bold", "black", "ocr", "kl", "zh", "zh_bold"]
            if key not in valid_keys:
                raise TypeError(
                    f"\033[41m[pymeili Error]\033[0m FontFamily.get() got an unexpected keyword argument: '{key}'. "
                    f"Valid keys: {', '.join(valid_keys)}"
                )
            return self._resolve_font(key)

        def change(self, **kwargs):
            """
            修改某個字型檔案路徑
            用法：
                font.change(default="path/to/font.ttf", zh="path/to/zh.ttf")
            """
            for key, path in kwargs.items():
                if not os.path.isfile(path):
                    raise FileNotFoundError(
                        f"\033[41m[pymeili Error]\033[0m FontFamily.change() got an invalid font path: '{path}'."
                    )
                self.config.set("FontFamily", key, os.path.basename(path))
            self.config.save()
            self.__init__(self.config)  # 更新屬性

        def inspect(self):
            """印出目前字型設定"""
            print("\033[44m[pymeili Info]\033[0m Font Family Config:")
            for key in ["default", "bold", "black", "ocr", "kl", "zh", "zh_bold"]:
                print(f"\tFontFamily.{key}:\t{self.config.get('FontFamily', key)}")

    # 設定主題
    class Theme:
        def __init__(self, config: ConfigManager = None):
            self.config = config if config else globals()['config']  # 使用全域的 config
            self.theme = self.config.get("General", "Theme", str)
            
        def __getitem__(self):
            return self

        def default(self):
            self.theme = "light"
            self.config.set("General", "Theme", "light")
            self.config.save()

        def switch(self):
            if self.theme == "light":
                self.theme = "dark"
            else:
                self.theme = "light"
            self.config.set("General", "Theme", self.theme)
            self.config.save()

        def get(self) -> str:
            return self.config.get("General", "Theme", str)

        def change(self, theme: str):
            theme_map = {
                "light": "light", "l": "light", "white": "light", "w": "light", "default": "light",
                "dark": "dark", "d": "dark", "black": "dark", "b": "dark"
            }
            if theme not in theme_map:
                raise TypeError(
                    f"\033[41m[pymeili Error]\033[0m Theme.change() got an unexpected keyword argument: '{theme}'. 'light' or 'dark' is valid."
                )
            self.theme = theme_map[theme]
            self.config.set("General", "Theme", self.theme)
            self.config.save()

        def inspect(self):
            print(f"\033[44m[pymeili Info]\033[0m Theme Config: {self.config.get('General', 'Theme', str)}")

    # 設定線寬
    class Linewidth:
        def __init__(self, config: ConfigManager = None):
            self.config = config if config else globals()['config']  # 使用全域的 config
            self.width = self.config.get("LineWidth", "default", int)

        def __getitem__(self):
            return self

        def default(self):
            self.width = 2
            self.config.set("LineWidth", "default", 2)
            self.config.save()

        def change(self, width: int):
            if not isinstance(width, int):
                raise TypeError(
                    f"\033[41m[pymeili Error]\033[0m Linewidth.change() got an unexpected keyword argument: '{width}'. int type is required."
                )
            self.width = width
            self.config.set("LineWidth", "default", width)
            self.config.save()

        def get(self) -> int:
            return self.config.get("LineWidth", "default", int)

        def inspect(self):
            print(f"\033[44m[pymeili Info]\033[0m Linewidth Config: {self.config.get('LineWidth', 'default', int)}")
            

    # Color Config
    class Color:
        color_keys = ["bg", "fg", "bg2", "fg2", "fg3", "fg4", "fg5", "fg6", "fg7", "fg8", "fg9"]
        def __init__(self, config: ConfigManager = None, theme: Theme = None):
            self.config = config if config else globals()['config']  # 使用全域的 config
            self.theme = theme if theme else Theme(config)
            self.load_colors()

        def load_colors(self):
            t = self.theme.get()
            section = "ColorsLight" if t == "light" else "ColorsDark"
            for key in self.color_keys:
                setattr(self, key, self.config.get(section, key, str))

        def __getitem__(self):
            return self

        def default(self):
            # Light theme defaults
            light_defaults = {
                "bg": "#FFFFFF", "fg": "#000000", "bg2": "#D7F0FB", "fg2": "#10A0D0",
                "fg3": "#AD025B", "fg4": "#B59457", "fg5": "#933318", "fg6": "#007F00",
                "fg7": "#FFA500", "fg8": "#C0C1C0", "fg9": "#000000"
            }
            # Dark theme defaults
            dark_defaults = {
                "bg": "#000000", "fg": "#FFFFFF", "bg2": "#003264", "fg2": "#10A0D0",
                "fg3": "#AD025B", "fg4": "#B59457", "fg5": "#933318", "fg6": "#007F00",
                "fg7": "#FFA500", "fg8": "#777777", "fg9": "#FFFFFF"
            }
            for key, value in light_defaults.items():
                self.config.set("ColorsLight", key, value)
            for key, value in dark_defaults.items():
                self.config.set("ColorsDark", key, value)
            self.config.save()
            self.load_colors()

        def change(self, theme=None, **kwargs):
            t = theme if theme else self.theme.get()
            if t in ["light", "l", "white", "w", "default"]:
                section = "ColorsLight"
            elif t in ["dark", "d", "black", "b"]:
                section = "ColorsDark"
            else:
                raise TypeError(f"\033[41m[pymeili Error]\033[0m Color.change() got an unexpected theme: '{t}'. 'light' or 'dark' is valid.")

            for key, value in kwargs.items():
                if key not in self.color_keys:
                    raise KeyError(f"\033[41m[pymeili Error]\033[0m Invalid color key: '{key}'")
                setattr(self, key, value)
                self.config.set(section, key, value)
            self.config.save()

        def get(self, key):
            if key not in self.color_keys:
                raise KeyError(f"\033[41m[pymeili Error]\033[0m Invalid color key: '{key}'")
            section = "ColorsLight" if self.theme.get() == "light" else "ColorsDark"
            return self.config.get(section, key)

        def get_keys(self):
            return self.color_keys

        def inspect(self):
            print(f"\033[44m[pymeili Info]\033[0m Color Configs:")
            for section in ["ColorsLight", "ColorsDark"]:
                print(f"\t{section}:")
                for key in self.color_keys:
                    print(f"\t\t{key} = {self.config.get(section, key, str)}")

    
    # True Color
    def _GetColorCode_(key):
        # 檢查key的類型
        if type(key) == str:
            if key in ["bg", "fg", "bg2", "fg2", "fg3", "fg4", "fg5", "fg6", "fg7", "fg8", "fg9"]:
                return Color().get(key)
            elif key[0] == '#' and len(key) == 7:
                return key
            else: raise TypeError(f"\033[45m[pymeili inner Error]\033[0m GetColorCode() got an unexpected keyword argument: '{key}'")
        elif type(key) == list:
            for i in range(len(key)):
                if key[i] in ["bg", "fg", "bg2", "fg2", "fg3", "fg4", "fg5", "fg6", "fg7", "fg8", "fg9"]:
                    key[i] = Color().get(key[i])
                elif key[i][0] == '#' and len(key[i]) == 7:
                    pass
                else: raise TypeError(f"\033[45m[pymeili inner Error]\033[0m GetColorCode() got an unexpected keyword argument: '{key}'")
            return key
        else: raise TypeError(f"\033[45m[pymeili inner Error]\033[0m GetColorCode() got an unexpected keyword argument: '{key}'")
                
    def _set_last_mappable(mappable):
        """更新全域最後一次繪圖對象 (scatter, contourf, pcolormesh, imshow, hexbin)"""
        global _last_mappable_
        _last_mappable_ = mappable
        return mappable


    def initfig(
        nrows=1, ncols=1,
        figsize=(8, 6),
        theme=None,
        width_ratios=None, height_ratios=None,
        wspace=0.2, hspace=0.3
    ):
        """建立 figure 並設定 theme、figsize 與子圖排版 (GridSpec + 全域管理)"""

        global _fig_, _axes_

        # 設定主題
        if theme is None:
            theme = Theme().get()
        Theme().change(theme)

        # 建立 figure
        fig = plt.figure(figsize=figsize)
        fig.set_facecolor(_GetColorCode_("bg"))

        # 如果只有一個 subplot 且無比例需求
        if nrows == 1 and ncols == 1 and not width_ratios and not height_ratios:
            ax = fig.add_subplot(111)
            _fig_, _axes_ = fig, np.array([[ax]])
            return fig, _axes_

        # 否則使用 GridSpec 管理子圖比例
        gs = gridspec.GridSpec(
            nrows, ncols, figure=fig,
            width_ratios=width_ratios,
            height_ratios=height_ratios,
            wspace=wspace, hspace=hspace
        )

        axes = []
        for i in range(nrows):
            row_axes = []
            for j in range(ncols):
                row_axes.append(fig.add_subplot(gs[i, j]))
            axes.append(row_axes)

        axes = np.array(axes)

        _fig_, _axes_ = fig, axes
        return fig, axes


    def initax(row=0, col=0, projection=None, background=True):
        """初始化單一子圖，設定 projection / background / 全域 _ax_"""
        global _fig_, _axes_, _ax_

        if _fig_ is None or _axes_ is None:
            # 如果還沒 initfig，自動建一個
            initfig()

        ax = _axes_[row, col]

        if projection is not None:
            # 移除原 ax，用 projection 取代
            _fig_.delaxes(ax)
            ax = _fig_.add_subplot(_axes_.shape[0], _axes_.shape[1],
                                row * _axes_.shape[1] + col + 1,
                                projection=projection)
            _axes_[row, col] = ax

        # 套用背景
        BackgroundHandler.set_background(ax, background)

        # 更新全域 _ax_
        _ax_ = ax
        return _ax_


    def setfig(fig, axes=None):
        """手動更換全域 fig 與 axes"""
        global _fig_, _axes_
        _fig_ = fig
        if axes is not None:
            _axes_ = axes
        return _fig_, _axes_


    def setax(ax):
        """手動更換全域 ax"""
        global _ax_
        _ax_ = ax
        return _ax_

    # =====================================================
    # Background Handler
    # =====================================================
    class BackgroundHandler:
        @staticmethod
        def set_background(ax, background):
            """根據軸類型與背景參數設定顏色"""

            if isinstance(ax, Axes3D):
                if background:
                    ax.xaxis.pane.set_facecolor(_GetColorCode_("bg2"))
                    ax.yaxis.pane.set_facecolor(_GetColorCode_("bg2"))
                    ax.zaxis.pane.set_facecolor(_GetColorCode_("bg2"))
                else:
                    ax.xaxis.pane.set_facecolor(_GetColorCode_("bg"))
                    ax.yaxis.pane.set_facecolor(_GetColorCode_("bg"))
                    ax.zaxis.pane.set_facecolor(_GetColorCode_("bg"))

            elif isinstance(ax, plt.Axes):
                ax.set_facecolor(_GetColorCode_("bg2") if background else _GetColorCode_("bg"))

            elif isinstance(ax, WindroseAxes):
                ax.set_facecolor(_GetColorCode_("bg2") if background else _GetColorCode_("bg"))

            elif isinstance(ax, Basemap):
                if background:
                    ax.drawmapboundary(fill_color=_GetColorCode_("bg2"))
                    ax.fillcontinents(color=_GetColorCode_("bg"), lake_color=_GetColorCode_("bg2"))
                else:
                    ax.drawmapboundary(fill_color=_GetColorCode_("bg"))

            elif isinstance(ax, cartopy.mpl.geoaxes.GeoAxesSubplot):
                if background:
                    ax.add_feature(cfeature.NaturalEarthFeature(
                        category='physical', name='ocean',
                        scale='50m', facecolor=_GetColorCode_("bg2")))
                    ax.add_feature(cfeature.NaturalEarthFeature(
                        category='physical', name='land',
                        scale='50m', facecolor=_GetColorCode_("bg")))
                else:
                    ax.set_facecolor(_GetColorCode_("bg"))
            else:
                raise TypeError(f"\033[41m[pymeili Error]\033[0m Unsupported Axes type: {type(ax)}. Supported types: Axes3D, plt.Axes, WindroseAxes, Basemap, cartopy.mpl.geoaxes.GeoAxesSubplot.")
    
    # Basic Function for plot
    def plot(x=0, y=0, ax=None, color="fg", linestyle="-", linewidth=None, **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        ax.plot(x, y, color=_GetColorCode_(color), linestyle=linestyle, linewidth=linewidth, **kwargs)
        return ax
    
    def triplot(x=0, y=0, ax=None, color="fg", linestyle="-", linewidth=None, **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        triang = tri.Triangulation(x, y)
        ax.triplot(triang, color=_GetColorCode_(color), linestyle=linestyle, linewidth=linewidth, **kwargs)
        return ax
    
    def contour(x=0, y=0, z=0, ax=None, color="fg", colors=None, cmap=None, linewidth=None, levels=None, **kwargs):
        """
        Draw contour lines with extended support for cmap and multiple colors.

        Parameters
        ----------
        x, y, z : array-like
            Data for contouring.
        ax : matplotlib Axes, optional
            Target axes. If None, use global _ax_.
        color : str, optional
            Default single color (if colors and cmap are both None).
        colors : str or list, optional
            If str → passed to _GetColorCode_. 
            If list → interpreted as a color sequence.
        cmap : str or list, optional
            If str → passed to cmaplist(str). 
            If list → custom LinearSegmentedColormap from list.
        linewidth : float, optional
            Line width of contours.
        levels : int or list, optional
            Contour levels (same as matplotlib).
        """
        if linewidth is None:
            linewidth = Linewidth().get()
        global _ax_
        if ax is None:
            ax = _ax_

        # 處理 colors / cmap
        if colors is None:
            if cmap is None:
                # 傳統模式：單色
                colors = _GetColorCode_(color)
                cm = None
            else:
                # cmap 模式
                cm = cmaplist(cmap)
                colors = None
        else:
            if cmap is None:
                # colors 模式：允許單色或多色 list
                if isinstance(colors, str):
                    colors = _GetColorCode_(colors)
                cm = None
            else:
                raise TypeError(f"\033[41m[pymeili Error]\033[0m contour() got unexpected keyword arguments: cannot specify both cmap and colors.")

        global CT
        CT = ax.contour(x, y, z, levels=levels, colors=colors, cmap=cm, linewidths=linewidth, **kwargs)
        return CT

    
    def clabel(ax=None, fontsize=None, **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("clabel")
        global _ax_
        if ax is None: ax = _ax_
        CL = ax.clabel(CT, **kwargs)
        for t in CL:
            t.set_font_properties(fm.FontProperties(fname=FontFamily().get("default"), size=fontsize))
        return ax
    
    def contourf(x=0, y=0, z=0, ax=None, cmap=None, colors=None, **kwargs):
        global _ax_, CTF
        if ax is None: ax = _ax_
        
        # === hatch-only 模式檢查 ===
        if "hatches" in kwargs and colors is not None:
            # 若 colors=['none', ...] 且有 hatches，強制走 hatch 模式
            CTF = ax.contourf(x, y, z, colors=colors, **kwargs)
            _set_last_mappable(CTF)
            return CTF
    
    
        if colors is None:
            if cmap is None:
                cmap = _GetColorCode_("fg") # 什麼都沒說，就用fg
            else:
                cmap = cmaplist(cmap) # cmap可為字串(關鍵字)或是list(自定義)，colors為None，則使用cmap
        else:
            if cmap is None:
                colors = _GetColorCode_(colors) # cmap為None，colors不為None，則使用colors
            else: # 同時指定cmap和colors，則報錯
                raise TypeError(f"\033[41m[pymeili Error]\033[0m contourf() got an unexpected keyword argument: 'cmap' and 'colors' cannot be specified at the same time.")
        
        
        if cmap is None:
            CTF = ax.contourf(x, y, z, colors=colors, **kwargs)
        if colors is None:
            CTF = ax.contourf(x, y, z, cmap=cmap, **kwargs)
        
        _set_last_mappable(CTF)  # 更新最後一次繪圖對象
        return CTF

        
    def tricontour(x=0, y=0, z=0, ax=None, color="fg", colors=None, linewidth=None, **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        if colors is None:
            colors = _GetColorCode_(color)
        else:
            colors = _GetColorCode_(colors)
        
        global CT
        CT = ax.tricontour(x, y, z, colors=colors, linewidths=linewidth, **kwargs)
        return ax

    def tricontourf(x=0, y=0, z=0, ax=None, cmap=None, colors=None,
                    linewidth=None, **kwargs):
        global _ax_, CTF
        if ax is None: ax = _ax_
        if linewidth is None: linewidth = Linewidth().get()

        # === hatch-only 模式檢查 ===
        if "hatches" in kwargs and colors is not None:
            # 若 colors=['none', ...] 且有 hatches，強制走 hatch 模式
            CTF = ax.contourf(x, y, z, colors=colors, **kwargs)
            _set_last_mappable(CTF)
            return CTF
        
        # cmap / colors 互斥判斷
        if colors is None:
            if cmap is None:
                cmap = _GetColorCode_("fg")  # 什麼都沒說，就用 fg
            else:
                cmap = cmaplist(cmap)
        else:
            if cmap is None:
                colors = _GetColorCode_(colors)
            else:
                raise TypeError(f"\033[41m[pymeili Error]\033[0m tricontourf() got an unexpected keyword argument: 'cmap' and 'colors' cannot be specified at the same time.")

        # 真正繪圖
        if cmap is None:
            CTF = ax.tricontourf(x, y, z, colors=colors, linewidths=linewidth, **kwargs)
        if colors is None:
            CTF = ax.tricontourf(x, y, z, cmap=cmap, linewidths=linewidth, **kwargs)

        # 更新懶人 colorbar 對象
        _set_last_mappable(CTF)

        return CTF

    
    def colorbar(ax=None, input=None, label='', ticks=None,
                labelsize=None, ticklabelsize=None, color=None,
                linewidth=None, shrink=0.95, aspect=15,
                fraction=0.05, pad=0.04, **kwargs):
        global _ax_, _last_mappable_
        if ax is None: ax = _ax_
        if input is None: input = _last_mappable_

        if input is None:
            raise RuntimeError(f"\033[41m[pymeili Error]\033[0m colorbar() has no valid mappable object. "
                            f"Did you forget to call scatter/contourf/pcolormesh/imshow first?")

        if labelsize is None: labelsize=_GetFontSize_("clabel")
        if ticklabelsize is None: ticklabelsize=_GetFontSize_("ticklabel")
        if color is None: color=_GetColorCode_("fg")
        else: color = _GetColorCode_(color)
        if linewidth is None: linewidth=Linewidth().get()

        CB = plt.colorbar(input, ax=ax, shrink=shrink, aspect=aspect,
                        fraction=fraction, pad=pad, ticks=ticks, **kwargs)

        # 標籤與樣式設定
        CB.set_label(label, fontproperties=fm.FontProperties(fname=FontFamily().get("default"),
                                                            size=labelsize), color=color)
        CB.ax.tick_params(color=color, labelsize=ticklabelsize, width=linewidth)
        CB.outline.set_edgecolor(color)
        CB.outline.set_linewidth(linewidth)

        for l in CB.ax.get_yticklabels() + CB.ax.get_xticklabels():
            l.set_font_properties(fm.FontProperties(fname=FontFamily().get("default"),
                                                    size=ticklabelsize))
            l.set_color(color)

        return CB

    
    def bar(x=0, y=0, ax=None, color="fg", width=0.8, edgewidth=Linewidth().get(), edgecolor="fg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.bar(x, y, color=_GetColorCode_(color), width=width, edgecolor=_GetColorCode_(edgecolor), linewidth=edgewidth, **kwargs)
        return ax
    
    def barh(x=0, y=0, ax=None, color="fg", height=0.8, edgewidth=Linewidth().get(), edgecolor="fg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.barh(x, y, color=_GetColorCode_(color), height=height, edgecolor=_GetColorCode_(edgecolor), linewidth=edgewidth, **kwargs)
        return ax
    
    def hist(x=0, ax=None, color="fg", bins=10, linewidth=None, **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        ax.hist(x, color=_GetColorCode_(color), bins=bins, linewidth=linewidth, **kwargs)
        return ax
    
    def hist2d(x=0, y=0, ax=None, color="fg", bins=10, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.hist2d(x, y, color=_GetColorCode_(color), bins=bins, **kwargs)
        return ax
    
    def scatter(x=0, y=0, ax=None, color="fg", colors=None, c=None, cmap=None,
                marker="o", s=20, edgecolor=None, linewidth=0.5, **kwargs):
        """
        Extended scatter plot with support for colormap, per-point colors, and marker edgecolor.

        Parameters
        ----------
        x, y : array-like
            Coordinates of points.
        ax : matplotlib Axes, optional
            Target axes. If None, use global _ax_.
        color : str, optional
            Default single color if no colors/cmap/c is specified.
        colors : list or str, optional
            - str: interpreted by _GetColorCode_
            - list: direct color sequence for each point
        c : array-like, optional
            Values mapped through cmap (typical usage in matplotlib).
        cmap : str or list, optional
            - str: passed to cmaplist(str)
            - list: custom colormap from list
        marker : str, optional
            Marker style.
        s : float or array, optional
            Marker size(s).
        edgecolor : str or list, optional
            Marker edge color. Default = same as facecolor if None.
        linewidth : float, optional
            Width of marker edges.
        """
        global _ax_
        if ax is None:
            ax = _ax_

        # edgecolor 預處理
        if edgecolor is not None:
            if isinstance(edgecolor, str):
                edgecolor = _GetColorCode_(edgecolor)

        # case 1: 使用 c + cmap
        if c is not None:
            if cmap is not None:
                cm = cmaplist(cmap)
            else:
                cm = None
            sc = ax.scatter(x, y, c=c, cmap=cm, marker=marker, s=s,
                            edgecolors=edgecolor, linewidths=linewidth, **kwargs)
            _set_last_mappable(sc)
            return sc

        # case 2: 使用 colors（list 或單色）
        if colors is not None:
            if isinstance(colors, str):
                colors = _GetColorCode_(colors)
            sc = ax.scatter(x, y, color=colors, marker=marker, s=s,
                            edgecolors=edgecolor, linewidths=linewidth, **kwargs)
            _set_last_mappable(sc)
            return sc

        # case 3: 使用單色 (舊行為)
        sc = ax.scatter(x, y, color=_GetColorCode_(color), marker=marker, s=s,
                        edgecolors=edgecolor, linewidths=linewidth, **kwargs)
        
        _set_last_mappable(sc)
        return sc


    
    def pie(x=0, ax=None, startangle=90, pctdistance=0.6, labeldistance=1.1, radius=1, labelsize=None, labelcolor="fg", widgesize=None, widgescolor="fg", counterclock=True, edgewidth=Linewidth().get(), edgecolor="bg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if labelsize is None: labelsize=_GetFontSize_("label")
        if widgesize is None: widgesize=_GetFontSize_("label")
        ax.pie(x, startangle=startangle, pctdistance=pctdistance, labeldistance=labeldistance, radius=radius, counterclock=counterclock, wedgeprops={'linewidth':edgewidth, 'edgecolor':_GetColorCode_(edgecolor)}, textprops={'fontsize':labelsize, 'color':_GetColorCode_(labelcolor)}, **kwargs)
        ax.axis('equal')
        return ax
    
    def polar(theta=0, r=0, ax=None, color="fg", linewidth=None, linestyle="-", **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        ax.plot(theta, r, color=_GetColorCode_(color), linewidth=linewidth, linestyle=linestyle, **kwargs)
        return ax
    
    def boxplot(x=0, ax=None, vert=True, patch_artist=True, showmeans = True, showcaps = True, showbox = True, widths = 0.5, facecolor="fg8", edgecolor="fg", boxlinewidth=Linewidth().get(), mediancolor="fg2", medianlinewidth=Linewidth().get(), meanmarker="o", meanmarkersize=5, meanmarkercolor="fg3", meanmarkeredgecolor="fg3", meanmarkerlinewidth=Linewidth().get(), whiskercolor="fg4", whiskerlinewidth=Linewidth().get(), capsize=3, capthick=Linewidth().get(), fliermarker="o", fliermarkersize=5, fliermarkercolor="fg5", fliermarkeredgecolor="fg5", fliermarkerlinewidth=Linewidth().get(), **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        boxprops = dict(linewidth=boxlinewidth, edgecolor=_GetColorCode_(edgecolor), facecolor=_GetColorCode_(facecolor))
        medianprops = dict(linewidth=medianlinewidth, color=_GetColorCode_(mediancolor))
        meanprops = dict(marker=meanmarker, markerfacecolor=_GetColorCode_(meanmarkercolor), markeredgecolor=_GetColorCode_(meanmarkeredgecolor), markeredgewidth=meanmarkerlinewidth, markersize=meanmarkersize)
        whiskerprops = dict(linewidth=whiskerlinewidth, color=_GetColorCode_(whiskercolor))
        capprops = dict(linewidth=capthick, color=_GetColorCode_(whiskercolor))
        flierprops = dict(marker=fliermarker, markerfacecolor=_GetColorCode_(fliermarkercolor), markeredgecolor=_GetColorCode_(fliermarkeredgecolor), markeredgewidth=fliermarkerlinewidth, markersize=fliermarkersize)
        ax.boxplot(x, vert=vert, patch_artist=patch_artist, showmeans=showmeans, showcaps=showcaps, showbox=showbox, widths=widths, boxprops=boxprops, medianprops=medianprops, meanprops=meanprops, whiskerprops=whiskerprops, capprops=capprops, flierprops=flierprops, **kwargs)
        return ax
    
    def text(x=0, y=0, s='', ax=None, fontsize=None, color="fg", fonttype="default", **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("text")
        if fonttype not in ["default", "bold", "black", "zh", "ocr", "zh_bold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'default', 'bold', 'black', 'zh', 'special', 'zh_bold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        ax.text(x, y, s, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
        return ax
    
    def textbox(x=0, y=0, s='', ax=None, fontsize=None, color="fg", fonttype="default", facecolor="bg", edgecolor="fg", boxalpha=1, boxpad=0.3, fill=True, edgewidth=None, mutation_aspect=None, **kwargs):
        if edgewidth is None: edgewidth=Linewidth().get()
        if fontsize is None: fontsize=_GetFontSize_("text")
        if fonttype not in ["default", "bold", "black", "zh", "ocr", "zh_bold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'default', 'bold', 'black', 'zh', 'special', 'zh_bold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        if mutation_aspect is None:
            boxstyle="square"
            ax.text(x, y, s, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), bbox=dict(boxstyle=boxstyle, facecolor=_GetColorCode_(facecolor), alpha=boxalpha, pad=boxpad, linewidth=edgewidth, fill=fill, edgecolor=_GetColorCode_(edgecolor)), **kwargs)
        else:
            boxstyle="round"
            ax.text(x, y, s, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), bbox=dict(boxstyle=boxstyle, facecolor=_GetColorCode_(facecolor), alpha=boxalpha, pad=boxpad, linewidth=edgewidth, fill=fill, mutation_aspect=mutation_aspect), **kwargs)
    
    def annotate_wedge(s='', xy=(0, 0), xytext=(0, 0), ax=None, fontsize=None, color="fg", arrowcolor="fg", fonttype="default", facecolor="bg", boxalpha=1, boxpad=0.3, fill=True, edgewidth=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if edgewidth is None: edgewidth=Linewidth().get()
        if fontsize is None: fontsize=_GetFontSize_("text")
        if fonttype not in ["default", "bold", "black", "zh", "ocr", "zh_bold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'default', 'bold', 'black', 'zh', 'special', 'zh_bold' or 'kl' is valid.")
        ax.annotate(s, xy=xy, xytext=xytext, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), arrowprops=dict(arrowstyle="wedge", color=_GetColorCode_(arrowcolor), linewidth=edgewidth), bbox=dict(boxstyle="square", facecolor=_GetColorCode_(facecolor), alpha=boxalpha, pad=boxpad, linewidth=edgewidth, fill=fill), **kwargs)
    
    def fill_between(x=0, y1=0, y2=0, ax=None, color="fg", alpha=0.5, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.fill_between(x, y1, y2, color=_GetColorCode_(color), alpha=alpha, **kwargs)
        return ax
    
    def fill_betweenx(x1=0, x2=0, y=0, ax=None, color="fg", alpha=0.5, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.fill_betweenx(x1, x2, y, color=_GetColorCode_(color), alpha=alpha, **kwargs)
        return ax
    
    def axhline(y=0, ax=None, color="fg", linestyle="-", linewidth=None, **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        ax.axhline(y, color=_GetColorCode_(color), linestyle=linestyle, linewidth=linewidth, **kwargs)
        return ax
    
    def axvline(x=0, ax=None, color="fg", linestyle="-", linewidth=None, **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        ax.axvline(x, color=_GetColorCode_(color), linestyle=linestyle, linewidth=linewidth, **kwargs)
        return ax
    
    def axhspan(ymin=0, ymax=1, xmin=0, xmax=1, ax=None, color=None, facecolor=None, linewidth=None, edgecolor=None, **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        if facecolor is not None:
            facecolor = _GetColorCode_(facecolor)
        if edgecolor is not  None:
            edgecolor = _GetColorCode_(edgecolor)
        if color is not None:
            color = _GetColorCode_(color)
        ax.axhspan(ymin, ymax, xmin=xmin, xmax=xmax, facecolor=facecolor, edgecolor=edgecolor, linewidth=linewidth, **kwargs)
        return ax
    
    def axvspan(xmin=0, xmax=1, ymin=0, ymax=1, ax=None, color=None, facecolor=None, linewidth=None, edgecolor=None, **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        if facecolor is not None:
            facecolor = _GetColorCode_(facecolor)
        if edgecolor is not  None:
            edgecolor = _GetColorCode_(edgecolor)
        if color is not None:
            color = _GetColorCode_(color)
        ax.axvspan(xmin, xmax, ymin=ymin, ymax=ymax, facecolor=facecolor, edgecolor=edgecolor, linewidth=linewidth, **kwargs)
        return ax
    
    
    def legend(label=None ,ax=None, fontsize=None, color="fg", frameon=True, framealpha=1, facecolor="bg", edgecolor="fg", edgewidth=None, title=None, title_fontsize=None, **kwargs):
        if edgewidth is None: edgewidth=Linewidth().get()
        if fontsize is None: fontsize=_GetFontSize_("legend")
        if title_fontsize is None: title_fontsize=_GetFontSize_("legend") * 1.2
        global _ax_
        if ax is None: ax = _ax_
        if label is None:
            if 'zorder' in kwargs:
                print("\033[43m[pymeili Warning]\033[0m legend() got an unexpected keyword argument: 'zorder' is not recommended in legend().")
                zorder = kwargs['zorder']
                kwargs.pop('zorder')
                LG = ax.legend(fontsize=fontsize, labelcolor=_GetColorCode_(color), frameon=frameon, framealpha=framealpha, facecolor=_GetColorCode_(facecolor), edgecolor=_GetColorCode_(edgecolor), title=title, prop=fm.FontProperties(fname=FontFamily().get("default"), size=fontsize), **kwargs)
                LG.set_zorder(zorder)
            else:
                LG = ax.legend(fontsize=fontsize, labelcolor=_GetColorCode_(color), frameon=frameon, framealpha=framealpha, facecolor=_GetColorCode_(facecolor), edgecolor=_GetColorCode_(edgecolor), title=title, prop=fm.FontProperties(fname=FontFamily().get("default"), size=fontsize), **kwargs)
            
        else:
            if 'zorder' in kwargs:
                print("\033[43m[pymeili Warning]\033[0m legend() got an unexpected keyword argument: 'zorder' is not recommended in legend().")
                zorder = kwargs['zorder']
                kwargs.pop('zorder')
                LG = ax.legend(label, fontsize=fontsize, labelcolor=_GetColorCode_(color), frameon=frameon, framealpha=framealpha, facecolor=_GetColorCode_(facecolor), edgecolor=_GetColorCode_(edgecolor), title=title, prop=fm.FontProperties(fname=FontFamily().get("default"), size=fontsize), **kwargs)
                LG.set_zorder(zorder)
            else:
                LG = ax.legend(label, fontsize=fontsize, labelcolor=_GetColorCode_(color), frameon=frameon, framealpha=framealpha, facecolor=_GetColorCode_(facecolor), edgecolor=_GetColorCode_(edgecolor), title=title, prop=fm.FontProperties(fname=FontFamily().get("default"), size=fontsize), **kwargs)
        
        LG.get_frame().set_boxstyle('Round', pad=0.2, rounding_size=-0.01)
        LG.get_frame().set_linewidth(edgewidth)
        if title is not None:
            #LG.get_title().set_fontsize(title_fontsize)
            LG.get_title().set_color(_GetColorCode_(color))  # optional: same color as labels
            LG.get_title().set_fontproperties(fm.FontProperties(fname=FontFamily().get("default"), size=title_fontsize))
        return ax
    
    def addlogo(logopath, x, y, width, height, alpha=1, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.imshow(logopath, extent=[x, x+width, y, y+height], alpha=alpha, **kwargs)
        return ax
    
    def barbs(x=0, y=0, u=0, v=0, ax=None, length=7, pivot='tip', c=None, barbcolor="fg", flagcolor="fg", cmap=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if c == 'auto':
            c = np.sqrt(u**2+v**2)
        if cmap is not None:
            global CTF
            cmap = cmaplist(cmap)
            CTF = ax.barbs(x, y, u, v, length=length, pivot=pivot, color=_GetColorCode_(barbcolor), flagcolor=_GetColorCode_(flagcolor), cmap=cmap, **kwargs)
            return ax
        if cmap is None:
            ax.barbs(x, y, u, v, length=length, pivot=pivot, color=_GetColorCode_(barbcolor), flagcolor=_GetColorCode_(flagcolor), **kwargs)
            return ax
        
    def quiver(x=0, y=0, u=0, v=0, ax=None, color="fg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if 'cmap' in kwargs:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m quiver() got an unexpected keyword argument: 'cmap' is not allowed in quiver(), use barbs() instead.")
        ax.quiver(x, y, u, v, color=_GetColorCode_(color), **kwargs)
        return ax
    
    def streamplot(x=0, y=0, u=0, v=0, ax=None, color="fg", linewidth=None, arrowstyle="-|>", arrowsize=1, density=1, **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        ax.streamplot(x, y, u, v, color=_GetColorCode_(color), linewidth=linewidth, arrowstyle=arrowstyle, arrowsize=arrowsize, density=density, **kwargs)
        return ax
    
    # Addtional Function for plot
    def inset_axes(bound, ax=None, **kwargs):
        global _ax_
        if bound==None: bound=[0.05, 0.05, 0.9, 0.9]
        if ax is None: ax = _ax_
        axins = ax.inset_axes(bound, **kwargs)
        return axins  
    
    def title(s='', ax=None, fontsize=None, color="fg", fonttype="bold", **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("title")
        if fonttype not in ["default", "bold", "black", "zh", "ocr", "zh_bold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'default', 'bold', 'black', 'zh', 'special', 'zh_bold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        ax.figure.suptitle(s, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
        return ax
    
    def lefttitle(s='', ax=None, fontsize=None, color="fg", fonttype="bold", loc='left', **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("title")
        if fonttype not in ["default", "bold", "black", "zh", "ocr", "zh_bold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'default', 'bold', 'black', 'zh', 'special', 'zh_bold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        ax.set_title(s, loc=loc, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
        return ax
    
    def centertitle(s='', ax=None, fontsize=None, color="fg", fonttype="bold", loc='center', **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("title")
        if fonttype not in ["default", "bold", "black", "zh", "ocr", "zh_bold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'default', 'bold', 'black', 'zh', 'special', 'zh_bold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        ax.set_title(s, loc=loc, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
        return ax
    
    def righttitle(s='', ax=None, fontsize=None, color="fg", fonttype="bold", loc='right', **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("title")
        if fonttype not in ["default", "bold", "black", "zh", "ocr", "zh_bold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'default', 'bold', 'black', 'zh', 'special', 'zh_bold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        ax.set_title(s, loc=loc, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
        return ax
    
    def pilltitle(x=0.25, y=0.985, s='', ax=None, fontsize=16, color="fg", facecolor="bg", edgecolor="fg", fonttype="default", **kwargs):
        if fonttype not in ["default", "bold", "black", "zh", "ocr", "zh_bold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'default', 'bold', 'black', 'zh', 'special', 'zh_bold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        prop = fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize)
        fig = gcf(ax)
        fig.text(
            x, y,  # 座標（圖框外），調整位置可視需要改變
            s, transform=ax.transAxes,
            fontproperties=prop,
            ha='center', va='top', color=_GetColorCode_(color), fontsize=16,
            bbox=dict(
                facecolor=_GetColorCode_(facecolor),
                edgecolor=_GetColorCode_(edgecolor),
                boxstyle='round,pad=0.35,rounding_size=0.95', linewidth=1.5
            ),
        )
        return ax
 
    def xlabel(s='', ax=None, fontsize=None, color="fg", fonttype="default", top=False, **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("label")
        if fonttype not in ["default", "bold", "black", "zh", "special"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m xlabel() got an unexpected keyword argument: fonttype='{fonttype}'.'default', 'bold', 'black', 'zh' or 'special' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        ax.set_xlabel(s, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
        if top:
            ax.tick_params(axis='x', labeltop=True)
            ax.xaxis.set_label_position('top')
            ax.xaxis.set_ticks_position('top')
        return ax
    
    def ylabel(s='', ax=None, fontsize=None, color="fg", fonttype="default", right=False, **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("label")
        if fonttype not in ["default", "bold", "black", "zh", "special"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m ylabel() got an unexpected keyword argument: fonttype='{fonttype}'. 'default', 'bold', 'black', 'zh' or 'special' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        ax.set_ylabel(s, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
        if right:
            ax.tick_params(axis='y', labelright=True)
            ax.yaxis.set_label_position('right')
            ax.yaxis.set_ticks_position('right')
        return ax
    
    def spines(top=True, right=True, bottom=True, left=True, ax=None, color='fg', linewidth=Linewidth().get(), **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if top:
            ax.spines['top'].set_color(_GetColorCode_(color))
            ax.spines['top'].set_linewidth(linewidth)
            ax.spines['top'].set_visible(True)
        if right:
            ax.spines['right'].set_color(_GetColorCode_(color))
            ax.spines['right'].set_linewidth(linewidth)
            ax.spines['right'].set_visible(True)
        if bottom:
            ax.spines['bottom'].set_color(_GetColorCode_(color))
            ax.spines['bottom'].set_linewidth(linewidth)
            ax.spines['bottom'].set_visible(True)
        if left:
            ax.spines['left'].set_color(_GetColorCode_(color))
            ax.spines['left'].set_linewidth(linewidth)
            ax.spines['left'].set_visible(True)
            
    def grid(ax=None, which='major', axis='both', color='fg8', linestyle=':', linewidth=Linewidth().get(), **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.grid(which=which, axis=axis, color=_GetColorCode_(color), linestyle=linestyle, linewidth=linewidth, **kwargs)
        return ax 
            
    def xticks(ticks=None, labels='auto', ax=None, fontsize=None, color="fg", fonttype="default", linewidth=Linewidth().get(), linelengths=5, top=False, direction='out', which='both', pad=5, **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("ticklabel")
        if fonttype not in ["default", "bold", "black", "zh", "ocr", "zh_bold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'default', 'bold', 'black', 'zh', 'special', 'zh_bold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        if ticks is None:
            ax.set_xticks([])
        else:
            ax.set_xticks(ticks)
        if labels is None:
            ax.set_xticklabels([])
        elif labels == 'auto':
            labels = [tick for tick in ticks]
            # transform ticks to str
            for i in range(len(labels)):
                labels[i] = str(labels[i])
            ax.set_xticklabels(labels, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
            ax.tick_params(axis='x', which=which, direction=direction, length=linelengths, width=linewidth, color=_GetColorCode_(color), top=top, pad=pad)
        else:
            ax.set_xticklabels(labels, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
            ax.tick_params(axis='x', which=which, direction=direction, length=linelengths, width=linewidth, color=_GetColorCode_(color), top=top, pad=pad)
        return ax
    
    def yticks(ticks=None, labels='auto', ax=None, fontsize=None, color="fg", fonttype="default", linewidth=Linewidth().get(), linelengths=5, right=False, direction='out', which='both', pad=5, **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("ticklabel")
        if fonttype not in ["default", "bold", "black", "zh", "ocr", "zh_bold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'default', 'bold', 'black', 'zh', 'special', 'zh_bold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        if ticks is None:
            ax.set_yticks([])
        else:
            ax.set_yticks(ticks)
        if labels is None:
            ax.set_yticklabels([])
        elif labels == 'auto':
            labels = [tick for tick in ticks]
            # transform ticks to str
            for i in range(len(labels)):
                labels[i] = str(labels[i])
            ax.set_yticklabels(labels, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
            ax.tick_params(axis='y', which=which, direction=direction, length=linelengths, width=linewidth, color=_GetColorCode_(color), right=right, pad=pad)
        else:
            ax.set_yticklabels(labels, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
            ax.tick_params(axis='y', which=which, direction=direction, length=linelengths, width=linewidth, color=_GetColorCode_(color), right=right, pad=pad)
        return ax
    
    def xscale(scale='log', base=10, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.set_xscale(scale, base, **kwargs)
        return ax
    
    def yscale(scale='log', base=10, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.set_yscale(scale, base, **kwargs)
        return ax
    
    def xlim(xmin=None, xmax=None, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.set_xlim(xmin, xmax, **kwargs)
        return ax
    
    def ylim(ymin=None, ymax=None, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.set_ylim(ymin, ymax, **kwargs)
        return ax
    
    def invert_xaxis(ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.invert_xaxis(**kwargs)
        return ax

    def invert_yaxis(ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.invert_yaxis(**kwargs)
        return ax
    
    def hidespines(ax=None, top=True, right=True, bottom=True, left=True):
        global _ax_
        if ax is None: ax = _ax_
        if top:
            ax.spines['top'].set_visible(False)
        if right:
            ax.spines['right'].set_visible(False)
        if bottom:
            ax.spines['bottom'].set_visible(False)
        if left:
            ax.spines['left'].set_visible(False)
        return ax
    
    def hideticks(ax=None, x=True, y=True):
        global _ax_
        if ax is None: ax = _ax_
        if x:
            ax.set_xticks([])
            ax.set_xticklabels([])
        if y:
            ax.set_yticks([])
            ax.set_yticklabels([])
        return ax
    
    def twinx(ax=None, label='', fontsize=None, color="fg", fonttype="default", **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("label")
        if fonttype not in ["default", "bold", "black", "zh", "ocr", "zh_bold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'default', 'bold', 'black', 'zh', 'special', 'zh_bold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        ax2 = ax.twinx()
        ax2.set_ylabel(label, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
        return ax2
    
    def twiny(ax=None, label='', fontsize=None, color="fg", fonttype="default", **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("label")
        if fonttype not in ["default", "bold", "black", "zh", "ocr", "zh_bold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'default', 'bold', 'black', 'zh', 'special', 'zh_bold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        ax2 = ax.twiny()
        ax2.set_xlabel(label, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
        return ax2

    def figsize(width=6.4, height=4.8, ax=None):
        global _ax_
        if ax is None: ax = _ax_
        ax.figure.set_size_inches(width, height)
        return ax

    def aspect(aspect='auto', adjustable=None, anchor=None, share=False, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.set_aspect(aspect, adjustable, anchor, share, **kwargs)
        return ax
    
    def axis(arg=None, ax=None):
        global _ax_
        if ax is None: ax = _ax_
        ax.axis(arg)
    
    def margin(ax=None, left=None, bottom=None, right=None, top=None, wspace=None, hspace=None):
        global _ax_
        if ax is None: ax = _ax_
        ax.figure.subplots_adjust(left=left, bottom=bottom, right=right, top=top, wspace=wspace, hspace=hspace)
        return ax
    
    # 3D Axes Functions
    def plot3d(x=0, y=0, z=0, ax=None, color="fg", linewidth=None, linestyle="-", **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m plot3d() got an unexpected Axes type: ax is not a 3D Axes instance."
        ax.plot(x, y, z, color=_GetColorCode_(color), linewidth=linewidth, linestyle=linestyle, **kwargs)
        return ax
    
    def scatter3d(x=0, y=0, z=0, ax=None, color="fg", marker="o", s=20, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m scatter3d() got an unexpected Axes type: ax is not a 3D Axes instance."
        ax.scatter(x, y, z, color=_GetColorCode_(color), marker=marker, s=s, **kwargs)
        return ax
    
    def bar3d(x=0, y=0, z=0, dx=0.5, dy=0.5, dz=0, ax=None, color="fg8", alpha=1, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m bar3d() got an unexpected Axes type: ax is not a 3D Axes instance."
        ax.bar3d(x, y, z, dx, dy, dz, color=_GetColorCode_(color), alpha=alpha, **kwargs)
        return ax
    
    def contour3d(x=0, y=0, z=0, ax=None, cmap=None, linewidth=None, zdir='z', offset=0, **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m contour3d() got an unexpected Axes type: ax is not a 3D Axes instance."
        ax.contour3D(x, y, z, color=cmaplist(cmap), linewidth=linewidth, zdir=zdir, offset=offset, **kwargs)
        return ax
    
    def contourf3d(x=0, y=0, z=0, ax=None, cmap=None, zdir='z', offset=0, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m contourf3d() got an unexpected Axes type: ax is not a 3D Axes instance."
        global CTF
        CTF = ax.contourf3D(x, y, z, cmap=cmaplist(cmap), zdir=zdir, offset=offset, **kwargs)
        _set_last_mappable(CTF)
        return CTF
        
    
    def plot_surface(x=0, y=0, z=0, ax=None,linewidth=None, rstride=1, cstride=1, cmap=None, antialiased=False, shade=False, **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m plot_surface() got an unexpected Axes type: ax is not a 3D Axes instance."
        global CTF
        if type(cmap) is None:
            CTF = ax.plot_surface(x, y, z, linewidth=linewidth, rstride=rstride, cstride=cstride, antialiased=False, shade=False, **kwargs)
        else:
            CTF = ax.plot_surface(x, y, z, cmap=cmaplist(cmap), linewidth=linewidth, rstride=rstride, cstride=cstride, antialiased=False, shade=False, **kwargs)
        return ax
    
    def quiver3d(x=0, y=0, z=0, u=0, v=0, w=0, ax=None, color="fg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m quiver3d() got an unexpected Axes type: ax is not a 3D Axes instance."
        ax.quiver(x, y, z, u, v, w, color=_GetColorCode_(color), **kwargs)
        return ax
    
    def voxels(voxels, facecolors='fg8', edgecolor='fg', alpha=1, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m voxels() got an unexpected Axes type: ax is not a 3D Axes instance."
        if type(facecolors) is str:
            ax.voxels(voxels, facecolors=facecolors, edgecolor=_GetColorCode_(edgecolor), alpha=alpha, **kwargs)
        elif type(facecolors) is list:
            facecolorlist = []
            for i in range(len(facecolors)):
                facecolorlist.append(_GetColorCode_(facecolors[i]))
            ax.voxels(voxels, facecolors=facecolorlist, edgecolor=_GetColorCode_(edgecolor), alpha=alpha, **kwargs)
        elif type(facecolors) is np.ndarray:
            ax.voxels(voxels, facecolors=facecolors, edgecolor=_GetColorCode_(edgecolor), alpha=alpha, **kwargs)
        else:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m voxels() got an unexpected keyword argument: facecolors='{facecolors}'. 'fg8' or list of color is valid.")
        return ax
    
    def zticks(ticks=None, labels='auto', ax=None, fontsize=None, color="fg", fonttype="default", linewidth=Linewidth().get(), linelengths=5, right=False, direction='out', which='both', pad=5, **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("ticklabel")
        if fonttype not in ["default", "bold", "black", "zh", "ocr", "zh_bold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'default', 'bold', 'black', 'zh', 'special', 'zh_bold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m zticks() got an unexpected Axes type: ax is not a 3D Axes instance."
        if ticks is None:
            ax.set_zticks([])
        else:
            ax.set_zticks(ticks)
        if labels is None:
            ax.set_zticklabels([])
        elif labels == 'auto':
            labels = [tick for tick in ticks]
            # transform ticks to str
            for i in range(len(labels)):
                labels[i] = str(labels[i])
            ax.set_zticklabels(labels, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
            ax.tick_params(axis='z', which=which, direction=direction, length=linelengths, width=linewidth, color=_GetColorCode_(color), right=right, pad=pad)
        else:
            ax.set_zticklabels(labels, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
            ax.tick_params(axis='z', which=which, direction=direction, length=linelengths, width=linewidth, color=_GetColorCode_(color), right=right, pad=pad)
        return ax
    
    def zscale(scale='log', base=10, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m zscale() got an unexpected Axes type: ax is not a 3D Axes instance."
        ax.set_zscale(scale, base, **kwargs)
        return ax
    
    def zlim(zmin=None, zmax=None, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m zlim() got an unexpected Axes type: ax is not a 3D Axes instance."
        ax.set_zlim(zmin, zmax, **kwargs)
        return ax
    
    def zlabel(s='', ax=None, fontsize=None, color="fg", fonttype="default", right=False, **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("label")
        if fonttype not in ["default", "bold", "black", "zh", "ocr", "zh_bold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'default', 'bold', 'black', 'zh', 'special', 'zh_bold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m zlabel() got an unexpected Axes type: ax is not a 3D Axes instance."
        ax.set_zlabel(s, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
        if right:
            ax.tick_params(axis='z', labelright=True)
        return ax
    

    # set 3d pane color
    def set_pane_color(color=False, grid=False, ax=None):
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m set_pane_color() got an unexpected Axes type: ax is not a 3D Axes instance."
        if color==False:
            ax.xaxis.pane.fill = False
            ax.yaxis.pane.fill = False
            ax.zaxis.pane.fill = False
        else:
            ax.xaxis.pane.set_facecolor(_GetColorCode_(color))
            ax.yaxis.pane.set_facecolor(_GetColorCode_(color))
            ax.zaxis.pane.set_facecolor(_GetColorCode_(color))
        if grid==False:
            ax.xaxis.pane.set_edgecolor('w')
            ax.yaxis.pane.set_edgecolor('w')
            ax.zaxis.pane.set_edgecolor('w')
        return ax
    
    
    
    
    # windrose config fxn
    def rbar(wd, ws, normed=True, opening=0.8, edgecolor='fg', linewidth=Linewidth().get(), ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if not isinstance(ax, WindroseAxes):
            print("\033[43m[pymeili Warning]\033[0m rbar() got an unexpected Axes type: ax is not a WindroseAxes instance.")
        ax.bar(wd, ws, normed=normed, opening=opening, edgecolor=_GetColorCode_(edgecolor), linewidth=linewidth, **kwargs)
        return ax
    
    def rbox(wd, ws, bins=5, normed=True, edgecolor='fg', linewidth=Linewidth().get(), ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if not isinstance(ax, WindroseAxes):
            print("\033[43m[pymeili Warning]\033[0m rbox() got an unexpected Axes type: ax is not a WindroseAxes instance.")
        ax.box(wd, ws, bins=bins, normed=normed, edgecolor=_GetColorCode_(edgecolor), linewidth=linewidth, **kwargs)
        return ax
    
    def rcontour(wd, ws, bins=5, ax=None, color="fg", colors=None, linewidth=None, **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        if not isinstance(ax, WindroseAxes):
            print("\033[43m[pymeili Warning]\033[0m rcontour() got an unexpected Axes type: ax is not a WindroseAxes instance.")
        if colors==None:
                colors = _GetColorCode_(color)
        else:
            colors = _GetColorCode_(colors)
        
        global CT
        ax.contour(wd, ws, bins=bins, colors=colors, linewidth=linewidth, **kwargs)
        return ax
        
    
    def rcontourf(wd, ws, bins=5, ax=None, cmap=None, colors=None, **kwargs):
        global _ax_, CTF
        if ax is None: ax = _ax_
        if not isinstance(ax, WindroseAxes):
            print("\033[43m[pymeili Warning]\033[0m rcontourf() got an unexpected Axes type: ax is not a WindroseAxes instance.")
        if colors is None:
            if cmap is None:
                cmap = _GetColorCode_("fg") # 什麼都沒說，就用fg
            else:
                cmap = cmaplist(cmap) # cmap可為字串(關鍵字)或是list(自定義)，colors為None，則使用cmap
        else:
            if cmap is None:
                colors = _GetColorCode_(colors) # cmap為None，colors不為None，則使用colors
            else: # 同時指定cmap和colors，則報錯
                raise TypeError(f"\033[41m[pymeili Error]\033[0m rcontourf() got an unexpected keyword argument: 'cmap' and 'colors' cannot be specified at the same time.")
        
        
        CTF = ax.contourf(wd, ws, bins=bins, cmap=cmap, colors=colors, **kwargs)
        
        _set_last_mappable(CTF)
        return CTF
        
            
    def set_rlabel_position(position='auto', ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if not isinstance(ax, WindroseAxes):
            print("\033[43m[pymeili Warning]\033[0m set_rlabel_position() got an unexpected Axes type: ax is not a WindroseAxes instance.")
        ax.set_rlabel_position(position, **kwargs)
        return ax
    
    def set_theta_zero_location(location='N', ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if not isinstance(ax, WindroseAxes):
            print("\033[43m[pymeili Warning]\033[0m set_theta_zero_location() got an unexpected Axes type: ax is not a WindroseAxes instance.")
        ax.set_theta_zero_location(location, **kwargs)
        return ax
    
    def set_theta_direction(direction='clockwise', ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if not isinstance(ax, WindroseAxes):
            print("\033[43m[pymeili Warning]\033[0m set_theta_direction() got an unexpected Axes type: ax is not a WindroseAxes instance.")
        ax.set_theta_direction(direction, **kwargs)
        return ax
    
    def rgrids(ax=None, linewidth=Linewidth().get(), linestyle=':', xcolor='fg', ycolor="fg8", xgrid=True, ygrid=True, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if not isinstance(ax, WindroseAxes):
            print("\033[43m[pymeili Warning]\033[0m rgrids() got an unexpected Axes type: ax is not a WindroseAxes instance.")
        ax.xaxis.grid(xgrid, linestyle='-', linewidth=linewidth, color=_GetColorCode_(xcolor), **kwargs)
        ax.yaxis.grid(ygrid, linestyle=linestyle, linewidth=linewidth, color=_GetColorCode_(ycolor), **kwargs)
        return ax
    
    def rspines(ax=None, color='fg', linewidth=Linewidth().get(), **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if not isinstance(ax, WindroseAxes):
            print("\033[43m[pymeili Warning]\033[0m rspines() got an unexpected Axes type: ax is not a WindroseAxes instance.")
        ax.spines['polar'].set_color(_GetColorCode_(color))
        ax.spines['polar'].set_linewidth(linewidth)
    
    def rticklabels(label=[], ax=None, fontsize=None, color="fg", fonttype="default", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if fontsize is None: fontsize=_GetFontSize_("ticklabel")
        if fonttype not in ["default", "bold", "black", "zh", "ocr", "zh_bold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'default', 'bold', 'black', 'zh', 'special', 'zh_bold' or 'kl' is valid.")
        ax.set_xticklabels(label, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
        return ax
    # Basemap config fxn
    def basemap(ax=None, projection='cyl', resolution='c', **kwargs):
        ax = Basemap(ax=ax, projection=projection, resolution=resolution, **kwargs)
        return ax
    
    def drawcoastlines(ax=None, linewidth=Linewidth().get()/2, color="fg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != Basemap: 
            print("\033[43m[pymeili Warning]\033[0m drawcoastlines() got an unexpected Axes type: ax is not a Basemap instance.")
        #if type(ax) == cartopy.mpl.geoaxes.GeoAxesSubplot:
        #    print("\033[43m[pymeili Warning]\033[0m Mismatched function: drawcoastlines() is not supported in cartopy. Use coastlines() instead.")
        ax.drawcoastlines(linewidth=linewidth, color=_GetColorCode_(color), **kwargs)
        return ax
    
    def drawcountries(ax=None, linewidth=Linewidth().get()/2, color="fg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != Basemap: 
            print("\033[43m[pymeili Warning]\033[0m drawcountries() got an unexpected Axes type: ax is not a Basemap instance.")
        #if type(ax) == cartopy.mpl.geoaxes.GeoAxesSubplot:
        #    print("\033[43m[pymeili Warning]\033[0m Mismatched function: drawcountries() is not supported in cartopy. Use countries() instead.")
        ax.drawcountries(linewidth=linewidth, color=_GetColorCode_(color), **kwargs)
        return ax

    def drawstates(ax=None, linewidth=Linewidth().get()/2, color="fg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != Basemap: 
            print("\033[43m[pymeili Warning]\033[0m drawstates() got an unexpected Axes type: ax is not a Basemap instance.")
        ax.drawstates(linewidth=linewidth, color=_GetColorCode_(color), **kwargs)
        return ax
    
    def drawrivers(ax=None, linewidth=Linewidth().get()/2, color="bg2", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != Basemap: 
            print("\033[43m[pymeili Warning]\033[0m drawrivers() got an unexpected Axes type: ax is not a Basemap instance.")
        ax.drawrivers(linewidth=linewidth, color=_GetColorCode_(color), **kwargs)
        return ax
    
    def drawlsmask(ax=None, land_color='rfg', ocean_color='bg', lakes=True, resolution='c', grid=5, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != Basemap: 
            print("\033[43m[pymeili Warning]\033[0m drawlsmask() got an unexpected Axes type: ax is not a Basemap instance.")
        _ax_.drawlsmask(land_color=_GetColorCode_(land_color), ocean_color=_GetColorCode_(ocean_color), lakes=lakes, resolution=resolution, grid=grid, **kwargs)
        return _ax_
    
    def fillcontinents(ax=None, color="fg", lake_color="bg2", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != Basemap: 
            print("\033[43m[pymeili Warning]\033[0m fillcontinents() got an unexpected Axes type: ax is not a Basemap instance.")
        #if type(ax) == cartopy.mpl.geoaxes.GeoAxesSubplot:
        #    print("\033[43m[pymeili Warning]\033[0m Mismatched function: fillcontinents() is not supported in cartopy. Use add_fillcontinents() instead.")
        _ax_.fillcontinents(color=_GetColorCode_(color), lake_color=_GetColorCode_(lake_color), **kwargs)
        return _ax_
    
    def drawmapboundary(ax=None, color="fg", linewidth=Linewidth().get()/2, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != Basemap: 
            print("\033[43m[pymeili Warning]\033[0m drawmapboundary() got an unexpected Axes type: ax is not a Basemap instance.")
        #if type(ax) == cartopy.mpl.geoaxes.GeoAxesSubplot:
        #    print("\033[43m[pymeili Warning]\033[0m Mismatched function: drawmapboundary() is not supported in cartopy. Use add_mapboundary() instead.")
        AXB = _ax_.drawmapboundary(color=_GetColorCode_(color), linewidth=linewidth, **kwargs)
        AXB.set_clip_on(False)
        return _ax_
    
    def readshapefile(shapefile=f'{MOTHER_PATH} / "pymeili_resource" /shapefile.shp', ax=None, name='states', drawbounds=True, linewidth=Linewidth().get()/2, color="fg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != Basemap: 
            print("\033[43m[pymeili Warning]\033[0m readshapefile() got an unexpected Axes type: ax is not a Basemap instance.")
        #if type(ax) == cartopy.mpl.geoaxes.GeoAxesSubplot:
        #    print("\033[43m[pymeili Warning]\033[0m Mismatched function: readshapefile() is not supported in cartopy. Use add_shapefile() instead.")
        _ax_.readshapefile(shapefile, name=name, drawbounds=drawbounds, linewidth=linewidth, color=_GetColorCode_(color), **kwargs)
        if not config.get("General", "MuteInfo", bool):
            print(f"\033[44m[pymeili Info]\033[0m Shapefile: {shapefile} is loaded.")
        return _ax_

    def drawmeridians(meridians, ax=None, linewidth=Linewidth().get()/2, color="fg", labels=[0,0,0,1], labelsize=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != Basemap: 
            print("\033[43m[pymeili Warning]\033[0m drawmeridians() got an unexpected Axes type: ax is not a Basemap instance.")
        if labelsize is None: labelsize=_GetFontSize_("ticklabel")
        _meridians_ = _ax_.drawmeridians(meridians, linewidth=linewidth, color=_GetColorCode_(color), labels=labels, fontsize=labelsize, **kwargs)
        # set label fonttype
        fonttype = "default"
        for label in _meridians_:
            try:
                _meridians_[label][1][0].set_fontproperties(fm.FontProperties(fname=FontFamily().get(fonttype), size=labelsize))
            except IndexError:
                pass # no label available
        return _ax_
    
    def drawparallels(parallels, ax=None, linewidth=Linewidth().get()/2, color="fg", labels=[1,0,0,0], labelsize=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != Basemap: 
            print("\033[43m[pymeili Warning]\033[0m drawparallels() got an unexpected Axes type: ax is not a Basemap instance.")
        if labelsize is None: labelsize=_GetFontSize_("ticklabel")
        _parallels_ = _ax_.drawparallels(parallels, linewidth=linewidth, color=_GetColorCode_(color), labels=labels, fontsize=labelsize, **kwargs)
        fonttype = "default"
        for label in _parallels_:
            try:
                _parallels_[label][1][0].set_fontproperties(fm.FontProperties(fname=FontFamily().get(fonttype), size=labelsize))
            except IndexError:
                pass
        return _ax_

    def shaderelief(ax=None, scale=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != Basemap: 
            print("\033[43m[pymeili Warning]\033[0m shaderelief() got an unexpected Axes type: ax is not a Basemap instance.")
        _ax_.shaderelief(scale=scale, **kwargs)
        return _ax_

    # Cartopy config fxn
    def coastlines(ax=None, linewidth=Linewidth().get()/2, color="fg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m coastlines() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.coastlines(linewidth=linewidth, color=_GetColorCode_(color), **kwargs)
        return ax
    
    def countries(ax=None, linewidth=Linewidth().get()/2, color="fg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m countries() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        if type(ax) == Basemap:
            print("\033[43m[pymeili Warning]\033[0m Mismatched function: countries() is not supported in Basemap. Use drawcountries() instead.")
        ax.add_feature(cfeature.BORDERS, linewidth=linewidth, color=_GetColorCode_(color), **kwargs)
        return ax
    
    def stock_img(ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m stock_img() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.stock_img(**kwargs)
        return ax
    
    def gridlines(ax=None, linewidth=Linewidth().get()/2, color="fg", draw_labels=True, dms=False, x_inline=False, y_inline=False, labelsize=None, linestyle='--', **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m gridlines() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        if type(ax) == Basemap:
            print("\033[43m[pymeili Warning]\033[0m Mismatched function: gridlines() is not supported in Basemap. Use drawparallels() and drawmeridians() instead.")
        gl = ax.gridlines(linewidth=linewidth, color=_GetColorCode_(color), draw_labels=draw_labels, dms=dms, x_inline=x_inline, y_inline=y_inline, linestyle=linestyle, **kwargs)
        # set fontsize, fontcolor, fonttype
        if labelsize is None: labelsize=_GetFontSize_("ticklabel")
        gl.xlabel_style = {'color': _GetColorCode_(color), 'fontsize': labelsize}
        gl.ylabel_style = {'color': _GetColorCode_(color), 'fontsize': labelsize}
        # set fonttype
        fonttype = "default"
        gl.xlabel_style['fontproperties'] = fm.FontProperties(fname=FontFamily().get(fonttype), size=labelsize)
        gl.ylabel_style['fontproperties'] = fm.FontProperties(fname=FontFamily().get(fonttype), size=labelsize)
        # Turn off right and top tick marks
        gl.right_labels = False
        gl.top_labels = False
        return ax
    
    #! ERROR WHEN USER DOES NOT SET XLIMITS AND Y LIMITS
    def add_mapboundary(ax=None, linewidth=Linewidth().get(), color="fg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m add_mapboundary() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        if type(ax) == Basemap:
            print("\033[43m[pymeili Warning]\033[0m Mismatched function: add_mapboundary() is not supported in Basemap. Use drawmapboundary() instead.")
        _ax_.add_patch(plt.Rectangle((ax.get_xlim()[0], ax.get_ylim()[0]),
                           ax.get_xlim()[1] - ax.get_xlim()[0],
                           ax.get_ylim()[1] - ax.get_ylim()[0],
                           fill=None, edgecolor=_GetColorCode_(color), linewidth=linewidth, **kwargs))
    
    def add_fillcontinents(ax=None, color="fg", lake_color="bg2", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m add_fillcontinents() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        if type(ax) == Basemap:
            print("\033[43m[pymeili Warning]\033[0m Mismatched function: add_fillcontinents() is not supported in Basemap. Use fillcontinents() instead.") 
        ax.add_feature(cfeature.LAND, color=_GetColorCode_(color), **kwargs)
        ax.add_feature(cfeature.LAKES, color=_GetColorCode_(lake_color), **kwargs)
        return ax
    
    def add_filloceans(ax=None, color="bg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m add_filloceans() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.add_feature(cfeature.OCEAN, color=_GetColorCode_(color), **kwargs)
        return ax

    def add_feature(feature, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m add_feature() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.add_feature(feature, **kwargs)
        return ax
    
    def add_geometries(geoms, crs, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m add_geometries() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.add_geometries(geoms, crs, **kwargs)
        return ax
    
    def add_image(factory, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m add_image() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.add_image(factory, **kwargs)
        return ax
    
    def add_raster(raster, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m add_raster() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.add_raster(raster, **kwargs)
        return ax
    
    def add_wmts(wmts, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m add_wmts() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.add_wmts(wmts, **kwargs)
        return ax
    
    def add_wms(wms, layers, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m add_wms() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.add_wms(wms, layers, **kwargs)
        return ax
    
    def autoscale_view(ax=None, tight=None, scalex=True, scaley=True):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m autoscale_view() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.autoscale_view(tight=tight, scalex=scalex, scaley=scaley)
        return ax
    
    def background_img(name='ne_shaded', resolution='low', extent=None, cache=False, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m background_img() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.background_img(name=name, resolution=resolution, extent=extent, cache=cache, **kwargs)
        return ax
    
    def set_extent(extent=None, crs=None, ax=None):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m set_extent() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.set_extent(extent, crs=crs)
        return ax
    
    def set_global(ax=None):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m set_global() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.set_global()
        return ax
    
    def add_shapefile(filename, ax=None, crs=ccrs.PlateCarree(), edgecolor='fg', facecolor=None, linewidth=Linewidth().get()/2, **kwargs):
        from cartopy.io.shapereader import Reader
        from cartopy.feature import ShapelyFeature
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m add_shapefile() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        # make sure the file exists
        if not os.path.exists(filename): raise FileNotFoundError(f"\033[41m[pymeili Error]\033[0m Shapefile: {filename} not found.")
        if facecolor is None: facecolor = "#00000000"
        else: facecolor = _GetColorCode_(facecolor)
        SF = ShapelyFeature(Reader(filename).geometries(), crs=crs, edgecolor=_GetColorCode_(edgecolor), facecolor=facecolor, linewidth=linewidth, **kwargs)
        print(f"\033[44m[pymeili Info]\033[0m Shapefile: {filename} is loaded.")
        _ax_.add_feature(SF)
        return _ax_
    
    # Image config fxn
    def imread(filename, **kwargs):
        return plt.imread(filename, **kwargs)
    
    def imshow(X, ax=None, axis='off', cmap=None, colors=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.axis(axis)


        if cmap is not None and colors is not None:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m imshow() got conflicting arguments: cannot use both cmap and colors.")
        elif colors is not None:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m colors is not supported in imshow(), use cmap instead.")

        if cmap is None:
            im = ax.imshow(X, **kwargs)
        else:
            im = ax.imshow(X, cmap=cmaplist(cmap), **kwargs)

        _set_last_mappable(im)
        return im

    def pcolor(x, y, z, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        return ax.pcolor(x, y, z, **kwargs)

    def pcolormesh(x, y, z, ax=None, cmap=None, colors=None,
                edgecolor=None, linewidth=0.0, **kwargs):
        """
        Extended pcolormesh with support for cmap/colormap list/colors and edgecolors.

        Parameters
        ----------
        x, y, z : array-like
            Grid coordinates and values.
        ax : matplotlib Axes, optional
            Target axes. If None, use global _ax_.
        cmap : str or list, optional
            - str: passed to cmaplist(str)
            - list: custom colormap
        colors : str or list, optional
            - str: single color via _GetColorCode_
            - list: direct color sequence
            Cannot be used together with cmap.
        edgecolor : str or list, optional
            Edge color(s) of mesh cells.
        linewidth : float, optional
            Line width for mesh edges.
        """
        global _ax_
        if ax is None:
            ax = _ax_

        # edgecolor 預處理
        if edgecolor is not None:
            if isinstance(edgecolor, str):
                edgecolor = _GetColorCode_(edgecolor)

        # 判斷輸入合法性
        if cmap is not None and colors is not None:
            raise TypeError(
                f"\033[41m[pymeili Error]\033[0m pcolormesh() got an unexpected keyword argument: "
                f"'cmap' and 'colors' cannot be specified at the same time."
            )

        # case 1: 使用 cmap
        if cmap is not None:
            pc = ax.pcolormesh(x, y, z,
                            cmap=cmaplist(cmap),
                            edgecolors=edgecolor,
                            linewidth=linewidth,
                            **kwargs)

        # case 2: 使用 colors
        elif colors is not None:
            if isinstance(colors, str):
                colors = _GetColorCode_(colors)
            pc = ax.pcolormesh(x, y, z,
                            colors=colors,
                            edgecolors=edgecolor,
                            linewidth=linewidth,
                            **kwargs)

        # case 3: 默認顏色 (單色)
        else:
            pc = ax.pcolormesh(x, y, z,
                            edgecolors=edgecolor,
                            linewidth=linewidth,
                            **kwargs)

        
        _set_last_mappable(pc)
        
        return pc


    def hexbin(x, y, C=None, ax=None, gridsize=100,
            cmap=None, colors=None,
            edgecolor=None, linewidth=0.0,
            mincnt=None, reduce_C_function=None, **kwargs):
        """
        Extended hexbin with support for cmap/colors and edgecolors.

        Parameters
        ----------
        x, y : array-like
            Input coordinates.
        C : array-like, optional
            Values at each (x, y). If None, hexbin counts number of points.
        ax : matplotlib Axes, optional
            Target axes. If None, use global _ax_.
        gridsize : int or tuple, default=100
            Number of hexagons in x-direction, or (nx, ny).
        cmap : str or list, optional
            - str: passed to cmaplist(str)
            - list: custom colormap
        colors : str or list, optional
            - str: single color via _GetColorCode_
            - list: direct color sequence
            Cannot be used together with cmap.
        edgecolor : str or list, optional
            Edge color(s) of hexagons.
        linewidth : float, optional
            Line width for hexagon edges.
        mincnt : int, optional
            If not None, only display hexagons with at least mincnt points.
        reduce_C_function : callable, optional
            Function of one variable, reduces C within bins (e.g. np.mean).
        kwargs : dict
            Additional arguments passed to ax.hexbin().

        Returns
        -------
        hb : PolyCollection
            The Hexbin mappable object.
        """
        global _ax_
        if ax is None:
            ax = _ax_

        # edgecolor 預處理
        if edgecolor is not None:
            if isinstance(edgecolor, str):
                edgecolor = _GetColorCode_(edgecolor)

        # 判斷輸入合法性
        if cmap is not None and colors is not None:
            raise TypeError(
                f"\033[41m[pymeili Error]\033[0m hexbin() got an unexpected keyword argument: "
                f"'cmap' and 'colors' cannot be specified at the same time."
            )

        # case 1: 使用 cmap
        if cmap is not None:
            hb = ax.hexbin(x, y, C,
                        gridsize=gridsize,
                        cmap=cmaplist(cmap),
                        edgecolors=edgecolor,
                        linewidths=linewidth,
                        mincnt=mincnt,
                        reduce_C_function=reduce_C_function,
                        **kwargs)

        # case 2: 使用 colors
        elif colors is not None:
            if isinstance(colors, str):
                colors = _GetColorCode_(colors)
            hb = ax.hexbin(x, y, C,
                        gridsize=gridsize,
                        facecolors=colors,
                        edgecolors=edgecolor,
                        linewidths=linewidth,
                        mincnt=mincnt,
                        reduce_C_function=reduce_C_function,
                        **kwargs)

        # case 3: 默認（matplotlib 自動顏色）
        else:
            hb = ax.hexbin(x, y, C,
                        gridsize=gridsize,
                        edgecolors=edgecolor,
                        linewidths=linewidth,
                        mincnt=mincnt,
                        reduce_C_function=reduce_C_function,
                        **kwargs)

        _set_last_mappable(hb)

        return hb

    
    
    



    # Advanced Addtional Function for plot
    from matplotlib.widgets import Button
    from mpl_toolkits.axes_grid1.inset_locator import InsetPosition
    
    def button(ax=None, pos=(0.5,-0.12) ,width=0.4, height=0.1, label='', color="bg", hovercolor="fg8", fontsize=None, fonttype="default", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if fontsize is None: fontsize=_GetFontSize_("text")
        if fonttype not in ["default", "bold", "black", "zh", "ocr", "zh_bold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'default', 'bold', 'black', 'zh', 'special', 'zh_bold' or 'kl' is valid.")
        
        # Create a button axes
        ax_btn = plt.axes([0, 0, 1, 1])
        # Create a button
        ip = InsetPosition(ax, [pos[0], pos[1], width, height])
        ax_btn.set_axes_locator(ip)
        axbutton = Button(ax_btn, label, color=_GetColorCode_(color), hovercolor=_GetColorCode_(hovercolor), **kwargs)
        axbutton.label.set_fontproperties(fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize))
        return axbutton


    # Miscellaneous Process
    def show(**kwargs):
        plt.show(**kwargs)
        
    def pause(interval):
        plt.pause(interval)
        
    def close():
        plt.close()
        
        
    def savefig(filename, dpi=300, transparent=False, bbox_inches='tight', pad_inches=0.1, record=True, **kwargs):
        plt.savefig(filename, dpi=dpi, transparent=transparent, bbox_inches=bbox_inches, pad_inches=pad_inches, **kwargs)
        if record:
            save_name = filename
            save_time = getTableTime()
            global production_name, production_time
            production_name.append(save_name)
            production_time.append(save_time)

        
    def clf():
        plt.clf()
        
    def cla():
        plt.cla()

    def gcf():
        global _fig_
        if _fig_ is None:
            _fig_ = plt.figure()
        return _fig_
    
    def gca(ax=None):
        global _ax_
        if ax is None: ax = _ax_
        return ax

    def tight_layout(ax=None, pad=1.08, h_pad=None, w_pad=None, rect=None,
                    fallback_adjust=True, left=0.05, right=0.95, top=0.95, bottom=0.05):
        """
        智能 tight_layout：若普通 Axes → 使用 tight_layout
        若特殊 Axes（GeoAxes / Basemap） → fallback 使用 subplots_adjust
        """
        global _ax_
        if ax is None:
            ax = _ax_

        fig = getattr(ax, "figure", None)
        if fig is None:
            raise ValueError("[pymeili Error] Axes has no associated figure.")

        try:
            # 嘗試 tight_layout
            fig.tight_layout(pad=pad, h_pad=h_pad, w_pad=w_pad, rect=rect)
        except Exception as e:
            # 若失敗且允許 fallback
            if fallback_adjust:
                print("[pymeili Warning] tight_layout failed, fallback to subplots_adjust.")
                fig.subplots_adjust(left=left, right=right, top=top, bottom=bottom,
                                    hspace=h_pad if h_pad is not None else 0.2,
                                    wspace=w_pad if w_pad is not None else 0.2)
            else:
                # 不允許 fallback → 繼續丟錯
                raise e
        return ax


    def ion():
        plt.ion()
        
    def ioff():
        plt.ioff()
        
    def isinteractive():
        plt.isinteractive()
        
    def record(title=None):
        table = printTable(production_name, production_time, title)
        return table

    # POST-PROCESSING
    def add_watermark(filepath, text="pymeili", fontsize=20, color="fg", fonttype="default", margin=10):
        if filepath is None: raise FileNotFoundError(f"\033[41m[pymeili Error]\033[0m add_watermark() got an unassigned keyword argument: filepath='{filepath}'.")
        if fontsize is None: fontsize=_GetFontSize_("text")
        if fonttype not in ["default", "bold", "black", "zh", "ocr", "zh_bold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'default', 'bold', 'black', 'zh', 'special', 'zh_bold' or 'kl' is valid.")
        from PIL import Image, ImageDraw, ImageFont
        from pathlib import Path
        # add watermark at the bottom right of the image
        img = Image.open(filepath)
        draw = ImageDraw.Draw(img)
        fontpath = FontFamily().get(fonttype)
        # 將所有fontpath中的' '換成'_'
        if fonttype == "zh":
            fontpath = str(fontpath).replace(' ', '_')
        font = ImageFont.truetype(str(Path(fontpath)), fontsize)
        textwidth, textheight = draw.textsize(text, font)
        width, height = img.size
        # calculate position
        margin = margin
        x = width - textwidth - margin
        y = height - textheight - margin
        # draw watermark
        draw.text((x, y), text, font=font, fill=_GetColorCode_(color))
        # save the image
        img.save(filepath)
        return img
    
    def convertgif(inputfolder, outputfolder, filename='output.gif', format='png', duration=0.5, loop=0, downresorate=1):
        if not os.path.exists(inputfolder): raise FileNotFoundError(f"\033[41m[pymeili Error]\033[0m convertgif() got an unexpected keyword argument: inputfolder='{inputfolder}' not found.")
        if not os.path.exists(outputfolder): os.makedirs(outputfolder)
        if filename.split('.')[-1] != 'gif': raise ValueError(f"\033[41m[pymeili Error]\033[0m convertgif() got an unexpected keyword argument: filename='{filename}'. The output filename should be a gif file.")
        if format not in ['png', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff', 'gif']: raise TypeError(f"\033[41m[pymeili Error]\033[0m convertgif() got an unexpected keyword argument: format='{format}'. 'png', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff' or 'gif' is valid.")
        if duration <= 0: raise ValueError(f"\033[41m[pymeili Error]\033[0m convertgif() got an unexpected keyword argument: duration='{duration}'. duration should be greater than 0.")
        if loop < 0: raise ValueError(f"\033[41m[pymeili Error]\033[0m convertgif() got an unexpected keyword argument: loop='{loop}'. loop should be greater than or equal to 0.")
        if downresorate <= 0: raise ValueError(f"\033[41m[pymeili Error]\033[0m convertgif() got an unexpected keyword argument: downresorate='{downresorate}'. downresorate should be greater than 0.")
        # get all images in the inputfolder
        images = glob.glob(f"{inputfolder}/*.{format}")
        # sort the images
        images.sort()
        # read images
        images = [imageio.v2.imread(image) for image in images]
        # downresorate
        images = [image[::downresorate, ::downresorate] for image in images]
        # save as gif
        imageio.mimsave(f"{outputfolder}/{filename}", images, duration=duration, loop=loop)
        return images

#except Exception as e:
#    print("\033[41m[pymeili Exception]\033[0m ", e)
#    exit()