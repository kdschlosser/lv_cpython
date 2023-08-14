/**
 * @file lv_conf.h
 * Configuration file for v9.0.0-dev
 */

/*
 * Copy this file as `lv_conf.h`
 * 1. simply next to the `lvgl` folder
 * 2. or any other places and
 *    - define `LV_CONF_INCLUDE_SIMPLE`
 *    - add the path as include path
 */

/* clang-format off */
/* #if 1 Set it to "1" to enable content*/

#ifndef LV_CONF_H
#define LV_CONF_H

#include <stdint.h>

/*====================
   COLOR SETTINGS
 *====================*/

/*Color depth: 8 (A8), 16 (RGB565), 24 (RGB888), 32 (XRGB8888)*/
#ifndef LV_COLOR_DEPTH
    #define LV_COLOR_DEPTH 32
#endif

#define LV_COLOR_CHROMA_KEY lv_color_hex(0x00ff00)

/*=========================
   STDLIB WRAPPER SETTINGS
 *=========================*/

/* Possible values
 * - LV_STDLIB_BUILTIN: LVGL's built in implementation
 * - LV_STDLIB_CLIB:    Standard C functions, like malloc, strlen, etc
 * - LV_STDLIB_CUSTOM:  Implement the functions externally
 */
#define LV_USE_STDLIB_MALLOC    LV_STDLIB_CLIB
#define LV_USE_STDLIB_STRING    LV_STDLIB_CLIB
#define LV_USE_STDLIB_SPRINTF   LV_STDLIB_CLIB


#if LV_USE_STDLIB_MALLOC == LV_STDLIB_BUILTIN
    /*Size of the memory available for `lv_malloc()` in bytes (>= 2kB)*/
    #define LV_MEM_SIZE (256 * 1024U)          /*[bytes]*/

    /*Size of the memory expand for `lv_malloc()` in bytes*/
    #define LV_MEM_POOL_EXPAND_SIZE 0

    /*Set an address for the memory pool instead of allocating it as a normal array. Can be in external SRAM too.*/
    #define LV_MEM_ADR 0     /*0: unused*/
    /*Instead of an address give a memory allocator that will be called to get a memory pool for LVGL. E.g. my_malloc*/
    #if LV_MEM_ADR == 0
        #undef LV_MEM_POOL_INCLUDE
        #undef LV_MEM_POOL_ALLOC
    #endif
#endif  /*LV_USE_MALLOC == LV_STDLIB_BUILTIN*/


#if LV_USE_STDLIB_SPRINTF == LV_STDLIB_BUILTIN
    #define LV_SPRINTF_USE_FLOAT 0
#endif  /*LV_USE_STDLIB_SPRINTF == LV_STDLIB_BUILTIN*/

/*====================
   HAL SETTINGS
 *====================*/

/*Default display refresh, input device read and animation step period.*/
#ifndef LV_DEF_REFR_PERIOD
    #define  LV_DEF_REFR_PERIOD 1  /*[ms]*/
#endif

/*Use a custom tick source that tells the elapsed time in milliseconds.
 *It removes the need to manually update the tick with `lv_tick_inc()`)*/
#define LV_TICK_CUSTOM 0
#if LV_TICK_CUSTOM
    #define LV_TICK_CUSTOM_INCLUDE "Arduino.h"         /*Header for the system time function*/
    #define LV_TICK_CUSTOM_SYS_TIME_EXPR (millis())    /*Expression evaluating to current system time in ms*/
    /*If using lvgl as ESP32 component*/
    // #define LV_TICK_CUSTOM_INCLUDE "esp_timer.h"
    // #define LV_TICK_CUSTOM_SYS_TIME_EXPR ((esp_timer_get_time() / 1000LL))
#endif   /*LV_TICK_CUSTOM*/

/*Default Dot Per Inch. Used to initialize default sizes such as widgets sized, style paddings.
 *(Not so important, you can adjust it to modify default sizes and spaces)*/
#ifndef LV_DPI_DEF
    #define LV_DPI_DEF 130     /*[px/inch]*/
#endif

/*========================
 * RENDERING CONFIGURATION
 *========================*/

/* Max. memory to be used for layers */
#define  LV_LAYER_MAX_MEMORY_USAGE             1024       /*[kB]*/

