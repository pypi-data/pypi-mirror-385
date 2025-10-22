#include "bap_polynom_mpz.h"
#include "bap_creator_mpz.h"
#include "bap_itermon_mpz.h"
#include "bap_itercoeff_mpz.h"
#include "bap__check_mpz.h"
#include "bap_add_polynom_mpz.h"

#define BAD_FLAG_mpz

/****************************************************************************
 ADDITION
 ****************************************************************************/

/*
 * texinfo: bap_add_polynom_mpz
 * Assign @math{A + B} to @var{R}.
 */

BAP_DLL void
bap_add_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *B)
{
  struct bap_creator_mpz crea;
  struct bap_itermon_mpz iterA, iterB;
  struct bap_polynom_mpz *P;
  enum ba0_compare_code code;
  struct bav_term TA, TB;
  ba0_mpz_t bunk;
  bool outA, outB;
  struct ba0_mark M;

  bap__check_compatible_mpz (A, B);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&TA);
  bav_init_term (&TB);
  bav_set_term (&TA, &A->total_rank);
  bav_set_term (&TB, &B->total_rank);
  bav_lcm_term (&TA, &TA, &TB);

  P = bap_new_polynom_mpz ();
  bap_begin_creator_mpz (&crea, P, &TA, bap_approx_total_rank,
      BA0_MAX (bap_nbmon_polynom_mpz (A), bap_nbmon_polynom_mpz (B)));

  bap_begin_itermon_mpz (&iterA, A);
  bap_begin_itermon_mpz (&iterB, B);
  ba0_mpz_init (bunk);
  outA = bap_outof_itermon_mpz (&iterA);
  outB = bap_outof_itermon_mpz (&iterB);
  if (!outA)
    bap_term_itermon_mpz (&TA, &iterA);
  if (!outB)
    bap_term_itermon_mpz (&TB, &iterB);
  while (!outA && !outB)
    {
      code = bav_compare_term (&TA, &TB);
      switch (code)
        {
        case ba0_lt:
          bap_write_creator_mpz (&crea, &TB,
              *bap_coeff_itermon_mpz (&iterB));
          bap_next_itermon_mpz (&iterB);
          outB = bap_outof_itermon_mpz (&iterB);
          if (!outB)
            bap_term_itermon_mpz (&TB, &iterB);
          break;
        case ba0_gt:
          bap_write_creator_mpz (&crea, &TA,
              *bap_coeff_itermon_mpz (&iterA));
          bap_next_itermon_mpz (&iterA);
          outA = bap_outof_itermon_mpz (&iterA);
          if (!outA)
            bap_term_itermon_mpz (&TA, &iterA);
          break;
        default:
          ba0_mpz_add (bunk, *bap_coeff_itermon_mpz (&iterA),
              *bap_coeff_itermon_mpz (&iterB));
          bap_write_creator_mpz (&crea, &TA, bunk);
          bap_next_itermon_mpz (&iterB);
          bap_next_itermon_mpz (&iterA);
          outB = bap_outof_itermon_mpz (&iterB);
          outA = bap_outof_itermon_mpz (&iterA);
          if (!outB)
            bap_term_itermon_mpz (&TB, &iterB);
          if (!outA)
            bap_term_itermon_mpz (&TA, &iterA);
        }
    }
  while (!outA)
    {
      bap_write_creator_mpz (&crea, &TA, *bap_coeff_itermon_mpz (&iterA));
      bap_next_itermon_mpz (&iterA);
      outA = bap_outof_itermon_mpz (&iterA);
      if (!outA)
        bap_term_itermon_mpz (&TA, &iterA);
    }
  while (!outB)
    {
      bap_write_creator_mpz (&crea, &TB, *bap_coeff_itermon_mpz (&iterB));
      bap_next_itermon_mpz (&iterB);
      outB = bap_outof_itermon_mpz (&iterB);
      if (!outB)
        bap_term_itermon_mpz (&TB, &iterB);
    }
  bap_close_creator_mpz (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mpz (R, P);
  ba0_restore (&M);
}

/*
 * texinfo: bap_add_polynom_numeric_mpz
 * Assign @math{A + c} to @var{R}.
 */

