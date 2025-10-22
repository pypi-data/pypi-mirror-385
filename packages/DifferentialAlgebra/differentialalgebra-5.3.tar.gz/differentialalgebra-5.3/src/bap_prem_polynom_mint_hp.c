#include "bap_polynom_mint_hp.h"
#include "bap_creator_mint_hp.h"
#include "bap_itermon_mint_hp.h"
#include "bap_itercoeff_mint_hp.h"
#include "bap_add_polynom_mint_hp.h"
#include "bap_mul_polynom_mint_hp.h"
#include "bap_prem_polynom_mint_hp.h"
#include "bap__check_mint_hp.h"
#include "bap_geobucket_mint_hp.h"
#include "bap_product_mint_hp.h"

#define BAD_FLAG_mint_hp

#if defined (BAD_FLAG_mpz)
#   include "bap_polyspec_mpz.h"
#endif

/*
 * Returns true if c divides A.
 * If so and Q is nonzsero, then Q = A/c.
 */

#if ! defined (BAD_FLAG_mpz)

/* The mpz_t case is handled in a separate file */

/*
 * texinfo: bap_is_numeric_factor_polynom_mint_hp
 * Return @code{true} if @var{c} divides @var{A}.
 * If so and @var{Q} is not the zero pointer, it is assigned @math{A / c}.
 */

BAP_DLL bool
bap_is_numeric_factor_polynom_mint_hp (
    struct bap_polynom_mint_hp *A,
    ba0_mint_hp_t c,
    struct bap_polynom_mint_hp *Q)
{
  ba0_mint_hp_t cbar;
  struct ba0_mark M;

  if (Q != BAP_NOT_A_POLYNOM_mint_hp && Q->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (Q == BAP_NOT_A_POLYNOM_mint_hp)
    return true;
  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mint_hp_init (cbar);
  ba0_mint_hp_invert (cbar, c);
  ba0_pull_stack ();
  bap_mul_polynom_numeric_mint_hp (Q, A, cbar);
  ba0_restore (&M);
  return true;
}

#endif

/*
 * Returns true if v divides A. If so and e is nonzero then *e
 * is the greatest degree d such that v^d divides A.
 */

/*
 * texinfo: bap_is_variable_factor_polynom_mint_hp
 * Return @code{true} if @var{v} divides @var{A}.
 * If so and @var{e} is not the zero pointer, it is assigned the highest
 * degree @var{d} such that @math{v^d} divides @var{A}.
 */

BAP_DLL bool
bap_is_variable_factor_polynom_mint_hp (
    struct bap_polynom_mint_hp *A,
    struct bav_variable *v,
    bav_Idegree *e)
{
  struct bap_itermon_mint_hp iter;
  struct bav_term T;
  bool found;
  ba0_int_p i;
  bav_Idegree d;
  struct ba0_mark M;

  if (bap_is_numeric_polynom_mint_hp (A))
    {
      if (e != (bav_Idegree *) 0)
        *e = 0;
      return false;
    }
  d = BAV_MAX_IDEGRE;
  found = true;
  ba0_record (&M);
  bap_begin_itermon_mint_hp (&iter, A);
  bav_init_term (&T);
  while (found && !bap_outof_itermon_mint_hp (&iter))
    {
      found = false;
      bap_term_itermon_mint_hp (&T, &iter);
      for (i = 0; !found && i < T.size; i++)
        {
          if (T.rg[i].var == v)
            {
              d = BA0_MIN (d, T.rg[i].deg);
              found = true;
            }
        }
      bap_next_itermon_mint_hp (&iter);
    }
  if (e != (bav_Idegree *) 0)
    *e = found ? d : 0;
  ba0_restore (&M);
  return found;
}

/* 
 * Elementary version of bap_is_factor_polynom_mint_hp
 */

static bool
bap_is_factor_elem_polynom_mint_hp (
    struct bap_polynom_mint_hp *A,
    struct bap_polynom_mint_hp *B,
    struct bap_polynom_mint_hp *Q)
{
  struct bap_itermon_mint_hp iterR, iterB;
  struct bap_creator_mint_hp creaQ;
  struct bap_polynom_mint_hp *P = (struct bap_polynom_mint_hp *) 0, *R;
  struct bav_term TQ, TR, TB, TQmax;
  ba0_mint_hp_t q, r, *cR, *cB;
  bool divisible, first = true;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&TQmax);
  bav_init_term (&TQ);
/*
 * False if the coefficient ring is not a domain.
 */
  if (!bav_is_factor_term (&A->total_rank, &B->total_rank, &TQmax))
    {
      divisible = false;
      goto fin;
    }

  if (Q != BAP_NOT_A_POLYNOM_mint_hp)
    {
      P = bap_new_polynom_mint_hp ();
      bap_begin_creator_mint_hp (&creaQ, P, &TQmax, bap_exact_total_rank,
          bap_nbmon_polynom_mint_hp (A));
    }

  divisible = true;

