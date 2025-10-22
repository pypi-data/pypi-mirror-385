#include "baz_polyspec_mpz.h"
#include "baz_gcd_polynom_mpz.h"
#include "baz_factor_polynom_mpz.h"

/*
 * UNIVARIATE GCD
 */

/*
 * Subfunction of baz_gcd_univariate_primitive_tableof_polynom_mpz.
 *
 * Return a small prime strictly less than prime, which does
 * not annihilate c1.
 */

static ba0_mint_hp
baz_univariate_gcd_determine_small_prime (
    ba0_mint_hp prime,
    ba0_mpz_t c1)
{
  ba0_mpz_t bunk;
  struct ba0_mark M;

  ba0_record (&M);
  ba0_mpz_init (bunk);
  do
    prime = ba0_previous_small_prime (prime);
  while (ba0_mpz_mod_ui (bunk, c1, (unsigned long) prime) == 0);
  ba0_restore (&M);
  return prime;
}

/*
 * Compute the gcd of univariate, numerically primitive, polynomials
 * Called directly or from baz_gcd_univariate_tableof_polynom_mpz
 */

static void
baz_gcd_univariate_primitive_tableof_polynom_mpz (
    struct bap_polynom_mpz *G,
    struct bap_tableof_polynom_mpz *polys)
{
  struct bap_polynom_mpzm Ghat, Gtilde;
  struct bap_tableof_polynom_mint_hp Abar;
  struct bap_polynom_mint_hp Gbar;
  struct ba0_mark M;
  ba0_mpz_t c1, g, ubar, utilde, pbar, ptilde;
  ba0_mint_hp p;
  ba0_int_p i;
  bool divisor_found;

  if (polys->size < 2)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
/*
 * Check all univariate in the same variable
 */
  {
    struct bav_term *T = &polys->tab[0]->total_rank;
    struct bav_variable *v;
    if (T->size != 1)
      BA0_RAISE_EXCEPTION (BA0_ERRALG);
    v = T->rg[0].var;
    for (i = 1; i < polys->size; i++)
      {
        T = &polys->tab[1]->total_rank;
        if (T->size != 1 || T->rg[0].var != v)
          BA0_RAISE_EXCEPTION (BA0_ERRALG);
      }
  }

  ba0_push_another_stack ();
  ba0_record (&M);
/*
 * c1 = the gcd of the leading coefficients of the polynomials
 */
  ba0_mpz_init (c1);
  ba0_mpz_gcd (c1, *bap_numeric_initial_polynom_mpz (polys->tab[0]),
      *bap_numeric_initial_polynom_mpz (polys->tab[1]));
  for (i = 2; i < polys->size; i++)
    ba0_mpz_gcd (c1, c1, *bap_numeric_initial_polynom_mpz (polys->tab[i]));
/*
 * p = a small prime which does not annihilate c1
 */
  p = baz_univariate_gcd_determine_small_prime (ba0_largest_small_prime () + 2,
      c1);
  ba0_mint_hp_module_set (p, true);
/*
 * Abar = polys mod p
 */
  ba0_init_table ((struct ba0_table *) &Abar);
  ba0_realloc2_table ((struct ba0_table *) &Abar, polys->size,
      (ba0_new_function *) & bap_new_polynom_mint_hp);
  for (i = 0; i < polys->size; i++)
    bap_polynom_mpz_to_mint_hp (Abar.tab[i], polys->tab[i]);
  Abar.size = polys->size;
/*
 * Gbar = gcd (Abar) mod p
 */
  bap_init_polynom_mint_hp (&Gbar);
  bap_Euclid_polynom_mint_hp (&Gbar, Abar.tab[0], Abar.tab[1]);
  for (i = 2; i < Abar.size && !bap_is_numeric_polynom_mint_hp (&Gbar); i++)
    bap_Euclid_polynom_mint_hp (&Gbar, &Gbar, Abar.tab[i]);
/*
 * One may stop here with gcd = 1
 */
  if (bap_is_numeric_polynom_mint_hp (&Gbar))
    {
      ba0_pull_stack ();
      if (G != BAP_NOT_A_POLYNOM_mpz)
        bap_set_polynom_one_mpz (G);
      ba0_restore (&M);
      return;
    }
/*
 * Start the multimodular process
 */
  ba0_mpz_init_set_ui (ptilde, p);
  ba0_mpzm_module_set (ptilde, true);

  bap_init_polynom_mpzm (&Gtilde);
  bap_init_polynom_mpzm (&Ghat);
  bap_polynom_mint_hp_to_mpzm (&Gtilde, &Gbar);
  bap_mul_polynom_numeric_mpzm (&Ghat, &Gtilde, c1);
  bap_mods_polynom_mpzm ((struct bap_polynom_mpz *) &Ghat, &Ghat);
  bap_numeric_primpart_polynom_mpz ((struct bap_polynom_mpz *) &Ghat,
      (struct bap_polynom_mpz *) &Ghat);

  ba0_mpz_init (g);
  ba0_mpz_init (ubar);
  ba0_mpz_init (utilde);
  ba0_mpz_init (pbar);

  for (;;)
    {
      divisor_found = true;
      for (i = 0; i < polys->size && divisor_found; i++)
        divisor_found =
            bap_is_factor_polynom_mpz (polys->tab[i],
            (struct bap_polynom_mpz *) &Ghat, BAP_NOT_A_POLYNOM_mpz);
      if (divisor_found)
        break;

      p = baz_univariate_gcd_determine_small_prime (p, c1);
      ba0_mint_hp_module_set (p, true);
      for (i = 0; i < polys->size; i++)
        bap_polynom_mpz_to_mint_hp (Abar.tab[i], polys->tab[i]);

      bap_Euclid_polynom_mint_hp (&Gbar, Abar.tab[0], Abar.tab[1]);
      for (i = 2; i < Abar.size && !bap_is_numeric_polynom_mint_hp (&Gbar); i++)
        bap_Euclid_polynom_mint_hp (&Gbar, &Gbar, Abar.tab[i]);
/*
 * One may stop here with gcd = 1
 */
      if (bap_is_numeric_polynom_mint_hp (&Gbar))
        {
          ba0_pull_stack ();
          if (G != BAP_NOT_A_POLYNOM_mpz)
            bap_set_polynom_one_mpz (G);
          ba0_restore (&M);
          return;
        }
      else if (bap_leading_degree_polynom_mint_hp (&Gbar) <
          bap_leading_degree_polynom_mpzm (&Gtilde))
/*
 * Primes have been unlucky so far. Restart the multimodular process
 */
        {
          ba0_mpz_set_ui (ptilde, p);
          ba0_mpzm_module_set (ptilde, true);
          bap_polynom_mint_hp_to_mpzm (&Gtilde, &Gbar);
          bap_mul_polynom_numeric_mpzm (&Ghat, &Gtilde, c1);
          bap_mods_polynom_mpzm ((struct bap_polynom_mpz *) &Ghat, &Ghat);
          bap_numeric_primpart_polynom_mpz ((struct bap_polynom_mpz *) &Ghat,
              (struct bap_polynom_mpz *) &Ghat);
        }
      else if (bap_leading_degree_polynom_mint_hp (&Gbar) ==
          bap_leading_degree_polynom_mpzm (&Gtilde))
/*
 * Chinese remaindering
 */
        {
          ba0_mpz_set_ui (pbar, p);
          ba0_mpz_gcdext (g, utilde, ubar, ptilde, pbar);
          ba0_mpz_mul (utilde, utilde, ptilde);
          ba0_mpz_mul (ubar, ubar, pbar);
          ba0_mpz_mul (ptilde, ptilde, pbar);
          ba0_mpzm_module_set (ptilde, false);
          bap_polynom_mint_hp_to_mpzm (&Ghat, &Gbar);
          bap_mul_polynom_numeric_mpz ((struct bap_polynom_mpz *) &Ghat,
              (struct bap_polynom_mpz *) &Ghat, utilde);
          bap_mul_polynom_numeric_mpz ((struct bap_polynom_mpz *) &Gtilde,
              (struct bap_polynom_mpz *) &Gtilde, ubar);
          bap_add_polynom_mpz ((struct bap_polynom_mpz *) &Ghat,
              (struct bap_polynom_mpz *) &Gtilde,
              (struct bap_polynom_mpz *) &Ghat);
          bap_polynom_mpz_to_mpzm (&Gtilde, (struct bap_polynom_mpz *) &Ghat);
          bap_mul_polynom_numeric_mpzm (&Ghat, &Gtilde, c1);
          bap_mods_polynom_mpzm ((struct bap_polynom_mpz *) &Ghat, &Ghat);
          bap_numeric_primpart_polynom_mpz ((struct bap_polynom_mpz *) &Ghat,
              (struct bap_polynom_mpz *) &Ghat);
        }
    }
/*
 * The gcd is found
 */
  ba0_pull_stack ();
  if (G != BAP_NOT_A_POLYNOM_mpz)
    bap_set_polynom_mpz (G, (struct bap_polynom_mpz *) &Ghat);
  ba0_restore (&M);
}

/*
 * texinfo: baz_gcd_univariate_tableof_polynom_mpz
 * Assign to @var{G} the gcd of all the elements of @var{polys}.
 * All polynomials are assumed to be univariate, depending on the same
 * variable.
 * Exception @code{BA0_ERRALG} is raised if @var{polys} is empty.
 */

BAZ_DLL void
baz_gcd_univariate_tableof_polynom_mpz (
    struct bap_polynom_mpz *G,
    struct bap_tableof_polynom_mpz *polys)
{
  struct bap_tableof_polynom_mpz primitive_polys;
  struct ba0_tableof_mpz cont;
  ba0_mpz_t gcd_cont;
  struct ba0_mark M;
  ba0_int_p i;
  bool no_gcd_cont;

  if (polys->size < 2)
    {
      if (polys->size == 1)
        {
          bap_set_polynom_mpz (G, polys->tab[0]);
          return;
        }
      BA0_RAISE_EXCEPTION (BA0_ERRALG);
    }

  ba0_push_another_stack ();
  ba0_record (&M);
/*
 * Compute the numeric contents of the polynomials (in cont)
 *             primitive parts of the polynomials (in primitive_polys)
 *             gcd of the numeric contents (in gcd_cont)
 */
  ba0_init_table ((struct ba0_table *) &cont);
  ba0_realloc2_table ((struct ba0_table *) &cont, polys->size,
      (ba0_new_function *) & ba0_new_mpz);
  cont.size = polys->size;
/*
 * primitive_polys is not initialized before the end of the next loop
 */
  ba0_init_table ((struct ba0_table *) &primitive_polys);
  ba0_realloc_table ((struct ba0_table *) &primitive_polys, polys->size);
  primitive_polys.size = polys->size;

  no_gcd_cont = false;
  for (i = 0; i < polys->size; i++)
    {
      bap_numeric_content_polynom_mpz (cont.tab[i], polys->tab[i]);
      if (ba0_mpz_cmp_ui (cont.tab[i], 1) == 0)
        {
          primitive_polys.tab[i] = polys->tab[i];
          no_gcd_cont = true;
        }
      else
        {
          primitive_polys.tab[i] = bap_new_polynom_mpz ();
          bap_exquo_polynom_numeric_mpz (primitive_polys.tab[i], polys->tab[i],
              cont.tab[i]);
        }
    }
/*
 * gcd_cont
 */
  if (no_gcd_cont)
    ba0_mpz_init_set_ui (gcd_cont, 1);
  else
    {
      ba0_mpz_init (gcd_cont);
      ba0_mpz_gcd (gcd_cont, cont.tab[0], cont.tab[1]);
      for (i = 2; i < polys->size; i++)
        ba0_mpz_gcd (gcd_cont, gcd_cont, cont.tab[i]);
    }

  ba0_pull_stack ();
  baz_gcd_univariate_primitive_tableof_polynom_mpz (G, &primitive_polys);

  if (ba0_mpz_cmp_ui (gcd_cont, 1) != 0)
    bap_mul_polynom_numeric_mpz (G, G, gcd_cont);
  ba0_restore (&M);
}

/*
 * HEURISTIC GCD
 * [Geddes, Czapor, Labahn, 1992, page 330]
 */

/*
 * Sorts A by increasing bap_nbmon_polynom_mpz.
 * Performs the same permutation on B. Bubble sort.
 */

static void
baz_gcdheu_sort_by_ascending_nbmon (
    struct bap_tableof_polynom_mpz *A,
    struct bap_tableof_polynom_mpz *B)
{
  ba0_int_p n, i, p, q;
  bool modified;

  modified = true;
  for (n = A->size - 1; n >= 1 && modified; n--)
    {
      modified = false;
      for (i = 0; i < n; i++)
        {
          p = bap_nbmon_polynom_mpz (A->tab[i]);
          q = bap_nbmon_polynom_mpz (A->tab[i + 1]);
          if (p > q)
            {
              BA0_SWAP (struct bap_polynom_mpz *,
                  A->tab[i],
                  A->tab[i + 1]);
              BA0_SWAP (struct bap_polynom_mpz *,
                  B->tab[i],
                  B->tab[i + 1]);
              modified = true;
            }
        }
    }
}

/*
 * Assigns to ksi a heuristic bound computed from polys
 */

static void
baz_gcdheu_first_value_for_ksi (
    ba0_mpz_t ksi,
    struct bap_tableof_polynom_mpz *polys)
{
  struct ba0_mark M;
  ba0_int_p i;
  struct ba0_tableof_mpz maxnorm;
  ba0_mpz_t t1, t2;
  ba0__mpz_struct *min_maxnorm, *min_t1_t2;

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_init_table ((struct ba0_table *) &maxnorm);
  ba0_realloc2_table ((struct ba0_table *) &maxnorm, polys->size,
      (ba0_new_function *) & ba0_new_mpz);
  for (i = 0; i < polys->size; i++)
    bap_maxnorm_polynom_mpz (maxnorm.tab[i], polys->tab[i]);
  maxnorm.size = polys->size;

