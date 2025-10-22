#include "bad_quench_regchain.h"
#include "bad_reduction.h"
#include "bad_regularize.h"
#include "bad_low_power_theorem.h"
#include "bad_global.h"

/*
 * SETTINGS
 */

/*
 * texinfo: bad_set_settings_preparation
 * Define as @var{zstring} the format which is used for printing the
 * @math{z_i}. If this parameter is zero, the format is restored
 * to its default value: @code{z%d}.
 */

BAD_DLL void
bad_set_settings_preparation (
    char *zstring)
{
  bad_initialized_global.preparation.zstring = zstring ? zstring : BAD_ZSTRING;
}

/*
 * texinfo: bad_get_settings_preparation
 * Assign to @var{zstring} the current
 * format identifier used for printing the @math{z_i}.
 * The argument may be zero.
 */

BAD_DLL void
bad_get_settings_preparation (
    char **zstring)
{
  if (zstring)
    *zstring = bad_initialized_global.preparation.zstring;
}

/*
 * PREPARATION TERMS
 */

/*
 * Initialized to the term 1
 */

static void
bad_init_preparation_term (
    struct bad_preparation_term *T)
{
  ba0_init_table ((struct ba0_table *) &T->z);
  ba0_init_table ((struct ba0_table *) &T->theta);
  ba0_init_table ((struct ba0_table *) &T->deg);
}

static struct bad_preparation_term *
bad_new_preparation_term (
    void)
{
  struct bad_preparation_term *T;

  T = (struct bad_preparation_term *) ba0_alloc (sizeof (struct
          bad_preparation_term));
  bad_init_preparation_term (T);
  return T;
}

static void
bad_realloc_preparation_term (
    struct bad_preparation_term *T,
    ba0_int_p n)
{
  if (T->theta.alloc < n)
    {
      ba0_realloc_table ((struct ba0_table *) &T->z, n);
      ba0_realloc2_table ((struct ba0_table *) &T->theta, n,
          (ba0_new_function *) & bav_new_term);
      ba0_realloc_table ((struct ba0_table *) &T->deg, n);
    }
}

static void
bad_set_preparation_term_one (
    struct bad_preparation_term *T)
{
  ba0_reset_table ((struct ba0_table *) &T->z);
  ba0_reset_table ((struct ba0_table *) &T->theta);
  ba0_reset_table ((struct ba0_table *) &T->deg);
}

static void
bad_set_preparation_term (
    struct bad_preparation_term *T,
    struct bad_preparation_term *U)
{
  ba0_int_p i;

  if (T != U)
    {
      bad_realloc_preparation_term (T, U->z.size);
      ba0_set_table ((struct ba0_table *) &T->z, (struct ba0_table *) &U->z);
      ba0_reset_table ((struct ba0_table *) &T->theta);
      for (i = 0; i < U->theta.size; i++)
        {
          bav_set_term (T->theta.tab[T->theta.size], U->theta.tab[i]);
          T->theta.size += 1;
        }
      ba0_set_table ((struct ba0_table *) &T->deg,
          (struct ba0_table *) &U->deg);
    }
}

/*
 * If a term involves a zi corresponding to a base field equation then
 * its degree is +infinity, so that it gets moved to the end of the
 * preparation equation.
 */

static bav_Idegree
bad_degree_preparation_term (
    struct bad_preparation_term *T,
    struct bad_base_field *K)
{
  bav_Idegree d;
  ba0_int_p i, n;

  n = K->relations.decision_system.size;
  d = 0;
  for (i = 0; i < T->deg.size && d != BA0_MAX_INT_P; i++)
    {
      if (T->z.tab[i] >= n)
        d += T->deg.tab[i];
      else
        d = BA0_MAX_INT_P;
    }
  return d;
}

static void
bad_printf_preparation_term (
    struct bad_preparation_term *T)
{
  struct bav_rank rg;
  struct bav_variable *v, *fakevar;
  struct bav_symbol *fakesym;
  bool first;
  struct ba0_mark M;
  ba0_int_p i;
  ba0_scanf_function *scanf_symbol;
  ba0_printf_function *printf_symbol;
  char *indexed_string;
  static char buffer[BA0_BUFSIZE];

