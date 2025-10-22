#include "baz_eval_polyspec_mpz.h"
#include "baz_eval_ratfrac.h"

/*
 * texinfo: baz_eval_to_ratfrac_at_ratfrac_polynom_mpz
 * Assign to @var{R} the rational fraction obtained by evaluating
 * @var{A} at @var{point}. 
 * The substitution is parallel: values are not substituted into values.
 * The evaluation is not differential.
 */

BAZ_DLL void
baz_eval_to_ratfrac_at_point_ratfrac_polynom_mpz (
    struct baz_ratfrac *R,
    struct bap_polynom_mpz *A,
    struct baz_point_ratfrac *point)
{
  struct baz_point_ratfrac pnt;
  struct baz_ratfrac result, val_term, tmp;
  struct bap_polynom_mpz B, coeff;
  struct bap_itercoeff_mpz iter;
  struct bav_term term, prev_term, ratio;
  struct bav_variable *v;
  bav_Iordering r;
  struct ba0_mark M;
  ba0_int_p i;

  ba0_push_another_stack ();
  ba0_record (&M);
/*
 * pnt = the values useful for evaluating A
 */
  ba0_init_point ((struct ba0_point *) &pnt);
  ba0_set_point ((struct ba0_point *) &pnt, (struct ba0_point *) point);
  i = pnt.size - 1;
  while (i > 0)
    {
      if (!bap_depend_polynom_mpz (A, pnt.tab[i]->var))
        ba0_delete_point ((struct ba0_point *) &pnt, (struct ba0_point *) &pnt,
            i);
      i -= 1;
    }
/*
 * To avoid pointless computations
 */
  if (pnt.size == 0)
    {
      ba0_pull_stack ();
      ba0_restore (&M);

      baz_set_ratfrac_polynom_mpz (R, A);
      return;
    }
/*
 * Create an ordering r such that the evaluated variables are
 * greater than any other one
 */
  r = bav_R_copy_ordering (bav_current_ordering ());
  bav_push_ordering (r);
  for (i = 0; i < pnt.size; i++)
    {
      v = pnt.tab[i]->var;
      bav_R_set_maximal_variable (v);
    }
/*
 * Sort the values of pnt w.r.t. r
 */
  for (i = 0; i < pnt.size; i++)
    {
      struct baz_ratfrac *Q = pnt.tab[i]->value;
      pnt.tab[i]->value = baz_new_readonly_ratfrac ();
      baz_sort_ratfrac (pnt.tab[i]->value, Q);
    }

  baz_init_ratfrac (&result);
  baz_init_ratfrac (&tmp);
/*
 * term = 1
 * val_term = term evaluated at point
 */
  bav_init_term (&term);
  baz_init_ratfrac (&val_term);
  baz_set_ratfrac_one (&val_term);
/*
 * prev_term = the previous value of term
 */
  bav_init_term (&prev_term);
  bav_init_term (&ratio);

  bap_init_readonly_polynom_mpz (&B);
  bap_init_readonly_polynom_mpz (&coeff);
  bap_sort_polynom_mpz (&B, A);
/*
 * v = the lowest variable of terms
 */
  v = pnt.tab[0]->var;
  bap_end_itercoeff_mpz (&iter, &B, v);
/*
 * Start with the lowest term to save computations when possible
 * If pnt involves a single value, this is equivalent to Horner scheme
 */
  while (!bap_outof_itercoeff_mpz (&iter))
    {
      BA0_SWAP (struct bav_term,
          term,
          prev_term);
      bap_term_itercoeff_mpz (&term, &iter);
      bap_coeff_itercoeff_mpz (&coeff, &iter);

      if (!bav_is_factor_term (&term, &prev_term, &ratio))
        {
          bav_set_term (&ratio, &term);
          baz_set_ratfrac_one (&val_term);
        }
      while (!bav_is_one_term (&ratio))
        {
          struct baz_value_ratfrac *value;
          v = ratio.rg[0].var;
          value =
              (struct baz_value_ratfrac *) ba0_bsearch_point (v,
              (struct ba0_point *) &pnt, (ba0_int_p *) 0);
          if ((struct ba0_value *) value == BA0_NOT_A_VALUE)
            BA0_RAISE_EXCEPTION (BA0_ERRALG);
          baz_mul_ratfrac (&val_term, &val_term, value->value);
          bav_exquo_term_variable (&ratio, &ratio, v, 1);
        }
      baz_mul_ratfrac_polynom_mpz (&tmp, &val_term, &coeff);
      baz_add_ratfrac (&result, &result, &tmp);
      bap_prev_itercoeff_mpz (&iter);
    }
  bap_close_itercoeff_mpz (&iter);

  ba0_pull_stack ();
  baz_set_ratfrac (R, &result);
  ba0_restore (&M);
  bav_pull_ordering ();
  bav_R_free_ordering (r);
  baz_physort_ratfrac (R);
}
