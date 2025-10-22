#include "baz_polyspec_mpz.h"
#include "baz_gcd_polynom_mpz.h"
#include "baz_factor_polynom_mpz.h"

/* 
 * Sets R to F multiplied by the unique polynomial P in Z[v]
 * with maxnorm less than n/2 and such that P(n) = c. 
 * The basis n is assumed to be odd.
 */

static void
baz_genpoly0_polynom_mpz (
    struct bap_polynom_mpz *R,
    ba0_mpz_t c,
    ba0_mpz_t n,
    struct bav_variable *v,
    struct bav_term *F)
{
  struct bap_creator_mpz crea;
  struct bav_term T;
  struct bav_rank rg;
  ba0_mpz_t a, b, q, r, pom_b_sur_2;
  ba0_int_p sgn_a;
  bav_Idegree d;
  struct ba0_mark M;

  if (ba0_mpz_even_p (n))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_mpz_init_set (a, c);
  ba0_mpz_init_set (b, n);
  ba0_mpz_init (q);
  ba0_mpz_init (r);

  sgn_a = ba0_mpz_sgn (a);

  ba0_mpz_init (pom_b_sur_2);
  ba0_mpz_tdiv_q_2exp (pom_b_sur_2, b, 1);      /* +/- b/2 */
  if (sgn_a < 0)
    ba0_mpz_neg (pom_b_sur_2, pom_b_sur_2);

  bav_init_term (&T);
  bav_realloc_term (&T, F->size + 1);
  rg.var = v;
  rg.deg = d = ba0_mpz_sizeinbase (a, 2);
  bav_mul_term_rank (&T, F, &rg);

  ba0_pull_stack ();
  bap_begin_creator_mpz (&crea, R, &T, bap_approx_total_rank, d);
  ba0_push_another_stack ();

  d = -1;
  while (sgn_a != 0)
    {
      d += 1;
      ba0_mpz_tdiv_qr (q, r, a, b);     /* sgn (r) = sgn (a) */
      if (sgn_a > 0)
        {
          if (ba0_mpz_cmp (r, pom_b_sur_2) >= 0)
            {
              ba0_mpz_sub (r, r, b);
              ba0_mpz_add_ui (a, q, 1);
            }
          else
            ba0_mpz_set (a, q);
        }
      else
        {
          if (ba0_mpz_cmp (r, pom_b_sur_2) <= 0)
            {
              ba0_mpz_add (r, r, b);
              ba0_mpz_sub_ui (a, q, 1);
            }
          else
            ba0_mpz_set (a, q);
        }
      sgn_a = ba0_mpz_sgn (a);
      if (ba0_mpz_cmp_ui (r, (unsigned long int) 0) != 0)
        {
          if (d > 0)
            {
              rg.var = v;
              rg.deg = d;
              bav_mul_term_rank (&T, F, &rg);
            }
          else
            bav_set_term (&T, F);
          ba0_pull_stack ();
          bap_write_creator_mpz (&crea, &T, r);
          ba0_push_another_stack ();
        }
    }
  ba0_pull_stack ();
  bap_close_creator_mpz (&crea);
  bap_reverse_polynom_mpz (R);
  ba0_restore (&M);
}

/*
 * texinfo: baz_genpoly_polynom_mpz
 * Assume @math{A \in Z [x_1,\ldots,x_\ell]}.
 * Assigns to @var{R} the unique polynomial of @math{Z [x_1,\ldots,x_\ell,\,v]}
 * such that @var{R} is equal to @var{A} modulo @math{(v-n)} and
 * maxnorm of @var{R} is less than @math{n/2}.
 * Exception @code{BA0_ERRALG} is raised if @var{n} is even.
 */

BAZ_DLL void
baz_genpoly_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A,
    ba0_mpz_t n,
    struct bav_variable *v)
{
  struct bap_itermon_mpz iter;
  struct bap_polynom_mpz *B, *G;
  struct bav_term T;
  ba0_mpz_t *c;
  struct ba0_mark M;

  if (ba0_mpz_even_p (n))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  ba0_push_another_stack ();
  ba0_record (&M);
  B = bap_new_polynom_mpz ();
  G = bap_new_polynom_mpz ();
  bav_init_term (&T);
  bap_begin_itermon_mpz (&iter, A);
  while (!bap_outof_itermon_mpz (&iter))
    {
      c = bap_coeff_itermon_mpz (&iter);
      bap_term_itermon_mpz (&T, &iter);
      baz_genpoly0_polynom_mpz (B, *c, n, v, &T);
      bap_add_polynom_mpz (G, G, B);
      bap_next_itermon_mpz (&iter);
    }
  ba0_pull_stack ();
  bap_set_polynom_mpz (R, G);
  ba0_restore (&M);
}

/*
 * texinfo: baz_yet_another_point_int_p_mpz
 * Assign to @var{point} a new evaluation point which does not annihilate
 * any of the polynomials in nonzero and does not evaluate any
 * factor of prod to @math{0, \pm 1, \pm 2}.
 * All variables present in @var{nonzero} and @var{prod} must occur
 * in @var{point}.
 * At least one of the variables present in @var{nonzero} or @var{prod}, 
 * and one of the variables which are not present in 
 * @var{nonzero} or @var{prod}, are guaranteed to be modified (if any). 
 * The variable avoid is not touched. 
 * It is allowed to be @code{BAV_NOT_A_VARIABLE}.
 * Exception @code{BA0_ERRALG} is raised if no value can be modified.
 */

BAZ_DLL void
baz_yet_another_point_int_p_mpz (
    struct bav_point_int_p *point,
    struct bap_tableof_polynom_mpz *nonzero,
    struct bap_product_mpz *prod,
    struct bav_variable *avoid)
{
  ba0_mpz_t value;
  ba0_int_p n, i, a, indmin, indmax, minimum, maximum, nbloops, incr;
  bool bad_point = false, modified[2];
  struct bav_dictionary_variable dict;
  struct bav_tableof_variable T;
  struct ba0_mark M;

