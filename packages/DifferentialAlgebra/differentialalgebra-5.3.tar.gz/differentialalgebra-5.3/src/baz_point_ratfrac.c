#include "baz_point_ratfrac.h"

/*
 * texinfo: baz_init_value_ratfrac
 * Initialize @var{V}.
 * The @code{var} field is initialized at @code{BAV_NOT_A_VARIABLE}.
 */

BAZ_DLL void
baz_init_value_ratfrac (
    struct baz_value_ratfrac *V)
{
  V->var = BAV_NOT_A_VARIABLE;
  V->value = baz_new_ratfrac ();
}

/*
 * texinfo: baz_new_value_ratfrac
 * Allocate a new @code{struct baz_value_ratfrac}, initialize it
 * and return it.
 */

BAZ_DLL struct baz_value_ratfrac *
baz_new_value_ratfrac (
    void)
{
  struct baz_value_ratfrac *V;
  V = (struct baz_value_ratfrac *) ba0_alloc (sizeof (struct
          baz_value_ratfrac));
  baz_init_value_ratfrac (V);
  return V;
}

/*
 * texinfo: baz_set_value_ratfrac
 * Assign @var{src} to @var{dst}.
 */

BAZ_DLL void
baz_set_value_ratfrac (
    struct baz_value_ratfrac *dst,
    struct baz_value_ratfrac *src)
{
  if (dst != src)
    {
      dst->var = src->var;
      baz_set_ratfrac (dst->value, src->value);
    }
}

/*
 * texinfo: baz_set_point_ratfrac
 * Assign @var{src} to @var{dst}.
 */

BAZ_DLL void
baz_set_point_ratfrac (
    struct baz_point_ratfrac *dst,
    struct baz_point_ratfrac *src)
{
  if (dst != src)
    {
      ba0_int_p i;

      ba0_realloc2_table ((struct ba0_table *) dst, src->size,
          (ba0_new_function *) & baz_new_value_ratfrac);
      for (i = 0; i < src->size; i++)
        baz_set_value_ratfrac (dst->tab[i], src->tab[i]);
      dst->size = src->size;
    }
}

/*
 * texinfo: baz_prolongate_point_ratfrac_variable
 * If @var{v} is a proper derivative of the @code{var} field of some
 * value in @var{P}, extend @var{P} with new values obtained by
 * differentiation (including one with @code{var} field equal to @var{v}). 
 * If @var{v} is not a proper derivative of the @code{var} field of some
 * value in @var{P}, the point is left unchanged.
 * The resulting point is stored in @var{R}.
 */

BAZ_DLL void
baz_prolongate_point_ratfrac_variable (
    struct baz_point_ratfrac *R,
    struct baz_point_ratfrac *P,
    struct bav_variable *v)
{
  bool found;
  ba0_int_p i;

  if (R != P)
    ba0_set_point ((struct ba0_point *) R, (struct ba0_point *) P);

  if (ba0_bsearch_point (v, (struct ba0_point *) R, (ba0_int_p *) 0))
    return;

  found = false;
  i = 0;
  while (i < P->size && !found)
    {
      if (bav_is_proper_derivative (v, P->tab[i]->var))
        found = true;
      else
        i += 1;
    }
  if (found)
    {
      struct baz_ratfrac *F;
      struct bav_term theta;
      struct bav_variable *w;
      bav_Idegree d;
      struct ba0_mark M;

      w = P->tab[i]->var;
      F = P->tab[i]->value;

      ba0_push_another_stack ();
      ba0_record (&M);
      bav_init_term (&theta);
      bav_operator_between_derivatives (&theta, v, w);
      d = bav_total_degree_term (&theta);
      ba0_pull_stack ();

      ba0_realloc2_table ((struct ba0_table *) R, R->size + d,
          (ba0_new_function *) & baz_new_value_ratfrac);

      for (i = 0; i < theta.size; i++)
        {
          struct bav_symbol *x;
          ba0_int_p j;

          x = theta.rg[i].var->root;
          for (j = 0; j < theta.rg[i].deg; j++)
            {
              w = bav_diff_variable (w, x);
              R->tab[R->size]->var = w;
              baz_diff_ratfrac (R->tab[R->size]->value, F, x);
              F = R->tab[R->size]->value;
              R->size += 1;
            }
        }

      ba0_restore (&M);
      ba0_sort_point ((struct ba0_point *) R, (struct ba0_point *) R);
    }
}

