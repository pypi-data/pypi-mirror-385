#include "bap_polynom_mpz.h"
#include "bap_add_polynom_mpz.h"
#include "bap_creator_mpz.h"
#include "bap_itermon_mpz.h"
#include "bap_itercoeff_mpz.h"
#include "bap__check_mpz.h"
#include "bap_product_mpz.h"
#include "bap_geobucket_mpz.h"

#define BAD_FLAG_mpz

/*************************************************************************
 All functions parameterized by a clot are static
 *************************************************************************/

static void
bap_init_polynom_clot_mpz (
    struct bap_polynom_mpz *A,
    struct bap_clot_mpz *C)
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
 * texinfo: bap_init_polynom_mpz
 * Initialize @var{A} to @math{0}.
 */

BAP_DLL void
bap_init_polynom_mpz (
    struct bap_polynom_mpz *A)
{
  struct bav_term T;
  struct bap_clot_mpz *C;

  bav_init_term (&T);
  C = bap_new_clot_mpz (&T);
  bap_init_polynom_clot_mpz (A, C);
}

/* 
 * texinfo: bap_init_readonly_polynom_mpz
 * Initialize @var{A} to @math{0} as a readonly polynomial.
 */

BAP_DLL void
bap_init_readonly_polynom_mpz (
    struct bap_polynom_mpz *A)
{
  A->clot = (struct bap_clot_mpz *) 0;
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
 * texinfo: bap_init_polynom_one_mpz
 * Initialize @var{A} to @math{1}.
 */

BAP_DLL void
bap_init_polynom_one_mpz (
    struct bap_polynom_mpz *A)
{
  struct bap_creator_mpz crea;
  struct bav_term T;
  struct bap_clot_mpz *C;
  ba0_mpz_t un;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mpz_init_set_ui (un, (unsigned long int) 1);
  ba0_pull_stack ();

  bav_init_term (&T);
  C = bap_new_clot_mpz (&T);
  bap_init_polynom_clot_mpz (A, C);
  bap_begin_creator_mpz (&crea, A, &T, bap_exact_total_rank, 1);
  bap_write_creator_mpz (&crea, &T, un);
  bap_close_creator_mpz (&crea);
  ba0_restore (&M);
}

/*
 * texinfo: bap_init_polynom_crk_mpz
 * Initialize @var{A} to @math{c\,@var{rg}}.
 * The coefficient @var{c} is allowed to be @math{0}.
 * The rank @var{rg} is allowed to be the rank of zero.
 */

BAP_DLL void
bap_init_polynom_crk_mpz (
    struct bap_polynom_mpz *A,
    ba0_mpz_t c,
    struct bav_rank *rg)
{
  struct bav_term T;
  struct bap_creator_mpz crea;
  struct bap_clot_mpz *C;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  bav_init_term (&T);
  if (!bav_is_zero_rank (rg))
    bav_set_term_rank (&T, rg);
  ba0_pull_stack ();

  C = bap_new_clot_mpz (&T);
  bap_init_polynom_clot_mpz (A, C);
  bap_begin_creator_mpz (&crea, A, &T, bap_exact_total_rank, 1);
  if ((!ba0_mpz_is_zero (c)) || (!bav_is_zero_rank (rg)))
    bap_write_creator_mpz (&crea, &T, c);

  ba0_restore (&M);
  bap_close_creator_mpz (&crea);
}

/****************************************************************************
 NEW

 All clot functions are static
 ****************************************************************************/

static struct bap_polynom_mpz *
bap_new_polynom_clot_mpz (
    struct bap_clot_mpz *C)
{
  struct bap_polynom_mpz *A;

  A = (struct bap_polynom_mpz *) ba0_alloc (sizeof (struct
          bap_polynom_mpz));
  bap_init_polynom_clot_mpz (A, C);
  return A;
}

/*
 * texinfo: bap_new_polynom_mpz
 * Allocate a new polynomial, initialize it and return it.
 */

BAP_DLL struct bap_polynom_mpz *
bap_new_polynom_mpz (
    void)
{
  struct bav_term T;
  struct bap_clot_mpz *C;

  bav_init_term (&T);
  C = bap_new_clot_mpz (&T);
  return bap_new_polynom_clot_mpz (C);
}

/*
 * texinfo: bap_new_readonly_polynom_mpz
 * Allocate a new polynomial, initialize it as a readonly polynomial
 * and return it.
 */

BAP_DLL struct bap_polynom_mpz *
bap_new_readonly_polynom_mpz (
    void)
{
  struct bap_polynom_mpz *A;

  A = (struct bap_polynom_mpz *) ba0_alloc (sizeof (struct
          bap_polynom_mpz));
  bap_init_readonly_polynom_mpz (A);
  return A;
}

/*
 * texinfo: bap_new_polynom_crk_mpz
 * Allocate a new polynomial, initialize it to @math{c\,@var{rg}}
 * and return it. 
 * The coefficient @var{c} is allowed to be @math{0}.
 * The rank @var{rg} is allowed to be the rank of zero.
 */

BAP_DLL struct bap_polynom_mpz *
bap_new_polynom_crk_mpz (
    ba0_mpz_t c,
    struct bav_rank *rg)
{
  struct bav_term T;
  struct bap_creator_mpz crea;
  struct bap_polynom_mpz *A;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  bav_init_term (&T);
  if (!bav_is_zero_rank (rg))
    bav_set_term_rank (&T, rg);
  ba0_pull_stack ();

  A = bap_new_polynom_mpz ();
  bap_begin_creator_mpz (&crea, A, &T, bap_exact_total_rank, 1);
  if ((!ba0_mpz_is_zero (c)) || (!bav_is_zero_rank (rg)))
    bap_write_creator_mpz (&crea, &T, c);

  ba0_restore (&M);

  bap_close_creator_mpz (&crea);
  return A;
}

/* 
 * texinfo: bap_new_polynom_one_mpz
 * Allocate a new polynomial, initialize it to @math{1} and return it.
 */

BAP_DLL struct bap_polynom_mpz *
bap_new_polynom_one_mpz (
    void)
{
  struct bap_polynom_mpz *A;
  ba0_mpz_t c;
  struct ba0_mark M;
  struct bav_rank rg;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mpz_init_set_ui (c, 1);
  ba0_pull_stack ();

  rg = bav_constant_rank ();
  A = bap_new_polynom_crk_mpz (c, &rg);
  ba0_restore (&M);
  return A;
}

/****************************************************************************
 SET
 ****************************************************************************/

/*
 * texinfo: bap_set_polynom_zero_mpz
 * Assign @math{0} to @var{A}.
 * The polynomial @var{A} is allowed to be readonly.
 */

BAP_DLL void
bap_set_polynom_zero_mpz (
    struct bap_polynom_mpz *A)
{
  if (A->access == bap_sequential_monom_access)
    A->seq.after = A->seq.first = 0;
  else
    A->ind.size = 0;
  bav_set_term_one (&A->total_rank);
}

/*
 * texinfo: bap_set_polynom_one_mpz
 * Assign @math{1} to @var{A}.
 * Exception @code{BA0_ERRALG} is raised if @var{A} has readonly mode.
 */

BAP_DLL void
bap_set_polynom_one_mpz (
    struct bap_polynom_mpz *A)
{
  struct bap_creator_mpz crea;
  struct bav_term T;
  ba0_mpz_t c;
  struct ba0_mark M;

  if (A->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mpz_init_set_ui (c, 1);
  bav_init_term (&T);
  ba0_pull_stack ();

  bap_begin_creator_mpz (&crea, A, &T, bap_exact_total_rank, 1);
  bap_write_creator_mpz (&crea, &T, c);
  bap_close_creator_mpz (&crea);

  ba0_restore (&M);
}

/*
 * texinfo: bap_set_polynom_crk_mpz
 * Assign @math{c\,@var{rg}} to @var{A}.
 * The coefficient @var{c} is allowed to be @math{0}.
 * The rank @var{rg} is allowed to be the rank of zero.
 * Note: the clot of @var{A} is modified even if the the result is zero.
 * Exception @code{BA0_ERRALG} is raised if @var{A} has readonly mode.
 */

BAP_DLL void
bap_set_polynom_crk_mpz (
    struct bap_polynom_mpz *A,
    ba0_mpz_t c,
    struct bav_rank *rg)
{
  struct bav_term T;
  struct bap_creator_mpz crea;
  struct ba0_mark M;