  min_maxnorm = maxnorm.tab[0];
  for (i = 1; i < maxnorm.size; i++)
    if (ba0_mpz_cmp (min_maxnorm, maxnorm.tab[i]) > 0)
      min_maxnorm = maxnorm.tab[i];
/*
 * t1 = min of the maxnorms times 2 plus 29
 */
  ba0_mpz_init (t1);
  ba0_mpz_mul_2exp (t1, min_maxnorm, 1);
  ba0_mpz_add_ui (t1, t1, (unsigned long int) 29);
/*
 * t2 = iquo (10000*sqrt(t1),101)
 */
  ba0_mpz_init (t2);
  ba0_mpz_sqrt (t2, t1);
  ba0_mpz_mul_ui (t2, t2, (unsigned long int) 10000);
  ba0_mpz_tdiv_q_ui (t2, t2, (unsigned long int) 101);
/*
 * min_t1_t2 = min (t1, t2)
 */
  if (ba0_mpz_cmp (t1, t2) > 0)
    min_t1_t2 = t2;
  else
    min_t1_t2 = t1;
/*
 * maxnorm = |maxnorm / lcoeff|
 */
  for (i = 0; i < maxnorm.size; i++)
    {
      ba0_mpz_tdiv_q (maxnorm.tab[i], maxnorm.tab[i],
          *bap_numeric_initial_polynom_mpz (polys->tab[i]));
      ba0_mpz_abs (maxnorm.tab[i], maxnorm.tab[i]);
    }
/*
 * min_maxnorm = 2 times min (|maxnorm / lcoeff|) plus 2
 */
  min_maxnorm = maxnorm.tab[0];
  for (i = 1; i < maxnorm.size; i++)
    if (ba0_mpz_cmp (min_maxnorm, maxnorm.tab[i]) > 0)
      min_maxnorm = maxnorm.tab[i];
  ba0_mpz_mul_2exp (min_maxnorm, min_maxnorm, 1);
  ba0_mpz_add_ui (min_maxnorm, min_maxnorm, (unsigned long int) 2);
/*
 * ksi = max (min_maxnorm, min_t1_t2) made odd
 */
  ba0_pull_stack ();
  if (ba0_mpz_cmp (min_maxnorm, min_t1_t2) > 0)
    ba0_mpz_set (ksi, min_maxnorm);
  else
    ba0_mpz_set (ksi, min_t1_t2);
  if (ba0_mpz_even_p (ksi))
    ba0_mpz_add_ui (ksi, ksi, (unsigned long int) 1);
  ba0_restore (&M);
}

/*
 * New odd value for ksi, using the square of the golden ratio
 */

static void
baz_gcdheu_next_value_for_ksi (
    ba0_mpz_t ksi)
{
  ba0_mpz_t t1;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mpz_init (t1);
  ba0_mpz_sqrt (t1, ksi);
  ba0_mpz_sqrt (t1, t1);
  ba0_mpz_mul (t1, t1, ksi);
  ba0_mpz_mul_ui (t1, t1, (unsigned long int) 73794);
  ba0_pull_stack ();
  ba0_mpz_tdiv_q_ui (ksi, t1, (unsigned long int) 27011);
  if (ba0_mpz_even_p (ksi))
    ba0_mpz_add_ui (ksi, ksi, (unsigned long int) 1);
  ba0_restore (&M);
}

/*
 * Returns true if baz_gcdheu_tableof_polynom_mpz is entering
 * too complex computations. The test is heuristic.
 */

static bool
baz_gcdheu_too_complex_problem (
    unsigned ba0_int_p toocomplex,
    ba0_mpz_t ksi,
    struct bap_tableof_polynom_mpz *polys,
    struct bav_variable *v,
    struct bav_term *X)
{
  struct bav_variable *w;
  unsigned ba0_int_p heur;
  unsigned ba0_int_p deg, maxdeg;
  ba0_int_p i, k;

  maxdeg = bap_degree_polynom_mpz (polys->tab[0], v);
  for (i = 1; i < polys->size; i++)
    {
      deg = bap_degree_polynom_mpz (polys->tab[i], v);
      if (deg > maxdeg)
        maxdeg = deg;
    }
  heur = ba0_mpz_sizeinbase (ksi, 16) * maxdeg;
  if (heur > toocomplex)
    return true;
  if (heur > toocomplex / 10 && X->size >= 2)
    {
      heur = 0;
      for (k = 1; k < X->size; k++)
        {
          w = X->rg[k].var;
          if (v != w)
            {
              maxdeg = bap_degree_polynom_mpz (polys->tab[0], w);
              for (i = 1; i < polys->size; i++)
                {
                  deg = bap_degree_polynom_mpz (polys->tab[i], w);
                  if (deg > maxdeg)
                    maxdeg = deg;
                }
              if (maxdeg > heur)
                heur = maxdeg;
            }
        }
      heur = ba0_mpz_size (ksi) * (X->rg[0].deg + 1) * heur;
      if (heur > 2 * toocomplex)
        return true;
    }
  return false;
}

/*
 * Assigns to G the gcd of the polynomials in polys0.
 * It is better, though not necessary, that polynomials are processed,
 * before calling this function, so that they all depend on the same
 * set of variables.
 *
 * This function implements a heuristic gcd algorithm. It may fail.
 * In the case of a failure or of a too complex computation, the
 * exception BAZ_ERRHEU is raised.
 *
 * Reasonable values for toocomplex should be picked in [4000, 10000].
 */

/*
 * texinfo: baz_gcdheu_tableof_polynom_mpz
 * Assign to @var{G} the gcd of the polynomials in @var{polys0}, computed
 * by means of heuristic gcd algorithm. The function may fail (possibly
 * because of a too complex computation).
 * In that case, it raises the exception @code{BAP_ERRHEU}.
 * The parameter @var{toocomplex} should provide an estimation of what
 * a too complex computation is (current values are picked in the range
 * [4000,10000]).
 */

BAZ_DLL void
baz_gcdheu_tableof_polynom_mpz (
    struct bap_polynom_mpz *G,
    struct bap_tableof_polynom_mpz *polys0,
    ba0_int_p toocomplex)
{
  struct bap_tableof_polynom_mpz polys, primitive_polys, evaluated_polys;
  struct bap_polynom_mpz lifted_gcd, lifted_evaluated_poly, gcd_evaluated_polys;
  struct bav_tableof_term term;
  struct bav_term gcd_term, X;
  struct bav_variable *v;
  struct ba0_tableof_mpz cont;
  ba0_mpz_t gcd_cont, ksi;
  struct ba0_mark M;
  ba0_int_p i, nbloops;
  bool a_root_was_hit, found, stop;
/* 
    BA0_RAISE_EXCEPTION (BAZ_ERRHEU);
 */
  ba0_push_another_stack ();
  ba0_record (&M);
/*
 * polys = the nonzero entries of polys0
 */
  ba0_init_table ((struct ba0_table *) &polys);
  ba0_realloc_table ((struct ba0_table *) &polys, polys0->size);
  for (i = 0; i < polys0->size; i++)
    if (!bap_is_zero_polynom_mpz (polys0->tab[i]))
      {
        polys.tab[polys.size] = polys0->tab[i];
        polys.size += 1;
      }
/*
 * If there are less than two polynomials, we are done
 */
  if (polys.size < 2)
    {
      ba0_pull_stack ();
      if (polys.size == 0)
        bap_set_polynom_zero_mpz (G);
      else if (G != polys.tab[0])
        bap_set_polynom_mpz (G, polys.tab[0]);
      ba0_restore (&M);
      return;
    }
/*
 * cont = the numerical content of polys
 * term = the obvious factors of the form x^k of polys
 * primitive_polys = polys / (cont*term)
 */
  ba0_init_table ((struct ba0_table *) &cont);
  ba0_realloc2_table ((struct ba0_table *) &cont, polys.size,
      (ba0_new_function *) & ba0_new_mpz);
  ba0_init_table ((struct ba0_table *) &term);
  ba0_realloc2_table ((struct ba0_table *) &term, polys.size,
      (ba0_new_function *) & bav_new_term);
  ba0_init_table ((struct ba0_table *) &primitive_polys);
  ba0_realloc2_table ((struct ba0_table *) &primitive_polys, polys.size,
      (ba0_new_function *) & bap_new_polynom_mpz);

  for (i = 0; i < polys.size; i++)
    {
      bap_numeric_content_polynom_mpz (cont.tab[i], polys.tab[i]);
      bap_minimal_total_rank_polynom_mpz (term.tab[i], polys.tab[i]);
      bap_exquo_polynom_term_mpz (primitive_polys.tab[i], polys.tab[i],
          term.tab[i]);
      bap_exquo_polynom_numeric_mpz (primitive_polys.tab[i],
          primitive_polys.tab[i], cont.tab[i]);
    }
  cont.size = polys.size;
  term.size = polys.size;
  primitive_polys.size = polys.size;
/*
 * gcd_cont = the gcd of the numerical content
 * gcd_term = the gcd of the obvious factors
 */
  ba0_mpz_init (gcd_cont);
  bav_init_term (&gcd_term);
  ba0_mpz_gcd (gcd_cont, cont.tab[0], cont.tab[1]);
  bav_gcd_term (&gcd_term, term.tab[0], term.tab[1]);
  for (i = 2; i < cont.size; i++)
    {
      ba0_mpz_gcd (gcd_cont, gcd_cont, cont.tab[i]);
      bav_gcd_term (&gcd_term, &gcd_term, term.tab[i]);
    }
/*
 * X = the set of variables which are common to all polynomials
 */
  bav_init_term (&X);
  bav_gcd_term (&X, &primitive_polys.tab[0]->total_rank,
      &primitive_polys.tab[1]->total_rank);
  for (i = 2; i < primitive_polys.size; i++)
    bav_gcd_term (&X, &X, &primitive_polys.tab[i]->total_rank);
/*
 * If X is empty, we are done
 */
  if (bav_is_one_term (&X))
    {
      ba0_pull_stack ();
      bap_set_polynom_monom_mpz (G, gcd_cont, &gcd_term);
      ba0_restore (&M);
      return;
    }

  v = X.rg[0].var;
/*
 * Computation of the heuristic bound ksi
 */
  ba0_mpz_init (ksi);
  baz_gcdheu_first_value_for_ksi (ksi, &primitive_polys);

  ba0_init_table ((struct ba0_table *) &evaluated_polys);
  ba0_realloc2_table ((struct ba0_table *) &evaluated_polys,
      primitive_polys.size, (ba0_new_function *) & bap_new_polynom_mpz);
  bap_init_polynom_mpz (&gcd_evaluated_polys);
  bap_init_polynom_mpz (&lifted_evaluated_poly);
  bap_init_polynom_mpz (&lifted_gcd);

  found = false;
  stop = false;
  for (nbloops = 0; nbloops < 6 && !found && !stop; nbloops++)
    {
      if (baz_gcdheu_too_complex_problem (toocomplex, ksi, &primitive_polys, v,
              &X))
        stop = true;
      else
        {
/*
 * If we are not at the first loop, compute a new value for ksi.
 */
          if (nbloops > 0)
            baz_gcdheu_next_value_for_ksi (ksi);
/*
 * evaluated_polys = primitive_polys evaluated at v = ksi
 */
          a_root_was_hit = false;
          for (i = 0; i < primitive_polys.size && !a_root_was_hit; i++)
            {
              bap_eval_to_polynom_at_numeric_polynom_mpz (evaluated_polys.tab
                  [i], primitive_polys.tab[i], v, ksi);
              a_root_was_hit = bap_is_zero_polynom_mpz (evaluated_polys.tab[i]);
              evaluated_polys.size = i + 1;
            }
/*
 * if a root of some element of primitive_polys was hit, take another ksi
 */
          if (!a_root_was_hit)
            {
/*
 * recursive call, giving gcd_evaluated_polys
 */
              baz_gcdheu_tableof_polynom_mpz (&gcd_evaluated_polys,
                  &evaluated_polys, toocomplex);
/*
 * lift gcd_evaluated_polys and division test
 */
              baz_genpoly_polynom_mpz (&lifted_gcd, &gcd_evaluated_polys, ksi,
                  v);
              bap_normal_numeric_primpart_polynom_mpz (&lifted_gcd,
                  &lifted_gcd);
              if (bap_is_factor_tableof_polynom_mpz (&lifted_gcd,
                      &primitive_polys))
                found = true;
              else
                {
/*
 * the direct lifting did not work.
 * evaluated_polys = evaluated_polys / gcd_evaluated_polys
 * so that evaluated_polys contain now the cofactors of gcd_evaluated_polys
 */
                  for (i = 0; i < evaluated_polys.size; i++)
                    bap_exquo_polynom_mpz (evaluated_polys.tab[i],
                        evaluated_polys.tab[i], &gcd_evaluated_polys);
/*
 * lift each cofactor evaluated_poly.tab [i] in lifted_evaluated_poly.
 * then tests primitive_polys.tab [i] / lifted_evaluated_poly for lifted_gcd.
 * starts by the simplest cofactors.
 */
                  baz_gcdheu_sort_by_ascending_nbmon (&evaluated_polys,
                      &primitive_polys);
                  for (i = 0; i < evaluated_polys.size && found; i++)
                    {
                      baz_genpoly_polynom_mpz (&lifted_evaluated_poly,
                          evaluated_polys.tab[i], ksi, v);
                      if (!bap_is_zero_polynom_mpz (&lifted_evaluated_poly)
                          && bap_is_factor_polynom_mpz (primitive_polys.tab[i],
                              &lifted_evaluated_poly, &lifted_gcd))
                        found =
                            bap_is_factor_tableof_polynom_mpz (&lifted_gcd,
                            &primitive_polys);
                    }
                }
            }
        }
    }
/*
 * found = true means that the gcd of the primitive_polys is in lifted_gcd.
 * One then still needs to multiply by gcd_cont and gcd_term.
 */
  if (found)
    {
      ba0_pull_stack ();
      bap_mul_polynom_monom_mpz (G, &lifted_gcd, gcd_cont, &gcd_term);
      ba0_restore (&M);
      return;
    }
  else
    BA0_RAISE_EXCEPTION (BAZ_ERRHEU);
}

/*
 * EXTENDED ZASSENHAUS GCD ALGORITHM
 */

/*
 * The weight of the variable v, in the polynomial A, is:
 *
 * weight (v, A) = 10 * nbmon (lcoeff (A, v)) + nbmon (A)
 *
 * This heuristic weight is used to determine the distinguished variable
 * and the lifting polynomial in the Extended Zassehaus gcd algorithm.
 */

static void
baz_EZG_estimate_weights_of_variables (
    struct ba0_tableof_int_p *W,
    struct bap_polynom_mpz *A)
{
  struct bap_itermon_mpz iter;
  struct bav_term U;
  ba0_int_p t, u, nbmon;