  R = bap_new_polynom_mint_hp ();
  bav_init_term (&TR);
  bav_init_term (&TB);
  ba0_mint_hp_init (q);
  ba0_mint_hp_init (r);
  bap_begin_itermon_mint_hp (&iterB, B);
  cB = bap_coeff_itermon_mint_hp (&iterB);
  bap_term_itermon_mint_hp (&TB, &iterB);
  while (divisible && (first || !bap_is_zero_polynom_mint_hp (R)))
    {
      bap_begin_itermon_mint_hp (&iterR, first ? A : R);
      bap_term_itermon_mint_hp (&TR, &iterR);
      if (!bav_is_factor_term (&TR, &TB, &TQ))
        {
          divisible = false;
          break;
        }
      cR = bap_coeff_itermon_mint_hp (&iterR);
#if defined (BAD_FLAG_mint_hp)
      ba0_mint_hp_div (q, *cR, *cB);
      r = 0;                    /* pour eviter un warning */
#elif defined (BAD_FLAG_mpzm) || defined (BAD_FLAG_mpq)
      ba0_mint_hp_div (q, *cR, *cB);
#elif defined (BAD_FLAG_mpz)
      ba0_mpz_tdiv_qr (q, r, *cR, *cB);
      if (ba0_mpz_sgn (r) != 0)
        {
          divisible = false;
          break;
        }
#endif
      bap_submulmon_polynom_mint_hp (R, first ? A : R, B, &TQ, q);
/*
 * False if the numerical coefficient ring is not a domain
 */
      if (!bav_is_factor_term (&TQmax, &TQ, (struct bav_term *) 0))
        {
          divisible = false;
          break;
        }
      if (Q != BAP_NOT_A_POLYNOM_mint_hp)
        bap_write_creator_mint_hp (&creaQ, &TQ, q);
      first = false;
    }
fin:
  if (divisible && Q != BAP_NOT_A_POLYNOM_mint_hp)
    {
      bap_close_creator_mint_hp (&creaQ);
      ba0_pull_stack ();
      bap_set_polynom_mint_hp (Q, P);
    }
  else
    ba0_pull_stack ();
  ba0_restore (&M);
  return divisible;
}

/*
 * Returns true if B divides A. If so and Q is nonzero then Q = A/B.
 * Does not work for coefficient rings which are not domains.
 */

/*
 * texinfo: bap_is_factor_polynom_mint_hp
 * Return @code{true} if @var{B} divides @var{A}.
 * If so and @var{Q} is not the zero pointer, it is assigned @math{A / B}.
 */

BAP_DLL bool
bap_is_factor_polynom_mint_hp (
    struct bap_polynom_mint_hp *A,
    struct bap_polynom_mint_hp *B,
    struct bap_polynom_mint_hp *Q)
{
  struct bap_itercoeff_mint_hp iter;
  struct bap_itermon_mint_hp itermon;
  struct bap_creator_mint_hp crea;
  struct bap_polynom_mint_hp q, c;
  struct bap_polynom_mint_hp *AA = (struct bap_polynom_mint_hp *) 0;
  struct bap_polynom_mint_hp *P = (struct bap_polynom_mint_hp *) 0;
  struct bav_term T, U;
  struct bav_variable *v, *w;
  bool divisible;
  bav_Iordering r;
  ba0_int_p i;
  struct ba0_mark M;

  if (bap_is_zero_polynom_mint_hp (B))
    BA0_RAISE_EXCEPTION (BAP_ERRNUL);
  bap__check_compatible_mint_hp (A, B);
  if (Q && Q->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
/*
 * Get rid of the case A == 0
 */
  if (bap_is_zero_polynom_mint_hp (A))
    {
      if (Q != BAP_NOT_A_POLYNOM_mint_hp)
        bap_set_polynom_zero_mint_hp (Q);
      return true;
    }

  ba0_push_another_stack ();
  ba0_record (&M);
  bav_init_term (&T);
/*
 * Get rid of the case B is a constant
 */
  if (bap_is_numeric_polynom_mint_hp (B))
    {
      ba0_mint_hp_t c;
      ba0_mint_hp_init_set (c, *bap_numeric_initial_polynom_mint_hp (B));
      ba0_pull_stack ();
      divisible = bap_is_numeric_factor_polynom_mint_hp (A, c, Q);
      ba0_restore (&M);
      return divisible;
    }
/*
 * A quick test, which is false if the coefficient ring is not a domain
 */
  if (!bav_is_factor_term (&A->total_rank, &B->total_rank, &T))
    {
      ba0_pull_stack ();
      ba0_restore (&M);
      return false;
    }
/*
 * Does A depend on variables which do not occur in B ?
 */
  {
    struct bav_dictionary_variable dict;
    struct bav_tableof_variable Bvars;
    ba0_int_p size, log2_size;

//    bav_R_mark_variables (false);

    log2_size = ba0_log2_int_p (B->total_rank.size) + 3;
    size = 1 << log2_size;

    bav_init_dictionary_variable (&dict, log2_size);
    ba0_init_table ((struct ba0_table *) &Bvars);
    ba0_realloc_table ((struct ba0_table *) &Bvars, size);

    bap_mark_indets_polynom_mint_hp (&dict, &Bvars, B);

    i = A->total_rank.size - 1;
    while (i >= 0 && bav_get_dictionary_variable (&dict, &Bvars,
            A->total_rank.rg[i].var) != BA0_NOT_AN_INDEX)
      i -= 1;
/*
 * If A does not, apply the elementary algorithm.
 */
    if (i < 0)
      {
        ba0_pull_stack ();
        divisible = bap_is_factor_elem_polynom_mint_hp (A, B, Q);
        ba0_restore (&M);
        return divisible;
      }
/*
 * If it does, one splits the set of variables of A into { L, N } where
 * L are the variables which do not occur in B, and N are the other ones.
 *
 * One views A as a linear combination c_i * t_i where the t_i are terms
 * over L. 
 */
    v = A->total_rank.rg[i].var;
    r = bav_R_copy_ordering (bav_current_ordering ());
    bav_push_ordering (r);
    while (i >= 0)
      {
        w = A->total_rank.rg[i].var;
        if (bav_get_dictionary_variable (&dict, &Bvars, w) == BA0_NOT_AN_INDEX)
          bav_R_set_maximal_variable (w);
        i -= 1;
      }
  }

  {
    struct bap_polynom_mint_hp *AA0 = bap_new_readonly_polynom_mint_hp ();
    bap_sort_polynom_mint_hp (AA0, A);
    AA = bap_new_polynom_mint_hp ();
    bap_set_polynom_mint_hp (AA, AA0);
  }

  bap_begin_itercoeff_mint_hp (&iter, AA, v);

  if (Q != BAP_NOT_A_POLYNOM_mint_hp)
    {
      bav_init_term (&U);
      bap_init_polynom_mint_hp (&q);
/*
 * T was initialized above (wrong if the coefficient ring is not a domain)
 */
      bav_sort_term (&T);
/*
 * Note that the monomials of P will temporarily not be sorted
 */
      P = bap_new_polynom_mint_hp ();
      bap_begin_creator_mint_hp (&crea, P, &T, bap_exact_total_rank,
          bap_nbmon_polynom_mint_hp (A));
    }
  bap_init_readonly_polynom_mint_hp (&c);
  divisible = true;
  while (divisible && !bap_outof_itercoeff_mint_hp (&iter))
    {
      bap_coeff_itercoeff_mint_hp (&c, &iter);
      if (Q != BAP_NOT_A_POLYNOM_mint_hp)
        {
          divisible = bap_is_factor_elem_polynom_mint_hp (&c, B, &q);
          if (divisible)
            {
              bap_term_itercoeff_mint_hp (&T, &iter);
              bap_begin_itermon_mint_hp (&itermon, &q);
              while (!bap_outof_itermon_mint_hp (&itermon))
                {
                  bap_term_itermon_mint_hp (&U, &itermon);
                  bav_mul_term (&U, &U, &T);
                  bap_write_creator_mint_hp (&crea, &U,
                      *bap_coeff_itermon_mint_hp (&itermon));
                  bap_next_itermon_mint_hp (&itermon);
                }
            }
        }
      else
        divisible =
            bap_is_factor_elem_polynom_mint_hp (&c, B, BAP_NOT_A_POLYNOM_mint_hp);
      if (divisible)
        bap_next_itercoeff_mint_hp (&iter);
    }

  i = bap_nbmon_polynom_mint_hp (A);

  if (divisible && Q != BAP_NOT_A_POLYNOM_mint_hp)
    {
      bap_close_creator_mint_hp (&crea);
      bav_pull_ordering ();
/*
 * The monomials of P eventually get sorted
 */
      bap_physort_polynom_mint_hp (P);

      ba0_pull_stack ();
      bap_set_polynom_mint_hp (Q, P);
    }
  else
    {
      bav_pull_ordering ();
      ba0_pull_stack ();
    }

  bav_R_free_ordering (r);
  ba0_restore (&M);
  return divisible;
}

/*
 * Returns true if A divides each element of T
 */

BAP_DLL bool
bap_is_factor_tableof_polynom_mint_hp (
    struct bap_polynom_mint_hp *A,
    struct bap_tableof_polynom_mint_hp *T)
{
  ba0_int_p i;
  bool b;

