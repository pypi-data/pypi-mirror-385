#include "bas_Zuple.h"
#include "bas_DL_tree.h"
#include "bas_Hurwitz.h"
#include "bas_positive_integer_roots.h"

/*
 * texinfo: bas_init_Zuple
 * Initialize @var{Z} to the empty Zuple.
 */

BAS_DLL void
bas_init_Zuple (
    struct bas_Zuple *Z)
{
  ba0_init_table ((struct ba0_table *) &Z->sigma);

  ba0_init_table ((struct ba0_table *) &Z->mu);

  ba0_init_table ((struct ba0_table *) &Z->zeta);

  bad_init_regchain (&Z->C);
  Z->P = (struct bap_listof_polynom_mpz *) 0;
  Z->S = (struct bap_listof_polynom_mpz *) 0;

  ba0_init_table ((struct ba0_table *) &Z->k);
  ba0_init_table ((struct ba0_table *) &Z->fn);
  ba0_init_table ((struct ba0_table *) &Z->der_fn);

  ba0_init_table ((struct ba0_table *) &Z->phi);
  ba0_init_table ((struct ba0_table *) &Z->deg);
  ba0_init_table ((struct ba0_table *) &Z->r);

  ba0_init_table ((struct ba0_table *) &Z->coeffs);
  ba0_init_table ((struct ba0_table *) &Z->A);
  ba0_init_table ((struct ba0_table *) &Z->roots);
  ba0_init_table ((struct ba0_table *) &Z->gamma);
  ba0_init_table ((struct ba0_table *) &Z->beta);
  ba0_init_table ((struct ba0_table *) &Z->delta);

  ba0_init_table ((struct ba0_table *) &Z->omega);

  Z->number = -1;
}

/*
 * texinfo: bas_new_Zuple
 * Allocate a new Zuple, initialize it and return it.
 */

BAS_DLL struct bas_Zuple *
bas_new_Zuple (
    void)
{
  struct bas_Zuple *Z;
  Z = (struct bas_Zuple *) ba0_alloc (sizeof (struct bas_Zuple));
  bas_init_Zuple (Z);
  return Z;
}

/*
 * texinfo: bas_set_number_Zuple
 * Set the @code{number} field of @var{Z} to @var{number}.
 */

BAS_DLL void
bas_set_number_Zuple (
    struct bas_Zuple *Z,
    ba0_int_p number)
{
  Z->number = number;
}

/*
 * Update the sigma field of U using the subscripted variables occurring in P
 */

static void
bas_update_sigma_variable (
    struct bas_Zuple *Z,
    struct bas_Yuple *U,
    struct bav_variable *v)
{
  ba0_int_p j, k;
  struct bav_symbol *y = v->root;

  if (bav_is_subscripted_symbol (y))
    {
      j = ba0_get_dictionary (&U->dict_R, (struct ba0_table *) &U->R,
          (void *) y->index_in_rigs);
      if (j != BA0_NOT_AN_INDEX)
        {
          k = bav_subscript_of_symbol (y);
          if (k > Z->sigma.tab[j])
            Z->sigma.tab[j] = k;
        }
    }
}

static void
bas_update_sigma_polynom_mpz (
    struct bas_Zuple *Z,
    struct bas_Yuple *U,
    struct bap_polynom_mpz *P)
{
  ba0_int_p i;

  for (i = 0; i < P->total_rank.size; i++)
    bas_update_sigma_variable (Z, U, P->total_rank.rg[i].var);
}

static void
bas_update_sigma_product_mpz (
    struct bas_Zuple *Z,
    struct bas_Yuple *U,
    struct bap_product_mpz *P)
{
  ba0_int_p i;

  for (i = 0; i < P->size; i++)
    if (P->tab[i].exponent > 0)
      bas_update_sigma_polynom_mpz (Z, U, &P->tab[i].factor);
}

static void
bas_add_to_P_Zuple (
    struct bas_Zuple *Z,
    struct bap_polynom_mpz *poly)
{
  Z->P =
      (struct bap_listof_polynom_mpz *)
      ba0_cons_list (bap_copy_polynom_mpz (poly), (struct ba0_list *) Z->P);
}

static void
bas_add_to_S_Zuple (
    struct bas_Zuple *Z,
    struct bap_polynom_mpz *poly)
{
  Z->S =
      (struct bap_listof_polynom_mpz *)
      ba0_cons_list (bap_copy_polynom_mpz (poly), (struct ba0_list *) Z->S);
}

/*
 * Store in the field @code{P} of @var{Z} all the prolongation 
 * equations to match all the subscripted variables up to the
 * subscripted prescribed by the @code{sigma} field of @var{Z}.
 */

static void
bas_prolongate_Zuple (
    struct bas_Zuple *Z,
    struct ba0_tableof_int_p *mu_max,
    struct bas_Yuple *U)
{
  struct bap_tableof_polynom_mpz *T;
  struct baz_ratfrac Q;
  struct bap_product_mpz prod;
  struct bap_polynom_mpz expanded_prod;
  struct ba0_mark M;
  ba0_int_p mu, n, o, r, beta, sigma, i;
  bool found, loop = true;

  ba0_push_another_stack ();
  ba0_record (&M);
  baz_init_ratfrac (&Q);
  bap_init_product_mpz (&prod);
  bap_init_polynom_mpz (&expanded_prod);
  ba0_pull_stack ();

  while (loop)
    {
      found = false;
      i = 0;
      while (i < U->Y.size && !found)
        {
          T = U->ode.tab[i];
          if (T->size > 0)
            {
/*
 * T->size > 0 means that there is a defining ODE for Y[i]
 */
              n = U->order.tab[i];
              o = U->ozs.tab[i];
              mu = Z->mu.tab[i];
              sigma = Z->sigma.tab[i];
              r = Z->r.tab[i];
              beta = Z->beta.tab[i];

              if (mu < sigma - o - n)
                {
/*
 * Minimal reason for a prolongation which can always be checked
 */
                  found = true;
                }
              else if (r != -1 && mu < sigma - o - n + r)
                {
/*
 * Whenever r is defined, this test replaces the above one.
 * It is more accurate because it takes into account the possible
 *  vanishing of leading coefficients. See [DL84, (6), page 216]
 */
                  found = true;
                }
              else if (beta != -1 && mu + 1 < beta)
                {
/*
 * Whenever beta is defined, this test must also be performed
 * Observe that this test and the former one are independent
 */
                  found = true;
                }
              if (found)
                {
                  if (mu + 1 == T->size)
                    {
                      ba0_realloc2_table ((struct ba0_table *) T, T->size + 1,
                          (ba0_new_function *) & bap_new_polynom_mpz);
                      bap_diff_polynom_mpz (T->tab[T->size],
                          T->tab[T->size - 1], U->x);
                      baz_prolongate_point_ratfrac_using_pattern_term
                          (&U->point, &U->point, &U->Ybar,
                          &T->tab[T->size]->total_rank);
                      T->size += 1;
                    }

                  mu += 1;
                  Z->mu.tab[i] = mu;

                  if (mu + 1 >= mu_max->tab[i])
                    mu_max->tab[i] = mu + 1;

                  ba0_push_another_stack ();

                  baz_eval_to_ratfrac_at_point_ratfrac_polynom_mpz (&Q,
                      T->tab[mu], &U->point);
                  if (!bap_is_numeric_polynom_mpz (&Q.denom))
                    BA0_RAISE_EXCEPTION (BA0_ERRALG);

                  bad_reduce_polynom_by_regchain (&prod,
                      (struct bap_product_mpz *) 0,
                      (struct bav_tableof_term *) 0,
                      &Q.numer, &Z->C,
                      bad_algebraic_reduction, bad_all_derivatives_to_reduce);

                  bap_expand_product_mpz (&expanded_prod, &prod);

                  ba0_pull_stack ();

                  bas_update_sigma_polynom_mpz (Z, U, &expanded_prod);
                  bas_add_to_P_Zuple (Z, &expanded_prod);
                }
              else
                i += 1;
            }
          else
            i += 1;
        }
      loop = found == true;
    }
  ba0_restore (&M);
}

