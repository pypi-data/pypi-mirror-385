#include "ba0_point.h"
#include "ba0_stack.h"
#include "ba0_global.h"

/*
 * texinfo: ba0_set_settings_value
 * Set to @var{equal_sign} the operator used for displaying values.
 */

BA0_DLL void
ba0_set_settings_value (
    char *equal_sign)
{
  ba0_initialized_global.value.equal_sign = equal_sign ? equal_sign : "=";
}

/*
 * texinfo: ba0_get_settings_value
 * Assign to *@var{equal_sign} the operator used to print values.
 */

BA0_DLL void
ba0_get_settings_value (
    char **equal_sign)
{
  if (equal_sign)
    *equal_sign = ba0_initialized_global.value.equal_sign;
}

/*
 * texinfo: ba0_init_value
 * Initialize @var{value} to the pair
 * (@code{BA0_NOT_A_VARIABLE}, @math{0}). Constructor.
 */

BA0_DLL void
ba0_init_value (
    struct ba0_value *value)
{
  value->var = BA0_NOT_A_VARIABLE;
  value->value = 0;
}

/*
 * texinfo: ba0_new_value
 * Allocate a new value, initialize it and return the result.
 */

BA0_DLL struct ba0_value *
ba0_new_value (
    void)
{
  struct ba0_value *value =
      (struct ba0_value *) ba0_alloc (sizeof (struct ba0_value));
  ba0_init_value (value);
  return value;
}

/*
 * texinfo: ba0_init_point
 * Initialize @var{point} to the empty point.
 */

BA0_DLL void
ba0_init_point (
    struct ba0_point *point)
{
  ba0_init_table ((struct ba0_table *) point);
}

/*
 * texinfo: ba0_new_point
 * Allocate a new point, initialize it and return it.
 */

BA0_DLL struct ba0_point *
ba0_new_point (
    void)
{
  struct ba0_point *point;
  point = (struct ba0_point *) ba0_alloc (sizeof (struct ba0_point));
  ba0_init_point (point);
  return point;
}


/*
 * texinfo: ba0_set_point
 * Store a copy of @var{src} to @var{dst}. The @code{struct ba0_value} 
 * @var{src} points to are duplicated but the @code{value} fields
 * of the @code{struct ba0_value} are not.
 */

BA0_DLL void
ba0_set_point (
    struct ba0_point *dst,
    struct ba0_point *src)
{
  ba0_int_p i;

  if (src != dst)
    {
      dst->size = 0;
      ba0_realloc2_table ((struct ba0_table *) dst, src->size,
          (ba0_new_function *) & ba0_new_value);
      for (i = 0; i < src->size; i++)
        {
          dst->tab[i]->var = src->tab[i]->var;
          dst->tab[i]->value = src->tab[i]->value;
        }
      dst->size = src->size;
    }
}

/*
 * texinfo: ba0_delete_point
 * Assign to @var{dst} a copy of @var{src} without its entry
 * number @var{index}.
 */

BA0_DLL void
ba0_delete_point (
    struct ba0_point *dst,
    struct ba0_point *src,
    ba0_int_p index)
{
  if (dst != src)
    ba0_set_point (dst, src);
  ba0_delete_table ((struct ba0_table *) dst, index);
}

static int
compare_value (
    const void *a,
    const void *b)
{
  struct ba0_value **aa = (struct ba0_value * *) a;
  struct ba0_value **bb = (struct ba0_value * *) b;

  return (int) (ba0_int_p) (*aa)->var - (int) (ba0_int_p) (*bb)->var;
}

/*
 * texinfo: ba0_sort_point
 * Sort the @code{tab} field of @var{src} by increasing addresses 
 * of @code{var} fields. This ordering is the one expected by many functions. 
 * Result in @var{dst}.
 */

BA0_DLL void
ba0_sort_point (
    struct ba0_point *dst,
    struct ba0_point *src)
{
  if (dst != src)
    ba0_set_point (dst, src);
  qsort (dst->tab, dst->size, sizeof (struct ba0_value *), &compare_value);
}

/*
 * texinfo: ba0_is_ambiguous_point
 * Return @code{true} if @var{point} contains two values
 * with the same variable. The point is supposed to be sorted.
 * See also @code{bav_is_differentially_ambiguous_point}.
 */

BA0_DLL bool
ba0_is_ambiguous_point (
    struct ba0_point *point)
{
  ba0_int_p i;
  for (i = 1; i < point->size; i++)
    if (point->tab[i] == point->tab[i - 1])
      return true;
  return false;
}

/*
 * texinfo: ba0_is_sorted_point
 * Return true if @code{ba0_bsearch_point} can be applied to @var{point},
 * false otherwise.
 */

BA0_DLL bool
ba0_is_sorted_point (
    struct ba0_point *point)
{
  ba0_int_p prev, cour, i;

  if (point->size < 2)
    return true;
  prev = (ba0_int_p) point->tab[0]->var;
  for (i = 1; i < point->size; i++)
    {
      cour = (ba0_int_p) point->tab[i]->var;
      if (prev - cour > 0)
        return false;
      prev = cour;
    }
  return true;
}

/*
 * texinfo: ba0_bsearch_point
 * Only applies to sorted points.
 * Return a value whose @code{var} field is @var{var}, the zero pointer if
 * no such value exists. If @var{index} is nonzero and a nonzero value
 * is returned, its index is stored in *@var{index}. If @var{index} is nonzero
 * the zero pointer is returned, *@var{index} receives the index in @code{tab}
 * which should receive @var{var}.
 */

BA0_DLL struct ba0_value *
ba0_bsearch_point (
    void *var,
    struct ba0_point *point,
    ba0_int_p *index)
{
  ba0_int_p i, j, m, c, p;
  bool found;

  found = false;
  i = 0;
  j = point->size;
  p = 0;
  while (i < j && !found)
    {
      m = (i + j) / 2;
      c = (ba0_int_p) var - (ba0_int_p) point->tab[m]->var;
      if (c > 0)
        {
          i = m + 1;
          p = i;
        }
      else if (c < 0)
        {
          j = m;
          p = j;
        }
      else
        {
          found = true;
          p = m;
        }
    }
  if (index)
    *index = p;
  return found ? point->tab[p] : BA0_NOT_A_VALUE;
}

/*
 * texinfo: ba0_assoc_point
 * Return a value whose @code{var} field is @var{var}, the zero pointer if
 * no such value exists. If @var{index} is nonzero and a nonzero value
 * is returned, its index is stored in *@var{index}. 
 */

BA0_DLL struct ba0_value *
ba0_assoc_point (
    void *var,
    struct ba0_point *point,
    ba0_int_p *index)
{
  ba0_int_p i;

  for (i = 0; i < point->size; i++)
    {
      if (point->tab[i]->var == var)
        {
          if (index != (ba0_int_p *) 0)
            *index = i;
          return point->tab[i];
        }
    }
  return BA0_NOT_A_VALUE;
}
