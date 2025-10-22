#include "bap_indexed_access.h"
#include "bap_iterator_indexed_access.h"

/*
 * texinfo: bap_init_indexed_access
 * Initialize @var{ind}.
 */

BAP_DLL void
bap_init_indexed_access (
    struct bap_indexed_access *ind)
{
  ind->alloc = 0;
  ind->size = 0;
  ba0_init_table ((struct ba0_table *) &ind->tab);
}

/*
 * texinfo: bap_realloc_indexed_access
 * Reallocate the field @code{tab} if @var{ind} so that it
 * can receive @var{nbmon} entries.
 */

BAP_DLL void
bap_realloc_indexed_access (
    struct bap_indexed_access *ind,
    ba0_int_p nbmon)
{
  struct ba0_tableof_int_p *tab;
  ba0_int_p n;

  n = nbmon - ind->tab.alloc;
  while (n > 0)
    {
      ind->tab.size = ind->tab.alloc;
      ba0_realloc2_table ((struct ba0_table *) &ind->tab, ind->tab.size + 1,
          (ba0_new_function *) & ba0_new_table);
      tab = ind->tab.tab[ind->tab.size++];
      ba0_t1_alloc (sizeof (ba0_int_p), n, (void **) &tab->tab,
          (unsigned ba0_int_p *) &tab->alloc);
      ind->alloc += tab->alloc;
      n -= tab->alloc;
    }
}

/*
 * texinfo: bap_reverse_indexed_access
 * Revert the sequence of indices present in @var{ind}.
 */

BAP_DLL void
bap_reverse_indexed_access (
    struct bap_indexed_access *ind)
{
  struct bap_iterator_indexed_access deb, fin;

  bap_begin_iterator_indexed_access (&deb, ind);
  bap_end_iterator_indexed_access (&fin, ind);
  while (deb.num.combined < fin.num.combined)
    {
      bap_swapindex_iterator_indexed_access (&deb, &fin);
      bap_next_iterator_indexed_access (&deb);
      bap_prev_iterator_indexed_access (&fin);
    }
}

/*
   --> ba0_embedded
*/

static char _indexed_tab[] = "bap_indexed_access.tab";
static char _indexed_tab_i[] = "bap_indexed_access.tab [i]";
static char _indexed_tab_i_tab[] = "bap_indexed_access.tab [i].tab";

BAP_DLL ba0_int_p
bap_garbage1_indexed_access (
    void *AA,
    enum ba0_garbage_code code)
{
  struct bap_indexed_access *A = (struct bap_indexed_access *) AA;
  ba0_int_p i, n = 0;

  if (code != ba0_embedded)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (A->tab.alloc > 0)
    n += ba0_new_gc_info (A->tab.tab, sizeof (void *) * A->tab.alloc,
        _indexed_tab);

  for (i = 0; i < A->tab.alloc; i++)
    {
      struct ba0_tableof_int_p *tab = A->tab.tab[i];
      n += ba0_new_gc_info (tab, sizeof (struct ba0_tableof_int_p),
          _indexed_tab_i);
      n += ba0_new_gc_info (tab->tab, sizeof (ba0_int_p) * tab->alloc,
          _indexed_tab_i_tab);
    }

  return n;
}

BAP_DLL void *
bap_garbage2_indexed_access (
    void *AA,
    enum ba0_garbage_code code)
{
  struct bap_indexed_access *A = (struct bap_indexed_access *) AA;
  ba0_int_p i;

  if (code != ba0_embedded)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (A->tab.alloc > 0)
    A->tab.tab =
        (struct ba0_tableof_int_p * *) ba0_new_addr_gc_info (A->tab.tab,
        _indexed_tab);
  for (i = 0; i < A->tab.alloc; i++)
    {
      struct ba0_tableof_int_p *tab;
      A->tab.tab[i] =
          (struct ba0_tableof_int_p *) ba0_new_addr_gc_info (A->tab.tab[i],
          _indexed_tab_i);
      tab = A->tab.tab[i];
      tab->tab =
          (ba0_int_p *) ba0_new_addr_gc_info (tab->tab, _indexed_tab_i_tab);
    }

  return (void *) 0;
}
