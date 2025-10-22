#if !defined (BAV_POINT_INT_P_H)
#   define BAV_POINT_INT_P_H 1

#   include "bav_common.h"
#   include "bav_variable.h"

BEGIN_C_DECLS

/*
 * texinfo: bav_value_int_p
 * This data type permits to associate a @code{ba0_int_p} value
 * to a variable. It can be parsed and printed using the
 * format @code{%value(%d)}.
 */

struct bav_value_int_p
{
  struct bav_variable *var;
  ba0_int_p value;
};


/*
 * texinfo: bav_point_int_p
 * This data type is a particular case of the type @code{struct ba0_point}.
 * It permits to associate @code{ba0_int_p} values to
 * many different variables. 
 * Many functions assume the @code{tab} field to be sorted
 * (see @code{ba0_sort_point}).
 * They can be parsed using @code{ba0_scanf/%point(%d)} and
 * printed by @code{ba0_printf/%point(%d)}.
 */

struct bav_point_int_p
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bav_value_int_p **tab;
};


END_C_DECLS
#endif /* !BAV_POINT_INT_P_H */
