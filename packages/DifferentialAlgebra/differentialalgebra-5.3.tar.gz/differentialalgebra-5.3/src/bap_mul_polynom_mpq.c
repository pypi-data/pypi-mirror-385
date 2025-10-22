#include "bap_polynom_mpq.h"
#include "bap_creator_mpq.h"
#include "bap_itermon_mpq.h"
#include "bap_itercoeff_mpq.h"
#include "bap_add_polynom_mpq.h"
#include "bap_mul_polynom_mpq.h"
#include "bap__check_mpq.h"
#include "bap_geobucket_mpq.h"

#define BAD_FLAG_mpq

/*
 * texinfo: bap_neg_polynom_mpq
 * Assign @math{- A} to @var{R}.
 */

BAP_DLL void
bap_neg_polynom_mpq (
    struct bap_polynom_mpq *R,
    struct bap_polynom_mpq *A)
{
  struct bap_itermon_mpq iter;
  struct bap_creator_mpq crea;
  struct bap_polynom_mpq S;
  struct bav_term T;
  ba0_int_p nbmon;
  struct ba0_mark M;

  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (bap_is_zero_polynom_mpq (A))
    bap_set_polynom_zero_mpq (R);
  else if (R == A)
    {
      bap_begin_itermon_mpq (&iter, A);
      while (!bap_outof_itermon_mpq (&iter))
        {
          ba0_mpq_neg (*bap_coeff_itermon_mpq (&iter),
              *bap_coeff_itermon_mpq (&iter));
          bap_next_itermon_mpq (&iter);
        }
    }
  else
    {
      bap_begin_itermon_mpq (&iter, A);

      nbmon = bap_nbmon_polynom_mpq (A) - R->clot->alloc;
      nbmon = nbmon > 0 ? nbmon : 0;

      if (bap_are_disjoint_polynom_mpq (R, A))
        {
          bap_begin_creator_mpq (&crea, R, &A->total_rank,
              bap_exact_total_rank, nbmon);

          if (bap_is_write_allable_creator_mpq (&crea, A))
            bap_write_neg_all_creator_mpq (&crea, A);
          else
            {
              ba0_push_another_stack ();
              ba0_record (&M);
              bav_init_term (&T);
              bav_realloc_term (&T, A->total_rank.size);
              ba0_pull_stack ();

              while (!bap_outof_itermon_mpq (&iter))
                {
                  bap_term_itermon_mpq (&T, &iter);
                  bap_write_neg_creator_mpq (&crea, &T,
                      *bap_coeff_itermon_mpq (&iter));
                  bap_next_itermon_mpq (&iter);
                }

              ba0_restore (&M);
            }
          bap_close_creator_mpq (&crea);
        }
      else
        {
          ba0_push_another_stack ();
          ba0_record (&M);
          bav_init_term (&T);
          bav_realloc_term (&T, A->total_rank.size);

          bap_init_polynom_mpq (&S);

          bap_begin_creator_mpq (&crea, &S, &A->total_rank,
              bap_exact_total_rank, bap_nbmon_polynom_mpq (A));
          while (!bap_outof_itermon_mpq (&iter))
            {
              bap_term_itermon_mpq (&T, &iter);
              bap_write_neg_creator_mpq (&crea, &T,
                  *bap_coeff_itermon_mpq (&iter));
              bap_next_itermon_mpq (&iter);
            }

          bap_close_creator_mpq (&crea);
          ba0_pull_stack ();

          bap_set_polynom_mpq (R, &S);
          ba0_restore (&M);
        }
    }
}

/*
 * texinfo: bap_mul_polynom_numeric_mpq
 * Assign @math{c\,A} to @var{R}.
 */