  if (A->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);
  bav_init_term (&T);
  if (!bav_is_zero_rank (rg))
    bav_set_term_rank (&T, rg);
  ba0_pull_stack ();

  bap_begin_creator_mpz (&crea, A, &T, bap_exact_total_rank, 1);
  if ((!ba0_mpz_is_zero (c)) && (!bav_is_zero_rank (rg)))
    bap_write_creator_mpz (&crea, &T, c);

  bap_close_creator_mpz (&crea);

  ba0_restore (&M);
}

/*
 * texinfo: bap_set_polynom_variable_mpz
 * Assign @math{v^d} to @var{A}.
 * Exception @code{BA0_ERRALG} is raised if @var{A} has readonly mode.
 */

BAP_DLL void
bap_set_polynom_variable_mpz (
    struct bap_polynom_mpz *A,
    struct bav_variable *v,
    bav_Idegree d)
{
  struct bav_term T;
  struct bap_creator_mpz crea;
  ba0_mpz_t c;
  struct ba0_mark M;

  if (A->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);
  bav_init_term (&T);
  bav_set_term_variable (&T, v, d);
  ba0_mpz_init_set_ui (c, 1);
  ba0_pull_stack ();

  bap_begin_creator_mpz (&crea, A, &T, bap_exact_total_rank, 1);
  if (!bav_is_one_term (&T))
    bap_write_creator_mpz (&crea, &T, c);
  bap_close_creator_mpz (&crea);

  ba0_restore (&M);
}

/* 
 * texinfo: bap_set_polynom_term_mpz
 * Assign @var{T} to @var{A}.
 * Exception @code{BA0_ERRALG} is raised if @var{A} has readonly mode.
 */

BAP_DLL void
bap_set_polynom_term_mpz (
    struct bap_polynom_mpz *A,
    struct bav_term *T)
{
  struct bap_creator_mpz crea;
  ba0_mpz_t c;
  struct ba0_mark M;

  if (A->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mpz_init_set_si (c, 1);
  ba0_pull_stack ();

  bap_begin_creator_mpz (&crea, A, T, bap_exact_total_rank, 1);
  bap_write_creator_mpz (&crea, T, c);
  bap_close_creator_mpz (&crea);
  ba0_restore (&M);
}

/* 
 * texinfo: bap_set_polynom_monom_mpz
 * Assign @math{c\,T} to @var{A}. 
 * The coefficient @var{c} is allowed to be @math{0}.
 * Exception @code{BA0_ERRALG} is raised if @var{A} has readonly mode.
 */

BAP_DLL void
bap_set_polynom_monom_mpz (
    struct bap_polynom_mpz *A,
    ba0_mpz_t c,
    struct bav_term *T)
{
  struct bap_creator_mpz crea;

  if (A->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (ba0_mpz_is_zero (c))
    bap_set_polynom_zero_mpz (A);
  else
    {
      bap_begin_creator_mpz (&crea, A, T, bap_exact_total_rank, 1);
      bap_write_creator_mpz (&crea, T, c);
      bap_close_creator_mpz (&crea);
    }
}

/*
 * texinfo: bap_set_polynom_mpz
 * Assign @var{B} to @var{A}.
 * The two polynomials are supposed to be disjoint.
 * Exception @code{BA0_ERRALG} is raised if @var{A} has readonly mode.
 */

BAP_DLL void
bap_set_polynom_mpz (
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *B)
{
  struct bap_creator_mpz crea;
  struct bap_itermon_mpz iter;
  struct bap_polynom_mpz C;
  struct bav_term T;
  ba0_mpz_t *c;
  ba0_int_p nbmon;
  struct ba0_mark M;

  if (A->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (bap_is_zero_polynom_mpz (B))
    bap_set_polynom_zero_mpz (A);
  else if (!bap_are_disjoint_polynom_mpz (A, B))
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

          bap_init_polynom_mpz (&C);
          bap_set_polynom_mpz (&C, B);

          ba0_pull_stack ();

          bap_set_polynom_mpz (A, &C);

          ba0_restore (&M);
        }
    }
  else
    {
      nbmon = bap_nbmon_polynom_mpz (B) - A->clot->alloc;
      nbmon = nbmon > 0 ? nbmon : 0;

      ba0_push_another_stack ();
      ba0_record (&M);
      bav_init_term (&T);
      bav_realloc_term (&T, B->total_rank.size);
      ba0_pull_stack ();

      bap_begin_creator_mpz (&crea, A, &B->total_rank, bap_exact_total_rank,
          nbmon);

      if (bap_is_write_allable_creator_mpz (&crea, B))
        bap_write_all_creator_mpz (&crea, B);
      else
        {
          bap_begin_itermon_mpz (&iter, B);
          while (!bap_outof_itermon_mpz (&iter))
            {
              c = bap_coeff_itermon_mpz (&iter);
              bap_term_itermon_mpz (&T, &iter);
              bap_write_creator_mpz (&crea, &T, *c);
              bap_next_itermon_mpz (&iter);
            }
        }
      bap_close_creator_mpz (&crea);
      ba0_restore (&M);
    }
}

/*
 * texinfo: bap_set_tableof_polynom_mpz
 * Assign @var{src} to @var{dst}.
 * Entries of @var{src} are allowed to be @code{BAP_NOT_A_POLYNOM_mpz}.
 */

BAP_DLL void
bap_set_tableof_polynom_mpz (
    struct bap_tableof_polynom_mpz *dst,
    struct bap_tableof_polynom_mpz *src)
{
  if (dst != src)
    {
      ba0_int_p i;

      ba0_realloc_table ((struct ba0_table *) dst, src->size);
      for (i = 0; i < src->size; i++)
        {
          if (src->tab[i] == BAP_NOT_A_POLYNOM_mpz)
            dst->tab[i] = BAP_NOT_A_POLYNOM_mpz;
          else
            {
              if (dst->tab[i] == BAP_NOT_A_POLYNOM_mpz)
                dst->tab[i] = bap_new_polynom_mpz ();
              bap_set_polynom_mpz (dst->tab[i], src->tab[i]);
            }
        }
      dst->size = src->size;
    }
}

/*
 * texinfo: bap_set_tableof_tableof_polynom_mpz
 * Assign @var{src} to @var{dst}.
 * All tables are allowed to involve zero entries.
 */

BAP_DLL void
bap_set_tableof_tableof_polynom_mpz (
    struct bap_tableof_tableof_polynom_mpz *dst,
    struct bap_tableof_tableof_polynom_mpz *src)
{
  if (dst != src)
    {
      ba0_int_p i;

      ba0_realloc_table ((struct ba0_table *) dst, src->size);
      for (i = 0; i < src->size; i++)
        {
          if (src->tab[i] == (struct bap_tableof_polynom_mpz *) 0)
            dst->tab[i] = (struct bap_tableof_polynom_mpz *) 0;
          else
            {
              if (dst->tab[i] == (struct bap_tableof_polynom_mpz *) 0)
                dst->tab[i] = (struct bap_tableof_polynom_mpz *)
                    ba0_new_table ();
              bap_set_tableof_polynom_mpz (dst->tab[i], src->tab[i]);
            }
        }
      dst->size = src->size;
    }
}


/* 
 * texinfo: bap_set_readonly_polynom_mpz
 * Assign @var{A} to @var{R}.
 * The polynomial @var{R} is readonly.
 * The two polynomials are not disjoint.
 */

BAP_DLL void
bap_set_readonly_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A)
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
      nbmon = bap_nbmon_polynom_mpz (A);
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
 * texinfo: bap_is_zero_polynom_mpz
 * Return @code{true} if @var{A} is equal to @math{0}.
 */

BAP_DLL bool
bap_is_zero_polynom_mpz (
    struct bap_polynom_mpz *A)
{
  return bap_nbmon_polynom_mpz (A) == 0;
}

/* 
 * texinfo: bap_is_one_polynom_mpz
 * Return @code{true} if @var{A} is equal to @math{1}.
 */

BAP_DLL bool
bap_is_one_polynom_mpz (
    struct bap_polynom_mpz *A)
{
  struct bap_itermon_mpz iter;
  ba0_mpz_t *lc;

