#if !defined (BAV_POINT_INTERVAL_MPQ_H)
#   define BAV_POINT_INTERVAL_MPQ_H 1

#   include "bav_common.h"
#   include "bav_variable.h"

BEGIN_C_DECLS

/*
 * texinfo: bav_value_interval_mpq
 * This data type associates an interval with @code{mpq_t} ends
 * to a variable. It can be parsed and printed using the
 * format @code{%value(%qi)}.
 */

struct bav_value_interval_mpq
{
  struct bav_variable *var;
  struct ba0_interval_mpq *value;
};


/* In the next one, all variables might be equal */

struct bav_tableof_value_interval_mpq
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bav_value_interval_mpq **tab;
};



/*
 * texinfo: bav_point_interval_mpq
 * This data type is a particular case of the type @code{struct ba0_point}.
 * It permits to associate @code{ba0_interval_mpq} values to
 * many different variables.
 * They can be parsed by @code{ba0_scanf/%point(%qi)} and printed
 * by @code{ba0_printf/%point(%qi)}.
 * Many functions assume the @code{tab} field to be sorted
 * (see @code{ba0_sort_point}).
 */

struct bav_point_interval_mpq
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bav_value_interval_mpq **tab;
};


struct bav_tableof_point_interval_mpq
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bav_point_interval_mpq **tab;
};


extern BAV_DLL struct bav_value_interval_mpq *bav_new_value_interval_mpq (
    void);

extern BAV_DLL void bav_set_value_interval_mpq (
    struct bav_value_interval_mpq *,
    struct bav_value_interval_mpq *);

extern BAV_DLL void bav_init_point_interval_mpq (
    struct bav_point_interval_mpq *);

extern BAV_DLL struct bav_point_interval_mpq *bav_new_point_interval_mpq (
    void);

extern BAV_DLL void bav_realloc_point_interval_mpq (
    struct bav_point_interval_mpq *,
    ba0_int_p);

extern BAV_DLL void bav_set_point_interval_mpq (
    struct bav_point_interval_mpq *,
    struct bav_point_interval_mpq *);

extern BAV_DLL void bav_set_coord_point_interval_mpq (
    struct bav_point_interval_mpq *,
    struct bav_variable *,
    struct ba0_interval_mpq *);

extern BAV_DLL void bav_intersect_coord_point_interval_mpq (
    struct bav_point_interval_mpq *,
    struct bav_point_interval_mpq *,
    struct bav_variable *,
    struct ba0_interval_mpq *);

extern BAV_DLL void bav_intersect_point_interval_mpq (
    struct bav_point_interval_mpq *,
    struct bav_point_interval_mpq *,
    struct bav_point_interval_mpq *);

extern BAV_DLL bool bav_is_empty_point_interval_mpq (
    struct bav_point_interval_mpq *);

extern BAV_DLL void bav_bisect_point_interval_mpq (
    struct bav_tableof_point_interval_mpq *,
    struct bav_point_interval_mpq *,
    ba0_int_p);

extern BAV_DLL void bav_set_tableof_point_interval_mpq (
    struct bav_tableof_point_interval_mpq *,
    struct bav_tableof_point_interval_mpq *);

END_C_DECLS
#endif /* !BAV_POINT_INTERVAL_MPQ_H */
