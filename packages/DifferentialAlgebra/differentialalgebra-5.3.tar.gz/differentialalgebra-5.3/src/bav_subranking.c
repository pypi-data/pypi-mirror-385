#include "bav_global.h"
#include "bav_symbol.h"
#include "bav_variable.h"
#include "bav_subranking.h"
#include "bav_typed_ident.h"

/*
 * This function is called from inf_grlexA, inf_grlexB, ...
 *
 * Symbols yv and yw both fit the same range indexed group in the same block.
 * The two symbols are different.
 * Return true if yv < yw
 */

static bool
inf_symbol_with_indices (
    struct bav_symbol *yv,
    struct bav_symbol *yw,
    struct bav_typed_ident *tid_v,
    struct bav_typed_ident *tid_w)
{
  struct ba0_range_indexed_group *g;
  ba0_int_p nv = tid_v->indices.tab[2];
  ba0_int_p nw = tid_w->indices.tab[2];
  ba0_int_p sum_v, sum_w, i, n;
/*
 * Both must fit some range indexed group
 */
  if ((nv != BA0_NOT_AN_INDEX && nw == BA0_NOT_AN_INDEX) ||
      (nv == BA0_NOT_AN_INDEX && nw != BA0_NOT_AN_INDEX))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
/*
 * Otherwise, the data structure is inconsistent
 */
  if (yv->index_in_rigs == BA0_NOT_AN_INDEX ||
      yw->index_in_rigs == BA0_NOT_AN_INDEX)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
/*
 * Had we used yw, we would have obtained a possibly different rig
 * but with the same indices
 */
  g = bav_global.R.rigs.tab[yv->index_in_rigs];
/*
 * Incomplete check that indices are the same
 */
  if (yv->subscripts.size == 0 || yv->subscripts.size != yw->subscripts.size ||
      yv->subscripts.size != g->lhs.size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  n = g->lhs.size;
/*
 * sum_v and sum_w are the sums of the indices of v and w
 *      with the idea that v < w if sum_v < sum_w
 * However, we have to take into account the fact that the ranges
 *      of the range indexed groups may go upward or downward.
 * When they go upward, we take the opposite of the index.
 */
  sum_v = 0;
  sum_w = 0;
  for (i = 0; i < n; i++)
    if (g->lhs.tab[i] > g->rhs.tab[i])
      {
        sum_v += yv->subscripts.tab[i];
        sum_w += yw->subscripts.tab[i];
      }
    else
      {
        sum_v -= yv->subscripts.tab[i];
        sum_v -= yw->subscripts.tab[i];
      }
  if (sum_v < sum_w)
    return true;
  else if (sum_v > sum_w)
    return false;
/*
 * sum_v and sum_w are equal
 * Let us perform a lexicographic comparison, still taking into
 *      account the fact that indices may go upward or downward
 */
  for (i = 0; i < yv->subscripts.size; i++)
    if (yv->subscripts.tab[i] != yw->subscripts.tab[i])
      {
        if (g->lhs.tab[i] > g->rhs.tab[i])
          {
            if (yv->subscripts.tab[i] < yw->subscripts.tab[i])
              return true;
            else
              return false;
          }
        else
          {
            if (yv->subscripts.tab[i] > yw->subscripts.tab[i])
              return true;
            else
              return false;
          }
      }
/*
 * Exactly the same indices!
 * Then the variables cannot be the same
 * And we compare their order of appearance in the range indexed group
 *      occurring in the block
 */
  if (nv == nw)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  if (nv > nw)
    return true;
  else
    return false;
}

/*
 * There is one function per subranking.
 * Each function returns true if v < w with respect to the subranking.
 *
 * Variables v and w belong to the same block in the table of blocks 
 *                  of the ordering
 *
 * tid_v = the entry corresponding to v->root in the 
 *                  typed_idents field of the ordering
 * tid_w = similar for w
 *
 * tid_v and tid_w may be zero but only on the case v and w are two
 *                  derivatives of the differential operator, which
 *                  is supposed to stand alone in its block.
 *
 * ders is the ders field of the ordering (the order of derivations matters)
 */

static bool
inf_grlexA (
    struct bav_variable *v,
    struct bav_variable *w,
    struct bav_typed_ident *tid_v,
    struct bav_typed_ident *tid_w,
    struct bav_tableof_symbol *ders)
{
  struct bav_symbol *yv = v->root;
  struct bav_symbol *yw = w->root;
  bav_Iorder v_order, w_order;
  ba0_int_p nv, nw;
  ba0_int_p i, d;