  if (point->size == 0 || (point->size == 1 && avoid == point->tab[0]->var))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  for (i = 0; i < nonzero->size; i++)
    if (bap_is_zero_polynom_mpz (nonzero->tab[i]))
      BA0_RAISE_EXCEPTION (BA0_ERRALG);

  modified[0] = false;
  modified[1] = false;

  ba0_push_another_stack ();
  ba0_record (&M);
/*
 * The variables actually present in nonzero
 */
  bav_init_dictionary_variable (&dict, 8);
  ba0_init_table ((struct ba0_table *) &T);
  ba0_realloc_table ((struct ba0_table *) &T, 256);

//  bav_R_mark_variables (false);
  for (i = 0; i < nonzero->size; i++)
    bap_mark_indets_polynom_mpz (&dict, &T, nonzero->tab[i]);
  for (i = 0; i < prod->size; i++)
    bap_mark_indets_polynom_mpz (&dict, &T, &prod->tab[i].factor);
//  bav_R_marked_variables (&T, true);

  ba0_mpz_init (value);
/*
 * First turn: modify a variable in nonzero or nonzero_one_two
 * Second turn: modify a variable outside nonzero
 */
  nbloops = 0;
  incr = 1;
  for (n = 0; n < 2; n++)
    {
      if (n == 0 && T.size == 0)
        continue;
      else if (n == 1 && T.size == point->size)
        continue;
/*
 * loop while the evaluation point is bad
 */
      indmin = -1;
      indmax = -1;
      do
        {
          minimum = BA0_MAX_INT_P;
          maximum = -BA0_MAX_INT_P;
          modified[n] = false;
          for (i = 0; i < point->size; i++)
            {
              if (point->tab[i]->var != avoid && ((n == 0
                          && ba0_member_table (point->tab[i]->var,
                              (struct ba0_table *) &T)) || (n == 1
                          && !ba0_member_table (point->tab[i]->var,
                              (struct ba0_table *) &T))))
                {
                  a = BA0_ABS (point->tab[i]->value);
                  if (a < minimum)
                    {
                      modified[n] = true;
                      indmin = i;
                      minimum = a;
                    }
                  if (a >= maximum)
                    {
                      modified[n] = true;
                      indmax = i;
                      maximum = a;
                    }
                }
            }
/*
 * The idea consists in modifying a variable with a minimal absolute value.
 */
          if (modified[n])
            {
              if (indmin == indmax || minimum != maximum)
                {
                  if (point->tab[indmin]->value > 0)
                    point->tab[indmin]->value =
                        -incr - point->tab[indmin]->value;
                  else
                    point->tab[indmin]->value =
                        incr - point->tab[indmin]->value;
                }
              else
                {
                  if (point->tab[indmax]->value > 0)
                    point->tab[indmax]->value =
                        -incr - point->tab[indmax]->value;
                  else
                    point->tab[indmax]->value =
                        incr - point->tab[indmax]->value;
                  point->tab[indmin]->value = 0;
                }
/*
 * At the second turn, the evaluation point is necessary good since the
 * values of nonzero are not modified.
 */
              bad_point = false;
              if (n == 0)
                {
                  for (i = 0; !bad_point && i < nonzero->size; i++)
                    {
                      if (!bap_is_numeric_polynom_mpz (nonzero->tab[i]))
                        {
                          bap_eval_to_numeric_at_point_int_p_polynom_mpz
                              (&value, nonzero->tab[i], point);
                          bad_point = ba0_mpz_sgn (value) == 0;
                        }
                    }
                  for (i = 0; !bad_point && i < prod->size; i++)
                    {
                      if (!bap_is_numeric_polynom_mpz (&prod->tab[i].factor))
                        {
                          bap_eval_to_numeric_at_point_int_p_polynom_mpz
                              (&value, &prod->tab[i].factor, point);
                          ba0_mpz_abs (value, value);
                          bad_point =
                              ba0_mpz_cmp_ui (value,
                              (unsigned long int) 2) <= 0;
                        }
                    }
                }
            }
          nbloops += 1;
          incr += 1;
        }
      while (bad_point);
    }
/*
    ba0_printf ("nbloops = %d\n", nbloops);
 */
  if (!modified[0] && !modified[1])
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  ba0_pull_stack ();
  ba0_restore (&M);
}

/***********************************************************************
 * HENSEL LIFTING - USED BY GCD AND FACTOR
 *
 * Data structure for Hensel lifting.
 * 
 * A is apolynomial in Z [x, y1, ..., yk], leader = x.
 * point is an evaluation point [y1 = a1, ..., yk = ak].
 * factors_mod_point is a factorization of lifting mod (point).
 * Its elements are polynomials in Z[x].
 * p is a prime number such that the elements of factors_mod_point
 * are relativaly prime in Z/pZ[x].
 * l is an exponent, up to which one wishes to lift the factorization
 * 
 *       A = factors_mod_point mod (point).
 *
 * initial is the initial of A.
 * factors_initial is a factorization of initial in Z [x, y1, ..., yk].
 */


BAZ_DLL void
baz_HL_init_ideal_lifting (
    struct baz_ideal_lifting *lifting)
{
  lifting->A = bap_new_polynom_mpz ();
  lifting->initial = bap_new_polynom_mpz ();
  bap_init_product_mpz (&lifting->factors_initial);
  bap_init_product_mpzm (&lifting->factors_mod_point);
  ba0_init_point ((struct ba0_point *) &lifting->point);
  ba0_mpz_init (lifting->p);
  lifting->l = 1;
}