  b = true;
  for (i = 0; i < T->size && b; i++)
    b = bap_is_factor_polynom_mint_hp (T->tab[i], A, BAP_NOT_A_POLYNOM_mint_hp);
  return b;
}

/*
 * R = A/T
 */

/*
 * texinfo: bap_exquo_polynom_term_mint_hp
 * Assign @math{A / T} to @var{R}.
 * Assumes that the division is exact.
 * May raise exception @code{BAV_EXEXQO} if division is not exact.
 */

BAP_DLL void
bap_exquo_polynom_term_mint_hp (
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A,
    struct bav_term *T)
{
  struct bap_itermon_mint_hp iter;
  struct bap_creator_mint_hp crea;
  struct bap_polynom_mint_hp *P;
  struct bav_term U;
  struct ba0_mark M;

  bap__check_ordering_mint_hp (A);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (bav_is_one_term (T))
    {
      if (R != A)
        bap_set_polynom_mint_hp (R, A);
      return;
    }

  ba0_push_another_stack ();
  ba0_record (&M);
  bav_init_term (&U);
  bav_set_term (&U, &A->total_rank);
  bav_exquo_term (&U, &U, T);

  bap_begin_itermon_mint_hp (&iter, A);
  P = bap_new_polynom_mint_hp ();
  bap_begin_creator_mint_hp (&crea, P, &U, bap_exact_total_rank,
      bap_nbmon_polynom_mint_hp (A));
  while (!bap_outof_itermon_mint_hp (&iter))
    {
      bap_term_itermon_mint_hp (&U, &iter);
      bav_exquo_term (&U, &U, T);
      bap_write_creator_mint_hp (&crea, &U, *bap_coeff_itermon_mint_hp (&iter));
      bap_next_itermon_mint_hp (&iter);
    }
  bap_close_creator_mint_hp (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mint_hp (R, P);
  ba0_restore (&M);
}

/*
 * R = A/B
 */

/*
 * texinfo: bap_exquo_polynom_mint_hp
 * Assign @math{A / B} to @var{R}.
 * Assumes that the division is exact.
 * May raise exception @code{BAV_EXEXQO} if division is not exact.
 */

BAP_DLL void
bap_exquo_polynom_mint_hp (
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A,
    struct bap_polynom_mint_hp *B)
{
  if (!bap_is_factor_polynom_mint_hp (A, B, R))
    BA0_RAISE_EXCEPTION (BAV_EXEXQO);
}

/*
 * R = A/P
 */

#if ! defined (BAD_FLAG_mpz)

/* The mpz_t case is handled just afterwards */

BAP_DLL void
bap_exquo_polynom_product_mint_hp (
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A,
    struct bap_product_mint_hp *P)
{
  struct bap_polynom_mint_hp B;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  bap_init_polynom_mint_hp (&B);
  bap_expand_product_mint_hp (&B, P);
  ba0_pull_stack ();
  bap_exquo_polynom_mint_hp (R, A, &B);
  ba0_restore (&M);
}

#else

BAP_DLL void
bap_exquo_polynom_product_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A,
    struct bap_product_mpz *P)
{
  struct bap_polynom_mpz B;
  struct ba0_mark M;
  ba0_int_p i, j;
  bool yet = false;

