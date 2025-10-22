#include "bap_polynom_mint_hp.h"
#include "bap_add_polynom_mint_hp.h"
#include "bap_creator_mint_hp.h"
#include "bap_itermon_mint_hp.h"
#include "bap_itercoeff_mint_hp.h"
#include "bap__check_mint_hp.h"
#include "bap_product_mint_hp.h"
#include "bap_geobucket_mint_hp.h"

#define BAD_FLAG_mint_hp

/*************************************************************************
 All functions parameterized by a clot are static
 *************************************************************************/

static void
bap_init_polynom_clot_mint_hp (
    struct bap_polynom_mint_hp *A,
    struct bap_clot_mint_hp *C)
{
  A->clot = C;
  bav_init_term (&A->total_rank);
  A->access = bap_sequential_monom_access;
  A->seq.first = 0;
  A->seq.after = C->size;
  bap_init_indexed_access (&A->ind);
  bap_init_set_termstripper (&A->tstrip, (struct bav_variable *) -1,
      C->ordering);
  A->readonly = false;
}

/*
 * texinfo: bap_init_polynom_mint_hp
 * Initialize @var{A} to @math{0}.
 */

BAP_DLL void
bap_init_polynom_mint_hp (
    struct bap_polynom_mint_hp *A)
{
  struct bav_term T;
  struct bap_clot_mint_hp *C;

  bav_init_term (&T);
  C = bap_new_clot_mint_hp (&T);
  bap_init_polynom_clot_mint_hp (A, C);
}

/* 
 * texinfo: bap_init_readonly_polynom_mint_hp
 * Initialize @var{A} to @math{0} as a readonly polynomial.
 */

BAP_DLL void
bap_init_readonly_polynom_mint_hp (
    struct bap_polynom_mint_hp *A)
{
  A->clot = (struct bap_clot_mint_hp *) 0;
  bav_init_term (&A->total_rank);
  A->access = bap_sequential_monom_access;
  A->seq.first = 0;
  A->seq.after = 0;
  bap_init_indexed_access (&A->ind);
  bap_init_set_termstripper (&A->tstrip, (struct bav_variable *) -1,
      bav_current_ordering ());
  A->readonly = true;
}

/*
 * texinfo: bap_init_polynom_one_mint_hp
 * Initialize @var{A} to @math{1}.
 */

BAP_DLL void
bap_init_polynom_one_mint_hp (
    struct bap_polynom_mint_hp *A)
{
  struct bap_creator_mint_hp crea;
  struct bav_term T;
  struct bap_clot_mint_hp *C;
  ba0_mint_hp_t un;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mint_hp_init_set_ui (un, (unsigned long int) 1);
  ba0_pull_stack ();

  bav_init_term (&T);
  C = bap_new_clot_mint_hp (&T);
  bap_init_polynom_clot_mint_hp (A, C);
  bap_begin_creator_mint_hp (&crea, A, &T, bap_exact_total_rank, 1);
  bap_write_creator_mint_hp (&crea, &T, un);
  bap_close_creator_mint_hp (&crea);
  ba0_restore (&M);
}

/*
 * texinfo: bap_init_polynom_crk_mint_hp
 * Initialize @var{A} to @math{c\,@var{rg}}.
 * The coefficient @var{c} is allowed to be @math{0}.
 * The rank @var{rg} is allowed to be the rank of zero.
 */

BAP_DLL void
bap_init_polynom_crk_mint_hp (
    struct bap_polynom_mint_hp *A,
    ba0_mint_hp_t c,
    struct bav_rank *rg)
{
  struct bav_term T;
  struct bap_creator_mint_hp crea;
  struct bap_clot_mint_hp *C;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  bav_init_term (&T);
  if (!bav_is_zero_rank (rg))
    bav_set_term_rank (&T, rg);
  ba0_pull_stack ();

  C = bap_new_clot_mint_hp (&T);
  bap_init_polynom_clot_mint_hp (A, C);
  bap_begin_creator_mint_hp (&crea, A, &T, bap_exact_total_rank, 1);
  if ((!ba0_mint_hp_is_zero (c)) || (!bav_is_zero_rank (rg)))
    bap_write_creator_mint_hp (&crea, &T, c);

  ba0_restore (&M);
  bap_close_creator_mint_hp (&crea);
}

/****************************************************************************
 NEW

 All clot functions are static
 ****************************************************************************/

static struct bap_polynom_mint_hp *
bap_new_polynom_clot_mint_hp (
    struct bap_clot_mint_hp *C)
{
  struct bap_polynom_mint_hp *A;

  A = (struct bap_polynom_mint_hp *) ba0_alloc (sizeof (struct
          bap_polynom_mint_hp));
  bap_init_polynom_clot_mint_hp (A, C);
  return A;
}

/*
 * texinfo: bap_new_polynom_mint_hp
 * Allocate a new polynomial, initialize it and return it.
 */

BAP_DLL struct bap_polynom_mint_hp *
bap_new_polynom_mint_hp (
    void)
{
  struct bav_term T;
  struct bap_clot_mint_hp *C;

  bav_init_term (&T);
  C = bap_new_clot_mint_hp (&T);
  return bap_new_polynom_clot_mint_hp (C);
}

/*
 * texinfo: bap_new_readonly_polynom_mint_hp
 * Allocate a new polynomial, initialize it as a readonly polynomial
 * and return it.
 */

BAP_DLL struct bap_polynom_mint_hp *
bap_new_readonly_polynom_mint_hp (
    void)
{
  struct bap_polynom_mint_hp *A;

  A = (struct bap_polynom_mint_hp *) ba0_alloc (sizeof (struct
          bap_polynom_mint_hp));
  bap_init_readonly_polynom_mint_hp (A);
  return A;
}

/*
 * texinfo: bap_new_polynom_crk_mint_hp
 * Allocate a new polynomial, initialize it to @math{c\,@var{rg}}
 * and return it. 
 * The coefficient @var{c} is allowed to be @math{0}.
 * The rank @var{rg} is allowed to be the rank of zero.
 */

BAP_DLL struct bap_polynom_mint_hp *
bap_new_polynom_crk_mint_hp (
    ba0_mint_hp_t c,
    struct bav_rank *rg)
{
  struct bav_term T;
  struct bap_creator_mint_hp crea;
  struct bap_polynom_mint_hp *A;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  bav_init_term (&T);
  if (!bav_is_zero_rank (rg))
    bav_set_term_rank (&T, rg);
  ba0_pull_stack ();

  A = bap_new_polynom_mint_hp ();
  bap_begin_creator_mint_hp (&crea, A, &T, bap_exact_total_rank, 1);
  if ((!ba0_mint_hp_is_zero (c)) || (!bav_is_zero_rank (rg)))
    bap_write_creator_mint_hp (&crea, &T, c);

  ba0_restore (&M);

  bap_close_creator_mint_hp (&crea);
  return A;
}

/* 
 * texinfo: bap_new_polynom_one_mint_hp
 * Allocate a new polynomial, initialize it to @math{1} and return it.
 */

BAP_DLL struct bap_polynom_mint_hp *
bap_new_polynom_one_mint_hp (
    void)
{
  struct bap_polynom_mint_hp *A;
  ba0_mint_hp_t c;
  struct ba0_mark M;
  struct bav_rank rg;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mint_hp_init_set_ui (c, 1);
  ba0_pull_stack ();

  rg = bav_constant_rank ();
  A = bap_new_polynom_crk_mint_hp (c, &rg);
  ba0_restore (&M);
  return A;
}

/****************************************************************************
 SET
 ****************************************************************************/

/*
 * texinfo: bap_set_polynom_zero_mint_hp
 * Assign @math{0} to @var{A}.
 * The polynomial @var{A} is allowed to be readonly.
 */

BAP_DLL void
bap_set_polynom_zero_mint_hp (
    struct bap_polynom_mint_hp *A)
{
  if (A->access == bap_sequential_monom_access)
    A->seq.after = A->seq.first = 0;
  else
    A->ind.size = 0;
  bav_set_term_one (&A->total_rank);
}

/*
 * texinfo: bap_set_polynom_one_mint_hp
 * Assign @math{1} to @var{A}.
 * Exception @code{BA0_ERRALG} is raised if @var{A} has readonly mode.
 */

BAP_DLL void
bap_set_polynom_one_mint_hp (
    struct bap_polynom_mint_hp *A)
{
  struct bap_creator_mint_hp crea;
  struct bav_term T;
  ba0_mint_hp_t c;
  struct ba0_mark M;

  if (A->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mint_hp_init_set_ui (c, 1);
  bav_init_term (&T);
  ba0_pull_stack ();

  bap_begin_creator_mint_hp (&crea, A, &T, bap_exact_total_rank, 1);
  bap_write_creator_mint_hp (&crea, &T, c);
  bap_close_creator_mint_hp (&crea);

  ba0_restore (&M);
}

/*
 * texinfo: bap_set_polynom_crk_mint_hp
 * Assign @math{c\,@var{rg}} to @var{A}.
 * The coefficient @var{c} is allowed to be @math{0}.
 * The rank @var{rg} is allowed to be the rank of zero.
 * Note: the clot of @var{A} is modified even if the the result is zero.
 * Exception @code{BA0_ERRALG} is raised if @var{A} has readonly mode.
 */

BAP_DLL void
bap_set_polynom_crk_mint_hp (
    struct bap_polynom_mint_hp *A,
    ba0_mint_hp_t c,
    struct bav_rank *rg)
{
  struct bav_term T;
  struct bap_creator_mint_hp crea;
  struct ba0_mark M;

  if (A->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);
  bav_init_term (&T);
  if (!bav_is_zero_rank (rg))
    bav_set_term_rank (&T, rg);
  ba0_pull_stack ();

  bap_begin_creator_mint_hp (&crea, A, &T, bap_exact_total_rank, 1);
  if ((!ba0_mint_hp_is_zero (c)) && (!bav_is_zero_rank (rg)))
    bap_write_creator_mint_hp (&crea, &T, c);

  bap_close_creator_mint_hp (&crea);

  ba0_restore (&M);
}

/*
 * texinfo: bap_set_polynom_variable_mint_hp
 * Assign @math{v^d} to @var{A}.
 * Exception @code{BA0_ERRALG} is raised if @var{A} has readonly mode.
 */

BAP_DLL void
bap_set_polynom_variable_mint_hp (
    struct bap_polynom_mint_hp *A,
    struct bav_variable *v,
    bav_Idegree d)
{
  struct bav_term T;
  struct bap_creator_mint_hp crea;
  ba0_mint_hp_t c;
  struct ba0_mark M;

  if (A->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);
  bav_init_term (&T);
  bav_set_term_variable (&T, v, d);
  ba0_mint_hp_init_set_ui (c, 1);
  ba0_pull_stack ();

  bap_begin_creator_mint_hp (&crea, A, &T, bap_exact_total_rank, 1);
  if (!bav_is_one_term (&T))
    bap_write_creator_mint_hp (&crea, &T, c);
  bap_close_creator_mint_hp (&crea);

  ba0_restore (&M);
}

/* 
 * texinfo: bap_set_polynom_term_mint_hp
 * Assign @var{T} to @var{A}.
 * Exception @code{BA0_ERRALG} is raised if @var{A} has readonly mode.
 */

BAP_DLL void
bap_set_polynom_term_mint_hp (
    struct bap_polynom_mint_hp *A,
    struct bav_term *T)
{
  struct bap_creator_mint_hp crea;
  ba0_mint_hp_t c;
  struct ba0_mark M;

