#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_belongs_to.h"

/*
 * EXPORTED
 * BelongsTo ([polynomials], regular chain)
 *
 * returns a list of boolean
 */

ALGEB
bmi_belongs_to (
    struct bmi_callback *callback)
{
  struct bad_regchain C;
  struct bap_tableof_polynom_mpq polys;
  struct bap_polynom_mpz numer;
  struct ba0_tableof_int_p result;
  enum bad_typeof_reduction type_red;
  ba0_int_p i;

  if (bmi_nops (callback) != 2)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_regchain_op (2, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRREGC);

  bmi_set_ordering_and_regchain (&C, 2, callback, __FILE__, __LINE__);
  if (bad_defines_a_differential_ideal_regchain (&C))
    type_red = bad_full_reduction;
  else
    type_red = bad_algebraic_reduction;

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
          bad_is_a_reduced_to_zero_polynom_by_regchain (&numer, &C, type_red);
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