BAP_DLL void
bap_add_polynom_numeric_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A,
    ba0_mpz_t c)
{
  struct ba0_mark M;
  struct bav_rank rg;

  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (bap_is_zero_polynom_mpz (A))
    {
      rg = bav_constant_rank ();
      bap_set_polynom_crk_mpz (R, c, &rg);
    }
  else if (R == A)
    {
      if (!ba0_mpz_is_zero (c))
        {
          struct bav_term T;
          struct bap_itermon_mpz iter;
          ba0_mpz_t *lc;

          ba0_push_another_stack ();
          ba0_record (&M);
          bav_init_term (&T);
          ba0_pull_stack ();
          bap_end_itermon_mpz (&iter, R);
          ba0_push_another_stack ();
          bap_term_itermon_mpz (&T, &iter);
          ba0_pull_stack ();
          if (bav_is_one_term (&T))
            {
              lc = bap_coeff_itermon_mpz (&iter);
              ba0_mpz_add (*lc, *lc, c);
              if (ba0_mpz_is_zero (*lc))
                {
                  if (R->access == bap_sequential_monom_access)
                    R->seq.after--;
                  else
                    R->ind.size--;
                }
            }
          else
            {
              struct bap_creator_mpz crea;

              bap_append_creator_mpz (&crea, R, 1);
              bav_set_term_one (&T);
              bap_write_creator_mpz (&crea, &T, c);
              bap_close_creator_mpz (&crea);
            }
          ba0_restore (&M);
        }
    }
  else if (!ba0_mpz_is_zero (c))
    {
      struct bap_polynom_mpz *P;
      struct bav_rank rg;

      ba0_push_another_stack ();
      ba0_record (&M);
      rg = bav_constant_rank ();
      P = bap_new_polynom_crk_mpz (c, &rg);
      ba0_pull_stack ();
      bap_add_polynom_mpz (R, A, P);
      ba0_restore (&M);
    }
  else
    bap_set_polynom_mpz (R, A);
}

/*
 * texinfo: bap_sub_polynom_mpz
 * Assign @math{A - B} to @var{R}.
 */

BAP_DLL void
bap_sub_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *B)
{
  struct bap_creator_mpz crea;
  struct bap_itermon_mpz iterA, iterB;
  struct bap_polynom_mpz *P;
  enum ba0_compare_code code;
  struct bav_term TA, TB;
  ba0_mpz_t bunk;
  bool outA, outB;
  struct ba0_mark M;

  bap__check_compatible_mpz (A, B);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&TA);
  bav_init_term (&TB);
  bav_set_term (&TA, &A->total_rank);
  bav_set_term (&TB, &B->total_rank);
  bav_lcm_term (&TA, &TA, &TB);

  P = bap_new_polynom_mpz ();
  bap_begin_creator_mpz (&crea, P, &TA, bap_approx_total_rank,
      BA0_MAX (bap_nbmon_polynom_mpz (A), bap_nbmon_polynom_mpz (B)));

  bap_begin_itermon_mpz (&iterA, A);
  bap_begin_itermon_mpz (&iterB, B);
  ba0_mpz_init (bunk);
  outA = bap_outof_itermon_mpz (&iterA);
  outB = bap_outof_itermon_mpz (&iterB);
  if (!outA)
    bap_term_itermon_mpz (&TA, &iterA);
  if (!outB)
    bap_term_itermon_mpz (&TB, &iterB);
  while (!outA && !outB)
    {
      code = bav_compare_term (&TA, &TB);
      switch (code)
        {
        case ba0_lt:
          bap_write_neg_creator_mpz (&crea, &TB,
              *bap_coeff_itermon_mpz (&iterB));
          bap_next_itermon_mpz (&iterB);
          outB = bap_outof_itermon_mpz (&iterB);
          if (!outB)
            bap_term_itermon_mpz (&TB, &iterB);
          break;
        case ba0_gt:
          bap_write_creator_mpz (&crea, &TA,
              *bap_coeff_itermon_mpz (&iterA));
          bap_next_itermon_mpz (&iterA);
          outA = bap_outof_itermon_mpz (&iterA);
          if (!outA)
            bap_term_itermon_mpz (&TA, &iterA);
          break;
        default:
          ba0_mpz_sub (bunk, *bap_coeff_itermon_mpz (&iterA),
              *bap_coeff_itermon_mpz (&iterB));
          bap_write_creator_mpz (&crea, &TA, bunk);
          bap_next_itermon_mpz (&iterB);
          bap_next_itermon_mpz (&iterA);
          outB = bap_outof_itermon_mpz (&iterB);
          outA = bap_outof_itermon_mpz (&iterA);
          if (!outB)
            bap_term_itermon_mpz (&TB, &iterB);
          if (!outA)
            bap_term_itermon_mpz (&TA, &iterA);
        }
    }
  while (!outA)
    {
      bap_write_creator_mpz (&crea, &TA, *bap_coeff_itermon_mpz (&iterA));
      bap_next_itermon_mpz (&iterA);
      outA = bap_outof_itermon_mpz (&iterA);
      if (!outA)
        bap_term_itermon_mpz (&TA, &iterA);
    }
  while (!outB)
    {
      bap_write_neg_creator_mpz (&crea, &TB,
          *bap_coeff_itermon_mpz (&iterB));
      bap_next_itermon_mpz (&iterB);
      outB = bap_outof_itermon_mpz (&iterB);
      if (!outB)
        bap_term_itermon_mpz (&TB, &iterB);
    }
  bap_close_creator_mpz (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mpz (R, P);
  ba0_restore (&M);
}

