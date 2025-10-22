#include "bap_polynom_mpq.h"
#include "bap_parse_polynom_mpq.h"
#include "bap_add_polynom_mpq.h"
#include "bap_creator_mpq.h"
#include "bap_itermon_mpq.h"
#include "bap_itercoeff_mpq.h"
#include "bap__check_mpq.h"
#include "bap_product_mpq.h"
#include "bap_geobucket_mpq.h"


#define BAD_FLAG_mpq

/*************************************************************************
 PARSER

POLYNOM   ::= [-] PRODUCT +/- ... +/- PRODUCT
PRODUCT   ::= POWER * ... * POWER
POWER     ::= ATOM [^ ba0_int_hp]
ATOM      ::= coefficient | polynom ident | struct bav_variable * | ( POLYNOM )

 *************************************************************************/

BAP_DLL void *
bap_scanf_atomic_polynom_mpq (
    void *P)
{
  struct bap_polynom_mpq *A = (struct bap_polynom_mpq *) P;
  struct bav_variable *v;
  struct bav_rank rg;
  ba0_mpq_t c;
  struct ba0_mark M;

  if (A == BAP_NOT_A_POLYNOM_mpq)
    A = bap_new_polynom_mpq ();
/*
 * Depending on their types, numerical coefficients do not
 * start with the same sets of possible tokens
 */
#if defined (BAD_FLAG_mpz) || defined (BAD_FLAG_mpzm)
  if (ba0_type_token_analex () == ba0_integer_token ||
      (ba0_type_token_analex () == ba0_string_token &&
          ba0_strcasecmp (ba0_value_token_analex (), "factorial") == 0))
#elif defined (BAD_FLAG_mpq)
  if (ba0_type_token_analex () == ba0_integer_token ||
      (ba0_type_token_analex () == ba0_string_token &&
          ba0_strcasecmp (ba0_value_token_analex (), "factorial") == 0) ||
      ba0_sign_token_analex ("."))
#elif defined (BAD_FLAG_mint_hp)
  if (ba0_type_token_analex () == ba0_integer_token)
#endif
    {
      ba0_push_another_stack ();
      ba0_record (&M);
      ba0_mpq_init (c);
#if !defined (BAD_FLAG_mint_hp)
      ba0_scanf_mpq (c);
#else
      ba0_scanf_mint_hp (&c);
#endif
      ba0_pull_stack ();
      rg = bav_constant_rank ();
      bap_set_polynom_crk_mpq (A, c, &rg);
      ba0_restore (&M);
    }
  else if (ba0_type_token_analex () == ba0_string_token)
    {
      bav_scanf_variable (&v);
/*
 * The parser does not check for zero derivatives of parameters
 */
      bap_set_polynom_variable_mpq (A, v, 1);
    }
  else if (ba0_sign_token_analex ("("))
    {
      ba0_get_token_analex ();
      bap_scanf_polynom_mpq (A);
      ba0_get_token_analex ();
      if (!ba0_sign_token_analex (")"))
        BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
    }
  else
    BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
  return A;
}


static void
bap_parse_and_expand_product_mpq (
    struct bap_polynom_mpq *R)
{
  struct bap_product_mpq *prod;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  prod = bap_scanf_product_mpq ((void *) 0);
  ba0_pull_stack ();
  bap_expand_product_mpq (R, prod);
  ba0_restore (&M);
}

/*
 * texinfo: bap_scanf_polynom_eqn_mpq
 * A polynomial parsing function which parses either a mere polynomial
 * or an equation of the form @math{p = q} where @math{p} and @math{q}
 * are two polynomials. In this case, the parsed polynomial is the 
 * difference @math{p - q}.
 * This function relies on @code{bap_scanf_polynom_mpq}.
 */

