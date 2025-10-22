#include "bap_termanager.h"

/*
   Compute tgest->zipping.size
   Take care to the knapsack problem which may arise in the case of 
        a change of ordering.
*/

static void
compute_zipping (
    struct bap_termanager *tgest)
{
  bav_Idegree d;
  ba0_int_p s, m;
  ba0_int_p i, z;

  if (tgest->total_rank.size == 0)
    {
      tgest->zipping.size = 0;
      return;
    }

  s = 0;
  m = -1;
/*
   s = sum of nbbits [i]
   m = max of nbbits [i]
*/
  for (i = 0; i < tgest->total_rank.size; i++)
    {
      for (z = 0, d = tgest->total_rank.rg[i].deg; d > 0; d >>= 1)
        z++;
      tgest->zipping.nbbits[i] = (char) z;
      tgest->zipping.mask[i] =
          (unsigned ba0_int_p) -1 >> (BA0_NBBITS_INT_P - z);
      s += z;
      if (z > m)
        m = z;
    }
/*
   What is the value of tgest->zipping.size ?

   One knows that one must store s bits on ba0_int_p.
   At each change of ba0_int_p, one may "loose" at most m-1 bits

   We are thus looking for x such that
	BA0_NBBITS_INT_P * x >= s + (x - 1) * (m - 1)
   i.e. such that
	(BA0_NBBITS_INT_P - m + 1) * x >= s - m + 1
   Therefore
                					        s - m + 1
	tgest->zipping.size = x = ceil ( ------------------------ )
				               	     BA0_NBBITS_INT_P - m + 1
*/
  {
    ba0_int_p p, q;

    p = s - m + 1;
    q = BA0_NBBITS_INT_P - m + 1;
    tgest->zipping.size = p % q == 0 ? p / q : p / q + 1;
  }
}

/* 
 * texinfo: bap_init_termanager
 * Initialize @var{tgest} with field @code{total_rank} equal to @var{T}.
 * Note that @var{T} may be a proper multiple of the actual total
 * rank of the clot.
 */

BAP_DLL void
bap_init_termanager (
    struct bap_termanager *tgest,
    struct bav_term *T)
{
  bav_init_term (&tgest->total_rank);
  bav_set_term (&tgest->total_rank, T);
  if (tgest->total_rank.alloc > 0)
    {
      tgest->zipping.nbbits =
          (unsigned char *) ba0_alloc (sizeof (unsigned char) *
          tgest->total_rank.alloc);
      tgest->zipping.mask =
          (unsigned ba0_int_p *) ba0_alloc (sizeof (unsigned ba0_int_p) *
          tgest->total_rank.alloc);
    }
  compute_zipping (tgest);
  tgest->zipping.alloc = tgest->zipping.size;
}

/* 
 * texinfo: bap_reset_termanager
 * Resets @var{tgest} with field @code{total_rank} equal to @var{T}.
 * Set @var{reinit} to @code{true} if it is necessary to
 * apply @code{bap_init_zipterm_array_termanager} to all arrays
 * of zipterms formerly handled by this termanager.
 */

BAP_DLL void
bap_reset_termanager (
    struct bap_termanager *tgest,
    struct bav_term *T,
    bool *reinit)
{
  ba0_int_p old_total_rank_alloc = tgest->total_rank.alloc;

  bav_set_term (&tgest->total_rank, T);
  if (tgest->total_rank.alloc > old_total_rank_alloc)
    {
      tgest->zipping.nbbits =
          (unsigned char *) ba0_alloc (sizeof (unsigned char) *
          tgest->total_rank.alloc);
      tgest->zipping.mask =
          (unsigned ba0_int_p *) ba0_alloc (sizeof (unsigned ba0_int_p) *
          tgest->total_rank.alloc);
    }
  compute_zipping (tgest);
  if (tgest->zipping.size > tgest->zipping.alloc)
    {
      *reinit = tgest->zipping.size > 1;
      tgest->zipping.alloc = tgest->zipping.size;
    }
  else
    *reinit = false;
}

/*
 * texinfo: bap_init_zipterm_array_termanager
 * Allocate each entry of the array @var{tab} of @var{n} zipterms so that 
 * @var{tab} can receive the zipterms handled by @var{tgest}.
 */

BAP_DLL void
bap_init_zipterm_array_termanager (
    struct bap_termanager *tgest,
    bap_zipterm *tab,
    ba0_int_p n)
{
  ba0_int_p i;
  if (tgest->zipping.alloc > 1)
    for (i = 0; i < n; i++)
      tab[i] =
          (bap_zipterm) ba0_alloc (sizeof (ba0_int_p) * tgest->zipping.alloc);
}

/*
 * texinfo: bap_equal_termanager
 * Return @code{true} if @var{A} and @var{B} have the same fields
 * @code{total_rank} so that their zipterms are compatible.
 */

BAP_DLL bool
bap_equal_termanager (
    struct bap_termanager *A,
    struct bap_termanager *B)
{
  return bav_equal_term (&A->total_rank, &B->total_rank);
}