#define LV_USE_DRAW_SW  1
#if LV_USE_DRAW_SW == 1

    /*Enable complex draw engine.
     *Required to draw shadow, gradient, rounded corners, circles, arc, skew lines, image transformations or any masks*/
    #define LV_DRAW_SW_DRAW_UNIT_CNT    1

    /* If a widget has `style_opa < 255` (not `bg_opa`, `text_opa` etc) or not NORMAL blend mode
     * it is buffered into a "simple" layer before rendering. The widget can be buffered in smaller chunks.
     * "Transformed layers" (if `transform_angle/zoom` are set) use larger buffers
     * and can't be drawn in chunks. */

    /*The target buffer size for simple layer chunks.*/
    #define LV_DRAW_SW_LAYER_SIMPLE_BUF_SIZE          (64 * 1024)   /*[bytes]*/

    /* 0: use a simple renderer capable of drawing only simple rectangles with gradient, images, texts, and straight lines only
     * 1: use a complex renderer capable of drawing rounded corners, shadow, skew lines, and arcs too */
    #define LV_DRAW_SW_COMPLEX          1

    #if LV_DRAW_SW_COMPLEX == 1
        /*Allow buffering some shadow calculation.
        *LV_DRAW_SW_SHADOW_CACHE_SIZE is the max. shadow size to buffer, where shadow size is `shadow_width + radius`
        *Caching has LV_DRAW_SW_SHADOW_CACHE_SIZE^2 RAM cost*/
        #define LV_DRAW_SW_SHADOW_CACHE_SIZE (1024)

        /* Set number of maximally cached circle data.
        * The circumference of 1/4 circle are saved for anti-aliasing
        * radius * 4 bytes are used per circle (the most often used radiuses are saved)
        * 0: to disable caching */
        #define LV_DRAW_SW_CIRCLE_CACHE_SIZE 16
    #endif
#endif

/*=================
 * OPERATING SYSTEM
 *=================*/
/*Select an operating system to use. Possible options:
 * - LV_OS_NONE
 * - LV_OS_PTHREAD
 * - LV_OS_FREERTOS
 * - LV_OS_CMSIS_RTOS2
 * - LV_OS_CUSTOM */
#define LV_USE_OS   LV_OS_NONE

#if LV_USE_OS == LV_OS_CUSTOM
    #define LV_OS_CUSTOM_INCLUDE <stdint.h>
#endif


/*=======================
 * FEATURE CONFIGURATION
 *=======================*/

/*-------------
 * Logging
 *-----------*/

/*Enable the log module*/
#define LV_USE_LOG 1
#if LV_USE_LOG

    /*How important log should be added:
    *LV_LOG_LEVEL_TRACE       A lot of logs to give detailed information
    *LV_LOG_LEVEL_INFO        Log important events
    *LV_LOG_LEVEL_WARN        Log if something unwanted happened but didn't cause a problem
    *LV_LOG_LEVEL_ERROR       Only critical issue, when the system may fail
    *LV_LOG_LEVEL_USER        Only logs added by the user
    *LV_LOG_LEVEL_NONE        Do not log anything*/
    #define LV_LOG_LEVEL LV_LOG_LEVEL_WARN

    /*1: Print the log with 'printf';
    *0: User need to register a callback with `lv_log_register_print_cb()`*/
    #define LV_LOG_PRINTF 0

    /*1: Enable print timestamp;
     *0: Disable print timestamp*/
    #define LV_LOG_USE_TIMESTAMP 0

    /*Enable/disable LV_LOG_TRACE in modules that produces a huge number of logs*/
    #define LV_LOG_TRACE_MEM        1
    #define LV_LOG_TRACE_TIMER      1
    #define LV_LOG_TRACE_INDEV      1
    #define LV_LOG_TRACE_DISP_REFR  1
    #define LV_LOG_TRACE_EVENT      1
    #define LV_LOG_TRACE_OBJ_CREATE 1
    #define LV_LOG_TRACE_LAYOUT     1
    #define LV_LOG_TRACE_ANIM       1
	#define LV_LOG_TRACE_MSG		1

#endif  /*LV_USE_LOG*/

/*-------------
 * Asserts
 *-----------*/

/*Enable asserts if an operation is failed or an invalid data is found.
 *If LV_USE_LOG is enabled an error message will be printed on failure*/
#define LV_USE_ASSERT_NULL          1   /*Check if the parameter is NULL. (Very fast, recommended)*/
#define LV_USE_ASSERT_MALLOC        1   /*Checks is the memory is successfully allocated or no. (Very fast, recommended)*/
#define LV_USE_ASSERT_STYLE         0   /*Check if the styles are properly initialized. (Very fast, recommended)*/
#define LV_USE_ASSERT_MEM_INTEGRITY 0   /*Check the integrity of `lv_mem` after critical operations. (Slow)*/
#define LV_USE_ASSERT_OBJ           0   /*Check the object's type and existence (e.g. not deleted). (Slow)*/

/*Add a custom handler when assert happens e.g. to restart the MCU*/
#define LV_ASSERT_HANDLER_INCLUDE <stdint.h>
#define LV_ASSERT_HANDLER while(1);   /*Halt by default*/

/*-------------
 * Debug
 *-----------*/

