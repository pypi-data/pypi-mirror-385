#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_coeffs.h"
#include "bmi_base_field_generators.h"

/*
 * The case of a numerical rational fraction
 */

#define PRINT
#undef PRINT

static ALGEB
bmi_coeffs_numerical_ratfrac (
    struct baz_ratfrac *A,
    struct bmi_callback *callback)
{
  char *stres;
  bool zero;
  ALGEB res;

#if defined (PRINT)
  ba0_printf ("bmi_coeffs_numerical_ratfrac\n");
#endif

  zero = baz_is_zero_ratfrac (A);
#if ! defined (BMI_BALSA)
  bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
  if (zero)
    stres = ba0_new_printf ("[], []");
  else
    stres = ba0_new_printf ("[%Qz], [1]", A);
  bmi_push_maple_gmp_allocators ();
  res = EvalMapleStatement (callback->kv, stres);
  bmi_pull_maple_gmp_allocators ();
#else
  if (zero)
    stres = ba0_new_printf ("[], []");
  else
    stres = ba0_new_printf ("[%Qz], [1]", A);
  res = bmi_balsa_new_string (stres);
#endif
  return res;
}

/*
 * The denominator of A is either numerical or involves only
 * variables larger than v. The variable v may be BAV_NOT_A_VARIABLE.
 * In that case, it is considered as the smallest possible variable
 */

static ALGEB
bmi_coeffs_larger (
    struct baz_ratfrac *A,
    struct bav_variable *v,
    struct bmi_callback *callback)
{
  struct baz_tableof_ratfrac terms, coeffs;
  struct bap_itercoeff_mpz iter;
  struct baz_ratfrac B;
  struct bap_polynom_mpz C;
  struct bav_term T;
  ba0_mpq_t icontent;
  bool collected;

#if defined (PRINT)
  ba0_printf ("larger: %Qz, %d\n", A, (ba0_int_p) v);
#endif

  if (bmi_is_table_op (bmi_nops (callback), callback))
    collected = false;
  else
    collected = bmi_bool_op (bmi_nops (callback), callback);

  if (v == BAV_NOT_A_VARIABLE)
    {
      if (!bap_is_numeric_polynom_mpz (&A->numer))
        v = A->numer.total_rank.rg[A->numer.total_rank.size - 1].var;
      else if (bap_is_numeric_polynom_mpz (&A->denom))
        return bmi_coeffs_numerical_ratfrac (A, callback);
      else
/*
 * The fraction is not numeric so that there exists at least one variable
 */
        v = bav_global.R.vars.tab[0];
    }
  else if (baz_is_numeric_ratfrac (A))
    return bmi_coeffs_numerical_ratfrac (A, callback);
/*
 * At this point, v != BAV_NOT_A_VARIABLE
 */
  ba0_mpq_init (icontent);
  bap_signed_numeric_content_polynom_mpz (ba0_mpq_numref (icontent), &A->numer);
  bap_exquo_polynom_numeric_mpz (&A->numer, &A->numer,
      ba0_mpq_numref (icontent));

  baz_init_ratfrac (&B);
  bap_signed_numeric_content_polynom_mpz (ba0_mpq_denref (icontent), &A->denom);
  bap_exquo_polynom_numeric_mpz (&B.denom, &A->denom,
      ba0_mpq_denref (icontent));

  ba0_mpq_canonicalize (icontent);

  bav_init_term (&T);
  bap_init_readonly_polynom_mpz (&C);

  ba0_init_table ((struct ba0_table *) &terms);
  ba0_init_table ((struct ba0_table *) &coeffs);

  bap_begin_itercoeff_mpz (&iter, &A->numer, v);
  while (!bap_outof_itercoeff_mpz (&iter))
    {
      if (terms.size == terms.alloc)
        {
          ba0_realloc2_table ((struct ba0_table *) &terms, 2 * terms.size + 1,
              (ba0_new_function *) & baz_new_ratfrac);
          ba0_realloc2_table ((struct ba0_table *) &coeffs,
              2 * terms.size + 1, (ba0_new_function *) & baz_new_ratfrac);
        }
      bap_term_itercoeff_mpz (&T, &iter);
      bap_set_polynom_term_mpz (&B.numer, &T);
      baz_reduce_ratfrac (terms.tab[terms.size], &B);
      bap_coeff_itercoeff_mpz (&C, &iter);
      baz_set_ratfrac_polynom_mpz (coeffs.tab[coeffs.size], &C);
      baz_mul_ratfrac_numeric_mpq
          (coeffs.tab[coeffs.size], coeffs.tab[coeffs.size], icontent);
      terms.size += 1;
      coeffs.size += 1;
      bap_next_itercoeff_mpz (&iter);
    }
  bap_close_itercoeff_mpz (&iter);

