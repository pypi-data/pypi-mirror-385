#include "bad_splitting_vertex.h"

/*
 * texinfo: bad_init_splitting_vertex
 * Initialize @var{V} to an empty vertex with number @code{BAD_NOT_A_NUMBER}.
 */

BAD_DLL void
bad_init_splitting_vertex (
    struct bad_splitting_vertex *V)
{
  V->number = BAD_NOT_A_NUMBER;
  V->is_first = false;
  V->shape = bad_ellipse_vertex;
  ba0_init_table ((struct ba0_table *) &V->edges);
  ba0_init_table ((struct ba0_table *) &V->thetas);
  ba0_init_table ((struct ba0_table *) &V->leaders);
}

/*
 * texinfo: bad_new_splitting_vertex
 * Allocate a new vertex, initialize it and return it.
 */

BAD_DLL struct bad_splitting_vertex *
bad_new_splitting_vertex (
    void)
{
  struct bad_splitting_vertex *V;

  V = (struct bad_splitting_vertex *) ba0_alloc (sizeof (struct
          bad_splitting_vertex));
  bad_init_splitting_vertex (V);
  return V;
}

/*
 * texinfo: bad_reset_splitting_vertex
 * Reset @var{V} to an empty vertex but set its number to @var{number}.
 * All other fields are assigned their default values.
 */

BAD_DLL void
bad_reset_splitting_vertex (
    struct bad_splitting_vertex *V,
    ba0_int_p number)
{
  V->number = number;
  V->is_first = false;
  V->shape = bad_ellipse_vertex;
  ba0_reset_table ((struct ba0_table *) &V->edges);
  ba0_reset_table ((struct ba0_table *) &V->thetas);
  ba0_reset_table ((struct ba0_table *) &V->leaders);
}

/*
 * texinfo: bad_set_splitting_vertex
 * Assign @var{src} to @var{dst}.
 */

BAD_DLL void
bad_set_splitting_vertex (
    struct bad_splitting_vertex *dst,
    struct bad_splitting_vertex *src)
{
  if (dst != src)
    {
      ba0_int_p i;

      dst->number = src->number;
      dst->is_first = src->is_first;
      dst->shape = src->shape;

      ba0_realloc2_table ((struct ba0_table *) &dst->edges,
          src->edges.size, (ba0_new_function *) & bad_new_splitting_edge);
      for (i = 0; i < src->edges.size; i++)
        bad_set_splitting_edge (dst->edges.tab[i], src->edges.tab[i]);
      dst->edges.size = src->edges.size;

      bav_set_tableof_term (&dst->thetas, &src->thetas);
      ba0_set_table ((struct ba0_table *) &dst->leaders,
          (struct ba0_table *) &src->leaders);
    }
}

/*
 * texinfo: bad_merge_thetas_leaders_splitting_vertex
 * Merge the field @code{leaders} of @var{V} with
 * @var{leaders} so that the resulting field @code{leaders} 
 * of @var{V} remains sorted by decreasing order.
 * Perform corresponding operations on the field @code{thetas}
 * of @var{V} and @var{thetas}.
 * In the case of a same entry in the field @code{leaders} 
 * of @var{V} and @var{leaders}, the least common multiple
 * of the corresponding entries of the field @code{thetas}
 * of @var{V} and @var{thetas} is taken.
 * The table @var{leaders} is supposed to be sorted by increasing
 * order.
 */

