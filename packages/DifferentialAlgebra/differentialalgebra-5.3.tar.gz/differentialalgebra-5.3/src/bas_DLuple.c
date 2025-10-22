#include "bas_DLuple.h"

/*
 * texinfo: bas_init_DLuple
 * Initialize @var{DL} to the empty DLuple.
 */

BAS_DLL void
bas_init_DLuple (
    struct bas_DLuple *DL)
{
  ba0_init_table ((struct ba0_table *) &DL->Y);
  baz_init_prolongation_pattern (&DL->Ybar);
  DL->x = BAV_NOT_A_SYMBOL;
  ba0_init_table ((struct ba0_table *) &DL->order);
  ba0_init_table ((struct ba0_table *) &DL->kappa);
  bad_init_regchain (&DL->C);
  DL->S = (struct bap_listof_polynom_mpz *) 0;
  ba0_init_table ((struct ba0_table *) &DL->k);
  ba0_init_table ((struct ba0_table *) &DL->r);
  DL->q = BAV_NOT_A_VARIABLE;
  ba0_init_table ((struct ba0_table *) &DL->A);
  ba0_init_table ((struct ba0_table *) &DL->gamma);
  ba0_init_table ((struct ba0_table *) &DL->mu);
  ba0_init_table ((struct ba0_table *) &DL->sigma);
  ba0_init_table ((struct ba0_table *) &DL->beta);
  ba0_init_table ((struct ba0_table *) &DL->delta);
}

/*
 * texinfo: bas_new_DLuple
 * Allocate a new DLuple, initialize it and return it.
 */

BAS_DLL struct bas_DLuple *
bas_new_DLuple (
    void)
{
  struct bas_DLuple *DL;
  DL = (struct bas_DLuple *) ba0_alloc (sizeof (struct bas_DLuple));
  bas_init_DLuple (DL);
  return DL;
}

/*
 * texinfo: bas_set_DLuple
 * Assign @var{src} to @var{dst}.
 */

BAS_DLL void
bas_set_DLuple (
    struct bas_DLuple *dst,
    struct bas_DLuple *src)
{
  if (dst != src)
    {
      ba0_set_table ((struct ba0_table *) &dst->Y,
          (struct ba0_table *) &src->Y);

      baz_set_prolongation_pattern (&dst->Ybar, &src->Ybar);

      ba0_set_table ((struct ba0_table *) &dst->order,
          (struct ba0_table *) &src->order);

      dst->x = src->x;

      ba0_set_table ((struct ba0_table *) &dst->kappa,
          (struct ba0_table *) &src->kappa);

      bad_set_regchain (&dst->C, &src->C);

      dst->S = (struct bap_listof_polynom_mpz *) ba0_copy ("%l[%Az]", src->S);

      ba0_set_table ((struct ba0_table *) &dst->k,
          (struct ba0_table *) &src->k);

      ba0_set_table ((struct ba0_table *) &dst->r,
          (struct ba0_table *) &src->r);

      dst->q = src->q;

      baz_set_tableof_ratfrac (&dst->A, &src->A);

      ba0_set_table ((struct ba0_table *) &dst->gamma,
          (struct ba0_table *) &src->gamma);

      ba0_set_table ((struct ba0_table *) &dst->mu,
          (struct ba0_table *) &src->mu);

      ba0_set_table ((struct ba0_table *) &dst->sigma,
          (struct ba0_table *) &src->sigma);

      ba0_set_table ((struct ba0_table *) &dst->beta,
          (struct ba0_table *) &src->beta);

      ba0_set_table ((struct ba0_table *) &dst->delta,
          (struct ba0_table *) &src->delta);
    }
}

/*
 * texinfo: bas_sizeof_DLuple
 * Return the size of the memory needed to perform a copy of @var{DL}.
 * If @var{code} is @code{ba0_embedded} then @var{DL} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account.
 */

