#include "bav_typed_ident.h"
#include "bav_differential_ring.h"
#include "bav_global.h"

/*
 * texinfo: bav_init_typed_ident
 * Initialize @var{tid} to the empty typed ident.
 */

BAV_DLL void
bav_init_typed_ident (
    struct bav_typed_ident *tid)
{
  tid->ident = (char *) 0;
  tid->type = bav_plain_ident;
  ba0_init_table ((struct ba0_table *) &tid->indices);
}

/*
 * texinfo: bav_new_typed_ident
 * Allocate a new typed ident, initialize it and return it.
 */

BAV_DLL struct bav_typed_ident *
bav_new_typed_ident (
    void)
{
  struct bav_typed_ident *tid;
  tid = (struct bav_typed_ident *) ba0_alloc (sizeof (struct bav_typed_ident));
  bav_init_typed_ident (tid);
  return tid;
}

/*
 * texinfo: bav_sizeof_typed_ident
 * Return the size needed to perform a copy of @var{tid}.
 * If @var{code} is @code{ba0_embedded} then @var{tid} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account.
 * If @var{strings_not_copied} is @code{true} then
 * the @code{ident} field of @var{tid} is supposed not to be copied.
 */

BAV_DLL unsigned ba0_int_p
bav_sizeof_typed_ident (
    struct bav_typed_ident *tid,
    enum ba0_garbage_code code,
    bool strings_not_copied)
{
  unsigned ba0_int_p size;

  if (code == ba0_isolated)
    size = ba0_allocated_size (sizeof (struct bav_typed_ident));
  else
    size = 0;
  if (!strings_not_copied)
    if (tid->ident != (char *) 0)
      size += ba0_allocated_size (strlen (tid->ident) + 1);
  size += ba0_sizeof_table ((struct ba0_table *) &tid->indices, ba0_embedded);
  return size;
}

/*
 * texinfo: bav_sizeof_tableof_typed_ident
 * Return the size needed to perform a copy of @var{T}.
 * If @var{code} is @code{ba0_embedded} then @var{T} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account. 
 * If @var{strings_not_copied} is @code{true} then
 * the strings occurring in @var{T} are supposed not to be copied.
 */

BAV_DLL unsigned ba0_int_p
bav_sizeof_tableof_typed_ident (
    struct bav_tableof_typed_ident *T,
    enum ba0_garbage_code code,
    bool strings_not_copied)
{
  unsigned ba0_int_p size;
  ba0_int_p i;

  size = ba0_sizeof_table ((struct ba0_table *) T, code);

  for (i = 0; i < T->size; i++)
    size += bav_sizeof_typed_ident (T->tab[i], ba0_isolated,
        strings_not_copied);

  return size;
}

/*
 * texinfo: bav_R_set_typed_ident
 * Copy @var{src} into @var{dst} without performing any string allocation.
 * The strings present in @var{src} are supposed to have copies in @var{R}.
 * Instead of duplicating them, the copies are used.
 * The needed size for the result is the one returned by
 * @code{bav_sizeof_typed_ident} with @var{strings_not_copied} set
 * to @code{true}.
 */

BAV_DLL void
bav_R_set_typed_ident (
    struct bav_typed_ident *dst,
    struct bav_typed_ident *src,
    struct bav_differential_ring *R)
{
  ba0_int_p j;

  j = ba0_get_dictionary_string (&R->dict_str_to_str,
      (struct ba0_table *) &R->strs, src->ident);
  if (j == BA0_NOT_AN_INDEX)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  dst->ident = R->strs.tab[j];
  dst->type = src->type;

  ba0_set_table ((struct ba0_table *) &dst->indices,
      (struct ba0_table *) &src->indices);
}

/*
 * texinfo: bav_R_set_tableof_typed_ident
 * Copy @var{src} into @var{dst} by calling
 * @code{bav_R_set_typed_ident}. See this function.
 */

BAV_DLL void
bav_R_set_tableof_typed_ident (
    struct bav_tableof_typed_ident *dst,
    struct bav_tableof_typed_ident *src,
    struct bav_differential_ring *R)
{
  ba0_int_p i;

  ba0_realloc2_table ((struct ba0_table *) dst, src->size,
      (ba0_new_function *) & bav_new_typed_ident);
  for (i = 0; i < src->size; i++)
    bav_R_set_typed_ident (dst->tab[i], src->tab[i], R);
  dst->size = src->size;
}

