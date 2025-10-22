#include "bad_critical_pair.h"
#include "bad_global.h"
#include "bad_stats.h"

/*
 * texinfo: bad_init_critical_pair
 * Initialize @var{pair} to an empty (meaningless) critical pair.
 */

BAD_DLL void
bad_init_critical_pair (
    struct bad_critical_pair *pair)
{
  pair->tag = bad_normal_critical_pair;
  bap_init_polynom_mpz (&pair->p);
  bap_init_polynom_mpz (&pair->q);
}

/*
 * texinfo: bad_new_critical_pair
 * Allocate a new critical pair, initialize it and return it.
 */

BAD_DLL struct bad_critical_pair *
bad_new_critical_pair (
    void)
{
  struct bad_critical_pair *pair;

  pair = (struct bad_critical_pair *) ba0_alloc (sizeof (struct
          bad_critical_pair));
  bad_init_critical_pair (pair);
  return pair;
}

/*
 * texinfo: bad_new_critical_pair_polynom_mpz
 * Return the new critical pair @math{\{p,\, q \}}.
 * Exception @code{BAD_ERRCRI} is raised if @math{\{p,\, q \}} is not 
 * a critical pair.
 */

BAD_DLL struct bad_critical_pair *
bad_new_critical_pair_polynom_mpz (
    struct bap_polynom_mpz *p,
    struct bap_polynom_mpz *q)
{
  struct bad_critical_pair *pair;
  pair = bad_new_critical_pair ();
  bad_set_critical_pair_polynom_mpz (pair, p, q);
  return pair;
}

/*
 * texinfo: bad_set_critical_pair
 * Assign @var{src} to @var{dst}.
 */

BAD_DLL void
bad_set_critical_pair (
    struct bad_critical_pair *dst,
    struct bad_critical_pair *src)
{
  bad_set_critical_pair_polynom_mpz (dst, &src->p, &src->q);
}

/*
 * texinfo: bad_set_critical_pair_polynom_mpz
 * Assign to @var{pair} the critical pair @math{\{ p, q \}}.
 * Exception @code{BAD_ERRCRI} is raised if @math{\{p,\, q \}} is not 
 * a critical pair.
 */

BAD_DLL void
bad_set_critical_pair_polynom_mpz (
    struct bad_critical_pair *pair,
    struct bap_polynom_mpz *p,
    struct bap_polynom_mpz *q)
{
  struct bav_variable *u, *v;
  u = bap_leader_polynom_mpz (p);
  v = bap_leader_polynom_mpz (q);
  if (u->root != v->root)
    BA0_RAISE_EXCEPTION (BAD_ERRCRI);
  bap_set_polynom_mpz (&pair->p, p);
  bap_set_polynom_mpz (&pair->q, q);
}

/*
 * texinfo: bad_is_a_reduction_critical_pair
 * Return @code{true} if @var{pair} is a reduction critical pair.
 * If it is and @var{var} is nonzero, assign to *@var{var} the highest 
 * of the leaders of the two pair elements.
 */

BAD_DLL bool
bad_is_a_reduction_critical_pair (
    struct bad_critical_pair *pair,
    struct bav_variable **var)
{
  struct bav_variable *u, *v;

  u = bap_leader_polynom_mpz (&pair->p);
  v = bap_leader_polynom_mpz (&pair->q);
  if (bav_is_derivative (u, v))
    {
      if (var != (struct bav_variable **) 0)
        *var = u;
      return true;
    }
  else if (bav_is_derivative (v, u))
    {
      if (var != (struct bav_variable **) 0)
        *var = v;
      return true;
    }
  else
    return false;
}

/*
 * texinfo: bad_is_an_algebraic_critical_pair
 * Return @code{true} if the two members of @var{pair}
 * have the same leader.
 */

BAD_DLL bool
bad_is_an_algebraic_critical_pair (
    struct bad_critical_pair *pair)
{
  struct bav_variable *u;
  struct bav_variable *v;

  u = bap_leader_polynom_mpz (&pair->p);
  v = bap_leader_polynom_mpz (&pair->q);

  return u == v;
}


/*
 * texinfo: bad_thetas_and_leaders_critical_pair
 * Assign to @var{leaders} the leading derivatives of the
 * elements of @var{pair} that need be differentiated in order
 * to compute the @math{\Delta}-polynomial and assign to @var{thetas}
 * the corresponding derivation operators.
 */

BAD_DLL void
bad_thetas_and_leaders_critical_pair (
    struct bav_tableof_term *thetas,
    struct bav_tableof_variable *leaders,
    struct bad_critical_pair *pair)
{
  struct bap_polynom_mpz *P1, *P2;
  struct bav_variable *u1, *u2, *u12;