BAS_DLL unsigned ba0_int_p
bas_sizeof_DLuple (
    struct bas_DLuple *DL,
    enum ba0_garbage_code code)
{
  unsigned ba0_int_p size;
  struct bap_listof_polynom_mpz *L;
  ba0_int_p i;

  if (code == ba0_isolated)
    size = ba0_allocated_size (sizeof (struct bas_DLuple));
  else
    size = 0;
  size += ba0_sizeof_table ((struct ba0_table *) &DL->Y, ba0_embedded);
  size += baz_sizeof_prolongation_pattern (&DL->Ybar, ba0_embedded);
  size += ba0_sizeof_table ((struct ba0_table *) &DL->order, ba0_embedded);
  size += ba0_sizeof_table ((struct ba0_table *) &DL->kappa, ba0_embedded);
  size += bad_sizeof_regchain (&DL->C, ba0_embedded);
  for (L = DL->S; L != (struct bap_listof_polynom_mpz *) 0; L = L->next)
    {
      size += ba0_allocated_size (sizeof (struct bap_listof_polynom_mpz));
      size += bap_sizeof_polynom_mpz (L->value, ba0_isolated);
    }
  size += ba0_sizeof_table ((struct ba0_table *) &DL->k, ba0_embedded);
  size += ba0_sizeof_table ((struct ba0_table *) &DL->r, ba0_embedded);

  size += ba0_allocated_size (DL->A.size * sizeof (struct baz_ratfrac *));
  for (i = 0; i < DL->A.size; i++)
    size += baz_sizeof_ratfrac (DL->A.tab[i], ba0_isolated);

  size += ba0_sizeof_table ((struct ba0_table *) &DL->gamma, ba0_embedded);
  size += ba0_sizeof_table ((struct ba0_table *) &DL->mu, ba0_embedded);
  size += ba0_sizeof_table ((struct ba0_table *) &DL->sigma, ba0_embedded);
  size += ba0_sizeof_table ((struct ba0_table *) &DL->beta, ba0_embedded);
  size += ba0_sizeof_table ((struct ba0_table *) &DL->delta, ba0_embedded);
  return size;
}

/*
 * texinfo: bas_switch_ring_DLuple
 * This low level function should be used in conjunction with
 * @code{bav_set_differential_ring}: if @var{R} is a ring obtained by
 * application of @code{bav_set_differential_ring}
 * to the ring @var{DL} refers to, then this function makes @var{DL}
 * refer to @var{R}.
 */

BAS_DLL void
bas_switch_ring_DLuple (
    struct bas_DLuple *DL,
    struct bav_differential_ring *R)
{
  struct bap_listof_polynom_mpz *L;
  ba0_int_p i;

  for (i = 0; i < DL->Y.size; i++)
    DL->Y.tab[i] = bav_switch_ring_symbol (DL->Y.tab[i], R);
  baz_switch_ring_prolongation_pattern (&DL->Ybar, R);
  DL->x = bav_switch_ring_symbol (DL->x, R);
  bad_switch_ring_regchain (&DL->C, R);
  for (L = DL->S; L != (struct bap_listof_polynom_mpz *) 0; L = L->next)
    bap_switch_ring_polynom_mpz (L->value, R);
  DL->q = bav_switch_ring_variable (DL->q, R);
  for (i = 0; i < DL->A.size; i++)
    baz_switch_ring_ratfrac (DL->A.tab[i], R);
}

/*
 * Subfunction of bas_set_YZuple_DLuple which checks the
 *      consistency of the result
 */

static void
bas_check_DLuple (
    struct bas_DLuple *DL,
    struct bas_Yuple *U)
{
  struct ba0_tableof_int_p met;
  struct ba0_mark M;
  ba0_int_p i;

  ba0_record (&M);
  ba0_init_table ((struct ba0_table *) &met);
  ba0_realloc_table ((struct ba0_table *) &met, DL->Y.size);
  for (i = 0; i < DL->Y.size; i++)
    met.tab[i] = false;
  met.size = DL->Y.size;

