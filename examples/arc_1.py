import os
import sys

base_path = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(base_path, '..', 'build')))

import lvgl as lv

import time

lv.init()
disp = lv.sdl_window_create(480, 320)
group = lv.group_create()
lv.group_set_default(group)
mouse = lv.sdl_mouse_create()
keyboard = lv.sdl_keyboard_create()
lv.indev_set_group(keyboard, group)


style = lv.style_t()
lv.style_init(style)

lv.style_set_arc_color(style, lv.palette_main(lv.PALETTE_RED))
lv.style_set_arc_width(style, 4)

# Create an object with the new style
obj = lv.arc_create(lv.scr_act())
lv.obj_add_style(obj, style, 0)
lv.obj_center(obj)

start = time.time()

while True:
    stop = time.time()
    diff = int((stop * 1000) - (start * 1000))
    if diff >= 1:
        start = stop
        lv.tick_inc(diff)
        lv.task_handler()