  ba0_push_another_stack ();
  ba0_record (&M);
  bap_init_polynom_mpz (&B);
  if (!ba0_mpz_is_one (P->num_factor))
    {
      bap_exquo_polynom_numeric_mpz (&B, A, P->num_factor);
      yet = true;
    }
  for (i = 0; i < P->size; i++)
    {
      for (j = 0; j < P->tab[i].exponent; j++)
        {
          bap_exquo_polynom_mpz (&B, yet ? &B : A, &P->tab[i].factor);
          yet = true;
        }
    }
  ba0_pull_stack ();
  if (yet)
    bap_set_polynom_mpz (R, &B);
  else if (R != A)
    bap_set_polynom_mpz (R, A);
  ba0_restore (&M);
}

#endif

/**************************************************************************
 PSEUDO DIVISION
 **************************************************************************/

/*
 * This function stores in R the sum of the C [i] * v^i
 */

static void
pseudo_division_rebuild_mint_hp (
    struct bap_polynom_mint_hp *R,
    struct bap_tableof_polynom_mint_hp *C,
    struct bav_variable *v)
{
  struct bap_creator_mint_hp crea;
  struct bap_itermon_mint_hp iter;
  ba0_mint_hp_t *lc;
  struct bav_term T;
  struct bav_rank rg;
  bav_Idegree d, j;
  ba0_int_p nbmon;
  struct ba0_mark M;
/*
 * One computes the number of monomials and the total rank of the result
 */
  ba0_push_another_stack ();
  ba0_record (&M);

  nbmon = 0;
  bav_init_term (&T);
  d = C->size - 1;
  while (d >= 0 && bap_is_zero_polynom_mint_hp (C->tab[d]))
    d--;
  for (j = 0; j <= d; j++)
    {
      nbmon += bap_nbmon_polynom_mint_hp (C->tab[j]);
      bav_lcm_term (&T, &T, &C->tab[j]->total_rank);
    }
  rg.var = v;
  if (d > 0)
    {
      rg.deg = d;
      bav_mul_term_rank (&T, &T, &rg);
    }

  ba0_pull_stack ();
  bap_begin_creator_mint_hp (&crea, R, &T, bap_exact_total_rank, nbmon);

  for (j = d; j >= 0; j--)
    {
      rg.deg = j;
      if (!bap_is_zero_polynom_mint_hp (C->tab[j]))
        {
          bap_begin_itermon_mint_hp (&iter, C->tab[j]);
          while (!bap_outof_itermon_mint_hp (&iter))
            {
              bap_term_itermon_mint_hp (&T, &iter);
              lc = bap_coeff_itermon_mint_hp (&iter);
              if (j > 0)
                bav_mul_term_rank (&T, &T, &rg);
              bap_write_creator_mint_hp (&crea, &T, *lc);
              bap_next_itermon_mint_hp (&iter);
            }
        }
    }
  bap_close_creator_mint_hp (&crea);
  ba0_restore (&M);
}

/*
 * Performs the pseudo-division of A by B.
 * One assumes that, if deg (A, ld B) > 0 then ld B = ld A.
 * The pseudo-quotient and pseudo-remainder are stored in Q and R.
 * Parameters Q and R may be zero.
 * The table ibp contains the powers of the initial of B
 * x is a variable greater than or equal to the leader of B
 */

static void
bap_pseudo_division_elem_polynom_mint_hp (
    struct bap_polynom_mint_hp *Q,
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A,
    struct bap_polynom_mint_hp *B,
    struct bav_variable *x,
    struct bap_tableof_polynom_mint_hp *ibp)
{
  struct bap_itercoeff_mint_hp iterA, iterB;
  struct bap_itermon_mint_hp itermon;
  struct bap_creator_mint_hp crea;
  struct bap_tableof_polynom_mint_hp C;
  struct bap_polynom_mint_hp coeff_A, coeff_B, tmp1, tmp2;
  struct bap_polynom_mint_hp *P = (struct bap_polynom_mint_hp *) 0;
  struct bav_term T;
  bav_Idegree degA, degB, j, k, t;
  struct ba0_mark M;

  degB = bap_degree_polynom_mint_hp (B, x);
  degA = bap_degree_polynom_mint_hp (A, x);

  if (degA < degB)
    {
      if (R != BAP_NOT_A_POLYNOM_mint_hp && R != A)
        bap_set_polynom_mint_hp (R, A);
      if (Q != BAP_NOT_A_POLYNOM_mint_hp)
        bap_set_polynom_zero_mint_hp (Q);
      return;
    }
/*
 * degree (A, ld B) >= degree (B, ld B)
 */
  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&T);

  bap_begin_itercoeff_mint_hp (&iterB, B, x);
  bap_begin_itercoeff_mint_hp (&iterA, A, x);

