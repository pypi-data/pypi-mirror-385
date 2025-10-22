#include "bap_polynom_mint_hp.h"
#include "bap_creator_mint_hp.h"
#include "bap_itermon_mint_hp.h"
#include "bap_itercoeff_mint_hp.h"
#include "bap__check_mint_hp.h"
#include "bap_add_polynom_mint_hp.h"

#define BAD_FLAG_mint_hp

/****************************************************************************
 ADDITION
 ****************************************************************************/

/*
 * texinfo: bap_add_polynom_mint_hp
 * Assign @math{A + B} to @var{R}.
 */

BAP_DLL void
bap_add_polynom_mint_hp (
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A,
    struct bap_polynom_mint_hp *B)
{
  struct bap_creator_mint_hp crea;
  struct bap_itermon_mint_hp iterA, iterB;
  struct bap_polynom_mint_hp *P;
  enum ba0_compare_code code;
  struct bav_term TA, TB;
  ba0_mint_hp_t bunk;
  bool outA, outB;
  struct ba0_mark M;

  bap__check_compatible_mint_hp (A, B);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&TA);
  bav_init_term (&TB);
  bav_set_term (&TA, &A->total_rank);
  bav_set_term (&TB, &B->total_rank);
  bav_lcm_term (&TA, &TA, &TB);

  P = bap_new_polynom_mint_hp ();
  bap_begin_creator_mint_hp (&crea, P, &TA, bap_approx_total_rank,
      BA0_MAX (bap_nbmon_polynom_mint_hp (A), bap_nbmon_polynom_mint_hp (B)));

  bap_begin_itermon_mint_hp (&iterA, A);
  bap_begin_itermon_mint_hp (&iterB, B);
  ba0_mint_hp_init (bunk);
  outA = bap_outof_itermon_mint_hp (&iterA);
  outB = bap_outof_itermon_mint_hp (&iterB);
  if (!outA)
    bap_term_itermon_mint_hp (&TA, &iterA);
  if (!outB)
    bap_term_itermon_mint_hp (&TB, &iterB);
  while (!outA && !outB)
    {
      code = bav_compare_term (&TA, &TB);
      switch (code)
        {
        case ba0_lt:
          bap_write_creator_mint_hp (&crea, &TB,
              *bap_coeff_itermon_mint_hp (&iterB));
          bap_next_itermon_mint_hp (&iterB);
          outB = bap_outof_itermon_mint_hp (&iterB);
          if (!outB)
            bap_term_itermon_mint_hp (&TB, &iterB);
          break;
        case ba0_gt:
          bap_write_creator_mint_hp (&crea, &TA,
              *bap_coeff_itermon_mint_hp (&iterA));
          bap_next_itermon_mint_hp (&iterA);
          outA = bap_outof_itermon_mint_hp (&iterA);
          if (!outA)
            bap_term_itermon_mint_hp (&TA, &iterA);
          break;
        default:
          ba0_mint_hp_add (bunk, *bap_coeff_itermon_mint_hp (&iterA),
              *bap_coeff_itermon_mint_hp (&iterB));
          bap_write_creator_mint_hp (&crea, &TA, bunk);
          bap_next_itermon_mint_hp (&iterB);
          bap_next_itermon_mint_hp (&iterA);
          outB = bap_outof_itermon_mint_hp (&iterB);
          outA = bap_outof_itermon_mint_hp (&iterA);
          if (!outB)
            bap_term_itermon_mint_hp (&TB, &iterB);
          if (!outA)
            bap_term_itermon_mint_hp (&TA, &iterA);
        }
    }
  while (!outA)
    {
      bap_write_creator_mint_hp (&crea, &TA, *bap_coeff_itermon_mint_hp (&iterA));
      bap_next_itermon_mint_hp (&iterA);
      outA = bap_outof_itermon_mint_hp (&iterA);
      if (!outA)
        bap_term_itermon_mint_hp (&TA, &iterA);
    }
  while (!outB)
    {
      bap_write_creator_mint_hp (&crea, &TB, *bap_coeff_itermon_mint_hp (&iterB));
      bap_next_itermon_mint_hp (&iterB);
      outB = bap_outof_itermon_mint_hp (&iterB);
      if (!outB)
        bap_term_itermon_mint_hp (&TB, &iterB);
    }
  bap_close_creator_mint_hp (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mint_hp (R, P);
  ba0_restore (&M);
}

