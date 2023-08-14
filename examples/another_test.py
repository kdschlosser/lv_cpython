import os
import sys

base_path = os.path.dirname(__file__)
lib_path = os.path.abspath(os.path.join(base_path, '..'))
sys.path.insert(0, lib_path)

import lvgl as lv

import display_driver


ui_Screen1 = lv.obj_create(None)
lv.obj_clear_flag(ui_Screen1, lv.OBJ_FLAG_SCROLLABLE)
lv.obj_set_style_bg_color(ui_Screen1, lv.color_hex(0x000000), 0)

ui_Arc1 = lv.arc_create(ui_Screen1)
lv.obj_set_width(ui_Arc1, 150)
lv.obj_set_height(ui_Arc1, 150)
lv.obj_set_align(ui_Arc1, lv.ALIGN_CENTER)
lv.arc_set_value(ui_Arc1, 0)
lv.arc_set_bg_angles(ui_Arc1, 0, 360)
# ui_Arc1.set_mode(ui_Arc1.MODE.SYMMETRICAL)
lv.obj_set_style_arc_color(
    ui_Arc1,
    lv.color_hex(0xFF00FF),
    lv.PART_INDICATOR | lv.STATE_DEFAULT
    )
lv.obj_set_style_arc_opa(ui_Arc1, 75, lv.PART_INDICATOR | lv.STATE_DEFAULT)
lv.obj_set_style_arc_opa(ui_Arc1, 0, lv.PART_MAIN | lv.STATE_DEFAULT)
lv.obj_set_style_bg_opa(ui_Arc1, 0, lv.PART_KNOB | lv.STATE_DEFAULT)
lv.arc_set_rotation(ui_Arc1, 270)
lv.obj_set_style_arc_rounded(ui_Arc1, False, lv.PART_INDICATOR | lv.STATE_DEFAULT)


ui_Arc2 = lv.arc_create(ui_Screen1)
lv.obj_set_width(ui_Arc2, 150)
lv.obj_set_height(ui_Arc2, 150)
lv.obj_set_align(ui_Arc2, lv.ALIGN_CENTER)
lv.arc_set_value(ui_Arc2, 26)
lv.arc_set_bg_angles(ui_Arc2, 0, 360)
# ui_Arc1.set_mode(ui_Arc1.MODE.SYMMETRICAL)
lv.obj_set_style_arc_color(
    ui_Arc2,
    lv.color_hex(0xFFFF00),
    lv.PART_INDICATOR | lv.STATE_DEFAULT
    )
lv.obj_set_style_arc_opa(ui_Arc2, 125, lv.PART_INDICATOR | lv.STATE_DEFAULT)
lv.obj_set_style_arc_opa(ui_Arc2, 0, lv.PART_MAIN | lv.STATE_DEFAULT)
lv.obj_set_style_bg_opa(ui_Arc2, 0, lv.PART_KNOB | lv.STATE_DEFAULT)
lv.arc_set_rotation(ui_Arc2, 180)
lv.obj_set_style_arc_rounded(ui_Arc2, False, lv.PART_INDICATOR | lv.STATE_DEFAULT)

ui_Arc3 = lv.arc_create(ui_Screen1)
lv.obj_set_width(ui_Arc3, 150)
lv.obj_set_height(ui_Arc3, 150)
lv.obj_set_align(ui_Arc3, lv.ALIGN_CENTER)
lv.arc_set_value(ui_Arc3, 50)
lv.arc_set_bg_angles(ui_Arc3, 0, 360)
# ui_Arc1.set_mode(ui_Arc1.MODE.SYMMETRICAL)
lv.obj_set_style_arc_color(
    ui_Arc3,
    lv.color_hex(0x00FFFF),
    lv.PART_INDICATOR | lv.STATE_DEFAULT
    )
lv.obj_set_style_arc_opa(ui_Arc3, 175, lv.PART_INDICATOR | lv.STATE_DEFAULT)
lv.obj_set_style_arc_opa(ui_Arc3, 0, lv.PART_MAIN | lv.STATE_DEFAULT)
lv.obj_set_style_bg_opa(ui_Arc3, 0, lv.PART_KNOB | lv.STATE_DEFAULT)
lv.arc_set_rotation(ui_Arc3, 90)
lv.obj_set_style_arc_rounded(ui_Arc3, False, lv.PART_INDICATOR | lv.STATE_DEFAULT)