/*1: Draw random colored rectangles over the redrawn areas*/
#define LV_USE_REFR_DEBUG 0

/*1: Draw a red overlay for ARGB layers and a green overlay for RGB layers*/
#define LV_USE_LAYER_DEBUG 0

/*1: Draw overlays with different colors for each draw_unit's tasks.
 *Also add the index number of the draw unit on white background.
 *For layers add the index number of the draw unit on black background.*/
#define LV_USE_PARALLEL_DRAW_DEBUG 0

/*------------------
 * STATUS MONITORING
 *------------------*/

/*1: Show CPU usage and FPS count
 * Requires `LV_USE_SYSMON = 1`*/
#ifndef LV_USE_PERF_MONITOR
    #define  LV_USE_PERF_MONITOR 0
#endif

#if LV_USE_PERF_MONITOR
    #define LV_USE_PERF_MONITOR_POS LV_ALIGN_BOTTOM_RIGHT

    /*0: Displays performance data on the screen, 1: Prints performance data using log.*/
    #define LV_USE_PERF_MONITOR_LOG_MODE 0
#endif

/*1: Show the used memory and the memory fragmentation
 * Requires `LV_USE_BUILTIN_MALLOC = 1`
 * Requires `LV_USE_SYSMON = 1`*/
#define LV_USE_MEM_MONITOR 0
#if LV_USE_MEM_MONITOR
    #define LV_USE_MEM_MONITOR_POS LV_ALIGN_BOTTOM_LEFT
#endif

/*-------------
 * Others
 *-----------*/

/*Maximum buffer size to allocate for rotation.
 *Only used if software rotation is enabled in the display driver.*/
#define LV_DISP_ROT_MAX_BUF (1920 * 1080 * 4)

/*Garbage Collector settings
 *Used if lvgl is bound to higher level language and the memory is managed by that language*/
#define LV_ENABLE_GC 0
#if LV_ENABLE_GC != 0
    #define LV_GC_INCLUDE "gc.h"                           /*Include Garbage Collector related things*/
#endif /*LV_ENABLE_GC*/

/*Default image cache size. Image caching keeps some images opened.
 *If only the built-in image formats are used there is no real advantage of caching.
 *With other image decoders (e.g. PNG or JPG) caching save the continuous open/decode of images.
 *However the opened images consume additional RAM.
 *0: to disable caching*/
#define LV_IMG_CACHE_DEF_SIZE 1


/*Number of stops allowed per gradient. Increase this to allow more stops.
 *This adds (sizeof(lv_color_t) + 1) bytes per additional stop*/
#ifndef LV_GRADIENT_MAX_STOPS
    #define  LV_GRADIENT_MAX_STOPS 32
#endif

/* Adjust color mix functions rounding. GPUs might calculate color mix (blending) differently.
 * 0: round down, 64: round up from x.75, 128: round up from half, 192: round up from x.25, 254: round up */
#define lv_color_mix_ROUND_OFS 0

/*=====================
 *  COMPILER SETTINGS
 *====================*/

/*For big endian systems set to 1*/
#define LV_BIG_ENDIAN_SYSTEM 0

/*Define a custom attribute to `lv_tick_inc` function*/
#define LV_ATTRIBUTE_TICK_INC

/*Define a custom attribute to `lv_timer_handler` function*/
#define LV_ATTRIBUTE_TIMER_HANDLER

/*Define a custom attribute to `lv_disp_flush_ready` function*/
#define LV_ATTRIBUTE_FLUSH_READY

/*Required alignment size for buffers*/
#define LV_ATTRIBUTE_MEM_ALIGN_SIZE 1

/*Will be added where memories needs to be aligned (with -Os data might not be aligned to boundary by default).
 * E.g. __attribute__((aligned(4)))*/
#define LV_ATTRIBUTE_MEM_ALIGN

/*Attribute to mark large constant arrays for example font's bitmaps*/
#define LV_ATTRIBUTE_LARGE_CONST

/*Compiler prefix for a big array declaration in RAM*/
#define LV_ATTRIBUTE_LARGE_RAM_ARRAY

/*Place performance critical functions into a faster memory (e.g RAM)*/
#define LV_ATTRIBUTE_FAST_MEM

/*Export integer constant to binding. This macro is used with constants in the form of LV_<CONST> that
 *should also appear on LVGL binding API such as Micropython.*/
#define LV_EXPORT_CONST_INT(int_value) struct _silence_gcc_warning /*The default value just prevents GCC warning*/

/*Extend the default -32k..32k coordinate range to -4M..4M by using int32_t for coordinates instead of int16_t*/
#define LV_USE_LARGE_COORD 1

/*==================
 *   FONT USAGE
 *===================*/