  if (A->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mint_hp_init_set_si (c, 1);
  ba0_pull_stack ();

  bap_begin_creator_mint_hp (&crea, A, T, bap_exact_total_rank, 1);
  bap_write_creator_mint_hp (&crea, T, c);
  bap_close_creator_mint_hp (&crea);
  ba0_restore (&M);
}

/* 
 * texinfo: bap_set_polynom_monom_mint_hp
 * Assign @math{c\,T} to @var{A}. 
 * The coefficient @var{c} is allowed to be @math{0}.
 * Exception @code{BA0_ERRALG} is raised if @var{A} has readonly mode.
 */

BAP_DLL void
bap_set_polynom_monom_mint_hp (
    struct bap_polynom_mint_hp *A,
    ba0_mint_hp_t c,
    struct bav_term *T)
{
  struct bap_creator_mint_hp crea;

  if (A->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (ba0_mint_hp_is_zero (c))
    bap_set_polynom_zero_mint_hp (A);
  else
    {
      bap_begin_creator_mint_hp (&crea, A, T, bap_exact_total_rank, 1);
      bap_write_creator_mint_hp (&crea, T, c);
      bap_close_creator_mint_hp (&crea);
    }
}

/*
 * texinfo: bap_set_polynom_mint_hp
 * Assign @var{B} to @var{A}.
 * The two polynomials are supposed to be disjoint.
 * Exception @code{BA0_ERRALG} is raised if @var{A} has readonly mode.
 */

BAP_DLL void
bap_set_polynom_mint_hp (
    struct bap_polynom_mint_hp *A,
    struct bap_polynom_mint_hp *B)
{
  struct bap_creator_mint_hp crea;
  struct bap_itermon_mint_hp iter;
  struct bap_polynom_mint_hp C;
  struct bav_term T;
  ba0_mint_hp_t *c;
  ba0_int_p nbmon;
  struct ba0_mark M;

  if (A->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (bap_is_zero_polynom_mint_hp (B))
    bap_set_polynom_zero_mint_hp (A);
  else if (!bap_are_disjoint_polynom_mint_hp (A, B))
    {
      if (A == B)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
      else if (B->access == bap_sequential_monom_access)
        {
          A->access = bap_sequential_monom_access;
          A->seq = B->seq;
          bav_set_term (&A->total_rank, &B->total_rank);
          bap_set_termstripper (&A->tstrip, &B->tstrip);
        }
      else
        {
          ba0_push_another_stack ();
          ba0_record (&M);

          bap_init_polynom_mint_hp (&C);
          bap_set_polynom_mint_hp (&C, B);

          ba0_pull_stack ();

          bap_set_polynom_mint_hp (A, &C);

          ba0_restore (&M);
        }
    }
  else
    {
      nbmon = bap_nbmon_polynom_mint_hp (B) - A->clot->alloc;
      nbmon = nbmon > 0 ? nbmon : 0;

      ba0_push_another_stack ();
      ba0_record (&M);
      bav_init_term (&T);
      bav_realloc_term (&T, B->total_rank.size);
      ba0_pull_stack ();

      bap_begin_creator_mint_hp (&crea, A, &B->total_rank, bap_exact_total_rank,
          nbmon);

      if (bap_is_write_allable_creator_mint_hp (&crea, B))
        bap_write_all_creator_mint_hp (&crea, B);
      else
        {
          bap_begin_itermon_mint_hp (&iter, B);
          while (!bap_outof_itermon_mint_hp (&iter))
            {
              c = bap_coeff_itermon_mint_hp (&iter);
              bap_term_itermon_mint_hp (&T, &iter);
              bap_write_creator_mint_hp (&crea, &T, *c);
              bap_next_itermon_mint_hp (&iter);
            }
        }
      bap_close_creator_mint_hp (&crea);
      ba0_restore (&M);
    }
}

/*
 * texinfo: bap_set_tableof_polynom_mint_hp
 * Assign @var{src} to @var{dst}.
 * Entries of @var{src} are allowed to be @code{BAP_NOT_A_POLYNOM_mint_hp}.
 */

BAP_DLL void
bap_set_tableof_polynom_mint_hp (
    struct bap_tableof_polynom_mint_hp *dst,
    struct bap_tableof_polynom_mint_hp *src)
{
  if (dst != src)
    {
      ba0_int_p i;

      ba0_realloc_table ((struct ba0_table *) dst, src->size);
      for (i = 0; i < src->size; i++)
        {
          if (src->tab[i] == BAP_NOT_A_POLYNOM_mint_hp)
            dst->tab[i] = BAP_NOT_A_POLYNOM_mint_hp;
          else
            {
              if (dst->tab[i] == BAP_NOT_A_POLYNOM_mint_hp)
                dst->tab[i] = bap_new_polynom_mint_hp ();
              bap_set_polynom_mint_hp (dst->tab[i], src->tab[i]);
            }
        }
      dst->size = src->size;
    }
}

/*
 * texinfo: bap_set_tableof_tableof_polynom_mint_hp
 * Assign @var{src} to @var{dst}.
 * All tables are allowed to involve zero entries.
 */

BAP_DLL void
bap_set_tableof_tableof_polynom_mint_hp (
    struct bap_tableof_tableof_polynom_mint_hp *dst,
    struct bap_tableof_tableof_polynom_mint_hp *src)
{
  if (dst != src)
    {
      ba0_int_p i;

      ba0_realloc_table ((struct ba0_table *) dst, src->size);
      for (i = 0; i < src->size; i++)
        {
          if (src->tab[i] == (struct bap_tableof_polynom_mint_hp *) 0)
            dst->tab[i] = (struct bap_tableof_polynom_mint_hp *) 0;
          else
            {
              if (dst->tab[i] == (struct bap_tableof_polynom_mint_hp *) 0)
                dst->tab[i] = (struct bap_tableof_polynom_mint_hp *)
                    ba0_new_table ();
              bap_set_tableof_polynom_mint_hp (dst->tab[i], src->tab[i]);
            }
        }
      dst->size = src->size;
    }
}


/* 
 * texinfo: bap_set_readonly_polynom_mint_hp
 * Assign @var{A} to @var{R}.
 * The polynomial @var{R} is readonly.
 * The two polynomials are not disjoint.
 */

BAP_DLL void
bap_set_readonly_polynom_mint_hp (
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A)
{
  if (R == A)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  R->clot = A->clot;
  bav_set_term (&R->total_rank, &A->total_rank);
  if (A->access == bap_sequential_monom_access)
    {
      R->access = bap_sequential_monom_access;
      R->seq = A->seq;
    }
  else
    {
      struct bap_creator_indexed_access crea;
      struct bap_iterator_indexed_access iter;
      ba0_int_p i, nbmon;

      R->access = bap_indexed_monom_access;
      nbmon = bap_nbmon_polynom_mint_hp (A);
      bap_realloc_indexed_access (&R->ind, nbmon);
      bap_begin_creator_indexed_access (&crea, &R->ind);
      bap_begin_iterator_indexed_access (&iter, &A->ind);
      for (i = 0; i < nbmon; i++)
        bap_write_creator_indexed_access (&crea,
            bap_read_iterator_indexed_access (&iter));
      bap_close_creator_indexed_access (&crea);
    }
  bap_set_termstripper (&R->tstrip, &A->tstrip);
  R->readonly = true;
}

/*
   PREDICATES
 */

/*
 * texinfo: bap_is_zero_polynom_mint_hp
 * Return @code{true} if @var{A} is equal to @math{0}.
 */

BAP_DLL bool
bap_is_zero_polynom_mint_hp (
    struct bap_polynom_mint_hp *A)
{
  return bap_nbmon_polynom_mint_hp (A) == 0;
}

/* 
 * texinfo: bap_is_one_polynom_mint_hp
 * Return @code{true} if @var{A} is equal to @math{1}.
 */

BAP_DLL bool
bap_is_one_polynom_mint_hp (
    struct bap_polynom_mint_hp *A)
{
  struct bap_itermon_mint_hp iter;
  ba0_mint_hp_t *lc;

  if (!bav_is_one_term (&A->total_rank))
    return false;
  bap_begin_itermon_mint_hp (&iter, A);
  lc = bap_coeff_itermon_mint_hp (&iter);
  return ba0_mint_hp_is_one (*lc);
}

/* 
 * texinfo: bap_is_numeric_polynom_mint_hp
 * Return @code{true} if @var{A} does not depend on any variable.
 */

BAP_DLL bool
bap_is_numeric_polynom_mint_hp (
    struct bap_polynom_mint_hp *A)
{
  return bap_is_zero_polynom_mint_hp (A) || bav_is_one_term (&A->total_rank);
}

/* 
 * texinfo: bap_is_univariate_polynom_mint_hp
 * Return @code{true} if @var{A} depends on a single variable.
 */

BAP_DLL bool
bap_is_univariate_polynom_mint_hp (
    struct bap_polynom_mint_hp *A)
{
  return A->total_rank.size <= 1;
}

/* 
 * texinfo: bap_is_variable_polynom_mint_hp
 * Return @code{true} if @var{A} is equal to a variable.
 */

BAP_DLL bool
bap_is_variable_polynom_mint_hp (
    struct bap_polynom_mint_hp *A)
{
  return bav_total_degree_term (&A->total_rank) == 1
      && bap_nbmon_polynom_mint_hp (A) == 1;
}

/*
 * texinfo: bap_is_solved_polynom_mint_hp
 * Return @code{true} if @var{A} has leading degree @math{1}
 * and a numeric initial.
 */

BAP_DLL bool
bap_is_solved_polynom_mint_hp (
    struct bap_polynom_mint_hp *A)
{
  struct bap_polynom_mint_hp init;
  struct ba0_mark M;
  bool b;

  if (bap_is_numeric_polynom_mint_hp (A))
    return false;

  if (bap_leading_degree_polynom_mint_hp (A) != 1)
    return false;

  ba0_record (&M);
  bap_init_readonly_polynom_mint_hp (&init);
  bap_initial_polynom_mint_hp (&init, A);
  b = bap_is_numeric_polynom_mint_hp (&init);
  ba0_restore (&M);

  return b;
}

/*
 * texinfo: bap_is_derivative_minus_independent_polynom_mint_hp
 * Return @code{true} if @var{A} has the form @math{v - B} where
 * @var{v} is a derivative and @var{B} is a polynomial which does
 * not depend on any derivative.
 */

BAP_DLL bool
bap_is_derivative_minus_independent_polynom_mint_hp (
    struct bap_polynom_mint_hp *A)
{
  ba0_int_p i;

