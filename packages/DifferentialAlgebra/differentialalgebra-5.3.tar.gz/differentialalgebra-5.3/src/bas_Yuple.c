#include "bas_Yuple.h"

/*
 * texinfo: bas_init_Yuple
 * Initialize @var{U} to the empty Yuple.
 */

BAS_DLL void
bas_init_Yuple (
    struct bas_Yuple *U)
{
  ba0_init_table ((struct ba0_table *) &U->Y);
  bav_init_dictionary_symbol (&U->dict_Y, 6);

  baz_init_prolongation_pattern (&U->Ybar);
  ba0_init_point ((struct ba0_point *) &U->point);

  ba0_init_table ((struct ba0_table *) &U->R);
  ba0_init_dictionary (&U->dict_R, 1, 6);

  ba0_init_table ((struct ba0_table *) &U->ozs);

  ba0_init_table ((struct ba0_table *) &U->kappa);

  ba0_init_table ((struct ba0_table *) &U->ode);
  ba0_init_table ((struct ba0_table *) &U->order);

  ba0_init_table ((struct ba0_table *) &U->sep);

  U->S = (struct bap_listof_polynom_mpz *) 0;

  ba0_init_table ((struct ba0_table *) &U->binomials);

  U->q = BAV_NOT_A_VARIABLE;
  U->x = BAV_NOT_A_SYMBOL;
}

/*
 * texinfo: bas_new_Yuple
 * Allocate a new Yuple, initialize it and return it.
 */

BAS_DLL struct bas_Yuple *
bas_new_Yuple (
    void)
{
  struct bas_Yuple *U;

  U = (struct bas_Yuple *) ba0_alloc (sizeof (struct bas_Yuple));
  bas_init_Yuple (U);
  return U;
}

/*
 * texinfo: bas_set_Yuple
 * Assign @var{src} to @var{dst}.
 */

BAS_DLL void
bas_set_Yuple (
    struct bas_Yuple *dst,
    struct bas_Yuple *src)
{
  if (dst != src)
    {
      ba0_set_table ((struct ba0_table *) &dst->Y,
          (struct ba0_table *) &src->Y);
      bav_set_dictionary_symbol (&dst->dict_Y, &src->dict_Y);

      baz_set_prolongation_pattern (&dst->Ybar, &src->Ybar);
      baz_set_point_ratfrac (&dst->point, &src->point);

      ba0_set_table ((struct ba0_table *) &dst->R,
          (struct ba0_table *) &src->R);
      ba0_set_dictionary (&dst->dict_R, &src->dict_R);

      ba0_set_table ((struct ba0_table *) &dst->ozs,
          (struct ba0_table *) &src->ozs);

      ba0_set_table ((struct ba0_table *) &dst->kappa,
          (struct ba0_table *) &src->kappa);

      bap_set_tableof_tableof_polynom_mpz (&dst->ode, &src->ode);
      ba0_set_table ((struct ba0_table *) &dst->order,
          (struct ba0_table *) &src->order);

      bap_set_tableof_tableof_polynom_mpz (&dst->sep, &src->sep);

      dst->S = ba0_copy ("%l[%Az]", src->S);

      bap_set_tableof_polynom_mpq (&dst->binomials, &src->binomials);

      dst->q = src->q;
      dst->x = src->x;
    }
}

/*
 * Evaluate y to a rational fraction Q using Ybar.
 * Among the variables Q depend on, there must be a single subscripted one.
 * Assign to index_in_rigs, the index_in_rigs of its symbol.
 * Assign to subscript the subscript of its symbol, which is also
 *      the subscript of the order zero variable corresponding to y.
 */

static void
bas_symbol_to_subscripted (
    ba0_int_p *index_in_rigs,
    ba0_int_p *subscript,
    struct bav_symbol *y,
    struct baz_prolongation_pattern *Ybar)
{
  struct bav_tableof_variable dst, src;
  struct bav_variable *v;
  struct ba0_mark M;
  ba0_int_p i;

  ba0_record (&M);

  ba0_init_table ((struct ba0_table *) &src);
  ba0_realloc_table ((struct ba0_table *) &src, 1);
  src.tab[0] = bav_symbol_to_variable (y);
  src.size = 1;

  ba0_init_table ((struct ba0_table *) &dst);

  baz_variable_mapping_prolongation_pattern (&dst, &src, Ybar);

  v = BAV_NOT_A_VARIABLE;
  for (i = 0; i < dst.size; i++)
    {
      if (bav_is_subscripted_symbol (dst.tab[i]->root))
        {
          if (v == BAV_NOT_A_VARIABLE)
            v = dst.tab[i];
          else
            BA0_RAISE_EXCEPTION (BAS_ERRPAT);
        }
    }
  if (v == BAV_NOT_A_VARIABLE)
    BA0_RAISE_EXCEPTION (BAS_ERRPAT);

  ba0_restore (&M);

  *index_in_rigs = v->root->index_in_rigs;
  *subscript = bav_subscript_of_symbol (v->root);
}