/*Montserrat fonts with ASCII range and some symbols using bpp = 4
 *https://fonts.google.com/specimen/Montserrat*/
#define LV_FONT_MONTSERRAT_8  1
#define LV_FONT_MONTSERRAT_10 1
#define LV_FONT_MONTSERRAT_12 1
#define LV_FONT_MONTSERRAT_14 1
#define LV_FONT_MONTSERRAT_16 1
#define LV_FONT_MONTSERRAT_18 1
#define LV_FONT_MONTSERRAT_20 1
#define LV_FONT_MONTSERRAT_22 1
#define LV_FONT_MONTSERRAT_24 1
#define LV_FONT_MONTSERRAT_26 1
#define LV_FONT_MONTSERRAT_28 1
#define LV_FONT_MONTSERRAT_30 1
#define LV_FONT_MONTSERRAT_32 1
#define LV_FONT_MONTSERRAT_34 1
#define LV_FONT_MONTSERRAT_36 1
#define LV_FONT_MONTSERRAT_38 1
#define LV_FONT_MONTSERRAT_40 1
#define LV_FONT_MONTSERRAT_42 1
#define LV_FONT_MONTSERRAT_44 1
#define LV_FONT_MONTSERRAT_46 1
#define LV_FONT_MONTSERRAT_48 1

/*Demonstrate special features*/
#define LV_FONT_MONTSERRAT_12_SUBPX      1
#define LV_FONT_MONTSERRAT_28_COMPRESSED 1  /*bpp = 3*/
#define LV_FONT_DEJAVU_16_PERSIAN_HEBREW 1  /*Hebrew, Arabic, Persian letters and all their forms*/
#define LV_FONT_SIMSUN_16_CJK            1  /*1000 most common CJK radicals*/

/*Pixel perfect monospace fonts*/
#define LV_FONT_UNSCII_8  1
#define LV_FONT_UNSCII_16 1

/*Optionally declare custom fonts here.
 *You can use these fonts as default font too and they will be available globally.
 *E.g. #define LV_FONT_CUSTOM_DECLARE   LV_FONT_DECLARE(my_font_1) LV_FONT_DECLARE(my_font_2)*/
#define LV_FONT_CUSTOM_DECLARE

/*Always set a default font*/
#define LV_FONT_DEFAULT &lv_font_montserrat_14

/*Enable handling large font and/or fonts with a lot of characters.
 *The limit depends on the font size, font face and bpp.
 *Compiler error will be triggered if a font needs it.*/
#define LV_FONT_FMT_TXT_LARGE 1

/*Enables/disables support for compressed fonts.*/
#define LV_USE_FONT_COMPRESSED 1

/*Enable drawing placeholders when glyph dsc is not found*/
#define LV_USE_FONT_PLACEHOLDER 1

/*=================
 *  TEXT SETTINGS
 *=================*/

/**
 * Select a character encoding for strings.
 * Your IDE or editor should have the same character encoding
 * - LV_TXT_ENC_UTF8
 * - LV_TXT_ENC_ASCII
 */
#define LV_TXT_ENC LV_TXT_ENC_UTF8

/*Can break (wrap) texts on these chars*/
#define LV_TXT_BREAK_CHARS " ,.;:-_)]}"

/*If a word is at least this long, will break wherever "prettiest"
 *To disable, set to a value <= 0*/
#define LV_TXT_LINE_BREAK_LONG_LEN 0

/*Minimum number of characters in a long word to put on a line before a break.
 *Depends on LV_TXT_LINE_BREAK_LONG_LEN.*/
#define LV_TXT_LINE_BREAK_LONG_PRE_MIN_LEN 3

/*Minimum number of characters in a long word to put on a line after a break.
 *Depends on LV_TXT_LINE_BREAK_LONG_LEN.*/
#define LV_TXT_LINE_BREAK_LONG_POST_MIN_LEN 3

/*Support bidirectional texts. Allows mixing Left-to-Right and Right-to-Left texts.
 *The direction will be processed according to the Unicode Bidirectional Algorithm:
 *https://www.w3.org/International/articles/inline-bidi-markup/uba-basics*/
#ifndef LV_USE_BIDI
    #define  LV_USE_BIDI 1
#endif

#if LV_USE_BIDI
    /*Set the default direction. Supported values:
    *`LV_BASE_DIR_LTR` Left-to-Right
    *`LV_BASE_DIR_RTL` Right-to-Left
    *`LV_BASE_DIR_AUTO` detect texts base direction*/
    #define LV_BIDI_BASE_DIR_DEF LV_BASE_DIR_AUTO
#endif

/*Enable Arabic/Persian processing
 *In these languages characters should be replaced with an other form based on their position in the text*/
#define LV_USE_ARABIC_PERSIAN_CHARS 0