  if (!bap_is_solved_polynom_mint_hp (A))
    return false;

  if (bav_symbol_type_variable (A->total_rank.rg[0].var) !=
      bav_dependent_symbol)
    return false;
  for (i = 1; i < A->total_rank.size; i++)
    if (bav_symbol_type_variable (A->total_rank.rg[i].var) ==
        bav_dependent_symbol)
      return false;
  return true;
}

/*
 * bap_is_rank_minus_monom_polynom_mint_hp
 * Return @code{true} if @var{A} has the form @math{v^d - M} where
 * @var{v} is the lading derivative of @var{A} and @var{M} is a
 * monomial.
 */

BAP_DLL bool
bap_is_rank_minus_monom_polynom_mint_hp (
    struct bap_polynom_mint_hp *A)
{
  struct bap_polynom_mint_hp init;

  if (bap_nbmon_polynom_mint_hp (A) > 2)
    return false;
  bap_init_readonly_polynom_mint_hp (&init);
  bap_initial_polynom_mint_hp (&init, A);
  return bap_is_one_polynom_mint_hp (&init);
}

/* 
 * texinfo: bap_depend_polynom_mint_hp
 * Return @code{true} if @var{A} depends on @var{v}.
 */

BAP_DLL bool
bap_depend_polynom_mint_hp (
    struct bap_polynom_mint_hp *A,
    struct bav_variable *v)
{
  ba0_int_p i;

  for (i = 0; i < A->total_rank.size; i++)
    if (A->total_rank.rg[i].var == v)
      return true;
  return false;
}

/*
 * texinfo: bap_depend_point_polynom_mint_hp
 * Return @code{true} if @var{A} depends on one of the
 * variables of @var{point}.

BAP_DLL bool
bap_depend_point_polynom_mint_hp (
    struct bap_polynom_mint_hp * A,
    struct ba0_point * point)
{
  for (i = 0; i < ->total_rank.size; i++)
    {
      struct bav_variable * v = A->total_rank.rg[i].var;
      if (ba0_bsearch_point (v, point, (ba0_int_p*)0) != BA0_NOT_A_VALUE)
        return true;
    }
  return false;
}
 */

/*
 * texinfo: bap_depend_only_polynom_mint_hp
 * Return @code{true} if @var{A} depends only on the variables 
 * present in @var{T}. The table @var{T} is supposed to be sorted
 * in ascending order.
*/

BAP_DLL bool
bap_depend_only_polynom_mint_hp (
    struct bap_polynom_mint_hp *A,
    struct bav_tableof_variable *T)
{
  bav_Inumber n = 0, m = 0;
  ba0_int_p i, j;

  i = 0;
  if (i < A->total_rank.size)
    n = bav_variable_number (A->total_rank.rg[i].var);
  j = T->size - 1;
  if (j >= 0)
    m = bav_variable_number (T->tab[j]);
  while (i < A->total_rank.size && j >= 0)
    {
      if (n > m)
        return false;
      else if (n < m)
        {
          j -= 1;
          m = bav_variable_number (T->tab[j]);
        }
      else
        {
          i += 1;
          j -= 1;
          n = bav_variable_number (A->total_rank.rg[i].var);
          m = bav_variable_number (T->tab[j]);
        }
    }
  return i == A->total_rank.size;
}

/***************************************************************************
 COMPARISON FUNCTIONS
 ***************************************************************************/

/*
 * texinfo: bap_compare_polynom_mint_hp
 * Enumerate all the monomials of @var{A} and @var{B} and
 * looks for the first terms which differ.
 * Return 
 * @code{ba0_lt} if the term of @var{A} is strictly less than that of @var{B},
 * @code{ba0_gt} if the term of @var{A} is 
 *          strictly greater than that of @var{B}, 
 * @code{ba0_eq} if @var{A} and @var{B} are equal, and
 * and @code{ba0_equiv} @var{A} and @var{B} have the same terms
 *          but not the same coefficients.
 */

BAP_DLL enum ba0_compare_code
bap_compare_polynom_mint_hp (
    struct bap_polynom_mint_hp *A,
    struct bap_polynom_mint_hp *B)
{
  struct bap_itermon_mint_hp iterA, iterB;
  enum ba0_compare_code code, resultat = ba0_eq;
  struct bav_term TA, TB;
  struct ba0_mark M;

  bap__check_compatible_mint_hp (A, B);

  if (A == B)
    return resultat;

  ba0_record (&M);
  bav_init_term (&TA);
  bav_init_term (&TB);
  bap_begin_itermon_mint_hp (&iterA, A);
  bap_begin_itermon_mint_hp (&iterB, B);
  while (!bap_outof_itermon_mint_hp (&iterA) && !bap_outof_itermon_mint_hp (&iterB))
    {
      bap_term_itermon_mint_hp (&TA, &iterA);
      bap_term_itermon_mint_hp (&TB, &iterB);
      code = bav_compare_term (&TA, &TB);
      if (code == ba0_lt || code == ba0_gt)
        {
          resultat = code;
          break;
        }
      if (resultat == ba0_eq
          && !ba0_mint_hp_are_equal (*bap_coeff_itermon_mint_hp (&iterA),
              *bap_coeff_itermon_mint_hp (&iterB)))
        resultat = ba0_equiv;
      bap_next_itermon_mint_hp (&iterA);
      bap_next_itermon_mint_hp (&iterB);
    }
  if (resultat == ba0_eq || resultat == ba0_equiv)
    {
      if (!bap_outof_itermon_mint_hp (&iterA))
        resultat = ba0_gt;
      else if (!bap_outof_itermon_mint_hp (&iterB))
        resultat = ba0_lt;
    }
  ba0_restore (&M);
  return resultat;
}

/* 
 * texinfo: bap_equal_polynom_mint_hp
 * Return @code{true} if @var{A} and @var{B} are equal.
 */

BAP_DLL bool
bap_equal_polynom_mint_hp (
    struct bap_polynom_mint_hp *A,
    struct bap_polynom_mint_hp *B)
{
  struct bap_itermon_mint_hp iterA, iterB;
  struct bav_term TA, TB;
  struct ba0_mark M;

  bap__check_compatible_mint_hp (A, B);

  if (A == B)
    return true;
  if (bap_nbmon_polynom_mint_hp (A) != bap_nbmon_polynom_mint_hp (B))
    return false;
  if (!bav_equal_term (&A->total_rank, &B->total_rank))
    return false;

  ba0_record (&M);
  bav_init_term (&TA);
  bav_init_term (&TB);
  bap_begin_itermon_mint_hp (&iterA, A);
  bap_begin_itermon_mint_hp (&iterB, B);
  while (!bap_outof_itermon_mint_hp (&iterA))
    {
      bap_term_itermon_mint_hp (&TA, &iterA);
      bap_term_itermon_mint_hp (&TB, &iterB);
      if (!bav_equal_term (&TA, &TB))
        {
          ba0_restore (&M);
          return false;
        }
      if (!ba0_mint_hp_are_equal (*bap_coeff_itermon_mint_hp (&iterA),
              *bap_coeff_itermon_mint_hp (&iterB)))
        {
          ba0_restore (&M);
          return false;
        }
      bap_next_itermon_mint_hp (&iterA);
      bap_next_itermon_mint_hp (&iterB);
    }
  ba0_restore (&M);
  return true;
}

/* 
 * texinfo: bap_gt_rank_polynom_mint_hp
 * Return @code{true} if @var{P} has strictly greater rank than @var{B}.
 * Both parameters are polynomials.
 */

BAP_DLL bool
bap_gt_rank_polynom_mint_hp (
    void *P,
    void *Q)
{
  struct bap_polynom_mint_hp *A = (struct bap_polynom_mint_hp *) P;
  struct bap_polynom_mint_hp *B = (struct bap_polynom_mint_hp *) Q;
  struct bav_rank Arg, Brg;

  Arg = bap_rank_polynom_mint_hp (A);
  Brg = bap_rank_polynom_mint_hp (B);

  return bav_gt_rank (&Arg, &Brg);
}

/* 
 * texinfo: bap_lt_rank_polynom_mint_hp
 * Return @code{true} if @var{P} has strictly lower rank than @var{B}.
 * Both parameters are polynomials.
 */

BAP_DLL bool
bap_lt_rank_polynom_mint_hp (
    void *P,
    void *Q)
{
  struct bap_polynom_mint_hp *A = (struct bap_polynom_mint_hp *) P;
  struct bap_polynom_mint_hp *B = (struct bap_polynom_mint_hp *) Q;
  struct bav_rank Arg, Brg;

  Arg = bap_rank_polynom_mint_hp (A);
  Brg = bap_rank_polynom_mint_hp (B);

  return bav_lt_rank (&Arg, &Brg);
}

/* 
 * texinfo: bap_equal_rank_polynom_mint_hp
 * Return @code{true} if @var{P} and @var{Q} have the same rank.
 */

BAP_DLL bool
bap_equal_rank_polynom_mint_hp (
    struct bap_polynom_mint_hp *P,
    struct bap_polynom_mint_hp *Q)
{
  struct bav_rank Prg, Qrg;

  Prg = bap_rank_polynom_mint_hp (P);
  Qrg = bap_rank_polynom_mint_hp (Q);

  return bav_equal_rank (&Prg, &Qrg);
}

/*
 * texinfo: bad_compare_rank_polynom_mint_hp
 * A comparison function for sorting tables of polynomials
 * by increasing rank, using @code{qsort}.
 */

BAP_DLL int
bap_compare_rank_polynom_mint_hp (
    const void *PP,
    const void *QQ)
{
  struct bap_polynom_mint_hp *P = *(struct bap_polynom_mint_hp **) PP;
  struct bap_polynom_mint_hp *Q = *(struct bap_polynom_mint_hp **) QQ;

  if (bap_lt_rank_polynom_mint_hp (P, Q))
    return -1;
  else if (bap_equal_rank_polynom_mint_hp (P, Q))
    return 0;
  else
    return 1;
}

/*
 * texinfo: bap_are_disjoint_polynom_mint_hp
 * Return @code{true} if @var{A} and @var{B} are disjoint, in the
 * sense that any modification on one of these polynomials has no
 * side effect on the other one.
 */

BAP_DLL bool
bap_are_disjoint_polynom_mint_hp (
    struct bap_polynom_mint_hp *A,
    struct bap_polynom_mint_hp *B)
{
  return A->clot != B->clot;
}

/* 
 * texinfo: bap_mark_indets_polynom_mint_hp
 * Append to @var{vars} the variables occurring in @var{A} which
 * are not already present in @var{vars}. 
 * Every element of @var{vars} is supposed to be registered in
 * the dictionary @var{dict}.
 */

BAP_DLL void
bap_mark_indets_polynom_mint_hp (
    struct bav_dictionary_variable *dict,
    struct bav_tableof_variable *vars,
    struct bap_polynom_mint_hp *A)
{
  ba0_int_p i;

