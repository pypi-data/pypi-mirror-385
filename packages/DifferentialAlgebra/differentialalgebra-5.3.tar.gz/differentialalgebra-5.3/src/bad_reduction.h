#if !defined (BAD_REDUCTION_H)
#   define BAD_REDUCTION_H 1

#   include "bad_common.h"
#   include "bad_regchain.h"
#   include "bad_base_field.h"

BEGIN_C_DECLS

/*
 * texinfo: bad_typeof_reduction
 * This data type permits to specify to reduction algorithms
 * the type of reduction to be performed.
 */

enum bad_typeof_reduction
{
  bad_full_reduction,
  bad_partial_reduction,
// no derivation is performed
  bad_algebraic_reduction
};

/*
 * texinfo: bad_typeof_derivative_to_reduce
 * This data type permits to indicate to reduction algorithms if
 * all derivatives have to be reduced or if the leading derivative
 * has to be preserved.
 */

enum bad_typeof_derivative_to_reduce
{
  bad_all_derivatives_to_reduce,
  bad_all_but_leader_to_reduce
};

/*
 * texinfo: bad_typeof_reduction_strategy
 * This data type permits to choose the method carried out by
 * the reduction algorithm.
 */

enum bad_typeof_reduction_strategy
{
// the polynomial to be reduced is factored/easy then reduction is performed factorwise and 
// gcd are computed to reduce power products of initial and separants involved in the process
// - default value
  bad_gcd_prem_and_factor_reduction_strategy,
// basic strategy
  bad_prem_reduction_strategy,
// a change of ordering is performed first in order
// to reduce polynomials coefficient per coefficient
  bad_prem_and_change_of_ordering_reduction_strategy,
};

/*
 * texinfo: bad_typeof_redzero_strategy
 * This data type permits to choose the method carried out by
 * the algorithms designed for testing if a differential polynomial
 * gets reduced to zero or not.
 */

enum bad_typeof_redzero_strategy
{
// the result is guaranteed - default value
  bad_deterministic_using_probabilistic_redzero_strategy,
// perform reduction and test if the result is zero
  bad_deterministic_redzero_strategy,
// the result is not guaranteed
  bad_probabilistic_redzero_strategy
};

/*
 * texinfo: bad_typeof_inclusion_test_result
 * This data type provides a return code after an inclusion
 * test between ideals presented by regular chains.
 */

enum bad_typeof_inclusion_test_result
{
  bad_inclusion_test_positive,
  bad_inclusion_test_negative,
  bad_inclusion_test_uncertain
};

extern BAD_DLL void bad_set_settings_reduction (
    enum bad_typeof_reduction_strategy,
    enum bad_typeof_redzero_strategy,
    ba0_int_p);

extern BAD_DLL void bad_get_settings_reduction (
    enum bad_typeof_reduction_strategy *,
    enum bad_typeof_redzero_strategy *,
    ba0_int_p *);

extern BAD_DLL void bad_reset_theta (
    struct bav_tableof_term *,
    struct bad_regchain *);

extern BAD_DLL void bad_reduce_easy_polynom_by_regchain (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bad_regchain *,
    enum bad_typeof_reduction);

extern BAD_DLL void bad_ensure_nonzero_initial_mod_regchain (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bad_regchain *,
    enum bad_typeof_reduction);

extern BAD_DLL void bad_reduce_polynom_by_regchain (
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bav_tableof_term *,
    struct bap_polynom_mpz *,
    struct bad_regchain *,
    enum bad_typeof_reduction,
    enum bad_typeof_derivative_to_reduce);

extern BAD_DLL void bad_reduce_product_by_regchain (
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bav_tableof_term *,
    struct bap_product_mpz *,
    struct bad_regchain *,
    enum bad_typeof_reduction,
    enum bad_typeof_derivative_to_reduce);

extern BAD_DLL bool bad_is_a_reduced_to_zero_polynom_by_regchain (
    struct bap_polynom_mpz *,
    struct bad_regchain *,
    enum bad_typeof_reduction);

extern BAD_DLL enum bad_typeof_inclusion_test_result bad_is_included_regchain (
    struct bad_regchain *,
    struct bad_regchain *,
    struct bad_base_field *);

extern BAD_DLL bool bad_is_a_reducible_polynom_by_regchain (
    struct bap_polynom_mpz *,
    struct bad_regchain *,
    enum bad_typeof_reduction,
    enum bad_typeof_derivative_to_reduce,
    struct bav_rank *,
    ba0_int_p *);

extern BAD_DLL bool bad_is_a_reducible_product_by_regchain (
    struct bap_product_mpz *,
    struct bad_regchain *,
    enum bad_typeof_reduction,
    enum bad_typeof_derivative_to_reduce,
    ba0_int_p *);

extern BAD_DLL bool bad_is_a_partially_reduced_polynom_wrt_regchain (
    struct bap_polynom_mpz *,
    struct bad_regchain *);

END_C_DECLS
#endif /* !BAD_REDUCTION_H */
