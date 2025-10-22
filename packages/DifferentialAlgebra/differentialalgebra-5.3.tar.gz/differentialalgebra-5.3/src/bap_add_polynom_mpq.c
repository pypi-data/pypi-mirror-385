#include "bap_polynom_mpq.h"
#include "bap_creator_mpq.h"
#include "bap_itermon_mpq.h"
#include "bap_itercoeff_mpq.h"
#include "bap__check_mpq.h"
#include "bap_add_polynom_mpq.h"

#define BAD_FLAG_mpq

/****************************************************************************
 ADDITION
 ****************************************************************************/

/*
 * texinfo: bap_add_polynom_mpq
 * Assign @math{A + B} to @var{R}.
 */

BAP_DLL void
bap_add_polynom_mpq (
    struct bap_polynom_mpq *R,
    struct bap_polynom_mpq *A,
    struct bap_polynom_mpq *B)
{
  struct bap_creator_mpq crea;
  struct bap_itermon_mpq iterA, iterB;
  struct bap_polynom_mpq *P;
  enum ba0_compare_code code;
  struct bav_term TA, TB;
  ba0_mpq_t bunk;
  bool outA, outB;
  struct ba0_mark M;

  bap__check_compatible_mpq (A, B);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&TA);
  bav_init_term (&TB);
  bav_set_term (&TA, &A->total_rank);
  bav_set_term (&TB, &B->total_rank);
  bav_lcm_term (&TA, &TA, &TB);

  P = bap_new_polynom_mpq ();
  bap_begin_creator_mpq (&crea, P, &TA, bap_approx_total_rank,
      BA0_MAX (bap_nbmon_polynom_mpq (A), bap_nbmon_polynom_mpq (B)));

  bap_begin_itermon_mpq (&iterA, A);
  bap_begin_itermon_mpq (&iterB, B);
  ba0_mpq_init (bunk);
  outA = bap_outof_itermon_mpq (&iterA);
  outB = bap_outof_itermon_mpq (&iterB);
  if (!outA)
    bap_term_itermon_mpq (&TA, &iterA);
  if (!outB)
    bap_term_itermon_mpq (&TB, &iterB);
  while (!outA && !outB)
    {
      code = bav_compare_term (&TA, &TB);
      switch (code)
        {
        case ba0_lt:
          bap_write_creator_mpq (&crea, &TB,
              *bap_coeff_itermon_mpq (&iterB));
          bap_next_itermon_mpq (&iterB);
          outB = bap_outof_itermon_mpq (&iterB);
          if (!outB)
            bap_term_itermon_mpq (&TB, &iterB);
          break;
        case ba0_gt:
          bap_write_creator_mpq (&crea, &TA,
              *bap_coeff_itermon_mpq (&iterA));
          bap_next_itermon_mpq (&iterA);
          outA = bap_outof_itermon_mpq (&iterA);
          if (!outA)
            bap_term_itermon_mpq (&TA, &iterA);
          break;
        default:
          ba0_mpq_add (bunk, *bap_coeff_itermon_mpq (&iterA),
              *bap_coeff_itermon_mpq (&iterB));
          bap_write_creator_mpq (&crea, &TA, bunk);
          bap_next_itermon_mpq (&iterB);
          bap_next_itermon_mpq (&iterA);
          outB = bap_outof_itermon_mpq (&iterB);
          outA = bap_outof_itermon_mpq (&iterA);
          if (!outB)
            bap_term_itermon_mpq (&TB, &iterB);
          if (!outA)
            bap_term_itermon_mpq (&TA, &iterA);
        }
    }
  while (!outA)
    {
      bap_write_creator_mpq (&crea, &TA, *bap_coeff_itermon_mpq (&iterA));
      bap_next_itermon_mpq (&iterA);
      outA = bap_outof_itermon_mpq (&iterA);
      if (!outA)
        bap_term_itermon_mpq (&TA, &iterA);
    }
  while (!outB)
    {
      bap_write_creator_mpq (&crea, &TB, *bap_coeff_itermon_mpq (&iterB));
      bap_next_itermon_mpq (&iterB);
      outB = bap_outof_itermon_mpq (&iterB);
      if (!outB)
        bap_term_itermon_mpq (&TB, &iterB);
    }
  bap_close_creator_mpq (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mpq (R, P);
  ba0_restore (&M);
}