  ba0_reset_table ((struct ba0_table *) thetas);
  ba0_reset_table ((struct ba0_table *) leaders);

  P1 = &pair->p;
  P2 = &pair->q;

  u1 = bap_leader_polynom_mpz (P1);
  u2 = bap_leader_polynom_mpz (P2);
  u12 = bav_lcd_variable (u1, u2);

  if (u12 == u1 || u12 == u2)
    {
      ba0_realloc2_table ((struct ba0_table *) thetas, 1,
          (ba0_new_function *) & bav_new_term);
      ba0_realloc_table ((struct ba0_table *) leaders, 1);
      thetas->size = 1;
      leaders->size = 1;
/*
 * Only the case u1 < u2 should occur but let us be on the safe side
 */
      if (u12 == u1 && u12 == u2)
        {
          bav_set_term_one (thetas->tab[0]);
          leaders->tab[0] = u1;
        }
      else if (bav_variable_number (u1) < bav_variable_number (u2))
        {
          bav_operator_between_derivatives (thetas->tab[0], u1, u2);
          leaders->tab[0] = u1;
        }
      else
        {
          bav_operator_between_derivatives (thetas->tab[0], u1, u2);
          leaders->tab[0] = u2;
        }
    }
  else
    {
      ba0_realloc2_table ((struct ba0_table *) thetas, 2,
          (ba0_new_function *) & bav_new_term);
      ba0_realloc_table ((struct ba0_table *) leaders, 2);
      thetas->size = 2;
      leaders->size = 2;

      leaders->tab[0] = u1;
      leaders->tab[1] = u2;
      bav_operator_between_derivatives (thetas->tab[0], u1, u12);
      bav_operator_between_derivatives (thetas->tab[1], u2, u12);
    }
}

/*
 * texinfo: bad_delta_polynom_critical_pair
 * Assign to @var{delta} the @math{\Delta}-polynomial generated by the
 * critical pair.
 */

BAD_DLL void
bad_delta_polynom_critical_pair (
    struct bap_polynom_mpz *delta,
    struct bad_critical_pair *pair)
{
  struct bap_polynom_mpz *P1, *P2;
  struct bap_polynom_mpz PP1, PP2, sep1, sep2;
  struct bav_variable *u1, *u2, *u12;
  struct bav_variable *s;
  struct ba0_mark M;

  bad_global.stats.critical_pairs_processed += 1;

  P1 = &pair->p;
  P2 = &pair->q;

  u1 = bap_leader_polynom_mpz (P1);
  u2 = bap_leader_polynom_mpz (P2);
  u12 = bav_lcd_variable (u1, u2);

  if (u12 == u1 || u12 == u2)
    {
/*
 * The non triangular case
 */
      if (bap_compare_polynom_mpz (P1, P2) == ba0_lt)
        {
          BA0_SWAP (struct bap_polynom_mpz *,
              P1,
              P2);
          BA0_SWAP (struct bav_variable *,
              u1,
              u2);
        }
/*
 * P2 has lower rank than P1
 */
      if (u12 == u2)
        baz_gcd_prem_polynom_mpz (delta, (struct bap_product_mpz *) 0, P1, P2,
            u2);
      else
        {
          ba0_push_another_stack ();
          ba0_record (&M);

          bap_init_polynom_mpz (&PP2);
          s = bav_derivation_between_derivatives (u12, u2);
          u2 = bav_diff_variable (u2, s->root);
          bap_diff_polynom_mpz (&PP2, P2, s->root);
          while (u2 != u12)
            {
              s = bav_derivation_between_derivatives (u12, u2);
              u2 = bav_diff_variable (u2, s->root);
              bap_diff_polynom_mpz (&PP2, &PP2, s->root);
            }

          ba0_pull_stack ();
/*
 * Beware to the case u12 = 0 (derivative of a parameter)
 */
          if (bap_depend_polynom_mpz (&PP2, u12))
            baz_gcd_prem_polynom_mpz (delta, (struct bap_product_mpz *) 0, P1,
                &PP2, u12);
          else
            bap_coeff_polynom_mpz (delta, P1, u1, 0);

          ba0_restore (&M);
        }
    }
  else
    {
/*
 * The triangular case
 */
      ba0_push_another_stack ();
      ba0_record (&M);
/*
 * Beware to the case u12 = 0 (derivative of a parameter)
 */
      bap_init_polynom_mpz (&PP1);
      s = bav_derivation_between_derivatives (u12, u1);
      u1 = bav_diff_variable (u1, s->root);
      bap_diff_polynom_mpz (&PP1, P1, s->root);
      while (u1 != u12)
        {
          s = bav_derivation_between_derivatives (u12, u1);
          u1 = bav_diff_variable (u1, s->root);
          bap_diff_polynom_mpz (&PP1, &PP1, s->root);
        }

      bap_init_polynom_mpz (&PP2);
      s = bav_derivation_between_derivatives (u12, u2);
      u2 = bav_diff_variable (u2, s->root);
      bap_diff_polynom_mpz (&PP2, P2, s->root);
      while (u2 != u12)
        {
          s = bav_derivation_between_derivatives (u12, u2);
          u2 = bav_diff_variable (u2, s->root);
          bap_diff_polynom_mpz (&PP2, &PP2, s->root);
        }

      bap_init_polynom_mpz (&sep1);
      bap_separant_polynom_mpz (&sep1, P1);
      bap_init_polynom_mpz (&sep2);
      bap_separant_polynom_mpz (&sep2, P2);

      baz_gcd_polynom_mpz (BAP_NOT_A_POLYNOM_mpz, &sep1, &sep2, &sep1, &sep2);

      if (bap_depend_polynom_mpz (&PP1, u12))
        {
          bap_reductum_polynom_mpz (&PP1, &PP1);
          PP1.readonly = false;
          bap_mul_polynom_mpz (&PP1, &PP1, &sep2);
          if (bap_leader_polynom_mpz (&PP2) != u12)
            BA0_RAISE_EXCEPTION (BAD_ERRDEL);
          bap_reductum_polynom_mpz (&PP2, &PP2);
          PP2.readonly = false;
          bap_mul_polynom_mpz (&PP2, &PP2, &sep1);
        }
      else
        {
          bap_mul_polynom_mpz (&PP1, &PP1, &sep2);
          bap_mul_polynom_mpz (&PP2, &PP2, &sep1);
        }

      ba0_pull_stack ();
      bap_sub_polynom_mpz (delta, &PP1, &PP2);

      ba0_restore (&M);
    }
}