  ba0_record (&M);

  if (T->z.size == 0)
    {
      ba0_printf ("1");
      return;
    }
/*
 * v = any dependent variable
 */
  i = 0;
  while (i < bav_global.R.vars.size &&
      bav_symbol_type_variable (bav_global.R.vars.tab[i]) !=
      bav_dependent_symbol)
    i += 1;
  if (i == bav_global.R.vars.size)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);
  v = bav_global.R.vars.tab[i];
/*
 * The idea consists in building a fake variable (from v) by replacing
 * the identifier of v by some zi. In order to benefit from the
 * variable printing functions (which may be customized by the user).
 */
  fakesym = ba0_alloc (sizeof (struct bav_symbol));
  memcpy (fakesym, v->root, sizeof (struct bav_symbol));
  fakesym->ident = buffer;
  fakevar = ba0_alloc (sizeof (struct bav_variable));
/*
 * The bav_printf_numbered_symbol makes no sense in this context.
 * If it is the symbol printing function, switch to the default one.
 */
  bav_get_settings_symbol (&scanf_symbol, &printf_symbol, &indexed_string);
  if (printf_symbol == &bav_printf_numbered_symbol)
    bav_set_settings_symbol (scanf_symbol, &bav_printf_default_symbol,
        indexed_string);
/*
 * Print a term
 */
  first = true;
  for (i = 0; i < T->z.size; i++)
    {
/*
 * The identifier becomes zi
 */
      ba0_sprintf (buffer, bad_initialized_global.preparation.zstring,
          T->z.tab[i] + 1);

      if (!first)
        ba0_printf ("*");
      first = false;
/*
 * Recover the derivation operator by differentiating v
 */
      v = bav_order_zero_variable (v);
      v = bav_diff2_variable (v, T->theta.tab[i]);
      memcpy (fakevar, v, sizeof (struct bav_variable));
      fakevar->root = fakesym;
/*
 * Build the rank
 */
      rg.var = fakevar;
      rg.deg = T->deg.tab[i];
/*
 * Print it. 
 */
      ba0_printf ("%rank", &rg);
    }
/*
 * Restore
 */
  bav_set_settings_symbol (scanf_symbol, printf_symbol, indexed_string);
  ba0_restore (&M);
}

static void
bad_eval_preparation_term (
    struct bap_polynom_mpz *R,
    struct bad_preparation_term *T,
    struct bad_base_field *K,
    struct bad_regchain *A)
{
  struct bap_polynom_mpz S1, S2;
  struct ba0_mark M;
  ba0_int_p i;

  ba0_push_another_stack ();
  ba0_record (&M);

  bap_init_polynom_mpz (&S1);
  bap_init_polynom_mpz (&S2);

  bap_set_polynom_one_mpz (&S1);
  for (i = 0; i < T->z.size; i++)
    {
      bap_diff2_polynom_mpz (&S2, A->decision_system.tab[T->z.tab[i]],
          T->theta.tab[i]);
      bap_pow_polynom_mpz (&S2, &S2, T->deg.tab[i]);
      bap_mul_polynom_mpz (&S1, &S1, &S2);
    }
  ba0_pull_stack ();
  bap_set_polynom_mpz (R, &S1);
  ba0_restore (&M);
}

/*
 * Multiplication by (theta z)**d
 */

static void
bad_mul_preparation_term_theta_z (
    struct bad_preparation_term *T,
    struct bad_preparation_term *U,
    struct bav_term *theta,
    ba0_int_p z,
    bav_Idegree d)
{
  ba0_int_p i;
  bool found;

  if (T != U)
    bad_set_preparation_term (T, U);

  i = 0;
  found = false;
  while (i < T->theta.size && !found)
    {
      if (T->z.tab[i] == z && bav_equal_term (T->theta.tab[i], theta))
        found = true;
      else
        i += 1;
    }
  if (found)
    T->deg.tab[i] += d;
  else
    {
      bad_realloc_preparation_term (T, T->theta.size + 1);

      T->z.tab[T->z.size] = z;
      bav_set_term (T->theta.tab[T->theta.size], theta);
      T->deg.tab[T->deg.size] = d;

      T->z.size += 1;
      T->theta.size += 1;
      T->deg.size += 1;
    }
}