/*
 * texinfo: bap_add_polynom_numeric_mpq
 * Assign @math{A + c} to @var{R}.
 */

BAP_DLL void
bap_add_polynom_numeric_mpq (
    struct bap_polynom_mpq *R,
    struct bap_polynom_mpq *A,
    ba0_mpq_t c)
{
  struct ba0_mark M;
  struct bav_rank rg;

  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (bap_is_zero_polynom_mpq (A))
    {
      rg = bav_constant_rank ();
      bap_set_polynom_crk_mpq (R, c, &rg);
    }
  else if (R == A)
    {
      if (!ba0_mpq_is_zero (c))
        {
          struct bav_term T;
          struct bap_itermon_mpq iter;
          ba0_mpq_t *lc;

          ba0_push_another_stack ();
          ba0_record (&M);
          bav_init_term (&T);
          ba0_pull_stack ();
          bap_end_itermon_mpq (&iter, R);
          ba0_push_another_stack ();
          bap_term_itermon_mpq (&T, &iter);
          ba0_pull_stack ();
          if (bav_is_one_term (&T))
            {
              lc = bap_coeff_itermon_mpq (&iter);
              ba0_mpq_add (*lc, *lc, c);
              if (ba0_mpq_is_zero (*lc))
                {
                  if (R->access == bap_sequential_monom_access)
                    R->seq.after--;
                  else
                    R->ind.size--;
                }
            }
          else
            {
              struct bap_creator_mpq crea;

              bap_append_creator_mpq (&crea, R, 1);
              bav_set_term_one (&T);
              bap_write_creator_mpq (&crea, &T, c);
              bap_close_creator_mpq (&crea);
            }
          ba0_restore (&M);
        }
    }
  else if (!ba0_mpq_is_zero (c))
    {
      struct bap_polynom_mpq *P;
      struct bav_rank rg;

      ba0_push_another_stack ();
      ba0_record (&M);
      rg = bav_constant_rank ();
      P = bap_new_polynom_crk_mpq (c, &rg);
      ba0_pull_stack ();
      bap_add_polynom_mpq (R, A, P);
      ba0_restore (&M);
    }
  else
    bap_set_polynom_mpq (R, A);
}

/*
 * texinfo: bap_sub_polynom_mpq
 * Assign @math{A - B} to @var{R}.
 */

BAP_DLL void
bap_sub_polynom_mpq (
    struct bap_polynom_mpq *R,
    struct bap_polynom_mpq *A,
    struct bap_polynom_mpq *B)
{
  struct bap_creator_mpq crea;
  struct bap_itermon_mpq iterA, iterB;
  struct bap_polynom_mpq *P;
  enum ba0_compare_code code;
  struct bav_term TA, TB;
  ba0_mpq_t bunk;
  bool outA, outB;
  struct ba0_mark M;