/*
 * Remove from S all elements which reduce to some nonzero base field element
 */

static void
bas_clean_S_Zuple (
    struct bas_Zuple *Z,
    struct bad_base_field *K)
{
  struct bap_listof_polynom_mpz *S;
  struct bap_product_mpz prod;
  struct ba0_mark M;
  bool loop;

  ba0_record (&M);
  bap_init_product_mpz (&prod);

  S = Z->S;
  loop = true;
  while (loop)
    {
      if (S != (struct bap_listof_polynom_mpz *) 0)
        {
          bad_reduce_polynom_by_regchain (&prod, (struct bap_product_mpz *) 0,
              (struct bav_tableof_term *) 0, S->value, &Z->C,
              bad_algebraic_reduction, bad_all_derivatives_to_reduce);

          if (bap_is_zero_product_mpz (&prod))
            BA0_RAISE_EXCEPTION (BA0_ERRALG);

          if (bad_member_product_base_field (&prod, K))
            S = S->next;
          else
            loop = false;
        }
      else
        loop = false;
    }

  Z->S = S;

  if (S != (struct bap_listof_polynom_mpz *) 0)
    {
      while (S->next != (struct bap_listof_polynom_mpz *) 0)
        {
          struct bap_listof_polynom_mpz *T = S->next;

          bad_reduce_polynom_by_regchain (&prod, (struct bap_product_mpz *) 0,
              (struct bav_tableof_term *) 0, T->value, &Z->C,
              bad_algebraic_reduction, bad_all_derivatives_to_reduce);

          if (bap_is_zero_product_mpz (&prod))
            BA0_RAISE_EXCEPTION (BA0_ERRALG);

          if (bad_member_product_base_field (&prod, K))
            S->next = T->next;
          else
            S = S->next;
        }
    }

  ba0_restore (&M);
}

/*
 * Run the regular chain decomposition algorithm in order to
 * extend the field @code{C} of the top element of @var{tabZ}
 * with the elements of @code{P} and @code{S} plus the ones
 * of the field @code{S} of @var{U}.
 * The computation is performed over the base field @var{K}.
 * Eventually, the top element of @var{tabZ} is rewritten
 * by finitely many new Zuples whose fields @code{P} are empty.
 */

static void
bas_process_equations_and_inequations_Zuple (
    struct bas_tableof_Zuple *tabZ,
    struct bas_Yuple *U,
    struct bas_DL_tree *tree,
    struct bad_base_field *K)
{
  struct bas_Zuple *Z = tabZ->tab[tabZ->size - 1];
  struct bad_intersectof_regchain *ideal1;
  struct bad_splitting_tree *tree1;
  struct bad_splitting_control control;
  struct bap_tableof_polynom_mpz eqns, ineqs;
  struct ba0_tableof_string properties;
  struct ba0_mark M;
  ba0_int_p i;

  if (Z->P == (struct bap_listof_polynom_mpz *) 0 &&
      Z->S == (struct bap_listof_polynom_mpz *) 0)
    return;

  ba0_push_another_stack ();
  ba0_record (&M);
/*
 * Initialize ideal1 and set its properties using that of ideal
 */
  ideal1 = bad_new_intersectof_regchain ();
  ba0_init_table ((struct ba0_table *) &properties);
  bad_properties_regchain (&properties, &Z->C);
  bad_set_properties_intersectof_regchain (ideal1, &properties);
  bad_set_automatic_properties_intersectof_regchain (ideal1);
  bad_clear_property_intersectof_regchain (ideal1, bad_prime_ideal_property);
/*  
 * Initialize tree to an inactive splitting tree
 */
  tree1 = bad_new_splitting_tree ();
  bad_reset_splitting_tree (tree1, bad_inactive_splitting_tree);
/*
 * Disable dimension argument for cutting branches in the splitting tree
 */
  bad_init_splitting_control (&control);
//  bad_set_dimension_lower_bound_splitting_control (&control,
//      bad_no_dimension_lower_bound, false);
/*
 * Call RosenfeldGroebner
 */
  ba0_init_table ((struct ba0_table *) &eqns);
  ba0_init_table ((struct ba0_table *) &ineqs);
  ba0_realloc_table ((struct ba0_table *) &ineqs,
      ba0_length_list ((struct ba0_list *) U->S) +
      ba0_length_list ((struct ba0_list *) Z->S));
  ba0_set_table_list ((struct ba0_table *) &eqns, (struct ba0_list *) Z->P);
  ba0_set_table_list ((struct ba0_table *) &ineqs, (struct ba0_list *) Z->S);
  ba0_append_table_list ((struct ba0_table *) &ineqs, (struct ba0_list *) U->S);

  if (tree->activity == bas_verbose_DL_tree)
    {
      ba0_printf ("Apply RosenfeldGroebner over:\n");
      ba0_printf ("eqns = %t[%Az]\n", &eqns);
      ba0_printf ("ineqs = %t[%Az]\n", &ineqs);
    }

  bad_Rosenfeld_Groebner (ideal1, tree1, &eqns, &ineqs, K, &Z->C, &control);
/*
 * Generate a Zuple per component of ideal1, overriding Z
 */
  ba0_pull_stack ();

  if (ideal1->inter.size == 0)
    {
      ba0_int_p father = Z->number;

      bas_set_vertex_consistency_DL_tree (tree, father,
          bas_inconsistent_vertex);

      tabZ->size -= 1;

      if (tree->activity == bas_verbose_DL_tree)
        {
          ba0_printf ("inconsistency detected: Zuple discarded\n");
        }
    }
  else
    {
      ba0_int_p father = Z->number;

      ba0_realloc2_table ((struct ba0_table *) tabZ,
          tabZ->size - 1 + ideal1->inter.size,
          (ba0_new_function *) & bas_new_Zuple);

      if (ideal1->inter.size == 1)
        {
          bad_set_regchain (&Z->C, ideal1->inter.tab[0]);
          bas_clean_S_Zuple (Z, K);
          if (tree->activity == bas_verbose_DL_tree)
            {
              ba0_printf ("the regular chain is prolongated\n");
            }
        }
      else
        {
          ba0_int_p child = bas_next_number_DL_tree (tree);
          bad_set_regchain (&Z->C, ideal1->inter.tab[0]);
          bas_set_number_Zuple (Z, child);
          bas_add_edge_DL_tree (tree, bas_RG_edge, father, child);
          if (tree->activity == bas_verbose_DL_tree)
            {
              ba0_printf ("the regular chain leads to %d new chains\n",
                  ideal1->inter.size);
            }
        }
/*
 * P is set to zero and all k[i] to -1
 * However S is kept
 * This will be inherited by all the Zuple built in the loop below
 */
      Z->P = (struct bap_listof_polynom_mpz *) 0;

      for (i = 1; i < ideal1->inter.size; i++)
        {
          ba0_int_p child = bas_next_number_DL_tree (tree);
          bas_set_but_change_regchain_Zuple (tabZ->tab[tabZ->size],
              Z, ideal1->inter.tab[i]);
          bas_clean_S_Zuple (Z, K);
          bas_set_number_Zuple (tabZ->tab[tabZ->size], child);
          bas_add_edge_DL_tree (tree, bas_RG_edge, father, child);
          if (tree->activity == bas_verbose_DL_tree)
            {
              ba0_printf ("Zuple %d leads to Zuple %d\n", father, child);
            }
          tabZ->size += 1;
        }
    }

