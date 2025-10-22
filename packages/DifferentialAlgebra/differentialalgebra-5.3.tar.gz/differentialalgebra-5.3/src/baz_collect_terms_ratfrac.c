#include "baz_polyspec_mpz.h"
#include "baz_collect_terms_ratfrac.h"

static bool
baz_are_likely_to_be_collected (
    struct baz_ratfrac *F,
    struct baz_ratfrac *G)
{
  return bav_equal_term (&F->numer.total_rank, &G->numer.total_rank)
      && bav_equal_term (&F->denom.total_rank, &G->denom.total_rank)
      && bap_nbmon_polynom_mpz (&F->numer) == bap_nbmon_polynom_mpz (&G->numer)
      && bap_nbmon_polynom_mpz (&F->denom) == bap_nbmon_polynom_mpz (&G->denom);
}

static void
baz_preprocess_for_collect (
    ba0_mpz_t contnum,
    ba0_mpz_t contden,
    struct bap_polynom_mpz *ppnum,
    struct bap_polynom_mpz *ppden,
    ba0_int_p *yet,
    struct baz_ratfrac *F)
{
  bap_signed_numeric_content_polynom_mpz (contnum, &F->numer);
  bap_signed_numeric_content_polynom_mpz (contden, &F->denom);
  bap_exquo_polynom_numeric_mpz (ppnum, &F->numer, contnum);
  bap_exquo_polynom_numeric_mpz (ppden, &F->denom, contden);
  *yet = true;
}

/*
 * A differential rational fraction was decomposed as 
 *      sum coeffs [i] * terms [i]
 * This algorithm looks for indices i and j such that 
 *      alpha * coeffs [i] = coeffs [j]
 * where alpha is a rational number. 
 * In such cases, one glues terms i and j together:
 *      coeffs [i] * (terms [i] + alpha*terms [j])
 *
 * The coeffs are supposed to be reduced rational fractions.
 */

/*
 * texinfo: baz_collect_terms_tableof_ratfrac
 * The table @var{coeffs} and @var{terms} are two tables of the same size.
 * They represent the sum of the products of the coefficients by the terms,
 * pairwise. The rational fractions are supposed to be reduced.
 * The function collects together the terms, whose coefficients are equal,
 * up to some multiplicative rational number factor.
 * Mathematically, the represented sum is not changed.
 */

BAZ_DLL void
baz_collect_terms_tableof_ratfrac (
    struct baz_tableof_ratfrac *collected_coeffs,
    struct baz_tableof_ratfrac *collected_terms,
    struct baz_tableof_ratfrac *coeffs,
    struct baz_tableof_ratfrac *terms)
{
  struct baz_tableof_ratfrac tmp_coeffs, tmp_terms;
  bool in_place;
  struct bap_tableof_polynom_mpz ppnum, ppden;
  struct ba0_tableof_mpz contnum, contden;
  struct ba0_tableof_int_p yet;
  ba0_mpq_t alpha, beta;
  ba0_int_p i, j;
  struct ba0_mark M;