  bap__check_compatible_mpq (A, B);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&TA);
  bav_init_term (&TB);
  bav_set_term (&TA, &A->total_rank);
  bav_set_term (&TB, &B->total_rank);
  bav_lcm_term (&TA, &TA, &TB);

  P = bap_new_polynom_mpq ();
  bap_begin_creator_mpq (&crea, P, &TA, bap_approx_total_rank,
      BA0_MAX (bap_nbmon_polynom_mpq (A), bap_nbmon_polynom_mpq (B)));

  bap_begin_itermon_mpq (&iterA, A);
  bap_begin_itermon_mpq (&iterB, B);
  ba0_mpq_init (bunk);
  outA = bap_outof_itermon_mpq (&iterA);
  outB = bap_outof_itermon_mpq (&iterB);
  if (!outA)
    bap_term_itermon_mpq (&TA, &iterA);
  if (!outB)
    bap_term_itermon_mpq (&TB, &iterB);
  while (!outA && !outB)
    {
      code = bav_compare_term (&TA, &TB);
      switch (code)
        {
        case ba0_lt:
          bap_write_neg_creator_mpq (&crea, &TB,
              *bap_coeff_itermon_mpq (&iterB));
          bap_next_itermon_mpq (&iterB);
          outB = bap_outof_itermon_mpq (&iterB);
          if (!outB)
            bap_term_itermon_mpq (&TB, &iterB);
          break;
        case ba0_gt:
          bap_write_creator_mpq (&crea, &TA,
              *bap_coeff_itermon_mpq (&iterA));
          bap_next_itermon_mpq (&iterA);
          outA = bap_outof_itermon_mpq (&iterA);
          if (!outA)
            bap_term_itermon_mpq (&TA, &iterA);
          break;
        default:
          ba0_mpq_sub (bunk, *bap_coeff_itermon_mpq (&iterA),
              *bap_coeff_itermon_mpq (&iterB));
          bap_write_creator_mpq (&crea, &TA, bunk);
          bap_next_itermon_mpq (&iterB);
          bap_next_itermon_mpq (&iterA);
          outB = bap_outof_itermon_mpq (&iterB);
          outA = bap_outof_itermon_mpq (&iterA);
          if (!outB)
            bap_term_itermon_mpq (&TB, &iterB);
          if (!outA)
            bap_term_itermon_mpq (&TA, &iterA);
        }
    }
  while (!outA)
    {
      bap_write_creator_mpq (&crea, &TA, *bap_coeff_itermon_mpq (&iterA));
      bap_next_itermon_mpq (&iterA);
      outA = bap_outof_itermon_mpq (&iterA);
      if (!outA)
        bap_term_itermon_mpq (&TA, &iterA);
    }
  while (!outB)
    {
      bap_write_neg_creator_mpq (&crea, &TB,
          *bap_coeff_itermon_mpq (&iterB));
      bap_next_itermon_mpq (&iterB);
      outB = bap_outof_itermon_mpq (&iterB);
      if (!outB)
        bap_term_itermon_mpq (&TB, &iterB);
    }
  bap_close_creator_mpq (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mpq (R, P);
  ba0_restore (&M);
}

/*
 * R = A - q * TQ * B
 */

/*
 * texinfo: bap_submulmon_polynom_mpq
 * Assign @math{A - q\,@emph{TQ}\,B} to @var{R}.
 */