BAZ_DLL void
baz_HL_printf_ideal_lifting (
    void *z)
{
  struct baz_ideal_lifting *lif = (struct baz_ideal_lifting *) z;

  ba0_put_string ("----------------------\n");
  ba0_printf ("A = %Az\n", lif->A);
  ba0_printf ("initial = %Az\n", lif->initial);
  ba0_printf ("factors_initial = %Pzm\n", &lif->factors_initial);
  ba0_printf ("factors_mod_point = %Pz\n", &lif->factors_mod_point);
  ba0_printf ("point = %t[%value(%d)]\n", &lif->point);
  ba0_printf ("p = %z\n", &lif->p);
  ba0_put_string ("l = ");
  ba0_put_int_p (lif->l);
  ba0_put_char ('\n');
  ba0_put_string ("----------------------\n");
}

/***********************************************
 REDISTRIBUTION OF THE FACTORS OF THE INITIAL
 ***********************************************/

/*
 * entiers is a table of lifting->factors_initial.size + 1 integers.
 * diviseurs also (or the zero pointer).
 * Assigns to diviseurs [i] an integer which does not divide any
 * 	entier [i] for j < i/
 * Exception BAZ_EXHDIS if impossible
 *
 */

BAZ_DLL void
baz_HL_integer_divisors (
    ba0_mpz_t *diviseurs,
    struct baz_ideal_lifting *lifting,
    ba0_mpz_t *entiers)
{
  ba0_mpz_t r, *tab;
  ba0_int_p i, j, n;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  n = lifting->factors_initial.size + 1;

  tab = (ba0_mpz_t *) ba0_alloc (sizeof (ba0_mpz_t) * n);
  ba0_mpz_init (r);

  for (i = 0; i < n; i++)
    {
      ba0_mpz_init_set (tab[i], entiers[i]);
      ba0_mpz_abs (tab[i], tab[i]);
      if (ba0_mpz_sgn (tab[i]) == 0)
        BA0_RAISE_EXCEPTION (BAZ_EXHDIS);
      for (j = i - 1; j >= 0; j--)
        {
          ba0_mpz_set (r, tab[j]);
          while (ba0_mpz_cmp_ui (r, 1) != 0)
            {
              ba0_mpz_gcd (r, r, tab[i]);
              ba0_mpz_divexact (tab[i], tab[i], r);
              if (ba0_mpz_cmp_ui (tab[i], 1) == 0)
                BA0_RAISE_EXCEPTION (BAZ_EXHDIS);
            }
        }
      if (diviseurs != (ba0_mpz_t *) 0)
        {
          ba0_pull_stack ();
          ba0_mpz_set (diviseurs[i], tab[i]);
          ba0_push_another_stack ();
        }
    }
  ba0_pull_stack ();
  ba0_restore (&M);
}

/*
 * factinit_mod_point contains the factors of the initial of lifting->A,
 * 	evaluated at point.
 * R    = lifting->A mod point.
 * cont = content of R.
 */

BAZ_DLL void
baz_HL_end_redistribute (
    struct baz_ideal_lifting *lifting,
    ba0_mpz_t *factinit_mod_point,
    struct bap_polynom_mpz *R,
    ba0_mpz_t cont)
{
  ba0_mpz_t *lc;
  ba0_mpz_t foo, bar, rha;
  struct bap_product_mpz new_factors_initial;
  struct bap_product_mpz new_factors_mod_point;
  struct bap_polynom_mpz tmp;
  ba0_int_p j, k;
  bav_Idegree e, m;
  bool lc_negatif;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  lc = bap_numeric_initial_polynom_mpz (R);
  lc_negatif = ba0_mpz_sgn (*lc) < 0;
/*
   cont is the content de lifting->A mod point.

   new_factors_initial = (1, ...,1). Length = the number of factors 
	of A mod point (2 in the case of the gcd).

   new_factors_initial.tab [j].factor = lcU [j]
 */

  bap_init_product_mpz (&new_factors_initial);
  bap_realloc_product_mpz (&new_factors_initial,
      lifting->factors_mod_point.size);
  for (j = 0; j < lifting->factors_mod_point.size; j++)
    bap_set_polynom_one_mpz (&new_factors_initial.tab[j].factor);
  new_factors_initial.size = lifting->factors_mod_point.size;

  ba0_mpz_init (foo);
  ba0_mpz_init (bar);

  bap_init_polynom_mpz (&tmp);

  for (k = lifting->factors_initial.size - 1; k >= 0; k--)
    {
/*
   factinit_mod_point [k] = fval
 */
      e = lifting->factors_initial.tab[k].exponent;
      for (j = 0; j < lifting->factors_mod_point.size && e > 0; j++)
        {
/*
   foo = lcu
   bar = intermediate struct bav_variable * 
 */
          lc = bap_numeric_initial_polynom_mpzm (&lifting->factors_mod_point.
              tab[j].factor);
          ba0_mpz_mul (foo, *lc, cont);
          bap_eval_to_numeric_at_point_int_p_polynom_mpz (&bar,
              &new_factors_initial.tab[j].factor, &lifting->point);
          ba0_mpz_divexact (foo, foo, bar);
          m = 0;
          for (;;)
            {
              if (m >= e)
                break;
              ba0_mpz_tdiv_qr (foo, bar, foo, factinit_mod_point[k]);
              if (ba0_mpz_sgn (bar) != 0)
                break;
              m++;
            }
          bap_pow_polynom_mpz (&tmp, &lifting->factors_initial.tab[k].factor,
              m);
          bap_mul_polynom_mpz (&new_factors_initial.tab[j].factor,
              &new_factors_initial.tab[j].factor, &tmp);
          e -= m;
        }
      if (e != 0)
        BA0_RAISE_EXCEPTION (BAZ_EXHDIS);
    }
/*
   One copies factors_mod_point in new_factors_mod_point.
   The possible sign is carried by the last factor.

   For the cast, see the comments at the beginning of the function.
 */
  bap_init_product_mpz (&new_factors_mod_point);
  ba0_mpz_set_ui (lifting->factors_mod_point.num_factor, 1);
  bap_set_product_mpz (&new_factors_mod_point,
      (struct bap_product_mpz *) &lifting->factors_mod_point);
  if (lc_negatif)
    {
      j = lifting->factors_mod_point.size - 1;
      bap_neg_polynom_mpz (&new_factors_mod_point.tab[j].factor,
          (struct bap_polynom_mpz *) &lifting->factors_mod_point.tab[j].factor);
    }
/*
   One adjusts what is left in cont.
 */
  if (ba0_mpz_cmp_ui (cont, 1) == 0)
    {
      for (j = 0; j < new_factors_mod_point.size; j++)
        {
          lc = bap_numeric_initial_polynom_mpz (&new_factors_mod_point.tab[j].
              factor);
          bap_eval_to_numeric_at_point_int_p_polynom_mpz (&foo,
              &new_factors_initial.tab[j].factor, &lifting->point);
          ba0_mpz_divexact (foo, *lc, foo);
          bap_mul_polynom_numeric_mpz (&new_factors_initial.tab[j].factor,
              &new_factors_initial.tab[j].factor, foo);
        }
    }
  else
    {
      ba0_mpz_init (rha);
      for (j = 0; j < new_factors_mod_point.size; j++)
        {
/*
   foo = lcUval
   bar = g
   rha = lcu / g puis lcUval / g
 */
          lc = bap_numeric_initial_polynom_mpz (&new_factors_mod_point.tab[j].
              factor);
          bap_eval_to_numeric_at_point_int_p_polynom_mpz (&foo,
              &new_factors_initial.tab[j].factor, &lifting->point);
          ba0_mpz_gcd (bar, *lc, foo);
          ba0_mpz_divexact (rha, *lc, bar);
          bap_mul_polynom_numeric_mpz (&new_factors_initial.tab[j].factor,
              &new_factors_initial.tab[j].factor, rha);
          ba0_mpz_divexact (rha, foo, bar);
          bap_mul_polynom_numeric_mpz (&new_factors_mod_point.tab[j].factor,
              &new_factors_mod_point.tab[j].factor, rha);
          ba0_mpz_divexact (cont, cont, rha);
        }
      if (ba0_mpz_cmp_ui (cont, 1) != 0)
        {
          for (j = 0; j < new_factors_mod_point.size; j++)
            {
              bap_mul_polynom_numeric_mpz (&new_factors_mod_point.tab[j].factor,
                  &new_factors_mod_point.tab[j].factor, cont);
              bap_mul_polynom_numeric_mpz (&new_factors_initial.tab[j].factor,
                  &new_factors_initial.tab[j].factor, cont);
            }
/*
   Only case where A gets modified.
 */
          ba0_mpz_pow_ui (cont, cont, new_factors_mod_point.size - 1);
          ba0_pull_stack ();
          bap_mul_polynom_numeric_mpz (lifting->A, lifting->A, cont);
          ba0_push_another_stack ();
        }
    }
  ba0_pull_stack ();
  bap_set_product_mpz (&lifting->factors_initial, &new_factors_initial);
  bap_set_product_mpzm (&lifting->factors_mod_point,
      (struct bap_product_mpzm *) &new_factors_mod_point);
  ba0_restore (&M);
}