  for (i = 0; i < DL->C.decision_system.size; i++)
    {
      struct bap_polynom_mpz *P = DL->C.decision_system.tab[i];
      ba0_int_p l;

      for (l = 0; l < P->total_rank.size; l++)
        {
          struct bav_variable *v = P->total_rank.rg[l].var;
          struct bav_symbol *y = v->root;
          ba0_int_p j, k;

          if (bav_is_subscripted_symbol (y))
            {
              j = ba0_get_dictionary (&U->dict_R, (struct ba0_table *) &U->R,
                  (void *) y->index_in_rigs);
              if (j != BA0_NOT_AN_INDEX)
                {
                  k = bav_subscript_of_symbol (y);
                  if (k > DL->sigma.tab[j])
                    BA0_RAISE_EXCEPTION (BA0_ERRALG);
                  else if (k == DL->sigma.tab[j])
                    met.tab[j] = true;
                }
            }
        }
    }

  for (i = 0; i < DL->Y.size; i++)
    {
      if (U->ode.tab[i]->size > 0)
        {
          struct bav_variable *v = bav_symbol_to_variable (DL->Y.tab[i]);
          ba0_int_p n, o, mu, sigma, r, k, beta, delta, gamma;

          n = DL->order.tab[i];
          o = U->ozs.tab[i];
          mu = DL->mu.tab[i];
          sigma = DL->sigma.tab[i];
          k = DL->k.tab[i];
          r = DL->r.tab[i];
          beta = DL->beta.tab[i];
          delta = DL->delta.tab[i];
          gamma = DL->gamma.tab[i];

          if (met.tab[i] == false)
            BA0_RAISE_EXCEPTION (BA0_ERRALG);
          if (beta != 2 * k + 2 + gamma + r)
            BA0_RAISE_EXCEPTION (BA0_ERRALG);
          if (bav_is_constant_variable (v, DL->x))
            {
              if (mu != 1)
                BA0_RAISE_EXCEPTION (BA0_ERRALG);
            }
          else
            {
              if (mu != sigma - o - n + r)
                BA0_RAISE_EXCEPTION (BA0_ERRALG);
            }
          if (mu + 1 < beta)
            BA0_RAISE_EXCEPTION (BA0_ERRALG);
          if (delta != n + 2 * k + 2 + gamma)
            BA0_RAISE_EXCEPTION (BA0_ERRALG);
        }
    }
}

/*
 * texinfo: bas_set_YZuple_DLuple
 * Assign to @var{DL} the DLuple defined by @var{U} and @var{Z}.
 * The result is obtained by copying the corresponding fields
 * of @var{U} and @var{Z}, except the field @code{S} of @var{DL}, which is the
 * union of the fields @code{S} of @var{U} and @var{Z}.
 */

BAS_DLL void
bas_set_YZuple_DLuple (
    struct bas_DLuple *DL,
    struct bas_Yuple *U,
    struct bas_Zuple *Z)
{
  struct bap_listof_polynom_mpz *L, *M;

  ba0_set_table ((struct ba0_table *) &DL->Y, (struct ba0_table *) &U->Y);

  baz_set_prolongation_pattern (&DL->Ybar, &U->Ybar);

  DL->x = U->x;

  ba0_set_table ((struct ba0_table *) &DL->order,
      (struct ba0_table *) &U->order);

  ba0_set_table ((struct ba0_table *) &DL->kappa,
      (struct ba0_table *) &U->kappa);

  bad_set_regchain (&DL->C, &Z->C);
  bad_set_number_regchain (&DL->C, Z->number);

  DL->S = (struct bap_listof_polynom_mpz *) ba0_copy ("%l[%Az]", Z->S);
  for (L = U->S; L != (struct bap_listof_polynom_mpz *) 0; L = L->next)
    {
      bool found = false;
      for (M = Z->S; M != (struct bap_listof_polynom_mpz *) 0 && !found;
          M = M->next)
        found = bap_equal_polynom_mpz (L->value, M->value);
      if (!found)
        DL->S =
            (struct bap_listof_polynom_mpz *) ba0_cons_list (L->value,
            (struct ba0_list *) DL->S);
    }

