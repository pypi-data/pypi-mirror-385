#include "bas_Denef_Lipshitz.h"
#include "bas_Yuple.h"
#include "bas_Zuple.h"

/*
 * Subfunction of bas_Denef_Lipshitz_leaf and bas_Denef_Lipshitz_resume
 * See these functions
 */

static void
bas_Denef_Lipshitz_leaf_core (
    struct bas_tableof_DLuple *DL,
    struct bas_DL_tree *tree,
    struct ba0_tableof_int_p *mu_max,
    struct bas_Yuple *U,
    struct bas_tableof_Zuple *tabZ,
    struct bad_base_field *K)
{
  ba0_int_p counter;

  counter = 0;
  while (tabZ->size > 0)
    {
      struct bas_Zuple *Z;
      enum bas_typeof_action_on_Zuple action;

      counter += 1;
      Z = tabZ->tab[tabZ->size - 1];

      action = bas_get_action_on_Zuple (Z, U);
      switch (action)
        {
        case bas_nothing_to_do_Zuple:

          bas_set_vertex_consistency_DL_tree (tree, Z->number,
              bas_consistent_vertex);

          ba0_realloc2_table ((struct ba0_table *) DL, DL->size + 1,
              (ba0_new_function *) & bas_new_DLuple);
          bas_set_YZuple_DLuple (DL->tab[DL->size], U, Z);
          DL->size += 1;
          tabZ->size -= 1;
          break;

        case bas_discard_Zuple:

          bas_set_vertex_consistency_DL_tree (tree, Z->number,
              bas_rejected_vertex);

          tabZ->size -= 1;
          break;

        case bas_k_to_secure_Zuple:
          bas_secure_k_Zuple (tabZ, mu_max, U, tree, K);
          break;

        case bas_r_to_secure_Zuple:
          bas_secure_r_Zuple (tabZ, mu_max, U, tree, K);
          break;

        case bas_beta_to_compute_Zuple:
          bas_compute_beta_Zuple (tabZ, mu_max, U, tree, K);
          break;

        case bas_A_to_specialize_and_beta_to_recompute_Zuple:
          bas_specialize_A_and_recompute_beta_Zuple (tabZ, mu_max, U, tree, K);
          break;
        }
    }
}

/*
 * texinfo: bas_Denef_Lipshitz_leaf
 * The regular differential chain @var{C} has been produced by 
 * @code{bad_Rosenfeld_Groebner} over some
 * initial differential system, possibly with @emph{ad hoc} equations
 * and over @var{K}.
 * The Yuple @var{U} is such that the field @code{kappa} is defined
 * for each differential indeterminate for which a formal power
 * series solution is sought and a defining differential equation
 * with a non numeric separant is present.
 * The function appends to @var{DL} finitely many DLuples obtained
 * by extending @var{C} with prolongation equations.
 * It assigns to @var{beta} the maximum-vector of the @code{beta}
 * fields of all produced DLuples.
 * Exception @code{BA0_ERRALG} is raised if the field @code{control}
 * of @var{beta} contains @code{bas_single_beta_control}.
 * This function is a sub-function of @code{bas_Denef_Lipshitz_aux}.
 */

BAS_DLL ba0_int_p
bas_Denef_Lipshitz_leaf (
    struct bas_tableof_DLuple *DL,
    struct bas_DL_tree *tree,
    ba0_int_p beta_in,
    struct bas_Yuple *U,
    struct bad_regchain *C,
    struct bad_base_field *K)
{
  struct bas_tableof_Zuple tabZ;
  struct ba0_tableof_int_p mu_max;
  struct ba0_mark M;
  ba0_int_p i, beta_out;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_init_table ((struct ba0_table *) &mu_max);
  ba0_realloc_table ((struct ba0_table *) &mu_max, U->Y.size);
  for (i = 0; i < U->Y.size; i++)
    mu_max.tab[i] = -1;
  mu_max.size = U->Y.size;
  ba0_pull_stack ();
/*
 * In principle we could have tabZ in another stack because it is
 * not returned by bas_Denef_Lipshitz_leaf. However ...
 */
  ba0_init_table ((struct ba0_table *) &tabZ);
  ba0_realloc2_table ((struct ba0_table *) &tabZ, 1,
      (ba0_new_function *) & bas_new_Zuple);
  tabZ.size = 1;
  bas_set_Yuple_Zuple (&tabZ, &mu_max, U, tree,
      (struct bap_tableof_polynom_mpz *) 0, C, K,
      (struct bav_tableof_variable *) 0);

