#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_preparation_equation.h"
#include "bmi_base_field_generators.h"

static void bmi_check_zstring (
    char *);
static ALGEB bmi_preparation_equation2 (
    struct bmi_callback *);

/*
 * EXPORTED
 *
 * The first form is kept for compatibility reasons but is deprecated.
 *
 * PreparationEquation (polynomial, regchain, n, congruence, zstring)
 * PreparationEquation (polynomial, regchain, generators, relations, congruence, zstring)
 */

ALGEB
bmi_preparation_equation (
    struct bmi_callback *callback)
{
  struct bad_preparation_equation E;
  struct bad_regchain A;
  struct bap_polynom_mpq F;
  struct bap_polynom_mpz numF;
  struct bap_polynom_mpz *ddz;
  ba0_mpz_t denF;
  ba0_int_p n;
  bool congruence;
  char *zstring, *nb, *stres;

  if (bmi_nops (callback) == 6)
    return bmi_preparation_equation2 (callback);

  if (bmi_nops (callback) != 5)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_regchain_op (2, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRREGC);

  bmi_set_ordering_and_regchain (&A, 2, callback, __FILE__, __LINE__);
/*
 * F is decomposed as numerator / denominator
 */
  bap_init_polynom_mpq (&F);
#if ! defined (BMI_BALSA)
  ba0_sscanf2 (bmi_string_op (1, callback), "%simplify_expanded_Aq", &F);
#else
  ba0_sscanf2 (bmi_string_op (1, callback), "%simplify_Aq", &F);
#endif
  bap_init_polynom_mpz (&numF);
  ba0_mpz_init (denF);
  bap_numer_polynom_mpq (&numF, denF, &F);
/*
 * The number of equations which should be considered as base field equations
 */
  nb = bmi_string_op (3, callback);
  n = atoi (nb);
  if (n >= A.decision_system.size)
    BA0_RAISE_EXCEPTION (BMI_ERRREGC);
/*
 * The congruence
 */
  congruence = bmi_bool_op (4, callback);
/*
 * The string used for printing the zi
 */
  zstring = bmi_string_op (5, callback);
  bmi_check_zstring (zstring);
  bad_set_settings_preparation (zstring);
/*
 * Compute the equation
 */
  bad_init_preparation_equation (&E);
#if defined (BEFORE_RG_3_8)
  bad_set_preparation_equation_polynom (&E, &numF, denF, &A, n, &ddz);
#else
/*
 * FIX ME: pass K from DifferentialAlgebra rather than n !
 */
  {
    struct bad_base_field K;
    struct bad_regchain Ak;
    bad_init_regchain (&Ak);
    bad_set_regchain (&Ak, &A);
    Ak.decision_system.size = n;
    bad_init_base_field (&K);

    bad_set_base_field_generators_and_relations
        (&K, (struct ba0_tableof_range_indexed_group *) 0, &Ak, true);

    bad_set_preparation_equation_polynom (&E, &numF, denF, &A, &K, &ddz);
  }
#endif
/*
 * Strip it if only the congruence is needed.
 */
  if (congruence)
    {
      bav_Idegree q;
      ba0_int_p l;

      bad_preparation_congruence (&l, &q, &E);
      E.terms.size = l;
      E.coeffs.size = l;
    }
/*
 * The result
 */
#if ! defined (BMI_BALSA)
  bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
#endif
  stres = ba0_new_printf ("%preparation_equation", &E);

  {
    ALGEB res;
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
 * EXPORTED
 *
 * PreparationEquation (polynomial, regchain, generators, relations, congruence, zstring)
 */

static ALGEB
bmi_preparation_equation2 (
    struct bmi_callback *callback)
{
  struct bad_preparation_equation E;
  struct bad_base_field K;
  struct bad_regchain A, C;
  struct bap_polynom_mpq F;
  struct bap_polynom_mpz numF;
  struct bap_polynom_mpz *ddz;
  struct ba0_tableof_range_indexed_group G;
  ba0_mpz_t denF;
  ba0_int_p n;
  bool congruence;
  char *zstring, *stres;
  char *generators;
  char *relations;

  if (!bmi_is_regchain_op (2, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRREGC);

  bmi_set_ordering_and_regchain (&A, 2, callback, __FILE__, __LINE__);
/*
 * F is decomposed as numerator / denominator
 */
  bap_init_polynom_mpq (&F);
#if ! defined (BMI_BALSA)
  ba0_sscanf2 (bmi_string_op (1, callback), "%simplify_expanded_Aq", &F);
#else
  ba0_sscanf2 (bmi_string_op (1, callback), "%simplify_Aq", &F);
#endif
  bap_init_polynom_mpz (&numF);
  ba0_mpz_init (denF);
  bap_numer_polynom_mpq (&numF, denF, &F);
/*
 * The number of equations which should be considered as base field equations
 */
  generators = bmi_string_op (3, callback);
  relations = bmi_string_op (4, callback);
/*
 * Borrowed from bmi_Rosenfeld_Groebner.c
 */
  ba0_init_table ((struct ba0_table *) &G);
  ba0_sscanf2 (generators, "%t[%range_indexed_group]", &G);

  bad_init_regchain (&C);
  ba0_sscanf2 (relations, "%pretend_regchain", &C);
/*
 * The differential prop. is important for the base field compatibility test.
 * It would not be present if the user had not specified any relations.
 */
  if (bad_defines_a_differential_ideal_regchain (&A))
    {
      if (C.decision_system.size == 0)
        bad_set_property_attchain (&C.attrib, bad_differential_ideal_property);
    }

  bad_init_base_field (&K);
  bad_set_base_field_generators_and_relations (&K, &G, &C, false);
/*
 * End of borrowing.
 * The number of equations defining the base field
 */
  n = K.relations.decision_system.size;

  if (n >= A.decision_system.size)
    BA0_RAISE_EXCEPTION (BMI_ERRREGC);
/*
 * The congruence
 */
  congruence = bmi_bool_op (5, callback);
/*
 * The string used for printing the zi
 */
  zstring = bmi_string_op (6, callback);
  bmi_check_zstring (zstring);
  bad_set_settings_preparation (zstring);
/*
 * Compute the equation
 */
  bad_init_preparation_equation (&E);
  bad_set_preparation_equation_polynom (&E, &numF, denF, &A, &K, &ddz);
/*
 * Strip it if only the congruence is needed.
 */
  if (congruence)
    {
      bav_Idegree q;
      ba0_int_p l;

      bad_preparation_congruence (&l, &q, &E);
      E.terms.size = l;
      E.coeffs.size = l;
    }
/*
 * The result
 */
#if ! defined (BMI_BALSA)
  bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
#endif
  stres = ba0_new_printf ("%preparation_equation", &E);

  {
    ALGEB res;
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
 * Calls ba0_get_format in order to perform the basic format checking
 * Then makes sure that there is only one special format code, which is "%d"
 */

static void
bmi_check_zstring (
    char *zstring)
{
  struct ba0_format *f;
  ba0_int_p i;

  f = ba0_get_format (zstring);
  i = 0;
  while (zstring[i] && zstring[i] != '%')
    i += 1;
  if (zstring[i] != '%' || zstring[i + 1] != 'd')
    BA0_RAISE_EXCEPTION (BMI_ERRZSTR);
  i += 2;
  while (zstring[i] && zstring[i] != '%')
    i += 1;
  if (zstring[i])
    BA0_RAISE_EXCEPTION (BMI_ERRZSTR);
}
