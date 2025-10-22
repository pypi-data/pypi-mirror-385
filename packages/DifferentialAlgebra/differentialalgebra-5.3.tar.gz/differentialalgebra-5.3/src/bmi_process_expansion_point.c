#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_process_expansion_point.h"

/*
 * ProcessExpansionPoint 
 * 	(list of rational fractions, list L of variables, regchain or DRing)
 *
 * Returns a sequence indepsubs, dersubs_u, dersubs_i, dersubs_op, freeders 
 * 	where
 *
 * depsubs is the list of indices in L of the independent variables
 *
 * dersubs_u is a list of derivatives u
 * dersubs_i is a list of indices in L of derivatives v, 
 * dersups_op is a list of derivation operators phi,
 *
 * 	such that u occurs in some rational fraction and phi v = u
 *
 * freeders is a list of derivatives occurring in the rational fractions,
 *      which are not derivatives of any v in L
 */

static int bav_comp_order (
    const void *x,
    const void *y);

ALGEB
bmi_process_expansion_point (
    struct bmi_callback *callback)
{
  struct bad_regchain C;
  struct baz_tableof_ratfrac U;
  struct bav_tableof_term dersubs_op;
  struct bav_dictionary_variable dict;
  struct bav_tableof_variable L, X, dersubs_u, freeders;
  struct bav_variable *u, *v, *former_v;
  bav_Iorder order_v, former_order_v;
  struct ba0_tableof_int_p dersubs_i, indepsubs;
  ba0_int_p i, j, former_j;
  bool found;
  char *ratfracs, *variables;

  if (bmi_nops (callback) != 3)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_table_op (3, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRDRNG);

  if (bmi_is_regchain_op (3, callback))
    bmi_set_ordering_and_regchain (&C, 3, callback, __FILE__, __LINE__);
  else
    bmi_set_ordering (3, callback, __FILE__, __LINE__);

  ratfracs = bmi_string_op (1, callback);
  ba0_init_table ((struct ba0_table *) &U);
#if ! defined (BMI_BALSA)
  ba0_sscanf2 (ratfracs, "%t[%simplify_expanded_Qz]", &U);
#else
  ba0_sscanf2 (ratfracs, "%t[%simplify_Qz]", &U);
#endif

  variables = bmi_string_op (2, callback);
  ba0_init_table ((struct ba0_table *) &L);
  ba0_sscanf2 (variables, "%t[%v]", &L);
/*
 * The sorted list of independent variables
 */
  ba0_init_table ((struct ba0_table *) &indepsubs);
  ba0_realloc_table ((struct ba0_table *) &indepsubs, bav_global.R.ders.size);
  for (i = 0; i < bav_global.R.ders.size; i++)
    {
      v = bav_global.R.vars.tab[bav_global.R.ders.tab[i]];
      if (ba0_member2_table (v, (struct ba0_table *) &L, &j))
        {
          indepsubs.tab[indepsubs.size] = j + 1;
          indepsubs.size += 1;
        }
    }
/*
 * The list of derivatives which occur in the rational fractions.
 * The list is sorted by decreasing total order (may not be necessary).
 */
  bav_init_dictionary_variable (&dict, 6);
  ba0_init_table ((struct ba0_table *) &X);
  ba0_realloc_table ((struct ba0_table *) &X, 64);
  for (i = 0; i < U.size; i++)
    {
      bap_mark_indets_polynom_mpz (&dict, &X, &U.tab[i]->numer);
      bap_mark_indets_polynom_mpz (&dict, &X, &U.tab[i]->denom);
    }
  i = 0;
  while (i < X.size)
    {
      if (bav_symbol_type_variable (X.tab[i]) == bav_independent_symbol)
        ba0_delete_table ((struct ba0_table *) &X, i);
      else
        i += 1;
    }
  qsort (X.tab, X.size, sizeof (struct bav_variable *), &bav_comp_order);
/*
 * The lists dersubs_u, dersubs_i, dersubs_op, freeders
 */
  ba0_init_table ((struct ba0_table *) &dersubs_u);
  ba0_realloc_table ((struct ba0_table *) &dersubs_u, X.size);
  ba0_init_table ((struct ba0_table *) &dersubs_i);
  ba0_realloc_table ((struct ba0_table *) &dersubs_i, X.size);
  ba0_init_table ((struct ba0_table *) &dersubs_op);
  ba0_realloc2_table ((struct ba0_table *) &dersubs_op, X.size,
      (ba0_new_function *) & bav_new_term);
  ba0_init_table ((struct ba0_table *) &freeders);
  ba0_realloc_table ((struct ba0_table *) &freeders, X.size);