  if (Q != BAP_NOT_A_POLYNOM_mint_hp)
    {
      ba0_int_p nbmon, nbmonA, nbmonB;
      struct bav_term U;

      if (degB > 0)
        {
          bav_shift_term (&T, &B->total_rank);
          bav_pow_term (&T, &T, degA - degB);
        }
      else
        bav_pow_term (&T, &B->total_rank, degA);

      if (degA > 0)
        {
          bav_init_term (&U);
          bav_shift_term (&U, &A->total_rank);
          bav_mul_term (&T, &T, &U);
        }
      else
        bav_mul_term (&T, &T, &A->total_rank);

      bav_mul_term_variable (&T, &T, x, degA - degB);

      nbmonA = bap_nbmon_polynom_mint_hp (A) / BA0_MAX (1, degA);
      nbmonB = bap_nbmon_polynom_mint_hp (B) / BA0_MAX (1, degB);
      nbmon = BA0_MAX (nbmonA, nbmonB);
      nbmon = BA0_MAX (nbmon, 1);
      nbmon *= degA - degB + 1;

      P = bap_new_polynom_mint_hp ();
      bap_begin_creator_mint_hp (&crea, P, &T, bap_approx_total_rank, nbmon);
    }
/*
 * Denote B [k] the kth coefficient of B.
 *
 * R0.
 *
 * Assign the coefficients of A to C [degA] .. C [0].
 * Apply Knuth remark: replacing C [t] by
 *    B [1]^(degA - degB - t) C [t] for t = 0 .. degA - degB - 1.
 *
 * To avoid side effects, if C [t] is zero, take the coefficient of x^t in A.
 */
  bap_init_readonly_polynom_mint_hp (&coeff_A);
  bap_init_readonly_polynom_mint_hp (&coeff_B);

  ba0_init_table ((struct ba0_table *) &C);
  ba0_realloc_table ((struct ba0_table *) &C, degA + 1);
  C.size = degA + 1;            /* la taille de C sera reduite a la fin */
  for (t = 0; t < degA - degB; t++)
    {
      C.tab[t] = bap_new_polynom_mint_hp ();
      bav_set_term_variable (&T, x, t);
      bap_seek_coeff_itercoeff_mint_hp (&coeff_A, &iterA, &T);
      bap_mul_polynom_mint_hp (C.tab[t], ibp->tab[degA - degB - t], &coeff_A);
    }
  for (t = degA - degB; t <= degA; t++)
    C.tab[t] = BAP_NOT_A_POLYNOM_mint_hp;
/*
 * R1.
 *
 * Do step R2 for k = degB - degA .. 0.
 * The algorithm terminates with R = C [degB - 1] .. C [0].
 */
  bap_init_polynom_mint_hp (&tmp1);
  bap_init_polynom_mint_hp (&tmp2);
  for (k = degA - degB; k >= 0; k--)
    {
/*
 * R2.
 *
 * Set Q [k] = C [degB + k] * ibp [k]
 * Here, Q [k] * x^k is stored in the creator.
 */
      if (Q != BAP_NOT_A_POLYNOM_mint_hp)
        {
          if (C.tab[degB + k] == BAP_NOT_A_POLYNOM_mint_hp)
            {
              bav_set_term_variable (&T, x, degB + k);
              bap_seek_coeff_itercoeff_mint_hp (&coeff_A, &iterA, &T);
              bap_mul_polynom_mint_hp (&tmp1, ibp->tab[k], &coeff_A);
            }
          else
            bap_mul_polynom_mint_hp (&tmp1, ibp->tab[k], C.tab[degB + k]);
          bap_begin_itermon_mint_hp (&itermon, &tmp1);
          while (!bap_outof_itermon_mint_hp (&itermon))
            {
              ba0_mint_hp_t *lc;

              lc = bap_coeff_itermon_mint_hp (&itermon);
              bap_term_itermon_mint_hp (&T, &itermon);
              bav_mul_term_variable (&T, &T, x, k);
              bap_write_creator_mint_hp (&crea, &T, *lc);
              bap_next_itermon_mint_hp (&itermon);
            }
        }
/*
 * Set C [j] = B [1] C [j] - C [degB + k] B [j - k] for j = degB + k - 1 .. 0.
 * When j < k this means that C [j] = B [1] C [j] since we treat B [-1], B [-2]
 * as zero. These multiplications could have been avoided if we had started
 * the algorithm by replacing C [t] by B [1]^(degA - degB - t) C [t] for
 * t = 0 .. degA - degB - 1.
 */
      for (j = degB + k - 1; j >= k; j--)
        {
          if (C.tab[j] == BAP_NOT_A_POLYNOM_mint_hp)
            {
              bav_set_term_variable (&T, x, j);
              bap_seek_coeff_itercoeff_mint_hp (&coeff_A, &iterA, &T);
              bap_mul_polynom_mint_hp (&tmp1, ibp->tab[1], &coeff_A);
              C.tab[j] = bap_new_polynom_mint_hp ();
            }
          else
            bap_mul_polynom_mint_hp (&tmp1, ibp->tab[1], C.tab[j]);
          bav_set_term_variable (&T, x, j - k);
          bap_seek_coeff_itercoeff_mint_hp (&coeff_B, &iterB, &T);
          if (C.tab[degB + k] == BAP_NOT_A_POLYNOM_mint_hp)
            {
              bav_set_term_variable (&T, x, degB + k);
              bap_seek_coeff_itercoeff_mint_hp (&coeff_A, &iterA, &T);
              bap_mul_polynom_mint_hp (&tmp2, &coeff_A, &coeff_B);
            }
          else
            bap_mul_polynom_mint_hp (&tmp2, C.tab[degB + k], &coeff_B);
          bap_sub_polynom_mint_hp (C.tab[j], &tmp1, &tmp2);
        }
    }
/*
 * The algorithm terminates with R = C [degB - 1] .. C [0].
 *
 * Creation of the remainder
 * One first recovers the intermediate data from the main stack
 */
  if (Q != BAP_NOT_A_POLYNOM_mint_hp)
    bap_close_creator_mint_hp (&crea);

