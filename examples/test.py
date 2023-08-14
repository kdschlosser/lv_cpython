import sys
import os

base_path = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(base_path, '..')))

import lvgl as lv

import wx
import threading
import time

import ctypes
from ctypes.wintypes import (
    HDC,
    DWORD,
    INT,
    UINT,
    LONG,
    WORD,
    BYTE,
    HWND,
    BOOL,
    HBITMAP
)

HEIGHT = 640
WIDTH = 480


UBYTE = ctypes.c_ubyte
VOID = ctypes.c_void_p

user32 = ctypes.windll.User32
gdi32 = ctypes.windll.Gdi32

GetDC = user32.GetDC
GetDC.restype = HDC

ReleaseDC = user32.ReleaseDC
ReleaseDC.restype = BOOL

_SetDIBitsToDevice = gdi32.SetDIBitsToDevice
_SetDIBitsToDevice.restype = INT

def SetDIBitsToDevice(hdc, lpvBits):
    hdc = HDC(hdc)
    xDest = INT(0)
    yDest = INT(0)
    w = DWORD(WIDTH)
    h = DWORD(HEIGHT)
    xSrc = INT(0)
    ySrc = INT(HEIGHT)
    StartScan = UINT(0)
    cLines = UINT(HEIGHT)
    lpvBits = VOID(ctypes.addressof(lpvBits))
    lpbmi = BITMAPINFO()
    ColorUse = UINT(DIB_RGB_COLORS)

    lpbmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    lpbmi.bmiHeader.biWidth = WIDTH
    lpbmi.bmiHeader.biHeight = HEIGHT
    lpbmi.bmiHeader.biPlanes = 1
    lpbmi.bmiHeader.biBitCount = 32
    lpbmi.bmiHeader.biCompression = BI_BITFIELDS
    lpbmi.bmiHeader.biSizeImage = WIDTH * HEIGHT * 4
    lpbmi.bmiHeader.biXPelsPerMeter = int(DPI * 39.3701)
    lpbmi.bmiHeader.biYPelsPerMeter = int(DPI * 39.3701)
    lpbmi.bmiHeader.biClrUsed = 0
    lpbmi.bmiHeader.biClrImportant = 0

    res = _SetDIBitsToDevice(
        hdc,
        xDest,
        yDest,
        w,
        h,
        xSrc,
        ySrc,
        StartScan,
        cLines,
        lpvBits,
        ctypes.byref(lpbmi),
        ColorUse
    )

    print(res)


DIB_RGB_COLORS = 0
DIB_PAL_COLORS = 1
BI_RGB = 0x0000
BI_BITFIELDS = 0x0003


class tagRGBQUAD(ctypes.Structure):
    _fields_ = [
        ('rgbBlue', BYTE),
        ('rgbGreen', BYTE),
        ('rgbRed', BYTE),
        ('rgbReserved', BYTE)
    ]


RGBQUAD = tagRGBQUAD


class tagBITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ('biSize', DWORD),
        # buffer width
        ('biWidth', LONG),
        # buffer height
        ('biHeight', LONG),
        # must be set to 1
        ('biPlanes', WORD),
        # bits per pixel (32)
        ('biBitCount', WORD),
        # set to BI_BITFIELDS
        ('biCompression', DWORD),
        # stride = ((((biWidth * biBitCount) + 31) & ~31) >> 3);
        # biSizeImage = abs(biHeight) * stride;
        ('biSizeImage', DWORD),

        ('biXPelsPerMeter', LONG),
        ('biYPelsPerMeter', LONG),
        # size of RGBQUAD array
        ('biClrUsed', DWORD),
        # set to 0
        ('biClrImportant', DWORD)
    ]


BITMAPINFOHEADER = tagBITMAPINFOHEADER
LPBITMAPINFOHEADER = ctypes.POINTER(tagBITMAPINFOHEADER)
PBITMAPINFOHEADER = ctypes.POINTER(tagBITMAPINFOHEADER)


