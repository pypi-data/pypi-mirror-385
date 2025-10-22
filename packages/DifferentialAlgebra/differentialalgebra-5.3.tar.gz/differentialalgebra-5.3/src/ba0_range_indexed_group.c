#include "ba0_global.h"
#include "ba0_exception.h"
#include "ba0_stack.h"
#include "ba0_garbage.h"
#include "ba0_basic_io.h"
#include "ba0_analex.h"
#include "ba0_scanf.h"
#include "ba0_printf.h"
#include "ba0_indexed_string.h"
#include "ba0_array.h"
#include "ba0_dictionary_string.h"

/*
 * texinfo: ba0_set_settings_range_indexed_group
 * Set the range operator and the string for infinity used for
 * printing range indexed groups to @var{oper} and @var{infinity}.
 * Set the bool which determines whether the right-hand side of
 * range indices should be included or excluded in ranges to @var{rhs_included}.
 * Set the bool which indicates whether range indexed groups which are
 * not plain strings should be quoted when printed.
 * All these arguments may be zero. In such cases, default values 
 * are restored.
 */

BA0_DLL void
ba0_set_settings_range_indexed_group (
    char *oper,
    char *infinity,
    bool rhs_included,
    bool protect_from_evaluation)
{
  if (oper)
    ba0_initialized_global.range_indexed_group.oper = oper;
  else
    ba0_initialized_global.range_indexed_group.oper =
        BA0_RANGE_INDEXED_GROUP_OPER;
  if (infinity)
    ba0_initialized_global.range_indexed_group.infinity = infinity;
  else
    ba0_initialized_global.range_indexed_group.infinity =
        BA0_RANGE_INDEXED_GROUP_INFINITY;
  ba0_initialized_global.range_indexed_group.rhs_included = rhs_included;
  ba0_initialized_global.range_indexed_group.quote_PFE =
      protect_from_evaluation;
}

/*
 * texinfo: ba0_get_settings_range_indexed_group
 * Assign to *@var{oper} and *@var{infinity} the strings used 
 * to print the range operator and the infinity string when printing.
 * Assign to *@var{rhs_included} the bool which determines whether
 * the right-hand side of range indices should be included or not
 * in the ranges.
 * Assign to *@var{protect_from_evaluation} the bool which indicates
 * if the range indexed groups which are not plain strings should be
 * quoted when printed.
 * All arguments are allowed to be zero.
 */

BA0_DLL void
ba0_get_settings_range_indexed_group (
    char **oper,
    char **infinity,
    bool *rhs_included,
    bool *protect_from_evaluation)
{
  if (oper)
    *oper = ba0_initialized_global.range_indexed_group.oper;
  if (infinity)
    *infinity = ba0_initialized_global.range_indexed_group.infinity;
  if (rhs_included)
    *rhs_included = ba0_initialized_global.range_indexed_group.rhs_included;
  if (protect_from_evaluation)
    *protect_from_evaluation =
        ba0_initialized_global.range_indexed_group.quote_PFE;
}

/*
 * texinfo: ba0_sizeof_range_indexed_group
 * Return the size needed to perform a copy of @var{G}.
 * If @var{code} is @code{ba0_embedded} then @var{G} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account.
 * If @var{strings_not_copied} is @code{true} then the range indexed strings
 * are supposed not to be copied.
 */

BA0_DLL unsigned ba0_int_p
ba0_sizeof_range_indexed_group (
    struct ba0_range_indexed_group *G,
    enum ba0_garbage_code code,
    bool strings_not_copied)
{
  unsigned ba0_int_p size;

  if (code == ba0_isolated)
    size = ba0_allocated_size (sizeof (struct ba0_range_indexed_group));
  else
    size = 0;
  size += ba0_sizeof_arrayof_double (&G->lhs, ba0_embedded);
  size += ba0_sizeof_arrayof_double (&G->rhs, ba0_embedded);
  if (strings_not_copied)
    size += ba0_sizeof_table ((struct ba0_table *) &G->strs, ba0_embedded);
  else
    size += ba0_sizeof_tableof_string (&G->strs, ba0_embedded);
  return size;
}

