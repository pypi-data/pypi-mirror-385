#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_differentiate.h"

/*
 * Differentiate (list(ratfrac) | regchain, fullset,
 * 				list (derivations), differential ring)
 *
 * fullset is now ignored: the defining equations of parameters are implicit.
 */

ALGEB
bmi_differentiate (
    struct bmi_callback *callback)
{
  struct bad_regchain C;
  struct baz_tableof_ratfrac U;
  struct bav_tableof_term T;
  struct bav_term *term;
  struct bav_symbol *y;
  bav_Idegree d;
  ba0_int_p k, i, j;
  char *polys, *lders, *stres;

  if (bmi_nops (callback) != 4)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_table_op (4, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRDRNG);

  if (bmi_is_regchain_op (1, callback))
    bmi_set_ordering_and_regchain (&C, 1, callback, __FILE__, __LINE__);
  else
    bmi_set_ordering (4, callback, __FILE__, __LINE__);

  lders = bmi_string_op (3, callback);
  ba0_init_table ((struct ba0_table *) &T);
  ba0_sscanf2 (lders, "%t[%term]", &T);

  if (bmi_is_regchain_op (1, callback))
    {
      for (k = 0; k < C.decision_system.size; k++)
        {
          for (i = 0; i < T.size; i++)
            {
              term = T.tab[i];
              for (j = 0; j < term->size; j++)
                {
                  y = term->rg[j].var->root;
                  for (d = 0; d < term->rg[j].deg; d++)
                    bap_diff_polynom_mpz (C.decision_system.tab[k],
                        C.decision_system.tab[k], y);
                }
            }
        }
#if ! defined (BMI_BALSA)
      bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
#endif
      stres = ba0_new_printf ("%t[%Az]", &C.decision_system);
    }
  else
    {
      polys = bmi_string_op (1, callback);
      ba0_init_table ((struct ba0_table *) &U);
#if ! defined (BMI_BALSA)
      ba0_sscanf2 (polys, "%t[%simplify_expanded_Qz]", &U);
#else
      ba0_sscanf2 (polys, "%t[%simplify_Qz]", &U);
#endif
      for (k = 0; k < U.size; k++)
        {
          for (i = 0; i < T.size; i++)
            {
              term = T.tab[i];
              for (j = 0; j < term->size; j++)
                {
                  y = term->rg[j].var->root;
                  for (d = 0; d < term->rg[j].deg; d++)
                    baz_diff_ratfrac (U.tab[k], U.tab[k], y);
                }
            }
        }
#if ! defined (BMI_BALSA)
      bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
#endif
      stres = ba0_new_printf ("%t[%Qz]", &U);
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