  if (collected)
    baz_collect_terms_tableof_ratfrac (&coeffs, &terms, &coeffs, &terms);
/*
fprintf (stderr, "larger: %s\n", (char*)res);
*/
  {
    char *stres;
    ALGEB res;
#if ! defined (BMI_BALSA)
    bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
    stres = ba0_new_printf ("%t[%Qz], %t[%Qz]", &coeffs, &terms);
    bmi_push_maple_gmp_allocators ();
    res = EvalMapleStatement (callback->kv, stres);
    bmi_pull_maple_gmp_allocators ();
#else
    stres = ba0_new_printf ("%t[%Qz], %t[%Qz]", &coeffs, &terms);
    res = bmi_balsa_new_string (stres);
#endif
    return res;
  }
}

/*
 * Handles the numerical rational fractions also
 * The denominator of A involves at least one variable.
 * All the variables of the denominator are lower than v.
 */

static ALGEB
bmi_coeffs_lower (
    struct baz_ratfrac *A,
    struct bav_variable *v,
    struct bmi_callback *callback)
{
  struct baz_tableof_ratfrac coeffs, terms;
  struct bap_itercoeff_mpz iter;
  struct bap_polynom_mpz C;
  struct bav_term T;
  ba0_mpz_t icnum;
  bool collected;

  if (bmi_is_table_op (bmi_nops (callback), callback))
    collected = false;
  else
    collected = bmi_bool_op (bmi_nops (callback), callback);

  ba0_init_table ((struct ba0_table *) &terms);
  ba0_init_table ((struct ba0_table *) &coeffs);
  ba0_mpz_init (icnum);
  bap_signed_numeric_content_polynom_mpz (icnum, &A->numer);
  bap_exquo_polynom_numeric_mpz (&A->numer, &A->numer, icnum);

  bav_init_term (&T);

  bap_init_readonly_polynom_mpz (&C);

  bap_begin_itercoeff_mpz (&iter, &A->numer, v);
  while (!bap_outof_itercoeff_mpz (&iter))
    {
      if (terms.size == terms.alloc)
        {
          ba0_realloc2_table ((struct ba0_table *) &terms, 2 * terms.size + 1,
              (ba0_new_function *) & baz_new_ratfrac);
          ba0_realloc2_table ((struct ba0_table *) &coeffs,
              2 * terms.size + 1, (ba0_new_function *) & baz_new_ratfrac);
        }
      bap_term_itercoeff_mpz (&T, &iter);
      baz_set_ratfrac_term (terms.tab[terms.size], &T);
      bap_coeff_itercoeff_mpz (&C, &iter);
      bap_mul_polynom_numeric_mpz (&coeffs.tab[coeffs.size]->numer, &C, icnum);
      bap_set_polynom_mpz (&coeffs.tab[coeffs.size]->denom, &A->denom);
      baz_reduce_ratfrac (coeffs.tab[coeffs.size], coeffs.tab[coeffs.size]);
      terms.size += 1;
      coeffs.size += 1;
      bap_next_itercoeff_mpz (&iter);
    }
  bap_close_itercoeff_mpz (&iter);

  if (collected)
    baz_collect_terms_tableof_ratfrac (&coeffs, &terms, &coeffs, &terms);
/*
fprintf (stderr, "lower: %s\n", (char*)res);
*/
  {
    char *stres;
    ALGEB res;
#if ! defined (BMI_BALSA)
    bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
    stres = ba0_new_printf ("%t[%Qz], %t[%Qz]", &coeffs, &terms);
    bmi_push_maple_gmp_allocators ();
    res = EvalMapleStatement (callback->kv, stres);
    bmi_pull_maple_gmp_allocators ();
#else
    stres = ba0_new_printf ("%t[%Qz], %t[%Qz]", &coeffs, &terms);
    res = bmi_balsa_new_string (stres);
#endif
    return res;
  }
}

static ALGEB bmi_coeffs2 (
    struct bmi_callback *callback);

/*
 * EXPORTED
 *
 * Coeffs (ratfrac, variable, differential ring)
 * Coeffs (ratfrac, generators, relations, differential ring)
 * Coeffs (ratfrac, variable, differential ring, collected)
 * Coeffs (ratfrac, generators, relations, differential ring, collected)
 *
 * Complicated way to handle collected in order to keep a binary 
 * compatibility with old versions of the library
 */

ALGEB
bmi_coeffs (
    struct bmi_callback *callback)
{
  struct baz_ratfrac A;
  struct bav_variable *v;
  ba0_int_p i;
  char *ratfrac, *variable;
  bool larger, lower;

  if (bmi_nops (callback) == 5 ||
      (bmi_nops (callback) == 4 && bmi_is_table_op (4, callback)))
    return bmi_coeffs2 (callback);

  bmi_set_ordering (3, callback, __FILE__, __LINE__);

#if defined (PRINT)
  printf ("%s\n", "Coeffs (ratfrac, variable, differential ring)");
#endif

