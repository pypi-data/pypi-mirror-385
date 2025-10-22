#if !defined (BA0_TABLE_H)
#   define BA0_TABLE_H 1

#   include "ba0_common.h"

BEGIN_C_DECLS

struct ba0_table
{
  ba0_int_p alloc;
  ba0_int_p size;
  void **tab;
};

struct ba0_tableof_table
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct ba0_table **tab;
};

extern BA0_DLL unsigned ba0_int_p ba0_sizeof_table (
    struct ba0_table *,
    enum ba0_garbage_code);

extern BA0_DLL void ba0_re_malloc_table (
    struct ba0_table *,
    ba0_int_p);

extern BA0_DLL void ba0_realloc_table (
    struct ba0_table *,
    ba0_int_p);

extern BA0_DLL void ba0_realloc2_table (
    struct ba0_table *,
    ba0_int_p,
    ba0_new_function *);

extern BA0_DLL void ba0_init_table (
    struct ba0_table *);

extern BA0_DLL void ba0_reset_table (
    struct ba0_table *);

extern BA0_DLL struct ba0_table *ba0_new_table (
    void);

extern BA0_DLL void ba0_set_table (
    struct ba0_table *,
    struct ba0_table *);

extern BA0_DLL void ba0_set2_table (
    struct ba0_table *,
    struct ba0_table *,
    ba0_new_function *,
    ba0_set_function *);

extern BA0_DLL void ba0_delete_table (
    struct ba0_table *,
    ba0_int_p);

extern BA0_DLL void ba0_insert_table (
    struct ba0_table *,
    ba0_int_p,
    void *);

extern BA0_DLL bool ba0_member_table (
    void *,
    struct ba0_table *);

extern BA0_DLL bool ba0_member2_table (
    void *,
    struct ba0_table *,
    ba0_int_p *);

extern BA0_DLL bool ba0_equal_table (
    struct ba0_table *,
    struct ba0_table *);

extern BA0_DLL void ba0_sort_table (
    struct ba0_table *,
    struct ba0_table *);

extern BA0_DLL void ba0_unique_table (
    struct ba0_table *,
    struct ba0_table *);

extern BA0_DLL bool ba0_is_unique_table (
    struct ba0_table *);

extern BA0_DLL void ba0_reverse_table (
    struct ba0_table *,
    struct ba0_table *);

extern BA0_DLL void ba0_concat_table (
    struct ba0_table *,
    struct ba0_table *,
    struct ba0_table *);

extern BA0_DLL void ba0_move_to_tail_table (
    struct ba0_table *,
    struct ba0_table *,
    ba0_int_p);

extern BA0_DLL void ba0_move_from_tail_table (
    struct ba0_table *,
    struct ba0_table *,
    ba0_int_p);

struct ba0_list;

extern BA0_DLL void ba0_append_table_list (
    struct ba0_table *,
    struct ba0_list *);

extern BA0_DLL void ba0_set_table_list (
    struct ba0_table *,
    struct ba0_list *);

END_C_DECLS
#endif /* ! BA0_TABLE_H */
