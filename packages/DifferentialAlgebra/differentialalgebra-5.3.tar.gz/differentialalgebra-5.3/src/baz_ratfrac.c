#include "baz_polyspec_mpz.h"
#include "baz_gcd_polynom_mpz.h"
#include "baz_ratfrac.h"

/*
 * Initializes R to zero.
 */

/*
 * texinfo: baz_init_ratfrac
 * Initialize @var{R} to zero.
 */

BAZ_DLL void
baz_init_ratfrac (
    struct baz_ratfrac *R)
{
  bap_init_polynom_mpz (&R->numer);
  bap_init_polynom_one_mpz (&R->denom);
}

/*
 * texinfo: baz_init_readonly_ratfrac
 * Initialize @var{R} to zero in readonly mode (note: the denominator is
 * not readonly).
 */

BAZ_DLL void
baz_init_readonly_ratfrac (
    struct baz_ratfrac *R)
{
  bap_init_readonly_polynom_mpz (&R->numer);
  bap_init_polynom_one_mpz (&R->denom);
}

/*
 * texinfo: baz_new_ratfrac
 * Allocate a new ratfrac, initialize it and return it.
 */

BAZ_DLL struct baz_ratfrac *
baz_new_ratfrac (
    void)
{
  struct baz_ratfrac *A;

  A = (struct baz_ratfrac *) ba0_alloc (sizeof (struct baz_ratfrac));
  baz_init_ratfrac (A);
  return A;
}

/*
 * texinfo: baz_new_readonly_ratfrac
 * Allocate a new ratfrac, initialize it in readonly mode and return it.
 */

BAZ_DLL struct baz_ratfrac *
baz_new_readonly_ratfrac (
    void)
{
  struct baz_ratfrac *A;

  A = (struct baz_ratfrac *) ba0_alloc (sizeof (struct baz_ratfrac));
  baz_init_readonly_ratfrac (A);
  return A;
}

/*
 * texinfo: baz_sizeof_ratfrac
 * Return the size of the memory needed to perform a copy of @var{A}.
 * If @var{code} is @code{ba0_embedded} then @var{A} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account.
 */

BAZ_DLL unsigned ba0_int_p
baz_sizeof_ratfrac (
    struct baz_ratfrac *A,
    enum ba0_garbage_code code)
{
  unsigned ba0_int_p size;

  if (code == ba0_isolated)
    size = ba0_allocated_size (sizeof (struct baz_ratfrac));
  else
    size = 0;

  size += bap_sizeof_polynom_mpz (&A->numer, ba0_embedded);
  size += bap_sizeof_polynom_mpz (&A->denom, ba0_embedded);

  return size;
}

/*
 * texinfo: baz_switch_ring_ratfrac
 * This low level function should be used in conjunction with
 * @code{bav_set_differential_ring}: if @var{R} is a ring obtained by
 * application of @code{bav_set_differential_ring}
 * to the ring @var{A} refers to, then this function makes @var{A}
 * refer to @var{R}. 
 */

BAZ_DLL void
baz_switch_ring_ratfrac (
    struct baz_ratfrac *A,
    struct bav_differential_ring *R)
{
  bap_switch_ring_polynom_mpz (&A->numer, R);
  bap_switch_ring_polynom_mpz (&A->denom, R);
}

/*
 * texinfo: baz_set_ratfrac
 * Assign @var{B} to @var{A}.
 */

BAZ_DLL void
baz_set_ratfrac (
    struct baz_ratfrac *A,
    struct baz_ratfrac *B)
{
  if (A != B)
    {
      bap_set_polynom_mpz (&A->numer, &B->numer);
      bap_set_polynom_mpz (&A->denom, &B->denom);
    }
}

/*  
 * texinfo: baz_set_tableof_ratfrac
 * Assign @var{src} to @var{dst}.
 * Entries of @var{src} are allowed to be @code{BAZ_NOT_A_RATFRAC}.
 */

BAZ_DLL void
baz_set_tableof_ratfrac (
    struct baz_tableof_ratfrac *dst,
    struct baz_tableof_ratfrac *src)
{
  if (dst != src)
    {
      ba0_int_p i;

      ba0_realloc_table ((struct ba0_table *) dst, src->size);
      for (i = 0; i < src->size; i++)
        {
          if (src->tab[i] == BAZ_NOT_A_RATFRAC)
            dst->tab[i] = BAZ_NOT_A_RATFRAC;
          else
            {
              if (dst->tab[i] == BAZ_NOT_A_RATFRAC)
                dst->tab[i] = baz_new_ratfrac ();
              baz_set_ratfrac (dst->tab[i], src->tab[i]);
            }
        }
      dst->size = src->size;
    }
}

/*
 * texinfo: baz_set_tableof_tableof_ratfrac
 * Assign @var{src} to @var{dst}.
 */

BAZ_DLL void
baz_set_tableof_tableof_ratfrac (
    struct baz_tableof_tableof_ratfrac *dst,
    struct baz_tableof_tableof_ratfrac *src)
{
  if (dst != src)
    {
      ba0_int_p i;

      ba0_realloc2_table ((struct ba0_table *) dst, src->size,
          (ba0_new_function *) & ba0_new_table);
      for (i = 0; i < src->size; i++)
        baz_set_tableof_ratfrac (dst->tab[i], src->tab[i]);
      dst->size = src->size;
    }
}

/*
 * texinfo: baz_set_ratfrac_zero
 * Assign @math{0} to @var{A}.
 */

BAZ_DLL void
baz_set_ratfrac_zero (
    struct baz_ratfrac *A)
{
  bap_set_polynom_zero_mpz (&A->numer);
  bap_set_polynom_one_mpz (&A->denom);
}

/*
 * texinfo: baz_set_ratfrac_one
 * Assign @math{1} to @var{A}.
 */

BAZ_DLL void
baz_set_ratfrac_one (
    struct baz_ratfrac *A)
{
  bap_set_polynom_one_mpz (&A->numer);
  bap_set_polynom_one_mpz (&A->denom);
}

/*
 * texinfo: baz_set_ratfrac_term
 * Assign @var{T} to @var{R}.
 */

BAZ_DLL void
baz_set_ratfrac_term (
    struct baz_ratfrac *R,
    struct bav_term *T)
{
  bap_set_polynom_term_mpz (&R->numer, T);
  bap_set_polynom_one_mpz (&R->denom);
}

/*
 * texinfo: baz_set_ratfrac_polynom_mpz
 * Assign @var{A} to @var{R}.
 */

BAZ_DLL void
baz_set_ratfrac_polynom_mpz (
    struct baz_ratfrac *R,
    struct bap_polynom_mpz *A)
{
  bap_set_polynom_mpz (&R->numer, A);
  bap_set_polynom_one_mpz (&R->denom);
}

/*
 * texinfo: baz_add_ratfrac_polynom_mpz
 * Assign @math{A + P} to @var{R}.
 */

