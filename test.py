import os
import sys

base_path = os.path.dirname(__file__)
lvgl_path = os.path.join(base_path, 'lvgl')

sys.path.insert(0, lvgl_path)
print('starting')

print('importing lvgl')
import lvgl

print('lv_init')
lvgl.lib.lv_init()
print('done')

print('lv_sdl_window_create')
disp = lvgl.lib.lv_sdl_window_create(480, 320)
print('disp:', disp)

print('lv_group_create')
group = lvgl.lib.lv_group_create()
print('group:', group)

print('v_group_set_default')
lvgl.lib.lv_group_set_default(group)

print('lv_sdl_mouse_create')
mouse = lvgl.lib.lv_sdl_mouse_create()
print('mouse:', mouse)

print('lv_sdl_keyboard_create')
keyboard = lvgl.lib.lv_sdl_keyboard_create()
print('keyboard:', keyboard)

print('lv_indev_set_group')
lvgl.lib.lv_indev_set_group(keyboard, group)
print('lv_indev_set_group')


screen = lvgl.lib.lv_scr_act()

btn = lvgl.lib.lv_btn_create(screen)
lvgl.lib.lv_obj_set_pos(btn, 10, 10)
lvgl.lib.lv_obj_set_size(btn, 120, 50)

label = lvgl.lib.lv_label_create(btn)
lvgl.lib.lv_label_set_text(label, b"Button")
lvgl.lib.lv_obj_center(label)


import time

start = time.time()


while True:
    stop = time.time()
    diff = int((stop * 1000) - (start * 1000))
    if diff >= 1:
        start = stop
        lvgl.lib.lv_tick_inc(diff)
        lvgl.lib.lv_task_handler()
