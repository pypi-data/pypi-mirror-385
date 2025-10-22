#include "bav_dictionary_symbol.h"

/*
 * texinfo: bav_init_dictionary_symbol
 * Initialize @var{D} to the empty dictionary.
 * The argument @var{log2_size} provides the initial size of
 * the field @code{area} of @var{D}.
 * It should be at least equal to @math{8}.
 */

BAV_DLL void
bav_init_dictionary_symbol (
    struct bav_dictionary_symbol *D,
    ba0_int_p log2_size)
{
  ba0_init_dictionary ((struct ba0_dictionary *) D,
      sizeof (struct bav_symbol), log2_size);
}

/*
 * texinfo: bav_reset_dictionary_symbol
 * Reset @var{D} to the empty dictionary.
 */

BAV_DLL void
bav_reset_dictionary_symbol (
    struct bav_dictionary_symbol *D)
{
  ba0_reset_dictionary ((struct ba0_dictionary *) D);
}

/*
 * texinfo: bav_sizeof_dictionary_symbol
 * Return the size needed to perform a copy of @var{D}.
 * If @var{code} is @code{ba0_embedded} then @var{D} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account.
 */

BAV_DLL unsigned ba0_int_p
bav_sizeof_dictionary_symbol (
    struct bav_dictionary_symbol *D,
    enum ba0_garbage_code code)
{
  return ba0_sizeof_dictionary ((struct ba0_dictionary *) D, code);
}

/*
 * texinfo: bav_set_dictionary_symbol
 * Assign @var{src} to @var{dst}.
 */

BAV_DLL void
bav_set_dictionary_symbol (
    struct bav_dictionary_symbol *dst,
    struct bav_dictionary_symbol *src)
{
  ba0_set_dictionary ((struct ba0_dictionary *) dst,
      (struct ba0_dictionary *) src);
}

/*
 * texinfo: bav_get_dictionary_symbol
 * Return the index in @var{T} of the element associated to @var{y}.
 * The element must have been recorded in @var{D}.
 * Return @code{BA0_NOT_AN_INDEX} if not found.
 */

BAV_DLL ba0_int_p
bav_get_dictionary_symbol (
    struct bav_dictionary_symbol *D,
    struct bav_tableof_symbol *T,
    struct bav_symbol *y)
{
  return ba0_get_dictionary ((struct ba0_dictionary *) D,
      (struct ba0_table *) T, y);
}

/*
 * texinfo: bav_add_dictionary_symbol
 * Add to @var{D} an entry for the @math{z}th element of @var{T} which
 * has key @var{y}.
 * The element may actually not yet be present in @var{T}.
 * Exception @code{BA0_ERRKEY} is raised if @var{y} 
 * is already present in @var{D}.
 */

BAV_DLL void
bav_add_dictionary_symbol (
    struct bav_dictionary_symbol *D,
    struct bav_tableof_symbol *T,
    struct bav_symbol *y,
    ba0_int_p z)
{
  ba0_add_dictionary ((struct ba0_dictionary *) D, (struct ba0_table *) T, y,
      z);
}