/*
 * texinfo: baz_prolongate_point_ratfrac_term
 * Apply @code{baz_prolongate_point_ratfrac_variable} to each
 * variable occurring in @var{term}. Result in @var{R}.
 */

BAZ_DLL void
baz_prolongate_point_ratfrac_term (
    struct baz_point_ratfrac *R,
    struct baz_point_ratfrac *P,
    struct bav_term *term)
{
  ba0_int_p i;

  if (P != R)
    ba0_set_point ((struct ba0_point *) R, (struct ba0_point *) P);
  for (i = 0; i < term->size; i++)
    baz_prolongate_point_ratfrac_variable (R, R, term->rg[i].var);
}

/*
 * texinfo: baz_prolongate_point_ratfrac_using_pattern_variable
 * Assign to @var{R} the point obtained by adding to @var{P}
 * one entry for @var{v} using @var{pattern}.
 * If @var{v} does not match @var{pattern} then @var{R} is
 * equal to @var{P}.
 */

BAZ_DLL void
baz_prolongate_point_ratfrac_using_pattern_variable (
    struct baz_point_ratfrac *R,
    struct baz_point_ratfrac *P,
    struct baz_prolongation_pattern *pattern,
    struct bav_variable *v)
{
  ba0_int_p i, j;

  if (R != P)
    ba0_set_point ((struct ba0_point *) R, (struct ba0_point *) P);

  if (ba0_bsearch_point (v, (struct ba0_point *) R, (ba0_int_p *) 0))
    return;

  if (ba0_member2_table (v->root, (struct ba0_table *) &pattern->deps, &i))
    {
      struct ba0_tableof_string vals;
      struct ba0_mark M;

      if (R->size == R->alloc)
        {
          ba0_int_p new_alloc = 2 * R->alloc + 1;
          ba0_realloc2_table ((struct ba0_table *) R, new_alloc,
              (ba0_new_function *) & baz_new_value_ratfrac);
        }

      ba0_push_another_stack ();
      ba0_record (&M);
      ba0_init_table ((struct ba0_table *) &vals);
      ba0_realloc_table ((struct ba0_table *) &vals, pattern->idents.size);

      for (j = 0; j < pattern->idents.size; j++)
        {
          char buffer[64];
          ba0_sprintf (buffer, "%d", v->order.tab[j]);
          vals.tab[vals.size] = ba0_strdup (buffer);
          vals.size += 1;
        }
      ba0_pull_stack ();

      BA0_TRY
      {
        ba0_push_subs_dict_analex (&pattern->dict, &pattern->idents, &vals);
        ba0_sscanf2 (pattern->exprs.tab[i], "%Qz", R->tab[R->size]->value);
        ba0_pull_subs_dict_analex ();
        ba0_restore (&M);
      }
      BA0_CATCH
      {
        ba0_pull_subs_dict_analex ();
        BA0_RE_RAISE_EXCEPTION;
      }
      BA0_ENDTRY;


      R->tab[R->size]->var = v;
      R->size += 1;

      ba0_sort_point ((struct ba0_point *) R, (struct ba0_point *) R);
    }
}

/*
 * texinfo: baz_prolongate_point_ratfrac_using_pattern_term
 * Apply @code{baz_prolongate_point_ratfrac_using_pattern_variable} to each
 * variable occurring in @var{term}. Result in @var{R}.
 */

BAZ_DLL void
baz_prolongate_point_ratfrac_using_pattern_term (
    struct baz_point_ratfrac *R,
    struct baz_point_ratfrac *P,
    struct baz_prolongation_pattern *pattern,
    struct bav_term *term)
{
  ba0_int_p i;

  if (P != R)
    ba0_set_point ((struct ba0_point *) R, (struct ba0_point *) P);
  for (i = 0; i < term->size; i++)
    baz_prolongate_point_ratfrac_using_pattern_variable (R, R, pattern,
        term->rg[i].var);
}