/*
 * texinfo: bap_add_polynom_numeric_mint_hp
 * Assign @math{A + c} to @var{R}.
 */

BAP_DLL void
bap_add_polynom_numeric_mint_hp (
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A,
    ba0_mint_hp_t c)
{
  struct ba0_mark M;
  struct bav_rank rg;

  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (bap_is_zero_polynom_mint_hp (A))
    {
      rg = bav_constant_rank ();
      bap_set_polynom_crk_mint_hp (R, c, &rg);
    }
  else if (R == A)
    {
      if (!ba0_mint_hp_is_zero (c))
        {
          struct bav_term T;
          struct bap_itermon_mint_hp iter;
          ba0_mint_hp_t *lc;

          ba0_push_another_stack ();
          ba0_record (&M);
          bav_init_term (&T);
          ba0_pull_stack ();
          bap_end_itermon_mint_hp (&iter, R);
          ba0_push_another_stack ();
          bap_term_itermon_mint_hp (&T, &iter);
          ba0_pull_stack ();
          if (bav_is_one_term (&T))
            {
              lc = bap_coeff_itermon_mint_hp (&iter);
              ba0_mint_hp_add (*lc, *lc, c);
              if (ba0_mint_hp_is_zero (*lc))
                {
                  if (R->access == bap_sequential_monom_access)
                    R->seq.after--;
                  else
                    R->ind.size--;
                }
            }
          else
            {
              struct bap_creator_mint_hp crea;

              bap_append_creator_mint_hp (&crea, R, 1);
              bav_set_term_one (&T);
              bap_write_creator_mint_hp (&crea, &T, c);
              bap_close_creator_mint_hp (&crea);
            }
          ba0_restore (&M);
        }
    }
  else if (!ba0_mint_hp_is_zero (c))
    {
      struct bap_polynom_mint_hp *P;
      struct bav_rank rg;

      ba0_push_another_stack ();
      ba0_record (&M);
      rg = bav_constant_rank ();
      P = bap_new_polynom_crk_mint_hp (c, &rg);
      ba0_pull_stack ();
      bap_add_polynom_mint_hp (R, A, P);
      ba0_restore (&M);
    }
  else
    bap_set_polynom_mint_hp (R, A);
}

/*
 * texinfo: bap_sub_polynom_mint_hp
 * Assign @math{A - B} to @var{R}.
 */

BAP_DLL void
bap_sub_polynom_mint_hp (
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A,
    struct bap_polynom_mint_hp *B)
{
  struct bap_creator_mint_hp crea;
  struct bap_itermon_mint_hp iterA, iterB;
  struct bap_polynom_mint_hp *P;
  enum ba0_compare_code code;
  struct bav_term TA, TB;
  ba0_mint_hp_t bunk;
  bool outA, outB;
  struct ba0_mark M;