  bav_init_term (&U);
  bav_realloc_term (&U, A->total_rank.size);
/*
 * W->tab [t] = 0
 */
  W->size = 0;
  ba0_realloc_table ((struct ba0_table *) W, A->total_rank.size);
  for (t = 0; t < A->total_rank.size; t++)
    W->tab[t] = 0;
  W->size = A->total_rank.size;
/*
 * W->tab [t] = nbmon (lcoeff (A, variable number t))
 */
  bap_begin_itermon_mpz (&iter, A);
  while (!bap_outof_itermon_mpz (&iter))
    {
      bap_term_itermon_mpz (&U, &iter);
      for (t = 0; t < A->total_rank.size; t++)
        for (u = 0; u < U.size; u++)
          {
            if (A->total_rank.rg[t].var == U.rg[u].var)
              {
                if (A->total_rank.rg[t].deg == U.rg[u].deg)
                  W->tab[t] = W->tab[t] + 1;
                break;
              }
          }
      bap_next_itermon_mpz (&iter);
    }
/*
 * W->tab [t] = 10 * nbmon (lcoeff (A, variable number t)) + nbmon (A)
 */
  nbmon = bap_nbmon_polynom_mpz (A);
  for (t = 0; t < A->total_rank.size; t++)
    W->tab[t] = W->tab[t] * 10 + nbmon;
}

/*
 * Determines heuristically the distinguished variable and the lifting
 * polynomial for the Extended Zassenhaus gcd algorithm.
 *
 * The distinguished variable is returned.
 * The table polys is sorted in such a way that the lifting polynomial
 * occurs at the beginning of the table.
 */

static struct bav_variable *
baz_EZG_distinguished_variable (
    struct bap_tableof_polynom_mpz *polys)
{
  struct bav_variable *v;
  struct ba0_tableof_tableof_int_p weights;
  struct ba0_tableof_int_p bestvar;
  struct ba0_tableof_int_p *weight;
  struct ba0_mark M;
  ba0_int_p i, j, n;
  bool modified;

  if (polys->size < 2)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_record (&M);
/*
 * weights.tab [t] = the weights of the variables of the polynomial number t
 */
  ba0_init_table ((struct ba0_table *) &weights);
  ba0_realloc2_table ((struct ba0_table *) &weights, polys->size,
      (ba0_new_function *) & ba0_new_table);
  for (i = 0; i < polys->size; i++)
    baz_EZG_estimate_weights_of_variables (weights.tab[i], polys->tab[i]);
  weights.size = polys->size;
/*
 * bestvar.tab [t] = the index of the smallest entry of weights.tab [t]
 */
  ba0_init_table ((struct ba0_table *) &bestvar);
  ba0_realloc_table ((struct ba0_table *) &bestvar, polys->size);
  for (i = 0; i < polys->size; i++)
    {
      weight = weights.tab[i];
      bestvar.tab[i] = 0;
      for (j = 1; j < weights.tab[i]->size; j++)
        {
          if (weight->tab[j] < weight->tab[bestvar.tab[i]])
            bestvar.tab[i] = j;
        }
    }
  bestvar.size = polys->size;
/*
 * Sorts polys, weights and bestvar by increasing bestvar.
 * Bubble sort.
 */
  modified = true;
  for (n = polys->size - 1; n >= 1 && modified; n--)
    {
      modified = false;
      for (i = 0; i < n; i++)
        {
          if (weights.tab[i]->tab[bestvar.tab[i]] >
              weights.tab[i + 1]->tab[bestvar.tab[i + 1]])
            {
              BA0_SWAP (struct bap_polynom_mpz *,
                  polys->tab[i],
                  polys->tab[i + 1]);
              BA0_SWAP (struct ba0_tableof_int_p *,
                  weights.tab[i],
                  weights.tab[i + 1]);
              BA0_SWAP (ba0_int_p, bestvar.tab[i], bestvar.tab[i + 1]);
              modified = true;
            }
        }
    }
/*
 * The distinguished variable
 */
  v = polys->tab[0]->total_rank.rg[bestvar.tab[0]].var;

  ba0_restore (&M);
  return v;
}

/*
 * Assigns to floor_prime a prime number of length greater than 
 *
 *             4 * (max (maxnorm (polys)) + 2)
 *
 * This prime number provides a floor value for the Hensel lifting.
 */

static void
baz_EZG_floor_prime (
    ba0_mpz_t floor_prime,
    struct bap_tableof_polynom_mpz *polys)
{
  ba0__mpz_struct *maxnorm, *max_maxnorm, *lb;
  struct ba0_mark M;
  ba0_int_p i;

  ba0_push_another_stack ();
  ba0_record (&M);
/*
 * max_maxnorm = (max (maxnorm (polys)) + 2
 */
  maxnorm = ba0_new_mpz ();
  max_maxnorm = ba0_new_mpz ();
  bap_maxnorm_polynom_mpz (max_maxnorm, polys->tab[0]);
  for (i = 1; i < polys->size; i++)
    {
      bap_maxnorm_polynom_mpz (maxnorm, polys->tab[i]);
      if (ba0_mpz_cmp (max_maxnorm, maxnorm) < 0)
        BA0_SWAP (ba0__mpz_struct *, max_maxnorm, maxnorm);
    }
  ba0_mpz_add_ui (max_maxnorm, max_maxnorm, (unsigned long int) 2);
/*
 * reuse maxnorm and call it lb, for legibility
 */
  lb = maxnorm;
  ba0_mpz_init_set_ui (lb, (unsigned long int) 1);
  ba0_mpz_mul_2exp (lb, lb, 4 * (unsigned long) ba0_mpz_sizeinbase (max_maxnorm,
          2));
  ba0_pull_stack ();
  ba0_mpz_nextprime (floor_prime, lb);
  ba0_restore (&M);
}

/*
 * The prime number of the Hensel lifting was given a floor value.
 * Some polynomials were evaluated at some evaluation point.
 * One needs to ensure that the leading coefficients of these polynomials
 * are not annihilated by the prime number.
 *
 * Assigns to lifting->p a prime number, greater than or equal to
 * floor_prime, which does not annihilate any numerical leading
 * coefficient of polys. Assigns 1 to lifting->l.
 */

static void
baz_EZG_set_modulus_part_ideal_lifting (
    struct baz_ideal_lifting *lifting,
    ba0_mpz_t floor_prime,
    struct bap_tableof_polynom_mpz *uni_polys)
{
  struct ba0_tableof_mpz lcoeff;
  struct ba0_mark M;
  ba0_mpz_t bunk;
  ba0_int_p i;
  bool found;

  ba0_mpz_set (lifting->p, floor_prime);
  lifting->l = 1;

  ba0_push_another_stack ();
  ba0_record (&M);
/*
 * lcoeff.tab [t] = the numerical leading coefficient of uni_polys->tab [t]
 */
  ba0_init_table ((struct ba0_table *) &lcoeff);
  ba0_realloc_table ((struct ba0_table *) &lcoeff, uni_polys->size);
  for (i = 0; i < uni_polys->size; i++)
    lcoeff.tab[i] = *bap_numeric_initial_polynom_mpz (uni_polys->tab[i]);
  lcoeff.size = uni_polys->size;

  ba0_mpz_init (bunk);
  do
    {
      found = true;
      for (i = 0; i < lcoeff.size && found; i++)
        {
          ba0_mpz_mod (bunk, lcoeff.tab[i], lifting->p);
          found = ba0_mpz_sgn (bunk) != 0;
        }
      if (!found)
        {
          ba0_pull_stack ();
          ba0_mpz_nextprime (lifting->p, lifting->p);
          ba0_push_another_stack ();
        }
    }
  while (!found);

  ba0_pull_stack ();
  ba0_restore (&M);
}

/*
 * The modulus of the Hensel lifting was chosen (lifting->p = p).
 * The evaluation point was chosen. One still needs to determine 
 * the factorization to be lifted. 
 * The requirement is that the factors are prime to the gcd.
 *
 * polys         = the multivariate polynomials.
 * uni_polys     = polys at the evaluation point.
 * gcd_uni_polys = the gcd of the univariate polynomials.
 *
 * Assigns to lifting->factors_mod_point a factorization
 *
 *           [ gcd_uni_polys, uni_cofactor ] mod p
 *
 * where uni_cofactor = some uni_polys.tab [i] / gcd_uni_polys mod p
 *
 * such that Gcd (gcd_uni_polys, uni_cofactor) = 1 mod p.
 * One possibly needs to consider a linear combination of uni_polys.tab [i].
 */

static void
baz_EZG_set_polynomial_part_ideal_lifting (
    struct baz_ideal_lifting *lifting,
    struct bap_tableof_polynom_mpz *polys,
    struct bap_tableof_polynom_mpz *uni_polys,
    struct bap_polynom_mpz *gcd_uni_polys)
{
  struct bap_tableof_polynom_mpzm cof_uni_poly_modp;
  struct bap_polynom_mpzm cof_comblin_modp, g_modp;
  struct bap_polynom_mpzm *gcd_uni_polys_modp, *A, *B;
  struct ba0_mark M;
  ba0_int_p nbloops, i, cA, cB;
  bool found;

