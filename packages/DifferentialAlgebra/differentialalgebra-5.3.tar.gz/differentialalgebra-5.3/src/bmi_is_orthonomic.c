#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_is_orthonomic.h"

/*
 * EXPORTED
 * IsOrthonomic (regchain, bool)
 *
 * bool = true: generalized definition
 *        false: strict definition
 *
 * returns a list of boolean
 *
 * FIX ME: a base field should be passed as a parameter
 */

ALGEB
bmi_is_orthonomic (
    struct bmi_callback *callback)
{
  struct bad_base_field *K;
  struct bad_regchain C;
  bool generalizeddef, b;

  if (bmi_nops (callback) != 2)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_regchain_op (1, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRREGC);

  bmi_set_ordering_and_regchain (&C, 1, callback, __FILE__, __LINE__);

  generalizeddef = bmi_bool_op (2, callback);

  K = bad_new_base_field ();

  if (generalizeddef)
    b = bad_is_explicit_regchain (&C);
  else
    b = bad_is_orthonomic_regchain (&C, K);

  {
    ALGEB res;
    bmi_push_maple_gmp_allocators ();
    res = ToMapleBoolean (callback->kv, (long) b);
    bmi_pull_maple_gmp_allocators ();
    return res;
  }
}
