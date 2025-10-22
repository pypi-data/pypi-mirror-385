#include "baz_polyspec_mpz.h"
#include "baz_gcd_polynom_mpz.h"
#include "baz_factor_polynom_mpz.h"


/****************************************
 SUB-MODULE : UNIVARIATE FACTORISATION 
 ****************************************/

/*
 * One wants to lift the factorisation
 *     P = 1/lc(P) f0 ... f{r-1} mod p
 * One lifts up to p^k > borne, deduced from Landau-Mignotte.
 * Lifted factors, in symmetrical representation, are stored in new_facts.
 * vrai_factor [i] = true if new_fact [i] is a true factor of P up to some
 * 	integer coefficient.
 * new_P = P divided by the product of the true factors already found.
 * Lifted factors are monic.
 * At the end, ba0_mpzm_module contains the power of p ... which fits.
 *
 * Parallel quadratic lifting.
 */

static void
Berlekamp_Hensel_lifting (
    struct bap_product_mpzm *new_fact,
    bool *vrai_factor,
    struct bap_polynom_mpz *new_P,
    struct bap_polynom_mpz *P,
    struct bap_product_mint_hp *fact,
    ba0_mint_hp p)
{
  struct bap_polynom_mpzm G, U, V, D, *W, *A, *F, *Z;
  ba0_mpz_t borne, bunk, *lcP, *lc, old_q, q, q2;
  bool old_q_is_prime;
  ba0_int_p i, r;
  struct ba0_mark M;

  W = (struct bap_polynom_mpzm *) 0;
  A = (struct bap_polynom_mpzm *) 0;
  Z = (struct bap_polynom_mpzm *) 0;

  bap_set_polynom_mpz (new_P, P);

  ba0_push_another_stack ();
  ba0_record (&M);

  lcP = bap_numeric_initial_polynom_mpz (P);

  ba0_mpz_init (borne);
  bap_maxnorm_polynom_mpz (borne, P);
  ba0_mpz_mul (borne, borne, *lcP);
  ba0_mpz_mul_2exp (borne, borne, bap_leading_degree_polynom_mpz (P) + 1);

  ba0_mpz_init (old_q);
  ba0_mpz_init_set_ui (q, p);
  ba0_mpzm_module_set (q, true);

  r = fact->size;
  F = (struct bap_polynom_mpzm *) ba0_alloc (sizeof (struct bap_polynom_mpzm) *
      r);
  for (i = 0; i < r; i++)
    {
      bap_init_polynom_mpzm (&F[i]);
      bap_polynom_mint_hp_to_mpzm (&F[i], &fact->tab[i].factor);
      vrai_factor[i] = false;
    }
/*
   F [0] = lcP * F [0] mod q
*/
  ba0_mpz_init_set (bunk, *lcP);
  ba0_mpz_mod (bunk, bunk, ba0_mpzm_module);
  bap_mul_polynom_numeric_mpzm (&F[0], &F[0], bunk);

  for (i = 0; i < r; i++)
    bap_mods_polynom_mpzm ((struct bap_polynom_mpz *) &F[i], &F[i]);
/*
for (i = 0; i < r; i++)
{   printf ("F [%d] = ", i);
    ba0_printf ("%Azm\n", &F [i]);
}
*/
  if (ba0_mpz_cmp (q, borne) <= 0)
    {
/*
   W [0] = F [0], 
   W [k] = F [k] * ... * F [r-1]
*/
      W = (struct bap_polynom_mpzm *) ba0_alloc (sizeof (struct
              bap_polynom_mpzm) * r);
      bap_init_polynom_mpzm (&W[r - 1]);
      bap_set_polynom_mpzm (&W[r - 1], &F[r - 1]);
      for (i = r - 2; i >= 1; i--)
        {
          bap_init_polynom_mpzm (&W[i]);
          bap_mul_polynom_mpzm (&W[i], &F[i], &W[i + 1]);
          bap_mods_polynom_mpzm ((struct bap_polynom_mpz *) &W[i], &W[i]);
        }
/*
for (i = 1; i < r - 1; i++)
{   printf ("W [%d] = ", i);
    ba0_printf ("%Azm\n", &W [i]);
}
*/
      bap_init_polynom_one_mpzm (&D);
      bap_init_polynom_mpzm (&U);
      bap_init_polynom_mpzm (&V);
      bap_init_polynom_mpzm (&G);
/*
   A [k] = 1 / (F [0] * ... * F [k-1] * F [k+1] * ... * F [r-1]) mod F [k]
*/
      A = (struct bap_polynom_mpzm *) ba0_alloc (sizeof (struct
              bap_polynom_mpzm) * r);
      for (i = 0; i < r - 1; i++)
        {
          bap_extended_Euclid_polynom_mpzm (&U, &V, &G, &F[i], &W[i + 1]);
          bap_init_polynom_mpzm (&A[i]);
          bap_mul_polynom_mpzm (&A[i], &V, &D);
          bap_Euclidean_division_polynom_mpzm (BAP_NOT_A_POLYNOM_mpzm, &A[i],
              &A[i], &F[i]);
          bap_mods_polynom_mpzm ((struct bap_polynom_mpz *) &A[i], &A[i]);
          bap_mul_polynom_mpzm (&D, &U, &D);
          bap_Euclidean_division_polynom_mpzm (BAP_NOT_A_POLYNOM_mpzm, &D, &D,
              &W[i + 1]);
        }
      bap_init_polynom_mpzm (&A[r - 1]);
      bap_mods_polynom_mpzm ((struct bap_polynom_mpz *) &A[r - 1], &D);
/*
for (i = 0; i < r; i++)
{   printf ("A [%d] = ", i);
    ba0_printf ("%Azm\n", &A [i]);
}
*/
      ba0_mpz_init (q2);
      ba0_mpz_mul (q2, q, q);
      ba0_mpzm_module_set (q2, false);
/*
   D = replace_lc (F [0], lcP mod q2) * F [1] * ... * F [r-1] - P mod q2
*/
      bap_set_polynom_mpzm (&D, &F[0]);
      lc = bap_numeric_initial_polynom_mpzm (&D);
      ba0_mpz_mod (*lc, *lcP, ba0_mpzm_module);
      for (i = 1; i < r; i++)
        bap_mul_polynom_mpzm (&D, &D, &F[i]);
      bap_polynom_mpz_to_mpzm (&U, P);
      bap_sub_polynom_mpzm (&D, &D, &U);
      bap_mods_polynom_mpzm ((struct bap_polynom_mpz *) &D, &D);

      Z = (struct bap_polynom_mpzm *) ba0_alloc (sizeof (struct
              bap_polynom_mpzm) * r);
      for (i = 0; i < r; i++)
        bap_init_polynom_mpzm (&Z[i]);
    }

  old_q_is_prime = true;
  while (ba0_mpz_cmp (q, borne) <= 0)
    {
      ba0_mpz_set (old_q, q);
      ba0_mpz_mul (q, q, q);
/*
ba0_printf ("D = %Azm\n", &D);
ba0_printf ("old_q = %z\n", old_q);
*/
      if (!bap_is_zero_polynom_mpzm (&D))
        {
/*
   D = D / old_q
*/
          bap_exquo_polynom_numeric_mpz ((struct bap_polynom_mpz *) &D,
              (struct bap_polynom_mpz *) &D, old_q);
          for (i = 0; i < r; i++)
            {
/*
   F [i] = F [i] - old_q * { rem (A [i] * D, F [i]) mod old_q } mod q
*/
              ba0_mpzm_module_set (old_q, old_q_is_prime);
              bap_mul_polynom_mpzm (&U, &A[i], &D);
              bap_Euclidean_division_polynom_mpzm (BAP_NOT_A_POLYNOM_mpzm, &U,
                  &U, &F[i]);
              bap_mods_polynom_mpzm ((struct bap_polynom_mpz *) &U, &U);
              bap_mul_polynom_numeric_mpz ((struct bap_polynom_mpz *) &U,
                  (struct bap_polynom_mpz *) &U, old_q);
              ba0_mpzm_module_set (q, false);
              bap_sub_polynom_mpzm (&F[i], &F[i], &U);
            }
/*
   F [0] = replace_lc (F [0], lcP mod q)
*/
          lc = bap_numeric_initial_polynom_mpzm (&F[0]);
          ba0_mpz_mod (*lc, *lcP, ba0_mpzm_module);

          for (i = 0; i < r; i++)
            bap_mods_polynom_mpzm ((struct bap_polynom_mpz *) &F[i], &F[i]);
/*
for (i = 0; i < r; i++)
{   printf ("F [%d] = ", i);
    ba0_printf ("%Azm\n", &F [i]);
}
*/
        }
/*
 * One tests if some new factors were discovered.
 * If so, one returns if less than two factors are left and one recomputes
 * the bound.
 */
      {
        struct bap_polynom_mpz *X = (struct bap_polynom_mpz *) &U;
        bool found = false;

        lc = bap_numeric_initial_polynom_mpz (new_P);
        ba0_mpz_mod (bunk, *lc, ba0_mpzm_module);
        for (i = 0; i < r; i++)
          {
            if (vrai_factor[i])
              continue;
            if (i == 0)
              bap_set_polynom_mpz (X, (struct bap_polynom_mpz *) &F[i]);
            else
              {
                bap_mul_polynom_numeric_mpzm (&U, &F[i], bunk);
                bap_mods_polynom_mpzm (X, &U);
              }
            bap_normal_numeric_primpart_polynom_mpz (X, X);
            ba0_pull_stack ();
            if (bap_is_factor_polynom_mpz (new_P, X, new_P))
              {
                vrai_factor[i] = true;
                found = true;
/*
ba0_printf ("vrai factor : %Az\n", X);
*/
              }
            ba0_push_another_stack ();
          }
        if (found)
          {
            ba0_int_p nb;
            for (i = 0, nb = 0; i < r; i++)
              if (vrai_factor[i])
                nb++;
            if (nb >= r - 1)
              break;
            bap_maxnorm_polynom_mpz (borne, new_P);
            ba0_mpz_mul (borne, borne, *lc);
            ba0_mpz_mul_2exp (borne, borne,
                bap_leading_degree_polynom_mpz (new_P) + 1);
          }
      }
/*
 * May happen either because q -> q^2 or because of the discov. of new factors
 */
      if (ba0_mpz_cmp (q, borne) > 0)
        break;

      ba0_mpz_mul (q2, q, q);
/*
   W [r-1] = F [r-1] mod q
   W [k] = F [k] * W [k+1] mod q^2 pour k = 1 .. r-2
*/
      bap_set_polynom_mpzm (&W[r - 1], &F[r - 1]);
      ba0_mpzm_module_set (q2, false);
      for (i = r - 2; i >= 1; i--)
        {
          bap_mul_polynom_mpzm (&W[i], &F[i], &W[i + 1]);
          bap_mods_polynom_mpzm ((struct bap_polynom_mpz *) &W[i], &W[i]);
        }
/*
for (i = 1; i < r - 1; i++)
{   printf ("W [%d] = ", i);
    ba0_printf ("%Azm\n", &W [i]);
}
*/
/*
   D = (replace_lc (F [0], lcP mod q^2) * W [1] - P) mod q^2
*/
      bap_set_polynom_mpzm (&D, &F[0]);
      lc = bap_numeric_initial_polynom_mpzm (&D);
      ba0_mpz_mod (*lc, *lcP, ba0_mpzm_module);
      bap_mul_polynom_mpzm (&D, &D, &W[1]);
      bap_polynom_mpz_to_mpzm (&U, P);
      bap_sub_polynom_mpzm (&D, &D, &U);
      bap_mods_polynom_mpzm ((struct bap_polynom_mpz *) &D, &D);
/*
ba0_printf ("D = %Azm\n", &D);
*/
/*
   Z [0] = F [0]
   Z [k] = F [k] * Z [k-1] mod q pour k = 1 a r-2
*/
      ba0_mpzm_module_set (q, false);
      bap_set_polynom_mpzm (&Z[0], &F[0]);
      for (i = 1; i < r - 1; i++)
        {
          bap_mul_polynom_mpzm (&Z[i], &F[i], &Z[i - 1]);
          bap_mods_polynom_mpzm ((struct bap_polynom_mpz *) &Z[i], &Z[i]);
        }
/*
for (i = 0; i < r - 1; i++)
{   printf ("Z [%d] = ", i);
    ba0_printf ("%Azm\n", &Z [i]);
}
*/
/*
   U = ((A [0] * W [1]) + (Z [r-2] * A [r-1]) - 1) mod q
*/
      bap_mul_polynom_mpzm (&U, &A[0], &W[1]);
      bap_mul_polynom_mpzm (&V, &Z[r - 2], &A[r - 1]);
      bap_add_polynom_mpzm (&U, &U, &V);
      ba0_mpz_set_si (bunk, -1);
      bap_add_polynom_numeric_mpzm (&U, &U, bunk);
/*
   U = (U + Z [i-1] * A [i] * W [i+1]) mod q pour i = 1 a r-2
*/
      for (i = 1; i < r - 1; i++)
        {
          bap_mul_polynom_mpzm (&V, &Z[i - 1], &A[i]);
          bap_mul_polynom_mpzm (&V, &V, &W[i + 1]);
          bap_add_polynom_mpzm (&U, &U, &V);
        }
      bap_mods_polynom_mpzm ((struct bap_polynom_mpz *) &U, &U);
/*
   U = U / old_q
*/
      bap_exquo_polynom_numeric_mpz ((struct bap_polynom_mpz *) &U,
          (struct bap_polynom_mpz *) &U, old_q);
/*
   A [i] = (A [i] - old_q * rem (A [i] * U mod old_q, F [i])) mod q 
   pour i = 0 .. r-1
*/
      for (i = 0; i < r; i++)
        {
          ba0_mpzm_module_set (old_q, old_q_is_prime);
          bap_mul_polynom_mpzm (&V, &A[i], &U);
          bap_Euclidean_division_polynom_mpzm (BAP_NOT_A_POLYNOM_mpzm, &V, &V,
              &F[i]);
          bap_mods_polynom_mpzm ((struct bap_polynom_mpz *) &V, &V);
          bap_mul_polynom_numeric_mpz ((struct bap_polynom_mpz *) &V,
              (struct bap_polynom_mpz *) &V, old_q);
          ba0_mpzm_module_set (q, false);
          bap_sub_polynom_mpzm (&A[i], &A[i], &V);
          bap_mods_polynom_mpzm ((struct bap_polynom_mpz *) &A[i], &A[i]);
        }
/*
for (i = 0; i < r; i++)
{   printf ("A [%d] = ", i);
    ba0_printf ("%Azm\n", &A [i]);
}
*/
      old_q_is_prime = false;
    }
  ba0_pull_stack ();
  bap_set_product_one_mpzm (new_fact);
  bap_realloc_product_mpzm (new_fact, r);
/*
    if (vrai_factor [0])
	bap_set_polynom_mpzm (&new_fact->tab [0].factor, &F [0]);
    else
	bap_numeric_initial_one_polynom_mpzm 
					(&new_fact->tab [0].factor, &F [0]);
*/
  bap_numeric_initial_one_polynom_mpzm (&new_fact->tab[0].factor, &F[0]);
  for (i = 1; i < r; i++)
    bap_set_polynom_mpzm (&new_fact->tab[i].factor, &F[i]);
  new_fact->size = r;
  ba0_restore (&M);
}

