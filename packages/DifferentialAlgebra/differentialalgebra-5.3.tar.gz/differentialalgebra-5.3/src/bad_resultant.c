#include "bad_resultant.h"
#include "bad_reduction.h"

/*
 * texinfo: bad_resultant_mod_regchain
 * Assign to @var{R} the resultant of @var{P} with respect to
 * the regular chain @var{A}. If @var{A} is differential then
 * @var{P} is replaced by its partial remainder with respect to @var{A}
 * before the resultant computation.
 * The resulting polynomial is zero if and only if @var{P} is 
 * a zero divisor modulo the ideal defined by @var{A}.
 */

BAD_DLL void
bad_resultant_mod_regchain (
    struct bap_product_mpz *R,
    struct bap_polynom_mpz *P,
    struct bad_regchain *A)
{
  struct bap_product_mpz *prod, *prod2, prod3;
  struct bap_polynom_mpz poly, sorted_Ai;
  struct bav_rank rk;
  bav_Iordering r;
  struct ba0_mark M;
  ba0_int_p i;
  bool nonzero;

  if (bad_is_zero_regchain (A))
    {
      bap_set_product_polynom_mpz (R, P, 1);
      return;
    }

  ba0_push_another_stack ();
  ba0_record (&M);

  prod = bap_new_product_mpz ();
  if (bad_has_property_regchain (A, bad_differential_ideal_property))
    {
      bad_reduce_polynom_by_regchain (prod, (struct bap_product_mpz *) 0,
          (struct bav_tableof_term *) 0, P, A,
          bad_partial_reduction, bad_all_derivatives_to_reduce);
    }
  else
    bap_set_product_polynom_mpz (prod, P, 1);
/*
 * At this stage, prod is partially reduced w.r.t. A
 */
  r = bav_R_copy_ordering (bav_current_ordering ());
  bav_push_ordering (r);

  for (i = 0; i < A->decision_system.size; i++)
    {
      struct bav_variable *v;
      v = bap_leader_polynom_mpz (A->decision_system.tab[i]);
      bav_R_set_maximal_variable (v);
    }
/*
 * The leaders of A are the highest variables in the ordering r
 */
  bap_physort_product_mpz (prod);
  prod2 = bap_new_product_mpz ();
  bap_init_polynom_mpz (&poly);
  bap_init_product_mpz (&prod3);
  rk = bav_constant_rank ();
  nonzero = !bap_is_zero_product_mpz (prod);
  bap_init_readonly_polynom_mpz (&sorted_Ai);
  for (i = A->decision_system.size - 1; nonzero && i >= 0; i--)
    {
      struct bav_variable *v;
      ba0_int_p j;

      v = bap_leader_polynom_mpz (A->decision_system.tab[i]);
      bap_sort_polynom_mpz (&sorted_Ai, A->decision_system.tab[i]);

      bap_set_polynom_crk_mpz (&poly, prod->num_factor, &rk);
      bap_resultant2_Ducos_polynom_mpz (prod2, &poly, &sorted_Ai, v);
      for (j = 0; j < prod->size; j++)
        {
          bap_resultant2_Ducos_polynom_mpz (&prod3, &prod->tab[j].factor,
              &sorted_Ai, v);
          bap_pow_product_mpz (&prod3, &prod3, prod->tab[j].exponent);
          bap_mul_product_mpz (prod2, prod2, &prod3);
        }
      BA0_SWAP (struct bap_product_mpz *,
          prod,
          prod2);
      nonzero = !bap_is_zero_product_mpz (prod);
    }

  bav_pull_ordering ();
  bap_physort_product_mpz (prod);
  bav_R_free_ordering (r);

  ba0_pull_stack ();
  bap_set_product_mpz (R, prod);
  ba0_restore (&M);
}
