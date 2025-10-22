#include "baz_realroot_mpq.h"
#include "baz_gcd_polynom_mpz.h"

/*
 * Assign to bound a bound on the moduli of the complex roots of P
 *
 * bound = 1 + max |a_i|/|a_n| 
 */

static void
baz_Cauchy_bound_polynom_mpz (
    ba0_mpq_t bound,
    struct bap_polynom_mpz *P)
{
  ba0_mpz_t maxnorm;
  ba0_mpq_t maxratio;
  ba0_mpz_t *lc;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_mpz_init (maxnorm);
  bap_maxnorm_polynom_mpz (maxnorm, P);

  ba0_mpq_init (maxratio);

  lc = bap_numeric_initial_polynom_mpz (P);
  ba0_mpq_set_num (maxratio, maxnorm);
  ba0_mpq_set_den (maxratio, *lc);
  if (ba0_mpz_sgn (*lc) < 0)
    ba0_mpq_neg (maxratio, maxratio);
  ba0_mpq_canonicalize (maxratio);
  ba0_mpz_add (ba0_mpq_numref (maxratio), ba0_mpq_numref (maxratio),
      ba0_mpq_denref (maxratio));

  ba0_pull_stack ();

  ba0_mpq_set (bound, maxratio);

  ba0_restore (&M);
}

/*
 * Assign to Q the polynomial P (alpha*x + beta)
 *
 * P and Q may point to the same polynomial
 */

static void
baz_Taylor_shift_polynom_mpq (
    struct bap_polynom_mpq *Q,
    struct bap_polynom_mpq *P,
    ba0_mpq_t alpha,
    ba0_mpq_t beta)
{
  struct ba0_tableof_mpq T;
  struct bap_itermon_mpq iter;
  struct bap_creator_mpq crea;
  struct bav_term term;
  struct bav_variable *v;
  bav_Idegree n, i, j;
  ba0_mpq_t temp;
  struct ba0_mark M;

  v = bap_leader_polynom_mpq (P);
  n = bap_leading_degree_polynom_mpq (P);

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_init_table ((struct ba0_table *) &T);
  ba0_realloc2_table ((struct ba0_table *) &T, n + 1,
      (ba0_new_function *) & ba0_new_mpq);

  bav_init_term (&term);
  bap_begin_itermon_mpq (&iter, P);
  while (!bap_outof_itermon_mpq (&iter))
    {
      bap_term_itermon_mpq (&term, &iter);
      i = bav_degree_term (&term, v);
      ba0_mpq_set (T.tab[i], *bap_coeff_itermon_mpq (&iter));
      bap_next_itermon_mpq (&iter);
    }
  bap_close_itermon_mpq (&iter);

  T.size = n + 1;

  ba0_mpq_init (temp);
  for (i = n; i >= 0; i--)
    {
      for (j = i + 1; j <= n; j++)
        {
          ba0_mpq_mul (temp, beta, T.tab[j]);
          ba0_mpq_add (T.tab[j - 1], T.tab[j - 1], temp);
          ba0_mpq_mul (T.tab[j], T.tab[j], alpha);
        }
    }

  for (i = n; i >= 0; i--)
    ba0_mpq_canonicalize (T.tab[i]);

  bav_set_term_variable (&term, v, n);

  ba0_pull_stack ();

  bap_begin_creator_mpq (&crea, Q, &term, bap_exact_total_rank, n + 1);
  for (i = n; i >= 0; i--)
    {
      bav_set_term_variable (&term, v, i);
      bap_write_creator_mpq (&crea, &term, T.tab[i]);
    }
  bap_close_creator_mpq (&crea);

  ba0_restore (&M);
}

/*
 * Assign to Q the polynomial x**n * P(1/x)
 *
 * P and Q must point to different polynomials
 */

static void
baz_reciprocal_polynom_mpq (
    struct bap_polynom_mpq *Q,
    struct bap_polynom_mpq *P)
{
  struct bap_creator_mpq crea;
  struct bap_itermon_mpq iter;
  struct bav_term term;
  struct bav_variable *v;
  bav_Idegree n, i;
  struct ba0_mark M;