  if (!bav_is_one_term (&A->total_rank))
    return false;
  bap_begin_itermon_mpz (&iter, A);
  lc = bap_coeff_itermon_mpz (&iter);
  return ba0_mpz_is_one (*lc);
}

/* 
 * texinfo: bap_is_numeric_polynom_mpz
 * Return @code{true} if @var{A} does not depend on any variable.
 */

BAP_DLL bool
bap_is_numeric_polynom_mpz (
    struct bap_polynom_mpz *A)
{
  return bap_is_zero_polynom_mpz (A) || bav_is_one_term (&A->total_rank);
}

/* 
 * texinfo: bap_is_univariate_polynom_mpz
 * Return @code{true} if @var{A} depends on a single variable.
 */

BAP_DLL bool
bap_is_univariate_polynom_mpz (
    struct bap_polynom_mpz *A)
{
  return A->total_rank.size <= 1;
}

/* 
 * texinfo: bap_is_variable_polynom_mpz
 * Return @code{true} if @var{A} is equal to a variable.
 */

BAP_DLL bool
bap_is_variable_polynom_mpz (
    struct bap_polynom_mpz *A)
{
  return bav_total_degree_term (&A->total_rank) == 1
      && bap_nbmon_polynom_mpz (A) == 1;
}

/*
 * texinfo: bap_is_solved_polynom_mpz
 * Return @code{true} if @var{A} has leading degree @math{1}
 * and a numeric initial.
 */

BAP_DLL bool
bap_is_solved_polynom_mpz (
    struct bap_polynom_mpz *A)
{
  struct bap_polynom_mpz init;
  struct ba0_mark M;
  bool b;

  if (bap_is_numeric_polynom_mpz (A))
    return false;

  if (bap_leading_degree_polynom_mpz (A) != 1)
    return false;

  ba0_record (&M);
  bap_init_readonly_polynom_mpz (&init);
  bap_initial_polynom_mpz (&init, A);
  b = bap_is_numeric_polynom_mpz (&init);
  ba0_restore (&M);

  return b;
}

/*
 * texinfo: bap_is_derivative_minus_independent_polynom_mpz
 * Return @code{true} if @var{A} has the form @math{v - B} where
 * @var{v} is a derivative and @var{B} is a polynomial which does
 * not depend on any derivative.
 */

BAP_DLL bool
bap_is_derivative_minus_independent_polynom_mpz (
    struct bap_polynom_mpz *A)
{
  ba0_int_p i;

  if (!bap_is_solved_polynom_mpz (A))
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
 * bap_is_rank_minus_monom_polynom_mpz
 * Return @code{true} if @var{A} has the form @math{v^d - M} where
 * @var{v} is the lading derivative of @var{A} and @var{M} is a
 * monomial.
 */

BAP_DLL bool
bap_is_rank_minus_monom_polynom_mpz (
    struct bap_polynom_mpz *A)
{
  struct bap_polynom_mpz init;

  if (bap_nbmon_polynom_mpz (A) > 2)
    return false;
  bap_init_readonly_polynom_mpz (&init);
  bap_initial_polynom_mpz (&init, A);
  return bap_is_one_polynom_mpz (&init);
}

/* 
 * texinfo: bap_depend_polynom_mpz
 * Return @code{true} if @var{A} depends on @var{v}.
 */

BAP_DLL bool
bap_depend_polynom_mpz (
    struct bap_polynom_mpz *A,
    struct bav_variable *v)
{
  ba0_int_p i;

