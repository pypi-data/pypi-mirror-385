#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_is_constant.h"

/*
 * IsConstant (list(ratfrac), derivation | "0", differential ring)
 */

ALGEB
bmi_is_constant (
    struct bmi_callback *callback)
{
  struct bad_regchain C;
  struct baz_tableof_ratfrac T;
  struct bav_symbol *x;
  struct ba0_tableof_int_p result;
  ba0_int_p i;
  char *derivation;
  char *ratfracs;

  if (bmi_nops (callback) != 3)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_table_op (3, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRDRNG);

  if (bmi_is_regchain_op (3, callback))
    bmi_set_ordering_and_regchain (&C, 3, callback, __FILE__, __LINE__);
  else
    bmi_set_ordering (3, callback, __FILE__, __LINE__);

  derivation = bmi_string_op (2, callback);
  if (strcmp (derivation, "0") == 0)
    x = (struct bav_symbol *) 0;
  else
    ba0_sscanf2 (derivation, "%y", &x);

  ratfracs = bmi_string_op (1, callback);
  ba0_init_table ((struct ba0_table *) &T);
#if ! defined (BMI_BALSA)
  ba0_sscanf2 (ratfracs, "%t[%simplify_expanded_Qz]", &T);
#else
  ba0_sscanf2 (ratfracs, "%t[%simplify_Qz]", &T);
#endif
  ba0_init_table ((struct ba0_table *) &result);
  ba0_realloc_table ((struct ba0_table *) &result, T.size);

  for (i = 0; i < T.size; i++)
    {
      result.tab[i] = baz_is_constant_ratfrac (T.tab[i], x);
      result.size = i + 1;
    }
#if ! defined (BMI_BALSA)
  {
    ALGEB res;
    bmi_push_maple_gmp_allocators ();
    res = MapleListAlloc (callback->kv, (M_INT) result.size);
    MapleGcProtect (callback->kv, res);
    for (i = 0; i < result.size; i++)
      MapleListAssign (callback->kv, res, (M_INT) i + 1,
          ToMapleBoolean (callback->kv, (long) result.tab[i]));
    bmi_pull_maple_gmp_allocators ();
    return res;
  }
#else
  {
    char *stres;
    ALGEB res;
    struct ba0_tableof_string result_string;

    ba0_init_table ((struct ba0_table *) &result_string);
    ba0_realloc_table ((struct ba0_table *) &result_string, result.size);
    for (i = 0; i < result.size; i++)
      {
#   if defined (BMI_SYMPY)
        result_string.tab[i] = result.tab[i] ? "True" : "False";
#   elif defined (BMI_SAGE)
        result_string.tab[i] = result.tab[i] ? "true" : "false";
#   endif
        result_string.size = i + 1;
      }
    stres = ba0_new_printf ("%t[%s]", &result_string);
    res = bmi_balsa_new_string (stres);
    return res;
  }
#endif
}