BAP_DLL void *
bap_scanf_polynom_eqn_mpq (
    void *R)
{
  struct bap_polynom_mpq *A = (struct bap_polynom_mpq *) R;
  struct bap_polynom_mpq B, C;
  struct ba0_mark M;

  if (A == (struct bap_polynom_mpq *) 0)
    A = bap_new_polynom_mpq ();

  ba0_push_another_stack ();
  ba0_record (&M);

  bap_init_polynom_mpq (&B);
  bap_scanf_polynom_mpq (&B);

  if (!ba0_sign_token_analex ("="))
    {
      ba0_pull_stack ();
      bap_set_polynom_mpq (A, &B);
    }
  else
    {
      bap_init_polynom_mpq (&C);
      ba0_get_token_analex ();
      bap_scanf_polynom_mpq (&C);
      ba0_pull_stack ();
      bap_sub_polynom_mpq (A, &B, &C);
    }

  ba0_restore (&M);
  return A;
}

/*
 * texinfo: bap_scanf_polynom_mpq
 * General parser for polynomials.
 * It is called by @code{ba0_scanf/%Aq}.
 * The parsed polynomial is returned and assigned to @var{R} if
 * @var{R} is not the zero address.
 * Zero derivatives of parameters are not simplified to zero.
 * Exception @code{BA0_ERRALG} is raised if @var{R} is readonly.
 */

BAP_DLL void *
bap_scanf_polynom_mpq (
    void *R)
{
  struct bap_polynom_mpq *A = (struct bap_polynom_mpq *) R;
  struct bap_geobucket_mpq S;
  struct bap_polynom_mpq P;
  struct ba0_mark M;

  if (A == BAP_NOT_A_POLYNOM_mpq)
    A = bap_new_polynom_mpq ();
  else if (A->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);
  bap_init_geobucket_mpq (&S);
  bap_init_polynom_mpq (&P);

  if (!ba0_sign_token_analex ("-"))
    {
      bap_parse_and_expand_product_mpq (&P);
      ba0_get_token_analex ();
      bap_add_geobucket_mpq (&S, &P);
    }
  while (ba0_sign_token_analex ("+") || ba0_sign_token_analex ("-"))
    {
      if (ba0_sign_token_analex ("+"))
        {
          ba0_get_token_analex ();
          bap_parse_and_expand_product_mpq (&P);
          ba0_get_token_analex ();
          bap_add_geobucket_mpq (&S, &P);
        }
      else
        {
          ba0_get_token_analex ();
          bap_parse_and_expand_product_mpq (&P);
          ba0_get_token_analex ();
          bap_sub_geobucket_mpq (&S, &P);
        }
    }
  ba0_unget_token_analex (1);
  ba0_pull_stack ();
  bap_set_polynom_geobucket_mpq (A, &S);
  ba0_restore (&M);
  return A;
}

/*
 * texinfo: bap_scanf_simplify_polynom_mpq
 * Another general parser for polynomials.
 * It is called by @code{ba0_scanf/%simplify_A_}.
 * The parsed polynomial is returned and assigned to @var{R} if
 * @var{R} is not the zero address.
 * Zero derivatives of parameters are simplified to zero.
 * The fact that derivations commute together is taken into account.
 * Exception @code{BA0_ERRALG} is raised if @var{R} is readonly.
 */

BAP_DLL void *
bap_scanf_simplify_polynom_mpq (
    void *A)
{
  struct bap_polynom_mpq *P;

  P = bap_scanf_polynom_mpq (A);

  if (bav_depends_on_zero_derivatives_of_parameter_term (&P->total_rank))
    bap_simplify_zero_derivatives_of_parameter_polynom_mpq (P, P);

  return P;
}

/*
 * texinfo: bap_scanf_expanded_polynom_mpq
 * General parser for polynomials in expanded form.
 * It is called by @code{ba0_scanf/%expanded_A_}.
 * Zero derivatives of parameters are not simplified to zero.
 * The parsed polynomial is returned and assigned to @var{R} if
 * @var{R} is not the zero address.
 * Exception @code{BA0_ERRALG} is raised if @var{R} is readonly.
 */