  ba0_restore (&M);
}

/*
 * texinfo: bas_set_Yuple_Zuple
 * Assign an initial value to the top element of @var{tabZ} 
 * using @var{U}, @var{eqns}, @var{C} and @var{K}. 
 * The parameter @var{C} contains the initial
 * regular differential chain to which the 
 * @code{bas_Denef_Lipshitz_leaf} function is applied.
 * The parameter @var{eqns} contains further equations
 * to be taken into account. It is allowed to be zero.
 * The field @code{sigma} is initialized using the subscripted
 * variables occurring in @var{C} (the @emph{ad hoc} equations),
 * the field @code{S} of @var{U} (the @emph{ad hoc} inequations),
 * @var{eqns} (further @emph{ad hoc} equations) and @var{vars}
 * (if nonzero).
 * The regular chain decomposition algorithm
 * is applied over the prolongation equations required by @code{sigma}. 
 * Eventually, the top element of @var{tabZ} is overwritten by finitely
 * many regular differential chains whose @code{P} fields are empty.
 */

BAS_DLL void
bas_set_Yuple_Zuple (
    struct bas_tableof_Zuple *tabZ,
    struct ba0_tableof_int_p *mu_max,
    struct bas_Yuple *U,
    struct bas_DL_tree *tree,
    struct bap_tableof_polynom_mpz *eqns,
    struct bad_regchain *C,
    struct bad_base_field *K,
    struct bav_tableof_variable *vars)
{
  struct bas_Zuple *Z = tabZ->tab[tabZ->size - 1];
  struct bap_listof_polynom_mpz *L;
  ba0_int_p i, n;

  n = U->Y.size;

  ba0_realloc_table ((struct ba0_table *) &Z->sigma, n);
  Z->sigma.size = n;

  ba0_realloc_table ((struct ba0_table *) &Z->mu, n);
  Z->mu.size = n;

  ba0_realloc_table ((struct ba0_table *) &Z->zeta, n);
  Z->zeta.size = n;

  ba0_realloc_table ((struct ba0_table *) &Z->k, n);
  Z->k.size = n;

  ba0_realloc2_table ((struct ba0_table *) &Z->fn, n,
      (ba0_new_function *) & ba0_new_table);
  Z->fn.size = n;

  ba0_realloc2_table ((struct ba0_table *) &Z->der_fn, n,
      (ba0_new_function *) & ba0_new_table);
  Z->der_fn.size = n;

  ba0_realloc_table ((struct ba0_table *) &Z->phi, n);
  Z->phi.size = n;

  ba0_realloc_table ((struct ba0_table *) &Z->deg, n);
  Z->deg.size = n;

  ba0_realloc_table ((struct ba0_table *) &Z->r, n);
  Z->r.size = n;

  ba0_realloc2_table ((struct ba0_table *) &Z->coeffs, n,
      (ba0_new_function *) & ba0_new_table);
  Z->coeffs.size = n;

  ba0_realloc2_table ((struct ba0_table *) &Z->A, n,
      (ba0_new_function *) & baz_new_ratfrac);
  Z->A.size = n;

  ba0_realloc2_table ((struct ba0_table *) &Z->roots, n,
      (ba0_new_function *) & ba0_new_table);
  Z->roots.size = n;

  ba0_realloc_table ((struct ba0_table *) &Z->gamma, n);
  Z->gamma.size = n;

  ba0_realloc_table ((struct ba0_table *) &Z->beta, n);
  Z->beta.size = n;

  ba0_realloc_table ((struct ba0_table *) &Z->delta, n);
  Z->delta.size = n;

  ba0_realloc_table ((struct ba0_table *) &Z->omega, n);
  Z->omega.size = n;

  for (i = 0; i < n; i++)
    {
      ba0_int_p j;

      Z->sigma.tab[i] = -1;
      Z->mu.tab[i] = -1;
      Z->zeta.tab[i] = -1;
      Z->k.tab[i] = -1;
      ba0_reset_table ((struct ba0_table *) Z->fn.tab[i]);
      ba0_reset_table ((struct ba0_table *) Z->der_fn.tab[i]);
      Z->phi.tab[i] = -1;
      Z->deg.tab[i] = -1;
      Z->r.tab[i] = -1;
      for (j = 0; j < n; j++)
        {
          ba0_reset_table ((struct ba0_table *) Z->coeffs.tab[j]);
          baz_set_ratfrac_zero (Z->A.tab[j]);
          ba0_reset_table ((struct ba0_table *) Z->roots.tab[j]);
        }
      Z->gamma.tab[i] = -1;
      Z->beta.tab[i] = -1;
      Z->delta.tab[i] = -1;
      Z->omega.tab[i] = false;
    }

  bad_set_regchain (&Z->C, C);
/*
 * No edge: this is a root
 */
  {
    ba0_int_p number = bas_next_number_DL_tree (tree);
    bas_set_number_Zuple (Z, number);
    bas_add_root_DL_tree (tree, number);
  }
/*
 * Update sigma with all the elements of C (not only the ODE)
 */
  for (i = 0; i < C->decision_system.size; i++)
    {
      struct bap_polynom_mpz *P = C->decision_system.tab[i];
      bas_update_sigma_polynom_mpz (Z, U, P);
    }
/*
 * Update sigma with all the elements of S
 */
  for (L = U->S; L != (struct bap_listof_polynom_mpz *) 0; L = L->next)
    bas_update_sigma_polynom_mpz (Z, U, L->value);
/*
 * Update sigma with all the elements of eqns
 * Store moreover the elements of eqns in the list of the equations to process
 */
  if (eqns != (struct bap_tableof_polynom_mpz *) 0)
    {
      for (i = 0; i < eqns->size; i++)
        {
          bas_update_sigma_polynom_mpz (Z, U, eqns->tab[i]);
          bas_add_to_P_Zuple (Z, eqns->tab[i]);
        }
    }
/*
 * Update sigma with the subscripted variables in vars
 */
  if (vars != (struct bav_tableof_variable *) 0)
    {
      for (i = 0; i < vars->size; i++)
        bas_update_sigma_variable (Z, U, vars->tab[i]);
    }

  if (tree->activity == bas_verbose_DL_tree)
    {
      ba0_printf ("root Zuple %d\n", Z->number);
    }

  bas_prolongate_Zuple (Z, mu_max, U);
  bas_process_equations_and_inequations_Zuple (tabZ, U, tree, K);
}

/*
 * texinfo: bas_set_but_change_regchain_Zuple
 * Assign @var{src} to @var{dst} except the @code{C} field of @var{dst}
 * which is set to @var{C}.
 */

