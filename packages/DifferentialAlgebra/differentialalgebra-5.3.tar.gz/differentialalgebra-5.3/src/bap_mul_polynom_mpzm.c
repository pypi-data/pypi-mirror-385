#include "bap_polynom_mpzm.h"
#include "bap_creator_mpzm.h"
#include "bap_itermon_mpzm.h"
#include "bap_itercoeff_mpzm.h"
#include "bap_add_polynom_mpzm.h"
#include "bap_mul_polynom_mpzm.h"
#include "bap__check_mpzm.h"
#include "bap_geobucket_mpzm.h"

#define BAD_FLAG_mpzm

/*
 * texinfo: bap_neg_polynom_mpzm
 * Assign @math{- A} to @var{R}.
 */

BAP_DLL void
bap_neg_polynom_mpzm (
    struct bap_polynom_mpzm *R,
    struct bap_polynom_mpzm *A)
{
  struct bap_itermon_mpzm iter;
  struct bap_creator_mpzm crea;
  struct bap_polynom_mpzm S;
  struct bav_term T;
  ba0_int_p nbmon;
  struct ba0_mark M;

  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (bap_is_zero_polynom_mpzm (A))
    bap_set_polynom_zero_mpzm (R);
  else if (R == A)
    {
      bap_begin_itermon_mpzm (&iter, A);
      while (!bap_outof_itermon_mpzm (&iter))
        {
          ba0_mpzm_neg (*bap_coeff_itermon_mpzm (&iter),
              *bap_coeff_itermon_mpzm (&iter));
          bap_next_itermon_mpzm (&iter);
        }
    }
  else
    {
      bap_begin_itermon_mpzm (&iter, A);

      nbmon = bap_nbmon_polynom_mpzm (A) - R->clot->alloc;
      nbmon = nbmon > 0 ? nbmon : 0;

      if (bap_are_disjoint_polynom_mpzm (R, A))
        {
          bap_begin_creator_mpzm (&crea, R, &A->total_rank,
              bap_exact_total_rank, nbmon);

          if (bap_is_write_allable_creator_mpzm (&crea, A))
            bap_write_neg_all_creator_mpzm (&crea, A);
          else
            {
              ba0_push_another_stack ();
              ba0_record (&M);
              bav_init_term (&T);
              bav_realloc_term (&T, A->total_rank.size);
              ba0_pull_stack ();

              while (!bap_outof_itermon_mpzm (&iter))
                {
                  bap_term_itermon_mpzm (&T, &iter);
                  bap_write_neg_creator_mpzm (&crea, &T,
                      *bap_coeff_itermon_mpzm (&iter));
                  bap_next_itermon_mpzm (&iter);
                }

              ba0_restore (&M);
            }
          bap_close_creator_mpzm (&crea);
        }
      else
        {
          ba0_push_another_stack ();
          ba0_record (&M);
          bav_init_term (&T);
          bav_realloc_term (&T, A->total_rank.size);

          bap_init_polynom_mpzm (&S);

          bap_begin_creator_mpzm (&crea, &S, &A->total_rank,
              bap_exact_total_rank, bap_nbmon_polynom_mpzm (A));
          while (!bap_outof_itermon_mpzm (&iter))
            {
              bap_term_itermon_mpzm (&T, &iter);
              bap_write_neg_creator_mpzm (&crea, &T,
                  *bap_coeff_itermon_mpzm (&iter));
              bap_next_itermon_mpzm (&iter);
            }

          bap_close_creator_mpzm (&crea);
          ba0_pull_stack ();

          bap_set_polynom_mpzm (R, &S);
          ba0_restore (&M);
        }
    }
}

/*
 * texinfo: bap_mul_polynom_numeric_mpzm
 * Assign @math{c\,A} to @var{R}.
 */