  for (i = 0; i < A->total_rank.size; i++)
    if (A->total_rank.rg[i].var == v)
      return true;
  return false;
}

/*
 * texinfo: bap_depend_point_polynom_mpz
 * Return @code{true} if @var{A} depends on one of the
 * variables of @var{point}.

BAP_DLL bool
bap_depend_point_polynom_mpz (
    struct bap_polynom_mpz * A,
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
 * texinfo: bap_depend_only_polynom_mpz
 * Return @code{true} if @var{A} depends only on the variables 
 * present in @var{T}. The table @var{T} is supposed to be sorted
 * in ascending order.
*/

BAP_DLL bool
bap_depend_only_polynom_mpz (
    struct bap_polynom_mpz *A,
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
 * texinfo: bap_compare_polynom_mpz
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
bap_compare_polynom_mpz (
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *B)
{
  struct bap_itermon_mpz iterA, iterB;
  enum ba0_compare_code code, resultat = ba0_eq;
  struct bav_term TA, TB;
  struct ba0_mark M;

  bap__check_compatible_mpz (A, B);

  if (A == B)
    return resultat;

  ba0_record (&M);
  bav_init_term (&TA);
  bav_init_term (&TB);
  bap_begin_itermon_mpz (&iterA, A);
  bap_begin_itermon_mpz (&iterB, B);
  while (!bap_outof_itermon_mpz (&iterA) && !bap_outof_itermon_mpz (&iterB))
    {
      bap_term_itermon_mpz (&TA, &iterA);
      bap_term_itermon_mpz (&TB, &iterB);
      code = bav_compare_term (&TA, &TB);
      if (code == ba0_lt || code == ba0_gt)
        {
          resultat = code;
          break;
        }
      if (resultat == ba0_eq
          && !ba0_mpz_are_equal (*bap_coeff_itermon_mpz (&iterA),
              *bap_coeff_itermon_mpz (&iterB)))
        resultat = ba0_equiv;
      bap_next_itermon_mpz (&iterA);
      bap_next_itermon_mpz (&iterB);
    }
  if (resultat == ba0_eq || resultat == ba0_equiv)
    {
      if (!bap_outof_itermon_mpz (&iterA))
        resultat = ba0_gt;
      else if (!bap_outof_itermon_mpz (&iterB))
        resultat = ba0_lt;
    }
  ba0_restore (&M);
  return resultat;
}

/* 
 * texinfo: bap_equal_polynom_mpz
 * Return @code{true} if @var{A} and @var{B} are equal.
 */

BAP_DLL bool
bap_equal_polynom_mpz (
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *B)
{
  struct bap_itermon_mpz iterA, iterB;
  struct bav_term TA, TB;
  struct ba0_mark M;

  bap__check_compatible_mpz (A, B);

  if (A == B)
    return true;
  if (bap_nbmon_polynom_mpz (A) != bap_nbmon_polynom_mpz (B))
    return false;
  if (!bav_equal_term (&A->total_rank, &B->total_rank))
    return false;

  ba0_record (&M);
  bav_init_term (&TA);
  bav_init_term (&TB);
  bap_begin_itermon_mpz (&iterA, A);
  bap_begin_itermon_mpz (&iterB, B);
  while (!bap_outof_itermon_mpz (&iterA))
    {
      bap_term_itermon_mpz (&TA, &iterA);
      bap_term_itermon_mpz (&TB, &iterB);
      if (!bav_equal_term (&TA, &TB))
        {
          ba0_restore (&M);
          return false;
        }
      if (!ba0_mpz_are_equal (*bap_coeff_itermon_mpz (&iterA),
              *bap_coeff_itermon_mpz (&iterB)))
        {
          ba0_restore (&M);
          return false;
        }
      bap_next_itermon_mpz (&iterA);
      bap_next_itermon_mpz (&iterB);
    }
  ba0_restore (&M);
  return true;
}

/* 
 * texinfo: bap_gt_rank_polynom_mpz
 * Return @code{true} if @var{P} has strictly greater rank than @var{B}.
 * Both parameters are polynomials.
 */

BAP_DLL bool
bap_gt_rank_polynom_mpz (
    void *P,
    void *Q)
{
  struct bap_polynom_mpz *A = (struct bap_polynom_mpz *) P;
  struct bap_polynom_mpz *B = (struct bap_polynom_mpz *) Q;
  struct bav_rank Arg, Brg;

  Arg = bap_rank_polynom_mpz (A);
  Brg = bap_rank_polynom_mpz (B);

  return bav_gt_rank (&Arg, &Brg);
}

/* 
 * texinfo: bap_lt_rank_polynom_mpz
 * Return @code{true} if @var{P} has strictly lower rank than @var{B}.
 * Both parameters are polynomials.
 */

BAP_DLL bool
bap_lt_rank_polynom_mpz (
    void *P,
    void *Q)
{
  struct bap_polynom_mpz *A = (struct bap_polynom_mpz *) P;
  struct bap_polynom_mpz *B = (struct bap_polynom_mpz *) Q;
  struct bav_rank Arg, Brg;

  Arg = bap_rank_polynom_mpz (A);
  Brg = bap_rank_polynom_mpz (B);

  return bav_lt_rank (&Arg, &Brg);
}

/* 
 * texinfo: bap_equal_rank_polynom_mpz
 * Return @code{true} if @var{P} and @var{Q} have the same rank.
 */

BAP_DLL bool
bap_equal_rank_polynom_mpz (
    struct bap_polynom_mpz *P,
    struct bap_polynom_mpz *Q)
{
  struct bav_rank Prg, Qrg;

  Prg = bap_rank_polynom_mpz (P);
  Qrg = bap_rank_polynom_mpz (Q);

  return bav_equal_rank (&Prg, &Qrg);
}

/*
 * texinfo: bad_compare_rank_polynom_mpz
 * A comparison function for sorting tables of polynomials
 * by increasing rank, using @code{qsort}.
 */

BAP_DLL int
bap_compare_rank_polynom_mpz (
    const void *PP,
    const void *QQ)
{
  struct bap_polynom_mpz *P = *(struct bap_polynom_mpz **) PP;
  struct bap_polynom_mpz *Q = *(struct bap_polynom_mpz **) QQ;

  if (bap_lt_rank_polynom_mpz (P, Q))
    return -1;
  else if (bap_equal_rank_polynom_mpz (P, Q))
    return 0;
  else
    return 1;
}

/*
 * texinfo: bap_are_disjoint_polynom_mpz
 * Return @code{true} if @var{A} and @var{B} are disjoint, in the
 * sense that any modification on one of these polynomials has no
 * side effect on the other one.
 */

BAP_DLL bool
bap_are_disjoint_polynom_mpz (
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *B)
{
  return A->clot != B->clot;
}

/* 
 * texinfo: bap_mark_indets_polynom_mpz
 * Append to @var{vars} the variables occurring in @var{A} which
 * are not already present in @var{vars}. 
 * Every element of @var{vars} is supposed to be registered in
 * the dictionary @var{dict}.
 */

BAP_DLL void
bap_mark_indets_polynom_mpz (
    struct bav_dictionary_variable *dict,
    struct bav_tableof_variable *vars,
    struct bap_polynom_mpz *A)
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
 * texinfo: bap_mark_indets_tableof_polynom_mpz
 * Append to @var{vars} the variables occurring in @var{T} which
 * are not already present in @var{vars}.
 * Every element of @var{vars} is supposed to be registered in
 * the dictionary @var{dict}.
 */

BAP_DLL void
bap_mark_indets_tableof_polynom_mpz (
    struct bav_dictionary_variable *dict,
    struct bav_tableof_variable *vars,
    struct bap_tableof_polynom_mpz *T)
{
  ba0_int_p i;

  for (i = 0; i < T->size; i++)
    bap_mark_indets_polynom_mpz (dict, vars, T->tab[i]);
}

/*
 * texinfo: bap_mark_indets_listof_polynom_mpz
 * Append to @var{vars} the variables occurring in @var{L} which
 * are not already present in @var{vars}.
 * Every element of @var{vars} is supposed to be registered in
 * the dictionary @var{dict}.
 */

BAP_DLL void
bap_mark_indets_listof_polynom_mpz (
    struct bav_dictionary_variable *dict,
    struct bav_tableof_variable *vars,
    struct bap_listof_polynom_mpz *L)
{
  struct bap_listof_polynom_mpz *M;

  for (M = L; M != (struct bap_listof_polynom_mpz *) 0; M = M->next)
    bap_mark_indets_polynom_mpz (dict, vars, M->value);
}

/*
 * texinfo: bap_set_total_rank_polynom_mpz
 * This low-level function computes and sets the @code{total_rank} field
 * of @var{A}.
 */

BAP_DLL void
bap_set_total_rank_polynom_mpz (
    struct bap_polynom_mpz *A)
{
  struct bav_dictionary_variable dict;
  struct bav_tableof_variable vars;
  struct ba0_tableof_int_p degs;

  struct bap_itermon_mpz iter;
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

  bap_begin_itermon_mpz (&iter, A);
  while (!bap_outof_itermon_mpz (&iter))
    {
      bap_term_itermon_mpz (&T, &iter);
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
      bap_next_itermon_mpz (&iter);
    }
  ba0_pull_stack ();
  bav_set_term_tableof_variable (&A->total_rank, &vars, &degs);
  ba0_restore (&M);
}

/*
 * texinfo: bap_reverse_polynom_mpz
 * This low-level function reverts the order of the monomials in
 * the clot of @var{A}.
 * Exception @code{BA0_ERRALG} is raised if @var{A} has readonly mode.
 */

BAP_DLL void
bap_reverse_polynom_mpz (
    struct bap_polynom_mpz *A)
{
  if (A->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  bap_reverse_clot_mpz (A->clot);
}

/*************************************************************************
 :REORDONNE
 *************************************************************************/

struct quicksort_data
{
  struct bap_iterator_indexed_access l;
  struct bap_iterator_indexed_access r;
  struct bap_itermon_mpz i;
  struct bap_itermon_mpz j;
  struct bap_itermon_mpz k;
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
    struct bap_polynom_mpz *R)
{
  bap_begin_iterator_indexed_access (&qs->l, &R->ind);
  bap_end_iterator_indexed_access (&qs->r, &R->ind);

  bap_begin_itermon_mpz (&qs->i, R);
  bap_begin_itermon_mpz (&qs->j, R);
  bap_begin_itermon_mpz (&qs->k, R);

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
quicksort_mpz (
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
      bap_goto_itermon_mpz (&qs->i, i);
      bap_goto_itermon_mpz (&qs->j, j);
      bap_goto_itermon_mpz (&qs->k, k);

      bap_term_itermon_mpz (&qs->Ti, &qs->i);
      bap_term_itermon_mpz (&qs->Tj, &qs->j);
      bap_term_itermon_mpz (&qs->Tk, &qs->k);
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
      bap_goto_itermon_mpz (&qs->i, i);
      bap_goto_itermon_mpz (&qs->j, j);
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
              bap_next_itermon_mpz (&qs->i);
              bap_term_itermon_mpz (&qs->Ti, &qs->i);
              code = bav_compare_term (&qs->Ti, &qs->pivot);
            }
          while (code == ba0_gt);
          do
            {
              j -= 1;
              bap_prev_itermon_mpz (&qs->j);
              bap_term_itermon_mpz (&qs->Tj, &qs->j);
              code = bav_compare_term (&qs->Tj, &qs->pivot);
            }
          while (code == ba0_lt);
        }
      while (i < j);
      bap_swapindex_iterator_indexed_access (&qs->i.iter_ix, &qs->r);
      bap_goto_iterator_indexed_access (&qs->r, i - 1);
      quicksort_mpz (l, i - 1, qs);
      bap_goto_iterator_indexed_access (&qs->l, i + 1);
      bap_goto_iterator_indexed_access (&qs->r, r);
      quicksort_mpz (i + 1, r, qs);
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
          bap_goto_itermon_mpz (&qs->j, l);
          bap_term_itermon_mpz (suiv, &qs->j);
          for (j = l; j <= i; j++)
            {
              BA0_SWAP (struct bav_term *,
                  cour,
                  suiv);
              bap_set_iterator_indexed_access (&i_cour, &qs->j.iter_ix);
              bap_next_itermon_mpz (&qs->j);
              bap_term_itermon_mpz (suiv, &qs->j);
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
 * texinfo: bap_sort_polynom_mpz
 * Assign to @var{R} the polynomial @var{A}, sorted w.r.t. the 
 * current ordering. The resulting polynomial @var{R} is readonly
 * and has indexed access. The polynomial @var{A} is left unchanged.
 */

BAP_DLL void
bap_sort_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A)
{
  struct bap_creator_indexed_access crea;
  struct bap_iterator_indexed_access iter;
  struct quicksort_data qs;
  ba0_int_p i, offset, nbmonA;
  struct ba0_mark M;

  nbmonA = bap_nbmon_polynom_mpz (A);
  if (nbmonA == 0)
    {
      bap_set_polynom_zero_mpz (R);
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
  quicksort_mpz (0, nbmonA - 1, &qs);
  ba0_restore (&M);
  R->readonly = true;
}

/*
 * texinfo: bap_physort_polynom_mpz
 * This low-level function sorts the polynomial @var{A} w.r.t.
 * the current ordering. The polynomial @var{A} is supposed to
 * have sequential access.
 */

BAP_DLL void
bap_physort_polynom_mpz (
    struct bap_polynom_mpz *A)
{
  if (A->access == bap_indexed_monom_access)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  bap_sort_clot_mpz (A->clot, A->seq.first, A->seq.after);
  bav_sort_term (&A->total_rank);
  bap_change_ordering_termstripper (&A->tstrip, bav_current_ordering ());
  bap_change_ordering_clot_mpz (A->clot, bav_current_ordering ());
}

/* 
 * texinfo: bap_nbmon_polynom_mpz
 * Return the number of monomials present in @var{A}.
 */

BAP_DLL ba0_int_p
bap_nbmon_polynom_mpz (
    struct bap_polynom_mpz *A)
{
  if (A->access == bap_sequential_monom_access)
    return A->seq.after - A->seq.first;
  else
    return A->ind.size;
}

/*
 * texinfo: bap_leader_polynom_mpz
 * Return the leading variable of @var{A}.
 * Exception @code{BAP_ERRCST} is raised if @var{A} does not
 * depend on any variable.
 */

BAP_DLL struct bav_variable *
bap_leader_polynom_mpz (
    struct bap_polynom_mpz *A)
{
  if (bap_is_numeric_polynom_mpz (A))
    BA0_RAISE_EXCEPTION (BAP_ERRCST);
  return bav_leader_term (&A->total_rank);
}

/*
 * texinfo: bap_rank_polynom_mpz
 * Return the leading rank of @var{A}.
 */

BAP_DLL struct bav_rank
bap_rank_polynom_mpz (
    struct bap_polynom_mpz *A)
{
  struct bav_rank rg;

  if (bap_is_zero_polynom_mpz (A))
    rg = bav_zero_rank ();
  else if (bav_is_one_term (&A->total_rank))
    rg = bav_constant_rank ();
  else
    rg = bav_leading_rank_term (&A->total_rank);
  return rg;
}

/*
 * texinfo: bap_leading_degree_polynom_mpz
 * Return the degree of @var{A} w.r.t. its leading variable.
 * Exception @code{BAP_ERRCST} is raised if @var{A} does not
 * depend on any variable.
 */

BAP_DLL bav_Idegree
bap_leading_degree_polynom_mpz (
    struct bap_polynom_mpz *A)
{
  if (bap_is_numeric_polynom_mpz (A))
    BA0_RAISE_EXCEPTION (BAP_ERRCST);
  return bav_leading_degree_term (&A->total_rank);
}

/*
 * texinfo: bap_total_order_polynom_mpz
 * Return the sum of the orders of all the derivatives @var{A}
 * depends on.
 */

BAP_DLL bav_Iorder
bap_total_order_polynom_mpz (
    struct bap_polynom_mpz *A)
{
  return bav_total_order_term (&A->total_rank);
}

/*
 * texinfo: bap_minimal_total_rank_polynom_mpz
 * Assign to @var{T} the gcd of all the terms occurring in @var{A}.
 * Exception @code{BAP_ERRNUL} is raised if @var{A} is @math{0}.
 */

BAP_DLL void
bap_minimal_total_rank_polynom_mpz (
    struct bav_term *T,
    struct bap_polynom_mpz *A)
{
  struct bap_itermon_mpz iter;
  struct bav_term U;
  struct bav_tableof_variable vars;
  struct ba0_tableof_int_p degs;
  struct bav_variable *v;
  ba0_int_p i, j;
  struct ba0_mark M;

  if (bap_is_zero_polynom_mpz (A))
    BA0_RAISE_EXCEPTION (BAP_ERRNUL);

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&U);
  bap_end_itermon_mpz (&iter, A);
  bap_term_itermon_mpz (&U, &iter);

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

      bap_begin_itermon_mpz (&iter, A);
      while (!bap_outof_itermon_mpz (&iter))
        {
          bap_term_itermon_mpz (&U, &iter);
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
          bap_next_itermon_mpz (&iter);
        }
      ba0_pull_stack ();
      bav_set_term_tableof_variable (T, &vars, &degs);
    }
  ba0_restore (&M);
}

/*
 * texinfo: bap_leading_term_polynom_mpz
 * Assign to @var{T} the leading term of @var{A}.
 * Exception @code{BAP_ERRNUL} is raised if @var{A} is @math{0}.
 */

BAP_DLL void
bap_leading_term_polynom_mpz (
    struct bav_term *T,
    struct bap_polynom_mpz *A)
{
  struct bap_itermon_mpz iter;

  if (bap_is_zero_polynom_mpz (A))
    BA0_RAISE_EXCEPTION (BAP_ERRNUL);

  bap_begin_itermon_mpz (&iter, A);
  bap_term_itermon_mpz (T, &iter);
}

/* 
 * texinfo: bap_numeric_initial_polynom_mpz
 * Return the address of the coefficient of the leading term
 * of @var{A}.
 * Exception @code{BAP_ERRNUL} is raised if @var{A} is @math{0}.
 */

BAP_DLL ba0_mpz_t *
bap_numeric_initial_polynom_mpz (
    struct bap_polynom_mpz *A)
{
  struct bap_itermon_mpz iter;
  ba0_mpz_t *c;

  if (bap_is_zero_polynom_mpz (A))
    BA0_RAISE_EXCEPTION (BAP_ERRNUL);

  bap_begin_itermon_mpz (&iter, A);
  c = bap_coeff_itermon_mpz (&iter);

  return c;
}

/*
 * texinfo: bap_initial_and_reductum_polynom_mpz
 * Assign to @var{initial} and @var{reductum} the initial
 * and the reductum of @var{A}, in readonly mode.
 * Both parameters are allowed to be the zero pointers.
 * Exception @code{BAP_ERRCST} is raised if @var{A} does not
 * depend on any variable.
 */

BAP_DLL void
bap_initial_and_reductum_polynom_mpz (
    struct bap_polynom_mpz *initial,
    struct bap_polynom_mpz *reductum,
    struct bap_polynom_mpz *A)
{
  struct bap_itercoeff_mpz iter;

  if (bap_is_numeric_polynom_mpz (A))
    BA0_RAISE_EXCEPTION (BAP_ERRCST);
  if ((A == initial && reductum != BAP_NOT_A_POLYNOM_mpz) || (A == initial
          && A == reductum))
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);
  bap_begin_itercoeff_mpz (&iter, A, bap_leader_polynom_mpz (A));
  if (initial != BAP_NOT_A_POLYNOM_mpz)
    bap_coeff_itercoeff_mpz (initial, &iter);
  if (reductum != BAP_NOT_A_POLYNOM_mpz)
    {
      bap_next_itermon_mpz (&iter.fin);
      bap_reductum_itermon_mpz (&iter.fin, reductum);
    }
}

/*
 * texinfo: bap_initial_polynom_mpz
 * Assign to @var{initial} the initial
 * of @var{A}, in readonly mode.
 * Exception @code{BAP_ERRCST} is raised if @var{A} does not
 * depend on any variable.
 */

BAP_DLL void
bap_initial_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A)
{
  bap_initial_and_reductum_polynom_mpz (R, BAP_NOT_A_POLYNOM_mpz, A);
}

/*
 * texinfo: bap_reductum_polynom_mpz
 * Assign to @var{reductum} the reductum
 * of @var{A}, in readonly mode.
 * Exception @code{BAP_ERRCST} is raised if @var{A} does not
 * depend on any variable.
 */

BAP_DLL void
bap_reductum_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A)
{
  bap_initial_and_reductum_polynom_mpz (BAP_NOT_A_POLYNOM_mpz, R, A);
}

/*
 * texinfo: bap_initial_and_reductum2_polynom_mpz
 * Variant of @code{bap_initial_and_reductum_polynom_mpz}
 * where the variable @var{v} w.r.t. which the initial and
 * the reductum are defined is specified.
 * This variable is supposed to be greater than or equal to the leader of A.
 * The polynomial @var{A} is allowed to be numeric.
 * The resulting polynomials are readonly.
 */

BAP_DLL void
bap_initial_and_reductum2_polynom_mpz (
    struct bap_polynom_mpz *initial,
    struct bap_polynom_mpz *reductum,
    struct bap_polynom_mpz *A,
    struct bav_variable *v)
{
  if (bap_is_numeric_polynom_mpz (A) || bap_leader_polynom_mpz (A) != v)
    {
      if (initial != BAP_NOT_A_POLYNOM_mpz)
        bap_set_readonly_polynom_mpz (initial, A);
      if (reductum != BAP_NOT_A_POLYNOM_mpz)
        bap_set_polynom_zero_mpz (reductum);
    }
  else
    bap_initial_and_reductum_polynom_mpz (initial, reductum, A);
}

/*
 * texinfo: bap_initial2_polynom_mpz
 * Variant of @code{bap_initial_polynom_mpz}.
 * See @code{bap_initial_and_reductum2_polynom_mpz}.
 */

BAP_DLL void
bap_initial2_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A,
    struct bav_variable *v)
{
  bap_initial_and_reductum2_polynom_mpz (R, BAP_NOT_A_POLYNOM_mpz, A, v);
}