BAP_DLL void
bap_submulmon_polynom_mpq (
    struct bap_polynom_mpq *R,
    struct bap_polynom_mpq *A,
    struct bap_polynom_mpq *B,
    struct bav_term *TQ,
    ba0_mpq_t q)
{
  struct bap_creator_mpq crea;
  struct bap_itermon_mpq iterA, iterB;
  struct bap_polynom_mpq *P;
  enum ba0_compare_code code;
  struct bav_term TA, TB;
  ba0_mpq_t cB, bunk;
  bool outA, outB;
  struct ba0_mark M;

  bap__check_compatible_mpq (A, B);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);
  bav_init_term (&TA);
  bav_init_term (&TB);
  bav_set_term (&TA, &A->total_rank);
  bav_set_term (&TB, &B->total_rank);
  bav_mul_term (&TB, &TB, TQ);
  bav_lcm_term (&TA, &TA, &TB);

  P = bap_new_polynom_mpq ();
  bap_begin_creator_mpq (&crea, P, &TA, bap_approx_total_rank,
      BA0_MAX (bap_nbmon_polynom_mpq (A), bap_nbmon_polynom_mpq (B)));

  bap_begin_itermon_mpq (&iterA, A);
  bap_begin_itermon_mpq (&iterB, B);
  ba0_mpq_init (bunk);
  ba0_mpq_init (cB);
  outA = bap_outof_itermon_mpq (&iterA);
  outB = bap_outof_itermon_mpq (&iterB);
  if (!outA)
    bap_term_itermon_mpq (&TA, &iterA);
  if (!outB)
    {
      bap_term_itermon_mpq (&TB, &iterB);
      bav_mul_term (&TB, &TB, TQ);
      ba0_mpq_mul (cB, *bap_coeff_itermon_mpq (&iterB), q);
    }
  while (!outA && !outB)
    {
      code = bav_compare_term (&TA, &TB);
      switch (code)
        {
        case ba0_lt:
          bap_write_neg_creator_mpq (&crea, &TB, cB);
          bap_next_itermon_mpq (&iterB);
          outB = bap_outof_itermon_mpq (&iterB);
          if (!outB)
            {
              bap_term_itermon_mpq (&TB, &iterB);
              bav_mul_term (&TB, &TB, TQ);
              ba0_mpq_mul (cB, *bap_coeff_itermon_mpq (&iterB), q);
            }
          break;
        case ba0_gt:
          bap_write_creator_mpq (&crea, &TA,
              *bap_coeff_itermon_mpq (&iterA));
          bap_next_itermon_mpq (&iterA);
          outA = bap_outof_itermon_mpq (&iterA);
          if (!outA)
            bap_term_itermon_mpq (&TA, &iterA);
          break;
        default:
          ba0_mpq_sub (bunk, *bap_coeff_itermon_mpq (&iterA), cB);
          bap_write_creator_mpq (&crea, &TA, bunk);
          bap_next_itermon_mpq (&iterB);
          bap_next_itermon_mpq (&iterA);
          outB = bap_outof_itermon_mpq (&iterB);
          outA = bap_outof_itermon_mpq (&iterA);
          if (!outB)
            {
              bap_term_itermon_mpq (&TB, &iterB);
              bav_mul_term (&TB, &TB, TQ);
              ba0_mpq_mul (cB, *bap_coeff_itermon_mpq (&iterB), q);
            }
          if (!outA)
            bap_term_itermon_mpq (&TA, &iterA);
        }
    }
  while (!outA)
    {
      bap_write_creator_mpq (&crea, &TA, *bap_coeff_itermon_mpq (&iterA));
      bap_next_itermon_mpq (&iterA);
      outA = bap_outof_itermon_mpq (&iterA);
      if (!outA)
        bap_term_itermon_mpq (&TA, &iterA);
    }
  while (!outB)
    {
      bap_write_neg_creator_mpq (&crea, &TB, cB);
      bap_next_itermon_mpq (&iterB);
      outB = bap_outof_itermon_mpq (&iterB);
      if (!outB)
        {
          bap_term_itermon_mpq (&TB, &iterB);
          bav_mul_term (&TB, &TB, TQ);
          ba0_mpq_mul (cB, *bap_coeff_itermon_mpq (&iterB), q);
        }
    }

  bap_close_creator_mpq (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mpq (R, P);
  ba0_restore (&M);
}

/*
 * R = cA * A + cB * B
 */

/*
 * texinfo: bap_comblin_polynom_mpq
 * Assign the linear combination @math{@emph{cA}\,A + @emph{cB}\,B}
 * to @var{R}.
 */

