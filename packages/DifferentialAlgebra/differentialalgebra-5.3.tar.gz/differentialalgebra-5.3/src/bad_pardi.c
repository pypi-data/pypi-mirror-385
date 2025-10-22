#include "bad_splitting_tree.h"
#include "bad_reduction.h"
#include "bad_regularize.h"
#include "bad_quadruple.h"
#include "bad_pardi.h"
#include "bad_global.h"
#include "bad_stats.h"

static void bad_pardi_set_quadruple_regchain (
    struct bad_quadruple *,
    bool *,
    struct bad_regchain *,
    struct bad_base_field *);

static void bad_throw_nonzero_factors_mod_regchain (
    struct bap_polynom_mpz *,
    struct bap_product_mpz *,
    struct bad_regchain *,
    struct bad_base_field *);

static void bad_ensure_rank (
    struct bap_polynom_mpz *,
    bool *,
    struct bad_quadruple *,
    struct bad_regchain *,
    struct bad_base_field *);

#define BAD_PARDI_DEBUG 1
#undef BAD_PARDI_DEBUG

/*
 * texinfo: bad_pardi
 * Compute a regular differential chain by change of ranking.
 * Assign to @var{Cbar} a regular chain with respect to the ordering @var{rbar}
 * defining the same ideal as @var{C}. The differential ideal and
 * prime ideal properties of
 * @var{Cbar} are inherited from @var{C}. The other properties must be 
 * set before calling the function.
 */

BAD_DLL void
bad_pardi (
    struct bad_regchain *Cbar,
    bav_Iordering rbar,
    struct bad_regchain *C)
{
  struct bad_base_field K;
  struct bad_selection_strategy *strategy;
  enum bad_typeof_reduction type_red;
  struct bad_tableof_quadruple *tabG;
  struct bad_quadruple *G;
  struct bad_intersectof_regchain *tabCbar;
  struct bav_tableof_term *theta = 0;
  struct bad_splitting_tree tree;
  bool *discarded_branch = 0;
  struct bap_product_mpz prod;
  struct bap_tableof_polynom_mpz ineqs;
  struct bap_tableof_product_mpz factored_ineqs;
  struct bap_tableof_tableof_polynom_mpz tabV;
  struct bap_tableof_polynom_mpz V;
  struct bap_polynom_mpz p;
  struct bav_variable *v;
  ba0_int_p counter, k;
  struct ba0_mark M;

  bad_init_stats ();
  bad_global.stats.begin = time (0);

  bad_init_splitting_tree (&tree);
  bad_reset_splitting_tree (&tree, bad_inactive_splitting_tree);

  ba0_push_another_stack ();
  ba0_record (&M);
/*
 * Generalize me: pass K and strategy as a parameter
 */
  bad_init_base_field (&K);

  bav_push_ordering (rbar);
/*
   tabG is a table containing a unique quadruple : G.
   G is initialized to < [], [], C, H_C w.r.t. the ordering of C >
   The differential ideal property of G->A are that of C (not prime ideal !)
   The other properties of G->A are that of Cbar.
 */
  tabG = (struct bad_tableof_quadruple *) ba0_new_table ();
  ba0_realloc2_table ((struct ba0_table *) tabG, 1,
      (ba0_new_function *) & bad_new_quadruple);
  tabG->size = 1;

  G = tabG->tab[0];

  G->A.attrib.property = Cbar->attrib.property;
  bad_clear_property_attchain (&G->A.attrib, bad_differential_ideal_property);
  bad_clear_property_attchain (&G->A.attrib, bad_prime_ideal_property);
  if (bad_defines_a_differential_ideal_regchain (C))
    {
      bad_set_property_attchain (&G->A.attrib, bad_differential_ideal_property);
      bad_set_property_attchain (&G->A.attrib, bad_squarefree_property);
    }
  bad_pardi_set_quadruple_regchain (G, discarded_branch, C, &K);
/*
   Working variables
*/
  bap_init_product_mpz (&prod);
  ba0_init_table ((struct ba0_table *) &ineqs);
  ba0_init_table ((struct ba0_table *) &factored_ineqs);
  ba0_init_table ((struct ba0_table *) &tabV);
  ba0_realloc_table ((struct ba0_table *) &tabV, 1);
  tabV.tab[0] = &V;
  tabV.size = 1;
  ba0_init_table ((struct ba0_table *) &V);
  bap_init_polynom_mpz (&p);
  type_red =
      bad_defines_a_differential_ideal_regchain (C) ? bad_full_reduction :
      bad_algebraic_reduction;
/*
   Loop while a critical pair or a polynomial is waiting for being processed
*/
  counter = 0;

