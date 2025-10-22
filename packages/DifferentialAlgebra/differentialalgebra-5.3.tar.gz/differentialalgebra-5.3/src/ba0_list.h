#if !defined (BA0_LIST_H)
#   define BA0_LIST_H

#   include "ba0_common.h"

BEGIN_C_DECLS

struct ba0_list
{
  void *value;
  struct ba0_list *next;
};


extern BA0_DLL struct ba0_list *ba0_sort_list (
    struct ba0_list *,
    ba0_cmp_function *);

extern BA0_DLL struct ba0_list *ba0_sort2_list (
    struct ba0_list *,
    ba0_cmp2_function *,
    void *);

extern BA0_DLL struct ba0_list *ba0_select_list (
    struct ba0_list *,
    ba0_unary_predicate *);

extern BA0_DLL struct ba0_list *ba0_delete_list (
    struct ba0_list *,
    ba0_unary_predicate *);

extern BA0_DLL struct ba0_list *ba0_insert_list (
    void *,
    struct ba0_list *,
    ba0_cmp_function *);

extern BA0_DLL struct ba0_list *ba0_insert2_list (
    void *,
    struct ba0_list *,
    ba0_cmp2_function *,
    void *);

extern BA0_DLL bool ba0_member_list (
    void *,
    struct ba0_list *);

extern BA0_DLL void *ba0_last_list (
    struct ba0_list *);

extern BA0_DLL struct ba0_list *ba0_butlast_list (
    struct ba0_list *);

extern BA0_DLL struct ba0_list *ba0_copy_list (
    struct ba0_list *);

extern BA0_DLL struct ba0_list *ba0_cons_list (
    void *,
    struct ba0_list *);

extern BA0_DLL struct ba0_list *ba0_endcons_list (
    void *,
    struct ba0_list *);

extern BA0_DLL struct ba0_list *ba0_reverse_list (
    struct ba0_list *);

extern BA0_DLL struct ba0_list *ba0_concat_list (
    struct ba0_list *,
    struct ba0_list *);

extern BA0_DLL void ba0_move_to_head_list (
    struct ba0_list *,
    ba0_int_p);

extern BA0_DLL ba0_int_p ba0_length_list (
    struct ba0_list *);

extern BA0_DLL void *ba0_ith_list (
    struct ba0_list *,
    ba0_int_p);

extern BA0_DLL struct ba0_list *ba0_map_list (
    ba0_unary_function *,
    struct ba0_list *);

END_C_DECLS
#endif /* !BA0_LIST_H */
