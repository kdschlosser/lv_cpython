import os
import sys

base_path = os.path.dirname(__file__)
lib_path = os.path.abspath(os.path.join(base_path, '..'))
sys.path.insert(0, lib_path)

import lvgl as lv
import time


lv.init()
disp = lv.sdl_window_create(lv.coord_t(480), 320)
group = lv.group_create()
lv.group_set_default(group)
mouse = lv.sdl_mouse_create()
keyboard = lv.sdl_keyboard_create()
lv.indev_set_group(keyboard, group)


def slider_event_cb(e):
    slider = lv.event_get_target_obj(e)

    # Refresh the text
    lv.label_set_text(label, str(lv.slider_get_value(slider)))


# Create a slider in the center of the display
slider = lv.slider_create(lv.scr_act())
lv.obj_set_width(slider, 200)
lv.obj_center(slider)
lv.obj_add_event(slider, slider_event_cb, lv.EVENT_VALUE_CHANGED, None)

# Create a label above the slider
label = lv.label_create(lv.scr_act())
lv.label_set_text(label, "0")
lv.obj_align_to(label, slider, lv.ALIGN_OUT_TOP_MID, 0, -15)


start = time.time()

val = 0
inc = 1

lv.slider_set_value(slider, val, lv.ANIM_ON)
while True:
    stop = time.time()
    diff = (stop * 1000) - (start * 1000)
    while diff < 1.0:
        stop = time.time()
        diff = (stop * 1000) - (start * 1000)

    val += inc
    if val in (0, 100):
        inc = -inc

    lv.slider_set_value(slider, val, lv.ANIM_ON)

    stop = time.time()
    diff = int((stop * 1000) - (start * 1000))
    start = stop
    lv.tick_inc(diff)
    lv.task_handler()
