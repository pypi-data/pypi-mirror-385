#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_equations.h"

static void
bmi_printf_rewrite_rules_mpz (
    struct bap_tableof_polynom_mpz *T,
    char po,
    char pf)
{
  struct bav_rank rg;
  struct bap_polynom_mpz init, red;
  ba0_int_p i;

  bap_init_readonly_polynom_mpz (&init);
  bap_init_readonly_polynom_mpz (&red);
  ba0_put_char (po);
  for (i = 0; i < T->size; i++)
    {
      rg = bap_rank_polynom_mpz (T->tab[i]);
      bap_initial_and_reductum_polynom_mpz (&init, &red, T->tab[i]);
#if defined (BMI_SYMPY)
      ba0_printf ("Eq (%rank, - (%Az)/(%Az))", &rg, &red, &init);
#elif defined (BMI_SAGE)
      ba0_printf ("%rank == - (%Az)/(%Az)", &rg, &red, &init);
#else
      ba0_printf ("%rank = - (%Az)/(%Az)", &rg, &red, &init);
#endif
      if (i < T->size - 1)
        ba0_put_string (", ");
    }
  ba0_put_char (pf);
}

static void
bmi_printf_rewrite_rules_mpq (
    struct bap_tableof_polynom_mpq *T,
    char po,
    char pf)
{
  struct bav_rank rg;
  struct bap_polynom_mpq init, red;
  ba0_int_p i;

  bap_init_readonly_polynom_mpq (&init);
  bap_init_readonly_polynom_mpq (&red);
  ba0_put_char (po);
  for (i = 0; i < T->size; i++)
    {
      rg = bap_rank_polynom_mpq (T->tab[i]);
      bap_initial_and_reductum_polynom_mpq (&init, &red, T->tab[i]);
#if defined (BMI_SYMPY)
      ba0_printf ("Eq (%rank, - (%Aq)/(%Aq))", &rg, &red, &init);
#elif defined (BMI_SAGE)
      ba0_printf ("%rank == - (%Aq)/(%Aq)", &rg, &red, &init);
#else
      ba0_printf ("%rank = - (%Aq)/(%Aq)", &rg, &red, &init);
#endif
      if (i < T->size - 1)
        ba0_put_string (", ");
    }
  ba0_put_char (pf);
}

/*
 * EXPORTED
 * Equations (regchain, fullset)
 *
 * Returns the sequence of the list of equations for each regchain.
 * At least one regchain is mandatory.
 *
 * fullset = true | false
 * fullset is now ignored: the defining equations of parameters are implicit
 */