/*
 * T = U * V
 */

static void
bad_mul_preparation_term (
    struct bad_preparation_term *T,
    struct bad_preparation_term *U,
    struct bad_preparation_term *V)
{
  struct bad_preparation_term R;
  ba0_int_p i;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  bad_init_preparation_term (&R);
  bad_set_preparation_term (&R, U);
  for (i = 0; i < V->z.size; i++)
    bad_mul_preparation_term_theta_z (&R, &R, V->theta.tab[i], V->z.tab[i],
        V->deg.tab[i]);
  ba0_pull_stack ();
  bad_set_preparation_term (T, &R);
  ba0_restore (&M);
}

/*
 * PREPARATION EQUATIONS
 */

/*
 * texinfo: bad_init_preparation_equation
 * Initialize @var{E}.
 */

BAD_DLL void
bad_init_preparation_equation (
    struct bad_preparation_equation *E)
{
  bap_init_product_mpz (&E->H);
  ba0_init_table ((struct ba0_table *) &E->coeffs);
  ba0_init_table ((struct ba0_table *) &E->terms);

  E->F = (struct bap_polynom_mpz *) 0;
  E->A = (struct bad_regchain *) 0;
  E->K = (struct bad_base_field *) 0;
}

/*
 * texinfo: bad_new_preparation_equation
 * Allocate a new preparation equation, initialize it and return it.
 */

BAD_DLL struct bad_preparation_equation *
bad_new_preparation_equation (
    void)
{
  struct bad_preparation_equation *E;

  E = (struct bad_preparation_equation *) ba0_alloc (sizeof (struct
          bad_preparation_equation));
  bad_init_preparation_equation (E);
  return E;
}

static void
bad_realloc_preparation_equation (
    struct bad_preparation_equation *P,
    ba0_int_p n)
{
  ba0_realloc2_table ((struct ba0_table *) &P->coeffs, n,
      (ba0_new_function *) & bap_new_polynom_mpz);
  ba0_realloc2_table ((struct ba0_table *) &P->terms, n,
      (ba0_new_function *) & bad_new_preparation_term);
}

/*
 * texinfo: bad_printf_preparation_equation
 * The printing function for preparation equations.
 * It is called by @code{ba0_printf/%preparation_equation}.
 */

BAD_DLL void
bad_printf_preparation_equation (
    void *A)
{
  struct bad_preparation_equation *E = (struct bad_preparation_equation *) A;
  ba0_int_p i;
  bool first;

  if (E->F == (struct bap_polynom_mpz *) 0)
    return;

  if (E->denom)
    ba0_printf ("%Pz * (1/%z)*(%Az) = ", &E->H, E->denom, E->F);
  else
    ba0_printf ("%Pz * (%Az) = ", &E->H, E->F);
  if (E->coeffs.size == 0)
    ba0_printf ("0");
  else
    {
      first = true;
      for (i = 0; i < E->coeffs.size; i++)
        {
          if (!first)
            ba0_printf (" + ");
          first = false;
          if (E->denom)
            ba0_printf ("(1/%z)*(%Az)*", E->denom, E->coeffs.tab[i]);
          else
            ba0_printf ("(%Az)*", E->coeffs.tab[i]);
          bad_printf_preparation_term (E->terms.tab[i]);
        }
    }
}

BAD_DLL void
bad_check_preparation_equation (
    struct bad_preparation_equation *E)
{
  struct bap_polynom_mpz lhs, rhs, R;
  struct ba0_mark M;
  ba0_int_p i;

  ba0_record (&M);

  bap_init_polynom_mpz (&lhs);
  bap_init_polynom_mpz (&rhs);

  bap_expand_product_mpz (&lhs, &E->H);
  bap_mul_polynom_mpz (&lhs, &lhs, E->F);

