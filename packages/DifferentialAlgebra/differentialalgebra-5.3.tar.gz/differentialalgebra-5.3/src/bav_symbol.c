#include "bav_symbol.h"
#include "bav_differential_ring.h"
#include "bav_global.h"

/*
 * texinfo: bav_set_settings_symbol
 * Set to @var{scanf_symbol} the function which prints symbols.
 * Set to @var{printf_symbol} the function which prints symbols.
 * Set to @var{IndexedBase_PFE} the string used to protect the
 * radicals of the symbols which fit range indexed groups when 
 * they get printed.
 * If these parameters are zero, the settings variables are reset to their
 * default values.
 */

BAV_DLL void
bav_set_settings_symbol (
    ba0_scanf_function *scanf_symbol,
    ba0_printf_function *printf_symbol,
    char *IndexedBase_PFE)
{
  bav_initialized_global.symbol.scanf =
      scanf_symbol ? scanf_symbol : &bav_scanf_default_symbol;
  bav_initialized_global.symbol.printf =
      printf_symbol ? printf_symbol : &bav_printf_default_symbol;
  bav_initialized_global.symbol.IndexedBase_PFE = IndexedBase_PFE;
}

/*
 * texinfo: bav_get_settings_symbol
 * Assign to *@var{scanf_symbol} the function which prints symbols.
 * Assign to *@var{printf_symbol} the function which prints symbols.
 * Assign to *@var{IndexedBase_PFE} the string used to protect the
 * radicals of the symbols which fit range indexed groups when 
 * they get printed.
 * Each argument may be zero.
 */

BAV_DLL void
bav_get_settings_symbol (
    ba0_scanf_function **scanf_symbol,
    ba0_printf_function **printf_symbol,
    char **IndexedBase_PFE)
{
  if (scanf_symbol)
    *scanf_symbol = bav_initialized_global.symbol.scanf;
  if (printf_symbol)
    *printf_symbol = bav_initialized_global.symbol.printf;
  if (IndexedBase_PFE)
    *IndexedBase_PFE = bav_initialized_global.symbol.IndexedBase_PFE;
}

/*
 * texinfo: bav_init_symbol
 * Initialize @var{s} to the empty symbol.
 */

BAV_DLL void
bav_init_symbol (
    struct bav_symbol *y)
{
  y->ident = (char *) 0;
  y->type = bav_independent_symbol;
  y->index_in_syms = BA0_NOT_AN_INDEX;
  y->index_in_rigs = BA0_NOT_AN_INDEX;
  ba0_init_table ((struct ba0_table *) &y->subscripts);
  y->derivation_index = BA0_NOT_AN_INDEX;
  y->index_in_pars = BA0_NOT_AN_INDEX;
}

/*
 * texinfo: bav_new_symbol
 * Allocate a new symbol, initialize it and return it.
 */

BAV_DLL struct bav_symbol *
bav_new_symbol (
    void)
{
  struct bav_symbol *y;

  y = (struct bav_symbol *) ba0_alloc (sizeof (struct bav_symbol));
  bav_init_symbol (y);
  return y;
}

/*
 * texinfo: bav_not_a_symbol
 * Return the constant @code{BAV_NOT_A_SYMBOL}.
 */

BAV_DLL struct bav_symbol *
bav_not_a_symbol (
    void)
{
  return BAV_NOT_A_SYMBOL;
}

/*
 * texinfo: bav_is_subscripted_symbol
 * Return @code{true} if @var{y} fits a range indexed group
 * (hence has subscripts) else @code{false}.
 */

BAV_DLL bool
bav_is_subscripted_symbol (
    struct bav_symbol *y)
{
  return y->index_in_rigs != BA0_NOT_AN_INDEX;
}

/*
 * texinfo: bav_subscript_of_symbol
 * Return the subscript of @var{y}, assuming that @var{y}
 * fits a range indexed string and has a single subscript.
 * Exception @code{BA0_ERRALG} is raised if @var{y} does not
 * fit any range indexed string.
 * Exception @code{BA0_ERRNYP} is raised if @var{y} has more
 * than one subscript.
 */

