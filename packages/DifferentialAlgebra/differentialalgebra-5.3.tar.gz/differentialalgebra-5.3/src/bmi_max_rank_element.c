#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_max_rank_element.h"

/*
 * EXPORTED
 *
 * MaxRank (list(polynomial), differential ring)
 *
 * Returns the Maximum and its index
 */

ALGEB
bmi_max_rank_element (
    struct bmi_callback *callback)
{
  struct bap_tableof_polynom_mpq T;
  struct bap_polynom_mpq *M;
  ba0_int_p i, m;
  char *eqns;

  if (bmi_nops (callback) != 2)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_table_op (2, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRDRNG);
  bmi_set_ordering (2, callback, __FILE__, __LINE__);

  eqns = bmi_string_op (1, callback);
  ba0_init_table ((struct ba0_table *) &T);
#if ! defined (BMI_BALSA)
  ba0_sscanf2 (eqns, "%t[%simplify_expanded_Aq]", &T);
#else
  ba0_sscanf2 (eqns, "%t[%simplify_Aq]", &T);
#endif

  if (T.size == 0)
    BA0_RAISE_EXCEPTION (BMI_ERRNIL);

  m = 0;
  M = T.tab[0];
  for (i = 1; i < T.size; i++)
    {
      if (bap_lt_rank_polynom_mpq (M, T.tab[i]))
        {
          m = i;
          M = T.tab[i];
        }
    }

  {
    char *stres;
    ALGEB res;
#if ! defined (BMI_BALSA)
    bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
#endif
    stres = ba0_new_printf ("%Aq, %d", M, m + 1);
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