  if (coeffs->size != terms->size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_init_table ((struct ba0_table *) &tmp_coeffs);
  ba0_init_table ((struct ba0_table *) &tmp_terms);

  if (collected_coeffs == coeffs && collected_terms == terms)
    in_place = true;
  else
    {
      in_place = false;
      ba0_set_table ((struct ba0_table *) &tmp_coeffs,
          (struct ba0_table *) coeffs);
      ba0_set2_table ((struct ba0_table *) &tmp_terms,
          (struct ba0_table *) terms, (ba0_new_function *) & baz_new_ratfrac,
          (ba0_set_function *) & baz_set_ratfrac);
    }
/*
 * Coeffs are not modified. They are decomposed as numerical content and 
 * primitive part for both the numerator and the denominator. Terms will
 * be modified.
 */
  ba0_init_table ((struct ba0_table *) &ppnum);
  ba0_init_table ((struct ba0_table *) &ppden);
  ba0_init_table ((struct ba0_table *) &contnum);
  ba0_init_table ((struct ba0_table *) &contden);
  ba0_init_table ((struct ba0_table *) &yet);
  ba0_realloc2_table ((struct ba0_table *) &ppnum, coeffs->size,
      (ba0_new_function *) & bap_new_polynom_mpz);
  ppnum.size = coeffs->size;
  ba0_realloc2_table ((struct ba0_table *) &ppden, coeffs->size,
      (ba0_new_function *) & bap_new_polynom_mpz);
  ppden.size = coeffs->size;
  ba0_realloc2_table ((struct ba0_table *) &contnum, coeffs->size,
      (ba0_new_function *) & ba0_new_mpz);
  contnum.size = coeffs->size;
  ba0_realloc2_table ((struct ba0_table *) &contden, coeffs->size,
      (ba0_new_function *) & ba0_new_mpz);
  contden.size = coeffs->size;
  ba0_realloc_table ((struct ba0_table *) &yet, coeffs->size);
  for (i = 0; i < coeffs->size; i++)
    yet.tab[i] = false;
  yet.size = coeffs->size;

  ba0_mpq_init (alpha);
  ba0_mpq_init (beta);

  i = 0;
  while (i < yet.size - 1)
    {
      j = i + 1;
      while (j < yet.size)
        {
          if (in_place ? baz_are_likely_to_be_collected (coeffs->tab[i],
                  coeffs->tab[j]) : baz_are_likely_to_be_collected (tmp_coeffs.
                  tab[i], tmp_coeffs.tab[j]))
            {
              if (!yet.tab[i])
                baz_preprocess_for_collect (contnum.tab[i], contden.tab[i],
                    ppnum.tab[i], ppden.tab[i], &yet.tab[i],
                    in_place ? coeffs->tab[i] : tmp_coeffs.tab[i]);
              if (!yet.tab[j])
                baz_preprocess_for_collect (contnum.tab[j], contden.tab[j],
                    ppnum.tab[j], ppden.tab[j], &yet.tab[j],
                    in_place ? coeffs->tab[j] : tmp_coeffs.tab[j]);
              if (bap_equal_polynom_mpz (ppnum.tab[i], ppnum.tab[j])
                  && bap_equal_polynom_mpz (ppden.tab[i], ppden.tab[j]))
                {
                  ba0_mpz_set (ba0_mpq_numref (alpha), contnum.tab[j]);
                  ba0_mpz_set (ba0_mpq_denref (alpha), contden.tab[j]);
                  ba0_mpz_set (ba0_mpq_numref (beta), contden.tab[i]);
                  ba0_mpz_set (ba0_mpq_denref (beta), contnum.tab[i]);
                  ba0_mpq_mul (alpha, alpha, beta);
/*
 * Denote ai,bi,aj,bj the numerical contents of the numerators and
 * denominators of coeffs [i] and coeffs [j] so that:
 *      coeffs [i] = ai/bi * pp/qq
 *      coeffs [j] = aj/bj * pp/qq
 * Compute alpha = bi/ai * aj/bj
 * Then coeffs [i] * terms [i] + coeffs [j] * terms [j]
 * =    coeffs [i] * terms [i] + aj/bj * bi/ai * coeffs [i] * terms [j]
 * =    coeffs [i] * terms [i] + alpha * coeffs [i] * terms [j]
 * =    coeffs [i] * (terms [i] + alpha * terms [j])
*/
                  if (in_place)
                    {
                      ba0_pull_stack ();
                      baz_mul_ratfrac_numeric_mpq (terms->tab[j], terms->tab[j],
                          alpha);
                      baz_add_ratfrac (terms->tab[i], terms->tab[i],
                          terms->tab[j]);
                      ba0_delete_table ((struct ba0_table *) coeffs, j);
                      ba0_delete_table ((struct ba0_table *) terms, j);
                      ba0_push_another_stack ();
                    }
                  else
                    {
                      baz_mul_ratfrac_numeric_mpq (tmp_terms.tab[j],
                          tmp_terms.tab[j], alpha);
                      baz_add_ratfrac (tmp_terms.tab[i], tmp_terms.tab[i],
                          tmp_terms.tab[j]);
                      ba0_delete_table ((struct ba0_table *) &tmp_coeffs, j);
                      ba0_delete_table ((struct ba0_table *) &tmp_terms, j);
                    }
                  ba0_delete_table ((struct ba0_table *) &ppnum, j);
                  ba0_delete_table ((struct ba0_table *) &ppden, j);
                  ba0_delete_table ((struct ba0_table *) &contnum, j);
                  ba0_delete_table ((struct ba0_table *) &contden, j);
                  ba0_delete_table ((struct ba0_table *) &yet, j);
                }
              else
                j += 1;
            }
          else
            j += 1;
        }
      i += 1;
    }
  ba0_pull_stack ();
  if (!in_place)
    {
      ba0_set_table ((struct ba0_table *) collected_coeffs,
          (struct ba0_table *) &tmp_coeffs);
      ba0_set2_table ((struct ba0_table *) collected_terms,
          (struct ba0_table *) &tmp_terms,
          (ba0_new_function *) & baz_new_ratfrac,
          (ba0_set_function *) & baz_set_ratfrac);
    }
  ba0_restore (&M);
}