/*
 * texinfo: bas_set_Y_Ybar_Yuple
 * Fill the fields of @var{U} which are determined by
 * @var{Y}, @var{Ybar}, @var{ineqs}, @var{q} and @var{x} only.
 * These fields are @code{Y}, @code{dict_Y}, @code{R}, @code{dict_R},
 * @code{ozs}, @code{S}, @code{q} and @code{x}.
 * All the other tables are allocated to the size of @var{Y}
 * and get initialized also but only to avoid keeping 
 * allocated tables with non initialized entries.
 * This function is called only once by @code{bas_Denef_Lipshitz}.
 * The field @code{S} is assigned the list of all the polynomials
 * of @var{ineqs} which are constant with respect to @var{x}.
 * Exceptions @code{BAV_ERRDSY} and @code{BAD_ERRIND} are raised in
 * the case of a wrong argument @var{Y}.
 * Exception @code{BAS_ERRPAT} is raised in the case of a wrong
 * argument @var{Ybar}.
 */

BAS_DLL void
bas_set_Y_Ybar_Yuple (
    struct bas_Yuple *U,
    struct bav_tableof_symbol *Y,
    struct baz_prolongation_pattern *Ybar,
    struct bap_tableof_polynom_mpz *ineqs,
    struct bav_variable *q,
    struct bav_symbol *x)
{
  struct bap_polynom_mpz *poly;
  ba0_int_p i, j, k, l;
  ba0_int_p n = Y->size;

  ba0_reset_table ((struct ba0_table *) &U->Y);
  ba0_realloc_table ((struct ba0_table *) &U->Y, n);
  bav_reset_dictionary_symbol (&U->dict_Y);

  baz_set_prolongation_pattern (&U->Ybar, Ybar);

  ba0_reset_dictionary (&U->dict_R);
  ba0_reset_table ((struct ba0_table *) &U->R);
  ba0_realloc_table ((struct ba0_table *) &U->R, n);

  ba0_realloc_table ((struct ba0_table *) &U->ozs, n);

  for (i = 0; i < n; i++)
    {
      j = bav_get_dictionary_symbol (&U->dict_Y, &U->Y, Y->tab[i]);
      if (j != BA0_NOT_AN_INDEX)
        BA0_RAISE_EXCEPTION (BAV_ERRDSY);
      if (Y->tab[i]->type != bav_dependent_symbol)
        BA0_RAISE_EXCEPTION (BAD_ERRIND);

      bav_add_dictionary_symbol (&U->dict_Y, &U->Y, Y->tab[i], U->Y.size);
      U->Y.tab[U->Y.size] = Y->tab[i];
      U->Y.size += 1;

      bas_symbol_to_subscripted (&k, &l, Y->tab[i], Ybar);
      j = ba0_get_dictionary (&U->dict_R, (struct ba0_table *) &U->R,
          (void *) k);
      if (j != BA0_NOT_AN_INDEX)
        BA0_RAISE_EXCEPTION (BAS_ERRPAT);
      ba0_add_dictionary (&U->dict_R, (struct ba0_table *) &U->R, (void *) k,
          U->R.size);
      U->R.tab[U->R.size] = k;
      U->R.size += 1;
      U->ozs.tab[U->ozs.size] = l;
      U->ozs.size += 1;
    }

  ba0_realloc_table ((struct ba0_table *) &U->kappa, n);
  U->kappa.size = n;

  ba0_realloc2_table ((struct ba0_table *) &U->ode, n,
      (ba0_new_function *) & ba0_new_table);
  U->ode.size = n;

  ba0_realloc_table ((struct ba0_table *) &U->order, n);
  U->order.size = n;

  ba0_realloc2_table ((struct ba0_table *) &U->sep, n,
      (ba0_new_function *) & ba0_new_table);
  U->sep.size = n;

  for (i = 0; i < n; i++)
    {
      U->kappa.tab[i] = -1;
      ba0_reset_table ((struct ba0_table *) U->ode.tab[i]);
      U->order.tab[i] = -1;
      ba0_reset_table ((struct ba0_table *) U->sep.tab[i]);
    }

  for (i = 0; i < ineqs->size; i++)
    {
      if (bap_is_constant_polynom_mpz (ineqs->tab[i], x))
        {
          poly = bap_new_polynom_mpz ();
          bap_normal_numeric_primpart_polynom_mpz (poly, ineqs->tab[i]);
          U->S =
              (struct bap_listof_polynom_mpz *) ba0_cons_list (poly,
              (struct ba0_list *) U->S);
        }
    }

  U->q = q;
  U->x = x;
}

/*
 * texinfo: bas_set_ode_Yuple
 * Fill the fields of @var{U} which are determined by @var{C} and @var{K}.
 * It is assumed that @code{bas_set_Y_Ybar_Yuple} has already been called.
 * This function is called for each regular differential chain 
 * produced by the differential elimination stage.
 * The fields are @code{ode}, @code{order} and @code{sep}.
 *
 * The field @code{kappa} is updated:
 * each entry of @code{kappa} is set to @math{0} if 
 * it is undefined (i.e. equal to @math{-1}) and the separant
 * of the corresponding ODE belongs to @var{K}.
 *
 * Exception @code{BA0_ERRALG} is raised if an entry of @code{kappa}
 * is undefined and the separant of its associated ODE does not belong
 * to @var{K}.
 */

