import os
import sys

base_path = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(base_path, '..', 'build')))

import lvgl as lv


import wx
import threading
import win_precise_time as wpt
import ctypes
import math
import time
import os


from ctypes.wintypes import LONG, HWND, INT, HDC, HGDIOBJ, BOOL, DWORD


UBYTE = ctypes.c_ubyte
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
ULW_ALPHA = 0x00000002
AC_SRC_OVER = 0x00000000
AC_SRC_ALPHA = 0x00000001
WS_POPUP = 0x80000000


class POINT(ctypes.Structure):
    _fields_ = [
        ('x', LONG),
        ('y', LONG)
    ]


class SIZE(ctypes.Structure):
    _fields_ = [
        ('cx', LONG),
        ('cy', LONG)
    ]


class BLENDFUNCTION(ctypes.Structure):
    _fields_ = [
        ('BlendOp', UBYTE),
        ('BlendFlags', UBYTE),
        ('SourceConstantAlpha', UBYTE),
        ('AlphaFormat', UBYTE)
    ]


user32 = ctypes.windll.User32
gdi32 = ctypes.windll.Gdi32

# LONG GetWindowLongW(
#   HWND hWnd,
#   int  nIndex
# )

GetWindowLongW = user32.GetWindowLongW
GetWindowLongW.restype = LONG

# LONG SetWindowLongW(
#   HWND hWnd,
#   int  nIndex,
#   LONG dwNewLong
# );
SetWindowLongW = user32.SetWindowLongW
SetWindowLongW.restype = LONG

# HDC GetDC(
#   HWND hWnd
# );
GetDC = user32.GetDC
GetDC.restype = HDC

# HWND GetDesktopWindow();
GetDesktopWindow = user32.GetDesktopWindow
GetDesktopWindow.restype = HWND

# HDC CreateCompatibleDC(
#   HDC hdc
# );
CreateCompatibleDC = gdi32.CreateCompatibleDC
CreateCompatibleDC.restype = HDC

# HGDIOBJ SelectObject(
#   HDC     hdc,
#   HGDIOBJ h
# );
SelectObject = gdi32.SelectObject
SelectObject.restype = HGDIOBJ

# BOOL UpdateLayeredWindow(
#   HWND          hWnd,
#   HDC           hdcDst,
#   POINT         *pptDst,
#   SIZE          *psize,
#   HDC           hdcSrc,
#   POINT         *pptSrc,
#   COLORREF      crKey,
#   BLENDFUNCTION *pblend,
#   DWORD         dwFlags
# );
UpdateLayeredWindow = user32.UpdateLayeredWindow
UpdateLayeredWindow.restype = BOOL


DeleteDC = gdi32.DeleteDC
DeleteDC.restype = BOOL


ReleaseDC = user32.ReleaseDC
ReleaseDC.restype = BOOL


COLORREF = DWORD


def RGB(r, g, b):
    return COLORREF(r | (g << 8) | (b << 16))


