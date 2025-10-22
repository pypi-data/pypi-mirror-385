#include "bmi_blad_eval.h"
#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_base_field_generators.h"

/*
 * BaseFieldGenerators (generators, relations, regchain | ring)
 */

ALGEB
bmi_base_field_generators (
    struct bmi_callback *callback)
{
  struct bad_base_field K;
  struct bad_regchain C, R;
  struct ba0_tableof_range_indexed_group G;
  char *generators, *relations;
  bool differential;

  if (bmi_nops (callback) != 3)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  else if (!bmi_is_table_op (3, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRDRNG);

  if (bmi_is_regchain_op (3, callback))
    bmi_set_ordering_and_regchain (&R, 3, callback, __FILE__, __LINE__);
  else
    bmi_set_ordering (3, callback, __FILE__, __LINE__);

  differential = bav_global.R.ders.size > 0;
  generators = bmi_string_op (1, callback);
  relations = bmi_string_op (2, callback);

  ba0_init_table ((struct ba0_table *) &G);
  ba0_sscanf2 (generators, "%t[%range_indexed_group]", &G);

  bad_init_regchain (&C);
  ba0_sscanf2 (relations, "%pretend_regchain", &C);
/*
 * Define the base field, then, get its list of generators
 */
  bad_init_base_field (&K);
  bad_set_base_field_generators_and_relations (&K, &G, &C, false);
  bad_base_field_generators (&G, &K);
/*
 * MAPLE only. This code does not work anymore.
 *
 * Append the list of independent variables, which are omitted by
 * bad_base_field_generators.
 * #if ! defined (BMI_BALSA)
 *   ba0_realloc_table ((struct ba0_table *) &T, T.size + bav_global.R.ders.size);
 *   for (i = 0; i < bav_global.R.ders.size; i++)
 *     {
 *       T.tab[T.size] = bav_global.R.vars.tab[bav_global.R.ders.tab[i]];
 *       T.size += 1;
 *     }
 * #endif
 */
  {
    char *stres;
    ALGEB res;
#if ! defined (BMI_BALSA)
    bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
#endif
    stres = ba0_new_printf ("%t[%range_indexed_group]", &G);
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