BAS_DLL void
bas_set_but_change_regchain_Zuple (
    struct bas_Zuple *dst,
    struct bas_Zuple *src,
    struct bad_regchain *C)
{
  if (dst != src)
    {
      ba0_set_table ((struct ba0_table *) &dst->sigma,
          (struct ba0_table *) &src->sigma);

      ba0_set_table ((struct ba0_table *) &dst->mu,
          (struct ba0_table *) &src->mu);

      ba0_set_table ((struct ba0_table *) &dst->zeta,
          (struct ba0_table *) &src->zeta);

      bad_set_regchain (&dst->C, C);

      dst->P = (struct bap_listof_polynom_mpz *) ba0_copy ("%l[%Az]", src->P);
      dst->S = (struct bap_listof_polynom_mpz *) ba0_copy ("%l[%Az]", src->S);

      ba0_set_table ((struct ba0_table *) &dst->k,
          (struct ba0_table *) &src->k);

      bap_set_tableof_tableof_polynom_mpz (&dst->fn, &src->fn);

      bap_set_tableof_tableof_polynom_mpz (&dst->der_fn, &src->der_fn);

      ba0_set_table ((struct ba0_table *) &dst->phi,
          (struct ba0_table *) &src->phi);

      ba0_set_table ((struct ba0_table *) &dst->deg,
          (struct ba0_table *) &src->deg);

      ba0_set_table ((struct ba0_table *) &dst->r,
          (struct ba0_table *) &src->r);

      baz_set_tableof_tableof_ratfrac (&dst->coeffs, &src->coeffs);

      baz_set_tableof_ratfrac (&dst->A, &src->A);

      ba0_set_tableof_tableof_mpz (&dst->roots, &src->roots);

      ba0_set_table ((struct ba0_table *) &dst->gamma,
          (struct ba0_table *) &src->gamma);

      ba0_set_table ((struct ba0_table *) &dst->beta,
          (struct ba0_table *) &src->beta);

      ba0_set_table ((struct ba0_table *) &dst->delta,
          (struct ba0_table *) &src->delta);

      ba0_set_table ((struct ba0_table *) &dst->omega,
          (struct ba0_table *) &src->omega);

      dst->number = src->number;
    }
}

/*
 * texinfo: bas_set_Zuple
 * Assign @var{src} to @var{dst}.
 */

BAS_DLL void
bas_set_Zuple (
    struct bas_Zuple *dst,
    struct bas_Zuple *src)
{
  if (dst != src)
    bas_set_but_change_regchain_Zuple (dst, src, &src->C);
}

/*
 * readonly data
 */

static struct
{
  enum bas_typeof_action_on_Zuple type;
  char *ident;
} bas_cases[] = { {bas_nothing_to_do_Zuple, "not"},
{bas_discard_Zuple, "dis"},
{bas_k_to_secure_Zuple, "k"},
{bas_r_to_secure_Zuple, "r"},
{bas_beta_to_compute_Zuple, "beta"},
{bas_A_to_specialize_and_beta_to_recompute_Zuple, "bagn"}
};

/*
 * texinfo: bas_typeof_action_on_Zuple_to_string
 * Return a string encoding for @var{type}.
 * The encoding is given by the following table
 * @verbatim
 *
 * "not"  bas_nothing_to_do_Zuple
 * "dis"  bas_discard_Zuple
 * "k"    bas_k_to_secure_Zuple
 * "r"    bas_r_to_secure_Zuple
 * "beta" bas_beta_to_compute_Zuple
 * "bagn" bas_A_to_specialize_and_beta_to_recompute_Zuple
 * @end verbatim
 */

BAS_DLL char *
bas_typeof_action_on_Zuple_to_string (
    enum bas_typeof_action_on_Zuple type)
{
  bool found = false;
  ba0_int_p n = sizeof (bas_cases) / sizeof (bas_cases[0]);
  ba0_int_p i = 0;

  while (i < n && !found)
    {
      if (type == bas_cases[i].type)
        found = true;
      else
        i += 1;
    }
  if (!found)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  return bas_cases[i].ident;
}


/*
 * texinfo: bas_typeof_action_on_Zuple
 * Return the next action to apply on @var{Z}, using @var{U}.
 * Exception @code{BA0_ERRALG} is raised if the field @code{P}
 * of @var{Z} is nonempty.
 */

BAS_DLL enum bas_typeof_action_on_Zuple
bas_get_action_on_Zuple (
    struct bas_Zuple *Z,
    struct bas_Yuple *U)
{
  ba0_int_p i;
  bool found = false;
/*
 * bas_discard_Zuple if the valuation k of some separant is not yet
 *      secured while the bound kappa has been reached
 */
  i = 0;
  while (i < U->Y.size && !found)
    {
      if (U->ode.tab[i]->size > 0 &&
          (Z->zeta.tab[i] == U->kappa.tab[i] && Z->k.tab[i] == -1))
        found = true;
      else
        i += 1;
    }

  if (found)
    return bas_discard_Zuple;
/*
 * there should not be any missing prolongation equation
 */
  i = 0;
  while (i < U->Y.size && !found)
    {
      if (U->ode.tab[i]->size > 0 &&
          Z->mu.tab[i] + U->order.tab[i] < Z->sigma.tab[i] - U->ozs.tab[i])
        found = true;
      else
        i += 1;
    }

  if (found)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
/*
 * there should not be any equation waiting for being processed
 */
  if (Z->P != (struct bap_listof_polynom_mpz *) 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
/*
 * bas_k_to_secure_Zuple if some k is not secured
 */
  i = 0;
  while (i < U->Y.size && !found)
    {
      if (U->ode.tab[i]->size > 0 && Z->k.tab[i] == -1)
        found = true;
      else
        i += 1;
    }
  if (found)
    return bas_k_to_secure_Zuple;
/*
 * bas_r_to_secure_Zuple if some r is not secured
 */
  i = 0;
  while (i < U->Y.size && !found)
    {
      if (U->ode.tab[i]->size > 0 && Z->r.tab[i] == -1)
        found = true;
      else
        i += 1;
    }
  if (found)
    return bas_r_to_secure_Zuple;
/*
 * bas_beta_to_compute if r is secured
 */
  i = 0;
  while (i < U->Y.size && !found)
    {
      if (U->ode.tab[i]->size > 0 && Z->beta.tab[i] == -1)
        found = true;
      else
        i += 1;
    }
  if (found)
    return bas_beta_to_compute_Zuple;
/*
 * bas_A_to_specialize_and_beta_to_recompute if not done
 */
  i = 0;
  while (i < U->Y.size && !found)
    {
      if (U->ode.tab[i]->size > 0 && Z->omega.tab[i] == false)
        found = true;
      else
        i += 1;
    }
  if (found)
    return bas_A_to_specialize_and_beta_to_recompute_Zuple;
/*
 * Eventually, we are done
 */
  return bas_nothing_to_do_Zuple;
}


/*
 * texinfo: bas_secure_k_Zuple
 * Rewrite the top element of @var{tabZ} with finitely many 
 * Zuples for which either @math{k} is defined or @code{zeta}
 * has increased.
 * The process involves new prolongation equations and 
 * a regular chain decomposition over @var{K}.
 * Exception @code{BA0_ERRALG} is raised if the field @math{k} of 
 * the top element of @var{tabZ} is defined for each differential 
 * indeterminate.
 */

BAS_DLL void
bas_secure_k_Zuple (
    struct bas_tableof_Zuple *tabZ,
    struct ba0_tableof_int_p *mu_max,
    struct bas_Yuple *U,
    struct bas_DL_tree *tree,
    struct bad_base_field *K)
{
  struct bas_Zuple *Z = tabZ->tab[tabZ->size - 1];
  struct bap_tableof_polynom_mpz *T;
  struct baz_ratfrac Q;
  struct bap_product_mpz prod;
  struct bap_polynom_mpz expanded_prod;
  struct ba0_mark M;
  ba0_int_p i, zeta, z, old_z;

