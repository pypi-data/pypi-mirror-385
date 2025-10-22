#include "bad_reduced_form.h"
#include "bad_regularize.h"

/*
 * If F = 0 mod C then 0.
 * If NF (F, C) is a ratfrac whose denominator has rank less than v,
 *    then NF (F, C). 
 * Else
 *    RF (initial) * RF (rank) + RF (tail)
 *
 * Observe v can be zero.
 * The ddz parameter is dummy since the normal form of a polynomial
 *    cannot fail.
 */

static void
bad_reduced_form_polynom_mod_regchain2 (
    struct baz_ratfrac *R,
    struct bap_polynom_mpz *F,
    struct bav_variable *v,
    struct bad_regchain *C,
    bool stop,
    struct bap_polynom_mpz * *ddz)
{
  struct baz_ratfrac RNF, Rinit, Rrg, Rred;
  struct bap_polynom_mpz Frg, init, red;
  struct bav_rank rgv, rgF, rgNF;
  struct ba0_mark M;

  rgv.var = v;
  rgv.deg = 1;

  rgF = bap_rank_polynom_mpz (F);

  if (bap_is_numeric_polynom_mpz (F))
    {
      baz_set_ratfrac_polynom_mpz (R, F);
      return;
    }

  ba0_push_another_stack ();
  ba0_record (&M);

  baz_init_ratfrac (&RNF);
  bad_normal_form_polynom_mod_regchain (&RNF, F, C, ddz);
  rgNF = bap_rank_polynom_mpz (&RNF.denom);
  if ((v == BAV_NOT_A_VARIABLE && bap_is_numeric_polynom_mpz (&RNF.denom))
      || (v != BAV_NOT_A_VARIABLE && bav_lt_rank (&rgNF, &rgv)))
    {
      ba0_pull_stack ();
      baz_set_ratfrac (R, &RNF);
    }
  else if (stop)
/*
 * stop = true iff we are processing RF (rank).
 * To avoid infinite recursion.
 */
    {
      ba0_pull_stack ();
      baz_set_ratfrac_polynom_mpz (R, F);
    }
  else
    {
      bap_init_readonly_polynom_mpz (&init);
      bap_init_readonly_polynom_mpz (&red);
      bap_initial_and_reductum_polynom_mpz (&init, &red, F);
      baz_init_ratfrac (&Rinit);
      bad_reduced_form_polynom_mod_regchain2 (&Rinit, &init, v, C, false, ddz);
      if (!baz_is_zero_ratfrac (&Rinit))
        {
          bap_init_polynom_mpz (&Frg);
          bap_set_polynom_variable_mpz (&Frg, rgF.var, rgF.deg);
          baz_init_ratfrac (&Rrg);
          bad_reduced_form_polynom_mod_regchain2 (&Rrg, &Frg, v, C, true, ddz);
          baz_mul_ratfrac (&Rinit, &Rinit, &Rrg);
        }
      baz_init_ratfrac (&Rred);
      bad_reduced_form_polynom_mod_regchain2 (&Rred, &red, v, C, false, ddz);

      ba0_pull_stack ();
      baz_add_ratfrac (R, &Rinit, &Rred);
    }

  ba0_restore (&M);
}

/*
 * texinfo: bad_reduced_form_polynom_mod_regchain
 * Assign to @var{R} a reduced form of @var{F} with respect to @var{C}.
 * If @var{v} is zero, the reduced form is a polynomial.
 * If @var{v} is nonzero, the reduced form is allowed to have a denominator 
 * of rank strictly less than @var{v}. 
 *
 * More generally, the reduced form @math{@var{RF}(F)} of @var{F} is 
 * defined as follows:
 * if the denominator of @math{@var{NF}(F)} has rank less than @var{v}
 * then @math{@var{RF}(F) = @var{NF}(F)} otherwise, decomposing
 * @math{F = i_F \, u^d + G}, we have 
 * @math{@var{RF}(F) = @var{RF}(i_F)\,@var{RF}(u^d) + @var{RF}(G)}.
 */

BAD_DLL void
bad_reduced_form_polynom_mod_regchain (
    struct baz_ratfrac *R,
    struct bap_polynom_mpz *F,
    struct bav_variable *v,
    struct bad_regchain *C)
{
  bad_reduced_form_polynom_mod_regchain2 (R, F, v, C, false,
      (struct bap_polynom_mpz * *) 0);
  baz_reduce_ratfrac (R, R);
}

/*
 * texinfo: bad_reduced_form_ratfrac_mod_regchain
 * Assign to @var{R} the fraction obtained by applying
 * @code{bad_reduced_form_polynom_mod_regchain} to the
 * numerator and the denominator of @var{F}.

BAD_DLL void
bad_reduced_form_ratfrac_mod_regchain (
    struct baz_ratfrac * R,
    struct baz_ratfrac * F,
    struct bav_variable * v,
    struct bad_regchain * C)
{
  struct baz_ratfrac R1, R2;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  baz_init_ratfrac (&R1);
  baz_init_ratfrac (&R2);
  bad_reduced_form_polynom_mod_regchain2
      (&R1, &F->numer, v, C, false, (struct bap_polynom_mpz * *) 0);
  bad_reduced_form_polynom_mod_regchain2
      (&R2, &F->denom, v, C, false, (struct bap_polynom_mpz * *) 0);
  ba0_pull_stack ();
  baz_div_ratfrac (R, &R1, &R2);
  ba0_restore (&M);
}
 */

/*
 * texinfo: bad_reduced_form_polynom_mod_intersectof_regchain
 * Assign to @var{tabR} the reduced forms of @var{F} w.r.t. each component
 * of @var{tabC}.
 */

BAD_DLL void
bad_reduced_form_polynom_mod_intersectof_regchain (
    struct baz_tableof_ratfrac *tabR,
    struct bap_polynom_mpz *F,
    struct bav_variable *v,
    struct bad_intersectof_regchain *tabC)
{
  ba0_int_p i;

  ba0_reset_table ((struct ba0_table *) tabR);
  ba0_realloc2_table ((struct ba0_table *) tabR, tabC->inter.size,
      (ba0_new_function *) & baz_new_ratfrac);
  for (i = 0; i < tabC->inter.size; i++)
    {
      bad_reduced_form_polynom_mod_regchain2 (tabR->tab[i], F, v,
          tabC->inter.tab[i], false, (struct bap_polynom_mpz * *) 0);
      baz_reduce_ratfrac (tabR->tab[i], tabR->tab[i]);
      tabR->size = i + 1;
    }
}
