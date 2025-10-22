#include "ba0_global.h"
#include "ba0_exception.h"
#include "ba0_stack.h"
#include "ba0_garbage.h"
#include "ba0_dictionary_typed_string.h"

/*
 * Return the first hash value of @var{ident} i.e. an index in the
 * field @code{area} of @var{D}.
 */

static ba0_int_p
ba0_hash1_dictionary_typed_string (
    struct ba0_dictionary_typed_string *D,
    char *ident,
    ba0_int_p type)
{
  ba0_int_p result;
  ba0_int_p i, j;

  result = 0;
  j = 0;
  for (i = 0; ident[i]; i++)
    {
/*
 * One ASCII code is less than 2**7
 * The contribution of ident[i] to result is small enough
 */
      if (j > D->log2_size - 7)
        j = 0;
      result += (ba0_int_p) (unsigned char) ident[i] << j;
      j += 1;
    }
/*
 * size is a power of two
 */
  result += 1 << (type + 1);
  result &= D->area.size - 1;
  return result;
}

/*
 * Return the second hash value of @var{ident} (useful in the case of 
 * collisions) i.e. a positive integer prime to the size of the field
 * @code{area} of @var{D}.
 */

static ba0_int_p
ba0_hash2_dictionary_typed_string (
    struct ba0_dictionary_typed_string *D,
    char *ident,
    ba0_int_p type)
{
  ba0_int_p result;
  ba0_int_p i, j;

  result = 0;
  j = 1;
  for (i = 0; ident[i]; i++)
    {
      if (j > D->log2_size - 7)
        j = 0;
      result += (ba0_int_p) (unsigned char) ident[i] << j;
      j += 1;
    }
  result &= D->area.size - 1;
/*
 * result has to be odd because size is a power of two
 */
  result += 1 << (type + 1);
  result |= 1;
  return result;
}

/*
 * texinfo: ba0_init_dictionary_typed_string
 * Initialize @var{D} to the empty dictionary.
 * The argument @var{object_to_ident} points to a function which
 * associates to any element of the dictionary its string identifier.
 * The argument @var{log2_size} provides the initial size of
 * the field @code{area} of @var{D}. 
 * It should be at least equal to @math{8}.
 */

BA0_DLL void
ba0_init_dictionary_typed_string (
    struct ba0_dictionary_typed_string *D,
    char *(*object_to_ident) (void *),
    ba0_int_p (*object_to_type) (void *),
    ba0_int_p log2_size)
{
  ba0_int_p i;

  if (log2_size < 8 || log2_size > 20)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  D->log2_size = log2_size;

  ba0_init_table ((struct ba0_table *) &D->area);

  D->object_to_ident = object_to_ident;
  D->object_to_type = object_to_type;
  D->used_entries = 0;
}

/*
 * texinfo: ba0_reset_dictionary_typed_string
 * Reset @var{D} to the empty dictionary.
 */

BA0_DLL void
ba0_reset_dictionary_typed_string (
    struct ba0_dictionary_typed_string *D)
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
 * texinfo: ba0_sizeof_dictionary_typed_string
 * Return the size needed to perform a copy of @var{D}.
 * If @var{code} is @code{ba0_embedded} then @var{D} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account.
 */

BA0_DLL unsigned ba0_int_p
ba0_sizeof_dictionary_typed_string (
    struct ba0_dictionary_typed_string *D,
    enum ba0_garbage_code code)
{
  unsigned ba0_int_p size;

  if (code == ba0_isolated)
    size = ba0_allocated_size (sizeof (struct ba0_dictionary_typed_string));
  else
    size = 0;

  size += ba0_sizeof_table ((struct ba0_table *) &D->area, ba0_embedded);
  return size;
}

/*
 * texinfo: ba0_set_dictionary_typed_string
 * Assign @var{src} to @var{dst}.
 */