  v_order = bav_total_order_variable (v);
  w_order = bav_total_order_variable (w);
/*
 * First compare total orders
 */
  if (v_order < w_order)
    return true;
  else if (v_order > w_order)
    return false;

  if (tid_v == (struct bav_typed_ident *) 0 &&
      (yv != yw || yv->type != bav_operator_symbol))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
/*
 * Second compare symbols
 */
  if (tid_v != (struct bav_typed_ident *) 0 && yv != yw)
    {
      if (yv->type != bav_dependent_symbol || yw->type != bav_dependent_symbol)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);

      nv = tid_v->indices.tab[1];
      nw = tid_w->indices.tab[1];

      if (nv > nw)
        return true;
      else if (nv < nw)
        return false;
      else
        return inf_symbol_with_indices (yv, yw, tid_v, tid_w);
    }
/*
 * Third compare derivative operators
 */
  for (i = 0; i < ders->size; i++)
    {
      d = ders->tab[i]->derivation_index;
      if (v->order.tab[d] < w->order.tab[d])
        return true;
      else if (v->order.tab[d] > w->order.tab[d])
        return false;
    }

  BA0_RAISE_EXCEPTION (BA0_ERRALG);
  return false;
}

static bool
inf_grlexB (
    struct bav_variable *v,
    struct bav_variable *w,
    struct bav_typed_ident *tid_v,
    struct bav_typed_ident *tid_w,
    struct bav_tableof_symbol *ders)
{
  struct bav_symbol *yv = v->root;
  struct bav_symbol *yw = w->root;
  bav_Iorder v_order, w_order;
  ba0_int_p nv, nw;
  ba0_int_p i, d;

  v_order = bav_total_order_variable (v);
  w_order = bav_total_order_variable (w);
/*
 * First compare total orders
 */
  if (v_order < w_order)
    return true;
  else if (v_order > w_order)
    return false;
/*
 * Second compare derivative operators
 */
  for (i = 0; i < ders->size; i++)
    {
      d = ders->tab[i]->derivation_index;
      if (v->order.tab[d] < w->order.tab[d])
        return true;
      else if (v->order.tab[d] > w->order.tab[d])
        return false;
    }

  if (tid_v == (struct bav_typed_ident *) 0 &&
      (yv != yw || yv->type != bav_operator_symbol))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
/*
 * Third compare symbols
 */
  if (tid_v != (struct bav_typed_ident *) 0 && yv != yw)
    {
      if (yv->type != bav_dependent_symbol || yw->type != bav_dependent_symbol)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);

      nv = tid_v->indices.tab[1];
      nw = tid_w->indices.tab[1];

      if (nv > nw)
        return true;
      else if (nv < nw)
        return false;
      else
        return inf_symbol_with_indices (yv, yw, tid_v, tid_w);
    }

  BA0_RAISE_EXCEPTION (BA0_ERRALG);
  return false;
}

static bool
inf_degrevlexA (
    struct bav_variable *v,
    struct bav_variable *w,
    struct bav_typed_ident *tid_v,
    struct bav_typed_ident *tid_w,
    struct bav_tableof_symbol *ders)
{
  struct bav_symbol *yv = v->root;
  struct bav_symbol *yw = w->root;
  bav_Iorder v_order, w_order;
  ba0_int_p nv, nw;
  ba0_int_p i, d;

  v_order = bav_total_order_variable (v);
  w_order = bav_total_order_variable (w);
/*
 * First compare total orders
 */
  if (v_order < w_order)
    return true;
  else if (v_order > w_order)
    return false;

  if (tid_v == (struct bav_typed_ident *) 0 &&
      (yv != yw || yv->type != bav_operator_symbol))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
/*
 * Second compare symbols
 */
  if (tid_v != (struct bav_typed_ident *) 0 && yv != yw)
    {
      if (yv->type != bav_dependent_symbol || yw->type != bav_dependent_symbol)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);

      nv = tid_v->indices.tab[1];
      nw = tid_w->indices.tab[1];

      if (nv > nw)
        return true;
      else if (nv < nw)
        return false;
      else
        return inf_symbol_with_indices (yv, yw, tid_v, tid_w);
    }