/*
 * texinfo: bap_reductum2_polynom_mpz
 * Variant of @code{bap_reductum_polynom_mpz}.
 * See @code{bap_initial_and_reductum2_polynom_mpz}.
 */

BAP_DLL void
bap_reductum2_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A,
    struct bav_variable *v)
{
  bap_initial_and_reductum2_polynom_mpz (BAP_NOT_A_POLYNOM_mpz, R, A, v);
}

/*
 * texinfo: bap_coeff2_polynom_mpz
 * Assign to @var{R} the coefficient of @math{v^d} in @var{A}.
 * The polynomial @var{R} is readonly.
 * The variable @var{v} is supposed too be greater than or
 * equal to the leader of @var{A}.
 */

BAP_DLL void
bap_coeff2_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A,
    struct bav_variable *v,
    bav_Idegree d)
{
  if (bap_is_numeric_polynom_mpz (A) || bap_leader_polynom_mpz (A) != v)
    {
      if (d == 0)
        bap_set_readonly_polynom_mpz (R, A);
      else
        bap_set_polynom_zero_mpz (R);
    }
  else
    {
      struct bap_itercoeff_mpz iter;
      struct bav_term T;
      struct ba0_mark M;

      ba0_push_another_stack ();
      ba0_record (&M);
      bav_init_term (&T);
      bav_set_term_variable (&T, v, d);
      ba0_pull_stack ();

      bap_begin_itercoeff_mpz (&iter, A, v);
      bap_seek_coeff_itercoeff_mpz (R, &iter, &T);
      ba0_restore (&M);
    }
}

