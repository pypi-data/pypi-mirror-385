#include "bad_regchain.h"
#include "bad_quench_regchain.h"
#include "bad_regularize.h"
#include "bad_intersectof_regchain.h"
#include "bad_reduction.h"
#include "bad_global.h"
#include "bad_invert.h"

/*
 * texinfo: bad_quench_regchain
 * This function transforms the triangular set @var{C} into one
 * regular chain @var{Cbar}. The properties that @var{Cbar} must
 * satisfy and are not satisfied by @var{C} are described in @var{map}.
 * The process may fail and raise an exception.
 *
 * If nonzero, the argument @var{discarded_branch} is set to @code{true}
 * if one branch has been discarded during the computation (case of
 * a common factor of an element of @var{C} and an initial or a separant).
 * Otherwise, it is set to @code{false}.
 *
 * Exception @code{BAD_EXRCNC} is raised if @var{C} is proved to be
 * inconsistent.
 *
 * Exception @code{BAD_EXRDDZ} is raised if a zerodivisor is exhibited.
 * In this case, if @var{ddz} is nonzero, then it is assigned the
 * exihibited zerodivisor, which has the same leader as some element
 * of @var{C} and an initial regular with respect to @var{C}.
 *
 * Polynomials are supposed to have coefficients in @var{K}.
 * The @code{bad_coherent_property} is not handled in this function.
 */

BAD_DLL void
bad_quench_regchain (
    struct bad_regchain *Cbar,
    struct bad_quench_map *map,
    struct bav_tableof_term *theta,
    bool *discarded_branch,
    struct bad_regchain *C,
    struct bad_base_field *K,
    struct bap_polynom_mpz * *ddz)
{
  struct bad_regchain D;
  struct bap_product_mpz R, U, G;
  struct bap_polynom_mpz init, sep;
  struct bap_polynom_mpz *volatile zerodiv;
  struct bav_tableof_term *phi;
  struct bav_rank rank_before, rank_after;
  volatile ba0_int_p k;
  volatile bool exception_due_to_the_initial, exception_due_to_the_separant;
  struct ba0_mark M;

  if (discarded_branch)
    *discarded_branch = false;
/*
 * Manage not to realloc theta later
 */
  if (theta)
    bad_reset_theta (theta, C);

  bav_push_ordering (C->attrib.ordering);

  ba0_push_another_stack ();
  ba0_record (&M);

  if (theta)
    phi = (struct bav_tableof_term *) ba0_new_table ();
  else
    phi = (struct bav_tableof_term *) 0;

  bad_init_regchain (&D);
  bad_set_regchain (&D, C);

  bap_init_product_mpz (&R);
  bap_init_product_mpz (&U);
  bap_init_product_mpz (&G);