/*==================
 * WIDGETS
 *================*/

/*Documentation of the widgets: https://docs.lvgl.io/latest/en/html/widgets/index.html*/
#ifndef LV_USE_ANIMIMG
    #define  LV_USE_ANIMIMG 1
#endif

#ifndef LV_USE_ARC
    #define  LV_USE_ARC 1
#endif

#ifndef LV_USE_BAR
    #define  LV_USE_BAR 1
#endif

#ifndef LV_USE_BTN
    #define  LV_USE_BTN 1
#endif

#ifndef LV_USE_BTNMATRIX
    #define  LV_USE_BTNMATRIX 1
#endif

#ifndef LV_USE_CALENDAR
    #define  LV_USE_CALENDAR 1
#endif
#if LV_USE_CALENDAR
    #define LV_CALENDAR_WEEK_STARTS_MONDAY 0
    #if LV_CALENDAR_WEEK_STARTS_MONDAY
        #define LV_CALENDAR_DEFAULT_DAY_NAMES {"Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"}
    #else
        #define LV_CALENDAR_DEFAULT_DAY_NAMES {"Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"}
    #endif

    #define LV_CALENDAR_DEFAULT_MONTH_NAMES {"January", "February", "March",  "April", "May",  "June", "July", "August", "September", "October", "November", "December"}
    #define LV_USE_CALENDAR_HEADER_ARROW 1
    #define LV_USE_CALENDAR_HEADER_DROPDOWN 1
#endif  /*LV_USE_CALENDAR*/

#ifndef LV_USE_CANVAS
    #define  LV_USE_CANVAS 1
#endif

#ifndef LV_USE_CHART
    #define  LV_USE_CHART 1
#endif

#ifndef LV_USE_CHECKBOX
    #define  LV_USE_CHECKBOX 1
#endif

#ifndef LV_USE_COLORWHEEL
    #define  LV_USE_COLORWHEEL 1
#endif

#ifndef LV_USE_DROPDOWN
    #define  LV_USE_DROPDOWN 1  /*Requires: lv_label*/
#endif

#ifndef LV_USE_IMG
    #define  LV_USE_IMG 1 /*Requires: lv_label*/
#endif

#ifndef LV_USE_IMGBTN
    #define  LV_USE_IMGBTN 1
#endif

#ifndef LV_USE_KEYBOARD
    #define  LV_USE_KEYBOARD 1
#endif

#ifndef LV_USE_LABEL
    #define  LV_USE_LABEL 1
#endif
#if LV_USE_LABEL
    #define LV_LABEL_TEXT_SELECTION 1 /*Enable selecting text of the label*/
    #define LV_LABEL_LONG_TXT_HINT 1  /*Store some extra info in labels to speed up drawing of very long texts*/
#endif

#ifndef LV_USE_LED
    #define  LV_USE_LED 1
#endif

#ifndef LV_USE_LINE
    #define  LV_USE_LINE 1
#endif

#ifndef LV_USE_LIST
    #define  LV_USE_LIST 1
#endif

#ifndef LV_USE_MENU
    #define  LV_USE_MENU 1
#endif

#ifndef LV_USE_METER
    #define  LV_USE_METER 1
#endif

#ifndef LV_USE_MSGBOX
    #define  LV_USE_MSGBOX 1
#endif

#ifndef LV_USE_ROLLER
    #define  LV_USE_ROLLER 1  /*Requires: lv_label*/
#endif

#ifndef LV_USE_SLIDER
    #define  LV_USE_SLIDER 1 /*Requires: lv_bar*/
#endif

#ifndef LV_USE_SPAN
    #define  LV_USE_SPAN 1
#endif
#if LV_USE_SPAN
    /*A line text can contain maximum num of span descriptor */
    #define LV_SPAN_SNIPPET_STACK_SIZE 64
#endif

#ifndef LV_USE_SPINBOX
    #define  LV_USE_SPINBOX 1
#endif

#ifndef LV_USE_SPINNER
    #define  LV_USE_SPINNER 1
#endif

#ifndef LV_USE_SWITCH
    #define  LV_USE_SWITCH 1
#endif

#ifndef LV_USE_TEXTAREA
    #define  LV_USE_TEXTAREA 1 /*Requires: lv_label*/
#endif
#if LV_USE_TEXTAREA != 0
    #define LV_TEXTAREA_DEF_PWD_SHOW_TIME 1500    /*ms*/
#endif

#ifndef LV_USE_TABLE
    #define  LV_USE_TABLE 1
#endif

#ifndef LV_USE_TABVIEW
    #define  LV_USE_TABVIEW 1
#endif

#ifndef LV_USE_TILEVIEW
    #define  LV_USE_TILEVIEW 1
#endif

