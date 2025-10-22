#include "bap_polynom_mpz.h"
#include "bap_geobucket_mpz.h"
#include "bap_creator_mpz.h"
#include "bap_itermon_mpz.h"
#include "bap_polyspec_mpz.h"
#include "bap_add_polynom_mpz.h"
#include "bap_mul_polynom_mpz.h"
#include "bap_polyspec_mpq.h"

/* 
 * Sets A to the numerator of B
 */

/*
 * texinfo: bap_polynom_mpq_to_mpz
 * Assign the numerator of @var{B} to @var{A}.
 */

BAP_DLL void
bap_polynom_mpq_to_mpz (
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpq *B)
{
  ba0_mpz_t denom;

  ba0_mpz_init (denom);
  bap_numer_polynom_mpq (A, denom, B);
}

/* 
 * Denote val = (x = \alpha).  
 * Assigns to R the coefficient of (x - \alpha)^k in the Taylor expansion
 * of A in x = \alpha.
 */

/*
 * Sets A to +/-B so that the leading coefficient of A is positive.
 */

/*
 * texinfo: bap_normal_sign_polynom_mpz
 * Assign to @var{\pm B} so that the leading coefficient of @var{A} is positive.
 */

BAP_DLL void
bap_normal_sign_polynom_mpz (
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *B)
{
  struct bap_itermon_mpz iter;
  ba0_mpz_t *lc;

  bap_begin_itermon_mpz (&iter, B);
  lc = bap_coeff_itermon_mpz (&iter);
  if (ba0_mpz_sgn (*lc) < 0)
    bap_neg_polynom_mpz (A, B);
  else if (A != B)
    bap_set_polynom_mpz (A, B);
}

/* 
 * Sets n to the maximum of the absolute values of the coefficients of A.
 */

/*
 * texinfo: bap_maxnorm_polynom_mpz
 * Assign to @var{n} the  maximum of the absolute values of the coefficients of
 * @var{A}.
 */

BAP_DLL void
bap_maxnorm_polynom_mpz (
    ba0_mpz_t n,
    struct bap_polynom_mpz *A)
{
  struct bap_itermon_mpz iter;

  if (bap_is_zero_polynom_mpz (A))
    BA0_RAISE_EXCEPTION (BAP_ERRNUL);

  bap_begin_itermon_mpz (&iter, A);
  ba0_mpz_abs (n, *bap_coeff_itermon_mpz (&iter));
  bap_next_itermon_mpz (&iter);
  while (!bap_outof_itermon_mpz (&iter))
    {
      ba0_mpz_t *c = bap_coeff_itermon_mpz (&iter);
      if (ba0_mpz_cmpabs (*c, n) > 0)
        ba0_mpz_abs (n, *c);
      bap_next_itermon_mpz (&iter);
    }
}

/* 
 * Sets n to the numerical content of A.
 */

/*
 * texinfo: bap_numeric_content_polynom_mpz
 * Assign to @var{n} the numerical content of @var{A}.
 */

BAP_DLL void
bap_numeric_content_polynom_mpz (
    ba0_mpz_t n,
    struct bap_polynom_mpz *A)
{
  struct bap_itermon_mpz iter;

  if (bap_is_zero_polynom_mpz (A))
    BA0_RAISE_EXCEPTION (BAP_ERRNUL);

  bap_begin_itermon_mpz (&iter, A);
  ba0_mpz_abs (n, *bap_coeff_itermon_mpz (&iter));
  bap_next_itermon_mpz (&iter);
  while (ba0_mpz_cmp_si (n, 1) != 0 && !bap_outof_itermon_mpz (&iter))
    {
      ba0_mpz_t *c = bap_coeff_itermon_mpz (&iter);
      ba0_mpz_gcd (n, n, *c);
      bap_next_itermon_mpz (&iter);
    }
}

/* 
 * Variant of the above function.  
 * The content n carries the same sign as the leading coefficient of A.
 */

/*
 * texinfo: bap_signed_numeric_content_polynom_mpz
 * Assign to @var{n} the numerical content of @var{A}.
 * The content carries the same sign as the leading coefficient of @var{A}.
 */

BAP_DLL void
bap_signed_numeric_content_polynom_mpz (
    ba0_mpz_t n,
    struct bap_polynom_mpz *A)
{
  struct bap_itermon_mpz iter;
  ba0_mpz_t *c;
  bool lc_negatif;

  if (bap_is_zero_polynom_mpz (A))
    BA0_RAISE_EXCEPTION (BAP_ERRNUL);