  bap_init_readonly_polynom_mpz (&init);
  bap_init_polynom_mpz (&sep);
/*
 * 1. partially_autoreduced must be satisfied before all other 
 *      properties except autoreduced
 * 2. autoreduced => partially_autoreduced
 * 3. normalized => regular
 * 4. regular must be satisfied before primitive
 *
 *    Indeed, in some contexts, the primitive part of a polynomial
 *    cannot be taken if the initial is not proved to be regular
 *    though this would be possible in some other contexts.
 */
  k = bad_first_index_quench_map (map);
  while (k < C->decision_system.size)
    {
/*
 * 1. autoreduced
 */
      rank_before = bap_rank_polynom_mpz (D.decision_system.tab[k]);

      if (bad_address_property_quench_map (&map->autoreduced, k))
        {
          enum bad_typeof_reduction type_red;

          if (bad_defines_a_differential_ideal_regchain (&D))
            type_red = bad_full_reduction;
          else
            type_red = bad_algebraic_reduction;

          if (bad_is_a_reducible_polynom_by_regchain (D.decision_system.tab[k],
                  &D, type_red, bad_all_but_leader_to_reduce,
                  (struct bav_rank *) 0, (ba0_int_p *) 0))
            {
              bad_reduce_polynom_by_regchain (&R, (struct bap_product_mpz *) 0,
                  phi,
                  D.decision_system.tab[k], &D, bad_full_reduction,
                  bad_all_but_leader_to_reduce);
              bap_expand_product_mpz (D.decision_system.tab[k], &R);

              if (theta)
                {
                  ba0_pull_stack ();
                  bav_lcm_tableof_term (theta, theta, phi);
                  ba0_push_another_stack ();
                }

              rank_after = bap_rank_polynom_mpz (D.decision_system.tab[k]);
              if (!bav_equal_rank (&rank_before, &rank_after))
                BA0_RAISE_EXCEPTION (BAD_EXRCNC);

              bad_fully_reduced_polynom_quench_map (map, k);
            }
          else
            {
              bad_is_an_already_satisfied_property_quench_map
                  (&map->autoreduced, k);
              bad_is_an_already_satisfied_property_quench_map
                  (&map->partially_autoreduced, k);
            }
        }
/*
 * 2. partially_autoreduced
 */
      if (bad_address_property_quench_map (&map->partially_autoreduced, k))
        {
          if (!bad_is_a_partially_reduced_polynom_wrt_regchain
              (D.decision_system.tab[k], &D))
            {
              bad_reduce_polynom_by_regchain (&R, (struct bap_product_mpz *) 0,
                  phi,
                  D.decision_system.tab[k], &D, bad_partial_reduction,
                  bad_all_but_leader_to_reduce);
              bap_expand_product_mpz (D.decision_system.tab[k], &R);

              if (theta)
                {
                  ba0_pull_stack ();
                  bav_lcm_tableof_term (theta, theta, phi);
                  ba0_push_another_stack ();
                }

              rank_after = bap_rank_polynom_mpz (D.decision_system.tab[k]);
              if (!bav_equal_rank (&rank_before, &rank_after))
                BA0_RAISE_EXCEPTION (BAD_EXRCNC);

              bad_partially_reduced_polynom_quench_map (map, k);
            }
          else
            bad_is_an_already_satisfied_property_quench_map
                (&map->partially_autoreduced, k);
        }
/*
 * Starting from here, D.decision_system.tab[k] is partially reduced
 *                                  w.r.t. p_1, ..., p_{k-1}
 *
 * 3. normalized
 */
      exception_due_to_the_initial = false;

      if (bad_address_property_quench_map (&map->normalized, k))
        {
          bap_initial_polynom_mpz (&init, D.decision_system.tab[k]);
          if (bad_depends_on_leader_of_regchain (&init, &D))
            {
              BA0_TRY
              {
                bad_invert_polynom_mod_regchain (&U, &G, &init, &D, K,
                    (struct bap_polynom_mpz * *) &zerodiv);

                BA0_CANCEL_EXCEPTION;

                bap_replace_initial2_polynom_mpz (D.decision_system.tab[k], &U,
                    &G, D.decision_system.tab[k]);

                bad_normalized_polynom_quench_map (map, k);
              }
              BA0_CATCH
              {
                if (ba0_global.exception.raised == BAD_EXRNUL)
                  BA0_RAISE_EXCEPTION (BAD_EXRCNC);
                else if (ba0_global.exception.raised != BAD_EXRDDZ)
                  BA0_RE_RAISE_EXCEPTION;
/*
 * Variables U and G may have been modified by bad_invert_polynom_mod_regchain
 */
                bap_init_product_mpz (&U);
                bap_init_product_mpz (&G);

                exception_due_to_the_initial = true;
              }
              BA0_ENDTRY;
/*
 * If the rank has decreased then BAD_EXRCNC should have been raised
 */
              rank_after = bap_rank_polynom_mpz (D.decision_system.tab[k]);
              if (!bav_equal_rank (&rank_before, &rank_after))
                BA0_RAISE_EXCEPTION (BA0_ERRALG);
            }
          else
            {
              bad_is_an_already_satisfied_property_quench_map (&map->normalized,
                  k);
              bad_is_an_already_satisfied_property_quench_map (&map->regular,
                  k);
            }
        }
/*
 * 4. regular
 */
      if ((!exception_due_to_the_initial)
          && bad_address_property_quench_map (&map->regular, k))
        {
          bap_initial_polynom_mpz (&init, D.decision_system.tab[k]);
          if (bad_depends_on_leader_of_regchain (&init, &D))
            {
              BA0_TRY
              {
                bad_check_regularity_polynom_mod_regchain (&init, &D, K,
                    (struct bap_polynom_mpz * *) &zerodiv);

                bad_is_an_already_satisfied_property_quench_map (&map->regular,
                    k);
              }
              BA0_CATCH
              {
                if (ba0_global.exception.raised == BAD_EXRNUL)
                  BA0_RAISE_EXCEPTION (BAD_EXRCNC);
                else if (ba0_global.exception.raised != BAD_EXRDDZ)
                  BA0_RE_RAISE_EXCEPTION;

                exception_due_to_the_initial = true;
              }
              BA0_ENDTRY;
            }
          else
            bad_is_an_already_satisfied_property_quench_map (&map->regular, k);
        }
/*
 * 5. primitive
 */
      if (bad_address_property_quench_map (&map->primitive, k))
        {
          baz_primpart_polynom_mpz (D.decision_system.tab[k],
              D.decision_system.tab[k], BAV_NOT_A_VARIABLE);

          bad_primitive_polynom_quench_map (map, k);
        }
/*
 * 6. squarefree
 */
      exception_due_to_the_separant = false;

      if ((!exception_due_to_the_initial)
          && bad_address_property_quench_map (&map->squarefree, k))
        {
          if (rank_before.deg > 1)
            {
              bap_separant_polynom_mpz (&sep, D.decision_system.tab[k]);
              BA0_TRY
              {
                bad_check_regularity_polynom_mod_regchain (&sep, &D, K,
                    (struct bap_polynom_mpz * *) &zerodiv);

                bad_is_an_already_satisfied_property_quench_map
                    (&map->squarefree, k);
              }
              BA0_CATCH
              {
                if (ba0_global.exception.raised == BAD_EXRNUL)
                  BA0_RAISE_EXCEPTION (BA0_ERRALG);
                else if (ba0_global.exception.raised != BAD_EXRDDZ)
                  BA0_RE_RAISE_EXCEPTION;

                exception_due_to_the_separant = true;
              }
              BA0_ENDTRY;
            }
          else
            bad_is_an_already_satisfied_property_quench_map (&map->squarefree,
                k);
        }
/*
 * 7. cosmetic operation 
 */
      if ((!exception_due_to_the_initial) && (!exception_due_to_the_separant))
        {
          ba0_mpz_t *lc;

          lc = bap_numeric_initial_polynom_mpz (D.decision_system.tab[k]);
          if (ba0_mpz_sgn (*lc) < 0)
            bap_neg_polynom_mpz (D.decision_system.tab[k],
                D.decision_system.tab[k]);
        }
      else
        {
/*
 * 8. Exception handling
 */
          struct bav_variable *v;
          struct bap_polynom_mpz *zdiv = (struct bap_polynom_mpz *) zerodiv;
/*
 * Let k be now such that leader (zerodiv) = leader (D.decision_system.tab[k])
 */
          v = bap_leader_polynom_mpz (zdiv);
          while (!bad_is_leader_of_regchain (v, &D, (ba0_int_p *) & k))
            {
/*
 * The loop is useful: tests/rg17.c
 */
              bap_initial_polynom_mpz (zdiv, zdiv);
              if (bap_is_independent_polynom_mpz (zdiv))
                BA0_RAISE_EXCEPTION (BA0_ERRALG);
              v = bap_leader_polynom_mpz (zdiv);
            }
/*
 * In these cases, the exception is handled non-locally (see above).
 */
          if ((exception_due_to_the_initial
                  && v != bap_leader_polynom_mpz (&init))
              || (exception_due_to_the_separant
                  && v != bap_leader_polynom_mpz (&sep)))
            {
              if (ddz != (struct bap_polynom_mpz * *) 0)
                {
                  *ddz = zdiv;
                  BA0_RAISE_EXCEPTION2 (BAD_EXRDDZ, "%Az", (void **) ddz);
                }
              else
                BA0_RAISE_EXCEPTION (BAD_EXRDDZ);
            }
/*
 * else the exception is handled locally (do not split cases) and
 * one branch is discarded
 */
          if (discarded_branch)
            *discarded_branch = true;

          bap_pquo_polynom_mpz (D.decision_system.tab[k], (bav_Idegree *) 0,
              D.decision_system.tab[k], zdiv, v);

          bad_pseudo_divided_polynom_quench_map (map, k);
        }
      k = bad_first_index_quench_map (map);
    }
  ba0_pull_stack ();
  bad_set_regchain (Cbar, &D);
  ba0_restore (&M);

