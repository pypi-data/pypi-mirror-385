#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_factor_derivative.h"

/*
 * FactorDerivative (derivative, differential ring)
 *
 * derivative = u[x,x,y] -> the list [u,x,x,y]
 */

ALGEB
bmi_factor_derivative (
    struct bmi_callback *callback)
{
  struct bav_term T;
  struct bav_variable *v, *d;
  bav_Iorder o;
  ba0_int_p i;
  char *derivative;

  if (bmi_nops (callback) != 2)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_table_op (2, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRDRNG);

  bmi_set_ordering (2, callback, __FILE__, __LINE__);

  derivative = bmi_string_op (1, callback);
  ba0_sscanf2 (derivative, "%v", &v);

  if (v == BAV_NOT_A_VARIABLE || v->root->type != bav_dependent_symbol)
    BA0_RAISE_EXCEPTION (BMI_ERRINDV);

  bav_init_term (&T);
  bav_realloc_term (&T, bav_global.R.ders.size);
  for (i = 0; i < bav_global.R.ders.size; i++)
    {
      d = bav_derivation_index_to_derivation (i);
      o = bav_order_variable (v, d->root);
      if (o > 0)
        {
          T.rg[T.size].var = d;
          T.rg[T.size].deg = o;
          T.size += 1;
        }
    }
  v = bav_order_zero_variable (v);

  {
    char *stres;
    ALGEB res;
#if ! defined (BMI_BALSA)
    bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
#endif
    stres = ba0_new_printf ("%term, %v", &T, v);
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
