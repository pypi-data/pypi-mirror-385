#if !defined (BA0_RANGE_INDEXED_GROUP)
#   define BA0_RANGE_INDEXED_GROUP 1

#   include "ba0_common.h"
#   include "ba0_double.h"
#   include "ba0_string.h"

BEGIN_C_DECLS

/*
 * texinfo: ba0_range_indexed_group
 * This data structure permits to describe a group of 
 * @dfn{range indexed strings}, which are strings indexed by integer numbers 
 * running over ranges. These strings (without their indices) are called
 * the @dfn{radicals} of the range indexed strings.
 * The arrays @code{lhs} and @code{rhs} have the same size, which
 * give the number of @dfn{range indices}.
 * Though stored in doubles, the left-hand and right-hand sides
 * of the ranges are either signed integers or @code{inf} or @code{-inf}.
 * The left-hand side of a range may be greater than, equal to or
 * lower than the right-hand side.
 * Here are a few examples: 
 * @verbatim
 * 1. y
 * 2. (x)[17:-3]
 * 3. (y,z)[0:inf,inf:-1]
 * @end verbatim
 * The radicals of the range indexed strings are @code{y}, @code{x}, 
 * @code{y} and @code{z}.
 * In Example 1, the range indexed group involves a single
 * range indexed string which has no range indices.
 * The range indexed group is said to describe a @dfn{plain string}.
 * In Example 2, the range indexed group involves a single
 * range indexed string which has a single range index.
 * In Example 3, the range indexed group involves two
 * range indexed strings; each of them admits two range indices.
 *
 * The aim of this data structure is to describe possibly infinite
 * ordered sets of variables. 
 * The range indexed group of Example 2
 * describes the ordered set: @code{x[17] > x[16] > ... > x[-2]} 
 * (the least index of the range is assumed to be excluded, as in Python,
 *  but this behaviour can be customized).
 * The variable @code{x[16]} is said to @dfn{fit} the range indexed string
 * @code{(x)[17:-3]}. The variables @code{x[18]} or @code{z[0]} do not.
 * In Example 3, the set of variables which fit the range indexed group is 
 * made of @code{y} and @code{z}, indexed by two nonnegative integers.
 */

struct ba0_range_indexed_group
{
// The left-hand sides of the ranges
  struct ba0_arrayof_double lhs;
// The right-hand sides of the ranges
  struct ba0_arrayof_double rhs;
// The table of the radicals of the range indexed strings
  struct ba0_tableof_string strs;
};

#   define BA0_NOT_A_RANGE_INDEXED_GROUP (struct ba0_range_indexed_group *)0

struct ba0_tableof_range_indexed_group
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct ba0_range_indexed_group **tab;
};

/*
 * Default values for entries in ba0_initialized_global
 */

#   define BA0_RANGE_INDEXED_GROUP_OPER ":"
#   define BA0_RANGE_INDEXED_GROUP_INFINITY "inf"

struct ba0_dictionary_string;

extern BA0_DLL void ba0_set_settings_range_indexed_group (
    char *,
    char *,
    bool,
    bool);

extern BA0_DLL void ba0_get_settings_range_indexed_group (
    char **,
    char **,
    bool *,
    bool *);

extern BA0_DLL unsigned ba0_int_p ba0_sizeof_range_indexed_group (
    struct ba0_range_indexed_group *,
    enum ba0_garbage_code,
    bool);

extern BA0_DLL unsigned ba0_int_p ba0_sizeof_tableof_range_indexed_group (
    struct ba0_tableof_range_indexed_group *,
    enum ba0_garbage_code,
    bool);

extern BA0_DLL void ba0_set_tableof_string_tableof_range_indexed_group (
    struct ba0_tableof_string *,
    struct ba0_tableof_range_indexed_group *);

extern BA0_DLL void ba0_set_range_indexed_group_with_tableof_string (
    struct ba0_range_indexed_group *,
    struct ba0_range_indexed_group *,
    struct ba0_dictionary_string *,
    struct ba0_tableof_string *);

extern BA0_DLL void ba0_set_tableof_range_indexed_group_with_tableof_string (
    struct ba0_tableof_range_indexed_group *,
    struct ba0_tableof_range_indexed_group *,
    struct ba0_dictionary_string *,
    struct ba0_tableof_string *);

extern BA0_DLL void ba0_init_range_indexed_group (
    struct ba0_range_indexed_group *);

extern BA0_DLL void ba0_reset_range_indexed_group (
    struct ba0_range_indexed_group *);

extern BA0_DLL struct ba0_range_indexed_group *ba0_new_range_indexed_group (
    void);

extern BA0_DLL void ba0_set_range_indexed_group (
    struct ba0_range_indexed_group *,
    struct ba0_range_indexed_group *);

extern BA0_DLL void ba0_set_range_indexed_group_string (
    struct ba0_range_indexed_group *,
    char *);

extern BA0_DLL bool ba0_is_plain_string_range_indexed_group (
    struct ba0_range_indexed_group *,
    char **);

extern BA0_DLL bool ba0_compatible_indices_range_indexed_group (
    struct ba0_range_indexed_group *,
    struct ba0_range_indexed_group *);

extern BA0_DLL bool ba0_fit_range_indexed_group (
    struct ba0_range_indexed_group *,
    char *,
    struct ba0_tableof_int_p *,
    ba0_int_p *);

extern BA0_DLL bool ba0_fit_indices_range_indexed_group (
    struct ba0_range_indexed_group *,
    struct ba0_tableof_int_p *);

extern BA0_DLL ba0_garbage1_function ba0_garbage1_range_indexed_group;

extern BA0_DLL ba0_garbage2_function ba0_garbage2_range_indexed_group;

extern BA0_DLL ba0_copy_function ba0_copy_range_indexed_group;

extern BA0_DLL ba0_scanf_function ba0_scanf_range_indexed_group;

extern BA0_DLL ba0_printf_function ba0_printf_range_indexed_group;

END_C_DECLS
#endif /* !BA0_RANGE_INDEXED_GROUP */