  bav_pull_ordering ();
}

/*
 * texinfo: bad_quench_and_handle_exceptions_regchain
 * Apply @code{bad_quench_regchain} to @var{C}, @var{map} and @var{K}, 
 * where @var{C} denotes the last element of @var{tabC}, and handle
 * the exceptions raised by this process. 
 *
 * The optional argument @var{ideal} is used to avoid splitting cases
 * in the case of the @code{bad_pardi} algorithm.
 *
 * The result is a possibly empty set of regular chains which are stored 
 * in @var{tabC} at indices greater than or equal to that of @var{C}.
 * Exceptions are handled as follows.
 * 
 * If the exception @code{BAD_EXRCNC} is raised then the current chain 
 * is discarded.
 * 
 * If the exception @code{BAD_EXRDDZ} is raised then a factorization 
 * @math{g\,h} of some @math{p_i \in C} is exhibited. 
 * The chain @var{C} is split by replacing @math{p_i} either 
 * by @math{g} or by @math{h} and the algorithm is recursively applied 
 * over each branch. 
 *
 * If @var{ideal} is nonzero and @var{g} (resp. @var{h}) does not lie
 * in the ideal that it defines, then the branch obtained by replacing
 * @math{p_i} by @math{g} (resp. @var{h}) is discarded. 
 * 
 * If nonzero, the argument @var{discarded_branch} is set to @code{true}
 * if at least one branch is discarded. Otherwise it is set to @code{false}.
 *
 * The @code{bad_coherent_property} is not handled by this function.
 */