BAS_DLL void
bas_set_ode_Yuple (
    struct bas_Yuple *U,
    struct bad_regchain *C,
    struct bad_base_field *K)
{
  ba0_int_p i;
/*
 * Reset all these fields
 */
  for (i = 0; i < U->Y.size; i++)
    {
      ba0_reset_table ((struct ba0_table *) U->ode.tab[i]);
      U->order.tab[i] = -1;
      ba0_reset_table ((struct ba0_table *) U->sep.tab[i]);
    }
/*
 * Fill the entries of ode, order, sep and update kappa
 */
  for (i = 0; i < C->decision_system.size; i++)
    {
      struct bav_variable *v;
      ba0_int_p j;

      v = bap_leader_polynom_mpz (C->decision_system.tab[i]);
      j = bav_get_dictionary_symbol (&U->dict_Y, &U->Y, v->root);
      if (j != BA0_NOT_AN_INDEX)
        {
          struct bap_tableof_polynom_mpz *S;

          S = U->ode.tab[j];
          ba0_realloc2_table ((struct ba0_table *) S, 1,
              (ba0_new_function *) & bap_new_polynom_mpz);
          bap_set_polynom_mpz (S->tab[0], C->decision_system.tab[i]);
          baz_prolongate_point_ratfrac_using_pattern_term (&U->point,
              &U->point, &U->Ybar, &S->tab[0]->total_rank);
          S->size = 1;

          U->order.tab[j] = bav_order_variable (v, U->x);

          S = U->sep.tab[j];
          ba0_realloc2_table ((struct ba0_table *) S, 1,
              (ba0_new_function *) & bap_new_polynom_mpz);
          bap_separant_polynom_mpz (S->tab[0], C->decision_system.tab[i]);
          S->size = 1;

          if (U->kappa.tab[j] == -1)
            {
              if (bad_member_nonzero_polynom_base_field (S->tab[0], K))
                U->kappa.tab[j] = 0;
              else
                BA0_RAISE_EXCEPTION (BA0_ERRALG);
            }
        }
    }
}

/*
 * texinfo: bas_prolongate_binomials_Yuple
 * Prolongate the @code{binomials} field of @var{U} up to the binomial
 * polynomial of degree @var{degree}. These polynomials depend on the
 * variable provided by the field @code{q} of @var{U}.
 * The successive values of the @code{binomials} table are:
 * @display
 * @math{[1], \quad [1, q], \quad [1, q(q-1)/2], \quad @dots{}}
 * @end display
 */

BAS_DLL void
bas_prolongate_binomials_Yuple (
    struct bas_Yuple *U,
    ba0_int_p degree)
{
  struct bap_polynom_mpq bin_fact;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  bap_init_polynom_mpq (&bin_fact);
  ba0_pull_stack ();

  ba0_realloc2_table ((struct ba0_table *) &U->binomials, degree + 1,
      (ba0_new_function *) & bap_new_polynom_mpq);
  if (U->binomials.size == 0)
    {
      bap_set_polynom_one_mpq (U->binomials.tab[0]);
      U->binomials.size = 1;
    }
  while (U->binomials.size <= degree)
    {
      ba0_push_another_stack ();
      ba0_scanf_printf ("%Aq", "(%v - %d)/%d", &bin_fact, U->q,
          U->binomials.size - 1, U->binomials.size);
      ba0_pull_stack ();
      bap_mul_polynom_mpq (U->binomials.tab[U->binomials.size],
          U->binomials.tab[U->binomials.size - 1], &bin_fact);
      U->binomials.size += 1;
    }
  ba0_restore (&M);
}

/*
 * texinfo: bas_printf_Yuple
 * The general printing function for Yuples.
 * It can be called through @code{ba0_printf/%Yuple}.
 */

BAS_DLL void
bas_printf_Yuple (
    void *U0)
{
  struct bas_Yuple *U = (struct bas_Yuple *) U0;
  ba0_printf
      ("Y = %t[%y]\n"
      "Ybar = %prolongation_pattern\n"
      "point = %point(%Qz)\n"
      "R = %t[%d]\n"
      "ozs = %t[%d]\n"
      "kappa = %t[%d]\n"
      "ode = %t[%t[%Az]]\n"
      "order = %t[%d]\n"
      "sep = %t[%t[%Az]]\n"
      "S = %l[%Az]\n"
      "binomials = %t[%Aq]\n"
      "q = %v\n"
      "x = %y\n",
      &U->Y, &U->Ybar, &U->point, &U->R, &U->ozs,
      &U->kappa, &U->ode, &U->order, &U->sep, U->S, &U->binomials, U->q, U->x);
}

BAS_DLL void *
bas_copy_Yuple (
    void *AA)
{
  struct bas_Yuple *B;

  B = bas_new_Yuple ();
  bas_set_Yuple (B, (struct bas_Yuple *) AA);
  return B;
}