/*
 * texinfo: bap_init_set_termanager
 * Assign @var{src} to @var{dst}.
 */

BAP_DLL void
bap_init_set_termanager (
    struct bap_termanager *dst,
    struct bap_termanager *src)
{
  ba0_int_p alloc;

  bav_init_term (&dst->total_rank);
  bav_set_term (&dst->total_rank, &src->total_rank);
  dst->zipping.size = src->zipping.size;
  dst->zipping.alloc = src->zipping.alloc;
  alloc = dst->total_rank.alloc;
  dst->zipping.nbbits =
      (unsigned char *) ba0_alloc (sizeof (unsigned char) * alloc);
  dst->zipping.mask =
      (unsigned ba0_int_p *) ba0_alloc (sizeof (unsigned ba0_int_p) * alloc);
  memcpy (dst->zipping.nbbits, src->zipping.nbbits,
      alloc * sizeof (unsigned char));
  memcpy (dst->zipping.mask, src->zipping.mask, alloc * sizeof (ba0_int_p));
}

/*
 * texinfo: bap_set_zipterm_zipterm_termanager
 * Assign @var{src_zipterm} (handled by @var{src_tgest}) to @var{dst_zipterm}
 * (handled by @var{dst_tgest}) in the special case where zipterms
 * are compatible.
 */

/*
 * Even in this case, take care to the fact that zipterms may be
 * ba0_int_p or ba0_int_p* !
 */

BAP_DLL void
bap_set_zipterm_zipterm_termanager (
    struct bap_termanager *dst_tgest,
    bap_zipterm *dst_zipterm,
    struct bap_termanager *src_tgest,
    bap_zipterm src_zipterm)
{
  if (dst_tgest->zipping.alloc <= 1)
    {
      if (src_tgest->zipping.alloc <= 1)
        *dst_zipterm = src_zipterm;
      else
        *dst_zipterm = *(bap_zipterm *) (void *) src_zipterm;
    }
  else
    {
      if (src_tgest->zipping.alloc <= 1)
        **(bap_zipterm **) (void *) dst_zipterm = src_zipterm;
      else
        {
          ba0_int_p *p, *q, i;
          p = *(ba0_int_p **) (void *) dst_zipterm;
          q = (ba0_int_p *) (void *) src_zipterm;
          for (i = 0; i < dst_tgest->zipping.size; i++)
            *p++ = *q++;
        }
    }
}

/*
 * texinfo: bap_set_zipterm_term_termanager
 * Compress @var{T} and store it in @var{zipterm}, which is handled
 * by @var{tgest}.
 */

BAP_DLL void
bap_set_zipterm_term_termanager (
    struct bap_termanager *tgest,
    bap_zipterm *zipterm,
    struct bav_term *T)
{
  ba0_int_p i, j, k, m, z, *tab;
/*
   Catches a hell a lot of bugs
*/
  if (!bav_is_factor_term (&tgest->total_rank, T, (struct bav_term *) 0))
    BA0_RAISE_EXCEPTION (BAP_ERRTGS);
/*
   tab points to the array of ba0_int_p which receives the compressed term
   i runs on tgest->total_rank
   j runs on T
   k runs on tab
   z is the ba0_int_p being built (i.e. tab [k])
   m = how many times the current degree must be shifted
*/
  tab =
      tgest->zipping.alloc <=
      1 ? (ba0_int_p *) (void *) zipterm : (ba0_int_p *) (void *) *zipterm;
  i = j = k = 0;
  while (j < T->size)
    {
      m = 0;
      z = 0;
      while (j < T->size
          && m + tgest->zipping.nbbits[i] <= (ba0_int_p) BA0_NBBITS_INT_P)
        {
          if (tgest->total_rank.rg[i].var == T->rg[j].var)
            z |= T->rg[j++].deg << m;
          m += tgest->zipping.nbbits[i];
          i++;
        }
      tab[k++] = z;
    }
  while (k < tgest->zipping.size)
    tab[k++] = 0;
}

/*
 * texinfo: bap_set_term_zipterm_termanager
 * Uncompress @var{zipterm}, which is handled by @var{tgest} and
 * store the result in @var{T}.
 */