BAP_DLL void
bap_mul_polynom_numeric_mpq (
    struct bap_polynom_mpq *R,
    struct bap_polynom_mpq *A,
    ba0_mpq_t c)
{
  struct bap_itermon_mpq iter;
  struct bap_creator_mpq crea;
  struct bap_polynom_mpq S;
  struct bav_term T;
  ba0_mpq_t prod, *lc;
  enum bap_typeof_total_rank type;
  ba0_int_p nbmon;
  struct ba0_mark M;

  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (ba0_mpq_is_zero (c))
    bap_set_polynom_zero_mpq (R);
  else if (ba0_mpq_is_one (c))
    {
      if (R != A)
        bap_set_polynom_mpq (R, A);
    }
  else if (R == A && ba0_domain_mpq ())
    {
      bap_begin_itermon_mpq (&iter, A);
      while (!bap_outof_itermon_mpq (&iter))
        {
          lc = bap_coeff_itermon_mpq (&iter);
          ba0_mpq_mul (*lc, *lc, c);
          if (ba0_mpq_is_zero (*lc))
            BA0_RAISE_EXCEPTION (BA0_ERRALG);
          bap_next_itermon_mpq (&iter);
        }
    }
  else
    {
      bap_begin_itermon_mpq (&iter, A);
      nbmon = bap_nbmon_polynom_mpq (A) - R->clot->alloc;
      nbmon = nbmon > 0 ? nbmon : 0;

      type = ba0_domain_mpq ()? bap_exact_total_rank : bap_approx_total_rank;

      if (bap_are_disjoint_polynom_mpq (R, A))
        {
          bap_begin_creator_mpq (&crea, R, &A->total_rank, type, nbmon);

          if (bap_is_write_allable_creator_mpq (&crea, A)
              && ba0_domain_mpq ())
            bap_write_mul_all_creator_mpq (&crea, A, c);
          else
            {
              ba0_push_another_stack ();
              ba0_record (&M);

              bav_init_term (&T);
              bav_realloc_term (&T, A->total_rank.size);

              ba0_mpq_init (prod);

              while (!bap_outof_itermon_mpq (&iter))
                {
                  lc = bap_coeff_itermon_mpq (&iter);
                  ba0_mpq_mul (prod, c, *lc);
                  if (!ba0_mpq_is_zero (prod))
                    {
                      bap_term_itermon_mpq (&T, &iter);
                      ba0_pull_stack ();
                      bap_write_creator_mpq (&crea, &T, prod);
                      ba0_push_another_stack ();
                    }
                  else if (ba0_domain_mpq ())
                    BA0_RAISE_EXCEPTION (BA0_ERRALG);
                  bap_next_itermon_mpq (&iter);
                }

              ba0_pull_stack ();
              ba0_restore (&M);
            }

          bap_close_creator_mpq (&crea);
        }
      else
        {
          ba0_push_another_stack ();
          ba0_record (&M);

          bap_init_polynom_mpq (&S);

          bav_init_term (&T);
          bav_realloc_term (&T, A->total_rank.size);

          ba0_mpq_init (prod);

          bap_begin_creator_mpq (&crea, &S, &A->total_rank, type,
              bap_nbmon_polynom_mpq (A));

          while (!bap_outof_itermon_mpq (&iter))
            {
              lc = bap_coeff_itermon_mpq (&iter);
              ba0_mpq_mul (prod, c, *lc);
              if (!ba0_mpq_is_zero (prod))
                {
                  bap_term_itermon_mpq (&T, &iter);
                  bap_write_creator_mpq (&crea, &T, prod);
                }
              else if (ba0_domain_mpq ())
                BA0_RAISE_EXCEPTION (BA0_ERRALG);
              bap_next_itermon_mpq (&iter);
            }

          bap_close_creator_mpq (&crea);

          ba0_pull_stack ();
          bap_set_polynom_mpq (R, &S);
          ba0_restore (&M);
        }
    }
}

/*
 * texinfo: bap_mul_polynom_value_int_p_mpq
 * Assign @math{A \, (x - \alpha)} to @var{R}, where @math{(x,\, \alpha)}
 * denotes @var{val}.
 */

BAP_DLL void
bap_mul_polynom_value_int_p_mpq (
    struct bap_polynom_mpq *R,
    struct bap_polynom_mpq *A,
    struct bav_value_int_p *val)
{
  struct bav_term T;
  struct bav_rank rg;
  ba0_mpq_t c;
  struct bap_creator_mpq crea;
  struct bap_polynom_mpq *P;
  struct ba0_mark M;

  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&T);
  rg.var = val->var;
  rg.deg = 1;
  bav_set_term_rank (&T, &rg);
  P = bap_new_polynom_mpq ();
  bap_begin_creator_mpq (&crea, P, &T, bap_exact_total_rank, 2);
  ba0_mpq_init_set_ui (c, 1);
  bap_write_creator_mpq (&crea, &T, c);
  bav_set_term_one (&T);
  ba0_mpq_set_si (c, val->value);
  bap_write_neg_creator_mpq (&crea, &T, c);
  bap_close_creator_mpq (&crea);
  ba0_pull_stack ();
  bap_mul_polynom_mpq (R, A, P);
  ba0_restore (&M);
}

/*
 * texinfo: bap_mul_polynom_term_mpq
 * Assign @math{A \, T} to @var{R}.
 */