/*
 * Returns a prime p which does not annihilate the leading coefficient
 * of A and such that A is squarefree.
 */

static ba0_mint_hp
determine_small_prime (
    struct bap_polynom_mpz *A)
{
  struct bap_polynom_mint_hp Abar, Sbar, Gbar;
  ba0_mpz_t bunk, *lc;
  bool found;
  struct ba0_mark M;

  ba0_record (&M);

  lc = bap_numeric_initial_polynom_mpz (A);
  ba0_mint_hp_module_set (ba0_smallest_small_prime (), true);
  bap_init_polynom_mint_hp (&Abar);
  bap_init_polynom_mint_hp (&Sbar);
  bap_init_polynom_mint_hp (&Gbar);
  ba0_mpz_init (bunk);
  found = false;
  while (!found)
    {
      if (ba0_mpz_mod_ui (bunk, *lc,
              (unsigned long int) ba0_mint_hp_module) != 0)
        {
          bap_polynom_mpz_to_mint_hp (&Abar, A);
          bap_separant_polynom_mint_hp (&Sbar, &Abar);
          bap_Euclid_polynom_mint_hp (&Gbar, &Abar, &Sbar);
          if (bap_is_numeric_polynom_mint_hp (&Gbar))
            found = true;
        }
      if (!found)
        ba0_mint_hp_module_set (ba0_next_small_prime (ba0_mint_hp_module),
            true);
    }
  ba0_restore (&M);
  return ba0_mint_hp_module;
}