BAZ_DLL void
baz_add_ratfrac_polynom_mpz (
    struct baz_ratfrac *R,
    struct baz_ratfrac *A,
    struct bap_polynom_mpz *P)
{
  struct bap_polynom_mpz B;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  bap_init_polynom_mpz (&B);
  bap_mul_polynom_mpz (&B, &A->denom, P);
  ba0_pull_stack ();
  bap_add_polynom_mpz (&R->numer, &A->numer, &B);
  ba0_restore (&M);
  if (R != A)
    bap_set_polynom_mpz (&R->denom, &A->denom);
}

/*
 * texinfo: baz_mul_ratfrac_polynom_mpz
 * Assign @math{A \, P} to @var{R}.
 */

BAZ_DLL void
baz_mul_ratfrac_polynom_mpz (
    struct baz_ratfrac *R,
    struct baz_ratfrac *A,
    struct bap_polynom_mpz *P)
{
  struct bap_polynom_mpz cofAden, cofP;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  bap_init_polynom_mpz (&cofAden);
  bap_init_polynom_mpz (&cofP);
  baz_gcd_polynom_mpz (BAP_NOT_A_POLYNOM_mpz, &cofAden, &cofP, &A->denom, P);
  ba0_pull_stack ();
  bap_mul_polynom_mpz (&R->numer, &A->numer, &cofP);
  bap_set_polynom_mpz (&R->denom, &cofAden);
  baz_normalize_numeric_initial_ratfrac (R);
  ba0_restore (&M);
}

/*
 * texinfo: baz_mul_ratfrac_polynom_mpq
 * Assign @math{A \, P} to @var{R}.
 */

BAZ_DLL void
baz_mul_ratfrac_polynom_mpq (
    struct baz_ratfrac *R,
    struct baz_ratfrac *A,
    struct bap_polynom_mpq *P)
{
  struct bap_polynom_mpz numer;
  ba0_mpq_t denom;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  bap_init_polynom_mpz (&numer);
  ba0_mpq_init (denom);
  ba0_mpz_set_ui (ba0_mpq_numref (denom), 1);
  bap_numer_polynom_mpq (&numer, ba0_mpq_denref (denom), P);
  ba0_pull_stack ();
  baz_mul_ratfrac_polynom_mpz (R, A, &numer);
  baz_mul_ratfrac_numeric_mpq (R, R, denom);
  ba0_restore (&M);
}

/*
 * texinfo: baz_set_ratfrac_fraction
 * Assign @math{P/Q} to @var{R}.
 */

BAZ_DLL void
baz_set_ratfrac_fraction (
    struct baz_ratfrac *R,
    struct bap_polynom_mpz *P,
    struct bap_polynom_mpz *Q)
{
  if (bap_is_zero_polynom_mpz (P))
    baz_set_ratfrac_zero (R);
  else if (bap_is_zero_polynom_mpz (Q))
    BA0_RAISE_EXCEPTION (BA0_ERRIVZ);
  else
    {
      bap_set_polynom_mpz (&R->numer, P);
      bap_set_polynom_mpz (&R->denom, Q);
      baz_reduce_ratfrac (R, R);
    }
}

static void *baz_scanf2_ratfrac (
    void *);

/*
 * texinfo: baz_scanf_ratfrac
 * The general parsing function of rational fractions.
 * It is called by @code{ba0_scanf/%Qz}.
 * This function does not simplify to zero the zero derivatives
 * of parameters. The fact that derivations commute is not taken
 * into account. See @code{baz_scanf_simplify_ratfrac}.
 */

BAZ_DLL void *
baz_scanf_ratfrac (
    void *R)
{
  struct baz_ratfrac *A;
  A = baz_scanf2_ratfrac (R);
  baz_reduce_ratfrac (A, A);
  return A;
}


/*
 * texinfo: baz_scanf_simplify_ratfrac
 * Parsing functions for rational fractions.
 * Zero derivatives of parameters are simplified to zero.
 * The fact that derivations commute is taken into account.
 * This function is called by @code{ba0_scanf/%simplify_Qz}.
 */

BAZ_DLL void *
baz_scanf_simplify_ratfrac (
    void *R)
{
  struct baz_ratfrac *A;
  bool numer_simplifies, denom_simplifies;

  A = baz_scanf2_ratfrac (R);
  numer_simplifies =
      bav_depends_on_zero_derivatives_of_parameter_term (&A->numer.total_rank);
  denom_simplifies =
      bav_depends_on_zero_derivatives_of_parameter_term (&A->denom.total_rank);

  if (denom_simplifies)
    {
      bap_simplify_zero_derivatives_of_parameter_polynom_mpz (&A->denom,
          &A->denom);
      if (bap_is_zero_polynom_mpz (&A->denom))
        BA0_RAISE_EXCEPTION (BA0_ERRIVZ);
/*
 * In the case of an exception, A gets corrupted.
 */
    }
  if (numer_simplifies)
    bap_simplify_zero_derivatives_of_parameter_polynom_mpz (&A->numer,
        &A->numer);

  baz_reduce_ratfrac (A, A);
  return A;
}

static void *
baz_scanf2_ratfrac (
    void *R)
{
  struct baz_ratfrac *A = (struct baz_ratfrac *) R;
  struct baz_ratfrac S, P;
  struct ba0_mark M;

  if (A == (struct baz_ratfrac *) 0)
    A = baz_new_ratfrac ();

  ba0_push_another_stack ();
  ba0_record (&M);
  baz_init_ratfrac (&S);
  baz_init_ratfrac (&P);

  if (!ba0_sign_token_analex ("-"))
    {
      baz_scanf_product_ratfrac (&S);
      ba0_get_token_analex ();
    }
  while (ba0_sign_token_analex ("+") || ba0_sign_token_analex ("-"))
    {
      if (ba0_sign_token_analex ("+"))
        {
          ba0_get_token_analex ();
          baz_scanf_product_ratfrac (&P);
          ba0_get_token_analex ();
          baz_add_ratfrac (&S, &S, &P);
        }
      else
        {
          ba0_get_token_analex ();
          baz_scanf_product_ratfrac (&P);
          ba0_get_token_analex ();
          baz_sub_ratfrac (&S, &S, &P);
        }
    }
  ba0_unget_token_analex (1);
  ba0_pull_stack ();
  baz_set_ratfrac (A, &S);
  ba0_restore (&M);
  return A;
}

static ba0_scanf_function baz_scanf_power_ratfrac;

BAZ_DLL void *
baz_scanf_product_ratfrac (
    void *AA)
{
  struct baz_ratfrac *A;
  struct baz_ratfrac B;
  struct ba0_mark M;

  if (AA == (void *) 0)
    A = baz_new_ratfrac ();
  else
    A = (struct baz_ratfrac *) AA;

  ba0_push_another_stack ();
  ba0_record (&M);
  baz_init_ratfrac (&B);
  ba0_pull_stack ();

  baz_scanf_power_ratfrac (A);

  ba0_get_token_analex ();
  while (ba0_sign_token_analex ("*") || ba0_sign_token_analex ("/"))
    {
      if (ba0_sign_token_analex ("*"))
        {
          ba0_get_token_analex ();
          ba0_push_another_stack ();
          baz_scanf_power_ratfrac (&B);
          ba0_pull_stack ();
          baz_mul_ratfrac (A, A, &B);
        }
      else
        {
          ba0_get_token_analex ();
          ba0_push_another_stack ();
          baz_scanf_power_ratfrac (&B);
          ba0_pull_stack ();
          baz_div_ratfrac (A, A, &B);
        }
      ba0_get_token_analex ();
    }

  ba0_unget_token_analex (1);

  ba0_restore (&M);
  return A;
}

