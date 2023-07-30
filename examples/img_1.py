import os
import sys

base_path = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(base_path, '..')))

import lvgl as lv

import time

lv.init()
disp = lv.sdl_window_create(800, 600)
group = lv.group_create()
lv.group_set_default(group)
mouse = lv.sdl_mouse_create()
keyboard = lv.sdl_keyboard_create()
lv.indev_set_group(keyboard, group)


#
# Using the Image style properties
#
# style = lv.style_t()
# lv.style_init(style)
# Set a background color and a radius
# lv.style_set_radius(style, 5)
# lv.style_set_bg_opa(style, lv.OPA_COVER)
# lv.style_set_bg_color(style, lv.palette_lighten(lv.PALETTE_GREY, 3))
# lv.style_set_border_width(style, 2)
# lv.style_set_border_color(style, lv.palette_main(lv.PALETTE_BLUE))

# lv.style_set_img_recolor(style, lv.palette_main(lv.PALETTE_BLUE))
# lv.style_set_img_recolor_opa(style, lv.OPA_50)
# lv.style_set_transform_angle(style, 300)

# Create an object with the new style
obj = lv.img_create(lv.scr_act())

with open(r"C:\Users\drsch\Downloads\768px-Sign-check-icon.png", 'rb') as f:
    img_data = f.read()
# print(img_data)

import ctypes


img_dsc = lv.img_dsc_t()
img_dsc.data = img_data
img_dsc.data_size = len(img_data)

lv.img_set_src(obj, img_dsc)
lv.obj_center(obj)
lv.obj_set_size(obj, 400, 400)
lv.obj_set_style_border_color(obj, lv.color_hex(0xFF0000), 0)
lv.obj_set_style_border_width(obj, 5, 0)
start = time.time()

while True:
    time.sleep(0.001)
    stop = time.time()
    diff = int((stop * 1000) - (start * 1000))
    start = stop
    lv.tick_inc(diff)
    lv.task_handler()