BAP_DLL void
bap_mul_polynom_term_mpq (
    struct bap_polynom_mpq *R,
    struct bap_polynom_mpq *A,
    struct bav_term *T)
{
  struct bap_itermon_mpq iter;
  struct bap_creator_mpq crea;
  struct bap_polynom_mpq *P;
  struct bav_term U;
  struct ba0_mark M;

  bap__check_ordering_mpq (A);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (bav_is_one_term (T))
    {
      if (R != A)
        bap_set_polynom_mpq (R, A);
      return;
    }

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&U);
  bav_set_term (&U, &A->total_rank);
  bav_mul_term (&U, &U, T);
  bap_begin_itermon_mpq (&iter, A);
  P = bap_new_polynom_mpq ();
  bap_begin_creator_mpq (&crea, P, &U, bap_exact_total_rank,
      bap_nbmon_polynom_mpq (A));
  while (!bap_outof_itermon_mpq (&iter))
    {
      bap_term_itermon_mpq (&U, &iter);
      bav_mul_term (&U, &U, T);
      bap_write_creator_mpq (&crea, &U, *bap_coeff_itermon_mpq (&iter));
      bap_next_itermon_mpq (&iter);
    }
  bap_close_creator_mpq (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mpq (R, P);
  ba0_restore (&M);
}

/*
 * texinfo: bap_mul_polynom_variable_mpq
 * Assign @math{A \, v^d} to @var{R}.
 */

BAP_DLL void
bap_mul_polynom_variable_mpq (
    struct bap_polynom_mpq *R,
    struct bap_polynom_mpq *A,
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
  bap_mul_polynom_term_mpq (R, A, &term);
  ba0_restore (&M);
}

/*
 * texinfo: bap_mul_polynom_monom_mpq
 * Assign @math{A \, c\, T} to @var{R}.
 */

BAP_DLL void
bap_mul_polynom_monom_mpq (
    struct bap_polynom_mpq *R,
    struct bap_polynom_mpq *A,
    ba0_mpq_t c,
    struct bav_term *T)
{
  struct bap_itermon_mpq iter;
  struct bap_creator_mpq crea;
  struct bap_polynom_mpq *P;
  struct bav_term U;
  ba0_mpq_t d;
  struct ba0_mark M;

  bap__check_ordering_mpq (A);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (ba0_mpq_is_zero (c))
    {
      bap_set_polynom_zero_mpq (R);
      return;
    }
  else if (ba0_mpq_is_one (c))
    {
      bap_mul_polynom_term_mpq (R, A, T);
      return;
    }

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&U);
  bav_set_term (&U, &A->total_rank);
  bav_mul_term (&U, &U, T);
  bap_begin_itermon_mpq (&iter, A);

  P = bap_new_polynom_mpq ();
#if defined (BAD_FLAG_mpz) || defined (BAD_FLAG_mpq)
  bap_begin_creator_mpq (&crea, P, &U, bap_exact_total_rank,
      bap_nbmon_polynom_mpq (A));
#else
  bap_begin_creator_mpq (&crea, P, &U, bap_approx_total_rank,
      bap_nbmon_polynom_mpq (A));
#endif

  ba0_mpq_init (d);

  while (!bap_outof_itermon_mpq (&iter))
    {
      bap_term_itermon_mpq (&U, &iter);
      bav_mul_term (&U, &U, T);
      ba0_mpq_mul (d, c, *bap_coeff_itermon_mpq (&iter));
      bap_write_creator_mpq (&crea, &U, d);
      bap_next_itermon_mpq (&iter);
    }
  bap_close_creator_mpq (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mpq (R, P);
  ba0_restore (&M);
}

/*****************************************************************************
 MULTIPLICATION
 *****************************************************************************/

static void
bap_mul_elem_polynom_mpq (
    struct bap_polynom_mpq *R,
    struct bap_polynom_mpq *A,
    struct bap_polynom_mpq *B)
{
  struct bap_creator_mpq crea;
  struct bap_itermon_mpq iterA, iterB;
  struct bap_polynom_mpq R1;
  struct bap_geobucket_mpq geo;
  ba0_mpq_t cz, *ca, *cb;
  struct bav_term TA, TB, TTB;
  enum bap_typeof_total_rank type;
  struct ba0_mark M;

  if (bap_nbmon_polynom_mpq (A) > bap_nbmon_polynom_mpq (B))
    BA0_SWAP (struct bap_polynom_mpq *,
        A,
        B);

  type = ba0_domain_mpq ()? bap_exact_total_rank : bap_approx_total_rank;

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_mpq_init (cz);