  i = 0;
  while (i < U->Y.size && (U->ode.tab[i]->size == 0 || Z->k.tab[i] != -1))
    i += 1;
  if (i == U->Y.size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
/*
 * i = the index of the differential indeterminate y
 */
  bas_set_aykrd_vertex_DL_tree (tree, Z->number, bas_k_to_secure_Zuple,
      U->Y.tab[i], BAS_NOT_A_NUMBER, BAS_NOT_A_NUMBER, BAS_NOT_A_NUMBER);

  ba0_push_another_stack ();
  ba0_record (&M);
  baz_init_ratfrac (&Q);
  bap_init_product_mpz (&prod);
  bap_init_polynom_mpz (&expanded_prod);
  ba0_pull_stack ();

  T = U->sep.tab[i];

  if (Z->zeta.tab[i] + 1 == T->size)
    {
      ba0_realloc2_table ((struct ba0_table *) T, T->size + 1,
          (ba0_new_function *) & bap_new_polynom_mpz);
      bap_diff_polynom_mpz (T->tab[T->size], T->tab[T->size - 1], U->x);
      baz_prolongate_point_ratfrac_using_pattern_term (&U->point,
          &U->point, &U->Ybar, &T->tab[T->size]->total_rank);
      T->size += 1;
    }
  Z->zeta.tab[i] += 1;

  zeta = Z->zeta.tab[i];

  if (tree->activity == bas_verbose_DL_tree)
    {
      ba0_printf ("secure k applied to Zuple %d, indeterminate %d = %y\n",
          Z->number, i, U->Y.tab[i]);
      ba0_printf ("try k = %d\n", zeta);
    }
/*
 * We want to reduce the order zeta prolongation polynomial of the separant
 *  by the regular chain.
 * In order to do this, we need to prolongate the chain.
 * In order not to prolongate too much, we perform a first reduction
 */
  ba0_push_another_stack ();

  if (U->kappa.tab[i] == BA0_MAX_INT_P &&
      bad_is_a_reduced_to_zero_polynom_by_regchain (T->tab[zeta], &Z->C,
          bad_full_reduction))
    {
      U->kappa.tab[i] = zeta;
      if (tree->activity == bas_verbose_DL_tree)
        ba0_printf
            ("the separant vanishes identically and kappa is infinite: set kappa to: %d\n",
            zeta);
    }

  baz_eval_to_ratfrac_at_point_ratfrac_polynom_mpz (&Q, T->tab[zeta],
      &U->point);
  if (!bap_is_numeric_polynom_mpz (&Q.denom))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  bad_reduce_polynom_by_regchain (&prod, (struct bap_product_mpz *) 0,
      (struct bav_tableof_term *) 0, &Q.numer, &Z->C,
      bad_algebraic_reduction, bad_all_derivatives_to_reduce);

  ba0_pull_stack ();

  bas_update_sigma_product_mpz (Z, U, &prod);
  bas_prolongate_Zuple (Z, mu_max, U);
  old_z = tabZ->size - 1;
  bas_process_equations_and_inequations_Zuple (tabZ, U, tree, K);

  z = tabZ->size - 1;
  while (z >= old_z)
    {
      ba0_int_p father;

      Z = tabZ->tab[z];
      father = Z->number;
/*
 * Here, we reduce the order zeta prolongation polynomial of the separant
 *  by one of the prolongated regular chains.
 */
      ba0_push_another_stack ();
      bad_reduce_polynom_by_regchain (&prod, (struct bap_product_mpz *) 0,
          (struct bav_tableof_term *) 0, &Q.numer, &Z->C,
          bad_algebraic_reduction, bad_all_derivatives_to_reduce);
      bad_remove_product_factors_base_field (&prod, &prod, K);
      bap_expand_product_mpz (&expanded_prod, &prod);
      ba0_pull_stack ();

      if (bad_member_product_base_field (&prod, K))
        {
          if (!bap_is_zero_product_mpz (&prod))
            {
              Z->k.tab[i] = Z->zeta.tab[i];
              Z->r.tab[i] = -1;
              Z->phi.tab[i] = -1;
              Z->deg.tab[i] = -1;
              if (tree->activity == bas_verbose_DL_tree)
                {
                  ba0_printf ("Zuple %d: k is found for %y and equal to %d\n",
                      Z->number, U->Y.tab[i], Z->k.tab[i]);
                }
            }
        }
      else
        {
          ba0_int_p j;

          if (Z->zeta.tab[i] < U->kappa.tab[i])
            {
              ba0_int_p child = bas_next_number_DL_tree (tree);

              ba0_realloc2_table ((struct ba0_table *) tabZ, tabZ->size + 1,
                  (ba0_new_function *) & bas_new_Zuple);

              bas_set_Zuple (tabZ->tab[tabZ->size], Z);
              bas_add_to_P_Zuple (tabZ->tab[tabZ->size], &expanded_prod);
              bas_set_number_Zuple (tabZ->tab[tabZ->size], child);
              bas_add_edge_DL_tree (tree, bas_vanishing_edge, father, child);
              tabZ->size += 1;

              if (tree->activity == bas_verbose_DL_tree)
                {
                  ba0_printf
                      ("Zuple %d to %d: consider the possible vanishing of %Az\n",
                      father, child, &expanded_prod);
                }
/*
 * One new equation to be processed: 
 *      the case of the prolongation polynomial of the separant being zero
 * All needed prolongations have been done already
 */
              bas_process_equations_and_inequations_Zuple (tabZ, U, tree, K);
            }
          else
            {
              if (tree->activity == bas_verbose_DL_tree)
                {
                  ba0_printf ("Zuple %d: bound kappa = %d is reached for %y\n",
                      Z->number, U->kappa.tab[i], U->Y.tab[i]);
                }
            }

          for (j = 0; j < prod.size; j++)
            bas_add_to_S_Zuple (Z, &prod.tab[j].factor);

          if (Z->zeta.tab[i] < U->kappa.tab[i])
            {
              ba0_int_p child = bas_next_number_DL_tree (tree);
              bas_set_number_Zuple (Z, child);
              bas_add_edge_DL_tree (tree, bas_non_vanishing_edge, father,
                  child);
            }

          Z->k.tab[i] = Z->zeta.tab[i];
          Z->r.tab[i] = -1;
          Z->phi.tab[i] = -1;
          Z->deg.tab[i] = -1;
          if (z != tabZ->size - 1)
            BA0_SWAP (struct bas_Zuple *,
                tabZ->tab[z],
                tabZ->tab[tabZ->size - 1]);

          if (tree->activity == bas_verbose_DL_tree)
            {
              ba0_printf ("Zuple %d to %d: consider the nonvanishing of %Az\n",
                  father, Z->number, &expanded_prod);
            }
/*
 * One new inequation to be processed: 
 *      the case of the prolongation polynomial of the separant being nonzero
 * All needed prolongations have been done already
 */
          bas_process_equations_and_inequations_Zuple (tabZ, U, tree, K);
        }
      z -= 1;
    }
  ba0_restore (&M);
}

/*
 * texinfo: bas_secure_r_Zuple
 * Rewrite the top element of @var{tabZ} with finitely many 
 * Zuples for which either @math{r} and @code{deg} are defined 
 * or @code{phi} has increased.
 * The field @code{fn} is computed.
 * The computation of the field @code{der_fn} is initiated.
 * The process involves new prolongation equations and 
 * a regular chain decomposition over @var{K}.
 * Exception @code{BA0_ERRALG} is raised if the field @math{r} of 
 * the top element of @var{tabZ} is defined for each differential 
 * indeterminate.
 */

BAS_DLL void
bas_secure_r_Zuple (
    struct bas_tableof_Zuple *tabZ,
    struct ba0_tableof_int_p *mu_max,
    struct bas_Yuple *U,
    struct bas_DL_tree *tree,
    struct bad_base_field *K)
{
  struct bas_Zuple *Z = tabZ->tab[tabZ->size - 1];
  struct baz_ratfrac Q;
  struct bap_product_mpz prod;
  struct bap_polynom_mpz expanded_prod;
  struct bap_tableof_polynom_mpz *fn, *der_fn;
  struct ba0_mark M;
  ba0_int_p i, k, deg, z, old_z;
  ba0_int_p father;

