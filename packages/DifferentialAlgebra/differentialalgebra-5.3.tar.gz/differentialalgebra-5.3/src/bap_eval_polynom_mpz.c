#include "bap_polynom_mpz.h"
#include "bap_creator_mpz.h"
#include "bap_itermon_mpz.h"
#include "bap_itercoeff_mpz.h"
#include "bap_add_polynom_mpz.h"
#include "bap_mul_polynom_mpz.h"
#include "bap_eval_polynom_mpz.h"
#include "bap_geobucket_mpz.h"
#include "bap__check_mpz.h"

#define BAD_FLAG_mpz
#if defined (BAD_FLAG_mpz) || defined (BAD_FLAG_mpzm) || defined (BAD_FLAG_mpq)

/*
 * Sets to point an evaluation point the variables of which being
 * that of A and the values of which being zero.
 * Variables appear by decreasing order.
 */

/*
 * texinfo: bap_set_point_polynom_mpz
 * Assign to @var{point} an evaluation point the variables of which being
 * that of @var{A} and the values of which being zero.
 * If @var{withld} is @code{false}, the leader of @var{A} is omitted in
 * @var{point}.
 * Variables occur in @var{point} by decreasing order.
 */

BAP_DLL void
bap_set_point_polynom_mpz (
    struct ba0_point *point,
    struct bap_polynom_mpz *A,
    bool withld)
{
  ba0_int_p i;

  point->size = 0;
  ba0_realloc2_table ((struct ba0_table *) point, A->total_rank.size,
      (ba0_new_function *) & ba0_new_value);
  for (i = withld ? 0 : 1; i < A->total_rank.size; i++)
    {
      point->tab[point->size]->var = A->total_rank.rg[i].var;
      point->tab[point->size]->value = 0;
      point->size += 1;
    }
  ba0_sort_point ((struct ba0_point *) point, (struct ba0_point *) point);
}

/*
 * texinfo: bap_eval_to_polynom_at_numeric_polynom_mpz
 * Assign to @var{R} the polynomial obtained by evaluating 
 * @var{A} at @math{v=c}.
 */

BAP_DLL void
bap_eval_to_polynom_at_numeric_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A,
    struct bav_variable *v,
    ba0_mpz_t c)
{
  struct bap_polynom_mpz B, C, E;
  struct bap_itercoeff_mpz iter;
  struct bav_term T;
  bav_Idegree d;
  bav_Iordering r;
  struct ba0_mark M;

  bap__check_ordering_mpz (A);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  r = bav_R_copy_ordering (bav_current_ordering ());
  bav_push_ordering (r);
  bav_R_set_maximal_variable (v);

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&T);

  bap_init_polynom_mpz (&B);
  bap_init_polynom_mpz (&C);
  bap_init_polynom_mpz (&E);
  bap_sort_polynom_mpz (&B, A);

  if (!bap_is_numeric_polynom_mpz (&B) && bap_leader_polynom_mpz (&B) == v)
    {
      bap_begin_itercoeff_mpz (&iter, &B, v);
      bap_coeff_itercoeff_mpz (&C, &iter);
      bap_term_itercoeff_mpz (&T, &iter);
      bap_set_polynom_mpz (&E, &C);
/*
   Horner scheme
*/
      for (d = bav_degree_term (&T, v) - 1; d >= 0; d--)
        {
          bap_mul_polynom_numeric_mpz (&E, &E, c);
          bav_set_term_variable (&T, v, d);
          bap_seek_coeff_itercoeff_mpz (&C, &iter, &T);
          if (!bap_is_zero_polynom_mpz (&C))
            bap_add_polynom_mpz (&E, &E, &C);
        }
      bap_close_itercoeff_mpz (&iter);
      ba0_pull_stack ();
      bap_set_polynom_mpz (R, &E);
    }
  else
    {
      ba0_pull_stack ();
      if (R != A)
        bap_set_polynom_mpz (R, A);
    }
  ba0_restore (&M);
  bav_pull_ordering ();
  bav_R_free_ordering (r);
  bap_physort_polynom_mpz (R);
}