BAP_DLL void
bap_comblin_polynom_mpq (
    struct bap_polynom_mpq *R,
    struct bap_polynom_mpq *A,
    ba0_int_p cA,
    struct bap_polynom_mpq *B,
    ba0_int_p cB)
{
  struct bap_creator_mpq crea;
  struct bap_itermon_mpq iterA, iterB;
  struct bap_polynom_mpq *P;
  enum ba0_compare_code code;
  struct bav_term TA, TB;
  ba0_mpq_t bunk, bink;
  bool outA, outB;
  struct ba0_mark M;

  bap__check_compatible_mpq (A, B);
  if (cA == 0 || cB == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&TA);
  bav_init_term (&TB);
  bav_set_term (&TA, &A->total_rank);
  bav_set_term (&TB, &B->total_rank);
  bav_lcm_term (&TA, &TA, &TB);

  P = bap_new_polynom_mpq ();
  bap_begin_creator_mpq (&crea, P, &TA, bap_approx_total_rank,
      BA0_MAX (bap_nbmon_polynom_mpq (A), bap_nbmon_polynom_mpq (B)));

  bap_begin_itermon_mpq (&iterA, A);
  bap_begin_itermon_mpq (&iterB, B);
  ba0_mpq_init (bunk);
  ba0_mpq_init (bink);
  outA = bap_outof_itermon_mpq (&iterA);
  outB = bap_outof_itermon_mpq (&iterB);
  if (!outA)
    bap_term_itermon_mpq (&TA, &iterA);
  if (!outB)
    bap_term_itermon_mpq (&TB, &iterB);
  while (!outA && !outB)
    {
      code = bav_compare_term (&TA, &TB);
      switch (code)
        {
        case ba0_lt:
/*
 * Specific cast.
 * GMP function expect long which is 32 bits instead of 64 on Windows 64.
 */
          ba0_mpq_mul_si (bunk, *bap_coeff_itermon_mpq (&iterB), (long) cB);
          bap_write_creator_mpq (&crea, &TB, bunk);
          bap_next_itermon_mpq (&iterB);
          outB = bap_outof_itermon_mpq (&iterB);
          if (!outB)
            bap_term_itermon_mpq (&TB, &iterB);
          break;
        case ba0_gt:
/*
 * Specific cast.
 * GMP function expect long which is 32 bits instead of 64 on Windows 64.
 */
          ba0_mpq_mul_si (bunk, *bap_coeff_itermon_mpq (&iterA), (long) cA);
          bap_write_creator_mpq (&crea, &TA, bunk);
          bap_next_itermon_mpq (&iterA);
          outA = bap_outof_itermon_mpq (&iterA);
          if (!outA)
            bap_term_itermon_mpq (&TA, &iterA);
          break;
        default:
/*
 * Specific cast.
 * GMP function expect long which is 32 bits instead of 64 on Windows 64.
 */
          ba0_mpq_mul_si (bunk, *bap_coeff_itermon_mpq (&iterA), (long) cA);
          ba0_mpq_mul_si (bink, *bap_coeff_itermon_mpq (&iterB), (long) cB);
          ba0_mpq_add (bunk, bunk, bink);
          bap_write_creator_mpq (&crea, &TA, bunk);
          bap_next_itermon_mpq (&iterB);
          bap_next_itermon_mpq (&iterA);
          outB = bap_outof_itermon_mpq (&iterB);
          outA = bap_outof_itermon_mpq (&iterA);
          if (!outB)
            bap_term_itermon_mpq (&TB, &iterB);
          if (!outA)
            bap_term_itermon_mpq (&TA, &iterA);
        }
    }
  while (!outA)
/*
 * Specific cast.
 * GMP function expect long which is 32 bits instead of 64 on Windows 64.
 */
    {
      ba0_mpq_mul_si (bunk, *bap_coeff_itermon_mpq (&iterA), (long) cA);
      bap_write_creator_mpq (&crea, &TA, bunk);
      bap_next_itermon_mpq (&iterA);
      outA = bap_outof_itermon_mpq (&iterA);
      if (!outA)
        bap_term_itermon_mpq (&TA, &iterA);
    }
  while (!outB)
/*
 * Specific cast.
 * GMP function expect long which is 32 bits instead of 64 on Windows 64.
 */
    {
      ba0_mpq_mul_si (bunk, *bap_coeff_itermon_mpq (&iterB), (long) cB);
      bap_write_creator_mpq (&crea, &TB, bunk);
      bap_next_itermon_mpq (&iterB);
      outB = bap_outof_itermon_mpq (&iterB);
      if (!outB)
        bap_term_itermon_mpq (&TB, &iterB);
    }
  bap_close_creator_mpq (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mpq (R, P);
  ba0_restore (&M);
}

/*
 * R = A * rg + B
 */

/*
 * texinfo: bap_addmulrk_polynom_mpq
 * Assign @math{A\,@emph{rg} + B} to @var{R}.
 */

BAP_DLL void
bap_addmulrk_polynom_mpq (
    struct bap_polynom_mpq *R,
    struct bap_polynom_mpq *A,
    struct bav_rank *rg,
    struct bap_polynom_mpq *B)
{
  struct bap_creator_mpq crea;
  struct bap_itermon_mpq iterA, iterB;
  struct bap_polynom_mpq *P;
  enum ba0_compare_code code;
  struct bav_term TA, TB;
  ba0_mpq_t bunk;
  bool outA, outB;
  struct ba0_mark M;

  bap__check_compatible_mpq (A, B);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&TA);
  bav_init_term (&TB);
  bav_set_term (&TA, &A->total_rank);
  bav_mul_term_rank (&TA, &TA, rg);
  bav_set_term (&TB, &B->total_rank);
  bav_lcm_term (&TA, &TA, &TB);

  P = bap_new_polynom_mpq ();
  bap_begin_creator_mpq (&crea, P, &TA, bap_approx_total_rank,
      BA0_MAX (bap_nbmon_polynom_mpq (A), bap_nbmon_polynom_mpq (B)));

  bap_begin_itermon_mpq (&iterA, A);
  bap_begin_itermon_mpq (&iterB, B);
  ba0_mpq_init (bunk);
  outA = bap_outof_itermon_mpq (&iterA);
  outB = bap_outof_itermon_mpq (&iterB);
  if (!outA)
    {
      bap_term_itermon_mpq (&TA, &iterA);
      bav_mul_term_rank (&TA, &TA, rg);
    }
  if (!outB)
    bap_term_itermon_mpq (&TB, &iterB);
  while (!outA && !outB)
    {
      code = bav_compare_term (&TA, &TB);
      switch (code)
        {
        case ba0_lt:
          bap_write_creator_mpq (&crea, &TB,
              *bap_coeff_itermon_mpq (&iterB));
          bap_next_itermon_mpq (&iterB);
          outB = bap_outof_itermon_mpq (&iterB);
          if (!outB)
            bap_term_itermon_mpq (&TB, &iterB);
          break;
        case ba0_gt:
          bap_write_creator_mpq (&crea, &TA,
              *bap_coeff_itermon_mpq (&iterA));
          bap_next_itermon_mpq (&iterA);
          outA = bap_outof_itermon_mpq (&iterA);
          if (!outA)
            {
              bap_term_itermon_mpq (&TA, &iterA);
              bav_mul_term_rank (&TA, &TA, rg);
            }
          break;
        default:
          ba0_mpq_add (bunk, *bap_coeff_itermon_mpq (&iterA),
              *bap_coeff_itermon_mpq (&iterB));
          bap_write_creator_mpq (&crea, &TA, bunk);
          bap_next_itermon_mpq (&iterB);
          bap_next_itermon_mpq (&iterA);
          outB = bap_outof_itermon_mpq (&iterB);
          outA = bap_outof_itermon_mpq (&iterA);
          if (!outB)
            bap_term_itermon_mpq (&TB, &iterB);
          if (!outA)
            {
              bap_term_itermon_mpq (&TA, &iterA);
              bav_mul_term_rank (&TA, &TA, rg);
            }
        }
    }
  while (!outA)
    {
      bap_write_creator_mpq (&crea, &TA, *bap_coeff_itermon_mpq (&iterA));
      bap_next_itermon_mpq (&iterA);
      outA = bap_outof_itermon_mpq (&iterA);
      if (!outA)
        {
          bap_term_itermon_mpq (&TA, &iterA);
          bav_mul_term_rank (&TA, &TA, rg);
        }
    }
  while (!outB)
    {
      bap_write_creator_mpq (&crea, &TB, *bap_coeff_itermon_mpq (&iterB));
      bap_next_itermon_mpq (&iterB);
      outB = bap_outof_itermon_mpq (&iterB);
      if (!outB)
        bap_term_itermon_mpq (&TB, &iterB);
    }
  bap_close_creator_mpq (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mpq (R, P);
  ba0_restore (&M);
}

/*
 * R = A * rg - B
 */

/*
 * texinfo: bap_submulrk_polynom_mpq
 * Assign @math{A\,@emph{rg} - B} to @var{R}.
 */

BAP_DLL void
bap_submulrk_polynom_mpq (
    struct bap_polynom_mpq *R,
    struct bap_polynom_mpq *A,
    struct bav_rank *rg,
    struct bap_polynom_mpq *B)
{
  struct bap_creator_mpq crea;
  struct bap_itermon_mpq iterA, iterB;
  struct bap_polynom_mpq *P;
  enum ba0_compare_code code;
  struct bav_term TA, TB;
  ba0_mpq_t bunk;
  bool outA, outB;
  struct ba0_mark M;

  bap__check_compatible_mpq (A, B);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&TA);
  bav_init_term (&TB);
  bav_set_term (&TA, &A->total_rank);
  bav_mul_term_rank (&TA, &TA, rg);
  bav_set_term (&TB, &B->total_rank);
  bav_lcm_term (&TA, &TA, &TB);

  P = bap_new_polynom_mpq ();
  bap_begin_creator_mpq (&crea, P, &TA, bap_approx_total_rank,
      BA0_MAX (bap_nbmon_polynom_mpq (A), bap_nbmon_polynom_mpq (B)));

  bap_begin_itermon_mpq (&iterA, A);
  bap_begin_itermon_mpq (&iterB, B);
  ba0_mpq_init (bunk);
  outA = bap_outof_itermon_mpq (&iterA);
  outB = bap_outof_itermon_mpq (&iterB);
  if (!outA)
    {
      bap_term_itermon_mpq (&TA, &iterA);
      bav_mul_term_rank (&TA, &TA, rg);
    }
  if (!outB)
    bap_term_itermon_mpq (&TB, &iterB);
  while (!outA && !outB)
    {
      code = bav_compare_term (&TA, &TB);
      switch (code)
        {
        case ba0_lt:
          bap_write_neg_creator_mpq (&crea, &TB,
              *bap_coeff_itermon_mpq (&iterB));
          bap_next_itermon_mpq (&iterB);
          outB = bap_outof_itermon_mpq (&iterB);
          if (!outB)
            bap_term_itermon_mpq (&TB, &iterB);
          break;
        case ba0_gt:
          bap_write_creator_mpq (&crea, &TA,
              *bap_coeff_itermon_mpq (&iterA));
          bap_next_itermon_mpq (&iterA);
          outA = bap_outof_itermon_mpq (&iterA);
          if (!outA)
            {
              bap_term_itermon_mpq (&TA, &iterA);
              bav_mul_term_rank (&TA, &TA, rg);
            }
          break;
        default:
          ba0_mpq_sub (bunk, *bap_coeff_itermon_mpq (&iterA),
              *bap_coeff_itermon_mpq (&iterB));
          bap_write_creator_mpq (&crea, &TA, bunk);
          bap_next_itermon_mpq (&iterB);
          bap_next_itermon_mpq (&iterA);
          outB = bap_outof_itermon_mpq (&iterB);
          outA = bap_outof_itermon_mpq (&iterA);
          if (!outB)
            bap_term_itermon_mpq (&TB, &iterB);
          if (!outA)
            {
              bap_term_itermon_mpq (&TA, &iterA);
              bav_mul_term_rank (&TA, &TA, rg);
            }
        }
    }
  while (!outA)
    {
      bap_write_creator_mpq (&crea, &TA, *bap_coeff_itermon_mpq (&iterA));
      bap_next_itermon_mpq (&iterA);
      outA = bap_outof_itermon_mpq (&iterA);
      if (!outA)
        {
          bap_term_itermon_mpq (&TA, &iterA);
          bav_mul_term_rank (&TA, &TA, rg);
        }
    }
  while (!outB)
    {
      bap_write_neg_creator_mpq (&crea, &TB,
          *bap_coeff_itermon_mpq (&iterB));
      bap_next_itermon_mpq (&iterB);
      outB = bap_outof_itermon_mpq (&iterB);
      if (!outB)
        bap_term_itermon_mpq (&TB, &iterB);
    }
  bap_close_creator_mpq (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mpq (R, P);
  ba0_restore (&M);
}


#undef BAD_FLAG_mpq