  strategy = bad_new_selection_strategy ();
  bad_set_strategy_selection_strategy (strategy,
      bad_lower_leader_first_selection_strategy);

  while (!bad_is_a_listof_rejected_critical_pair (G->D)
      || G->P != (struct bap_listof_polynom_mpz *) 0)
    {
      struct bad_critical_pair *pair;
/*
   One picks a new equation (from P or a Delta-polynomial from D).
   One reduces it (here, fully) w.r.t. A.
   The reduction process outputs a product of factors.
   At least one of the factors lies in ideal (C). 
   One sets p to any of them and one ensures that the initial and the 
	separant of p does not lie in ideal (C).
 */
#if defined (BAD_PARDI_DEBUG)
      ba0_printf ("pardi: loop %d\n", counter);
#endif
      counter += 1;
      bad_pick_and_remove_quadruple (&p, G, &pair, strategy);
/*
   If the reduction to zero test is deterministic, we may as well
   skip it since we are going to reduce p anyway.

   If it is probabilistic, it is better to perform it before
   the reduction.
 */
      if (bad_initialized_global.reduction.redzero_strategy ==
          bad_probabilistic_redzero_strategy)
        {
          if (bad_is_a_reduced_to_zero_polynom_by_regchain (&p, &G->A,
                  type_red))
            {
              bad_global.stats.reductions_to_zero += 1;
              continue;
            }
        }

      bad_reduce_polynom_by_regchain (&prod, (struct bap_product_mpz *) 0,
          (struct bav_tableof_term *) 0, &p,
          &G->A, type_red, bad_all_derivatives_to_reduce);
      bad_preprocess_equation_quadruple (&prod, &ineqs, &factored_ineqs,
          discarded_branch, G, &K);
      bad_report_simplification_of_inequations_quadruple (tabG, &ineqs,
          &factored_ineqs);
      if (tabG->size != 1)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
      bad_throw_nonzero_factors_mod_regchain (&p, &prod, C, &K);
      bad_ensure_rank (&p, discarded_branch, G, C, &K);
      if (bap_is_zero_polynom_mpz (&p))
        {
          bad_global.stats.reductions_to_zero += 1;
          continue;
        }
/*
 * Some critical pairs would be discarded by the easy criterion
 * but give interesting nonzero polynomials. Since it happens
 * at the beginning of the computations, the penalty for some
 * pairs is increased.
 */
      if (pair && pair->tag != bad_normal_critical_pair)
        {
          bad_double_penalty_selection_strategy (strategy);
        }

      if (bad_member_polynom_base_field (&p, &K))
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
      v = bap_leader_polynom_mpz (&p);

      if (!bad_is_leader_of_regchain (v, &G->A, &k))
        bad_complete_quadruple (tabG, theta, discarded_branch, &tree, &p, C, &K,
            strategy);
      else
        {
          bad_Euclid_mod_regchain (&tabV, tabG, bad_basic_Euclid,
              G->A.decision_system.tab[k], &p, v, true, true, C, &K,
              (struct bap_polynom_mpz * *) 0);
/*
   Completion only if the gcd is different from the element of A.
   Observe that the gcd is always different from the element of A when
	full reduction is performed.
 */
          if (bap_leading_degree_polynom_mpz (V.tab[0]) !=
              bap_leading_degree_polynom_mpz (G->A.decision_system.tab[k]))
            bad_complete_quadruple (tabG, theta, discarded_branch, &tree,
                V.tab[0], C, &K, strategy);
        }
    }
/*
   G = < A, [], [], S > and A = 0, S <> 0 is a regular differential system.
   One performs reg_characteristic.

   tabCbar is allocated in the working stack.
   This is not a problem for ideal (C) is prime hence no splittings will occur.
*/
  tabCbar = bad_new_intersectof_regchain ();
  ba0_realloc_table ((struct ba0_table *) &tabCbar->inter, 1);
  tabCbar->inter.tab[0] = Cbar;
  tabCbar->inter.size = 0;
/*
   The differential ideal and prime ideal properties of Cbar are 
        inherited from C (even primality this time).
*/
  if (bad_has_property_attchain (&C->attrib, bad_differential_ideal_property))
    bad_set_property_attchain (&tabCbar->attrib,
        bad_differential_ideal_property);
  if (bad_has_property_attchain (&C->attrib, bad_prime_ideal_property))
    bad_set_property_attchain (&tabCbar->attrib, bad_prime_ideal_property);