  for (i = 0; i < A->total_rank.size; i++)
    {
      struct bav_variable *v = A->total_rank.rg[i].var;
      if (bav_get_dictionary_variable (dict, vars, v) == BA0_NOT_AN_INDEX)
        {
          if (vars->size == vars->alloc)
            {
              ba0_int_p new_alloc = 2 * vars->alloc + 1;
              ba0_realloc_table ((struct ba0_table *) vars, new_alloc);
            }
          bav_add_dictionary_variable (dict, vars, v, vars->size);
          vars->tab[vars->size] = v;
          vars->size += 1;
        }
    }
}

/*
 * texinfo: bap_mark_indets_tableof_polynom_mint_hp
 * Append to @var{vars} the variables occurring in @var{T} which
 * are not already present in @var{vars}.
 * Every element of @var{vars} is supposed to be registered in
 * the dictionary @var{dict}.
 */

BAP_DLL void
bap_mark_indets_tableof_polynom_mint_hp (
    struct bav_dictionary_variable *dict,
    struct bav_tableof_variable *vars,
    struct bap_tableof_polynom_mint_hp *T)
{
  ba0_int_p i;

  for (i = 0; i < T->size; i++)
    bap_mark_indets_polynom_mint_hp (dict, vars, T->tab[i]);
}

/*
 * texinfo: bap_mark_indets_listof_polynom_mint_hp
 * Append to @var{vars} the variables occurring in @var{L} which
 * are not already present in @var{vars}.
 * Every element of @var{vars} is supposed to be registered in
 * the dictionary @var{dict}.
 */

BAP_DLL void
bap_mark_indets_listof_polynom_mint_hp (
    struct bav_dictionary_variable *dict,
    struct bav_tableof_variable *vars,
    struct bap_listof_polynom_mint_hp *L)
{
  struct bap_listof_polynom_mint_hp *M;

  for (M = L; M != (struct bap_listof_polynom_mint_hp *) 0; M = M->next)
    bap_mark_indets_polynom_mint_hp (dict, vars, M->value);
}

/*
 * texinfo: bap_set_total_rank_polynom_mint_hp
 * This low-level function computes and sets the @code{total_rank} field
 * of @var{A}.
 */

BAP_DLL void
bap_set_total_rank_polynom_mint_hp (
    struct bap_polynom_mint_hp *A)
{
  struct bav_dictionary_variable dict;
  struct bav_tableof_variable vars;
  struct ba0_tableof_int_p degs;

  struct bap_itermon_mint_hp iter;
  struct bav_term T;
  ba0_int_p i;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_dictionary_variable (&dict, 6);
  ba0_init_table ((struct ba0_table *) &vars);
  ba0_realloc_table ((struct ba0_table *) &vars, 64);
  ba0_init_table ((struct ba0_table *) &degs);
  ba0_realloc_table ((struct ba0_table *) &degs, 64);

  bav_init_term (&T);

  bap_begin_itermon_mint_hp (&iter, A);
  while (!bap_outof_itermon_mint_hp (&iter))
    {
      bap_term_itermon_mint_hp (&T, &iter);
      for (i = 0; i < T.size; i++)
        {
          struct bav_variable *v;
          ba0_int_p j;

          v = T.rg[i].var;
          j = bav_get_dictionary_variable (&dict, &vars, v);
          if (j == BA0_NOT_AN_INDEX)
            {
              bav_add_dictionary_variable (&dict, &vars, v, vars.size);
              if (vars.size == vars.alloc)
                {
                  ba0_int_p new_alloc = 2 * vars.alloc + 1;
                  ba0_realloc_table ((struct ba0_table *) &vars, new_alloc);
                  ba0_realloc_table ((struct ba0_table *) &degs, new_alloc);
                }
              vars.tab[vars.size] = v;
              degs.tab[degs.size] = T.rg[i].deg;
              vars.size += 1;
              degs.size += 1;
            }
          else if (T.rg[i].deg > degs.tab[j])
            degs.tab[j] = T.rg[i].deg;
        }
      bap_next_itermon_mint_hp (&iter);
    }
  ba0_pull_stack ();
  bav_set_term_tableof_variable (&A->total_rank, &vars, &degs);
  ba0_restore (&M);
}

/*
 * texinfo: bap_reverse_polynom_mint_hp
 * This low-level function reverts the order of the monomials in
 * the clot of @var{A}.
 * Exception @code{BA0_ERRALG} is raised if @var{A} has readonly mode.
 */

BAP_DLL void
bap_reverse_polynom_mint_hp (
    struct bap_polynom_mint_hp *A)
{
  if (A->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  bap_reverse_clot_mint_hp (A->clot);
}

/*************************************************************************
 :REORDONNE
 *************************************************************************/

struct quicksort_data
{
  struct bap_iterator_indexed_access l;
  struct bap_iterator_indexed_access r;
  struct bap_itermon_mint_hp i;
  struct bap_itermon_mint_hp j;
  struct bap_itermon_mint_hp k;
  struct bav_term Ti;
  struct bav_term Tj;
  struct bav_term Tk;
  struct bav_term pivot;
  unsigned ba0_int_p zi;
  unsigned ba0_int_p zj;
  unsigned ba0_int_p zk;
};

static void
bap_init_quicksort_data (
    struct quicksort_data *qs,
    struct bap_polynom_mint_hp *R)
{
  bap_begin_iterator_indexed_access (&qs->l, &R->ind);
  bap_end_iterator_indexed_access (&qs->r, &R->ind);

  bap_begin_itermon_mint_hp (&qs->i, R);
  bap_begin_itermon_mint_hp (&qs->j, R);
  bap_begin_itermon_mint_hp (&qs->k, R);