#ifndef LV_USE_WIN
    #define  LV_USE_WIN 1
#endif

/*==================
 * THEMES
 *==================*/

/*A simple, impressive and very complete theme*/

#ifndef LV_USE_THEME_DEFAULT
    #define  LV_USE_THEME_DEFAULT 1
#endif

#if LV_USE_THEME_DEFAULT

    /*0: Light mode; 1: Dark mode*/
    #ifndef LV_THEME_DEFAULT_DARK
        #define  LV_THEME_DEFAULT_DARK 1
    #endif

    /*1: Enable grow on press*/
    #ifndef LV_THEME_DEFAULT_GROW
        #define  LV_THEME_DEFAULT_GROW 1
    #endif

    /*Default transition time in [ms]*/
    #define LV_THEME_DEFAULT_TRANSITION_TIME 80
#endif /*LV_USE_THEME_DEFAULT*/

/*A very simple theme that is a good starting point for a custom theme*/
#ifndef LV_USE_THEME_BASIC
    #define  LV_USE_THEME_BASIC 1
#endif

/*A theme designed for monochrome displays*/
#ifndef LV_USE_THEME_MONO
    #define  LV_USE_THEME_MONO 0
#endif

/*==================
 * LAYOUTS
 *==================*/

/*A layout similar to Flexbox in CSS.*/
#ifndef LV_USE_FLEX
    #define  LV_USE_FLEX 1
#endif

/*A layout similar to Grid in CSS.*/
#ifndef LV_USE_GRID
    #define  LV_USE_GRID 1
#endif

/*====================
 * 3RD PARTS LIBRARIES
 *====================*/

/*File system interfaces for common APIs */

/*API for fopen, fread, etc*/
#define LV_USE_FS_STDIO 0
#if LV_USE_FS_STDIO
    #define LV_FS_STDIO_LETTER '\0'     /*Set an upper cased letter on which the drive will accessible (e.g. 'A')*/
    #define LV_FS_STDIO_PATH ""         /*Set the working directory. File/directory paths will be appended to it.*/
    #define LV_FS_STDIO_CACHE_SIZE 0    /*>0 to cache this number of bytes in lv_fs_read()*/
#endif

/*API for open, read, etc*/
#define LV_USE_FS_POSIX 0
#if LV_USE_FS_POSIX
    #define LV_FS_POSIX_LETTER '\0'     /*Set an upper cased letter on which the drive will accessible (e.g. 'A')*/
    #define LV_FS_POSIX_PATH ""         /*Set the working directory. File/directory paths will be appended to it.*/
    #define LV_FS_POSIX_CACHE_SIZE 0    /*>0 to cache this number of bytes in lv_fs_read()*/
#endif

/*API for CreateFile, ReadFile, etc*/
#define LV_USE_FS_WIN32 0
#if LV_USE_FS_WIN32
    #define LV_FS_WIN32_LETTER '\0'     /*Set an upper cased letter on which the drive will accessible (e.g. 'A')*/
    #define LV_FS_WIN32_PATH ""         /*Set the working directory. File/directory paths will be appended to it.*/
    #define LV_FS_WIN32_CACHE_SIZE 0    /*>0 to cache this number of bytes in lv_fs_read()*/
#endif

/*API for FATFS (needs to be added separately). Uses f_open, f_read, etc*/
#define LV_USE_FS_FATFS 0
#if LV_USE_FS_FATFS
    #define LV_FS_FATFS_LETTER '\0'     /*Set an upper cased letter on which the drive will accessible (e.g. 'A')*/
    #define LV_FS_FATFS_CACHE_SIZE 0    /*>0 to cache this number of bytes in lv_fs_read()*/
#endif

/*PNG decoder library*/
#ifndef LV_USE_PNG
    #define  LV_USE_PNG 1
#endif

/*BMP decoder library*/
#ifndef LV_USE_BMP
    #define  LV_USE_BMP 1
#endif

/* JPG + split JPG decoder library.
 * Split JPG is a custom format optimized for embedded systems. */
#ifndef LV_USE_SJPG
    #define  LV_USE_SJPG 1
#endif

/*GIF decoder library*/
#ifndef LV_USE_GIF
    #define  LV_USE_GIF 1
#endif

/*QR code library*/
#ifndef LV_USE_QRCODE
    #define  LV_USE_QRCODE 1
#endif

/*Barcode code library*/
#ifndef LV_USE_BARCODE
    #define  LV_USE_BARCODE 1
#endif

