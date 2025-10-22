#include "bav_point_interval_mpq.h"

/*
 * texinfo: bav_new_value_interval_mpq
 * Allocate a new value, initializes it and returns it.
 */

BAV_DLL struct bav_value_interval_mpq *
bav_new_value_interval_mpq (
    void)
{
  struct bav_value_interval_mpq *value;

  value = (struct bav_value_interval_mpq *) ba0_new_value ();
  value->value = ba0_new_interval_mpq ();
  return value;
}

/*
 * texinfo: bav_set_value_interval_mpq
 * Assign @var{src} to @var{dst}.
 */

BAV_DLL void
bav_set_value_interval_mpq (
    struct bav_value_interval_mpq *dst,
    struct bav_value_interval_mpq *src)
{
  if (src != dst)
    {
      dst->var = src->var;
      ba0_set_interval_mpq (dst->value, src->value);
    }
}

/*
 * texinfo: bav_init_point_interval_mpq
 * Initialize @var{point} to the empty interval.
 */

BAV_DLL void
bav_init_point_interval_mpq (
    struct bav_point_interval_mpq *point)
{
  ba0_init_table ((struct ba0_table *) point);
}

/*
 * texinfo: bav_new_point_interval_mpq
 * Allocate a new point and returns it.
 */

BAV_DLL struct bav_point_interval_mpq *
bav_new_point_interval_mpq (
    void)
{
  struct bav_point_interval_mpq *point;

  point =
      (struct bav_point_interval_mpq *) ba0_alloc (sizeof (struct
          bav_point_interval_mpq));
  bav_init_point_interval_mpq (point);
  return point;
}

/*
 * texinfo: bav_realloc_point_interval_mpq
 * Reallocate @var{point} so that it can receive at least @var{n} values.
 */

BAV_DLL void
bav_realloc_point_interval_mpq (
    struct bav_point_interval_mpq *point,
    ba0_int_p n)
{
  ba0_realloc2_table ((struct ba0_table *) point, n,
      (ba0_new_function *) & bav_new_value_interval_mpq);
}

/*
 * texinfo: bav_set_point_interval_mpq
 * Assign @var{src} to @var{dst}.
 */

BAV_DLL void
bav_set_point_interval_mpq (
    struct bav_point_interval_mpq *dst,
    struct bav_point_interval_mpq *src)
{
  ba0_int_p i;

  if (dst != src)
    {
      dst->size = 0;
      bav_realloc_point_interval_mpq (dst, src->size);
      for (i = 0; i < src->size; i++)
        bav_set_value_interval_mpq (dst->tab[i], src->tab[i]);
      dst->size = src->size;
    }
}

/*
 * texinfo: bav_set_coord_point_interval_mpq
 * Associate the value @var{X} to the variable @var{v} in @var{point}.
 * The variable @var{v} does not need to be already present in @var{point}.
 * If @var{point} was sorted by increasing addresses of variables, it
 * is still so after insertion of a new value.
 */

BAV_DLL void
bav_set_coord_point_interval_mpq (
    struct bav_point_interval_mpq *point,
    struct bav_variable *v,
    struct ba0_interval_mpq *X)
{
  struct bav_value_interval_mpq *value;
  ba0_int_p i;

  if (ba0_bsearch_point (v, (struct ba0_point *) point, &i) != BA0_NOT_A_VALUE)
    ba0_set_interval_mpq (point->tab[i]->value, X);
  else
    {
      value = bav_new_value_interval_mpq ();
      value->var = v;
      ba0_set_interval_mpq (value->value, X);
      ba0_insert_table ((struct ba0_table *) point, i, value);
#if defined (DEBUG)
      if (!ba0_is_sorted_point ((struct ba0_point *) point))
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
#endif
    }
}

/*
 * texinfo: bav_intersect_coord_point_interval_mpq
 * Intersect the value associated to @var{v} with @var{X}, in @var{src}.
 * The result is stored in @var{dst}. If @var{v} is not already present
 * in @var{src}, associate the value @var{X} to the variable @var{v}.
 * If @var{point} was sorted by increasing addresses of variables, it
 * is still so after insertion of a new value.
 */

BAV_DLL void
bav_intersect_coord_point_interval_mpq (
    struct bav_point_interval_mpq *dst,
    struct bav_point_interval_mpq *src,
    struct bav_variable *v,
    struct ba0_interval_mpq *X)
{
  struct bav_value_interval_mpq *value;
  ba0_int_p i;