BAD_DLL void
bad_merge_thetas_leaders_splitting_vertex (
    struct bad_splitting_vertex *V,
    struct bav_tableof_term *thetas,
    struct bav_tableof_variable *leaders)
{
  ba0_int_p i, j, k, n;
  ba0_int_p ni, nj;

#if defined (BA0_MEMCHECK)
/*
 * Check that leaders is sorted in increasing order
 */
  for (i = 1; i < leaders->size; i++)
    {
      if (leaders->tab[i] == BAV_NOT_A_VARIABLE)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
      ni = bav_variable_number (leaders->tab[i]);
      nj = bav_variable_number (leaders->tab[i - 1]);
      if (ni <= nj)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
    }
#endif
  n = 0;
  i = 0;
  j = 0;
/*
 * Count n = the number of entries to add to V->leaders and V->thetas
 */
  while (i < leaders->size && j < V->leaders.size)
    {
      if (bav_is_one_term (thetas->tab[i]))
        i += 1;
      else
        {
          ni = bav_variable_number (leaders->tab[i]);
          nj = bav_variable_number (V->leaders.tab[j]);
          if (ni < nj)
            {
              n += 1;
              i += 1;
            }
          else if (ni > nj)
            j += 1;
          else
            {
              i += 1;
              j += 1;
            }
        }
    }
  while (i < leaders->size)
    {
      if (!bav_is_one_term (thetas->tab[i]))
        n += 1;
      i += 1;
    }
  ba0_realloc_table ((struct ba0_table *) &V->leaders, V->leaders.size + n);
  ba0_realloc2_table ((struct ba0_table *) &V->thetas, V->thetas.size + n,
      (ba0_new_function *) & bav_new_term);
  i = leaders->size - 1;
  j = V->leaders.size - 1;
  k = j + n;
  while (i >= 0 && j >= 0)
    {
      if (bav_is_one_term (thetas->tab[i]))
        i -= 1;
      else
        {
          ni = bav_variable_number (leaders->tab[i]);
          nj = bav_variable_number (V->leaders.tab[j]);
          if (ni > nj)
            {
              V->leaders.tab[k] = leaders->tab[i];
              bav_set_term (V->thetas.tab[k], thetas->tab[i]);
              k -= 1;
              i -= 1;
            }
          else if (ni < nj)
            {
              if (j != k)
                {
                  V->leaders.tab[k] = V->leaders.tab[j];
                  bav_set_term (V->thetas.tab[k], V->thetas.tab[j]);
                }
              k -= 1;
              j -= 1;
            }
          else
            {
              V->leaders.tab[k] = V->leaders.tab[j];
              bav_lcm_term (V->thetas.tab[k], V->thetas.tab[j], thetas->tab[i]);
              k -= 1;
              j -= 1;
              i -= 1;
            }
        }
    }
  while (i >= 0 && k >= 0)
    {
      if (!bav_is_one_term (thetas->tab[i]))
        {
          V->leaders.tab[k] = leaders->tab[i];
          bav_set_term (V->thetas.tab[k], thetas->tab[i]);
          k -= 1;
        }
      i -= 1;
    }
  V->thetas.size += n;
  V->leaders.size += n;
#if defined (BA0_MEMCHECK)
/*
 * Check the result
 */
  for (i = 1; i < V->leaders.size; i++)
    {
      if (V->leaders.tab[i] == BAV_NOT_A_VARIABLE)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
      ni = bav_variable_number (V->leaders.tab[i]);
      nj = bav_variable_number (V->leaders.tab[i - 1]);
      if (ni <= nj)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
    }
#endif
}

static struct
{
  enum bad_shapeof_splitting_vertex shape;
  char *ident;
} bad_cases[] = { {bad_parallelogram_vertex, "parallelogram"},
{bad_triangle_vertex, "triangle"},
{bad_box_vertex, "box"},
{bad_ellipse_vertex, "ellipse"},
{bad_hexagon_vertex, "hexagon"}
};

/*
 * texinfo: bad_shapeof_splitting_vertex_to_string
 * Return a string encoding for @var{shape}.
 */

BAD_DLL char *
bad_shapeof_splitting_vertex_to_string (
    enum bad_shapeof_splitting_vertex shape)
{
  bool found = false;
  ba0_int_p n = (ba0_int_p) (sizeof (bad_cases) / sizeof (bad_cases[0]));
  ba0_int_p i = 0;

  while (i < n && !found)
    {
      if (shape == bad_cases[i].shape)
        found = true;
      else
        i += 1;
    }
  if (!found)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  return bad_cases[i].ident;
}

