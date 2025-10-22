#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_normal_form.h"

/*
 * EXPORTED
 * NormalForm (list(ratfrac), regchain, ..., regchain)
 *
 * At least one regchain is mandatory.
 *
 * In the case of many different regchains, it is assumed that they
 * are the components of a radical decomposition.
 *
 * The result is the sequence of the normal forms.
 */

ALGEB
bmi_normal_form (
    struct bmi_callback *callback)
{
  struct ba0_table R;
  struct baz_tableof_ratfrac A;
  struct bad_intersectof_regchain tabC;
  ba0_int_p i, nops;

  nops = bmi_nops (callback);
  if (nops < 2)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  for (i = 2; i <= nops; i++)
    if (!bmi_is_regchain_op ((long) i, callback))
      BA0_RAISE_EXCEPTION (BMI_ERRREGC);
  bmi_set_ordering_and_intersectof_regchain
      (&tabC, 2, callback, __FILE__, __LINE__);
/*
 * The rational fraction whose NF we are looking for.
 * Other initializations.
 */
  ba0_init_table ((struct ba0_table *) &A);
#if ! defined (BMI_BALSA)
  ba0_sscanf2 (bmi_string_op (1, callback), "%t[%simplify_expanded_Qz]", &A);
#else
  ba0_sscanf2 (bmi_string_op (1, callback), "%t[%simplify_Qz]", &A);
#endif
  ba0_init_table (&R);
  ba0_realloc2_table (&R, A.size, (ba0_new_function *) & ba0_new_table);
/*
 * Build the regchain in the BLAD sense
 */
  while (R.size < A.size)
    {
      bad_normal_form_ratfrac_mod_intersectof_regchain
          ((struct baz_tableof_ratfrac *) R.tab[R.size], A.tab[R.size],
          &tabC, (struct bap_polynom_mpz * *) 0);
      R.size += 1;
    }

  {
    char *stres;
    ALGEB res;
#if ! defined (BMI_BALSA)
    bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
    stres = ba0_new_printf ("%t[%t[%Qz]]", &R);
    bmi_push_maple_gmp_allocators ();
    res = EvalMapleStatement (callback->kv, stres);
    bmi_pull_maple_gmp_allocators ();
#else
    stres = ba0_new_printf ("%t[%t[%Qz]]", &R);
    res = bmi_balsa_new_string (stres);
#endif
    return res;
  }
}