  ba0_pull_stack ();

  if (R != BAP_NOT_A_POLYNOM_mint_hp)
    {
      C.size = degB;
      pseudo_division_rebuild_mint_hp (R, &C, x);
    }
/*
 * The quotient, now
 */
  if (Q != BAP_NOT_A_POLYNOM_mint_hp)
    bap_set_polynom_mint_hp (Q, P);

  ba0_restore (&M);
}

/*
 * Pseudo-division of A by B, both polynomials being viewed as
 * polynomials in the leader of B. The pseudo-quotient and the 
 * pseudo-remainder are stored in Q and R. The integer *e
 * receives the power to which the initial of B was raised to perform
 * the operation. Parameters Q, R and e may be zero.
 */

/*
 * texinfo: bap_pseudo_division_polynom_mint_hp
 * Pseudo division of @var{A} by @var{B}, both polynomial being viewed as
 * univariate polynomials in @var{x}, or in the leading variable of @var{B}, if
 * @var{x} is zero. 
 * The pseudo quotient (resp. pseudo remainder) is stored in @var{Q} 
 * (resp. @var{R})
 * if this pointer is non zero. The integer *@var{e} (if @var{e} is nonzero)
 * is assigned the power to which the initial of @var{B} is raised to perform 
 * the division.
 * If @var{x} is nonzero, it must be greater than or equal to the
 * leader of @var{B}. If is is zero, @var{B} is not allowed to be numeric.
 */

BAP_DLL void
bap_pseudo_division_polynom_mint_hp (
    struct bap_polynom_mint_hp *Q,
    struct bap_polynom_mint_hp *R,
    bav_Idegree *e,
    struct bap_polynom_mint_hp *A,
    struct bap_polynom_mint_hp *B,
    struct bav_variable *x)
{
  struct bap_itercoeff_mint_hp iter;
  struct bap_creator_mint_hp crea_quotient, crea_reste;
  struct bap_itermon_mint_hp itermon;
  struct bap_tableof_polynom_mint_hp ibp;
  struct bap_polynom_mint_hp lambda;
  struct bap_polynom_mint_hp *AA, *quotient, *reste;
  struct bap_polynom_mint_hp *Pquotient = (struct bap_polynom_mint_hp *) 0;
  struct bap_polynom_mint_hp *Preste = (struct bap_polynom_mint_hp *) 0;
  ba0_mint_hp_t *lc;
  struct bav_term T, U;
  struct bav_variable *v, *w;
  bav_Iordering r;
  bav_Idegree degA, degB, deg_lambda, k;
  ba0_int_p nbmonA, nbmonB, nbmon;
  ba0_int_p i;
  struct ba0_mark M;

  bap__check_ordering_mint_hp (B);
  if (bap_is_zero_polynom_mint_hp (B))
    BA0_RAISE_EXCEPTION (BAP_ERRNUL);
  if (x == BAV_NOT_A_VARIABLE && bap_is_numeric_polynom_mint_hp (B))
    BA0_RAISE_EXCEPTION (BAP_ERRCST);
  if ((Q != BAP_NOT_A_POLYNOM_mint_hp && Q->readonly)
      || (R != BAP_NOT_A_POLYNOM_mint_hp && R->readonly))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (x == BAV_NOT_A_VARIABLE)
    x = bap_leader_polynom_mint_hp (B);

  degB = bap_degree_polynom_mint_hp (B, x);
  degA = bap_degree_polynom_mint_hp (A, x);

  if (degA < degB)
    {
      if (R != BAP_NOT_A_POLYNOM_mint_hp && R != A)
        bap_set_polynom_mint_hp (R, A);
      if (Q != BAP_NOT_A_POLYNOM_mint_hp)
        bap_set_polynom_zero_mint_hp (Q);
      if (e != (bav_Idegree *) 0)
        *e = 0;
      return;
    }
/*
 * degree (A, ld B) >= degree (B, ld B)
 *
 * Building of the table of the powers of B
 */
  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_init_table ((struct ba0_table *) &ibp);
  ba0_realloc2_table ((struct ba0_table *) &ibp, degA - degB + 2,
      (ba0_new_function *) & bap_new_polynom_mint_hp);
  ibp.size = degA - degB + 2;

  bap_set_polynom_one_mint_hp (ibp.tab[0]);

  bap_initial2_polynom_mint_hp (ibp.tab[1], B, x);

  for (k = 2; k < ibp.size; k++)
    bap_mul_polynom_mint_hp (ibp.tab[k], ibp.tab[k - 1], ibp.tab[1]);
/*
 * Does A involve variables which do not occur in B ?
 */
  {
    struct bav_dictionary_variable dict;
    struct bav_tableof_variable Bvars;
    ba0_int_p size, log2_size;

//    bav_R_mark_variables (false);

    log2_size = ba0_log2_int_p (B->total_rank.size) + 3;
    size = 1 << log2_size;

    bav_init_dictionary_variable (&dict, log2_size);
    ba0_init_table ((struct ba0_table *) &Bvars);
    ba0_realloc_table ((struct ba0_table *) &Bvars, size);

    bap_mark_indets_polynom_mint_hp (&dict, &Bvars, B);

    i = A->total_rank.size - 1;
    while (i >= 0 && bav_get_dictionary_variable (&dict, &Bvars,
            A->total_rank.rg[i].var) != BA0_NOT_AN_INDEX)
      i -= 1;
/*
 * If not, apply the basic method
 */
    if (i < 0)
      {
        ba0_pull_stack ();
        bap_pseudo_division_elem_polynom_mint_hp (Q, R, A, B, x, &ibp);
        if (e != (bav_Idegree *) 0)
          *e = degA - degB + 1;
        ba0_restore (&M);
        return;
      }
/*
 * If yes, view A as the sum of the lambda_i * T_i  where the T_i are
 * terms over the alphabet of the non shared variables.
 *
 * Apply the elementary method over the lambda_i and adjust.
 * The quotient and the remainder are created using creators.
 * Non shared variables are greater than the other ones.
 */
    v = A->total_rank.rg[i].var;
    r = bav_R_copy_ordering (bav_current_ordering ());
    bav_push_ordering (r);
    while (i >= 0)
      {
        w = A->total_rank.rg[i].var;
        if (bav_get_dictionary_variable (&dict, &Bvars, w) == BA0_NOT_AN_INDEX)
          bav_R_set_maximal_variable (w);
        i -= 1;
      }
  }