  if (polys->size < 2 || uni_polys->size != polys->size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_mpzm_module_set (lifting->p, true);
/*
 * factors_mod_point = [ gcd_uni_polys, a polynomial to be determined ]
 */
  bap_set_product_one_mpzm (&lifting->factors_mod_point);
  bap_realloc_product_mpzm (&lifting->factors_mod_point, 2);
  bap_polynom_mpz_to_mpzm (&lifting->factors_mod_point.tab[0].factor,
      gcd_uni_polys);
  lifting->factors_mod_point.size = 2;
/*
 * in the sequel, one determines lifting->A,
 *                               lifting->factors_mod_point.tab [1].factor
 */
  ba0_push_another_stack ();
  ba0_record (&M);
/*
 * gcd_uni_polys_modp = gcd_uni_polys mod p
 */
  gcd_uni_polys_modp = &lifting->factors_mod_point.tab[0].factor;
  ba0_init_table ((struct ba0_table *) &cof_uni_poly_modp);
  ba0_realloc_table ((struct ba0_table *) &cof_uni_poly_modp, uni_polys->size);
  bap_init_polynom_mpzm (&g_modp);
/*
 * does there exist some i such that
 *
 *        Gcd (cof_uni_poly_modp, gcd_uni_polys_modp) = 1 mod p
 *
 * where cof_uni_poly_modp = uni_polys->tab [i] / gcd_uni_polys_modp mod p ?
 * If there does, we are done.
 */
  found = false;
  i = 0;
  while (i < uni_polys->size && !found)
    {
      cof_uni_poly_modp.tab[i] = bap_new_polynom_mpzm ();
      bap_polynom_mpz_to_mpzm (cof_uni_poly_modp.tab[i], uni_polys->tab[i]);
      bap_exquo_polynom_mpzm (cof_uni_poly_modp.tab[i],
          cof_uni_poly_modp.tab[i], gcd_uni_polys_modp);
      cof_uni_poly_modp.size += 1;
      bap_Euclid_polynom_mpzm (&g_modp, cof_uni_poly_modp.tab[i],
          gcd_uni_polys_modp);
      if (bap_is_numeric_polynom_mpzm (&g_modp))
        found = true;
      else
        i += 1;
    }
  if (found)
    {
      ba0_pull_stack ();
      bap_set_polynom_mpz (lifting->A, polys->tab[i]);
      bap_set_polynom_mpzm (&lifting->factors_mod_point.tab[1].factor,
          cof_uni_poly_modp.tab[i]);
      ba0_restore (&M);
      return;
    }
/*
 * There does not exist any such i. 
 * We are doomed to enumerate linear combinations of the two first polynomials.
 *
 *            cA   1  2  1  3  2  4
 * Enumerate  -- = -, -, -, -, -, -, ...
 *            cB   1  1  2  2  3  3
 *
 */
  bap_init_polynom_mpzm (&cof_comblin_modp);
  A = cof_uni_poly_modp.tab[0];
  B = cof_uni_poly_modp.tab[1];
  cA = 1;
  cB = 1;

  for (nbloops = 0; !found; nbloops++)
    {
      bap_comblin_polynom_mpzm (&cof_comblin_modp, A, cA, B, cB);
      bap_Euclid_polynom_mpzm (&g_modp, &cof_comblin_modp, gcd_uni_polys_modp);
      if (bap_is_numeric_polynom_mpzm (&g_modp))
        found = true;
      else if (cA == 1)
        cA = 2;
      else if (cA > cB)
        BA0_SWAP (ba0_int_p, cA, cB);
      else
        cA += 2;
    }

  ba0_pull_stack ();
  bap_comblin_polynom_mpz (lifting->A, polys->tab[0], cA, polys->tab[1], cB);
  bap_set_polynom_mpzm (&lifting->factors_mod_point.tab[1].factor,
      &cof_comblin_modp);
  ba0_restore (&M);
}

/*
 * texinfo: baz_extended_Zassenhaus_gcd_tableof_polynom_mpz
 * Assign to @var{G} the gcd of the polynomials in @var{polys0}, computed
 * using the extended Zassenhaus gcd algorithm.
 * If @var{giveup} is @code{true} then the gcd algorithms (recursively called
 * by this function) which are considered as the most costly are not called
 * and the function may fail to compute a complete gcd.
 */

BAZ_DLL void
baz_extended_Zassenhaus_gcd_tableof_polynom_mpz (
    struct bap_product_mpz *G,
    struct bap_tableof_polynom_mpz *polys0,
    bool giveup)
{
  struct baz_ideal_lifting lifting;
  struct bap_itercoeff_mpz iter;
  struct bap_tableof_polynom_mpz polys, polys1, uni_polys, nonzero;
  struct bap_product_mpz tmp_prod, gcd_cont, lifted_factors;
  struct bap_polynom_mpz tmp, gcd_uni_polys;
  struct bap_polynom_mpz volatile *gcd;

  struct bav_term term_one;
  struct bav_rank rg;
  struct bav_variable volatile *x = BAV_NOT_A_VARIABLE;
  volatile bav_Iordering r, r0;
  volatile bav_Idegree degre_x;

  struct ba0_mark M;
  ba0_mpz_t floor_prime;
  volatile ba0_int_p nb_confirm, nb_tries, nb_success;
  ba0_int_p i;
  bool found;

  ba0_push_another_stack ();
  ba0_record (&M);
/*
 * Any modular operation requires ba0_mpzm_module to be set.
 */
  ba0_mpz_init (floor_prime);
  baz_EZG_floor_prime (floor_prime, polys0);
  ba0_mpzm_module_set (floor_prime, true);

  baz_HL_init_ideal_lifting (&lifting);
/*
 * polys = the nonzero entries to polys0
 * polys gets modified a few lines afterwards
 */
  ba0_init_table ((struct ba0_table *) &polys);
  ba0_realloc_table ((struct ba0_table *) &polys, polys0->size);
  for (i = 0; i < polys0->size; i++)
    {
      if (!bap_is_zero_polynom_mpz (polys0->tab[i]))
        {
          polys.tab[polys.size] = polys0->tab[i];
          polys.size += 1;
        }
    }
/*
 * Get rid of degenerate cases
 */
  if (polys.size < 2)
    {
      ba0_pull_stack ();
      if (polys.size == 0)
        bap_set_product_zero_mpz (G);
      else
        bap_set_product_polynom_mpz (G, polys.tab[0], 1);
      ba0_restore (&M);
      return;
    }
/*
 * the distinguished variable becomes the leading variable.
 * polys is sorted by increasing "complexity".
 * polys.tab [i] is sorted with respect to the new ordering.
 */
  x = baz_EZG_distinguished_variable (&polys);

  r0 = bav_current_ordering ();
  r = bav_R_copy_ordering (r0);
  bav_push_ordering (r);

  bav_R_set_maximal_variable ((struct bav_variable *) x);
  bap_init_readonly_polynom_mpz (&tmp);
  for (i = 0; i < polys.size; i++)
    {
      bap_sort_polynom_mpz (&tmp, polys.tab[i]);
      polys.tab[i] = (struct bap_polynom_mpz *) bap_copy_polynom_mpz (&tmp);
    }
/*
 * lifting.point receives [y1 = 0, ..., yk = 0] (x is shifted out)
 */
  bap_set_point_polynom_mpz ((struct ba0_point *) &lifting.point, polys.tab[0],
      false);
/*
 * gcd_cont = the gcd of the contents of the polynomials, with respect to x.
 *
 * Compute first gcd_cont, which is smaller than each content.
 * Then simplify each polynomial and remove the content of what is left.
 */
  bap_init_product_mpz (&gcd_cont);
  bap_init_polynom_mpz (&tmp);
  baz_content_tableof_polynom_mpz (&gcd_cont, &polys, (struct bav_variable *) x,
      giveup);
  if (!bap_is_one_product_mpz (&gcd_cont))
    {
      bap_expand_product_mpz (&tmp, &gcd_cont);
      for (i = 0; i < polys.size; i++)
        bap_exquo_polynom_mpz (polys.tab[i], polys.tab[i], &tmp);
    }
  ba0_init_table ((struct ba0_table *) &polys1);
  ba0_realloc_table ((struct ba0_table *) &polys1, 1);
  polys1.size = 1;
  bap_init_product_mpz (&tmp_prod);
  for (i = 0; i < polys.size; i++)
    {
      polys1.tab[0] = polys.tab[i];
      baz_content_tableof_polynom_mpz (&tmp_prod, &polys1,
          (struct bav_variable *) x, giveup);
      if (!bap_is_one_product_mpz (&tmp_prod))
        {
          bap_expand_product_mpz (&tmp, &tmp_prod);
          bap_exquo_polynom_mpz (polys.tab[i], polys.tab[i], &tmp);
        }
    }
/*
 * gcd_cont is recorded in G and can be forgotten
 */
  ba0_pull_stack ();
  bav_pull_ordering ();
  bap_sort_product_mpz (&gcd_cont, &gcd_cont);
  bap_set_product_mpz (G, &gcd_cont);
  bav_push_ordering (r);
  ba0_push_another_stack ();
/*
 * nonzero = the leading and trailing coefficients of the polynomials
 */
  ba0_init_table ((struct ba0_table *) &nonzero);
  ba0_realloc2_table ((struct ba0_table *) &nonzero, 2 * polys.size,
      (ba0_new_function *) & bap_new_readonly_polynom_mpz);
  bav_init_term (&term_one);
  for (i = 0; i < polys.size; i++)
    {
      bap_begin_itercoeff_mpz (&iter, polys.tab[i], (struct bav_variable *) x);
      bap_coeff_itercoeff_mpz (nonzero.tab[nonzero.size], &iter);
      bap_seek_coeff_itercoeff_mpz (nonzero.tab[nonzero.size + 1], &iter,
          &term_one);
      bap_coeff_itercoeff_mpz (nonzero.tab[nonzero.size + 1], &iter);
      nonzero.size += 2;
    }
  bap_set_product_one_mpz (&tmp_prod);

  ba0_init_table ((struct ba0_table *) &uni_polys);
  ba0_realloc2_table ((struct ba0_table *) &uni_polys, polys.size,
      (ba0_new_function *) & bap_new_polynom_mpz);

  bap_init_polynom_mpz (&gcd_uni_polys);
  bap_init_product_mpz (&lifted_factors);

  nb_confirm = 2;
  nb_success = 0;
  nb_tries = 0;
  degre_x = BA0_MAX_INT_P;

  found = false;
  while (!found)
    {
      while (degre_x > 0 && nb_success < nb_confirm)
        {
          nb_tries += 1;
          baz_yet_another_point_int_p_mpz (&lifting.point, &nonzero, &tmp_prod,
              BAV_NOT_A_VARIABLE);

          ba0_reset_table ((struct ba0_table *) &uni_polys);
          for (i = 0; i < polys.size; i++)
            {
              bap_evalcoeff_at_point_int_p_polynom_mpz (uni_polys.tab[i],
                  polys.tab[i], &lifting.point);
              uni_polys.size += 1;
            }
          baz_gcd_univariate_tableof_polynom_mpz (&gcd_uni_polys, &uni_polys);
          rg = bap_rank_polynom_mpz (&gcd_uni_polys);
          if (rg.deg < degre_x)
            {
              degre_x = rg.deg;
              nb_success = 1;
            }
          else if (rg.deg == degre_x)
            nb_success++;
        }
      if (degre_x == 0)
/*
 * the univariate gcd is one: we are done
 */
        {
          found = true;
          continue;
        }
      i = 0;
      while (i < polys.size
          && degre_x < bap_leading_degree_polynom_mpz (polys.tab[i]))
        i += 1;
      if (i < polys.size)
        {
/*
 * the univariate gcd has the same leading degree as polys.tab [i]
 */
          if (bap_is_factor_tableof_polynom_mpz (polys.tab[i], &polys))
            {
/*
 * polys.tab [i] divides each polys.tab [k]: we are done
 *
 * this test was not exactly done by the calling function because the
 * multivariate polynomials were not yet primitive.
 */
              ba0_pull_stack ();
              bav_pull_ordering ();
              bap_sort_polynom_mpz (polys.tab[i], polys.tab[i]);
              bap_mul_product_polynom_mpz (G, G, polys.tab[i], 1);
              bav_push_ordering (r);
              ba0_push_another_stack ();
              found = true;
              continue;
            }
/*
 * polys.tab [i] does not divide each polys.tab [k]: unlucky evaluation point
 */
          degre_x -= 1;
          nb_success = 0;
          continue;
        }
/*
 * the univariate gcd has degree strictly less than the leading degree
 * of any polys.tab [i]. Start Hensel lifting.
 *
 * first set the prime number
 */
      baz_EZG_set_modulus_part_ideal_lifting (&lifting, floor_prime,
          &uni_polys);
/*
 * make the univariate polynomials numerically primitive
 */
      for (i = 0; i < uni_polys.size; i++)
        bap_normal_numeric_primpart_polynom_mpz (uni_polys.tab[i],
            uni_polys.tab[i]);
      bap_normal_numeric_primpart_polynom_mpz (&gcd_uni_polys, &gcd_uni_polys);
/*
 * set the polynomial to be lifted
 */
      baz_EZG_set_polynomial_part_ideal_lifting (&lifting, &polys, &uni_polys,
          &gcd_uni_polys);
/*
 * the problem of the leading coefficient
 */
      bap_initial_polynom_mpz (lifting.initial, lifting.A);
      baz_factor_polynom_mpz (&lifting.factors_initial, lifting.initial);

      BA0_TRY
      {
        baz_HL_redistribute_the_factors_of_the_initial (&lifting);
      }
      BA0_CATCH
      {
        if (ba0_global.exception.raised != BAZ_EXHDIS)
          BA0_RE_RAISE_EXCEPTION;
        nb_success -= 1;
        continue;
      }
      BA0_ENDTRY BA0_TRY
      {
        baz_HL_ideal_Hensel_lifting (
            &lifted_factors,
            &lifting);
      }
      BA0_CATCH
      {
        if (ba0_global.exception.raised != BAP_EXHNCP
            && ba0_global.exception.raised != BAZ_EXHENS)
          BA0_RE_RAISE_EXCEPTION;
        nb_success -= 1;
        continue;
      }
      BA0_ENDTRY;
/*
 * the gcd is supposed to be found in &lifted_factors.tab [0].factor
 */
      gcd = &lifted_factors.tab[0].factor;
      bap_normal_numeric_primpart_polynom_mpz ((struct bap_polynom_mpz *) gcd,
          (struct bap_polynom_mpz *) gcd);
      if (bap_is_factor_tableof_polynom_mpz ((struct bap_polynom_mpz *) gcd,
              &polys))
        {
          ba0_pull_stack ();
          bav_pull_ordering ();
          bap_sort_polynom_mpz ((struct bap_polynom_mpz *) gcd,
              (struct bap_polynom_mpz *) gcd);
          bap_mul_product_polynom_mpz (G, G, (struct bap_polynom_mpz *) gcd, 1);
          bav_push_ordering (r);
          ba0_push_another_stack ();
          found = true;
          continue;
        }
      else
        nb_success -= 1;
    }
  ba0_pull_stack ();
  bav_pull_ordering ();
  bav_R_free_ordering (r);

  ba0_restore (&M);
}

/*
 * FACTORED POLYNOM MPZ - DATA STRUCTURE FOR THE GCD ALGORITHM
 */

static void
baz_init_factored_polynom_mpz (
    struct baz_factored_polynom_mpz *A)
{
  bap_init_product_mpz (&A->outer);
  bap_init_polynom_mpz (&A->poly);
}

static struct baz_factored_polynom_mpz *
baz_new_factored_polynom_mpz (
    void)
{
  struct baz_factored_polynom_mpz *A;

  A = (struct baz_factored_polynom_mpz *) ba0_alloc (sizeof (struct
          baz_factored_polynom_mpz));
  baz_init_factored_polynom_mpz (A);
  return A;
}

static void
baz_printf_factored_polynom_mpz (
    void *AA)
{
  struct baz_factored_polynom_mpz *A = (struct baz_factored_polynom_mpz *) AA;

  ba0_printf ("(%Pz)*(%Az)", &A->outer, &A->poly);
}

/*
 * GCD DATA
 */

static void
baz_init_gcd_data (
    struct baz_gcd_data *gcd_data)
{
  gcd_data->proved_relatively_prime = false;
  bap_init_product_mpz (&gcd_data->common);
  ba0_init_table ((struct ba0_table *) &gcd_data->F);
}

static void
baz_reset_gcd_data (
    struct baz_gcd_data *gcd_data)
{
  gcd_data->proved_relatively_prime = false;
  bap_set_product_one_mpz (&gcd_data->common);
  ba0_reset_table ((struct ba0_table *) &gcd_data->F);
}

static void
baz_realloc_gcd_data (
    struct baz_gcd_data *gcd_data,
    ba0_int_p n)
{
  ba0_realloc2_table ((struct ba0_table *) &gcd_data->F, n,
      (ba0_new_function *) & baz_new_factored_polynom_mpz);
}

BAZ_DLL void
baz_printf_gcd_data (
    void *GG)
{
  struct baz_gcd_data *gcd_data = (struct baz_gcd_data *) GG;
  ba0_int_p i;

  ba0_put_char ('[');
  for (i = 0; i < gcd_data->F.size; i++)
    {
      if (i > 0)
        ba0_put_string (", ");
      ba0_printf ("(%Pz)*", &gcd_data->common);
      baz_printf_factored_polynom_mpz (gcd_data->F.tab[i]);
    }
  ba0_put_char (']');
}

/*
 * For qsort. See below.
 */

static int
comp_factored_polynom_ascending (
    const void *x,
    const void *y)
{
  struct baz_factored_polynom_mpz *A = *(struct baz_factored_polynom_mpz * *) x;
  struct baz_factored_polynom_mpz *B = *(struct baz_factored_polynom_mpz * *) y;
  struct bav_term TA, TB;
  struct ba0_mark M;
  enum ba0_compare_code code;

  ba0_record (&M);
  bav_init_term (&TA);
  bav_init_term (&TB);
  bap_leading_term_polynom_mpz (&TA, &A->poly);
  bap_leading_term_polynom_mpz (&TB, &B->poly);
  code = bav_compare_term (&TA, &TB);
  ba0_restore (&M);

  if (code == ba0_lt)
    return -1;
  else if (code == ba0_eq)
    return 0;
  else
    return 1;
}

/*
 * Sorts the table F by ascending leading terms.
 * Remove duplicates.
 */

static void
baz_sort_and_remove_duplicates_gcd_data (
    struct baz_gcd_data *gcd_data,
    enum ba0_sort_mode mode)
{
  ba0_int_p i;

  switch (mode)
    {
    case ba0_descending_mode:
      BA0_RAISE_EXCEPTION (BA0_ERRNYP);
      break;
    case ba0_ascending_mode:
      qsort (gcd_data->F.tab, gcd_data->F.size,
          sizeof (struct baz_factored_polynom_mpz *),
          &comp_factored_polynom_ascending);
      break;
    }
  i = 0;
  while (i < gcd_data->F.size - 1)
    {
      if (bap_equal_polynom_mpz (&gcd_data->F.tab[i]->poly,
              &gcd_data->F.tab[i + 1]->poly))
        ba0_delete_table ((struct ba0_table *) &gcd_data->F, i);
      else
        i += 1;
    }
}

/*
 * If a polynomial (poly fields) depends on a variable v which does not occur
 * in some other polynomial or which lies in Y, then replace this 
 * polynomial by its set of coefficients with respect to v. 
 *
 * The gcd part, (common field), is assumed to involve the numerical factors
 * and the obvious factors of the form x^k.
 *
 * This assumption permits us to remove such factors from the extracted
 * coefficients and move them to the outer fields.
 *
 * The table F gets sorted by increasing leading term.
 * Duplicated entries are removed.
 *
 * In principle, the polynomials in the poly fields depend on exactly the
 * same set of indeterminates. Unless the polynomials are proved relatively
 * prime (proved_relatively_prime field).
 */

static void
baz_replace_by_coefficients_gcd_data (
    struct baz_gcd_data *gcd_data,
    struct bav_tableof_variable *Y)
{
  struct bap_itercoeff_mpz iter;
  struct bap_polynom_mpz B, C;
  struct bap_polynom_mpz *A;
  struct bav_term T, Touter;
  struct bav_dictionary_variable dict_for_Z;
  struct bav_tableof_variable X, Z;
  struct ba0_tableof_int_p cntr;
  struct bav_variable *v;
  volatile bav_Iordering r = 0, r0;
  struct ba0_mark M;
  ba0_mpz_t cont;
  ba0_int_p i, j, k, d, size, log2_size;