static ba0_scanf_function baz_scanf_atomic_ratfrac;

static void *
baz_scanf_power_ratfrac (
    void *AA)
{
  struct baz_ratfrac *A;
  bav_Idegree d = 0;            /* to avoid a warning */
  bool exponent;

  if (AA == (void *) 0)
    A = baz_new_ratfrac ();
  else
    A = (struct baz_ratfrac *) AA;

  baz_scanf_atomic_ratfrac (A);
  ba0_get_token_analex ();

  exponent = false;
  if (ba0_sign_token_analex ("^"))
    exponent = true;
  else if (ba0_sign_token_analex ("*"))
    {
      ba0_get_token_analex ();
      if (ba0_sign_token_analex ("*"))
        exponent = true;
      else
        ba0_unget_token_analex (1);
    }

  if (exponent)
    {
      ba0_get_token_analex ();
      if (ba0_type_token_analex () == ba0_integer_token)
        d = (bav_Idegree) atoi (ba0_value_token_analex ());
      else if (ba0_sign_token_analex ("("))
        ba0_scanf ("(%d)", &d);
      else
        BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
      baz_pow_ratfrac (A, A, d);
    }
  else
    ba0_unget_token_analex (1);

  return A;
}

static void *
baz_scanf_atomic_ratfrac (
    void *AA)
{
  struct baz_ratfrac *A;
  struct bap_polynom_mpz P;
  struct bav_variable *v;
  ba0_mpz_t c;
  struct ba0_mark M;

  if (AA == (void *) 0)
    A = baz_new_ratfrac ();
  else
    A = (struct baz_ratfrac *) AA;
/*
 * The set of possible starting tokens
 */
  if (ba0_type_token_analex () == ba0_integer_token ||
      (ba0_type_token_analex () == ba0_string_token &&
          ba0_strcasecmp (ba0_value_token_analex (), "factorial") == 0))
    {
      struct bav_rank rg;

      ba0_push_another_stack ();
      ba0_record (&M);
      ba0_mpz_init (c);
      ba0_scanf ("%z", c);
      bap_init_polynom_mpz (&P);
      rg = bav_constant_rank ();
      bap_set_polynom_crk_mpz (&P, c, &rg);
      ba0_pull_stack ();
      baz_set_ratfrac_polynom_mpz (A, &P);
      ba0_restore (&M);
    }
  else if (ba0_type_token_analex () == ba0_string_token)
    {
      ba0_push_another_stack ();
      ba0_record (&M);
      bap_init_polynom_mpz (&P);
      ba0_scanf ("%v", &v);
/*
 * Do not check for zero derivatives of parameters
 */
      bap_set_polynom_variable_mpz (&P, v, 1);
      ba0_pull_stack ();
      baz_set_ratfrac_polynom_mpz (A, &P);
      ba0_restore (&M);
    }
  else if (ba0_sign_token_analex ("("))
    {
      ba0_get_token_analex ();
      baz_scanf2_ratfrac (A);
      ba0_get_token_analex ();
      if (!ba0_sign_token_analex (")"))
        BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
    }
  else
    BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
  return A;
}

/*
 * texinfo: baz_scanf_expanded_ratfrac
 * Parsing functions for rational fractions.
 * The numerator and the denominator are supposed to be expanded
 * polynomials over the rational numbers.
 * This function does not simplify to zero the zero derivatives
 * of parameters. The fact that derivations commute is not taken
 * into account. See @code{baz_scanf_simplify_expanded_ratfrac}.
 * This function is called by @code{ba0_scanf/%expanded_Qz}.
 */

BAZ_DLL void *
baz_scanf_expanded_ratfrac (
    void *AA)
{
  struct baz_ratfrac *A;
  struct bap_polynom_mpq Anum, Aden;
  struct ba0_mark M;
  ba0_mpq_t q;
  ba0_mpz_t qnum, qden;
  ba0_mpz_t den_numer, den_denom;
  bool minus, coeffnum;
  ba0_int_p n;

  if (AA == (void *) 0)
    A = baz_new_ratfrac ();
  else
    A = (struct baz_ratfrac *) AA;

  ba0_push_another_stack ();
  ba0_record (&M);
/*
 * Read a possible starting minus sign.
 * This minus sign will only matter if there is a leading numerical factor.
 * It will then apply to this factor.
 * The variable n counts tokens
 */

  if (ba0_sign_token_analex ("-"))
    {
      ba0_get_token_analex ();
      minus = true;
      n = 1;
    }
  else
    {
      minus = false;
      n = 0;
    }
/*
 * Read a possible leading numerical factor.
 * We are not yet sure that the numerical factor is a global factor.
 *
 * Observe that we cannot read directly a rational number for
 * a rational fraction of the form 1/u would raise an exception.
 */
  ba0_mpz_init_set_ui (qnum, 1);
  ba0_mpz_init_set_ui (qden, 1);
  if (ba0_type_token_analex () == ba0_integer_token ||
      (ba0_type_token_analex () == ba0_string_token &&
          ba0_strcasecmp (ba0_value_token_analex (), "factorial") == 0))
    {
      coeffnum = true;
      ba0_scanf_mpz (qnum);
      ba0_get_token_analex ();
      n += 1;
      if (ba0_sign_token_analex ("/"))
        {
          ba0_get_token_analex ();
          n += 1;
          if (ba0_type_token_analex () == ba0_integer_token ||
              (ba0_type_token_analex () == ba0_string_token &&
                  ba0_strcasecmp (ba0_value_token_analex (), "factorial") == 0))
            {
              ba0_scanf_mpz (qden);
              ba0_get_token_analex ();
              n += 1;
            }
          else
            {
              ba0_unget_token_analex (1);
              n -= 1;
            }
        }
    }
  else
    coeffnum = false;
  ba0_mpq_init (q);
  ba0_mpq_set_num (q, qnum);
  ba0_mpq_set_den (q, qden);
  ba0_mpq_canonicalize (q);
  if (minus)
    ba0_mpq_neg (q, q);
/*
 * If there is a leading numerical factor then, it is in q.
 * The minus sign is taken into account.
 * 
 * If there is no leading numerical factor then we will have to
 * undo all ba0_get_token before reading the numerator. In this case,
 * the number of ba0_unget_token to perform is stored in n.
 */
  if (!coeffnum)
    {
      if (ba0_sign_token_analex ("*") || ba0_sign_token_analex ("/")
          || ba0_sign_token_analex ("+") || ba0_sign_token_analex ("-"))
        BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
    }
/*
 * Let us read the numerator and denominator of the rational fraction
 */
  bap_init_polynom_mpq (&Anum);
  bap_init_polynom_mpq (&Aden);
  bap_set_polynom_one_mpq (&Anum);
  bap_set_polynom_one_mpq (&Aden);

  if ((coeffnum && ba0_sign_token_analex ("*")) || !coeffnum)
    {
      if (ba0_sign_token_analex ("*"))
        {
          ba0_get_token_analex ();
          n += 1;
        }
      if (!ba0_sign_token_analex ("("))
        {
/*
 * The leading rational is actually not a leading numerical factor.
 * Undo all ba0_get_token_analex and reset q to 1/1.
 */
          ba0_unget_token_analex (n);
          ba0_mpq_set_ui (q, 1);
        }
/*
 * Read numerator and denominator
 */
      bap_scanf_expanded_polynom_mpq (&Anum);
      ba0_get_token_analex ();
      if (ba0_sign_token_analex ("/"))
        {
          ba0_get_token_analex ();
          bap_scanf_expanded_polynom_mpq (&Aden);
        }
      else
        ba0_unget_token_analex (1);
    }
  else if (ba0_sign_token_analex ("+") || ba0_sign_token_analex ("-"))
    {
/*
 * numerical factor +/- ...
 */
      ba0_unget_token_analex (n);
      ba0_mpq_set_ui (q, 1);
/*
 * Read numerator 
 */
      bap_scanf_expanded_polynom_mpq (&Anum);
    }
  else if (ba0_sign_token_analex ("/"))
    {
      ba0_get_token_analex ();
      bap_scanf_expanded_polynom_mpq (&Aden);
    }
  else
    ba0_unget_token_analex (1);
/*
 * Incorporate the numerical factor q in Anum.
 */
  bap_mul_polynom_numeric_mpq (&Anum, &Anum, q);
/*
 * Let us compute the result
 */
  ba0_pull_stack ();

  ba0_mpz_init (den_numer);
  ba0_mpz_init (den_denom);
  bap_numer_polynom_mpq (&A->numer, den_numer, &Anum);
  bap_numer_polynom_mpq (&A->denom, den_denom, &Aden);
  bap_mul_polynom_numeric_mpz (&A->numer, &A->numer, den_denom);
  bap_mul_polynom_numeric_mpz (&A->denom, &A->denom, den_numer);
  if (ba0_mpz_sgn (*bap_numeric_initial_polynom_mpz (&A->denom)) < 0)
    {
      bap_neg_polynom_mpz (&A->numer, &A->numer);
      bap_neg_polynom_mpz (&A->denom, &A->denom);
    }
  ba0_restore (&M);
  return A;
}