static ALGEB
bmi__equations (
    struct bmi_callback *callback,
    bool rw)
{
  struct bad_regchain C;
  char *stres;

  if (bmi_nops (callback) != 2)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_regchain_op (1, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRREGC);

  bmi_set_ordering_and_regchain (&C, 1, callback, __FILE__, __LINE__);

#if ! defined (BMI_BALSA)
  bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
#endif
  if (rw)
    {
      ba0_record_output ();
      ba0_set_output_counter ();
      bmi_printf_rewrite_rules_mpz (&C.decision_system, '[', ']');
      stres = ba0_persistent_malloc (ba0_output_counter () + 1);
      ba0_set_output_string (stres);
      bmi_printf_rewrite_rules_mpz (&C.decision_system, '[', ']');
      ba0_restore_output ();
    }
  else
    stres = ba0_new_printf ("%t[%Az]", &C.decision_system);

  {
    ALGEB res;
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


ALGEB
bmi_equations (
    struct bmi_callback *callback)
{
  return bmi__equations (callback, false);
}

ALGEB
bmi_rewrite_rules (
    struct bmi_callback *callback)
{
  return bmi__equations (callback, true);
}

/*
 * Subfunctions of EquationWithLeaderOrOrder
 */

static bool
bmi_test_leader_eq (
    struct bav_variable *v,
    bool numeric,
    struct bav_variable *u)
{
  return (!numeric) && u == v;
}

static bool
bmi_test_rank_eq (
    struct bav_rank *rg,
    struct bav_rank *rk)
{
  return bav_equal_rank (rk, rg);
}

static bool
bmi_test_order_eq (
    bav_Iorder o,
    bool indep,
    bav_Iorder p)
{
  return (!indep) && o == p;
}

static bool
bmi_test_leader_ne (
    struct bav_variable *v,
    bool numeric,
    struct bav_variable *u)
{
  return (!numeric) && u != v;
}

static bool
bmi_test_rank_ne (
    struct bav_rank *rg,
    struct bav_rank *rk)
{
  return !bav_equal_rank (rk, rg);
}

static bool
bmi_test_order_ne (
    bav_Iorder o,
    bool indep,
    bav_Iorder p)
{
  return (!indep) && o != p;
}

static bool
bmi_test_leader_gt (
    struct bav_variable *v,
    bool numeric,
    struct bav_variable *u)
{
  return (!numeric) && bav_variable_number (u) > bav_variable_number (v);
}

static bool
bmi_test_rank_gt (
    struct bav_rank *rg,
    struct bav_rank *rk)
{
  return bav_gt_rank (rk, rg);
}

static bool
bmi_test_order_gt (
    bav_Iorder o,
    bool indep,
    bav_Iorder p)
{
  return (!indep) && p > o;
}

static bool
bmi_test_leader_ge (
    struct bav_variable *v,
    bool numeric,
    struct bav_variable *u)
{
  return (!numeric) && bav_variable_number (u) >= bav_variable_number (v);
}

static bool
bmi_test_rank_ge (
    struct bav_rank *rg,
    struct bav_rank *rk)
{
  return bav_equal_rank (rk, rg) || bav_gt_rank (rk, rg);
}

static bool
bmi_test_order_ge (
    bav_Iorder o,
    bool indep,
    bav_Iorder p)
{
  return (!indep) && p >= o;
}

static bool
bmi_test_leader_lt (
    struct bav_variable *v,
    bool numeric,
    struct bav_variable *u)
{
  return (!numeric) && bav_variable_number (u) < bav_variable_number (v);
}

static bool
bmi_test_rank_lt (
    struct bav_rank *rg,
    struct bav_rank *rk)
{
  return bav_lt_rank (rk, rg);
}

static bool
bmi_test_order_lt (
    bav_Iorder o,
    bool indep,
    bav_Iorder p)
{
  return (!indep) && p < o;
}

static bool
bmi_test_leader_le (
    struct bav_variable *v,
    bool numeric,
    struct bav_variable *u)
{
  return (!numeric) && bav_variable_number (u) <= bav_variable_number (v);
}

static bool
bmi_test_rank_le (
    struct bav_rank *rg,
    struct bav_rank *rk)
{
  return bav_equal_rank (rk, rg) || bav_lt_rank (rk, rg);
}

static bool
bmi_test_order_le (
    bav_Iorder o,
    bool indep,
    bav_Iorder p)
{
  return (!indep) && p <= o;
}

static bool
bmi_test_leader_deriv_eq (
    struct bav_variable *v,
    bool numeric,
    struct bav_variable *u)
{
  return (!numeric) && u->root->type != bav_independent_symbol
      && bav_is_derivative (u, v);
}

static bool
bmi_test_leader_deriv_ne (
    struct bav_variable *v,
    bool numeric,
    struct bav_variable *u)
{
  return (!numeric) && (u->root->type == bav_independent_symbol
      || !bav_is_derivative (u, v));
}

static bool
bmi_test_leader_proper_eq (
    struct bav_variable *v,
    bool numeric,
    struct bav_variable *u)
{
  return (!numeric) && u->root->type != bav_independent_symbol
      && u != v && bav_is_derivative (u, v);
}

static bool
bmi_test_leader_proper_ne (
    struct bav_variable *v,
    bool numeric,
    struct bav_variable *u)
{
  return (!numeric) && (u->root->type == bav_independent_symbol
      || u == v || !bav_is_derivative (u, v));
}

/*
 * "order >= 3"
 * "derivative (u(x,y)) < leader"
 * etc.
 */

static void
bmi_parse_criterion (
    char **keyword,
    char **relop,
    char **modifier,
    char **derv,
    char *criterion)
{
  static char *rlp[] = { "==", "!=", "<=", "<", ">=", ">" };
  static char *ix_rlp[] =
      { BMI_IX_eq, BMI_IX_ne, BMI_IX_le, BMI_IX_lt, BMI_IX_ge,
    BMI_IX_gt
  };
  static char *ix_rev_rlp[] =
      { BMI_IX_eq, BMI_IX_ne, BMI_IX_ge, BMI_IX_gt, BMI_IX_le,
    BMI_IX_lt
  };
  static int nbop = sizeof (rlp) / sizeof (char *);
  static char *kwds[] = { BMI_IX_order, BMI_IX_rank, BMI_IX_leader };
  static int nbkwds = sizeof (kwds) / sizeof (char *);
  static char *mdfrs[] = { BMI_IX_deriv, BMI_IX_proper };
  static int nbmdfrs = sizeof (mdfrs) / sizeof (char *);
  char *left, *right, *p;
  int i, j, len;
  bool found;
/*
 * Look for i such that rlp [i] lies in criterion
 */
  p = (char *) 0;
  i = 0;
  while (i < nbop && p == (char *) 0)
    {
      p = strstr (criterion, rlp[i]);
      if (p == (char *) 0)
        i += 1;
    }
  if (p == (char *) 0)
    BA0_RAISE_EXCEPTION (BMI_ERRCRIT);
/*
 * store in left what is on the lhs of rlp [i]
 */
  len = p - criterion;
  left = (char *) ba0_alloc ((len + 1) * sizeof (char));
  strncpy (left, criterion, len);
  do
    {
      left[len] = '\0';
      len -= 1;
    }
  while (len >= 0 && isspace ((int) left[len]));
/*
 * store in right what is on the rhs of rlp [i]
 */
  right = (char *) ba0_alloc (strlen (criterion));
  p += strlen (rlp[i]);
  while (isspace (*p))
    p += 1;
  len = strlen (p);
  right = (char *) ba0_alloc ((len + 1) * sizeof (char));
  strncpy (right, p, len);
  do
    {
      right[len] = '\0';
      len -= 1;
    }
  while (len >= 0 && isspace ((int) right[len]));
/*
 * Compute keyword and relop
 */
  found = false;
  j = 0;
  while (j < nbkwds && !found)
    {
      if (strcmp (left, kwds[j]) == 0)
        found = true;
      else
        j += 1;
    }
  if (found)
    {
      *keyword = kwds[j];
      *relop = ix_rlp[i];
    }
  else
    {
      j = 0;
      while (j < nbkwds && !found)
        {
          if (strcmp (right, kwds[j]) == 0)
            found = true;
          else
            j += 1;
        }
      if (!found)
        BA0_RAISE_EXCEPTION (BMI_ERRCRIT);
      *keyword = kwds[j];
      *relop = ix_rev_rlp[i];
      BA0_SWAP (char *,
          left,
          right);
    }
/*
 * Compute modifier and derv in right
 */
  found = false;
  j = 0;
  while (j < nbmdfrs && !found)
    {
      if (strncmp (right, mdfrs[j], strlen (mdfrs[j])) == 0)
        found = true;
      else
        j += 1;
    }
  if (found)
    {
      *modifier = mdfrs[j];
      i = 0;
      while (right[i] != '\0' && right[i] != '(')
        i += 1;
      i += 1;
      while (isspace (right[i]))
        i += 1;
      j = strlen (right) - 1;
      while (j > i && right[j] != ')')
        j -= 1;
      if (right[j] != ')')
        BA0_RAISE_EXCEPTION (BMI_ERRCRIT);
      j -= 1;
      while (isspace (right[j]))
        j -= 1;
      right[j + 1] = '\0';
      *derv = right + i;
    }
  else
    {
      *modifier = BMI_IX_identical;
      *derv = right;
    }
/*
    printf ("%s|%s|%s|%s\n", *keyword, *relop, *modifier, *derv);
 */
}

/*
 * EXPORTED
 * This function is actually called through the Equations function
 * of the DifferentialAlgebra package.
 *
 * EquationsWithCriterion 
 * 	(list(polynomial) | regchain, 
 * 	 keyword, relop, modifier, derv, fullset, differential ring)
 *
 * Returns a subsequence of the list of equations
 *
 * fullset is now ignored: the defining equations of parameters are implicit
 */

static ALGEB
bmi__equations_with_criterion (
    struct bmi_callback *callback,
    bool rw)
{
  struct bad_regchain C;
  struct ba0_table *T;
  struct bav_rank rg;
  struct bav_variable *v;
  bav_Iorder o;
  char *eqns, *criterion, *keyword, *relop, *modifier, *derv;
  char *stres;
  bool (
      *fleader) (
      struct bav_variable *,
      bool,
      struct bav_variable *);
  bool (
      *forder) (
      bav_Iorder,
      bool,
      bav_Iorder);
  bool (
      *frank) (
      struct bav_rank *,
      struct bav_rank *);
  bool leader, rank, order, integer;
  ba0_int_p i, nops;

  fleader = 0;
  frank = 0;
  forder = 0;
  o = 0;                        /* to avoid a warning */

  nops = bmi_nops (callback);

  if (nops != 7 && nops != 4)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_table_op (nops, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRDRNG);

  if (bmi_is_regchain_op (1, callback))
    bmi_set_ordering_and_regchain (&C, 1, callback, __FILE__, __LINE__);
  else
    bmi_set_ordering (nops, callback, __FILE__, __LINE__);

  if (nops == 7)
    {
      keyword = bmi_string_op (2, callback);
      relop = bmi_string_op (3, callback);
      modifier = bmi_string_op (4, callback);
      derv = bmi_string_op (5, callback);
    }
  else
    {
      criterion = bmi_string_op (2, callback);
      bmi_parse_criterion (&keyword, &relop, &modifier, &derv, criterion);
    }

  if (bmi_is_regchain_op (1, callback))
    {
      integer = true;
      T = (struct ba0_table *) &C.decision_system;
    }
  else
    {
      eqns = bmi_string_op (1, callback);
      integer = false;
      T = ba0_new_table ();
#if ! defined (BMI_BALSA)
      ba0_sscanf2 (eqns, "%t[%simplify_expanded_Aq]", T);
#else
      ba0_sscanf2 (eqns, "%t[%simplify_Aq]", T);
#endif
    }

  leader = rank = order = false;
  if (strcmp (keyword, BMI_IX_leader) == 0)
    {
      leader = true;
      ba0_sscanf2 (derv, "%v", &v);
    }
  else if (strcmp (keyword, BMI_IX_order) == 0)
    {
      order = true;
      o = (bav_Iorder) atoi (derv);
    }
  else if (strcmp (keyword, BMI_IX_rank) == 0)
    {
      rank = true;
      ba0_sscanf2 (derv, "%rank", &rg);
    }
  else
    BA0_RAISE_EXCEPTION (BMI_ERRCRIT);

  if (strcmp (relop, BMI_IX_eq) == 0)
    {
      if (strcmp (modifier, BMI_IX_deriv) == 0)
        fleader = &bmi_test_leader_deriv_eq;
      else if (strcmp (modifier, BMI_IX_proper) == 0)
        fleader = &bmi_test_leader_proper_eq;
      else
        fleader = &bmi_test_leader_eq;
      frank = &bmi_test_rank_eq;
      forder = &bmi_test_order_eq;
    }
  else if (strcmp (relop, BMI_IX_ne) == 0)
    {
      if (strcmp (modifier, BMI_IX_deriv) == 0)
        fleader = &bmi_test_leader_deriv_ne;
      else if (strcmp (modifier, BMI_IX_proper) == 0)
        fleader = &bmi_test_leader_proper_ne;
      else
        fleader = &bmi_test_leader_ne;
      frank = &bmi_test_rank_ne;
      forder = &bmi_test_order_ne;
    }
  else if (strcmp (relop, BMI_IX_gt) == 0)
    {
      fleader = &bmi_test_leader_gt;
      frank = &bmi_test_rank_gt;
      forder = &bmi_test_order_gt;
    }
  else if (strcmp (relop, BMI_IX_ge) == 0)
    {
      fleader = &bmi_test_leader_ge;
      frank = &bmi_test_rank_ge;
      forder = &bmi_test_order_ge;
    }
  else if (strcmp (relop, BMI_IX_lt) == 0)
    {
      fleader = &bmi_test_leader_lt;
      frank = &bmi_test_rank_lt;
      forder = &bmi_test_order_lt;
    }
  else if (strcmp (relop, BMI_IX_le) == 0)
    {
      fleader = &bmi_test_leader_le;
      frank = &bmi_test_rank_le;
      forder = &bmi_test_order_le;
    }
  else
    BA0_RAISE_EXCEPTION (BMI_ERRCRIT);

  if (leader)
    {
      for (i = T->size - 1; i >= 0; i--)
        {
          struct bav_variable *u;
          bool b;

          b = integer ?
              bap_is_numeric_polynom_mpz ((struct bap_polynom_mpz *) T->tab[i])
              : bap_is_numeric_polynom_mpq ((struct bap_polynom_mpq *)
              T->tab[i]);
          u = b ? BAV_NOT_A_VARIABLE : integer ? bap_leader_polynom_mpz ((struct
                  bap_polynom_mpz *) T->tab[i]) :
              bap_leader_polynom_mpq ((struct bap_polynom_mpq *) T->tab[i]);
          if (!(*fleader) (v, b, u))
            ba0_delete_table (T, i);
        }
    }
  else if (order)
    {
      for (i = T->size - 1; i >= 0; i--)
        {
          bav_Iorder p;
          bool b;

          b = integer ?
              bap_is_independent_polynom_mpz
              ((struct bap_polynom_mpz *) T->tab[i]) :
              bap_is_independent_polynom_mpq ((struct bap_polynom_mpq *)
              T->tab[i]);
          p = b ? 0 : integer ?
              bap_total_order_polynom_mpz ((struct bap_polynom_mpz *)
              T->tab[i]) :
              bap_total_order_polynom_mpq ((struct bap_polynom_mpq *)
              T->tab[i]);
          if (!(*forder) (o, b, p))
            ba0_delete_table (T, i);
        }
    }
  else
    {
      for (i = T->size - 1; i >= 0; i--)
        {
          struct bav_rank rk;

          rk = integer ?
              bap_rank_polynom_mpz ((struct bap_polynom_mpz *) T->tab[i]) :
              bap_rank_polynom_mpq ((struct bap_polynom_mpq *) T->tab[i]);
          if (!(*frank) (&rg, &rk))
            ba0_delete_table (T, i);
        }
    }
#if ! defined (BMI_BALSA)
  bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
#endif
  if (T->size == 0)
    stres = ba0_strdup ("[]");
  else if (rw)
    {
      ba0_record_output ();
      ba0_set_output_counter ();
      if (integer)
        bmi_printf_rewrite_rules_mpz ((struct bap_tableof_polynom_mpz *) T, '[',
            ']');
      else
        bmi_printf_rewrite_rules_mpq ((struct bap_tableof_polynom_mpq *) T, '[',
            ']');
      stres = ba0_persistent_malloc (ba0_output_counter () + 1);
      ba0_set_output_string (stres);
      if (integer)
        bmi_printf_rewrite_rules_mpz ((struct bap_tableof_polynom_mpz *) T, '[',
            ']');
      else
        bmi_printf_rewrite_rules_mpq ((struct bap_tableof_polynom_mpq *) T, '[',
            ']');
      ba0_restore_output ();
    }
  else
    stres = ba0_new_printf (integer ? "%t[%Az]" : "%t[%Aq]", T);

  {
    ALGEB res;
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

ALGEB
bmi_equations_with_criterion (
    struct bmi_callback *callback)
{
  return bmi__equations_with_criterion (callback, false);
}

ALGEB
bmi_rewrite_rules_with_criterion (
    struct bmi_callback *callback)
{
  return bmi__equations_with_criterion (callback, true);
}