  ba0_set_table ((struct ba0_table *) &DL->k, (struct ba0_table *) &Z->k);

  ba0_set_table ((struct ba0_table *) &DL->r, (struct ba0_table *) &Z->r);

  DL->q = U->q;

  baz_set_tableof_ratfrac (&DL->A, &Z->A);

  ba0_set_table ((struct ba0_table *) &DL->gamma,
      (struct ba0_table *) &Z->gamma);

  ba0_set_table ((struct ba0_table *) &DL->mu, (struct ba0_table *) &Z->mu);

  ba0_set_table ((struct ba0_table *) &DL->sigma,
      (struct ba0_table *) &Z->sigma);

  ba0_set_table ((struct ba0_table *) &DL->beta, (struct ba0_table *) &Z->beta);

  ba0_set_table ((struct ba0_table *) &DL->delta,
      (struct ba0_table *) &Z->delta);
#if defined (BA0_HEAVY_DEBUG)
  bas_check_DLuple (DL, U);
#endif
}

/*
 * texinfo: bas_constant_variables_DLuple
 * Assign to @var{sigma} the maximum of the subscripts of the 
 * variables @code{y[i]} occurring in the field @code{C} of
 * @var{DL}, where @code{y[i]} denotes some subscripted variable 
 * associated to some element of the field @code{Y} of @var{DL} 
 * (@math{-1} if undefined). 
 * The @math{i}th entry of @var{sigma} corresponds to
 * the @math{i}th entry of the field @code{Y} of @var{DL}.
 * Assign to @var{omega} all the constant variables occurring
 * in the field @code{C} of @var{DL} which are not the leaders
 * of any element of @code{C}.
 */

BAS_DLL void
bas_constant_variables_DLuple (
    struct ba0_tableof_int_p *sigma,
    struct bav_tableof_variable *omega,
    struct bas_DLuple *DL)
{
  struct bas_Yuple U;
  struct bap_tableof_polynom_mpz S;
  struct bav_dictionary_variable dict;
  struct bav_tableof_variable vars;
  struct ba0_mark M;
  ba0_int_p i;

  ba0_realloc_table ((struct ba0_table *) sigma, DL->Y.size);
  for (i = 0; i < sigma->alloc; i++)
    sigma->tab[i] = BAS_NOT_A_NUMBER;
  sigma->size = sigma->alloc;

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_init_table ((struct ba0_table *) &S);
  ba0_set_table_list ((struct ba0_table *) &S, (struct ba0_list *) DL->S);

  bas_init_Yuple (&U);
  bas_set_Y_Ybar_Yuple (&U, &DL->Y, &DL->Ybar, &S, DL->q, DL->x);

  ba0_init_table ((struct ba0_table *) &vars);
  bav_init_dictionary_variable (&dict, 8);

  for (i = 0; i < DL->C.decision_system.size; i++)
    {
      struct bap_polynom_mpz *poly = DL->C.decision_system.tab[i];
      ba0_int_p k;

      for (k = 0; k < poly->total_rank.size; k++)
        {
          struct bav_variable *v = poly->total_rank.rg[k].var;
          struct bav_symbol *y = v->root;
          if (bav_is_constant_variable (v, DL->x))
            {
              ba0_int_p j;
              if (bav_is_subscripted_symbol (y))
                {
                  j = ba0_get_dictionary (&U.dict_R, (struct ba0_table *) &U.R,
                      (void *) y->index_in_rigs);
                  if (j != BA0_NOT_AN_INDEX)
                    {
                      ba0_int_p s = bav_subscript_of_symbol (y);
                      if (s > sigma->tab[j])
                        sigma->tab[j] = s;
                    }
                }
              if (!bad_is_leader_of_regchain (v, &DL->C, (ba0_int_p *) 0))
                {
                  j = bav_get_dictionary_variable (&dict, &vars, v);
                  if (j == BA0_NOT_AN_INDEX)
                    {
                      if (vars.size == vars.alloc)
                        {
                          int new_alloc = 2 * vars.alloc + 1;
                          ba0_realloc_table ((struct ba0_table *) &vars,
                              new_alloc);
                        }
                      vars.tab[vars.size] = v;
                      vars.size += 1;
                      bav_add_dictionary_variable (&dict, &vars, v,
                          vars.size - 1);
                    }
                }
            }
        }
    }

