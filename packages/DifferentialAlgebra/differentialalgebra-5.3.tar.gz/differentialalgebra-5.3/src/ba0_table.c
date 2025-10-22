#include "ba0_stack.h"
#include "ba0_exception.h"
#include "ba0_list.h"
#include "ba0_table.h"
#include "ba0_global.h"

/*
 * texinfo: ba0_sizeof_table
 * Return the size needed to perform a copy of @var{T}.
 * If @var{code} is @code{ba0_embedded} then @var{T} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account. 
 */

BA0_DLL unsigned ba0_int_p
ba0_sizeof_table (
    struct ba0_table *T,
    enum ba0_garbage_code code)
{
  unsigned ba0_int_p size;
  if (code == ba0_isolated)
    size = ba0_allocated_size (sizeof (struct ba0_table));
  else
    size = 0;
/*
 * T->size because ba0_copy uses T->size
 */
  if (T->size > 0)
    size += ba0_allocated_size (T->size * sizeof (void *));
  return size;
}

/*
 * texinfo: ba0_realloc_table
 * Reallocate the table if needed in such a way that the table can
 * receive at least @var{n} elements. Formerly stored elements are kept.
 * New entries are initialized to zero.
 */

BA0_DLL void
ba0_realloc_table (
    struct ba0_table *T,
    ba0_int_p n)
{
  void **tab;

  if (n > T->alloc)
    {
      tab = (void **) ba0_alloc (sizeof (void *) * n);
      memcpy (tab, T->tab, T->size * sizeof (void *));
      memset (tab + T->alloc, 0, (n - T->alloc) * sizeof (void *));
      T->tab = tab;
      T->alloc = n;
    }
}

/*
 * texinfo: ba0_re_malloc_table
 * The entries of the table @var{T} are supposed to be allocated using
 * @code{ba0_malloc}. Reallocate the table if needed (using @code{ba0_malloc})
 * in such a way that the table can receive at least @var{n} elements. 
 * Formerly stored elements are kept.
 */

BA0_DLL void
ba0_re_malloc_table (
    struct ba0_table *T,
    ba0_int_p n)
{
  void **tab;

  if (n > T->alloc)
    {
      tab = (void **) ba0_malloc (sizeof (void *) * n);
      if (T->tab)
        {
          memcpy (tab, T->tab, T->alloc * sizeof (void *));
          ba0_free (T->tab);
          ba0_malloc_counter -= T->alloc * sizeof (void *);
        }
      T->tab = tab;
      T->alloc = n;
    }
}

/*
 * texinfo: ba0_realloc2_table
 * Variant of the above function but initialize the new entries with the values
 * returned by @var{new_objet}.
 */

BA0_DLL void
ba0_realloc2_table (
    struct ba0_table *T,
    ba0_int_p n,
    ba0_new_function *new_objet)
{
  void **tab;
  ba0_int_p i;

  if (n > T->alloc)
    {
      tab = (void **) ba0_alloc (sizeof (void *) * n);
      memcpy (tab, T->tab, T->size * sizeof (void *));
      for (i = T->size; i < n; i++)
        tab[i] = (*new_objet) ();
      T->tab = tab;
      T->alloc = n;
    }
}

/*
 * texinfo: ba0_init_table
 * Initialize @var{T} (constructor).
 */

BA0_DLL void
ba0_init_table (
    struct ba0_table *T)
{
  T->alloc = 0;
  T->size = 0;
  T->tab = (void **) 0;
}

/*
 * texinfo: ba0_reset_table
 * Set to zero the number of used elements of @var{T}.
 */

BA0_DLL void
ba0_reset_table (
    struct ba0_table *T)
{
  T->size = 0;
}

/*
 * texinfo: ba0_new_table
 * Allocate a new @code{struct ba0_table} in the current stack,
 * apply the constructor over it and return the result.
 */

BA0_DLL struct ba0_table *
ba0_new_table (
    void)
{
  struct ba0_table *T;

  T = (struct ba0_table *) ba0_alloc (sizeof (struct ba0_table));
  ba0_init_table (T);
  return T;
}

/*
 * texinfo: ba0_delete_table
 * Remove the @var{i}th element of @var{T}.
 */

BA0_DLL void
ba0_delete_table (
    struct ba0_table *T,
    ba0_int_p i)
{
  if (i == T->size)
    T->size--;
  else if (i < T->size)
    {
      void *x = T->tab[i];
      memmove (T->tab + i, T->tab + i + 1, (T->size - i - 1) * sizeof (void *));
      T->tab[--T->size] = x;
    }
}