/*
 * texinfo: baz_scanf_simplify_expanded_ratfrac
 * Parsing functions for rational fractions.
 * The numerator and the denominator are supposed to be expanded
 * polynomials over the rational numbers.
 * This function simplifies to zero the zero derivatives of parameters. 
 * The fact that derivations commute is taken into account. 
 * This function is called by @code{ba0_scanf/%simplify_expanded_Qz}.
 */

BAZ_DLL void *
baz_scanf_simplify_expanded_ratfrac (
    void *R)
{
  struct baz_ratfrac *A;
  bool numer_simplifies, denom_simplifies;
/*
 * Fix me.
 * It should be a call to scanf_expanded_ratfrac but this latter
 * function misses some cases.
 * The call to baz_scanf2_ratfrac catches u[x,y] - u[y,x] = 0
 * The function is thus a duplicate of baz_scanf_simplify_ratfrac
 */
  A = baz_scanf2_ratfrac (R);
  numer_simplifies =
      bav_depends_on_zero_derivatives_of_parameter_term (&A->numer.total_rank);
  denom_simplifies =
      bav_depends_on_zero_derivatives_of_parameter_term (&A->denom.total_rank);

  if (denom_simplifies)
    {
      bap_simplify_zero_derivatives_of_parameter_polynom_mpz (&A->denom,
          &A->denom);
      if (bap_is_zero_polynom_mpz (&A->denom))
        BA0_RAISE_EXCEPTION (BA0_ERRIVZ);
/*
 * In the case of an exception, A gets corrupted.
 */
    }
  if (numer_simplifies)
    bap_simplify_zero_derivatives_of_parameter_polynom_mpz (&A->numer,
        &A->numer);

  baz_reduce_ratfrac (A, A);
  return A;
}

/*
 * texinfo: baz_printf_ratfrac
 * The general printing function for rational fractions.
 * It is called by @code{ba0_printf/%Qz}.
 */

BAZ_DLL void
baz_printf_ratfrac (
    void *AA)
{
  struct baz_ratfrac *A = (struct baz_ratfrac *) AA;

  if (A == BAZ_NOT_A_RATFRAC)
    ba0_put_string ("null");
  else if (baz_is_zero_ratfrac (A))
    ba0_put_char ('0');
  else if (bap_is_one_polynom_mpz (&A->denom))
    bap_printf_polynom_mpz (&A->numer);
  else
    {
      if (bap_nbmon_polynom_mpz (&A->numer) == 1)
        bap_printf_polynom_mpz (&A->numer);
      else
        {
          ba0_put_char ('(');
          bap_printf_polynom_mpz (&A->numer);
          ba0_put_string (")");
        }
      ba0_put_string ("/(");
      bap_printf_polynom_mpz (&A->denom);
      ba0_put_char (')');
    }
}

/*
 * Readonly static data
 */

static char _struct_ratfrac[] = "struct baz_ratfrac";

BAZ_DLL ba0_int_p
baz_garbage1_ratfrac (
    void *AA,
    enum ba0_garbage_code code)
{
  struct baz_ratfrac *A = (struct baz_ratfrac *) AA;
  ba0_int_p n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (A, sizeof (struct baz_ratfrac), _struct_ratfrac);

  n += bap_garbage1_polynom_mpz (&A->numer, ba0_embedded);
  n += bap_garbage1_polynom_mpz (&A->denom, ba0_embedded);

  return n;
}

BAZ_DLL void *
baz_garbage2_ratfrac (
    void *AA,
    enum ba0_garbage_code code)
{
  struct baz_ratfrac *A;

  if (code == ba0_isolated)
    A = ba0_new_addr_gc_info (AA, _struct_ratfrac);
  else
    A = (struct baz_ratfrac *) AA;

  bap_garbage2_polynom_mpz (&A->numer, ba0_embedded);
  bap_garbage2_polynom_mpz (&A->denom, ba0_embedded);
  return A;
}

BAZ_DLL void *
baz_copy_ratfrac (
    void *AA)
{
  struct baz_ratfrac *B;

  B = baz_new_ratfrac ();
  baz_set_ratfrac (B, (struct baz_ratfrac *) AA);
  return B;
}

/*
 * texinfo: baz_sort_ratfrac
 * Sort @var{A} with respect to the current ordering.
 * The result, which is readonly, is stored in @var{R}.
 */

BAZ_DLL void
baz_sort_ratfrac (
    struct baz_ratfrac *R,
    struct baz_ratfrac *A)
{
  bap_sort_polynom_mpz (&R->numer, &A->numer);
  bap_sort_polynom_mpz (&R->denom, &A->denom);
}

/*
 * texinfo: baz_physort_ratfrac
 * Apply @code{bap_physort_polynom_mpz} over the numerator and
 * the denominator of @var{R}.
 */

BAZ_DLL void
baz_physort_ratfrac (
    struct baz_ratfrac *R)
{
  bap_physort_polynom_mpz (&R->numer);
  bap_physort_polynom_mpz (&R->denom);
}