  ba0_pull_stack ();
  ba0_set_table ((struct ba0_table *) omega, (struct ba0_table *) &vars);
  ba0_restore (&M);
}

/*
 * texinfo: bas_series_coefficients_DLuple
 * Assign to @var{T} the normal forms of the coefficients of the
 * series defined by @var{DL}.
 * The @math{i}th entry of @var{T} corresponds to the the @math{i}th entry 
 * @code{y} of the field @code{Y} of @var{DL}. It contains the normal
 * forms of @code{y[0], y[1], y[2]/2, ..., y[n]/n!} where @math{n} denotes the
 * maximum of the subscripts of the @code{y[i]}, occurring in the
 * field @code{C} of @var{DL}.
 */

BAS_DLL void
bas_series_coefficients_DLuple (
    struct baz_tableof_tableof_ratfrac *T,
    struct bas_DLuple *DL)
{
  struct baz_point_ratfrac point;
  struct bap_polynom_mpz poly;
  struct bav_tableof_variable omega;
  struct bav_tableof_variable derivatives;
  struct ba0_tableof_int_p sigma;
  ba0_mpq_t factorial, one_over_factorial;
  struct ba0_mark M;
  ba0_int_p i;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_init_table ((struct ba0_table *) &sigma);
  ba0_init_table ((struct ba0_table *) &omega);
  bas_constant_variables_DLuple (&sigma, &omega, DL);
  ba0_init_table ((struct ba0_table *) &derivatives);
  ba0_init_point ((struct ba0_point *) &point);
  bap_init_polynom_mpz (&poly);
  ba0_mpq_init (factorial);
  ba0_mpq_init (one_over_factorial);
  ba0_pull_stack ();

  ba0_realloc2_table ((struct ba0_table *) T, sigma.size,
      (ba0_new_function *) & ba0_new_table);
  T->size = sigma.size;

  for (i = 0; i < sigma.size; i++)
    {
      if (sigma.tab[i] != BAS_NOT_A_NUMBER)
        {
          struct bav_variable *v;
          ba0_int_p j;

          ba0_push_another_stack ();

          ba0_realloc_table ((struct ba0_table *) &derivatives,
              sigma.tab[i] + 1);

          v = bav_symbol_to_variable (DL->Y.tab[i]);
          derivatives.tab[0] = v;

          for (j = 1; j <= sigma.tab[i]; j++)
            derivatives.tab[j] =
                bav_diff_variable (derivatives.tab[j - 1], DL->x);
          derivatives.size = sigma.tab[i] + 1;

          for (j = 0; j < derivatives.size; j++)
            baz_prolongate_point_ratfrac_using_pattern_variable (&point, &point,
                &DL->Ybar, derivatives.tab[j]);

          ba0_pull_stack ();

          ba0_realloc2_table ((struct ba0_table *) T->tab[i], sigma.tab[i] + 1,
              (ba0_new_function *) & baz_new_ratfrac);

          ba0_reset_table ((struct ba0_table *) T->tab[i]);

          for (j = 0; j < derivatives.size; j++)
            {
              struct baz_tableof_ratfrac *U = T->tab[i];

              ba0_push_another_stack ();
              bap_set_polynom_variable_mpz (&poly, derivatives.tab[j], 1);

              if (j == 0)
                ba0_mpq_set_si (factorial, 1);
              else if (j > 1)
                ba0_mpq_mul_si (factorial, factorial, j);
              ba0_mpq_invert (one_over_factorial, factorial);

              ba0_pull_stack ();

              baz_eval_to_ratfrac_at_point_ratfrac_polynom_mpz (U->tab[j],
                  &poly, &point);

              bad_normal_form_ratfrac_mod_regchain (U->tab[j], U->tab[j],
                  &DL->C, (struct bap_polynom_mpz **) 0);

              baz_mul_ratfrac_numeric_mpq (U->tab[j], U->tab[j],
                  one_over_factorial);

              U->size += 1;
            }
        }
    }