  ba0_push_another_stack ();
  ba0_record (&M);
  baz_init_ratfrac (&Q);
  bap_init_product_mpz (&prod);
  bap_init_polynom_mpz (&expanded_prod);
  ba0_pull_stack ();
/*
 * Look for some index i for which r needs be secured
 */
  i = 0;
  while (i < U->Y.size && (U->ode.tab[i]->size == 0 || Z->r.tab[i] != -1))
    i += 1;
  if (i == U->Y.size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
/*
 * k = the valuation of the separant - is a required secured data
 */
  k = Z->k.tab[i];

  fn = Z->fn.tab[i];
  der_fn = Z->der_fn.tab[i];

  bas_set_aykrd_vertex_DL_tree (tree, Z->number, bas_r_to_secure_Zuple,
      U->Y.tab[i], k, BAS_NOT_A_NUMBER, BAS_NOT_A_NUMBER);
/*
 * (phi, deg) = the coordinates of the last processed coefficient
 *            = (-1,-1) if first time
 */
  if (Z->phi.tab[i] == -1)
    {
      struct bap_tableof_polynom_mpz *T = U->ode.tab[i];
      ba0_int_p two_k_plus_two = 2 * k + 2;
/*
 * first time here ? 
 * prolongate the ode table up to 2*k + 2 - we will need them
 */
      ba0_realloc2_table ((struct ba0_table *) T, two_k_plus_two + 1,
          (ba0_new_function *) & bap_new_polynom_mpz);
      while (T->size <= two_k_plus_two)
        {
          bap_diff_polynom_mpz (T->tab[T->size], T->tab[T->size - 1], U->x);
          baz_prolongate_point_ratfrac_using_pattern_term (&U->point,
              &U->point, &U->Ybar, &T->tab[T->size]->total_rank);
          T->size += 1;
        }
/*
 * compute fn and initialize der_fn
 * fn = [f_n, f_{n+1}, f_{n+2}, ..., f_{n+k}] (notations of [DL84])
 */
      bas_Hurwitz_coeffs (fn, T->tab[0], T->tab[two_k_plus_two], k, U->x);
      ba0_realloc2_table ((struct ba0_table *) der_fn, k + 1,
          (ba0_new_function *) & bap_new_polynom_mpz);

      bap_set_polynom_mpz (der_fn->tab[0], fn->tab[0]);
      der_fn->size = 1;
    }
  else
    Z->deg.tab[i] -= 1;
/*
 * Loop at most once
 */
  while (Z->deg.tab[i] == -1)
    {
      Z->phi.tab[i] += 1;
      if (Z->phi.tab[i] == k)
        Z->deg.tab[i] = Z->phi.tab[i];
      else
        Z->deg.tab[i] = Z->phi.tab[i] - 1;
    }
/*
 * next value of der_fn
 * [f_n]
 * [f_{n+1}, f_n']
 * [f_{n+2}, f_{n+1}', f_n'']
 */
  while (Z->phi.tab[i] > der_fn->size - 1)
    {
      ba0_int_p j;
      for (j = der_fn->size; j > 0; j--)
        {
          bap_diff_polynom_mpz (der_fn->tab[j], der_fn->tab[j - 1], U->x);
          baz_prolongate_point_ratfrac_using_pattern_term (&U->point,
              &U->point, &U->Ybar, &der_fn->tab[j]->total_rank);
        }
      bap_set_polynom_mpz (der_fn->tab[0], fn->tab[der_fn->size]);
      der_fn->size += 1;
    }
/*
 * (phi,deg) = the coordinates of the coefficient to process
 *           = (1,0) if first time
 */
  father = Z->number;

  if (Z->phi.tab[i] == k)
    {
/*
 * If we start row k then r = k and deg = k - the most common case
 */
      Z->r.tab[i] = Z->phi.tab[i];
      Z->beta.tab[i] = -1;

      if (tree->activity == bas_verbose_DL_tree)
        {
          ba0_printf ("secure r applied to Zuple %d, indeterminate %d = %y\n",
              Z->number, i, U->Y.tab[i]);
          ba0_printf ("value r = k = %d reached\n", Z->phi.tab[i]);
        }
    }
  else
    {
/*
 * The index deg goes downward so that the coefficients of the polynomial A(q)
 * are considered by decreasing degree - hence if r gets secured then
 * deg contains the degree of A(q)
 */
      deg = Z->deg.tab[i];

      if (tree->activity == bas_verbose_DL_tree)
        {
          ba0_printf ("secure r applied to Zuple %d, indeterminate %d = %y\n",
              Z->number, i, U->Y.tab[i]);
          ba0_printf ("try (r,d) = (%d,%d)\n", Z->phi.tab[i], Z->deg.tab[i]);
        }
/*
 * We want to reduce the order zero prolongation polynomial of der_fn[deg]
 *  by the regular chain.
 * In order to do this, we need to prolongate the chain.
 * In order not to prolongate too much, we perform a first reduction
 */
      ba0_push_another_stack ();

      baz_eval_to_ratfrac_at_point_ratfrac_polynom_mpz (&Q,
          der_fn->tab[deg], &U->point);

      if (!bap_is_numeric_polynom_mpz (&Q.denom))
        BA0_RAISE_EXCEPTION (BA0_ERRALG);

      bad_reduce_polynom_by_regchain (&prod, (struct bap_product_mpz *) 0,
          (struct bav_tableof_term *) 0, &Q.numer, &Z->C,
          bad_algebraic_reduction, bad_all_derivatives_to_reduce);

      ba0_pull_stack ();

      bas_update_sigma_product_mpz (Z, U, &prod);
      bas_prolongate_Zuple (Z, mu_max, U);

      old_z = tabZ->size - 1;
      bas_process_equations_and_inequations_Zuple (tabZ, U, tree, K);

      z = tabZ->size - 1;
      while (z >= old_z)
        {
          Z = tabZ->tab[z];
          father = Z->number;
/*
 * Here, we reduce the order zero prolongation polynomial of der_fn[deg]
 *  by one of the prolongated regular chains.
 */
          ba0_push_another_stack ();
          bad_reduce_polynom_by_regchain (&prod,
              (struct bap_product_mpz *) 0,
              (struct bav_tableof_term *) 0, &Q.numer, &Z->C,
              bad_algebraic_reduction, bad_all_derivatives_to_reduce);

          bad_remove_product_factors_base_field (&prod, &prod, K);
          bap_expand_product_mpz (&expanded_prod, &prod);
          ba0_pull_stack ();

          if (bap_is_numeric_product_mpz (&prod))
            {
              if (!bap_is_zero_product_mpz (&prod))
                {
                  Z->r.tab[i] = Z->phi.tab[i];
                  Z->beta.tab[i] = -1;
                }
            }
          else
            {
              ba0_int_p j;
              ba0_int_p child = bas_next_number_DL_tree (tree);

              ba0_realloc2_table ((struct ba0_table *) tabZ,
                  tabZ->size + 1, (ba0_new_function *) & bas_new_Zuple);
              bas_set_Zuple (tabZ->tab[tabZ->size], Z);
              bas_add_to_P_Zuple (tabZ->tab[tabZ->size], &expanded_prod);
              bas_set_number_Zuple (tabZ->tab[tabZ->size], child);
              bas_add_edge_DL_tree (tree, bas_vanishing_edge, father, child);
              tabZ->size += 1;
/*
 * One new equation to be processed: 
 *  the case of the order zero prolongation polynomial of der_fn[deg] being zero
 * All needed prolongations have been done already
 */
              bas_process_equations_and_inequations_Zuple (tabZ, U, tree, K);

              for (j = 0; j < prod.size; j++)
                bas_add_to_S_Zuple (Z, &prod.tab[j].factor);
              child = bas_next_number_DL_tree (tree);
              bas_set_number_Zuple (Z, child);
              bas_add_edge_DL_tree (tree, bas_non_vanishing_edge, father,
                  child);
              if (z != tabZ->size - 1)
                BA0_SWAP (struct bas_Zuple *,
                    tabZ->tab[z],
                    tabZ->tab[tabZ->size - 1]);
/*
 * One new inequation to be processed: 
 *  the case of the order zero prolongation polynomial of der_fn[deg] nonzero
 * All needed prolongations have been done already
 */
              bas_process_equations_and_inequations_Zuple (tabZ, U, tree, K);
            }
          z -= 1;
        }
    }
}

/*
 * Compute the fields @code{A}, @code{roots}, @code{gamma}, 
 * @code{beta} and @code{delta} from the fields @code{coeffs}
 * and @code{deg}.
 */

static void
bas_coeffs_to_A_Zuple (
    struct bas_Zuple *Z,
    struct bas_Yuple *U,
    ba0_int_p i)
{
  struct baz_tableof_ratfrac *coeffs;
  struct bap_tableof_polynom_mpz *der_fn;
  ba0_int_p j, deg;

  deg = Z->deg.tab[i];
  coeffs = Z->coeffs.tab[i];
  der_fn = Z->der_fn.tab[i];
/*
 * compute the polynomial A(q) = Z->A.tab[i]
 */
  for (j = deg; j >= 0; j--)
    {
/*
 * The normal form of a polynomial should not raise any exception
 * This should however be checked with the current implementation
 *
 * We modify coeffs. Later we clear denominators.
 * Thus we should restart from der_fn. 
 * Optimize me: the recomputation of coeffs->tab[j] could be saved.
 */
      baz_eval_to_ratfrac_at_point_ratfrac_polynom_mpz (coeffs->tab[j],
          der_fn->tab[j], &U->point);
      bad_normal_form_ratfrac_mod_regchain (coeffs->tab[j],
          coeffs->tab[j], &Z->C, (struct bap_polynom_mpz **) 0);

      if (j == deg)
        {
          baz_mul_ratfrac_polynom_mpq (Z->A.tab[i], coeffs->tab[j],
              U->binomials.tab[j]);
        }
      else
        {
          baz_mul_ratfrac_polynom_mpq (coeffs->tab[j], coeffs->tab[j],
              U->binomials.tab[j]);
          baz_add_ratfrac (Z->A.tab[i], Z->A.tab[i], coeffs->tab[j]);
        }
    }
/*
 * Remove content. Why keeping rational fractions, then?
 */
  {
    struct bap_polynom_mpz poly;
    struct ba0_mark M;

    ba0_push_another_stack ();
    ba0_record (&M);
    bap_init_polynom_mpz (&poly);
    baz_primpart_polynom_mpz (&poly, &Z->A.tab[i]->numer, U->q);
    bap_normal_numeric_primpart_polynom_mpz (&poly, &poly);
    ba0_pull_stack ();
    baz_set_ratfrac_polynom_mpz (Z->A.tab[i], &poly);
    ba0_restore (&M);
  }
/*
 * compute the nonnegative integer roots of A(q) = Z->A.tab[i]
 */
  bas_nonnegative_integer_roots (Z->roots.tab[i], &Z->A.tab[i]->numer, U->q,
      &Z->C);
/*
 * then compute gamma, beta and delta
 */
  if (Z->roots.tab[i]->size == 0)
    Z->gamma.tab[i] = 0;
  else
    {
      struct ba0_tableof_mpz *T = Z->roots.tab[i];
      Z->gamma.tab[i] = ba0_mpz_get_si (T->tab[T->size - 1]) + 1;
    }

  Z->beta.tab[i] = 2 * Z->k.tab[i] + 2 + Z->gamma.tab[i] + Z->r.tab[i];
  Z->delta.tab[i] = Z->beta.tab[i] + U->order.tab[i] - Z->r.tab[i];
}

/*
 * texinfo: bas_compute_beta_Zuple
 * Rewrite the top element of @var{tabZ} with finitely many 
 * Zuples for which either a first value for @math{beta} is computed.
 * The process involves new prolongation equations and 
 * a regular chain decomposition over @var{K}.
 * The field @code{omega} of all new Zuples is set to @code{false}.
 * Exception @code{BA0_ERRALG} is raised if the field @math{beta} of 
 * the top element of @var{tabZ} is defined for each differential 
 * indeterminate.
 */

BAS_DLL void
bas_compute_beta_Zuple (
    struct bas_tableof_Zuple *tabZ,
    struct ba0_tableof_int_p *mu_max,
    struct bas_Yuple *U,
    struct bas_DL_tree *tree,
    struct bad_base_field *K)
{
  struct bas_Zuple *Z = tabZ->tab[tabZ->size - 1];
  struct baz_tableof_ratfrac *coeffs;
  struct bap_tableof_polynom_mpz *der_fn;
  struct bap_product_mpz prod;
  struct ba0_mark M;
  ba0_int_p deg, i, j, k, z, old_z;
/*
 * Look for some index i for which beta needs be computed
 */
  i = 0;
  while (i < U->Y.size && (U->ode.tab[i]->size == 0 ||
          Z->r.tab[i] == -1 || Z->beta.tab[i] != -1))
    i += 1;
  if (i == U->Y.size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);
  bap_init_product_mpz (&prod);
  ba0_pull_stack ();
/*
 * Used only for setting breakpoint in gdb
 */
  k = Z->k.tab[i];

