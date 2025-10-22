#if !defined (BAP_POLYNOM_mpq_H)
#   define BAP_POLYNOM_mpq_H 1

#   include "bap_common.h"
#   include "bap_clot_mpq.h"
#   include "bap_sequential_access.h"
#   include "bap_indexed_access.h"
#   include "bap_termstripper.h"

#   define BAD_FLAG_mpq

BEGIN_C_DECLS

/*
 * texinfo: bap_polynom_mpq
 * This data type implements polynomials.
 * Note that the @code{total_rank} field contains the exact
 * total rank of the polynomial while the @code{total_rank} field 
 * of the term manager of its clot only contains a multiple
 * of this total rank.
 */

struct bap_polynom_mpq
{
  struct bap_clot_mpq *clot;  // the underlying clot
  struct bav_term total_rank;   // the total rank of the polynomial
  bool readonly;                // true if modifications are forbidden
  enum bap_typeof_monom_access access;
  struct bap_sequential_access seq;     // in case of a sequential access
  struct bap_indexed_access ind;        // in case of an indexed access
  struct bap_termstripper tstrip;       // for stripping terms
};


#   define BAP_NOT_A_POLYNOM_mpq	(struct bap_polynom_mpq*)0

struct bap_tableof_polynom_mpq
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bap_polynom_mpq **tab;
};

struct bap_listof_polynom_mpq
{
  struct bap_polynom_mpq *value;
  struct bap_listof_polynom_mpq *next;
};

struct bap_tableof_tableof_polynom_mpq
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bap_tableof_polynom_mpq **tab;
};

struct bap_tableof_listof_polynom_mpq
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bap_listof_polynom_mpq **tab;
};

extern BAP_DLL void bap_init_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_init_readonly_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_init_polynom_one_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_init_polynom_crk_mpq (
    struct bap_polynom_mpq *,
    ba0_mpq_t,
    struct bav_rank *);

extern BAP_DLL struct bap_polynom_mpq *bap_new_polynom_mpq (
    void);

extern BAP_DLL struct bap_polynom_mpq *bap_new_readonly_polynom_mpq (
    void);

extern BAP_DLL struct bap_polynom_mpq *bap_new_polynom_one_mpq (
    void);

extern BAP_DLL struct bap_polynom_mpq *bap_new_polynom_crk_mpq (
    ba0_mpq_t,
    struct bav_rank *);

extern BAP_DLL void bap_set_polynom_zero_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_set_polynom_one_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_set_polynom_crk_mpq (
    struct bap_polynom_mpq *,
    ba0_mpq_t,
    struct bav_rank *);

extern BAP_DLL void bap_set_polynom_variable_mpq (
    struct bap_polynom_mpq *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_set_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_set_tableof_polynom_mpq (
    struct bap_tableof_polynom_mpq *,
    struct bap_tableof_polynom_mpq *);

extern BAP_DLL void bap_set_tableof_tableof_polynom_mpq (
    struct bap_tableof_tableof_polynom_mpq *,
    struct bap_tableof_tableof_polynom_mpq *);

extern BAP_DLL void bap_set_readonly_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_set_polynom_term_mpq (
    struct bap_polynom_mpq *,
    struct bav_term *);

extern BAP_DLL void bap_set_polynom_monom_mpq (
    struct bap_polynom_mpq *,
    ba0_mpq_t,
    struct bav_term *);

extern BAP_DLL void bap_set_total_rank_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL bool bap_is_zero_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL bool bap_is_one_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL bool bap_is_numeric_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL bool bap_is_univariate_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL bool bap_depend_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL bool bap_depend_only_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bav_tableof_variable *);

extern BAP_DLL bool bap_is_variable_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL bool bap_is_solved_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL bool bap_is_derivative_minus_independent_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL bool bap_is_rank_minus_monom_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL bool bap_are_disjoint_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL enum ba0_compare_code bap_compare_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL bool bap_equal_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL ba0_cmp_function bap_gt_rank_polynom_mpq;

extern BAP_DLL ba0_cmp_function bap_lt_rank_polynom_mpq;

extern BAP_DLL bool bap_equal_rank_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL int bap_compare_rank_polynom_mpq (
    const void *,
    const void *);

extern BAP_DLL void bap_reverse_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_mark_indets_polynom_mpq (
    struct bav_dictionary_variable *,
    struct bav_tableof_variable *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_mark_indets_tableof_polynom_mpq (
    struct bav_dictionary_variable *,
    struct bav_tableof_variable *,
    struct bap_tableof_polynom_mpq *);

extern BAP_DLL void bap_mark_indets_listof_polynom_mpq (
    struct bav_dictionary_variable *,
    struct bav_tableof_variable *,
    struct bap_listof_polynom_mpq *);

extern BAP_DLL void bap_mark_ranks_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_sort_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_physort_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL ba0_int_p bap_nbmon_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_minimal_total_rank_polynom_mpq (
    struct bav_term *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_leading_term_polynom_mpq (
    struct bav_term *,
    struct bap_polynom_mpq *);

extern BAP_DLL struct bav_variable *bap_leader_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL struct bav_rank bap_rank_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL bav_Idegree bap_leading_degree_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL bav_Idegree bap_degree_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL bav_Idegree bap_total_degree_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL bav_Iorder bap_total_order_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL ba0_mpq_t *bap_numeric_initial_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_initial_and_reductum_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_initial_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_reductum_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_initial_and_reductum2_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL void bap_initial2_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL void bap_reductum2_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL void bap_coeff2_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_lcoeff_and_reductum_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL void bap_lcoeff_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL void bap_coeff_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_coeff_and_reductum_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_replace_initial_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_separant_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_separant2_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL void bap_sort_tableof_polynom_mpq (
    struct bap_tableof_polynom_mpq *,
    enum ba0_sort_mode);

extern BAP_DLL unsigned ba0_int_p bap_sizeof_polynom_mpq (
    struct bap_polynom_mpq *,
    enum ba0_garbage_code);

extern BAP_DLL void bap_switch_ring_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bav_differential_ring *);

extern BAP_DLL ba0_garbage1_function bap_garbage1_polynom_mpq;

extern BAP_DLL ba0_garbage2_function bap_garbage2_polynom_mpq;

extern BAP_DLL ba0_copy_function bap_copy_polynom_mpq;

END_C_DECLS
#   undef  BAD_FLAG_mpq
#endif /* !BAP_POLYNOM_mpq_H */