  if (P == Q)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  v = bap_leader_polynom_mpq (P);
  n = bap_leading_degree_polynom_mpq (P);

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&term);
  bav_set_term_variable (&term, v, n);

  ba0_pull_stack ();

  bap_begin_creator_mpq (&crea, Q, &term, bap_exact_total_rank, n + 1);

  bap_end_itermon_mpq (&iter, P);
  while (!bap_outof_itermon_mpq (&iter))
    {
      bap_term_itermon_mpq (&term, &iter);
      i = bav_degree_term (&term, v);
      bav_set_term_variable (&term, v, n - i);
      bap_write_creator_mpq (&crea, &term, *bap_coeff_itermon_mpq (&iter));
      bap_prev_itermon_mpq (&iter);
    }
  bap_close_itermon_mpq (&iter);
  bap_close_creator_mpq (&crea);

  ba0_restore (&M);
}

/*
 * Return the number of sign variations in the list of the
 * nonzero coefficients of P. This number provides a bound on
 * the number of positive roots of P (Descartes rule of signs).
 */

static ba0_int_p
baz_v_polynom_mpq (
    struct bap_polynom_mpq *P)
{
  struct bap_itermon_mpq iter;
  ba0_mpq_t *prev, *cour;
  ba0_int_p v;

  v = 0;
  bap_begin_itermon_mpq (&iter, P);
  cour = bap_coeff_itermon_mpq (&iter);
  bap_next_itermon_mpq (&iter);
  while (!bap_outof_itermon_mpq (&iter))
    {
      prev = cour;
      cour = bap_coeff_itermon_mpq (&iter);
      if (ba0_mpq_sgn (*prev) != ba0_mpq_sgn (*cour))
        v += 1;
      bap_next_itermon_mpq (&iter);
    }
  bap_close_itermon_mpq (&iter);
  return v;
}

/*
 * Apply Descartes rule over the interval ]0,1[.
 * The return number provides a bound on the number of roots of P
 * in this interval.
 */

static ba0_int_p
baz_v01_polynom_mpq (
    struct bap_polynom_mpq *P)
{
  struct bap_polynom_mpq Q;
  struct ba0_mark M;
  ba0_mpq_t one;
  ba0_int_p result;

  ba0_record (&M);
  ba0_mpq_init_set_si (one, 1);
  bap_init_polynom_mpq (&Q);
  baz_reciprocal_polynom_mpq (&Q, P);
  baz_Taylor_shift_polynom_mpq (&Q, &Q, one, one);
  result = baz_v_polynom_mpq (&Q);
  ba0_restore (&M);
  return result;
}

/*
 * Assign P(x) to y and P'(x) to yp
 * Both pointers y and yp may be zero
 */

static void
baz_eval_numeric_polynom_mpq (
    ba0_mpq_t y,
    ba0_mpq_t yp,
    struct bap_polynom_mpq *P,
    ba0_mpq_t x)
{
  struct bap_itermon_mpq iter;
  struct bav_term term;
  struct bav_variable *v;
  bav_Idegree i, j;
  ba0_mpq_t z, zp, tmp;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&term);
  if (yp)
    {
      ba0_mpq_init (zp);
      ba0_mpq_init (tmp);
    }
/*
 * # Horner scheme
 *
 * yp = 0   # yp = y'
 * y  = a[n]
 * for i = n-1, n-2, ..., 0
 *  yp = yp*x + y
 *  y  = y*x + a[i]
 *
 * in the loop below, exponents decrease not as regularly as above
 * so that we use two indices : 
 *  j = index of previous nonzero coeff and
 *  i = index of current nonzero coeff
 *
 * z qnd zp are temporary variables for y and yp
 */

  bap_begin_itermon_mpq (&iter, P);
  ba0_mpq_init_set (z, *bap_coeff_itermon_mpq (&iter));
  v = bap_leader_polynom_mpq (P);
  j = bap_leading_degree_polynom_mpq (P);

  bap_next_itermon_mpq (&iter);
  while (!bap_outof_itermon_mpq (&iter))
    {
      bap_term_itermon_mpq (&term, &iter);
      i = bav_degree_term (&term, v);
      if (yp)
        ba0_mpq_set (tmp, z);
      while (j != i)
        {
          if (yp)
            ba0_mpq_mul (zp, zp, x);
          ba0_mpq_mul (z, z, x);
          j -= 1;
        }
      if (yp)
        ba0_mpq_add (zp, zp, tmp);
      ba0_mpq_add (z, z, *bap_coeff_itermon_mpq (&iter));
      bap_next_itermon_mpq (&iter);
    }
  bap_close_itermon_mpq (&iter);
  if (yp)
    ba0_mpq_set (tmp, z);
  while (j > 0)
    {
      if (yp)
        ba0_mpq_mul (zp, zp, x);
      ba0_mpq_mul (z, z, x);
      j -= 1;
    }
  ba0_mpq_canonicalize (z);
  if (yp)
    {
      ba0_mpq_add (zp, zp, tmp);
      ba0_mpq_canonicalize (zp);
    }
  ba0_pull_stack ();
  if (y)
    ba0_mpq_set (y, z);
  if (yp)
    ba0_mpq_set (yp, zp);
  ba0_restore (&M);
}