/*
 * texinfo: bap_lcoeff_and_reductum_polynom_mpz
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
bap_lcoeff_and_reductum_polynom_mpz (
    struct bap_polynom_mpz *lcoeff,
    struct bap_polynom_mpz *reductum,
    struct bap_polynom_mpz *A,
    struct bav_variable *v)
{
  struct bap_polynom_mpz AA, lc, red;
  struct ba0_mark M;

  if ((lcoeff != BAP_NOT_A_POLYNOM_mpz && lcoeff->readonly)
      || (reductum != BAP_NOT_A_POLYNOM_mpz && reductum->readonly))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (bap_is_numeric_polynom_mpz (A) || (v != BAV_NOT_A_VARIABLE
          && v != bap_leader_polynom_mpz (A)))
    {
      if (!bap_depend_polynom_mpz (A, v))
        {
          if (lcoeff != BAP_NOT_A_POLYNOM_mpz && lcoeff != A)
            bap_set_polynom_mpz (lcoeff, A);
          if (reductum != BAP_NOT_A_POLYNOM_mpz)
            bap_set_polynom_zero_mpz (reductum);
        }
      else
        {
          bav_Iordering r;

          ba0_push_another_stack ();
          ba0_record (&M);

          r = bav_R_copy_ordering (bav_current_ordering ());
          bav_push_ordering (r);
          bav_R_set_maximal_variable (v);

          bap_init_readonly_polynom_mpz (&AA);
          bap_init_readonly_polynom_mpz (&lc);
          bap_init_readonly_polynom_mpz (&red);
          bap_sort_polynom_mpz (&AA, A);
          bap_initial_and_reductum_polynom_mpz (lcoeff !=
              BAP_NOT_A_POLYNOM_mpz ? &lc : BAP_NOT_A_POLYNOM_mpz,
              reductum !=
              BAP_NOT_A_POLYNOM_mpz ? &red : BAP_NOT_A_POLYNOM_mpz, &AA);

          bav_pull_ordering ();
          ba0_pull_stack ();
          if (lcoeff != BAP_NOT_A_POLYNOM_mpz)
            bap_set_polynom_mpz (lcoeff, &lc);
          if (reductum != BAP_NOT_A_POLYNOM_mpz)
            bap_set_polynom_mpz (reductum, &red);

          bav_R_free_ordering (r);
          ba0_restore (&M);
        }
    }
  else
    {
      ba0_push_another_stack ();
      ba0_record (&M);

      bap_init_readonly_polynom_mpz (&lc);
      bap_init_readonly_polynom_mpz (&red);
      bap_initial_and_reductum_polynom_mpz (lcoeff !=
          BAP_NOT_A_POLYNOM_mpz ? &lc : BAP_NOT_A_POLYNOM_mpz,
          reductum != BAP_NOT_A_POLYNOM_mpz ? &red : BAP_NOT_A_POLYNOM_mpz,
          A);

      ba0_pull_stack ();
      if (lcoeff != BAP_NOT_A_POLYNOM_mpz)
        bap_set_polynom_mpz (lcoeff, &lc);
      if (reductum != BAP_NOT_A_POLYNOM_mpz)
        bap_set_polynom_mpz (reductum, &red);

      ba0_restore (&M);
    }
}

/*
 * texinfo: bap_lcoeff_polynom_mpz
 * Variant of @code{bap_lcoeff_and_reductum_polynom_mpz}
 * for the leading coefficient only.
 */

BAP_DLL void
bap_lcoeff_polynom_mpz (
    struct bap_polynom_mpz *lcoeff,
    struct bap_polynom_mpz *A,
    struct bav_variable *v)
{
  bap_lcoeff_and_reductum_polynom_mpz (lcoeff, BAP_NOT_A_POLYNOM_mpz, A, v);
}