  bap__check_compatible_mint_hp (A, B);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&TA);
  bav_init_term (&TB);
  bav_set_term (&TA, &A->total_rank);
  bav_set_term (&TB, &B->total_rank);
  bav_lcm_term (&TA, &TA, &TB);

  P = bap_new_polynom_mint_hp ();
  bap_begin_creator_mint_hp (&crea, P, &TA, bap_approx_total_rank,
      BA0_MAX (bap_nbmon_polynom_mint_hp (A), bap_nbmon_polynom_mint_hp (B)));

  bap_begin_itermon_mint_hp (&iterA, A);
  bap_begin_itermon_mint_hp (&iterB, B);
  ba0_mint_hp_init (bunk);
  outA = bap_outof_itermon_mint_hp (&iterA);
  outB = bap_outof_itermon_mint_hp (&iterB);
  if (!outA)
    bap_term_itermon_mint_hp (&TA, &iterA);
  if (!outB)
    bap_term_itermon_mint_hp (&TB, &iterB);
  while (!outA && !outB)
    {
      code = bav_compare_term (&TA, &TB);
      switch (code)
        {
        case ba0_lt:
          bap_write_neg_creator_mint_hp (&crea, &TB,
              *bap_coeff_itermon_mint_hp (&iterB));
          bap_next_itermon_mint_hp (&iterB);
          outB = bap_outof_itermon_mint_hp (&iterB);
          if (!outB)
            bap_term_itermon_mint_hp (&TB, &iterB);
          break;
        case ba0_gt:
          bap_write_creator_mint_hp (&crea, &TA,
              *bap_coeff_itermon_mint_hp (&iterA));
          bap_next_itermon_mint_hp (&iterA);
          outA = bap_outof_itermon_mint_hp (&iterA);
          if (!outA)
            bap_term_itermon_mint_hp (&TA, &iterA);
          break;
        default:
          ba0_mint_hp_sub (bunk, *bap_coeff_itermon_mint_hp (&iterA),
              *bap_coeff_itermon_mint_hp (&iterB));
          bap_write_creator_mint_hp (&crea, &TA, bunk);
          bap_next_itermon_mint_hp (&iterB);
          bap_next_itermon_mint_hp (&iterA);
          outB = bap_outof_itermon_mint_hp (&iterB);
          outA = bap_outof_itermon_mint_hp (&iterA);
          if (!outB)
            bap_term_itermon_mint_hp (&TB, &iterB);
          if (!outA)
            bap_term_itermon_mint_hp (&TA, &iterA);
        }
    }
  while (!outA)
    {
      bap_write_creator_mint_hp (&crea, &TA, *bap_coeff_itermon_mint_hp (&iterA));
      bap_next_itermon_mint_hp (&iterA);
      outA = bap_outof_itermon_mint_hp (&iterA);
      if (!outA)
        bap_term_itermon_mint_hp (&TA, &iterA);
    }
  while (!outB)
    {
      bap_write_neg_creator_mint_hp (&crea, &TB,
          *bap_coeff_itermon_mint_hp (&iterB));
      bap_next_itermon_mint_hp (&iterB);
      outB = bap_outof_itermon_mint_hp (&iterB);
      if (!outB)
        bap_term_itermon_mint_hp (&TB, &iterB);
    }
  bap_close_creator_mint_hp (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mint_hp (R, P);
  ba0_restore (&M);
}

/*
 * R = A - q * TQ * B
 */

/*
 * texinfo: bap_submulmon_polynom_mint_hp
 * Assign @math{A - q\,@emph{TQ}\,B} to @var{R}.
 */