/*
 * Third compare derivative operators
 */
  for (i = ders->size - 1; i >= 0; i--)
    {
      d = ders->tab[i]->derivation_index;
      if (v->order.tab[d] > w->order.tab[d])
        return true;
      else if (v->order.tab[d] < w->order.tab[d])
        return false;
    }

  BA0_RAISE_EXCEPTION (BA0_ERRALG);
  return false;
}

static bool
inf_degrevlexB (
    struct bav_variable *v,
    struct bav_variable *w,
    struct bav_typed_ident *tid_v,
    struct bav_typed_ident *tid_w,
    struct bav_tableof_symbol *ders)
{
  struct bav_symbol *yv = v->root;
  struct bav_symbol *yw = w->root;
  bav_Iorder v_order, w_order;
  ba0_int_p nv, nw;
  ba0_int_p i, d;

  v_order = bav_total_order_variable (v);
  w_order = bav_total_order_variable (w);
/*
 * First compare total orders
 */
  if (v_order < w_order)
    return true;
  else if (v_order > w_order)
    return false;
/*
 * Second compare derivative operators
 */
  for (i = ders->size - 1; i >= 0; i--)
    {
      d = ders->tab[i]->derivation_index;
      if (v->order.tab[d] > w->order.tab[d])
        return true;
      else if (v->order.tab[d] < w->order.tab[d])
        return false;
    }

  if (tid_v == (struct bav_typed_ident *) 0 &&
      (yv != yw || yv->type != bav_operator_symbol))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
/*
 * Third compare symbols
 */
  if (tid_v != (struct bav_typed_ident *) 0 && yv != yw)
    {
      if (yv->type != bav_dependent_symbol || yw->type != bav_dependent_symbol)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);

      nv = tid_v->indices.tab[1];
      nw = tid_w->indices.tab[1];

      if (nv > nw)
        return true;
      else if (nv < nw)
        return false;
      else
        return inf_symbol_with_indices (yv, yw, tid_v, tid_w);
    }

  BA0_RAISE_EXCEPTION (BA0_ERRALG);
  return false;
}

static bool
inf_lex (
    struct bav_variable *v,
    struct bav_variable *w,
    struct bav_typed_ident *tid_v,
    struct bav_typed_ident *tid_w,
    struct bav_tableof_symbol *ders)
{
  struct bav_symbol *yv = v->root;
  struct bav_symbol *yw = w->root;
  ba0_int_p nv, nw;
  ba0_int_p i, d;
/*
 * First compare derivative operators
 */
  for (i = 0; i < ders->size; i++)
    {
      d = ders->tab[i]->derivation_index;
      if (v->order.tab[d] < w->order.tab[d])
        return true;
      else if (v->order.tab[d] > w->order.tab[d])
        return false;
    }

  if (tid_v == (struct bav_typed_ident *) 0 &&
      (yv != yw || yv->type != bav_operator_symbol))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
/*
 * Second compare symbols
 */
  if (tid_v != (struct bav_typed_ident *) 0 && yv != yw)
    {
      if (yv->type != bav_dependent_symbol || yw->type != bav_dependent_symbol)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);

      nv = tid_v->indices.tab[1];
      nw = tid_w->indices.tab[1];

      if (nv > nw)
        return true;
      else if (nv < nw)
        return false;
      else
        return inf_symbol_with_indices (yv, yw, tid_v, tid_w);
    }

  BA0_RAISE_EXCEPTION (BA0_ERRALG);
  return false;
}

/*
 * Readonly data structure.
 * Read also in bav_block.
 */

static struct bav_subranking bav_subranking_table[] = {
  {"grlexA", inf_grlexA},
  {"grlexB", inf_grlexB},
  {"degrevlexA", inf_degrevlexA},
  {"degrevlexB", inf_degrevlexB},
  {"lex", inf_lex}
};

#define BAV_NB_SUBRANKINGS	\
	(sizeof (bav_subranking_table) / sizeof (struct bav_subranking))

/*
 * texinfo: bav_is_subranking
 * Return @code{true} if @var{ident} is the identifier of a subranking.
 * If so, @var{subranking} is assigned the corresponding
 * value, read from a static readonly array.
 */

BAV_DLL bool
bav_is_subranking (
    char *ident,
    struct bav_subranking **subranking)
{
  ba0_int_p i;

  for (i = 0; i < (ba0_int_p) BAV_NB_SUBRANKINGS; i++)
    {
      if (ba0_strcasecmp (ident, bav_subranking_table[i].ident) == 0)
        {
          *subranking = &bav_subranking_table[i];
          return true;
        }
    }
  return false;
}