BAV_DLL ba0_int_p
bav_subscript_of_symbol (
    struct bav_symbol *y)
{
  if (y->subscripts.size == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  if (y->subscripts.size > 1)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);
  return y->subscripts.tab[0];
}

/*
 * texinfo: bav_sizeof_symbol
 * Return the size needed to copy @var{y}.
 * If @var{code} is @code{ba0_embedded} then @var{y} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account.
 * If @var{strings_not_copied} then the strings occurring in @var{y}
 * are supposed not to be copied.
 */

BAV_DLL unsigned ba0_int_p
bav_sizeof_symbol (
    struct bav_symbol *y,
    enum ba0_garbage_code code,
    bool strings_not_copied)
{
  unsigned ba0_int_p size;

  if (code == ba0_isolated)
    size = ba0_allocated_size (sizeof (struct bav_symbol));
  else
    size = 0;
  if (!strings_not_copied)
    size += ba0_allocated_size (strlen (y->ident) + 1);
  size += ba0_sizeof_table ((struct ba0_table *) &y->subscripts, ba0_embedded);
  return size;
}

/*
 * texinfo: bav_R_set_symbol
 * This low level function assigns @var{src} to @var{dst}.
 * The field @code{ident} of @var{dst} is however given by @var{ident}.
 */

BAV_DLL void
bav_R_set_symbol (
    struct bav_symbol *dst,
    struct bav_symbol *src,
    char *ident)
{
  dst->ident = ident;
  dst->type = src->type;
  dst->index_in_syms = src->index_in_syms;
  dst->index_in_rigs = src->index_in_rigs;
  ba0_set_table ((struct ba0_table *) &dst->subscripts,
      (struct ba0_table *) &src->subscripts);
  dst->derivation_index = src->derivation_index;
  dst->index_in_pars = src->index_in_pars;
}

/*
 * texinfo: bav_is_a_derivation
 * Return @code{true} if @var{string} is equal to the @code{ident}
 * field of an existing derivation.
 */

BAV_DLL bool
bav_is_a_derivation (
    char *string)
{
  return bav_R_string_to_existing_derivation (string) != BAV_NOT_A_SYMBOL;
}

/*
 * texinfo: bav_switch_ring_symbol
 * Return the symbol of @var{R} which has the same index in 
 * @code{R->syms} as @var{y}. This low level function should be used 
 * in conjunction with @code{bav_set_differential_ring}: 
 * if @var{R} is a ring obtained by application of 
 * @code{bav_set_differential_ring} to the ring @var{y} refers to, 
 * then this function returns the element of @var{R} which corresponds 
 * to @var{y}.
 */

BAV_DLL struct bav_symbol *
bav_switch_ring_symbol (
    struct bav_symbol *y,
    struct bav_differential_ring *R)
{
  return R->syms.tab[y->index_in_syms];
}

/* 
 * texinfo: bav_scanf_default_symbol
 * The default function for parsing symbols, called by @code{ba0_scanf/%y}. 
 * A symbol is denoted by any indexed string the last indexed string
 * indices of which is not formed of derivations.
 * Exception @code{BAV_ERRUSY} is raised if the symbol is not recognized.
 */

BAV_DLL void *
bav_scanf_default_symbol (
    void *z)
{
  struct ba0_indexed_string *indexed;
  struct bav_variable *v;
  struct bav_symbol *y;
  struct ba0_mark M;
  ba0_int_p counter;

  ba0_push_another_stack ();
  ba0_record (&M);
  indexed = ba0_scanf_indexed_string_with_counter (0, &counter);
  ba0_pull_stack ();

  if (ba0_has_trailing_indices_indexed_string (indexed, &bav_is_a_derivation))
    {
      ba0_unget_token_analex (counter + 1);
      indexed->Tindic.size -= 1;
    }

  v = bav_indexed_string_to_variable (indexed);
  if (v == BAV_NOT_A_VARIABLE)
    {
      (*bav_initialized_global.common.unknown) (indexed);
      BA0_RAISE_PARSER_EXCEPTION (BAV_ERRUSY);
    }

  y = v->root;

  if (z != (void *) 0)
    *(struct bav_symbol * *) z = y;
  ba0_restore (&M);
  return y;
}