  bav_set_point_interval_mpq (dst, src);
  if (ba0_bsearch_point (v, (struct ba0_point *) dst, &i) != BA0_NOT_A_VALUE)
    ba0_intersect_interval_mpq (dst->tab[i]->value, dst->tab[i]->value, X);
  else
    {
      value = bav_new_value_interval_mpq ();
      value->var = v;
      ba0_set_interval_mpq (value->value, X);
      ba0_insert_table ((struct ba0_table *) dst, i, value);
#if defined (DEBUG)
      if (!ba0_is_sorted_point ((struct ba0_point *) dst))
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
#endif
    }
}

/*
 * texinfo: bav_intersect_point_interval_mpq
 * Intersect @var{Q} and @var{R} variable-wise.
 * Result in @var{P}. The point @var{P} thus contains values for all the
 * variables present in @var{Q} or in @var{R}.
 */

BAV_DLL void
bav_intersect_point_interval_mpq (
    struct bav_point_interval_mpq *P,
    struct bav_point_interval_mpq *Q,
    struct bav_point_interval_mpq *R)
{
  ba0_int_p i;

  if (P != Q && P != R)
    bav_set_point_interval_mpq (P, Q);
  else if (P != Q)              /* then P == R */
    BA0_SWAP (struct bav_point_interval_mpq *,
        Q,
        R);
  if (P != R)                   /* to cover the case P == Q == R */
    {
      for (i = 0; i < R->size; i++)
        bav_intersect_coord_point_interval_mpq
            (P, P, R->tab[i]->var, R->tab[i]->value);
    }
}

/*
 * texinfo: bav_is_empty_point_interval_mpq
 * Return @code{true} if @var{point} is empty, i.e. if it contains at least
 * one value associated to the empty interval.
 */

BAV_DLL bool
bav_is_empty_point_interval_mpq (
    struct bav_point_interval_mpq *point)
{
  ba0_int_p i;
  bool b;

  b = false;
  for (i = 0; i < point->size && !b; i++)
    b = ba0_is_empty_interval_mpq (point->tab[i]->value);
  return b;
}

/*
 * texinfo: bav_bisect_point_interval_mpq
 * Split the value of index @var{coord} of @var{point} into two
 * intervals. The result is stored in @var{T}.
 */

BAV_DLL void
bav_bisect_point_interval_mpq (
    struct bav_tableof_point_interval_mpq *T,
    struct bav_point_interval_mpq *point,
    ba0_int_p coord)
{
  ba0__mpq_struct *a, *b;
  struct ba0_mark M;
  ba0_mpq_t m;

  a = point->tab[coord]->value->a;
  b = point->tab[coord]->value->b;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mpq_init (m);
  ba0_middle_interval_mpq (m, point->tab[coord]->value);
  ba0_pull_stack ();

  ba0_realloc2_table ((struct ba0_table *) T, 2 * T->size + 2,
      (ba0_new_function *) & bav_new_point_interval_mpq);
  if (point != T->tab[T->size + 1])
    {
      bav_set_point_interval_mpq (T->tab[T->size + 1], point);
      ba0_set_interval_mpq_mpq (T->tab[T->size + 1]->tab[coord]->value, a, m);
      bav_set_point_interval_mpq (T->tab[T->size], point);
      ba0_set_interval_mpq_mpq (T->tab[T->size]->tab[coord]->value, m, b);
    }
  else
    {
      bav_set_point_interval_mpq (T->tab[T->size], point);
      ba0_set_interval_mpq_mpq (T->tab[T->size]->tab[coord]->value, m, b);
      bav_set_point_interval_mpq (T->tab[T->size + 1], point);
      ba0_set_interval_mpq_mpq (T->tab[T->size + 1]->tab[coord]->value, a, m);
    }
  T->size += 2;
  ba0_restore (&M);
}

/*
 * texinfo: bav_set_tableof_point_interval_mpq
 * Assign @var{src} to @var{dst}.
 */

BAV_DLL void
bav_set_tableof_point_interval_mpq (
    struct bav_tableof_point_interval_mpq *dst,
    struct bav_tableof_point_interval_mpq *src)
{
  ba0_int_p i;

  if (dst != src)
    {
      dst->size = 0;
      ba0_realloc2_table ((struct ba0_table *) dst, src->size,
          (ba0_new_function *) & bav_new_point_interval_mpq);
      for (i = 0; i < src->size; i++)
        {
          bav_set_point_interval_mpq (dst->tab[i], src->tab[i]);
          dst->size = i + 1;
        }
    }
}
