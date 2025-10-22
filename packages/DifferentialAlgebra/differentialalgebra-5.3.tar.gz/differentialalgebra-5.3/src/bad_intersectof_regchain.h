#if !defined (BAD_INTERSECTOF_REGCHAIN_H)
#   define BAD_INTERSECTOF_REGCHAIN_H 1

#   include "bad_common.h"
#   include "bad_regchain.h"
#   include "bad_reduction.h"
#   include "bad_base_field.h"

BEGIN_C_DECLS

/*
 * texinfo: bad_intersectof_regchain
 * This data structure mostly is a table a regular chain.
 * Mathematically, the ideal that it represents is the intersection
 * of the ideals defined by the chains.
 */

struct bad_intersectof_regchain
{
  struct bad_attchain attrib;
  struct bad_tableof_regchain inter;
};


extern BAD_DLL void bad_init_intersectof_regchain (
    struct bad_intersectof_regchain *);

extern BAD_DLL void bad_reset_intersectof_regchain (
    struct bad_intersectof_regchain *);

extern BAD_DLL struct bad_intersectof_regchain *bad_new_intersectof_regchain (
    void);

extern BAD_DLL void bad_realloc_intersectof_regchain (
    struct bad_intersectof_regchain *,
    ba0_int_p);

extern BAD_DLL void bad_set_intersectof_regchain_regchain (
    struct bad_intersectof_regchain *,
    struct bad_regchain *);

extern BAD_DLL void bad_append_intersectof_regchain_regchain (
    struct bad_intersectof_regchain *,
    struct bad_regchain *);

extern BAD_DLL void bad_append_intersectof_regchain (
    struct bad_intersectof_regchain *,
    struct bad_intersectof_regchain *);

extern BAD_DLL void bad_set_intersectof_regchain (
    struct bad_intersectof_regchain *,
    struct bad_intersectof_regchain *);

extern BAD_DLL void bad_set_property_intersectof_regchain (
    struct bad_intersectof_regchain *,
    enum bad_property_attchain);

extern BAD_DLL void bad_clear_property_intersectof_regchain (
    struct bad_intersectof_regchain *,
    enum bad_property_attchain);

extern BAD_DLL void bad_set_properties_intersectof_regchain (
    struct bad_intersectof_regchain *,
    struct ba0_tableof_string *);

extern BAD_DLL void bad_set_automatic_properties_intersectof_regchain (
    struct bad_intersectof_regchain *);

extern BAD_DLL bool bad_has_property_intersectof_regchain (
    struct bad_intersectof_regchain *,
    enum bad_property_attchain);

extern BAD_DLL void bad_properties_intersectof_regchain (
    struct ba0_tableof_string *,
    struct bad_intersectof_regchain *);

extern BAD_DLL struct bad_regchain *bad_get_regchain_intersectof_regchain (
    struct bad_intersectof_regchain *,
    ba0_int_p);

extern BAD_DLL void bad_sort_intersectof_regchain (
    struct bad_intersectof_regchain *,
    struct bad_intersectof_regchain *);

extern BAD_DLL void bad_remove_redundant_components_intersectof_regchain (
    struct bad_intersectof_regchain *,
    struct bad_intersectof_regchain *,
    struct bad_base_field *);

extern BAD_DLL void bad_fast_primality_test_intersectof_regchain (
    struct bad_intersectof_regchain *);

extern BAD_DLL ba0_scanf_function bad_scanf_intersectof_regchain;

extern BAD_DLL ba0_scanf_function bad_scanf_intersectof_pretend_regchain;

extern BAD_DLL ba0_printf_function bad_printf_intersectof_regchain;

extern BAD_DLL ba0_printf_function bad_printf_intersectof_regchain_equations;

extern BAD_DLL ba0_garbage1_function bad_garbage1_intersectof_regchain;

extern BAD_DLL ba0_garbage2_function bad_garbage2_intersectof_regchain;

extern BAD_DLL ba0_copy_function bad_copy_intersectof_regchain;

END_C_DECLS
#endif /* !BAD_INTERSECTOF_REGCHAIN_H */
