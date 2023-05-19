try:
    import lvgl as lv
except ImportError:
    import os
    import sys

    base_path = os.path.dirname(__file__)
    sys.path.insert(0, os.path.abspath(os.path.join(base_path, '..', 'build')))

    import lvgl as lv

import time


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

disp = lv.sdl_window_create(480, 320)
group = lv.group_create()
lv.group_set_default(group)
mouse = lv.sdl_mouse_create()
keyboard = lv.sdl_keyboard_create()
lv.indev_set_group(keyboard, group)

lv.demo_benchmark(1)

#
#
# def anim_x(a, v):
#     lv.obj_set_x(obj, v)
#
#
# def anim_size(a, v):
#     lv.obj_set_size(obj, v, v)
#
#
# #
# # Create a playback animation
# #
# obj = lv.obj_create(lv.scr_act())
# lv.obj_set_style_bg_color(obj, lv.palette_main(lv.PALETTE_RED), 0)
# lv.obj_set_style_radius(obj, lv.RADIUS_CIRCLE, 0)
#
# lv.obj_align(obj, lv.ALIGN_LEFT_MID, 10, 0)
#
# a1 = lv.anim_t()
# lv.anim_init(a1)
# lv.anim_set_var(a1, obj)
# lv.anim_set_values(a1, 10, 50)
# lv.anim_set_time(a1, 1000)
# lv.anim_set_playback_delay(a1, 100)
# lv.anim_set_playback_time(a1, 300)
# lv.anim_set_repeat_delay(a1, 500)
# lv.anim_set_repeat_count(a1, lv.ANIM_REPEAT_INFINITE)
# lv.anim_set_path_cb(a1, lv.anim_path_ease_in_out)
# lv.anim_set_custom_exec_cb(a1, anim_size)
# lv.anim_start(a1)
#
# a2 = lv.anim_t()
# lv.anim_init(a2)
# lv.anim_set_var(a2, obj)
# lv.anim_set_values(a2, 10, 240)
# lv.anim_set_time(a2, 1000)
# lv.anim_set_playback_delay(a2, 100)
# lv.anim_set_playback_time(a2, 300)
# lv.anim_set_repeat_delay(a2, 500)
# lv.anim_set_repeat_count(a2, lv.ANIM_REPEAT_INFINITE)
# lv.anim_set_path_cb(a2, lv.anim_path_ease_in_out)
# lv.anim_set_custom_exec_cb(a2, anim_x)
# lv.anim_start(a2)

while True:
    time.sleep(0.001)
    lv.task_handler()