/*
 * ba0_mpzm_module contains the right power of some prime number.
 * One must combiner the factors of a_combiner, with indices l <= i < r,
 * 	in order to obtain true factors.
 * One knows that none of them is a true factor alone.
 *
 * Factors of a_combiner are monic.
 * Found true factors are appended to prod (up to the power k).
 *
 * A can be modified (it belongs to the auxiliary stack).
 */

static void
combine_factors_univaries_mpzm (
    struct bap_product_mpz *prod,
    struct bap_polynom_mpz *A,
    bav_Idegree k,
    struct bap_product_mpzm *a_combiner,
    ba0_int_p l,
    ba0_int_p r)
{
/*
 * If 3 factors or less, A is irreducible.
 */
  if (r - l <= 3)
    {
      if (r != l)
        {
          bap_mul_product_polynom_mpz (prod, prod, A, k);
/*
ba0_printf ("Facteur irreductible = %Az\n", A);
*/
        }
    }
  else
    {
      struct bap_polynom_mpzm F;
      ba0_int_p i, j, n;
      ba0_mpz_t c, lc;
      struct ba0_mark M;

      ba0_push_another_stack ();
      ba0_record (&M);
/*
   lc = lcoeff (A) mod ba0_mpzm_module
*/
      ba0_mpz_init (lc);
      ba0_mpz_mod (lc, *bap_numeric_initial_polynom_mpz (A), ba0_mpzm_module);

      bap_init_polynom_mpzm (&F);
/*
   c = 2^(r-l-1) - 2
*/
      ba0_mpz_init (c);
      ba0_mpz_ui_pow_ui (c, 2, r - l - 1);
      ba0_mpz_sub_ui (c, c, 2);
      while (ba0_mpz_cmp_ui (c, 2) > 0)
        {
/*
   n = number of 1 bits
*/
          n = 0;
          for (i = l; i < r; i++)
            {
              if (ba0_mpz_tstbit (c, (unsigned long) i))
                n++;
            }
/*
 * If at least two 1-bits and two 0-bits, it is worth testing 
 * the partition.
 */
          if (n >= 2 && n <= r - l - 2)
            {
/*
   i = the index of the first 1-bit.
   j = the index of the second one.
*/
              i = l;
              while (!ba0_mpz_tstbit (c, (unsigned long) i))
                i++;
              j = i + 1;
              while (!ba0_mpz_tstbit (c, (unsigned long) j))
                j++;
/*
 * F = the product of the factors whose bit is 1.
 * F = primpart (F * lc (A) mod ba0_mpzm_module)
 */
              bap_mul_polynom_mpzm (&F, &a_combiner->tab[i].factor,
                  &a_combiner->tab[j].factor);
              for (i = j + 1; i < r; i++)
                {
                  if (ba0_mpz_tstbit (c, (unsigned long) i))
                    bap_mul_polynom_mpzm (&F, &F, &a_combiner->tab[i].factor);
                }
              bap_mul_polynom_numeric_mpzm (&F, &F, lc);
              bap_mods_polynom_mpzm ((struct bap_polynom_mpz *) &F, &F);
              bap_normal_numeric_primpart_polynom_mpz ((struct bap_polynom_mpz
                      *) &F, (struct bap_polynom_mpz *) &F);
/*
   If F | A then
*/
              if (bap_is_factor_polynom_mpz (A, (struct bap_polynom_mpz *) &F,
                      A))
                {
/*
   A = A / F
   The n 1-bit factors are grouped in the beginning of the table.
*/
                  i = l;
                  j = r - 1;
                  while (i < j)
                    {
                      while (i < j && ba0_mpz_tstbit (c, (unsigned long) i))
                        i++;
                      while (i < j && !ba0_mpz_tstbit (c, (unsigned long) j))
                        j--;
                      if (i < j)
                        {
                          BA0_SWAP (struct bap_polynom_mpzm,
                              a_combiner->tab[i].factor,
                              a_combiner->tab[j].factor);
                          i++;
                          j--;
                        }
                    }
                  ba0_pull_stack ();
                  combine_factors_univaries_mpzm (prod,
                      (struct bap_polynom_mpz *) &F, k, a_combiner, l, n);
                  ba0_push_another_stack ();
/*
 * The other factors. One recomputes c = 2^(r-l-1)-2.
 */
                  l = n + 1;
                  ba0_mpz_ui_pow_ui (c, 2, r - l - 1);
                  ba0_mpz_sub_ui (c, c, 2);
                }
              else
                ba0_mpz_sub_ui (c, c, 1);
            }
          else
            ba0_mpz_sub_ui (c, c, 1);
        }
      ba0_pull_stack ();
      bap_mul_product_polynom_mpz (prod, prod, A, k);
/*
ba0_printf ("Facteur irreductible = %Az\n", A);
*/
      ba0_restore (&M);
    }
}

