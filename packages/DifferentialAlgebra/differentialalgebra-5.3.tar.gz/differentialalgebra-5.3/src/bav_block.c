#include "bav_block.h"
#include "bav_differential_ring.h"

/*
 * texinfo: bav_init_block
 * Initialize @var{b} to the empty block.
 */

BAV_DLL void
bav_init_block (
    struct bav_block *b)
{
  b->subr = (struct bav_subranking *) 0;
  ba0_init_table ((struct ba0_table *) &b->rigs);
}

/*
 * texinfo: bav_reset_block
 * Empty the block @var{b}.
 */

BAV_DLL void
bav_reset_block (
    struct bav_block *b)
{
  b->subr = (struct bav_subranking *) 0;
  ba0_reset_table ((struct ba0_table *) &b->rigs);
}

/*
 * texinfo: bav_is_empty_block
 * Return @code{true} if @var{b} is empty.
 */

BAV_DLL bool
bav_is_empty_block (
    struct bav_block *b)
{
  return b->rigs.size == 0;
}

/*
 * texinfo: bav_new_block
 * Allocate a new block in the current stack, initialize it and
 * return it.
 */

BAV_DLL struct bav_block *
bav_new_block (
    void)
{
  struct bav_block *b;

  b = (struct bav_block *) ba0_alloc (sizeof (struct bav_block));
  bav_init_block (b);
  return b;
}

/*
 * texinfo: bav_scanf_block
 * The parsing function for blocks.
 * It is called by @code{ba0_scanf/%b}.
 * Exception @code{BAV_ERRBLO} can be raised.
 */

BAV_DLL void *
bav_scanf_block (
    void *z)
{
  struct bav_block *b;

  if (z == (void *) 0)
    b = bav_new_block ();
  else
    b = (struct bav_block *) z;

  if (ba0_sign_token_analex ("["))
    {
      bav_is_subranking ("grlexA", &b->subr);
      ba0_scanf ("%t[%range_indexed_group]", &b->rigs);
    }
  else if (ba0_type_token_analex () == ba0_string_token &&
      bav_is_subranking (ba0_value_token_analex (), &b->subr))
    {
      ba0_get_token_analex ();
      ba0_scanf ("%t[%range_indexed_group]", &b->rigs);
    }
  else if (ba0_type_token_analex () == ba0_string_token ||
      ba0_sign_token_analex ("("))
    {
      bav_is_subranking ("grlexA", &b->subr);
      ba0_realloc_table ((struct ba0_table *) &b->rigs, 1);
      b->rigs.tab[0] = ba0_scanf_range_indexed_group (0);
      b->rigs.size = 1;
    }
  else
    BA0_RAISE_PARSER_EXCEPTION (BAV_ERRBLO);
  return b;
}

/*
 * texinfo: bav_printf_block
 * The printing function for blocks.
 * It is called by @code{ba0_printf/%b}.
 */

BAV_DLL void
bav_printf_block (
    void *z)
{
  struct bav_block *b = (struct bav_block *) z;

  ba0_printf ("%s%t[%range_indexed_group]", b->subr->ident, &b->rigs);
}

/*
 * texinfo: bav_sizeof_block
 * Return the size needed to copy @var{b}.
 * If @var{code} is @code{ba0_embedded} then @var{b} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account.
 * If @var{strings_not_copied} then the strings occurring in @var{b}
 * are supposed not to be copied.
 */

BAV_DLL unsigned ba0_int_p
bav_sizeof_block (
    struct bav_block *b,
    enum ba0_garbage_code code,
    bool strings_not_copied)
{
  unsigned ba0_int_p size;

  if (code == ba0_isolated)
    size = ba0_allocated_size (sizeof (struct bav_block));
  else
    size = 0;
  size += ba0_sizeof_tableof_range_indexed_group (&b->rigs, ba0_embedded,
      strings_not_copied);
  return size;
}

/* texinfo: bav_sizeof_tableof_block
 * Return the size needed to copy @var{T}.
 * If @var{code} is @code{ba0_embedded} then @var{T} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account.
 * If @var{strings_not_copied} then the strings occurring in the
 * blocks of @var{T} are supposed not to be copied.
 */

BAV_DLL unsigned ba0_int_p
bav_sizeof_tableof_block (
    struct bav_tableof_block *T,
    enum ba0_garbage_code code,
    bool strings_not_copied)
{
  unsigned ba0_int_p size;
  ba0_int_p i;

  size = ba0_sizeof_table ((struct ba0_table *) T, code);
  for (i = 0; i < T->size; i++)
    size += bav_sizeof_block (T->tab[i], ba0_isolated, strings_not_copied);
  return size;
}

/*
 * texinfo: bav_R_set_block
 * Copy @var{src} into @var{dst} without performing any string allocation.
 * The strings occurring in @var{src} are supposed to be present in @var{R}.
 * Each time a string has to be assigned, its copy in @var{R} is used.
 * The size needed for the copy is the one returned by
 * @code{bav_sizeof_block}.
 */

BAV_DLL void
bav_R_set_block (
    struct bav_block *dst,
    struct bav_block *src,
    struct bav_differential_ring *R)
{
  dst->subr = src->subr;
  ba0_set_tableof_range_indexed_group_with_tableof_string (&dst->rigs,
      &src->rigs, &R->dict_str_to_str, &R->strs);
}

/*
 * texinfo: bav_R_set_tableof_block
 * Copy @var{src} into @var{dst} without performing any string allocation
 * by using @code{bav_R_set_block}. See this function.
 */

BAV_DLL void
bav_R_set_tableof_block (
    struct bav_tableof_block *dst,
    struct bav_tableof_block *src,
    struct bav_differential_ring *R)
{
  ba0_int_p i;

  ba0_realloc2_table ((struct ba0_table *) dst, src->size,
      (ba0_new_function *) & bav_new_block);
  for (i = 0; i < src->size; i++)
    bav_R_set_block (dst->tab[i], src->tab[i], R);
  dst->size = src->size;
}
