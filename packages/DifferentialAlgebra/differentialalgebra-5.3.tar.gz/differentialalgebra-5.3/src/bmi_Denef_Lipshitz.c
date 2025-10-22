#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_Denef_Lipshitz.h"

/*
 * EXPORTED
 * DenefLipshitz (equations, inequations,
 *         properties,
 *         differential ring,
 *         Y, Ybar,
 *         q, x, beta_control)
 *
 *     or
 *
 * DenefLipshitz (equations, inequations, DLuple)
 * 
 * equations and inequations are lists of differential polynomials
 * properties are lists of attributes
 * differential ring is a table
 * Y is the list of differential indeterminates for which series are sought
 * Ybar permits to compute prolongation equations from differential polynomials
 * q is the variable for the polynomial A(q)
 * x is the derivation
 * beta_control is not used anymore
 */

ALGEB
bmi_Denef_Lipshitz (
    struct bmi_callback *callback)
{
  char *str_equations;
  char *str_inequations;
  char *str_properties;
  char *str_Y;
  char *str_Ybar;
  char *str_q;
  char *str_x;
  char *str_beta_control;

  struct bas_tableof_DLuple DL;
  struct bas_DL_tree tree;
  struct bap_tableof_polynom_mpz eqns;
  struct bap_tableof_polynom_mpz ineqs;
  struct ba0_tableof_string properties;
  struct bav_tableof_symbol Y;
  struct baz_prolongation_pattern Ybar;
  struct bav_variable *q;
  struct bav_symbol *x;

  char *str_stripped_DLuple;
  ALGEB L, L1, L2, L3, stripped_DLuple, cell;
  ba0_int_p i;

  if (bmi_nops (callback) == 9)
    {
      if (!bmi_is_table_op (4, callback))
        BA0_RAISE_EXCEPTION (BMI_ERRDRNG);

      bmi_set_ordering (4, callback, __FILE__, __LINE__);

      str_equations = bmi_string_op (1, callback);
      str_inequations = bmi_string_op (2, callback);
      str_properties = bmi_string_op (3, callback);
      str_Y = bmi_string_op (5, callback);
      str_Ybar = bmi_string_op (6, callback);
      str_q = bmi_string_op (7, callback);
      str_x = bmi_string_op (8, callback);
      str_beta_control = bmi_string_op (9, callback);

      ba0_init_table ((struct ba0_table *) &DL);
      bas_init_DL_tree (&tree);
      bas_reset_DL_tree (&tree, bas_quiet_DL_tree);
      ba0_init_table ((struct ba0_table *) &eqns);
      ba0_init_table ((struct ba0_table *) &ineqs);
      ba0_init_table ((struct ba0_table *) &properties);
      ba0_init_table ((struct ba0_table *) &Y);
      baz_init_prolongation_pattern (&Ybar);

      ba0_sscanf2 (str_equations, "%t[%simplify_Az]", &eqns);
      ba0_sscanf2 (str_inequations, "%t[%simplify_Az]", &ineqs);
      ba0_sscanf2 (str_properties, "%t[%s]", &properties);
      ba0_sscanf2 (str_Y, "%t[%y]", &Y);
      ba0_sscanf2 (str_Ybar, "%prolongation_pattern", &Ybar);
      ba0_sscanf2 (str_q, "%v", &q);
      ba0_sscanf2 (str_x, "%y", &x);

      bas_Denef_Lipshitz (&DL, &tree, &eqns, &ineqs, &properties, &Y, &Ybar, q,
          x);
    }
  else if (bmi_nops (callback) == 3)
    {
      struct bas_DLuple U;

      if (!bmi_is_table_op (3, callback))
        BA0_RAISE_EXCEPTION (BMI_ERRDLUP);

      bmi_set_ordering_and_DLuple (&U, 3, callback, __FILE__, __LINE__);

      str_equations = bmi_string_op (1, callback);
      str_inequations = bmi_string_op (2, callback);

      ba0_init_table ((struct ba0_table *) &DL);
      ba0_init_table ((struct ba0_table *) &eqns);
      ba0_init_table ((struct ba0_table *) &ineqs);

      ba0_sscanf2 (str_equations, "%t[%simplify_Az]", &eqns);
      ba0_sscanf2 (str_inequations, "%t[%simplify_Az]", &ineqs);

      bas_Denef_Lipshitz_resume (&DL, &U, &eqns, &ineqs);
    }
  else
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);

  bmi_push_maple_gmp_allocators ();
  L = MapleListAlloc (callback->kv, 3);
  MapleGcProtect (callback->kv, L);
  L1 = MapleListAlloc (callback->kv, DL.size);
  MapleListAssign (callback->kv, L, 1, L1);
  L2 = MapleListAlloc (callback->kv, DL.size);
  MapleListAssign (callback->kv, L, 2, L2);
  L3 = MapleListAlloc (callback->kv, DL.size);
  MapleListAssign (callback->kv, L, 3, L3);

  for (i = 0; i < DL.size; i++)
    {
      bmi_pull_maple_gmp_allocators ();
      str_stripped_DLuple = ba0_new_printf ("%stripped_DLuple", DL.tab[i]);
      stripped_DLuple = bmi_balsa_new_string (str_stripped_DLuple);
      bmi_push_maple_gmp_allocators ();
      MapleListAssign (callback->kv, L1, i + 1, stripped_DLuple);
      bmi_pull_maple_gmp_allocators ();
      cell = bmi_rtable_regchain
          (callback->kv, &DL.tab[i]->C, __FILE__, __LINE__);
      cell = bmi_balsa_new_regchain (cell);
      bmi_push_maple_gmp_allocators ();
      MapleListAssign (callback->kv, L2, i + 1, cell);
      bmi_pull_maple_gmp_allocators ();
      cell = bmi_rtable_DLuple (callback->kv, DL.tab[i], __FILE__, __LINE__);
      cell = bmi_balsa_new_DLuple (cell);
      bmi_push_maple_gmp_allocators ();
      MapleListAssign (callback->kv, L3, i + 1, cell);
    }
  MapleGcAllow (callback->kv, L);
  bmi_pull_maple_gmp_allocators ();
  return L;
}
