#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_field_element.h"
#include "bmi_base_field_generators.h"

/*
 * EXPORTED
 * FieldElement ([rational fractions], generators, relations, dring)
 *
 * returns a list of boolean
 */

ALGEB
bmi_field_element (
    struct bmi_callback *callback)
{
  struct bad_base_field K;
  struct bad_regchain C;
  struct baz_tableof_ratfrac Q;
  struct ba0_tableof_range_indexed_group G;
  struct ba0_tableof_int_p result;
  ba0_int_p i;
  char *generators, *relations;

  if (bmi_nops (callback) != 4)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_table_op (4, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRREGC);

  if (bmi_is_regchain_op (4, callback))
    bmi_set_ordering_and_regchain (&C, 4, callback, __FILE__, __LINE__);
  else
    bmi_set_ordering (4, callback, __FILE__, __LINE__);

  generators = bmi_string_op (2, callback);
  relations = bmi_string_op (3, callback);

  ba0_init_table ((struct ba0_table *) &G);
  ba0_sscanf2 (generators, "%t[%range_indexed_group]", &G);

  bad_init_regchain (&C);
  ba0_sscanf2 (relations, "%pretend_regchain", &C);

  bad_init_base_field (&K);
  bad_set_base_field_generators_and_relations (&K, &G, &C, false);
/*
    ba0_printf ("%base_field\n", &K);
 */
  ba0_init_table ((struct ba0_table *) &Q);
#if ! defined (BMI_BALSA)
  ba0_sscanf2 (bmi_string_op (1, callback), "%t[%simplify_expanded_Qz]", &Q);
#else
  ba0_sscanf2 (bmi_string_op (1, callback), "%t[%simplify_Qz]", &Q);
#endif

  ba0_init_table ((struct ba0_table *) &result);
  ba0_realloc_table ((struct ba0_table *) &result, Q.size);

  for (i = 0; i < Q.size; i++)
    {
      result.tab[result.size] =
          bad_member_polynom_base_field (&Q.tab[i]->numer, &K) &&
          bad_member_nonzero_polynom_base_field (&Q.tab[i]->denom, &K);
/*
	ba0_printf ("%Qz, %d\n", Q.tab [i], result.tab [i]);
*/
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