BAD_DLL void
bad_quench_and_handle_exceptions_regchain (
    struct bad_intersectof_regchain *tabC,
    struct bad_quench_map *map,
    struct bav_tableof_term *theta,
    bool *discarded_branch,
    struct bad_regchain *ideal,
    struct bad_base_field *K)
{
  struct bad_regchain *C;
  struct bap_polynom_mpz *volatile g = BAP_NOT_A_POLYNOM_mpz;   /* to avoid a warning */
  struct bav_tableof_term *phi_quench, *phi_handle;
  volatile bool discarded_by_quench;
  volatile bool discarded_by_handle;

  if (ideal != (struct bad_regchain *) 0
      && !bad_defines_a_prime_ideal_regchain (ideal))
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  bav_push_ordering (tabC->attrib.ordering);
  C = tabC->inter.tab[tabC->inter.size - 1];

  if (theta)
    {
      phi_quench = (struct bav_tableof_term *) ba0_new_table ();
      phi_handle = (struct bav_tableof_term *) ba0_new_table ();
      bad_reset_theta (phi_quench, C);
      bad_reset_theta (phi_handle, C);
    }
  else
    {
      phi_quench = (struct bav_tableof_term *) 0;
      phi_handle = (struct bav_tableof_term *) 0;
    }

  discarded_by_quench = false;
  discarded_by_handle = false;

