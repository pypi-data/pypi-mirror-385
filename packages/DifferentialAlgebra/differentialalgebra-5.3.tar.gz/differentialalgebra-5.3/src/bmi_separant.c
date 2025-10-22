#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_separant.h"

/*
 * EXPORTED
 * Separant (ratfrac, differential ring)
 * Separant (list(ratfrac) | regchain, fullset, 
 * 					derivative, differential ring)
 *
 * By convention, if derivative = 0 then the lcoeff is taken w.r.t. 
 * the leading derivative
 *
 * fullset is now ignored: the defining equations of parameters are implicit
 */

ALGEB
bmi_separant (
    struct bmi_callback *callback)
{
  struct bad_regchain C;
  struct baz_tableof_ratfrac ratfracs;
  struct bap_tableof_polynom_mpz polys;
  struct bav_variable *v;
  ba0_int_p i;
  char *derivative, *stres;

  if (bmi_nops (callback) != 4)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_table_op (4, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRDRNG);

  if (bmi_is_regchain_op (1, callback))
    bmi_set_ordering_and_regchain (&C, 1, callback, __FILE__, __LINE__);
  else
    bmi_set_ordering (4, callback, __FILE__, __LINE__);

  derivative = bmi_string_op (3, callback);
  if (!isdigit ((int) derivative[0]))
    ba0_sscanf2 (derivative, "%v", &v);

  if (bmi_is_table_op (1, callback))
    {
      ba0_init_table ((struct ba0_table *) &polys);
      ba0_realloc2_table ((struct ba0_table *) &polys, C.decision_system.size,
          (ba0_new_function *) & bap_new_polynom_mpz);
      if (isdigit ((int) derivative[0]))
        {
          for (i = 0; i < C.decision_system.size; i++)
            bap_separant_polynom_mpz
                (polys.tab[polys.size++], C.decision_system.tab[i]);
        }
      else
        {
          for (i = 0; i < C.decision_system.size; i++)
            bap_separant2_polynom_mpz
                (polys.tab[polys.size++], C.decision_system.tab[i], v);
        }
#if ! defined (BMI_BALSA)
      bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
#endif
      stres = ba0_new_printf ("%t[%Az]", &polys);
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
      if (isdigit ((int) derivative[0]))
        {
          for (i = 0; i < ratfracs.size; i++)
            baz_separant_ratfrac (ratfracs.tab[i], ratfracs.tab[i]);
        }
      else
        {
          for (i = 0; i < ratfracs.size; i++)
            baz_separant2_ratfrac (ratfracs.tab[i], ratfracs.tab[i], v);
        }
#if ! defined (BMI_BALSA)
      bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
#endif
      stres = ba0_new_printf ("%t[%Qz]", &ratfracs);
    }

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