static ba0_int_p
bad_estimated_nbmon_derivative (
    struct bap_polynom_mpz *P,
    struct bav_term *T)
{
  struct bap_itermon_mpz iter;
  struct bav_term term;
  ba0_int_p dop, degree, degree_to_dop, result, i;
  struct ba0_mark M;

  ba0_record (&M);

  result = 0;
  dop = bav_total_degree_term (T);
  bap_begin_itermon_mpz (&iter, P);
  bav_init_term (&term);
  while (!bap_outof_itermon_mpz (&iter))
    {
      bap_term_itermon_mpz (&term, &iter);
      degree = bav_total_degree_term (&term);
      degree_to_dop = 1;
      for (i = 0; i < dop; i++)
        degree_to_dop *= degree;
      result += degree_to_dop;
      bap_next_itermon_mpz (&iter);
    }
  bap_close_itermon_mpz (&iter);

  ba0_restore (&M);
  return result;
}

static ba0_int_p
bad_estimated_nbmon_delta_polynomial (
    struct bad_critical_pair *pair)
{
  struct bap_polynom_mpz *P1, *P2;
  struct bav_term T;
  struct bav_variable *u1, *u2, *u12;
  ba0_int_p d1, d2;
  struct ba0_mark M;

  ba0_record (&M);
  P1 = &pair->p;
  P2 = &pair->q;
  u1 = bap_leader_polynom_mpz (P1);
  u2 = bap_leader_polynom_mpz (P2);
  u12 = bav_lcd_variable (u1, u2);
  bav_init_term (&T);
  bav_operator_between_derivatives (&T, u1, u12);
  d1 = bad_estimated_nbmon_derivative (P1, &T);
  bav_operator_between_derivatives (&T, u2, u12);
  d2 = bad_estimated_nbmon_derivative (P2, &T);
  ba0_restore (&M);
  return d1 + d2;
}

/*
 * texinfo: bad_is_a_simpler_critical_pair
 * Heuristic function which returns @code{true} if @var{P} should be considered 
 * before @var{Q} in a list of critical pairs waiting for being processed,
 * according to @var{strategy}.
 * This function is used to sort the lists of critical pairs
 * occurring in quadruples. It is based on estimates of the sizes of the
 * @math{\Delta}-polynomials. Critical pairs whose @math{\Delta}-polynomials
 * have fewer monomials are considered simpler. 
 */

BAD_DLL bool
bad_is_a_simpler_critical_pair (
    struct bad_critical_pair *P,
    struct bad_critical_pair *Q,
    struct bad_selection_strategy *strategy)
{
  struct bav_variable *a, *b;
  bav_Iorder ord_a, ord_b;
  bav_Inumber num_a, num_b;
  ba0_int_p nbm_a, nbm_b;
  ba0_int_p penalty_a, penalty_b;
/*
 * Compare the sizes of the Delta-Polynomials
 * The criterion is used as a penalty.
 */
  nbm_a = bad_estimated_nbmon_delta_polynomial (P);
  nbm_b = bad_estimated_nbmon_delta_polynomial (Q);