  ba0_push_another_stack ();
  ba0_record (&M);

  size = bav_global.R.vars.size;
  log2_size = ba0_log2_int_p (size);
//  size <<= 3;     Would be nicer but is actually useless
  log2_size += 3;

  bav_init_dictionary_variable (&dict_for_Z, log2_size);
  ba0_init_table ((struct ba0_table *) &X);
  ba0_init_table ((struct ba0_table *) &Z);
  ba0_init_table ((struct ba0_table *) &cntr);
  ba0_realloc_table ((struct ba0_table *) &X, size);
  ba0_realloc_table ((struct ba0_table *) &Z, size);
  ba0_realloc_table ((struct ba0_table *) &cntr, size);

  bap_init_readonly_polynom_mpz (&B);
  bap_init_readonly_polynom_mpz (&C);
  bav_init_term (&T);
  bav_init_term (&Touter);
  ba0_mpz_init (cont);

  for (;;)
    {
/*
 * First compute:
 * Z = the set of variables which occur in the polynomials.
 * X = the set of variables which occur in some polynomials, but not 
 *      all of them, union Y.
 *
 * for each variable Z[i] we have cntr[i] = the number of polynomials
 *      in which Z[i] occurs
 */
      bav_reset_dictionary_variable (&dict_for_Z);
      ba0_reset_table ((struct ba0_table *) &Z);
      ba0_reset_table ((struct ba0_table *) &cntr);
      for (i = 0; i < gcd_data->F.size; i++)
        {
          A = &gcd_data->F.tab[i]->poly;
          for (j = 0; j < A->total_rank.size; j++)
            {
              v = A->total_rank.rg[j].var;
              k = bav_get_dictionary_variable (&dict_for_Z, &Z, v);
              if (k == BA0_NOT_AN_INDEX)
                {
                  bav_add_dictionary_variable (&dict_for_Z, &Z, v, Z.size);
                  Z.tab[Z.size] = v;
                  Z.size += 1;
                  cntr.tab[cntr.size] = 1;
                  cntr.size += 1;
                }
              else
                cntr.tab[k] += 1;
            }
        }
      ba0_reset_table ((struct ba0_table *) &X);
      for (i = 0; i < Z.size; i++)
        {
          v = Z.tab[i];
          if (cntr.tab[i] != gcd_data->F.size
              || (Y != (struct bav_tableof_variable *) 0
                  && ba0_member_table (v, (struct ba0_table *) Y)))
            {
              X.tab[X.size] = v;
              X.size += 1;
            }
        }
/*
 * Analysis of the result.
 */
      if (X.size == Z.size)
        {
/*
 * The variables which remain in the gcd_data->tab [i]->poly are the ones
 * in Z, not in X. Thus, if Z = X then we can stop.
 */
          gcd_data->proved_relatively_prime = true;
          break;
        }
      else if (X.size == 0)
/*
 * No coefficients need to be taken anymore.
 */
        break;
/*
 * r = a new ordering such that all variables of X are greater than 
 *     the other ones. 
 * v = the minimal variable of X
 */
      bav_sort_tableof_variable (&X, ba0_ascending_mode);

      r0 = bav_current_ordering ();
      r = bav_R_copy_ordering (r0);
      bav_push_ordering (r);

      for (i = 0; i < X.size; i++)
        bav_R_set_maximal_variable (X.tab[i]);
      v = X.tab[0];
/*
 * Replace each polynomial by its coefficients with respect to v
 */
      for (i = gcd_data->F.size - 1; i >= 0; i--)
        {
          A = &gcd_data->F.tab[i]->poly;
          if (A->total_rank.size != Z.size - X.size)
            {
              bap_sort_polynom_mpz (&B, A);
/*
 * Count the monomials for reallocating
 */
              d = 0;
              bap_begin_itercoeff_mpz (&iter, &B, v);
              while (!bap_outof_itercoeff_mpz (&iter))
                {
                  d += 1;
                  bap_next_itercoeff_mpz (&iter);
                }
              bap_close_itercoeff_mpz (&iter);

              ba0_pull_stack ();
              baz_realloc_gcd_data (gcd_data, gcd_data->F.size + d);
              ba0_push_another_stack ();
/*
 * Extract the coefficients
 */
              bap_begin_itercoeff_mpz (&iter, &B, v);
              while (!bap_outof_itercoeff_mpz (&iter))
                {
                  bap_coeff_itercoeff_mpz (&C, &iter);
                  bap_signed_numeric_content_polynom_mpz (cont, &C);
                  bap_minimal_total_rank_polynom_mpz (&T, &C);
                  bap_term_itercoeff_mpz (&Touter, &iter);
                  bav_mul_term (&Touter, &Touter, &T);

                  ba0_pull_stack ();

                  bap_exquo_polynom_term_mpz (&gcd_data->F.tab[gcd_data->F.
                          size]->poly, &C, &T);
/*
 * Beware to the ordering of the result
 */
                  bav_pull_ordering ();
                  bap_physort_polynom_mpz (&gcd_data->F.tab[gcd_data->F.size]->
                      poly);
                  bav_sort_term (&Touter);

                  bap_mul_product_term_mpz (&gcd_data->F.tab[gcd_data->F.size]->
                      outer, &gcd_data->F.tab[i]->outer, &Touter);
                  bap_exquo_polynom_numeric_mpz (&gcd_data->F.tab[gcd_data->F.
                          size]->poly, &gcd_data->F.tab[gcd_data->F.size]->poly,
                      cont);
                  bap_mul_product_numeric_mpz (&gcd_data->F.tab[gcd_data->F.
                          size]->outer,
                      &gcd_data->F.tab[gcd_data->F.size]->outer, cont);

                  bav_push_ordering (r);
                  ba0_push_another_stack ();
                  gcd_data->F.size += 1;
                  bap_next_itercoeff_mpz (&iter);
                }
              bap_close_itercoeff_mpz (&iter);
              ba0_delete_table ((struct ba0_table *) &gcd_data->F, i);
            }
        }

      bav_pull_ordering ();
      bav_R_free_ordering (r);
    }

  ba0_pull_stack ();
  ba0_restore (&M);

  if (!gcd_data->proved_relatively_prime)
    baz_sort_and_remove_duplicates_gcd_data (gcd_data, ba0_ascending_mode);
}

/*
 * Stores polys in gcd_data. 
 * Terminates by a call to baz_replace_by_coefficients_gcd_data.
 */

static void
baz_set_gcd_data_tableof_polynom_mpz (
    struct baz_gcd_data *gcd_data,
    struct bap_tableof_polynom_mpz *polys)
{
  struct bav_tableof_term term;
  struct bav_term TG;
  struct ba0_mark M;
  struct ba0_tableof_mpz cont;
  ba0_mpz_t contG;
  ba0_int_p i;

  baz_reset_gcd_data (gcd_data);
  baz_realloc_gcd_data (gcd_data, polys->size);

  ba0_push_another_stack ();
  ba0_record (&M);
/*
 * Skip zero polynomials. Remove the obvious factors x^k from the poly fields
 */
  bav_init_term (&TG);
  ba0_init_table ((struct ba0_table *) &term);
  ba0_realloc2_table ((struct ba0_table *) &term, polys->size,
      (ba0_new_function *) & bav_new_term);
  for (i = 0; i < polys->size; i++)
    {
      if (!bap_is_zero_polynom_mpz (polys->tab[i]))
        {
          bap_minimal_total_rank_polynom_mpz (term.tab[term.size],
              polys->tab[i]);
          ba0_pull_stack ();
          bap_exquo_polynom_term_mpz (&gcd_data->F.tab[gcd_data->F.size]->poly,
              polys->tab[i], term.tab[term.size]);
          ba0_push_another_stack ();
          term.size += 1;
          gcd_data->F.size += 1;
        }
    }
/*
 * There must be at least one non-zero polynomial
 */
  if (gcd_data->F.size == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
/*
 * The gcd of the obvious factors x^k is stored in the common field.
 */
  bav_set_term (&TG, term.tab[0]);
  for (i = 1; i < term.size; i++)
    bav_gcd_term (&TG, &TG, term.tab[i]);

  for (i = 0; i < term.size; i++)
    {
      bav_exquo_term (term.tab[i], term.tab[i], &TG);
      ba0_pull_stack ();
      bap_mul_product_term_mpz (&gcd_data->F.tab[i]->outer,
          &gcd_data->F.tab[i]->outer, term.tab[i]);
      ba0_push_another_stack ();
    }
  ba0_pull_stack ();
  bap_mul_product_term_mpz (&gcd_data->common, &gcd_data->common, &TG);
  ba0_push_another_stack ();
/*
 * Remove the numerical factors from the poly fields.
 */
  ba0_init_table ((struct ba0_table *) &cont);
  ba0_realloc2_table ((struct ba0_table *) &cont, gcd_data->F.size,
      (ba0_new_function *) & ba0_new_mpz);
  for (i = 0; i < gcd_data->F.size; i++)
    {
      bap_signed_numeric_content_polynom_mpz (cont.tab[i],
          &gcd_data->F.tab[i]->poly);
      ba0_pull_stack ();
      bap_exquo_polynom_numeric_mpz (&gcd_data->F.tab[i]->poly,
          &gcd_data->F.tab[i]->poly, cont.tab[i]);
      ba0_push_another_stack ();
    }
  cont.size = gcd_data->F.size;
/*
 * The gcd of the numerical factors is stored in the common field.
 */
  ba0_mpz_init_set (contG, cont.tab[0]);
  if (cont.size == 1)
    ba0_mpz_abs (contG, contG);
  else
    for (i = 1; i < cont.size; i++)
      ba0_mpz_gcd (contG, contG, cont.tab[i]);

  for (i = 0; i < cont.size; i++)
    {
      ba0_mpz_divexact (cont.tab[i], cont.tab[i], contG);
      ba0_pull_stack ();
      bap_mul_product_numeric_mpz (&gcd_data->F.tab[i]->outer,
          &gcd_data->F.tab[i]->outer, cont.tab[i]);
      ba0_push_another_stack ();
    }
  ba0_pull_stack ();
  bap_mul_product_numeric_mpz (&gcd_data->common, &gcd_data->common, contG);
/*
 * Calls baz_replace_by_coefficients_gcd_data with Y = empty set.
 */
  baz_replace_by_coefficients_gcd_data (gcd_data,
      (struct bav_tableof_variable *) 0);
}


/*
 * FAST TEST FOR GCD = 1
 */

/*
 * Subfunction of baz_test_relatively_prime_gcd_data.
 * Tests if A divides each gcd_data->F.tab [i]->poly.
 * If it does, moves the factor A to gcd_data->common.
 */

static bool
baz_is_true_factor_gcd_data (
    struct ba0_tableof_int_p *is_modified,
    struct baz_gcd_data *gcd_data,
    struct bap_polynom_mpz *A)
{
  struct bap_tableof_polynom_mpz T;
  struct ba0_tableof_int_p is_factor;
  struct ba0_mark M;
  ba0_int_p i;
  bool is_true_factor;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_init_table ((struct ba0_table *) &T);
  ba0_realloc2_table ((struct ba0_table *) &T, gcd_data->F.size,
      (ba0_new_function *) & bap_new_polynom_mpz);
  ba0_init_table ((struct ba0_table *) &is_factor);
  ba0_realloc_table ((struct ba0_table *) &is_factor, gcd_data->F.size);
  ba0_reset_table ((struct ba0_table *) is_modified);
  is_true_factor = true;
  for (i = 0; i < gcd_data->F.size; i++)
    {
      is_factor.tab[is_factor.size] =
          bap_is_factor_polynom_mpz (&gcd_data->F.tab[i]->poly, A,
          T.tab[T.size]);
      is_true_factor = is_true_factor && is_factor.tab[is_factor.size];
/* 
 * if a factor has been discovered then the polynomial is going
 * to be modified i.e. divided by the factor
 */
      is_modified->tab[is_modified->size] = is_factor.tab[is_factor.size];
      is_modified->size += 1;
      is_factor.size += 1;
      T.size += 1;
    }
  ba0_pull_stack ();
  if (is_true_factor)
    {
      bap_mul_product_polynom_mpz (&gcd_data->common, &gcd_data->common, A, 1);
      for (i = 0; i < gcd_data->F.size; i++)
        {
          bap_set_polynom_mpz (&gcd_data->F.tab[i]->poly, T.tab[i]);
          is_factor.tab[i] =
              bap_is_factor_polynom_mpz (&gcd_data->F.tab[i]->poly, A,
              T.tab[i]);
        }
    }
  for (i = 0; i < gcd_data->F.size; i++)
    {
      while (is_factor.tab[i])
        {
          bap_mul_product_polynom_mpz (&gcd_data->F.tab[i]->outer,
              &gcd_data->F.tab[i]->outer, A, 1);
          bap_set_polynom_mpz (&gcd_data->F.tab[i]->poly, T.tab[i]);
          is_factor.tab[i] =
              bap_is_factor_polynom_mpz (&gcd_data->F.tab[i]->poly, A,
              T.tab[i]);
        }
    }
  ba0_restore (&M);
  return is_true_factor;
}

/*
 * Subfunction of baz_test_relatively_prime_gcd_data.
 * Tests if the first poly field divides all the other ones. 
 * In that case, the gcd is found.
 * Relies more or less on the fact that the table F is sorted by
 * ascending order.
 */

static bool
baz_the_first_element_divides_them_all_gcd_data (
    struct baz_gcd_data *gcd_data)
{
  struct bap_polynom_mpz *A;
  ba0_int_p i;
  bool it_divides;