  bav_init_term (&TTB);
  bav_set_term (&TTB, &B->total_rank);

  bav_init_term (&TA);
  bav_init_term (&TB);

  bap_init_geobucket_mpq (&geo);
  bap_init_polynom_mpq (&R1);

  bap_begin_itermon_mpq (&iterA, A);
  while (!bap_outof_itermon_mpq (&iterA))
    {
      ca = bap_coeff_itermon_mpq (&iterA);
      bap_term_itermon_mpq (&TA, &iterA);
      bav_mul_term (&TB, &TTB, &TA);
      bap_begin_creator_mpq (&crea, &R1, &TB, type,
          bap_nbmon_polynom_mpq (B));
      bap_begin_itermon_mpq (&iterB, B);
      while (!bap_outof_itermon_mpq (&iterB))
        {
          cb = bap_coeff_itermon_mpq (&iterB);
          ba0_mpq_mul (cz, *ca, *cb);
          bap_term_itermon_mpq (&TB, &iterB);
          bav_mul_term (&TB, &TB, &TA);
          bap_write_creator_mpq (&crea, &TB, cz);
          bap_next_itermon_mpq (&iterB);
        }
      bap_close_creator_mpq (&crea);
      bap_add_geobucket_mpq (&geo, &R1);
      bap_next_itermon_mpq (&iterA);
    }
  ba0_pull_stack ();
  bap_set_polynom_geobucket_mpq (R, &geo);
  ba0_restore (&M);
}

/*
 * texinfo: bap_mul_polynom_mpq
 * Assign @math{A\,B} to @var{R}.
 */

BAP_DLL void
bap_mul_polynom_mpq (
    struct bap_polynom_mpq *R,
    struct bap_polynom_mpq *A,
    struct bap_polynom_mpq *B)
{
  struct bap_itercoeff_mpq iterA, iterB;
  struct bap_itermon_mpq iter;
  struct bap_creator_mpq crea;
  struct bap_polynom_mpq C, CA, CB;
  struct bap_polynom_mpq *AA, *BB, *P;
  struct bav_term T, U, TA, TB;
  struct bav_variable *xa, *xb;
  bav_Iordering r;
  ba0_int_p i;
  struct ba0_mark M;

  bap__check_compatible_mpq (A, B);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (bap_is_numeric_polynom_mpq (B))
    BA0_SWAP (struct bap_polynom_mpq *,
        A,
        B);
/*
 * If any of the two polynomials is numeric then A is so.
 */
  if (bap_is_numeric_polynom_mpq (A))
    {
      if (bap_is_zero_polynom_mpq (A) || bap_is_zero_polynom_mpq (B))
        bap_set_polynom_zero_mpq (R);
      else
        {
          ba0_mpq_t c;            /* else bug when A == R */
          ba0_push_another_stack ();
          ba0_record (&M);
          ba0_mpq_init_set (c, *bap_numeric_initial_polynom_mpq (A));
          ba0_pull_stack ();
          bap_mul_polynom_numeric_mpq (R, B, c);
          ba0_restore (&M);
        }
      return;
    }

