#include "bap_add_polynom_mpzm.h"
#include "bap_mul_polynom_mpzm.h"
#include "bap_creator_mpzm.h"
#include "bap_itermon_mpzm.h"
#include "bap_geobucket_mpzm.h"

#define BAD_FLAG_mpzm


/*
 * texinfo: bap_init_geobucket_mpzm
 * Initialize @var{geo} to @math{0}.
 */

BAP_DLL void
bap_init_geobucket_mpzm (
    struct bap_geobucket_mpzm *geo)
{
  ba0_init_table ((struct ba0_table *) geo);
}

/*
 * texinfo: bap_reset_geobucket_mpzm
 * Reset @var{geo} to @math{0}.
 */

BAP_DLL void
bap_reset_geobucket_mpzm (
    struct bap_geobucket_mpzm *geo)
{
  ba0_reset_table ((struct ba0_table *) geo);
}

/*
 * geo = geo * A
 */

/*
 * texinfo: bap_mul_geobucket_mpzm
 * Multiplie @var{geo} by @var{A}.
 */

BAP_DLL void
bap_mul_geobucket_mpzm (
    struct bap_geobucket_mpzm *geo,
    struct bap_polynom_mpzm *A)
{
  ba0_int_p i, j, n, two_pow_j;

  if (bap_is_zero_polynom_mpzm (A))
    bap_reset_geobucket_mpzm (geo);
  else if (!bap_is_one_polynom_mpzm (A))
    {
/*
 * First multiply
 */
      for (i = 0; i < geo->size; i++)
        if (!bap_is_zero_polynom_mpzm (geo->tab[i]))
          bap_mul_polynom_mpzm (geo->tab[i], geo->tab[i], A);
/*
 * The numbers of monomials changed. Move entries.
 */
      i = geo->size - 1;
      while (i >= 0)
        {
          n = bap_nbmon_polynom_mpzm (geo->tab[i]);
          if (n > 0)
            {
/*
 * Move tab[i] to tab [j]. Find j.
 */
              j = i;
              two_pow_j = 1 << j;
              while (n > two_pow_j)
                {
                  j += 1;
                  two_pow_j <<= 1;
                }

              if (j >= geo->size)
                {
                  ba0_realloc2_table ((struct ba0_table *) geo, j + 2,
                      (ba0_new_function *) & bap_new_polynom_mpzm);
                  geo->size = j + 1;
                }

              if (j != i)
                {
                  if (bap_is_zero_polynom_mpzm (geo->tab[j]))
                    {
                      BA0_SWAP (struct bap_polynom_mpzm *,
                          geo->tab[i],
                          geo->tab[j]);
                      i -= 1;
                    }
                  else
                    {
                      bap_add_polynom_mpzm (geo->tab[j], geo->tab[j],
                          geo->tab[i]);
                      bap_set_polynom_zero_mpzm (geo->tab[i]);
/*
 * The sum may, also, have changed the number of monomials.
 * Restart from j.
 */
                      i = j;
                    }
                }
              else
                i -= 1;
            }
          else
            i -= 1;
        }
    }
}

/*
 * geo = geo * c. Assume a domain.
 */

/*
 * texinfo: bap_mul_geobucket_numeric_mpzm
 * Multiplie @var{geo} by @var{c}.
 */

BAP_DLL void
bap_mul_geobucket_numeric_mpzm (
    struct bap_geobucket_mpzm *geo,
    ba0_mpzm_t c)
{
  ba0_int_p i;

  if (ba0_mpzm_is_zero (c))
    bap_reset_geobucket_mpzm (geo);
  else if (ba0_mpzm_is_one (c))
    {
      for (i = 0; i < geo->size; i++)
        if (!bap_is_zero_polynom_mpzm (geo->tab[i]))
          bap_mul_polynom_numeric_mpzm (geo->tab[i], geo->tab[i], c);
    }
}

/*
 * geo = geo + A
 */

/*
 * texinfo: bap_add_geobucket_mpzm
 * Add @var{A} to @var{geo}.
 */

BAP_DLL void
bap_add_geobucket_mpzm (
    struct bap_geobucket_mpzm *geo,
    struct bap_polynom_mpzm *A)
{
  ba0_int_p i, two_pow_i;

  i = bap_ceil_log2 (bap_nbmon_polynom_mpzm (A));
  if (i >= geo->size)
    {
      ba0_realloc2_table ((struct ba0_table *) geo, i + 2,
          (ba0_new_function *) & bap_new_polynom_mpzm);
      bap_set_polynom_mpzm (geo->tab[i], A);
      geo->size = i + 1;
    }
  else
    {
      bap_add_polynom_mpzm (geo->tab[i], geo->tab[i], A);
      two_pow_i = 1 << i;
      while (bap_nbmon_polynom_mpzm (geo->tab[i]) > two_pow_i)
        {
          bap_add_polynom_mpzm (geo->tab[i + 1], geo->tab[i + 1], geo->tab[i]);
          bap_set_polynom_zero_mpzm (geo->tab[i]);
          i += 1;
          two_pow_i <<= 1;
        }
/*
   i is the last index used
*/
      if (i >= geo->size)
        {
          geo->size = i + 1;
          ba0_realloc2_table ((struct ba0_table *) geo, i + 2,
              (ba0_new_function *) & bap_new_polynom_mpzm);
        }
    }
}

/*
 * geo = geo - A
 */

/*
 * texinfo: bap_sub_geobucket_mpzm
 * Subtract @var{A} from @var{geo}.
 */

BAP_DLL void
bap_sub_geobucket_mpzm (
    struct bap_geobucket_mpzm *geo,
    struct bap_polynom_mpzm *A)
{
  ba0_int_p i, two_pow_i;