ui_Arc4 = lv.arc_create(ui_Screen1)
lv.obj_set_width(ui_Arc4, 125)
lv.obj_set_height(ui_Arc4, 125)
lv.obj_set_align(ui_Arc4, lv.ALIGN_CENTER)
lv.arc_set_value(ui_Arc4, 76)
lv.arc_set_bg_angles(ui_Arc4, 0, 360)
# ui_Arc1.set_mode(ui_Arc1.MODE.SYMMETRICAL)
lv.obj_set_style_arc_color(
    ui_Arc4,
    lv.color_hex(0x007BFF),
    lv.PART_INDICATOR | lv.STATE_DEFAULT
    )
lv.obj_set_style_arc_opa(ui_Arc4, 75, lv.PART_INDICATOR | lv.STATE_DEFAULT)
lv.obj_set_style_arc_opa(ui_Arc4, 0, lv.PART_MAIN | lv.STATE_DEFAULT)
lv.obj_set_style_bg_opa(ui_Arc4, 0, lv.PART_KNOB | lv.STATE_DEFAULT)
lv.arc_set_rotation(ui_Arc4, 50)
lv.obj_set_style_arc_rounded(ui_Arc4, False, lv.PART_INDICATOR | lv.STATE_DEFAULT)




ui_Arc5 = lv.arc_create(ui_Screen1)
lv.obj_set_width(ui_Arc5, 125)
lv.obj_set_height(ui_Arc5, 125)
lv.obj_set_align(ui_Arc5, lv.ALIGN_CENTER)
lv.arc_set_value(ui_Arc5, 20)
lv.arc_set_bg_angles(ui_Arc5, 0, 360)
# ui_Arc1.set_mode(ui_Arc1.MODE.SYMMETRICAL)
lv.obj_set_style_arc_color(
    ui_Arc5,
    lv.color_hex(0x7BFF00),
    lv.PART_INDICATOR | lv.STATE_DEFAULT
    )
lv.obj_set_style_arc_opa(ui_Arc5, 125, lv.PART_INDICATOR | lv.STATE_DEFAULT)
lv.obj_set_style_arc_opa(ui_Arc5, 0, lv.PART_MAIN | lv.STATE_DEFAULT)
lv.obj_set_style_bg_opa(ui_Arc5, 0, lv.PART_KNOB | lv.STATE_DEFAULT)
lv.arc_set_rotation(ui_Arc5, 300)
lv.obj_set_style_arc_rounded(ui_Arc5, False, lv.PART_INDICATOR | lv.STATE_DEFAULT)




ui_Arc6 = lv.arc_create(ui_Screen1)
lv.obj_set_width(ui_Arc6, 125)
lv.obj_set_height(ui_Arc6, 125)
lv.obj_set_align(ui_Arc6, lv.ALIGN_CENTER)
lv.arc_set_value(ui_Arc6, 60)
lv.arc_set_bg_angles(ui_Arc6, 0, 360)
# ui_Arc1.set_mode(ui_Arc1.MODE.SYMMETRICAL)
lv.obj_set_style_arc_color(
    ui_Arc6,
    lv.color_hex(0xFF007B),
    lv.PART_INDICATOR | lv.STATE_DEFAULT
    )
lv.obj_set_style_arc_opa(ui_Arc6, 125, lv.PART_INDICATOR | lv.STATE_DEFAULT)
lv.obj_set_style_arc_opa(ui_Arc6, 0, lv.PART_MAIN | lv.STATE_DEFAULT)
lv.obj_set_style_bg_opa(ui_Arc6, 0, lv.PART_KNOB | lv.STATE_DEFAULT)
lv.arc_set_rotation(ui_Arc6, 130)
lv.obj_set_style_arc_rounded(ui_Arc6, False, lv.PART_INDICATOR | lv.STATE_DEFAULT)


ui_Arc7 = lv.arc_create(ui_Screen1)
lv.obj_set_width(ui_Arc7, 100)
lv.obj_set_height(ui_Arc7, 100)
lv.obj_set_align(ui_Arc7, lv.ALIGN_CENTER)
lv.arc_set_value(ui_Arc7, 45)
lv.arc_set_bg_angles(ui_Arc7, 0, 360)
# ui_Arc1.set_mode(ui_Arc1.MODE.SYMMETRICAL)
lv.obj_set_style_arc_color(
    ui_Arc7,
    lv.color_hex(0xFF0000),
    lv.PART_INDICATOR | lv.STATE_DEFAULT
    )