  der_fn = Z->der_fn.tab[i];
  deg = Z->deg.tab[i];
  coeffs = Z->coeffs.tab[i];

  if (der_fn->size - 1 != Z->r.tab[i])
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  bas_set_aykrd_vertex_DL_tree (tree, Z->number, bas_beta_to_compute_Zuple,
      U->Y.tab[i], k, Z->r.tab[i], deg);

  bas_prolongate_binomials_Yuple (U, deg);

  ba0_realloc2_table ((struct ba0_table *) coeffs, deg + 1,
      (ba0_new_function *) & baz_new_ratfrac);
/*
 * The coefficients of the polynomial A(q) may contain subscripted
 *  variables requiring some prolongation.
 *
 * We consider them one by one, reduce them by the regular chain
 *  (to avoid pointless prolongations) and prolongate
 */
  for (j = deg; j >= 0; j--)
    {
      baz_eval_to_ratfrac_at_point_ratfrac_polynom_mpz (coeffs->tab[j],
          der_fn->tab[j], &U->point);

      if (!bap_is_numeric_polynom_mpz (&coeffs->tab[j]->denom))
        BA0_RAISE_EXCEPTION (BA0_ERRALG);

      ba0_push_another_stack ();

      bad_reduce_polynom_by_regchain (&prod, (struct bap_product_mpz *) 0,
          (struct bav_tableof_term *) 0, &coeffs->tab[j]->numer, &Z->C,
          bad_algebraic_reduction, bad_all_derivatives_to_reduce);

      ba0_pull_stack ();

      bas_update_sigma_product_mpz (Z, U, &prod);
      bas_prolongate_Zuple (Z, mu_max, U);
    }
  coeffs->size = deg + 1;
/*
 * Simplification of the generated prolongation equations
 */
  old_z = tabZ->size - 1;
  bas_process_equations_and_inequations_Zuple (tabZ, U, tree, K);
  z = tabZ->size - 1;
  while (z >= old_z)
    {
      Z = tabZ->tab[z];
/*
 * Actual computation of beta
 */
      bas_coeffs_to_A_Zuple (Z, U, i);
/*
 * The new value of beta may require some further prolongation
 * It does not require to update sigma, though
 */
      bas_prolongate_Zuple (Z, mu_max, U);

      if (z != tabZ->size - 1)
        BA0_SWAP (struct bas_Zuple *,
            tabZ->tab[z],
            tabZ->tab[tabZ->size - 1]);

      bas_process_equations_and_inequations_Zuple (tabZ, U, tree, K);

      z -= 1;
    }
/*
 * For all newly generated Zuple, omega is set to false
 */
  for (z = old_z; z < tabZ->size; z++)
    {
      Z = tabZ->tab[z];
      Z->omega.tab[i] = false;
    }

