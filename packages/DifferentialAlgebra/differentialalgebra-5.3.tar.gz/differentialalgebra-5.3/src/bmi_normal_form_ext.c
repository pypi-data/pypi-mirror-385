#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_normal_form_ext.h"

/*
 * EXPORTED
 * NormalFormHandlingExceptions (ratfrac, regchain)
 */

ALGEB
bmi_normal_form_handling_exceptions (
    struct bmi_callback *callback)
{
  struct bad_intersectof_regchain tabC, tabNUL;
  struct baz_tableof_ratfrac tabNF;
  struct baz_ratfrac A;

  if (bmi_nops (callback) != 2)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_regchain_op (2, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRREGC);
/*
 * Initialize tabC as an intersection of one regchain
 */
  bmi_set_ordering_and_intersectof_regchain
      (&tabC, 2, callback, __FILE__, __LINE__);
/*
 * The rational fraction whose NF we are looking for
 */
  baz_init_ratfrac (&A);
#if ! defined (BMI_BALSA)
  ba0_sscanf2 (bmi_string_op (1, callback), "%simplify_expanded_Qz", &A);
#else
  ba0_sscanf2 (bmi_string_op (1, callback), "%simplify_Qz", &A);
#endif
/*
 * Compute the NF
 */
  bad_init_intersectof_regchain (&tabNUL);
  ba0_init_table ((struct ba0_table *) &tabNF);
  bad_normal_form_handling_exceptions_ratfrac_mod_regchain
      (&tabNF, &tabC, &tabNUL, &A);
  {
    ALGEB L, L1, L2, P, poly, cell;
    ba0_int_p i;
    char *stres;

    bmi_push_maple_gmp_allocators ();

    L = MapleListAlloc (callback->kv, 2);
    MapleGcProtect (callback->kv, L);
    L1 = MapleListAlloc (callback->kv, tabNF.size);
    MapleListAssign (callback->kv, L, 1, L1);
    L2 = MapleListAlloc (callback->kv, tabNUL.inter.size);
    MapleListAssign (callback->kv, L, 2, L2);

#if ! defined (BMI_BALSA)
    bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
#endif
    for (i = 0; i < tabNF.size; i++)
      {
        P = MapleListAlloc (callback->kv, 2);
        MapleListAssign (callback->kv, L1, i + 1, P);

        bmi_pull_maple_gmp_allocators ();
        stres = ba0_new_printf ("%Qz", tabNF.tab[i]);
#if ! defined (BMI_BALSA)
        bmi_push_maple_gmp_allocators ();
        poly = EvalMapleStatement (callback->kv, stres);
        bmi_pull_maple_gmp_allocators ();
#else
        poly = bmi_balsa_new_string (stres);
#endif
        bmi_push_maple_gmp_allocators ();
        MapleListAssign (callback->kv, P, 1, poly);
        bmi_pull_maple_gmp_allocators ();

        cell = bmi_rtable_regchain
            (callback->kv, tabC.inter.tab[i], __FILE__, __LINE__);
#if defined (BMI_BALSA)
/*
 * In BALSA, one computes the whole table, not the mere rtable
 */
        cell = bmi_balsa_new_regchain (cell);
#endif
        bmi_push_maple_gmp_allocators ();

        MapleListAssign (callback->kv, P, 2, cell);
      }
    for (i = 0; i < tabNUL.inter.size; i++)
      {
        bmi_pull_maple_gmp_allocators ();
        cell = bmi_rtable_regchain
            (callback->kv, tabNUL.inter.tab[i], __FILE__, __LINE__);
#if defined (BMI_BALSA)
/*
 * In BALSA, one computes the whole table, not the mere rtable
 */
        cell = bmi_balsa_new_regchain (cell);
#endif
        bmi_push_maple_gmp_allocators ();

        MapleListAssign (callback->kv, L2, i + 1, cell);
      }
    MapleGcAllow (callback->kv, L);

    bmi_pull_maple_gmp_allocators ();

    return L;
  }
}