  bas_Denef_Lipshitz_leaf_core (DL, tree, &mu_max, U, &tabZ, K);

  beta_out = beta_in;
  for (i = 0; i < mu_max.size; i++)
    if (beta_out < mu_max.tab[i])
      beta_out = mu_max.tab[i];

  for (i = 0; i < U->kappa.size; i++)
    if (beta_out < U->kappa.tab[i])
      beta_out = U->kappa.tab[i];

  ba0_restore (&M);
  return beta_out;
}

/*
 * Subfunction of bas_Denef_Lipshitz_aux
 * Return the max order of all the derivation operators encoded in thetas
 * such that the associated differential indeterminate in leaders belongs to Y
 */

static ba0_int_p
bas_max_thetas (
    struct bav_tableof_variable *leaders,
    struct bav_tableof_term *thetas,
    struct bas_Yuple *U)
{
  struct bav_symbol *y;
  ba0_int_p i, j, k, max_order = 0;

  for (i = 0; i < leaders->size; i++)
    {
      y = leaders->tab[i]->root;;
      j = bav_get_dictionary_symbol (&U->dict_Y, &U->Y, y);
      if (j != BA0_NOT_AN_INDEX)
        {
          k = bav_total_degree_term (thetas->tab[i]);
          if (k > max_order)
            max_order = k;
        }
    }
  return max_order;
}

/*
 * texinfo: bas_Denef_Lipshitz_aux
 * The ideal @var{ideal} and the splitting tree @var{RG_tree} have been 
 * produced by the @code{bad_Rosenfeld_Groebner} algorithm over some
 * initial differential system, possibly with @emph{ad hoc} equations
 * and over @var{K}.
 * The argument @var{number} is the number of some node in @var{RG_tree}.
 * The Yuple @var{U} has been partially initialized: the data related
 * to the differential indeterminates for which a formal power
 * series solution is sought have been computed but not the data
 * related to the defining ODE of these differential indeterminates.
 * The function appends to @var{DL} finitely many DLuples obtained
 * by processing the components of @var{ideal} which belong to
 * the splitting tree starting at vertex @var{number}.
 * It assigns to @var{beta} the bound defined by all these
 * DLuples and the differential reductions performed by the
 * differential elimination process.
 * This function is a sub-function of @code{bas_Denef_Lipshitz}.
 */

BAS_DLL ba0_int_p
bas_Denef_Lipshitz_aux (
    struct bas_tableof_DLuple *DL,
    struct bas_DL_tree *DL_tree,
    ba0_int_p beta_in,
    struct bas_Yuple *U,
    struct bad_intersectof_regchain *ideal,
    struct bad_splitting_tree *RG_tree,
    ba0_int_p number,
    struct bad_base_field *K)
{
  struct bad_splitting_vertex *V;
  enum bad_typeof_splitting_edge type = bad_none_edge;
  ba0_int_p delta, beta_out = 0;

  V = RG_tree->vertices.tab[number];
  delta = bas_max_thetas (&V->leaders, &V->thetas, U);

  if (V->edges.size > 0)
    type = V->edges.tab[0]->type;

