#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_differential_prem.h"

static ALGEB bmi_differential_prem2 (
    struct bmi_callback *callback);

/*
 * EXPORTED
 * DifferentialPrem (differential polynomial, method, regchain)
 * DifferentialPrem (differential polynomial, method, redset, drideal)
 *
 * returns a sequence H, R
 * where H is the power product of initials and separants
 *       R is the remainder
 */

ALGEB
bmi_differential_prem (
    struct bmi_callback *callback)
{
  struct bad_regchain C;
  struct bap_polynom_mpq F;
  struct bap_product_mpz H, R;
  struct bap_polynom_mpz numer;
  ba0_mpz_t denom;
  char *method;
  enum bad_typeof_reduction type_red = bad_full_reduction;
/*
 * to avoid a warning 
 */
  if (bmi_nops (callback) != 3)
    return bmi_differential_prem2 (callback);
  if (!bmi_is_regchain_op (3, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRREGC);

  bmi_set_ordering_and_regchain (&C, 3, callback, __FILE__, __LINE__);

  method = bmi_string_op (2, callback);
  if (!bad_defines_a_differential_ideal_regchain (&C) ||
      strcmp (method, BMI_IX_algebraically) == 0)
    type_red = bad_algebraic_reduction;
  else if (strcmp (method, BMI_IX_partially) == 0)
    type_red = bad_partial_reduction;
  else if (strcmp (method, BMI_IX_fully) == 0)
    type_red = bad_full_reduction;
  else
    BA0_RAISE_EXCEPTION (BMI_ERRMETH);

  bap_init_polynom_mpq (&F);
#if ! defined (BMI_BALSA)
  ba0_sscanf2 (bmi_string_op (1, callback), "%simplify_expanded_Aq", &F);
#else
  ba0_sscanf2 (bmi_string_op (1, callback), "%simplify_Aq", &F);
#endif

  bap_init_polynom_mpz (&numer);
  ba0_mpz_init (denom);
  bap_numer_polynom_mpq (&numer, denom, &F);

  bap_init_product_mpz (&H);
  bap_init_product_mpz (&R);
  bad_reduce_polynom_by_regchain
      (&R, &H, (struct bav_tableof_term *) 0, &numer, &C, type_red,
      bad_all_derivatives_to_reduce);

  {
    ALGEB res;
    char *stres;
#if ! defined (BMI_BALSA)
    bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
#endif
    stres = ba0_new_printf ("%Pz, (%Pz)/(%z)", &H, &R, denom);
/*
        ba0_printf ("(1). %s\n", stres);
 */
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

/*
 * DifferentialPrem2 (differential polynomial, method, redset, drideal)
 *
 * returns a sequence H, R
 * where H is the power product of initials and separants
 *       R is the remainder
 */

static ALGEB
bmi_differential_prem2 (
    struct bmi_callback *callback)
{
  struct bad_regchain C;
  struct bap_polynom_mpq F;
  struct bap_product_mpz H, R;
  struct bap_polynom_mpz numer;
  struct ba0_tableof_string properties;
  ba0_mpz_t denom;
  ba0_int_p i;
  char *method;
  enum bad_typeof_reduction type_red = bad_full_reduction;
/*
 * to avoid a warning 
 */

  if (bmi_nops (callback) != 4)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_table_op (4, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRDRNG);

  if (bmi_is_regchain_op (4, callback))
    bmi_set_ordering_and_regchain (&C, 4, callback, __FILE__, __LINE__);
  else
    bmi_set_ordering (4, callback, __FILE__, __LINE__);

  method = bmi_string_op (2, callback);
  if (bav_global.R.ders.size == 0 || strcmp (method, BMI_IX_algebraically) == 0)
    type_red = bad_algebraic_reduction;
  else if (strcmp (method, BMI_IX_partially) == 0)
    type_red = bad_partial_reduction;
  else if (strcmp (method, BMI_IX_fully) == 0)
    type_red = bad_full_reduction;
  else
    BA0_RAISE_EXCEPTION (BMI_ERRMETH);

  bap_init_polynom_mpq (&F);
#if ! defined (BMI_BALSA)
  ba0_sscanf2 (bmi_string_op (1, callback), "%simplify_expanded_Aq", &F);
#else
  ba0_sscanf2 (bmi_string_op (1, callback), "%simplify_Aq", &F);
#endif

  bap_init_polynom_mpz (&numer);
  ba0_mpz_init (denom);
  bap_numer_polynom_mpq (&numer, denom, &F);
/*
 * Mostly: C = PretendRegchain (redset)
 */
  bad_init_regchain (&C);
  ba0_sscanf2
      (bmi_string_op (3, callback), "%t[%expanded_Az]", &C.decision_system);
  for (i = 0; i < C.decision_system.size; i++)
    if (bap_is_independent_polynom_mpz (C.decision_system.tab[i]))
      BA0_RAISE_EXCEPTION (BMI_ERRIND);
  ba0_init_table ((struct ba0_table *) &properties);
  if (bav_global.R.ders.size > 0)
    ba0_sscanf2 ("[differential]", "%t[%s]", &properties);
  bad_set_regchain_tableof_polynom_mpz
      (&C, &C.decision_system, &properties, true);
/*
 * Go
 */
  bap_init_product_mpz (&H);
  bap_init_product_mpz (&R);
  bad_reduce_polynom_by_regchain
      (&R, &H, (struct bav_tableof_term *) 0, &numer, &C, type_red,
      bad_all_derivatives_to_reduce);

  {
    ALGEB res;
    char *stres;
#if ! defined (BMI_BALSA)
    bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
#endif
    stres = ba0_new_printf ("%Pz, (%Pz)/(%z)", &H, &R, denom);
/*
ba0_printf ("(2). %s\n", stres);
*/
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