  bav_init_term (&qs->Ti);
  bav_init_term (&qs->Tj);
  bav_init_term (&qs->Tk);
  bav_init_term (&qs->pivot);
  qs->zi = qs->zj = qs->zk = 0;
}

/*
   Cette variante suppose qu'il n'y a pas de doublons dans les
	\'el\'ements \`a trier (ce qui est vrai pour des termes).
   Le polyn\^ome est tri\'e par ordre d\'ecroissant.
   L'iterateur sert a se deplacer dans le polynome.
   Les struct bav_term sont des variables de travail.
*/

static void
quicksort_mint_hp (
    ba0_int_p l,
    ba0_int_p r,
    struct quicksort_data *qs)
{
  ba0_int_p i, j, k;
  enum ba0_compare_code code;
/*
 * Readonly static data
 */
  static ba0_int_p alpha[] = { 1, 2, 2, 3, 4, 1, 3 };
/*
 * -  -  -  -  -  -  -      
 */
  static ba0_int_p beta[] = { 1, 3, 1, 4, 3, 2, 2 };
  if (r - l > 8)
    {
      i = (alpha[qs->zi] * (l + 2) + beta[qs->zi] * (r - 2)) / (alpha[qs->zi] +
          beta[qs->zi]);
      qs->zi = (qs->zi + 1) % 7;
      j = (alpha[qs->zj] * (l + 1) + beta[qs->zj] * (i - 1)) / (alpha[qs->zj] +
          beta[qs->zj]);
      qs->zj = (qs->zj + 3) % 7;
      k = (alpha[qs->zk] * (i + 1) + beta[qs->zk] * (r - 1)) / (alpha[qs->zk] +
          beta[qs->zk]);
      qs->zk = (qs->zk + 5) % 7;
      if (i == j || i == k || j == k)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
      bap_goto_itermon_mint_hp (&qs->i, i);
      bap_goto_itermon_mint_hp (&qs->j, j);
      bap_goto_itermon_mint_hp (&qs->k, k);

      bap_term_itermon_mint_hp (&qs->Ti, &qs->i);
      bap_term_itermon_mint_hp (&qs->Tj, &qs->j);
      bap_term_itermon_mint_hp (&qs->Tk, &qs->k);
/*
   On souhaite que le pivot soit le median de T [i], T [j], T [k].
   On doit echanger T [l] avec le median et T [r] avec le max.
*/
      code = bav_compare_term (&qs->Ti, &qs->Tj);
      if (code == ba0_gt)
        {
          code = bav_compare_term (&qs->Tj, &qs->Tk);
          if (code == ba0_gt)
            {
              bap_swapindex_iterator_indexed_access (&qs->l, &qs->j.iter_ix);
              bap_swapindex_iterator_indexed_access (&qs->r, &qs->i.iter_ix);
/* T [i] > T [j] > T [k] */
              bav_set_term (&qs->pivot, &qs->Tj);
            }
          else
            {
              code = bav_compare_term (&qs->Ti, &qs->Tk);
              if (code == ba0_gt)
                {
                  bap_swapindex_iterator_indexed_access (&qs->l,
                      &qs->k.iter_ix);
                  bap_swapindex_iterator_indexed_access (&qs->r,
                      &qs->i.iter_ix);
/* T [i] > T [k] > T [j] */
                  bav_set_term (&qs->pivot, &qs->Tk);
                }
              else
                {
                  bap_swapindex_iterator_indexed_access (&qs->l,
                      &qs->i.iter_ix);
                  bap_swapindex_iterator_indexed_access (&qs->r,
                      &qs->k.iter_ix);
/* T [k] > T [i] > T [j] */
                  bav_set_term (&qs->pivot, &qs->Ti);
                }
            }
        }
      else
        {
          code = bav_compare_term (&qs->Tk, &qs->Tj);
          if (code == ba0_gt)
            {
              bap_swapindex_iterator_indexed_access (&qs->l, &qs->j.iter_ix);
              bap_swapindex_iterator_indexed_access (&qs->r, &qs->k.iter_ix);
/* T [k] > T [j] > T [i] */
              bav_set_term (&qs->pivot, &qs->Tj);
            }
          else
            {
              code = bav_compare_term (&qs->Tk, &qs->Ti);
              if (code == ba0_gt)
                {
                  bap_swapindex_iterator_indexed_access (&qs->l,
                      &qs->k.iter_ix);
                  bap_swapindex_iterator_indexed_access (&qs->r,
                      &qs->j.iter_ix);
/* T [j] > T [k] > T [i] */
                  bav_set_term (&qs->pivot, &qs->Tk);
                }
              else
                {
                  bap_swapindex_iterator_indexed_access (&qs->l,
                      &qs->i.iter_ix);
                  bap_swapindex_iterator_indexed_access (&qs->r,
                      &qs->j.iter_ix);
/* T [j] > T [i] > T [k] */
                  bav_set_term (&qs->pivot, &qs->Ti);
                }
            }
        }
/*
   Invariants (sauf avant le 1er tour).
   i, j in [l, r]
   T [i] < pivot (sauf 1er tour ou on a egalite)
   T [j] > pivot
   Les T [k < i] sont > pivot
   Les T [k > j] sont < pivot
*/
      i = l;
      j = r;
      bap_goto_itermon_mint_hp (&qs->i, i);
      bap_goto_itermon_mint_hp (&qs->j, j);
      do
        {
          bap_swapindex_iterator_indexed_access (&qs->i.iter_ix,
              &qs->j.iter_ix);
          do
            {
              i += 1;
/*
   Dans la mesure ou l'access est indexe, il n'y aurait aucun avantage
   a utiliser un next_itermon au lieu d'un goto_itermon.
*/
              bap_next_itermon_mint_hp (&qs->i);
              bap_term_itermon_mint_hp (&qs->Ti, &qs->i);
              code = bav_compare_term (&qs->Ti, &qs->pivot);
            }
          while (code == ba0_gt);
          do
            {
              j -= 1;
              bap_prev_itermon_mint_hp (&qs->j);
              bap_term_itermon_mint_hp (&qs->Tj, &qs->j);
              code = bav_compare_term (&qs->Tj, &qs->pivot);
            }
          while (code == ba0_lt);
        }
      while (i < j);
      bap_swapindex_iterator_indexed_access (&qs->i.iter_ix, &qs->r);
      bap_goto_iterator_indexed_access (&qs->r, i - 1);
      quicksort_mint_hp (l, i - 1, qs);
      bap_goto_iterator_indexed_access (&qs->l, i + 1);
      bap_goto_iterator_indexed_access (&qs->r, r);
      quicksort_mint_hp (i + 1, r, qs);
    }
  else
    {
      bool sorted;
      struct bav_term *cour, *suiv;
      struct bap_iterator_indexed_access i_cour;

      sorted = false;
      cour = &qs->Ti;
      suiv = &qs->Tj;
      for (i = r - 1; !sorted && i >= l; i--)
        {
          sorted = true;
          bap_goto_itermon_mint_hp (&qs->j, l);
          bap_term_itermon_mint_hp (suiv, &qs->j);
          for (j = l; j <= i; j++)
            {
              BA0_SWAP (struct bav_term *,
                  cour,
                  suiv);
              bap_set_iterator_indexed_access (&i_cour, &qs->j.iter_ix);
              bap_next_itermon_mint_hp (&qs->j);
              bap_term_itermon_mint_hp (suiv, &qs->j);
              code = bav_compare_term (cour, suiv);
              if (code == ba0_lt)
                {
                  BA0_SWAP (struct bav_term *,
                      cour,
                      suiv);
                  bap_swapindex_iterator_indexed_access (&i_cour,
                      &qs->j.iter_ix);
                  sorted = false;
                }
            }
        }
    }
}

/*
 * texinfo: bap_sort_polynom_mint_hp
 * Assign to @var{R} the polynomial @var{A}, sorted w.r.t. the 
 * current ordering. The resulting polynomial @var{R} is readonly
 * and has indexed access. The polynomial @var{A} is left unchanged.
 */

BAP_DLL void
bap_sort_polynom_mint_hp (
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A)
{
  struct bap_creator_indexed_access crea;
  struct bap_iterator_indexed_access iter;
  struct quicksort_data qs;
  ba0_int_p i, offset, nbmonA;
  struct ba0_mark M;

  nbmonA = bap_nbmon_polynom_mint_hp (A);
  if (nbmonA == 0)
    {
      bap_set_polynom_zero_mint_hp (R);
      return;
    }

  if (A == R)
    {
      if (A->access == bap_sequential_monom_access)
        {
          offset = A->seq.first;
          A->access = bap_indexed_monom_access;
          bap_realloc_indexed_access (&A->ind, nbmonA);
          bap_begin_creator_indexed_access (&crea, &A->ind);
          for (i = 0; i < nbmonA; i++)
            bap_write_creator_indexed_access (&crea, offset + i);
          bap_close_creator_indexed_access (&crea);
        }
    }
  else
    {
      R->clot = A->clot;
      R->access = bap_indexed_monom_access;
      bap_realloc_indexed_access (&R->ind, nbmonA);
      bap_begin_creator_indexed_access (&crea, &R->ind);
      if (A->access == bap_sequential_monom_access)
        {
          offset = A->seq.first;
          for (i = 0; i < nbmonA; i++)
            bap_write_creator_indexed_access (&crea, offset + i);
        }
      else
        {
          bap_begin_iterator_indexed_access (&iter, &A->ind);
          for (i = 0; i < nbmonA; i++)
            bap_write_creator_indexed_access (&crea,
                bap_read_iterator_indexed_access (&iter));
        }
      bap_close_creator_indexed_access (&crea);
      bap_set_termstripper (&R->tstrip, &A->tstrip);
      bav_set_term (&R->total_rank, &A->total_rank);
    }
  bav_sort_term (&R->total_rank);
  bap_append_termstripper (&R->tstrip, (struct bav_variable *) -1,
      bav_current_ordering ());

  ba0_record (&M);
  bap_init_quicksort_data (&qs, R);
  quicksort_mint_hp (0, nbmonA - 1, &qs);
  ba0_restore (&M);
  R->readonly = true;
}

/*
 * texinfo: bap_physort_polynom_mint_hp
 * This low-level function sorts the polynomial @var{A} w.r.t.
 * the current ordering. The polynomial @var{A} is supposed to
 * have sequential access.
 */

BAP_DLL void
bap_physort_polynom_mint_hp (
    struct bap_polynom_mint_hp *A)
{
  if (A->access == bap_indexed_monom_access)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  bap_sort_clot_mint_hp (A->clot, A->seq.first, A->seq.after);
  bav_sort_term (&A->total_rank);
  bap_change_ordering_termstripper (&A->tstrip, bav_current_ordering ());
  bap_change_ordering_clot_mint_hp (A->clot, bav_current_ordering ());
}

/* 
 * texinfo: bap_nbmon_polynom_mint_hp
 * Return the number of monomials present in @var{A}.
 */

BAP_DLL ba0_int_p
bap_nbmon_polynom_mint_hp (
    struct bap_polynom_mint_hp *A)
{
  if (A->access == bap_sequential_monom_access)
    return A->seq.after - A->seq.first;
  else
    return A->ind.size;
}

/*
 * texinfo: bap_leader_polynom_mint_hp
 * Return the leading variable of @var{A}.
 * Exception @code{BAP_ERRCST} is raised if @var{A} does not
 * depend on any variable.
 */

BAP_DLL struct bav_variable *
bap_leader_polynom_mint_hp (
    struct bap_polynom_mint_hp *A)
{
  if (bap_is_numeric_polynom_mint_hp (A))
    BA0_RAISE_EXCEPTION (BAP_ERRCST);
  return bav_leader_term (&A->total_rank);
}

/*
 * texinfo: bap_rank_polynom_mint_hp
 * Return the leading rank of @var{A}.
 */

BAP_DLL struct bav_rank
bap_rank_polynom_mint_hp (
    struct bap_polynom_mint_hp *A)
{
  struct bav_rank rg;

  if (bap_is_zero_polynom_mint_hp (A))
    rg = bav_zero_rank ();
  else if (bav_is_one_term (&A->total_rank))
    rg = bav_constant_rank ();
  else
    rg = bav_leading_rank_term (&A->total_rank);
  return rg;
}

/*
 * texinfo: bap_leading_degree_polynom_mint_hp
 * Return the degree of @var{A} w.r.t. its leading variable.
 * Exception @code{BAP_ERRCST} is raised if @var{A} does not
 * depend on any variable.
 */

BAP_DLL bav_Idegree
bap_leading_degree_polynom_mint_hp (
    struct bap_polynom_mint_hp *A)
{
  if (bap_is_numeric_polynom_mint_hp (A))
    BA0_RAISE_EXCEPTION (BAP_ERRCST);
  return bav_leading_degree_term (&A->total_rank);
}

/*
 * texinfo: bap_total_order_polynom_mint_hp
 * Return the sum of the orders of all the derivatives @var{A}
 * depends on.
 */

BAP_DLL bav_Iorder
bap_total_order_polynom_mint_hp (
    struct bap_polynom_mint_hp *A)
{
  return bav_total_order_term (&A->total_rank);
}

/*
 * texinfo: bap_minimal_total_rank_polynom_mint_hp
 * Assign to @var{T} the gcd of all the terms occurring in @var{A}.
 * Exception @code{BAP_ERRNUL} is raised if @var{A} is @math{0}.
 */

BAP_DLL void
bap_minimal_total_rank_polynom_mint_hp (
    struct bav_term *T,
    struct bap_polynom_mint_hp *A)
{
  struct bap_itermon_mint_hp iter;
  struct bav_term U;
  struct bav_tableof_variable vars;
  struct ba0_tableof_int_p degs;
  struct bav_variable *v;
  ba0_int_p i, j;
  struct ba0_mark M;

  if (bap_is_zero_polynom_mint_hp (A))
    BA0_RAISE_EXCEPTION (BAP_ERRNUL);

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&U);
  bap_end_itermon_mint_hp (&iter, A);
  bap_term_itermon_mint_hp (&U, &iter);

  if (bav_is_one_term (&U))
    {
      ba0_pull_stack ();
      bav_set_term_one (T);
    }
  else
    {
      ba0_init_table ((struct ba0_table *) &vars);
      ba0_realloc_table ((struct ba0_table *) &vars, A->total_rank.size);
      ba0_init_table ((struct ba0_table *) &degs);
      ba0_realloc_table ((struct ba0_table *) &degs, A->total_rank.size);
      for (i = 0; i < A->total_rank.size; i++)
        {
          vars.tab[i] = A->total_rank.rg[i].var;
          degs.tab[i] = A->total_rank.rg[i].deg;
        }
      vars.size = A->total_rank.size;
      degs.size = A->total_rank.size;

      bap_begin_itermon_mint_hp (&iter, A);
      while (!bap_outof_itermon_mint_hp (&iter))
        {
          bap_term_itermon_mint_hp (&U, &iter);
          i = 0;
          for (j = 0; j < U.size; j++)
            {
              while (vars.tab[i] != U.rg[j].var)
                {
                  degs.tab[i] = 0;
                  i += 1;
                }
              if (degs.tab[i] > U.rg[j].deg)
                degs.tab[i] = U.rg[j].deg;
              i += 1;
            }
          while (i < degs.size)
            {
              degs.tab[i] = 0;
              i += 1;
            }
          bap_next_itermon_mint_hp (&iter);
        }
      ba0_pull_stack ();
      bav_set_term_tableof_variable (T, &vars, &degs);
    }
  ba0_restore (&M);
}

/*
 * texinfo: bap_leading_term_polynom_mint_hp
 * Assign to @var{T} the leading term of @var{A}.
 * Exception @code{BAP_ERRNUL} is raised if @var{A} is @math{0}.
 */

BAP_DLL void
bap_leading_term_polynom_mint_hp (
    struct bav_term *T,
    struct bap_polynom_mint_hp *A)
{
  struct bap_itermon_mint_hp iter;

  if (bap_is_zero_polynom_mint_hp (A))
    BA0_RAISE_EXCEPTION (BAP_ERRNUL);