  {
    struct bap_polynom_mint_hp *AA0 = bap_new_readonly_polynom_mint_hp ();
    bap_sort_polynom_mint_hp (AA0, A);
    AA = bap_new_polynom_mint_hp ();
    bap_set_polynom_mint_hp (AA, AA0);
  }

  bap_begin_itercoeff_mint_hp (&iter, AA, v);

  bav_init_term (&T);
  bav_init_term (&U);
  if (degB > 0)
    {
      bav_shift_term (&U, &B->total_rank);
      bav_pow_term (&U, &U, degA - degB);
    }
  else
    bav_pow_term (&U, &B->total_rank, degA);
  bav_mul_term (&T, &U, &AA->total_rank);

  nbmonA = bap_nbmon_polynom_mint_hp (A) / BA0_MAX (1, degA);
  nbmonB = bap_nbmon_polynom_mint_hp (B) / BA0_MAX (1, degB);
  nbmon = BA0_MAX (nbmonA, nbmonB);
  nbmon = BA0_MAX (1, nbmon);
  if (Q != BAP_NOT_A_POLYNOM_mint_hp)
    {
/*
 * Note that the monomials of Pquotient will temporarily not be sorted
 */
      Pquotient = bap_new_polynom_mint_hp ();
      bap_begin_creator_mint_hp (&crea_quotient, Pquotient, &T,
          bap_approx_total_rank, nbmon * (degA - degB + 1));
    }

  if (R != BAP_NOT_A_POLYNOM_mint_hp)
    {
      if (degB > 0)
        {
          bav_shift_term (&U, &B->total_rank);
          bav_mul_term (&T, &T, &U);
        }
      else
        bav_mul_term (&T, &T, &B->total_rank);
/*
 * Note that the monomials of Preste will temporarily not be sorted
 */
      Preste = bap_new_polynom_mint_hp ();
      bap_begin_creator_mint_hp (&crea_reste, Preste, &T, bap_approx_total_rank,
          nbmon * (degB + 1));
    }

  bap_init_readonly_polynom_mint_hp (&lambda);
  quotient = Q == BAP_NOT_A_POLYNOM_mint_hp ? Q : bap_new_polynom_mint_hp ();
  reste = R == BAP_NOT_A_POLYNOM_mint_hp ? R : bap_new_polynom_mint_hp ();

  while (!bap_outof_itercoeff_mint_hp (&iter))
    {
      bap_coeff_itercoeff_mint_hp (&lambda, &iter);
      deg_lambda = bap_degree_polynom_mint_hp (&lambda, x);
      bap_term_itercoeff_mint_hp (&T, &iter);
      if (deg_lambda >= degB)
        bap_pseudo_division_elem_polynom_mint_hp (quotient, reste, &lambda, B, x,
            &ibp);
      if (Q != BAP_NOT_A_POLYNOM_mint_hp && deg_lambda >= degB)
        {
          bap_mul_polynom_mint_hp (quotient, quotient,
              ibp.tab[degA - deg_lambda]);
          bap_begin_itermon_mint_hp (&itermon, quotient);
          while (!bap_outof_itermon_mint_hp (&itermon))
            {
              lc = bap_coeff_itermon_mint_hp (&itermon);
              bap_term_itermon_mint_hp (&U, &itermon);
              bav_mul_term (&U, &U, &T);
              bap_write_creator_mint_hp (&crea_quotient, &U, *lc);
              bap_next_itermon_mint_hp (&itermon);
            }
        }
      if (R != BAP_NOT_A_POLYNOM_mint_hp)
        {
          if (deg_lambda >= degB)
            {
              bap_mul_polynom_mint_hp (reste, reste, ibp.tab[degA - deg_lambda]);
            }
          else
            bap_mul_polynom_mint_hp (reste, &lambda, ibp.tab[degA - degB + 1]);
          bap_begin_itermon_mint_hp (&itermon, reste);
          while (!bap_outof_itermon_mint_hp (&itermon))
            {
              lc = bap_coeff_itermon_mint_hp (&itermon);
              bap_term_itermon_mint_hp (&U, &itermon);
              bav_mul_term (&U, &U, &T);
              bap_write_creator_mint_hp (&crea_reste, &U, *lc);
              bap_next_itermon_mint_hp (&itermon);
            }
        }
      bap_next_itercoeff_mint_hp (&iter);
    }
/*
 * The monomials of Pquotient and Preste eventually get sorted
 */
  if (Q != BAP_NOT_A_POLYNOM_mint_hp)
    {
      bap_close_creator_mint_hp (&crea_quotient);
      bav_pull_ordering ();
      bap_physort_polynom_mint_hp (Pquotient);
      bav_push_ordering (r);
    }
  if (R != BAP_NOT_A_POLYNOM_mint_hp)
    {
      bap_close_creator_mint_hp (&crea_reste);
      bav_pull_ordering ();
      bap_physort_polynom_mint_hp (Preste);
      bav_push_ordering (r);
    }

