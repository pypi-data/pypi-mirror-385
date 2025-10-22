#include "baz_prospec_mpz.h"
#include "baz_polyspec_mpz.h"
#include "baz_gcd_polynom_mpz.h"

/*
 * texinfo: baz_factor_numeric_content_product_mpz
 * Assign to @var{R} the product obtained by replacing each factor
 * of @var{A} by its sign-normalized numerical primitive.
 * Some factors of @var{A} may get collected in @var{R}.
 */

BAZ_DLL void
baz_factor_numeric_content_product_mpz (
    struct bap_product_mpz *R,
    struct bap_product_mpz *A)
{
  struct bap_polynom_mpz ppA;
  ba0_mpz_t cont;
  ba0_int_p a;
  struct ba0_mark M;

  if (bap_is_zero_product_mpz (A))
    {
      bap_set_product_zero_mpz (R);
      return;
    }

  if (R == A)
    {
      struct bap_product_mpz B;

      ba0_push_another_stack ();
      ba0_record (&M);
      bap_init_product_mpz (&B);
      bap_set_product_mpz (&B, A);
      ba0_pull_stack ();
      baz_factor_numeric_content_product_mpz (R, &B);
      ba0_restore (&M);
      return;
    }

  bap_set_product_one_mpz (R);
  bap_mul_product_numeric_mpz (R, R, A->num_factor);
  bap_realloc_product_mpz (R, A->size);

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_mpz_init (cont);
  bap_init_polynom_mpz (&ppA);

  for (a = 0; a < A->size; a++)
    {
      if (A->tab[a].exponent > 0)
        {
          bap_signed_numeric_content_polynom_mpz (cont, &A->tab[a].factor);
          bap_exquo_polynom_numeric_mpz (&ppA, &A->tab[a].factor, cont);
          ba0_mpz_pow_ui (cont, cont, A->tab[a].exponent);

          ba0_pull_stack ();
          bap_mul_product_numeric_mpz (R, R, cont);
          bap_mul_product_polynom_mpz (R, R, &ppA, A->tab[a].exponent);
          ba0_push_another_stack ();
        }
    }

  ba0_pull_stack ();
  ba0_restore (&M);
}

/* 
 * texinfo: baz_gcd_product_mpz
 *
 * Assign to @var{G} the gcd of the products @var{A} and @var{B}.
 * The products @var{cofA} and @var{cofB} are assigned @math{A/G} and
 * @math{B/G}. The parameters @var{G}, @var{cofA} and @var{cofB} may
 * be the zero pointer. 
 * The result variables have their numerical contents factored.
 */

BAZ_DLL void
baz_gcd_product_mpz (
    struct bap_product_mpz *G,
    struct bap_product_mpz *cofA,
    struct bap_product_mpz *cofB,
    struct bap_product_mpz *A,
    struct bap_product_mpz *B)
{
  struct bap_product_mpz GG, AA, BB;
  struct bap_polynom_mpz g, cofa, cofb;
  ba0_int_p a, b, dG;
  bool lost_A_factor;
  ba0_mpz_t cont;
  struct ba0_mark M;

  if (bap_is_zero_product_mpz (A))
    {
      if (G != (struct bap_product_mpz *) 0 && G != B)
        bap_set_product_mpz (G, B);
      if (cofA != (struct bap_product_mpz *) 0)
        bap_set_product_zero_mpz (cofA);
      if (cofB != (struct bap_product_mpz *) 0)
        bap_set_product_one_mpz (cofB);
      return;
    }
  else if (bap_is_zero_product_mpz (B))
    {
      if (G != (struct bap_product_mpz *) 0 && G != A)
        bap_set_product_mpz (G, A);
      if (cofA != (struct bap_product_mpz *) 0)
        bap_set_product_one_mpz (cofA);
      if (cofB != (struct bap_product_mpz *) 0)
        bap_set_product_zero_mpz (cofB);
      return;
    }

