#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_pretend_regchain.h"

/*
 * EXPORTED
 * PretendRegularDifferentialChain (equations, properties, 
 *                                          pretend, differential ring)
 */

ALGEB
bmi_pretend_regchain (
    struct bmi_callback *callback)
{
  struct bad_regchain C;
  struct ba0_tableof_string properties;
  ba0_int_p i;
  bool pretend;
  char *streqns, *strprop;

  if (bmi_nops (callback) != 4)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_table_op (4, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRREGC);

  bmi_set_ordering (4, callback, __FILE__, __LINE__);

  bad_init_regchain (&C);
  streqns = bmi_string_op (1, callback);
#if ! defined (BMI_BALSA)
  ba0_sscanf2 (streqns, "%t[%expanded_Az]", &C.decision_system);
#else
  ba0_sscanf2 (streqns, "%t[%Az]", &C.decision_system);
#endif
  for (i = 0; i < C.decision_system.size; i++)
    if (bap_is_independent_polynom_mpz (C.decision_system.tab[i]))
      BA0_RAISE_EXCEPTION (BMI_ERRIND);

  strprop = bmi_string_op (2, callback);
  ba0_init_table ((struct ba0_table *) &properties);
  ba0_sscanf2 (strprop, "%t[%s]", &properties);

  pretend = strcmp (bmi_string_op (3, callback), "true") == 0 ? true : false;

  bad_set_regchain_tableof_polynom_mpz (&C, &C.decision_system, &properties,
      pretend);

  bad_fast_primality_test_regchain (&C);

  {
    ALGEB res;
    res = bmi_rtable_regchain (callback->kv, &C, __FILE__, __LINE__);
#if defined (BMI_BALSA)
/*
 * In BALSA, one returns the whole table, not the mere rtable
 */
    res = bmi_balsa_new_regchain (res);
#endif
    return res;
  }
}