BAP_DLL void
bap_mul_polynom_numeric_mpzm (
    struct bap_polynom_mpzm *R,
    struct bap_polynom_mpzm *A,
    ba0_mpzm_t c)
{
  struct bap_itermon_mpzm iter;
  struct bap_creator_mpzm crea;
  struct bap_polynom_mpzm S;
  struct bav_term T;
  ba0_mpzm_t prod, *lc;
  enum bap_typeof_total_rank type;
  ba0_int_p nbmon;
  struct ba0_mark M;

  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (ba0_mpzm_is_zero (c))
    bap_set_polynom_zero_mpzm (R);
  else if (ba0_mpzm_is_one (c))
    {
      if (R != A)
        bap_set_polynom_mpzm (R, A);
    }
  else if (R == A && ba0_domain_mpzm ())
    {
      bap_begin_itermon_mpzm (&iter, A);
      while (!bap_outof_itermon_mpzm (&iter))
        {
          lc = bap_coeff_itermon_mpzm (&iter);
          ba0_mpzm_mul (*lc, *lc, c);
          if (ba0_mpzm_is_zero (*lc))
            BA0_RAISE_EXCEPTION (BA0_ERRALG);
          bap_next_itermon_mpzm (&iter);
        }
    }
  else
    {
      bap_begin_itermon_mpzm (&iter, A);
      nbmon = bap_nbmon_polynom_mpzm (A) - R->clot->alloc;
      nbmon = nbmon > 0 ? nbmon : 0;

      type = ba0_domain_mpzm ()? bap_exact_total_rank : bap_approx_total_rank;

      if (bap_are_disjoint_polynom_mpzm (R, A))
        {
          bap_begin_creator_mpzm (&crea, R, &A->total_rank, type, nbmon);

          if (bap_is_write_allable_creator_mpzm (&crea, A)
              && ba0_domain_mpzm ())
            bap_write_mul_all_creator_mpzm (&crea, A, c);
          else
            {
              ba0_push_another_stack ();
              ba0_record (&M);

              bav_init_term (&T);
              bav_realloc_term (&T, A->total_rank.size);

              ba0_mpzm_init (prod);

              while (!bap_outof_itermon_mpzm (&iter))
                {
                  lc = bap_coeff_itermon_mpzm (&iter);
                  ba0_mpzm_mul (prod, c, *lc);
                  if (!ba0_mpzm_is_zero (prod))
                    {
                      bap_term_itermon_mpzm (&T, &iter);
                      ba0_pull_stack ();
                      bap_write_creator_mpzm (&crea, &T, prod);
                      ba0_push_another_stack ();
                    }
                  else if (ba0_domain_mpzm ())
                    BA0_RAISE_EXCEPTION (BA0_ERRALG);
                  bap_next_itermon_mpzm (&iter);
                }

              ba0_pull_stack ();
              ba0_restore (&M);
            }

          bap_close_creator_mpzm (&crea);
        }
      else
        {
          ba0_push_another_stack ();
          ba0_record (&M);

          bap_init_polynom_mpzm (&S);

          bav_init_term (&T);
          bav_realloc_term (&T, A->total_rank.size);

          ba0_mpzm_init (prod);

          bap_begin_creator_mpzm (&crea, &S, &A->total_rank, type,
              bap_nbmon_polynom_mpzm (A));

          while (!bap_outof_itermon_mpzm (&iter))
            {
              lc = bap_coeff_itermon_mpzm (&iter);
              ba0_mpzm_mul (prod, c, *lc);
              if (!ba0_mpzm_is_zero (prod))
                {
                  bap_term_itermon_mpzm (&T, &iter);
                  bap_write_creator_mpzm (&crea, &T, prod);
                }
              else if (ba0_domain_mpzm ())
                BA0_RAISE_EXCEPTION (BA0_ERRALG);
              bap_next_itermon_mpzm (&iter);
            }

          bap_close_creator_mpzm (&crea);

          ba0_pull_stack ();
          bap_set_polynom_mpzm (R, &S);
          ba0_restore (&M);
        }
    }
}