/*
 * texinfo: bap_eval_to_polynom_at_polynom_polynom_mpz
 * Assign to @var{R} the polynomial obtained by evaluating 
 * @var{A} at @math{v=val}.
 * The evaluation is not differential i.e. derivatives of @var{v}
 * do not get evaluated at derivatives of @var{val}.

BAP_DLL void
bap_eval_to_polynom_at_polynom_polynom_mpz (
    struct bap_polynom_mpz * R,
    struct bap_polynom_mpz * A,
    struct bav_variable * v,
    struct bap_polynom_mpz * val)
{
  struct bap_geobucket_mpz geo;
  struct bap_polynom_mpz B, coeff, value;
  struct bap_itercoeff_mpz iter;
  struct bav_term T;
  bav_Idegree d;
  bav_Iordering r;
  struct ba0_mark M;

  bap__check_ordering_mpz (A);
  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  r = bav_R_copy_ordering (bav_current_ordering ());
  bav_push_ordering (r);
  bav_R_set_maximal_variable (v);

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&T);

  bap_init_readonly_polynom_mpz (&B);
  bap_init_readonly_polynom_mpz (&coeff);
  bap_init_readonly_polynom_mpz (&value);
//  bap_init_polynom_mpz (&G);
  bap_init_geobucket_mpz (&geo);
  bap_sort_polynom_mpz (&B, A);
  bap_sort_polynom_mpz (&value, val);

  if (!bap_is_numeric_polynom_mpz (&B) && bap_leader_polynom_mpz (&B) == v)
    {
      bap_begin_itercoeff_mpz (&iter, &B, v);
      bap_coeff_itercoeff_mpz (&coeff, &iter);
      bap_term_itercoeff_mpz (&T, &iter);
//      bap_set_polynom_mpz (&G, &coeff);
      bap_add_geobucket_mpz (&geo, &coeff);

   Horner scheme

      for (d = bav_degree_term (&T, v) - 1; d >= 0; d--)
        {
//          bap_mul_polynom_mpz (&G, &G, &value);
          bap_mul_geobucket_mpz (&geo, &value);
          bav_set_term_variable (&T, v, d);
          bap_seek_coeff_itercoeff_mpz (&coeff, &iter, &T);
          if (!bap_is_zero_polynom_mpz (&coeff))
            {
//              bap_add_polynom_mpz (&G, &G, &coeff);
              bap_add_geobucket_mpz (&geo, &coeff);
            }
        }
      bap_close_itercoeff_mpz (&iter);
      ba0_pull_stack ();
//      bap_set_polynom_mpz (R, &G);
      bap_set_polynom_geobucket_mpz (R, &geo);
    }
  else
    {
      ba0_pull_stack ();
      if (R != A)
        bap_set_polynom_mpz (R, A);
    }
  ba0_restore (&M);
  bav_pull_ordering ();
  bav_R_free_ordering (r);
  bap_physort_polynom_mpz (R);
}
 */

#endif

#if defined (BAD_FLAG_mpz) || defined (BAD_FLAG_mpzm)
/*
 * texinfo: bap_eval_to_polynom_at_value_int_p_polynom_mpz
 * Assign to @var{R} the polynomial obtained by evaluating @var{A} at @var{val}.
 */

BAP_DLL void
bap_eval_to_polynom_at_value_int_p_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A,
    struct bav_value_int_p *val)
{
  ba0_mpz_t c;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mpz_init_set_si (c, val->value);
  ba0_pull_stack ();

  bap_eval_to_polynom_at_numeric_polynom_mpz (R, A, val->var, c);
  ba0_restore (&M);
}

/*
 * texinfo: bap_eval_to_polynom_at_point_int_p_polynom_mpz
 * Assign @var{A} mod @var{point} to @var{R}.
 */

