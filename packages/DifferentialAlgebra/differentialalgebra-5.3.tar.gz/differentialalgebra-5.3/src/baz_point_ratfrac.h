#if ! defined (BAZ_POINT_RATFRAC_H)
#   define BAZ_POINT_RATFRAC_H

#   include "baz_ratfrac.h"
#   include "baz_prolongation_pattern.h"

BEGIN_C_DECLS

/*
 * texinfo: baz_value_ratfrac
 * This data type permits to associate a @code{baz_ratfrac} value
 * to a variable.
 */

struct baz_value_ratfrac
{
  struct bav_variable *var;
  struct baz_ratfrac *value;
};


/*
 * texinfo: baz_point_ratfrac
 * This data type is a particular case of the type @code{struct ba0_point}.
 * It permits to associate @code{baz_ratfrac} values to
 * many different variables. 
 * Many functions assume the @code{tab} field to be sorted
 * (see @code{ba0_sort_point}).
 * They can be parsed using @code{ba0_scanf/%point(%Qz)} and
 * printed by @code{ba0_printf/%point(%Qz)}.
 */

struct baz_point_ratfrac
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct baz_value_ratfrac **tab;
};

extern BAZ_DLL void baz_init_value_ratfrac (
    struct baz_value_ratfrac *);

extern BAZ_DLL struct baz_value_ratfrac *baz_new_value_ratfrac (
    void);

extern BAZ_DLL void baz_set_value_ratfrac (
    struct baz_value_ratfrac *,
    struct baz_value_ratfrac *);

extern BAZ_DLL void baz_set_point_ratfrac (
    struct baz_point_ratfrac *,
    struct baz_point_ratfrac *);

extern BAZ_DLL void baz_prolongate_point_ratfrac_variable (
    struct baz_point_ratfrac *,
    struct baz_point_ratfrac *,
    struct bav_variable *);

extern BAZ_DLL void baz_prolongate_point_ratfrac_term (
    struct baz_point_ratfrac *,
    struct baz_point_ratfrac *,
    struct bav_term *);

extern BAZ_DLL void baz_prolongate_point_ratfrac_using_pattern_variable (
    struct baz_point_ratfrac *,
    struct baz_point_ratfrac *,
    struct baz_prolongation_pattern *,
    struct bav_variable *);

extern BAZ_DLL void baz_prolongate_point_ratfrac_using_pattern_term (
    struct baz_point_ratfrac *,
    struct baz_point_ratfrac *,
    struct baz_prolongation_pattern *,
    struct bav_term *);

END_C_DECLS
#endif /* !BAZ_POINT_RATFRAC_H */
