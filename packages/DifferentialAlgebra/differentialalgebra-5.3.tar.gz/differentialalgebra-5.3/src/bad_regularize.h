#if !defined (BAD_REGULARIZE_H)
#   define BAD_REGULARIZE_H 1

#   include "bad_common.h"
#   include "bad_regchain.h"
#   include "bad_base_field.h"
#   include "bad_quadruple.h"

BEGIN_C_DECLS

/*
 * texinfo: bad_typeof_regularize_strategy
 * This data type permits to indicate to regularization algorithms
 * the strategy to be carried out. All tests are based on 
 * pseudoremainder sequence computations.
 */

enum bad_typeof_regularize_strategy
{
// Lionel Ducos algorithm is applied
  bad_subresultant_regularize_strategy = 1,
// pseudoremainders are computed using baz_gcd_pseudo_division_polynom_mpz
  bad_gcd_prem_regularize_strategy,
// pseudoremainders are computed factor per factor using
//  baz_gcd_pseudo_division_polynom_mpz
  bad_gcd_prem_and_factor_regularize_strategy
};

/*
 * texinfo: bad_typeof_Euclid
 * This data type permits to control the type of extended Euclidean
 * algorithm to be performed.
 */

enum bad_typeof_Euclid
{
  bad_basic_Euclid,
  bad_half_extended_Euclid,
  bad_extended_Euclid
};

/*
 * texinfo: bad_typeof_context
 * This data type indicates to regularization methods the context
 * from which they are called.
 */

enum bad_typeof_context
{
// from an algebraic inverse computation
  bad_inverse_context,
// from the PARDI algorithm (change of ordering on regular chains)
  bad_pardi_context,
// from the RosenfeldGroebner algorithm
  bad_rg_context
};

extern BAD_DLL void bad_set_settings_regularize (
    enum bad_typeof_regularize_strategy);

extern BAD_DLL void bad_get_settings_regularize (
    enum bad_typeof_regularize_strategy *);

extern BAD_DLL void bad_Euclid_mod_regchain (
    struct bap_tableof_tableof_polynom_mpz *,
    struct bad_tableof_quadruple *,
    enum bad_typeof_Euclid,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *,
    bool,
    bool,
    struct bad_regchain *,
    struct bad_base_field *,
    struct bap_polynom_mpz **);

extern BAD_DLL void bad_check_regularity_polynom_mod_regchain (
    struct bap_polynom_mpz *,
    struct bad_regchain *,
    struct bad_base_field *,
    struct bap_polynom_mpz **);

extern BAD_DLL void bad_reg_characteristic_regchain (
    struct bad_intersectof_regchain *,
    struct bap_listof_polynom_mpz *,
    struct bad_regchain *,
    struct bad_base_field *);

extern BAD_DLL void bad_normal_form_polynom_mod_regchain (
    struct baz_ratfrac *,
    struct bap_polynom_mpz *,
    struct bad_regchain *,
    struct bap_polynom_mpz **);

extern BAD_DLL void bad_normal_form_ratfrac_mod_regchain (
    struct baz_ratfrac *,
    struct baz_ratfrac *,
    struct bad_regchain *,
    struct bap_polynom_mpz **);

extern BAD_DLL void bad_normal_form_ratfrac_mod_intersectof_regchain (
    struct baz_tableof_ratfrac *,
    struct baz_ratfrac *,
    struct bad_intersectof_regchain *,
    struct bap_polynom_mpz **);

extern BAD_DLL void bad_normal_form_handling_exceptions_ratfrac_mod_regchain (
    struct baz_tableof_ratfrac *,
    struct bad_intersectof_regchain *,
    struct bad_intersectof_regchain *,
    struct baz_ratfrac *);

END_C_DECLS
#endif /* !BAD_REGULARIZE_H */
