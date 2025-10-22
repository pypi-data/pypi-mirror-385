#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_ranking.h"

/*
 * EXPORTED
 */

ALGEB
bmi_ranking (
    struct bmi_callback *callback)
{
  bav_Iordering r;
  char *stres;
  ALGEB res;

  if (bmi_nops (callback) != 1)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_table_op (1, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRDRNG);
  r = bmi_set_ordering (1, callback, __FILE__, __LINE__);

#if ! defined (BMI_BALSA)
  bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
#endif
  stres = ba0_new_printf ("%ordering", r);
  bmi_push_maple_gmp_allocators ();
#if ! defined (BMI_BALSA)
  res = EvalMapleStatement (callback->kv, stres);
#else
  res = bmi_balsa_new_string (stres);
#endif
  bmi_pull_maple_gmp_allocators ();
  return res;
}