  ba0_restore (&M);
}

/*
 * texinfo: bas_specialize_A_and_recompute_beta_Zuple
 * Rewrite the top element of @var{tabZ} with finitely many Zuples
 * for which either the field @code{omega} is @code{true} or
 * at least one coefficient of @code{coeffs} has been further reduced
 * by @code{C}. 
 * The process involves new prolongation equations and
 * a regular chain decomposition over @var{K}.
 * Exception @code{BA0_ERRALG} is raised if the field @code{omega} of
 * the top element of @var{tabZ} is @code{true} for each differential
 * indeterminate.
 */

BAS_DLL void
bas_specialize_A_and_recompute_beta_Zuple (
    struct bas_tableof_Zuple *tabZ,
    struct ba0_tableof_int_p *mu_max,
    struct bas_Yuple *U,
    struct bas_DL_tree *tree,
    struct bad_base_field *K)
{
  struct bas_Zuple *Z = tabZ->tab[tabZ->size - 1];
  struct baz_tableof_ratfrac *coeffs;
  ba0_int_p i, j, deg;
  bool reducible;
/*
 * Look for some index i for which beta possibly needs be recomputed
 */
  i = 0;
  while (i < U->Y.size && (U->ode.tab[i]->size == 0 ||
          Z->beta.tab[i] == -1 || Z->omega.tab[i] == true))
    i += 1;
  if (i == U->Y.size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  coeffs = Z->coeffs.tab[i];
  deg = Z->deg.tab[i];

  bas_set_aykrd_vertex_DL_tree (tree, Z->number,
      bas_A_to_specialize_and_beta_to_recompute_Zuple, U->Y.tab[i], Z->k.tab[i],
      Z->r.tab[i], Z->deg.tab[i]);
/*
 * Is there any coefficient of A(q) which has become reducible?
 */
  reducible = false;
  for (j = 0; j <= deg && !reducible; j++)
    {
      if (bad_is_a_reducible_polynom_by_regchain (&coeffs->tab[j]->numer, &Z->C,
              bad_algebraic_reduction, bad_all_derivatives_to_reduce,
              (struct bav_rank *) 0, (ba0_int_p *) 0))
        reducible = true;
    }

  if (!reducible)
    {
/*
 * No: we are done
 */
      Z->omega.tab[i] = true;
    }
  else
    {
      ba0_int_p z, old_z;
/*
 * Yes: we recompute A(q) and beta
 * The new value of beta may require further prolongations
 */
      bas_coeffs_to_A_Zuple (Z, U, i);

      bas_prolongate_Zuple (Z, mu_max, U);

      old_z = tabZ->size - 1;
      bas_process_equations_and_inequations_Zuple (tabZ, U, tree, K);
/*
 * For all newly generated Zuple, set omega to false
 */
      for (z = old_z; z < tabZ->size; z++)
        { ba0_int_p j;

          Z = tabZ->tab[z];
          for (j = 0; j < U->Y.size; j++)
            Z->omega.tab[j] = false;
        }
    }
}

/*
 * texinfo: bas_printf_Zuple
 * The general printing function for Zuples.
 * It can be called through @code{ba0_printf/%Zuple}.
 */

BAS_DLL void
bas_printf_Zuple (
    void *Z0)
{
  struct bas_Zuple *Z = (struct bas_Zuple *) Z0;
  ba0_printf
      ("number = %d\n"
      "sigma  = %t[%d]\n"
      "mu   = %t[%d]\n"
      "zeta = %t[%d]\n"
      "C = %regchain_equations\n"
      "P = %l[%Az]\n"
      "S = %l[%Az]\n"
      "k = %t[%d]\n"
      "fn = %t[%t[%Az]]\n"
      "der_fn = %t[%t[%Az]]\n"
      "phi = %t[%d]\n"
      "deg = %t[%d]\n"
      "r = %t[%d]\n"
      "coeffs = %t[%t[%Qz]]\n"
      "A = %t[%Qz]\n"
      "roots = %t[%t[%z]]\n"
      "gamma = %t[%d]\n"
      "beta  = %t[%d]\n"
      "delta = %t[%d]\n"
      "omega  = %t[%d]\n",
      Z->number,
      &Z->sigma, &Z->mu, &Z->zeta, &Z->C, Z->P, Z->S, &Z->k,
      &Z->fn, &Z->der_fn, &Z->phi, &Z->deg, &Z->r,
      &Z->coeffs, &Z->A, &Z->roots, &Z->gamma, &Z->beta, &Z->delta, &Z->omega);
}