/* 
 * texinfo: bav_scanf2_symbol
 * Variant of @code{bav_scanf_default_symbol} which requires the symbol
 * to be followed by a sequence of indexed string indices.
 * The sequence is not part of the symbol.
 * Exception @code{BAV_ERRUSY} is raised if the symbol is not recognized.
 * Exception @code{BA0_ERRSYN} if the mandatory sequence of
 * indexed string indices is missing.
 */

BAV_DLL void *
bav_scanf2_symbol (
    void *z)
{
  struct ba0_indexed_string *indexed;
  struct bav_variable *v;
  struct bav_symbol *y;
  struct ba0_mark M;
  ba0_int_p counter;

  ba0_push_another_stack ();
  ba0_record (&M);
  indexed = ba0_scanf_indexed_string_with_counter (0, &counter);
  ba0_pull_stack ();

  if (indexed->Tindic.size == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRSYN);

  ba0_unget_token_analex (counter + 1);
  indexed->Tindic.size -= 1;

  v = bav_indexed_string_to_variable (indexed);
  if (v == BAV_NOT_A_VARIABLE)
    {
      (*bav_initialized_global.common.unknown) (indexed);
      BA0_RAISE_PARSER_EXCEPTION (BAV_ERRUSY);
    }

  y = v->root;

  if (z != (void *) 0)
    *(struct bav_symbol * *) z = y;
  ba0_restore (&M);
  return y;
}

/*
 * texinfo: bav_printf_default_symbol
 * The default function for printing symbols (the @code{ident} field
 * is printed).
 * It is called by @code{ba0_printf/%y}.
 */

BAV_DLL void
bav_printf_default_symbol (
    void *z)
{
  struct bav_symbol *y = (struct bav_symbol *) z;
  if (y->index_in_rigs == BA0_NOT_AN_INDEX ||
      bav_initialized_global.symbol.IndexedBase_PFE == (char *) 0)
    ba0_put_string (y->ident);
  else
    {
      char *radical = bav_global.R.rigs.tab[y->index_in_rigs]->strs.tab[0];
      ba0_int_p i;

      ba0_put_string (bav_initialized_global.symbol.IndexedBase_PFE);
      ba0_put_string ("('");
      ba0_put_string (radical);
      ba0_put_string ("')");
      ba0_put_char ('[');
      for (i = 0; i < y->subscripts.size; i++)
        {
          if (i > 0)
            ba0_put_char (',');
          ba0_put_int_p (y->subscripts.tab[i]);
        }
      ba0_put_char (']');
    }
}

/*
 * texinfo: bav_printf_numbered_symbol
 * A possible function for printing symbols (an underscore
 * followed by the value of the @code{index_in_syms} field of the symbol.
 */

BAV_DLL void
bav_printf_numbered_symbol (
    void *z)
{
  struct bav_symbol *s = (struct bav_symbol *) z;

  if (s->type == bav_independent_symbol || s->type == bav_dependent_symbol)
    ba0_printf ("%s%d", "_", s->index_in_syms);
  else
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
}

/*
 * texinfo: bav_scanf_symbol
 * The general parsing function for symbols.
 * It is called by @code{ba0_scanf/%y}.
 */

BAV_DLL void *
bav_scanf_symbol (
    void *z)
{
  void *r = (void *) 0;

  if (bav_initialized_global.symbol.scanf != (ba0_scanf_function *) 0)
    r = (*bav_initialized_global.symbol.scanf) (z);
  else
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  return r;
}

/*
 * texinfo: bav_printf_symbol
 * The general printing function for symbols.
 * It is called by @code{ba0_printf/%y}.
 */

BAV_DLL void
bav_printf_symbol (
    void *z)
{
  if (bav_initialized_global.symbol.printf != (ba0_printf_function *) 0)
    (*bav_initialized_global.symbol.printf) (z);
  else
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
}