  BA0_TRY
  {
    bad_quench_regchain (C, map, phi_quench, (bool *) &discarded_by_quench, C,
        K, (struct bap_polynom_mpz * *) &g);
/*
   The above quenching operation has not raised any unhandled exception
 */
    bav_pull_ordering ();
  }
  BA0_CATCH
  {
    bav_pull_ordering ();
    bad_handle_splitting_exceptions_regchain (tabC, map, phi_handle,
        (bool *) &discarded_by_handle, (struct bap_polynom_mpz *) g, ideal,
        ba0_global.exception.raised, K);
  }
  BA0_ENDTRY;

  if (theta)
    bav_lcm_tableof_term (theta, phi_quench, phi_handle);

  if (discarded_branch)
    *discarded_branch = discarded_by_quench || discarded_by_handle;
}

/*
 * texinfo: bad_handle_splitting_exceptions_regchain
 * Denote @var{C} the last element of @var{tabC}.
 * While quenching @var{C} (see above) or performing a normal form computation 
 * modulo @var{C}, one of the exceptions @code{BAD_EXRCNC} and @code{BAD_EXRDDZ}
 * can be raised. This function handles such exceptions, which are given 
 * in @var{raised}.
 * 
 * If the exception is @code{BAD_EXRCNC}, the
 * regular chain @var{C} is just discarded from @var{tabC}. 
 * 
 * If the exception is @code{BAD_EXRDDZ} then @var{g} contains
 * a polynomial with the same leader as some @math{p_i \in C}
 * and an initial which is regular with respect to @var{C}.
 * This polynomial provides a factorization @math{g\,h} of @math{p_i \in C}.
 *
 * The chain @var{C} is then split by replacing @math{p_i} either 
 * by @math{g} or by @math{h}.
 * If @var{map} is zero, it is initialized assuming all properties of @var{C}
 * are satisfied. It is then updated according to the exception
 * and @code{bad_quench_and_handle_exceptions_regchain} is applied over 
 * each branch. 
 * 
 * If @var{ideal} is nonzero and @var{g} (resp. @var{h}) does not lie
 * in the ideal that it defines, then the branch obtained by replacing
 * @math{p_i} by @math{g} (resp. @var{h}) is discarded. 
 * 
 * Note: Exception @code{BAD_EXRNUL}, which looks pretty much like 
 * @code{BAD_EXRCNC} and may be raised while performing
 * an algebraic inverse computation, is not handled in this function
 * in order to allow a specific treatment by the calling function
 * (normal form computations).
 *
 * If nonzero, the argument @var{discarded_branch} is set to @code{true}
 * if at least one branch is discarded. Otherwise it is set to @code{false}.
 */

BAD_DLL void
bad_handle_splitting_exceptions_regchain (
    struct bad_intersectof_regchain *tabC,
    struct bad_quench_map *map,
    struct bav_tableof_term *theta,
    bool *discarded_branch,
    struct bap_polynom_mpz *g,
    struct bad_regchain *ideal,
    char *raised,
    struct bad_base_field *K)
{
  struct bad_regchain *C;
  struct bad_regchain *D = (struct bad_regchain *) 0;
  enum bad_typeof_reduction type_red;
  struct bap_polynom_mpz *h;
  struct bav_variable *v;
  ba0_int_p l;
  struct bav_tableof_term *phi_g, *phi_h;
  bool consider_g, consider_h;
  bool discarded_by_g, discarded_by_h;
  struct ba0_mark M;

  if (ideal != (struct bad_regchain *) 0
      && !bad_defines_a_prime_ideal_regchain (ideal))
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  bav_push_ordering (tabC->attrib.ordering);

  if (theta)
    {
      phi_g = (struct bav_tableof_term *) ba0_new_table ();
      phi_h = (struct bav_tableof_term *) ba0_new_table ();
    }
  else
    {
      phi_g = (struct bav_tableof_term *) 0;
      phi_h = (struct bav_tableof_term *) 0;
    }

  tabC->inter.size -= 1;
  C = tabC->inter.tab[tabC->inter.size];