  former_v = BAV_NOT_A_VARIABLE;
  former_j = -1;
  former_order_v = -1;

  for (i = 0; i < X.size; i++)
    {
      u = X.tab[i];
      found = false;
      for (j = 0; j < L.size; j++)
        {
          v = L.tab[j];
          if (bav_symbol_type_variable (v) == bav_dependent_symbol)
            {
              order_v = bav_total_order_variable (v);
              if (bav_is_derivative (u, v) &&
                  ((!found) || (found && order_v > former_order_v)))
                {
                  former_v = v;
                  former_order_v = order_v;
                  former_j = j;
                  found = true;
                }
            }
        }
      if (found)
        {
          dersubs_u.tab[dersubs_u.size] = u;
          dersubs_i.tab[dersubs_i.size] = former_j + 1;
          bav_operator_between_derivatives
              (dersubs_op.tab[dersubs_op.size], former_v, u);
          dersubs_u.size += 1;
          dersubs_i.size += 1;
          dersubs_op.size += 1;
        }
      else
        {
          freeders.tab[freeders.size] = u;
          freeders.size += 1;
        }
    }
/*
 * The result
 */
  {
    ALGEB res;
    char *stres;
#if ! defined (BMI_BALSA)
    bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
    stres =
        ba0_new_printf ("%t[%d], %t[%v], %t[%d], %t[%term], %t[%v]",
        &indepsubs, &dersubs_u, &dersubs_i, &dersubs_op, &freeders);
    bmi_push_maple_gmp_allocators ();
    res = EvalMapleStatement (callback->kv, stres);
    bmi_pull_maple_gmp_allocators ();
#else
/*
 * The sequence is converted as a list
 */
    bmi_push_maple_gmp_allocators ();
    res = MapleListAlloc (callback->kv, 5);
    bmi_pull_maple_gmp_allocators ();

    stres = ba0_new_printf ("%t[%d]", &indepsubs);

    bmi_push_maple_gmp_allocators ();
    MapleListAssign (callback->kv, res, 1, bmi_balsa_new_string (stres));
    bmi_pull_maple_gmp_allocators ();

    stres = ba0_new_printf ("%t[%v]", &dersubs_u);

    bmi_push_maple_gmp_allocators ();
    MapleListAssign (callback->kv, res, 2, bmi_balsa_new_string (stres));
    bmi_pull_maple_gmp_allocators ();

    stres = ba0_new_printf ("%t[%d]", &dersubs_i);

    bmi_push_maple_gmp_allocators ();
    MapleListAssign (callback->kv, res, 3, bmi_balsa_new_string (stres));
    bmi_pull_maple_gmp_allocators ();

    stres = ba0_new_printf ("%t[%term]", &dersubs_op);

    bmi_push_maple_gmp_allocators ();
    MapleListAssign (callback->kv, res, 4, bmi_balsa_new_string (stres));
    bmi_pull_maple_gmp_allocators ();

    stres = ba0_new_printf ("%t[%v]", &freeders);

    bmi_push_maple_gmp_allocators ();
    MapleListAssign (callback->kv, res, 5, bmi_balsa_new_string (stres));
    bmi_pull_maple_gmp_allocators ();
#endif
    return res;
  }
}

/*
 * To be used with qsort.
 * One wants the variables with lower order first.
 * Thus order (x) > order (y) ==> x < y
 */

static int
bav_comp_order (
    const void *x,
    const void *y)
{
  bav_Iorder ox, oy;
  ox = bav_total_order_variable (*(struct bav_variable * *) x);
  oy = bav_total_order_variable (*(struct bav_variable * *) y);
  return ox < oy ? -1 : ox == oy ? 0 : 1;
}