  bap_begin_itermon_mint_hp (&iter, A);
  bap_term_itermon_mint_hp (T, &iter);
}

/* 
 * texinfo: bap_numeric_initial_polynom_mint_hp
 * Return the address of the coefficient of the leading term
 * of @var{A}.
 * Exception @code{BAP_ERRNUL} is raised if @var{A} is @math{0}.
 */

BAP_DLL ba0_mint_hp_t *
bap_numeric_initial_polynom_mint_hp (
    struct bap_polynom_mint_hp *A)
{
  struct bap_itermon_mint_hp iter;
  ba0_mint_hp_t *c;

  if (bap_is_zero_polynom_mint_hp (A))
    BA0_RAISE_EXCEPTION (BAP_ERRNUL);

  bap_begin_itermon_mint_hp (&iter, A);
  c = bap_coeff_itermon_mint_hp (&iter);

  return c;
}

/*
 * texinfo: bap_initial_and_reductum_polynom_mint_hp
 * Assign to @var{initial} and @var{reductum} the initial
 * and the reductum of @var{A}, in readonly mode.
 * Both parameters are allowed to be the zero pointers.
 * Exception @code{BAP_ERRCST} is raised if @var{A} does not
 * depend on any variable.
 */

BAP_DLL void
bap_initial_and_reductum_polynom_mint_hp (
    struct bap_polynom_mint_hp *initial,
    struct bap_polynom_mint_hp *reductum,
    struct bap_polynom_mint_hp *A)
{
  struct bap_itercoeff_mint_hp iter;

  if (bap_is_numeric_polynom_mint_hp (A))
    BA0_RAISE_EXCEPTION (BAP_ERRCST);
  if ((A == initial && reductum != BAP_NOT_A_POLYNOM_mint_hp) || (A == initial
          && A == reductum))
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);
  bap_begin_itercoeff_mint_hp (&iter, A, bap_leader_polynom_mint_hp (A));
  if (initial != BAP_NOT_A_POLYNOM_mint_hp)
    bap_coeff_itercoeff_mint_hp (initial, &iter);
  if (reductum != BAP_NOT_A_POLYNOM_mint_hp)
    {
      bap_next_itermon_mint_hp (&iter.fin);
      bap_reductum_itermon_mint_hp (&iter.fin, reductum);
    }
}

/*
 * texinfo: bap_initial_polynom_mint_hp
 * Assign to @var{initial} the initial
 * of @var{A}, in readonly mode.
 * Exception @code{BAP_ERRCST} is raised if @var{A} does not
 * depend on any variable.
 */

BAP_DLL void
bap_initial_polynom_mint_hp (
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A)
{
  bap_initial_and_reductum_polynom_mint_hp (R, BAP_NOT_A_POLYNOM_mint_hp, A);
}

/*
 * texinfo: bap_reductum_polynom_mint_hp
 * Assign to @var{reductum} the reductum
 * of @var{A}, in readonly mode.
 * Exception @code{BAP_ERRCST} is raised if @var{A} does not
 * depend on any variable.
 */

BAP_DLL void
bap_reductum_polynom_mint_hp (
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A)
{
  bap_initial_and_reductum_polynom_mint_hp (BAP_NOT_A_POLYNOM_mint_hp, R, A);
}

/*
 * texinfo: bap_initial_and_reductum2_polynom_mint_hp
 * Variant of @code{bap_initial_and_reductum_polynom_mint_hp}
 * where the variable @var{v} w.r.t. which the initial and
 * the reductum are defined is specified.
 * This variable is supposed to be greater than or equal to the leader of A.
 * The polynomial @var{A} is allowed to be numeric.
 * The resulting polynomials are readonly.
 */

BAP_DLL void
bap_initial_and_reductum2_polynom_mint_hp (
    struct bap_polynom_mint_hp *initial,
    struct bap_polynom_mint_hp *reductum,
    struct bap_polynom_mint_hp *A,
    struct bav_variable *v)
{
  if (bap_is_numeric_polynom_mint_hp (A) || bap_leader_polynom_mint_hp (A) != v)
    {
      if (initial != BAP_NOT_A_POLYNOM_mint_hp)
        bap_set_readonly_polynom_mint_hp (initial, A);
      if (reductum != BAP_NOT_A_POLYNOM_mint_hp)
        bap_set_polynom_zero_mint_hp (reductum);
    }
  else
    bap_initial_and_reductum_polynom_mint_hp (initial, reductum, A);
}

/*
 * texinfo: bap_initial2_polynom_mint_hp
 * Variant of @code{bap_initial_polynom_mint_hp}.
 * See @code{bap_initial_and_reductum2_polynom_mint_hp}.
 */

BAP_DLL void
bap_initial2_polynom_mint_hp (
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A,
    struct bav_variable *v)
{
  bap_initial_and_reductum2_polynom_mint_hp (R, BAP_NOT_A_POLYNOM_mint_hp, A, v);
}

/*
 * texinfo: bap_reductum2_polynom_mint_hp
 * Variant of @code{bap_reductum_polynom_mint_hp}.
 * See @code{bap_initial_and_reductum2_polynom_mint_hp}.
 */

BAP_DLL void
bap_reductum2_polynom_mint_hp (
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A,
    struct bav_variable *v)
{
  bap_initial_and_reductum2_polynom_mint_hp (BAP_NOT_A_POLYNOM_mint_hp, R, A, v);
}

/*
 * texinfo: bap_coeff2_polynom_mint_hp
 * Assign to @var{R} the coefficient of @math{v^d} in @var{A}.
 * The polynomial @var{R} is readonly.
 * The variable @var{v} is supposed too be greater than or
 * equal to the leader of @var{A}.
 */

BAP_DLL void
bap_coeff2_polynom_mint_hp (
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A,
    struct bav_variable *v,
    bav_Idegree d)
{
  if (bap_is_numeric_polynom_mint_hp (A) || bap_leader_polynom_mint_hp (A) != v)
    {
      if (d == 0)
        bap_set_readonly_polynom_mint_hp (R, A);
      else
        bap_set_polynom_zero_mint_hp (R);
    }
  else
    {
      struct bap_itercoeff_mint_hp iter;
      struct bav_term T;
      struct ba0_mark M;

      ba0_push_another_stack ();
      ba0_record (&M);
      bav_init_term (&T);
      bav_set_term_variable (&T, v, d);
      ba0_pull_stack ();

      bap_begin_itercoeff_mint_hp (&iter, A, v);
      bap_seek_coeff_itercoeff_mint_hp (R, &iter, &T);
      ba0_restore (&M);
    }
}

/*
 * texinfo: bap_lcoeff_and_reductum_polynom_mint_hp
 * Assign to @var{lcoeff} and @var{reductum} the leading coefficient
 * and the reductum of @var{A} w.r.t. @var{v} (or w.r.t. the leading
 * variable of @var{A} if @var{v} is @code{BAV_NOT_A_VARIABLE}.
 * The variable @var{v} is not required to be greater than
 * or equal to the leading variable of @var{A}.
 * The resulting polynomials are not readonly.
 * They are disjoint from @var{A}.
 * Exception @code{BA0_ERRALG} is raised if @var{lcoeff} or
 * @var{reductum} has readonly mode.
 */

BAP_DLL void
bap_lcoeff_and_reductum_polynom_mint_hp (
    struct bap_polynom_mint_hp *lcoeff,
    struct bap_polynom_mint_hp *reductum,
    struct bap_polynom_mint_hp *A,
    struct bav_variable *v)
{
  struct bap_polynom_mint_hp AA, lc, red;
  struct ba0_mark M;