/*
 * texinfo: bap_coeff_and_reductum_polynom_mpz
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
bap_coeff_and_reductum_polynom_mpz (
    struct bap_polynom_mpz *C,
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A,
    struct bav_variable *v,
    bav_Idegree d)
{
  struct bap_itermon_mpz iter;
  struct bap_creator_mpz creaC, creaR;
  struct bap_polynom_mpz CC, RR;
  struct bav_term T, U;
  struct ba0_mark M;
  ba0_int_p i, nbmon;

  if (R == (struct bap_polynom_mpz *) 0)
    {
      bap_coeff_polynom_mpz (C, A, v, d);
      return;
    }
  else if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  if (C != (struct bap_polynom_mpz *) 0 && C->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  if (C == R)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (bap_is_numeric_polynom_mpz (A) || (v != BAV_NOT_A_VARIABLE
          && !bap_depend_polynom_mpz (A, v)))
    {
      if (d == 0)
        {
          if (C != A && C != (struct bap_polynom_mpz *) 0)
            bap_set_polynom_mpz (C, A);
          bap_set_polynom_zero_mpz (R);
        }
      else
        {
          if (C != (struct bap_polynom_mpz *) 0)
            bap_set_polynom_zero_mpz (C);
          if (R != A)
            bap_set_polynom_mpz (R, A);
        }
      return;
    }

  nbmon = bap_nbmon_polynom_mpz (A);

  ba0_push_another_stack ();
  ba0_record (&M);
  bav_init_term (&T);
  bav_init_term (&U);

  if (C != A && R != A)
    {
      ba0_pull_stack ();
      if (C != (struct bap_polynom_mpz *) 0)
        bap_begin_creator_mpz (&creaC, C, &A->total_rank,
            bap_approx_total_rank, nbmon / 2 + 1);
      bap_begin_creator_mpz (&creaR, R, &A->total_rank, bap_approx_total_rank,
          nbmon / 2 + 1);
      ba0_push_another_stack ();
    }
  else
    {
      bap_init_polynom_mpz (&CC);
      bap_init_polynom_mpz (&RR);
      if (C != (struct bap_polynom_mpz *) 0)
        bap_begin_creator_mpz (&creaC, &CC, &A->total_rank,
            bap_approx_total_rank, nbmon / 2 + 1);
      bap_begin_creator_mpz (&creaR, &RR, &A->total_rank,
          bap_approx_total_rank, nbmon / 2 + 1);
    }

  bap_begin_itermon_mpz (&iter, A);
  while (!bap_outof_itermon_mpz (&iter))
    {
      bap_term_itermon_mpz (&T, &iter);
      i = 0;
      while (i < T.size && T.rg[i].var != v)
        i++;
      if ((i < T.size && T.rg[i].deg == d) || (i == T.size && d == 0))
        {
          bav_exquo_term_variable (&U, &T, v, d);
          if (C != A && R != A)
            {
              ba0_pull_stack ();
              if (C != (struct bap_polynom_mpz *) 0)
                bap_write_creator_mpz (&creaC, &U,
                    *bap_coeff_itermon_mpz (&iter));
              ba0_push_another_stack ();
            }
          else
            bap_write_creator_mpz (&creaC, &U,
                *bap_coeff_itermon_mpz (&iter));
        }
      else
        {
          if (C != A && R != A)
            {
              ba0_pull_stack ();
              bap_write_creator_mpz (&creaR, &T,
                  *bap_coeff_itermon_mpz (&iter));
              ba0_push_another_stack ();
            }
          else
            bap_write_creator_mpz (&creaR, &T,
                *bap_coeff_itermon_mpz (&iter));
        }
      bap_next_itermon_mpz (&iter);
    }
  bap_close_itermon_mpz (&iter);

  if (C != A && R != A)
    {
      ba0_pull_stack ();
      if (C != (struct bap_polynom_mpz *) 0)
        bap_close_creator_mpz (&creaC);
      bap_close_creator_mpz (&creaR);
      ba0_push_another_stack ();
    }
  else
    {
      if (C != (struct bap_polynom_mpz *) 0)
        bap_close_creator_mpz (&creaC);
      bap_close_creator_mpz (&creaR);
    }

  ba0_pull_stack ();
  if (C == A || R == A)
    {
      if (C != (struct bap_polynom_mpz *) 0)
        bap_set_polynom_mpz (C, &CC);
      bap_set_polynom_mpz (R, &RR);
    }
  ba0_restore (&M);
}

/* 
 * texinfo: bap_degree_polynom_mpz
 * Return the degree of @var{A} w.r.t. @var{v}.
 * Return @math{-1} if @var{A} is @math{0}.
 */

BAP_DLL bav_Idegree
bap_degree_polynom_mpz (
    struct bap_polynom_mpz *A,
    struct bav_variable *v)
{
  ba0_int_p i;

  if (bap_is_zero_polynom_mpz (A))
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
 * texinfo: bap_coeff_polynom_mpz
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
bap_coeff_polynom_mpz (
    struct bap_polynom_mpz *C,
    struct bap_polynom_mpz *A,
    struct bav_variable *v,
    bav_Idegree d)
{
  struct bap_itercoeff_mpz iter;
  struct bap_polynom_mpz AA, coeff;
  struct bav_term T;
  struct ba0_mark M;

  if (C->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  if (bap_is_numeric_polynom_mpz (A) || (v != BAV_NOT_A_VARIABLE
          && v != bap_leader_polynom_mpz (A)))
    {
      if (!bap_depend_polynom_mpz (A, v))
        {
          if (d == 0)
            {
              if (C != A)
                bap_set_polynom_mpz (C, A);
            }
          else
            bap_set_polynom_zero_mpz (C);
        }
      else
        {
          bav_Iordering r;

          ba0_push_another_stack ();
          ba0_record (&M);

          r = bav_R_copy_ordering (bav_current_ordering ());
          bav_push_ordering (r);
          bav_R_set_maximal_variable (v);

          bap_init_readonly_polynom_mpz (&AA);
          bap_init_readonly_polynom_mpz (&coeff);
          bap_sort_polynom_mpz (&AA, A);
          bap_begin_itercoeff_mpz (&iter, &AA, v);
          bav_init_term (&T);
          bav_set_term_variable (&T, v, d);
          bap_seek_coeff_itercoeff_mpz (&coeff, &iter, &T);

          bav_pull_ordering ();
          ba0_pull_stack ();
          bap_set_polynom_mpz (C, &coeff);

          bav_R_free_ordering (r);
          ba0_restore (&M);
        }
    }
  else
    {
      ba0_push_another_stack ();
      ba0_record (&M);

      bap_init_readonly_polynom_mpz (&coeff);
      bav_init_term (&T);
      bav_set_term_variable (&T, bap_leader_polynom_mpz (A), d);
      bap_begin_itercoeff_mpz (&iter, A, bap_leader_polynom_mpz (A));
      bap_seek_coeff_itercoeff_mpz (&coeff, &iter, &T);

      ba0_pull_stack ();
      bap_set_polynom_mpz (C, &coeff);

      ba0_restore (&M);
    }
}

/*
 * texinfo: bap_total_degree_polynom_mpz
 * Return the total degree of @var{A}.
 * Return @math{-1} if @var{A} is @math{0}.
 */

BAP_DLL bav_Idegree
bap_total_degree_polynom_mpz (
    struct bap_polynom_mpz *A)
{
  return bav_total_degree_term (&A->total_rank);
}

/*
 * texinfo: bap_replace_initial_polynom_mpz
 * Assign to @var{R} the polynomial obtained by replacing the
 * initial of @var{A} by @var{C}.
 * Exception @code{BAP_ERRCST} is raised if @var{A} is numeric.
 * xception @code{BA0_ERRALG} is raised if @var{R} is readonly.
 */

BAP_DLL void
bap_replace_initial_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *C)
{
  struct bap_creator_mpz crea;
  struct bap_itercoeff_mpz iter;
  struct bap_itermon_mpz itermon;
  struct bap_polynom_mpz *P;
  struct bav_term T;
  struct bav_rank rg;
  ba0_mpz_t *lc;
  struct ba0_mark M;

  if (bap_is_numeric_polynom_mpz (A))
    BA0_RAISE_EXCEPTION (BAP_ERRCST);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&T);
  bav_set_term (&T, &A->total_rank);
  bav_lcm_term (&T, &T, &C->total_rank);

  P = bap_new_polynom_mpz ();
  bap_begin_creator_mpz (&crea, P, &T, bap_approx_total_rank,
      bap_nbmon_polynom_mpz (A) + bap_nbmon_polynom_mpz (C));

