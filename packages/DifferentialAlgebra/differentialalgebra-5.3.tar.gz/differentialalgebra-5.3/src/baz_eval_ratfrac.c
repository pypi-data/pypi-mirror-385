#include "baz_eval_polyspec_mpz.h"
#include "baz_eval_ratfrac.h"

/*
 * texinfo: baz_eval_to_polynom_at_point_int_p_ratfrac
 * Assign @var{A} mod @var{point} to @var{R}.
 * Exception @code{BA0_ERRALG} is raised if some variables of 
 * the denominator of @var{A} do not get evaluated.
 * Exception @code{BA0_ERRIVZ} is raised if the denominator
 * of @var{A} evaluates to zero.
 */

BAZ_DLL void
baz_eval_to_polynom_at_point_int_p_ratfrac (
    struct bap_polynom_mpq *R,
    struct baz_ratfrac *A,
    struct bav_point_int_p *point)
{
  struct bap_polynom_mpz numer;
  ba0_mpz_t denom;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_mpz_init (denom);
  bap_eval_to_numeric_at_point_int_p_polynom_mpz (&denom, &A->denom, point);
  if (ba0_mpz_sgn (denom) == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRIVZ);
  bap_init_polynom_mpz (&numer);
  bap_eval_to_polynom_at_point_int_p_polynom_mpz (&numer, &A->numer, point);

  ba0_pull_stack ();
  bap_set_polynom_numer_denom_mpq (R, &numer, denom);
  ba0_restore (&M);
}

/*
 * texinfo: baz_eval_to_ratfrac_at_point_ratfrac_ratfrac
 * Assign to @var{R} the rational fraction obtained by evaluating @var{A}
 * at @var{point}. The evaluation is non differential.
 */

BAZ_DLL void
baz_eval_to_ratfrac_at_point_ratfrac_ratfrac (
    struct baz_ratfrac *R,
    struct baz_ratfrac *A,
    struct baz_point_ratfrac *point)
{
  struct baz_ratfrac numer, denom;
  struct ba0_mark M;
  ba0_push_another_stack ();
  ba0_record (&M);

  baz_init_ratfrac (&numer);
  baz_init_ratfrac (&denom);
  baz_eval_to_ratfrac_at_point_ratfrac_polynom_mpz (&numer, &A->numer, point);
  baz_eval_to_ratfrac_at_point_ratfrac_polynom_mpz (&denom, &A->denom, point);
  ba0_pull_stack ();
  baz_div_ratfrac (R, &numer, &denom);
  ba0_restore (&M);
}

/*
 * texinfo: baz_evaluate_to_ratfrac_at_point_ratfrac_ratfrac
 * Assign to @var{R} the rational fraction obtained by evaluating @var{A}
 * at @var{point}. 
 * The evaluation is differential: the evaluation point used for 
 * evaluating @var{A} is obtained by prolongating @var{point} 
 * (see @code{baz_prolongate_point_ratfrac}) but
 * the parameter @var{point} is left unchanged.
 */

BAZ_DLL void
baz_evaluate_to_ratfrac_at_point_ratfrac_ratfrac (
    struct baz_ratfrac *R,
    struct baz_ratfrac *A,
    struct baz_point_ratfrac *point)
{
  struct baz_point_ratfrac pnt;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_init_point ((struct ba0_point *) &pnt);
  ba0_set_point ((struct ba0_point *) &pnt, (struct ba0_point *) point);
  baz_prolongate_point_ratfrac_term (&pnt, &pnt, &A->numer.total_rank);
  baz_prolongate_point_ratfrac_term (&pnt, &pnt, &A->denom.total_rank);
  ba0_pull_stack ();
  baz_eval_to_ratfrac_at_point_ratfrac_ratfrac (R, A, &pnt);
  ba0_restore (&M);
}

/*
 * texinfo: baz_twice_evaluate_to_ratfrac_at_point_ratfrac_ratfrac
 * Assign to @var{R} the rational fraction obtained by evaluating @var{A}
 * at a point as explained below.
 * The evaluation point used for evaluating @var{A} is obtained by 
 * prolongating @var{point0} (by means of differentiations), then
 * evaluating the right hand sides at @var{point1} (without any
 * prolongation).
 * The substitution is parallel: values are not substituted into values.
 * This function is useful for evaluating a rational fraction in @math{y}
 * at a series @math{\bar{y}}$ in an independent variable @math{x}, then
 * evaluate the result at @math{x=0}.
 */

BAZ_DLL void
baz_twice_evaluate_to_ratfrac_at_point_ratfrac_ratfrac (
    struct baz_ratfrac *R,
    struct baz_ratfrac *A,
    struct baz_point_ratfrac *point0,
    struct baz_point_ratfrac *point1)
{
  struct baz_point_ratfrac pnt;
  struct ba0_mark M;
  ba0_int_p i;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_init_point ((struct ba0_point *) &pnt);
  ba0_set_point ((struct ba0_point *) &pnt, (struct ba0_point *) point0);
  baz_prolongate_point_ratfrac_term (&pnt, &pnt, &A->numer.total_rank);
  baz_prolongate_point_ratfrac_term (&pnt, &pnt, &A->denom.total_rank);
  for (i = 0; i < pnt.size; i++)
    {
      struct baz_ratfrac *Q = pnt.tab[i]->value;
      pnt.tab[i]->value = baz_new_ratfrac ();
      baz_eval_to_ratfrac_at_point_ratfrac_ratfrac (pnt.tab[i]->value, Q,
          point1);
    }
  ba0_pull_stack ();
  baz_eval_to_ratfrac_at_point_ratfrac_ratfrac (R, A, &pnt);
  ba0_restore (&M);
}
