#include "ba0_global.h"
#include "ba0_exception.h"
#include "ba0_stack.h"
#include "ba0_garbage.h"
#include "ba0_dictionary.h"

/*
 * Return the first hash value of @var{key} i.e. an index in the
 * field @code{area} of @var{D}.
 */

static ba0_int_p
ba0_hash1_dictionary (
    struct ba0_dictionary *D,
    void *key)
{
  ba0_int_p result = (ba0_int_p) ((unsigned ba0_int_p) key >> D->shift);
  result &= D->area.size - 1;
  return result;
}

/*
 * Return the second hash value of @var{key} (useful in the case of 
 * collisions) i.e. a positive integer prime to the size of the field
 * @code{area} of @var{D}.
 */

static ba0_int_p
ba0_hash2_dictionary (
    struct ba0_dictionary *D,
    char *key)
{
  ba0_int_p result = (ba0_int_p) ((unsigned ba0_int_p) key >> D->shift);
  result &= D->area.size - 1;
/*
 * result has to be odd because size is a power of two
 */
  result |= 1;
  return result;
}

/*
 * texinfo: ba0_init_dictionary
 * Initialize @var{D} to the empty dictionary.
 * The argument @var{sizelt} contains the size in bytes
 * of the elements the dictionary keys point to.
 * The argument @var{log2_size} provides the initial size of
 * the field @code{area} of @var{D}. 
 * It should be at least equal to @math{8}.
 */

BA0_DLL void
ba0_init_dictionary (
    struct ba0_dictionary *D,
    ba0_int_p sizelt,
    ba0_int_p log2_size)
{
  ba0_int_p i;

  if (log2_size < 1 || log2_size > 20)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  D->log2_size = log2_size;

  D->shift = ba0_log2_int_p (sizelt);

  ba0_init_table ((struct ba0_table *) &D->area);
  D->used_entries = 0;
}

/*
 * texinfo: ba0_reset_dictionary
 * Reset @var{D} to the empty dictionary.
 */

BA0_DLL void
ba0_reset_dictionary (
    struct ba0_dictionary *D)
{
  ba0_int_p i;

  if (D->used_entries > 0)
    {
      for (i = 0; i < D->area.size; i++)
        D->area.tab[i] = BA0_NOT_AN_INDEX;
      D->used_entries = 0;
    }
}

/*
 * texinfo: ba0_sizeof_dictionary
 * Return the size needed to perform a copy of @var{D}.
 * If @var{code} is @code{ba0_embedded} then @var{D} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account.
 */

BA0_DLL unsigned ba0_int_p
ba0_sizeof_dictionary (
    struct ba0_dictionary *D,
    enum ba0_garbage_code code)
{
  unsigned ba0_int_p size;

  if (code == ba0_isolated)
    size = ba0_allocated_size (sizeof (struct ba0_dictionary));
  else
    size = 0;

  size += ba0_sizeof_table ((struct ba0_table *) &D->area, ba0_embedded);
  return size;
}

/*
 * texinfo: ba0_set_dictionary
 * Assign @var{src} to @var{dst}.
 */

BA0_DLL void
ba0_set_dictionary (
    struct ba0_dictionary *dst,
    struct ba0_dictionary *src)
{
  ba0_set_table ((struct ba0_table *) &dst->area,
      (struct ba0_table *) &src->area);
  dst->log2_size = src->log2_size;
  dst->shift = src->shift;
  dst->used_entries = src->used_entries;
}

/*
 * texinfo: ba0_get_dictionary
 * Return the index in @var{T} of the element with identifier @var{key}.
 * The element must have been recorded in @var{D}.
 * Return @code{BA0_NOT_AN_INDEX} if not found.
 */

