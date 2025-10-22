#if !defined (BAV_TERM_H)
#   define BAV_TERM_H 1

#   include "bav_common.h"
#   include "bav_rank.h"
#   include "bav_point_int_p.h"
#   include "bav_parameter.h"
#   include "bav_point_interval_mpq.h"

BEGIN_C_DECLS

/*
 * texinfo: bav_term
 * A @dfn{term} is a product of ranks (the ranks of zero and of nonzero
 * constants are forbidden) sorted by decreasing order with respect to the
 * current ordering.
 * The empty product encodes the term @math{1}.
 * The leading rank of a nonempty product is the leading rank of the term.
 */

struct bav_term
{
// number of entries allocated to rg
  ba0_int_p alloc;
// number of entries used in rg
  ba0_int_p size;
// the array of ranks, by decreasing order with respect to the current ordering
  struct bav_rank *rg;
};

struct bav_listof_term
{
  struct bav_term *value;
  struct bav_listof_term *next;
};

struct bav_tableof_term
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bav_term **tab;
};

extern BAV_DLL void bav_realloc_term (
    struct bav_term *,
    ba0_int_p);

extern BAV_DLL void bav_init_term (
    struct bav_term *);

extern BAV_DLL struct bav_term *bav_new_term (
    void);

extern BAV_DLL void bav_set_term_one (
    struct bav_term *);

extern BAV_DLL void bav_set_term_variable (
    struct bav_term *,
    struct bav_variable *,
    bav_Idegree);

extern BAV_DLL void bav_set_term_rank (
    struct bav_term *,
    struct bav_rank *);

extern BAV_DLL void bav_set_term (
    struct bav_term *,
    struct bav_term *);

extern BAV_DLL void bav_set_tableof_term (
    struct bav_tableof_term *,
    struct bav_tableof_term *);

extern BAV_DLL void bav_lcm_tableof_term (
    struct bav_tableof_term *,
    struct bav_tableof_term *,
    struct bav_tableof_term *);

extern BAV_DLL void bav_shift_term (
    struct bav_term *,
    struct bav_term *);

extern BAV_DLL void bav_strip_term (
    struct bav_term *,
    struct bav_term *,
    bav_Inumber);

extern BAV_DLL bool bav_is_one_term (
    struct bav_term *);

extern BAV_DLL struct bav_variable *bav_leader_term (
    struct bav_term *);

extern BAV_DLL bav_Idegree bav_leading_degree_term (
    struct bav_term *);

extern BAV_DLL bav_Idegree bav_total_degree_term (
    struct bav_term *);

extern BAV_DLL bav_Idegree bav_degree_term (
    struct bav_term *,
    struct bav_variable *);

extern BAV_DLL bav_Iorder bav_total_order_term (
    struct bav_term *);

extern BAV_DLL bav_Idegree bav_maximal_degree_term (
    struct bav_term *);

extern BAV_DLL struct bav_rank bav_leading_rank_term (
    struct bav_term *);

extern BAV_DLL bool bav_disjoint_term (
    struct bav_term *,
    struct bav_term *);

extern BAV_DLL bool bav_equal_term (
    struct bav_term *,
    struct bav_term *);

extern BAV_DLL bool bav_gt_term (
    struct bav_term *,
    struct bav_term *);

extern BAV_DLL bool bav_lt_term (
    struct bav_term *,
    struct bav_term *);

extern BAV_DLL void bav_sort_term (
    struct bav_term *);

extern BAV_DLL void bav_sort_tableof_term (
    struct bav_tableof_term *);

extern BAV_DLL void bav_lcm_term (
    struct bav_term *,
    struct bav_term *,
    struct bav_term *);

extern BAV_DLL void bav_gcd_term (
    struct bav_term *,
    struct bav_term *,
    struct bav_term *);

extern BAV_DLL void bav_mul_term (
    struct bav_term *,
    struct bav_term *,
    struct bav_term *);

extern BAV_DLL void bav_mul_term_rank (
    struct bav_term *,
    struct bav_term *,
    struct bav_rank *);

extern BAV_DLL void bav_mul_term_variable (
    struct bav_term *,
    struct bav_term *,
    struct bav_variable *,
    bav_Idegree);

extern BAV_DLL void bav_pow_term (
    struct bav_term *,
    struct bav_term *,
    bav_Idegree);

extern BAV_DLL void bav_exquo_term (
    struct bav_term *,
    struct bav_term *,
    struct bav_term *);

extern BAV_DLL void bav_exquo_term_variable (
    struct bav_term *,
    struct bav_term *,
    struct bav_variable *,
    bav_Idegree);

extern BAV_DLL bool bav_is_factor_term (
    struct bav_term *,
    struct bav_term *,
    struct bav_term *);

extern BAV_DLL void bav_diff_term (
    struct bav_term *,
    struct bav_term *,
    struct bav_symbol *);

extern BAV_DLL void bav_set_term_tableof_variable (
    struct bav_term *,
    struct bav_tableof_variable *,
    struct ba0_tableof_int_p *);

extern BAV_DLL void bav_term_at_point_int_p (
    ba0_mpz_t,
    struct bav_term *,
    struct bav_point_int_p *);

extern BAV_DLL void bav_term_at_point_interval_mpq (
    struct ba0_interval_mpq *,
    struct bav_term *,
    struct bav_point_interval_mpq *);

extern BAV_DLL ba0_garbage1_function bav_garbage1_term;

extern BAV_DLL ba0_garbage2_function bav_garbage2_term;

extern BAV_DLL ba0_scanf_function bav_scanf_term;

extern BAV_DLL ba0_printf_function bav_printf_term;

extern BAV_DLL ba0_copy_function bav_copy_term;

struct bav_differential_ring;

extern BAV_DLL void bav_switch_ring_term (
    struct bav_term *,
    struct bav_differential_ring *);

extern BAV_DLL bool bav_depends_on_zero_derivatives_of_parameter_term (
    struct bav_term *);

END_C_DECLS
#endif /* !BAV_TERM_H */