/*
 * Refine the isolation interval ]a0, b0[ of P to an interval
 * of width less than epsilon. 
 *
 * If a0 < b0 then the resulting interval is open
 * If a0 = b0 then the resulting interval is closed
 *
 * The polynomial P is supposed to be squarefree
 */

static void
baz_refine_interval_polynom_mpq (
    ba0_mpq_t a0,
    ba0_mpq_t b0,
    ba0_mpq_t epsilon,
    struct bap_polynom_mpq *P)
{
  ba0_mpq_t a, b, one_half, tmp, m, P_at_a, P_at_m;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_mpq_init_set (a, a0);
  ba0_mpq_init_set (b, b0);
  ba0_mpq_init (one_half);
  ba0_mpq_set_si_si (one_half, 1, 2);
  ba0_mpq_init (tmp);
  ba0_mpq_init (m);
  ba0_mpq_init (P_at_a);
  ba0_mpq_init (P_at_m);
  baz_eval_numeric_polynom_mpq (P_at_a, (ba0__mpq_struct *) 0, P, a);
  if (ba0_mpq_sgn (P_at_a) == 0)
    baz_eval_numeric_polynom_mpq ((ba0__mpq_struct *) 0, P_at_a, P, a);
/*
 * P_at_a is nonzero since P is squarefree
 */
  ba0_mpq_sub (tmp, b, a);
  while (ba0_mpq_cmp (tmp, epsilon) > 0)
    {
      ba0_mpq_add (m, a, b);
      ba0_mpq_mul (m, m, one_half);
      ba0_mpq_canonicalize (m);
      baz_eval_numeric_polynom_mpq (P_at_m, (ba0__mpq_struct *) 0, P, m);
      if (ba0_mpq_sgn (P_at_m) == 0)
        {
          ba0_mpq_set (a, m);
          ba0_mpq_set (b, m);
        }
      else if (ba0_mpq_sgn (P_at_m) != ba0_mpq_sgn (P_at_a))
        ba0_mpq_set (b, m);
      else
        {
          ba0_mpq_set (a, m);
          ba0_mpq_set (P_at_a, P_at_m);
        }
      ba0_mpq_sub (tmp, b, a);
    }
  ba0_pull_stack ();
  ba0_mpq_set (a0, a);
  ba0_mpq_set (b0, b);
  ba0_restore (&M);
}

/*
 * Consider first the case: type = baz_isolation_interval.
 * Assign to T intervals which are either open or closed.
 * Open intervals are disjoint and have width less than epsilon.
 * Closed intervals contain a single rational number. 
 * Each interval isolates exactly one root of P0 in the range ]a, b[. 
 * Each root of P0 in this range is isolated in exactly one interval.
 * There is bijection between the roots alpha0 of P0 in ]a, b[ and the
 * roots alpha of P in ]0, 1[ given by : alpha0 = a + (b - a) * alpha
 *
 * Consider now the case: type = baz_any_interval.
 * Open intervals are disjoint and have width less than epsilon.
 * Each root of P0 in the range ]a, b[ is contained in some interval.
 * However, an open interval may not contain any root of P0 or contain
 * more than one root.
 *
 * The array T is supposed to be large enough to receive all the roots
 */