  if (V->shape == bad_box_vertex)
    {
      struct bad_regchain *C;
      ba0_int_p old_size;
/*
 * It is necessarily associated to some regular differential chain C
 */
      C = bad_get_regchain_intersectof_regchain (ideal, number);
      if (C == (struct bad_regchain *) 0)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
/*
 * Finish initializing U - in particular kappa[i] for base field separants
 */
      bas_set_ode_Yuple (U, C, K);
/*
 * Apply the leaf algorithm
 */
      old_size = DL->size;
      beta_out = bas_Denef_Lipshitz_leaf (DL, DL_tree, beta_in, U, C, K);
      beta_out += delta;
    }
  else if (V->edges.size == 0)
    {
      beta_out = beta_in + delta;
    }
  else if (type == bad_factor_edge)
    {
      ba0_int_p i, beta_i;
/*
 * This type is associated to inequation production
 * Thus the third argument of bas_Denef_Lipshitz_aux is regularly updated and
 *
 *      beta_out = beta_1 * e_1 + ... + beta_t * e_t
 */
      beta_out = 0;
      beta_i = beta_in;
      for (i = 0; i < V->edges.size; i++)
        {
          ba0_int_p dst = V->edges.tab[i]->dst;
          ba0_int_p mult = V->edges.tab[i]->multiplicity;
          beta_i =
              bas_Denef_Lipshitz_aux (DL, DL_tree, beta_i, U, ideal, RG_tree,
              dst, K);
          beta_out += mult * beta_i;
        }
      beta_out += delta;
    }
  else if (type == bad_separant_edge)
    {
      struct bav_symbol *y = V->edges.tab[0]->leader->root;
      ba0_int_p dst, beta_i = 0;
      ba0_int_p j, new_kappa_j, old_kappa_j;
/*
 * This type is associated to inequation production      
 * There are 1 or 2 children
 */
      if (V->edges.size == 2)
        {
          dst = V->edges.tab[0]->dst;
          beta_i =
              bas_Denef_Lipshitz_aux (DL, DL_tree, beta_in, U, ideal, RG_tree,
              dst, K);
          new_kappa_j = beta_i;
        }
      else if (V->edges.size == 1)
        {
          beta_i = beta_in;
          new_kappa_j = 0;
        }
      else
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
/*
 * j = the index associated to y
 * the old value of kappa_y is saved for further restoration
 */
      j = bav_get_dictionary_symbol (&U->dict_Y, &U->Y, y);
      if (j != BA0_NOT_AN_INDEX)
        {
          old_kappa_j = U->kappa.tab[j];
          U->kappa.tab[j] = new_kappa_j;
        }
      else
        old_kappa_j = 0;
/*
 * The third argument of bas_Denef_Lipshitz_aux is beta_i
 */
      dst = V->edges.tab[V->edges.size - 1]->dst;
      beta_i =
          bas_Denef_Lipshitz_aux (DL, DL_tree, beta_i, U, ideal, RG_tree, dst,
          K);

      if (j != BA0_NOT_AN_INDEX)
        U->kappa.tab[j] = old_kappa_j;

      beta_out = beta_i + delta;
    }
  else if (type == bad_initial_edge)
    {
      ba0_int_p dst, beta_i;
/*
 * This type produces inequations
 * Thus the third argument to bas_Denef_Lipshitz_aux is regularly updated and
 *
 *      beta_out = max (beta_1, beta_2) = beta_2
 */
      if (V->edges.size == 2)
        {
          dst = V->edges.tab[0]->dst;
          beta_i =
              bas_Denef_Lipshitz_aux (DL, DL_tree, beta_in, U, ideal, RG_tree,
              dst, K);
        }
      else
        beta_i = beta_in;

      dst = V->edges.tab[V->edges.size - 1]->dst;
      beta_i =
          bas_Denef_Lipshitz_aux (DL, DL_tree, beta_i, U, ideal, RG_tree, dst,
          K);
      beta_out = beta_i + delta;
    }
  else if (type == bad_regularize_edge || type == bad_reg_characteristic_edge)
    {
      ba0_int_p i, beta_i;
/*
 * These types correspond to factorizations but do not produce inequations
 * Thus the third argument to bas_Denef_Lipshitz_aux is beta_in and
 *
 *      beta_out = beta_1 + ... + beta_t
 *
 * No multiplicities because the regular differential chain is squarefree
 */
      beta_out = 0;
      for (i = 0; i < V->edges.size; i++)
        {
          ba0_int_p dst = V->edges.tab[i]->dst;
          beta_i =
              bas_Denef_Lipshitz_aux (DL, DL_tree, beta_in, U, ideal, RG_tree,
              dst, K);
          beta_out += beta_i;
        }
      beta_out += delta;
    }
  else if (V->edges.size == 1)
    {
      ba0_int_p dst, beta_i;
/*
 * bad_critical_pair_edge, bad_critical_pair_novar_edge, 
 * bad_redzero_edge, bad_first_edge
 */
      dst = V->edges.tab[0]->dst;
      beta_i =
          bas_Denef_Lipshitz_aux (DL, DL_tree, beta_in, U, ideal, RG_tree, dst,
          K);

      beta_out = beta_i + delta;
    }
  else
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  return beta_out;
}

