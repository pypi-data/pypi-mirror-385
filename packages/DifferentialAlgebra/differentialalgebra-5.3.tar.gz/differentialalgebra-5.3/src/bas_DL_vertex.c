#include "bas_DL_vertex.h"

/*
 * texinfo: bas_init_DL_vertex
 * Initialize @var{V} to an empty vertex with number @code{BAS_NOT_A_NUMBER}.
 */

BAS_DLL void
bas_init_DL_vertex (
    struct bas_DL_vertex *V)
{
  V->number = BAS_NOT_A_NUMBER;
  V->consistency = bas_uncertain_vertex;
  ba0_init_table ((struct ba0_table *) &V->edges);
  V->action = bas_nothing_to_do_Zuple;
  V->y = BAV_NOT_A_SYMBOL;
  V->k = BAS_NOT_A_NUMBER;
  V->r = BAS_NOT_A_NUMBER;
  V->deg = BAS_NOT_A_NUMBER;
}

/*
 * texinfo: bas_new_DL_vertex
 * Allocate a new vertex, initialize it and return it.
 */

BAS_DLL struct bas_DL_vertex *
bas_new_DL_vertex (
    void)
{
  struct bas_DL_vertex *V;

  V = (struct bas_DL_vertex *) ba0_alloc (sizeof (struct bas_DL_vertex));
  bas_init_DL_vertex (V);
  return V;
}

/*
 * texinfo: bas_reset_DL_vertex
 * Reset @var{V} to an empty vertex but set its number to @var{number}.
 */

BAS_DLL void
bas_reset_DL_vertex (
    struct bas_DL_vertex *V,
    ba0_int_p number)
{
  V->number = number;
  V->consistency = bas_uncertain_vertex;
  ba0_reset_table ((struct ba0_table *) &V->edges);
  V->action = bas_nothing_to_do_Zuple;
  V->y = BAV_NOT_A_SYMBOL;
  V->k = BAS_NOT_A_NUMBER;
  V->r = BAS_NOT_A_NUMBER;
  V->deg = BAS_NOT_A_NUMBER;
}

/*
 * texinfo: bas_set_DL_vertex
 * Assign @var{src} to @var{dst}.
 */

BAS_DLL void
bas_set_DL_vertex (
    struct bas_DL_vertex *dst,
    struct bas_DL_vertex *src)
{
  if (dst != src)
    {
      ba0_int_p i;

      dst->number = src->number;
      dst->consistency = src->consistency;

      ba0_realloc2_table ((struct ba0_table *) &dst->edges,
          src->edges.size, (ba0_new_function *) & bas_new_DL_edge);
      for (i = 0; i < src->edges.size; i++)
        bas_set_DL_edge (dst->edges.tab[i], src->edges.tab[i]);
      dst->edges.size = src->edges.size;

      dst->action = src->action;
      dst->y = src->y;
      dst->k = src->k;
      dst->r = src->r;
      dst->deg = src->deg;
    }
}

/*
 * texinfo: bas_set_aykrd_DL_vertex
 * Set the fields @code{action}, @code{y}, @code{k}, @code{r} and 
 * @code{deg} of @var{V}
 * to @var{action}, @var{y}, @var{k}, @var{r} and @var{deg}.
 */

BAS_DLL void
bas_set_aykrd_DL_vertex (
    struct bas_DL_vertex *V,
    enum bas_typeof_action_on_Zuple action,
    struct bav_symbol *y,
    ba0_int_p k,
    ba0_int_p r,
    ba0_int_p deg)
{
  V->action = action;
  V->y = y;
  V->k = k;
  V->r = r;
  V->deg = deg;
}

/*
 * texinfo: bas_printf_DL_vertex
 * The general printing function for vertices.
 * It can be called through @code{ba0_printf/%DL_vertex}.
 */

BAS_DLL void
bas_printf_DL_vertex (
    void *A)
{
  struct bas_DL_vertex *V = (struct bas_DL_vertex *) A;

  if (V->y == BAV_NOT_A_SYMBOL)
    ba0_printf ("<empty vertex>");
  else
    {
      char *action;
      action = bas_typeof_action_on_Zuple_to_string (V->action);
      ba0_printf ("<%d, %t[%DL_edge], %s, %y, %d, %d, %d>",
          V->number, &V->edges, action, V->y, V->k, V->r, V->deg);
    }
}

static char _struct_DL_vertex[] = "struct bas_DL_vertex";

BAS_DLL ba0_int_p
bas_garbage1_DL_vertex (
    void *A,
    enum ba0_garbage_code code)
{
  struct bas_DL_vertex *V = (struct bas_DL_vertex *) A;
  ba0_int_p n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (V, sizeof (struct bas_DL_vertex), _struct_DL_vertex);
  n += ba0_garbage1 ("%t[%DL_edge]", &V->edges, ba0_embedded);
  return n;
}

BAS_DLL void *
bas_garbage2_DL_vertex (
    void *A,
    enum ba0_garbage_code code)
{
  struct bas_DL_vertex *V;

  if (code == ba0_isolated)
    V = (struct bas_DL_vertex *) ba0_new_addr_gc_info (A, _struct_DL_vertex);
  else
    V = (struct bas_DL_vertex *) A;
  ba0_garbage2 ("%t[%DL_edge]", &V->edges, ba0_embedded);
  return V;
}

BAS_DLL void *
bas_copy_DL_vertex (
    void *A)
{
  struct bas_DL_vertex *V;

  V = bas_new_DL_vertex ();
  bas_set_DL_vertex (V, (struct bas_DL_vertex *) A);
  return V;
}