class tagBITMAPINFO(ctypes.Structure):
    _fields_ = [
        ('bmiHeader', BITMAPINFOHEADER),
        ('bmiColors', RGBQUAD * 1)
    ]


BITMAPINFO = tagBITMAPINFO
LPBITMAPINFO = ctypes.POINTER(tagBITMAPINFO)
PBITMAPINFO = ctypes.POINTER(tagBITMAPINFO)

_CreateBitmap = gdi32.CreateBitmap
# _CreateBitmap.restype = HBITMAP

def CreateBitmap(pBits):
  nWidth = INT(WIDTH)
  nHeight = INT(HEIGHT)
  nPlanes = UINT(1)
  nBitCount = UINT(32)
  lpBits = ctypes.c_void_p(ctypes.addressof(pBits))
  return _CreateBitmap(nWidth, nHeight, nPlanes, nBitCount, lpBits)


class Frame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(
            self,
            None,
            -1,
            style=(
                wx.FRAME_SHAPED |
                wx.NO_BORDER |
                wx.FRAME_NO_TASKBAR |
                wx.STAY_ON_TOP
            )
        )
        self.buf = None
        self.disp = None

        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda x: None)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.SetClientSize((WIDTH, HEIGHT))

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

    def OnPaint(self, evt):
        if self.disp is not None:
            buf = ctypes.cast(self.buf, ctypes.POINTER(ctypes.c_uint8 * (WIDTH * HEIGHT * 4))).contents
            print(type(buf))
            for i in range(WIDTH):
                print(buf[i])

            print('BMP')
            bmp = wx.Bitmap.FromBufferRGBA(WIDTH, HEIGHT, buf)
            print('BMP Created')

            pdc = wx.PaintDC(self)
            print('DC created')

            pdc.DrawBitmap(bmp, 0, 0)
            print('BMP rendered')
            pdc.Destroy()
            del pdc

            lv.disp_flush_ready(self.disp)

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
        indev_data.contents.key = self.key

    def get_mouse_state(self, indev_data):
        indev_data.contents.state = self.state
        indev_data.contents.point.x = self.mouse_point.x
        indev_data.contents.point.y = self.mouse_point.y

    def on_mouse_leave(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()
            self.state = lv.INDEV_STATE_RELEASED
            point = evt.GetPosition()
            self.mouse_point.x = point.x
            self.mouse_point.y = point.y

        evt.Skip()

    def on_mouse_move(self, evt):
        if self.HasCapture():
            point = evt.GetPosition()
            self.mouse_point.x = point.x
            self.mouse_point.y = point.y

    def on_left_up(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()
            self.state = lv.INDEV_STATE_RELEASED
            point = evt.GetPosition()
            self.mouse_point.x = point.x
            self.mouse_point.y = point.y

        evt.Skip()

    def on_left_down(self, evt):
        if not self.HasCapture():
            self.CaptureMouse()
            self.state = lv.INDEV_STATE_PRESSED
            point = evt.GetPosition()
            self.mouse_point.x = point.x
            self.mouse_point.y = point.y

        evt.Skip()

    def flush_lvgl(self, disp, area, px_map):
        self.disp = disp
        self.buf = px_map

        def _do():
            self.Refresh()

        wx.CallAfter(_do)


app = wx.App()
frame = Frame()
frame.Show()


def keyboard_cb(_, data):
    frame.get_keyboard_state(data)


def mouse_cb(_, data):
    frame.get_mouse_state(data)

DPI = 0

def run():
    global DPI
    print('init')
    lv.init()
    print('disp_create')

    disp = lv.disp_create(WIDTH, HEIGHT)

    DPI = lv.disp_get_dpi(disp)

    print('disp_set_flush_cb')

    lv.disp_set_flush_cb(disp, frame.flush_lvgl)

    print('buf_1')

    buf_1 = (lv.color_t * (WIDTH * HEIGHT))()
    buf_2 = (lv.color_t * (WIDTH * HEIGHT))()
    print('disp_set_draw_buffers')

    lv.disp_set_draw_buffers(disp, buf_1,  buf_2, WIDTH * HEIGHT, lv.DISP_RENDER_MODE_PARTIAL)
    print('group_create')
    #
    # group = lv.group_create()
    # print('group_set_default')
    #
    # lv.group_set_default(group)
    # print('indev_create')
    #
    # mouse = lv.indev_create().contents
    # print('indev_set_type')
    #
    # lv.indev_set_type(mouse, lv.INDEV_TYPE_POINTER)
    # print('indev_set_read_cb')
    #
    # lv.indev_set_read_cb(mouse, mouse_cb)
    # print('timer_set_period')
    #
    # lv.timer_set_period(mouse.read_timer, 1)
    #
    # print('indev_create')
    #
    # keyboard = lv.indev_create().contents
    # print('indev_set_type')
    #
    # lv.indev_set_type(keyboard, lv.INDEV_TYPE_KEYPAD)
    # print('indev_set_read_cb')
    #
    # lv.indev_set_read_cb(keyboard, keyboard_cb)
    # print('timer_set_period')
    #
    # lv.timer_set_period(keyboard.read_timer, 1)
    #
    # print('indev_set_group')
    #
    # # lv.indev_set_group(keyboard, group)

    print('scr_act')
    time.sleep(0.001)

    screen = lv.scr_act()

    print('obj_set_style_bg_color')


    lv.obj_set_style_bg_color(screen, lv.color_hex(0x000000), 0)

    def value_changed_event_cb(e):

        txt = "{:d}%".format(lv.arc_get_value(arc))
        lv.label_set_text(label, txt)

        # Rotate the label to the current position of the arc
        lv.arc_rotate_obj_to_angle(arc, label, 50)

    print('label_create')

    label = lv.label_create(screen)
    print('obj_set_style_text_color')

    lv.obj_set_style_text_color(label, lv.color_hex(0x00FF00), 0)

    # lv.obj_set_style_text_font(label, lv.font_montserrat_24, 0)

    # Create an Arc
    print('arc_create')

    arc = lv.arc_create(screen)
    print('obj_set_style_arc_color')

    lv.obj_set_style_arc_color(arc, lv.color_hex(0xFF0000), lv.PART_INDICATOR)
    print('obj_set_size')

    lv.obj_set_size(arc, 200, 200)
    print('obj_set_style_arc_width')

    lv.obj_set_style_arc_width(arc, 30, 0)
    print('obj_set_style_arc_width')

    lv.obj_set_style_arc_width(arc, 30, lv.PART_INDICATOR)
    print('arc_set_rotation')

    lv.arc_set_rotation(arc, 135)
    print('arc_set_bg_angles')

    lv.arc_set_bg_angles(arc, 0, 270)
    print('arc_set_value')

    lv.arc_set_value(arc, 0)
    print('obj_center')

    lv.obj_center(arc)
    print('obj_add_event')

    lv.obj_add_event(
        arc,
        value_changed_event_cb,
        lv.EVENT_VALUE_CHANGED,
        None
    )
    print('obj_send_event')

    # Manually update the label for the first time
    lv.obj_send_event(arc, lv.EVENT_VALUE_CHANGED, None)

    val = 0
    inc = 1

    start_time = time.time()
    print('loop')

    while True:
        stop_time = time.time()

        diff = int(stop_time - start_time)
        if diff >= 1:
            lv.tick_inc(diff)

            val += inc
            if val in (0, 100):
                inc = -inc

            lv.arc_set_value(arc, val)
            lv.obj_send_event(arc, lv.EVENT_VALUE_CHANGED, None)

            lv.task_handler()
            start_time = stop_time


t = threading.Thread(target=run)
t.daemon = True
t.start()

app.MainLoop()