/*
 * texinfo: bas_Denef_Lipshitz
 * The tables @var{eqns} and @var{ineqs} contain the differential
 * system of equations and inequations to be processed.
 * The table @var{properties} provides the properties needed by
 * the @code{bad_Rosenfeld_Groebner} function.
 * The table @var{Y} contains the differential indeterminates for
 * which formal power series solutions are sought.
 * The prolongation pattern @var{Ybar} associates to each 
 * differential indeterminate in @var{Y} the subscripted variables
 * used to denote the coefficients of its formal power series solution.
 * The variable @var{q} contains the variable used for the polynomials
 * @math{A(q)} (see @code{struct bas_Zuple}).
 * The symbol @var{x} provides the derivation of the problem.
 * The function applies an experimental version of the @code{DenefLipshitz} 
 * algorithm over all these input data, using the strategy given by
 * @var{beta_control} and store the result in @var{DL}.
 */

BAS_DLL void
bas_Denef_Lipshitz (
    struct bas_tableof_DLuple *DL,
    struct bas_DL_tree *tree,
    struct bap_tableof_polynom_mpz *eqns,
    struct bap_tableof_polynom_mpz *ineqs,
    struct ba0_tableof_string *properties,
    struct bav_tableof_symbol *Y,
    struct baz_prolongation_pattern *Ybar,
    struct bav_variable *q,
    struct bav_symbol *x)
{
  struct bas_Yuple U;
  struct bad_intersectof_regchain *ideal;
  struct bad_splitting_tree *RG_tree;
  struct bad_base_field K;
  struct bad_regchain A;
  struct bad_splitting_control control;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
/*
 * Initialize ideal and set its properties 
 */
  ideal = bad_new_intersectof_regchain ();
  bad_set_properties_intersectof_regchain (ideal, properties);
  bad_set_automatic_properties_intersectof_regchain (ideal);
  bad_clear_property_intersectof_regchain (ideal, bad_prime_ideal_property);
/*
 * Initialize RG_tree to quiet splitting tree
 */
  RG_tree = bad_new_splitting_tree ();
  bad_reset_splitting_tree (RG_tree, bad_quiet_splitting_tree);
/*
 * Initialize K - which is supposed to be the field of the rational numbers
 */
  bad_init_base_field (&K);
  if (bad_has_property_intersectof_regchain (ideal, bad_autoreduced_property))
    K.assume_reduced = true;
/*
 * Initialize A and its properties
 */
  bad_init_regchain (&A);
  bad_set_properties_regchain (&A, properties);
  bad_set_automatic_properties_regchain (&A);
/*
 * Differential elimination stage for DenefLipshitz
 */
  bad_init_splitting_control (&control);
  bad_set_DenefLipshitz_splitting_control (&control, true);
/*
 * RosenfeldGroebner
 */
  bad_Rosenfeld_Groebner (ideal, RG_tree, eqns, ineqs, &K, &A, &control);