/*
 * texinfo: bap_mul_polynom_value_int_p_mpzm
 * Assign @math{A \, (x - \alpha)} to @var{R}, where @math{(x,\, \alpha)}
 * denotes @var{val}.
 */

BAP_DLL void
bap_mul_polynom_value_int_p_mpzm (
    struct bap_polynom_mpzm *R,
    struct bap_polynom_mpzm *A,
    struct bav_value_int_p *val)
{
  struct bav_term T;
  struct bav_rank rg;
  ba0_mpzm_t c;
  struct bap_creator_mpzm crea;
  struct bap_polynom_mpzm *P;
  struct ba0_mark M;

  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&T);
  rg.var = val->var;
  rg.deg = 1;
  bav_set_term_rank (&T, &rg);
  P = bap_new_polynom_mpzm ();
  bap_begin_creator_mpzm (&crea, P, &T, bap_exact_total_rank, 2);
  ba0_mpzm_init_set_ui (c, 1);
  bap_write_creator_mpzm (&crea, &T, c);
  bav_set_term_one (&T);
  ba0_mpzm_set_si (c, val->value);
  bap_write_neg_creator_mpzm (&crea, &T, c);
  bap_close_creator_mpzm (&crea);
  ba0_pull_stack ();
  bap_mul_polynom_mpzm (R, A, P);
  ba0_restore (&M);
}

/*
 * texinfo: bap_mul_polynom_term_mpzm
 * Assign @math{A \, T} to @var{R}.
 */

BAP_DLL void
bap_mul_polynom_term_mpzm (
    struct bap_polynom_mpzm *R,
    struct bap_polynom_mpzm *A,
    struct bav_term *T)
{
  struct bap_itermon_mpzm iter;
  struct bap_creator_mpzm crea;
  struct bap_polynom_mpzm *P;
  struct bav_term U;
  struct ba0_mark M;

  bap__check_ordering_mpzm (A);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (bav_is_one_term (T))
    {
      if (R != A)
        bap_set_polynom_mpzm (R, A);
      return;
    }

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&U);
  bav_set_term (&U, &A->total_rank);
  bav_mul_term (&U, &U, T);
  bap_begin_itermon_mpzm (&iter, A);
  P = bap_new_polynom_mpzm ();
  bap_begin_creator_mpzm (&crea, P, &U, bap_exact_total_rank,
      bap_nbmon_polynom_mpzm (A));
  while (!bap_outof_itermon_mpzm (&iter))
    {
      bap_term_itermon_mpzm (&U, &iter);
      bav_mul_term (&U, &U, T);
      bap_write_creator_mpzm (&crea, &U, *bap_coeff_itermon_mpzm (&iter));
      bap_next_itermon_mpzm (&iter);
    }
  bap_close_creator_mpzm (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mpzm (R, P);
  ba0_restore (&M);
}

/*
 * texinfo: bap_mul_polynom_variable_mpzm
 * Assign @math{A \, v^d} to @var{R}.
 */

BAP_DLL void
bap_mul_polynom_variable_mpzm (
    struct bap_polynom_mpzm *R,
    struct bap_polynom_mpzm *A,
    struct bav_variable *v,
    bav_Idegree d)
{
  struct bav_term term;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  bav_init_term (&term);
  bav_set_term_variable (&term, v, d);
  ba0_pull_stack ();
  bap_mul_polynom_term_mpzm (R, A, &term);
  ba0_restore (&M);
}

/*
 * texinfo: bap_mul_polynom_monom_mpzm
 * Assign @math{A \, c\, T} to @var{R}.
 */

