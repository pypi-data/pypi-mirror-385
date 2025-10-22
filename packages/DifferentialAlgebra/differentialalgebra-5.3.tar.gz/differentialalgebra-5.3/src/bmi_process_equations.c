#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_process_equations.h"

/*
 * EXPORTED
 * ProcessEquations (equations, differential ring)
 *
 * Private function, called from Sage only
 * 
 * The input equations may involve rational fractions and, even,
 * relational expressions between rational fractions. The function
 * returns a list [ eqns, ineq ], where eqns and ineq are lists 
 * of polynomials.
 */

ALGEB
bmi_process_equations (
    struct bmi_callback *callback)
{
  char *equations;
  struct baz_tableof_rel_ratfrac T;
  struct bap_tableof_polynom_mpz eqns, ineq;
  struct baz_ratfrac Q;
  ba0_int_p i;

  if (bmi_nops (callback) != 2)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_table_op (2, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRDRNG);

  bmi_set_ordering (2, callback, __FILE__, __LINE__);

  equations = bmi_string_op (1, callback);
/*
 * The equations and inequations
 */
  ba0_init_table ((struct ba0_table *) &eqns);
  ba0_init_table ((struct ba0_table *) &ineq);

  baz_init_ratfrac (&Q);

  ba0_init_table ((struct ba0_table *) &T);
  ba0_sscanf2 (equations, "%t[%relQz]", &T);
  for (i = 0; i < T.size; i++)
    {
      baz_set_ratfrac_rel_ratfrac (&Q, T.tab[i]);
      if (T.tab[i]->op == baz_none_relop || T.tab[i]->op == baz_equal_relop)
        {
          if (eqns.size >= eqns.alloc)
            ba0_realloc2_table ((struct ba0_table *) &eqns, 2 * eqns.size + 1,
                (ba0_new_function *) & bap_new_polynom_mpz);
          bap_set_polynom_mpz (eqns.tab[eqns.size], &Q.numer);
          eqns.size += 1;
        }
      else if (T.tab[i]->op == baz_not_equal_relop)
        {
          if (ineq.size >= ineq.alloc)
            ba0_realloc2_table ((struct ba0_table *) &ineq, 2 * ineq.size + 1,
                (ba0_new_function *) & bap_new_polynom_mpz);
          bap_set_polynom_mpz (ineq.tab[ineq.size], &Q.numer);
          ineq.size += 1;
        }
      else
        BA0_RAISE_EXCEPTION (BMI_ERRROP);

      if (!bap_is_numeric_polynom_mpz (&Q.denom))
        {
          if (ineq.size >= ineq.alloc)
            ba0_realloc2_table ((struct ba0_table *) &ineq, 2 * ineq.size + 1,
                (ba0_new_function *) & bap_new_polynom_mpz);
          bap_set_polynom_mpz (ineq.tab[ineq.size], &Q.denom);
          ineq.size += 1;
        }
    }
/*
 * The result
 */
  {
    ALGEB A, L;
    char *stres;

    bmi_push_maple_gmp_allocators ();
    L = MapleListAlloc (callback->kv, 2);
    MapleGcProtect (callback->kv, L);
    bmi_pull_maple_gmp_allocators ();

#if ! defined (BMI_BALSA)
    bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
#endif
    stres = ba0_new_printf ("%t[%Az]", &eqns);

    bmi_push_maple_gmp_allocators ();
#if ! defined (BMI_BALSA)
    A = EvalMapleStatement (callback->kv, stres);
#else
    A = bmi_balsa_new_string (stres);
#endif
    MapleListAssign (callback->kv, L, 1, A);
    bmi_pull_maple_gmp_allocators ();

    stres = ba0_new_printf ("%t[%Az]", &ineq);

    bmi_push_maple_gmp_allocators ();
#if ! defined (BMI_BALSA)
    A = EvalMapleStatement (callback->kv, stres);
#else
    A = bmi_balsa_new_string (stres);
#endif
    MapleListAssign (callback->kv, L, 2, A);
    bmi_pull_maple_gmp_allocators ();

    return L;
  }
}
