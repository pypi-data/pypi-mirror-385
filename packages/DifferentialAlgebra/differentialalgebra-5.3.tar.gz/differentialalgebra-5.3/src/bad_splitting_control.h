#if !defined (BAD_SPLITTING_CONTROL_H)
#   define BAD_SPLITTING_CONTROL_H 1

#   include "bad_common.h"
#   include "bad_regchain.h"

BEGIN_C_DECLS

/*
 * texinfo: bad_typeof_dimension_lower_bound
 * This data type permits to specify to differential elimination
 * algorithms the type of dimension lower bound to be applied.
 * Such a lower bound permits to cut any branch of the splitting
 * tree leading to regular chains of differential dimension
 * strictly less than the number of input equations.
 * Note that such a strategy is proved in the algebraic case
 * and in the case of a single differential equation.
 * The other cases are conjectural.
 */

enum bad_typeof_dimension_lower_bound
{
// do not take into account any dimension lower bound
  bad_no_dimension_lower_bound,
// apply it in the case of a non-differential system
  bad_algebraic_dimension_lower_bound,
// apply it in the case of an ordinary differential system
  bad_ode_dimension_lower_bound,
// apply it in the case of a partial differential system
  bad_pde_dimension_lower_bound
};

/* 
 * texinfo: bad_splitting_control
 * This data type permits to specify a splitting control strategy
 * to differential elimination algorithms.
 * 
 * The field @code{first_leaf_only} indicates if the differential
 * elimination process must stop at the first consistent regular
 * chain obtained. Default value is @code{false}.
 *
 * The field @code{dimlb} indicates the type of dimension argument
 * that should be taken into account. Default value is
 * @code{bad_algebraic_dimension_lower_bound}.
 *
 * The field @code{apply_dimlb_one_eq} indicates if the case of
 * a single input equation should be considered specifically (provided
 * that @code{dimlb} is different from @code{bad_no_dimension_lower_bound}).
 * If set to @code{true}, branches of the splitting tree leading to
 * regular chains of differential dimension strictly less than the 
 * number of input equations (which is then equal to @math{1}) are discarded.
 * Default value is @code{true}.
 *
 * The field @code{DenefLipshitz} indicates if we are performing the
 * differential elimination stage of @code{bas_DenefLipshitz}. If this
 * is the case, the other @code{first_leaf_only} and @code{apply_dimlb_one_eq}
 * are set to @code{false} and @code{dimlb} is set to 
 * @code{bad_no_dimension_lower_bound}. 
 * Moreover, the inequations are not used to discard quadruples before
 * the final algebraic processing.
 */

struct bad_splitting_control
{
// Stop at the first consistent regular chain (if any)
  bool first_leaf_only;
// Should a dimension lower bound be taken into account ?
  enum bad_typeof_dimension_lower_bound dimlb;
// Should the case of a single input equation be handled specifically?
  bool apply_dimlb_one_eq;
// Are we in the differential elimination stage of the DenefLipshitz algorithm?
  bool DenefLipshitz;
};

struct bad_base_field;

extern BAD_DLL void bad_init_splitting_control (
    struct bad_splitting_control *);

extern BAD_DLL struct bad_splitting_control *bad_new_splitting_control (
    void);

extern BAD_DLL void bad_set_splitting_control (
    struct bad_splitting_control *,
    struct bad_splitting_control *);

extern BAD_DLL void bad_set_first_leaf_only_splitting_control (
    struct bad_splitting_control *,
    bool);

extern BAD_DLL void bad_set_dimension_lower_bound_splitting_control (
    struct bad_splitting_control *,
    enum bad_typeof_dimension_lower_bound,
    bool);

extern BAD_DLL bool bad_apply_dimension_lower_bound_splitting_control (
    struct bad_splitting_control *,
    struct bad_regchain *,
    struct bap_listof_polynom_mpz *,
    struct bad_base_field *,
    bool,
    ba0_int_p *);

extern BAD_DLL void bad_set_DenefLipshitz_splitting_control (
    struct bad_splitting_control *,
    bool);

END_C_DECLS
#endif /* !BAD_SPLITTING_CONTROL_H */
