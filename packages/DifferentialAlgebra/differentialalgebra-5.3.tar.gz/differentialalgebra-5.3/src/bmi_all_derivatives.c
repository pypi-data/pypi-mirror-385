#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_all_derivatives.h"

static ALGEB bmi_all_derivatives2 (
    struct bmi_callback *callback);

/*
 * AllDerivatives (ordre, regchain)
 * AllDerivatives (depv, ordre, R, corners)
 *
 * If depv is "0", then returns the list of all the derivatives of 
 * all the independent variables. Call from Indets. See below.
 *
 * Returns the list of all the derivatives of depv, of total order less 
 * than or equal to ordre, which are not derivatives of corners.
 * Call from PowerSeriesSolution.
 */

ALGEB
bmi_all_derivatives (
    struct bmi_callback *callback)
{
  struct bad_regchain C;
  struct bav_tableof_variable T, U;
  struct bav_variable *u;
  bav_Iorder ord;
  char *depv, *ordre, *corners;

  if (bmi_nops (callback) != 4)
    return bmi_all_derivatives2 (callback);
  if (!bmi_is_table_op (3, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRDRNG);

  if (bmi_is_regchain_op (3, callback))
    bmi_set_ordering_and_regchain (&C, 3, callback, __FILE__, __LINE__);
  else
    bmi_set_ordering (3, callback, __FILE__, __LINE__);

  depv = bmi_string_op (1, callback);
  ordre = bmi_string_op (2, callback);
  corners = bmi_string_op (4, callback);

  ba0_sscanf2 (depv, "%v", &u);
  ord = (bav_Iorder) atoi (ordre);
  ba0_init_table ((struct ba0_table *) &T);
  ba0_sscanf2 (corners, "%t[%v]", &T);

  ba0_init_table ((struct ba0_table *) &U);
  ba0_realloc_table ((struct ba0_table *) &U, 20);
  while (u != BAV_NOT_A_VARIABLE && bav_total_order_variable (u) <= ord)
    {
      if (U.size == U.alloc)
        ba0_realloc_table ((struct ba0_table *) &U, U.size * 2);
      U.tab[U.size] = u;
      U.size += 1;
      u = bav_next_derivative (u, &T);
    }

  {
    ALGEB res;
    char *stres;
#if ! defined (BMI_BALSA)
    bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
#endif
    stres = ba0_new_printf ("%t[%v]", &U);
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

/*
 * All derivatives of all the dependent variables
 * Called through Indets (ideal, selection=iniconds(ordre))
 */

static ALGEB
bmi_all_derivatives2 (
    struct bmi_callback *callback)
{
  struct bad_regchain C;
  struct bav_tableof_variable T, U;
  struct bav_variable *u;
  bav_Iorder ord;
  char *ordre;
  ba0_int_p i;

  if (bmi_nops (callback) != 2)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_regchain_op (2, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRDRNG);

  bmi_set_ordering_and_regchain (&C, 2, callback, __FILE__, __LINE__);

  ordre = bmi_string_op (1, callback);
  ord = (bav_Iorder) atoi (ordre);

  ba0_init_table ((struct ba0_table *) &T);
  ba0_realloc_table ((struct ba0_table *) &T, C.decision_system.size);
  for (i = 0; i < C.decision_system.size; i++)
    {
      T.tab[i] = bap_leader_polynom_mpz (C.decision_system.tab[i]);
      T.size = i + 1;
    }
/*
 * It used to be a loop on bav_global.R.deps (the dependent variables)
 * but it may not make sense anymore. Temporary fix.
 */
  ba0_init_table ((struct ba0_table *) &U);
  ba0_realloc_table ((struct ba0_table *) &U, 20);
  for (i = 0; i < bav_global.R.syms.size; i++)
    {
      struct bav_symbol *y = bav_global.R.syms.tab[i];
      if (y->type == bav_dependent_symbol)
        {
          u = bav_R_string_to_existing_variable (y->ident);
          if (ba0_member_table (u, (struct ba0_table *) &T))
            u = BAV_NOT_A_VARIABLE;
          while (u != BAV_NOT_A_VARIABLE && bav_total_order_variable (u) <= ord)
            {
              if (U.size == U.alloc)
                ba0_realloc_table ((struct ba0_table *) &U, U.size * 2);
              U.tab[U.size] = u;
              U.size += 1;
              u = bav_next_derivative (u, &T);
            }
        }
    }

  {
    ALGEB res;
    char *stres;
#if ! defined (BMI_BALSA)
    bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
#endif
    stres = ba0_new_printf ("%t{%v}", &U);
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