  if (tree->activity == bas_verbose_DL_tree)
    bad_dot_splitting_tree (RG_tree);

  ba0_pull_stack ();
/*
 * U lies in the same stack as DL - necessarily because it will be reallocated
 * However beta does not because it will not be reallocated
 */
  bas_init_Yuple (&U);
  bas_set_Y_Ybar_Yuple (&U, Y, Ybar, ineqs, q, x);

  bas_Denef_Lipshitz_aux (DL, tree, 0, &U, ideal, RG_tree, 0, &K);

  ba0_restore (&M);
}

/*
 * texinfo: bas_prolongate_DLuple
 * Assign to @var{dst} the DLuple obtained by prolongating @var{src}
 * using @var{vars}. The table @var{vars} is supposed to contained
 * subscripted variables. These variables provide the prolongation
 * limits.
 */

BAS_DLL void
bas_prolongate_DLuple (
    struct bas_DLuple *dst,
    struct bas_DLuple *src,
    struct bav_tableof_variable *vars)
{
  struct bas_tableof_DLuple DL;
  struct bas_DL_tree tree;
  struct bas_tableof_Zuple tabZ;
  struct ba0_tableof_int_p mu_max;
  struct bad_base_field K;
  struct bas_Yuple U;
  struct bap_listof_polynom_mpz *L;
  struct bap_tableof_polynom_mpz all_ineqs;
  struct ba0_mark M;
  ba0_int_p i;

  ba0_push_another_stack ();
  ba0_record (&M);
/*
 * The field of the rational numbers
 */
  bad_init_base_field (&K);
  if (bad_has_property_regchain (&src->C, bad_autoreduced_property))
    K.assume_reduced = true;
/*
 * mu_max
 */
  ba0_init_table ((struct ba0_table *) &mu_max);
  ba0_realloc_table ((struct ba0_table *) &mu_max, src->Y.size);
  for (i = 0; i < src->Y.size; i++)
    mu_max.tab[i] = -1;
  mu_max.size = src->Y.size;
/*
 * DL
 */
  ba0_init_table ((struct ba0_table *) &DL);
  bas_init_DL_tree (&tree);
  bas_reset_DL_tree (&tree, bas_quiet_DL_tree);
/*
 * Start restoring U
 */
  bas_init_Yuple (&U);
/*
 * all_ineqs = ineqs + src->S 
 */
  ba0_init_table ((struct ba0_table *) &all_ineqs);
  ba0_realloc_table ((struct ba0_table *) &all_ineqs,
      ba0_length_list ((struct ba0_list *) src->S));
  for (L = src->S; L != (struct bap_listof_polynom_mpz *) 0; L = L->next)
    {
      all_ineqs.tab[all_ineqs.size] = L->value;
      all_ineqs.size += 1;
    }

  bas_set_Y_Ybar_Yuple (&U, &src->Y, &src->Ybar, &all_ineqs, src->q, src->x);
/*
 * Restore kappa
 */
  ba0_set_table ((struct ba0_table *) &U.kappa,
      (struct ba0_table *) &src->kappa);
/*
 * Finish restoring U 
 */
  bas_set_ode_Yuple (&U, &src->C, &K);
/*
 * tabZ
 */
  ba0_init_table ((struct ba0_table *) &tabZ);
  ba0_realloc2_table ((struct ba0_table *) &tabZ, 1,
      (ba0_new_function *) & bas_new_Zuple);
  tabZ.size = 1;
  bas_set_Yuple_Zuple (&tabZ, &mu_max, &U, &tree,
      (struct bap_tableof_polynom_mpz *) 0, &src->C, &K, vars);