/*FreeType library*/
#define LV_USE_FREETYPE 0
#if LV_USE_FREETYPE
    /*Memory used by FreeType to cache characters [bytes]*/
    #define LV_FREETYPE_CACHE_SIZE (64 * 1024)

    /*Let FreeType to use LVGL memory and file porting*/
    #define LV_FREETYPE_USE_LVGL_PORT 0

    /* 1: bitmap cache use the sbit cache, 0:bitmap cache use the image cache. */
    /* sbit cache:it is much more memory efficient for small bitmaps(font size < 256) */
    /* if font size >= 256, must be configured as image cache */
    #define LV_FREETYPE_SBIT_CACHE 0

    /* Maximum number of opened FT_Face/FT_Size objects managed by this cache instance. */
    /* (0:use system defaults) */
    #define LV_FREETYPE_CACHE_FT_FACES 4
    #define LV_FREETYPE_CACHE_FT_SIZES 4
#endif

/* Built-in TTF decoder */
#ifndef LV_USE_TINY_TTF
    #define LV_USE_TINY_TTF 1
#endif

#if LV_USE_TINY_TTF
    /* Enable loading TTF data from files */
    #define LV_TINY_TTF_FILE_SUPPORT 1
#endif

/*Rlottie library*/
#define LV_USE_RLOTTIE 0

/*FFmpeg library for image decoding and playing videos
 *Supports all major image formats so do not enable other image decoder with it*/
#define LV_USE_FFMPEG 0
#if LV_USE_FFMPEG
    /*Dump input information to stderr*/
    #define LV_FFMPEG_DUMP_FORMAT 0
#endif

/*==================
 * OTHERS
 *==================*/

/*1: Enable API to take snapshot for object*/
#ifndef LV_USE_SNAPSHOT
    #define  LV_USE_SNAPSHOT 1
#endif

/*1: Enable system monitor component*/
#ifndef LV_USE_SYSMON
    #define  LV_USE_SYSMON 0
#endif
/*1: Enable the runtime performance profiler*/
#ifndef LV_USE_PROFILER
    #define  LV_USE_PROFILER 0
#endif

#if LV_USE_PROFILER
    /*1: Enable the built-in profiler*/
    #define LV_USE_PROFILER_BUILTIN 1
    #if LV_USE_PROFILER_BUILTIN
        /*Default profiler trace buffer size*/
        #define LV_PROFILER_BUILTIN_BUF_SIZE (16 * 1024)     /*[bytes]*/
    #endif

    /*Header to include for the profiler*/
    #define LV_PROFILER_INCLUDE "lvgl/src/misc/lv_profiler_builtin.h"

    /*Profiler start point function*/
    #define LV_PROFILER_BEGIN   LV_PROFILER_BUILTIN_BEGIN

    /*Profiler end point function*/
    #define LV_PROFILER_END     LV_PROFILER_BUILTIN_END
#endif

/*1: Enable Monkey test*/
#ifndef LV_USE_MONKEY
    #define  LV_USE_MONKEY 0
#endif

/*1: Enable grid navigation*/
#ifndef LV_USE_GRIDNAV
    #define  LV_USE_GRIDNAV 1
#endif

/*1: Enable lv_obj fragment*/
#ifndef LV_USE_FRAGMENT
    #define  LV_USE_FRAGMENT 0
#endif

/*1: Support using images as font in label or span widgets */
#ifndef LV_USE_IMGFONT
    #define  LV_USE_IMGFONT 1
#endif

#if LV_USE_IMGFONT
    /*Imgfont image file path maximum length*/
    #define LV_IMGFONT_PATH_MAX_LEN 64

    /*1: Use img cache to buffer header information*/
    #define LV_IMGFONT_USE_IMG_CACHE_HEADER 0
#endif

/*1: Enable a published subscriber based messaging system */
#ifndef LV_USE_MSG
    #define  LV_USE_MSG 1
#endif

/*1: Enable Pinyin input method*/
/*Requires: lv_keyboard*/
#ifndef LV_USE_IME_PINYIN
    #define  LV_USE_IME_PINYIN 1
#endif

#if LV_USE_IME_PINYIN
    /*1: Use default thesaurus*/
    /*If you do not use the default thesaurus, be sure to use `lv_ime_pinyin` after setting the thesauruss*/
    #define LV_IME_PINYIN_USE_DEFAULT_DICT 1
    /*Set the maximum number of candidate panels that can be displayed*/
    /*This needs to be adjusted according to the size of the screen*/
    #define LV_IME_PINYIN_CAND_TEXT_NUM 6

    /*Use 9 key input(k9)*/
    #define LV_IME_PINYIN_USE_K9_MODE      1
    #if LV_IME_PINYIN_USE_K9_MODE == 1
        #define LV_IME_PINYIN_K9_CAND_TEXT_NUM 3
    #endif // LV_IME_PINYIN_USE_K9_MODE
#endif

/*1: Enable file explorer*/
/*Requires: lv_table*/
#ifndef LV_USE_FILE_EXPLORER
    #define  LV_USE_FILE_EXPLORER 1