  bap_init_polynom_mpz (&R);
  for (i = 0; i < E->coeffs.size; i++)
    {
      bad_eval_preparation_term (&R, E->terms.tab[i], E->K, E->A);
      bap_mul_polynom_mpz (&R, &R, E->coeffs.tab[i]);
      bap_add_polynom_mpz (&rhs, &rhs, &R);
    }

  if (!bap_equal_polynom_mpz (&lhs, &rhs))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_restore (&M);
}

static void bad_set_preparation_equation_polynom2 (
    struct bad_preparation_equation *E,
    struct bap_polynom_mpz *F,
    ba0_mpz_t denom,
    struct bad_regchain *A,
    struct bad_base_field *K);

/*
 * We have
 *
 * (E)    H * F = sum coeffs [i] * terms [i]
 *
 * moreover
 *
 * coeffs [k] is reducible by A [z] at rank rg
 *
 * One wants to reduce coeffs [k]. One computes:
 *
 * Hk * coeffs [k] = Q * theta A [z] + R
 *
 * (Eq)   Hq * Q = sum coeffs_q [l] * terms_q [l]
 *
 * Multiply (E) by Hk * Hq. One gets:
 *
 * Hk * Hq * F = sum {i != k} Hk * Hq * coeffs [i] * terms [i]
 *             + Hq * Hk * coeffs [k] * terms [k]
 *
 *             = sum {i != k} Hk * Hq * coeffs [i] * terms [i]
 *             + Hq * Q * theta A [z] * terms [k]
 *             + Hq * R * terms [k]
 *
 *             = sum {i != k} Hk * Hq * coeffs [i] * terms [i]
 *             + sum coeffs_q [l] * (terms_q [l] * theta A [z] * terms [k])
 *             + Hq * R * terms [k]
 */

static void
bad_reduce_preparation_equation (
    struct bad_preparation_equation *E,
    ba0_int_p k,
    ba0_int_p z,
    struct bav_rank *rg)
{
  struct bap_tableof_polynom_mpz *A;
  struct bad_preparation_equation Eq;
  struct bap_polynom_mpz coeffk, B, Q, R, init, Hqexp;
  struct bap_polynom_mpz *Hk;
  struct bad_preparation_term termk;
  struct bav_term theta;
  struct bav_rank rg_z;
  bav_Idegree e;
  ba0_int_p i;
  struct ba0_mark M;

#define RG_DEBUG
#undef RG_DEBUG
#if defined (RG_DEBUG)
  static int counter = 0;
  ba0_printf
      ("INPUT BAD_REDUCE_PREPARATION_EQUATION (%d):\n%preparation_equation, k = %d, z = %d, rg = %rank\n\n",
      counter++, E, k, z, rg);
  bad_check_preparation_equation (E);
#endif

  A = &E->A->decision_system;

  ba0_push_another_stack ();
  ba0_record (&M);

  bad_init_preparation_equation (&Eq);
  bap_init_polynom_mpz (&coeffk);
  bad_init_preparation_term (&termk);
  bap_init_polynom_mpz (&B);
  bap_init_polynom_mpz (&Q);
  bap_init_polynom_mpz (&R);
  bap_init_polynom_mpz (&Hqexp);
  bav_init_term (&theta);

  bap_set_polynom_mpz (&coeffk, E->coeffs.tab[k]);
  bad_set_preparation_term (&termk, E->terms.tab[k]);
/*
 * Perform the pseudo division of coeffk by theta A[z]
 */
  rg_z = bap_rank_polynom_mpz (A->tab[z]);
  bav_operator_between_derivatives (&theta, rg->var, rg_z.var);

  bap_diff2_polynom_mpz (&B, A->tab[z], &theta);
  bap_pseudo_division_polynom_mpz (&Q, &R, &e, &coeffk, &B, rg->var);