BAP_DLL void
bap_mul_polynom_monom_mpzm (
    struct bap_polynom_mpzm *R,
    struct bap_polynom_mpzm *A,
    ba0_mpzm_t c,
    struct bav_term *T)
{
  struct bap_itermon_mpzm iter;
  struct bap_creator_mpzm crea;
  struct bap_polynom_mpzm *P;
  struct bav_term U;
  ba0_mpzm_t d;
  struct ba0_mark M;

  bap__check_ordering_mpzm (A);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (ba0_mpzm_is_zero (c))
    {
      bap_set_polynom_zero_mpzm (R);
      return;
    }
  else if (ba0_mpzm_is_one (c))
    {
      bap_mul_polynom_term_mpzm (R, A, T);
      return;
    }

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&U);
  bav_set_term (&U, &A->total_rank);
  bav_mul_term (&U, &U, T);
  bap_begin_itermon_mpzm (&iter, A);

  P = bap_new_polynom_mpzm ();
#if defined (BAD_FLAG_mpz) || defined (BAD_FLAG_mpq)
  bap_begin_creator_mpzm (&crea, P, &U, bap_exact_total_rank,
      bap_nbmon_polynom_mpzm (A));
#else
  bap_begin_creator_mpzm (&crea, P, &U, bap_approx_total_rank,
      bap_nbmon_polynom_mpzm (A));
#endif

  ba0_mpzm_init (d);

  while (!bap_outof_itermon_mpzm (&iter))
    {
      bap_term_itermon_mpzm (&U, &iter);
      bav_mul_term (&U, &U, T);
      ba0_mpzm_mul (d, c, *bap_coeff_itermon_mpzm (&iter));
      bap_write_creator_mpzm (&crea, &U, d);
      bap_next_itermon_mpzm (&iter);
    }
  bap_close_creator_mpzm (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mpzm (R, P);
  ba0_restore (&M);
}

/*****************************************************************************
 MULTIPLICATION
 *****************************************************************************/

static void
bap_mul_elem_polynom_mpzm (
    struct bap_polynom_mpzm *R,
    struct bap_polynom_mpzm *A,
    struct bap_polynom_mpzm *B)
{
  struct bap_creator_mpzm crea;
  struct bap_itermon_mpzm iterA, iterB;
  struct bap_polynom_mpzm R1;
  struct bap_geobucket_mpzm geo;
  ba0_mpzm_t cz, *ca, *cb;
  struct bav_term TA, TB, TTB;
  enum bap_typeof_total_rank type;
  struct ba0_mark M;

  if (bap_nbmon_polynom_mpzm (A) > bap_nbmon_polynom_mpzm (B))
    BA0_SWAP (struct bap_polynom_mpzm *,
        A,
        B);

  type = ba0_domain_mpzm ()? bap_exact_total_rank : bap_approx_total_rank;

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_mpzm_init (cz);

  bav_init_term (&TTB);
  bav_set_term (&TTB, &B->total_rank);

  bav_init_term (&TA);
  bav_init_term (&TB);

  bap_init_geobucket_mpzm (&geo);
  bap_init_polynom_mpzm (&R1);

  bap_begin_itermon_mpzm (&iterA, A);
  while (!bap_outof_itermon_mpzm (&iterA))
    {
      ca = bap_coeff_itermon_mpzm (&iterA);
      bap_term_itermon_mpzm (&TA, &iterA);
      bav_mul_term (&TB, &TTB, &TA);
      bap_begin_creator_mpzm (&crea, &R1, &TB, type,
          bap_nbmon_polynom_mpzm (B));
      bap_begin_itermon_mpzm (&iterB, B);
      while (!bap_outof_itermon_mpzm (&iterB))
        {
          cb = bap_coeff_itermon_mpzm (&iterB);
          ba0_mpzm_mul (cz, *ca, *cb);
          bap_term_itermon_mpzm (&TB, &iterB);
          bav_mul_term (&TB, &TB, &TA);
          bap_write_creator_mpzm (&crea, &TB, cz);
          bap_next_itermon_mpzm (&iterB);
        }
      bap_close_creator_mpzm (&crea);
      bap_add_geobucket_mpzm (&geo, &R1);
      bap_next_itermon_mpzm (&iterA);
    }
  ba0_pull_stack ();
  bap_set_polynom_geobucket_mpzm (R, &geo);
  ba0_restore (&M);
}