#endif

#if LV_USE_FILE_EXPLORER
    /*Maximum length of path*/
    #define LV_FILE_EXPLORER_PATH_MAX_LEN        (128)
    /*Quick access bar, 1:use, 0:not use*/
    /*Requires: lv_list*/
    #define LV_FILE_EXPLORER_QUICK_ACCESS        1
#endif

/*==================
 * DEVICES
 *==================*/

/*Use SDL to open window on PC and handle mouse and keyboard*/

#ifdef MICROPY_SDL
    #define LV_USE_SDL 1
#else
#ifdef CPYTHON_SDL
    #define LV_USE_SDL 1
#else
    #define LV_USE_SDL 0
#endif
#endif

#if LV_USE_SDL
    #define LV_SDL_INCLUDE_PATH    <SDL2/SDL.h>
    #ifndef LV_SDL_PARTIAL_MODE
        #define LV_SDL_PARTIAL_MODE    0    /*Recommended only to emulate a setup with a display controller*/
    #endif
    #define LV_SDL_FULLSCREEN      0
    #define LV_SDL_DIRECT_EXIT     1    /*1: Exit the application when all SDL widows are closed*/
#endif

/*Driver for /dev/fb*/
#define LV_USE_LINUX_FBDEV      0
#if LV_USE_LINUX_FBDEV
    #define LV_LINUX_FBDEV_BSD  0
#endif

/*Driver for /dev/dri/card*/
#define LV_USE_LINUX_DRM        0

/*Interface for TFT_eSPI*/
#define LV_USE_TFT_ESPI         0

/*==================
* EXAMPLES
*==================*/

/*Enable the examples to be built with the library*/
#ifndef LV_BUILD_EXAMPLES
    #define  LV_BUILD_EXAMPLES 1
#endif

/*===================
 * DEMO USAGE
 ====================*/

/*Show some widget. It might be required to increase `LV_MEM_SIZE` */
#ifndef LV_USE_DEMO_WIDGETS
    #define  LV_USE_DEMO_WIDGETS 1
#endif

#if LV_USE_DEMO_WIDGETS
    #ifndef LV_DEMO_WIDGETS_SLIDESHOW
        #define  LV_DEMO_WIDGETS_SLIDESHOW 0
    #endif
#endif

/*Demonstrate the usage of encoder and keyboard*/
#ifndef LV_USE_DEMO_KEYPAD_AND_ENCODER
    #define  LV_USE_DEMO_KEYPAD_AND_ENCODER 0
#endif

/*Benchmark your system*/
#ifndef LV_USE_DEMO_BENCHMARK
    #define  LV_USE_DEMO_BENCHMARK 1
#endif

#if LV_USE_DEMO_BENCHMARK
    #ifndef LV_DEMO_BENCHMARK_RGB565A8
        /*Use RGB565A8 images with 16 bit color depth instead of ARGB8565*/
        #define  LV_DEMO_BENCHMARK_RGB565A8 0
    #endif
#endif

/*Stress test for LVGL*/
#ifndef LV_USE_DEMO_STRESS
    #define  LV_USE_DEMO_STRESS 1
#endif


/*Music player demo*/
#ifndef LV_USE_DEMO_MUSIC
    #define  LV_USE_DEMO_MUSIC 1
#endif

#if LV_USE_DEMO_MUSIC
    #ifndef LV_DEMO_MUSIC_SQUARE
        #define  LV_DEMO_MUSIC_SQUARE 0
    #endif

    #ifndef LV_DEMO_MUSIC_LANDSCAPE
        #define  LV_DEMO_MUSIC_LANDSCAPE 1
    #endif

    #ifndef LV_DEMO_MUSIC_ROUND
        #define  LV_DEMO_MUSIC_ROUND 0
    #endif

    #ifndef LV_DEMO_MUSIC_LARGE
        #define  LV_DEMO_MUSIC_LARGE 0
    #endif


    #ifndef LV_DEMO_MUSIC_AUTO_PLAY
        #define  LV_DEMO_MUSIC_AUTO_PLAY 0
    #endif

#endif

/*Flex layout demo*/
#ifndef LV_USE_DEMO_FLEX_LAYOUT
    #define  LV_USE_DEMO_FLEX_LAYOUT 1
#endif

/*Smart-phone like multi-language demo*/

#ifndef LV_USE_DEMO_MULTILANG
    #define  LV_USE_DEMO_MULTILANG 1
#endif

/*Widget transformation demo*/

#ifndef LV_USE_DEMO_TRANSFORM
    #define  LV_USE_DEMO_TRANSFORM 1
#endif

/*--END OF LV_CONF_H--*/

#endif /*LV_CONF_H*/