/*
 * Initializes the variables factinit_mod_point, R and cont.
 *
 * Assigns (a, b1, ..., bn) to factinit_mod_point where: 
 * a :  the content of the polynomial to be lifted, multiplied by the 
 * 	numerical factor of its initial.
 * bi : the factors of the initial mod point.
 *
 * One assigns lifting->A mod point to R and its content to cont.
 */

BAZ_DLL void
baz_HL_begin_redistribute (
    struct baz_ideal_lifting *lifting,
    ba0_mpz_t *factinit_mod_point,
    struct bap_polynom_mpz *R,
    ba0_mpz_t cont)
{
  ba0_int_p i;

  for (i = 0; i < lifting->factors_initial.size; i++)
    bap_eval_to_numeric_at_point_int_p_polynom_mpz (&factinit_mod_point[i + 1],
        &lifting->factors_initial.tab[i].factor, &lifting->point);
  bap_evalcoeff_at_point_int_p_polynom_mpz (R, lifting->A, &lifting->point);

  bap_numeric_content_polynom_mpz (cont, R);
  ba0_mpz_mul (factinit_mod_point[0], cont,
      lifting->factors_initial.num_factor);
}

/*
 * Modifies A, factors_mod_point and factors_initial.
 *
 * Essentially, this is factors_initial which is modified.
 * One reduces this product to as many factors as there are factors
 * to be lifted (i.e. |factors_mod_point|) by grouping some factors.
 *
 * new_factors_mod_point has type ba0_mpz.
 * - lifting->factors_mod_point, which is in symmetric representation,
 *   is viewed as a bap_product_mpz.
 * - At the end, new_factors_mod_point is reassigned as is to 
 *   lifting->factors_mod_point (one keeps the symmetric representation
 *   modulo lifting->p ^ lifting->l).
 *
 * Function split as two functions to save one computation in the 
 * factor case.
 */

BAZ_DLL void
baz_HL_redistribute_the_factors_of_the_initial (
    struct baz_ideal_lifting *lifting)
{
  ba0_mpz_t *factinit_mod_point;
  ba0_mpz_t cont;
  struct bap_polynom_mpz R;
  ba0_int_p i;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  factinit_mod_point =
      (ba0_mpz_t *) ba0_alloc (sizeof (ba0_mpz_t) * (1 +
          lifting->factors_initial.size));
  for (i = 0; i < 1 + lifting->factors_initial.size; i++)
    ba0_mpz_init (factinit_mod_point[i]);

  bap_init_polynom_mpz (&R);
  ba0_mpz_init (cont);

  baz_HL_begin_redistribute (lifting, factinit_mod_point, &R, cont);
  baz_HL_integer_divisors ((ba0_mpz_t *) 0, lifting, factinit_mod_point);
  ba0_pull_stack ();
  baz_HL_end_redistribute (lifting, factinit_mod_point + 1, &R, cont);
  ba0_restore (&M);
}