  ratfrac = bmi_string_op (1, callback);
  baz_init_ratfrac (&A);
#if ! defined (BMI_BALSA)
  ba0_sscanf2 (ratfrac, "%simplify_expanded_Qz", &A);
#else
  ba0_sscanf2 (ratfrac, "%simplify_Qz", &A);
#endif

  variable = bmi_string_op (2, callback);
  if (strcmp (variable, "0") == 0)
    v = BAV_NOT_A_VARIABLE;
  else
    ba0_sscanf2 (variable, "%v", &v);

  larger = lower = false;
  for (i = 0; i < A.denom.total_rank.size; i++)
    {
      struct bav_variable *w = A.denom.total_rank.rg[i].var;
      if (v == BAV_NOT_A_VARIABLE ||
          bav_variable_number (w) >= bav_variable_number (v))
        larger = true;
      else
        lower = true;
    }
/*
 * larger = the denominator involves at least one variable
 *          all the variables of the denominator are larger than v
 * lower  = the denominator involves at least one variable
 *          all the variables of the denominator are lower than v
 */
  if (larger && lower)
    BA0_RAISE_EXCEPTION (BMI_ERRCOEF);
/*
ba0_printf ("larger = %d, lower = %d\n", larger, lower);
if (v == BAV_NOT_A_VARIABLE)
    ba0_printf ("v = BAV_NOT_A_VARIABLE\n");
else
    ba0_printf ("v = %v\n", v);
 */
  return !lower ? bmi_coeffs_larger (&A, v, callback) :
      bmi_coeffs_lower (&A, v, callback);
}

/*
 * Coeffs (ratfrac, generators, relations, differential ring)
 * Coeffs (ratfrac, generators, relations, differential ring, collected)
 */

static ALGEB
bmi_coeffs2 (
    struct bmi_callback *callback)
{
  struct bad_base_field K;
  struct bad_regchain C;
  struct baz_ratfrac A;
  struct ba0_tableof_range_indexed_group G;
  struct bav_dictionary_variable dict;
  struct bav_tableof_variable vars;
  struct bav_variable *v;
  ba0_int_p i;
  char *ratfrac, *generators, *relations;
  bool larger, lower;

/*
ba0_printf ("%s\n", "Coeffs (ratfrac, generators, relations, differential ring)\n");
 */
  bmi_set_ordering (4, callback, __FILE__, __LINE__);
/*
 * A is decomposed as numerator / denominator
 */
  ratfrac = bmi_string_op (1, callback);
  baz_init_ratfrac (&A);
#if ! defined (BMI_BALSA)
  ba0_sscanf2 (ratfrac, "%simplify_expanded_Qz", &A);
#else
  ba0_sscanf2 (ratfrac, "%simplify_Qz", &A);
#endif

  generators = bmi_string_op (2, callback);
  relations = bmi_string_op (3, callback);
/*
 * Borrowed from bmi_Rosenfeld_Groebner.c
 */
  ba0_init_table ((struct ba0_table *) &G);
  ba0_sscanf2 (generators, "%t[%range_indexed_group]", &G);

  bad_init_regchain (&C);
  ba0_sscanf2 (relations, "%pretend_regchain", &C);

  bad_init_base_field (&K);
  bad_set_base_field_generators_and_relations (&K, &G, &C, false);
/*
 * End of borrowing.
 */
  bav_init_dictionary_variable (&dict, 6);
  ba0_init_table ((struct ba0_table *) &vars);
  ba0_realloc_table ((struct ba0_table *) &vars, 64);

  bap_mark_indets_polynom_mpz (&dict, &vars, &A.numer);
  bap_mark_indets_polynom_mpz (&dict, &vars, &A.denom);

  v = BAV_NOT_A_VARIABLE;
  for (i = 0; i < vars.size; i++)
    {
      if (!bad_member_variable_base_field (vars.tab[i], &K))
        {
          if (v == BAV_NOT_A_VARIABLE || bav_gt_variable (v, vars.tab[i]))
            v = vars.tab[i];
        }
    }
/*
 * All the variables of A lie in the base field
 */
  if (v == BAV_NOT_A_VARIABLE)
    return bmi_coeffs_numerical_ratfrac (&A, callback);
/*
 * v is the smallest variable not in the base field
 */
  larger = lower = false;
  for (i = 0; i < A.denom.total_rank.size; i++)
    {
      struct bav_variable *w = A.denom.total_rank.rg[i].var;
      if (v == BAV_NOT_A_VARIABLE ||
          bav_variable_number (w) >= bav_variable_number (v))
        larger = true;
      else
        lower = true;
    }
/*
 * larger = the denominator involves at least one variable
 *          all the variables of the denominator are larger than v
 * lower  = the denominator involves at least one variable
 *          all the variables of the denominator are lower than v
 */
  if (larger && lower)
    BA0_RAISE_EXCEPTION (BMI_ERRCOEF);

  return !lower ? bmi_coeffs_larger (&A, v, callback) :
      bmi_coeffs_lower (&A, v, callback);
}