/*
 * texinfo: baz_is_zero_ratfrac
 * Return @code{true} if @var{R} if @math{0}.
 */

BAZ_DLL bool
baz_is_zero_ratfrac (
    struct baz_ratfrac *R)
{
  return bap_is_zero_polynom_mpz (&R->numer);
}

/*
 * texinfo: baz_is_one_ratfrac
 * Return @code{true} if @var{R} is @math{1}.
 */

BAZ_DLL bool
baz_is_one_ratfrac (
    struct baz_ratfrac *R)
{
  return bap_equal_polynom_mpz (&R->numer, &R->denom);
}

/*
 * texinfo: baz_is_numeric_ratfrac
 * Return @code{true} if the numerator and the denomnator of @var{R}
 * are numerical.
 */

BAZ_DLL bool
baz_is_numeric_ratfrac (
    struct baz_ratfrac *R)
{
  return bap_is_numeric_polynom_mpz (&R->numer)
      && bap_is_numeric_polynom_mpz (&R->denom);
}

/*
 * texinfo: baz_equal_ratfrac
 * Return @code{true} if @var{A} and @var{B} have the same numerator and the
 * same denominator.
 */

BAZ_DLL bool
baz_equal_ratfrac (
    struct baz_ratfrac *A,
    struct baz_ratfrac *B)
{
  return bap_equal_polynom_mpz (&A->numer, &B->numer)
      && bap_equal_polynom_mpz (&A->denom, &B->denom);
}

/*
 * texinfo: baz_depend_ratfrac
 * Return @code{true} if @var{A} depends on @var{v}.
 */

BAZ_DLL bool
baz_depend_ratfrac (
    struct baz_ratfrac *A,
    struct bav_variable *v)
{
  return bap_depend_polynom_mpz (&A->numer, v)
      || bap_depend_polynom_mpz (&A->denom, v);
}

/*
 * texinfo: baz_mark_indets_ratfrac
 * Append to @var{vars} the variables occurring in @var{R} which are
 * not already present in @var{vars}. Each element of @var{vars}
 * is supposed to be registered in the dictionary @var{dict}.
 */

BAZ_DLL void
baz_mark_indets_ratfrac (
    struct bav_dictionary_variable *dict,
    struct bav_tableof_variable *vars,
    struct baz_ratfrac *R)
{
  bap_mark_indets_polynom_mpz (dict, vars, &R->numer);
  bap_mark_indets_polynom_mpz (dict, vars, &R->denom);
}

/*
 * texinfo: baz_leader_ratfrac
 * Return the highest variable occurring in the numerator and the denominator
 * of @var{A}. The rational fraction is supposed to be reduced.
 * Exception @code{BAP_ERRCST} is raised if @var{R} is numerical.
 */

BAZ_DLL struct bav_variable *
baz_leader_ratfrac (
    struct baz_ratfrac *R)
{
  struct bav_variable *w = BAV_NOT_A_VARIABLE;

  if (bap_is_numeric_polynom_mpz (&R->numer))
    {
      if (bap_is_numeric_polynom_mpz (&R->denom))
        BA0_RAISE_EXCEPTION (BAP_ERRCST);
      else
        w = bap_leader_polynom_mpz (&R->denom);
    }
  else if (bap_is_numeric_polynom_mpz (&R->denom))
    w = bap_leader_polynom_mpz (&R->numer);
  else
    {
      struct bav_variable *u, *v;
/*
 * The fraction is supposed to be reduced
 */
      u = bap_leader_polynom_mpz (&R->numer);
      v = bap_leader_polynom_mpz (&R->denom);
      w = bav_variable_number (u) > bav_variable_number (v) ? u : v;
    }
  return w;
}

static struct bav_rank
baz_rank_ratfrac2 (
    struct bap_polynom_mpz *numer,
    struct bap_polynom_mpz *denom)
{
  struct bav_rank rg, rgnum, rgden;
#undef BAP_OLD_RANKDEF
#if defined (BAP_OLD_RANKDEF)
  struct bap_polynom_mpz rem;
  struct ba0_mark M;
#endif

  rgnum = bap_rank_polynom_mpz (numer);
  rgden = bap_rank_polynom_mpz (denom);
  if (bav_is_constant_rank (&rgden))
    rg = rgnum;
  else if (bav_is_constant_rank (&rgnum))
    {
      rg.var = rgden.var;
      rg.deg = -rgden.deg;
    }
  else if (bav_variable_number (rgnum.var) > bav_variable_number (rgden.var))
    rg = rgnum;
  else if (bav_variable_number (rgnum.var) < bav_variable_number (rgden.var))
    {
      rg.var = rgden.var;
      rg.deg = -rgden.deg;
    }
  else if (rgnum.deg != rgden.deg)
    {
      rg.var = rgnum.var;
      rg.deg = rgnum.deg - rgden.deg;
    }
  else
#if defined (BAP_OLD_RANKDEF)
    {
      ba0_record (&M);
      bap_init_polynom_mpz (&rem);
      bap_prem_polynom_mpz (&rem, (bav_Idegree *) 0, numer, denom, rgnum.var);
      rg = baz_rank_ratfrac2 (&rem, denom);
      ba0_restore (&M);
    }
#else
    rg = bav_constant_rank2 (rgnum.var);
#endif
  return rg;
}

/*
 * texinfo: baz_rank_ratfrac
 * Return the rank of @var{A}, which is defined as follows:
 * if @var{A} is numeric, then its rank is the constant rank (or the rank
 * of zero), else it is @math{v^{n-d}} where @math{v}, @math{n} and @math{d}
 * denote the leader of @var{A}, the degree of its numerator in @math{v}
 * and the degree of its denominator in @math{v}. When @math{n=d}, the
 * rank of @math{A} is the constant rank.
 */

BAZ_DLL struct bav_rank
baz_rank_ratfrac (
    struct baz_ratfrac *R)
{
  return baz_rank_ratfrac2 (&R->numer, &R->denom);
}

/*
 * texinfo: baz_compare_rank_ratfrac
 * A comparison function for sorting tables of rational fractions
 * by increasing rank, using @code{qsort}.
 */

BAZ_DLL int
baz_compare_rank_ratfrac (
    const void *PP,
    const void *QQ)
{
  struct baz_ratfrac *P = *(struct baz_ratfrac * *) PP;
  struct baz_ratfrac *Q = *(struct baz_ratfrac * *) QQ;
  struct bav_rank rk_P, rk_Q;

  rk_P = baz_rank_ratfrac (P);
  rk_Q = baz_rank_ratfrac (Q);

  if (bav_equal_rank (&rk_P, &rk_Q))
    return 0;
  else if (bav_lt_rank (&rk_P, &rk_Q))
    return -1;
  else
    return 1;
}

/*
 * texinfo: baz_initial_ratfrac
 * Assign to @var{init} the initial of @var{R} in readonly mode.
 * Raises the exception @code{BAP_ERRNHL} if the rank of @var{R}
 * has negative degree.
 */

BAZ_DLL void
baz_initial_ratfrac (
    struct baz_ratfrac *init,
    struct baz_ratfrac *R)
{
  struct bav_rank rg;