  ba0_restore (&M);
}

/*
 * texinfo: bas_scanf_DLuple
 * The general parsing function for DLuples.
 * It can be called through @code{ba0_scanf/%DLuple}.
 */

BAS_DLL void *
bas_scanf_DLuple (
    void *DL0)
{
  struct bas_DLuple *DL;

  if (DL0 == (void *) 0)
    DL = bas_new_DLuple ();
  else
    DL = (struct bas_DLuple *) DL0;

  ba0_scanf ("DLuple (Y = %t[%y], "
      "Ybar = %prolongation_pattern, "
      "x = %y, "
      "order = %t[%d], "
      "kappa = %t[%d], "
      "C = %regchain, "
      "S = %l[%Az], "
      "k = %t[%d], "
      "r = %t[%d], "
      "q = %v, "
      "A = %t[%Qz], "
      "gamma = %t[%d], "
      "mu    = %t[%d], "
      "sigma = %t[%d], "
      "beta  = %t[%d], "
      "delta = %t[%d])",
      &DL->Y, &DL->Ybar, &DL->x, &DL->order, &DL->kappa, &DL->C, &DL->S,
      &DL->k, &DL->r, &DL->q, &DL->A, &DL->gamma, &DL->mu, &DL->sigma,
      &DL->beta, &DL->delta);

  return DL;
}

/*
 * texinfo: bas_printf_DLuple
 * The general printing function for DLuples.
 * It can be called through @code{ba0_printf/%DLuple}.
 */

BAS_DLL void
bas_printf_DLuple (
    void *DL0)
{
  struct bas_DLuple *DL = (struct bas_DLuple *) DL0;
  ba0_printf
      ("DLuple (Y = %t[%y], "
      "Ybar = %prolongation_pattern, "
      "x = %y, "
      "order = %t[%d], "
      "kappa = %t[%d], "
      "C = %regchain, "
      "S = %l[%Az], "
      "k = %t[%d], "
      "r = %t[%d], "
      "q = %v, "
      "A = %t[%Qz], "
      "gamma = %t[%d], "
      "mu = %t[%d], "
      "sigma = %t[%d], "
      "beta = %t[%d], "
      "delta = %t[%d])",
      &DL->Y, &DL->Ybar, DL->x, &DL->order, &DL->kappa, &DL->C, DL->S,
      &DL->k, &DL->r, DL->q, &DL->A, &DL->gamma, &DL->mu, &DL->sigma,
      &DL->beta, &DL->delta);
}

/*
 * texinfo: bas_printf_stripped_DLuple
 * A printing function for DLuples called by the @code{bmi} library.
 * The regular chain field of the DLuple is not printed.
 * It can be called through @code{ba0_printf/%stripped_DLuple}.
 */

BAS_DLL void
bas_printf_stripped_DLuple (
    void *DL0)
{
  struct bas_DLuple *DL = (struct bas_DLuple *) DL0;
  ba0_printf
      ("[%t[%y], "
      "%prolongation_pattern, "
      "%y, "
      "%t[%d], "
      "%t[%d], "
      "%l[%Az], "
      "%t[%d], "
      "%t[%d], "
      "%v, "
      "%t[%Qz], "
      "%t[%d], "
      "%t[%d], "
      "%t[%d], "
      "%t[%d], "
      "%t[%d]]",
      &DL->Y, &DL->Ybar, DL->x, &DL->order, &DL->kappa, DL->S,
      &DL->k, &DL->r, DL->q, &DL->A, &DL->gamma, &DL->mu, &DL->sigma,
      &DL->beta, &DL->delta);
}