/*
 * texinfo: ba0_insert_table
 * Insert @var{p} in @var{T} at index @var{i}.
 * Exception @code{BA0_ERRALG} is raised if @var{i} is negative or
 * greater than the number of used elements of @var{T}.
 */

BA0_DLL void
ba0_insert_table (
    struct ba0_table *T,
    ba0_int_p i,
    void *p)
{
  if (i < 0 || i > T->size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  ba0_realloc_table (T, T->size + 1);
  memmove (T->tab + i + 1, T->tab + i, (T->size - i) * sizeof (void *));
  T->tab[i] = p;
  T->size++;
}

/*
 * texinfo: ba0_member_table
 * Return @code{true} if @var{x} belongs to @var{T} else @code{false}.
 */

BA0_DLL bool
ba0_member_table (
    void *p,
    struct ba0_table *T)
{
  ba0_int_p i;

  for (i = 0; i < T->size; i++)
    if (p == T->tab[i])
      return true;
  return false;
}

/*
 * texinfo: ba0_member2_table
 * Return @code{true} if @var{x} belongs to @var{T} else @code{false}.
 * In the first case, *@var{index} is assigned the index of @var{x}
 * in @var{T}, provided that @var{index} is nonzero.
 */

BA0_DLL bool
ba0_member2_table (
    void *p,
    struct ba0_table *T,
    ba0_int_p *index)
{
  ba0_int_p i;

  for (i = 0; i < T->size; i++)
    if (p == T->tab[i])
      {
        if (index)
          *index = i;
        return true;
      }
  return false;
}

/*
 * texinfo: ba0_equal_table
 * Return @code{true} if @var{T} and @var{U} have the same entries, in
 * the same order.
 */

BA0_DLL bool
ba0_equal_table (
    struct ba0_table *T,
    struct ba0_table *U)
{
  ba0_int_p i;

  if (T->size != U->size)
    return false;
  for (i = 0; i < T->size; i++)
    if (T->tab[i] != U->tab[i])
      return false;
  return true;
}

/*
 * texinfo: ba0_is_unique_table
 * Return @code{true} if the elements of @var{T} are pairwise different
 * else @code{false}. The table @var{T} is not necessarily sorted.
 */

BA0_DLL bool
ba0_is_unique_table (
    struct ba0_table *T)
{
  ba0_int_p i, j;

  for (i = 0; i < T->size - 1; i++)
    {
      for (j = i + 1; j < T->size; j++)
        if (T->tab[i] == T->tab[j])
          return false;
    }
  return true;
}

static int
compare_addresses (
    const void *a,
    const void *b)
{
  void *aa = *(void **) a;
  void *bb = *(void **) b;

  if (aa < bb)
    return -1;
  else if (aa == bb)
    return 0;
  else
    return 1;
}

/*
 * texinfo: ba0_sort_table
 * Sort the @code{tab} field of @var{src} by increasing addresses.
 * Result in @var{dst}.
 */
BA0_DLL void
ba0_sort_table (
    struct ba0_table *dst,
    struct ba0_table *src)
{
  if (dst != src)
    ba0_set_table (dst, src);
  qsort (dst->tab, dst->size, sizeof (void *), &compare_addresses);
}

/*
 * texinfo: ba0_unique_table
 * Remove duplicated elements from @var{U}. 
 * The table @var{U} is supposed to be sorted.
 * Result in @var{T}.
 */

BA0_DLL void
ba0_unique_table (
    struct ba0_table *T,
    struct ba0_table *U)
{
  ba0_int_p i, j;

  if (T != U)
    ba0_set_table (T, U);
  i = 1;
  while (i < T->size)
    {
      if (T->tab[i] == T->tab[i - 1])
        ba0_delete_table (T, i);
      else
        i += 1;
    }
}

/*
 * texinfo: ba0_reverse_table
 * Reverse the elements of @var{U}. Result in @var{T}.
 */

BA0_DLL void
ba0_reverse_table (
    struct ba0_table *T,
    struct ba0_table *U)
{
  ba0_int_p i, j;

  if (T == U)
    {
      for (i = 0, j = T->size - 1; i < j; i++, j--)
        BA0_SWAP (void *,
            T->tab[i],
            T->tab[j]);
    }
  else
    {
      ba0_reset_table (T);
      ba0_realloc_table (T, U->size);
      T->size = U->size;
      for (i = 0, j = U->size - 1; j >= 0; i++, j--)
        T->tab[i] = U->tab[j];
    }
}

/*
 * texinfo: ba0_concat_table
 * Assign to @var{T} the result of the concatenation of @var{U} and @var{V}.
 */

BA0_DLL void
ba0_concat_table (
    struct ba0_table *T,
    struct ba0_table *U,
    struct ba0_table *V)
{
  ba0_realloc_table (T, U->size + V->size);
  memmove (T->tab + U->size, V->tab, sizeof (void *) * V->size);
  if (T != U)
    memmove (T->tab, U->tab, sizeof (void *) * U->size);
  T->size = U->size + V->size;
}

/*
 * texinfo: ba0_set_table
 * Copy @var{U} to @var{T}.
 */

BA0_DLL void
ba0_set_table (
    struct ba0_table *T,
    struct ba0_table *U)
{
  if (T != U)
    {
      T->size = 0;
      ba0_realloc_table (T, U->size);
      memcpy (T->tab, U->tab, U->size * sizeof (void *));
      T->size = U->size;
    }
}

/*
 * texinfo: ba0_set2_table
 * Copy @var{U} to @var{T}, duplicating each element of @var{T}.
 */

BA0_DLL void
ba0_set2_table (
    struct ba0_table *T,
    struct ba0_table *U,
    ba0_new_function *newf,
    ba0_set_function *set)
{
  ba0_int_p i;

  if (T != U)
    {
      ba0_realloc2_table (T, U->size, newf);
      T->size = 0;
      for (i = 0; i < U->size; i++)
        {
          (*set) (T->tab[i], U->tab[i]);
          T->size += 1;
        }
    }
}

/*
 * texinfo: ba0_set_table_list
 * Copy @var{L} to @var{T}.
 */

BA0_DLL void
ba0_set_table_list (
    struct ba0_table *T,
    struct ba0_list *L)
{
  ba0_reset_table (T);
  ba0_append_table_list (T, L);
}

/*
 * texinfo: ba0_append_table_list
 * Append @var{L} to @var{T}.
 */

BA0_DLL void
ba0_append_table_list (
    struct ba0_table *T,
    struct ba0_list *L)
{
  ba0_int_p i, j;

  j = ba0_length_list (L);
  ba0_realloc_table (T, T->size + j);
  for (i = 0; i < j; i++)
    {
      T->tab[T->size] = L->value;
      T->size += 1;
      L = L->next;
    }
}

/*
 * Moves U.tab [g] at U.tab [U.size-1]. result in T.
 * The elements in U.tab [g+1, ... U.size-1] are shifted to the left.
 */

/*
 * texinfo: ba0_move_to_tail_table
 * Perform a left rotation on the elements of @var{U} whose indices are greater
 * than or equal to @var{g}, so that the element of @var{U} which was formerly
 * at index @var{g}, occurs at the end of @var{U}. Result in @var{T}.
 * Exception @code{BA0_ERRALG} is raised if @var{g} is negative or
 * greater than the number of used elements of @var{T}.
 */

BA0_DLL void
ba0_move_to_tail_table (
    struct ba0_table *T,
    struct ba0_table *U,
    ba0_int_p g)
{
  void *elt;

  if (g < 0 || g >= U->size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (T == U)
    {
      if (g != U->size - 1)
        {
          elt = U->tab[g];
          memmove (U->tab + g, U->tab + g + 1,
              (U->size - 1 - g) * sizeof (void *));
          U->tab[U->size - 1] = elt;
        }
    }
  else
    {
      ba0_set_table (T, U);
      ba0_move_to_tail_table (T, T, g);
    }
}

/*
 * Reciprocal operation. Result in T.
 * Moves U.tab [U.size-1] to U.tab [g].
 * The elements in U.tab [g, ..., U.size-2] are shifted to the right.
 */

/*
 * texinfo: ba0_move_from_tail_table
 * The inverse of the former operation.
 * Performs a right rotation on the elements of @var{U} whose indices are greater
 * than or equal to @var{g}, so that the element of @var{U} which was formerly
 * at the end of @var{U}, occurs at index @var{g}. Result in @var{T}.
 * Exception @code{BA0_ERRALG} is raised if @var{g} is negative or
 * greater than the number of used elements of @var{T}.
 */

BA0_DLL void
ba0_move_from_tail_table (
    struct ba0_table *T,
    struct ba0_table *U,
    ba0_int_p g)
{
  void *elt;

  if (g < 0 || g >= U->size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (T == U)
    {
      if (g != U->size - 1)
        {
          elt = U->tab[U->size - 1];
          memmove (U->tab + g + 1, U->tab + g,
              (U->size - 1 - g) * sizeof (void *));
          U->tab[g] = elt;
        }
    }
  else
    {
      ba0_set_table (T, U);
      ba0_move_from_tail_table (T, T, g);
    }
}