/*
 * R = A - q * TQ * B
 */

/*
 * texinfo: bap_submulmon_polynom_mpz
 * Assign @math{A - q\,@emph{TQ}\,B} to @var{R}.
 */

BAP_DLL void
bap_submulmon_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *B,
    struct bav_term *TQ,
    ba0_mpz_t q)
{
  struct bap_creator_mpz crea;
  struct bap_itermon_mpz iterA, iterB;
  struct bap_polynom_mpz *P;
  enum ba0_compare_code code;
  struct bav_term TA, TB;
  ba0_mpz_t cB, bunk;
  bool outA, outB;
  struct ba0_mark M;

  bap__check_compatible_mpz (A, B);
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

  P = bap_new_polynom_mpz ();
  bap_begin_creator_mpz (&crea, P, &TA, bap_approx_total_rank,
      BA0_MAX (bap_nbmon_polynom_mpz (A), bap_nbmon_polynom_mpz (B)));

  bap_begin_itermon_mpz (&iterA, A);
  bap_begin_itermon_mpz (&iterB, B);
  ba0_mpz_init (bunk);
  ba0_mpz_init (cB);
  outA = bap_outof_itermon_mpz (&iterA);
  outB = bap_outof_itermon_mpz (&iterB);
  if (!outA)
    bap_term_itermon_mpz (&TA, &iterA);
  if (!outB)
    {
      bap_term_itermon_mpz (&TB, &iterB);
      bav_mul_term (&TB, &TB, TQ);
      ba0_mpz_mul (cB, *bap_coeff_itermon_mpz (&iterB), q);
    }
  while (!outA && !outB)
    {
      code = bav_compare_term (&TA, &TB);
      switch (code)
        {
        case ba0_lt:
          bap_write_neg_creator_mpz (&crea, &TB, cB);
          bap_next_itermon_mpz (&iterB);
          outB = bap_outof_itermon_mpz (&iterB);
          if (!outB)
            {
              bap_term_itermon_mpz (&TB, &iterB);
              bav_mul_term (&TB, &TB, TQ);
              ba0_mpz_mul (cB, *bap_coeff_itermon_mpz (&iterB), q);
            }
          break;
        case ba0_gt:
          bap_write_creator_mpz (&crea, &TA,
              *bap_coeff_itermon_mpz (&iterA));
          bap_next_itermon_mpz (&iterA);
          outA = bap_outof_itermon_mpz (&iterA);
          if (!outA)
            bap_term_itermon_mpz (&TA, &iterA);
          break;
        default:
          ba0_mpz_sub (bunk, *bap_coeff_itermon_mpz (&iterA), cB);
          bap_write_creator_mpz (&crea, &TA, bunk);
          bap_next_itermon_mpz (&iterB);
          bap_next_itermon_mpz (&iterA);
          outB = bap_outof_itermon_mpz (&iterB);
          outA = bap_outof_itermon_mpz (&iterA);
          if (!outB)
            {
              bap_term_itermon_mpz (&TB, &iterB);
              bav_mul_term (&TB, &TB, TQ);
              ba0_mpz_mul (cB, *bap_coeff_itermon_mpz (&iterB), q);
            }
          if (!outA)
            bap_term_itermon_mpz (&TA, &iterA);
        }
    }
  while (!outA)
    {
      bap_write_creator_mpz (&crea, &TA, *bap_coeff_itermon_mpz (&iterA));
      bap_next_itermon_mpz (&iterA);
      outA = bap_outof_itermon_mpz (&iterA);
      if (!outA)
        bap_term_itermon_mpz (&TA, &iterA);
    }
  while (!outB)
    {
      bap_write_neg_creator_mpz (&crea, &TB, cB);
      bap_next_itermon_mpz (&iterB);
      outB = bap_outof_itermon_mpz (&iterB);
      if (!outB)
        {
          bap_term_itermon_mpz (&TB, &iterB);
          bav_mul_term (&TB, &TB, TQ);
          ba0_mpz_mul (cB, *bap_coeff_itermon_mpz (&iterB), q);
        }
    }

  bap_close_creator_mpz (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mpz (R, P);
  ba0_restore (&M);
}

/*
 * R = cA * A + cB * B
 */

/*
 * texinfo: bap_comblin_polynom_mpz
 * Assign the linear combination @math{@emph{cA}\,A + @emph{cB}\,B}
 * to @var{R}.
 */

BAP_DLL void
bap_comblin_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A,
    ba0_int_p cA,
    struct bap_polynom_mpz *B,
    ba0_int_p cB)
{
  struct bap_creator_mpz crea;
  struct bap_itermon_mpz iterA, iterB;
  struct bap_polynom_mpz *P;
  enum ba0_compare_code code;
  struct bav_term TA, TB;
  ba0_mpz_t bunk, bink;
  bool outA, outB;
  struct ba0_mark M;

  bap__check_compatible_mpz (A, B);
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

  P = bap_new_polynom_mpz ();
  bap_begin_creator_mpz (&crea, P, &TA, bap_approx_total_rank,
      BA0_MAX (bap_nbmon_polynom_mpz (A), bap_nbmon_polynom_mpz (B)));

  bap_begin_itermon_mpz (&iterA, A);
  bap_begin_itermon_mpz (&iterB, B);
  ba0_mpz_init (bunk);
  ba0_mpz_init (bink);
  outA = bap_outof_itermon_mpz (&iterA);
  outB = bap_outof_itermon_mpz (&iterB);
  if (!outA)
    bap_term_itermon_mpz (&TA, &iterA);
  if (!outB)
    bap_term_itermon_mpz (&TB, &iterB);
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
          ba0_mpz_mul_si (bunk, *bap_coeff_itermon_mpz (&iterB), (long) cB);
          bap_write_creator_mpz (&crea, &TB, bunk);
          bap_next_itermon_mpz (&iterB);
          outB = bap_outof_itermon_mpz (&iterB);
          if (!outB)
            bap_term_itermon_mpz (&TB, &iterB);
          break;
        case ba0_gt:
/*
 * Specific cast.
 * GMP function expect long which is 32 bits instead of 64 on Windows 64.
 */
          ba0_mpz_mul_si (bunk, *bap_coeff_itermon_mpz (&iterA), (long) cA);
          bap_write_creator_mpz (&crea, &TA, bunk);
          bap_next_itermon_mpz (&iterA);
          outA = bap_outof_itermon_mpz (&iterA);
          if (!outA)
            bap_term_itermon_mpz (&TA, &iterA);
          break;
        default:
/*
 * Specific cast.
 * GMP function expect long which is 32 bits instead of 64 on Windows 64.
 */
          ba0_mpz_mul_si (bunk, *bap_coeff_itermon_mpz (&iterA), (long) cA);
          ba0_mpz_mul_si (bink, *bap_coeff_itermon_mpz (&iterB), (long) cB);
          ba0_mpz_add (bunk, bunk, bink);
          bap_write_creator_mpz (&crea, &TA, bunk);
          bap_next_itermon_mpz (&iterB);
          bap_next_itermon_mpz (&iterA);
          outB = bap_outof_itermon_mpz (&iterB);
          outA = bap_outof_itermon_mpz (&iterA);
          if (!outB)
            bap_term_itermon_mpz (&TB, &iterB);
          if (!outA)
            bap_term_itermon_mpz (&TA, &iterA);
        }
    }
  while (!outA)