  if (raised == BAD_EXRCNC)
    {
/*
 * The current branch leads to the unit ideal. 
 */
      bav_pull_ordering ();
      if (discarded_branch)
        *discarded_branch = true;
      return;
    }
  else if (raised != BAD_EXRDDZ)
    BA0_RAISE_EXCEPTION (raised);
/* 
 * A factorization C->decision_system [l] = g * h is exhibited. 
 * This factorization leads to a splitting (some branches may be 
 * discarded using the regular chain ideal) at index l. 
 * The quenching operation is restarted on all branches from index l.
 */
  v = bap_leader_polynom_mpz (g);
  if (!bad_is_leader_of_regchain (v, C, &l))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  type_red =
      bad_defines_a_differential_ideal_attchain (&tabC->attrib) ?
      bad_full_reduction : bad_algebraic_reduction;

  consider_g = ideal == (struct bad_regchain *) 0
      || bad_is_a_reduced_to_zero_polynom_by_regchain (g, ideal, type_red);
/*
 * consider_g = false => call from pardi which does not mind
 *  about discarded branches
 */
  ba0_push_another_stack ();
  ba0_record (&M);
  h = bap_new_polynom_mpz ();
  bap_pquo_polynom_mpz (h, (bav_Idegree *) 0, C->decision_system.tab[l], g, v);
  ba0_pull_stack ();

  consider_h = ideal == (struct bad_regchain *) 0
      || bad_is_a_reduced_to_zero_polynom_by_regchain (h, ideal, type_red);
/*
 * consider_h = false => call from pardi which does not mind
 *  about discarded branches
 */
  if (consider_h && !consider_g)
    {
      BA0_SWAP (struct bap_polynom_mpz *,
          g,
          h);
      BA0_SWAP (bool,
          consider_g,
          consider_h);
    }

  if (consider_h)
    D = (struct bad_regchain *) bad_copy_regchain (C);

  if (consider_g)
    {
      struct bad_quench_map map_g;

      bap_set_polynom_mpz (C->decision_system.tab[l], g);

      ba0_push_another_stack ();
      if (map != (struct bad_quench_map *) 0)
        bad_init_set_quench_map (&map_g, map);
      else
        {
          bad_init_quench_map (&map_g, C);
          bad_set_all_properties_quench_map (&map_g, true);
        }
      ba0_pull_stack ();

      bad_pseudo_divided_polynom_quench_map (&map_g, l);

      ba0_realloc_table ((struct ba0_table *) &tabC->inter,
          tabC->inter.size + 1);
      tabC->inter.size += 1;

      bad_quench_and_handle_exceptions_regchain (tabC, &map_g, phi_g,
          &discarded_by_g, ideal, K);
    }
  else
    discarded_by_g = true;      /* useless because call from pardi */

  if (consider_h)
    {
      struct bad_quench_map map_h;

      bap_set_polynom_mpz (D->decision_system.tab[l], h);

      ba0_realloc_table ((struct ba0_table *) &tabC->inter,
          tabC->inter.size + 1);
      tabC->inter.tab[tabC->inter.size] = D;
      tabC->inter.size += 1;

      ba0_push_another_stack ();
      if (map != (struct bad_quench_map *) 0)
        bad_init_set_quench_map (&map_h, map);
      else
        {
          bad_init_quench_map (&map_h, D);
          bad_set_all_properties_quench_map (&map_h, true);
        }
      ba0_pull_stack ();

      bad_pseudo_divided_polynom_quench_map (&map_h, l);

      bad_quench_and_handle_exceptions_regchain (tabC, &map_h, phi_h,
          &discarded_by_h, ideal, K);
    }
  else
    discarded_by_h = true;      /* useless because call from pardi */

  ba0_restore (&M);
  bav_pull_ordering ();

  if (theta)
    {
      bav_sort_tableof_term (phi_g);
      bav_sort_tableof_term (phi_h);
      bav_lcm_tableof_term (theta, phi_g, phi_h);
    }

  if (discarded_branch)
    *discarded_branch = discarded_by_g || discarded_by_h;
}