static void
baz_isolate01_polynom_mpq (
    struct ba0_tableof_interval_mpq *T,
    struct bap_polynom_mpq *P,
    ba0_mpq_t a,
    ba0_mpq_t b,
    enum baz_typeof_realroot_interval type,
    ba0_mpq_t epsilon,
    struct bap_polynom_mpq *P0)
{
  ba0_int_p n;

  if (type == baz_any_interval)
    {
      ba0_mpq_t temp;
      struct ba0_mark M;
      bool small_enough;

      ba0_record (&M);
      ba0_mpq_init (temp);
      ba0_mpq_sub (temp, b, a);
      small_enough = ba0_mpq_cmp (temp, epsilon) <= 0;
      ba0_restore (&M);

      if (small_enough)
        {
          ba0_set_interval_mpq_type_mpq (T->tab[T->size], ba0_open_interval, a,
              b);
          T->size += 1;
          return;
        }
    }

  n = baz_v01_polynom_mpq (P);
  if (n == 1)
    {
      baz_refine_interval_polynom_mpq (a, b, epsilon, P0);
      if (ba0_mpq_cmp (a, b) == 0)
        ba0_set_interval_mpq_type_mpq (T->tab[T->size], ba0_closed_interval, a,
            a);
      else
        ba0_set_interval_mpq_type_mpq (T->tab[T->size], ba0_open_interval, a,
            b);
      T->size += 1;
    }
  else if (n > 1)
    {
      struct bap_polynom_mpq Q;
      ba0_mpq_t one_half, zero, middle;
      struct ba0_mark M;

      ba0_push_another_stack ();
      ba0_record (&M);

      ba0_mpq_init (zero);
      ba0_mpq_init (one_half);
      ba0_mpq_init (middle);
      ba0_mpq_set_si_si (one_half, 1, 2);
      ba0_mpq_add (middle, a, b);
      ba0_mpq_mul (middle, middle, one_half);
      ba0_mpq_canonicalize (middle);

      bap_init_polynom_mpq (&Q);

      baz_Taylor_shift_polynom_mpq (&Q, P, one_half, zero);
      ba0_pull_stack ();

      baz_isolate01_polynom_mpq (T, &Q, a, middle, type, epsilon, P0);

      ba0_push_another_stack ();
      baz_eval_numeric_polynom_mpq (zero, (ba0__mpq_struct *) 0, P0, middle);
      ba0_pull_stack ();

      if (ba0_mpq_is_zero (zero))
        {
          ba0_set_interval_mpq_type_mpq (T->tab[T->size], ba0_closed_interval,
              middle, middle);
          T->size += 1;
        }

      ba0_push_another_stack ();
      baz_Taylor_shift_polynom_mpq (&Q, P, one_half, one_half);
      ba0_pull_stack ();

      baz_isolate01_polynom_mpq (T, &Q, middle, b, type, epsilon, P0);
      ba0_restore (&M);
    }
}

/*
 * Comparison function for qsort
 */

static int
baz_compare_interval_mpq (
    const void *X0,
    const void *Y0)
{
  struct ba0_interval_mpq *X = *(struct ba0_interval_mpq **) X0;
  struct ba0_interval_mpq *Y = *(struct ba0_interval_mpq **) Y0;

  if (ba0_is_less_interval_mpq (X, Y))
    return -1;
  else
    return 1;
}

/*
 * texinfo: baz_positive_roots_polynom_mpq
 * Consider first the case where @var{type} is @code{baz_isolation_interval}.
 * Append to @var{T} intervals which are either open or closed.
 * Open intervals are disjoint and have width less than @var{epsilon}.
 * Each closed interval contains a single rational number.
 * Each interval isolates exactly one positive root of @var{P0}.
 * Each positive root of @var{P0} is isolated in exactly one interval.
 *
 * Consider now the case where @var{type} is @code{baz_any_interval}.
 * Open intervals are disjoint and have width less than @var{epsilon}.
 * Each positive root of @var{P0} is contained in some interval.
 * However, an open interval may not contain any root of @var{P0} or contain
 * more than one root.
 *
 * The polynomial @var{P0} must be a univariate polynomial.
 *
 * The resulting table @var{T} is sorted by increasing order.
 */