/*
 * texinfo: ba0_sizeof_tableof_range_indexed_group
 * Return the size needed to perform a copy of @var{T}.
 * If @var{code} is @code{ba0_embedded} then @var{T} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account.
 * If @var{strings_not_copied} is @code{true} then the radicals of the 
 * range indexed strings of @var{T} are supposed not to be copied.
 */

BA0_DLL unsigned ba0_int_p
ba0_sizeof_tableof_range_indexed_group (
    struct ba0_tableof_range_indexed_group *T,
    enum ba0_garbage_code code,
    bool strings_not_copied)
{
  unsigned ba0_int_p size;
  ba0_int_p i;

  size = ba0_sizeof_table ((struct ba0_table *) T, code);
  for (i = 0; i < T->size; i++)
    size += ba0_sizeof_range_indexed_group (T->tab[i], ba0_isolated,
        strings_not_copied);
  return size;
}

/*
 * texinfo: ba0_set_tableof_string_tableof_range_indexed_group
 * Store in @var{T} all the range indexed strings occurring in @var{rigs}.
 * The strings are not duplicated.
 */

BA0_DLL void
ba0_set_tableof_string_tableof_range_indexed_group (
    struct ba0_tableof_string *T,
    struct ba0_tableof_range_indexed_group *rigs)
{
  ba0_int_p counter, i, j;

  counter = 0;
  for (i = 0; i < rigs->size; i++)
    counter += rigs->tab[i]->strs.size;

  ba0_reset_table ((struct ba0_table *) T);
  ba0_realloc_table ((struct ba0_table *) T, counter);
  for (i = 0; i < rigs->size; i++)
    for (j = 0; j < rigs->tab[i]->strs.size; j++)
      T->tab[T->size++] = rigs->tab[i]->strs.tab[j];
}

/*
 * texinfo: ba0_set_range_indexed_group_with_tableof_string
 * Assign @var{src} to @var{dst} without any duplication of
 * the radicals of the range indexed strings.
 * Indeed, each radical in @var{src} has a copy in @var{T}
 * whose index is supposed to be registered in @var{D}.
 * Instead of duplicating strings, the copies are used.
 * Exception @code{BA0_ERRALG} is raised if some string
 * is not found in @var{D}.
 */

BA0_DLL void
ba0_set_range_indexed_group_with_tableof_string (
    struct ba0_range_indexed_group *dst,
    struct ba0_range_indexed_group *src,
    struct ba0_dictionary_string *D,
    struct ba0_tableof_string *T)
{
  ba0_int_p i;

  ba0_set_array ((struct ba0_array *) &dst->lhs,
      (struct ba0_array *) &src->lhs);
  ba0_set_array ((struct ba0_array *) &dst->rhs,
      (struct ba0_array *) &src->rhs);
  ba0_reset_table ((struct ba0_table *) &dst->strs);
  ba0_realloc_table ((struct ba0_table *) &dst->strs, src->strs.size);
  for (i = 0; i < src->strs.size; i++)
    {
      ba0_int_p j = ba0_get_dictionary_string (D, (struct ba0_table *) T,
          src->strs.tab[i]);
      if (j == BA0_NOT_AN_INDEX)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
      dst->strs.tab[i] = T->tab[j];
    }
  dst->strs.size = src->strs.size;
}

/*
 * texinfo: ba0_set_tableof_range_indexed_group_with_tableof_string
 * Assign @var{src} to @var{dst} without any duplication of
 * the radicals of the range indexed strings.
 * Indeed, each radical in @var{src} has a copy in @var{T}
 * whose index is supposed to be registered in @var{D}.
 * Instead of duplicating strings, the copies are used.
 * Exception @code{BA0_ERRALG} is raised if some string is
 * not found in @var{D}.
 * This function is called by @code{bav_R_set_differential_ring}
 * and @code{bav_R_new_ordering}.
 */

