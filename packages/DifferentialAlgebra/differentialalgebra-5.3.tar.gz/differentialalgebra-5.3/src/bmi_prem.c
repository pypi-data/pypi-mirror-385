#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_prem.h"

/*
 * EXPORTED
 * Prem (list(ratfrac), regchain)
 */

ALGEB
bmi_prem (
    struct bmi_callback *callback)
{
  struct bad_regchain C;
  enum bad_typeof_reduction type_red;
  struct baz_tableof_ratfrac ratfracs;
  struct bap_tableof_product_mpz prod_num;
  struct bap_tableof_product_mpz prod_den;
  ba0_int_p i;
  char *str_ratfracs, *stres;

  if (bmi_nops (callback) != 2)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_regchain_op (2, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRREGC);

  bmi_set_ordering_and_regchain (&C, 2, callback, __FILE__, __LINE__);

  str_ratfracs = bmi_string_op (1, callback);
  ba0_init_table ((struct ba0_table *) &ratfracs);
  ba0_sscanf2 (str_ratfracs, "%t[%simplify_expanded_Qz]", &ratfracs);

  ba0_init_table ((struct ba0_table *) &prod_num);
  ba0_realloc2_table ((struct ba0_table *) &prod_num, ratfracs.size,
      (ba0_new_function *) & bap_new_product_mpz);

  ba0_init_table ((struct ba0_table *) &prod_den);
  ba0_realloc2_table ((struct ba0_table *) &prod_den, ratfracs.size,
      (ba0_new_function *) & bap_new_product_mpz);
/*
 * The prem of a fraction P/Q is defined as R/S where
 * - R is the prem of P and
 * - S is the prem of Q
 */
  if (bad_has_property_regchain (&C, bad_differential_ideal_property))
    type_red = bad_full_reduction;
  else
    type_red = bad_algebraic_reduction;

  for (i = 0; i < ratfracs.size; i++)
    {
      struct bap_polynom_mpz *numer;
      struct bap_polynom_mpz *denom;
      numer = &ratfracs.tab[i]->numer;
      denom = &ratfracs.tab[i]->denom;

      bad_reduce_polynom_by_regchain (prod_num.tab[i],
          (struct bap_product_mpz *) 0,
          (struct bav_tableof_term *) 0, numer, &C, type_red,
          bad_all_derivatives_to_reduce);
      bad_reduce_polynom_by_regchain (prod_den.tab[i],
          (struct bap_product_mpz *) 0,
          (struct bav_tableof_term *) 0, denom, &C, type_red,
          bad_all_derivatives_to_reduce);
      if (bap_is_zero_product_mpz (prod_den.tab[i]))
        BA0_RAISE_EXCEPTION (BA0_ERRIVZ);

      prod_num.size = i + 1;
      prod_den.size = i + 1;
    }

#if ! defined (BMI_BALSA)
  bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
#endif
/*
 * The following piece of code is adapted from ba0_new_printf
 */
  ba0_record_output ();
  BA0_TRY
  {
    ba0_set_output_counter ();
    ba0_put_char ('[');
    for (i = 0; i < prod_num.size; i++)
      {
        if (i > 0)
          ba0_put_string (", ");
        ba0_printf ("(%Pz)/(%Pz)", prod_num.tab[i], prod_den.tab[i]);
      }
    ba0_put_char (']');
    stres = ba0_persistent_malloc (ba0_output_counter () + 1);
    ba0_set_output_string (stres);
    ba0_put_char ('[');
    for (i = 0; i < prod_num.size; i++)
      {
        if (i > 0)
          ba0_put_string (", ");
        ba0_printf ("(%Pz)/(%Pz)", prod_num.tab[i], prod_den.tab[i]);
      }
    ba0_put_char (']');
    ba0_restore_output ();
  }
  BA0_CATCH
  {
    ba0_restore_output ();
    BA0_RE_RAISE_EXCEPTION;
  }
  BA0_ENDTRY;

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
