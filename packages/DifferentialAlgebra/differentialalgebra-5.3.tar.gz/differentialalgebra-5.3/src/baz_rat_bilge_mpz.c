#include "baz_gcd_polynom_mpz.h"
#include "baz_polyspec_mpz.h"
#include "baz_ratfrac.h"
#include "baz_rat_bilge_mpz.h"

#define RATBILGE_CHECK_INVARIANT
#undef RATBILGE_CHECK_INVARIANT

/*
 * Computes R such that the separant of R wrt v is equal to P.
 * The denominator of R is supposed not to depend on v.
 */

static void
baz_int_ratfrac (
    struct baz_ratfrac *R,
    struct baz_ratfrac *P,
    struct bav_variable *v)
{
  struct bap_creator_mpq crea;
  struct bap_itermon_mpz iter;
  struct bap_polynom_mpq N;
  struct bap_polynom_mpz numer, denom;
  struct bav_term term;
  bav_Idegree d;
  struct ba0_mark M;
  ba0_mpq_t q;
  ba0_mpz_t z;

  ba0_push_another_stack ();
  ba0_record (&M);

  bap_init_polynom_mpq (&N);
  bap_init_polynom_mpz (&numer);
  bap_init_polynom_mpz (&denom);
  bav_init_term (&term);
  ba0_mpq_init (q);
  ba0_mpz_init (z);

  bav_mul_term_variable (&term, &P->numer.total_rank, v, 1);
  bap_begin_creator_mpq (&crea, &N, &term, bap_exact_total_rank,
      bap_nbmon_polynom_mpz (&P->numer));
  bap_begin_itermon_mpz (&iter, &P->numer);
  while (!bap_outof_itermon_mpz (&iter))
    {
      bap_term_itermon_mpz (&term, &iter);
      d = bav_degree_term (&term, v);
      bav_mul_term_variable (&term, &term, v, 1);
      ba0_mpq_set_z (q, *bap_coeff_itermon_mpz (&iter));
      ba0_mpz_mul_ui (ba0_mpq_denref (q), ba0_mpq_denref (q),
          (unsigned long) d + 1);
      bap_write_creator_mpq (&crea, &term, q);
      bap_next_itermon_mpz (&iter);
    }
  bap_close_creator_mpq (&crea);
  bap_numer_polynom_mpq (&numer, z, &N);
  bap_mul_polynom_numeric_mpz (&denom, &P->denom, z);
  ba0_pull_stack ();
  baz_set_ratfrac_fraction (R, &numer, &denom);
  ba0_restore (&M);
}

/*
 * Variant w.r.t. Algorithm 1 : the content is not returned separately
 * but as a factor of B.
 */

static void
baz_prepare_for_integration_mpz (
    struct bap_polynom_mpz *cont,
    struct bap_polynom_mpz *N,
    struct bap_polynom_mpz *B,
    struct baz_ratfrac *F,
    struct bav_variable *v)
{
  struct bap_tableof_polynom_mpz polys;
  struct bap_product_mpz A0, A1, C0, tmp;
  struct bap_polynom_mpz B0, D0, S, Q0, Q1;
  struct ba0_mark M;
  ba0_int_p i;