/*
 * Computations are modulo lifting->p ^ lifting->l which is assumed
 * to bound the maxnorms of the polynomials of lifting.
 * Symmetric representation everywhere.
 */

BAZ_DLL void
baz_HL_ideal_Hensel_lifting (
    struct bap_product_mpz *lifted_factors,
    struct baz_ideal_lifting *lifting)
{
  ba0_int_p i, j, k, nb_x, nb_f;
  bav_Idegree maxdeg;
  struct bap_polynom_mpzm *A_eval, *lc_A_eval;
  ba0_mpz_t *value;
  struct bap_polynom_mpzm *E, *C, *monome;
  struct bap_product_mpzm new_factors, old_factors;
  struct bap_polynom_mpzm *sigma;
  ba0_int_p *perm, nb_perm;
  struct bap_polynom_mpz *Z;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_mpzm_module_pow_ui (lifting->p, lifting->l, true);

  nb_x = lifting->point.size;
  nb_f = lifting->factors_mod_point.size;

  A_eval =
      (struct bap_polynom_mpzm *) ba0_alloc (sizeof (struct bap_polynom_mpzm) *
      (nb_x + 1));
  lc_A_eval =
      (struct bap_polynom_mpzm *) ba0_alloc (sizeof (struct bap_polynom_mpzm) *
      (nb_x + 1) * nb_f);
  value = (ba0_mpz_t *) ba0_alloc (sizeof (ba0_mpz_t) * nb_x);
/*
   [x0 = a0, ..., x{nb_x-1} = a{nb_x-1}]
   lifting = A = f0 * ... * f{nb_f-1}.

   for 0 <= j < nb_x

	value [j] = aj

   for 0 <= j < nb_x + 1

	A_eval [j] = A mod (x_j = aj, ..., x{nb_x-1} = a{nb_x-1}, p^l) 
	lc_A_eval [j * nb_f + i] = fi mod 
			   (x_j = aj, ..., x{nb_x-1} = a{nb_x-1}, p^l)
 */
  bap_init_polynom_mpzm (&A_eval[nb_x]);
  bap_set_polynom_mpzm (&A_eval[nb_x], (struct bap_polynom_mpzm *) lifting->A);

  for (i = 0; i < nb_f; i++)
    {
      bap_init_polynom_mpzm (&lc_A_eval[nb_x * nb_f + i]);
      bap_set_polynom_mpzm (&lc_A_eval[nb_x * nb_f + i],
          (struct bap_polynom_mpzm *) &lifting->factors_initial.tab[i].factor);
    }
  for (j = nb_x - 1; j >= 0; j--)
    {
      bap_init_polynom_mpzm (&A_eval[j]);
      ba0_mpzm_init_set_si (value[j], lifting->point.tab[j]->value);
      bap_eval_to_polynom_at_numeric_polynom_mpzm (&A_eval[j], &A_eval[j + 1],
          lifting->point.tab[j]->var, value[j]);
      for (i = 0; i < nb_f; i++)
        {
          bap_init_polynom_mpzm (&lc_A_eval[j * nb_f + i]);
          bap_eval_to_polynom_at_numeric_polynom_mpzm (&lc_A_eval[j * nb_f + i],
              &lc_A_eval[(j + 1) * nb_f + i], lifting->point.tab[j]->var,
              value[j]);
        }
    }
/* 
   maxdeg = max degree (for all variables).
   Hensel lifting modulo point^maxdeg.
 */
  for (i = 1, maxdeg = 0; i < lifting->A->total_rank.size; i++)
    if (lifting->A->total_rank.rg[i].deg > maxdeg)
      maxdeg = lifting->A->total_rank.rg[i].deg;

  E = bap_new_polynom_mpzm ();
  C = bap_new_polynom_mpzm ();
  bap_init_product_mpzm (&old_factors);
  bap_init_product_mpzm (&new_factors);
  bap_set_product_mpzm (&new_factors, &lifting->factors_mod_point);
  sigma =
      (struct bap_polynom_mpzm *) ba0_alloc (sizeof (struct bap_polynom_mpzm) *
      nb_f);
  for (i = 0; i < nb_f; i++)
    bap_init_polynom_mpzm (&sigma[i]);
/*
   new_factors in symmetric representation.
 */
  Z = bap_new_polynom_mpz ();
/*
   (perm, nb_perm) encodes a permutation in new_factors.
   Useful when a true factor is identified (one moves it to the
	end and one decrements the number of factors).
 */
  perm = (ba0_int_p *) ba0_alloc (sizeof (ba0_int_p) * nb_f);

