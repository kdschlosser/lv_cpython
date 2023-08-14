import os
import sys

base_path = os.path.dirname(__file__)
lib_path = os.path.abspath(os.path.join(base_path, '..'))
sys.path.insert(0, lib_path)

import lvgl as lv
import time


lv.init()
disp = lv.sdl_window_create(1920, 1080)
group = lv.group_create()
lv.group_set_default(group)
mouse = lv.sdl_mouse_create()
keyboard = lv.sdl_keyboard_create()
lv.indev_set_group(keyboard, group)

lv.demo_benchmark(lv.DEMO_BENCHMARK_MODE_RENDER_AND_DRIVER)

while True:
    time.sleep(0.001)
    lv.tick_inc(1)
    lv.task_handler()