  rg = baz_rank_ratfrac (R);
  if (rg.deg <= 0)
    BA0_RAISE_EXCEPTION (BAZ_ERRNHL);
  if (init != R)
    bap_set_readonly_polynom_mpz (&init->denom, &R->denom);
  bap_initial_polynom_mpz (&init->numer, &R->numer);
}

/*
 * texinfo: baz_reductum_ratfrac
 * Assign to @var{reductum} the reductum of @var{R} in readonly mode.
 * Raises the exception @code{BAP_ERRNHL} if the rank of @var{R}
 * has negative degree.
 */

BAZ_DLL void
baz_reductum_ratfrac (
    struct baz_ratfrac *reductum,
    struct baz_ratfrac *R)
{
  struct bav_rank rg;

  rg = baz_rank_ratfrac (R);
  if (rg.deg <= 0)
    BA0_RAISE_EXCEPTION (BAZ_ERRNHL);
  if (reductum != R)
    bap_set_readonly_polynom_mpz (&reductum->denom, &R->denom);
  bap_reductum_polynom_mpz (&reductum->numer, &R->numer);
}

/*
 * texinfo: baz_lcoeff_and_reductum_ratfrac
 * Assign to @var{lcoeff} and @var{reductum} the leading coefficient and
 * the reductum of @var{R} with respect to @var{v}. The variable @var{v} does not
 * need to be greater than or equal to the leading variable of @var{R}.
 * If @var{v} is the zero pointer, it is taken to be the leading variable
 * of @var{R}.
 * The rational fraction @var{R} may be a numerical rational fraction.
 * In that case, @var{R} is assigned to @var{lcoeff} and zero is
 * assigned to @var{reductum}.
 * The resulting rational fractions are plain rational fractions (not readonly).
 * Exception @code{BAP_ERRNHL} is raised if @var{v} is zero and the rank
 * of @var{R} has negative degree.
 * Exception @code{BAP_ERRVPD} is raised if @var{v} is nonzero and is 
 * present in the denominator of @var{R}.
 */

BAZ_DLL void
baz_lcoeff_and_reductum_ratfrac (
    struct baz_ratfrac *lcoeff,
    struct baz_ratfrac *reductum,
    struct baz_ratfrac *R,
    struct bav_variable *v)
{
  struct bav_rank rg;

  if (v == BAV_NOT_A_VARIABLE)
    {
      rg = baz_rank_ratfrac (R);
      if (rg.deg <= 0)
        BA0_RAISE_EXCEPTION (BAZ_ERRNHL);
    }
  else if (bap_depend_polynom_mpz (&R->denom, v))
    BA0_RAISE_EXCEPTION (BAZ_ERRVPD);

  if (lcoeff != (struct baz_ratfrac *) 0 && lcoeff != R)
    bap_set_polynom_mpz (&lcoeff->denom, &R->denom);
  if (reductum != (struct baz_ratfrac *) 0 && reductum != R)
    bap_set_polynom_mpz (&reductum->denom, &R->denom);
  bap_lcoeff_and_reductum_polynom_mpz (lcoeff !=
      (struct baz_ratfrac *) 0 ? &lcoeff->numer : (struct bap_polynom_mpz *) 0,
      reductum !=
      (struct baz_ratfrac *) 0 ? &reductum->numer : (struct bap_polynom_mpz *)
      0, &R->numer, v);
}

/*
 * texinfo: baz_numer_ratfrac
 * Assign to @var{A} the numerator of @var{R}.
 */

BAZ_DLL void
baz_numer_ratfrac (
    struct bap_polynom_mpz *A,
    struct baz_ratfrac *R)
{
  bap_set_polynom_mpz (A, &R->numer);
}

/*
 * texinfo: baz_denom_ratfrac
 * Assign to @var{A} the denominator of @var{R}.
 */

BAZ_DLL void
baz_denom_ratfrac (
    struct bap_polynom_mpz *A,
    struct baz_ratfrac *R)
{
  bap_set_polynom_mpz (A, &R->denom);
}

/*
 * texinfo: baz_normalize_numeric_initial_ratfrac
 * Make the numeric leading coefficient of the denominator of @var{R}
 * positive.
 */

BAZ_DLL void
baz_normalize_numeric_initial_ratfrac (
    struct baz_ratfrac *R)
{
  if (ba0_mpz_sgn (*bap_numeric_initial_polynom_mpz (&R->denom)) < 0)
    {
      bap_neg_polynom_mpz (&R->numer, &R->numer);
      bap_neg_polynom_mpz (&R->denom, &R->denom);
    }
}

/*
 * texinfo: baz_reduce_numeric_ratfrac
 * Divide the numerator and the denominator of @var{A} by the gcd of their
 * numerical content. Result in @var{R}.
 * The numerical leading coefficient of the denominator of @var{R} is positive.
 */

BAZ_DLL void
baz_reduce_numeric_ratfrac (
    struct baz_ratfrac *R,
    struct baz_ratfrac *A)
{
  ba0_mpz_t contnum, contden, gcd;
  struct ba0_mark M;

  if (baz_is_zero_ratfrac (A))
    baz_set_ratfrac_zero (R);
  else
    {
      ba0_push_another_stack ();
      ba0_record (&M);
      ba0_mpz_init (contnum);
      ba0_mpz_init (contden);
      ba0_mpz_init (gcd);
      bap_numeric_content_polynom_mpz (contnum, &A->numer);
      bap_numeric_content_polynom_mpz (contden, &A->denom);
      ba0_mpz_gcd (gcd, contnum, contden);
      if (ba0_mpz_sgn (*bap_numeric_initial_polynom_mpz (&A->denom)) < 0)
        ba0_mpz_neg (gcd, gcd);
      ba0_pull_stack ();
      bap_exquo_polynom_numeric_mpz (&R->numer, &A->numer, gcd);
      bap_exquo_polynom_numeric_mpz (&R->denom, &A->denom, gcd);
      ba0_restore (&M);
    }
}

/*
 * texinfo: baz_reduce_ratfrac
 * Assign to @var{R} the reduced fraction @var{A}.
 * The gcd of the numerator and the denominator of @var{A} is factored out.
 * The numerical leading coefficient of the denominator of @var{R} is positive.
 */

BAZ_DLL void
baz_reduce_ratfrac (
    struct baz_ratfrac *R,
    struct baz_ratfrac *A)
{
  if (bap_is_zero_polynom_mpz (&A->numer))
    baz_set_ratfrac_zero (R);
  else if (bap_is_numeric_polynom_mpz (&A->denom))
    baz_reduce_numeric_ratfrac (R, A);
  else
    {
      baz_gcd_polynom_mpz (BAP_NOT_A_POLYNOM_mpz, &R->numer, &R->denom,
          &A->numer, &A->denom);
      baz_normalize_numeric_initial_ratfrac (R);
    }
}

/*
 * texinfo: baz_neg_ratfrac
 * Assign @math{- A} to @var{R}.
 */

BAZ_DLL void
baz_neg_ratfrac (
    struct baz_ratfrac *R,
    struct baz_ratfrac *A)
{
  bap_neg_polynom_mpz (&R->numer, &A->numer);
  if (R != A)
    bap_set_polynom_mpz (&R->denom, &A->denom);
}