  if (bap_nbmon_polynom_mpq (B) == 1)
    {
      BA0_SWAP (struct bap_polynom_mpq *,
          A,
          B);
    }
/*
 * If any of the two polynomials is a monomial then A is so.
 */
  if (bap_nbmon_polynom_mpq (A) == 1)
    {
      ba0_mpq_t c;
      ba0_push_another_stack ();
      ba0_record (&M);
      bap_begin_itermon_mpq (&iter, A);
      bav_init_term (&T);
      bap_term_itermon_mpq (&T, &iter);
      ba0_mpq_init_set (c, *bap_coeff_itermon_mpq (&iter));
      ba0_pull_stack ();
      bap_mul_polynom_monom_mpq (R, B, c, &T);
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
      BA0_SWAP (struct bap_polynom_mpq *,
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
      bap_mul_elem_polynom_mpq (R, A, B);
      return;
    }
/*
 * A depends on at least one variable which is not common with B
 */
  ba0_push_another_stack ();
  ba0_record (&M);

  {
    struct bap_polynom_mpq *AA0 = bap_new_readonly_polynom_mpq ();
    bap_sort_polynom_mpq (AA0, A);
    AA = bap_new_polynom_mpq ();
    bap_set_polynom_mpq (AA, AA0);
  }

  bap_begin_itercoeff_mpq (&iterA, AA, xa);

  if (xb != BAV_NOT_A_VARIABLE)
    {
      struct bap_polynom_mpq *BB0 = bap_new_readonly_polynom_mpq ();
      bap_sort_polynom_mpq (BB0, B);
      BB = bap_new_polynom_mpq ();
      bap_set_polynom_mpq (BB, BB0);
    }
  else
    BB = B;

  bap_init_polynom_mpq (&C);
  bap_init_polynom_mpq (&CA);
  bap_init_polynom_mpq (&CB);
  bav_init_term (&T);
  bav_init_term (&TA);
  bav_init_term (&TB);
  bav_init_term (&U);

  bav_mul_term (&T, &AA->total_rank, &BB->total_rank);
  i = BA0_MAX (bap_nbmon_polynom_mpq (AA), bap_nbmon_polynom_mpq (BB));
/*
 * Note: the monomials of P will temporarily not be sorted
 */
  P = bap_new_polynom_mpq ();
#if defined (BAD_FLAG_mpz) || defined (BAD_FLAG_mpq)
  bap_begin_creator_mpq (&crea, P, &T, bap_exact_total_rank, i);
#else
  bap_begin_creator_mpq (&crea, P, &T, bap_approx_total_rank, i);
#endif

  while (!bap_outof_itercoeff_mpq (&iterA))
    {
      bap_coeff_itercoeff_mpq (&CA, &iterA);
      bap_term_itercoeff_mpq (&TA, &iterA);
      bap_begin_itercoeff_mpq (&iterB, BB,
          xb == BAV_NOT_A_VARIABLE ? xa : xb);
      while (!bap_outof_itercoeff_mpq (&iterB))
        {
          bap_coeff_itercoeff_mpq (&CB, &iterB);
          bap_term_itercoeff_mpq (&TB, &iterB);

          bav_mul_term (&T, &TA, &TB);
          bap_mul_elem_polynom_mpq (&C, &CA, &CB);

          bap_begin_itermon_mpq (&iter, &C);
          while (!bap_outof_itermon_mpq (&iter))
            {
              ba0_mpq_t *c;

              c = bap_coeff_itermon_mpq (&iter);
              bap_term_itermon_mpq (&U, &iter);
              bav_mul_term (&U, &U, &T);
              bap_write_creator_mpq (&crea, &U, *c);
              bap_next_itermon_mpq (&iter);
            }
          bap_next_itercoeff_mpq (&iterB);
        }
      bap_next_itercoeff_mpq (&iterA);
    }
  bap_close_creator_mpq (&crea);
  bav_pull_ordering ();
/*
 * Now, the monomials get sorted
 */
  bap_physort_polynom_mpq (P);

  bav_R_free_ordering (r);
  ba0_pull_stack ();

  i = BA0_MAX (bap_nbmon_polynom_mpq (A), bap_nbmon_polynom_mpq (B));

  bap_set_polynom_mpq (R, P);

  ba0_restore (&M);
}

/*
 * texinfo: bap_pow_polynom_mpq
 * Assign @math{A^d} to @var{R}.
 */

BAP_DLL void
bap_pow_polynom_mpq (
    struct bap_polynom_mpq *R,
    struct bap_polynom_mpq *A,
    bav_Idegree n)
{
  struct bap_polynom_mpq E, F;
  bav_Idegree p;
  bool E_vaut_un;
  struct ba0_mark M;

  if (n == 0)
    bap_set_polynom_one_mpq (R);
  else if (n == 1)
    {
      if (R != A)
        bap_set_polynom_mpq (R, A);
    }
  else
    {
      ba0_push_another_stack ();
      ba0_record (&M);

      if (n % 2 == 1)
        {
          bap_init_polynom_mpq (&E);
          bap_set_polynom_mpq (&E, A);
          E_vaut_un = false;
        }
      else
        E_vaut_un = true;

      bap_init_polynom_mpq (&F);
      bap_mul_polynom_mpq (&F, A, A);

      for (p = n / 2; p != 1; p /= 2)
        {
          if (p % 2 == 1)
            {
              if (E_vaut_un)
                {
                  bap_init_polynom_mpq (&E);
                  bap_set_polynom_mpq (&E, &F);
                  E_vaut_un = false;
                }
              else
                bap_mul_polynom_mpq (&E, &F, &E);
            }
          bap_mul_polynom_mpq (&F, &F, &F);
        }
      ba0_pull_stack ();
      if (E_vaut_un)
        bap_set_polynom_mpq (R, &F);
      else
        bap_mul_polynom_mpq (R, &E, &F);
      ba0_restore (&M);
    }
}

#undef BAD_FLAG_mpq