lv.obj_set_style_arc_opa(ui_Arc7, 75, lv.PART_INDICATOR | lv.STATE_DEFAULT)
lv.obj_set_style_arc_opa(ui_Arc7, 0, lv.PART_MAIN | lv.STATE_DEFAULT)
lv.obj_set_style_bg_opa(ui_Arc7, 0, lv.PART_KNOB | lv.STATE_DEFAULT)
lv.arc_set_rotation(ui_Arc7, 240)
lv.obj_set_style_arc_rounded(ui_Arc7, False, lv.PART_INDICATOR | lv.STATE_DEFAULT)


ui_Arc8 = lv.arc_create(ui_Screen1)
lv.obj_set_width(ui_Arc8, 100)
lv.obj_set_height(ui_Arc8, 100)
lv.obj_set_align(ui_Arc8, lv.ALIGN_CENTER)
lv.arc_set_value(ui_Arc8, 82)
lv.arc_set_bg_angles(ui_Arc8, 0, 360)
# ui_Arc1.set_mode(ui_Arc1.MODE.SYMMETRICAL)
lv.obj_set_style_arc_color(
    ui_Arc8,
    lv.color_hex(0x0000FF),
    lv.PART_INDICATOR | lv.STATE_DEFAULT
    )
lv.obj_set_style_arc_opa(ui_Arc8, 175, lv.PART_INDICATOR | lv.STATE_DEFAULT)
lv.obj_set_style_arc_opa(ui_Arc8, 0, lv.PART_MAIN | lv.STATE_DEFAULT)
lv.obj_set_style_bg_opa(ui_Arc8, 0, lv.PART_KNOB | lv.STATE_DEFAULT)
lv.arc_set_rotation(ui_Arc8, 200)
lv.obj_set_style_arc_rounded(ui_Arc8, False, lv.PART_INDICATOR | lv.STATE_DEFAULT)


ui_Arc9 = lv.arc_create(ui_Screen1)
lv.obj_set_width(ui_Arc9, 100)
lv.obj_set_height(ui_Arc9, 100)
lv.obj_set_align(ui_Arc9, lv.ALIGN_CENTER)
lv.arc_set_value(ui_Arc9, 2)
lv.arc_set_bg_angles(ui_Arc9, 0, 360)
# ui_Arc1.set_mode(ui_Arc1.MODE.SYMMETRICAL)
lv.obj_set_style_arc_color(
    ui_Arc9,
    lv.color_hex(0x00FF00),
    lv.PART_INDICATOR | lv.STATE_DEFAULT
    )
lv.obj_set_style_arc_opa(ui_Arc9, 125, lv.PART_INDICATOR | lv.STATE_DEFAULT)
lv.obj_set_style_arc_opa(ui_Arc9, 0, lv.PART_MAIN | lv.STATE_DEFAULT)
lv.obj_set_style_bg_opa(ui_Arc9, 0, lv.PART_KNOB | lv.STATE_DEFAULT)
lv.arc_set_rotation(ui_Arc9, 100)
lv.obj_set_style_arc_rounded(ui_Arc9, False, lv.PART_INDICATOR | lv.STATE_DEFAULT)

lv.scr_load(ui_Screen1)

# values = [0, 25, 50, 75]
value_incs = [1, -1, 1, -1, -1, 1, 1, -1, 1]
rotation_incs = [-3, 3, -3, 3, -3, 3, 3, -3, 3]
arcs = [ui_Arc1, ui_Arc2, ui_Arc3, ui_Arc4, ui_Arc5, ui_Arc6, ui_Arc7, ui_Arc8,
        ui_Arc9]
coords = [[-1, 1], [-3, -2], [4, 1], [3, -3]]
coord_incs = [[-1, 1], [-1, -1], [1, 1], [1, -1]]

disp = lv.disp_get_default()

for arc in arcs:
    lv.obj_update_layout(arc)


import gc

def timer_cb(_):
    for i, arc in enumerate(arcs):
        value = lv.arc_get_value(arc)

        value_inc = value_incs[i]
        rotation_inc = rotation_incs[i]

        rotation = lv.arc_get_rotation(arc)

        rotation += rotation_inc
        if rotation <= 0 or rotation >= 360:
            rotation_inc = -rotation_inc
            rotation_incs[i] = rotation_inc

        value += value_inc
        if value in (0, 100):
            value_inc = -value_inc
            value_incs[i] = value_inc

        lv.arc_set_rotation(arc, rotation)
        lv.arc_set_value(arc, value)

        lv.obj_invalidate(arc)


timer = lv.timer_create_basic()
lv.timer_set_period(timer, 1)
lv.timer_set_cb(timer, timer_cb)

lv.main_loop()