BAP_DLL void
bap_submulmon_polynom_mint_hp (
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A,
    struct bap_polynom_mint_hp *B,
    struct bav_term *TQ,
    ba0_mint_hp_t q)
{
  struct bap_creator_mint_hp crea;
  struct bap_itermon_mint_hp iterA, iterB;
  struct bap_polynom_mint_hp *P;
  enum ba0_compare_code code;
  struct bav_term TA, TB;
  ba0_mint_hp_t cB, bunk;
  bool outA, outB;
  struct ba0_mark M;

  bap__check_compatible_mint_hp (A, B);
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

  P = bap_new_polynom_mint_hp ();
  bap_begin_creator_mint_hp (&crea, P, &TA, bap_approx_total_rank,
      BA0_MAX (bap_nbmon_polynom_mint_hp (A), bap_nbmon_polynom_mint_hp (B)));

  bap_begin_itermon_mint_hp (&iterA, A);
  bap_begin_itermon_mint_hp (&iterB, B);
  ba0_mint_hp_init (bunk);
  ba0_mint_hp_init (cB);
  outA = bap_outof_itermon_mint_hp (&iterA);
  outB = bap_outof_itermon_mint_hp (&iterB);
  if (!outA)
    bap_term_itermon_mint_hp (&TA, &iterA);
  if (!outB)
    {
      bap_term_itermon_mint_hp (&TB, &iterB);
      bav_mul_term (&TB, &TB, TQ);
      ba0_mint_hp_mul (cB, *bap_coeff_itermon_mint_hp (&iterB), q);
    }
  while (!outA && !outB)
    {
      code = bav_compare_term (&TA, &TB);
      switch (code)
        {
        case ba0_lt:
          bap_write_neg_creator_mint_hp (&crea, &TB, cB);
          bap_next_itermon_mint_hp (&iterB);
          outB = bap_outof_itermon_mint_hp (&iterB);
          if (!outB)
            {
              bap_term_itermon_mint_hp (&TB, &iterB);
              bav_mul_term (&TB, &TB, TQ);
              ba0_mint_hp_mul (cB, *bap_coeff_itermon_mint_hp (&iterB), q);
            }
          break;
        case ba0_gt:
          bap_write_creator_mint_hp (&crea, &TA,
              *bap_coeff_itermon_mint_hp (&iterA));
          bap_next_itermon_mint_hp (&iterA);
          outA = bap_outof_itermon_mint_hp (&iterA);
          if (!outA)
            bap_term_itermon_mint_hp (&TA, &iterA);
          break;
        default:
          ba0_mint_hp_sub (bunk, *bap_coeff_itermon_mint_hp (&iterA), cB);
          bap_write_creator_mint_hp (&crea, &TA, bunk);
          bap_next_itermon_mint_hp (&iterB);
          bap_next_itermon_mint_hp (&iterA);
          outB = bap_outof_itermon_mint_hp (&iterB);
          outA = bap_outof_itermon_mint_hp (&iterA);
          if (!outB)
            {
              bap_term_itermon_mint_hp (&TB, &iterB);
              bav_mul_term (&TB, &TB, TQ);
              ba0_mint_hp_mul (cB, *bap_coeff_itermon_mint_hp (&iterB), q);
            }
          if (!outA)
            bap_term_itermon_mint_hp (&TA, &iterA);
        }
    }
  while (!outA)
    {
      bap_write_creator_mint_hp (&crea, &TA, *bap_coeff_itermon_mint_hp (&iterA));
      bap_next_itermon_mint_hp (&iterA);
      outA = bap_outof_itermon_mint_hp (&iterA);
      if (!outA)
        bap_term_itermon_mint_hp (&TA, &iterA);
    }
  while (!outB)
    {
      bap_write_neg_creator_mint_hp (&crea, &TB, cB);
      bap_next_itermon_mint_hp (&iterB);
      outB = bap_outof_itermon_mint_hp (&iterB);
      if (!outB)
        {
          bap_term_itermon_mint_hp (&TB, &iterB);
          bav_mul_term (&TB, &TB, TQ);
          ba0_mint_hp_mul (cB, *bap_coeff_itermon_mint_hp (&iterB), q);
        }
    }

  bap_close_creator_mint_hp (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mint_hp (R, P);
  ba0_restore (&M);
}

/*
 * R = cA * A + cB * B
 */

/*
 * texinfo: bap_comblin_polynom_mint_hp
 * Assign the linear combination @math{@emph{cA}\,A + @emph{cB}\,B}
 * to @var{R}.
 */

BAP_DLL void
bap_comblin_polynom_mint_hp (
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A,
    ba0_int_p cA,
    struct bap_polynom_mint_hp *B,
    ba0_int_p cB)
{
  struct bap_creator_mint_hp crea;
  struct bap_itermon_mint_hp iterA, iterB;
  struct bap_polynom_mint_hp *P;
  enum ba0_compare_code code;
  struct bav_term TA, TB;
  ba0_mint_hp_t bunk, bink;
  bool outA, outB;
  struct ba0_mark M;

  bap__check_compatible_mint_hp (A, B);
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

  P = bap_new_polynom_mint_hp ();
  bap_begin_creator_mint_hp (&crea, P, &TA, bap_approx_total_rank,
      BA0_MAX (bap_nbmon_polynom_mint_hp (A), bap_nbmon_polynom_mint_hp (B)));

  bap_begin_itermon_mint_hp (&iterA, A);
  bap_begin_itermon_mint_hp (&iterB, B);
  ba0_mint_hp_init (bunk);
  ba0_mint_hp_init (bink);
  outA = bap_outof_itermon_mint_hp (&iterA);
  outB = bap_outof_itermon_mint_hp (&iterB);
  if (!outA)
    bap_term_itermon_mint_hp (&TA, &iterA);
  if (!outB)
    bap_term_itermon_mint_hp (&TB, &iterB);
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
          ba0_mint_hp_mul_si (bunk, *bap_coeff_itermon_mint_hp (&iterB), (long) cB);
          bap_write_creator_mint_hp (&crea, &TB, bunk);
          bap_next_itermon_mint_hp (&iterB);
          outB = bap_outof_itermon_mint_hp (&iterB);
          if (!outB)
            bap_term_itermon_mint_hp (&TB, &iterB);
          break;
        case ba0_gt:
/*
 * Specific cast.
 * GMP function expect long which is 32 bits instead of 64 on Windows 64.
 */
          ba0_mint_hp_mul_si (bunk, *bap_coeff_itermon_mint_hp (&iterA), (long) cA);
          bap_write_creator_mint_hp (&crea, &TA, bunk);
          bap_next_itermon_mint_hp (&iterA);
          outA = bap_outof_itermon_mint_hp (&iterA);
          if (!outA)
            bap_term_itermon_mint_hp (&TA, &iterA);
          break;
        default:
/*
 * Specific cast.
 * GMP function expect long which is 32 bits instead of 64 on Windows 64.
 */
          ba0_mint_hp_mul_si (bunk, *bap_coeff_itermon_mint_hp (&iterA), (long) cA);
          ba0_mint_hp_mul_si (bink, *bap_coeff_itermon_mint_hp (&iterB), (long) cB);
          ba0_mint_hp_add (bunk, bunk, bink);
          bap_write_creator_mint_hp (&crea, &TA, bunk);
          bap_next_itermon_mint_hp (&iterB);
          bap_next_itermon_mint_hp (&iterA);
          outB = bap_outof_itermon_mint_hp (&iterB);
          outA = bap_outof_itermon_mint_hp (&iterA);
          if (!outB)
            bap_term_itermon_mint_hp (&TB, &iterB);
          if (!outA)
            bap_term_itermon_mint_hp (&TA, &iterA);
        }
    }
  while (!outA)