/*
 * texinfo: baz_add_ratfrac
 * Assign @math{A + B} to @math{R}.
 */

BAZ_DLL void
baz_add_ratfrac (
    struct baz_ratfrac *R,
    struct baz_ratfrac *A,
    struct baz_ratfrac *B)
{
  struct bap_polynom_mpz Abar, Bbar;
  struct ba0_mark M;

  if (bap_equal_polynom_mpz (&A->denom, &B->denom))
    {
      bap_add_polynom_mpz (&R->numer, &A->numer, &B->numer);
      if (R != A && R != B)
        bap_set_polynom_mpz (&R->denom, &A->denom);
    }
  else
    {
      ba0_push_another_stack ();
      ba0_record (&M);

      bap_init_polynom_mpz (&Abar);
      bap_init_polynom_mpz (&Bbar);
      bap_mul_polynom_mpz (&Bbar, &A->numer, &B->denom);
      bap_mul_polynom_mpz (&Abar, &B->numer, &A->denom);

      ba0_pull_stack ();

      bap_add_polynom_mpz (&R->numer, &Abar, &Bbar);
      if (bap_is_zero_polynom_mpz (&R->numer))
        baz_set_ratfrac_zero (R);
      else
        bap_mul_polynom_mpz (&R->denom, &A->denom, &B->denom);

      ba0_restore (&M);
    }
  baz_reduce_ratfrac (R, R);
}

/*
 * texinfo: baz_sub_ratfrac
 * Assign @math{A - B} to @math{R}.
 */

BAZ_DLL void
baz_sub_ratfrac (
    struct baz_ratfrac *R,
    struct baz_ratfrac *A,
    struct baz_ratfrac *B)
{
  struct bap_polynom_mpz Abar, Bbar;
  struct ba0_mark M;

  if (bap_equal_polynom_mpz (&A->denom, &B->denom))
    {
      bap_sub_polynom_mpz (&R->numer, &A->numer, &B->numer);
      if (R != A && R != B)
        bap_set_polynom_mpz (&R->denom, &A->denom);
    }
  else
    {
      ba0_push_another_stack ();
      ba0_record (&M);

      bap_init_polynom_mpz (&Abar);
      bap_init_polynom_mpz (&Bbar);
      bap_mul_polynom_mpz (&Bbar, &A->numer, &B->denom);
      bap_mul_polynom_mpz (&Abar, &B->numer, &A->denom);

      ba0_pull_stack ();

      bap_sub_polynom_mpz (&R->numer, &Bbar, &Abar);
      if (bap_is_zero_polynom_mpz (&R->numer))
        baz_set_ratfrac_zero (R);
      else
        bap_mul_polynom_mpz (&R->denom, &A->denom, &B->denom);

      ba0_restore (&M);
    }
  baz_reduce_ratfrac (R, R);
}

/*
 * texinfo: baz_mul_ratfrac_numeric
 * Assign @math{c\,A} to @math{R}.
 */

BAZ_DLL void
baz_mul_ratfrac_numeric (
    struct baz_ratfrac *R,
    struct baz_ratfrac *A,
    ba0_mpz_t c)
{
  if (baz_is_zero_ratfrac (A) || ba0_mpz_sgn (c) == 0)
    baz_set_ratfrac_zero (R);
  else if (ba0_mpz_is_one (c))
    {
      if (R != A)
        baz_set_ratfrac (R, A);
    }
  else
    {
      bap_mul_polynom_numeric_mpz (&R->numer, &A->numer, c);
      if (R != A)
        bap_set_polynom_mpz (&R->denom, &A->denom);
      baz_reduce_numeric_ratfrac (R, R);
    }
}

/*
 * texinfo: baz_mul_ratfrac_numeric_mpq
 * Assign @math{q\,A} to @math{R}.
 */

BAZ_DLL void
baz_mul_ratfrac_numeric_mpq (
    struct baz_ratfrac *R,
    struct baz_ratfrac *A,
    ba0_mpq_t q)
{
  if (baz_is_zero_ratfrac (A) || ba0_mpz_sgn (ba0_mpq_numref (q)) == 0)
    baz_set_ratfrac_zero (R);
  else if (ba0_mpq_is_one (q))
    {
      if (R != A)
        baz_set_ratfrac (R, A);
    }
  else
    {
      bap_mul_polynom_numeric_mpz (&R->numer, &A->numer, ba0_mpq_numref (q));
      bap_mul_polynom_numeric_mpz (&R->denom, &A->denom, ba0_mpq_denref (q));
      if (R != A)
        bap_set_polynom_mpz (&R->denom, &A->denom);
      baz_reduce_numeric_ratfrac (R, R);
    }
}

/*
 * texinfo: baz_mul_ratfrac_variable
 * Assign @math{A\,v^d} to @var{R}.
 */

BAZ_DLL void
baz_mul_ratfrac_variable (
    struct baz_ratfrac *R,
    struct baz_ratfrac *A,
    struct bav_variable *v,
    bav_Idegree d)
{
  struct bav_term term;
  bav_Idegree e;
  struct ba0_mark M;

  if (d == 0)
    {
      if (A != R)
        baz_set_ratfrac (R, A);
      return;
    }
  else
    {
      bap_is_variable_factor_polynom_mpz (&A->denom, v, &e);
      if (e == 0)
        {
          bap_mul_polynom_variable_mpz (&R->numer, &A->numer, v, d);
          if (A != R)
            bap_set_polynom_mpz (&R->denom, &A->denom);
        }
      else
        {
          if (e < d)
            bap_mul_polynom_variable_mpz (&R->numer, &A->numer, v, d - e);

          ba0_push_another_stack ();
          ba0_record (&M);
          bav_init_term (&term);
          bav_set_term_variable (&term, v, e);
          ba0_pull_stack ();

          bap_exquo_polynom_term_mpz (&R->denom, &A->denom, &term);

          ba0_restore (&M);
        }
    }
}


/*
 * texinfo: baz_mul_ratfrac
 * Assign @math{A\,B} to @math{R}.
 */

BAZ_DLL void
baz_mul_ratfrac (
    struct baz_ratfrac *R,
    struct baz_ratfrac *A,
    struct baz_ratfrac *B)
{
  if (baz_is_zero_ratfrac (A) || baz_is_zero_ratfrac (B))
    baz_set_ratfrac_zero (R);
  else
    {
      struct bap_polynom_mpz cofAnum, cofAden, cofBnum, cofBden;
      struct ba0_mark M;

      ba0_push_another_stack ();
      ba0_record (&M);

      bap_init_polynom_mpz (&cofAnum);
      bap_init_polynom_mpz (&cofAden);
      bap_init_polynom_mpz (&cofBnum);
      bap_init_polynom_mpz (&cofBden);
      baz_gcd_polynom_mpz (BAP_NOT_A_POLYNOM_mpz, &cofAnum, &cofBden, &A->numer,
          &B->denom);
      baz_gcd_polynom_mpz (BAP_NOT_A_POLYNOM_mpz, &cofAden, &cofBnum, &A->denom,
          &B->numer);

      ba0_pull_stack ();
      bap_mul_polynom_mpz (&R->numer, &cofAnum, &cofBnum);
      bap_mul_polynom_mpz (&R->denom, &cofAden, &cofBden);
      baz_normalize_numeric_initial_ratfrac (R);
      ba0_restore (&M);
    }
}

