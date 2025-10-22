#include "bap_clot_mpq.h"

#define BAD_FLAG_mpq

/****************************************************************************
 struct bap_table2of_monom_mpq *
 ****************************************************************************/

/*
   Allocate a struct bap_table2of_monom_mpq * with a capacity of at least n monomials.
   Initialize the coefficients.
*/

static struct bap_table2of_monom_mpq *
new_table2of_monom_mpq (
    struct bap_termanager *tgest,
    ba0_int_p n)
{
  struct bap_table2of_monom_mpq *mont;
  ba0_int_p i;

  mont =
      (struct bap_table2of_monom_mpq *) ba0_alloc (sizeof (struct
          bap_table2of_monom_mpq));
  ba0_t2_alloc (sizeof (ba0_mpq_t), sizeof (bap_zipterm), n,
      (void **) &mont->coeff, (void **) &mont->zipterm,
      (unsigned ba0_int_p *) &mont->alloc);
  bap_init_zipterm_array_termanager (tgest, mont->zipterm, mont->alloc);
  mont->size = 0;
  for (i = 0; i < mont->alloc; i++)
    {
      ba0_mpq_init (mont->coeff[i]);
    }
  return mont;
}

/****************************************************************************
 The CLOT
 ****************************************************************************/

static void
check_clot_mpq (
    struct bap_clot_mpq *C)
{
#if defined (BA0_HEAVY_DEBUG)
  ba0_int_p cumul_size, cumul_alloc, i;

  if (C == (struct bap_clot_mpq *) 0)
    return;