/*
 * texinfo: bap_mul_polynom_mpzm
 * Assign @math{A\,B} to @var{R}.
 */

BAP_DLL void
bap_mul_polynom_mpzm (
    struct bap_polynom_mpzm *R,
    struct bap_polynom_mpzm *A,
    struct bap_polynom_mpzm *B)
{
  struct bap_itercoeff_mpzm iterA, iterB;
  struct bap_itermon_mpzm iter;
  struct bap_creator_mpzm crea;
  struct bap_polynom_mpzm C, CA, CB;
  struct bap_polynom_mpzm *AA, *BB, *P;
  struct bav_term T, U, TA, TB;
  struct bav_variable *xa, *xb;
  bav_Iordering r;
  ba0_int_p i;
  struct ba0_mark M;

  bap__check_compatible_mpzm (A, B);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (bap_is_numeric_polynom_mpzm (B))
    BA0_SWAP (struct bap_polynom_mpzm *,
        A,
        B);
/*
 * If any of the two polynomials is numeric then A is so.
 */
  if (bap_is_numeric_polynom_mpzm (A))
    {
      if (bap_is_zero_polynom_mpzm (A) || bap_is_zero_polynom_mpzm (B))
        bap_set_polynom_zero_mpzm (R);
      else
        {
          ba0_mpzm_t c;            /* else bug when A == R */
          ba0_push_another_stack ();
          ba0_record (&M);
          ba0_mpzm_init_set (c, *bap_numeric_initial_polynom_mpzm (A));
          ba0_pull_stack ();
          bap_mul_polynom_numeric_mpzm (R, B, c);
          ba0_restore (&M);
        }
      return;
    }

