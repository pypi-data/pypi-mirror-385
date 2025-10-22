#if ! defined (BA0_INTERVAL_MPQ_H)
#   define BA0_INTERVAL_MPQ_H 1

#   include "ba0_common.h"
#   include "ba0_gmp.h"
#   include "ba0_macros_mpq.h"

BEGIN_C_DECLS

enum ba0_typeof_interval
{
  ba0_closed_interval,
  ba0_open_interval,
  ba0_empty_interval,
  ba0_infinite_interval,
  ba0_left_infinite_interval,
  ba0_right_infinite_interval
};

struct ba0_interval_mpq
{
  ba0_mpq_t a;
  ba0_mpq_t b;
  enum ba0_typeof_interval type;
};


struct ba0_tableof_interval_mpq
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct ba0_interval_mpq **tab;
};


struct ba0_listof_interval_mpq
{
  struct ba0_interval_mpq *value;
  struct ba0_listof_interval_mpq *next;
};


extern BA0_DLL bool ba0_domain_interval_mpq (
    void);

extern BA0_DLL void ba0_init_interval_mpq (
    struct ba0_interval_mpq *);

extern BA0_DLL struct ba0_interval_mpq *ba0_new_interval_mpq (
    void);

extern BA0_DLL void ba0_set_interval_mpq_si (
    struct ba0_interval_mpq *,
    ba0_int_p);

extern BA0_DLL void ba0_set_interval_mpq_ui (
    struct ba0_interval_mpq *,
    unsigned ba0_int_p);

extern BA0_DLL void ba0_set_interval_mpq_double (
    struct ba0_interval_mpq *,
    double);

extern BA0_DLL void ba0_set_interval_mpq_mpq (
    struct ba0_interval_mpq *,
    ba0_mpq_t,
    ba0_mpq_t);

extern BA0_DLL void ba0_set_interval_mpq_type_mpq (
    struct ba0_interval_mpq *,
    enum ba0_typeof_interval,
    ba0_mpq_t,
    ba0_mpq_t);

extern BA0_DLL void ba0_set_interval_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_is_empty_interval_mpq (
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_is_closed_interval_mpq (
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_is_open_interval_mpq (
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_is_unbounded_interval_mpq (
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_is_zero_interval_mpq (
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_is_one_interval_mpq (
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_are_equal_interval_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_contains_zero_interval_mpq (
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_is_positive_interval_mpq (
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_is_negative_interval_mpq (
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_is_nonpositive_interval_mpq (
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_is_nonnegative_interval_mpq (
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_is_less_interval_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_are_disjoint_interval_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_member_interval_mpq (
    ba0_mpq_t,
    struct ba0_interval_mpq *);

extern BA0_DLL bool ba0_is_subset_interval_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_element_interval_mpq (
    ba0_mpq_t,
    struct ba0_interval_mpq *,
    unsigned ba0_int_p);

extern BA0_DLL void ba0_middle_interval_mpq (
    ba0_mpq_t,
    struct ba0_interval_mpq *);

extern BA0_DLL double ba0_middle_interval_mpq_double (
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_width_interval_mpq (
    ba0_mpq_t,
    struct ba0_interval_mpq *);

extern BA0_DLL double ba0_width_interval_mpq_double (
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_middle_interval_mpq (
    ba0_mpq_t,
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_intersect_interval_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_abs_interval_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_neg_interval_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_add_interval_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_add_interval_mpq_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *,
    ba0_mpq_t);

extern BA0_DLL void ba0_sub_interval_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_sub_mpq_interval_mpq (
    struct ba0_interval_mpq *,
    ba0_mpq_t,
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_sub_interval_mpq_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *,
    ba0_mpq_t);

extern BA0_DLL void ba0_mul_interval_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_mul_interval_mpq_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *,
    ba0_mpq_t);

extern BA0_DLL void ba0_mul_interval_mpq_si (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *,
    ba0_int_p);

extern BA0_DLL void ba0_mul_interval_mpq_ui (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *,
    unsigned ba0_int_p);

extern BA0_DLL void ba0_pow_interval_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *,
    ba0_int_p);

extern BA0_DLL void ba0_pow_interval_mpq_mpq (
    struct ba0_interval_mpq *,
    ba0_mpq_t,
    ba0_int_p n);

extern BA0_DLL void ba0_div_interval_mpq (
    struct ba0_tableof_interval_mpq *,
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_div_mpq_interval_mpq (
    struct ba0_tableof_interval_mpq *,
    ba0_mpq_t,
    struct ba0_interval_mpq *);

extern BA0_DLL void ba0_div_interval_mpq_mpq (
    struct ba0_interval_mpq *,
    struct ba0_interval_mpq *,
    ba0_mpq_t);

extern BA0_DLL ba0_scanf_function ba0_scanf_interval_mpq;

extern BA0_DLL ba0_printf_function ba0_printf_interval_mpq;

extern BA0_DLL ba0_garbage1_function ba0_garbage1_interval_mpq;

extern BA0_DLL ba0_garbage2_function ba0_garbage2_interval_mpq;

extern BA0_DLL ba0_copy_function ba0_copy_interval_mpq;

END_C_DECLS
#endif
