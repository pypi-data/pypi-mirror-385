#include "bap_polyspec_mpz.h"
// #include "baz_factor_polynom_mpz.h"
#include "bap_polyspec_mpq.h"
#include "bap_itermon_mpz.h"
#include "bap_itermon_mpq.h"
#include "bap_creator_mpz.h"
#include "bap_creator_mpq.h"

BAP_DLL void
bap_polynom_mpq_to_mpq (
    struct bap_polynom_mpq *A,
    struct bap_polynom_mpq *B)
{
  bap_set_polynom_mpq (A, B);
}

/*
 * texinfo: bap_polynom_mpz_to_mpq
 * Assign @var{B} to @var{A}.
 */

BAP_DLL void
bap_polynom_mpz_to_mpq (
    struct bap_polynom_mpq *A,
    struct bap_polynom_mpz *B)
{
  bap_set_polynom_numer_denom_mpq (A, B, (ba0__mpz_struct *) 0);
}

/*
 * texinfo: bap_set_polynom_numer_denom_mpq
 * Assign @math{B/denom} to @var{A}.
 * If @var{denom} is the zero pointer then it is supposed to be equal to
 * @math{1}. 
 * Exception @code{BA0_ERRIVZ} is raised if the value of @var{denom} is zero.
 */

BAP_DLL void
bap_set_polynom_numer_denom_mpq (
    struct bap_polynom_mpq *A,
    struct bap_polynom_mpz *B,
    ba0_mpz_t denom)
{
  struct bap_creator_mpq crea;
  struct bap_itermon_mpz iter;
  struct bav_term T;
  struct ba0_mark M;
  ba0_mpq_t q;

  if (bap_is_zero_polynom_mpz (B))
    {
      bap_set_polynom_zero_mpq (A);
      return;
    }

  if (denom != (ba0__mpz_struct *) 0 && ba0_mpz_sgn (denom) == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRIVZ);

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&T);
  bav_set_term (&T, &B->total_rank);

  ba0_mpq_init (q);

  ba0_pull_stack ();
  bap_begin_creator_mpq (&crea, A, &T, bap_exact_total_rank,
      bap_nbmon_polynom_mpz (B));
  ba0_push_another_stack ();

  bap_begin_itermon_mpz (&iter, B);
  while (!bap_outof_itermon_mpz (&iter))
    {
      bap_term_itermon_mpz (&T, &iter);
      ba0_mpq_set_z (q, *bap_coeff_itermon_mpz (&iter));
      if (denom != (ba0__mpz_struct *) 0)
        {
          ba0_mpq_set_den (q, denom);
          ba0_mpq_canonicalize (q);
        }

      ba0_pull_stack ();
      bap_write_creator_mpq (&crea, &T, q);
      ba0_push_another_stack ();

      bap_next_itermon_mpz (&iter);
    }
  ba0_pull_stack ();
  bap_close_creator_mpq (&crea);
  ba0_restore (&M);
}

/*
 * texinfo: bap_numer_polynom_mpq
 * Assign to @var{A} and @var{denom} the numerator and the denominator of
 * @var{B}. The parameter @var{denom} may be the zero pointer.
 */

BAP_DLL void
bap_numer_polynom_mpq (
    struct bap_polynom_mpz *A,
    ba0_mpz_t denom,
    struct bap_polynom_mpq *B)
{
  struct bap_creator_mpz crea;
  struct bap_itermon_mpq iter;
  struct bap_polynom_mpz *P;
  struct bav_term T;
  ba0_mpz_t q, tmp_denom;
  ba0_mpq_t *c;
  struct ba0_mark M;

  if (bap_is_zero_polynom_mpq (B))
    {
      bap_set_polynom_zero_mpz (A);
      if (denom != 0)
        ba0_mpz_set_ui (denom, 1);
      return;
    }

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_mpz_init (tmp_denom);
  bap_denom_polynom_mpq (tmp_denom, B);

  bav_init_term (&T);
  bav_set_term (&T, &B->total_rank);

  ba0_mpz_init (q);

  P = bap_new_polynom_mpz ();
  bap_begin_creator_mpz (&crea, P, &T, bap_exact_total_rank,
      bap_nbmon_polynom_mpq (B));
  bap_begin_itermon_mpq (&iter, B);
  while (!bap_outof_itermon_mpq (&iter))
    {
      bap_term_itermon_mpq (&T, &iter);
      c = bap_coeff_itermon_mpq (&iter);
      ba0_mpz_divexact (q, tmp_denom, ba0_mpq_denref (*c));
      ba0_mpz_mul (q, q, ba0_mpq_numref (*c));
      bap_write_creator_mpz (&crea, &T, q);
      bap_next_itermon_mpq (&iter);
    }
  bap_close_creator_mpz (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mpz (A, P);
  if (denom != 0)
    ba0_mpz_set (denom, tmp_denom);
  ba0_restore (&M);
}

/*-
\paragraph{void bap_denom_polynom_mpq (mpz_t n, struct bap_polynom_mpq * A)}
Sets $n$ to the denominator of~$A$.
-*/

/*
 * texinfo: bap_denom_polynom_mpq
 * Assign to @var{denom} the denominator of
 * @var{B}.
 */

BAP_DLL void
bap_denom_polynom_mpq (
    ba0_mpz_t n,
    struct bap_polynom_mpq *A)
{
  struct bap_itermon_mpq iter;

  if (bap_is_zero_polynom_mpq (A))
    BA0_RAISE_EXCEPTION (BAP_ERRNUL);
  bap_begin_itermon_mpq (&iter, A);
  ba0_mpz_set (n, ba0_mpq_denref (*bap_coeff_itermon_mpq (&iter)));
  bap_next_itermon_mpq (&iter);
  while (!bap_outof_itermon_mpq (&iter))
    {
      ba0_mpz_lcm (n, n, ba0_mpq_denref (*bap_coeff_itermon_mpq (&iter)));
      bap_next_itermon_mpq (&iter);
    }
}

/*
 * texinfo: bap_product_mpz_to_mpq
 * Assign @var{B} to @var{A}.
 */

BAP_DLL void
bap_product_mpz_to_mpq (
    struct bap_product_mpq *R,
    struct bap_product_mpz *P)
{
  ba0_int_p i;

  ba0_mpq_set_z (R->num_factor, P->num_factor);

  R->size = 0;
  bap_realloc_product_mpq (R, P->size);
  for (i = 0; i < P->size; i++)
    {
      bap_polynom_mpz_to_mpq (&R->tab[i].factor, &P->tab[i].factor);
      R->tab[i].exponent = P->tab[i].exponent;
      R->size++;
    }
}
