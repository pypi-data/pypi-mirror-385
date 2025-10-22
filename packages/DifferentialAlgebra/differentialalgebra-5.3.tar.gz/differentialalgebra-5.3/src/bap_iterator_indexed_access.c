#include "bap_iterator_indexed_access.h"

/*
 * texinfo: bap_begin_iterator_indexed_access
 * Set @var{iter} on the first entry of @var{ind}.
 */

BAP_DLL void
bap_begin_iterator_indexed_access (
    struct bap_iterator_indexed_access *iter,
    struct bap_indexed_access *ind)
{
  iter->ind = ind;
  iter->num.primary = 0;
  iter->num.secondary = 0;
  iter->num.combined = 0;
}

/*
 * texinfo: bap_end_iterator_indexed_access
 * Set @var{iter} on the last entry of @var{ind}.
 */

BAP_DLL void
bap_end_iterator_indexed_access (
    struct bap_iterator_indexed_access *iter,
    struct bap_indexed_access *ind)
{
  struct ba0_tableof_int_p *tab;

  iter->ind = ind;
  iter->num.primary = ind->tab.size - 1;
  tab = ind->tab.tab[iter->num.primary];
  iter->num.secondary = tab->size - 1;
  iter->num.combined = ind->size - 1;
}

/*
 * texinfo: bap_outof_iterator_indexed_access
 * Return @code{true} if @var{iter} is outside its @code{ind} field.
 */

BAP_DLL bool
bap_outof_iterator_indexed_access (
    struct bap_iterator_indexed_access *iter)
{
  return iter->num.combined < 0 || iter->num.combined >= iter->ind->size;
}

/*
 * texinfo: bap_next_iterator_indexed_access
 * Move @var{iter} to the next entry.
 * Exception @code{BA0_ERRALG} is raised if @var{iter} is outside 
 * its @code{ind} field before the call.
 */

BAP_DLL void
bap_next_iterator_indexed_access (
    struct bap_iterator_indexed_access *iter)
{
  struct ba0_tableof_int_p *tab;

  if (bap_outof_iterator_indexed_access (iter))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  tab = iter->ind->tab.tab[iter->num.primary];
  if (++iter->num.secondary >= tab->alloc)
    {
      iter->num.primary++;
      iter->num.secondary = 0;
    }
  iter->num.combined++;
}

/*
 * texinfo: bap_prev_iterator_indexed_access
 * Move @var{iter} to the previous entry.
 * Exception @code{BA0_ERRALG} is raised if @var{iter} is outside 
 * its @code{ind} field before the call.
 */

BAP_DLL void
bap_prev_iterator_indexed_access (
    struct bap_iterator_indexed_access *iter)
{
  struct ba0_tableof_int_p *tab;

  if (bap_outof_iterator_indexed_access (iter))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (--iter->num.secondary < 0)
    {
      iter->num.primary--;
      if (iter->num.primary >= 0)
        {
          tab = iter->ind->tab.tab[iter->num.primary];
          iter->num.secondary = tab->alloc - 1;
        }
    }
  iter->num.combined--;
}

/*
 * texinfo: bap_goto_iterator_indexed_access
 * Move @var{iter} to the @var{n}th entry.
 * Exception @code{BA0_ERRALG} is raised if @var{n} is not a
 * valid entry number.
 */