  if (gcd_data->F.size == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  A = &gcd_data->F.tab[0]->poly;
  it_divides = true;
  for (i = 1; i < gcd_data->F.size && it_divides; i++)
    it_divides =
        bap_is_factor_polynom_mpz (A, &gcd_data->F.tab[i]->poly,
        BAP_NOT_A_POLYNOM_mpz);
  return it_divides;
}

/*
 * Fast method for testing if the polys fields are relatively prime.
 * The idea consists in evaluating all the variables but one and 
 * performing univariate gcd. 
 * 
 * Each variable is tested as the selected variable.
 *
 * If all the univariate gcd are one, the polynomials are considered
 * as proved relatively prime.
 *
 * In principle, the Y table receives the set of the variables with 
 * respect to which the univariate gcds are one. However, computations
 * get interrupted whenever the polynomials are proved relatively prime.
 */

static void
baz_test_relatively_prime_gcd_data (
    struct bav_tableof_variable *Y,
    struct baz_gcd_data *gcd_data,
    ba0_int_p nbtries_per_var)
{
  struct bap_tableof_polynom_mpz polys, nonzero, unipolys;
  struct bap_product_mpz tmp_prod;
  struct bap_polynom_mpz gcd;
  struct bav_point_int_p point;
  struct ba0_tableof_int_p is_modified;
  struct bav_term *vars;
  struct bav_variable *ld, *v;
  volatile bav_Iordering r, r0;
  struct ba0_mark M;
  ba0_int_p i, j, k;
  bool b, all_gcd_are_one, v_disappeared, suspected_relatively_prime;

  if (gcd_data->F.size == 0 || gcd_data->proved_relatively_prime)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_reset_table ((struct ba0_table *) Y);

  if (gcd_data->F.size == 1)
    {
      gcd_data->proved_relatively_prime = false;
      return;
    }
/*
 * Resize Y. More or less rely on the fact that the polynomials depend 
 * on exactly the same set of variables.
 */
  vars = &gcd_data->F.tab[0]->poly.total_rank;
  ld = bap_leader_polynom_mpz (&gcd_data->F.tab[0]->poly);
  ba0_realloc_table ((struct ba0_table *) Y, vars->size);
  if (vars->size == 1)
    {
/*
 * In the univariate case, the test becomes an actual gcd computation.
 */
      ba0_push_another_stack ();
      ba0_record (&M);
      bap_init_polynom_mpz (&gcd);

      ba0_init_table ((struct ba0_table *) &unipolys);
      ba0_realloc2_table ((struct ba0_table *) &unipolys, gcd_data->F.size,
          (ba0_new_function *) & bap_new_readonly_polynom_mpz);
      unipolys.size = gcd_data->F.size;

      for (j = 0; j < gcd_data->F.size; j++)
        bap_set_readonly_polynom_mpz (unipolys.tab[j],
            &gcd_data->F.tab[j]->poly);

      baz_gcd_univariate_primitive_tableof_polynom_mpz (&gcd, &unipolys);
      ba0_pull_stack ();

      if (!bap_is_one_polynom_mpz (&gcd))
        {
          for (j = 0; j < gcd_data->F.size; j++)
            bap_exquo_polynom_mpz (&gcd_data->F.tab[j]->poly,
                &gcd_data->F.tab[j]->poly, &gcd);
          bap_mul_product_polynom_mpz (&gcd_data->common, &gcd_data->common,
              &gcd, 1);
        }
/*
 * Here, the polynomials are relatively prime and Y receives the variable.
 */
      Y->tab[0] = vars->rg[0].var;
      Y->size = 1;

      suspected_relatively_prime = true;
    }
  else
    {
      ba0_record (&M);
/*
 * Multivariate polynomials
 */
      bap_init_polynom_mpz (&gcd);
      ba0_init_table ((struct ba0_table *) &polys);
      ba0_realloc2_table ((struct ba0_table *) &polys, gcd_data->F.size,
          (ba0_new_function *) & bap_new_readonly_polynom_mpz);
      polys.size = gcd_data->F.size;

      ba0_init_point ((struct ba0_point *) &point);
      bap_set_point_polynom_mpz ((struct ba0_point *) &point,
          &gcd_data->F.tab[0]->poly, true);
/*
 * nonzero = polynomials which should not annihilate
 */
      ba0_init_table ((struct ba0_table *) &nonzero);
      ba0_init_table ((struct ba0_table *) &unipolys);
      ba0_realloc2_table ((struct ba0_table *) &nonzero, gcd_data->F.size,
          (ba0_new_function *) & bap_new_polynom_mpz);
      ba0_realloc2_table ((struct ba0_table *) &unipolys, gcd_data->F.size,
          (ba0_new_function *) & bap_new_polynom_mpz);
      nonzero.size = gcd_data->F.size;
      unipolys.size = gcd_data->F.size;
      ba0_init_table ((struct ba0_table *) &is_modified);
      ba0_realloc_table ((struct ba0_table *) &is_modified, gcd_data->F.size);
      bap_init_product_mpz (&tmp_prod);

      suspected_relatively_prime = true;
      for (i = 0; i < vars->size; i++)
        {
          v = point.tab[i]->var;
          if (v != ld)
            {
              r0 = bav_current_ordering ();
              r = bav_R_copy_ordering (r0);
              bav_push_ordering (r);
              bav_R_set_maximal_variable (v);
              for (j = 0; j < gcd_data->F.size; j++)
                bap_sort_polynom_mpz (polys.tab[j], &gcd_data->F.tab[j]->poly);
//              bav_sort_point_int_p (&point);
            }
          else
            {
              for (j = 0; j < gcd_data->F.size; j++)
                bap_set_readonly_polynom_mpz (polys.tab[j],
                    &gcd_data->F.tab[j]->poly);
            }
/*
 * The leading coefficients w.r.t. the ith variable must be nonzero
 */
          for (j = 0; j < gcd_data->F.size; j++)
            bap_lcoeff_polynom_mpz (nonzero.tab[j], polys.tab[j], v);
/*
 * all_gcd_are_one applies to the gcd with v being the distinguished variable.
 */
          all_gcd_are_one = true;
          v_disappeared = false;
          for (k = 0; k < nbtries_per_var && !v_disappeared; k++)
            {
/*
 * Get a new evaluation point. Do not modify the ith variable.
 */
              baz_yet_another_point_int_p_mpz (&point, &nonzero, &tmp_prod, v);
/*
 * Evaluate the polynomials and get univariate polynomials.
 * The degrees of the polynomials cannot degenerate.
 * Polynomials are made numerically primitive.
 */
              for (j = 0; j < gcd_data->F.size; j++)
                {
                  bap_evalcoeff_at_point_int_p_polynom_mpz (unipolys.tab[j],
                      polys.tab[j], &point);
                  if (bap_is_zero_polynom_mpz (unipolys.tab[j]))
                    BA0_RAISE_EXCEPTION (BA0_ERRALG);
                  bap_numeric_primpart_polynom_mpz (unipolys.tab[j],
                      unipolys.tab[j]);
                }
              baz_gcd_univariate_primitive_tableof_polynom_mpz (&gcd,
                  &unipolys);
/*
 * If the gcd is one, then we proceed with the next step.
 * If the gcd is not one, then we test if the gcd is actually a
 * true divisor of the input polynomials. 
 * - If it is, then we simplify the input polynomials and proceed 
 *   with the next step as if the gcd had been one. 
 * - If it is not, the polynomials are proved not relatively prime 
 *   and we can stop.
 *
 * Since the input polynomials are numerically primitive, so are
 * their factors.
 */
              if (!bap_is_numeric_polynom_mpz (&gcd))
                {
                  ba0_pull_stack ();
                  if (v != ld)
                    {
                      bav_pull_ordering ();
                      bap_physort_polynom_mpz (&gcd);
                      b = baz_is_true_factor_gcd_data (&is_modified, gcd_data,
                          &gcd);
                      bav_push_ordering (r);
                    }
                  else
                    b = baz_is_true_factor_gcd_data (&is_modified, gcd_data,
                        &gcd);
/*
 * If b is true then a true factor has been discovered and 
 * the polynomials, after division by the true factor, have
 * a gcd equal to one. Thus all_gcd_are_one is kept as is.
 * If b is false then, since the gcd is not numeric, we
 * can toggle all_gcd_are_one to false.
 */
                  if (!b)
                    all_gcd_are_one = false;
/*
 * gcd_data was modified. Then rebuild polys.
 */
                  for (j = 0; j < gcd_data->F.size && !v_disappeared; j++)
                    if (is_modified.tab[j])
                      v_disappeared =
                          !bap_depend_polynom_mpz (&gcd_data->F.tab[j]->poly,
                          v);
                  if (v != ld)
                    {
                      for (j = 0; j < gcd_data->F.size; j++)
                        if (is_modified.tab[j])
                          bap_sort_polynom_mpz (polys.tab[j],
                              &gcd_data->F.tab[j]->poly);
                    }
                  else
                    {
                      for (j = 0; j < gcd_data->F.size; j++)
                        if (is_modified.tab[j])
                          bap_set_readonly_polynom_mpz (polys.tab[j],
                              &gcd_data->F.tab[j]->poly);
                    }
                  ba0_push_another_stack ();
                }
            }
          if (v != ld)
            {
              bav_pull_ordering ();
              bav_R_free_ordering (r);
            }
          if (all_gcd_are_one || v_disappeared)
            {
              if (ba0_member_table (v, (struct ba0_table *) Y))
                BA0_RAISE_EXCEPTION (BA0_ERRALG);
              Y->tab[Y->size] = v;
              Y->size += 1;
            }
          else
            suspected_relatively_prime = false;
        }
    }
  ba0_restore (&M);
  gcd_data->proved_relatively_prime = suspected_relatively_prime;
}

/*
 * Assigns the gcd of A and B to G. 
 * Polynomials cofA, cofB - if nonzero - receive A/G and B/G.
 */

/*
 * texinfo: baz_gcd_polynom_mpz
 * Assign to @var{G} the gcd of the polynomials @var{A} and @var{B}.
 * The polynomials @var{cofA} and @var{cofB} are assigned @math{A/G} and
 * @math{B/G}. The parameters @var{G}, @var{cofA} and @var{cofB} may
 * be the zero pointer. 
 */

BAZ_DLL void
baz_gcd_polynom_mpz (
    struct bap_polynom_mpz *G,
    struct bap_polynom_mpz *cofA,
    struct bap_polynom_mpz *cofB,
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *B)
{
  struct bap_tableof_polynom_mpz polys;
  struct bap_product_mpz prod_G2;
  struct bap_polynom_mpz G2, cofA2, cofB2;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_init_table ((struct ba0_table *) &polys);
  ba0_realloc_table ((struct ba0_table *) &polys, 2);
  polys.tab[0] = A;
  polys.tab[1] = B;
  polys.size = 2;
  bap_init_product_mpz (&prod_G2);
  bap_init_polynom_mpz (&G2);
  bap_init_polynom_mpz (&cofA2);
  bap_init_polynom_mpz (&cofB2);
  baz_gcd_tableof_polynom_mpz (&prod_G2, &polys, false);
  bap_expand_product_mpz (&G2, &prod_G2);
  if (cofA != BAP_NOT_A_POLYNOM_mpz)
    bap_exquo_polynom_mpz (&cofA2, A, &G2);
  if (cofB != BAP_NOT_A_POLYNOM_mpz)
    bap_exquo_polynom_mpz (&cofB2, B, &G2);
  ba0_pull_stack ();
  if (G != BAP_NOT_A_POLYNOM_mpz)
    bap_set_polynom_mpz (G, &G2);
  if (cofA != BAP_NOT_A_POLYNOM_mpz)
    bap_set_polynom_mpz (cofA, &cofA2);
  if (cofB != BAP_NOT_A_POLYNOM_mpz)
    bap_set_polynom_mpz (cofB, &cofB2);
  ba0_restore (&M);
}

/*
 * Assigns to G the gcd of the elements of polys
 */

/*
 * texinfo: baz_gcd_tableof_polynom_mpz
 * Assign to @var{G} the gcd of the polynomials in @var{polys0}.
 * This function relies on many different algorithms.
 * If @var{giveup} is @code{true} then the algorithms which are considered
 * as the most costly are not called and the function may fail to compute
 * a complete gcd.
 */

BAZ_DLL void
baz_gcd_tableof_polynom_mpz (
    struct bap_product_mpz *G,
    struct bap_tableof_polynom_mpz *polys,
    bool giveup)
{
  struct baz_gcd_data gcd_data;
  struct bap_product_mpz prod_gcd;
  struct bap_tableof_polynom_mpz polys2;
  struct bap_polynom_mpz gcd;
  struct bav_tableof_variable Y;
  struct ba0_mark M;
  ba0_int_p i;

  ba0_push_another_stack ();
  ba0_record (&M);

  baz_init_gcd_data (&gcd_data);
  ba0_init_table ((struct ba0_table *) &Y);
/*
 * First sets gcd_data with polys. 
 *
 * Then apply the fast test for relative primality (nbtries_per_var = 2). 
 *
 * Then, if the test does not prove relative primality, one gets a set Y of
 * variables which permits to replace further polynomials by their 
 * coefficients.
 *
 * The polynomials can be proved relatively prime at each stage.
 */
  baz_set_gcd_data_tableof_polynom_mpz (&gcd_data, polys);
  if (!gcd_data.proved_relatively_prime)
    baz_test_relatively_prime_gcd_data (&Y, &gcd_data, 2);
  if (!gcd_data.proved_relatively_prime)
    baz_replace_by_coefficients_gcd_data (&gcd_data, &Y);

  if (gcd_data.proved_relatively_prime)
    {
/*
 * Univariate polynomials are handled here.
 */
      ba0_pull_stack ();
      bap_set_product_mpz (G, &gcd_data.common);
    }
  else if (baz_the_first_element_divides_them_all_gcd_data (&gcd_data))
    {
/*
 * The case of a single polynomial is handled here
 */
      ba0_pull_stack ();
      bap_mul_product_polynom_mpz (G, &gcd_data.common,
          &gcd_data.F.tab[0]->poly, 1);
    }
  else
    {
      BA0_TRY
      {
/*
 * Try the heuristic gcd
 */
        bap_init_polynom_mpz (&gcd);
        ba0_init_table ((struct ba0_table *) &polys2);
        ba0_realloc_table ((struct ba0_table *) &polys2, gcd_data.F.size);
        for (i = 0; i < gcd_data.F.size; i++)
          polys2.tab[i] = &gcd_data.F.tab[i]->poly;
        polys2.size = gcd_data.F.size;
        baz_gcdheu_tableof_polynom_mpz (&gcd, &polys2, 8000);
        ba0_pull_stack ();
        bap_mul_product_polynom_mpz (G, &gcd_data.common, &gcd, 1);
      }
      BA0_CATCH
      {
        if (ba0_global.exception.raised == BA0_ERROOM
            || ba0_global.exception.raised == BA0_ERRALR)
          BA0_RE_RAISE_EXCEPTION;
        if (ba0_global.exception.raised != BAZ_ERRHEU)
          BA0_RAISE_EXCEPTION (BAZ_ERRGCD);
/*
 * The heuristic gcd failed. One switches to the second method unless giveup.
 */
        if (giveup)
          {
            ba0_pull_stack ();
            bap_set_product_mpz (G, &gcd_data.common);
          }
        else
          {
/*
 * The extended Zassenhaus gcd method is only applied if giveup = false
 */
            bap_init_product_mpz (&prod_gcd);
            ba0_init_table ((struct ba0_table *) &polys2);
            ba0_realloc_table ((struct ba0_table *) &polys2, gcd_data.F.size);
            for (i = 0; i < gcd_data.F.size; i++)
              polys2.tab[i] = &gcd_data.F.tab[i]->poly;
            polys2.size = gcd_data.F.size;
            baz_extended_Zassenhaus_gcd_tableof_polynom_mpz (&prod_gcd, &polys2,
                false);
            ba0_pull_stack ();
            bap_mul_product_mpz (G, &gcd_data.common, &prod_gcd);
          }
      }
      BA0_ENDTRY;
    }
  ba0_restore (&M);
}

/*
 * Only applies if x is zero or greater than or equal to 
 * the leader of each polynomial. 
 *
 * polys0 is assumed to involve non-numeric polynomials only
 */

static void
baz_content2_tableof_polynom_mpz (
    struct bap_product_mpz *G,
    struct bap_tableof_polynom_mpz *polys0,
    struct bav_variable *x,
    bool giveup)
{
  struct bap_itercoeff_mpz iter;
  struct bap_tableof_polynom_mpz polys;
  struct bav_variable *v, *y;
  struct ba0_mark M;
  ba0_int_p i, nbcoeff;

  if (x != BAV_NOT_A_VARIABLE)
    {
      nbcoeff = 0;
      for (i = 0; i < polys0->size; i++)
        {
          y = bap_leader_polynom_mpz (polys0->tab[i]);
          if (x == y)
            nbcoeff += bap_leading_degree_polynom_mpz (polys0->tab[i]) + 1;
          else if (bav_gt_variable (y, x))
            BA0_RAISE_EXCEPTION (BA0_ERRALG);
          else
            nbcoeff += 1;
        }
      v = x;
    }
  else
    {
      v = BAV_NOT_A_VARIABLE;
      for (i = 0; i < polys0->size; i++)
        {
/* 
 * Should be a useless test. Safer code anyway.
 */
          if (!bap_is_numeric_polynom_mpz (polys0->tab[i]))
            {
              y = bap_leader_polynom_mpz (polys0->tab[i]);
              if (v == BAV_NOT_A_VARIABLE || bav_gt_variable (y, v))
                v = y;
            }
        }
      if (v == BAV_NOT_A_VARIABLE)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
/*
 * v is the maximum of the variables occurring in polys0
 */
      nbcoeff = 0;
      for (i = 0; i < polys0->size; i++)
        {
          y = bap_leader_polynom_mpz (polys0->tab[i]);
          if (y == v)
            nbcoeff += bap_leading_degree_polynom_mpz (polys0->tab[i]) + 1;
          else
            nbcoeff += 1;
        }
    }
/*
 * From now on, work with v. Number of coefficients of polys0 wrt v = nbcoeff
 */
  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_init_table ((struct ba0_table *) &polys);
  ba0_realloc2_table ((struct ba0_table *) &polys, nbcoeff,
      (ba0_new_function *) & bap_new_readonly_polynom_mpz);
  for (i = 0; i < polys0->size; i++)
    {
      bap_begin_itercoeff_mpz (&iter, polys0->tab[i], v);
      while (!bap_outof_itercoeff_mpz (&iter))
        {
          bap_coeff_itercoeff_mpz (polys.tab[polys.size], &iter);
          polys.size += 1;
          bap_next_itercoeff_mpz (&iter);
        }
      bap_close_itercoeff_mpz (&iter);
    }
  ba0_pull_stack ();
  baz_gcd_tableof_polynom_mpz (G, &polys, giveup);
  ba0_restore (&M);
}

/*
 * texinfo: baz_content_tableof_polynom_mpz
 * Assign to @var{G} the gcd of the coefficients of the elements
 * of @var{polys0} with respect to @var{v} (or the
 * highest derivative occurring in @var{polys0}, if @var{v} is zero).
 * This function relies on @code{baz_gcd_tableof_polynom_mpz}.
 * If @var{giveup} is @code{true} then the algorithms which are considered
 * as the most costly are not called and the function may fail to compute
 * a complete gcd.
 */

BAZ_DLL void
baz_content_tableof_polynom_mpz (
    struct bap_product_mpz *G,
    struct bap_tableof_polynom_mpz *polys0,
    struct bav_variable *x,
    bool giveup)
{
  struct bap_product_mpz gcd_prod;
  struct bap_tableof_polynom_mpz polys1, polys2;
  struct bav_variable *v, *w;
  volatile bav_Iordering r = 0, r0;
  struct ba0_mark M;
  ba0_int_p i;
  bool nonzero_constant;
/*
 * At least one nonzero polynomial. 
 */
  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_init_table ((struct ba0_table *) &polys1);
  ba0_realloc_table ((struct ba0_table *) &polys1, polys0->size);
  nonzero_constant = false;
  for (i = 0; i < polys0->size; i++)
    {
      if (!bap_is_zero_polynom_mpz (polys0->tab[i]))
        {
          nonzero_constant = nonzero_constant
              || bap_is_numeric_polynom_mpz (polys0->tab[i]);
          polys1.tab[polys1.size] = polys0->tab[i];
          polys1.size += 1;
        }
    }
  ba0_pull_stack ();

  if (polys1.size < 1)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
/*
 * if x is zero then baz_content2_tableof_polynom_mpz
 */
  if (nonzero_constant)
    baz_gcd_tableof_polynom_mpz (G, &polys1, giveup);
  else if (x == BAV_NOT_A_VARIABLE)
    baz_content2_tableof_polynom_mpz (G, &polys1, x, giveup);
  else
    {
/*
 * v = the maximum of the leaders of the elements of polys0
 */
      v = bap_leader_polynom_mpz (polys1.tab[0]);
      for (i = 1; i < polys1.size; i++)
        {
          w = bap_leader_polynom_mpz (polys1.tab[i]);
          if (bav_gt_variable (w, v))
            v = w;
        }
/*
 * if x >= v then baz_content2_tableof_polynom_mpz
 */
      if (x == v || bav_gt_variable (x, v))
        baz_content2_tableof_polynom_mpz (G, &polys1, x, giveup);
      else
        {
/*
 * change ordering, then call baz_content2_tableof_polynom_mpz
 */
          ba0_push_another_stack ();

          r0 = bav_current_ordering ();
          r = bav_R_copy_ordering (r0);
          bav_push_ordering (r);
          bav_R_set_maximal_variable (x);

          ba0_init_table ((struct ba0_table *) &polys2);
          ba0_realloc2_table ((struct ba0_table *) &polys2, polys1.size,
              (ba0_new_function *) & bap_new_readonly_polynom_mpz);
          for (i = 0; i < polys1.size; i++)
            {
              bap_sort_polynom_mpz (polys2.tab[polys2.size], polys1.tab[i]);
              polys2.size += 1;
            }
          bap_init_product_mpz (&gcd_prod);
          baz_content2_tableof_polynom_mpz (&gcd_prod, &polys2, x, giveup);

          bav_pull_ordering ();
          bav_R_free_ordering (r);

          bap_sort_product_mpz (&gcd_prod, &gcd_prod);

          ba0_pull_stack ();
          bap_set_product_mpz (G, &gcd_prod);
        }
    }
  ba0_restore (&M);
}

/*
 * texinfo: baz_content_polynom_mpz
 * Assign to @var{R} the content of @var{A} w.r.t. variable @var{v} or
 * its leader, if @var{v} is zero.
 */

BAZ_DLL void
baz_content_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A,
    struct bav_variable *v)
{
  struct bap_tableof_polynom_mpz polys;
  struct bap_product_mpz cont_prod;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_init_table ((struct ba0_table *) &polys);
  ba0_realloc_table ((struct ba0_table *) &polys, 1);
  polys.tab[0] = A;
  polys.size = 1;
  bap_init_product_mpz (&cont_prod);
  baz_content_tableof_polynom_mpz (&cont_prod, &polys, v, false);
  ba0_pull_stack ();
  bap_expand_product_mpz (R, &cont_prod);
  ba0_restore (&M);
}

/*
 * texinfo: baz_primpart_polynom_mpz
 * Assign to @var{R} the primitive part of @var{A} w.r.t. variable @var{v} or
 * its leader, if @var{v} is zero.
 */

BAZ_DLL void
baz_primpart_polynom_mpz (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpz *A,
    struct bav_variable *v)
{
  struct bap_polynom_mpz cont;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  bap_init_polynom_mpz (&cont);
  baz_content_polynom_mpz (&cont, A, v);
  ba0_pull_stack ();
  bap_exquo_polynom_mpz (R, A, &cont);
  ba0_restore (&M);
}

/*
 * Yun := proc (P0)
 *     local x, cont, F, FP, A, B, BP, C, D, d, result;
 *     if indets (P0) = {} then
 *         return P0;
 *     else
 *         x := indets (P0) [1];
 *         cont := content (P0, x, 'F');
 *         FP := diff (F, x);
 *         A := gcd (F, FP);
 *         d := 1;
 *         B := normal (F / A);
 *         BP := diff (B, x);
 *         C := normal (FP / A);
 *         D := C - BP;
 *         result := NULL;
 *         do
 *             A := gcd (B, D);
 *             if A <> 1 then
 *                 result := result, A^d;
 *             end if;
 *             B := normal (B / A);
 *             if B = 1 or B = -1 then break end if;
 *             BP := diff (B, x);
 *             C := normal (D / A);
 *             D := C - BP;
 *             d := d + 1
 *         end do;
 *         return B*cont, result;
 *     end if
 * end proc:
 */

/*
 * Let x be an indeterminate
 * Assume F = a * F1 * F2^2 * ... * Fn^n where:
 * - deg (a, x) = 0
 * - the Fi are squarefree
 * - gcd (Fi, Fj) = 1 whenever i <> j
 * Then
 * F' =       a * F1' * F2^2 * ... * Fn^n 
 *      + 2 * a * F1 + F2 * F2' * ... * Fn^n
 *      + ...
 *      * n * a * F1 * F2^2 * ... * n * Fn^(n-1) * Fn'.
 *    = a * F2 * F3^2 * ... * Fn^(n-1) * 
 *      [ F1' * F2  * ... * Fn + F1 * F2' * ... * Fn + ... + 
 *                                                 F1 * F2 * ... * Fn' ]
 * A0 = gcd (F, F') 
 *    = a * F2 * F3^2 * ... * Fn^(n-1)
 * B1 = F / A0
 *    = F1 * F2 * ... * Fn
 * C1 = F' / A0 
 *    = F1' * F2  * ... * Fn + 2 * F1 * F2' * ... * Fn + ... + 
 *                                                 n * F1 * F2 * ... * Fn'
 * D1 = C1 - B1'
 *    = F1 * F2' * ... * Fn + 2 * F1 * F2 * F3' * ... * Fn + ... +
 *                                                 (n-1) * F1 * F2 * ... * Fn'
 * A1 = gcd (B1, D1)
 *    = F1
 * B2 = B1 / A1
 *    = F2 * F3 * ... * Fn
 * C2 = D1 / A1
 *    = F2' * ... * Fn + 2 * F2 * F3' * ... * Fn + ... + (n-1) * F2 * ... * Fn'
 * D2 = C2 - B2'
 *    = F2 * F3' * ... * Fn + ... + (n-2) * F2 * ... * Fn'
 */

/*
 * texinfo: baz_Yun_polynom_mpz
 * Assign to @var{prod} the squarefree decomposition of @var{P0} in the sense
 * of Yun, w.r.t. its leading derivative. 
 * If @var{giveup} is @code{true} then the algorithms which are considered
 * as the most costly are not called and the function may fail to compute
 * a complete gcd.
 * This function relies on @code{baz_gcd_tableof_polynom_mpz}.
 */

BAZ_DLL void
baz_Yun_polynom_mpz (
    struct bap_product_mpz *prod,
    struct bap_polynom_mpz *P0,
    bool giveup)
{
  struct bap_tableof_polynom_mpz polys;
  struct bap_product_mpz cont, result, A;
  struct bap_polynom_mpz F, FP, B, BP, C, D;
  struct bav_variable *x;
  bav_Idegree d;
  struct ba0_mark M;
  ba0_int_p i;

  if (bap_is_numeric_polynom_mpz (P0))
    {
      bap_set_product_polynom_mpz (prod, P0, 1);
      return;
    }

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_init_table ((struct ba0_table *) &polys);
  ba0_realloc_table ((struct ba0_table *) &polys, 2);
  bap_init_product_mpz (&result);
  bap_init_product_mpz (&cont);
  bap_init_product_mpz (&A);
  bap_init_polynom_mpz (&F);
  bap_init_polynom_mpz (&FP);
  bap_init_polynom_mpz (&B);
  bap_init_polynom_mpz (&BP);
  bap_init_polynom_mpz (&C);
  bap_init_polynom_mpz (&D);

  x = bap_leader_polynom_mpz (P0);

  polys.tab[0] = P0;
  polys.size = 1;
  baz_content_tableof_polynom_mpz (&cont, &polys, x, giveup);

  bap_exquo_polynom_product_mpz (&F, P0, &cont);

  bap_separant2_polynom_mpz (&FP, &F, x);

  polys.tab[0] = &F;
  polys.tab[1] = &FP;
  polys.size = 2;
  baz_gcd_tableof_polynom_mpz (&A, &polys, giveup);

  d = 1;
  bap_exquo_polynom_product_mpz (&B, &F, &A);
  bap_separant2_polynom_mpz (&BP, &B, x);
  bap_exquo_polynom_product_mpz (&C, &FP, &A);
  bap_sub_polynom_mpz (&D, &C, &BP);

  for (;;)
    {
      polys.tab[0] = &B;
      polys.tab[1] = &D;
      baz_gcd_tableof_polynom_mpz (&A, &polys, giveup);
      if (!bap_is_numeric_product_mpz (&A))
        {
/*
 * A bit complicated stuff because the multiplication by a power of
 * a product is not implemented. Observe A is a product of irreducible
 * simple factors and that there is no content anymore.
 */
          bap_pow_product_mpz (&A, &A, d);
          bap_mul_product_mpz (&result, &result, &A);
          if (!ba0_mpz_is_one (A.num_factor))
            BA0_RAISE_EXCEPTION (BA0_ERRALG);
          for (i = 0; i < A.size; i++)
            {
              if (A.tab[i].exponent != d)
                BA0_RAISE_EXCEPTION (BA0_ERRALG);
              A.tab[i].exponent = 1;
            }
        }
      d += 1;
      bap_exquo_polynom_product_mpz (&B, &B, &A);
      if (bap_is_numeric_polynom_mpz (&B))
        break;
      bap_separant2_polynom_mpz (&BP, &B, x);
      bap_exquo_polynom_product_mpz (&C, &D, &A);
      bap_sub_polynom_mpz (&D, &C, &BP);
    }
  ba0_pull_stack ();
  bap_mul_product_mpz (prod, &result, &cont);
  if (!bap_is_one_polynom_mpz (&B))
    bap_mul_product_polynom_mpz (prod, prod, &B, 1);
  ba0_restore (&M);
}

/*
 * Assigns the Yun squarefree decomposition of A to prod.
 * It is assumed that A is numerically primitive.
 */

/*
 * texinfo: baz_squarefree_polynom_mpz
 * Call @code{baz_Yun_polynom_mpz} with @var{giveup} equal to @code{false}.
 */

BAZ_DLL void
baz_squarefree_polynom_mpz (
    struct bap_product_mpz *prod,
    struct bap_polynom_mpz *A)
{
  baz_Yun_polynom_mpz (prod, A, false);
}


/*
 * FACTOR EASY
 */

/*
 * For qsort. See below.
 */

static int
comp_nbmon_ascending_polynom_mpz (
    const void *x,
    const void *y)
{
  struct bap_polynom_mpz *A = *(struct bap_polynom_mpz * *) x;
  struct bap_polynom_mpz *B = *(struct bap_polynom_mpz * *) y;
  ba0_int_p nA, nB;

  nA = bap_nbmon_polynom_mpz (A);
  nB = bap_nbmon_polynom_mpz (B);
  if (nA < nB)
    return -1;
  else if (nA == nB)
    return 0;
  else
    return 1;
}

/*
 * Subfunction of baz_factor_easy_polynom_mpz
 *
 * Removes the content of A0, then performs a squarefree factorization.
 * Applies recursively to the content.
 *
 * A0 is assumed to be numerically primitive
 *
 * All computations are performed in the current stack.
 * Garbage collection is performed by the calling function.
 */

static void
baz_factor_easy2_polynom_mpz (
    struct bap_product_mpz *prod,
    struct bap_polynom_mpz *A0,
    bool giveup)
{
  struct bap_product_mpz cont, prod2;
  struct bap_tableof_polynom_mpz polys;
  struct bap_polynom_mpz B;
  ba0_int_p i;

  if (bap_is_numeric_polynom_mpz (A0) || (bap_is_univariate_polynom_mpz (A0)
          && bap_leading_degree_polynom_mpz (A0) == 1))
    bap_set_product_polynom_mpz (prod, A0, 1);
  else
    {
      bap_set_product_one_mpz (prod);
/*
 * cont = content of A0
 */
      ba0_init_table ((struct ba0_table *) &polys);
      ba0_realloc_table ((struct ba0_table *) &polys, 1);
      polys.tab[0] = A0;
      polys.size = 1;
      bap_init_product_mpz (&cont);
      baz_content_tableof_polynom_mpz (&cont, &polys, BAV_NOT_A_VARIABLE,
          giveup);
/*
 * Recursive calls to each factor of the content
 */
      bap_init_product_mpz (&prod2);
      for (i = 0; i < cont.size; i++)
        {
          baz_factor_easy2_polynom_mpz (&prod2, &cont.tab[i].factor, giveup);
          bap_pow_product_mpz (&prod2, &prod2, cont.tab[i].exponent);
          bap_mul_product_mpz (prod, prod, &prod2);
        }
/*
 * Remove the content from A0 and performs a squarefree factorization
 * on what is left.
 */
      bap_init_polynom_mpz (&B);
      bap_exquo_polynom_product_mpz (&B, A0, &cont);
      baz_Yun_polynom_mpz (&prod2, &B, giveup);

      bap_mul_product_mpz (prod, prod, &prod2);
    }
}

/*
 * texinfo: baz_factor_easy_polynom_mpz
 * Assign to @var{prod} a factorization of @var{A0} which is not too difficult
 * to compute and not necessarily irreducible. 
 * Eventually, if a factor of @var{prod} has a nontrivial gcd with some 
 * element of @var{F0} then it divides it.
 * The argument @var{keep} is assigned a table of the same size as 
 * @var{prod}. The @math{i}th element of @var{keep} is @code{true}
 * if and only if the @math{i}th factor of @var{prod} does not divides any
 * element of @var{F0}.
 * The @code{false} entries appear in the leftmost part of @var{keep},
 * the @code{true} entries in the rightmost part.
 */

BAZ_DLL void
baz_factor_easy_polynom_mpz (
    struct bap_product_mpz *prod,
    struct ba0_tableof_bool *keep,
    struct bap_polynom_mpz *A0,
    struct bap_listof_polynom_mpz *F0)
{
  struct bap_tableof_polynom_mpz polys, F;
  struct bap_product_mpz prod0, prod1, prod2, prod3;
  struct bap_polynom_mpz A;
  struct bav_term T, U;
  struct ba0_mark M;
  ba0_mpz_t num_cont;
  ba0_int_p i, j;
  bool giveup;