/*
 * Let puis = (A, k).
 * The polynomial A is univariate, primitive, squarefree and with 
 * positive leading coeff. Multiplies prod by the irreducible factorisation
 * of A, to the power k.
 */

static void
baz_factor_univariate_polynom_mpz (
    struct bap_product_mpz *prod,
    struct bap_power_mpz *puis)
{
  struct bap_polynom_mpz *A;
  bav_Idegree k;
  struct bap_polynom_mint_hp Abar;
  struct bap_product_mint_hp prod_mod;
  ba0_mint_hp p;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  A = &puis->factor;
  k = puis->exponent;
/*
ba0_printf ("A factoriser : %Az\n", A);
*/
  p = determine_small_prime (A);
  ba0_mint_hp_module_set (p, true);
  bap_init_polynom_mint_hp (&Abar);
  bap_polynom_mpz_to_mint_hp (&Abar, A);
  bap_numeric_initial_one_polynom_mint_hp (&Abar, &Abar);
  bap_init_product_mint_hp (&prod_mod);
  bap_Berlekamp_mint_hp (&prod_mod, &Abar);
/*
printf ("premier choisi : %d\n", (int)p);
ba0_printf ("Apres Berlekamp : %Pim\n", &prod_mod);
*/
  if (prod_mod.size == 1)
    {
      ba0_pull_stack ();
      bap_mul_product_polynom_mpz (prod, prod, A, k);
/*
   July 2004
	ba0_push_another_stack ();
*/
    }
  else
    {
      struct bap_polynom_mpz new_A;
      struct bap_product_mpzm new_factor;
      bool *vrai_factor;
      ba0_mpz_t lc;
      ba0_int_p i, n;

      bap_init_polynom_mpz (&new_A);
      ba0_mpzm_module_set_ui (3, true);
      bap_init_product_mpzm (&new_factor);
      vrai_factor = (bool *) ba0_alloc (sizeof (bool) * prod_mod.size);
      Berlekamp_Hensel_lifting (&new_factor, vrai_factor, &new_A, A, &prod_mod,
          p);
/*
ba0_printf ("Apres Hensel lifting : %Pz\n", &new_factor);
*/
/*
 * One records the true factors, found during the lifting.
 */
      ba0_mpz_init (lc);
      ba0_mpz_mod (lc, *bap_numeric_initial_polynom_mpz (A), ba0_mpzm_module);
      for (i = 0, n = 0; i < new_factor.size; i++)
        {
          if (vrai_factor[i])
            {
              bap_mul_polynom_numeric_mpzm (&new_factor.tab[i].factor,
                  &new_factor.tab[i].factor, lc);
              bap_mods_polynom_mpzm ((struct bap_polynom_mpz *)
                  &new_factor.tab[i].factor, &new_factor.tab[i].factor);
              bap_normal_numeric_primpart_polynom_mpz ((struct bap_polynom_mpz
                      *) &new_factor.tab[i].factor,
                  (struct bap_polynom_mpz *) &new_factor.tab[i].factor);
              ba0_pull_stack ();
              bap_mul_product_polynom_mpz (prod, prod,
                  (struct bap_polynom_mpz *) &new_factor.tab[i].factor, k);
              ba0_push_another_stack ();
            }
          else
            n++;
        }
/*
 * One suppresses from new_factor all true factors.
 */
      for (i = 0, n = 0; i < new_factor.size; i++)
        {
          if (!vrai_factor[i])
            {
              if (i != n)
                bap_set_polynom_mpzm (&new_factor.tab[n].factor,
                    &new_factor.tab[i].factor);
              n += 1;
            }
        }
      new_factor.size = n;
      ba0_pull_stack ();
      combine_factors_univaries_mpzm (prod, &new_A, k, &new_factor, 0, n);
    }
  ba0_restore (&M);
}

