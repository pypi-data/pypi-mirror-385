#if ! defined (BA0_POINT_H)
#   define BA0_POINT_H 1

#   include "ba0_common.h"

BEGIN_C_DECLS

/*
 * texinfo: ba0_value
 * This data type permits to associate a value to a variable
 * (variables are defined in the @code{bav} library).
 *
 * It can be parsed and printed using formats of the form
 * @code{%value(%something)}. The input output syntax for values
 * is @code{var = value}. The equality sign can be customized
 * (see @code{ba0_set_settings_value}).
 */

struct ba0_value
{
  void *var;
  void *value;
};

#   define BA0_NOT_A_VALUE (struct ba0_value *)0

#   define BA0_NOT_A_VARIABLE 0

#   define BA0_POINT_OPER "="

/*
 * texinfo: ba0_point
 * This data type permits to associate values to many different variables.
 * It actually is a duplicate of @code{struct ba0_table} so that many
 * table functions may be applied to points.
 * Many functions require the @code{tab} field to be
 * sorted (see @code{ba0_sort_point}).
 *
 * It can be parsed and printed using formats of the form 
 * @code{%point(%something)} which is more precise than
 * @code{%t(%value(%something))} since parsed points are sorted
 * and tested against ambiguity (exception @code{BA0_ERRAMB} is
 * raised by the parser if the variables are not pairwise distinct).
 *
 * This data type gets specialized as @code{struct bav_point_int_p}
 * and @code{struct bav_point_interval_mpq} in the @code{bav} library
 * and as @code{baz_point_ratfrac} in the @code{baz} library.
 */

struct ba0_point
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct ba0_value **tab;
};


extern BA0_DLL void ba0_set_settings_value (
    char *);

extern BA0_DLL void ba0_get_settings_value (
    char **);

extern BA0_DLL void ba0_init_value (
    struct ba0_value *);

extern BA0_DLL struct ba0_value *ba0_new_value (
    void);

extern BA0_DLL void ba0_init_point (
    struct ba0_point *);

extern BA0_DLL struct ba0_point *ba0_new_point (
    void);

extern BA0_DLL void ba0_set_point (
    struct ba0_point *,
    struct ba0_point *);

extern BA0_DLL void ba0_sort_point (
    struct ba0_point *,
    struct ba0_point *);

extern BA0_DLL bool ba0_is_sorted_point (
    struct ba0_point *);

extern BA0_DLL bool ba0_is_ambiguous_point (
    struct ba0_point *);

extern BA0_DLL void ba0_delete_point (
    struct ba0_point *,
    struct ba0_point *,
    ba0_int_p);

extern BA0_DLL struct ba0_value *ba0_bsearch_point (
    void *,
    struct ba0_point *,
    ba0_int_p *);

extern BA0_DLL struct ba0_value *ba0_assoc_point (
    void *,
    struct ba0_point *,
    ba0_int_p *);

END_C_DECLS
#endif /* !BA0_POINT_H */