  ba0_push_another_stack ();
  ba0_record (&M);

  if (G != (struct bap_product_mpz *) 0)
    bap_init_product_mpz (&GG);
  bap_init_product_mpz (&AA);
  bap_init_product_mpz (&BB);

  bap_set_product_mpz (&AA, A);
  bap_set_product_mpz (&BB, B);

  bap_init_polynom_mpz (&g);
  bap_init_polynom_mpz (&cofa);
  bap_init_polynom_mpz (&cofb);

  a = 0;
  b = 0;
  while (a < AA.size && b < BB.size)
    {
/*
 * The two next tests seem to be useless but they do not harm.
 */
      if (AA.tab[a].exponent == 0)
        {
          a += 1;
          continue;
        }
      if (BB.tab[b].exponent == 0)
        {
          b += 1;
          if (b >= BB.size)
            {
              a += 1;
              b = 0;
            }
          continue;
        }
      baz_gcd_polynom_mpz (&g, &cofa, &cofb, &AA.tab[a].factor,
          &BB.tab[b].factor);
      if (bap_is_one_polynom_mpz (&g))
        {
/*
 * The factors are coprime. Compare the current A factor to the next B one.
 * If all B factors have been considered, restart with the next A one.
 */
          b += 1;
          if (b == BB.size)
            {
              a += 1;
              b = 0;
            }
          continue;
        }
/*
 * The current factors of A and B are not coprime. Simplify.
 */
      dG = BA0_MIN (AA.tab[a].exponent, BB.tab[b].exponent);
      if (G != (struct bap_product_mpz *) 0)
        bap_mul_product_polynom_mpz (&GG, &GG, &g, dG);
      bap_mul_product_polynom_mpz (&AA, &AA, &cofa, dG);
      bap_mul_product_polynom_mpz (&BB, &BB, &cofb, dG);
      lost_A_factor = AA.tab[a].exponent == dG;
      bap_exquo_product_polynom_mpz (&AA, &AA, &AA.tab[a].factor, dG);
      bap_exquo_product_polynom_mpz (&BB, &BB, &BB.tab[b].factor, dG);
/*
 * At least one of the two current factors of A and B was removed by the exquo
 * operations. If it is the A factor, then the new current A factor is 
 * completely new. It must be compared to all B factors, starting from 
 * the first one.
 */
      if (lost_A_factor)
        b = 0;
    }

  baz_factor_numeric_content_product_mpz (&AA, &AA);
  baz_factor_numeric_content_product_mpz (&BB, &BB);

  ba0_mpz_init (cont);
  ba0_mpz_gcd (cont, AA.num_factor, BB.num_factor);
  ba0_mpz_divexact (AA.num_factor, AA.num_factor, cont);
  ba0_mpz_divexact (BB.num_factor, BB.num_factor, cont);

  if (G != (struct bap_product_mpz *) 0)
    {
      baz_factor_numeric_content_product_mpz (&GG, &GG);
      ba0_mpz_mul (GG.num_factor, GG.num_factor, cont);
    }

  ba0_pull_stack ();

  if (G != (struct bap_product_mpz *) 0)
    bap_set_product_mpz (G, &GG);
  if (cofA != (struct bap_product_mpz *) 0)
    bap_set_product_mpz (cofA, &AA);
  if (cofB != (struct bap_product_mpz *) 0)
    bap_set_product_mpz (cofB, &BB);

  if (cofA != (struct bap_product_mpz *) 0
      && cofB != (struct bap_product_mpz *) 0
      && ba0_mpz_sgn (cofA->num_factor) < 0
      && ba0_mpz_sgn (cofB->num_factor) < 0)
    {
      ba0_mpz_neg (cofA->num_factor, cofA->num_factor);
      ba0_mpz_neg (cofB->num_factor, cofB->num_factor);
      if (G != (struct bap_product_mpz *) 0)
        ba0_mpz_neg (G->num_factor, G->num_factor);
    }

  ba0_restore (&M);
}
