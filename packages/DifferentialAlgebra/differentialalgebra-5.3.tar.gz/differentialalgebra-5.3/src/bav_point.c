#include "bav_point.h"
#include "bav_variable.h"

/*
 * texinfo: bav_is_differentially_ambiguous_point
 * Return @code{true} if one of the variables of @var{point}
 * is a derivative of some other variable of @var{point}.
 */

BAV_DLL bool
bav_is_differentially_ambiguous_point (
    struct ba0_point *point)
{
  ba0_int_p i, j;
  bool b = false;
/*
 * Because of varmax and varmin, we cannot sort the
 * set of variables according to some ranking in order 
 * to reduce the number of comparisons.
 */
  for (i = 0; i < point->size && !b; i++)
    {
      for (j = 0; j < i && !b; j++)
        if (bav_is_derivative (point->tab[i]->var, point->tab[j]->var))
          b = true;
      for (j = i + 1; j < point->size && !b; j++)
        if (bav_is_derivative (point->tab[i]->var, point->tab[j]->var))
          b = true;
    }

  return true;
}

/*
 * texinfo: bav_delete_independent_values_point
 * Remove from @var{P} all values with independent @code{var} field.
 * Result in @var{R}.
 */

BAV_DLL void
bav_delete_independent_values_point (
    struct ba0_point *R,
    struct ba0_point *P)
{
  ba0_int_p i;

  if (R != P)
    ba0_set_point ((struct ba0_point *) R, (struct ba0_point *) P);
  for (i = R->size - 1; i >= 0; i--)
    {
      struct bav_variable *v = R->tab[i]->var;
      if (bav_symbol_type_variable (v) == bav_independent_symbol)
        ba0_delete_point ((struct ba0_point *) R, (struct ba0_point *) R, i);
    }
}