  if (bap_is_numeric_polynom_mpz (&F->denom))
    {
      bap_set_polynom_mpz (B, &F->denom);
      bap_set_polynom_mpz (N, &F->numer);
    }
  else
    {
      ba0_push_another_stack ();
      ba0_record (&M);

      ba0_init_table ((struct ba0_table *) &polys);
      ba0_realloc_table ((struct ba0_table *) &polys, 2);
      bap_init_product_mpz (&A0);
      bap_init_product_mpz (&A1);
      bap_init_product_mpz (&C0);
      bap_init_product_mpz (&tmp);
      bap_init_polynom_mpz (&B0);
      bap_init_polynom_mpz (&D0);
      bap_init_polynom_mpz (&S);
      bap_init_polynom_mpz (&Q0);
      bap_init_polynom_mpz (&Q1);
/*
 * F->denom = cont * Q0
 * Q0 = F1 * F2^2 * ... * Fn^n
 */
      ba0_pull_stack ();
      baz_content_polynom_mpz (cont, &F->denom, v);
      ba0_push_another_stack ();
      bap_exquo_polynom_mpz (&Q0, &F->denom, cont);
/*
 * A0 = gcd (Q0, Q0')
 *    = F2 * F3^2 * ... * Fn^(n-1)
 * B0 = Q0 / A0
 *    = F1 * F2 * F3 * ... * Fn
*/
      bap_separant2_polynom_mpz (&S, &Q0, v);
      polys.tab[0] = &Q0;
      polys.tab[1] = &S;
      polys.size = 2;
      baz_gcd_tableof_polynom_mpz (&A0, &polys, false);
      bap_exquo_polynom_product_mpz (&B0, &Q0, &A0);
/*
 *         C0 := gcd (A0, B0);           # C0 = F2 * F3 * ... * Fn
 *         D0 := normal (B0 / C0);       # D0 = F1
 *
 * is rewritten as:
 *
 * C0 = 1
 * D0 = B0
 * for (i = 0; i < A0.size; i++)
 *    tmp = gcd (A0.tab [i].factor, D0)
 *    C0 = C0 * tmp
 *    D0 = D0 / tmp
 */
      bap_set_polynom_mpz (&D0, &B0);
      polys.tab[0] = &D0;
      for (i = 0; i < A0.size; i++)
        {
          if (A0.tab[i].exponent > 0)
            {
/*
 * we do not care for the exponents since B0 is squarefree
 */
              polys.tab[1] = &A0.tab[i].factor;
              baz_gcd_tableof_polynom_mpz (&tmp, &polys, false);
              bap_mul_product_mpz (&C0, &C0, &tmp);
              bap_exquo_polynom_product_mpz (&D0, &D0, &tmp);
            }
        }
/*
 * A1 = gcd (A0, A0')
 *    = F3 * ... * Fn^(n-2)
 */
      bap_expand_product_mpz (&Q1, &A0);
      bap_separant2_polynom_mpz (&S, &Q1, v);
      polys.tab[0] = &Q1;
      polys.tab[1] = &S;
      polys.size = 2;
      baz_gcd_tableof_polynom_mpz (&A1, &polys, false);
/*
 * N = F->numer * D0 * A1
 * B = D0 * A0 
 */
      bap_mul_product_polynom_mpz (&A1, &A1, &D0, 1);
      bap_mul_product_polynom_mpz (&A1, &A1, &F->numer, 1);
      bap_mul_product_polynom_mpz (&A0, &A0, &D0, 1);
      ba0_pull_stack ();
      bap_expand_product_mpz (N, &A1);
      bap_expand_product_mpz (B, &A0);
      ba0_restore (&M);
    }
}

/*
 * Computes result and whatsleft such that
 * separant (result, v) + whatsleft = F0
 * whatsleft = 0 iff there exists result such that separant (result, v) = F0
 *
 * v is not necessary the leading derivative of F0 (case of a rational
 * fraction depending on constants and independent variables only).
 */

static void
baz_integrate_with_remainder_mpz (
    struct baz_ratfrac *result,
    struct baz_ratfrac *whatsleft,
    struct baz_ratfrac *F0,
    struct bav_variable *v)
{
  struct baz_ratfrac R, W, F, tmp_r;
  struct bap_polynom_mpz N, B, H, P, Q, Tail, cont;
  struct bav_term T;
  struct bav_variable *w;
  bav_Idegree dN, dB, dA;
  struct ba0_mark M;
  ba0_mpz_t z;
  bool v_is_ge_varmax = true;

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_mpz_init (z);
  bav_init_term (&T);

