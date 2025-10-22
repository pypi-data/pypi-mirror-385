#include "bas_positive_integer_roots.h"

/*
 * texinfo: bas_nonnegative_integer_roots
 * Assign to @var{T} the nonnegative integer roots of @var{P},
 * viewed as a univariate polynomial in @var{v}, with coefficients
 * taken modulo the ideal defined by @var{A}.
 * If @var{v} is @code{BAV_NOT_A_VARIABLE}, it is supposed to
 * be the leader of @var{P}.
 * The roots are sorted by increasing value.
 */

BAS_DLL void
bas_nonnegative_integer_roots (
    struct ba0_tableof_mpz *T,
    struct bap_polynom_mpz *P,
    struct bav_variable *v,
    struct bad_regchain *A)
{
  struct baz_tableof_ratfrac U;
  struct bav_point_int_p point;
  struct bap_tableof_polynom_mpq V;
  struct bap_polynom_mpq Q, constant_coeff;
  struct bav_variable *u;
  bav_Iordering r;
  ba0_int_p d, i, j;
  struct ba0_mark M0, M1;

  ba0_reset_table ((struct ba0_table *) T);

  if (v == BAV_NOT_A_VARIABLE)
    v = bap_leader_polynom_mpz (P);

  d = bap_degree_polynom_mpz (P, v);

  if (d < 1)
    {
      if (d < 0)
        {
          ba0_realloc2_table ((struct ba0_table *) T, 1,
              (ba0_new_function *) & ba0_new_mpz);
          ba0_mpz_set_si (T->tab[0], 0);
          T->size = 1;
        }
      return;
    }

  ba0_push_another_stack ();
  ba0_record (&M0);

  {
    struct bap_polynom_mpz C;
/*
 * U the table of the normal forms of the coefficients of P
 */
    bap_init_polynom_mpz (&C);
    ba0_init_table ((struct ba0_table *) &U);
    ba0_realloc2_table ((struct ba0_table *) &U, d + 1,
        (ba0_new_function *) & baz_new_ratfrac);
    for (i = 0; i <= d; i++)
      {
        bap_coeff_polynom_mpz (&C, P, v, i);
        bad_normal_form_polynom_mod_regchain (U.tab[i], &C, A,
            (struct bap_polynom_mpz **) 0);
      }
  }
/*
 * Update the degree d
 */
  while (d > 0 && baz_is_zero_ratfrac (U.tab[d]))
    d -= 1;
  U.size = d + 1;
  if (d == 0)
    {
      ba0_pull_stack ();
      ba0_restore (&M0);
      return;
    }
/*
 * vars the table of the variables occurring in the denominators
 */
  ba0_record (&M1);

  {
    struct bav_dictionary_variable dict;
    struct bav_tableof_variable vars;
    ba0_int_p size, log2_size;

    log2_size = 8;
    size = 1 << log2_size;
    bav_init_dictionary_variable (&dict, log2_size);
    ba0_init_table ((struct ba0_table *) &vars);
    ba0_realloc_table ((struct ba0_table *) &vars, size);

    for (i = 0; i <= d; i++)
      bap_mark_indets_polynom_mpz (&dict, &vars, &U.tab[i]->denom);
/*
 * point the evaluation point in order to get rid of denominators
 */
    ba0_init_point ((struct ba0_point *) &point);
    ba0_realloc2_table ((struct ba0_table *) &point, vars.size,
        (ba0_new_function *) & ba0_new_value);
    for (i = 0; i < vars.size; i++)
      {
        point.tab[i]->var = vars.tab[i];
        point.tab[i]->value = 0;
      }
    point.size = vars.size;
    ba0_sort_point ((struct ba0_point *) &point, (struct ba0_point *) &point);
  }

  if (point.size > 0)
    {
      struct bap_tableof_polynom_mpz nonzero;
      struct bap_product_mpz prod;
/*
 * nonzero the table of the polynomials which must not vanish:
 * - the denominators
 * - the numerator of the leading coefficient
 */
      ba0_init_table ((struct ba0_table *) &nonzero);
      ba0_realloc_table ((struct ba0_table *) &nonzero, d + 2);
      for (i = 0; i <= d; i++)
        nonzero.tab[i] = &U.tab[i]->denom;
      nonzero.tab[d + 1] = &U.tab[d]->numer;
      nonzero.size = d + 2;
/*
 * Computation of the evaluation point
 */
      bap_init_product_mpz (&prod);
      baz_yet_another_point_int_p_mpz (&point, &nonzero, &prod,
          BAV_NOT_A_VARIABLE);
    }
/*
 * V the table of the polynomials obtained by evaluation of the normal forms
 */
  ba0_init_table ((struct ba0_table *) &V);
  ba0_realloc2_table ((struct ba0_table *) &V, d + 1,
      (ba0_new_function *) & bap_new_polynom_mpq);
  for (i = 0; i <= d; i++)
    baz_eval_to_polynom_at_point_int_p_ratfrac (V.tab[i], U.tab[i], &point);
  V.size = d + 1;
/*
 * The variable v becomes the lowest variable
 */
  r = bav_R_copy_ordering (bav_current_ordering ());
  bav_push_ordering (r);
  bav_R_set_minimal_variable (v);