/***************************************
 SUB-MODULE : MULTIVARIATE FACTORISATION
 ***************************************/

/*
 * Assigns to point some new struct bav_point_int_p * which does not annihilate
 * nonzero and does not map any factor fo fact_init over 0, +/-1, +/-2
 * and fact_init->num_factor.
 */

/* 
 * Selects the distinghished variable for extended_Zassenhaus_factor.
 * Picks the one of smallest degree.
 * Tie breaks: considers the size of the leading coeff.
 */

static struct bav_variable *
baz_EZF_distinguished_variable (
    struct bap_polynom_mpz *A)
{
  struct bap_polynom_mpz AA, lc;

  volatile bav_Iordering r, r0;
  struct bav_variable *v, *min_var;
  bav_Idegree min_deg;

  struct ba0_mark M;
  ba0_int_p i, n, lc_nbmon, min_nbmon;

  min_var = A->total_rank.rg[0].var;
  min_deg = A->total_rank.rg[0].deg;
  n = 1;
  for (i = 1; i < A->total_rank.size; i++)
    {
      if (min_deg > A->total_rank.rg[i].deg)
        {
          min_var = A->total_rank.rg[i].var;
          min_deg = A->total_rank.rg[i].deg;
          n = 1;
        }
      else if (min_deg == A->total_rank.rg[i].deg)
        n++;
    }
  if (n != 1)
    {
      ba0_record (&M);
      min_nbmon = BA0_MAX_INT_P;
      bap_init_readonly_polynom_mpz (&AA);
      bap_init_readonly_polynom_mpz (&lc);

      r0 = bav_current_ordering ();
      r = bav_R_copy_ordering (r0);
      bav_push_ordering (r);

      for (i = 0; i < A->total_rank.size; i++)
        {
          if (A->total_rank.rg[i].deg == min_deg)
            {
              v = A->total_rank.rg[i].var;
              bav_R_set_maximal_variable (v);
              bap_sort_polynom_mpz (&AA, A);
              bap_initial_polynom_mpz (&lc, &AA);
              lc_nbmon = bap_nbmon_polynom_mpz (&lc);
              if (lc_nbmon < min_nbmon)
                {
                  min_var = v;
                  min_nbmon = lc_nbmon;
                }
            }
        }

      bav_pull_ordering ();
      bav_R_free_ordering (r);

      ba0_restore (&M);
    }
  return min_var;
}

