#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_indets.h"

/*
 * EXPORTED
 *
 * Indets (list(polynomials) | regchain | differential ring, 
 * 		selection, 
 *              fullset | variable | 0, 
 *              differential ring | regular chain)
 *     
 *     Applies to the variables occurring in the list of polynomials
 *
 *     If the first op is a differential ring then it is the same as
 *     the last op and the function applies to the ring variables.
 *
 * fullset is now ignored: the defining equations of parameters are implicit
 */

ALGEB
bmi_indets (
    struct bmi_callback *callback)
{
  struct bad_regchain C;
  struct baz_tableof_ratfrac T;
  struct bav_tableof_variable U;
  struct bav_dictionary_variable dict;
  struct bav_tableof_variable vars;
  struct bav_variable *v;
  struct bav_symbol *sym;
  ba0_int_p i;
  bool depvars, indepvars, derivatives, allvars, params, constants;
  char *eqns, *selection;

  if (bmi_nops (callback) != 4)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_table_op (4, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRDRNG);

  if (bmi_is_regchain_op (1, callback))
    bmi_set_ordering_and_regchain (&C, 1, callback, __FILE__, __LINE__);
  else if (bmi_is_regchain_op (4, callback))
    bmi_set_ordering_and_regchain (&C, 4, callback, __FILE__, __LINE__);
  else
    bmi_set_ordering (4, callback, __FILE__, __LINE__);

  bav_init_dictionary_variable (&dict, 6);
  ba0_init_table ((struct ba0_table *) &vars);
  ba0_realloc_table ((struct ba0_table *) &vars, 64);

  selection = bmi_string_op (2, callback);
/*
 * What the criterion applies to
 */
  if (bmi_is_regchain_op (1, callback))
    {
      if (strcmp (selection, BMI_IX_constants) == 0)
        BA0_RAISE_EXCEPTION (BMI_ERRCRIT);
      for (i = 0; i < C.decision_system.size; i++)
        bap_mark_indets_polynom_mpz (&dict, &vars, C.decision_system.tab[i]);
    }
  else if (bmi_is_dring_op (1, callback))
    {
      ba0_set_table ((struct ba0_table *) &vars,
          (struct ba0_table *) &bav_global.R.vars);
    }
  else
    {
      eqns = bmi_string_op (1, callback);
      ba0_init_table ((struct ba0_table *) &T);
#if ! defined (BMI_BALSA)
      ba0_sscanf2 (eqns, "%t[%simplify_expanded_Qz]", &T);
#else
      ba0_sscanf2 (eqns, "%t[%simplify_Qz]", &T);
#endif
      for (i = 0; i < T.size; i++)
        {
          bap_mark_indets_polynom_mpz (&dict, &vars, &T.tab[i]->numer);
          bap_mark_indets_polynom_mpz (&dict, &vars, &T.tab[i]->denom);
        }
    }

  depvars = indepvars = derivatives = allvars = params = constants = false;
  if (strcmp (selection, BMI_IX_depvars) == 0
      || strcmp (selection, "dependent") == 0)
    depvars = true;
  else if (strcmp (selection, BMI_IX_indepvars) == 0 ||
      strcmp (selection, "independent") == 0 ||
      strcmp (selection, "derivations") == 0)
    indepvars = true;
  else if (strcmp (selection, BMI_IX_derivs) == 0)
    derivatives = true;
  else if (strcmp (selection, BMI_IX_allvars) == 0 ||
      strcmp (selection, "all") == 0)
    allvars = true;
  else if (strcmp (selection, BMI_IX_params) == 0)
    params = true;
  else if (strcmp (selection, BMI_IX_constants) == 0)
    {
      char *strsym = bmi_string_op (3, callback);
      if (strcmp (strsym, "0") == 0)
        sym = BAV_NOT_A_SYMBOL;
      else
        {
          ba0_sscanf2 (strsym, "%y", &sym);
          if (sym->type != bav_independent_symbol)
            BA0_RAISE_EXCEPTION (BMI_ERRDER);
        }
      constants = true;
    }
  else
    BA0_RAISE_EXCEPTION (BMI_ERRCRIT);

  ba0_init_table ((struct ba0_table *) &U);
  ba0_realloc_table ((struct ba0_table *) &U, bav_global.R.vars.size);

  for (i = 0; i < vars.size; i++)
    {
      v = vars.tab[i];
      if (allvars)
        U.tab[U.size++] = v;
      else if (derivatives && bav_symbol_type_variable (v) ==
          bav_dependent_symbol)
        U.tab[U.size++] = v;
      else if (depvars && bav_symbol_type_variable (v) == bav_dependent_symbol)
        U.tab[U.size++] = bav_order_zero_variable (v);
      else if (params && bav_is_a_parameter
          (v->root, (struct bav_parameter **) 0))
        U.tab[U.size++] = v;
      else if (indepvars && bav_symbol_type_variable (v) ==
          bav_independent_symbol)
        U.tab[U.size++] = v;
      else if (constants &&
          bav_symbol_type_variable (v) == bav_dependent_symbol &&
          bav_is_constant_variable (v, sym))
        U.tab[U.size++] = v;
    }
  ba0_sort_table ((struct ba0_table *) &U, (struct ba0_table *) &U);
  ba0_unique_table ((struct ba0_table *) &U, (struct ba0_table *) &U);

  {
    char *stres;
    ALGEB res;
#if ! defined (BMI_BALSA)
    bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
    stres = ba0_new_printf ("%t{%v}", &U);
#else
    stres = ba0_new_printf ("%t[%v]", &U);
#endif
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