/*
 * Specific cast.
 * GMP function expect long which is 32 bits instead of 64 on Windows 64.
 */
    {
      ba0_mpz_mul_si (bunk, *bap_coeff_itermon_mpz (&iterA), (long) cA);
      bap_write_creator_mpz (&crea, &TA, bunk);
      bap_next_itermon_mpz (&iterA);
      outA = bap_outof_itermon_mpz (&iterA);
      if (!outA)
        bap_term_itermon_mpz (&TA, &iterA);
    }
  while (!outB)
/*
 * Specific cast.
 * GMP function expect long which is 32 bits instead of 64 on Windows 64.
 */
    {
      ba0_mpz_mul_si (bunk, *bap_coeff_itermon_mpz (&iterB), (long) cB);
      bap_write_creator_mpz (&crea, &TB, bunk);
      bap_next_itermon_mpz (&iterB);
      outB = bap_outof_itermon_mpz (&iterB);
      if (!outB)
        bap_term_itermon_mpz (&TB, &iterB);
    }
  bap_close_creator_mpz (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mpz (R, P);
  ba0_restore (&M);
}

/*
 * R = A * rg + B
 */

/*
 * texinfo: bap_addmulrk_polynom_mpz
 * Assign @math{A\,@emph{rg} + B} to @var{R}.
 */