class Frame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(
            self,
            None,
            -1,
            style=(
                # wx.FRAME_SHAPED |
                wx.NO_BORDER |
                wx.FRAME_NO_TASKBAR |
                wx.STAY_ON_TOP
            )
        )
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.on_erase_background)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.SetClientSize((800, 600))

        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_mouse_leave)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)


        self.key = 0
        self.mouse_point = lv.point_t()
        self.mouse_point.x = 0
        self.mouse_point.y = 0
        self.state = lv.INDEV_STATE_RELEASED
        self.key_state = lv.INDEV_STATE_RELEASED
        self.count = 0
        self.start = time.time()
        self.Show()
        self.pptDst = POINT(*self.GetPosition())
        self.psize = SIZE(*self.GetClientSize())

        self.pptSrc = POINT(0, 0)
        self.crKey = RGB(0, 0, 0)
        self.hndl = self.GetHandle()

    def on_erase_background(self, event):
        dc = wx.ClientDC(self)
        gcdc = wx.GCDC(dc)
        gcdc.SetBackground(wx.TRANSPARENT_BRUSH)

        gcdc.Destroy()
        del gcdc

        dc.Destroy()
        del dc

        event.Skip()

    def OnPaint(self, evt):
        pass

    def draw_alpha(self, bmp):
        style = GetWindowLongW(HWND(self.hndl), INT(GWL_EXSTYLE))
        SetWindowLongW(HWND(self.hndl), INT(GWL_EXSTYLE), LONG(style | WS_EX_LAYERED))

        hdcDst = GetDC(HWND(self.hndl))
        hdcMem = CreateCompatibleDC(HDC(hdcDst))

        pblend = BLENDFUNCTION(AC_SRC_OVER, 0, 255, AC_SRC_ALPHA)
        old_bmp = SelectObject(HDC(hdcMem), HGDIOBJ(bmp.GetHandle()))
        UpdateLayeredWindow(
            HWND(self.hndl),
            HDC(hdcDst),
            ctypes.byref(self.pptDst),
            ctypes.byref(self.psize),
            HDC(hdcMem),
            ctypes.byref(self.pptSrc),
            self.crKey,
            ctypes.byref(pblend),
            DWORD(ULW_ALPHA)
        )
        SelectObject(HDC(hdcMem), HWND(old_bmp))

        ReleaseDC(None, HDC(hdcMem))
        DeleteDC(HDC(hdcMem))

        ReleaseDC(None, HDC(hdcDst))
        DeleteDC(HDC(hdcDst))

    def on_key_down(self, evt):
        key = evt.GetUnicodeKey()
        if key == wx.WXK_NONE:
            key = evt.GetKeyCode()
            mapping = {
                wx.WXK_ESCAPE: wx.WXK_ESCAPE,
                wx.WXK_DELETE: wx.WXK_DELETE,
                wx.WXK_NUMPAD_DELETE: wx.WXK_DELETE,
                wx.WXK_BACK: wx.WXK_BACK,
                wx.WXK_NUMPAD_DOWN: 18,
                wx.WXK_DOWN: 18,
                wx.WXK_NUMPAD_LEFT: 20,
                wx.WXK_LEFT: 20,
                wx.WXK_NUMPAD_RIGHT: 19,
                wx.WXK_RIGHT: 19,
                wx.WXK_NUMPAD_UP: 17,
                wx.WXK_UP: 17,
                wx.WXK_NUMPAD_ENTER: 10,
                wx.WXK_RETURN: 10,
                wx.WXK_NUMPAD_HOME: 2,
                wx.WXK_HOME: 2,
                wx.WXK_NUMPAD_END: 3,
                wx.WXK_END: 3,
                wx.WXK_MEDIA_NEXT_TRACK: 9,
                wx.WXK_TAB: 9,
                wx.WXK_NUMPAD_TAB: 9,
                wx.WXK_PAGEUP: 9,
                wx.WXK_MEDIA_PREV_TRACK: 11,
                wx.WXK_PAGEDOWN: 11,
                wx.WXK_NUMPAD0: ord('0'),
                wx.WXK_NUMPAD1: ord('1'),
                wx.WXK_NUMPAD2: ord('2'),
                wx.WXK_NUMPAD3: ord('3'),
                wx.WXK_NUMPAD4: ord('4'),
                wx.WXK_NUMPAD5: ord('5'),
                wx.WXK_NUMPAD6: ord('6'),
                wx.WXK_NUMPAD7: ord('7'),
                wx.WXK_NUMPAD8: ord('8'),
                wx.WXK_NUMPAD9: ord('9'),
                wx.WXK_NUMPAD_ADD: ord('+'),
                wx.WXK_NUMPAD_DECIMAL: ord('.'),
                wx.WXK_NUMPAD_DIVIDE: ord('/'),
                wx.WXK_NUMPAD_EQUAL: ord('='),
                wx.WXK_NUMPAD_MULTIPLY: ord('*'),
                wx.WXK_NUMPAD_SEPARATOR: ord('|'),
                wx.WXK_NUMPAD_SPACE: ord(' '),
                wx.WXK_NUMPAD_SUBTRACT: ord('-'),
            }

            self.key = mapping.get(key, 0)

        else:
            self.key = int(key)

        if self.key != 0:
            self.key_state = lv.INDEV_STATE_PRESSED
        else:
            self.key_state = lv.INDEV_STATE_RELEASED

        evt.Skip()

    def on_key_up(self, evt):
        self.key = 0
        self.key_state = lv.INDEV_STATE_RELEASED
        evt.Skip()

    def get_keyboard_state(self, indev_data):
        indev_data.key = self.key

    def get_mouse_state(self, indev_data):
        global mouse_event_waiting
        indev_data.state = self.state
        indev_data.point.x = self.mouse_point.x
        indev_data.point.y = self.mouse_point.y
        mouse_event_waiting = False

    def on_mouse_leave(self, evt):
        if self.HasCapture():
            global mouse_event_waiting
            self.ReleaseMouse()
            self.state = lv.INDEV_STATE_RELEASED
            point = evt.GetPosition()
            self.mouse_point.x = point.x
            self.mouse_point.y = point.y
            mouse_event_waiting = True

        evt.Skip()

    def on_mouse_move(self, evt):
        if self.HasCapture():
            global mouse_event_waiting
            print('wx_mouse_move')
            point = evt.GetPosition()
            self.mouse_point.x = point.x
            self.mouse_point.y = point.y
            mouse_event_waiting = True

    def on_left_up(self, evt):
        if self.HasCapture():
            global mouse_event_waiting
            print('wx left up')
            self.ReleaseMouse()
            self.state = lv.INDEV_STATE_RELEASED
            point = evt.GetPosition()
            self.mouse_point.x = point.x
            self.mouse_point.y = point.y
            mouse_event_waiting = True

        evt.Skip()

    def on_left_down(self, evt):
        if not self.HasCapture():
            global mouse_event_waiting
            print('wx left down')
            self.CaptureMouse()
            self.state = lv.INDEV_STATE_PRESSED
            point = evt.GetPosition()
            self.mouse_point.x = point.x
            self.mouse_point.y = point.y
            mouse_event_waiting = True

        evt.Skip()

    def flush_lvgl(self, disp, area, px_map):
        width = area.x2 - area.x1 + 1
        height = area.y2 - area.y1 + 1
        size = width * height

        dbuf = px_map.as_buffer('uint8_t', size * 4)

        bmp = wx.Bitmap(*self.GetClientSize())
        bmp.CopyFromBuffer(dbuf, wx.BitmapBufferFormat_RGBA)
        self.draw_alpha(bmp)

        bmp.Destroy()
        del bmp

        lv.disp_flush_ready(disp)

        self.count += 1

        if not self.count % 300:
            stop = time.time()
            diff = (stop * 1000) - (self.start * 1000)
            print(1 / (diff / 300 / 1000))
            self.count = 0
            self.start = time.time()