BA0_DLL ba0_int_p
ba0_get_dictionary (
    struct ba0_dictionary *D,
    struct ba0_table *T,
    void *key)
{
  ba0_int_p i, j;
  ba0_int_p result = BA0_NOT_AN_INDEX;

  if (D->area.size == 0)
    return BA0_NOT_AN_INDEX;

  i = ba0_hash1_dictionary (D, key);
  j = D->area.tab[i];
  if (j == BA0_NOT_AN_INDEX)
    result = BA0_NOT_AN_INDEX;
  else if (j >= T->size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  else
    {
      if (T->tab[j] == key)
        {
/*
 * Found at first try
 */
          result = j;
        }
      else
        {
          ba0_int_p k = ba0_hash2_dictionary (D, key);
          bool loop = true;
/*
 * Collisions
 */
          result = BA0_NOT_AN_INDEX;
          while (loop)
            {
              i = (i + k) & (D->area.size - 1);
              j = D->area.tab[i];
              if (j == BA0_NOT_AN_INDEX)
                loop = false;
              else if (j >= T->size)
                BA0_RAISE_EXCEPTION (BA0_ERRALG);
              else
                {
                  if (T->tab[j] == key)
                    {
                      result = j;
                      loop = false;
                    }
                }
            }
        }
    }
  return result;
}

/*
 * Subfunction of ba0_add_dictionary
 *
 * Same specification as ba0_add_dictionary 
 * but area is supposed to be already resized - if needed
 */

static void
ba0_add2_dictionary (
    struct ba0_dictionary *D,
    struct ba0_table *T,
    void *key,
    ba0_int_p z)
{
  ba0_int_p i, j;
  char *string;

  i = ba0_hash1_dictionary (D, key);
  j = D->area.tab[i];
  if (j == BA0_NOT_AN_INDEX)
    {
/*
 * Found at first try
 */
      D->area.tab[i] = z;
    }
  else if (j >= T->size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  else
    {
      if (T->tab[j] == key)
        BA0_RAISE_EXCEPTION (BA0_ERRKEY);
      else
        {
          ba0_int_p k = ba0_hash2_dictionary (D, key);
          bool loop = true;
/*
 * Collisions
 */
          while (loop)
            {
              i = (i + k) & (D->area.size - 1);
              j = D->area.tab[i];
              if (j == BA0_NOT_AN_INDEX)
                {
                  loop = false;
                  D->area.tab[i] = z;
                }
              else if (j >= T->size)
                BA0_RAISE_EXCEPTION (BA0_ERRALG);
              else
                {
                  if (T->tab[j] == key)
                    BA0_RAISE_EXCEPTION (BA0_ERRKEY);
                }
            }
        }
    }
  D->used_entries += 1;
}

/*
 * texinfo: ba0_add_dictionary
 * Add to @var{D} an entry for the @math{z}th element of @var{T} which
 * has key @var{key}.
 * The element may actually not yet be present in @var{T}.
 * Exception @code{BA0_ERRKEY} is raised if 
 * the key is already present in @var{D}.
 */

BA0_DLL void
ba0_add_dictionary (
    struct ba0_dictionary *D,
    struct ba0_table *T,
    void *key,
    ba0_int_p z)
{
  if (D->area.size <= T->size << 2)
    {
      ba0_int_p *old_area = D->area.tab;
      ba0_int_p old_size = D->area.size;
      ba0_int_p new_size;
      ba0_int_p i;

      if (old_size == 0)
        new_size = 1 << D->log2_size;
      else
        new_size = 2 * old_size;

      ba0_realloc_table ((struct ba0_table *) &D->area, new_size);
      for (i = 0; i < new_size; i++)
        D->area.tab[i] = BA0_NOT_AN_INDEX;
      D->area.size = new_size;
      D->log2_size += 1;
      D->used_entries = 0;

      for (i = 0; i < old_size; i++)
        {
          ba0_int_p j = old_area[i];
          if (j != BA0_NOT_AN_INDEX)
            ba0_add2_dictionary (D, T, T->tab[j], j);
        }
    }
  ba0_add2_dictionary (D, T, key, z);
}