  if (bap_nbmon_polynom_mpzm (B) == 1)
    {
      BA0_SWAP (struct bap_polynom_mpzm *,
          A,
          B);
    }
/*
 * If any of the two polynomials is a monomial then A is so.
 */
  if (bap_nbmon_polynom_mpzm (A) == 1)
    {
      ba0_mpzm_t c;
      ba0_push_another_stack ();
      ba0_record (&M);
      bap_begin_itermon_mpzm (&iter, A);
      bav_init_term (&T);
      bap_term_itermon_mpzm (&T, &iter);
      ba0_mpzm_init_set (c, *bap_coeff_itermon_mpzm (&iter));
      ba0_pull_stack ();
      bap_mul_polynom_monom_mpzm (R, B, c, &T);
      ba0_restore (&M);
      return;
    }
/*
 * Neither A nor B is numeric.
 */
  {
    struct bav_dictionary_variable dict;
    struct bav_tableof_variable vars;
    struct ba0_tableof_int_p common;
    struct bav_variable *v;
    ba0_int_p size, log2_size, j;

    ba0_push_another_stack ();
    ba0_record (&M);

    size = A->total_rank.size + B->total_rank.size;
    log2_size = ba0_log2_int_p (size);
    size <<= 3;
    log2_size += 3;
    bav_init_dictionary_variable (&dict, log2_size);
    ba0_init_table ((struct ba0_table *) &vars);
    ba0_realloc_table ((struct ba0_table *) &vars, size);
    ba0_init_table ((struct ba0_table *) &common);
    ba0_realloc_table ((struct ba0_table *) &common, size);

    for (i = 0; i < A->total_rank.size; i++)
      {
        v = A->total_rank.rg[i].var;
        bav_add_dictionary_variable (&dict, &vars, v, vars.size);
        vars.tab[vars.size] = v;
        vars.size += 1;
        common.tab[common.size] = false;
        common.size += 1;
      }
    for (i = 0; i < B->total_rank.size; i++)
      {
        v = B->total_rank.rg[i].var;
        j = bav_get_dictionary_variable (&dict, &vars, v);
        if (j == BA0_NOT_AN_INDEX)
          {
            bav_add_dictionary_variable (&dict, &vars, v, vars.size);
            vars.tab[vars.size] = v;
            vars.size += 1;
            common.tab[common.size] = false;
            common.size += 1;
          }
        else
          common.tab[j] = true;
      }
/*
 * In the ordering r (to be built below) we want the variables
 *      which are NOT common to A and B to be greater than any other one
 * Moreover, we want
 * xa = the least non common variable of A in the ordering r
 * xb = the least non common variable of B in the ordering r
 */
    r = bav_R_copy_ordering (bav_current_ordering ());
    bav_push_ordering (r);

    xa = BAV_NOT_A_VARIABLE;
    for (i = A->total_rank.size - 1; i >= 0; i--)
      {
        v = A->total_rank.rg[i].var;
        j = bav_get_dictionary_variable (&dict, &vars, v);
        if (j == BA0_NOT_AN_INDEX)
          BA0_RAISE_EXCEPTION (BA0_ERRALG);
        if (common.tab[j] == false)
          {
            if (xa == BAV_NOT_A_VARIABLE)
              xa = v;
            bav_R_set_maximal_variable (v);
          }
      }
    xb = BAV_NOT_A_VARIABLE;
    for (i = B->total_rank.size - 1; i >= 0; i--)
      {
        v = B->total_rank.rg[i].var;
        j = bav_get_dictionary_variable (&dict, &vars, v);
        if (common.tab[j] == false)
          {
            if (xb == BAV_NOT_A_VARIABLE)
              xb = v;
            bav_R_set_maximal_variable (v);
          }
      }
    ba0_pull_stack ();
    ba0_restore (&M);
  }
/*
 * If any of the two polynomials has all its variables common with
 * the other one then so is B
 */
  if (xa == BAV_NOT_A_VARIABLE)
    {
      BA0_SWAP (struct bap_polynom_mpzm *,
          A,
          B);
      BA0_SWAP (struct bav_variable *,
          xa,
          xb);
    }
/*
 * Exit the case of two polynomials over the same set of variables
 */
  if (xa == BAV_NOT_A_VARIABLE)
    {
      bav_pull_ordering ();
      bav_R_free_ordering (r);
      bap_mul_elem_polynom_mpzm (R, A, B);
      return;
    }
/*
 * A depends on at least one variable which is not common with B
 */
  ba0_push_another_stack ();
  ba0_record (&M);

  {
    struct bap_polynom_mpzm *AA0 = bap_new_readonly_polynom_mpzm ();
    bap_sort_polynom_mpzm (AA0, A);
    AA = bap_new_polynom_mpzm ();
    bap_set_polynom_mpzm (AA, AA0);
  }

  bap_begin_itercoeff_mpzm (&iterA, AA, xa);

  if (xb != BAV_NOT_A_VARIABLE)
    {
      struct bap_polynom_mpzm *BB0 = bap_new_readonly_polynom_mpzm ();
      bap_sort_polynom_mpzm (BB0, B);
      BB = bap_new_polynom_mpzm ();
      bap_set_polynom_mpzm (BB, BB0);
    }
  else
    BB = B;

  bap_init_polynom_mpzm (&C);
  bap_init_polynom_mpzm (&CA);
  bap_init_polynom_mpzm (&CB);
  bav_init_term (&T);
  bav_init_term (&TA);
  bav_init_term (&TB);
  bav_init_term (&U);