  if (bap_is_zero_polynom_mpz (&Q))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  Hk = bap_new_polynom_mpz ();
  if (bav_is_one_term (&theta))
    {
      bap_init_readonly_polynom_mpz (&init);
      bap_initial_polynom_mpz (&init, A->tab[z]);
      bap_pow_polynom_mpz (Hk, &init, e);
    }
  else
    {
      bap_separant_polynom_mpz (Hk, A->tab[z]);
      bap_pow_polynom_mpz (Hk, Hk, e);
    }
/*
 * Compute the preparation equation for the quotient Q
 */
  bad_set_preparation_equation_polynom2 (&Eq, &Q, (ba0__mpz_struct *) 0, E->A,
      E->K);
  bap_expand_product_mpz (&Hqexp, &Eq.H);
/*
 * Incorporation in (E)
 */
  ba0_pull_stack ();
/*
 * step 1: delete the kth entry of E.
 */
  ba0_delete_table ((struct ba0_table *) &E->coeffs, k);
  ba0_delete_table ((struct ba0_table *) &E->terms, k);
  bad_realloc_preparation_equation (E, E->coeffs.size + Eq.coeffs.size + 1);
/* 
 * step 2: H and the coeffs [i] (i != k) are multiplied by Hk * Hq
 */
  bap_mul_product_mpz (&E->H, &E->H, &Eq.H);
  bap_mul_product_polynom_mpz (&E->H, &E->H, Hk, 1);
  for (i = 0; i < E->coeffs.size; i++)
    {
      bap_mul_polynom_mpz (E->coeffs.tab[i], E->coeffs.tab[i], &Hqexp);
      bap_mul_polynom_mpz (E->coeffs.tab[i], E->coeffs.tab[i], Hk);
    }
/*
 * step 3: add (sum coeffs_q [l]* terms_q [l]) * termk * theta z
 */
  for (i = 0; i < Eq.coeffs.size; i++)
    {
      bap_set_polynom_mpz (E->coeffs.tab[E->coeffs.size], Eq.coeffs.tab[i]);
      bad_mul_preparation_term (E->terms.tab[E->terms.size], Eq.terms.tab[i],
          &termk);
      bad_mul_preparation_term_theta_z (E->terms.tab[E->terms.size],
          E->terms.tab[E->terms.size], &theta, z, 1);
      E->coeffs.size += 1;
      E->terms.size += 1;
    }
/*
 * step 4: add Hq * R * termk to E provided that R is non zero
 */
  if (!bap_is_zero_polynom_mpz (&R))
    {
      bap_mul_polynom_mpz (E->coeffs.tab[E->coeffs.size], &R, &Hqexp);
      bad_set_preparation_term (E->terms.tab[E->terms.size], &termk);
      E->coeffs.size += 1;
      E->terms.size += 1;
    }

#if defined (RG_DEBUG)
  ba0_printf
      ("OUTPUT BAD_REDUCE_PREPARATION_EQUATION (%d):\n%preparation_equation, k = %d, z = %d, rg = %rank\n",
      --counter, E, k, z, rg);
  bad_check_preparation_equation (E);
#endif
  ba0_restore (&M);
}

/*
 * Compute most of a preparation equation for F and stores it in E since
 * the coeffs [i] are not guaranteed to be regular with respect to A.
 */

static void
bad_set_preparation_equation_polynom2 (
    struct bad_preparation_equation *E,
    struct bap_polynom_mpz *F,
    ba0_mpz_t denom,
    struct bad_regchain *A,
    struct bad_base_field *K)
{
  struct bav_rank rg;
  ba0_int_p i, z;
  bool modified;
/*
 * Initialize (E) to 1 * F = F * 1
 */
  E->F = F;
  E->denom = denom;
  E->A = A;
  E->K = K;