  bap_init_polynom_mpz (&cont);
  bap_init_polynom_mpz (&N);
  bap_init_polynom_mpz (&B);
  bap_init_readonly_polynom_mpz (&H);
  bap_init_readonly_polynom_mpz (&Tail);
  bap_init_polynom_mpz (&P);
  bap_init_polynom_mpz (&Q);

  baz_init_ratfrac (&R);
  baz_init_ratfrac (&W);
  baz_init_ratfrac (&F);
  baz_init_ratfrac (&tmp_r);

  baz_set_ratfrac (&F, F0);

  if (!baz_is_numeric_ratfrac (&F))
    {
      w = baz_leader_ratfrac (&F);
      if (bav_variable_number (v) < bav_variable_number (w))
        {
          v_is_ge_varmax = false;
          bap_init_polynom_mpz (&H);
          bap_init_polynom_mpz (&Tail);
        }
    }
/*
 * Invariant: F + separant (R, v) + W = F0
 */
  while (!baz_is_zero_ratfrac (&F))
    {
/*
 * Check the invariant
 */
#if defined (RATBILGE_CHECK_INVARIANT)
      baz_separant2_ratfrac (&tmp_r, &R, v);
      baz_add_ratfrac (&tmp_r, &tmp_r, &W);
      baz_add_ratfrac (&tmp_r, &tmp_r, &F);
      baz_sub_ratfrac (&tmp_r, &tmp_r, F0);
      if (!baz_is_zero_ratfrac (&tmp_r))
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
#endif
      baz_prepare_for_integration_mpz (&cont, &N, &B, &F, v);
/*
 * So that F = N / B^2
 */
      if (bap_degree_polynom_mpz (&B, v) == 0)
        {
/*
 * The case of a rational fraction whose denominator does not depend on v.
 * In particular, the case of polynomials.
 *
 * R += int (F, v)
 * W is unchanged
 * 
 * In particular, if the denominator of the input fraction F0 does
 * not depend on v, whatsleft is zero.
 */
          baz_int_ratfrac (&tmp_r, &F, v);
          baz_add_ratfrac (&R, &R, &tmp_r);
          baz_reduce_ratfrac (&R, &R);
          baz_set_ratfrac_zero (&F);
        }
      else
        {
/*
 * We look for A such that (A/B)' = N/B^2.
 * Thus    N = A'*B - A*B'.
 * Denote  A = cA*v^dA + qA and B = cB*v^dB + qB.
 * Then    N = (dA - dB)*cA*cB*v^(dA + dB - 1) + something smaller
 * Thus   dA = dN - dB + 1
 */
          dB = bap_degree_polynom_mpz (&B, v);
          dN = bap_degree_polynom_mpz (&N, v);
          dA = dN - dB + 1;
          if (dN == 2 * dB - 1 || dA < 0)
            {
/*
 * First observe that dN <> 2*dB - 1.
 * With other words, if dN = 2*dB - 1 or dA < 0, the fraction cannot
 * be integrated.
 *
 * H = cN*v^dN
 * W = W + H / B^2
 * F = (N - H) / B^2 
 *   = F - H / B^2
 */
              if (v_is_ge_varmax)
                {
                  bav_set_term_variable (&T, v, dN);
                  bap_split_polynom_mpz (&H, &Tail, &N, &T);
                }
              else
                {
                  bap_lcoeff_and_reductum_polynom_mpz (&H, &Tail, &N, v);
                  bap_mul_polynom_variable_mpz (&H, &H, v, dN);
                }
              bap_pow_polynom_mpz (&P, &B, 2);
              bap_mul_polynom_mpz (&P, &P, &cont);
              baz_set_ratfrac_fraction (&tmp_r, &H, &P);
              baz_add_ratfrac (&W, &W, &tmp_r);
              baz_reduce_ratfrac (&W, &W);
              baz_set_ratfrac_fraction (&F, &Tail, &P);
              baz_reduce_ratfrac (&F, &F);
            }
          else
            {
/*
 * P     = cB * (dA - dB) * B
 * Q     = cN*v^dA
 * tmp_r = Q / P
 */
              if (v_is_ge_varmax)
                bap_initial2_polynom_mpz (&H, &B, v);
              else
                bap_lcoeff_polynom_mpz (&H, &B, v);
              ba0_mpz_set_si (z, (long) (dA - dB));
              bap_mul_polynom_numeric_mpz (&P, &H, z);
              bap_mul_polynom_mpz (&P, &P, &cont);
              bap_mul_polynom_mpz (&P, &P, &B);

              if (v_is_ge_varmax)
                bap_initial2_polynom_mpz (&H, &N, v);
              else
                bap_lcoeff_polynom_mpz (&H, &N, v);
              bap_mul_polynom_variable_mpz (&Q, &H, v, dA);
              baz_set_ratfrac_fraction (&tmp_r, &Q, &P);
              baz_reduce_ratfrac (&tmp_r, &tmp_r);
/*
 * R = R + tmp_r
 * F = F - diff (tmp_r, v)
 */
              baz_add_ratfrac (&R, &R, &tmp_r);
              baz_reduce_ratfrac (&R, &R);
              baz_separant2_ratfrac (&tmp_r, &tmp_r, v);
              baz_sub_ratfrac (&F, &F, &tmp_r);
              baz_reduce_ratfrac (&F, &F);
            }
        }
    }
/*
 * Check the invariant
 */
#if defined (RATBILGE_CHECK_INVARIANT)
  baz_separant2_ratfrac (&tmp_r, &R, v);
  baz_add_ratfrac (&tmp_r, &tmp_r, &W);
  baz_add_ratfrac (&tmp_r, &tmp_r, &F);
  baz_sub_ratfrac (&tmp_r, &tmp_r, F0);
  if (!baz_is_zero_ratfrac (&tmp_r))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
#endif
  ba0_pull_stack ();
  baz_set_ratfrac (result, &R);
  baz_set_ratfrac (whatsleft, &W);
  ba0_restore (&M);
}