/*
 * Specific cast.
 * GMP function expect long which is 32 bits instead of 64 on Windows 64.
 */
    {
      ba0_mint_hp_mul_si (bunk, *bap_coeff_itermon_mint_hp (&iterA), (long) cA);
      bap_write_creator_mint_hp (&crea, &TA, bunk);
      bap_next_itermon_mint_hp (&iterA);
      outA = bap_outof_itermon_mint_hp (&iterA);
      if (!outA)
        bap_term_itermon_mint_hp (&TA, &iterA);
    }
  while (!outB)
/*
 * Specific cast.
 * GMP function expect long which is 32 bits instead of 64 on Windows 64.
 */
    {
      ba0_mint_hp_mul_si (bunk, *bap_coeff_itermon_mint_hp (&iterB), (long) cB);
      bap_write_creator_mint_hp (&crea, &TB, bunk);
      bap_next_itermon_mint_hp (&iterB);
      outB = bap_outof_itermon_mint_hp (&iterB);
      if (!outB)
        bap_term_itermon_mint_hp (&TB, &iterB);
    }
  bap_close_creator_mint_hp (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mint_hp (R, P);
  ba0_restore (&M);
}

/*
 * R = A * rg + B
 */

/*
 * texinfo: bap_addmulrk_polynom_mint_hp
 * Assign @math{A\,@emph{rg} + B} to @var{R}.
 */