  bap_set_product_one_mpz (&E->H);
  bad_realloc_preparation_equation (E, 1);
  bap_set_polynom_mpz (E->coeffs.tab[0], F);
  bad_set_preparation_term_one (E->terms.tab[0]);
  E->coeffs.size = 1;
  E->terms.size = 1;
/*
 * Reduce
 */
  do
    {
      modified = false;
      i = 0;
      while (i < E->coeffs.size && !modified)
        {
/*
 * First perform the reductions by the base field equations
 */
          if (bad_is_a_reducible_polynom_by_regchain (E->coeffs.tab[i],
                  &K->relations, bad_full_reduction,
                  bad_all_derivatives_to_reduce, &rg, &z))
            {
              bad_reduce_preparation_equation (E, i, z, &rg);
              modified = true;
/* 
 * Then perform the reductions by the other equations
 */
            }
          else if (bad_is_a_reducible_polynom_by_regchain (E->coeffs.tab[i], A,
                  bad_full_reduction, bad_all_derivatives_to_reduce, &rg, &z))
            {
              bad_reduce_preparation_equation (E, i, z, &rg);
/*
                ba0_printf ("%preparation_equation\n", E);
                bad_check_preparation_equation (E);
 */
              modified = true;
            }
          else
            i += 1;
        }
    }
  while (modified);
}

/*
 * texinfo: bad_set_preparation_equation_polynom
 * Assign to @var{E} a preparation equation for @var{F}/@var{denom} and @var{A}.
 * The regularity test on the coefficients @math{c_i} may raise an
 * exception. The zero divisor is then recovered in @var{ddz}.
 * The parameter @var{K} provides the base field and indicates 
 * the elements of @var{A} which must be considered as base field equations.
 */

BAD_DLL void
bad_set_preparation_equation_polynom (
    struct bad_preparation_equation *E,
    struct bap_polynom_mpz *F,
    ba0_mpz_t denom,
    struct bad_regchain *A,
    struct bad_base_field *K,
    struct bap_polynom_mpz * *ddz)
{
  ba0_int_p i, j;
  bav_Idegree di, dj;
  bool swap;

  if (K->relations.decision_system.size > A->decision_system.size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  bad_set_preparation_equation_polynom2 (E, F, denom, A, K);
/*
 * Special case
 */
  if (bap_is_zero_polynom_mpz (F))
    {
      E->coeffs.size = 0;
      E->terms.size = 0;
      return;
    }
/*
 * Terms are sorted by increasing degree
 */
  do
    {
      swap = false;
      for (i = 0; i < E->terms.size - 1; i++)
        {
          di = bad_degree_preparation_term (E->terms.tab[i], K);
          j = i + 1;
          dj = bad_degree_preparation_term (E->terms.tab[j], K);
          if (dj < di)
            {
              BA0_SWAP (struct bad_preparation_term *,
                  E->terms.tab[i],
                  E->terms.tab[j]);
              BA0_SWAP (struct bap_polynom_mpz *,
                  E->coeffs.tab[i],
                  E->coeffs.tab[j]);
              swap = true;
            }
        }
    }
  while (swap);
/*
 * Regularity testing. May raise an exception.
 */
  for (i = 0; i < E->coeffs.size; i++)
    bad_check_regularity_polynom_mod_regchain (E->coeffs.tab[i], A, K, ddz);
}

/*
 * texinfo: bad_preparation_congruence
 * Assign to @var{q} the minimum total degree of the power products of 
 * derivatives of the @math{z_i} which occur in @var{E}. 
 * Assign to @var{l} the number of such terms which have degree @var{q}. 
 * Observe that these @var{l} monomials occur at the first place of the 
 * tables of @var{E}.
 * Terms which involve derivatives of @math{z_i} corresponding to base
 * field equations cannot be part of the congruence.
 */

BAD_DLL void
bad_preparation_congruence (
    ba0_int_p *l,
    bav_Idegree *q,
    struct bad_preparation_equation *E)
{
  bav_Idegree d;
  ba0_int_p i;

