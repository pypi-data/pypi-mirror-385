#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_reduced_form.h"

/*
 * EXPORTED
 * ReducedForm (list(ratfrac), variable, regchain, ..., regchain)
 *
 * At least one regchain is mandatory.
 *
 * In the case of many different regchains, it is assumed that they
 * are the components of a radical decomposition.
 *
 * The variable may be the string "0"
 *
 * The result is the sequence of the reduced forms.
 */

ALGEB
bmi_reduced_form (
    struct bmi_callback *callback)
{
  struct bad_intersectof_regchain tabC;
  struct ba0_table R;
  struct baz_tableof_ratfrac *RF;
  struct bap_tableof_polynom_mpq A;
  struct bap_polynom_mpz numer;
  struct bav_variable *u;
  char *variable;
  ba0_mpz_t gcd, denom, bunk;
  ba0_int_p i, nops;

  nops = bmi_nops (callback);
  if (nops < 3)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  for (i = 3; i <= nops; i++)
    if (!bmi_is_regchain_op ((long) i, callback))
      BA0_RAISE_EXCEPTION (BMI_ERRREGC);
  bmi_set_ordering_and_intersectof_regchain
      (&tabC, 3, callback, __FILE__, __LINE__);
/*
 * The rational fraction whose NF we are looking for.
 */
  ba0_init_table ((struct ba0_table *) &A);
#if ! defined (BMI_BALSA)
  ba0_sscanf2 (bmi_string_op (1, callback), "%t[%simplify_expanded_Aq]", &A);
#else
  ba0_sscanf2 (bmi_string_op (1, callback), "%t[%simplify_Aq]", &A);
#endif
/*
 * The variable. A "0" means "no variable"
 */
  variable = bmi_string_op (2, callback);
  if (strcmp (variable, "0") == 0)
    u = BAV_NOT_A_VARIABLE;
  else
    ba0_sscanf2 (variable, "%v", &u);

  ba0_init_table (&R);
  ba0_realloc2_table (&R, A.size, (ba0_new_function *) & ba0_new_table);
/*
 * Compute the reduced forms of the polynomials
 */
  bap_init_polynom_mpz (&numer);
  ba0_mpz_init (denom);
  ba0_mpz_init (bunk);
  ba0_mpz_init (gcd);
  while (R.size < A.size)
    {
      bap_numer_polynom_mpq (&numer, denom, A.tab[R.size]);
/*
 * Compute the reduced forms of the numerators
 */
      bad_reduced_form_polynom_mod_intersectof_regchain
          ((struct baz_tableof_ratfrac *) R.tab[R.size], &numer, u, &tabC);
/*
 * Report the denominators of the input polynomials
 */
      RF = (struct baz_tableof_ratfrac *) R.tab[R.size];
      for (i = 0; i < RF->size; i++)
        {
          if (!baz_is_zero_ratfrac (RF->tab[i]))
            {
              bap_numeric_content_polynom_mpz (bunk, &RF->tab[i]->numer);
              ba0_mpz_gcd (gcd, bunk, denom);
              bap_exquo_polynom_numeric_mpz
                  (&RF->tab[i]->numer, &RF->tab[i]->numer, gcd);
              ba0_mpz_divexact (bunk, denom, gcd);
              bap_mul_polynom_numeric_mpz
                  (&RF->tab[i]->denom, &RF->tab[i]->denom, bunk);
            }
        }
      R.size += 1;
    }

  {
    char *stres;
    ALGEB res;
#if ! defined (BMI_BALSA)
    bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
#endif
    stres = ba0_new_printf ("%t[%t[%Qz]]", &R);
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