static void
baz_EZF_set_modulus_part_ideal_lifting (
    struct baz_ideal_lifting *lifting)
{
  ba0_mpz_t prime, bunk, bink;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_mpz_init (prime);
  ba0_mpz_init (bunk);
  ba0_mpz_init (bink);

  bap_maxnorm_polynom_mpz (prime, lifting->A);
  ba0_mpz_mul_2exp (prime, prime, 4 * ba0_mpz_sizeinbase (prime, 2) + 7);
  ba0_mpz_nextprime (prime, prime);
  bap_eval_to_numeric_at_point_int_p_polynom_mpz (&bunk, lifting->initial,
      &lifting->point);
  do
    {
      ba0_mpz_mod (bink, bunk, prime);
      if (ba0_mpz_sgn (bink) == 0)
        ba0_mpz_nextprime (prime, prime);
    }
  while (ba0_mpz_sgn (bink) == 0);
  ba0_pull_stack ();
  ba0_mpz_init_set (lifting->p, prime);
  lifting->l = 1;
  ba0_restore (&M);
}

/*
 * Let puis = (A, k).
 * the polynomial A depends on at least two variables. It is squarefree,
 * numerically primitiveand primitive w.r.t. any variable.
 * Multiplies prod by the irreducible factorisation of A to the power k.
 */

static void
baz_extended_Zassenhaus_factor_polynom_mpz (
    struct bap_product_mpz *prod,
    struct bap_power_mpz *puis)
{
  struct baz_ideal_lifting lifting;
  struct bap_itercoeff_mpz iter;
  struct bap_tableof_polynom_mpz nonzero, nonzero_one_two;
  struct bap_product_mpz lifted_factors;
  struct bap_polynom_mpz tmp;
  struct bap_polynom_mpz volatile *Ax;
  struct bap_polynom_mpz volatile *newAx;
  struct bap_polynom_mpz volatile *A;
  struct bap_polynom_mpz volatile *G;

  struct bav_term term_one;
  volatile bav_Iordering r, r0;
  struct bav_variable *x;
  bav_Idegree k;

  struct ba0_mark M;
  volatile ba0_int_p nb_factors, nb_confirm, nb_success, nb_tries;
  ba0_int_p i;

  ba0_mpz_t cont;
  ba0_mpz_t *lc;
  ba0_mpz_t *factinit_mod_point;
  volatile bool lc_negatif;

  A = &puis->factor;
  k = puis->exponent;

  ba0_push_another_stack ();
  ba0_record (&M);
/*
 * the distinguished variable becomes the leading variable
 */
  x = baz_EZF_distinguished_variable ((struct bap_polynom_mpz *) A);

  r0 = bav_current_ordering ();
  r = bav_R_copy_ordering (r0);
  bav_push_ordering (r);

  bav_R_set_maximal_variable (x);
/*
 * Any modular operation requires ba0_mpzm_module to be set.
 */
  ba0_mpzm_module_set_ui (3, true);
  baz_HL_init_ideal_lifting (&lifting);
/*
 * lifting.A = A sorted with respect to the new ordering
 */
  bap_init_readonly_polynom_mpz (&tmp);
  bap_sort_polynom_mpz (&tmp, (struct bap_polynom_mpz *) A);
  bap_set_polynom_mpz (lifting.A, &tmp);
  lc = bap_numeric_initial_polynom_mpz (lifting.A);
  lc_negatif = ba0_mpz_sgn (*lc) < 0;
  if (lc_negatif)
    bap_neg_polynom_mpz (lifting.A, lifting.A);

  bap_initial_polynom_mpz (lifting.initial, lifting.A);
  baz_factor_polynom_mpz (&lifting.factors_initial, lifting.initial);
/*
 * lifting.point receives [y1 = 0, ..., yk = 0] (x is shifted out)
 */
  bap_set_point_polynom_mpz ((struct ba0_point *) &lifting.point, lifting.A,
      false);
/*
 * nonzero = the trailing coefficient of A
 * nonzero_one_two = the irreducible factors of the initial of A
 */
  ba0_init_table ((struct ba0_table *) &nonzero);
  ba0_realloc2_table ((struct ba0_table *) &nonzero, 1,
      (ba0_new_function *) & bap_new_readonly_polynom_mpz);
  bap_begin_itercoeff_mpz (&iter, lifting.A, x);
  bav_init_term (&term_one);
  bap_seek_coeff_itercoeff_mpz (nonzero.tab[0], &iter, &term_one);
  nonzero.size = 1;