  ba0_pull_stack ();

  bad_global.stats.end = time (0);

  bad_reg_characteristic_quadruple (tabCbar, G, C, &K);
  if (bad_has_property_attchain (&C->attrib, bad_differential_ideal_property))
    bad_set_property_attchain (&Cbar->attrib, bad_differential_ideal_property);
  if (bad_has_property_attchain (&C->attrib, bad_prime_ideal_property))
    bad_set_property_attchain (&Cbar->attrib, bad_prime_ideal_property);
  if (bad_defines_a_differential_ideal_regchain (Cbar))
    bad_set_property_attchain (&Cbar->attrib, bad_coherence_property);

  ba0_restore (&M);
  bav_pull_ordering ();
}

/*
   Store C in P and H_C (or I_C in the algebraic case) taken w.r.t. the
	ordering of C in S.

   The current ordering is rbar.

    discarded_branch is unused.
*/

static void
bad_pardi_set_quadruple_regchain (
    struct bad_quadruple *G,
    bool *discarded_branch,
    struct bad_regchain *C,
    struct bad_base_field *K)
{
  struct bap_polynom_mpz pbar, init, sep;
  ba0_int_p i;

  bap_init_readonly_polynom_mpz (&pbar);

  bap_init_readonly_polynom_mpz (&init);
  if (bad_defines_a_differential_ideal_regchain (C))
    bap_init_polynom_mpz (&sep);

  for (i = 0; i < C->decision_system.size; i++)
    {
      bap_sort_polynom_mpz (&pbar, C->decision_system.tab[i]);
      G->P = bad_insert_in_listof_polynom_mpz (&pbar, G->P);

      bav_push_ordering (C->attrib.ordering);

      bap_initial_polynom_mpz (&init, C->decision_system.tab[i]);

      if (!bad_member_polynom_base_field (&init, K))
        {
          bav_pull_ordering ();
          bap_sort_polynom_mpz (&pbar, &init);
          bad_simplify_and_store_in_S_quadruple (G, discarded_branch, &pbar, K);
          bav_push_ordering (C->attrib.ordering);
        }

      if (bad_defines_a_differential_ideal_regchain (C)
          && bap_leading_degree_polynom_mpz (C->decision_system.tab[i]) > 1)
        {
          bap_separant_polynom_mpz (&sep, C->decision_system.tab[i]);
          bav_pull_ordering ();
          bap_sort_polynom_mpz (&pbar, &sep);
          bad_simplify_and_store_in_S_quadruple (G, discarded_branch, &pbar, K);
          bav_push_ordering (C->attrib.ordering);
        }

      bav_pull_ordering ();
    }
}

/*
 * Assigns to p the only factor of p which is zero mod C
 */

static void
bad_throw_nonzero_factors_mod_regchain (
    struct bap_polynom_mpz *p,
    struct bap_product_mpz *prod,
    struct bad_regchain *C,
    struct bad_base_field *K)
{
  enum bad_typeof_reduction type_red;
  ba0_int_p i;
  bool found;

  type_red =
      bad_defines_a_differential_ideal_regchain (C) ? bad_full_reduction :
      bad_algebraic_reduction;

  if (bap_is_zero_product_mpz (prod))
    bap_set_polynom_zero_mpz (p);
  else
    {
      found = false;
      i = 0;
      while (i < prod->size - 1 && !found)
        {
          if (!bad_member_polynom_base_field (&prod->tab[i].factor, K))
            found =
                bad_is_a_reduced_to_zero_polynom_by_regchain (&prod->tab[i].
                factor, C, type_red);
          if (!found)
            i++;
        }
      bap_set_polynom_mpz (p, &prod->tab[i].factor);
    }
}

/*
   If i_p is zero mod C then p := reductum (p)
   else if s_p is zero mod C then p := prem (p, s_p)

   If something is zero mod C but not mod A then it is stored in P.

   discarded_branch is unused.
 */