  for (j = 0; j < nb_x; j++)
    {
      bap_mods_polynom_mpzm ((struct bap_polynom_mpz *) &A_eval[j + 1],
          &A_eval[j + 1]);

      bap_set_product_mpzm (&old_factors, &new_factors);
      monome = bap_new_polynom_one_mpzm ();
      for (i = 0; i < nb_f; i++)
        bap_replace_initial_polynom_mpzm (&new_factors.tab[i].factor,
            &new_factors.tab[i].factor, &lc_A_eval[(j + 1) * nb_f + i]);
      bap_expand_product_mpzm (E, &new_factors);
      bap_sub_polynom_mpzm (E, &A_eval[j + 1], E);
      nb_perm = 0;
      k = 1;
      while (!bap_is_zero_polynom_mpzm (E)
          && k <= bap_degree_polynom_mpzm (&A_eval[j + 1],
              lifting->point.tab[j]->var))
        {
          bap_mul_polynom_value_int_p_mpzm (monome, monome,
              lifting->point.tab[j]);
          bap_coeftayl_polynom_mpzm (C, E, lifting->point.tab[j], k);
          if (!bap_is_zero_polynom_mpzm (C))
            {
              lifting->point.size = j;
              bap_multi_Diophante_polynom_mpzm (sigma, &old_factors, C,
                  &lifting->point, maxdeg, lifting->p, lifting->l);
              lifting->point.size = nb_x;
/*
 * In the frequent case of 2 factors, one computes the new value of E
 * by updating the old one.
 */
              if (new_factors.size == 2)
                {
                  struct bap_polynom_mpzm *temp1, *temp2, *psigma;
                  struct ba0_mark M;

                  ba0_push_another_stack ();
                  ba0_record (&M);
                  temp1 = bap_new_polynom_mpzm ();
                  temp2 = bap_new_polynom_mpzm ();
                  bap_mul_polynom_mpzm (temp1, monome, monome);
                  psigma = bap_new_polynom_mpzm ();
                  bap_mul_polynom_mpzm (psigma, &sigma[0], &sigma[1]);
                  bap_mul_polynom_mpzm (psigma, psigma, temp1);
                  bap_mul_polynom_mpzm (temp1, &sigma[0],
                      &new_factors.tab[1].factor);
                  bap_mul_polynom_mpzm (temp2, &sigma[1],
                      &new_factors.tab[0].factor);
                  bap_add_polynom_mpzm (temp1, temp1, temp2);
                  bap_mul_polynom_mpzm (temp1, temp1, monome);
                  bap_add_polynom_mpzm (temp1, temp1, psigma);
                  ba0_pull_stack ();
                  bap_sub_polynom_mpzm (E, E, temp1);
                  ba0_restore (&M);
                }
              for (i = 0; i < new_factors.size; i++)
                {
                  bap_mul_polynom_mpzm (&sigma[i], &sigma[i], monome);
                  bap_add_polynom_mpzm (&new_factors.tab[i].factor,
                      &new_factors.tab[i].factor, &sigma[i]);
                }
/*
 * In the general case, on applies the algorithm described page 273.
 */
              if (new_factors.size != 2)
                {
                  bap_expand_product_mpzm (E, &new_factors);
                  bap_sub_polynom_mpzm (E, &A_eval[j + 1], E);
                }
/*
 * Looks if some factors are not already found by dividing out.
 */
              if (!bap_is_zero_polynom_mpzm (E))
                {
                  bool modifie = false;
                  i = 0;
                  while (i < new_factors.size && new_factors.size > 1)
                    {
                      bap_mods_polynom_mpzm ((struct bap_polynom_mpz *)
                          &new_factors.tab[i].factor,
                          &new_factors.tab[i].factor);
                      if (bap_is_factor_polynom_mpz ((struct bap_polynom_mpz *)
                              &A_eval[j + 1],
                              (struct bap_polynom_mpz *) &new_factors.tab[i].
                              factor, Z))
                        {
                          bap_set_polynom_mpz ((struct bap_polynom_mpz *)
                              &A_eval[j + 1], Z);
                          if (i < new_factors.size - 1)
                            {
                              BA0_SWAP (struct bap_polynom_mpzm,
                                  new_factors.tab[i].factor,
                                  new_factors.tab[new_factors.size - 1].factor);
                              BA0_SWAP (struct bap_polynom_mpzm,
                                  old_factors.tab[i].factor,
                                  old_factors.tab[old_factors.size - 1].factor);
                            }
                          new_factors.size--;
                          old_factors.size--;
                          perm[nb_perm++] = i;
                          modifie = true;
                        }
                      else
                        i++;
                    }
                  if (modifie)
                    {
                      if (new_factors.size == 1)
                        {
                          bap_polynom_mpz_to_mpzm (&new_factors.tab[0].factor,
                              (struct bap_polynom_mpz *) &A_eval[j + 1]);
                          bap_set_polynom_zero_mpzm (E);
                        }
                      else
                        {
                          bap_polynom_mpz_to_mpzm (&A_eval[j + 1],
                              (struct bap_polynom_mpz *) &A_eval[j + 1]);
                          bap_mods_polynom_mpzm ((struct bap_polynom_mpz *)
                              &A_eval[j + 1], &A_eval[j + 1]);
                          bap_expand_product_mpzm (E, &new_factors);
                          bap_sub_polynom_mpzm (E, &A_eval[j + 1], E);
                        }
                    }
                }
            }
          k++;
        }
      while (nb_perm > 0)
        {
          BA0_SWAP (struct bap_polynom_mpzm,
              new_factors.tab[perm[nb_perm - 1]].factor,
              new_factors.tab[new_factors.size].factor);
          new_factors.size++;
          nb_perm--;
        }
    }
/*
 * End test + Symmetrical form.
 */
  bap_mods_product_mpzm ((struct bap_product_mpz *) &new_factors, &new_factors);
  bap_expand_product_mpz (Z, (struct bap_product_mpz *) &new_factors);
  bap_sub_polynom_mpz (Z, lifting->A, Z);
  bap_polynom_mpz_to_mpzm (E, Z);
  if (!bap_is_zero_polynom_mpzm (E))
    BA0_RAISE_EXCEPTION (BAZ_EXHENS);
/*
 * See tests/gcd1.c
 */
  if (!bap_is_zero_polynom_mpz (Z))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_pull_stack ();
  bap_set_product_mpz (lifted_factors, (struct bap_product_mpz *) &new_factors);
  ba0_restore (&M);
}

/*
 * texinfo: baz_monomial_reduce_polynom_mpz
 * Given @var{A} and @var{B} (@var{B} being non-numeric), 
 * compute a relation @math{c\, A = B\, Q + R} with @var{R} reduced (in
 * the sense of the Gr@"{o}bner basis theory) w.r.t. @var{B}.
 */