  ba0_init_table ((struct ba0_table *) &nonzero_one_two);
  ba0_realloc_table ((struct ba0_table *) &nonzero_one_two,
      lifting.factors_initial.size);
  for (i = 0; i < lifting.factors_initial.size; i++)
    {
      nonzero_one_two.tab[nonzero_one_two.size] =
          &lifting.factors_initial.tab[i].factor;
      nonzero_one_two.size += 1;
    }

  G = bap_new_polynom_mpz ();
  Ax = bap_new_polynom_mpz ();
  newAx = bap_new_polynom_mpz ();

  ba0_mpz_init (cont);

  factinit_mod_point =
      (ba0_mpz_t *) ba0_alloc (sizeof (ba0_mpz_t) * (1 +
          lifting.factors_initial.size));
  for (i = 0; i < 1 + lifting.factors_initial.size; i++)
    ba0_mpz_init (factinit_mod_point[i]);

  bap_init_product_mpz (&lifted_factors);

  nb_factors = BA0_MAX_INT_P;
  nb_confirm = 2;
  for (;;)
    {
      nb_tries = 0;
      nb_success = 0;
      while (nb_success < nb_confirm && nb_factors != 1)
        {
          nb_tries += 1;

          baz_yet_another_point_int_p_mpz (&lifting.point, &nonzero,
              &lifting.factors_initial, BAV_NOT_A_VARIABLE);

          baz_HL_begin_redistribute (&lifting, factinit_mod_point,
              (struct bap_polynom_mpz *) newAx, cont);

          if (bap_equal_polynom_mpz ((struct bap_polynom_mpz *) Ax,
                  (struct bap_polynom_mpz *) newAx))
            continue;
/*
 * The exception point is removed immediately: volatile is not needed
 */
          BA0_TRY
          {
            baz_HL_integer_divisors ((ba0_mpz_t *) 0, &lifting,
                factinit_mod_point);
          }
          BA0_CATCH
          {
            if (ba0_global.exception.raised != BAZ_EXHDIS)
              BA0_RE_RAISE_EXCEPTION;
            continue;
          }
          BA0_ENDTRY;

          bap_separant_polynom_mpz ((struct bap_polynom_mpz *) G,
              (struct bap_polynom_mpz *) newAx);
          baz_gcd_polynom_mpz ((struct bap_polynom_mpz *) G,
              BAP_NOT_A_POLYNOM_mpz, BAP_NOT_A_POLYNOM_mpz,
              (struct bap_polynom_mpz *) G, (struct bap_polynom_mpz *) newAx);
          if (!bap_is_numeric_polynom_mpz ((struct bap_polynom_mpz *) G))
            continue;

          BA0_SWAP (struct bap_polynom_mpz volatile *,
              Ax,
              newAx);
          baz_factor_polynom_mpz ((struct bap_product_mpz *)
              &lifting.factors_mod_point, (struct bap_polynom_mpz *) Ax);
          if (lifting.factors_mod_point.size < nb_factors)
            {
              nb_factors = lifting.factors_mod_point.size;
              nb_success = 1;
            }
          else if (lifting.factors_mod_point.size == nb_factors)
            nb_success += 1;
        }

      if (nb_factors == 1)
        {
          ba0_pull_stack ();
          bav_pull_ordering ();
          bap_mul_product_polynom_mpz (prod, prod, (struct bap_polynom_mpz *) A,
              k);
          break;
        }
/*
 * Exception point is removed immediately: volatile is not needed
 */
      BA0_TRY
      {
        baz_HL_end_redistribute (&lifting, factinit_mod_point + 1,
            (struct bap_polynom_mpz *) Ax, cont);
      }
      BA0_CATCH
      {
        if (ba0_global.exception.raised != BAZ_EXHDIS)
          BA0_RE_RAISE_EXCEPTION;
        continue;
      }
      BA0_ENDTRY;

      baz_EZF_set_modulus_part_ideal_lifting (&lifting);
/*
 * Exception point is removed immediately: volatile is not needed
 */
      BA0_TRY
      {
        baz_HL_ideal_Hensel_lifting (&lifted_factors, &lifting);
      }
      BA0_CATCH
      {
        if (ba0_global.exception.raised != BAP_EXHNCP
            && ba0_global.exception.raised != BAZ_EXHENS)
          BA0_RE_RAISE_EXCEPTION;
/*
printf ("point d'evaluation malchanceux\n");
*/
        nb_success -= 1;
        continue;
      }
      BA0_ENDTRY;

      for (i = 0; i < lifted_factors.size; i++)
        bap_normal_numeric_primpart_polynom_mpz (&lifted_factors.tab[i].factor,
            &lifted_factors.tab[i].factor);
      ba0_pull_stack ();
      bav_pull_ordering ();
      for (i = 0; i < lifted_factors.size; i++)
        {
          bap_sort_polynom_mpz (&lifted_factors.tab[i].factor,
              &lifted_factors.tab[i].factor);
          lifted_factors.tab[i].factor.readonly = false;
          if (lc_negatif)
            {
              lc = bap_numeric_initial_polynom_mpz (&lifted_factors.tab[i].
                  factor);
              if (ba0_mpz_sgn (*lc) < 0)
                {
                  bap_neg_polynom_mpz (&lifted_factors.tab[i].factor,
                      &lifted_factors.tab[i].factor);
                  lc_negatif = false;
                }
            }
          bap_mul_product_polynom_mpz (prod, prod,
              &lifted_factors.tab[i].factor, k);
        }
      if (lc_negatif)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
      break;
    }
  bav_R_free_ordering (r);
  ba0_restore (&M);
}

/***************************************
 MAIN MODULE
 ***************************************/