BA0_DLL void
ba0_set_tableof_range_indexed_group_with_tableof_string (
    struct ba0_tableof_range_indexed_group *dst,
    struct ba0_tableof_range_indexed_group *src,
    struct ba0_dictionary_string *D,
    struct ba0_tableof_string *T)
{
  ba0_int_p i;
/*
 * Resize dst 
 */
  ba0_reset_table ((struct ba0_table *) dst);
  ba0_realloc2_table ((struct ba0_table *) dst, src->size,
      (ba0_new_function *) & ba0_new_range_indexed_group);
  for (i = 0; i < src->size; i++)
    ba0_set_range_indexed_group_with_tableof_string (dst->tab[i], src->tab[i],
        D, T);
  dst->size = src->size;
}

/*
 * texinfo: ba0_init_range_indexed_group
 * Initialize @var{G} to the empty range indexed group.
 */

BA0_DLL void
ba0_init_range_indexed_group (
    struct ba0_range_indexed_group *G)
{
  ba0_init_array ((struct ba0_array *) &G->lhs);
  ba0_init_array ((struct ba0_array *) &G->rhs);
  ba0_init_table ((struct ba0_table *) &G->strs);
}

/*
 * texinfo: ba0_reset_range_indexed_group
 * Reset @var{G} to the empty range indexed group.
 */

BA0_DLL void
ba0_reset_range_indexed_group (
    struct ba0_range_indexed_group *G)
{
  ba0_reset_array ((struct ba0_array *) &G->lhs);
  ba0_reset_array ((struct ba0_array *) &G->rhs);
  ba0_reset_table ((struct ba0_table *) &G->strs);
}

/*
 * texinfo: ba0_new_range_indexed_group
 * Allocate a new range indexed group, initialize it and return it.
 */

BA0_DLL struct ba0_range_indexed_group *
ba0_new_range_indexed_group (
    void)
{
  struct ba0_range_indexed_group *G;

  G = (struct ba0_range_indexed_group *) ba0_alloc (sizeof (struct
          ba0_range_indexed_group));
  ba0_init_range_indexed_group (G);
  return G;
}

/*
 * texinfo: ba0_set_range_indexed_group
 * Assign (a full copy of) @var{src} to @var{dst}.
 */

BA0_DLL void
ba0_set_range_indexed_group (
    struct ba0_range_indexed_group *dst,
    struct ba0_range_indexed_group *src)
{
  if (dst != src)
    {
      ba0_int_p i;

      ba0_set_array ((struct ba0_array *) &dst->lhs,
          (struct ba0_array *) &src->lhs);
      ba0_set_array ((struct ba0_array *) &dst->rhs,
          (struct ba0_array *) &src->rhs);
      ba0_reset_table ((struct ba0_table *) &dst->strs);
      ba0_realloc_table ((struct ba0_table *) &dst->strs, src->strs.size);
      for (i = 0; i < src->strs.size; i++)
        dst->strs.tab[i] = ba0_strdup (src->strs.tab[i]);
      dst->strs.size = src->strs.size;
    }
}

/*
 * texinfo: ba0_set_range_indexed_group_string
 * Assign @var{string} to @var{G} as a plain string.
 * The string is not duplicated.
 */

BA0_DLL void
ba0_set_range_indexed_group_string (
    struct ba0_range_indexed_group *G,
    char *string)
{
  ba0_reset_array ((struct ba0_array *) &G->lhs);
  ba0_reset_array ((struct ba0_array *) &G->rhs);
  ba0_reset_table ((struct ba0_table *) &G->strs);
  ba0_realloc_table ((struct ba0_table *) &G->strs, 1);
  G->strs.tab[0] = string;
  G->strs.size = 1;
}