  bav_pull_ordering ();
  bav_R_free_ordering (r);

  ba0_pull_stack ();
  if (Q != BAP_NOT_A_POLYNOM_mint_hp)
    bap_set_polynom_mint_hp (Q, Pquotient);
  if (R != BAP_NOT_A_POLYNOM_mint_hp)
    bap_set_polynom_mint_hp (R, Preste);
  if (e != (bav_Idegree *) 0)
    *e = degA - degB + 1;

  ba0_restore (&M);
}

/* Variant of the above function.  */

/*
 * texinfo: bap_prem_polynom_mint_hp
 * Variant of @code{bap_pseudo_division_polynom_mint_hp}.
 */

BAP_DLL void
bap_prem_polynom_mint_hp (
    struct bap_polynom_mint_hp *R,
    bav_Idegree *e,
    struct bap_polynom_mint_hp *A,
    struct bap_polynom_mint_hp *B,
    struct bav_variable *x)
{
  bap_pseudo_division_polynom_mint_hp (BAP_NOT_A_POLYNOM_mint_hp, R, e, A, B, x);
}

/* Variant of the above function.  */

/*
 * texinfo: bap_pquo_polynom_mint_hp
 * Variant of @code{bap_pseudo_division_polynom_mint_hp}.
 */

BAP_DLL void
bap_pquo_polynom_mint_hp (
    struct bap_polynom_mint_hp *Q,
    bav_Idegree *e,
    struct bap_polynom_mint_hp *A,
    struct bap_polynom_mint_hp *B,
    struct bav_variable *x)
{
  bap_pseudo_division_polynom_mint_hp (Q, BAP_NOT_A_POLYNOM_mint_hp, e, A, B, x);
}

/*
 * Division of A by B viewed as polynomials in v.
 * In this function, it is assumed that the initial of B divides 
 * exactly the initial of the current remainder while the degree of this
 * remainder (w.r.t. v) is greater than or equal to that of B.
 */

/*
 * texinfo: bap_rem_polynom_mint_hp
 * Division of @math{A} by @math{B}, both polynomial being viewed as
 * univariate polynomials in @var{x}. It is assumed
 * that the leading coefficient of @var{B} with respect to @var{x}
 * divides exactly the leading coefficient of each remainder.
 * If @var{x} is nonzero, it must be greater than or equal to the
 * leader of @var{B}. If is is zero, @var{B} is not allowed to be numeric and
 * @var{x} is understood to be the leading variable of @var{B}.
 */

BAP_DLL void
bap_rem_polynom_mint_hp (
    struct bap_polynom_mint_hp *Q,
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A,
    struct bap_polynom_mint_hp *B,
    struct bav_variable *v)
{
  struct bap_polynom_mint_hp reste, lcR, redR, lcB, redB, C;
  struct bap_geobucket_mint_hp quotient;
  struct bav_term T;
  bav_Idegree ddeg;
  bool first;
  struct bav_rank rg;
  struct ba0_mark M;

  if (bap_is_zero_polynom_mint_hp (B))
    BA0_RAISE_EXCEPTION (BAP_ERRCST);
  if (v == BAV_NOT_A_VARIABLE && bap_is_numeric_polynom_mint_hp (B))
    BA0_RAISE_EXCEPTION (BAP_ERRCST);
  if ((Q != BAP_NOT_A_POLYNOM_mint_hp && Q->readonly)
      || (R != BAP_NOT_A_POLYNOM_mint_hp && R->readonly))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  if (v == BAV_NOT_A_VARIABLE)
    v = bap_leader_polynom_mint_hp (B);
  ddeg = bap_degree_polynom_mint_hp (A, v) - bap_degree_polynom_mint_hp (B, v);
  if (ddeg < 0)
    {
      bap_set_polynom_zero_mint_hp (Q);
      if (R != A)
        bap_set_polynom_mint_hp (R, A);
      return;
    }

  ba0_push_another_stack ();
  ba0_record (&M);

  bap_init_readonly_polynom_mint_hp (&lcB);
  bap_init_readonly_polynom_mint_hp (&redB);
  bap_initial_and_reductum2_polynom_mint_hp (&lcB, &redB, B, v);

  bap_init_geobucket_mint_hp (&quotient);
  bap_init_polynom_mint_hp (&reste);
  bap_init_readonly_polynom_mint_hp (&lcR);
  bap_init_readonly_polynom_mint_hp (&redR);
  bap_init_polynom_mint_hp (&C);
  bav_init_term (&T);
  rg.var = v;

  first = true;
  while (ddeg >= 0)
    {
      bap_initial_and_reductum2_polynom_mint_hp (&lcR, &redR, first ? A : &reste,
          v);
      bap_exquo_polynom_mint_hp (&C, &lcR, &lcB);
      rg.deg = ddeg;
      bav_set_term_rank (&T, &rg);
      bap_mul_polynom_term_mint_hp (&C, &C, &T);
      bap_add_geobucket_mint_hp (&quotient, &C);
      bap_mul_polynom_mint_hp (&C, &C, &redB);
      bap_sub_polynom_mint_hp (&reste, &redR, &C);
      ddeg =
          bap_degree_polynom_mint_hp (&reste, v) - bap_degree_polynom_mint_hp (B,
          v);
      first = false;
    }
  ba0_pull_stack ();
  bap_set_polynom_mint_hp (R, &reste);
  bap_set_polynom_geobucket_mint_hp (Q, &quotient);
  ba0_restore (&M);
}

#undef BAD_FLAG_mint_hp
