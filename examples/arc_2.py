
import os
import sys

base_path = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(base_path, '..')))

import lvgl as lv

import time


lv.init()
disp = lv.sdl_window_create(400, 400)
group = lv.group_create()
lv.group_set_default(group)
mouse = lv.sdl_mouse_create()
keyboard = lv.sdl_keyboard_create()
lv.indev_set_group(keyboard, group)

def value_changed_event_cb(e, label):

    txt = "{:d}%".format(lv.arc_get_value(arc))
    lv.label_set_text(label, txt)

    # Rotate the label to the current position of the arc
    lv.arc_rotate_obj_to_angle(arc, label, 25)


label = lv.label_create(lv.scr_act())
lv.obj_set_style_text_color(label, lv.color_hex(0x00FF00), 0)
# Create an Arc
arc = lv.arc_create(lv.scr_act())
lv.obj_set_style_arc_color(arc, lv.color_hex(0xFF0000), lv.PART_INDICATOR)
lv.obj_set_size(arc, 200, 200)
lv.obj_set_style_arc_width(arc, 20, lv.PART_INDICATOR)
lv.obj_set_style_arc_width(arc, 20, 0)

lv.arc_set_rotation(arc, 135)
lv.arc_set_bg_angles(arc, 0, 270)
lv.arc_set_value(arc, 10)
lv.obj_center(arc)
lv.obj_add_event(arc, lambda e: value_changed_event_cb(e, label), lv.EVENT_VALUE_CHANGED, None)

# Manually update the label for the first time
lv.obj_send_event(arc, lv.EVENT_VALUE_CHANGED, None)


start = time.time()

val = 10
inc = 1

while True:
    stop = time.time()
    diff = (stop * 1000) - (start * 1000)
    while diff < 1.0:
        stop = time.time()
        diff = (stop * 1000) - (start * 1000)

    val += inc
    if val in (0, 100):
        inc = -inc

    lv.arc_set_value(arc, val)
    lv.obj_send_event(arc, lv.EVENT_VALUE_CHANGED, None)

    stop = time.time()
    diff = int((stop * 1000) - (start * 1000))
    start = stop
    lv.tick_inc(diff)
    lv.task_handler()
