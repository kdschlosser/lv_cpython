try:
    import lvgl as lv
except ImportError:
    import os
    import sys

    base_path = os.path.dirname(__file__)
    sys.path.insert(0, os.path.abspath(os.path.join(base_path, '..', 'build')))

    import lvgl as lv


import math
import time
import os


last_tick = time.time()


def tick_cb(_):
    global last_tick

    curr_tick = time.time()
    diff = (curr_tick * 1000) - (last_tick * 1000)

    int_diff = int(diff)
    remainder = diff - int_diff

    curr_tick -= remainder / 1000
    last_tick = curr_tick

    lv.tick_inc(int_diff)


lv.init()

tick_dsc = lv.tick_dsc_t()
lv.tick_set_cb(tick_dsc, tick_cb)

disp = lv.sdl_window_create(800, 600)
group = lv.group_create()
lv.group_set_default(group)
mouse = lv.sdl_mouse_create()
keyboard = lv.sdl_keyboard_create()
lv.indev_set_group(keyboard, group)


LV_PART_KNOB_CENTER = 0x090000
LV_PART_KNOB_RING = 0x0A0000
LV_PART_KNOB_GRIP = 0x0B0000

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


class Point(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def lv_point(self):
        return lv.point_t(x=int(self.x), y=int(self.y))


class seg(object):

    def __init__(self, line_width, end1, end2, line):
        self.end1 = end1
        self.end2 = end2
        self.line = line
        self._is_lit = False

        self.off_color = lv.color_hex(0x191919)
        self.on_color = lv.color_hex(0x17F203)
        self.on_opa = 255

        poly_dsc = self.poly_dsc = lv.draw_rect_dsc_t()
        lv.draw_rect_dsc_init(poly_dsc)
        poly_dsc.bg_color = self.off_color
        poly_dsc.bg_opa = 255

        line_dsc = self.line_dsc = lv.draw_line_dsc_t()
        lv.draw_line_dsc_init(line_dsc)
        line_dsc.color = self.off_color
        line_dsc.width = line_width
        line_dsc.opa = 255
        line_dsc.round_start = False
        line_dsc.round_end = False

    def set_color(self, color, opa):
        self.on_color = color
        self.on_opa = opa
        self.is_lit = self._is_lit

    @property
    def is_lit(self):
        return self._is_lit

    @is_lit.setter
    def is_lit(self, value):
        self._is_lit = value

        if value:
            self.poly_dsc.bg_color = self.on_color
            self.line_dsc.color = self.on_color
        else:
            self.poly_dsc.bg_color = self.off_color
            self.line_dsc.color = self.off_color

    def draw(self, canvas):
        lv.canvas_draw_line(canvas, self.line, 2, self.line_dsc)
        lv.canvas_draw_polygon(canvas, self.end1, 3, self.poly_dsc)
        lv.canvas_draw_polygon(canvas, self.end2, 3, self.poly_dsc)


class digit(object):

    def __init__(self, x, y, width, height, only_one=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        size = min(width, height)

        seg_width = int(size * 0.20)
        seg_length = int(size * 0.72)
        seg_line_length = int(seg_length * 0.77)
        seg_end_height = int((seg_length - seg_line_length) / 2)
        seg_end_center = int(seg_width / 2)

        offset_y = int(height * 0.87)
        offset_x = int(width * 0.75)

        center_y = int(height / 2) + y
        x = int((width - offset_x) / 2) + x
        y = int((height - offset_y) / 2) + y

        seg1 = (
            Point(x - 1, center_y - 1),
            Point(x - 1, y + 1)
        )
        seg2 = (
            Point(x + 1, y - 1),
            Point(x + offset_x - 1, y - 1)
        )
        seg3 = (
            Point(x + offset_x + 1, y + 1),
            Point(x + offset_x + 1, center_y - 1)
        )
        seg4 = (
            Point(x + offset_x + 1, center_y + 1),
            Point(x + offset_x + 1, y + offset_y - 1)
        )
        seg5 = (
            Point(x + 1, y + offset_y + 1),
            Point(x + offset_x - 1, y + offset_y + 1)
        )
        seg6 = (
            Point(x - 1, y + offset_y - 1), Point(x - 1, center_y + 1)
        )
        seg7 = (
            Point(x + 1, center_y),
            Point(x + offset_x - 1, center_y)
        )

        seg1 = (
            (seg1[0].lv_point, Point(
                seg1[0].x - seg_end_center,
                seg1[0].y - seg_end_height
                ).lv_point, Point(
                seg1[0].x + seg_end_center,
                seg1[0].y - seg_end_height
                ).lv_point),
            (seg1[1].lv_point, Point(
                seg1[1].x - seg_end_center,
                seg1[1].y + seg_end_height
                ).lv_point, Point(
                seg1[1].x + seg_end_center,
                seg1[1].y + seg_end_height
                ).lv_point),
            (Point(seg1[0].x, seg1[0].y - seg_end_height).lv_point,
             Point(seg1[1].x, seg1[1].y + seg_end_height).lv_point)
        )

        seg2 = (
            (seg2[0].lv_point, Point(
                seg2[0].x + seg_end_height,
                seg2[0].y - seg_end_center
                ).lv_point, Point(
                seg2[0].x + seg_end_height,
                seg2[0].y + seg_end_center
                ).lv_point),
            (seg2[1].lv_point, Point(
                seg2[1].x - seg_end_height,
                seg2[1].y - seg_end_center
                ).lv_point, Point(
                seg2[1].x - seg_end_height,
                seg2[1].y + seg_end_center
                ).lv_point),
            (Point(seg2[0].x + seg_end_height, seg2[0].y).lv_point,
             Point(seg2[1].x - seg_end_height, seg2[1].y).lv_point)
        )

        seg3 = (
            (seg3[0].lv_point, Point(
                seg3[0].x - seg_end_center,
                seg3[0].y + seg_end_height
                ).lv_point, Point(
                seg3[0].x + seg_end_center,
                seg3[0].y + seg_end_height
                ).lv_point),
            (seg3[1].lv_point, Point(
                seg3[1].x - seg_end_center,
                seg3[1].y - seg_end_height
                ).lv_point, Point(
                seg3[1].x + seg_end_center,
                seg3[1].y - seg_end_height
                ).lv_point),
            (Point(seg3[0].x, seg3[0].y + seg_end_height).lv_point,
             Point(seg3[1].x, seg3[1].y - seg_end_height).lv_point)
        )

        seg4 = (
            (seg4[0].lv_point, Point(
                seg4[0].x - seg_end_center,
                seg4[0].y + seg_end_height
                ).lv_point, Point(
                seg4[0].x + seg_end_center,
                seg4[0].y + seg_end_height
                ).lv_point),
            (seg4[1].lv_point, Point(
                seg4[1].x - seg_end_center,
                seg4[1].y - seg_end_height
                ).lv_point, Point(
                seg4[1].x + seg_end_center,
                seg4[1].y - seg_end_height
                ).lv_point),
            (Point(seg4[0].x, seg4[0].y + seg_end_height).lv_point,
             Point(seg4[1].x, seg4[1].y - seg_end_height).lv_point)
        )

        seg5 = (
            (seg5[0].lv_point, Point(
                seg5[0].x + seg_end_height,
                seg5[0].y - seg_end_center
                ).lv_point, Point(
                seg5[0].x + seg_end_height,
                seg5[0].y + seg_end_center
                ).lv_point),
            (seg5[1].lv_point, Point(
                seg5[1].x - seg_end_height,
                seg5[1].y - seg_end_center
                ).lv_point, Point(
                seg5[1].x - seg_end_height,
                seg5[1].y + seg_end_center
                ).lv_point),
            (Point(seg5[0].x + seg_end_height, seg5[0].y).lv_point,
             Point(seg5[1].x - seg_end_height, seg5[1].y).lv_point)
        )

        seg6 = (
            (seg6[0].lv_point, Point(
                seg6[0].x - seg_end_center,
                seg6[0].y - seg_end_height
                ).lv_point, Point(
                seg6[0].x + seg_end_center,
                seg6[0].y - seg_end_height
                ).lv_point),
            (seg6[1].lv_point, Point(
                seg6[1].x - seg_end_center,
                seg6[1].y + seg_end_height
                ).lv_point, Point(
                seg6[1].x + seg_end_center,
                seg6[1].y + seg_end_height
                ).lv_point),
            (Point(seg6[0].x, seg6[0].y - seg_end_height).lv_point,
             Point(seg6[1].x, seg6[1].y + seg_end_height).lv_point)
        )

        seg7 = (
            (seg7[0].lv_point, Point(
                seg7[0].x + seg_end_height,
                seg7[0].y - seg_end_center
                ).lv_point, Point(
                seg7[0].x + seg_end_height,
                seg7[0].y + seg_end_center
                ).lv_point),
            (seg7[1].lv_point, Point(
                seg7[1].x - seg_end_height,
                seg7[1].y - seg_end_center
                ).lv_point, Point(
                seg7[1].x - seg_end_height,
                seg7[1].y + seg_end_center
                ).lv_point),
            (Point(seg7[0].x + seg_end_height, seg7[0].y).lv_point,
             Point(seg7[1].x - seg_end_height, seg7[1].y).lv_point)
        )

        seg1 = seg(seg_width, *seg1)
        seg2 = seg(seg_width, *seg2)
        seg3 = seg(seg_width, *seg3)
        seg4 = seg(seg_width, *seg4)
        seg5 = seg(seg_width, *seg5)
        seg6 = seg(seg_width, *seg6)
        seg7 = seg(seg_width, *seg7)

        self.only_one = only_one

        if only_one:
            self.all_segs = (seg3, seg4)

            self.mapping = (
                (),
                (seg3, seg4)
            )

        else:
            self.all_segs = (seg1, seg2, seg3, seg4, seg5, seg6, seg7)

            self.mapping = (
                (seg1, seg2, seg3, seg4, seg5, seg6),
                (seg3, seg4),
                (seg2, seg3, seg5, seg6, seg7),
                (seg2, seg3, seg4, seg5, seg7),
                (seg1, seg3, seg4, seg7),
                (seg1, seg2, seg4, seg5, seg7),
                (seg1, seg2, seg4, seg5, seg6, seg7),
                (seg2, seg3, seg4),
                (seg1, seg2, seg3, seg4, seg5, seg6, seg7),
                (seg1, seg2, seg3, seg4, seg5, seg7)
            )

    def set_value(self, val):
        if val is None:
            for s in self.all_segs:
                s.is_lit = False

        else:
            segs = self.mapping[val]

            for s in self.all_segs:
                if s in segs:
                    s.is_lit = True
                else:
                    s.is_lit = False

    def draw(self, dsc):
        for s in self.all_segs:
            s.draw(dsc)

    def set_color(self, color, opa):
        for s in self.all_segs:
            s.set_color(color, opa)


base_path = os.path.dirname(__file__)

with open(os.path.join(base_path, 'assets', 'knob_gradient.png'), 'rb') as f:
    knob_gradient_data = f.read()

with open(os.path.join(base_path, 'assets', 'knob_glass.png'), 'rb') as f:
    knob_glass_data = f.read()

glass = lv.img_dsc_t(
    data_size=len(knob_glass_data),
    data=knob_glass_data
)

ui_img_gradient = lv.img_dsc_t(
    data_size=len(knob_gradient_data),
    data=knob_gradient_data
)


class segmented_display(lv.obj_t):

    def __init__(self, parent):
        super().__init__()
        obj = lv.obj_create(parent)
        obj.cast(self)

        self.canvas = lv.canvas_create(self)

        self._max_value = 0
        self.digits = []

        self.glass_img = glass_img = lv.img_create(self)
        lv.img_set_src(glass_img, glass)
        lv.obj_set_width(glass_img, lv.SIZE_CONTENT)  # NOQA
        lv.obj_set_height(glass_img, lv.SIZE_CONTENT)  # NOQA
        lv.obj_set_align(glass_img, lv.ALIGN_CENTER)
        lv.obj_clear_flag(glass_img, lv.OBJ_FLAG_CLICKABLE)
        lv.obj_clear_flag(glass_img, lv.OBJ_FLAG_SCROLLABLE)

        self.on_color = lv.color_hex(0x17F203)
        self.on_opa = 255
        self._bg_color = lv.color_hex(0x000000)

        lv.obj_set_style_img_recolor(glass_img, self._bg_color, 0)
        lv.obj_set_style_img_recolor_opa(glass_img, 25, 0)

        self.cbuf = bytes(lv.color_t.sizeof() * 2 * 2)
        lv.canvas_set_buffer(self.canvas, self.cbuf,
                             2, 2, lv.COLOR_FORMAT_NATIVE)
        lv.obj_center(self.canvas)
        zoom = int(remap(lv.obj_get_width(self), 0, 100, 0, 255))
        lv.img_set_zoom(glass_img, zoom)

        lv.obj_set_style_bg_color(self, self._bg_color, 0)
        lv.obj_set_style_bg_opa(self, 255, 0)

        # self.set_style_outline_color(lv.color_hex(0x000000), 0)
        # self.set_style_outline_width(1, 0)
        # self.set_style_outline_opa(255, 0)

        # self.set_style_border_color(lv.color_hex(0x686868), 0)
        # self.set_style_border_width(2, 0)
        # self.set_style_border_opa(255, 0)

        # self.set_style_shadow_color(lv.color_hex(0x000000), 0)
        # self.set_style_shadow_width(2, 0)
        # self.set_style_shadow_opa(255, 0)
        # self.set_style_shadow_spread(2, 0)

    def set_style_text_color(self, color, selector):
        self.on_color = color

        for d in self.digits:
            d.set_color(color, self.on_opa)

        self.__draw()

    def set_style_text_opa(self, opa, selector):
        self.on_opa = opa

        for d in self.digits:
            d.set_color(self.on_color, opa)

    def set_size(self, diameter):
        lv.obj_set_size(self, diameter, diameter)

        height = int(diameter / 3)
        width = int(diameter * 0.90)

        self.cbuf = bytes(lv.color_t.sizeof() * width * height)
        lv.canvas_set_buffer(self.canvas, self.cbuf, width,
                             height, lv.COLOR_FORMAT_NATIVE)
        lv.canvas_fill_bg(self.canvas, self._bg_color, lv.OPA_COVER)

        zoom = int(remap(diameter, 0, 100, 0, 255))
        lv.img_set_zoom(self.glass_img, zoom)
        self.__draw()

    def set_style_bg_color(self, color, selector):
        lv.obj_set_style_bg_color(self, color, selector)
        self._bg_color = color
        lv.canvas_fill_bg(self.canvas, color, lv.OPA_COVER)
        # self.glass_img.set_style_img_recolor(self._bg_color, 0)
        # self.glass_img.set_style_img_recolor_opa(255, 0)
        self.__draw()

    def set_max_value(self, value):
        value = str(value)
        self.digits.clear()

        lv.obj_update_layout(self)
        diameter = lv.obj_get_width(self)

        height = int(diameter / 3)
        width = int(diameter * 0.90)

        x = int(remap(height, 0, 189, 0, 95))
        y = 0

        character_width = int(width / (len(value) + 2))
        spacing = (width - (character_width * len(value)) - (x * 2)) - 1

        for i, v in enumerate(list(value)):
            if i == 0 and v == '1':
                only_one = True
            else:
                only_one = False

            if only_one:
                x -= int(character_width / 2)

            self.digits.append(digit(x, y, character_width, height, only_one))
            x += character_width + spacing

        lv.canvas_fill_bg(self.canvas, self._bg_color, lv.OPA_COVER)
        self.__draw()

    def __draw(self):
        for d in self.digits:
            d.draw(self.canvas)

    def set_value(self, val):
        val = list(str(int(val)))
        used_digits = []

        for i in range(len(self.digits) - 1, -1, -1):
            if not val:
                break

            v = val.pop(len(val) - 1)
            d = self.digits[i]

            d.set_value(int(v))
            used_digits.append(d)

        for d in self.digits:
            if d not in used_digits:
                d.set_value(None)

        self.__draw()


def _build_gradient(begin_rgb, end_rgb, nb):
    def rgb2hex(r, g, b):
        return (r & 0xFF) << 16 | (g & 0xFF) << 8 | (b & 0xFF)

    br, bg, bb = begin_rgb
    er, eg, eb = end_rgb

    r_diff = er - br
    g_diff = eg - bg
    b_diff = eb - bb

    r_fact = r_diff / float(nb)
    g_fact = g_diff / float(nb)
    b_fact = b_diff / float(nb)

    for i in range(0, nb + 1):
        yield rgb2hex(
            fround(br + (i * r_fact)),
            fround(bg + (i * g_fact)),
            fround(bb + (i * b_fact))
        )


def remap(value, old_min, old_max, new_min, new_max):
    return (((value - old_min) * (new_max - new_min)) / (
                old_max - old_min)) + new_min


def _remap(value, old_min, old_max, new_min, new_max):
    return fround(
        (((value - old_min) * (new_max - new_min)) / (
                old_max - old_min)) + new_min
    )


def fround(value):
    value = int(value * 10.0 + 0.5)
    return int(value / 10)


def _point_on_circle(degree, center_x, center_y, radius):
    radians = math.radians(degree)
    x = int(center_x + (radius * math.cos(radians)))
    y = int(center_y + (radius * math.sin(radians)))
    return x, y


def _get_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def _get_angle(x1, y1, x2, y2):
    return math.degrees(math.atan2(y1 - y2, x1 - x2))


class _tick(lv.obj_t):

    def __init__(self, parent):
        super().__init__()
        obj = lv.obj_create(parent)
        obj.cast(self)

        self._points = None
        self._major = False
        self._width = None
        lv.obj_add_style(self, _style, 0)
        lv.obj_set_style_shadow_width(self, 20, 0)
        # set_style_shadow_color
        lv.obj_set_style_shadow_opa(self, 0, 0)
        lv.obj_set_style_shadow_spread(self, 0, 0)

    @property
    def is_major(self):
        return self._major

    @is_major.setter
    def is_major(self, value):
        self._major = value

    def get_style_line_color(self, selector):
        return lv.obj_get_style_bg_color(self, selector)

    def set_style_line_color(self, color, selector):
        lv.obj_set_style_bg_color(self, color, selector)
        lv.obj_set_style_shadow_color(self, color, selector)

    def set_style_line_opa(self, opa, selector):
        lv.obj_set_style_bg_opa(self, opa, selector)
        lv.obj_set_style_shadow_opa(self, opa, selector)

    def get_style_line_opa(self, selector):
        return lv.obj_get_style_bg_opa(self, selector)

    def set_points(self, points, length):
        self._points = points

        if self._width is not None:
            self.__set_position()

    def __set_position(self):
        lv.obj_set_style_transform_angle(self, 0, 0)

        p1, p2 = self._points
        height = _get_distance(p1.x, p1.y, p2.x, p2.y)

        parent = lv.obj_get_parent(self)
        lv.obj_update_layout(parent)

        center_x = int(lv.obj_get_width(parent) / 2)
        center_y = int(lv.obj_get_height(parent) / 2)
        radius = _get_distance(center_x, center_y, p1.x, p1.y)

        lv.obj_set_height(self, int(height))

        radius -= int(height / 2)

        angle = _get_angle(p1.x, p1.y, p2.x, p2.y)
        # x, y = _point_on_circle(
        #     angle,
        #     center_x - self._width,
        #     center_y - height,
        #     radius
        #     )

        lv.obj_set_x(self, p1.x)
        lv.obj_set_y(self, p1.y)
        lv.obj_set_style_transform_angle(self, int((angle - 270) * 10), 0)

    def get_points(self):
        return self._points

    def get_style_line_width(self, selector):
        return self._width

    def set_style_line_width(self, width, selector):
        # lv.obj_set_style_shadow_spread(self, 0, 0)  # max(1, int(width / 4)), 0)
        lv.obj_set_width(self, max(1, int(width * 0.75)))
        self._width = width
        if self._points is not None:
            self.__set_position()

    @property
    def length(self):
        if self._points is None:
            raise RuntimeError('this should not happen, sanity check')

        p1, p2 = self._points

        return _get_distance(p1.x, p1.y, p2.x, p2.y)

    @property
    def angle(self):
        if self._points is None:
            raise RuntimeError('this should not happen, sanity check')

        p1 = self._points[0]

        return math.degrees(math.atan2(p1.y, p1.x))


class knob_ctrl(lv.obj_t):

    def __init__(self, parent):
        super().__init__()
        obj = lv.obj_create(parent)
        obj.cast(self)

        lv.obj_add_style(self, _style, 0)
        lv.obj_add_flag(self, lv.OBJ_FLAG_OVERFLOW_VISIBLE)

        lv.obj_update_layout(parent)
        size = 320
        size -= 20

        lv.obj_set_width(self, size)
        lv.obj_set_height(self, size)
        lv.obj_clear_flag(self, lv.OBJ_FLAG_SCROLLABLE)
        lv.obj_set_align(self, lv.ALIGN_CENTER)

        shadow_size = int(round(size * 0.7))

        self._shadow = shadow = lv.obj_create(self)
        lv.obj_set_width(shadow, shadow_size)
        lv.obj_set_height(shadow, shadow_size)
        lv.obj_add_style(shadow, _style, 0)
        lv.obj_set_style_radius(shadow, int(round(shadow_size / 2)), 0)
        lv.obj_set_align(shadow, lv.ALIGN_CENTER)
        lv.obj_set_style_shadow_opa(shadow, 175, 0)
        # shadow.set_style_shadow_color(lv.color_hex(0x7F7F7F), 0)

        lv.obj_set_style_shadow_width(shadow, 60, 0)
        lv.obj_set_style_shadow_spread(shadow, 2, 0)
        lv.obj_set_style_shadow_ofs_x(shadow, -20, 0)
        lv.obj_set_style_shadow_ofs_y(shadow, -20, 0)
        lv.obj_clear_flag(shadow, lv.OBJ_FLAG_SCROLLABLE)
        lv.obj_clear_flag(shadow, lv.OBJ_FLAG_CLICKABLE)

        self._glow = glow = lv.obj_create(self)
        lv.obj_set_width(glow, shadow_size)
        lv.obj_set_height(glow, shadow_size)
        lv.obj_set_align(glow, lv.ALIGN_CENTER)
        lv.obj_clear_flag(glow, lv.OBJ_FLAG_SCROLLABLE)
        lv.obj_clear_flag(glow, lv.OBJ_FLAG_CLICKABLE)
        lv.obj_add_style(glow, _style, 0)
        lv.obj_set_style_bg_opa(glow, 255, 0)

        lv.obj_set_style_radius(glow, int(shadow_size / 2), 0)
        lv.obj_set_style_shadow_color(glow, lv.color_hex(0xFF0000), 0)
        lv.obj_set_style_shadow_opa(glow, 255, 0)
        lv.obj_set_style_shadow_width(glow, 40, 0)
        lv.obj_set_style_shadow_spread(glow, 5, 0)

        ring_img_size = _remap(shadow_size, 0, 200, 0, 256)

        self._ring_img = ring_img = lv.img_create(glow)
        lv.img_set_src(ring_img, ui_img_gradient)
        lv.obj_set_width(ring_img, lv.SIZE_CONTENT)  # NOQA
        lv.obj_set_height(ring_img, lv.SIZE_CONTENT)  # NOQA
        lv.obj_set_align(ring_img, lv.ALIGN_CENTER)
        lv.obj_clear_flag(ring_img, lv.OBJ_FLAG_CLICKABLE)
        lv.obj_clear_flag(ring_img, lv.OBJ_FLAG_SCROLLABLE)
        lv.obj_set_style_img_recolor(ring_img, lv.color_hex(0x646464), 0)
        lv.obj_set_style_img_recolor_opa(ring_img, 255, 0)
        lv.img_set_zoom(ring_img, ring_img_size)

        indent_size = int(shadow_size * 0.7)

        self._segmented_display = None
        self._seg_color = None
        self._seg_opa = None

        self._indent = indent = lv.obj_create(self)
        lv.obj_set_width(indent, indent_size)
        lv.obj_set_height(indent, indent_size)
        lv.obj_set_align(indent, lv.ALIGN_CENTER)
        lv.obj_clear_flag(indent, lv.OBJ_FLAG_SCROLLABLE)
        lv.obj_clear_flag(indent, lv.OBJ_FLAG_CLICKABLE)
        lv.obj_add_style(indent, _style, 0)

        lv.obj_set_style_radius(indent, int(indent_size / 2), 0)
        lv.obj_set_style_bg_color(indent, lv.color_hex(0x000000), 0)
        lv.obj_set_style_bg_opa(indent, 55, 0)

        self._indent_img = indent_img = lv.img_create(indent)
        lv.img_set_src(indent_img, ui_img_gradient)
        lv.obj_set_width(indent_img, lv.SIZE_CONTENT)  # NOQA
        lv.obj_set_height(indent_img, lv.SIZE_CONTENT)  # NOQA
        lv.obj_set_align(indent_img, lv.ALIGN_CENTER)
        lv.obj_clear_flag(indent_img, lv.OBJ_FLAG_SCROLLABLE)
        lv.obj_clear_flag(indent_img, lv.OBJ_FLAG_CLICKABLE)

        lv.img_set_angle(indent_img, 1800)
        indent_img_size = _remap(indent_size, 0, 151, 0, 194)
        lv.img_set_zoom(indent_img, indent_img_size)

        lv.obj_set_style_img_recolor(indent_img, lv.color_hex(0x646464), 0)
        lv.obj_set_style_img_recolor_opa(indent_img, 255, 0)

        knob_size = int(((shadow_size - indent_size) / 2) * 0.6)
        self._start_angle = 135
        self._stop_angle = 405

        self._knob_r = knob_r = (
                (((shadow_size - indent_size) / 2) + indent_size) / 2
        )

        self._knob_glow = knob_glow = lv.obj_create(self)

        lv.obj_set_width(knob_glow, knob_size)
        lv.obj_set_height(knob_glow, knob_size)
        lv.obj_set_align(knob_glow, lv.ALIGN_CENTER)

        knob_x, knob_y = _point_on_circle(self._start_angle, 0, 0, knob_r)

        lv.obj_set_x(knob_glow, knob_x)
        lv.obj_set_y(knob_glow, knob_y)
        lv.obj_clear_flag(knob_glow, lv.OBJ_FLAG_SCROLLABLE)
        lv.obj_add_style(knob_glow, _style, 0)

        lv.obj_set_style_radius(knob_glow, int(knob_size / 2), 0)

        lv.obj_set_style_bg_opa(knob_glow, 255, 0)
        lv.obj_set_style_shadow_color(knob_glow, lv.color_hex(0xFF0000), 0)
        lv.obj_set_style_shadow_opa(knob_glow, 255, 0)
        lv.obj_set_style_shadow_width(knob_glow, 5, 0)
        lv.obj_set_style_shadow_spread(knob_glow, 2, 0)

        self._knob_img = knob_img = lv.img_create(knob_glow)
        lv.img_set_src(knob_img, ui_img_gradient)
        lv.obj_set_width(knob_img, lv.SIZE_CONTENT)  # NOQA
        lv.obj_set_height(knob_img, lv.SIZE_CONTENT)  # NOQA
        lv.obj_set_x(knob_img, -1)
        lv.obj_set_y(knob_img, -1)
        lv.obj_set_align(knob_img, lv.ALIGN_CENTER)
        lv.obj_clear_flag(knob_img, lv.OBJ_FLAG_SCROLLABLE)
        lv.img_set_angle(knob_img, 1800)

        img_size = _remap(knob_size, 0, 16, 0, 21)
        lv.img_set_zoom(knob_img, img_size)
        lv.obj_set_style_img_recolor(knob_img, lv.color_hex(0x646464), 0)
        lv.obj_set_style_img_recolor_opa(knob_img, 255, 0)

        lv.obj_add_event(
            knob_glow,
            self.__drag_event_handler,
            lv.EVENT_PRESSING,
        )
        lv.obj_add_event(
            knob_img,
            self.__drag_event_handler,
            lv.EVENT_PRESSING,
        )
        self._captured = False

        disp = lv.disp_get_default()  # NOQA
        self._disp_width = lv.disp_get_hor_res(disp)
        self._disp_height = lv.disp_get_ver_res(disp)

        self._snap_angles = False
        self._synchronize_glow = True
        self._scale_ticks = None
        self._scale_major_ticks = None

        self._min_value = 0
        self._max_value = 100
        self._value = -1
        self._increment = 0.01
        self._ticks = []
        self._tick_pass = False

        self._fade_timer = None
        self._last_tick_num = 0
        self.set_scale_ticks(101, 3, 8)
        self.set_scale_major_ticks(5, 3, 13)

        grad_dsc = lv.grad_dsc_t()
        grad_dsc.stops_count = 2

        stop1 = lv.gradient_stop_t()
        stop2 = lv.gradient_stop_t()

        stop1.color = lv.color_hex(0x00FF00)
        stop2.color = lv.color_hex(0xFF0000)

        stop1.frac = int(255 * 0.7)
        stop2.frac = 255

        grad_dsc.stops = [stop1, stop2]

        self._tick_match_value = True
        self._tick_fade = True
        self.set_style_bg_grad(grad_dsc, lv.PART_TICKS)
        self.set_value(self._min_value)

    def __tick_fade(self, t):
        tick_num = int(
            remap(
                self._value,
                self._min_value,
                self._max_value,
                0,
                len(self._ticks)
                )
            )
        last_tick_num = self._last_tick_num

        if abs(tick_num - last_tick_num) <= 10:
            if self._tick_pass:
                self._tick_pass = False
                return
            else:
                self._tick_pass = True

        elif self._tick_pass:
            self._tick_pass = False

        if last_tick_num < tick_num:
            ticks = list(range(last_tick_num + 1, tick_num + 1, 1))
            last_tick_num += 1
        elif last_tick_num > tick_num:
            ticks = list(range(last_tick_num - 1, tick_num - 1, -1))
            last_tick_num -= 1
        else:
            lv.timer_del(t)
            self._fade_timer = None
            self._last_value = self._value
            return

        for i, tick in enumerate(self._ticks):
            if i in ticks:
                self._ticks[i].set_style_line_opa(255, 0)
            else:
                self._ticks[i].set_style_line_opa(0, 0)

        self._last_tick_num = last_tick_num

    def get_tick_fade(self):
        return self._tick_fade

    def set_tick_fade(self, value):
        self._tick_fade = value

    def get_tick_match_value(self):
        return self._tick_match_value

    def set_tick_match_value(self, value):
        self._tick_match_value = value
        self.__set_knob(self._value)

    def get_synchronize_glow(self):
        return self._synchronize_glow

    def set_synchronize_glow(self, value):
        self._synchronize_glow = value
        self.__set_knob(self._value)

    def get_min_value(self):
        return self._min_value

    def set_min_value(self, value):
        self._min_value = value
        self.__set_knob(self._value)

    def get_max_value(self):
        return self._max_value

    def set_max_value(self, value):
        self._max_value = value
        self.__set_knob(self._value)

    def set_range(self, min_value, max_value):
        self._min_value = min_value
        self._max_value = max_value
        self.__set_knob(self._value)

    def get_value(self):
        return self._value

    def set_value(self, value):
        remainder = value % self._increment

        if remainder < self._increment / 2:
            value -= remainder
        else:
            value += self._increment - remainder

        self._value = value
        self.__set_knob(value)

    def get_snap_angles(self):
        return self._snap_angles

    def set_snap_angles(self, value):
        self._snap_angles = value
        self.__set_knob(self._value)

    def get_increment(self):
        return self._increment

    def set_increment(self, value):
        self._increment = value
        self.__set_knob(self._value)

    def get_start_angle(self):
        return self._start_angle

    def set_start_angle(self, value):
        self._start_angle = value

    def get_stop_angle(self):
        return self._stop_angle

    def set_stop_angle(self, value):
        self._stop_angle = value

    def set_angles(self, start, stop):
        self._start_angle = start
        self._stop_angle = stop

    def set_segment_display(self, value):
        if value:
            if self._segmented_display is None:
                lv.obj_update_layout(self)

                width = lv.obj_get_width(self)
                height = lv.obj_get_height(self)

                size = min(height, width)

                self._segmented_display = seg_display = segmented_display(self)

                shadow_size = int(round(size * 0.7))
                indent_size = int(shadow_size * 0.7)
                seg_size = int(indent_size * 0.9)
                seg_display.set_size(seg_size)
                lv.obj_set_align(seg_display, lv.ALIGN_CENTER)
                lv.obj_clear_flag(seg_display, lv.OBJ_FLAG_SCROLLABLE)
                lv.obj_clear_flag(seg_display, lv.OBJ_FLAG_CLICKABLE)
                lv.obj_add_style(seg_display, _style, 0)
                seg_display.set_style_bg_color(lv.color_hex(0x000000), 0)
                lv.obj_set_style_bg_opa(seg_display, 255, 0)
                lv.obj_set_style_radius(seg_display, int(seg_size / 2), 0)

                if self._seg_color is not None:
                    seg_display.set_style_text_color(self._seg_color, 0)

                if self._seg_opa is not None:
                    seg_display.set_style_text_opa(self._seg_opa, 0)

                seg_display.set_max_value(int(self._max_value))
                seg_display.set_value(int(self._value))
                self.__set_knob(self._value)

        elif self._segmented_display is not None:
            lv.obj_del(self._segmented_display)
            self._segmented_display = None
            lv.obj_invalidate(self)
            self.__set_knob(self._value)

    def set_scale_ticks(self, count, line_width, length):
        if count == 0:
            self._scale_ticks = None
            for i, tick in enumerate(self._ticks):
                if tick is None or tick.is_major:
                    continue

                lv.timer_del(tick)
                self._ticks[i] = None
            return

        else:
            self._scale_ticks = (count, line_width, length)

        width = lv.obj_get_width(self)
        height = lv.obj_get_height(self)

        center_x = int(width / 2)
        center_y = int(height / 2)

        size = min(width, height)
        angle_range = self._stop_angle - self._start_angle
        angle_increment = angle_range / (count - 1)

        outer_radius = (size / 2) - 4
        inner_radius = outer_radius - length

        ticks = []

        for i in range(count):
            angle = self._start_angle + i * angle_increment

            x1, y1 = _point_on_circle(angle, center_x, center_y, outer_radius)

            if len(self._ticks) - 1 >= i:
                tick = self._ticks[i]
                if tick is None:
                    tick = _tick(self)
                    x2, y2 = _point_on_circle(
                        angle,
                        center_x,
                        center_y,
                        inner_radius
                    )

                    tick.set_style_line_width(line_width, 0)

                elif tick.is_major:
                    x2, y2 = _point_on_circle(
                        angle,
                        center_x,
                        center_y,
                        outer_radius - tick.length
                    )

                else:
                    x2, y2 = _point_on_circle(
                        angle,
                        center_x,
                        center_y,
                        inner_radius
                    )
                    tick.set_style_line_width(line_width, 0)
            else:
                tick = _tick(self)

                x2, y2 = _point_on_circle(
                    angle,
                    center_x,
                    center_y,
                    inner_radius
                )

                tick.set_style_line_width(line_width, 0)

            # lv.obj_set_style_line_rounded(tick, True, 0)
            tick.set_points(
                [lv.point_t(x=x1, y=y1), lv.point_t(x=x2, y=y2)],
                2
            )
            ticks.append(tick)

        for tick in self._ticks:
            if tick is None:
                continue

            if tick not in ticks:
                tick.delete()

        self._ticks.clear()
        self._ticks.extend(ticks[:])

    def set_scale_major_ticks(self, increment, line_width, length):
        width = lv.obj_get_width(self)
        height = lv.obj_get_height(self)

        center_x = int(width / 2.0)
        center_y = int(height / 2.0)

        if increment == 0:
            self._scale_major_ticks = None

            for i, tick in enumerate(self._ticks):
                if tick is None or not tick.is_major:
                    continue

                if self._scale_ticks is None:
                    lv.timer_del(tick)
                else:
                    line_width, length = self._scale_ticks[1:]
                    p1, p2 = tick.get_points()

                    x1 = p1.x
                    y1 = p1.y
                    x2 = p2.x
                    y2 = p2.y
                    outer_radius = _get_distance(x1, y1, center_x, center_y)
                    inner_radius = outer_radius - length
                    angle = _get_angle(x1, y1, x2, y2)
                    x2, y2 = _point_on_circle(
                        angle,
                        center_x,
                        center_y,
                        inner_radius
                    )
                    tick.set_style_line_width(line_width, 0)
                    tick.set_points(
                        [lv.point_t(x=x1, y=y1),
                         lv.point_t(x=x2, y=y2)],  # NOQA
                        2
                    )

            if self._scale_ticks is None:
                self._ticks.clear()

            return

        self._scale_major_ticks = (increment, line_width, length)

        size = min(width, height)

        outer_radius = (size / 2.0) - 4
        inner_radius = outer_radius - length

        angle_range = self._stop_angle - self._start_angle
        angle_increment = angle_range / (len(self._ticks) - 1)

        for i in range(0, len(self._ticks), increment):
            tick = self._ticks[i]

            angle = self._start_angle + i * angle_increment

            x1, y1 = _point_on_circle(angle, center_x, center_y, outer_radius)
            x2, y2 = _point_on_circle(angle, center_x, center_y, inner_radius)

            tick.set_style_line_width(line_width, 0)
            tick.set_points(
                [lv.point_t(x=x1, y=y1), lv.point_t(x=x2, y=y2)],
                2
            )
            tick.is_major = True

    def __set_knob(self, value):
        angle = remap(
            value,
            self._min_value,
            self._max_value,
            self._start_angle,
            self._stop_angle
            )

        x, y = _point_on_circle(angle, 0, 0, self._knob_r)

        tick_num = int(
            remap(value, self._min_value, self._max_value, 0, len(self._ticks))
            )

        if self._synchronize_glow:
            if tick_num < len(self._ticks):
                tick = self._ticks[tick_num]
                color = tick.get_style_line_color(0)
                lv.obj_set_style_shadow_color(self._knob_glow, color, 0)
                lv.obj_set_style_shadow_color(self._glow, color, 0)

                if self._segmented_display is not None:
                    self._segmented_display.set_style_text_color(color, 0)

        if self._tick_fade:
            if self._fade_timer is None:
                self._fade_timer = lv.timer_create(self.__tick_fade, 1)

        elif self._tick_match_value:
            for i, tick in enumerate(self._ticks):
                if i <= tick_num:
                    tick.set_style_line_opa(255, 0)
                else:
                    tick.set_style_line_opa(0, 0)

        lv.obj_set_x(self._knob_glow, x)
        lv.obj_set_y(self._knob_glow, y)

        if self._segmented_display is not None:
            self._segmented_display.set_value(int(value))

    def __drag_event_handler(self, _):
        indev = lv.indev_get_act()

        point = lv.point_t()
        lv.indev_get_point(indev, point)  # NOQA

        knob_x1 = lv.obj_get_x(self) + lv.obj_get_x(self._knob_glow)
        knob_y1 = lv.obj_get_y(self) + lv.obj_get_y(self._knob_glow)
        knob_x2 = knob_x1 + lv.obj_get_x(self._knob_glow)
        knob_y2 = knob_y1 + lv.obj_get_y(self._knob_glow)

        hit_offset = int(lv.obj_get_x(self._knob_glow) * 0.4)

        knob_x1 -= hit_offset
        knob_y1 -= hit_offset

        knob_x2 += hit_offset
        knob_y2 += hit_offset

        if not knob_x1 < point.x < knob_x2:
            return
        if not knob_y1 < point.y < knob_y2:
            return

        x = point.x - self._disp_width + int(round(self._disp_width / 2))
        y = point.y - self._disp_height + int(round(self._disp_height / 2))

        if self._max_value > self._min_value:
            value_range = self._max_value - self._min_value
            min_value = self._min_value
            max_value = self._max_value
        elif self._min_value > self._max_value:
            value_range = self._min_value - self._max_value
            min_value = self._max_value
            max_value = self._min_value
        else:
            raise RuntimeError('min and max values should not match')

        angle_range = self._stop_angle - self._start_angle
        angle = math.degrees(math.atan2(y, x))

        if angle < 0:
            angle += 360

        angle_offset = angle - self._start_angle
        angle_factor = angle_offset / angle_range

        if angle_factor < 0:
            angle += 360

            angle_offset = angle - self._start_angle
            angle_factor = angle_offset / angle_range

        value = (value_range * angle_factor) + min_value

        if value < min_value:
            return
        elif value > max_value:
            return
        else:
            remainder = value % self._increment

            if remainder < self._increment / 2:
                value -= remainder
            else:
                value += self._increment - remainder

        self._value = value

        self.__set_knob(self._value)
        # lv.event_send(self, lv.EVENT.VALUE_CHANGED, None)

    def __set_sizes(self):
        lv.obj_update_layout(self)

        width = lv.obj_get_width(self)
        height = lv.obj_get_height(self)
        size = min(width, height)

        shadow_size = int(size * 0.7)
        # img_size = _remap(size, 0, 250, 0, 256)
        ring_img_size = _remap(shadow_size, 0, 200, 0, 256)

        indent_size = int(shadow_size * 0.7)
        indent_img_size = _remap(indent_size, 0, 151, 0, 194)
        knob_size = int(((shadow_size - indent_size) / 2) * 0.6)
        knob_img_size = _remap(knob_size, 0, 16, 0, 21)

        self._knob_r = knob_r = (
                (((shadow_size - indent_size) / 2) + indent_size) / 2
        )
        knob_x, knob_y = _point_on_circle(self._start_angle, 0, 0, knob_r)

        lv.obj_set_x(self._knob_glow, knob_x)
        lv.obj_set_y(self._knob_glow, knob_y)

        lv.obj_set_width(self._shadow, shadow_size)
        lv.obj_set_height(self._shadow, shadow_size)
        lv.obj_set_style_radius(self._shadow, int(shadow_size / 2), 0)

        lv.obj_set_width(self._glow, shadow_size)
        lv.obj_set_height(self._glow, shadow_size)
        lv.obj_set_style_radius(self._glow, int(shadow_size / 2), 0)

        lv.obj_set_width(self._indent, indent_size)
        lv.obj_set_height(self._indent, indent_size)
        lv.obj_set_style_radius(self._indent, int(indent_size / 2), 0)

        if self._segmented_display is not None:
            seg_size = int(indent_size * 0.9)

            self._segmented_display.set_size(seg_size)
            lv.obj_set_style_radius(self._segmented_display, int(seg_size / 2), 0)
            self._segmented_display.set_max_value(self._max_value)

        lv.obj_set_width(self._knob_glow, knob_size)
        lv.obj_set_height(self._knob_glow, knob_size)
        lv.obj_set_style_radius(self._knob_glow, int(knob_size / 2), 0)

        lv.img_set_zoom(self._ring_img, ring_img_size)
        lv.img_set_zoom(self._indent_img, indent_img_size)
        lv.img_set_zoom(self._knob_img, knob_img_size)

    def set_style_bg_color(self, color, selector):
        if selector | lv.PART_KNOB == selector:
            selector ^= lv.PART_KNOB

            if self._segmented_display is not None:
                lv.obj_set_style_bg_color(self._indent, color, selector)

            lv.obj_set_style_bg_color(self._glow, color, selector)

        elif selector | lv.PART_TICKS == selector:
            selector ^= lv.PART_TICKS

            for tick in self._ticks:
                tick.set_style_line_color(color, selector)

            # self._ticks_img.set_style_img_recolor(color, selector)

        elif selector | LV_PART_KNOB_CENTER == selector:
            selector ^= LV_PART_KNOB_CENTER

            if self._segmented_display is not None:
                self._segmented_display.set_style_bg_color(color, selector)
            else:
                lv.obj_set_style_bg_color(self._indent, color, selector)

        elif selector | LV_PART_KNOB_RING == selector:
            selector ^= LV_PART_KNOB_RING
            lv.obj_set_style_bg_color(self._glow, color, selector)

        elif selector | lv.PART_INDICATOR == selector:
            selector ^= lv.PART_INDICATOR
            lv.obj_set_style_bg_color(self._knob_glow, color, selector)

        else:
            lv.obj_set_style_bg_color(self, color, selector)

    def set_style_bg_opa(self, opa, selector):
        if selector | lv.PART_KNOB == selector:
            selector ^= lv.PART_KNOB

            if self._segmented_display is not None:
                lv.obj_set_style_bg_opa(self._indent, opa, selector)

            lv.obj_set_style_bg_opa(self._glow, opa, selector)

        elif selector | lv.PART_TICKS == selector:
            selector ^= lv.PART_TICKS

            for tick in self._ticks:
                tick.set_style_line_opa(opa, selector)

            # self._ticks_img.set_style_img_recolor_opa(opa, selector)

        elif selector | LV_PART_KNOB_CENTER == selector:
            selector ^= LV_PART_KNOB_CENTER
            if self._segmented_display is not None:
                self._segmented_display.set_style_bg_opa(opa, selector)
            else:
                lv.obj_set_style_bg_opa(self._indent, opa, selector)

        elif selector | LV_PART_KNOB_RING == selector:
            selector ^= LV_PART_KNOB_RING
            lv.obj_set_style_bg_opa(self._glow, opa, selector)

        elif selector | lv.PART_INDICATOR == selector:
            selector ^= lv.PART_INDICATOR
            lv.obj_set_style_bg_opa(self._knob_glow, opa, selector)

        else:
            lv.obj_set_style_bg_opa(self, opa, selector)

    def set_style_bg_grad_color(self, color, selector):
        if selector | lv.PART_KNOB == selector:
            selector ^= lv.PART_KNOB
            if self._segmented_display is not None:
                lv.obj_set_style_img_recolor(self._indent_img, color, selector)

            lv.obj_set_style_img_recolor(self._ring_img, color, selector)

        elif selector | lv.PART_TICKS == selector:
            raise NotImplementedError

        elif selector | LV_PART_KNOB_CENTER == selector:
            selector ^= LV_PART_KNOB_CENTER
            if self._segmented_display is not None:
                self._segmented_display.set_style_bg_grad_color(color, selector)
            else:
                lv.obj_set_style_img_recolor(self._indent_img, color, selector)

        elif selector | LV_PART_KNOB_RING == selector:
            selector ^= LV_PART_KNOB_RING
            lv.obj_set_style_img_recolor(self._ring_img, color, selector)

        elif selector | lv.PART_INDICATOR == selector:
            selector ^= lv.PART_INDICATOR
            lv.obj_set_style_img_recolor(self._knob_img, color, selector)

        else:
            lv.obj_set_style_bg_grad_color(self, color, selector)

    def set_style_bg_main_stop(self, *args, **kwargs):
        raise NotImplementedError

    def set_style_bg_grad_stop(self, *args, **kwargs):
        raise NotImplementedError

    def set_style_bg_grad(self, grad_desc, selector):
        gradient = []

        last_color = None
        stops = grad_desc.stops
        time.sleep(1)
        for i in range(grad_desc.stops_count):
            stop = stops[i]
            color = stop.color
            color = (color.red, color.green, color.blue)

            if last_color is not None:
                frac = stop.frac / 255
                num_steps = int(len(self._ticks) * frac)
                gradient.extend(
                    list(
                        lv.color_hex(color)
                        for color in
                        _build_gradient(last_color, color, num_steps)
                    )
                )

            last_color = color

        if selector | lv.PART_TICKS == selector:
            selector ^= lv.PART_TICKS
            for i, tick in enumerate(self._ticks):
                tick.set_style_line_color(gradient[i], selector)
        else:
            raise NotImplementedError

    def set_style_bg_dither_mode(self, *args, **kwargs):
        raise NotImplementedError

    def set_style_bg_grad_dir(self, value, selector):
        if selector | lv.PART_KNOB == selector:
            selector ^= lv.PART_KNOB
            lv.img_set_angle(self._indent_img, value + 1800)
            lv.img_set_angle(self._ring_img, value)

        elif selector | lv.PART_TICKS == selector:
            raise NotImplementedError

        elif selector | LV_PART_KNOB_CENTER == selector:
            selector ^= LV_PART_KNOB_CENTER
            lv.img_set_angle(self._indent_img, value)

        elif selector | LV_PART_KNOB_RING == selector:
            selector ^= LV_PART_KNOB_RING
            lv.img_set_angle(self._ring_img, value)

        elif selector | lv.PART_INDICATOR == selector:
            selector ^= lv.PART_INDICATOR
            lv.img_set_angle(self._knob_img, value)

    def set_style_outline_color(self, color, selector):
        if selector | lv.PART_KNOB == selector:
            selector ^= lv.PART_KNOB
            if self._segmented_display is not None:
                lv.obj_set_style_outline_color(self._indent, color, selector)

            lv.obj_set_style_outline_color(self._glow, color, selector)

        elif selector | lv.PART_TICKS == selector:
            selector ^= lv.PART_TICKS
            for tick in self._ticks:
                tick.set_style_outline_color(color, selector)

            # self._ticks_img.set_style_img_recolor(color, selector)

        elif selector | LV_PART_KNOB_CENTER == selector:
            selector ^= LV_PART_KNOB_CENTER
            if self._segmented_display is not None:
                self._segmented_display.set_style_outline_color(color, selector)
            else:
                lv.obj_set_style_outline_color(self._indent, color, selector)

        elif selector | LV_PART_KNOB_RING == selector:
            selector ^= LV_PART_KNOB_RING
            lv.obj_set_style_outline_color(self._glow, color, selector)

        elif selector | lv.PART_INDICATOR == selector:
            selector ^= lv.PART_INDICATOR
            lv.obj_set_style_outline_color(self._knob_glow, color, selector)

        else:
            lv.obj_set_style_outline_color(self._glow, color, selector)

    def set_style_outline_width(self, value, selector):
        if selector | lv.PART_KNOB == selector:
            selector ^= lv.PART_KNOB
            if self._segmented_display is not None:
                lv.obj_set_style_outline_width(self._indent, value, selector)

            lv.obj_set_style_outline_width(self._glow, value, selector)

        elif selector | lv.PART_TICKS == selector:
            selector ^= lv.PART_TICKS

            for tick in self._ticks:
                tick.set_style_outline_width(value, selector)

        elif selector | LV_PART_KNOB_CENTER == selector:
            selector ^= LV_PART_KNOB_CENTER

            if self._segmented_display is not None:
                self._segmented_display.set_style_outline_width(value, selector)
            else:
                lv.obj_set_style_outline_width(self._indent, value, selector)

        elif selector | LV_PART_KNOB_RING == selector:
            selector ^= LV_PART_KNOB_RING
            lv.obj_set_style_outline_width(self._glow, value, selector)

        elif selector | lv.PART_INDICATOR == selector:
            selector ^= lv.PART_INDICATOR
            lv.obj_set_style_outline_width(self._knob_glow, value, selector)

        else:
            lv.obj_set_style_outline_width(self._glow, value, selector)

    def set_style_outline_opa(self, opa, selector):
        if selector | lv.PART_KNOB == selector:
            selector ^= lv.PART_KNOB
            if self._segmented_display is not None:
                lv.obj_set_style_outline_opa(self._indent, opa, selector)

            lv.obj_set_style_outline_opa(self._glow, opa, selector)

        elif selector | lv.PART_TICKS == selector:
            selector ^= lv.PART_TICKS

            for tick in self._ticks:
                tick.set_style_outline_opa(opa, selector)

            # self._ticks_img.set_style_img_recolor_opa(opa, selector)

        elif selector | LV_PART_KNOB_CENTER == selector:
            selector ^= LV_PART_KNOB_CENTER
            if self._segmented_display is not None:
                self._segmented_display.set_style_outline_opa(opa, selector)
            else:
                lv.obj_set_style_outline_opa(self._indent, opa, selector)

        elif selector | LV_PART_KNOB_RING == selector:
            selector ^= LV_PART_KNOB_RING
            lv.obj_set_style_outline_opa(self._glow, opa, selector)

        elif selector | lv.PART_INDICATOR == selector:
            selector ^= lv.PART_INDICATOR
            lv.obj_set_style_outline_opa(self._knob_glow, opa, selector)

        else:
            lv.obj_set_style_outline_opa(self._glow, opa, selector)

    def set_style_border_color(self, color, selector):
        if selector | lv.PART_KNOB == selector:
            selector ^= lv.PART_KNOB
            if self._segmented_display is not None:
                lv.obj_set_style_border_color(self._indent, color, selector)

            lv.obj_set_style_border_color(self._glow, color, selector)

        elif selector | lv.PART_TICKS == selector:
            selector ^= lv.PART_TICKS
            for tick in self._ticks:
                tick.set_style_border_color(color, selector)

            # self._ticks_img.set_style_img_recolor(color, selector)

        elif selector | LV_PART_KNOB_CENTER == selector:
            selector ^= LV_PART_KNOB_CENTER
            if self._segmented_display is not None:
                self._segmented_display.set_style_border_color(color, selector)
            else:
                lv.obj_set_style_border_color(self._indent, color, selector)

        elif selector | LV_PART_KNOB_RING == selector:
            selector ^= LV_PART_KNOB_RING
            lv.obj_set_style_border_color(self._glow, color, selector)

        elif selector | lv.PART_INDICATOR == selector:
            selector ^= lv.PART_INDICATOR
            lv.obj_set_style_border_color(self._knob_glow, color, selector)

        else:
            lv.obj_set_style_border_color(self._glow, color, selector)

    def set_style_border_opa(self, opa, selector):
        if selector | lv.PART_KNOB == selector:
            selector ^= lv.PART_KNOB
            if self._segmented_display is not None:
                lv.obj_set_style_border_opa(self._indent, opa, selector)

            lv.obj_set_style_border_opa(self._glow, opa, selector)

        elif selector | lv.PART_TICKS == selector:
            selector ^= lv.PART_TICKS

            for tick in self._ticks:
                tick.set_style_border_opa(opa, selector)

            # self._ticks_img.set_style_img_recolor_opa(opa, selector)

        elif selector | LV_PART_KNOB_CENTER == selector:
            selector ^= LV_PART_KNOB_CENTER
            if self._segmented_display is not None:
                self._segmented_display.set_style_border_opa(opa, selector)
            else:
                lv.obj_set_style_border_opa(self._indent, opa, selector)

        elif selector | LV_PART_KNOB_RING == selector:
            selector ^= LV_PART_KNOB_RING
            lv.obj_set_style_border_opa(self._glow, opa, selector)

        elif selector | lv.PART_INDICATOR == selector:
            selector ^= lv.PART_INDICATOR
            lv.obj_set_style_border_opa(self._knob_glow, opa, selector)

        else:
            lv.obj_set_style_border_opa(self._glow, opa, selector)

    def set_style_border_width(self, value, selector):
        if selector | lv.PART_KNOB == selector:
            selector ^= lv.PART_KNOB
            if self._segmented_display is not None:
                lv.obj_set_style_border_width(self._indent, value, selector)

            lv.obj_set_style_border_width(self._glow, value, selector)

        elif selector | lv.PART_TICKS == selector:
            selector ^= lv.PART_TICKS

            for tick in self._ticks:
                tick.set_style_border_width(value, selector)

        elif selector | LV_PART_KNOB_CENTER == selector:
            selector ^= LV_PART_KNOB_CENTER
            if self._segmented_display is not None:
                self._segmented_display.set_style_border_width(value, selector)
            else:
                lv.obj_set_style_border_width(self._indent, value, selector)

        elif selector | LV_PART_KNOB_RING == selector:
            selector ^= LV_PART_KNOB_RING
            lv.obj_set_style_border_width(self._glow, value, selector)

        elif selector | lv.PART_INDICATOR == selector:
            selector ^= lv.PART_INDICATOR
            lv.obj_set_style_border_width(self._knob_glow, value, selector)

        else:
            lv.obj_set_style_border_width(self._glow, value, selector)

    def set_style_shadow_width(self, value, selector):
        if selector | lv.PART_KNOB == selector:
            selector ^= lv.PART_KNOB
            lv.obj_set_style_shadow_width(self._glow, value, selector)

        elif selector | lv.PART_TICKS == selector:
            selector ^= lv.PART_TICKS

            for tick in self._ticks:
                tick.set_style_shadow_width(value, selector)

        elif selector | LV_PART_KNOB_CENTER == selector:
            raise NotImplementedError

        elif selector | LV_PART_KNOB_RING == selector:
            selector ^= LV_PART_KNOB_RING
            lv.obj_set_style_shadow_width(self._glow, value, selector)

        elif selector | lv.PART_INDICATOR == selector:
            selector ^= lv.PART_INDICATOR
            lv.obj_set_style_shadow_width(self._knob_glow, value, selector)

        else:
            lv.obj_set_style_shadow_width(self._shadow, value, selector)

    def set_style_shadow_ofs_x(self, value, selector):
        if selector | lv.PART_KNOB == selector:
            selector ^= lv.PART_KNOB
            lv.obj_set_style_shadow_ofs_x(self._glow, value, selector)

        elif selector | lv.PART_TICKS == selector:
            selector ^= lv.PART_TICKS

            for tick in self._ticks:
                tick.set_style_shadow_ofs_x(value, selector)

        elif selector | LV_PART_KNOB_CENTER == selector:
            raise NotImplementedError

        elif selector | LV_PART_KNOB_RING == selector:
            selector ^= LV_PART_KNOB_RING
            lv.obj_set_style_shadow_ofs_x(self._glow, value, selector)

        elif selector | lv.PART_INDICATOR == selector:
            selector ^= lv.PART_INDICATOR
            lv.obj_set_style_shadow_ofs_x(self._knob_glow, value, selector)

        else:
            lv.obj_set_style_shadow_ofs_x(self._shadow, value, selector)

    def set_style_shadow_ofs_y(self, value, selector):
        if selector | lv.PART_KNOB == selector:
            selector ^= lv.PART_KNOB
            lv.obj_set_style_shadow_ofs_y(self._glow, value, selector)

        elif selector | lv.PART_TICKS == selector:
            selector ^= lv.PART_TICKS

            for tick in self._ticks:
                tick.set_style_shadow_ofs_y(value, selector)

        elif selector | LV_PART_KNOB_CENTER == selector:
            raise NotImplementedError

        elif selector | LV_PART_KNOB_RING == selector:
            selector ^= LV_PART_KNOB_RING
            lv.obj_set_style_shadow_ofs_y(self._glow, value, selector)

        elif selector | lv.PART_INDICATOR == selector:
            selector ^= lv.PART_INDICATOR
            lv.obj_set_style_shadow_ofs_y(self._knob_glow, value, selector)

        else:
            lv.obj_set_style_shadow_ofs_y(self._shadow, value, selector)

    def set_style_shadow_spread(self, value, selector):
        if selector | lv.PART_KNOB == selector:
            selector ^= lv.PART_KNOB
            lv.obj_set_style_shadow_spread(self._glow, value, selector)

        elif selector | lv.PART_TICKS == selector:
            selector ^= lv.PART_TICKS

            for tick in self._ticks:
                tick.set_style_shadow_spread(value, selector)

        elif selector | LV_PART_KNOB_CENTER == selector:
            raise NotImplementedError

        elif selector | LV_PART_KNOB_RING == selector:
            selector ^= LV_PART_KNOB_RING
            lv.obj_set_style_shadow_spread(self._glow, value, selector)

        elif selector | lv.PART_INDICATOR == selector:
            selector ^= lv.PART_INDICATOR
            lv.obj_set_style_shadow_spread(self._knob_glow, value, selector)

        else:
            lv.obj_set_style_shadow_spread(self._shadow, value, selector)

    def set_style_shadow_color(self, color, selector):
        if selector | lv.PART_KNOB == selector:
            selector ^= lv.PART_KNOB
            lv.obj_set_style_shadow_color(self._glow, color, selector)

        elif selector | lv.PART_TICKS == selector:
            selector ^= lv.PART_TICKS

            for tick in self._ticks:
                tick.set_style_shadow_color(color, selector)

        elif selector | LV_PART_KNOB_CENTER == selector:
            raise NotImplementedError

        elif selector | LV_PART_KNOB_RING == selector:
            selector ^= LV_PART_KNOB_RING
            lv.obj_set_style_shadow_color(self._glow, color, selector)

        elif selector | lv.PART_INDICATOR == selector:
            selector ^= lv.PART_INDICATOR
            lv.obj_set_style_shadow_color(self._knob_glow, color, selector)

        else:
            lv.obj_set_style_shadow_color(self._shadow, color, selector)

    def set_style_shadow_opa(self, opa, selector):
        if selector | lv.PART_KNOB == selector:
            selector ^= lv.PART_KNOB
            lv.obj_set_style_shadow_opa(self._glow, opa, selector)

        elif selector | lv.PART_TICKS == selector:
            selector ^= lv.PART_TICKS

            for tick in self._ticks:
                tick.set_style_shadow_opa(opa, selector)

        elif selector | LV_PART_KNOB_CENTER == selector:
            raise NotImplementedError

        elif selector | LV_PART_KNOB_RING == selector:
            selector ^= LV_PART_KNOB_RING
            lv.obj_set_style_shadow_opa(self._glow, opa, selector)

        elif selector | lv.PART_INDICATOR == selector:
            selector ^= lv.PART_INDICATOR
            lv.obj_set_style_shadow_opa(self._knob_glow, opa, selector)

        else:
            lv.obj_set_style_shadow_opa(self._shadow, opa, selector)

    def set_style_text_color(self, color, selector):
        self._seg_color = color
        if self._segmented_display is not None:
            self._segmented_display.set_style_text_color(color, selector)

    def set_style_text_opa(self, opa, selector):
        self._seg_opa = opa
        if self._segmented_display is not None:
            self._segmented_display.set_style_text_opa(opa, selector)

    def set_style_width(self, value, selector):
        raise NotImplementedError

    def set_style_height(self, value, selector):
        raise NotImplementedError

    def set_width(self, value):
        lv.obj_update_layout(self)
        self.set_size(value, lv.obj_get_height(self))

    def set_height(self, value):
        lv.obj_update_layout(self)
        self.set_size(lv.obj_get_height(self), value)

    def set_size(self, width, height):
        lv.obj_update_layout(self)

        old_width = lv.obj_get_width(self)
        old_height = lv.obj_get_height(self)
        old_diameter = min(old_width, old_height)

        lv.obj_set_size(self, width, height)
        self.__set_sizes()

        new_diameter = min(width, height)

        if self._scale_ticks is not None:
            count, line_width, length = self._scale_ticks

            width_factor = line_width / old_diameter
            length_factor = length / old_diameter

            self.set_scale_ticks(
                count,
                max(1, int(new_diameter * width_factor)),
                max(1, int(new_diameter * length_factor))
            )

        if self._scale_major_ticks is not None:
            increment, line_width, length = self._scale_major_ticks

            width_factor = line_width / old_diameter
            length_factor = length / old_diameter

            self.set_scale_major_ticks(
                increment,
                max(1, int(new_diameter * width_factor)),
                max(1, int(new_diameter * length_factor))
            )


screen = lv.scr_act()
lv.obj_set_style_bg_color(screen, lv.color_hex(0x2D2D2D), 0)
lv.obj_set_style_bg_opa(screen, 255, 0)
lv.obj_set_scrollbar_mode(screen, lv.SCROLLBAR_MODE_OFF)

volume = knob_ctrl(screen)
lv.obj_center(volume)
volume.set_segment_display(True)
volume.set_size(550, 550)

while True:
    time.sleep(0.001)
    lv.task_handler()
