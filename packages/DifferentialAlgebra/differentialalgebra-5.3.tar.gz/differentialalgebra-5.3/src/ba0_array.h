#if !defined (BA0_ARRAY_H)
#   define BA0_ARRAY_H 1

#   include "ba0_common.h"

BEGIN_C_DECLS

struct ba0_array
{
  ba0_int_p alloc;
  ba0_int_p size;
  char *tab;
  ba0_int_p sizelt;
};


#   define BA0_ARRAY(A,i) ((A)->tab + (i)*  (A)->sizelt)

extern BA0_DLL void ba0_realloc_array (
    struct ba0_array *,
    ba0_int_p,
    ba0_int_p);

extern BA0_DLL void ba0_realloc2_array (
    struct ba0_array *,
    ba0_int_p,
    ba0_int_p,
    ba0_init_function *);

extern BA0_DLL void ba0_init_array (
    struct ba0_array *);

extern BA0_DLL void ba0_reset_array (
    struct ba0_array *);

extern BA0_DLL struct ba0_array *ba0_new_array (
    void);

extern BA0_DLL void ba0_set_array (
    struct ba0_array *,
    struct ba0_array *);

extern BA0_DLL void ba0_delete_array (
    struct ba0_array *,
    ba0_int_p);

extern BA0_DLL void ba0_reverse_array (
    struct ba0_array *,
    struct ba0_array *);

extern BA0_DLL void ba0_concat_array (
    struct ba0_array *,
    struct ba0_array *,
    struct ba0_array *);

END_C_DECLS
#endif /* ! BA0_ARRAY_H */
