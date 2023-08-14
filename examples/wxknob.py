import os
import sys

base_path = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(base_path, '..')))

import lvgl as lv


import wx
import threading
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
        print(indev_data)
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
            lv.indev_read_timer_cb(mouse.read_timer)
            mouse_event_waiting = True

        evt.Skip()

    def on_mouse_move(self, evt):
        if self.HasCapture():
            global mouse_event_waiting
            print('wx_mouse_move')
            point = evt.GetPosition()
            self.mouse_point.x = point.x
            self.mouse_point.y = point.y
            lv.indev_read_timer_cb(mouse.read_timer)
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
            lv.indev_read_timer_cb(mouse.read_timer)
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
            lv.indev_read_timer_cb(mouse.read_timer)
            mouse_event_waiting = True

        evt.Skip()

    def flush_lvgl(self, disp, area, px_map):
        bmp = wx.Bitmap(*self.GetClientSize())
        bmp.CopyFromBuffer(_buf1, wx.BitmapBufferFormat_RGBA)
        self.draw_alpha(bmp)

        bmp.Destroy()
        del bmp

        lv.disp_flush_ready(disp)
        print('flushed')


app = wx.App()
frame = Frame()


def keyboard_cb(_, data):
    frame.get_keyboard_state(data)


def mouse_cb(_, data):
    print(data)
    frame.get_mouse_state(data)


def log_cb(level, message):
    message = message * 1000

    print(message)


mouse_event_waiting = False

_buf1 = bytearray(800 * 600 * 4)

mouse = None

def run():
    global mouse
    lv.init()

    lv.log_register_print_cb(log_cb)

    disp = lv.disp_create(800, 600)

    lv.disp_set_flush_cb(disp, frame.flush_lvgl)
    lv.disp_set_color_format(disp, lv.COLOR_FORMAT_XRGB8888)
    _array_buf = lv.uint8_t * (800 * 600 * 4)

    lv.disp_set_color_format(disp, lv.COLOR_FORMAT_ARGB8888)
    lv.disp_set_draw_buffers(disp, _array_buf.from_buffer(_buf1),  None, 800 * 600, lv.DISP_RENDER_MODE_FULL)

    group = lv.group_create()
    lv.group_set_default(group)

    mouse = lv.indev_create()
    lv.indev_set_type(mouse, lv.INDEV_TYPE_POINTER)
    lv.indev_set_read_cb(mouse, mouse_cb)

    import ctypes

    print(mouse.disabled)
    print(disp.prev_scr)
    print()
    # lv.timer_set_period(mouse.read_timer, 5)

    keyboard = lv.indev_create()
    lv.indev_set_type(keyboard, lv.INDEV_TYPE_KEYPAD)
    lv.indev_set_read_cb(keyboard, keyboard_cb)
    # lv.timer_set_period(keyboard.read_timer, 5)

    lv.indev_set_group(keyboard, group)

    screen = lv.scr_act()
    lv.obj_set_style_bg_color(screen, lv.color_hex(0x2D2D2D), 0)
    lv.obj_set_style_bg_opa(screen, 255, 0)
    lv.obj_set_scrollbar_mode(screen, lv.SCROLLBAR_MODE_OFF)

    import knob

    volume = knob.knob_ctrl(screen)

    lv.obj_center(volume.obj)
    # volume.set_segment_display(True)
    volume.set_size(500, 500)

    print('running')
    while True:
        # start_time = time.time()
        time.sleep(0.0001)

        lv.tick_inc(1)
        lv.task_handler()
        # stop_time = time.time()
        # print((stop_time - start_time) * 1000)


t = threading.Thread(target=run)
t.daemon = True
t.start()

app.MainLoop()