BAP_DLL void *
bap_scanf_expanded_polynom_mpq (
    void *R)
{
  struct bap_polynom_mpq *A = (struct bap_polynom_mpq *) R;
  struct bap_creator_mpq crea;
  struct bav_term T;
  struct bav_listof_term *terms;
  struct ba0_mark M;
  struct ba0_listof_mpq *coeffs;
  ba0_int_p parentheses, nbmon;
  bool minus, plus;

  if (A == BAP_NOT_A_POLYNOM_mpq)
    A = bap_new_polynom_mpq ();
  else if (A->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  parentheses = 0;
  while (ba0_sign_token_analex ("("))
    {
      ba0_get_token_analex ();
      parentheses += 1;
    }
/*
 * First step: reading the polynomial into two lists: terms and coeffs.
 * Data are allocated in another stack
 */
  ba0_push_another_stack ();
  ba0_record (&M);
  coeffs = (struct ba0_listof_mpq *) 0;
  terms = (struct bav_listof_term *) 0;
  if (ba0_sign_token_analex ("-"))
    {
      minus = true;
      plus = false;
      ba0_get_token_analex ();
    }
  else
    {
      minus = false;
      plus = true;
    }
  bav_init_term (&T);
  nbmon = 0;
  while (minus || plus)
    {
#if ! defined (BAD_FLAG_mint_hp)
      coeffs =
          (struct ba0_listof_mpq *) ba0_cons_list (ba0_new_mpq (),
          (struct ba0_list *) coeffs);
#else
      coeffs =
          (struct ba0_listof_mpq *) ba0_cons_list (0,
          (struct ba0_list *) coeffs);
#endif
      terms =
          (struct bav_listof_term *) ba0_cons_list (bav_new_term (),
          (struct ba0_list *) terms);
/*
 * Depending on their types, numerical coefficients do not
 * start with the same sets of possible tokens
 */
#if defined (BAD_FLAG_mpz) || defined (BAD_FLAG_mpzm)
      if (ba0_type_token_analex () == ba0_integer_token ||
          (ba0_type_token_analex () == ba0_string_token &&
              ba0_strcasecmp (ba0_value_token_analex (), "factorial") == 0))
#elif defined (BAD_FLAG_mpq)
      if (ba0_type_token_analex () == ba0_integer_token ||
          (ba0_type_token_analex () == ba0_string_token &&
              ba0_strcasecmp (ba0_value_token_analex (), "factorial") == 0) ||
          ba0_sign_token_analex ("."))
#elif defined (BAD_FLAG_mint_hp)
      if (ba0_type_token_analex () == ba0_integer_token)
#endif
        {
#if !defined (BAD_FLAG_mint_hp)
          ba0_scanf_mpq (coeffs->value);
#else
/*
 * Two steps scanf. Beware to the ba0_listof_mint_hp declaration.
 * Otherwise bug on PPC 32.
 */
          {
            ba0_mint_hp c;
            ba0_scanf_mint_hp (&c);
            coeffs->value = c;
          }
#endif
          if (minus)
            {
              ba0_mpq_neg (coeffs->value, coeffs->value);
            }
          ba0_get_token_analex ();
          if (ba0_sign_token_analex ("*"))
            {
              ba0_get_token_analex ();
              bav_scanf_term (terms->value);
            }
          else
            ba0_unget_token_analex (1);
        }
      else
        {
          if (plus)
            {
              ba0_mpq_set_si (coeffs->value, 1);
            }
          else
            {
              ba0_mpq_set_si (coeffs->value, -1);
            }
          bav_scanf_term (terms->value);
        }
      bav_lcm_term (&T, &T, terms->value);
      nbmon += 1;
      ba0_get_token_analex ();
      if (ba0_sign_token_analex ("+"))
        {
          plus = true;
          minus = false;
        }
      else if (ba0_sign_token_analex ("-"))
        {
          minus = true;
          plus = false;
        }
      else
        {
          plus = false;
          minus = false;
        }
      if (plus || minus)
        ba0_get_token_analex ();
    }
  ba0_unget_token_analex (1);

  ba0_pull_stack ();

  while (parentheses)
    {
      ba0_get_token_analex ();
      if (!ba0_sign_token_analex (")"))
        BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
      parentheses -= 1;
    }
/*
 * Second step: creating the polynomial. Monomials are not sorted.
 */
  bap_begin_creator_mpq (&crea, A, &T, bap_exact_total_rank, nbmon);
  while (coeffs != (struct ba0_listof_mpq *) 0)
    {
#if ! defined (BAD_FLAG_mint_hp)
      bap_write_creator_mpq (&crea, (struct bav_term *) terms->value,
          coeffs->value);
#else
      bap_write_creator_mpq (&crea, (struct bav_term *) terms->value,
          (ba0_mpq_t) coeffs->value);
#endif
      coeffs = coeffs->next;
      terms = terms->next;
    }
  bap_close_creator_mpq (&crea);
/*
 * Last step: sorting the monomials and freeing the memory
 */
  ba0_restore (&M);
  bap_physort_polynom_mpq (A);
  return A;
}

/*
 * texinfo: bap_printf_polynom_mpq
 * General printing function for polynomials.
 * It is called by @code{ba0_printf/%Aq}.
 */

BAP_DLL void
bap_printf_polynom_mpq (
    void *R)
{
  struct bap_polynom_mpq *P = (struct bap_polynom_mpq *) R;
  struct bap_itermon_mpq iter;
  ba0_mpq_t c, *coe;
  ba0_mpq_t zero, one;
  struct bav_term T;
  bool first;
  struct ba0_mark M;
/*
 * The null case is useful in the bas library
 */
  if (P == BAP_NOT_A_POLYNOM_mpq)
    ba0_put_string ("null");
  else
    {
      ba0_record (&M);
      ba0_mpq_init_set_ui (zero, 0);
      ba0_mpq_init_set_ui (one, 1);

      if (bap_is_zero_polynom_mpq (P))
        {
          ba0_printf ("%q", zero);
          ba0_restore (&M);
          return;
        }


      bap_begin_itermon_mpq (&iter, P);
      ba0_mpq_init (c);
      bav_init_term (&T);
      first = true;
      while (!bap_outof_itermon_mpq (&iter))
        {
          coe = bap_coeff_itermon_mpq (&iter);
          bap_term_itermon_mpq (&T, &iter);
          if (first)
            {
              if (ba0_mpq_is_negative (*coe))
                {
                  ba0_put_char ('-');
#if defined (BAD_FLAG_mpzm)
                  ba0_mpz_neg (c, *coe);
#elif defined (BAD_FLAG_mint_hp)
                  c = (ba0_mint_hp) (-(ba0_int_hp) * coe);
#else
                  ba0_mpq_neg (c, *coe);
#endif
                }
              else
                {
                  ba0_mpq_set (c, *coe);
                }
            }
          else
            {
              if (ba0_mpq_is_negative (*coe))
                {
                  ba0_put_string (" - ");
#if defined (BAD_FLAG_mpzm)
                  ba0_mpz_neg (c, *coe);
#elif defined (BAD_FLAG_mint_hp)
                  c = (ba0_mint_hp) (-(ba0_int_hp) * coe);
#else
                  ba0_mpq_neg (c, *coe);
#endif
                }
              else
                {
                  ba0_put_string (" + ");
                  ba0_mpq_set (c, *coe);
                }
            }
          if (!ba0_mpq_is_one (c))
            {
#if defined (BAD_FLAG_mint_hp)
              ba0_printf_mint_hp (&c);
#else
              ba0_printf_mpq (c);
#endif
              if (!bav_is_one_term (&T) && !ba0_global.common.LaTeX)
                ba0_put_char ('*');
            }
          else if (bav_is_one_term (&T))
            {
#if defined (BAD_FLAG_mint_hp)
              ba0_printf_mint_hp (&one);
#else
              ba0_printf ("%q", one);
#endif
            }
          if (!bav_is_one_term (&T))
            bav_printf_term (&T);
          first = false;
          bap_next_itermon_mpq (&iter);
        }
      ba0_restore (&M);
    }
}

/*
 * Return true if twice the same term occurs in A
 */

static bool
bap_has_doubled_terms_mpq (
    struct bap_polynom_mpq *A)
{
  struct bap_itermon_mpq iter;
  struct bav_term *prec, *cour;
  struct ba0_mark M;
  bool doubled;

  if (bap_nbmon_polynom_mpq (A) < 2)
    return false;

  ba0_record (&M);

  prec = bav_new_term ();
  cour = bav_new_term ();
  bap_begin_itermon_mpq (&iter, A);
  bap_term_itermon_mpq (prec, &iter);
  bap_next_itermon_mpq (&iter);
  doubled = false;
  while (!doubled && !bap_outof_itermon_mpq (&iter))
    {
      bap_term_itermon_mpq (cour, &iter);
      doubled = bav_equal_term (prec, cour);
      BA0_SWAP (struct bav_term *,
          prec,
          cour);
      bap_next_itermon_mpq (&iter);
    }
  bap_close_itermon_mpq (&iter);

  ba0_restore (&M);
  return doubled;
}

/*
 * texinfo: bap_simplify_zero_derivatives_of_parameter_polynom_mpq
 * Simplify @var{A} by rewriting to zero the derivatives of the
 * parameters present in @var{P} which turn out to be zero.
 * Assign the result to @var{R}. 
 */

BAP_DLL void
bap_simplify_zero_derivatives_of_parameter_polynom_mpq (
    struct bap_polynom_mpq *R,
    struct bap_polynom_mpq *A)
{
  struct bap_geobucket_mpq G;
  struct bap_itermon_mpq iter;
  struct bap_polynom_mpq monom;
  struct bav_term T;
  ba0_mpq_t *c;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  bap_init_geobucket_mpq (&G);
  bap_init_polynom_mpq (&monom);
  bav_init_term (&T);

  bap_begin_itermon_mpq (&iter, A);
  while (!bap_outof_itermon_mpq (&iter))
    {
      c = bap_coeff_itermon_mpq (&iter);
      bap_term_itermon_mpq (&T, &iter);
      if (!bav_depends_on_zero_derivatives_of_parameter_term (&T))
        {
          bap_set_polynom_monom_mpq (&monom, *c, &T);
          bap_add_geobucket_mpq (&G, &monom);
        }
      bap_next_itermon_mpq (&iter);
    }
  bap_close_itermon_mpq (&iter);

  ba0_pull_stack ();
  bap_set_polynom_geobucket_mpq (R, &G);
  ba0_restore (&M);
}


/*
 * texinfo: bap_scanf_simplify_expanded_polynom_mpq
 * Another general parser for polynomials in expanded form.
 * It is called by @code{ba0_scanf/%simplify_expanded_A_}.
 * This one simplifies the zero derivatives of parameters
 * occurring in the parsed polynomial and takes into account
 * the fact that derivations commute.
 * The parsed polynomial is returned and assigned to @var{R} if
 * @var{R} is not the zero address.
 * Exception @code{BA0_ERRALG} is raised if @var{R} is readonly.
 */

BAP_DLL void *
bap_scanf_simplify_expanded_polynom_mpq (
    void *A)
{
  struct bap_polynom_mpq *P;

  P = bap_scanf_expanded_polynom_mpq (A);

  if (bav_depends_on_zero_derivatives_of_parameter_term (&P->total_rank)
      || bap_has_doubled_terms_mpq (P))
    bap_simplify_zero_derivatives_of_parameter_polynom_mpq (P, P);

  return P;
}

#undef BAD_FLAG_mpq