  bas_Denef_Lipshitz_leaf_core (&DL, &tree, &mu_max, &U, &tabZ, &K);

  if (DL.size != 1)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_pull_stack ();

  bas_set_DLuple (dst, DL.tab[0]);

  ba0_restore (&M);
}

/*
 * texinfo: bas_Denef_Lipshitz_resume
 * The DLuple @var{DL0} has been produced by the 
 * @code{bas_Denef_Lipshitz_leaf} or the 
 * @code{bas_Denef_Lipshitz_resume} function.
 * Resume the computation, taking into account the new equations
 * and inequations stored in @var{eqns} and @var{ineqs}.
 * Append the new DLuples to @var{DL}.
 */

BAS_DLL void
bas_Denef_Lipshitz_resume (
    struct bas_tableof_DLuple *DL,
    struct bas_DLuple *DL0,
    struct bap_tableof_polynom_mpz *eqns,
    struct bap_tableof_polynom_mpz *ineqs)
{
  struct bas_DL_tree tree;
  struct bas_tableof_Zuple tabZ;
  struct bad_base_field K;
  struct bas_Yuple U;
  struct bap_listof_polynom_mpz *L;
  struct bap_tableof_polynom_mpz all_ineqs;
  struct ba0_mark M;
  struct ba0_tableof_int_p mu_max;
  ba0_int_p i;

  ba0_push_another_stack ();
  ba0_record (&M);
/*
 * mu_max
 */
  ba0_init_table ((struct ba0_table *) &mu_max);
  ba0_realloc_table ((struct ba0_table *) &mu_max, DL0->Y.size);
  for (i = 0; i < DL0->Y.size; i++)
    mu_max.tab[i] = -1;
  mu_max.size = DL0->Y.size;
/*
 * The field of the rational numbers
 */
  bad_init_base_field (&K);
  if (bad_has_property_regchain (&DL0->C, bad_autoreduced_property))
    K.assume_reduced = true;
/*
 * all_ineqs = ineqs + DL0->S 
 */
  ba0_init_table ((struct ba0_table *) &all_ineqs);
  ba0_realloc_table ((struct ba0_table *) &all_ineqs, ineqs->size +
      ba0_length_list ((struct ba0_list *) DL0->S));
  ba0_set_table ((struct ba0_table *) &all_ineqs, (struct ba0_table *) ineqs);
  for (L = DL0->S; L != (struct bap_listof_polynom_mpz *) 0; L = L->next)
    {
      all_ineqs.tab[all_ineqs.size] = L->value;
      all_ineqs.size += 1;
    }

  ba0_pull_stack ();
/*
 * The tree
 */
  bas_init_DL_tree (&tree);
  bas_reset_DL_tree (&tree, bas_quiet_DL_tree);
/*
 * Start restoring U
 */
  bas_init_Yuple (&U);
  bas_set_Y_Ybar_Yuple (&U, &DL0->Y, &DL0->Ybar, &all_ineqs, DL0->q, DL0->x);
/*
 * Restore kappa
 */
  ba0_set_table ((struct ba0_table *) &U.kappa,
      (struct ba0_table *) &DL0->kappa);
/*
 * Finish restoring U
 */
  bas_set_ode_Yuple (&U, &DL0->C, &K);

/*
 * tabZ
 */
  ba0_init_table ((struct ba0_table *) &tabZ);
  ba0_realloc2_table ((struct ba0_table *) &tabZ, 1,
      (ba0_new_function *) & bas_new_Zuple);
  tabZ.size = 1;
  bas_set_Yuple_Zuple (&tabZ, &mu_max, &U, &tree, eqns, &DL0->C, &K,
      (struct bav_tableof_variable *) 0);

  bas_Denef_Lipshitz_leaf_core (DL, &tree, &mu_max, &U, &tabZ, &K);

  ba0_restore (&M);
}