BAZ_DLL void
baz_monomial_reduce_polynom_mpz (
    struct bap_polynom_mpz *Q,
    struct bap_polynom_mpz *R,
    ba0_mpz_t c,
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *B)
{
  struct bap_itermon_mpz iter;
  struct bap_geobucket_mpz Qbar;
  struct bap_polynom_mpz Rbar, MQ;
  struct bav_term tQ, tR, tB;
  struct ba0_mark M;
  ba0_mpz_t *cB, *cR;
  ba0_mpz_t q, g, cbar, cbar0;
  bool first, found;

  if (bap_is_numeric_polynom_mpz (B))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&tB);
  bap_leading_term_polynom_mpz (&tB, B);
  cB = bap_numeric_initial_polynom_mpz (B);

  if (c != (ba0__mpz_struct *) 0)
    ba0_mpz_init_set_ui (cbar, 1);
  if (Q != (struct bap_polynom_mpz *) 0)
    bap_init_geobucket_mpz (&Qbar);

  bav_init_term (&tR);
  bav_init_term (&tQ);

  ba0_mpz_init (g);
  ba0_mpz_init (q);
  ba0_mpz_init (cbar0);

  bap_init_polynom_mpz (&Rbar);
  bap_init_polynom_mpz (&MQ);
/*
 * Loop invariant: cbar*A = B*Qbar + (first ? A : Rbar)
 */
  first = true;
  do
    {
/*
 * Looks for a term that could be rewritten
 */
      found = false;
      bap_begin_itermon_mpz (&iter, first ? A : &Rbar);
      while (!found && !bap_outof_itermon_mpz (&iter))
        {
          bap_term_itermon_mpz (&tR, &iter);
          if (bav_is_factor_term (&tR, &tB, &tQ))
            {
              cR = bap_coeff_itermon_mpz (&iter);
              found = true;
            }
          else
            bap_next_itermon_mpz (&iter);
        }
      bap_close_itermon_mpz (&iter);
      if (found)
        {
/*
 * Performs the substitution
 */
          ba0_mpz_gcd (g, *cR, *cB);
          ba0_mpz_divexact (q, *cR, g);
          ba0_mpz_divexact (cbar0, *cB, g);

          if (Q != (struct bap_polynom_mpz *) 0)
            {
              bap_mul_geobucket_numeric_mpz (&Qbar, cbar0);
              bap_set_polynom_monom_mpz (&MQ, q, &tQ);
              bap_add_geobucket_mpz (&Qbar, &MQ);
            }
          if (c != (ba0__mpz_struct *) 0)
            {
              ba0_mpz_mul (cbar, cbar, cbar0);
            }
          bap_mul_polynom_numeric_mpz (&Rbar, first ? A : &Rbar, cbar0);
          bap_submulmon_polynom_mpz (&Rbar, &Rbar, B, &tQ, q);
          first = false;
        }
    }
  while (found);
  ba0_pull_stack ();
  if (Q != (struct bap_polynom_mpz *) 0)
    bap_set_polynom_geobucket_mpz (Q, &Qbar);
  if (c != (ba0__mpz_struct *) 0)
    ba0_mpz_set (c, cbar);
  if (R != (struct bap_polynom_mpz *) 0)
    {
      if (first)
        {
          if (R != A)
            bap_set_polynom_mpz (R, A);
        }
      else
        bap_set_polynom_mpz (R, &Rbar);
    }
  ba0_restore (&M);
}

static void
baz_gcd_pseudo_division_elem_polynom_mpz (
    struct bap_polynom_mpz *Q,
    struct bap_polynom_mpz *R,
    struct bap_product_mpz *H,
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *B,
    struct bav_variable *x)
{
  struct bap_geobucket_mpz quotient;
  struct bap_polynom_mpz reste, lcR, redR, cR, lcB, redB, cB;
  struct bav_term T;
  bav_Idegree degR, degB;
  struct ba0_mark M;
  ba0_mpz_t c;
  bool first;

  degB = bap_degree_polynom_mpz (B, x);
  degR = bap_degree_polynom_mpz (A, x);

  if (H != (struct bap_product_mpz *) 0)
    bap_set_product_one_mpz (H);

  if (degR < degB)
    {
      if (R != BAP_NOT_A_POLYNOM_mpz && R != A)
        bap_set_polynom_mpz (R, A);
      if (Q != BAP_NOT_A_POLYNOM_mpz)
        bap_set_polynom_zero_mpz (Q);
      return;
    }

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&T);

  if (Q != BAP_NOT_A_POLYNOM_mpz)
    bap_init_geobucket_mpz (&quotient);

  bap_init_polynom_mpz (&reste);
  bap_init_polynom_mpz (&cR);
  bap_init_polynom_mpz (&cB);

  bap_init_readonly_polynom_mpz (&lcB);
  bap_init_readonly_polynom_mpz (&redB);
  bap_initial_and_reductum2_polynom_mpz (&lcB, &redB, B, x);

  bap_init_readonly_polynom_mpz (&lcR);
  bap_init_readonly_polynom_mpz (&redR);

  ba0_mpz_init (c);