  {
    struct bap_geobucket_mpq geo;
/*
 * Q the polynomial obtained by forming the sum of the V[i] * v**i
 */
    bap_init_geobucket_mpq (&geo);
    bap_init_polynom_mpq (&Q);
    for (i = 0; i <= d; i++)
      {
        bap_sort_polynom_mpq (V.tab[i], V.tab[i]);
        bap_mul_polynom_variable_mpq (&Q, V.tab[i], v, i);
        bap_add_geobucket_mpq (&geo, &Q);
      }
    bap_set_polynom_geobucket_mpq (&Q, &geo);
  }

/*
 * W the table of the coefficients of Q (coefficients being polynomials in v)
 * Q the gcd of the elements of W
 */
  u = bav_smallest_greater_variable (v);
  if (u != BAV_NOT_A_VARIABLE)
    {
// if (u == BAV_NOT_A_VARIABLE) there is nothing to do
      struct bap_tableof_polynom_mpz W;
      struct bap_polynom_mpq C;
      struct bap_itercoeff_mpq iter;
      struct bap_polynom_mpz gcd;
      struct bap_product_mpz gcd_prod;

      ba0_init_table ((struct ba0_table *) &W);
      bap_init_readonly_polynom_mpq (&C);
      bap_begin_itercoeff_mpq (&iter, &Q, u);
      while (!bap_outof_itercoeff_mpq (&iter))
        {
          if (W.size == W.alloc)
            {
              ba0_realloc2_table ((struct ba0_table *) &W, 2 * W.alloc + 1,
                  (ba0_new_function *) & bap_new_polynom_mpz);
            }
          bap_coeff_itercoeff_mpq (&C, &iter);
          bap_numer_polynom_mpq (W.tab[W.size], (ba0__mpz_struct *) 0, &C);
          W.size += 1;
          bap_next_itercoeff_mpq (&iter);
        }
      bap_close_itercoeff_mpq (&iter);
      bap_init_product_mpz (&gcd_prod);
      baz_gcd_tableof_polynom_mpz (&gcd_prod, &W, false);
      bap_init_polynom_mpz (&gcd);
      bap_expand_product_mpz (&gcd, &gcd_prod);
      bap_set_polynom_numer_denom_mpq (&Q, &gcd, (ba0__mpz_struct *) 0);
    }
/*
 * Compute the positive integer roots of Q
 */
  bap_init_polynom_mpq (&constant_coeff);
  bap_coeff_polynom_mpq (&constant_coeff, &Q, v, 0);

  ba0_pull_stack ();
  if (bap_is_numeric_polynom_mpq (&Q))
    ba0_reset_table ((struct ba0_table *) T);
  else
    baz_positive_integer_roots_polynom_mpq (T, &Q);
/*
 * Add the zero root if any
 */
  if (bap_is_zero_polynom_mpq (&constant_coeff))
    {
      ba0__mpz_struct *z = ba0_new_mpz ();
      ba0_insert_table ((struct ba0_table *) T, 0, z);
    }

  ba0_push_another_stack ();
/*
 * Remove the temporary ranking
 */
  bav_pull_ordering ();
  bav_R_free_ordering (r);
  ba0_restore (&M1);
/*
 * Remove the roots of Q which are not roots of P
 */
  {
    struct baz_ratfrac result;

    i = T->size - 1;
    baz_init_ratfrac (&result);
    while (i >= 0)
      {
// Horner scheme
        baz_set_ratfrac (&result, U.tab[d]);
        for (j = d - 1; j >= 0; j--)
          {
            baz_mul_ratfrac_numeric (&result, &result, T->tab[i]);
            baz_add_ratfrac (&result, &result, U.tab[j]);
          }
// The ba0_delete_table function does not allocate memory
        if (!baz_is_zero_ratfrac (&result))
          ba0_delete_table ((struct ba0_table *) T, i);
        i -= 1;
      }
  }

  ba0_pull_stack ();
  ba0_restore (&M0);
}