  if (C->tab.size > C->tab.alloc || C->size > C->alloc)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (C->size > 0 && C->tab.tab == (struct bap_table2of_monom_mpq * *) 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  cumul_size = 0;
  cumul_alloc = 0;
  for (i = 0; i < C->tab.size; i++)
    {
      if (C->tab.tab[i] == (struct bap_table2of_monom_mpq *) 0)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
      if (i < C->tab.size - 1 && C->tab.tab[i]->size != C->tab.tab[i]->alloc)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
      cumul_size += C->tab.tab[i]->size;
      cumul_alloc += C->tab.tab[i]->alloc;
      if (cumul_size < 0 || cumul_alloc < 0)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
    }

  if (cumul_size != C->size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  while (i < C->tab.alloc
      && C->tab.tab[i] != (struct bap_table2of_monom_mpq *) 0)
    cumul_alloc += C->tab.tab[i++]->alloc;

  if (cumul_alloc != C->alloc)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
#else
  C = (struct bap_clot_mpq *) 0;
#endif
}

static void
init_clot_mpq (
    struct bap_clot_mpq *C,
    struct bav_term *T)
{
  C->alloc = 0;
  C->size = 0;
  bap_init_termanager (&C->tgest, T);
  ba0_init_table ((struct ba0_table *) &C->tab);
  C->ordering = bav_current_ordering ();
}

/*
  Initializes C and stores D in it.
  The sub-arrays of struct bap_table2of_monom_mpq * are shared.
*/

static void
init_set_clot_mpq (
    struct bap_clot_mpq *C,
    struct bap_clot_mpq *D)
{
  C->alloc = D->alloc;
  C->size = D->size;
  bap_init_set_termanager (&C->tgest, &D->tgest);
  C->tab = D->tab;
  C->ordering = D->ordering;
}


/*
 * texinfo: bap_new_clot_mpq
 * Allocate a clot, initialize it and return it.
 * The term @var{T} is supposed to be a multiple of all terms
 * present in the clot.
 */

BAP_DLL struct bap_clot_mpq *
bap_new_clot_mpq (
    struct bav_term *T)
{
  struct bap_clot_mpq *C;

  C = (struct bap_clot_mpq *) ba0_alloc (sizeof (struct bap_clot_mpq));
  init_clot_mpq (C, T);
  return C;
}

/*
 * texinfo: bap_is_zero_clot_mpq
 * Return @code{true} if @var{C} is zero i.e. if @var{C} is empty
 * since monomial coefficients are supposed to be nonzero.
 */

BAP_DLL bool
bap_is_zero_clot_mpq (
    struct bap_clot_mpq *C)
{
  return C->size == 0;
}


/* 
 * texinfo: bap_reverse_clot_mpq
 * Revert the sequence of monomials of @var{C}.
 * This low-level function is used by the few functions which
 * build clot in the (wrong) ascending order.
 */

BAP_DLL void
bap_reverse_clot_mpq (
    struct bap_clot_mpq *C)
{
  struct bap_itermon_clot_mpq I, J;
  ba0_int_p i;
  struct ba0_mark M;

  ba0_record (&M);
  bap_begin_itermon_clot_mpq (&I, C);
  bap_end_itermon_clot_mpq (&J, C);
  for (i = 0; i < C->size / 2; i++)
    {
      bap_swap_itermon_clot_mpq (&I, &J);
      bap_next_itermon_clot_mpq (&I);
      bap_prev_itermon_clot_mpq (&J);
    }
  ba0_restore (&M);
}

/*
 * texinfo: bap_change_ordering_clot_mpq
 * Assign @var{r} to the field @code{ordering} of @var{C}.
 * This low-level function is used by @code{bap_physort_polynom_mpq} only.
 */

BAP_DLL void
bap_change_ordering_clot_mpq (
    struct bap_clot_mpq *C,
    bav_Iordering r)
{
  C->ordering = r;
}

/**********************************************************************
 * ITERATORS OF MONOMIALS OVER A CLOT
 **********************************************************************/

/*
 * texinfo: bap_begin_itermon_clot_mpq
 * Set @var{iter} on the first monomial of @var{clot}.
 * If @var{clot} is empty, @var{iter} is set outside the @var{clot}.
 */

BAP_DLL void
bap_begin_itermon_clot_mpq (
    struct bap_itermon_clot_mpq *iter,
    struct bap_clot_mpq *clot)
{
  check_clot_mpq (clot);
  iter->clot = clot;
  iter->num.primary = 0;
  iter->num.secondary = 0;
  iter->num.combined = 0;
}

/*
 * texinfo: bap_end_itermon_clot_mpq
 * Set @var{iter} on the last monomial of @var{clot}.
 * If @var{clot} is empty, @var{iter} is set outside the @var{clot}.
 */

BAP_DLL void
bap_end_itermon_clot_mpq (
    struct bap_itermon_clot_mpq *iter,
    struct bap_clot_mpq *clot)
{
  check_clot_mpq (clot);
  iter->clot = clot;
  if (bap_is_zero_clot_mpq (clot))
    {
      iter->num.primary = -1;
      iter->num.combined = -1;
    }
  else
    {
      iter->num.primary = clot->tab.size - 1;
      iter->num.secondary = clot->tab.tab[iter->num.primary]->size - 1;
      iter->num.combined = clot->size - 1;
    }
}

/*
 * texinfo: bap_outof_itermon_clot_mpq
 * Return @code{true} if @var{iter} is set outside its clot.
 */

BAP_DLL bool
bap_outof_itermon_clot_mpq (
    struct bap_itermon_clot_mpq *iter)
{
  return iter->num.combined < 0 || iter->num.combined >= iter->clot->size;
}

/*
 * texinfo: bap_next_itermon_clot_mpq
 * Set @var{iter} on the next monomial of its clot.
 * Exception @code{BA0_ERRALG} is raised if @var{iter} was outside
 * its clot before the call.
 */

BAP_DLL void
bap_next_itermon_clot_mpq (
    struct bap_itermon_clot_mpq *iter)
{
  struct bap_table2of_monom_mpq *m;

  if (bap_outof_itermon_clot_mpq (iter))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  m = iter->clot->tab.tab[iter->num.primary];
  if (++iter->num.secondary == m->size)
    {
      iter->num.primary++;
      iter->num.secondary = 0;
    }
  iter->num.combined++;
}

/*
 * texinfo: bap_prev_itermon_clot_mpq
 * Set @var{iter} on the previous monomial of its clot.
 * Exception @code{BA0_ERRALG} is raised if @var{iter} was outside
 * its clot before the call.
 */

BAP_DLL void
bap_prev_itermon_clot_mpq (
    struct bap_itermon_clot_mpq *iter)
{
  struct bap_table2of_monom_mpq *m;

  if (bap_outof_itermon_clot_mpq (iter))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (--iter->num.secondary < 0)
    {
      iter->num.primary--;
      if (iter->num.primary >= 0)
        {
          m = iter->clot->tab.tab[iter->num.primary];
          iter->num.secondary = m->size - 1;
        }
    }
  iter->num.combined--;
}

/*
 * texinfo: bap_number_itermon_clot_mpq
 * Return the number of the current monomial of @var{iter}.
 */

BAP_DLL ba0_int_p
bap_number_itermon_clot_mpq (
    struct bap_itermon_clot_mpq *iter)
{
  return iter->num.combined;
}

/*
 * texinfo: bap_term_itermon_clot_mpq
 * Assign to @var{T} the current term of @var{iter}.
 * Exception @code{BA0_ERRALG} is raised if @var{iter} is outside
 * its clot.
 */

BAP_DLL void
bap_term_itermon_clot_mpq (
    struct bav_term *T,
    struct bap_itermon_clot_mpq *iter)
{
  bap_zipterm c;

  if (bap_outof_itermon_clot_mpq (iter))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  c = iter->clot->tab.tab[iter->num.primary]->zipterm[iter->num.secondary];
  bap_set_term_zipterm_termanager (&iter->clot->tgest, T, c);
}

/*
 * texinfo: bap_coeff_itermon_clot_mpq
 * Return the address of the current coefficient of @var{iter}.
 * Exception @code{BA0_ERRALG} is raised if @var{iter} is outside
 * its clot.
 */

BAP_DLL ba0_mpq_t *
bap_coeff_itermon_clot_mpq (
    struct bap_itermon_clot_mpq *iter)
{
  if (bap_outof_itermon_clot_mpq (iter))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  return &iter->clot->tab.tab[iter->num.primary]->coeff[iter->num.secondary];
}

/*
 * texinfo: bap_swap_itermon_clot_mpq
 * Swap the current monomials of @var{I} and @var{J}.
 * Exception @code{BA0_ERRALG} is raised if @var{I} or @var{J} is 
 * outside its clot.
 */

BAP_DLL void
bap_swap_itermon_clot_mpq (
    struct bap_itermon_clot_mpq *I,
    struct bap_itermon_clot_mpq *J)
{
  struct bap_table2of_monom_mpq *mi, *mj;
  if (bap_outof_itermon_clot_mpq (I) || bap_outof_itermon_clot_mpq (J))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  mi = I->clot->tab.tab[I->num.primary];
  mj = J->clot->tab.tab[J->num.primary];
  BA0_SWAP (bap_zipterm, mi->zipterm[I->num.secondary],
      mj->zipterm[J->num.secondary]);
  ba0_mpq_swap (mi->coeff[I->num.secondary], mj->coeff[J->num.secondary]);
}

/*
 * texinfo: bap_goto_itermon_clot_mpq
 * Set @var{iter} to the monomial number @var{numero} of its clot.
 * Exception @code{BA0_ERRALG} is raised if @var{numero} is not
 * the number of some monomial of the clot.
 */

BAP_DLL void
bap_goto_itermon_clot_mpq (
    struct bap_itermon_clot_mpq *iter,
    ba0_int_p numero)
{
  struct bap_table2of_monom_mpq **tab;
  ba0_int_p primary, secondary;

  if (numero < 0 || numero >= iter->clot->size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  tab = (struct bap_table2of_monom_mpq * *) iter->clot->tab.tab;
  primary = 0;
  secondary = numero;
  while (secondary >= tab[primary]->size)
    {
      secondary -= tab[primary]->size;
      primary++;
    }
  iter->num.combined = numero;
  iter->num.primary = primary;
  iter->num.secondary = secondary;
}

/**********************************************************************
 * CREATORS OF CLOT
 **********************************************************************/

/*
 * texinfo: bap_begin_creator_clot_mpq
 * Set @var{crea} at the beginning of @var{clot}.
 * The term manager of @var{clot} is set to @var{T}, which is
 * a multiple of all terms which are going to be stored in @var{clot}.
 * If some new arrays of type @code{struct bap_table2of_monom_mpq *} are
 * required during the creation process, they will have 
 * @var{table2of_monom_alloc} entries.
 */

BAP_DLL void
bap_begin_creator_clot_mpq (
    struct bap_creator_clot_mpq *crea,
    struct bap_clot_mpq *clot,
    struct bav_term *T,
    ba0_int_p table2of_monom_alloc)
{
  struct bap_table2of_monom_mpq *m;
  ba0_int_p n;
  bool reinit;

  bap_reset_termanager (&clot->tgest, T, &reinit);
  if (reinit)
    {
      for (n = 0; n < clot->tab.size; n++)
        {
          m = clot->tab.tab[n];
          bap_init_zipterm_array_termanager (&clot->tgest, m->zipterm,
              m->alloc);
        }
      for (n = clot->tab.size; n < clot->tab.alloc; n++)
        {
          m = clot->tab.tab[n];
          if (m != 0)
            bap_init_zipterm_array_termanager (&clot->tgest, m->zipterm,
                m->alloc);
        }
    }

  clot->ordering = bav_current_ordering ();

  crea->iter.clot = clot;

  crea->iter.num.combined = 0;
  crea->iter.num.primary = 0;
  crea->iter.num.secondary = 0;

  crea->table2of_monom_alloc = table2of_monom_alloc;
}

/*
 * texinfo: bap_append_creator_clot_mpq
 * Set @var{crea} at the end of @var{clot} so that the newly recorded
 * monomials get appended to @var{clot}.
 * If some new arrays of type @code{struct bap_table2of_monom_mpq *} are
 * required during the creation process, they will have
 * @var{table2of_monom_alloc} entries.
 */

BAP_DLL void
bap_append_creator_clot_mpq (
    struct bap_creator_clot_mpq *crea,
    struct bap_clot_mpq *clot,
    ba0_int_p table2of_monom_alloc)
{
  struct bap_table2of_monom_mpq *m;

  check_clot_mpq (clot);

  crea->iter.clot = clot;
  crea->iter.num.combined = clot->size;

  if (bap_is_zero_clot_mpq (clot))
    {
      crea->iter.num.primary = 0;
      crea->iter.num.secondary = 0;
    }
  else
    {
      crea->iter.num.primary = clot->tab.size - 1;
      m = clot->tab.tab[crea->iter.num.primary];
      crea->iter.num.secondary = m->size;
      if (crea->iter.num.secondary == m->alloc)
        {
          crea->iter.num.primary++;
          crea->iter.num.secondary = 0;
        }
    }
  crea->table2of_monom_alloc = table2of_monom_alloc;
}

/*
  Returns the struct bap_table2of_monom_mpq * crea points to.
  Allocates a struct bap_table2of_monom_mpq * if there is no place left.
  If as many used monomials as allocated monomials
     one needs to allocate a new mont_mpq
     Now, if tab.tab is full then it must be
        resized before allocating the mont_mpq.
  else
     there is no need to allocated a new mont_mpq
     it may be useful to move to the next mont_mpq.
*/

static struct bap_table2of_monom_mpq *
mont_address_creator_clot_mpq (
    struct bap_creator_clot_mpq *crea)
{
  struct bap_clot_mpq *clot;
  struct bap_table2of_monom_mpq *mont;

  clot = crea->iter.clot;

  if (clot->alloc == crea->iter.num.combined)
    {
      if (clot->tab.alloc == crea->iter.num.primary)
        {
          struct bap_table2of_monom_mpq **new_tab;
          ba0_int_p n, new_alloc;

          new_alloc = 2 * clot->tab.alloc + 1;
          new_tab =
              (struct bap_table2of_monom_mpq * *) ba0_alloc (sizeof (void *) *
              new_alloc);
          memcpy (new_tab, clot->tab.tab,
              clot->tab.alloc * sizeof (struct bap_table2of_monom_mpq *));
          for (n = clot->tab.alloc; n < new_alloc; n++)
            new_tab[n] = (struct bap_table2of_monom_mpq *) 0;
          clot->tab.alloc = new_alloc;
          clot->tab.tab = (struct bap_table2of_monom_mpq * *) new_tab;
        }
      mont =
          new_table2of_monom_mpq (&clot->tgest, crea->table2of_monom_alloc);
      clot->tab.tab[crea->iter.num.primary] = mont;
      clot->alloc += mont->alloc;
    }
  else
    mont = clot->tab.tab[crea->iter.num.primary];

  return mont;
}

/*
   There is a slight difference with bap_next_itermon_clot_mpq (comparison
   with alloc instead of size though it amounts to the same). There is no
   overflow test.
*/

static void
next_creator_clot_mpq (
    struct bap_creator_clot_mpq *crea)
{
  struct bap_table2of_monom_mpq *mont;

  mont = crea->iter.clot->tab.tab[crea->iter.num.primary];
  if (++crea->iter.num.secondary == mont->alloc)
    {
      crea->iter.num.primary++;
      crea->iter.num.secondary = 0;
    }
  crea->iter.num.combined++;
}

/*
 * texinfo: bap_write_creator_clot_mpq
 * Write the monomial @math{c\,T} in the clot processed by @var{crea}.
 * The coefficient @var{c} is allowed to be zero (then nothing is done).
 * The creator then moves to the next available monomial entry.
 */

BAP_DLL void
bap_write_creator_clot_mpq (
    struct bap_creator_clot_mpq *crea,
    struct bav_term *T,
    ba0_mpq_t c)
{
  struct bap_table2of_monom_mpq *mont;

  if (ba0_mpq_is_zero (c))
    return;

  mont = mont_address_creator_clot_mpq (crea);

  bap_set_zipterm_term_termanager (&crea->iter.clot->tgest,
      &mont->zipterm[crea->iter.num.secondary], T);
  ba0_mpq_set (mont->coeff[crea->iter.num.secondary], c);

  next_creator_clot_mpq (crea);
}

/*
 * texinfo: bap_write_neg_creator_clot_mpq
 * Write the monomial @math{-c\,T} in the clot processed by @var{crea}.
 * The coefficient @var{c} is allowed to be zero (then nothing is done).
 * The creator then moves to the next available monomial entry.
 */

BAP_DLL void
bap_write_neg_creator_clot_mpq (
    struct bap_creator_clot_mpq *crea,
    struct bav_term *T,
    ba0_mpq_t c)
{
  struct bap_table2of_monom_mpq *mont;

  if (ba0_mpq_is_zero (c))
    return;

  mont = mont_address_creator_clot_mpq (crea);

  bap_set_zipterm_term_termanager (&crea->iter.clot->tgest,
      &mont->zipterm[crea->iter.num.secondary], T);
  ba0_mpq_neg (mont->coeff[crea->iter.num.secondary], c);

  next_creator_clot_mpq (crea);
}

/*
 * texinfo: bap_write_term_creator_clot_mpq
 * Assign @var{T} to the current term of the clot processed by @var{crea}.
 * The coefficient is left unchanged.
 * The creator then moves to the next available monomial entry.
 */

BAP_DLL void
bap_write_term_creator_clot_mpq (
    struct bap_creator_clot_mpq *crea,
    struct bav_term *T)
{
  struct bap_table2of_monom_mpq *mont;

  mont = mont_address_creator_clot_mpq (crea);
  bap_set_zipterm_term_termanager (&crea->iter.clot->tgest,
      &mont->zipterm[crea->iter.num.secondary], T);
  next_creator_clot_mpq (crea);
}

/*
 * texinfo: bap_write_all_creator_clot_mpq
 * Write on the clot processed by @var{crea} all the monomials
 * of @var{clot} which have numbers in the range @math{l \leq n < r}.
 */

BAP_DLL void
bap_write_all_creator_clot_mpq (
    struct bap_creator_clot_mpq *crea,
    struct bap_clot_mpq *clot,
    ba0_int_p l,
    ba0_int_p r)
{
  struct bap_itermon_clot_mpq iter;
  struct bap_table2of_monom_mpq *d_mont, *s_mont;
  bap_zipterm *d_clef, s_clef;
  ba0_int_p i;

  if (l == r)
    return;

  bap_begin_itermon_clot_mpq (&iter, clot);
  bap_goto_itermon_clot_mpq (&iter, l);

  for (i = l; i < r; i++)
    {
      s_mont = iter.clot->tab.tab[iter.num.primary];
      s_clef = s_mont->zipterm[iter.num.secondary];
      d_mont = mont_address_creator_clot_mpq (crea);
      d_clef = &d_mont->zipterm[crea->iter.num.secondary];
      bap_set_zipterm_zipterm_termanager (&crea->iter.clot->tgest, d_clef,
          &iter.clot->tgest, s_clef);
      ba0_mpq_set (d_mont->coeff[crea->iter.num.secondary],
          s_mont->coeff[iter.num.secondary]);
      bap_next_itermon_clot_mpq (&iter);
      next_creator_clot_mpq (crea);
    }
}

/* 
 * texinfo: bap_write_neg_all_creator_clot_mpq
 * Write on the clot processed by @var{crea} the opposite of all the monomials
 * of @var{clot} which have numbers in the range @math{l \leq n < r}
 * (the signs of the coefficients are changed).
 */


BAP_DLL void
bap_write_neg_all_creator_clot_mpq (
    struct bap_creator_clot_mpq *crea,
    struct bap_clot_mpq *clot,
    ba0_int_p l,
    ba0_int_p r)
{
  struct bap_itermon_clot_mpq iter;
  struct bap_table2of_monom_mpq *d_mont, *s_mont;
  bap_zipterm *d_clef, s_clef;
  ba0_int_p i;

  if (l == r)
    return;

  bap_begin_itermon_clot_mpq (&iter, clot);
  bap_goto_itermon_clot_mpq (&iter, l);

  for (i = l; i < r; i++)
    {
      s_mont = iter.clot->tab.tab[iter.num.primary];
      s_clef = s_mont->zipterm[iter.num.secondary];
      d_mont = mont_address_creator_clot_mpq (crea);
      d_clef = &d_mont->zipterm[crea->iter.num.secondary];
      bap_set_zipterm_zipterm_termanager (&crea->iter.clot->tgest, d_clef,
          &iter.clot->tgest, s_clef);
      ba0_mpq_neg (d_mont->coeff[crea->iter.num.secondary],
          s_mont->coeff[iter.num.secondary]);
      bap_next_itermon_clot_mpq (&iter);
      next_creator_clot_mpq (crea);
    }
}

/*
 * texinfo: bap_write_mul_all_creator_clot_mpq
 * Write on the clot processed by @var{crea} all the monomials
 * of @var{clot} which have numbers in the range @math{l \leq n < r}
 * multiplied by @var{c}.
 * If @var{c} is zero, nothing is done.
 */

BAP_DLL void
bap_write_mul_all_creator_clot_mpq (
    struct bap_creator_clot_mpq *crea,
    struct bap_clot_mpq *clot,
    ba0_mpq_t c,
    ba0_int_p l,
    ba0_int_p r)
{
  struct bap_itermon_clot_mpq iter;
  struct bap_table2of_monom_mpq *d_mont, *s_mont;
  bap_zipterm *d_clef, s_clef;
  ba0_int_p i;

  if (l == r || ba0_mpq_is_zero (c))
    return;

  bap_begin_itermon_clot_mpq (&iter, clot);
  bap_goto_itermon_clot_mpq (&iter, l);

  for (i = l; i < r; i++)
    {
      s_mont = iter.clot->tab.tab[iter.num.primary];
      s_clef = s_mont->zipterm[iter.num.secondary];
      d_mont = mont_address_creator_clot_mpq (crea);
      d_clef = &d_mont->zipterm[crea->iter.num.secondary];
      bap_set_zipterm_zipterm_termanager (&crea->iter.clot->tgest, d_clef,
          &iter.clot->tgest, s_clef);
      ba0_mpq_mul (d_mont->coeff[crea->iter.num.secondary],
          s_mont->coeff[iter.num.secondary], c);
      if (ba0_mpq_is_zero (d_mont->coeff[crea->iter.num.secondary]))
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
      bap_next_itermon_clot_mpq (&iter);
      next_creator_clot_mpq (crea);
    }
}

#if defined (BAD_FLAG_mpz)

/*
 * texinfo: bap_write_mul_all_creator_clot_mpz
 * This function only applies to the case of @code{mpz_t{ coefficients.
 * Write on the clot processed by @var{crea} all the monomials
 * of @var{clot} which have numbers in the range @math{l \leq n < r}
 * divided by @var{c}.
 * The integer @var{c} is supposed to divide exactly each coefficient.
 */

BAP_DLL void
bap_write_exquo_all_creator_clot_mpz (
    struct bap_creator_clot_mpz *crea,
    struct bap_clot_mpz *clot,
    ba0_mpz_t c,
    ba0_int_p l,
    ba0_int_p r)
{
  struct bap_itermon_clot_mpq iter;
  struct bap_table2of_monom_mpq *d_mont, *s_mont;
  bap_zipterm *d_clef, s_clef;
  ba0_int_p i;

  if (l == r || ba0_mpq_is_one (c))
    return;

  bap_begin_itermon_clot_mpq (&iter, clot);
  bap_goto_itermon_clot_mpq (&iter, l);

  for (i = l; i < r; i++)
    {
      s_mont = iter.clot->tab.tab[iter.num.primary];
      s_clef = s_mont->zipterm[iter.num.secondary];
      d_mont = mont_address_creator_clot_mpq (crea);
      d_clef = &d_mont->zipterm[crea->iter.num.secondary];
      bap_set_zipterm_zipterm_termanager (&crea->iter.clot->tgest, d_clef,
          &iter.clot->tgest, s_clef);
      ba0_mpz_divexact (d_mont->coeff[crea->iter.num.secondary],
          s_mont->coeff[iter.num.secondary], c);
      bap_next_itermon_clot_mpq (&iter);
      next_creator_clot_mpq (crea);
    }
}
#endif

/*
 * texinfo: bap_close_creator_clot_mpq
 * Achieve the creation process. 
 * The resulting clot is not necessarily sorted.
 */

BAP_DLL void
bap_close_creator_clot_mpq (
    struct bap_creator_clot_mpq *crea)
{
  struct bap_clot_mpq *clot;
  struct bap_table2of_monom_mpq *m;
  ba0_int_p i;

  clot = crea->iter.clot;

  clot->size = crea->iter.num.combined;

  for (i = 0; i < crea->iter.num.primary; i++)
    {
      m = clot->tab.tab[i];
      m->size = m->alloc;
    }

  if (crea->iter.num.secondary != 0)
    {
      m = clot->tab.tab[crea->iter.num.primary];
      m->size = crea->iter.num.secondary;
      clot->tab.size = crea->iter.num.primary + 1;
    }
  else
    clot->tab.size = crea->iter.num.primary;

  for (i = clot->tab.size; i < clot->tab.alloc; i++)
    {
      m = clot->tab.tab[i];
      if (m != (struct bap_table2of_monom_mpq *) 0)
        m->size = 0;
    }
  check_clot_mpq (clot);
}

/*
 * Moves the creator to the monomial with number {\em numero}.
 * No allocation is performed. It is assumed that the monomial exists.
 */

BAP_DLL void
bap_goto_creator_clot_mpq (
    struct bap_creator_clot_mpq *crea,
    ba0_int_p numero)
{
  bap_goto_itermon_clot_mpq (&crea->iter, numero);
}

/****************************************************************************
 * BAP_SORT_CLOT
 ****************************************************************************/

/*
 * Type declaration used for a local variable of quicksort.
 */

struct quicksort_data
{
  struct bap_itermon_clot_mpq l;
  struct bap_itermon_clot_mpq r;
  struct bap_itermon_clot_mpq i;
  struct bap_itermon_clot_mpq j;
  struct bap_itermon_clot_mpq k;
  struct bav_term Tl;
  struct bav_term Tr;
  struct bav_term Ti;
  struct bav_term Tj;
  struct bav_term Tk;
  struct bav_term pivot;
  unsigned ba0_int_p zi;
  unsigned ba0_int_p zj;
  unsigned ba0_int_p zk;
};

static void
bap_init_quicksort_data_mpq (
    struct quicksort_data *qs,
    struct bap_clot_mpq *clot)
{
  bap_begin_itermon_clot_mpq (&qs->l, clot);
  bap_begin_itermon_clot_mpq (&qs->r, clot);
  bap_begin_itermon_clot_mpq (&qs->i, clot);
  bap_begin_itermon_clot_mpq (&qs->j, clot);
  bap_begin_itermon_clot_mpq (&qs->k, clot);
  bav_init_term (&qs->Tl);
  bav_init_term (&qs->Tr);
  bav_init_term (&qs->Ti);
  bav_init_term (&qs->Tj);
  bav_init_term (&qs->Tk);
  bav_init_term (&qs->pivot);
  qs->zi = qs->zj = qs->zk = 0;
}

static void
quicksort_clot_mpq (
    ba0_int_p l,
    ba0_int_p r,
    struct quicksort_data *qs)
{
  ba0_int_p i, j, k;
  enum ba0_compare_code code;
/*
 * Readonly static data structure
 */
  static ba0_int_p alpha[] = { 1, 2, 2, 3, 4, 1, 3 };
/*
 * -  -  -  -  -  -  -         
 */
  static ba0_int_p beta[] = { 1, 3, 1, 4, 3, 2, 2 };

  if (r - l > 8)
    {
      i = (alpha[qs->zi] * (l + 2) + beta[qs->zi] * (r - 2)) / (alpha[qs->zi] +
          beta[qs->zi]);
      qs->zi = (qs->zi + 1) % 7;
      j = (alpha[qs->zj] * (l + 1) + beta[qs->zj] * (i - 1)) / (alpha[qs->zj] +
          beta[qs->zj]);
      qs->zj = (qs->zj + 3) % 7;
      k = (alpha[qs->zk] * (i + 1) + beta[qs->zk] * (r - 1)) / (alpha[qs->zk] +
          beta[qs->zk]);
      qs->zk = (qs->zk + 5) % 7;
      if (i == j || i == k || j == k)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
      bap_goto_itermon_clot_mpq (&qs->l, l);
      bap_term_itermon_clot_mpq (&qs->Tl, &qs->l);
      bap_goto_itermon_clot_mpq (&qs->r, r);
      bap_term_itermon_clot_mpq (&qs->Tr, &qs->r);
      bap_goto_itermon_clot_mpq (&qs->i, i);
      bap_term_itermon_clot_mpq (&qs->Ti, &qs->i);
      bap_goto_itermon_clot_mpq (&qs->j, j);
      bap_term_itermon_clot_mpq (&qs->Tj, &qs->j);
      bap_goto_itermon_clot_mpq (&qs->k, k);
      bap_term_itermon_clot_mpq (&qs->Tk, &qs->k);
/*
   On souhaite que le pivot soit le median de T [i], T [j], T [k].
   On doit echanger T [l] avec le median et T [r] avec le max.
*/
      code = bav_compare_term (&qs->Ti, &qs->Tj);
      if (code == ba0_gt)
        {
          code = bav_compare_term (&qs->Tj, &qs->Tk);
          if (code == ba0_gt)
            {
              bap_swap_itermon_clot_mpq (&qs->l, &qs->j);
              bap_swap_itermon_clot_mpq (&qs->r, &qs->i);
/* T [i] > T [j] > T [k] */
              bav_set_term (&qs->pivot, &qs->Tj);
            }
          else
            {
              code = bav_compare_term (&qs->Ti, &qs->Tk);
              if (code == ba0_gt)
                {
                  bap_swap_itermon_clot_mpq (&qs->l, &qs->k);
                  bap_swap_itermon_clot_mpq (&qs->r, &qs->i);
/* T [i] > T [k] > T [j] */
                  bav_set_term (&qs->pivot, &qs->Tk);
                }
              else
                {
                  bap_swap_itermon_clot_mpq (&qs->l, &qs->i);
                  bap_swap_itermon_clot_mpq (&qs->r, &qs->k);
/* T [k] > T [i] > T [j] */
                  bav_set_term (&qs->pivot, &qs->Ti);
                }
            }
        }
      else
        {
          code = bav_compare_term (&qs->Tk, &qs->Tj);
          if (code == ba0_gt)
            {
              bap_swap_itermon_clot_mpq (&qs->l, &qs->j);
              bap_swap_itermon_clot_mpq (&qs->r, &qs->k);
/* T [k] > T [j] > T [i] */
              bav_set_term (&qs->pivot, &qs->Tj);
            }
          else
            {
              code = bav_compare_term (&qs->Tk, &qs->Ti);
              if (code == ba0_gt)
                {
                  bap_swap_itermon_clot_mpq (&qs->l, &qs->k);
                  bap_swap_itermon_clot_mpq (&qs->r, &qs->j);
/* T [j] > T [k] > T [i] */
                  bav_set_term (&qs->pivot, &qs->Tk);
                }
              else
                {
                  bap_swap_itermon_clot_mpq (&qs->l, &qs->i);
                  bap_swap_itermon_clot_mpq (&qs->r, &qs->j);
/* T [j] > T [i] > T [k] */
                  bav_set_term (&qs->pivot, &qs->Ti);
                }
            }
        }
/*
   Invariants (sauf avant le 1er tour).
   i, j in [l, r]
   T [i] < pivot (sauf 1er tour ou on a egalite)
   T [j] > pivot
   Les T [k < i] sont > pivot
   Les T [k > j] sont < pivot
*/
      i = l;
      j = r;
      qs->i = qs->l;
      qs->j = qs->r;
      do
        {
          bap_swap_itermon_clot_mpq (&qs->i, &qs->j);
          do
            {
              i += 1;
              bap_next_itermon_clot_mpq (&qs->i);
              bap_term_itermon_clot_mpq (&qs->Ti, &qs->i);
              code = bav_compare_term (&qs->Ti, &qs->pivot);
            }
          while (code == ba0_gt);
          do
            {
              j -= 1;
              bap_prev_itermon_clot_mpq (&qs->j);
              bap_term_itermon_clot_mpq (&qs->Tj, &qs->j);
              code = bav_compare_term (&qs->Tj, &qs->pivot);
            }
          while (code == ba0_lt);
        }
      while (i < j);
      bap_swap_itermon_clot_mpq (&qs->i, &qs->r);
      quicksort_clot_mpq (l, i - 1, qs);
      quicksort_clot_mpq (i + 1, r, qs);
    }
  else
    {
      bool sorted;
      struct bav_term *cour, *suiv;

      sorted = false;
      cour = &qs->Ti;
      suiv = &qs->Tj;
      for (i = r - 1; !sorted && i >= l; i--)
        {
          sorted = true;
          bap_goto_itermon_clot_mpq (&qs->i, l);
          bap_term_itermon_clot_mpq (cour, &qs->i);
          bap_goto_itermon_clot_mpq (&qs->j, l + 1);
          bap_term_itermon_clot_mpq (suiv, &qs->j);
          code = bav_compare_term (cour, suiv);
          if (code == ba0_lt)
            {
              BA0_SWAP (struct bav_term *,
                  cour,
                  suiv);
              bap_swap_itermon_clot_mpq (&qs->i, &qs->j);
              sorted = false;
            }
          for (j = l + 1; j <= i; j++)
            {
              qs->i = qs->j;
              bap_next_itermon_clot_mpq (&qs->j);
              BA0_SWAP (struct bav_term *,
                  cour,
                  suiv);
              bap_term_itermon_clot_mpq (suiv, &qs->j);
              code = bav_compare_term (cour, suiv);
              if (code == ba0_lt)
                {
                  BA0_SWAP (struct bav_term *,
                      cour,
                      suiv);
                  bap_swap_itermon_clot_mpq (&qs->i, &qs->j);
                  sorted = false;
                }
            }
        }
    }
}

/*
 * texinfo: bap_sort_clot_mpq
 * Sorts the sequence of monomials of @var{clot} which have
 * numbers @math{l \leq n < r} by decreasing order, according
 * to the lexicographic ordering induced by the ordering.
 * This low-level function is used by @code{bap_physort_polynom_mpq}.
 */


BAP_DLL void
bap_sort_clot_mpq (
    struct bap_clot_mpq *clot,
    ba0_int_p l,
    ba0_int_p r)
{
  struct bap_clot_mpq old_clot;
  struct bap_creator_clot_mpq crea;
  struct bap_itermon_clot_mpq iter;
  struct quicksort_data qs;
  struct bav_term T;
  ba0_int_p i;
  struct ba0_mark M;

  if (l >= r)
    return;

  ba0_record (&M);

  init_set_clot_mpq (&old_clot, clot);
  bap_begin_itermon_clot_mpq (&iter, &old_clot);
  bap_goto_itermon_clot_mpq (&iter, l);

  bav_init_term (&T);
  bav_set_term (&T, &clot->tgest.total_rank);
  bav_sort_term (&T);
  bap_begin_creator_clot_mpq (&crea, clot, &T, 0);

  bap_goto_creator_clot_mpq (&crea, l);

  for (i = l; i < r; i++)
    {
      bap_term_itermon_clot_mpq (&T, &iter);
      bav_sort_term (&T);
      bap_write_term_creator_clot_mpq (&crea, &T);
      bap_next_itermon_clot_mpq (&iter);
    }

  bap_init_quicksort_data_mpq (&qs, clot);
  quicksort_clot_mpq (l, r - 1, &qs);
  ba0_restore (&M);
}

/****************************************************************************
 GARBAGE COLLECTOR AND RELATED FUNCTIONS
 ****************************************************************************/

/*
 * Readonly static data
 */

static char _struct_mont[] = "struct bap_table2of_monom_mpq";
static char _struct_table2of_monom_zipterm[] =
    "struct bap_table2of_monom_mpq *->zipterm";
static char _struct_table2of_monom_coeff[] =
    "struct bap_table2of_monom_mpq *->coeff";

static ba0_int_p
garbage1_table2of_monom_mpq (
    struct bap_termanager *tgest,
    struct bap_table2of_monom_mpq *A,
    enum ba0_garbage_code code)
{
  ba0_int_p n = 0;

  if (A == (struct bap_table2of_monom_mpq *) 0)
    return 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (A, sizeof (struct bap_table2of_monom_mpq),
        _struct_mont);
  n += ba0_new_gc_info (A->zipterm, sizeof (bap_zipterm) * A->alloc,
      _struct_table2of_monom_zipterm);
  n += ba0_new_gc_info (A->coeff, sizeof (ba0_mpq_t) * A->alloc,
      _struct_table2of_monom_coeff);
  if (bap_worth_garbage_zipterm_termanager (tgest))
    {
      ba0_int_p i;
      for (i = 0; i < A->alloc; i++)
        n += bap_garbage1_zipterm_termanager (tgest, A->zipterm[i],
            ba0_embedded);
    }

#if ! defined (BAD_FLAG_mint_hp)
  {
    ba0_int_p i;
    for (i = 0; i < A->alloc; i++)
      n += ba0_garbage1_mpq (&A->coeff[i], ba0_embedded);
  }
#endif
  return n;
}

/*
 * Readonly static data
 */

static char _struct_clot[] = "struct bap_clot_mpq";
static char _struct_clot_tab[] = "struct bap_clot_mpq *->tab.tab";

BAP_DLL ba0_int_p
bap_garbage1_clot_mpq (
    void *AA,
    enum ba0_garbage_code code)
{
  struct bap_clot_mpq *A = (struct bap_clot_mpq *) AA;
  ba0_int_p i, n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (A, sizeof (struct bap_clot_mpq), _struct_clot);

  if (A->tab.tab)
    n += ba0_new_gc_info (A->tab.tab,
        sizeof (struct bap_table2of_monom_mpq *) * A->tab.alloc,
        _struct_clot_tab);

  n += bap_garbage1_termanager (&A->tgest, ba0_embedded);

  for (i = 0; i < A->tab.alloc; i++)
    n += garbage1_table2of_monom_mpq (&A->tgest, A->tab.tab[i], ba0_isolated);

  return n;
}

static struct bap_table2of_monom_mpq *
garbage2_table2of_monom_mpq (
    struct bap_termanager *tgest,
    struct bap_table2of_monom_mpq *A,
    enum ba0_garbage_code code)
{

  if (A == (struct bap_table2of_monom_mpq *) 0)
    return A;

  if (code == ba0_isolated)
    A = (struct bap_table2of_monom_mpq *) ba0_new_addr_gc_info (A,
        _struct_mont);

  A->zipterm =
      (bap_zipterm *) ba0_new_addr_gc_info (A->zipterm,
      _struct_table2of_monom_zipterm);

  A->coeff =
      (ba0_mpq_t *) ba0_new_addr_gc_info (A->coeff, _struct_table2of_monom_coeff);

  if (bap_worth_garbage_zipterm_termanager (tgest))
    {
      ba0_int_p i;
      for (i = 0; i < A->alloc; i++)
        A->zipterm[i] =
            bap_garbage2_zipterm_termanager (tgest, A->zipterm[i],
            ba0_embedded);
    }

#if ! defined (BAD_FLAG_mint_hp)
  {
    ba0_int_p i;
    for (i = 0; i < A->alloc; i++)
      ba0_garbage2_mpq (&A->coeff[i], ba0_embedded);
  }
#endif
  return A;
}

BAP_DLL void *
bap_garbage2_clot_mpq (
    void *AA,
    enum ba0_garbage_code code)
{
  struct bap_clot_mpq *A;
  ba0_int_p i;

  if (code == ba0_isolated)
    A = (struct bap_clot_mpq *) ba0_new_addr_gc_info (AA, _struct_clot);
  else
    A = (struct bap_clot_mpq *) AA;

  if (A->tab.tab)
    A->tab.tab =
        (struct bap_table2of_monom_mpq * *) ba0_new_addr_gc_info (A->tab.tab,
        _struct_clot_tab);

  bap_garbage2_termanager (&A->tgest, ba0_embedded);

  for (i = 0; i < A->tab.alloc; i++)
    A->tab.tab[i] =
        garbage2_table2of_monom_mpq (&A->tgest, A->tab.tab[i], ba0_isolated);

  return A;
}

BAP_DLL void
bap_switch_ring_clot_mpq (
    struct bap_clot_mpq *clot,
    struct bav_differential_ring *R)
{
  bap_switch_ring_termanager (&clot->tgest, R);
}

#undef BAD_FLAG_mpq
