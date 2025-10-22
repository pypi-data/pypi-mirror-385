#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_attributes.h"

/*
 * EXPORTED
 */

ALGEB
bmi_attributes (
    struct bmi_callback *callback)
{
  struct bad_regchain C;
  struct ba0_tableof_string prop;
  char *stres;
  ALGEB res;

  if (bmi_nops (callback) != 1)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_regchain_op (1, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRREGC);

  bmi_set_ordering_and_regchain (&C, 1, callback, __FILE__, __LINE__);

  ba0_init_table ((struct ba0_table *) &prop);
  bad_properties_attchain (&prop, &C.attrib);

  stres = ba0_new_printf ("%t[%s]", &prop);
  bmi_push_maple_gmp_allocators ();
#if ! defined (BMI_BALSA)
  res = EvalMapleStatement (callback->kv, stres);
#else
  res = bmi_balsa_new_string (stres);
#endif
  bmi_pull_maple_gmp_allocators ();
  return res;
}