BAZ_DLL void
baz_positive_roots_polynom_mpq (
    struct ba0_tableof_interval_mpq *T,
    struct bap_polynom_mpq *P0,
    enum baz_typeof_realroot_interval type,
    ba0_mpq_t epsilon)
{
  struct bap_product_mpz prod;
  struct bap_polynom_mpz P;
  struct bap_polynom_mpq Q, R;
  ba0_mpq_t bound, zero;
  ba0_int_p i, n;
  struct ba0_mark M;

  if (!bap_is_univariate_polynom_mpq (P0))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  if (bap_is_numeric_polynom_mpq (P0))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);

  bap_init_polynom_mpz (&P);
  bap_numer_polynom_mpq (&P, (ba0__mpz_struct *) 0, P0);
  bap_init_product_mpz (&prod);
  baz_squarefree_polynom_mpz (&prod, &P);

  n = 0;
  for (i = 0; i < prod.size; i++)
    n += bap_leading_degree_polynom_mpz (&prod.tab[i].factor);

  ba0_pull_stack ();
  ba0_realloc2_table ((struct ba0_table *) T, n,
      (ba0_new_function *) & ba0_new_interval_mpq);
  T->size = 0;
  ba0_push_another_stack ();

  bap_init_polynom_mpq (&Q);
  bap_init_polynom_mpq (&R);
  ba0_mpq_init (bound);
  ba0_mpq_init_set_ui (zero, 0);
  for (i = 0; i < prod.size; i++)
    {
      baz_Cauchy_bound_polynom_mpz (bound, &prod.tab[i].factor);
      bap_polynom_mpz_to_mpq (&R, &prod.tab[i].factor);
      baz_Taylor_shift_polynom_mpq (&Q, &R, bound, zero);
      ba0_pull_stack ();
      baz_isolate01_polynom_mpq (T, &Q, zero, bound, type, epsilon, &R);
      ba0_push_another_stack ();
    }

  ba0_pull_stack ();

  qsort (T->tab, T->size, sizeof (struct ba0_interval_mpq *),
      &baz_compare_interval_mpq);

  ba0_restore (&M);
}

/*
 * texinfo: baz_positive_integer_roots_polynom_mpq
 * Assign to @var{T} the positive integer roots of @var{P}, sorted
 * by increasing value.
 */

BAZ_DLL void
baz_positive_integer_roots_polynom_mpq (
    struct ba0_tableof_mpz *T,
    struct bap_polynom_mpq *P)
{
  struct ba0_tableof_interval_mpq U;
  ba0_mpq_t epsilon, quotient_q;
  ba0_mpz_t remainder, quotient;
  ba0_int_p i;
  struct ba0_mark M;

  if (!bap_is_univariate_polynom_mpq (P))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  if (bap_is_numeric_polynom_mpq (P))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_init_table ((struct ba0_table *) &U);
  ba0_mpq_init_set_si (epsilon, 1);
  baz_positive_roots_polynom_mpq (&U, P, baz_any_interval, epsilon);

  ba0_mpq_init (quotient_q);
  ba0_mpz_init (quotient);
  ba0_mpz_init (remainder);

  ba0_pull_stack ();
  ba0_realloc2_table ((struct ba0_table *) T, U.size,
      (ba0_new_function *) & ba0_new_mpz);
  T->size = 0;
  ba0_push_another_stack ();

  for (i = 0; i < U.size; i++)
    {
      if (ba0_is_closed_interval_mpq (U.tab[i]))
        {
          ba0_mpz_tdiv_qr (quotient, remainder, ba0_mpq_numref (U.tab[i]->a),
              ba0_mpq_denref (U.tab[i]->a));
          if (ba0_mpz_sgn (remainder) == 0)
            {
/*
 * A positive integer root is isolated
 */
              ba0_pull_stack ();
              ba0_mpz_set (T->tab[T->size], quotient);
              T->size += 1;
              ba0_push_another_stack ();
            }
        }
      else
        {
/*
 * The interval is open and its width is <= 1
 * The bounds cannot be roots.
 * Thus the only candidate is the at most one integer in the interval
 */
          ba0_mpz_tdiv_q (quotient, ba0_mpq_numref (U.tab[i]->a),
              ba0_mpq_denref (U.tab[i]->a));
          ba0_mpz_add_ui (quotient, quotient, 1);
          ba0_mpq_set_z (quotient_q, quotient);
          if (ba0_member_interval_mpq (quotient_q, U.tab[i]))
            {
              baz_eval_numeric_polynom_mpq (epsilon, (ba0__mpq_struct *) 0, P,
                  quotient_q);
              if (ba0_mpq_sgn (epsilon) == 0)
                {
                  ba0_pull_stack ();
                  ba0_mpz_set (T->tab[T->size], quotient);
                  T->size += 1;
                  ba0_push_another_stack ();
                }
            }
        }
    }