/*
 * texinfo: ba0_is_plain_string_range_indexed_group
 * Return @code{true} if @var{G} is a plain string, else @code{false}.
 * In any case, if @var{string} is nonzero then *@var{string}
 * is assigned the first range indexed string of @var{G}.
 */

BA0_DLL bool
ba0_is_plain_string_range_indexed_group (
    struct ba0_range_indexed_group *G,
    char **string)
{
  bool b;

  if (G->strs.size == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (string)
    *string = G->strs.tab[0];

  b = G->strs.size == 1 && G->lhs.size == 0;

  return b;
}

BA0_DLL bool
ba0_compatible_indices_range_indexed_group (
    struct ba0_range_indexed_group *G,
    struct ba0_range_indexed_group *H)
{
  ba0_int_p i;
  bool b;

  if (G->lhs.size != H->lhs.size)
    return false;

  b = true;
  if (ba0_initialized_global.range_indexed_group.rhs_included)
    {
      for (i = 0; i < G->lhs.size && b; i++)
        if (!((G->lhs.tab[i] == H->lhs.tab[i] &&
                    G->rhs.tab[i] == H->rhs.tab[i]) ||
                (G->lhs.tab[i] == H->rhs.tab[i] &&
                    G->rhs.tab[i] == H->lhs.tab[i])))
          b = false;
    }
  else
    {
      for (i = 0; i < G->lhs.size && b; i++)
        {
          ba0_int_p delta;
          if (G->lhs.tab[i] <= G->rhs.tab[i])
            delta = 1;
          else
            delta = -1;
          if (!((G->lhs.tab[i] == H->lhs.tab[i] &&
                      G->rhs.tab[i] == H->rhs.tab[i]) ||
                  (G->lhs.tab[i] == H->rhs.tab[i] + delta &&
                      G->rhs.tab[i] == H->lhs.tab[i] + delta)))
            b = false;
        }
    }
  return b;
}

/*
 * texinfo: ba0_fit_range_indexed_group
 * Return @code{true} if @var{radical}[@var{indices}] fits @var{G} else
 * @code{false}. The string @var{radical} must be equal to some element
 * of the field @code{strs} of @var{G}. Each @math{i} in @var{indices}
 * must belong to the corresponding range of @var{G}.
 * In the positive case, if @var{index} is nonzero, then *@var{index} is
 * assigned the index of @var{radical} in the field @code{strs} of @var{G}.
 */

BA0_DLL bool
ba0_fit_range_indexed_group (
    struct ba0_range_indexed_group *G,
    char *radical,
    struct ba0_tableof_int_p *indices,
    ba0_int_p *index)
{
  ba0_int_p i;
  bool b;

  if (indices->size != G->lhs.size)
    return false;

  b = false;
  i = 0;
  while (i < G->strs.size && !b)
    {
      if (strcmp (G->strs.tab[i], radical) == 0)
        b = true;
      else
        i += 1;
    }
  if (!b)
    return false;

  if (ba0_initialized_global.range_indexed_group.rhs_included)
    {
      for (i = 0; b && i < indices->size; i++)
        {
          if (G->lhs.tab[i] < G->rhs.tab[i])
            b = G->lhs.tab[i] <= indices->tab[i] &&
                indices->tab[i] <= G->rhs.tab[i];
          else
            b = G->rhs.tab[i] <= indices->tab[i] &&
                indices->tab[i] <= G->lhs.tab[i];
        }
    }
  else
    {
      for (i = 0; b && i < indices->size; i++)
        {
          if (G->lhs.tab[i] < G->rhs.tab[i])
            b = G->lhs.tab[i] <= indices->tab[i] &&
                indices->tab[i] < G->rhs.tab[i];
          else
            b = G->rhs.tab[i] < indices->tab[i] &&
                indices->tab[i] <= G->lhs.tab[i];
        }
    }
  return b;
}

/*
 * texinfo: ba0_fit_indices_range_indexed_group
 * Variant of @code{ba0_fit_range_indexed_group} where only
 * indices are checked.
 */

BA0_DLL bool
ba0_fit_indices_range_indexed_group (
    struct ba0_range_indexed_group *G,
    struct ba0_tableof_int_p *indices)
{
  ba0_int_p i;
  bool b;

  if (indices->size != G->lhs.size)
    return false;

  b = true;

  if (ba0_initialized_global.range_indexed_group.rhs_included)
    {
      for (i = 0; b && i < indices->size; i++)
        {
          if (G->lhs.tab[i] < G->rhs.tab[i])
            b = G->lhs.tab[i] <= indices->tab[i] &&
                indices->tab[i] <= G->rhs.tab[i];
          else
            b = G->rhs.tab[i] <= indices->tab[i] &&
                indices->tab[i] <= G->lhs.tab[i];
        }
    }
  else
    {
      for (i = 0; b && i < indices->size; i++)
        {
          if (G->lhs.tab[i] < G->rhs.tab[i])
            b = G->lhs.tab[i] <= indices->tab[i] &&
                indices->tab[i] < G->rhs.tab[i];
          else
            b = G->rhs.tab[i] < indices->tab[i] &&
                indices->tab[i] <= G->lhs.tab[i];
        }
    }
  return b;
}

static char _struct_range_indexed_group[] = "struct range_indexed_group";
static char _lhs[] = "arrayof_double.tab";
static char _rhs[] = "arrayof_double.tab";
static char _strs[] = "tableof_string.tab";

BA0_DLL ba0_int_p
ba0_garbage1_range_indexed_group (
    void *z,
    enum ba0_garbage_code code)
{
  struct ba0_range_indexed_group *G = (struct ba0_range_indexed_group *) z;
  ba0_int_p i, n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (G, sizeof (struct ba0_range_indexed_group),
        _struct_range_indexed_group);
  if (G->lhs.tab)
    n += ba0_new_gc_info (G->lhs.tab, G->lhs.alloc * G->lhs.sizelt, _lhs);
  if (G->rhs.tab)
    n += ba0_new_gc_info (G->rhs.tab, G->rhs.alloc * G->rhs.sizelt, _rhs);
  if (G->strs.tab)
    {
      n += ba0_new_gc_info (G->strs.tab, G->strs.alloc * sizeof (char *),
          _strs);
      for (i = 0; i < G->strs.alloc; i++)
        {
          if (G->strs.tab[i])
            n += ba0_garbage1_string (G->strs.tab[i], ba0_isolated);
        }
    }
  return n;
}

BA0_DLL void *
ba0_garbage2_range_indexed_group (
    void *z,
    enum ba0_garbage_code code)
{
  struct ba0_range_indexed_group *G;
  ba0_int_p i;

  if (code == ba0_isolated)
    G = (struct ba0_range_indexed_group *) ba0_new_addr_gc_info (z,
        _struct_range_indexed_group);
  else
    G = (struct ba0_range_indexed_group *) z;
  if (G->lhs.tab)
    G->lhs.tab = (double *) ba0_new_addr_gc_info (G->lhs.tab, _lhs);
  if (G->rhs.tab)
    G->rhs.tab = (double *) ba0_new_addr_gc_info (G->rhs.tab, _rhs);
  if (G->strs.tab)
    {
      G->strs.tab = (char **) ba0_new_addr_gc_info (G->strs.tab, _strs);
      for (i = 0; i < G->strs.alloc; i++)
        {
          if (G->strs.tab[i])
            G->strs.tab[i] = ba0_garbage2_string (G->strs.tab[i], ba0_isolated);
        }
    }
  return G;
}

BA0_DLL void *
ba0_copy_range_indexed_group (
    void *z)
{
  struct ba0_range_indexed_group *src = (struct ba0_range_indexed_group *) z;
  struct ba0_range_indexed_group *dst;

  dst = ba0_new_range_indexed_group ();
  ba0_set_range_indexed_group (dst, src);
  return dst;
}

/*
 * texinfo: ba0_printf_range_indexed_group
 * General printing function for range indexed groups.
 * It can be called using @code{ba0_printf/%range_indexed_group}.
 * The strings used for the range operator and the infinity can
 * be customized.
 */

BA0_DLL void
ba0_printf_range_indexed_group (
    void *z)
{
  struct ba0_range_indexed_group *G = (struct ba0_range_indexed_group *) z;
  char *string;
  ba0_int_p i;

  if (ba0_is_plain_string_range_indexed_group (G, &string))
    ba0_printf_string (string);
  else if (G->strs.size > 0)
    {
      if (ba0_initialized_global.range_indexed_group.quote_PFE)
        ba0_put_char ('\'');
      ba0_printf ("%t(%s)", &G->strs);
      if (G->lhs.size > 0)
        {
          ba0_put_char ('[');
          for (i = 0; i < G->lhs.size; i++)
            {
              double lhs = G->lhs.tab[i];
              double rhs = G->rhs.tab[i];
              if (i > 0)
                ba0_put_char (',');
              if (ba0_isinf (lhs))
                {
                  if (lhs < 0)
                    ba0_put_char ('-');
                  ba0_put_string (ba0_initialized_global.
                      range_indexed_group.infinity);
                }
              else
                ba0_printf ("%d", (ba0_int_p) lhs);
              ba0_put_string (ba0_initialized_global.range_indexed_group.oper);
              if (ba0_isinf (rhs))
                {
                  if (rhs < 0)
                    ba0_put_char ('-');
                  ba0_put_string (ba0_initialized_global.
                      range_indexed_group.infinity);
                }
              else
                ba0_printf ("%d", (ba0_int_p) rhs);
            }
          ba0_put_char (']');
        }
      if (ba0_initialized_global.range_indexed_group.quote_PFE)
        ba0_put_char ('\'');
    }
}

/*
 * texinfo: ba0_scanf_range_indexed_group
 * General parsing function for range indexed groups.
 * It can be called using @code{ba0_scanf/%range_indexed_group}.
 * The grammar is:
 * @verbatim
 * RIG ::= <radical>
 * RIG ::= "(" <non-empty sequence of radicals ")" 
 *                  "[" non-empty sequence of RANGE "]"
 * RANGE ::= <[-]integer | [-]infinity> <range operator> 
 *                  <[-]integer | [-]infinity>
 * @end verbatim
 * The accepted range operator may be customized but @code{":"}
 * and @code{".."} are allowed.
 * The accepted string for infinity may be customized but @code{"oo"},
 * @code{"inf"}, @code{"infty"} and @code{"infinity"} are allowed.
 */

BA0_DLL void *
ba0_scanf_range_indexed_group (
    void *z)
{
  struct ba0_range_indexed_group *G, *z_G;
/*
 * Work on a data structure different from z to avoid any corruption
 * on z in case of a raised exception
 */
  G = ba0_new_range_indexed_group ();

  if (!ba0_sign_token_analex ("("))
    {
/*
 * If no starting parenthesis then just read an indexed string
 */
      ba0_realloc_table ((struct ba0_table *) &G->strs, 1);
      G->strs.tab[0] = ba0_scanf_indexed_string_as_a_string (0);
      G->strs.size = 1;
    }
  else
    {
/*
 * Read a nonempty group of indexed strings surrounded by parentheses
 */
      ba0_scanf ("%t(%six)", &G->strs);
      if (G->strs.size == 0)
        BA0_RAISE_EXCEPTION (BA0_ERRSYN);
/*
 * Read [ lhs : rhs, lhs : rhs, ..., lhs : rhs ]
 * The separator is either ":" or ".."
 * lhs and rhs may be preceded by a minus sign
 * they are
 * - integers
 * - oo, inf, infty, infinity
 */
      ba0_get_token_analex ();
      if (ba0_sign_token_analex ("["))
        {
          do
            {
              bool negative;

              if (G->lhs.size == G->lhs.alloc)
                {
                  ba0_int_p new_alloc = 2 * G->lhs.alloc + 1;
                  ba0_realloc_array ((struct ba0_array *) &G->lhs,
                      new_alloc, sizeof (double));
                  ba0_realloc_array ((struct ba0_array *) &G->rhs,
                      new_alloc, sizeof (double));
                }
              ba0_get_token_analex ();
              if (ba0_sign_token_analex ("-"))
                {
                  negative = true;
                  ba0_get_token_analex ();
                }
              else
                negative = false;

              if (ba0_type_token_analex () == ba0_integer_token)
                G->lhs.tab[G->lhs.size] = ba0_atof (ba0_value_token_analex ());
              else if (ba0_type_token_analex () == ba0_string_token &&
                  (strcmp (ba0_value_token_analex (),
                          ba0_initialized_global.
                          range_indexed_group.infinity) == 0
                      || strcmp (ba0_value_token_analex (), "oo") == 0
                      || strcmp (ba0_value_token_analex (), "inf") == 0
                      || strcmp (ba0_value_token_analex (), "infty") == 0
                      || strcmp (ba0_value_token_analex (), "infinity") == 0))
                G->lhs.tab[G->lhs.size] = ba0_atof ("inf");
              else
                BA0_RAISE_EXCEPTION (BA0_ERRSYN);
              if (negative)
                G->lhs.tab[G->lhs.size] = -G->lhs.tab[G->lhs.size];
              G->lhs.size += 1;
              ba0_get_token_analex ();

              if (ba0_sign_token_analex
                  (ba0_initialized_global.range_indexed_group.oper))
                ba0_get_token_analex ();
              else if (ba0_sign_token_analex (":"))
                ba0_get_token_analex ();
              else if (ba0_sign_token_analex ("."))
                {
                  ba0_get_token_analex ();
                  if (!ba0_sign_token_analex ("."))
                    BA0_RAISE_EXCEPTION (BA0_ERRSYN);
                  ba0_get_token_analex ();
                }
              else
                BA0_RAISE_EXCEPTION (BA0_ERRSYN);

              if (ba0_sign_token_analex ("-"))
                {
                  negative = true;
                  ba0_get_token_analex ();
                }
              else
                negative = false;

              if (ba0_type_token_analex () == ba0_integer_token)
                G->rhs.tab[G->rhs.size] = ba0_atof (ba0_value_token_analex ());
              else if (ba0_type_token_analex () == ba0_string_token &&
                  (strcmp (ba0_value_token_analex (),
                          ba0_initialized_global.
                          range_indexed_group.infinity) == 0
                      || strcmp (ba0_value_token_analex (), "oo") == 0
                      || strcmp (ba0_value_token_analex (), "inf") == 0
                      || strcmp (ba0_value_token_analex (), "infty") == 0
                      || strcmp (ba0_value_token_analex (), "infinity") == 0))
                G->rhs.tab[G->rhs.size] = ba0_atof ("inf");
              else
                BA0_RAISE_EXCEPTION (BA0_ERRSYN);
              if (negative)
                G->rhs.tab[G->rhs.size] = -G->rhs.tab[G->rhs.size];
              G->rhs.size += 1;
              ba0_get_token_analex ();
            }
          while (ba0_sign_token_analex (","));
          if (!ba0_sign_token_analex ("]"))
            BA0_RAISE_EXCEPTION (BA0_ERRSYN);
        }
      else
        ba0_unget_token_analex (1);
    }

  if (z != (void *) 0)
    {
      z_G = (struct ba0_range_indexed_group *) z;
      ba0_set_range_indexed_group (z_G, G);
    }
  else
    z_G = G;

  return z_G;
}
