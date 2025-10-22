#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_number_of_equations.h"

/*
 * EXPORTED
 * NumberOfEquations (regchain)
 */

ALGEB
bmi_number_of_equations (
    struct bmi_callback *callback)
{
  struct bad_regchain C;

  if (bmi_nops (callback) != 1)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_regchain_op (1, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRREGC);

  bmi_set_ordering_and_regchain (&C, 1, callback, __FILE__, __LINE__);

  {
    ALGEB res;
    char *stres;
    stres = ba0_new_printf ("%d", C.decision_system.size);
    bmi_push_maple_gmp_allocators ();
#if ! defined (BMI_BALSA)
    res = EvalMapleStatement (callback->kv, stres);
#else
    res = bmi_balsa_new_string (stres);
#endif
    bmi_pull_maple_gmp_allocators ();
    return res;
  }
}