BAP_DLL void
bap_addmulrk_polynom_mint_hp (
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A,
    struct bav_rank *rg,
    struct bap_polynom_mint_hp *B)
{
  struct bap_creator_mint_hp crea;
  struct bap_itermon_mint_hp iterA, iterB;
  struct bap_polynom_mint_hp *P;
  enum ba0_compare_code code;
  struct bav_term TA, TB;
  ba0_mint_hp_t bunk;
  bool outA, outB;
  struct ba0_mark M;

  bap__check_compatible_mint_hp (A, B);
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

  P = bap_new_polynom_mint_hp ();
  bap_begin_creator_mint_hp (&crea, P, &TA, bap_approx_total_rank,
      BA0_MAX (bap_nbmon_polynom_mint_hp (A), bap_nbmon_polynom_mint_hp (B)));

  bap_begin_itermon_mint_hp (&iterA, A);
  bap_begin_itermon_mint_hp (&iterB, B);
  ba0_mint_hp_init (bunk);
  outA = bap_outof_itermon_mint_hp (&iterA);
  outB = bap_outof_itermon_mint_hp (&iterB);
  if (!outA)
    {
      bap_term_itermon_mint_hp (&TA, &iterA);
      bav_mul_term_rank (&TA, &TA, rg);
    }
  if (!outB)
    bap_term_itermon_mint_hp (&TB, &iterB);
  while (!outA && !outB)
    {
      code = bav_compare_term (&TA, &TB);
      switch (code)
        {
        case ba0_lt:
          bap_write_creator_mint_hp (&crea, &TB,
              *bap_coeff_itermon_mint_hp (&iterB));
          bap_next_itermon_mint_hp (&iterB);
          outB = bap_outof_itermon_mint_hp (&iterB);
          if (!outB)
            bap_term_itermon_mint_hp (&TB, &iterB);
          break;
        case ba0_gt:
          bap_write_creator_mint_hp (&crea, &TA,
              *bap_coeff_itermon_mint_hp (&iterA));
          bap_next_itermon_mint_hp (&iterA);
          outA = bap_outof_itermon_mint_hp (&iterA);
          if (!outA)
            {
              bap_term_itermon_mint_hp (&TA, &iterA);
              bav_mul_term_rank (&TA, &TA, rg);
            }
          break;
        default:
          ba0_mint_hp_add (bunk, *bap_coeff_itermon_mint_hp (&iterA),
              *bap_coeff_itermon_mint_hp (&iterB));
          bap_write_creator_mint_hp (&crea, &TA, bunk);
          bap_next_itermon_mint_hp (&iterB);
          bap_next_itermon_mint_hp (&iterA);
          outB = bap_outof_itermon_mint_hp (&iterB);
          outA = bap_outof_itermon_mint_hp (&iterA);
          if (!outB)
            bap_term_itermon_mint_hp (&TB, &iterB);
          if (!outA)
            {
              bap_term_itermon_mint_hp (&TA, &iterA);
              bav_mul_term_rank (&TA, &TA, rg);
            }
        }
    }
  while (!outA)
    {
      bap_write_creator_mint_hp (&crea, &TA, *bap_coeff_itermon_mint_hp (&iterA));
      bap_next_itermon_mint_hp (&iterA);
      outA = bap_outof_itermon_mint_hp (&iterA);
      if (!outA)
        {
          bap_term_itermon_mint_hp (&TA, &iterA);
          bav_mul_term_rank (&TA, &TA, rg);
        }
    }
  while (!outB)
    {
      bap_write_creator_mint_hp (&crea, &TB, *bap_coeff_itermon_mint_hp (&iterB));
      bap_next_itermon_mint_hp (&iterB);
      outB = bap_outof_itermon_mint_hp (&iterB);
      if (!outB)
        bap_term_itermon_mint_hp (&TB, &iterB);
    }
  bap_close_creator_mint_hp (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mint_hp (R, P);
  ba0_restore (&M);
}

/*
 * R = A * rg - B
 */

/*
 * texinfo: bap_submulrk_polynom_mint_hp
 * Assign @math{A\,@emph{rg} - B} to @var{R}.
 */

BAP_DLL void
bap_submulrk_polynom_mint_hp (
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A,
    struct bav_rank *rg,
    struct bap_polynom_mint_hp *B)
{
  struct bap_creator_mint_hp crea;
  struct bap_itermon_mint_hp iterA, iterB;
  struct bap_polynom_mint_hp *P;
  enum ba0_compare_code code;
  struct bav_term TA, TB;
  ba0_mint_hp_t bunk;
  bool outA, outB;
  struct ba0_mark M;