  rg = bap_rank_polynom_mpz (A);
  bap_begin_itermon_mpz (&itermon, C);
  while (!bap_outof_itermon_mpz (&itermon))
    {
      bap_term_itermon_mpz (&T, &itermon);
      bav_mul_term_rank (&T, &T, &rg);
      lc = bap_coeff_itermon_mpz (&itermon);
      bap_write_creator_mpz (&crea, &T, *lc);
      bap_next_itermon_mpz (&itermon);
    }
  bap_begin_itercoeff_mpz (&iter, A, bap_leader_polynom_mpz (A));
  bap_next_itermon_mpz (&iter.fin);
  while (!bap_outof_itermon_mpz (&iter.fin))
    {
      bap_term_itermon_mpz (&T, &iter.fin);
      lc = bap_coeff_itermon_mpz (&iter.fin);
      bap_write_creator_mpz (&crea, &T, *lc);
      bap_next_itermon_mpz (&iter.fin);
    }
  bap_close_creator_mpz (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mpz (R, P);
  ba0_restore (&M);
}

/*
 * texinfo: bap_separant_polynom_mpz
 * Assign to @var{R} the separant of @var{A}.
 * Exception @code{BAP_ERRCST} is raised if @var{A} is numeric.
 * Exception @code{BA0_ERRALG} is raised if @var{R} is readonly.
 */

BAP_DLL void
bap_separant_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A)
{
  struct bap_itermon_mpz iter;
  struct bap_creator_mpz crea;
  struct bap_polynom_mpz *P;
  ba0_mpz_t c;
  struct bav_term T;
  struct bav_rank rg;
  struct ba0_mark M;

  if (bap_is_numeric_polynom_mpz (A))
    BA0_RAISE_EXCEPTION (BAP_ERRCST);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mpz_init (c);
  bav_init_term (&T);
  bav_set_term (&T, &A->total_rank);

  rg = bav_leading_rank_term (&T);

  if (T.rg[0].deg == 1)
    bav_shift_term (&T, &T);
  else
    T.rg[0].deg -= 1;

  P = bap_new_polynom_mpz ();
  bap_begin_creator_mpz (&crea, P, &T, bap_approx_total_rank,
      bap_nbmon_polynom_mpz (A));

  bap_begin_itermon_mpz (&iter, A);
  bap_term_itermon_mpz (&T, &iter);
  for (;;)
    {
      if (T.rg[0].deg == 1)
        {
          bav_shift_term (&T, &T);
          bap_write_creator_mpz (&crea, &T, *bap_coeff_itermon_mpz (&iter));
        }
      else
        {
          ba0_mpz_mul_ui (c, *bap_coeff_itermon_mpz (&iter), T.rg[0].deg);
          T.rg[0].deg -= 1;
          bap_write_creator_mpz (&crea, &T, c);
        }
      bap_next_itermon_mpz (&iter);
      if (bap_outof_itermon_mpz (&iter))
        break;
      bap_term_itermon_mpz (&T, &iter);
      if (bav_is_one_term (&T) || bav_leader_term (&T) != rg.var)
        break;
    }
  bap_close_creator_mpz (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mpz (R, P);
  ba0_restore (&M);
}

/*
 * texinfo: bap_separant2_polynom_mpz
 * Assign to @var{R} the separant of @var{A} w.r.t. @var{v}.
 * Exception @code{BAP_ERRCST} is raised if @var{A} is numeric.
 * xception @code{BA0_ERRALG} is raised if @var{R} is readonly.
 */

BAP_DLL void
bap_separant2_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A,
    struct bav_variable *v)
{
  struct bap_polynom_mpz B;
  bav_Iordering r;
  struct ba0_mark M;

  if (!bap_depend_polynom_mpz (A, v))
    bap_set_polynom_zero_mpz (R);
  else if (bap_leader_polynom_mpz (A) == v)
    bap_separant_polynom_mpz (R, A);
  else
    {
      ba0_push_another_stack ();
      ba0_record (&M);
      r = bav_R_copy_ordering (bav_current_ordering ());
      bav_push_ordering (r);
      bav_R_set_maximal_variable (v);
      bap_init_readonly_polynom_mpz (&B);
      bap_sort_polynom_mpz (&B, A);
      ba0_pull_stack ();
      bap_separant_polynom_mpz (R, &B);
      bav_pull_ordering ();
      bap_physort_polynom_mpz (R);
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
  struct bap_polynom_mpz *A = *(struct bap_polynom_mpz * *) x;
  struct bap_polynom_mpz *B = *(struct bap_polynom_mpz * *) y;
  struct bav_term TA, TB;
  struct ba0_mark M;
  enum ba0_compare_code code;

  ba0_record (&M);
  bav_init_term (&TA);
  bav_init_term (&TB);
  bap_leading_term_polynom_mpz (&TA, A);
  bap_leading_term_polynom_mpz (&TB, B);
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
  struct bap_polynom_mpz *A = *(struct bap_polynom_mpz * *) x;
  struct bap_polynom_mpz *B = *(struct bap_polynom_mpz * *) y;
  struct bav_term TA, TB;
  struct ba0_mark M;
  enum ba0_compare_code code;

  ba0_record (&M);
  bav_init_term (&TA);
  bav_init_term (&TB);
  bap_leading_term_polynom_mpz (&TA, A);
  bap_leading_term_polynom_mpz (&TB, B);
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
 * texinfo: bap_sort_tableof_polynom_mpz
 * Sort @var{T} in ascending or descending order 
 * depending on @var{mode}.
 */

BAP_DLL void
bap_sort_tableof_polynom_mpz (
    struct bap_tableof_polynom_mpz *T,
    enum ba0_sort_mode mode)
{
  switch (mode)
    {
    case ba0_descending_mode:
      qsort (T->tab, T->size, sizeof (struct bap_polynom_mpz *),
          &comp_polynom_descending);
      break;
    case ba0_ascending_mode:
      qsort (T->tab, T->size, sizeof (struct bap_polynom_mpz *),
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

static char _struct_polynom[] = "struct bap_polynom_mpz";
static char _struct_polynom_rang[] = "struct bap_polynom_mpz *->total_rank";

BAP_DLL ba0_int_p
bap_garbage1_polynom_mpz (
    void *AA,
    enum ba0_garbage_code code)
{
  struct bap_polynom_mpz *A = (struct bap_polynom_mpz *) AA;
  ba0_int_p n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (A, sizeof (struct bap_polynom_mpz),
        _struct_polynom);

  n += bap_garbage1_clot_mpz (A->clot, ba0_isolated);

  if (A->total_rank.rg != (struct bav_rank *) 0)
    n += ba0_new_gc_info (A->total_rank.rg,
        sizeof (struct bav_rank) * A->total_rank.alloc, _struct_polynom_rang);

  n += bap_garbage1_indexed_access (&A->ind, ba0_embedded);

  return n;
}

BAP_DLL void *
bap_garbage2_polynom_mpz (
    void *AA,
    enum ba0_garbage_code code)
{
  struct bap_polynom_mpz *A;

  if (code == ba0_isolated)
    A = (struct bap_polynom_mpz *) ba0_new_addr_gc_info (AA, _struct_polynom);
  else
    A = (struct bap_polynom_mpz *) AA;

  A->clot =
      (struct bap_clot_mpz *) bap_garbage2_clot_mpz (A->clot, ba0_isolated);

  if (A->total_rank.rg != (struct bav_rank *) 0)
    A->total_rank.rg =
        (struct bav_rank *) ba0_new_addr_gc_info (A->total_rank.rg,
        _struct_polynom_rang);

  bap_garbage2_indexed_access (&A->ind, ba0_embedded);

  return A;
}

BAP_DLL void *
bap_copy_polynom_mpz (
    void *AA)
{
  struct bap_polynom_mpz *A = (struct bap_polynom_mpz *) AA;
  struct bap_polynom_mpz *B;

  B = bap_new_polynom_mpz ();
  bap_set_polynom_mpz (B, A);
  return B;
}

/*
 * texinfo: bap_sizeof_polynom_mpz
 * Return the number of bytes used to store @var{F}.
 * If @var{code} is @code{ba0_embedded} then @var{F} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account.
 */

BAP_DLL unsigned ba0_int_p
bap_sizeof_polynom_mpz (
    struct bap_polynom_mpz *F,
    enum ba0_garbage_code code)
{
  struct bap_polynom_mpz *P, Q;
  struct ba0_mark A;
  struct ba0_mark B;
  unsigned ba0_int_p size;
/*
 * To be improved!
 */
  ba0_record (&A);
  if (code == ba0_isolated)
    {
      P = bap_new_polynom_mpz ();
      bap_set_polynom_mpz (P, F);
    }
  else
    {
      bap_init_polynom_mpz (&Q);
      bap_set_polynom_mpz (&Q, F);
    }
  ba0_record (&B);
  size = ba0_range_mark (&A, &B);
  ba0_restore (&A);
  return size;
}

/*
 * texinfo: bap_switch_ring_polynom_mpz
 * Apply @code{bav_switch_ring_variable} over all the variables occurring
 * in @var{A}. The polynomial @var{A} is modified.
 * This low level function should be used in conjunction with
 * @code{bav_set_differential_ring}: if @var{R} is a ring obtained by
 * application of @code{bav_set_differential_ring} to the ring @var{A} 
 * refers to, then this function transforms @var{A} as a polynomial of @var{R}.
 */

BAP_DLL void
bap_switch_ring_polynom_mpz (
    struct bap_polynom_mpz *A,
    struct bav_differential_ring *R)
{
  bav_switch_ring_term (&A->total_rank, R);
  bap_switch_ring_termstripper (&A->tstrip, R);
  if (A->clot)
    bap_switch_ring_clot_mpz (A->clot, R);
}

#undef BAD_FLAG_mpz