/*
 * texinfo: bav_get_typed_ident_from_symbol
 * Return the index in @var{T} of the typed ident associated
 * to @var{y}. The typed ident must have been recorded in @var{D}.
 * Return @code{BA0_NOT_AN_INDEX} if not found.
 */

BAV_DLL ba0_int_p
bav_get_typed_ident_from_symbol (
    struct ba0_dictionary_typed_string *D,
    struct bav_tableof_typed_ident *T,
    struct bav_symbol *y)
{
  ba0_int_p j;

  if (y->index_in_rigs == BA0_NOT_AN_INDEX)
    j = ba0_get_dictionary_typed_string (D, (struct ba0_table *) T,
        y->ident, bav_plain_ident);
  else
    {
      char *string = bav_global.R.rigs.tab[y->index_in_rigs]->strs.tab[0];
      j = ba0_get_dictionary_typed_string (D, (struct ba0_table *) T,
          string, bav_range_indexed_string_radical_ident);
    }
  return j;
}

/*
 * texinfo: bav_R_append_tableof_typed_ident_block
 * Append to @var{T} the entries corresponding to the block @var{B}
 * with first index field equal to @var{first_index}.
 * The strings present in @var{B} are supposed to have copies in @var{R}.
 * Instead of duplicating them, the copies are used.
 */

BAV_DLL void
bav_R_append_tableof_typed_ident_block (
    struct bav_tableof_typed_ident *T,
    ba0_int_p first_index,
    struct bav_block *B,
    struct bav_differential_ring *R)
{
  struct ba0_tableof_int_p *U;
  ba0_int_p i, j, k;
  char *string;

  for (i = 0; i < B->rigs.size; i++)
    {
      if (ba0_is_plain_string_range_indexed_group (B->rigs.tab[i], &string))
        {
          if (T->size == T->alloc)
            {
              ba0_int_p new_alloc = 2 * T->alloc + 1;
              ba0_realloc2_table ((struct ba0_table *) T, new_alloc,
                  (ba0_new_function *) & bav_new_typed_ident);
            }
          k = ba0_get_dictionary_string (&R->dict_str_to_str,
              (struct ba0_table *) &R->strs, string);
          T->tab[T->size]->ident = R->strs.tab[k];
          T->tab[T->size]->type = bav_plain_ident;
          U = &T->tab[T->size]->indices;
          ba0_realloc_table ((struct ba0_table *) U, 3);
          U->tab[0] = first_index;
          U->tab[1] = i;
          U->tab[2] = BA0_NOT_AN_INDEX;
          U->size = 3;
          T->size += 1;
        }
      else
        {
          struct ba0_range_indexed_group *g = B->rigs.tab[i];
          for (j = 0; j < g->strs.size; j++)
            {
              if (T->size == T->alloc)
                {
                  ba0_int_p new_alloc = 2 * T->alloc + 1;
                  ba0_realloc2_table ((struct ba0_table *) T, new_alloc,
                      (ba0_new_function *) & bav_new_typed_ident);
                }
              k = ba0_get_dictionary_string (&R->dict_str_to_str,
                  (struct ba0_table *) &R->strs, g->strs.tab[j]);
              T->tab[T->size]->ident = R->strs.tab[k];
              T->tab[T->size]->type = bav_range_indexed_string_radical_ident;
              U = &T->tab[T->size]->indices;
              ba0_realloc_table ((struct ba0_table *) U, 3);
              U->tab[0] = first_index;
              U->tab[1] = i;
              U->tab[2] = j;
              U->size = 3;
              T->size += 1;
            }
        }
    }
}

/*
 * texinfo: bav_R_set_tableof_typed_ident_tableof_block
 * Fill the table @var{T} with all the blocks occurring in @var{B}.
 * The strings present in @var{B} are supposed to have copies in @var{R}.
 * Instead of duplicating them, the copies are used.
 */

BAV_DLL void
bav_R_set_tableof_typed_ident_tableof_block (
    struct bav_tableof_typed_ident *T,
    struct bav_tableof_block *B,
    struct bav_differential_ring *R)
{
  ba0_int_p i, j, n;

  n = 0;
  for (i = 0; i < B->size; i++)
    for (j = 0; j < B->tab[i]->rigs.size; j++)
      n += B->tab[i]->rigs.tab[j]->strs.size;

  ba0_reset_table ((struct ba0_table *) T);
  ba0_realloc2_table ((struct ba0_table *) T, n,
      (ba0_new_function *) & bav_new_typed_ident);
  for (i = 0; i < B->size; i++)
    bav_R_append_tableof_typed_ident_block (T, i, B->tab[i], R);
}
