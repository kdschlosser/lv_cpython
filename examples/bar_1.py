try:
    import lvgl as lv
except ImportError:
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


def set_temp(bar, temp):
    lv.bar_set_value(bar, temp, lv.ANIM_ON)

#
# A temperature meter example
#

style_indic = lv.style_t()

lv.style_init(style_indic)
lv.style_set_bg_opa(style_indic, lv.OPA_COVER)
lv.style_set_bg_color(style_indic, lv.palette_main(lv.PALETTE_RED))
lv.style_set_bg_grad_color(style_indic, lv.palette_main(lv.PALETTE_BLUE))
lv.style_set_bg_grad_dir(style_indic, lv.GRAD_DIR_VER)

bar = lv.bar_create(lv.scr_act())
lv.obj_add_style(bar, style_indic, lv.PART_INDICATOR)
lv.obj_set_size(bar, 20, 200)
lv.obj_center(bar)
lv.bar_set_range(bar, -20, 40)

a = lv.anim_t()
lv.anim_init(a)
lv.anim_set_time(a, 3000)
lv.anim_set_playback_time(a, 3000)
lv.anim_set_var(a, bar)
lv.anim_set_values(a, -20, 40)
lv.anim_set_repeat_count(a, lv.ANIM_REPEAT_INFINITE)
lv.anim_set_custom_exec_cb(a, lv.anim_custom_exec_cb_t(lambda a, val: set_temp(bar,val)))
lv.anim_start(a)


start = time.time()

while True:
    stop = time.time()
    diff = int((stop * 1000) - (start * 1000))
    if diff >= 1:
        start = stop
        lv.tick_inc(diff)
        lv.task_handler()