  bav_mul_term (&T, &AA->total_rank, &BB->total_rank);
  i = BA0_MAX (bap_nbmon_polynom_mpzm (AA), bap_nbmon_polynom_mpzm (BB));
/*
 * Note: the monomials of P will temporarily not be sorted
 */
  P = bap_new_polynom_mpzm ();
#if defined (BAD_FLAG_mpz) || defined (BAD_FLAG_mpq)
  bap_begin_creator_mpzm (&crea, P, &T, bap_exact_total_rank, i);
#else
  bap_begin_creator_mpzm (&crea, P, &T, bap_approx_total_rank, i);
#endif

  while (!bap_outof_itercoeff_mpzm (&iterA))
    {
      bap_coeff_itercoeff_mpzm (&CA, &iterA);
      bap_term_itercoeff_mpzm (&TA, &iterA);
      bap_begin_itercoeff_mpzm (&iterB, BB,
          xb == BAV_NOT_A_VARIABLE ? xa : xb);
      while (!bap_outof_itercoeff_mpzm (&iterB))
        {
          bap_coeff_itercoeff_mpzm (&CB, &iterB);
          bap_term_itercoeff_mpzm (&TB, &iterB);

          bav_mul_term (&T, &TA, &TB);
          bap_mul_elem_polynom_mpzm (&C, &CA, &CB);

          bap_begin_itermon_mpzm (&iter, &C);
          while (!bap_outof_itermon_mpzm (&iter))
            {
              ba0_mpzm_t *c;

              c = bap_coeff_itermon_mpzm (&iter);
              bap_term_itermon_mpzm (&U, &iter);
              bav_mul_term (&U, &U, &T);
              bap_write_creator_mpzm (&crea, &U, *c);
              bap_next_itermon_mpzm (&iter);
            }
          bap_next_itercoeff_mpzm (&iterB);
        }
      bap_next_itercoeff_mpzm (&iterA);
    }
  bap_close_creator_mpzm (&crea);
  bav_pull_ordering ();
/*
 * Now, the monomials get sorted
 */
  bap_physort_polynom_mpzm (P);

  bav_R_free_ordering (r);
  ba0_pull_stack ();

  i = BA0_MAX (bap_nbmon_polynom_mpzm (A), bap_nbmon_polynom_mpzm (B));

  bap_set_polynom_mpzm (R, P);

  ba0_restore (&M);
}

/*
 * texinfo: bap_pow_polynom_mpzm
 * Assign @math{A^d} to @var{R}.
 */

BAP_DLL void
bap_pow_polynom_mpzm (
    struct bap_polynom_mpzm *R,
    struct bap_polynom_mpzm *A,
    bav_Idegree n)
{
  struct bap_polynom_mpzm E, F;
  bav_Idegree p;
  bool E_vaut_un;
  struct ba0_mark M;

  if (n == 0)
    bap_set_polynom_one_mpzm (R);
  else if (n == 1)
    {
      if (R != A)
        bap_set_polynom_mpzm (R, A);
    }
  else
    {
      ba0_push_another_stack ();
      ba0_record (&M);

      if (n % 2 == 1)
        {
          bap_init_polynom_mpzm (&E);
          bap_set_polynom_mpzm (&E, A);
          E_vaut_un = false;
        }
      else
        E_vaut_un = true;

      bap_init_polynom_mpzm (&F);
      bap_mul_polynom_mpzm (&F, A, A);

      for (p = n / 2; p != 1; p /= 2)
        {
          if (p % 2 == 1)
            {
              if (E_vaut_un)
                {
                  bap_init_polynom_mpzm (&E);
                  bap_set_polynom_mpzm (&E, &F);
                  E_vaut_un = false;
                }
              else
                bap_mul_polynom_mpzm (&E, &F, &E);
            }
          bap_mul_polynom_mpzm (&F, &F, &F);
        }
      ba0_pull_stack ();
      if (E_vaut_un)
        bap_set_polynom_mpzm (R, &F);
      else
        bap_mul_polynom_mpzm (R, &E, &F);
      ba0_restore (&M);
    }
}

#undef BAD_FLAG_mpzm
