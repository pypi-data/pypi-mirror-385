#if !defined (BA0_MATRIX_H)
#   define BA0_MATRIX_H 1

#   include "ba0_common.h"

BEGIN_C_DECLS

struct ba0_matrix
{
  ba0_int_p alloc;
  ba0_int_p nrow;
  ba0_int_p ncol;
  void **entry;
};


#   define BA0_MAT(M,i,j) (M)->entry [(M)->ncol*  (i) + j]

extern BA0_DLL void ba0_realloc_matrix (
    struct ba0_matrix *,
    ba0_int_p,
    ba0_int_p);

extern BA0_DLL void ba0_realloc2_matrix (
    struct ba0_matrix *,
    ba0_int_p,
    ba0_int_p,
    ba0_new_function *);

extern BA0_DLL void ba0_init_matrix (
    struct ba0_matrix *);

extern BA0_DLL void ba0_reset_matrix (
    struct ba0_matrix *);

extern BA0_DLL struct ba0_matrix *ba0_new_matrix (
    void);

extern BA0_DLL void ba0_set_matrix_unity (
    struct ba0_matrix *,
    ba0_int_p,
    ba0_new_function *,
    ba0_unary_operation *,
    ba0_unary_operation *);

extern BA0_DLL void ba0_set_matrix (
    struct ba0_matrix *,
    struct ba0_matrix *);

extern BA0_DLL void ba0_set_matrix2 (
    struct ba0_matrix *,
    struct ba0_matrix *,
    ba0_new_function *,
    ba0_binary_operation *);

extern BA0_DLL void ba0_set_matrix_unity (
    struct ba0_matrix *,
    ba0_int_p,
    ba0_new_function *,
    ba0_unary_operation *,
    ba0_unary_operation *);

extern BA0_DLL bool ba0_is_zero_matrix (
    struct ba0_matrix *,
    ba0_unary_predicate *);

extern BA0_DLL bool ba0_is_unity_matrix (
    struct ba0_matrix *,
    ba0_unary_predicate *,
    ba0_unary_predicate *);

extern BA0_DLL void ba0_swap_rows_matrix (
    struct ba0_matrix *,
    ba0_int_p,
    ba0_int_p);

extern BA0_DLL void ba0_swap_columns_matrix (
    struct ba0_matrix *,
    ba0_int_p,
    ba0_int_p);

extern BA0_DLL void ba0_add_matrix (
    struct ba0_matrix *,
    struct ba0_matrix *,
    struct ba0_matrix *,
    ba0_new_function *,
    ba0_ternary_operation *);

extern BA0_DLL void ba0_mul_matrix (
    struct ba0_matrix *,
    struct ba0_matrix *,
    struct ba0_matrix *,
    ba0_new_function *,
    ba0_unary_operation *,
    ba0_binary_operation *,
    ba0_ternary_operation *,
    ba0_ternary_operation *);

END_C_DECLS
#endif /* !BA0_MATRIX_H */