  if (bap_is_numeric_polynom_mpz (A0))
    {
      bap_set_product_polynom_mpz (prod, A0, 1);
      ba0_realloc_table ((struct ba0_table *) keep, 1);
      keep->tab[0] = false;
      keep->size = 1;
      return;
    }

  giveup = true;

  ba0_push_another_stack ();
  ba0_record (&M);
/*
 * F = F0 sorted by ascending number of monomials
 */
  ba0_init_table ((struct ba0_table *) &F);
  if (F0 != (struct bap_listof_polynom_mpz *) 0)
    {
      ba0_set_table_list ((struct ba0_table *) &F, (struct ba0_list *) F0);
      qsort (F.tab, F.size, sizeof (struct bap_polynom_mpz *),
          &comp_nbmon_ascending_polynom_mpz);
    }
/*
 * Get rid of the numerical content and of the obvious factors. 
 */
  bap_init_polynom_mpz (&A);
  bav_init_term (&T);
  bav_init_term (&U);
  bap_minimal_total_rank_polynom_mpz (&T, A0);
  bap_exquo_polynom_term_mpz (&A, A0, &T);
  ba0_mpz_init (num_cont);
  bap_signed_numeric_content_polynom_mpz (num_cont, &A);
  bap_exquo_polynom_numeric_mpz (&A, &A, num_cont);
/*
 * The numerical content of A0 is in num_cont
 * The obvious factors of A0 are in prod0
 * A = A0 / prod0 / num_cont
 */
  bap_init_product_mpz (&prod0);
  bap_mul_product_term_mpz (&prod0, &prod0, &T);
/*
 * Look for common factors of A and elements of F0
 * Eventually, these common factors are in prod1
 * The remaining (non common) factor is in A
 */
  bap_init_product_mpz (&prod1);
  bap_init_product_mpz (&prod2);
  bap_init_product_mpz (&prod3);
  ba0_init_table ((struct ba0_table *) &polys);
  ba0_realloc_table ((struct ba0_table *) &polys, 2);
  polys.size = 2;

