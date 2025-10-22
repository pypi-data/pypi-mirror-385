#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_leading_derivative.h"

/*
 * EXPORTED
 * LeadingDerivative (list(ratfrac) | regchain, fullset, differential ring)
 *
 * fullset is now ignored: the defining equations of parameters are implicit
 */

ALGEB
bmi_leading_derivative (
    struct bmi_callback *callback)
{
  struct bad_regchain C;
  struct baz_tableof_ratfrac ratfracs;
  struct bav_tableof_variable T;
  ba0_int_p i;

  if (bmi_nops (callback) != 3)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_table_op (3, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRDRNG);

  if (bmi_is_regchain_op (1, callback))
    bmi_set_ordering_and_regchain (&C, 1, callback, __FILE__, __LINE__);
  else
    bmi_set_ordering (3, callback, __FILE__, __LINE__);

  ba0_init_table ((struct ba0_table *) &T);

  if (bmi_is_table_op (1, callback))
    {
      ba0_realloc_table ((struct ba0_table *) &T, C.decision_system.size);
      for (i = 0; i < C.decision_system.size; i++)
        T.tab[T.size++] = bap_leader_polynom_mpz (C.decision_system.tab[i]);
    }
  else
    {
      ba0_init_table ((struct ba0_table *) &ratfracs);
#if ! defined (BMI_BALSA)
      ba0_sscanf2
          (bmi_string_op (1, callback), "%t[%simplify_expanded_Qz]", &ratfracs);
#else
      ba0_sscanf2 (bmi_string_op (1, callback), "%t[%Qz]", &ratfracs);
#endif
      ba0_realloc_table ((struct ba0_table *) &T, ratfracs.size);
      for (i = 0; i < ratfracs.size; i++)
        T.tab[T.size++] = baz_leader_ratfrac (ratfracs.tab[i]);
    }

  {
    char *stres;
    ALGEB res;
#if ! defined (BMI_BALSA)
    bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
#endif
    stres = ba0_new_printf ("%t[%v]", &T);
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