BAP_DLL void
bap_addmulrk_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A,
    struct bav_rank *rg,
    struct bap_polynom_mpz *B)
{
  struct bap_creator_mpz crea;
  struct bap_itermon_mpz iterA, iterB;
  struct bap_polynom_mpz *P;
  enum ba0_compare_code code;
  struct bav_term TA, TB;
  ba0_mpz_t bunk;
  bool outA, outB;
  struct ba0_mark M;

  bap__check_compatible_mpz (A, B);
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

  P = bap_new_polynom_mpz ();
  bap_begin_creator_mpz (&crea, P, &TA, bap_approx_total_rank,
      BA0_MAX (bap_nbmon_polynom_mpz (A), bap_nbmon_polynom_mpz (B)));

  bap_begin_itermon_mpz (&iterA, A);
  bap_begin_itermon_mpz (&iterB, B);
  ba0_mpz_init (bunk);
  outA = bap_outof_itermon_mpz (&iterA);
  outB = bap_outof_itermon_mpz (&iterB);
  if (!outA)
    {
      bap_term_itermon_mpz (&TA, &iterA);
      bav_mul_term_rank (&TA, &TA, rg);
    }
  if (!outB)
    bap_term_itermon_mpz (&TB, &iterB);
  while (!outA && !outB)
    {
      code = bav_compare_term (&TA, &TB);
      switch (code)
        {
        case ba0_lt:
          bap_write_creator_mpz (&crea, &TB,
              *bap_coeff_itermon_mpz (&iterB));
          bap_next_itermon_mpz (&iterB);
          outB = bap_outof_itermon_mpz (&iterB);
          if (!outB)
            bap_term_itermon_mpz (&TB, &iterB);
          break;
        case ba0_gt:
          bap_write_creator_mpz (&crea, &TA,
              *bap_coeff_itermon_mpz (&iterA));
          bap_next_itermon_mpz (&iterA);
          outA = bap_outof_itermon_mpz (&iterA);
          if (!outA)
            {
              bap_term_itermon_mpz (&TA, &iterA);
              bav_mul_term_rank (&TA, &TA, rg);
            }
          break;
        default:
          ba0_mpz_add (bunk, *bap_coeff_itermon_mpz (&iterA),
              *bap_coeff_itermon_mpz (&iterB));
          bap_write_creator_mpz (&crea, &TA, bunk);
          bap_next_itermon_mpz (&iterB);
          bap_next_itermon_mpz (&iterA);
          outB = bap_outof_itermon_mpz (&iterB);
          outA = bap_outof_itermon_mpz (&iterA);
          if (!outB)
            bap_term_itermon_mpz (&TB, &iterB);
          if (!outA)
            {
              bap_term_itermon_mpz (&TA, &iterA);
              bav_mul_term_rank (&TA, &TA, rg);
            }
        }
    }
  while (!outA)
    {
      bap_write_creator_mpz (&crea, &TA, *bap_coeff_itermon_mpz (&iterA));
      bap_next_itermon_mpz (&iterA);
      outA = bap_outof_itermon_mpz (&iterA);
      if (!outA)
        {
          bap_term_itermon_mpz (&TA, &iterA);
          bav_mul_term_rank (&TA, &TA, rg);
        }
    }
  while (!outB)
    {
      bap_write_creator_mpz (&crea, &TB, *bap_coeff_itermon_mpz (&iterB));
      bap_next_itermon_mpz (&iterB);
      outB = bap_outof_itermon_mpz (&iterB);
      if (!outB)
        bap_term_itermon_mpz (&TB, &iterB);
    }
  bap_close_creator_mpz (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mpz (R, P);
  ba0_restore (&M);
}

/*
 * R = A * rg - B
 */

/*
 * texinfo: bap_submulrk_polynom_mpz
 * Assign @math{A\,@emph{rg} - B} to @var{R}.
 */

BAP_DLL void
bap_submulrk_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A,
    struct bav_rank *rg,
    struct bap_polynom_mpz *B)
{
  struct bap_creator_mpz crea;
  struct bap_itermon_mpz iterA, iterB;
  struct bap_polynom_mpz *P;
  enum ba0_compare_code code;
  struct bav_term TA, TB;
  ba0_mpz_t bunk;
  bool outA, outB;
  struct ba0_mark M;