BAP_DLL void
bap_goto_iterator_indexed_access (
    struct bap_iterator_indexed_access *iter,
    ba0_int_p n)
{
  struct ba0_tableof_int_p **tab;
  ba0_int_p i, j;

  if (n < 0 || n >= iter->ind->size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  tab = iter->ind->tab.tab;
  for (i = 0, j = n; j >= tab[i]->size; i++)
    j -= tab[i]->size;
  iter->num.combined = n;
  iter->num.primary = i;
  iter->num.secondary = j;
}

/*
 * texinfo: bap_index_iterator_indexed_access
 * Return the current index.
 * Exception @code{BA0_ERRALG} is raised if @var{iter} is outside 
 * its @code{ind} field before the call.
 */

BAP_DLL ba0_int_p
bap_index_iterator_indexed_access (
    struct bap_iterator_indexed_access *iter)
{
  struct ba0_tableof_int_p *tab;

  if (bap_outof_iterator_indexed_access (iter))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  tab = iter->ind->tab.tab[iter->num.primary];
  return tab->tab[iter->num.secondary];
}

/*
 * texinfo: bap_read_iterator_indexed_access
 * Return the current index then move @var{iter} to the next entry.
 */

BAP_DLL ba0_int_p
bap_read_iterator_indexed_access (
    struct bap_iterator_indexed_access *iter)
{
  ba0_int_p index;

  index = bap_index_iterator_indexed_access (iter);
  bap_next_iterator_indexed_access (iter);
  return index;
}

/*
 * texinfo: bap_swapindex_iterator_indexed_access
 * Swap the current indices of @var{I} and @var{J}.
 * Exception @code{BA0_ERRALG} is raised if any of the iterators
 * is outside its @code{ind} field.
 */

BAP_DLL void
bap_swapindex_iterator_indexed_access (
    struct bap_iterator_indexed_access *I,
    struct bap_iterator_indexed_access *J)
{
  struct ba0_tableof_int_p *ti, *tj;

  if (bap_outof_iterator_indexed_access (I)
      || bap_outof_iterator_indexed_access (J))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  ti = I->ind->tab.tab[I->num.primary];
  tj = J->ind->tab.tab[J->num.primary];
  BA0_SWAP (ba0_int_p, ti->tab[I->num.secondary], tj->tab[J->num.secondary]);
}

/*
 * texinfo: bap_set_iterator_indexed_access
 * Assign @var{J} to @var{I}.
 */

BAP_DLL void
bap_set_iterator_indexed_access (
    struct bap_iterator_indexed_access *I,
    struct bap_iterator_indexed_access *J)
{
  *I = *J;
}

/*
 * texinfo: bap_begin_creator_indexed_access
 * Set @var{crea} at the beginning of @var{ind}.
 */

BAP_DLL void
bap_begin_creator_indexed_access (
    struct bap_creator_indexed_access *crea,
    struct bap_indexed_access *ind)
{
  crea->ind = ind;
  crea->num.primary = 0;
  crea->num.secondary = 0;
  crea->num.combined = 0;
}

/*
 * texinfo: bap_write_creator_indexed_access
 * Assign @var{n} to the current index of @var{crea}.
 * Move @var{crea} to the next available entry of its @code{ind} field.
 */

BAP_DLL void
bap_write_creator_indexed_access (
    struct bap_creator_indexed_access *crea,
    ba0_int_p n)
{
  struct ba0_tableof_int_p *tab;

  if (crea->num.combined >= crea->ind->alloc)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  tab = crea->ind->tab.tab[crea->num.primary];
  tab->tab[crea->num.secondary++] = n;
  if (crea->num.secondary == tab->alloc)
    {
      crea->num.primary++;
      crea->num.secondary = 0;
    }
  crea->num.combined++;
}

/*
 * texinfo: bap_close_creator_indexed_access
 * Complete the creation process.
 */

BAP_DLL void
bap_close_creator_indexed_access (
    struct bap_creator_indexed_access *crea)
{
  struct ba0_tableof_int_p *tab;
  ba0_int_p i;

  for (i = 0; i < crea->num.primary; i++)
    {
      tab = crea->ind->tab.tab[i];
      tab->size = tab->alloc;
    }
  if (crea->num.secondary != 0)
    {
      tab = crea->ind->tab.tab[crea->num.primary];
      tab->size = crea->num.secondary;
      crea->ind->tab.size = crea->num.primary + 1;
    }
  else
    crea->ind->tab.size = crea->num.primary;
  for (i = crea->ind->tab.size; i < crea->ind->tab.alloc; i++)
    {
      tab = crea->ind->tab.tab[i];
      tab->size = 0;
    }
  crea->ind->size = crea->num.combined;
}