/*
 * Subfunction of baz_factor_polynom_mpz.
 * A is numerically primitive, with no factor of the form x^k, primitive
 * w.r.t. any variable.
 *
 * prod is both an input and an output parameter.
 */

static void
baz_factor_non_trivial_primitive_polynom_mpz (
    struct bap_product_mpz *prod,
    struct bap_polynom_mpz *A)
{
  struct bap_product_mpz sqrf;
  ba0_int_p i;
  struct ba0_mark M;

  if (!bap_is_numeric_polynom_mpz (A))
    {
      ba0_push_another_stack ();
      ba0_record (&M);
      bap_init_product_mpz (&sqrf);
      baz_squarefree_polynom_mpz (&sqrf, A);
      ba0_pull_stack ();
/*
ba0_printf ("Factorisation squarefree = %Pz\n", &sqrf);
*/
      for (i = 0; i < sqrf.size; i++)
        {
          if (bap_is_univariate_polynom_mpz (A))
            baz_factor_univariate_polynom_mpz (prod, &sqrf.tab[i]);
          else
            baz_extended_Zassenhaus_factor_polynom_mpz (prod, &sqrf.tab[i]);
        }
      ba0_restore (&M);
    }
}

/*
 * Subfunction of baz_factor_polynom_mpz
 *
 * A is numerically primitive, with no factor of the form x^k.
 *
 * /!\
 * ---
 *
 * The current stack is the working stack of the calling function.
 * One can modify what belongs to that stack.
 */

static void
baz_factor_non_trivial_polynom_mpz (
    struct bap_product_mpz *prod,
    struct bap_polynom_mpz *A)
{
  struct bav_term T;
  struct bap_polynom_mpz C;
  struct bap_polynom_mpz *cont;
  ba0_int_p i;
  struct bav_variable *v;

  if (bap_is_numeric_polynom_mpz (A))
    return;
/*
 * Special care for variables which appear linearly.
 * Multiplies prod by primpart (A, x)
 * Replace A by content (A, x).
 */
  bap_init_polynom_mpz (&C);
  cont = bap_new_polynom_mpz ();

  i = 0;
  while (i < A->total_rank.size)
    {
      if (A->total_rank.rg[i].deg == 1)
        {
          baz_content_polynom_mpz (cont, A, A->total_rank.rg[i].var);

          if (!bap_is_one_polynom_mpz (cont))
            bap_exquo_polynom_mpz (A, A, cont);
          ba0_pull_stack ();
          bap_mul_product_polynom_mpz (prod, prod, A, 1);
          ba0_push_another_stack ();

          BA0_SWAP (struct bap_polynom_mpz *,
              A,
              cont);
          i = 0;
        }
      else
        i++;
    }

/*
 * For the unknowns x which do not occur linearly, factor content (A, x).
 * Accumulates in prod.
 * Replaces A by primpart (A, x).
 */
  bav_init_term (&T);
  bav_set_term (&T, &A->total_rank);
  for (i = 0; i < T.size; i++)
    {
      if (!bap_depend_polynom_mpz (A, T.rg[i].var))
        continue;
      v = A->total_rank.rg[i].var;
      bap_lcoeff_polynom_mpz (&C, A, v);
      if (bap_nbmon_polynom_mpz (&C) < 2)
        continue;
      baz_content_polynom_mpz (cont, A, v);
      if (!bap_is_one_polynom_mpz (cont))
        bap_exquo_polynom_mpz (A, A, cont);
      baz_factor_non_trivial_polynom_mpz (prod, cont);
    }

  ba0_pull_stack ();
  baz_factor_non_trivial_primitive_polynom_mpz (prod, A);
  ba0_push_another_stack ();
}

/*
 * Assigns the irreducible factorization of A to prod.
 * The numerical factor of prod receives the gcd of the coefficients
 * of A and carries the sign of the leading coeff.
 */

/*
 * texinfo: baz_factor_polynom_mpz
 * Assign to @var{prod} the complete factorization of @var{A} over
 * the integers.
 * The numerical factor of @var{prod} receives the gcd of the numerical
 * coefficients of @var{A} and carries the sign of the leading coefficient.
 */

BAZ_DLL void
baz_factor_polynom_mpz (
    struct bap_product_mpz *prod,
    struct bap_polynom_mpz *A)
{
  struct bap_polynom_mpz AA;
  struct bav_term T;
  struct ba0_mark M;
/*
 * Reinit prod. Takes the numerical factor into account.
 */
/*
ba0_printf ("Entree dans factor : %Az\n", A);
*/
  bap_set_product_one_mpz (prod);
  bap_signed_numeric_content_polynom_mpz (prod->num_factor, A);

  ba0_push_another_stack ();
  ba0_record (&M);
/*
   Exit constant polynomials
*/
  if (!bap_is_numeric_polynom_mpz (A))
    {
      bap_init_polynom_mpz (&AA);
      bap_exquo_polynom_numeric_mpz (&AA, A, prod->num_factor);
/*
   Get rid of factors of the form x^k
*/
      bav_init_term (&T);
      bap_minimal_total_rank_polynom_mpz (&T, &AA);
      bap_exquo_polynom_term_mpz (&AA, &AA, &T);
      ba0_pull_stack ();
      bap_mul_product_term_mpz (prod, prod, &T);
      ba0_push_another_stack ();
      baz_factor_non_trivial_polynom_mpz (prod, &AA);
    }

  ba0_pull_stack ();
  ba0_restore (&M);
}