  ba0_pull_stack ();
  ba0_restore (&M);
}

/*
 * texinfo: baz_positive_integer_roots_polynom_mpz
 * Assign to @var{T} the positive integer roots of @var{P},
 * viewed as a univariate polynomial in @var{v}.
 * The polynomial @var{P} may depend on other variables than @var{v}.
 * If @var{v} is @code{BAV_NOT_A_VARIABLE}, it is supposed to
 * be the leader of @var{P}.
 * The roots are sorted by increasing value.
 */

BAZ_DLL void
baz_positive_integer_roots_polynom_mpz (
    struct ba0_tableof_mpz *T,
    struct bap_polynom_mpz *P,
    struct bav_variable *v)
{
  struct bap_polynom_mpq Q;
  struct bap_polynom_mpz Pbar;
  struct bav_variable *u;
  bav_Iordering r;
  ba0_int_p d;
  struct ba0_mark M;

  ba0_reset_table ((struct ba0_table *) T);

  if (v == BAV_NOT_A_VARIABLE)
    v = bap_leader_polynom_mpz (P);

  d = bap_degree_polynom_mpz (P, v);

  if (d < 1)
    return;

  ba0_push_another_stack ();
  ba0_record (&M);
/*
 * The variable v becomes the lowest variable
 */
  r = bav_R_copy_ordering (bav_current_ordering ());
  bav_push_ordering (r);
  bav_R_set_minimal_variable (v);

  bap_init_readonly_polynom_mpz (&Pbar);
  bap_sort_polynom_mpz (&Pbar, P);

  bap_init_polynom_mpq (&Q);

  u = bav_smallest_greater_variable (v);
  if (u == BAV_NOT_A_VARIABLE)
    bap_set_polynom_numer_denom_mpq (&Q, &Pbar, (ba0__mpz_struct *) 0);
  else
    {
      struct bap_tableof_polynom_mpz W;
      struct bap_itercoeff_mpz iter;
      struct bap_polynom_mpz gcd;
      struct bap_product_mpz gcd_prod;

      ba0_init_table ((struct ba0_table *) &W);
      bap_begin_itercoeff_mpz (&iter, &Pbar, u);
      while (!bap_outof_itercoeff_mpz (&iter))
        {
          if (W.size == W.alloc)
            {
              ba0_realloc2_table ((struct ba0_table *) &W, 2 * W.alloc + 1,
                  (ba0_new_function *) & bap_new_readonly_polynom_mpz);
            }
          bap_coeff_itercoeff_mpz (W.tab[W.size], &iter);
          W.size += 1;
          bap_next_itercoeff_mpz (&iter);
        }
      bap_close_itercoeff_mpz (&iter);
      bap_init_product_mpz (&gcd_prod);
      baz_gcd_tableof_polynom_mpz (&gcd_prod, &W, false);
      bap_init_polynom_mpz (&gcd);
      bap_expand_product_mpz (&gcd, &gcd_prod);
      bap_set_polynom_numer_denom_mpq (&Q, &gcd, (ba0__mpz_struct *) 0);
    }
/*
 * Compute the positive integer roots of Q
 */
  ba0_pull_stack ();
  if (bap_is_numeric_polynom_mpq (&Q))
    ba0_reset_table ((struct ba0_table *) T);
  else
    baz_positive_integer_roots_polynom_mpq (T, &Q);
  ba0_push_another_stack ();
/*
 * Remove the temporary ranking
 */
  bav_pull_ordering ();
  bav_R_free_ordering (r);
  ba0_pull_stack ();
  ba0_restore (&M);
}