  i = bap_ceil_log2 (bap_nbmon_polynom_mpzm (A));
  if (i >= geo->size)
    {
      ba0_realloc2_table ((struct ba0_table *) geo, i + 2,
          (ba0_new_function *) & bap_new_polynom_mpzm);
      bap_neg_polynom_mpzm (geo->tab[i], A);
      geo->size = i + 1;
    }
  else
    {
      bap_sub_polynom_mpzm (geo->tab[i], geo->tab[i], A);
      two_pow_i = 1 << i;
      while (bap_nbmon_polynom_mpzm (geo->tab[i]) > two_pow_i)
        {
          bap_add_polynom_mpzm (geo->tab[i + 1], geo->tab[i + 1], geo->tab[i]);
          bap_set_polynom_zero_mpzm (geo->tab[i]);
          i += 1;
          two_pow_i <<= 1;
        }
/*
   i is the last used index
*/
      if (i >= geo->size)
        {
          geo->size = i + 1;
          ba0_realloc2_table ((struct ba0_table *) geo, i + 2,
              (ba0_new_function *) & bap_new_polynom_mpzm);
        }
    }
}

/*
 * A = geo
 */

/*
 * texinfo: bap_set_polynom_geobucket_mpzm
 * Assign @var{geo} to @var{A}.
 */

BAP_DLL void
bap_set_polynom_geobucket_mpzm (
    struct bap_polynom_mpzm *A,
    struct bap_geobucket_mpzm *geo)
{
  struct bap_creator_mpzm crea;
  struct bap_itermon_mpzm *iter;
  struct bav_term *T, U;
  enum ba0_compare_code code;
  ba0_mpzm_t *lcm, *lc;
  ba0_int_p im, i, deb, fin;
  bool found;
  struct ba0_mark M;

  if (geo->size == 0)
    {
      bap_set_polynom_zero_mpzm (A);
      return;
    }

  ba0_push_another_stack ();
  ba0_record (&M);

  iter =
      (struct bap_itermon_mpzm *) ba0_alloc (sizeof (struct bap_itermon_mpzm)
      * geo->size);
  T = (struct bav_term *) ba0_alloc (sizeof (struct bav_term) * geo->size);

  bav_init_term (&U);

  deb = 0;
  while (deb < geo->size && bap_is_zero_polynom_mpzm (geo->tab[deb]))
    deb++;
  fin = geo->size - 1;
  while (fin >= deb && bap_is_zero_polynom_mpzm (geo->tab[fin]))
    fin--;

  for (i = deb; i <= fin; i++)
    {
      bap_begin_itermon_mpzm (&iter[i], geo->tab[i]);
      bav_init_term (&T[i]);
      if (!bap_is_zero_polynom_mpzm (geo->tab[i]))
        bap_term_itermon_mpzm (&T[i], &iter[i]);
      bav_lcm_term (&U, &U, &geo->tab[i]->total_rank);
    }

  ba0_pull_stack ();
  bap_begin_creator_mpzm (&crea, A, &U, bap_approx_total_rank,
      bap_nbmon_polynom_mpzm (geo->tab[fin]));
  ba0_push_another_stack ();
/*
 * To avoid some pointless warnings (or use -Wno-uninitialized)
 */
  lcm = (ba0_mpzm_t *) 0;
  im = 0;

  while (deb <= fin)
    {
      found = false;
      while (!found && deb <= fin)
        {
          im = deb;
          if (bap_outof_itermon_mpzm (&iter[im]))
            BA0_RAISE_EXCEPTION (BA0_ERRALG);
          lcm = bap_coeff_itermon_mpzm (&iter[im]);
          found = true;
          for (i = im + 1; found && i <= fin; i++)
            {
              if (bap_outof_itermon_mpzm (&iter[i]))
                continue;
              code = bav_compare_term (&T[im], &T[i]);
              if (code == ba0_lt)
                {
                  im = i;
                  lcm = bap_coeff_itermon_mpzm (&iter[im]);
                }
              else if (code == ba0_eq)
                {
                  lc = bap_coeff_itermon_mpzm (&iter[i]);
                  ba0_mpzm_add (*lc, *lc, *lcm);
                  bap_next_itermon_mpzm (&iter[im]);
                  if (!bap_outof_itermon_mpzm (&iter[im]))
                    bap_term_itermon_mpzm (&T[im], &iter[im]);
                  im = i;
                  lcm = lc;
                  if (ba0_mpzm_is_zero (*lcm))
                    {
                      found = false;
                      bap_next_itermon_mpzm (&iter[im]);
                      if (!bap_outof_itermon_mpzm (&iter[im]))
                        bap_term_itermon_mpzm (&T[im], &iter[im]);
                    }
                  while (deb <= fin && bap_outof_itermon_mpzm (&iter[deb]))
                    deb++;
                  while (deb <= fin && bap_outof_itermon_mpzm (&iter[fin]))
                    fin--;
                }
            }
        }
      if (found)
        {
          ba0_pull_stack ();
          bap_write_creator_mpzm (&crea, &T[im], *lcm);
          ba0_push_another_stack ();
          bap_next_itermon_mpzm (&iter[im]);
          if (!bap_outof_itermon_mpzm (&iter[im]))
            bap_term_itermon_mpzm (&T[im], &iter[im]);
          while (deb <= fin && bap_outof_itermon_mpzm (&iter[deb]))
            deb++;
          while (deb <= fin && bap_outof_itermon_mpzm (&iter[fin]))
            fin--;
        }
    }

  ba0_pull_stack ();
  bap_close_creator_mpzm (&crea);
  ba0_restore (&M);
}

#undef BAD_FLAG_mpzm
