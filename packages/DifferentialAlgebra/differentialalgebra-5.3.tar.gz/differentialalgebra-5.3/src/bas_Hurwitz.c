#include "bas_Hurwitz.h"

/*
 * texinfo: bas_Hurwitz_coeffs
 * Assign to @var{fn} the table @math{[f_n, f_{n+1}, \ldots, f_{n+k}]}
 * of the Hurwitz coefficients defined by
 * 
 * @display 
 * @math{P^{(2\,k+2)} = y^{(n+2\,k+2)}\,f_n + y^{(n+2\,k+1)}\,f_{n+1} + \cdots +  y^{(n+k+2)}\,f_{n+k} + f_{n+k+1}}
 * @end display
 *
 * where the leader of @var{P} is @math{y^{(n)}},
 * the @math{f_i} are polynomials in @math{y} of order at most @math{i}
 * and @math{f_n} is the separant of @var{P}. 
 * Differentiations are performed with respect to @var{x}.
 *
 * If nonzero, @var{P_2k_2} must contain @math{P^{(2\,k+2)}}.
 *
 * The formula is due to Hurwitz (1889).
 * It is used in [DL84, Lemma 2.2, page 215].
 */

BAS_DLL void
bas_Hurwitz_coeffs (
    struct bap_tableof_polynom_mpz *fn,
    struct bap_polynom_mpz *P,
    struct bap_polynom_mpz *P_2k_2,
    ba0_int_p k,
    struct bav_symbol *x)
{
  struct bap_polynom_mpz coeff;
  struct bav_term theta;
  struct bav_variable *u, *v, *w;
  struct ba0_mark M;
  ba0_int_p i;

  ba0_realloc2_table ((struct ba0_table *) fn, k + 1,
      (ba0_new_function *) & bap_new_polynom_mpz);

  bap_separant_polynom_mpz (fn->tab[0], P);
  fn->size = 1;

  ba0_push_another_stack ();
  ba0_record (&M);

  if (P_2k_2 == BAP_NOT_A_POLYNOM_mpz)
    {
      P_2k_2 = bap_new_polynom_mpz ();
      bap_diff_polynom_mpz (P_2k_2, P, x);
      for (i = 1; i < 2 * k + 2; i++)
        bap_diff_polynom_mpz (P_2k_2, P_2k_2, x);
    }
// u = y^{(n)}
  u = bap_leader_polynom_mpz (P);
  v = bav_symbol_to_variable (x);
// w = y^{(n + k + 2)}
  bav_init_term (&theta);
  bav_set_term_variable (&theta, v, k + 2);
  w = bav_diff2_variable (u, &theta);

  bap_init_polynom_mpz (&coeff);
  for (i = 1; i <= k; i++)
    {
// w = y^{(n + 2k + 2 - i)}
      bav_set_term_variable (&theta, v, 2 * k + 2 - i);
      w = bav_diff2_variable (u, &theta);
      ba0_pull_stack ();
// fn[i] = coeff (P_2k_2, w)
      bap_coeff_polynom_mpz (fn->tab[i], P_2k_2, w, 1);
      fn->size = i + 1;
      ba0_push_another_stack ();
    }

  ba0_pull_stack ();
  ba0_restore (&M);
}
