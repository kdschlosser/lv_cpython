/**
 * @file lv_draw.h
 *
 */

#ifndef LV_DRAW_H
#define LV_DRAW_H

#ifdef __cplusplus
extern "C" {
#endif

/*********************
 *      INCLUDES
 *********************/
#include "../lv_conf_internal.h"

#include "../misc/lv_style.h"
#include "../misc/lv_txt.h"
#include "lv_img_decoder.h"
#include "lv_img_cache.h"

#include "lv_draw_rect.h"
#include "lv_draw_label.h"
#include "lv_draw_img.h"
#include "lv_draw_line.h"
#include "lv_draw_triangle.h"
#include "lv_draw_arc.h"
#include "lv_draw_mask.h"
#include "lv_draw_transform.h"
#include "lv_draw_layer.h"

/*********************
 *      DEFINES
 *********************/

/**********************
 *      TYPEDEFS
 **********************/

typedef struct {
    void * user_data;
} lv_draw_mask_t;


typedef struct {
    const lv_area_t * clip_area;
    lv_area_t * buf_area;
    void * buf;
    lv_color_format_t color_format;
} lv_draw_layer_ctx_original_t;


typedef struct _lv_draw_layer_ctx_t {
    lv_area_t area_full;
    lv_area_t area_act;
    lv_coord_t max_row_with_alpha;
    lv_coord_t max_row_with_no_alpha;
    void * buf;
    lv_draw_layer_ctx_original_t original;
} lv_draw_layer_ctx_t;


typedef void (*lv_draw_ctx_init_buf_cb_t)(struct _lv_draw_ctx_t * draw_ctx);

typedef void (*lv_draw_ctx_draw_rect_cb_t)(struct _lv_draw_ctx_t * draw_ctx, const lv_draw_rect_dsc_t * dsc, const lv_area_t * coords);

typedef void (*lv_draw_ctx_draw_arc_cb_t)(struct _lv_draw_ctx_t * draw_ctx, const lv_draw_arc_dsc_t * dsc, const lv_point_t * center,
                 uint16_t radius,  uint16_t start_angle, uint16_t end_angle);

typedef void (*lv_draw_ctx_draw_img_decoded_cb_t)(struct _lv_draw_ctx_t * draw_ctx, const lv_draw_img_dsc_t * dsc, const lv_area_t * coords,
                         const uint8_t * map_p, const lv_draw_img_sup_t * sup, lv_color_format_t color_format);

typedef lv_res_t (*lv_draw_ctx_draw_img_cb_t)(struct _lv_draw_ctx_t * draw_ctx, const lv_draw_img_dsc_t * draw_dsc,
                     const lv_area_t * coords, const void * src);

typedef void (*lv_draw_ctx_draw_letter_cb_t)(struct _lv_draw_ctx_t * draw_ctx, const lv_draw_label_dsc_t * dsc,  const lv_point_t * pos_p,
                    uint32_t letter);


typedef void (*lv_draw_ctx_draw_line_cb_t)(struct _lv_draw_ctx_t * draw_ctx, const lv_draw_line_dsc_t * dsc, const lv_point_t * point1,
                  const lv_point_t * point2);


typedef void (*lv_draw_ctx_draw_polygon_cb_t)(struct _lv_draw_ctx_t * draw_ctx, const lv_draw_rect_dsc_t * draw_dsc,
                     const lv_point_t points[], uint16_t point_cnt);


/**
 * Get an area of a transformed image (zoomed and/or rotated)
 * @param draw_ctx      pointer to a draw context
 * @param dest_area     get this area of the result image. It assumes that the original image is placed to the 0;0 position.
 * @param src_buf       the source image
 * @param src_w         width of the source image in [px]
 * @param src_h         height of the source image in [px]
 * @param src_stride    the stride in [px].
 * @param draw_dsc      an `lv_draw_img_dsc_t` descriptor containing the transformation parameters
 * @param cf            the color format of `src_buf`
 * @param cbuf          place the colors of the pixels on `dest_area` here in RGB format
 * @param abuf          place the opacity of the pixels on `dest_area` here
 */
typedef void (*lv_draw_ctx_draw_transform_cb_t)(struct _lv_draw_ctx_t * draw_ctx, const lv_area_t * dest_area, const void * src_buf,
                       lv_coord_t src_w, lv_coord_t src_h, lv_coord_t src_stride,
                       const lv_draw_img_dsc_t * draw_dsc, const lv_draw_img_sup_t * sup, lv_color_format_t cf, lv_color_t * cbuf,
                       lv_opa_t * abuf);

/**
 * Wait until all background operations are finished. (E.g. GPU operations)
 */
typedef void (*lv_draw_ctx_wait_for_finish_cb_t)(struct _lv_draw_ctx_t * draw_ctx);

/**
 * Copy an area from buffer to an other
 * @param draw_ctx      pointer to a draw context
 * @param dest_buf      copy the buffer into this buffer
 * @param dest_stride   the width of the dest_buf in pixels
 * @param dest_area     the destination area
 * @param src_buf       copy from this buffer
 * @param src_stride    the width of src_buf in pixels
 * @param src_area      the source area.
 *
 * @note dest_area and src_area must have the same width and height
 *       but can have different x and y position.
 * @note dest_area and src_area must be clipped to the real dimensions of the buffers
 */

typedef void (*lv_draw_ctx_buffer_copy_cb_t)(struct _lv_draw_ctx_t * draw_ctx, void * dest_buf, lv_coord_t dest_stride,
                    const lv_area_t * dest_area,
                    void * src_buf, lv_coord_t src_stride, const lv_area_t * src_area);

/**
 * Convert the content of `draw_ctx->buf` to `draw_ctx->color_format`
 * @param draw_ctx
 */
typedef void (*lv_draw_ctx_buffer_convert_cb_t)(struct _lv_draw_ctx_t * draw_ctx);

typedef void (*lv_draw_ctx_buffer_clear_cb_t)(struct _lv_draw_ctx_t * draw_ctx);

/**
 * Initialize a new layer context.
 * The original buffer and area data are already saved from `draw_ctx` to `layer_ctx`
 * @param draw_ctx      pointer to the current draw context
 * @param layer_area    the coordinates of the layer
 * @param flags         OR-ed flags from @lv_draw_layer_flags_t
 * @return              pointer to the layer context, or NULL on error
 */
typedef struct _lv_draw_layer_ctx_t * (*lv_draw_ctx_layer_init_cb_t)(struct _lv_draw_ctx_t * draw_ctx, struct _lv_draw_layer_ctx_t * layer_ctx,
                                            lv_draw_layer_flags_t flags);

/**
 * Adjust the layer_ctx and/or draw_ctx based on the `layer_ctx->area_act`.
 * It's called only if flags has `LV_DRAW_LAYER_FLAG_CAN_SUBDIVIDE`
 * @param draw_ctx      pointer to the current draw context
 * @param layer_ctx     pointer to a layer context
 * @param flags         OR-ed flags from @lv_draw_layer_flags_t
 */
typedef void (*lv_draw_ctx_layer_adjust_cb_t)(struct _lv_draw_ctx_t * draw_ctx, struct _lv_draw_layer_ctx_t * layer_ctx,
                     lv_draw_layer_flags_t flags);

/**
 * Blend a rendered layer to `layer_ctx->area_act`
 * @param draw_ctx      pointer to the current draw context
 * @param layer_ctx     pointer to a layer context
 * @param draw_dsc      pointer to an image draw descriptor
 */
typedef void (*lv_draw_ctx_layer_blend_cb_t)(struct _lv_draw_ctx_t * draw_ctx, struct _lv_draw_layer_ctx_t * layer_ctx,
                    const lv_draw_img_dsc_t * draw_dsc);

/**
 * Destroy a layer context. The original buffer and area data of the `draw_ctx` will be restored
 * and the `layer_ctx` itself will be freed automatically.
 * @param draw_ctx      pointer to the current draw context
 * @param layer_ctx     pointer to a layer context
 */
typedef void (*lv_draw_ctx_layer_destroy_cb_t)(struct _lv_draw_ctx_t * draw_ctx, lv_draw_layer_ctx_t * layer_ctx);

typedef struct _lv_draw_ctx_t  {
    /**
     *  Pointer to a buffer to draw into
     */
    void * buf;

    /**
     * The position and size of `buf` (absolute coordinates)
     */
    lv_area_t * buf_area;

    /**
     * The current clip area with absolute coordinates, always the same or smaller than `buf_area`
     */
    const lv_area_t * clip_area;

    /**
     * The rendered image in draw_ctx->buf will be converted to this format
     * using draw_ctx->buffer_convert.
     */
    lv_color_format_t color_format;

    lv_draw_ctx_init_buf_cb_t init_buf;

    lv_draw_ctx_draw_rect_cb_t draw_rect;

    lv_draw_ctx_draw_arc_cb_t draw_arc;

    lv_draw_ctx_draw_img_decoded_cb_t draw_img_decoded;

    lv_draw_ctx_draw_img_cb_t draw_img;

    lv_draw_ctx_draw_letter_cb_t draw_letter;

    lv_draw_ctx_draw_line_cb_t draw_line;

    lv_draw_ctx_draw_polygon_cb_t draw_polygon;

    /**
     * Get an area of a transformed image (zoomed and/or rotated)
     */
    lv_draw_ctx_draw_transform_cb_t draw_transform;

    /**
     * Wait until all background operations are finished. (E.g. GPU operations)
     */
    lv_draw_ctx_wait_for_finish_cb_t wait_for_finish;

    /**
     * Copy an area from buffer to an other
     */
    lv_draw_ctx_buffer_copy_cb_t buffer_copy;

    /**
     * Convert the content of `draw_ctx->buf` to `draw_ctx->color_format`
     */
    lv_draw_ctx_buffer_convert_cb_t buffer_convert;

    lv_draw_ctx_buffer_clear_cb_t buffer_clear;

    /**
     * Initialize a new layer context.
     * The original buffer and area data are already saved from `draw_ctx` to `layer_ctx`
     */
    lv_draw_ctx_layer_init_cb_t layer_init;

    /**
     * Adjust the layer_ctx and/or draw_ctx based on the `layer_ctx->area_act`.
     * It's called only if flags has `LV_DRAW_LAYER_FLAG_CAN_SUBDIVIDE`
     */
    lv_draw_ctx_layer_adjust_cb_t layer_adjust;

    /**
     * Blend a rendered layer to `layer_ctx->area_act`
     */
    lv_draw_ctx_layer_blend_cb_t layer_blend;

    /**
     * Destroy a layer context. The original buffer and area data of the `draw_ctx` will be restored
     * and the `layer_ctx` itself will be freed automatically.
     */
    lv_draw_ctx_layer_destroy_cb_t layer_destroy;

    /**
     * Size of a layer context in bytes.
     */
    size_t layer_instance_size;

    void * user_data;
} lv_draw_ctx_t;

/**********************
 * GLOBAL PROTOTYPES
 **********************/

void lv_draw_init(void);


void lv_draw_wait_for_finish(lv_draw_ctx_t * draw_ctx);

/**********************
 *  GLOBAL VARIABLES
 **********************/

/**********************
 *      MACROS
 **********************/

/**********************
 *   POST INCLUDES
 *********************/

#ifdef __cplusplus
} /*extern "C"*/
#endif

#endif /*LV_DRAW_H*/
