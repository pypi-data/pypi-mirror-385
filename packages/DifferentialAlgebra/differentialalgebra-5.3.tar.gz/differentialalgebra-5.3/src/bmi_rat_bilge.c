#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_rat_bilge.h"

#define DOPRINT
#undef DOPRINT

/*      
 * RatBilge (list(ratfrac), derivation, iterated, differential ring)
 */

ALGEB
bmi_rat_bilge (
    struct bmi_callback *callback)
{
  struct bad_regchain C;
  struct baz_tableof_ratfrac T;
  struct baz_tableof_ratfrac *P;
  struct ba0_table result;
  struct bav_variable *vx;
  struct bav_symbol *x;
  ba0_int_p i;
  char *derivation;
  char *ratfracs;
  bool iterated, numer_pwcc, denom_pwcc;

  if (bmi_nops (callback) != 4)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_table_op (4, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRDRNG);

  if (bmi_is_regchain_op (4, callback))
    bmi_set_ordering_and_regchain (&C, 4, callback, __FILE__, __LINE__);
  else
    bmi_set_ordering (4, callback, __FILE__, __LINE__);

  derivation = bmi_string_op (2, callback);
  ba0_sscanf2 (derivation, "%v", &vx);
  x = vx->root;

  iterated = bmi_bool_op (3, callback);
#if defined (DOPRINT)
  printf ("iterated = %d\n", iterated);
#endif
  ratfracs = bmi_string_op (1, callback);
  ba0_init_table ((struct ba0_table *) &T);
#if ! defined (BMI_BALSA)
  ba0_sscanf2 (ratfracs, "%t[%simplify_expanded_Qz]", &T);
#else
  ba0_sscanf2 (ratfracs, "%t[%simplify_Qz]", &T);
#endif

  ba0_init_table (&result);
  ba0_realloc_table (&result, T.size);
/*
 * P starts with the first whatsleft
 */
  for (i = 0; i < T.size; i++)
    {
      P = (struct baz_tableof_ratfrac *) ba0_new_table ();
      ba0_realloc2_table ((struct ba0_table *) P, 2,
          (ba0_new_function *) & baz_new_ratfrac);
      if (!iterated)
        {
          baz_rat_bilge_mpz (P->tab[1], P->tab[0], T.tab[i], x);
          P->size = 2;
/*
 * Not iterated: two rational fractions
 */
        }
      else
        {
          BA0_SWAP (struct baz_ratfrac *,
              P->tab[P->size],
              T.tab[i]);
          P->size = 1;
          numer_pwcc =
              bap_is_polynomial_with_constant_coefficients_mpz (&P->
              tab[P->size - 1]->numer, vx, x);
          denom_pwcc =
              bap_is_polynomial_with_constant_coefficients_mpz (&P->
              tab[P->size - 1]->denom, vx, x);
          while (!numer_pwcc || !denom_pwcc)
            {
              if (P->size >= P->alloc)
                ba0_realloc2_table ((struct ba0_table *) P, 2 * P->size + 1,
                    (ba0_new_function *) & baz_new_ratfrac);
              baz_rat_bilge_mpz
                  (P->tab[P->size], P->tab[P->size - 1],
                  P->tab[P->size - 1], x);
              P->size += 1;
              numer_pwcc =
                  bap_is_polynomial_with_constant_coefficients_mpz (&P->
                  tab[P->size - 1]->numer, vx, x);
              denom_pwcc =
                  bap_is_polynomial_with_constant_coefficients_mpz (&P->
                  tab[P->size - 1]->denom, vx, x);
            }
          if (baz_is_zero_ratfrac (P->tab[P->size - 1]))
            P->size -= 1;
/*
 * Iterated: a possibly empty list of rational fractions
 * Empty if T.tab [i] is zero. The last zero is removed.
 */
        }
      result.tab[i] = P;
      result.size = i + 1;
    }

  {
    ALGEB res;
    char *stres;

#if ! defined (BMI_BALSA)
    bav_set_settings_symbol (0, &bav_printf_numbered_symbol);
    stres = ba0_new_printf ("%t[%t[%Qz]]", &result);
    bmi_push_maple_gmp_allocators ();
    res = EvalMapleStatement (callback->kv, stres);
    bmi_pull_maple_gmp_allocators ();
#else
    stres = ba0_new_printf ("%t[%t[%Qz]]", &result);
    res = bmi_balsa_new_string (stres);
#endif
/*
 *      bmi_push_maple_gmp_allocators ();
 *      res = MapleListAlloc (callback->kv, (M_INT)T.size);
 *      bmi_pull_maple_gmp_allocators ();
 *      for (i = 0; i < T.size; i++)
 *      {   ALGEB res2;
 *          ba0_int_p j;
 *          P = (struct baz_tableof_ratfrac *)result.tab [i];
 *          bmi_push_maple_gmp_allocators (); 
 *          res2 = MapleListAlloc (callback->kv, (M_INT)result.size);
 *          bmi_pull_maple_gmp_allocators ();
 *          for (j = 0; j < P->size; j++)
 *          {	stres = ba0_new_printf ("%Qz", P->tab [j]);
 *              bmi_push_maple_gmp_allocators (); 
 *      	MapleListAssign (callback->kv, res2, (M_INT)j, 
 *      					bmi_balsa_new_string (stres));
 *              bmi_pull_maple_gmp_allocators ();
 *          }
 *          bmi_push_maple_gmp_allocators ();
 *          MapleListAssign (callback->kv, res, (M_INT)i+1, res2);
 *          bmi_pull_maple_gmp_allocators ();
 *      }
 */
    return res;

  }
}