/*
 * Returns the smallest variable w, present in A, such that w > v.
 * If such a w does not exist, return BAV_NOT_A_VARIABLE
 */

static struct bav_variable *
baz_smallest_greater_variable (
    struct bap_polynom_mpz *A,
    struct bav_variable *v)
{
  struct bav_variable *w, *z;
  bav_Inumber numv, numw, numz;
  ba0_int_p i;

  numv = bav_variable_number (v);
  w = BAV_NOT_A_VARIABLE;
  numw = -1;                    /* to avoid a warning */
  for (i = 0; i < A->total_rank.size; i++)
    {
      z = A->total_rank.rg[i].var;
      numz = bav_variable_number (z);
      if (numz > numv && (w == BAV_NOT_A_VARIABLE || numw > numz))
        {
          w = z;
          numw = numz;
        }
    }
  return w;
}

/*
 * Computes result and whatsleft such that
 * diff (result, x) + whatsleft = F
 * If F is a total derivative then whatsleft is zero
 */

/*
 * texinfo: baz_rat_bilge_mpz
 * Compute two rational differential fractions @var{R} and @var{W} such that
 * the derivative of @var{R} w.r.t. @var{x} plus @var{W} is equal to @var{F}.
 * If @var{F} is the derivative of some rational differential fraction, then
 * @var{W} is zero. This algorithm is mostly due to Fran@,{c}ois Lemaire.
 */

BAZ_DLL void
baz_rat_bilge_mpz (
    struct baz_ratfrac *result,
    struct baz_ratfrac *whatsleft,
    struct baz_ratfrac *F0,
    struct bav_symbol *x)
{
  struct baz_ratfrac F, R, W, R2, W2, F2;
  struct bap_polynom_mpz H, P;
  struct bav_term T;
  struct bav_variable *vN, *vB, *v, *w, *vx;
  struct ba0_mark M;
  bool numer_pwcc, denom_pwcc;