  if (E->terms.size == 0)
    {
      *l = 0;
      *q = 0;
    }
  else
    {
      d = bad_degree_preparation_term (E->terms.tab[0], E->K);
      if (d == BA0_MAX_INT_P)
        {
          *l = 0;
          *q = 0;
        }
      else
        {
          i = 1;
          while (i < E->terms.size
              && bad_degree_preparation_term (E->terms.tab[i], E->K) == d)
            i += 1;
          *q = d;
          *l = i;
        }
    }
}

/*
 * texinfo: bad_low_power_theorem_condition_to_be_a_component
 * Return @code{true} if the preparation equation (congruence) @var{E}
 * satisfies the necessary and sufficient condition provided in the Low
 * Power Theorem (Kolchin, IV, 15, Theorem 6) for @var{A} to be
 * an irredundant component of the representation of the 
 * radical of the differential ideal generated by @var{F} as an 
 * intersection of regular differential chains.
 * 
 * Observe that the function does not check the fact that @var{A} only
 * consists of one element i.e. that @var{A} = @math{A_1}. This condition
 * is not checked here in order to permit the application of the
 * Low Power Theorem to differential polynomials with coefficients
 * taken in some nontrivial base field.
 */

BAD_DLL bool
bad_low_power_theorem_condition_to_be_a_component (
    struct bad_preparation_equation *E)
{
  struct bad_preparation_term *T;
  bav_Idegree q;
  ba0_int_p l;

  bad_preparation_congruence (&l, &q, E);
  if (l != 1 || q == 0)
    return false;
  T = E->terms.tab[0];
  if (T->z.size != 1 || !bav_is_one_term (T->theta.tab[0]))
    return false;
  return true;
}

/*
 * texinfo: bad_low_power_theorem_simplify_intersectof_regchain
 * The intersection @var{T} is assumed to be produced by
 * @code{bad_Rosenfeld_Groebner} over a single differential polynomial @math{F},
 * with coefficients in the base field @var{K}. 
 * Remove from @var{T} the
 * redundant components of the radical of the differential ideal generated
 * by @var{F}, by applying the Low Power Theorem. 
 * The result is stored in @var{S}.
 * The result may involve components which are not in @var{T}.
 * It may even involve more components than @var{T}.
 */

BAD_DLL void
bad_low_power_theorem_simplify_intersectof_regchain (
    struct bad_intersectof_regchain *S0,
    struct bad_intersectof_regchain *T0,
    struct bad_base_field *K)
{
  struct bad_preparation_equation E;
  struct bad_intersectof_regchain S, T, aux;
  struct bad_regchain *general_component, *A;
  struct bap_polynom_mpz *F, *ddz;
  ba0_mpz_t denom;
  struct ba0_mark M;
  ba0_int_p i;

  if (T0->inter.size == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  general_component = T0->inter.tab[0];
  if (bad_number_of_elements_over_base_field_regchain (general_component, K)
      != 1)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  F = general_component->decision_system.tab
      [general_component->decision_system.size - 1];

  ba0_push_another_stack ();
  ba0_record (&M);

  bad_init_intersectof_regchain (&T);
  bad_set_intersectof_regchain (&T, T0);

  bad_init_intersectof_regchain (&S);
  bad_set_intersectof_regchain_regchain (&S, general_component);
  bad_init_intersectof_regchain (&aux);

  ba0_mpz_init_set_ui (denom, 1);
  for (i = 1; i < T.inter.size; i++)
    {
      A = T.inter.tab[i];
      if (bad_number_of_elements_over_base_field_regchain (A, K) == 1)
        {
          BA0_TRY
          {
            bad_init_preparation_equation (&E);
            bad_set_preparation_equation_polynom (&E, F, denom, A, K, &ddz);
            if (bad_low_power_theorem_condition_to_be_a_component (&E))
              bad_append_intersectof_regchain_regchain (&S, A);
          }
          BA0_CATCH
          {
            if (ba0_global.exception.raised != BAD_EXRDDZ)
              BA0_RE_RAISE_EXCEPTION;
            bad_set_intersectof_regchain_regchain (&aux, A);

            bad_handle_splitting_exceptions_regchain (&aux,
                (struct bad_quench_map *) 0, (struct bav_tableof_term *) 0,
                (bool *) 0, ddz, (struct bad_regchain *) 0, BAD_EXRDDZ, K);
            bad_append_intersectof_regchain (&T, &aux);
          }
          BA0_ENDTRY;
        }
    }

  ba0_pull_stack ();
  bad_set_intersectof_regchain (S0, &S);
  ba0_restore (&M);
}