/*
 * texinfo: baz_invert_ratfrac
 * Assign @math{1/A} to @math{R}.
 */

BAZ_DLL void
baz_invert_ratfrac (
    struct baz_ratfrac *R,
    struct baz_ratfrac *A)
{
  if (baz_is_zero_ratfrac (A))
    BA0_RAISE_EXCEPTION (BA0_ERRIVZ);
  if (R == A)
    {
      BA0_SWAP (struct bap_polynom_mpz,
          R->numer,
          R->denom);
    }
  else
    {
      bap_set_polynom_mpz (&R->numer, &A->denom);
      bap_set_polynom_mpz (&R->denom, &A->numer);
    }
  baz_normalize_numeric_initial_ratfrac (R);
}

/*
 * texinfo: baz_div_ratfrac
 * Assign @math{A/B} to @math{R}.
 */

BAZ_DLL void
baz_div_ratfrac (
    struct baz_ratfrac *R,
    struct baz_ratfrac *A,
    struct baz_ratfrac *B)
{
  struct baz_ratfrac C;

  if (baz_is_zero_ratfrac (B))
    BA0_RAISE_EXCEPTION (BA0_ERRIVZ);

  C.numer = B->denom;
  C.denom = B->numer;

  baz_mul_ratfrac (R, A, &C);
}

/*
 * texinfo: baz_pow_ratfrac
 * Assign @math{A^d} to @var{R}. The exponent @var{d} is allowed to be negative.
 */

BAZ_DLL void
baz_pow_ratfrac (
    struct baz_ratfrac *R,
    struct baz_ratfrac *A,
    bav_Idegree d)
{
  if (d == 0)
    baz_set_ratfrac_one (R);
  else if (d == 1)
    {
      if (R != A)
        baz_set_ratfrac (R, A);
    }
  else
    {
      bap_pow_polynom_mpz (&R->numer, &A->numer, d > 0 ? d : -d);
      bap_pow_polynom_mpz (&R->denom, &A->denom, d > 0 ? d : -d);
      if (d < 0)
        baz_invert_ratfrac (R, R);
    }

}

/*
 * texinfo: baz_separant_ratfrac
 * Assign the separant of @var{A} (i.e. its derivative with respect to
 * its leader) to @var{R}.
 */

BAZ_DLL void
baz_separant_ratfrac (
    struct baz_ratfrac *R,
    struct baz_ratfrac *A)
{
  struct bap_polynom_mpz sep_num_A;
  struct bap_polynom_mpz sep_den_A;
  struct bav_variable *u;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  u = baz_leader_ratfrac (A);

  if (bap_is_numeric_polynom_mpz (&A->numer)
      || bap_leader_polynom_mpz (&A->numer) != u)
    {
      bap_init_polynom_mpz (&sep_den_A);
      bap_separant_polynom_mpz (&sep_den_A, &A->denom);
      bap_mul_polynom_mpz (&sep_den_A, &sep_den_A, &A->numer);
      ba0_pull_stack ();
      bap_neg_polynom_mpz (&R->numer, &sep_den_A);
      bap_pow_polynom_mpz (&R->denom, &A->denom, 2);
    }
  else if (bap_is_numeric_polynom_mpz (&A->denom)
      || bap_leader_polynom_mpz (&A->denom) != u)
    {
      ba0_pull_stack ();
      bap_separant_polynom_mpz (&R->numer, &A->numer);
      if (A != R)
        bap_set_polynom_mpz (&R->denom, &A->denom);
    }
  else
    {
      bap_init_polynom_mpz (&sep_num_A);
      bap_init_polynom_mpz (&sep_den_A);
      bap_separant_polynom_mpz (&sep_num_A, &A->numer);
      bap_separant_polynom_mpz (&sep_den_A, &A->denom);
      bap_mul_polynom_mpz (&sep_num_A, &sep_num_A, &A->denom);
      bap_mul_polynom_mpz (&sep_den_A, &sep_den_A, &A->numer);

      ba0_pull_stack ();

      bap_sub_polynom_mpz (&R->numer, &sep_num_A, &sep_den_A);
      bap_pow_polynom_mpz (&R->denom, &A->denom, 2);
    }
  ba0_restore (&M);
  baz_reduce_ratfrac (R, R);
}

/*
 * texinfo: baz_separant2_ratfrac
 * Assign @math{\partial A / \partial v} to @math{R}.
 */

BAZ_DLL void
baz_separant2_ratfrac (
    struct baz_ratfrac *R,
    struct baz_ratfrac *A,
    struct bav_variable *v)
{
  struct baz_ratfrac B;
  bav_Iordering r;
  struct ba0_mark M;

  if (!baz_depend_ratfrac (A, v))
    baz_set_ratfrac_zero (R);
  else if (baz_leader_ratfrac (A) == v)
    baz_separant_ratfrac (R, A);
  else
    {
      ba0_push_another_stack ();
      ba0_record (&M);
      r = bav_R_copy_ordering (bav_current_ordering ());
      bav_push_ordering (r);
      bav_R_set_maximal_variable (v);
      baz_init_readonly_ratfrac (&B);
      baz_sort_ratfrac (&B, A);
      ba0_pull_stack ();
      baz_separant_ratfrac (R, &B);
      bav_pull_ordering ();
      baz_physort_ratfrac (R);
      bav_R_free_ordering (r);
      ba0_restore (&M);
    }
}

/*
 * texinfo: baz_diff_ratfrac
 * Assign to @var{R} the rational fraction obtained by differentiating 
 * @var{A} with respect to @var{s}. 
 */

BAZ_DLL void
baz_diff_ratfrac (
    struct baz_ratfrac *R,
    struct baz_ratfrac *A,
    struct bav_symbol *s)
{
  struct bap_polynom_mpz B;
  struct bap_polynom_mpz C;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  bap_init_polynom_mpz (&B);
  bap_init_polynom_mpz (&C);

  bap_diff_polynom_mpz (&B, &A->numer, s);
  bap_diff_polynom_mpz (&C, &A->denom, s);

  bap_mul_polynom_mpz (&B, &B, &A->denom);
  bap_mul_polynom_mpz (&C, &C, &A->numer);

  ba0_pull_stack ();

  bap_sub_polynom_mpz (&R->numer, &B, &C);
  if (bap_is_zero_polynom_mpz (&R->numer))
    baz_set_ratfrac_zero (R);
  else
    bap_pow_polynom_mpz (&R->denom, &A->denom, 2);

  ba0_restore (&M);
}

/*
 * texinfo: baz_is_constant_ratfrac
 * Return @code{true} if the derivative of @var{A} with respect to 
 * @var{s} is zero.
 */

BAZ_DLL bool
baz_is_constant_ratfrac (
    struct baz_ratfrac *A,
    struct bav_symbol *s)
{
  return bap_is_constant_polynom_mpz (&A->numer, s)
      && bap_is_constant_polynom_mpz (&A->denom, s);
}