  if ((lcoeff != BAP_NOT_A_POLYNOM_mint_hp && lcoeff->readonly)
      || (reductum != BAP_NOT_A_POLYNOM_mint_hp && reductum->readonly))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (bap_is_numeric_polynom_mint_hp (A) || (v != BAV_NOT_A_VARIABLE
          && v != bap_leader_polynom_mint_hp (A)))
    {
      if (!bap_depend_polynom_mint_hp (A, v))
        {
          if (lcoeff != BAP_NOT_A_POLYNOM_mint_hp && lcoeff != A)
            bap_set_polynom_mint_hp (lcoeff, A);
          if (reductum != BAP_NOT_A_POLYNOM_mint_hp)
            bap_set_polynom_zero_mint_hp (reductum);
        }
      else
        {
          bav_Iordering r;

          ba0_push_another_stack ();
          ba0_record (&M);

          r = bav_R_copy_ordering (bav_current_ordering ());
          bav_push_ordering (r);
          bav_R_set_maximal_variable (v);

          bap_init_readonly_polynom_mint_hp (&AA);
          bap_init_readonly_polynom_mint_hp (&lc);
          bap_init_readonly_polynom_mint_hp (&red);
          bap_sort_polynom_mint_hp (&AA, A);
          bap_initial_and_reductum_polynom_mint_hp (lcoeff !=
              BAP_NOT_A_POLYNOM_mint_hp ? &lc : BAP_NOT_A_POLYNOM_mint_hp,
              reductum !=
              BAP_NOT_A_POLYNOM_mint_hp ? &red : BAP_NOT_A_POLYNOM_mint_hp, &AA);

          bav_pull_ordering ();
          ba0_pull_stack ();
          if (lcoeff != BAP_NOT_A_POLYNOM_mint_hp)
            bap_set_polynom_mint_hp (lcoeff, &lc);
          if (reductum != BAP_NOT_A_POLYNOM_mint_hp)
            bap_set_polynom_mint_hp (reductum, &red);

          bav_R_free_ordering (r);
          ba0_restore (&M);
        }
    }
  else
    {
      ba0_push_another_stack ();
      ba0_record (&M);

      bap_init_readonly_polynom_mint_hp (&lc);
      bap_init_readonly_polynom_mint_hp (&red);
      bap_initial_and_reductum_polynom_mint_hp (lcoeff !=
          BAP_NOT_A_POLYNOM_mint_hp ? &lc : BAP_NOT_A_POLYNOM_mint_hp,
          reductum != BAP_NOT_A_POLYNOM_mint_hp ? &red : BAP_NOT_A_POLYNOM_mint_hp,
          A);

      ba0_pull_stack ();
      if (lcoeff != BAP_NOT_A_POLYNOM_mint_hp)
        bap_set_polynom_mint_hp (lcoeff, &lc);
      if (reductum != BAP_NOT_A_POLYNOM_mint_hp)
        bap_set_polynom_mint_hp (reductum, &red);

      ba0_restore (&M);
    }
}

/*
 * texinfo: bap_lcoeff_polynom_mint_hp
 * Variant of @code{bap_lcoeff_and_reductum_polynom_mint_hp}
 * for the leading coefficient only.
 */

BAP_DLL void
bap_lcoeff_polynom_mint_hp (
    struct bap_polynom_mint_hp *lcoeff,
    struct bap_polynom_mint_hp *A,
    struct bav_variable *v)
{
  bap_lcoeff_and_reductum_polynom_mint_hp (lcoeff, BAP_NOT_A_POLYNOM_mint_hp, A, v);
}

/*
 * texinfo: bap_coeff_and_reductum_polynom_mint_hp
 * Assign to @var{C} the coefficient of @var{v^d} in @var{A}
 * (the leading variable of @var{A} is taken if @var{v} is 
 * @code{BAV_NOT_A_VARIABLE}).
 * Assign to @var{R} the polynomial @math{A - C\,v^d}.
 * The variable @var{v} is not required to be greater than
 * or equal to the leading variable of @var{A}.
 * The resulting polynomials are not readonly.
 * They are disjoint from @var{A}.
 * Exception @code{BA0_ERRALG} is raised one of them has readonly mode.
 */

/*
   Write A = 

      a_e v^e + ... + a_{d+1} v^{d+1} + a_d v^d + a_{d-1} v^{d-1} + ... + a_0

   Assigns a_d to C and 
	   a_e v^e + ... + a_{d+1} v^{d+1} + a_{d-1} v^{d-1} + ... + a_0 to R.

   Polynomials C and R may be zero.
*/

BAP_DLL void
bap_coeff_and_reductum_polynom_mint_hp (
    struct bap_polynom_mint_hp *C,
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A,
    struct bav_variable *v,
    bav_Idegree d)
{
  struct bap_itermon_mint_hp iter;
  struct bap_creator_mint_hp creaC, creaR;
  struct bap_polynom_mint_hp CC, RR;
  struct bav_term T, U;
  struct ba0_mark M;
  ba0_int_p i, nbmon;

  if (R == (struct bap_polynom_mint_hp *) 0)
    {
      bap_coeff_polynom_mint_hp (C, A, v, d);
      return;
    }
  else if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  if (C != (struct bap_polynom_mint_hp *) 0 && C->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  if (C == R)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (bap_is_numeric_polynom_mint_hp (A) || (v != BAV_NOT_A_VARIABLE
          && !bap_depend_polynom_mint_hp (A, v)))
    {
      if (d == 0)
        {
          if (C != A && C != (struct bap_polynom_mint_hp *) 0)
            bap_set_polynom_mint_hp (C, A);
          bap_set_polynom_zero_mint_hp (R);
        }
      else
        {
          if (C != (struct bap_polynom_mint_hp *) 0)
            bap_set_polynom_zero_mint_hp (C);
          if (R != A)
            bap_set_polynom_mint_hp (R, A);
        }
      return;
    }

  nbmon = bap_nbmon_polynom_mint_hp (A);

  ba0_push_another_stack ();
  ba0_record (&M);
  bav_init_term (&T);
  bav_init_term (&U);

  if (C != A && R != A)
    {
      ba0_pull_stack ();
      if (C != (struct bap_polynom_mint_hp *) 0)
        bap_begin_creator_mint_hp (&creaC, C, &A->total_rank,
            bap_approx_total_rank, nbmon / 2 + 1);
      bap_begin_creator_mint_hp (&creaR, R, &A->total_rank, bap_approx_total_rank,
          nbmon / 2 + 1);
      ba0_push_another_stack ();
    }
  else
    {
      bap_init_polynom_mint_hp (&CC);
      bap_init_polynom_mint_hp (&RR);
      if (C != (struct bap_polynom_mint_hp *) 0)
        bap_begin_creator_mint_hp (&creaC, &CC, &A->total_rank,
            bap_approx_total_rank, nbmon / 2 + 1);
      bap_begin_creator_mint_hp (&creaR, &RR, &A->total_rank,
          bap_approx_total_rank, nbmon / 2 + 1);
    }

  bap_begin_itermon_mint_hp (&iter, A);
  while (!bap_outof_itermon_mint_hp (&iter))
    {
      bap_term_itermon_mint_hp (&T, &iter);
      i = 0;
      while (i < T.size && T.rg[i].var != v)
        i++;
      if ((i < T.size && T.rg[i].deg == d) || (i == T.size && d == 0))
        {
          bav_exquo_term_variable (&U, &T, v, d);
          if (C != A && R != A)
            {
              ba0_pull_stack ();
              if (C != (struct bap_polynom_mint_hp *) 0)
                bap_write_creator_mint_hp (&creaC, &U,
                    *bap_coeff_itermon_mint_hp (&iter));
              ba0_push_another_stack ();
            }
          else
            bap_write_creator_mint_hp (&creaC, &U,
                *bap_coeff_itermon_mint_hp (&iter));
        }
      else
        {
          if (C != A && R != A)
            {
              ba0_pull_stack ();
              bap_write_creator_mint_hp (&creaR, &T,
                  *bap_coeff_itermon_mint_hp (&iter));
              ba0_push_another_stack ();
            }
          else
            bap_write_creator_mint_hp (&creaR, &T,
                *bap_coeff_itermon_mint_hp (&iter));
        }
      bap_next_itermon_mint_hp (&iter);
    }
  bap_close_itermon_mint_hp (&iter);

  if (C != A && R != A)
    {
      ba0_pull_stack ();
      if (C != (struct bap_polynom_mint_hp *) 0)
        bap_close_creator_mint_hp (&creaC);
      bap_close_creator_mint_hp (&creaR);
      ba0_push_another_stack ();
    }
  else
    {
      if (C != (struct bap_polynom_mint_hp *) 0)
        bap_close_creator_mint_hp (&creaC);
      bap_close_creator_mint_hp (&creaR);
    }

  ba0_pull_stack ();
  if (C == A || R == A)
    {
      if (C != (struct bap_polynom_mint_hp *) 0)
        bap_set_polynom_mint_hp (C, &CC);
      bap_set_polynom_mint_hp (R, &RR);
    }
  ba0_restore (&M);
}

/* 
 * texinfo: bap_degree_polynom_mint_hp
 * Return the degree of @var{A} w.r.t. @var{v}.
 * Return @math{-1} if @var{A} is @math{0}.
 */

BAP_DLL bav_Idegree
bap_degree_polynom_mint_hp (
    struct bap_polynom_mint_hp *A,
    struct bav_variable *v)
{
  ba0_int_p i;

  if (bap_is_zero_polynom_mint_hp (A))
    return -1;
/*
   On cherche si v figure dans le total_rank de A (indice i)
*/
  i = 0;
  while (i < A->total_rank.size && A->total_rank.rg[i].var != v)
    i++;
  return i == A->total_rank.size ? 0 : A->total_rank.rg[i].deg;
}

/*
 * texinfo: bap_coeff_polynom_mint_hp
 * Assign to @var{C} the coefficient of @var{v^d} in @var{A}
 * (the leading variable of @var{A} is taken if @var{v} is 
 * @code{BAV_NOT_A_VARIABLE}).
 * The variable @var{v} is not required to be greater than
 * or equal to the leading variable of @var{A}.
 * The resulting polynomial is not readonly.
 * It is disjoint from @var{A}.
 * Exception @code{BA0_ERRALG} is raised if it has readonly mode.
 */

BAP_DLL void
bap_coeff_polynom_mint_hp (
    struct bap_polynom_mint_hp *C,
    struct bap_polynom_mint_hp *A,
    struct bav_variable *v,
    bav_Idegree d)
{
  struct bap_itercoeff_mint_hp iter;
  struct bap_polynom_mint_hp AA, coeff;
  struct bav_term T;
  struct ba0_mark M;

  if (C->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  if (bap_is_numeric_polynom_mint_hp (A) || (v != BAV_NOT_A_VARIABLE
          && v != bap_leader_polynom_mint_hp (A)))
    {
      if (!bap_depend_polynom_mint_hp (A, v))
        {
          if (d == 0)
            {
              if (C != A)
                bap_set_polynom_mint_hp (C, A);
            }
          else
            bap_set_polynom_zero_mint_hp (C);
        }
      else
        {
          bav_Iordering r;

          ba0_push_another_stack ();
          ba0_record (&M);

          r = bav_R_copy_ordering (bav_current_ordering ());
          bav_push_ordering (r);
          bav_R_set_maximal_variable (v);

          bap_init_readonly_polynom_mint_hp (&AA);
          bap_init_readonly_polynom_mint_hp (&coeff);
          bap_sort_polynom_mint_hp (&AA, A);
          bap_begin_itercoeff_mint_hp (&iter, &AA, v);
          bav_init_term (&T);
          bav_set_term_variable (&T, v, d);
          bap_seek_coeff_itercoeff_mint_hp (&coeff, &iter, &T);

          bav_pull_ordering ();
          ba0_pull_stack ();
          bap_set_polynom_mint_hp (C, &coeff);

          bav_R_free_ordering (r);
          ba0_restore (&M);
        }
    }
  else
    {
      ba0_push_another_stack ();
      ba0_record (&M);

      bap_init_readonly_polynom_mint_hp (&coeff);
      bav_init_term (&T);
      bav_set_term_variable (&T, bap_leader_polynom_mint_hp (A), d);
      bap_begin_itercoeff_mint_hp (&iter, A, bap_leader_polynom_mint_hp (A));
      bap_seek_coeff_itercoeff_mint_hp (&coeff, &iter, &T);

      ba0_pull_stack ();
      bap_set_polynom_mint_hp (C, &coeff);

      ba0_restore (&M);
    }
}

/*
 * texinfo: bap_total_degree_polynom_mint_hp
 * Return the total degree of @var{A}.
 * Return @math{-1} if @var{A} is @math{0}.
 */

BAP_DLL bav_Idegree
bap_total_degree_polynom_mint_hp (
    struct bap_polynom_mint_hp *A)
{
  return bav_total_degree_term (&A->total_rank);
}

/*
 * texinfo: bap_replace_initial_polynom_mint_hp
 * Assign to @var{R} the polynomial obtained by replacing the
 * initial of @var{A} by @var{C}.
 * Exception @code{BAP_ERRCST} is raised if @var{A} is numeric.
 * xception @code{BA0_ERRALG} is raised if @var{R} is readonly.
 */

BAP_DLL void
bap_replace_initial_polynom_mint_hp (
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A,
    struct bap_polynom_mint_hp *C)
{
  struct bap_creator_mint_hp crea;
  struct bap_itercoeff_mint_hp iter;
  struct bap_itermon_mint_hp itermon;
  struct bap_polynom_mint_hp *P;
  struct bav_term T;
  struct bav_rank rg;
  ba0_mint_hp_t *lc;
  struct ba0_mark M;

  if (bap_is_numeric_polynom_mint_hp (A))
    BA0_RAISE_EXCEPTION (BAP_ERRCST);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&T);
  bav_set_term (&T, &A->total_rank);
  bav_lcm_term (&T, &T, &C->total_rank);

  P = bap_new_polynom_mint_hp ();
  bap_begin_creator_mint_hp (&crea, P, &T, bap_approx_total_rank,
      bap_nbmon_polynom_mint_hp (A) + bap_nbmon_polynom_mint_hp (C));

  rg = bap_rank_polynom_mint_hp (A);
  bap_begin_itermon_mint_hp (&itermon, C);
  while (!bap_outof_itermon_mint_hp (&itermon))
    {
      bap_term_itermon_mint_hp (&T, &itermon);
      bav_mul_term_rank (&T, &T, &rg);
      lc = bap_coeff_itermon_mint_hp (&itermon);
      bap_write_creator_mint_hp (&crea, &T, *lc);
      bap_next_itermon_mint_hp (&itermon);
    }
  bap_begin_itercoeff_mint_hp (&iter, A, bap_leader_polynom_mint_hp (A));
  bap_next_itermon_mint_hp (&iter.fin);
  while (!bap_outof_itermon_mint_hp (&iter.fin))
    {
      bap_term_itermon_mint_hp (&T, &iter.fin);
      lc = bap_coeff_itermon_mint_hp (&iter.fin);
      bap_write_creator_mint_hp (&crea, &T, *lc);
      bap_next_itermon_mint_hp (&iter.fin);
    }
  bap_close_creator_mint_hp (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mint_hp (R, P);
  ba0_restore (&M);
}

/*
 * texinfo: bap_separant_polynom_mint_hp
 * Assign to @var{R} the separant of @var{A}.
 * Exception @code{BAP_ERRCST} is raised if @var{A} is numeric.
 * Exception @code{BA0_ERRALG} is raised if @var{R} is readonly.
 */

BAP_DLL void
bap_separant_polynom_mint_hp (
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A)
{
  struct bap_itermon_mint_hp iter;
  struct bap_creator_mint_hp crea;
  struct bap_polynom_mint_hp *P;
  ba0_mint_hp_t c;
  struct bav_term T;
  struct bav_rank rg;
  struct ba0_mark M;

  if (bap_is_numeric_polynom_mint_hp (A))
    BA0_RAISE_EXCEPTION (BAP_ERRCST);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mint_hp_init (c);
  bav_init_term (&T);
  bav_set_term (&T, &A->total_rank);

  rg = bav_leading_rank_term (&T);

  if (T.rg[0].deg == 1)
    bav_shift_term (&T, &T);
  else
    T.rg[0].deg -= 1;

  P = bap_new_polynom_mint_hp ();
  bap_begin_creator_mint_hp (&crea, P, &T, bap_approx_total_rank,
      bap_nbmon_polynom_mint_hp (A));

  bap_begin_itermon_mint_hp (&iter, A);
  bap_term_itermon_mint_hp (&T, &iter);
  for (;;)
    {
      if (T.rg[0].deg == 1)
        {
          bav_shift_term (&T, &T);
          bap_write_creator_mint_hp (&crea, &T, *bap_coeff_itermon_mint_hp (&iter));
        }
      else
        {
          ba0_mint_hp_mul_ui (c, *bap_coeff_itermon_mint_hp (&iter), T.rg[0].deg);
          T.rg[0].deg -= 1;
          bap_write_creator_mint_hp (&crea, &T, c);
        }
      bap_next_itermon_mint_hp (&iter);
      if (bap_outof_itermon_mint_hp (&iter))
        break;
      bap_term_itermon_mint_hp (&T, &iter);
      if (bav_is_one_term (&T) || bav_leader_term (&T) != rg.var)
        break;
    }
  bap_close_creator_mint_hp (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mint_hp (R, P);
  ba0_restore (&M);
}

/*
 * texinfo: bap_separant2_polynom_mint_hp
 * Assign to @var{R} the separant of @var{A} w.r.t. @var{v}.
 * Exception @code{BAP_ERRCST} is raised if @var{A} is numeric.
 * xception @code{BA0_ERRALG} is raised if @var{R} is readonly.
 */

BAP_DLL void
bap_separant2_polynom_mint_hp (
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A,
    struct bav_variable *v)
{
  struct bap_polynom_mint_hp B;
  bav_Iordering r;
  struct ba0_mark M;

  if (!bap_depend_polynom_mint_hp (A, v))
    bap_set_polynom_zero_mint_hp (R);
  else if (bap_leader_polynom_mint_hp (A) == v)
    bap_separant_polynom_mint_hp (R, A);
  else
    {
      ba0_push_another_stack ();
      ba0_record (&M);
      r = bav_R_copy_ordering (bav_current_ordering ());
      bav_push_ordering (r);
      bav_R_set_maximal_variable (v);
      bap_init_readonly_polynom_mint_hp (&B);
      bap_sort_polynom_mint_hp (&B, A);
      ba0_pull_stack ();
      bap_separant_polynom_mint_hp (R, &B);
      bav_pull_ordering ();
      bap_physort_polynom_mint_hp (R);
      bav_R_free_ordering (r);
      ba0_restore (&M);
    }
}

/*
 * Sorting tables of polynomials
 */
/*
 * For qsort. See below
 */

static int
comp_polynom_ascending (
    const void *x,
    const void *y)
{
  struct bap_polynom_mint_hp *A = *(struct bap_polynom_mint_hp * *) x;
  struct bap_polynom_mint_hp *B = *(struct bap_polynom_mint_hp * *) y;
  struct bav_term TA, TB;
  struct ba0_mark M;
  enum ba0_compare_code code;

  ba0_record (&M);
  bav_init_term (&TA);
  bav_init_term (&TB);
  bap_leading_term_polynom_mint_hp (&TA, A);
  bap_leading_term_polynom_mint_hp (&TB, B);
  code = bav_compare_term (&TA, &TB);
  ba0_restore (&M);

  if (code == ba0_lt)
    return -1;
  else if (code == ba0_eq)
    return 0;
  else
    return 1;
}

static int
comp_polynom_descending (
    const void *x,
    const void *y)
{
  struct bap_polynom_mint_hp *A = *(struct bap_polynom_mint_hp * *) x;
  struct bap_polynom_mint_hp *B = *(struct bap_polynom_mint_hp * *) y;
  struct bav_term TA, TB;
  struct ba0_mark M;
  enum ba0_compare_code code;

  ba0_record (&M);
  bav_init_term (&TA);
  bav_init_term (&TB);
  bap_leading_term_polynom_mint_hp (&TA, A);
  bap_leading_term_polynom_mint_hp (&TB, B);
  code = bav_compare_term (&TA, &TB);
  ba0_restore (&M);

  if (code == ba0_gt)
    return -1;
  else if (code == ba0_eq)
    return 0;
  else
    return 1;
}

/*
 * texinfo: bap_sort_tableof_polynom_mint_hp
 * Sort @var{T} in ascending or descending order 
 * depending on @var{mode}.
 */

BAP_DLL void
bap_sort_tableof_polynom_mint_hp (
    struct bap_tableof_polynom_mint_hp *T,
    enum ba0_sort_mode mode)
{
  switch (mode)
    {
    case ba0_descending_mode:
      qsort (T->tab, T->size, sizeof (struct bap_polynom_mint_hp *),
          &comp_polynom_descending);
      break;
    case ba0_ascending_mode:
      qsort (T->tab, T->size, sizeof (struct bap_polynom_mint_hp *),
          &comp_polynom_ascending);
      break;
    }
}

/****************************************************************************
 GARBAGE COLLECTOR
 ****************************************************************************/

/*
 * Readonly static data
 */

static char _struct_polynom[] = "struct bap_polynom_mint_hp";
static char _struct_polynom_rang[] = "struct bap_polynom_mint_hp *->total_rank";

BAP_DLL ba0_int_p
bap_garbage1_polynom_mint_hp (
    void *AA,
    enum ba0_garbage_code code)
{
  struct bap_polynom_mint_hp *A = (struct bap_polynom_mint_hp *) AA;
  ba0_int_p n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (A, sizeof (struct bap_polynom_mint_hp),
        _struct_polynom);

  n += bap_garbage1_clot_mint_hp (A->clot, ba0_isolated);

  if (A->total_rank.rg != (struct bav_rank *) 0)
    n += ba0_new_gc_info (A->total_rank.rg,
        sizeof (struct bav_rank) * A->total_rank.alloc, _struct_polynom_rang);

  n += bap_garbage1_indexed_access (&A->ind, ba0_embedded);

  return n;
}

BAP_DLL void *
bap_garbage2_polynom_mint_hp (
    void *AA,
    enum ba0_garbage_code code)
{
  struct bap_polynom_mint_hp *A;

  if (code == ba0_isolated)
    A = (struct bap_polynom_mint_hp *) ba0_new_addr_gc_info (AA, _struct_polynom);
  else
    A = (struct bap_polynom_mint_hp *) AA;

  A->clot =
      (struct bap_clot_mint_hp *) bap_garbage2_clot_mint_hp (A->clot, ba0_isolated);

  if (A->total_rank.rg != (struct bav_rank *) 0)
    A->total_rank.rg =
        (struct bav_rank *) ba0_new_addr_gc_info (A->total_rank.rg,
        _struct_polynom_rang);

  bap_garbage2_indexed_access (&A->ind, ba0_embedded);

  return A;
}

BAP_DLL void *
bap_copy_polynom_mint_hp (
    void *AA)
{
  struct bap_polynom_mint_hp *A = (struct bap_polynom_mint_hp *) AA;
  struct bap_polynom_mint_hp *B;

  B = bap_new_polynom_mint_hp ();
  bap_set_polynom_mint_hp (B, A);
  return B;
}

/*
 * texinfo: bap_sizeof_polynom_mint_hp
 * Return the number of bytes used to store @var{F}.
 * If @var{code} is @code{ba0_embedded} then @var{F} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account.
 */

BAP_DLL unsigned ba0_int_p
bap_sizeof_polynom_mint_hp (
    struct bap_polynom_mint_hp *F,
    enum ba0_garbage_code code)
{
  struct bap_polynom_mint_hp *P, Q;
  struct ba0_mark A;
  struct ba0_mark B;
  unsigned ba0_int_p size;
/*
 * To be improved!
 */
  ba0_record (&A);
  if (code == ba0_isolated)
    {
      P = bap_new_polynom_mint_hp ();
      bap_set_polynom_mint_hp (P, F);
    }
  else
    {
      bap_init_polynom_mint_hp (&Q);
      bap_set_polynom_mint_hp (&Q, F);
    }
  ba0_record (&B);
  size = ba0_range_mark (&A, &B);
  ba0_restore (&A);
  return size;
}

/*
 * texinfo: bap_switch_ring_polynom_mint_hp
 * Apply @code{bav_switch_ring_variable} over all the variables occurring
 * in @var{A}. The polynomial @var{A} is modified.
 * This low level function should be used in conjunction with
 * @code{bav_set_differential_ring}: if @var{R} is a ring obtained by
 * application of @code{bav_set_differential_ring} to the ring @var{A} 
 * refers to, then this function transforms @var{A} as a polynomial of @var{R}.
 */

BAP_DLL void
bap_switch_ring_polynom_mint_hp (
    struct bap_polynom_mint_hp *A,
    struct bav_differential_ring *R)
{
  bav_switch_ring_term (&A->total_rank, R);
  bap_switch_ring_termstripper (&A->tstrip, R);
  if (A->clot)
    bap_switch_ring_clot_mint_hp (A->clot, R);
}

#undef BAD_FLAG_mint_hp