  bap__check_compatible_mint_hp (A, B);
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

  P = bap_new_polynom_mint_hp ();
  bap_begin_creator_mint_hp (&crea, P, &TA, bap_approx_total_rank,
      BA0_MAX (bap_nbmon_polynom_mint_hp (A), bap_nbmon_polynom_mint_hp (B)));

  bap_begin_itermon_mint_hp (&iterA, A);
  bap_begin_itermon_mint_hp (&iterB, B);
  ba0_mint_hp_init (bunk);
  outA = bap_outof_itermon_mint_hp (&iterA);
  outB = bap_outof_itermon_mint_hp (&iterB);
  if (!outA)
    {
      bap_term_itermon_mint_hp (&TA, &iterA);
      bav_mul_term_rank (&TA, &TA, rg);
    }
  if (!outB)
    bap_term_itermon_mint_hp (&TB, &iterB);
  while (!outA && !outB)
    {
      code = bav_compare_term (&TA, &TB);
      switch (code)
        {
        case ba0_lt:
          bap_write_neg_creator_mint_hp (&crea, &TB,
              *bap_coeff_itermon_mint_hp (&iterB));
          bap_next_itermon_mint_hp (&iterB);
          outB = bap_outof_itermon_mint_hp (&iterB);
          if (!outB)
            bap_term_itermon_mint_hp (&TB, &iterB);
          break;
        case ba0_gt:
          bap_write_creator_mint_hp (&crea, &TA,
              *bap_coeff_itermon_mint_hp (&iterA));
          bap_next_itermon_mint_hp (&iterA);
          outA = bap_outof_itermon_mint_hp (&iterA);
          if (!outA)
            {
              bap_term_itermon_mint_hp (&TA, &iterA);
              bav_mul_term_rank (&TA, &TA, rg);
            }
          break;
        default:
          ba0_mint_hp_sub (bunk, *bap_coeff_itermon_mint_hp (&iterA),
              *bap_coeff_itermon_mint_hp (&iterB));
          bap_write_creator_mint_hp (&crea, &TA, bunk);
          bap_next_itermon_mint_hp (&iterB);
          bap_next_itermon_mint_hp (&iterA);
          outB = bap_outof_itermon_mint_hp (&iterB);
          outA = bap_outof_itermon_mint_hp (&iterA);
          if (!outB)
            bap_term_itermon_mint_hp (&TB, &iterB);
          if (!outA)
            {
              bap_term_itermon_mint_hp (&TA, &iterA);
              bav_mul_term_rank (&TA, &TA, rg);
            }
        }
    }
  while (!outA)
    {
      bap_write_creator_mint_hp (&crea, &TA, *bap_coeff_itermon_mint_hp (&iterA));
      bap_next_itermon_mint_hp (&iterA);
      outA = bap_outof_itermon_mint_hp (&iterA);
      if (!outA)
        {
          bap_term_itermon_mint_hp (&TA, &iterA);
          bav_mul_term_rank (&TA, &TA, rg);
        }
    }
  while (!outB)
    {
      bap_write_neg_creator_mint_hp (&crea, &TB,
          *bap_coeff_itermon_mint_hp (&iterB));
      bap_next_itermon_mint_hp (&iterB);
      outB = bap_outof_itermon_mint_hp (&iterB);
      if (!outB)
        bap_term_itermon_mint_hp (&TB, &iterB);
    }
  bap_close_creator_mint_hp (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mint_hp (R, P);
  ba0_restore (&M);
}


#undef BAD_FLAG_mint_hp