  penalty_a = P->tag == bad_normal_critical_pair ? 1 : strategy->penalty;
  penalty_b = Q->tag == bad_normal_critical_pair ? 1 : strategy->penalty;

  nbm_a *= penalty_a;
  nbm_b *= penalty_b;

  if (nbm_a < nbm_b)
    return true;
  else if (nbm_a > nbm_b)
    return false;
/*
 * Compare the orders of the variables
 */
  a = bav_lcd_variable (bap_leader_polynom_mpz (&P->p),
      bap_leader_polynom_mpz (&P->q));
  b = bav_lcd_variable (bap_leader_polynom_mpz (&Q->p),
      bap_leader_polynom_mpz (&Q->q));

  ord_a = bav_total_order_variable (a);
  ord_b = bav_total_order_variable (b);

  if (ord_a < ord_b)
    return true;
  else if (ord_a > ord_b)
    return false;
/*
 * Compare a and b with respect to the ranking
 */
  num_a = bav_variable_number (a);
  num_b = bav_variable_number (b);

  if (num_a < num_b)
    return true;
  else if (num_a > num_b)
    return false;
/*
 * To avoid warnings
 */
  return false;
}

/*
 * texinfo: bad_scanf_critical_pair
 * The parsing function for critical pairs.
 * It is called by @code{ba0_scanf/%critical_pair}.
 */

BAD_DLL void *
bad_scanf_critical_pair (
    void *A)
{
  struct bad_critical_pair *pair;

  if (A == (void *) 0)
    pair = bad_new_critical_pair ();
  else
    pair = (struct bad_critical_pair *) A;

  ba0_scanf ("{%Az, %Az}", &pair->p, &pair->q);

  return pair;
}

/*
 * texinfo: bad_printf_critical_pair
 * The printing function for critical pairs.
 * It is called by @code{ba0_printf/%critical_pair}.
 */

BAD_DLL void
bad_printf_critical_pair (
    void *A)
{
  struct bad_critical_pair *pair = (struct bad_critical_pair *) A;

  if (pair->tag == bad_normal_critical_pair)
    ba0_printf ("(normal)");
  else
    ba0_printf ("(rejected)");

  if (ba0_global.common.LaTeX)
    ba0_printf ("\\{%Az,\\, %Az\\}", &pair->p, &pair->q);
  else
    ba0_printf ("{%Az, %Az}", &pair->p, &pair->q);
}

/*
 * Readonly static data
 */

static char _critical[] = "struct bad_critical_pair";

BAD_DLL ba0_int_p
bad_garbage1_critical_pair (
    void *A,
    enum ba0_garbage_code code)
{
  struct bad_critical_pair *pair = (struct bad_critical_pair *) A;
  ba0_int_p n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (pair, sizeof (struct bad_critical_pair), _critical);
  n += bap_garbage1_polynom_mpz (&pair->p, ba0_embedded);
  n += bap_garbage1_polynom_mpz (&pair->q, ba0_embedded);

  return n;
}

BAD_DLL void *
bad_garbage2_critical_pair (
    void *A,
    enum ba0_garbage_code code)
{
  struct bad_critical_pair *pair;

  if (code == ba0_isolated)
    pair = (struct bad_critical_pair *) ba0_new_addr_gc_info (A, _critical);
  else
    pair = (struct bad_critical_pair *) A;

  bap_garbage2_polynom_mpz (&pair->p, ba0_embedded);
  bap_garbage2_polynom_mpz (&pair->q, ba0_embedded);

  return pair;
}

BAD_DLL void *
bad_copy_critical_pair (
    void *A)
{
  struct bad_critical_pair *pair;

  pair = bad_new_critical_pair ();
  bad_set_critical_pair (pair, (struct bad_critical_pair *) A);
  return pair;
}

/*
 * texinfo: bad_is_a_listof_rejected_critical_pair
 * Return @code{true} if the elements of @var{L} are all rejected
 * critical pairs. This function is used by @code{bad_pardi} and
 * @code{bad_Rosenfeld_Groebner} to stop their main loops.
 */

BAD_DLL bool
bad_is_a_listof_rejected_critical_pair (
    struct bad_listof_critical_pair *L)
{
  while (L != (struct bad_listof_critical_pair *) 0)
    {
      if (L->value->tag == bad_normal_critical_pair)
        return false;
      L = L->next;
    }
  return true;
}