BA0_DLL void
ba0_set_dictionary_typed_string (
    struct ba0_dictionary_typed_string *dst,
    struct ba0_dictionary_typed_string *src)
{
  ba0_set_table ((struct ba0_table *) &dst->area,
      (struct ba0_table *) &src->area);
  dst->log2_size = src->log2_size;
  dst->used_entries = src->used_entries;
  dst->object_to_ident = src->object_to_ident;
  dst->object_to_type = src->object_to_type;
}

/*
 * texinfo: ba0_get_dictionary_typed_string
 * Return the index in @var{T} of the element with identifier @var{ident}
 * and type @var{type}. The element must have been recorded in @var{D}.
 * Return @code{BA0_NOT_AN_INDEX} if not found.
 */

BA0_DLL ba0_int_p
ba0_get_dictionary_typed_string (
    struct ba0_dictionary_typed_string *D,
    struct ba0_table *T,
    char *ident,
    ba0_int_p type)
{
  ba0_int_p i, j;
  ba0_int_p result = BA0_NOT_AN_INDEX;
  char *string;
  ba0_int_p string_type;

  if (D->area.size == 0)
    return BA0_NOT_AN_INDEX;

  i = ba0_hash1_dictionary_typed_string (D, ident, type);
  j = D->area.tab[i];
  if (j == BA0_NOT_AN_INDEX)
    result = BA0_NOT_AN_INDEX;
  else if (j >= T->size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  else
    {
      string = D->object_to_ident (T->tab[j]);
      string_type = D->object_to_type (T->tab[j]);
      if (type == string_type && strcmp (string, ident) == 0)
        {
/*
 * Found at first try
 */
          result = j;
        }
      else
        {
          ba0_int_p k = ba0_hash2_dictionary_typed_string (D, ident, type);
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
                  string = D->object_to_ident (T->tab[j]);
                  string_type = D->object_to_type (T->tab[j]);
                  if (type == string_type && strcmp (string, ident) == 0)
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
 * Subfunction of ba0_add_dictionary_typed_string
 *
 * Same specification as ba0_add_dictionary_typed_string 
 * but area is supposed to be already resized - if needed
 */

static void
ba0_add2_dictionary_typed_string (
    struct ba0_dictionary_typed_string *D,
    struct ba0_table *T,
    char *ident,
    ba0_int_p type,
    ba0_int_p z)
{
  ba0_int_p i, j;
  char *string;
  ba0_int_p string_type;

  i = ba0_hash1_dictionary_typed_string (D, ident, type);
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
      string = D->object_to_ident (T->tab[j]);
      string_type = D->object_to_type (T->tab[j]);
      if (type == string_type && strcmp (string, ident) == 0)
        BA0_RAISE_EXCEPTION (BA0_ERRKEY);
      else
        {
          ba0_int_p k = ba0_hash2_dictionary_typed_string (D, ident, type);
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
                  string = D->object_to_ident (T->tab[j]);
                  string_type = D->object_to_type (T->tab[j]);
                  if (type == string_type && strcmp (string, ident) == 0)
                    BA0_RAISE_EXCEPTION (BA0_ERRKEY);
                }
            }
        }
    }
  D->used_entries += 1;
}

/*
 * texinfo: ba0_add_dictionary_typed_string
 * Add to @var{D} an entry for the @math{z}th element of @var{T} which
 * has identifier @var{ident} and type @var{type}.
 * The element may actually not yet be present in @var{T}.
 * Exception @code{BA0_ERRKEY} is raised if the key 
 * is already present in @var{D}.
 */

BA0_DLL void
ba0_add_dictionary_typed_string (
    struct ba0_dictionary_typed_string *D,
    struct ba0_table *T,
    char *ident,
    ba0_int_p type,
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
            {
              char *string = D->object_to_ident (T->tab[j]);
              ba0_int_p string_type = D->object_to_type (T->tab[j]);
              ba0_add2_dictionary_typed_string (D, T, string, string_type, j);
            }
        }
    }
  ba0_add2_dictionary_typed_string (D, T, ident, type, z);
}
