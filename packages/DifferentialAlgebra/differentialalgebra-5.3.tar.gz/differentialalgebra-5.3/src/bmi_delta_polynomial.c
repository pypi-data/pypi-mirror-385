#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_delta_polynomial.h"

/*
 * EXPORTED
 * DeltaPolynomial (p, q, dring)
 */

ALGEB
bmi_delta_polynomial (
    struct bmi_callback *callback)
{
  struct bad_regchain C;
  struct bad_critical_pair pair;
  struct bap_polynom_mpq P, Q;
  struct bap_polynom_mpz numP, numQ, delta;
  char *p, *q;

  if (bmi_nops (callback) != 3)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_table_op (3, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRREGC);

  if (bmi_is_regchain_op (3, callback))
    bmi_set_ordering_and_regchain (&C, 3, callback, __FILE__, __LINE__);
  else
    bmi_set_ordering (3, callback, __FILE__, __LINE__);

  p = bmi_string_op (1, callback);
  q = bmi_string_op (2, callback);

  bap_init_polynom_mpq (&P);
  bap_init_polynom_mpq (&Q);
#if ! defined (BMI_BALSA)
  ba0_sscanf2 (p, "%simplify_expanded_Aq", &P);
  ba0_sscanf2 (q, "%simplify_expanded_Aq", &Q);
#else
  ba0_sscanf2 (p, "%simplify_Aq", &P);
  ba0_sscanf2 (q, "%simplify_Aq", &Q);
#endif
  bap_init_polynom_mpz (&numP);
  bap_init_polynom_mpz (&numQ);
  bap_numer_polynom_mpq (&numP, 0, &P);
  bap_numer_polynom_mpq (&numQ, 0, &Q);

  bad_init_critical_pair (&pair);
  bad_set_critical_pair_polynom_mpz (&pair, &numP, &numQ);

  bap_init_polynom_mpz (&delta);
  bad_delta_polynom_critical_pair (&delta, &pair);
  if (!bap_is_zero_polynom_mpz (&delta))
    bap_normal_numeric_primpart_polynom_mpz (&delta, &delta);

  {
    ALGEB res;
    char *stres;
#if ! defined (BMI_BALSA)
    bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
#endif
    stres = ba0_new_printf ("%Az", &delta);
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