  bap_begin_itermon_mpz (&iter, A);
  c = bap_coeff_itermon_mpz (&iter);
  ba0_mpz_abs (n, *c);
  lc_negatif = ba0_mpz_sgn (*c) < 0;
  bap_next_itermon_mpz (&iter);
  while (ba0_mpz_cmp_si (n, 1) != 0 && !bap_outof_itermon_mpz (&iter))
    {
      c = bap_coeff_itermon_mpz (&iter);
      ba0_mpz_gcd (n, n, *c);
      bap_next_itermon_mpz (&iter);
    }
  if (lc_negatif)
    ba0_mpz_neg (n, n);
}

/* 
 * Sets A to the numerical primitive part of B.
 */

/*
 * texinfo: bap_numeric_primpart_polynom_mpz
 * Assign to @var{A} the numerical primitive part of @var{B}.
 */

BAP_DLL void
bap_numeric_primpart_polynom_mpz (
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *B)
{
  ba0_mpz_t cont;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mpz_init (cont);
  bap_numeric_content_polynom_mpz (cont, B);
  ba0_pull_stack ();
  bap_exquo_polynom_numeric_mpz (A, B, cont);
  ba0_restore (&M);
}

/* 
 * Variant of the above function. 
 * The leading coefficient of A is positive.
 */

/*
 * texinfo: bap_normal_numeric_primpart_polynom_mpz
 * Assign to @var{A} the numerical primitive part of @var{B}.
 * The leading coefficient of @var{A} is positive.
 */

BAP_DLL void
bap_normal_numeric_primpart_polynom_mpz (
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *B)
{
  ba0_mpz_t cont;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mpz_init (cont);
  bap_signed_numeric_content_polynom_mpz (cont, B);
  ba0_pull_stack ();
  bap_exquo_polynom_numeric_mpz (A, B, cont);
  ba0_restore (&M);
}

/*
 * texinfo: bap_exquo_polynom_numeric_mpz
 * Assign to @var{R} the polynomial @math{A / n}.
 * The division is assumed to be exact.
 * May raise exception @code{BAV_EXEXQO}.
 */

BAP_DLL void
bap_exquo_polynom_numeric_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A,
    ba0_mpz_t n)
{
  if (!bap_is_numeric_factor_polynom_mpz (A, n, R))
    BA0_RAISE_EXCEPTION (BAV_EXEXQO);
}

/* 
 * Returns true if n | A.  
 * If so and R is nonzero then R = A/n.
 */

/*
 * texinfo: bap_is_numeric_factor_polynom_mpz
 * Return @code{true} if @var{n} divides @var{A}.
 * If so and @var{R} is not the zero pointer then it is assigned @math{A/n}.
 */

BAP_DLL bool
bap_is_numeric_factor_polynom_mpz (
    struct bap_polynom_mpz *A,
    ba0_mpz_t n,
    struct bap_polynom_mpz *R)
{
  struct bap_itermon_mpz iter;
  struct bap_creator_mpz crea;
  struct bap_polynom_mpz *P = (struct bap_polynom_mpz *) 0;
  struct bav_term T;
  ba0_mpz_t q, r, *lc;
  bool divisible;
  struct ba0_mark M;

  if (ba0_mpz_cmp_si (n, 1) == 0)
    {
      if (R != BAP_NOT_A_POLYNOM_mpz && R != A)
        bap_set_polynom_mpz (R, A);
      return true;
    }

  if (ba0_mpz_cmp_si (n, -1) == 0)
    {
      if (R != BAP_NOT_A_POLYNOM_mpz)
        bap_neg_polynom_mpz (R, A);
      return true;
    }

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_mpz_init (q);
  ba0_mpz_init (r);
  bav_init_term (&T);
  bav_set_term (&T, &A->total_rank);

  if (R != BAP_NOT_A_POLYNOM_mpz)
    {
      P = bap_new_polynom_mpz ();
      bap_begin_creator_mpz (&crea, P, &T, bap_exact_total_rank,
          bap_nbmon_polynom_mpz (A));
    }

  bap_begin_itermon_mpz (&iter, A);
  divisible = true;
  while (divisible && !bap_outof_itermon_mpz (&iter))
    {
      bap_term_itermon_mpz (&T, &iter);
      lc = bap_coeff_itermon_mpz (&iter);
      ba0_mpz_tdiv_qr (q, r, *lc, n);
      if (ba0_mpz_sgn (r) != 0)
        divisible = false;
      else
        {
          if (R != BAP_NOT_A_POLYNOM_mpz)
            bap_write_creator_mpz (&crea, &T, q);
          bap_next_itermon_mpz (&iter);
        }
    }
  if (divisible && R != BAP_NOT_A_POLYNOM_mpz)
    {
      bap_close_creator_mpz (&crea);
      ba0_pull_stack ();
      bap_set_polynom_mpz (R, P);
    }
  ba0_restore (&M);
  return divisible;
}