  bap__check_compatible_mpz (A, B);
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

  P = bap_new_polynom_mpz ();
  bap_begin_creator_mpz (&crea, P, &TA, bap_approx_total_rank,
      BA0_MAX (bap_nbmon_polynom_mpz (A), bap_nbmon_polynom_mpz (B)));

  bap_begin_itermon_mpz (&iterA, A);
  bap_begin_itermon_mpz (&iterB, B);
  ba0_mpz_init (bunk);
  outA = bap_outof_itermon_mpz (&iterA);
  outB = bap_outof_itermon_mpz (&iterB);
  if (!outA)
    {
      bap_term_itermon_mpz (&TA, &iterA);
      bav_mul_term_rank (&TA, &TA, rg);
    }
  if (!outB)
    bap_term_itermon_mpz (&TB, &iterB);
  while (!outA && !outB)
    {
      code = bav_compare_term (&TA, &TB);
      switch (code)
        {
        case ba0_lt:
          bap_write_neg_creator_mpz (&crea, &TB,
              *bap_coeff_itermon_mpz (&iterB));
          bap_next_itermon_mpz (&iterB);
          outB = bap_outof_itermon_mpz (&iterB);
          if (!outB)
            bap_term_itermon_mpz (&TB, &iterB);
          break;
        case ba0_gt:
          bap_write_creator_mpz (&crea, &TA,
              *bap_coeff_itermon_mpz (&iterA));
          bap_next_itermon_mpz (&iterA);
          outA = bap_outof_itermon_mpz (&iterA);
          if (!outA)
            {
              bap_term_itermon_mpz (&TA, &iterA);
              bav_mul_term_rank (&TA, &TA, rg);
            }
          break;
        default:
          ba0_mpz_sub (bunk, *bap_coeff_itermon_mpz (&iterA),
              *bap_coeff_itermon_mpz (&iterB));
          bap_write_creator_mpz (&crea, &TA, bunk);
          bap_next_itermon_mpz (&iterB);
          bap_next_itermon_mpz (&iterA);
          outB = bap_outof_itermon_mpz (&iterB);
          outA = bap_outof_itermon_mpz (&iterA);
          if (!outB)
            bap_term_itermon_mpz (&TB, &iterB);
          if (!outA)
            {
              bap_term_itermon_mpz (&TA, &iterA);
              bav_mul_term_rank (&TA, &TA, rg);
            }
        }
    }
  while (!outA)
    {
      bap_write_creator_mpz (&crea, &TA, *bap_coeff_itermon_mpz (&iterA));
      bap_next_itermon_mpz (&iterA);
      outA = bap_outof_itermon_mpz (&iterA);
      if (!outA)
        {
          bap_term_itermon_mpz (&TA, &iterA);
          bav_mul_term_rank (&TA, &TA, rg);
        }
    }
  while (!outB)
    {
      bap_write_neg_creator_mpz (&crea, &TB,
          *bap_coeff_itermon_mpz (&iterB));
      bap_next_itermon_mpz (&iterB);
      outB = bap_outof_itermon_mpz (&iterB);
      if (!outB)
        bap_term_itermon_mpz (&TB, &iterB);
    }
  bap_close_creator_mpz (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mpz (R, P);
  ba0_restore (&M);
}


#undef BAD_FLAG_mpz