  ba0_push_another_stack ();
  ba0_record (&M);

  baz_init_ratfrac (&F);
  baz_init_ratfrac (&R);
  baz_init_ratfrac (&W);
  baz_init_ratfrac (&R2);
  baz_init_ratfrac (&W2);
  baz_init_ratfrac (&F2);

  bap_init_readonly_polynom_mpz (&H);
  bap_init_readonly_polynom_mpz (&P);

  bav_init_term (&T);

  baz_reduce_ratfrac (&F, F0);
/*
 * Invariant: F + differentiate (R, x) + W = F0
 */
  while (!baz_is_zero_ratfrac (&F))
    {
/*
 * Check the invariant
 */
#if defined (RATBILGE_CHECK_INVARIANT)
      baz_diff_ratfrac (&W2, &R, x);
      baz_add_ratfrac (&W2, &W2, &W);
      baz_add_ratfrac (&W2, &W2, &F);
      baz_sub_ratfrac (&W2, &W2, F0);
      if (!baz_is_zero_ratfrac (&W2))
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
#endif
      vx = bav_symbol_to_variable (x);
      numer_pwcc =
          bap_is_polynomial_with_constant_coefficients_mpz (&F.numer, vx, x);
      denom_pwcc =
          bap_is_polynomial_with_constant_coefficients_mpz (&F.denom, vx, x);

      if (numer_pwcc && denom_pwcc)
        {
/*
 * Case of a fraction which depend only on independent variables and constants
 * Just integrate.
 */
          baz_integrate_with_remainder_mpz (&R2, &W2, &F,
              bav_symbol_to_variable (x));
          baz_add_ratfrac (&R, &R, &R2);
          baz_reduce_ratfrac (&R, &R);
          baz_add_ratfrac (&W, &W, &W2);
          baz_reduce_ratfrac (&W, &W);
          baz_set_ratfrac_zero (&F);
        }
      else if (numer_pwcc)
        {
/*
 * Case of a numerator which depend only on independent variables and constants
 * The fraction is not integrable.
 */
          baz_add_ratfrac (&W, &W, &F);
          baz_reduce_ratfrac (&W, &W);
          baz_set_ratfrac_zero (&F);
        }
      else
        {
/*
 * Case of a numerator which is a true differential polynomial
 */
          vN = bap_leader_polynom_mpz (&F.numer);
          if (!denom_pwcc)
            vB = bap_leader_polynom_mpz (&F.denom);
          if (!denom_pwcc
              && bav_variable_number (vN) <= bav_variable_number (vB))
            {
/*
 * The denominator depends on higher derivatives than vN.
 * The fraction is not integrable.
 */
              baz_add_ratfrac (&W, &W, &F);
              baz_reduce_ratfrac (&W, &W);
              baz_set_ratfrac_zero (&F);
            }
          else if (bav_order_variable (vN, x) == 0)
            {
/*
 * We put in W the terms which depend on vN
 */
              bav_set_term_variable (&T, vN, 1);
              bap_split_polynom_mpz (&H, &P, &F.numer, &T);
              baz_set_ratfrac_fraction (&W2, &H, &F.denom);
              baz_add_ratfrac (&W, &W, &W2);
              baz_reduce_ratfrac (&W, &W);
              bap_set_polynom_mpz (&F.numer, &P);
              baz_reduce_ratfrac (&F, &F);
            }
          else if (bap_leading_degree_polynom_mpz (&F.numer) > 1)
            {
/*
 * We put in W the terms in vN^i, for i >= 2 
 */
              bav_set_term_variable (&T, vN, 2);
              bap_split_polynom_mpz (&H, &P, &F.numer, &T);
              baz_set_ratfrac_fraction (&W2, &H, &F.denom);
              baz_add_ratfrac (&W, &W, &W2);
              baz_reduce_ratfrac (&W, &W);
              bap_set_polynom_mpz (&F.numer, &P);
              baz_reduce_ratfrac (&F, &F);
            }
          else
            {
/*
 * v is such that diff (v, x) = vN
 */
              v = bav_int_variable (vN, x);
/*
 * H  = coeff (F.numer, vN, 1) = initial (F.numer)
 * F2 = H / F.denom
 */
              bap_initial2_polynom_mpz (&H, &F.numer, vN);
              baz_set_ratfrac_fraction (&F2, &H, &F.denom);
              baz_reduce_ratfrac (&F2, &F2);
/*
 * w is the smallest variable > v which occurs in the numerator of F2 
 *   is BAV_NOT_A_VARIABLE if no such variable exists.
 */
              w = baz_smallest_greater_variable (&F2.numer, v);
              if (w != BAV_NOT_A_VARIABLE)
                {
/*
 * Split the numerator of F2 as H + P where all monomials of H depend
 * on variables >= w and all monomials of H depend on variables < w.
 * W2 = vN * H / denom (F2)
 * W = W + W2
 * F = F - W2
 */
                  bav_set_term_variable (&T, w, 1);
                  bap_split_polynom_mpz (&H, &P, &F2.numer, &T);
                  baz_set_ratfrac_fraction (&W2, &H, &F2.denom);
                  baz_mul_ratfrac_variable (&W2, &W2, vN, 1);
                  baz_add_ratfrac (&W, &W, &W2);
                  baz_reduce_ratfrac (&W, &W);
                  baz_sub_ratfrac (&F, &F, &W2);
                  baz_reduce_ratfrac (&F, &F);
                }
              else
                {
                  w = baz_smallest_greater_variable (&F2.denom, v);
                  if (w != BAV_NOT_A_VARIABLE)
                    {
/*
 * The denominator depends on derivatives w such than d/dx v > vN.
 * The fraction is not integrable .
 */
                      baz_add_ratfrac (&W, &W, &F);
                      baz_reduce_ratfrac (&W, &W);
                      baz_set_ratfrac_zero (&F);
                    }
                  else
                    {
                      baz_integrate_with_remainder_mpz (&R2, &W2, &F2, v);
                      if (!baz_is_zero_ratfrac (&W2))
                        {
/*
 * W2 = W2 * vN
 * F = F - W2
 * W = W + W2
 */
                          baz_mul_ratfrac_variable (&W2, &W2, vN, 1);
                          baz_sub_ratfrac (&F, &F, &W2);
                          baz_reduce_ratfrac (&F, &F);
                          baz_add_ratfrac (&W, &W, &W2);
                          baz_reduce_ratfrac (&W, &W);
                        }
                      if (!baz_is_zero_ratfrac (&R2))
                        {
/*
 * R = R + R2
 * F = F - diff (R2, x)
 */
                          baz_add_ratfrac (&R, &R, &R2);
                          baz_reduce_ratfrac (&R, &R);
                          baz_diff_ratfrac (&R2, &R2, x);
                          baz_sub_ratfrac (&F, &F, &R2);
                          baz_reduce_ratfrac (&F, &F);
                        }
                    }
                }
            }
        }
    }
/*
 * Check the invariant
 */
#if defined (RATBILGE_CHECK_INVARIANT)
  baz_diff_ratfrac (&W2, &R, x);
  baz_add_ratfrac (&W2, &W2, &W);
  baz_add_ratfrac (&W2, &W2, &F);
  baz_sub_ratfrac (&W2, &W2, F0);
  if (!baz_is_zero_ratfrac (&W2))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
#endif
  ba0_pull_stack ();
  baz_set_ratfrac (result, &R);
  baz_set_ratfrac (whatsleft, &W);
  ba0_restore (&M);
}