static void
bad_ensure_rank (
    struct bap_polynom_mpz *p,
    bool *discarded_branch,
    struct bad_quadruple *G,
    struct bad_regchain *C,
    struct bad_base_field *K)
{
  enum bad_typeof_reduction type_red;
  struct bap_product_mpz prod_init, prod_sep;
  struct bap_polynom_mpz init, sep;
  struct ba0_tableof_bool keep;
  struct ba0_mark M;
  ba0_int_p i;
  bool rankfall, reduced_to_zero;

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_init_table ((struct ba0_table *) &keep);
  bap_init_readonly_polynom_mpz (&init);
  bap_init_product_mpz (&prod_init);
  if (bad_defines_a_differential_ideal_regchain (&G->A))
    {
      bap_init_polynom_mpz (&sep);
      bap_init_product_mpz (&prod_sep);
      type_red = bad_full_reduction;
    }
  else if (bad_has_property_regchain (&G->A, bad_squarefree_property))
    {
      bap_init_polynom_mpz (&sep);
      bap_init_product_mpz (&prod_sep);
      type_red = bad_algebraic_reduction;
    }
  else
    type_red = bad_algebraic_reduction;


  rankfall = true;
  while (rankfall)
    {
      rankfall = false;
      if (bad_member_polynom_base_field (p, K))
        continue;
      bap_initial_polynom_mpz (&init, p);
      baz_factor_easy_polynom_mpz (&prod_init, &keep, &init, G->S);
      reduced_to_zero = false;
      for (i = 0; i < prod_init.size; i++)
        if (bad_is_a_reduced_to_zero_polynom_by_regchain (&prod_init.tab[i].
                factor, C, type_red))
          {
            reduced_to_zero = true;
            if (!bad_is_a_reduced_to_zero_polynom_by_regchain (&prod_init.tab
                    [i].factor, &G->A, type_red))
              {
                ba0_pull_stack ();
                bad_simplify_and_store_in_P_quadruple (G, discarded_branch,
                    &prod_init.tab[i].factor, K);
                ba0_push_another_stack ();
              }
          }
      if (reduced_to_zero)
        {
          ba0_pull_stack ();
          bap_reductum_polynom_mpz (p, p);
          p->readonly = false;
          ba0_push_another_stack ();
          rankfall = true;
        }
      else if ((bad_defines_a_differential_ideal_regchain (&G->A)
              || bad_has_property_regchain (&G->A, bad_squarefree_property))
          && bap_leading_degree_polynom_mpz (p) > 1)
        {
          bap_separant_polynom_mpz (&sep, p);
          baz_factor_easy_polynom_mpz (&prod_sep, &keep, &sep, G->S);
          reduced_to_zero = false;
          for (i = 0; i < prod_sep.size; i++)
            if (bad_is_a_reduced_to_zero_polynom_by_regchain (&prod_sep.tab[i].
                    factor, C, type_red))
              {
                reduced_to_zero = true;
                if (!bad_is_a_reduced_to_zero_polynom_by_regchain (&prod_sep.tab
                        [i].factor, &G->A, type_red))
                  {
                    ba0_pull_stack ();
                    bad_simplify_and_store_in_P_quadruple (G, discarded_branch,
                        &prod_sep.tab[i].factor, K);
                    ba0_push_another_stack ();
                  }
              }
          if (reduced_to_zero)
            {
              ba0_pull_stack ();
              bap_prem_polynom_mpz (p, (bav_Idegree *) 0, p, &sep,
                  BAV_NOT_A_VARIABLE);
              ba0_push_another_stack ();
              rankfall = true;
            }
        }
    }

  ba0_pull_stack ();

  if (!bap_is_zero_polynom_mpz (p))
    {
      for (i = 0; i < prod_init.size; i++)
        bad_simplify_and_store_in_S_quadruple (G, discarded_branch,
            &prod_init.tab[i].factor, K);
      if ((bad_defines_a_differential_ideal_regchain (&G->A)
              || bad_has_property_regchain (&G->A, bad_squarefree_property))
          && bap_leading_degree_polynom_mpz (p) > 1)
        {
          for (i = 0; i < prod_sep.size; i++)
            bad_simplify_and_store_in_S_quadruple (G, discarded_branch,
                &prod_sep.tab[i].factor, K);
        }
    }

  ba0_restore (&M);
}