/*
 * texinfo: bap_replace_initial2_polynom_mpz
 * Assign to @var{R} the polynomial obtained by replacing the
 * initial of @math{U\,A} by @var{G}.
 * This function is used for normalizing regular chain polynomials.
 * In this context, @var{U} is the algebraic inverse of the
 * initial of @var{A}.
 * Exception @code{BAP_ERRCST} is raised if @var{A} is numeric.
 * Exception @code{BA0_ERRALG} is raised if @var{R} is readonly.
 */

BAP_DLL void
bap_replace_initial2_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_product_mpz *U,
    struct bap_product_mpz *G,
    struct bap_polynom_mpz *A)
{
  struct bap_polynom_mpz init, tail, red;
  struct bav_term T;
  struct bav_rank rg;
  struct ba0_mark M;

  if (bap_is_numeric_polynom_mpz (A))
    BA0_RAISE_EXCEPTION (BAP_ERRCST);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);

  rg = bap_rank_polynom_mpz (A);

  bav_init_term (&T);
  bav_set_term_rank (&T, &rg);

  bap_init_polynom_mpz (&init);
  bap_expand_product_mpz (&init, G);
  bap_mul_polynom_term_mpz (&init, &init, &T);

  bap_init_readonly_polynom_mpz (&red);
  bap_reductum_polynom_mpz (&red, A);
  bap_init_polynom_mpz (&tail);
  bap_expand_product_mpz (&tail, U);
  bap_mul_polynom_mpz (&tail, &tail, &red);

  ba0_pull_stack ();
  bap_add_polynom_mpz (R, &init, &tail);
  ba0_restore (&M);
}

/*
 * texinfo: bap_separant_and_sepuctum_polynom_mpz
 * Assign to @var{S} the separant of @var{A}.
 * Assign to @var{R} the polynomial @math{d\,A - v\,S} where
 * @math{v^d} denotes the rank of @var{A}.
 * The argument @var{S} is allowed to be zero.
 * Exception @code{BAP_ERRCST} is raised if @var{A} is numeric.
 * Exception @code{BA0_ERRALG} is raised if @var{S} or @var{R} is readonly.
 */

BAP_DLL void
bap_separant_and_sepuctum_polynom_mpz (
    struct bap_polynom_mpz *S,
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A)
{
  struct bap_polynom_mpz *sep, red, red_sep, tmp;
  struct bav_term T;
  struct bav_rank rg;
  struct ba0_mark M;

  if (bap_is_numeric_polynom_mpz (A))
    BA0_RAISE_EXCEPTION (BAP_ERRCST);
  if (S && S->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);

  bap_init_readonly_polynom_mpz (&red);
  bap_reductum_polynom_mpz (&red, A);

  rg = bap_rank_polynom_mpz (A);

  if (rg.deg == 1)
    {
      struct bap_polynom_mpz init;
      if (S)
        {
          bap_init_readonly_polynom_mpz (&init);
          bap_initial_polynom_mpz (&init, A);
        }
      ba0_pull_stack ();
      if (S)
        bap_set_polynom_mpz (S, &init);
      bap_set_polynom_mpz (R, &red);
    }
  else
    {
      bav_init_term (&T);
      bav_set_term_variable (&T, rg.var, 1);

      if (S)
        {
          ba0_pull_stack ();
          bap_separant_polynom_mpz (S, A);
          ba0_push_another_stack ();
          sep = S;
        }
      else
        {
          sep = bap_new_polynom_mpz ();
          bap_separant_polynom_mpz (sep, A);
        }
      bap_init_readonly_polynom_mpz (&red_sep);
      bap_reductum_polynom_mpz (&red_sep, sep);

      bap_init_polynom_mpz (&tmp);
      bap_mul_polynom_term_mpz (&tmp, &red_sep, &T);

      ba0_pull_stack ();
      bap_comblin_polynom_mpz (R, &red, rg.deg, &tmp, -1);
    }
  ba0_restore (&M);
}

/*
 * texinfo: bap_sepuctum_polynom_mpz
 * Assign to @var{R} the polynomial @math{d\,A - v\,S} where
 * @math{v^d} and @var{S} denote the rank and the separant of @var{A}.
 * Exception @code{BAP_ERRCST} is raised if @var{A} is numeric.
 * Exception @code{BA0_ERRALG} is raised if @var{R} is readonly.
 */

BAP_DLL void
bap_sepuctum_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A)
{
  bap_separant_and_sepuctum_polynom_mpz ((struct bap_polynom_mpz *) 0, R, A);
}
