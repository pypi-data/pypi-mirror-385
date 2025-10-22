#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_is_reduced.h"

static ALGEB bmi_is_reduced2 (
    struct bmi_callback *callback);

/*
 * EXPORTED
 * IsReduced (list of differential polynomials, method, regchain)
 * IsReduced (list of differential polynomials, method, redset, drideal)
 *
 * returns a list of boolean
 */

ALGEB
bmi_is_reduced (
    struct bmi_callback *callback)
{
  struct bad_regchain C;
  struct bap_tableof_polynom_mpq polys;
  struct bap_polynom_mpz numer;
  struct ba0_tableof_int_p result;
  char *method;
  enum bad_typeof_reduction type_red;
  ba0_int_p i;

  if (bmi_nops (callback) != 3)
    return bmi_is_reduced2 (callback);
  if (!bmi_is_regchain_op (3, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRREGC);

  bmi_set_ordering_and_regchain (&C, 3, callback, __FILE__, __LINE__);

  method = bmi_string_op (2, callback);
  if (!bad_defines_a_differential_ideal_regchain (&C) ||
      strcmp (method, BMI_IX_algebraically) == 0)
    type_red = bad_algebraic_reduction;
  else if (strcmp (method, BMI_IX_partially) == 0)
    type_red = bad_partial_reduction;
  else
    type_red = bad_full_reduction;

  ba0_init_table ((struct ba0_table *) &polys);
#if ! defined (BMI_BALSA)
  ba0_sscanf2 (bmi_string_op (1, callback), "%t[%simplify_expanded_Aq]",
      &polys);
#else
  ba0_sscanf2 (bmi_string_op (1, callback), "%t[%simplify_Aq]", &polys);
#endif
  ba0_init_table ((struct ba0_table *) &result);
  ba0_realloc_table ((struct ba0_table *) &result, polys.size);

  bap_init_polynom_mpz (&numer);

  for (i = 0; i < polys.size; i++)
    {
      bap_numer_polynom_mpq (&numer, 0, polys.tab[i]);
      result.tab[result.size] =
          !bad_is_a_reducible_polynom_by_regchain
          (&numer, &C, type_red, bad_all_derivatives_to_reduce,
          (struct bav_rank *) 0, (ba0_int_p *) 0);
      result.size += 1;
    }

  {
    ALGEB res;
    bmi_push_maple_gmp_allocators ();
    res = MapleListAlloc (callback->kv, (M_INT) result.size);
    for (i = 0; i < result.size; i++)
      MapleListAssign (callback->kv, res, (M_INT) i + 1,
          ToMapleBoolean (callback->kv, (long) result.tab[i]));
    bmi_pull_maple_gmp_allocators ();
    return res;
  }
}

/*
 * IsReduced2 (list of differential polynomials, method, redset, drideal)
 *
 * returns a list of boolean
 */

static ALGEB
bmi_is_reduced2 (
    struct bmi_callback *callback)
{
  struct bad_regchain C;
  struct bap_tableof_polynom_mpq polys;
  struct bap_polynom_mpz numer;
  struct ba0_tableof_string properties;
  struct ba0_tableof_int_p result;
  char *method;
  enum bad_typeof_reduction type_red;
  ba0_int_p i;

  if (bmi_nops (callback) != 4)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_table_op (4, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRDRNG);

  if (bmi_is_regchain_op (4, callback))
    bmi_set_ordering_and_regchain (&C, 4, callback, __FILE__, __LINE__);
  else
    bmi_set_ordering (4, callback, __FILE__, __LINE__);

  method = bmi_string_op (2, callback);
  if (bav_global.R.ders.size == 0 || strcmp (method, BMI_IX_algebraically) == 0)
    type_red = bad_algebraic_reduction;
  else if (strcmp (method, BMI_IX_partially) == 0)
    type_red = bad_partial_reduction;
  else
    type_red = bad_full_reduction;

  ba0_init_table ((struct ba0_table *) &polys);
#if ! defined (BMI_BALSA)
  ba0_sscanf2 (bmi_string_op (1, callback), "%t[%simplify_expanded_Aq]",
      &polys);
#else
  ba0_sscanf2 (bmi_string_op (1, callback), "%t[%simplify_Aq]", &polys);
#endif
/*
 * Mostly: C = PretendRegchain (redset)
 */
  bad_init_regchain (&C);
#if ! defined (BMI_BALSA)
  ba0_sscanf2
      (bmi_string_op (3, callback), "%t[%expanded_Az]", &C.decision_system);
#else
  ba0_sscanf2 (bmi_string_op (3, callback), "%t[%simplify_Az]",
      &C.decision_system);
#endif
  for (i = 0; i < C.decision_system.size; i++)
    if (bap_is_independent_polynom_mpz (C.decision_system.tab[i]))
      BA0_RAISE_EXCEPTION (BMI_ERRIND);
  ba0_init_table ((struct ba0_table *) &properties);
  if (bav_global.R.ders.size > 0)
    ba0_sscanf2 ("[differential]", "%t[%s]", &properties);
  bad_set_regchain_tableof_polynom_mpz
      (&C, &C.decision_system, &properties, true);
/*
 * Go
 */
  ba0_init_table ((struct ba0_table *) &result);
  ba0_realloc_table ((struct ba0_table *) &result, polys.size);

  bap_init_polynom_mpz (&numer);

  for (i = 0; i < polys.size; i++)
    {
      bap_numer_polynom_mpq (&numer, 0, polys.tab[i]);
      result.tab[result.size] =
          !bad_is_a_reducible_polynom_by_regchain
          (&numer, &C, type_red, bad_all_derivatives_to_reduce,
          (struct bav_rank *) 0, (ba0_int_p *) 0);
      result.size += 1;
    }

  {
    ALGEB res;
    bmi_push_maple_gmp_allocators ();
    res = MapleListAlloc (callback->kv, (M_INT) result.size);
    for (i = 0; i < result.size; i++)
      MapleListAssign (callback->kv, res, (M_INT) i + 1,
          ToMapleBoolean (callback->kv, (long) result.tab[i]));
    bmi_pull_maple_gmp_allocators ();
    return res;
  }
}