/*
 * texinfo: bad_scanf_splitting_vertex
 * The general parsing function for vertices.
 * It can be called through @code{ba0_scanf/%splitting_vertex}.
 * The expected syntax is as follows (the last string
 * is supposed to be @code{true} or @code{false}):
 * @verbatim
 * <%d, is_first, shape, %t[%splitting_edge], %t[%term], %t[%v]>
 * @end verbatim
 */

BAD_DLL void *
bad_scanf_splitting_vertex (
    void *A)
{
  struct bad_splitting_vertex *V;
  char buff0[BA0_BUFSIZE], buff1[BA0_BUFSIZE];
  ba0_int_p i, n;
  bool found;

  if (A == (void *) 0)
    V = bad_new_splitting_vertex ();
  else
    {
      V = (struct bad_splitting_vertex *) A;
      bad_reset_splitting_vertex (V, V->number);
    }

  ba0_scanf
      ("<%d, %s, %s, %t[%splitting_edge], %t[%term], %t[%v]>",
      &V->number, buff0, buff1, &V->edges, &V->thetas, &V->leaders);

  if (ba0_strcasecmp (buff0, "true") == 0)
    V->is_first = true;
  else if (ba0_strcasecmp (buff0, "false") == 0)
    V->is_first = false;
  else
    BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);

  found = false;
  i = 0;
  n = (ba0_int_p) (sizeof (bad_cases) / sizeof (bad_cases[0]));
  while (!found && i < n)
    {
      found = ba0_strcasecmp (buff1, bad_cases[i].ident) == 0;
      if (!found)
        i += 1;
    }
  if (found)
    V->shape = bad_cases[i].shape;
  else
    BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);

  return V;
}

/*
 * texinfo: bad_printf_splitting_vertex
 * The general printing function for vertices.
 * It can be called through @code{ba0_printf/%splitting_vertex}.
 */

BAD_DLL void
bad_printf_splitting_vertex (
    void *A)
{
  struct bad_splitting_vertex *V = (struct bad_splitting_vertex *) A;
  char buffer[32], *shape;

  if (V->is_first)
    strcpy (buffer, "true");
  else
    strcpy (buffer, "false");

  shape = bad_shapeof_splitting_vertex_to_string (V->shape);

  ba0_printf
      ("<%d, %s, %s, %t[%splitting_edge], %t[%term], %t[%v]>",
      V->number, buffer, shape, &V->edges, &V->thetas, &V->leaders);
}

static char _struct_splitting_vertex[] = "struct bad_splitting_vertex";

BAD_DLL ba0_int_p
bad_garbage1_splitting_vertex (
    void *A,
    enum ba0_garbage_code code)
{
  struct bad_splitting_vertex *V = (struct bad_splitting_vertex *) A;
  ba0_int_p n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (V, sizeof (struct bad_splitting_vertex),
        _struct_splitting_vertex);
  n += ba0_garbage1 ("%t[%splitting_edge]", &V->edges, ba0_embedded);
  n += ba0_garbage1 ("%t[%term]", &V->thetas, ba0_embedded);
  n += ba0_garbage1 ("%t[%v]", &V->leaders, ba0_embedded);
  return n;
}

BAD_DLL void *
bad_garbage2_splitting_vertex (
    void *A,
    enum ba0_garbage_code code)
{
  struct bad_splitting_vertex *V;

  if (code == ba0_isolated)
    V = (struct bad_splitting_vertex *) ba0_new_addr_gc_info (A,
        _struct_splitting_vertex);
  else
    V = (struct bad_splitting_vertex *) A;
  ba0_garbage2 ("%t[%splitting_edge]", &V->edges, ba0_embedded);
  ba0_garbage2 ("%t[%term]", &V->thetas, ba0_embedded);
  ba0_garbage2 ("%t[%v]", &V->leaders, ba0_embedded);
  return V;
}

BAD_DLL void *
bad_copy_splitting_vertex (
    void *A)
{
  struct bad_splitting_vertex *V;

  V = bad_new_splitting_vertex ();
  bad_set_splitting_vertex (V, (struct bad_splitting_vertex *) A);
  return V;
}