/*
 * Loop invariant: H*A = B*quotient + (first ? A : reste)
 */
  first = true;
  do
    {
#define WITH_MONOMIAL_REDUCE 1
#undef WITH_MONOMIAL_REDUCE
#if defined (WITH_MONOMIAL_REDUCE)
/*
 * One starts by a monomial reduction.
 */
      baz_monomial_reduce_polynom_mpz (&cB, &reste, c, first ? A : &reste, B);
      if (H != (struct bap_product_mpz *) 0)
        {
          ba0_pull_stack ();
          bap_mul_product_numeric_mpz (H, H, c);
          ba0_push_another_stack ();
        }
      if (Q != BAP_NOT_A_POLYNOM_mpz)
        {
          bap_mul_geobucket_numeric_mpz (&quotient, c);
          bap_add_geobucket_mpz (&quotient, &cB);
        }
      bap_initial_and_reductum2_polynom_mpz (&lcR, &redR, &reste, x);
#else
      bap_initial_and_reductum2_polynom_mpz (&lcR, &redR, first ? A : &reste,
          x);
#endif
/*
 * One proceeds with a prem-like algorithm
 */
      baz_gcd_polynom_mpz (BAP_NOT_A_POLYNOM_mpz, &cR, &cB, &lcR, &lcB);

      if (H != (struct bap_product_mpz *) 0)
        {
          ba0_pull_stack ();
          bap_mul_product_polynom_mpz (H, H, &cB, 1);
          ba0_push_another_stack ();
        }
/*
   reste = (lc (B) / g) * reste - (lc (reste) / g) * x^ddeg * B

more precisely, one has:

   reste = (lc (B) / g) * red (reste) - (lc (reste) / g) * x^ddeg * red (B)
	   ^^^^^^^^^^^^			^^^^^^^^^^^^^^^^
		cB			      cR
*/
      bap_mul_polynom_mpz (&reste, &redR, &cB);

      bav_set_term_variable (&T, x, degR - degB);
      bap_mul_polynom_term_mpz (&cR, &cR, &T);

      if (Q != BAP_NOT_A_POLYNOM_mpz)
        {
          bap_mul_geobucket_mpz (&quotient, &cB);
          bap_add_geobucket_mpz (&quotient, &cR);
        }

      bap_mul_polynom_mpz (&cR, &cR, &redB);

      bap_sub_polynom_mpz (&reste, &reste, &cR);

      degR = bap_degree_polynom_mpz (&reste, x);

      first = false;
    }
  while (degR >= degB);

  ba0_pull_stack ();

  if (R != BAP_NOT_A_POLYNOM_mpz)
    bap_set_polynom_mpz (R, &reste);
  if (Q != BAP_NOT_A_POLYNOM_mpz)
    bap_set_polynom_geobucket_mpz (Q, &quotient);

  ba0_restore (&M);
}

/*
 * texinfo: baz_gcd_pseudo_division_polynom_mpz
 * Variant of the pseudo division algorithm where, at each step, the current
 * remainder is multiplied by the smallest needed factor.
 * This factor is determined by a gcd computation. 
 * The product @var{H} receives the product by which @var{A} was multiplied
 * during the process. Parameters @var{Q}, @var{R} and @var{H} may be the
 * zero pointer. The variable @var{x} may be zero. In that case, it
 * is understood to be the leading variable of @var{B}.
 */

BAZ_DLL void
baz_gcd_pseudo_division_polynom_mpz (
    struct bap_polynom_mpz *Q,
    struct bap_polynom_mpz *R,
    struct bap_product_mpz *H,
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *B,
    struct bav_variable *x)
{
  struct bap_polynom_mpz AA;
  volatile bav_Iordering r, r0;
  bav_Idegree degA, degB;
  struct ba0_mark M;

  if (bap_is_zero_polynom_mpz (B))
    BA0_RAISE_EXCEPTION (BAP_ERRNUL);
  if (x == BAV_NOT_A_VARIABLE && bap_is_numeric_polynom_mpz (B))
    BA0_RAISE_EXCEPTION (BAP_ERRCST);
  if ((Q != BAP_NOT_A_POLYNOM_mpz && Q->readonly) || (R != BAP_NOT_A_POLYNOM_mpz
          && R->readonly))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (x == BAV_NOT_A_VARIABLE)
    x = bap_leader_polynom_mpz (B);
  degB = bap_degree_polynom_mpz (B, x);
  degA = bap_degree_polynom_mpz (A, x);

  if (degA < degB)
    {
      if (R != BAP_NOT_A_POLYNOM_mpz && R != A)
        bap_set_polynom_mpz (R, A);
      if (Q != BAP_NOT_A_POLYNOM_mpz)
        bap_set_polynom_zero_mpz (Q);
      if (H != (struct bap_product_mpz *) 0)
        bap_set_product_one_mpz (H);
    }
  else if (bap_is_numeric_polynom_mpz (A)
      || bav_variable_number (bap_leader_polynom_mpz (A)) <=
      bav_variable_number (x))
    baz_gcd_pseudo_division_elem_polynom_mpz (Q, R, H, A, B, x);
  else
    {
      r0 = bav_current_ordering ();
      r = bav_R_copy_ordering (r0);
      bav_push_ordering (r);

      bav_R_set_maximal_variable (x);

      ba0_push_another_stack ();
      ba0_record (&M);

      bap_init_readonly_polynom_mpz (&AA);
      bap_sort_polynom_mpz (&AA, A);

      ba0_pull_stack ();

      baz_gcd_pseudo_division_elem_polynom_mpz (Q, R, H, &AA, B, x);

      ba0_restore (&M);

      bav_pull_ordering ();
      bav_R_free_ordering (r);

      if (Q != BAP_NOT_A_POLYNOM_mpz)
        bap_physort_polynom_mpz (Q);
      if (R != BAP_NOT_A_POLYNOM_mpz)
        bap_physort_polynom_mpz (R);
      if (H != (struct bap_product_mpz *) 0)
        bap_physort_product_mpz (H);

    }
}

/*
 * texinfo: baz_gcd_prem_polynom_mpz
 * Variant of @code{baz_gcd_pseudo_division_polynom_mpz}.
 */

BAZ_DLL void
baz_gcd_prem_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_product_mpz *H,
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *B,
    struct bav_variable *x)
{
  baz_gcd_pseudo_division_polynom_mpz (BAP_NOT_A_POLYNOM_mpz, R, H, A, B, x);
}

/*
 * texinfo: baz_gcd_pquo_polynom_mpz
 * Variant of @code{baz_gcd_pseudo_division_polynom_mpz}.
 */

BAZ_DLL void
baz_gcd_pquo_polynom_mpz (
    struct bap_polynom_mpz *Q,
    struct bap_product_mpz *H,
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *B,
    struct bav_variable *x)
{
  baz_gcd_pseudo_division_polynom_mpz (Q, BAP_NOT_A_POLYNOM_mpz, H, A, B, x);
}