BAP_DLL void
bap_eval_to_polynom_at_point_int_p_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A,
    struct bav_point_int_p *point)
{
  if (point->size == 0)
    {
      if (A != R)
        bap_set_polynom_mpz (R, A);
    }
  else if (point->size == 1)
    bap_eval_to_polynom_at_value_int_p_polynom_mpz (R, A, point->tab[0]);
  else
    {
      struct bap_polynom_mpz B;
      ba0_int_p i;
      struct ba0_mark M;

      ba0_push_another_stack ();
      ba0_record (&M);
      bap_init_polynom_mpz (&B);
      bap_eval_to_polynom_at_value_int_p_polynom_mpz (&B, A, point->tab[0]);
      for (i = 1; i < point->size - 1; i++)
        bap_eval_to_polynom_at_value_int_p_polynom_mpz (&B, &B,
            point->tab[i]);
      ba0_pull_stack ();
      bap_eval_to_polynom_at_value_int_p_polynom_mpz (R, &B,
          point->tab[point->size - 1]);
      ba0_restore (&M);
    }
}

/*
 * texinfo: bap_eval_to_numeric_at_point_int_p_polynom_mpz
 * Assign @var{A} modulo @var{point} to @var{res}.
 * Exception @code{BA0_ERRALG} is raised if some variables of @var{A}
 * do not get evaluated.
 */

BAP_DLL void
bap_eval_to_numeric_at_point_int_p_polynom_mpz (
    ba0_mpz_t *res,
    struct bap_polynom_mpz *A,
    struct bav_point_int_p *point)
{
  struct bap_itermon_mpz iter;
  ba0_mpz_t v, p;
  struct bav_term T;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&T);
  ba0_mpz_init (v);
  ba0_mpz_init (p);

  bap_begin_itermon_mpz (&iter, A);
  while (!bap_outof_itermon_mpz (&iter))
    {
      bap_term_itermon_mpz (&T, &iter);
      bav_term_at_point_int_p (p, &T, point);
      ba0_mpz_mul (p, *bap_coeff_itermon_mpz (&iter), p);
      ba0_mpz_add (v, v, p);
      bap_next_itermon_mpz (&iter);
    }
  ba0_pull_stack ();
  ba0_mpz_set (*res, v);
  ba0_restore (&M);
}

/*
 * texinfo: bap_evalcoeff_at_point_int_p_polynom_mpz
 * Assign to @var{R} the polynomial @var{A} modulo @var{point}.
 * It is assumed that @var{point} gives values to all the variables of @var{A}
 * apart its leader.
 */

BAP_DLL void
bap_evalcoeff_at_point_int_p_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A,
    struct bav_point_int_p *point)
{
  struct bap_creator_mpz crea;
  struct bap_itercoeff_mpz iter;
  struct bap_polynom_mpz C;
  struct bap_polynom_mpz *P;
  struct bav_term T;
  ba0_mpz_t c;
  struct bav_rank rg;
  struct ba0_mark M;

  if (R->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (bap_is_numeric_polynom_mpz (A))
    {
      if (A != R)
        bap_set_polynom_mpz (R, A);
      return;
    }

  ba0_push_another_stack ();
  ba0_record (&M);

  bap_init_polynom_mpz (&C);
  ba0_mpz_init (c);

  rg = bap_rank_polynom_mpz (A);
  bav_init_term (&T);
  bav_set_term_rank (&T, &rg);
  P = bap_new_polynom_mpz ();
  bap_begin_creator_mpz (&crea, P, &T, bap_approx_total_rank, rg.deg);
  bap_begin_itercoeff_mpz (&iter, A, rg.var);
  while (!bap_outof_itercoeff_mpz (&iter))
    {
      bap_coeff_itercoeff_mpz (&C, &iter);
      bap_term_itercoeff_mpz (&T, &iter);
      bap_eval_to_numeric_at_point_int_p_polynom_mpz (&c, &C, point);
      if (!ba0_mpz_is_zero (c))
        bap_write_creator_mpz (&crea, &T, c);
      bap_next_itercoeff_mpz (&iter);
    }
  bap_close_creator_mpz (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mpz (R, P);
  ba0_restore (&M);
}

#endif
#undef BAD_FLAG_mpz