app = wx.App()
frame = Frame()


def keyboard_cb(_, data):
    frame.get_keyboard_state(data)


def mouse_cb(_, data):
    frame.get_mouse_state(data)


last_tick = wpt.time_ns()


def tick_cb(_):
    global last_tick

    curr_tick = wpt.time_ns()
    diff = curr_tick - last_tick

    int_diff = int(diff / 1000000)
    remainder = diff - int_diff
    curr_tick -= remainder
    last_tick = curr_tick
    lv.tick_inc(int_diff)


mouse_event_waiting = False


def run():
    lv.init()

    tick_dsc = lv.tick_dsc_t()
    lv.tick_set_cb(tick_dsc, tick_cb)

    disp = lv.disp_create(800, 600)

    lv.disp_set_flush_cb(disp, frame.flush_lvgl)

    _buf1 = lv.color_t.as_array(size=800 * 600)

    _buf1 = _buf1._obj

    # _buf1 = _lib_lvgl.ffi.new('lv_color32_t[{0}]'.format())
    lv.disp_set_color_format(disp, lv.COLOR_FORMAT_ARGB8888)
    lv.disp_set_draw_buffers(disp, _buf1,  None, 800 * 600, lv.DISP_RENDER_MODE_FULL)

    group = lv.group_create()
    lv.group_set_default(group)

    mouse = lv.indev_create()
    lv.indev_set_type(mouse, lv.INDEV_TYPE_POINTER)
    lv.indev_set_read_cb(mouse, mouse_cb)
    lv.timer_del(mouse.read_timer)

    keyboard = lv.indev_create()
    lv.indev_set_type(keyboard, lv.INDEV_TYPE_KEYPAD)
    lv.indev_set_read_cb(keyboard, keyboard_cb)
    lv.timer_set_period(keyboard.read_timer, 1)

    lv.indev_set_group(keyboard, group)

    _style = lv.style_t()
    lv.style_init(_style)  # NOQA

    lv.style_set_bg_color(_style, lv.color_hex(0x000000))  # NOQA
    lv.style_set_bg_opa(_style, 0)  # NOQA
    lv.style_set_border_color(_style, lv.color_hex(0x000000))  # NOQA
    lv.style_set_border_opa(_style, 0)  # NOQA
    lv.style_set_border_width(_style, 0)  # NOQA
    lv.style_set_margin_bottom(_style, 0)  # NOQA
    lv.style_set_margin_left(_style, 0)  # NOQA
    lv.style_set_margin_right(_style, 0)  # NOQA
    lv.style_set_margin_top(_style, 0)  # NOQA
    lv.style_set_outline_color(_style, lv.color_hex(0x000000))  # NOQA
    lv.style_set_outline_opa(_style, 0)  # NOQA
    lv.style_set_outline_pad(_style, 0)  # NOQA
    lv.style_set_outline_width(_style, 0)  # NOQA
    lv.style_set_pad_left(_style, 0)  # NOQA
    lv.style_set_pad_right(_style, 0)  # NOQA
    lv.style_set_pad_top(_style, 0)  # NOQA
    lv.style_set_pad_bottom(_style, 0)  # NOQA
    lv.style_set_radius(_style, 0)  # NOQA
    lv.style_set_shadow_color(_style, lv.color_hex(0x000000))  # NOQA
    lv.style_set_shadow_opa(_style, 0)  # NOQA
    lv.style_set_shadow_spread(_style, 0)  # NOQA
    lv.style_set_shadow_width(_style, 0)  # NOQA
    lv.style_set_shadow_ofs_x(_style, 0)  # NOQA
    lv.style_set_shadow_ofs_y(_style, 0)  # NOQA

    screen = lv.scr_act()
    lv.obj_set_style_bg_color(screen, lv.color_hex(0x000000), 0)
    lv.obj_set_style_bg_opa(screen, 0, 0)


    class Menu(lv.obj_t):

        def __init__(self, parent, name):

            super().__init__()
            obj = lv.obj_create(parent)
            obj.cast(self)
            lv.obj_add_style(self, _style, 0)

            lv.obj_set_style_border_opa(self, 150, 0)
            lv.obj_set_style_border_color(self, lv.color_hex(0xFF0000), 0)
            lv.obj_set_style_border_width(self, 5, 0)

            lv.obj_set_style_border_opa(self, 225, lv.STATE_PRESSED)
            lv.obj_set_style_border_color(self, lv.color_hex(0x0000FF), lv.STATE_PRESSED)
            lv.obj_set_style_border_width(self, 8, lv.STATE_PRESSED)

            lv.obj_set_style_bg_opa(self, 125, 0)
            lv.obj_set_style_bg_color(self, lv.color_hex(0x000000), 0)

            lv.obj_set_style_text_opa(self, 255, 0)
            lv.obj_set_style_text_color(self, lv.color_hex(0xFF0000), 0)

            self.label = label = lv.label_create(self)
            lv.label_set_text(label, ' ' * 30)

            lv.obj_set_style_text_font(label, lv.font_montserrat_20, 0)

            lv.obj_align(label, lv.ALIGN_LEFT_MID, 20, 0)

            self.children = []
            lv.obj_add_flag(self, lv.OBJ_FLAG_HIDDEN)

        def add_child(self, child):
            self.children.append(child)

        def set_text(self, text):
            lv.label_set_text(self.label, text)

        def show(self, value):
            if value:
                lv.obj_clear_flag(self, lv.OBJ_FLAG_HIDDEN)
            else:
                lv.obj_add_flag(self, lv.OBJ_FLAG_HIDDEN)

    class MenuItem(lv.obj_t):

        def __init__(self, parent):

            super().__init__()
            obj = lv.obj_create(parent)
            obj.cast(self)
            lv.obj_add_style(self, _style, 0)

            lv.obj_set_style_border_opa(self, 150, 0)
            lv.obj_set_style_border_color(self, lv.color_hex(0xFF0000), 0)
            lv.obj_set_style_border_width(self, 5, 0)

            lv.obj_set_style_border_opa(self, 225, lv.STATE_PRESSED)
            lv.obj_set_style_border_color(
                self,
                lv.color_hex(0x0000FF),
                lv.STATE_PRESSED
                )
            lv.obj_set_style_border_width(self, 8, lv.STATE_PRESSED)

            lv.obj_set_style_bg_opa(self, 125, 0)
            lv.obj_set_style_bg_color(self, lv.color_hex(0x000000), 0)

            lv.obj_set_style_text_opa(self, 255, 0)
            lv.obj_set_style_text_color(self, lv.color_hex(0xFF0000), 0)

            self.label = label = lv.label_create(self)
            lv.label_set_text(label, ' ' * 30)

            lv.obj_set_style_text_font(label, lv.font_montserrat_20, 0)

            lv.obj_align(label, lv.ALIGN_LEFT_MID, 20, 0)

            lv.obj_add_flag(self, lv.OBJ_FLAG_HIDDEN)

        def set_text(self, text):
            lv.label_set_text(self.label, text)

        def show(self, value):
            if value:
                lv.obj_clear_flag(self, lv.OBJ_FLAG_HIDDEN)
            else:
                lv.obj_add_flag(self, lv.OBJ_FLAG_HIDDEN)


    class BinaryItem(MenuItem):
        states = ['Off', 'On']

        def __init__(self, parent, name):
            MenuItem.__init__(self, parent)
            self.name = name

            self.state = 'Off'
            self.type = bool
            self.set_text(name + ': ' + self.state)

        def set_state(self, state):
            self.state = self.states[int(state)]
            self.set_text(f'{self.name}: {self.state}')

        def on_click(self, e):
            self.set_state(not bool(self.states.index(self.state)))



    class VariableItem(MenuItem):

        def __init__(self, parent, name):
            MenuItem.__init__(self, parent)
            self.name = name

            self.state = 'Off'
            self.type = float
            self.set_text(name + ': ' + self.state)

            self.slider = lv.slider_create(self)

            lv.obj_align(self.label, lv.ALIGN_TOP_LEFT, 20, 20)
            lv.obj_align(self.slider, lv.ALIGN_BOTTOM_LEFT, 20, 20)

            lv.slider_set_range(self.slider, 0, 1000)
            lv.obj_add_event(self.slider, self.on_slider, lv.EVENT_VALUE_CHANGED)

        def on_slider(self, e):
            value = lv.slider_get_value(self.slider)
            value /= 10.0
            self.set_state(value)

        def set_state(self, state):
            self.state = 'Off' if state == 0.0 else round(state, 2)
            self.set_text(f'{self.name}: {self.state}')

    class ChoiceItem()
    class ChoiceMenu(lv.obj_t):

        def __init__(self, parent, menu_items):



    class ChoiceItem(MenuItem):
        states = []

        def __init__(self, parent, name):
            MenuItem.__init__(self, parent)
            self.name = name
            self.state = self.states[0]
            self.type = bool
            self.set_text(name + ': ' + self.state)
            lv.obj_add_event(self, self.on_click, lv.EVENT_CLICKED)

        def set_state(self, state):
            self.state = self.states[int(state)]
            self.set_text(f'{self.name}: {self.state}')

        def on_click(self, e):
            self.set_state(not bool(self.states.index(self.state)))

    class BinarySwitch(BinaryItem):
        pass

    class MultilevelSwitch(VariableItem):
        pass


    class FanSwitch(ChoiceItem):
        pass

    menus = {
        'MediaRoom': {
            'Lights': {
                'Swittch 1': {
                    'state': 'On',
                    'states': ['Off', 'On'],
                    'value_type': bool
                },
                'Switch 2': {
                    'state': 35.0,
                    'value_type': float,
                },
            },

        },
        'Living Room': {},
        'Master Suite': {},
        'Spare Bedroom 1': {},
        'Spare Bedroom 2': {},
        'Hallway': {},
        'Kitchen': {},
        'Outside': {},
        'Main Bathroom': {},
        'HVAC': {}
    }




    while True:
        wpt.sleep(0.001)

        # lv.obj_invalidate(screen)
        # lv.refr_now(disp)
        lv.task_handler()


t = threading.Thread(target=run)
t.daemon = True
t.start()

app.MainLoop()