  i = 0;
  while (i < F.size && !bap_is_numeric_polynom_mpz (&A))
    {
      polys.tab[0] = &A;
      polys.tab[1] = F.tab[i];
      baz_gcd_tableof_polynom_mpz (&prod2, &polys, giveup);
/*
 * prod2 = gcd (A, F.tab [i])
 */
      if (!bap_is_one_product_mpz (&prod2))
        {
/*
 * A = A / prod2
 * Apply factor_easy2 over factor of prod2 before recording in prod1
 */
          bap_exquo_polynom_product_mpz (&A, &A, &prod2);
          if (ba0_mpz_cmp_ui (prod2.num_factor, (unsigned long int) 1) != 0)
            BA0_RAISE_EXCEPTION (BA0_ERRALG);
          for (j = 0; j < prod2.size; j++)
            {
              baz_factor_easy2_polynom_mpz (&prod3, &prod2.tab[j].factor,
                  giveup);
              bap_pow_product_mpz (&prod3, &prod3, prod2.tab[j].exponent);
              bap_mul_product_mpz (&prod1, &prod1, &prod3);
            }
        }
      if (bap_is_numeric_product_mpz (&prod2))
        {
          if (!bap_is_one_product_mpz (&prod2))
            BA0_RAISE_EXCEPTION (BA0_ERRALG);
          i += 1;
        }
    }
/*
 * Distribute the factors of prod0 in T and U
 */
  bav_set_term_one (&T);
  bav_set_term_one (&U);
  for (i = 0; i < prod0.size; i++)
    {
      struct bav_variable *v = bap_leader_polynom_mpz (&prod0.tab[i].factor);
      bool found = false;
      for (j = 0; j < F.size && !found; j++)
        {
          if (bap_is_variable_factor_polynom_mpz (F.tab[j], v,
                  (bav_Idegree *) 0))
            {
              found = true;
              bav_mul_term_variable (&T, &T, v, prod0.tab[i].exponent);
            }
        }
      if (!found)
        bav_mul_term_variable (&U, &U, v, prod0.tab[i].exponent);
    }
/*
 * Apply factor_easy2 over A. Result in prod3. Multiply by U
 */
  baz_factor_easy2_polynom_mpz (&prod3, &A, giveup);
  bap_mul_product_term_mpz (&prod3, &prod3, &U);

  ba0_pull_stack ();
  bap_mul_product_term_mpz (prod, &prod1, &T);
  bap_mul_product_numeric_mpz (prod, prod, num_cont);
  j = prod->size;
  bap_mul_product_mpz (prod, prod, &prod3);
  ba0_realloc_table ((struct ba0_table *) keep, prod->size);
  for (i = 0; i < j; i++)
    keep->tab[i] = false;
  for (i = j; i < prod->size; i++)
    keep->tab[i] = true;
  keep->size = prod->size;
#if defined (BA0_HEAVY_DEBUG)
  {
    struct bap_polynom_mpz B;
    ba0_push_another_stack ();
    bap_init_polynom_mpz (&B);
    bap_expand_product_mpz (&B, prod);
    bap_sub_polynom_mpz (&B, &B, A0);
    ba0_pull_stack ();
    if (! bap_is_zero_polynom_mpz (&B))
      BA0_RAISE_EXCEPTION (BA0_ERRALG);
  }
#endif
  ba0_restore (&M);
}

/*
 * texinfo: baz_factor_easy_product_mpz
 * Assign to @var{prod} a factorization of @var{prod0} which is not too difficult
 * to compute and not necessarily irreducible. 
 * Eventually, if a factor of @var{prod} has a nontrivial gcd with some 
 * element of @var{F0} then it divides it.
 * The argument @var{keep} is assigned a table of the same size as 
 * @var{prod}. The @math{i}th element of @var{keep} is @code{true}
 * if and only if the @math{i}th factor of @var{prod} does not divides any
 * element of @var{F0}.
 * The @code{false} entries appear in the leftmost part of @var{keep},
 * the @code{true} entries in the rightmost part.
 */

BAZ_DLL void
baz_factor_easy_product_mpz (
    struct bap_product_mpz *prod,
    struct ba0_tableof_bool *keep,
    struct bap_product_mpz *prod0,
    struct bap_listof_polynom_mpz *F0)
{
  struct bap_tableof_product_mpz Tprod;
  struct ba0_tableof_tableof_bool Tkeep;
  struct ba0_mark M;
  ba0_int_p i, j, n;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_init_table ((struct ba0_table *) &Tprod);
  ba0_init_table ((struct ba0_table *) &Tkeep);
  ba0_realloc2_table ((struct ba0_table *) &Tprod, prod0->size,
      (ba0_new_function *) & bap_new_product_mpz);
  ba0_realloc2_table ((struct ba0_table *) &Tkeep, prod0->size,
      (ba0_new_function *) & ba0_new_table);
  for (i = 0; i < prod0->size; i++)
    {
      if (prod0->tab[i].exponent > 0)
        {
          baz_factor_easy_polynom_mpz (Tprod.tab[i], Tkeep.tab[i],
              &prod0->tab[i].factor, F0);
          bap_pow_product_mpz (Tprod.tab[i], Tprod.tab[i],
              prod0->tab[i].exponent);
          Tprod.size += 1;
          Tkeep.size += 1;
        }
    }
  ba0_pull_stack ();

  bap_set_product_numeric_mpz (prod, prod0->num_factor);

  n = 0;
  for (i = 0; i < Tprod.size; i++)
    n += Tprod.tab[i]->size;
  bap_realloc_product_mpz (prod, n);
  ba0_realloc_table ((struct ba0_table *) keep, n);
  for (i = 0; i < Tprod.size; i++)
    {
      struct bap_product_mpz *prod_i = Tprod.tab[i];
      struct ba0_tableof_bool *keep_i = Tkeep.tab[i];
      for (j = 0; j < keep_i->size && !keep_i->tab[j]; j++)
        bap_mul_product_polynom_mpz (prod, prod, &prod_i->tab[j].factor,
            prod_i->tab[j].exponent);
    }
  keep->size = 0;
  for (i = 0; i < prod->size; i++)
    {
      keep->tab[i] = false;
      keep->size += 1;
    }
  for (i = 0; i < Tprod.size; i++)
    {
      struct bap_product_mpz *prod_i = Tprod.tab[i];
      struct ba0_tableof_bool *keep_i = Tkeep.tab[i];
      for (j = keep_i->size - 1; j >= 0 && keep_i->tab[j]; j--)
        bap_mul_product_polynom_mpz (prod, prod, &prod_i->tab[j].factor,
            prod_i->tab[j].exponent);
    }
  for (i = keep->size; i < prod->size; i++)
    {
      keep->tab[i] = true;
      keep->size += 1;
    }
  for (i = 0; i < Tprod.size; i++)
    {
      struct bap_product_mpz *prod_i = Tprod.tab[i];
      bap_mul_product_numeric_mpz (prod, prod, prod_i->num_factor);
    }
#if defined (BA0_HEAVY_DEBUG)
  {
    struct bap_polynom_mpz B, C;
    ba0_push_another_stack ();
    bap_init_polynom_mpz (&B);
    bap_init_polynom_mpz (&C);
    bap_expand_product_mpz (&B, prod);
    bap_expand_product_mpz (&C, prod0);
    bap_sub_polynom_mpz (&B, &B, &C);
    ba0_pull_stack ();
    if (! bap_is_zero_polynom_mpz (&B))
      BA0_RAISE_EXCEPTION (BA0_ERRALG);
  }
#endif
  ba0_restore (&M);
}