BAP_DLL void
bap_set_term_zipterm_termanager (
    struct bap_termanager *tgest,
    struct bav_term *T,
    bap_zipterm zipterm)
{
  ba0_int_p i, j, k, m, d, z, *tab;
/*
   tab points to the array of ba0_int_p to be uncompressed
   i runs on tgest->total_rank
   j runs on T
   k runs on tab
   z = the ba0_int_p being uncompressed (i.e. tab [k])
   m = how many times z must be shifted to get the current degree

   the first loop determines the size of the term
   the second loop builds the term
*/
  tab =
      tgest->zipping.alloc <=
      1 ? (ba0_int_p *) & zipterm : (ba0_int_p *) (void *) zipterm;
  i = j = k = 0;
  while (i < tgest->total_rank.size)
    {
      m = 0;
      z = tab[k];
      while (i < tgest->total_rank.size
          && m + tgest->zipping.nbbits[i] <= (ba0_int_p) BA0_NBBITS_INT_P)
        {
          d = z & tgest->zipping.mask[i];
          if (d != 0)
            j++;
          m += tgest->zipping.nbbits[i];
          z >>= tgest->zipping.nbbits[i];
          i++;
        }
      k++;
    }
  bav_set_term_one (T);
  bav_realloc_term (T, j);
  i = j = k = 0;
  while (i < tgest->total_rank.size)
    {
      m = 0;
      z = tab[k];
      while (i < tgest->total_rank.size
          && m + tgest->zipping.nbbits[i] <= (ba0_int_p) BA0_NBBITS_INT_P)
        {
          d = z & tgest->zipping.mask[i];
          if (d != 0)
            {
              T->rg[j].var = tgest->total_rank.rg[i].var;
              T->rg[j++].deg = d;
            }
          m += tgest->zipping.nbbits[i];
          z >>= tgest->zipping.nbbits[i];
          i++;
        }
      k++;
    }
  T->size = j;
}

/**************************************************************************
 GARBAGE COLLECTOR
 **************************************************************************/

/* 
   The termanager is inlined in a larger structure.

   --> embedded
*/

/*
* Readonly static data
*/

static char _termanager[] = "struct bap_termanager *->total_rank.rg";
static char _termanager_nbbits[] = "struct bap_termanager *->zipping.nbbits";
static char _termanager_mask[] = "struct bap_termanager *->zipping.mask";

BAP_DLL ba0_int_p
bap_garbage1_termanager (
    void *TT,
    enum ba0_garbage_code code)
{
  struct bap_termanager *T = (struct bap_termanager *) TT;
  ba0_int_p n = 0;

  if (code != ba0_embedded)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (T->total_rank.alloc > 0)
    {
      n += ba0_new_gc_info (T->total_rank.rg,
          sizeof (struct bav_rank) * T->total_rank.alloc, _termanager);

      n += ba0_new_gc_info (T->zipping.nbbits,
          ba0_ceil_align (sizeof (unsigned char) * T->total_rank.alloc),
          _termanager_nbbits);
      n += ba0_new_gc_info (T->zipping.mask,
          sizeof (unsigned ba0_int_p) * T->total_rank.alloc, _termanager_mask);
    }

  return n;
}

/*
   The termanager is inlined in a larger structure.
   The returned value is thus pointless.
*/

BAP_DLL void *
bap_garbage2_termanager (
    void *TT,
    enum ba0_garbage_code code)
{
  struct bap_termanager *T = (struct bap_termanager *) TT;

  if (code != ba0_embedded)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (T->total_rank.alloc > 0)
    {
      T->total_rank.rg =
          (struct bav_rank *) ba0_new_addr_gc_info (T->total_rank.rg,
          _termanager);
      T->zipping.nbbits =
          (unsigned char *) ba0_new_addr_gc_info (T->zipping.nbbits,
          _termanager_nbbits);
      T->zipping.mask =
          (unsigned ba0_int_p *) ba0_new_addr_gc_info (T->zipping.mask,
          _termanager_mask);
    }
  return (void *) 0;
}

/*
 * texinfo: bap_worth_garbage_zipterm_termanager
 * Return @code{true} if the zipterms handled by @var{tgest} are
 * allocated areas, which thus need to be processed by the 
 * garbage collector.
 */

BAP_DLL bool
bap_worth_garbage_zipterm_termanager (
    struct bap_termanager *tgest)
{
  return tgest->zipping.alloc > 1;
}

/*
 * Readonly static data
 */

static char _zipterm[] = "bap_zipterm";

BAP_DLL ba0_int_p
bap_garbage1_zipterm_termanager (
    struct bap_termanager *tgest,
    bap_zipterm key,
    enum ba0_garbage_code code)
{
  ba0_int_p n = 0;

  if (code != ba0_embedded)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  if (tgest->zipping.alloc <= 1)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  n += ba0_new_gc_info ((void *) key, sizeof (ba0_int_p) * tgest->zipping.alloc,
      _zipterm);
  return n;
}

BAP_DLL bap_zipterm
bap_garbage2_zipterm_termanager (
    struct bap_termanager *tgest,
    bap_zipterm key,
    enum ba0_garbage_code code)
{
  if (code != ba0_embedded)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  key = (bap_zipterm) ba0_new_addr_gc_info ((void *) key, _zipterm);
  return key;
}

/*
 * texinfo: bap_switch_ring_termanager
 * Apply @code{bav_switch_ring_term} to the @code{total_rank} field
 * of @var{tgest}.
 */

BAP_DLL void
bap_switch_ring_termanager (
    struct bap_termanager *tgest,
    struct bav_differential_ring *R)
{
  bav_switch_ring_term (&tgest->total_rank, R);
}
