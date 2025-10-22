#include "bas_DL_tree.h"

/*
 * texinfo: bas_init_DL_tree
 * Initialize @var{tree} to an empty inactive tree.
 */

BAS_DLL void
bas_init_DL_tree (
    struct bas_DL_tree *tree)
{
  tree->activity = bas_inactive_DL_tree;
  ba0_init_table ((struct ba0_table *) &tree->vertices);
  ba0_init_table ((struct ba0_table *) &tree->roots);
  tree->number = 1;
}

/*
 * texinfo: bas_new_DL_tree
 * Allocate a new tree, initialize it and return it.
 */

BAS_DLL struct bas_DL_tree *
bas_new_DL_tree (
    void)
{
  struct bas_DL_tree *tree;

  tree = (struct bas_DL_tree *) ba0_alloc (sizeof (struct bas_DL_tree));
  bas_init_DL_tree (tree);
  return tree;
}

/*
 * texinfo: bas_reset_DL_tree
 * Reset @var{tree} to an empty tree with activity level @var{level}.
 */

BAS_DLL void
bas_reset_DL_tree (
    struct bas_DL_tree *tree,
    enum bas_activity_level_DL_tree level)
{
  tree->activity = level;
  ba0_reset_table ((struct ba0_table *) &tree->vertices);
  ba0_reset_table ((struct ba0_table *) &tree->roots);
  tree->number = 1;
}

/*
 * texinfo: bas_add_root_DL_tree
 * Store the vertex number @var{root} in the @code{roots} field of @var{tree}.
 */

BAS_DLL void
bas_add_root_DL_tree (
    struct bas_DL_tree *tree,
    ba0_int_p root)
{
  if (root < 0 || root > tree->number)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (tree->activity != bas_inactive_DL_tree)
    {
      ba0_realloc_table ((struct ba0_table *) &tree->roots,
          tree->roots.size + 1);
      tree->roots.tab[tree->roots.size] = root;
      tree->roots.size += 1;
    }
}

static void
bas_realloc_tableof_DL_vertex (
    struct bas_tableof_DL_vertex *T,
    ba0_int_p n)
{
  if (n > T->alloc)
    {
      ba0_int_p new_alloc = 2 * T->alloc + 1;
      while (new_alloc < n)
        new_alloc = 2 * new_alloc + 1;
      ba0_realloc2_table ((struct ba0_table *) T, new_alloc,
          (ba0_new_function *) & bas_new_DL_vertex);
    }
}

static void
bas_set_tableof_DL_vertex (
    struct bas_tableof_DL_vertex *dst,
    struct bas_tableof_DL_vertex *src)
{
  ba0_int_p i;

  if (dst != src)
    {
      ba0_realloc2_table ((struct ba0_table *) dst, src->size,
          (ba0_new_function *) & bas_new_DL_vertex);
      for (i = 0; i < src->size; i++)
        bas_set_DL_vertex (dst->tab[i], src->tab[i]);
      dst->size = src->size;
    }
}

/*
 * texinfo: bas_set_DL_tree
 * Assign @var{src} to @var{dst}.
 */

BAS_DLL void
bas_set_DL_tree (
    struct bas_DL_tree *dst,
    struct bas_DL_tree *src)
{
  if (dst != src)
    {
      dst->activity = src->activity;
      bas_set_tableof_DL_vertex (&dst->vertices, &src->vertices);
      dst->number = src->number;
    }
}

/*
 * texinfo: bas_next_number_DL_tree
 * Return the next available Zuple number available in @var{tree}. 
 * This function does not allocate any memory.
 */

BAS_DLL ba0_int_p
bas_next_number_DL_tree (
    struct bas_DL_tree *tree)
{
  return tree->number++;
}

/*
 * texinfo: bas_ith_vertex_DL_tree
 * Return the vertex dedicated to the Zuple
 * identified by @var{number} in @var{tree}.
 * This function may perform memory allocation.
 */

BAS_DLL struct bas_DL_vertex *
bas_ith_vertex_DL_tree (
    struct bas_DL_tree *tree,
    ba0_int_p number)
{
  struct bas_DL_vertex *V;
  ba0_int_p i = number;

  if (i < 0 || i >= tree->number)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (tree->activity == bas_inactive_DL_tree)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (i >= tree->vertices.size)
    {
      bas_realloc_tableof_DL_vertex (&tree->vertices, tree->number);
      while (i >= tree->vertices.size)
        {
          bas_reset_DL_vertex (tree->vertices.tab[tree->vertices.size],
              tree->vertices.size);
          tree->vertices.size += 1;
        }
    }

  V = tree->vertices.tab[i];
  return V;
}

/*
 * texinfo: bas_add_edge_DL_tree
 * Add the edge defined by @var{type}, @var{src}
 * and @var{dst} to @var{tree}. 
 * In the case of an inactive tree, the edge is not
 * recorded.
 */

BAS_DLL void
bas_add_edge_DL_tree (
    struct bas_DL_tree *tree,
    enum bas_typeof_DL_edge type,
    ba0_int_p src,
    ba0_int_p dst)
{
  struct bas_DL_vertex *V;
  ba0_int_p i;

  if (src < 0 || src >= tree->number || dst < 0 || dst >= tree->number)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (tree->activity != bas_inactive_DL_tree)
    {
/*
 * This call is only meant to create the vertex dst
 */
      bas_ith_vertex_DL_tree (tree, dst);

      V = bas_ith_vertex_DL_tree (tree, src);
/*
 * Check consistency of src and the fact that the edge is not
 *      already stored
 */
      for (i = 0; i < V->edges.size; i++)
        if (V->edges.tab[i]->src != src || V->edges.tab[i]->dst == dst)
          BA0_RAISE_EXCEPTION (BA0_ERRALG);

      if (V->edges.size == V->edges.alloc)
        {
          ba0_int_p new_alloc = 2 * V->edges.alloc + 2;
          ba0_realloc2_table ((struct ba0_table *) &V->edges, new_alloc,
              (ba0_new_function *) & bas_new_DL_edge);
        }

      bas_set_tsd_DL_edge (V->edges.tab[V->edges.size], type, src, dst);

      V->edges.size += 1;
    }
}

/*
 * texinfo: bas_set_vertex_consistency_DL_tree
 * Set the field @code{consistency} of 
 * the vertex @var{number} of @var{tree}
 * to @var{consistency}.
 */

BAS_DLL void
bas_set_vertex_consistency_DL_tree (
    struct bas_DL_tree *tree,
    ba0_int_p number,
    enum bas_typeof_consistency_vertex consistency)
{
  struct bas_DL_vertex *V;

  if (tree->activity != bas_inactive_DL_tree)
    {
      V = bas_ith_vertex_DL_tree (tree, number);
      V->consistency = consistency;
    }
}

/*
 * texinfo: bas_set_aykrd_vertex_DL_tree
 * Set the fields @code{action}, @code{y}, @code{k}, @code{r} and 
 * @code{deg} of the 
 * vertex with number @var{number} of @var{tree} to 
 * @var{action}, @var{y}, @var{k}, @var{r} and @var{deg}.
 */

BAS_DLL void
bas_set_aykrd_vertex_DL_tree (
    struct bas_DL_tree *tree,
    ba0_int_p number,
    enum bas_typeof_action_on_Zuple action,
    struct bav_symbol *y,
    ba0_int_p k,
    ba0_int_p r,
    ba0_int_p deg)
{
  if (number < 0 || number >= tree->number)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (tree->activity != bas_inactive_DL_tree)
    {
      struct bas_DL_vertex *V;
      V = bas_ith_vertex_DL_tree (tree, number);
      bas_set_aykrd_DL_vertex (V, action, y, k, r, deg);
    }
}

static void
bas_dot_vertex_DL_tree (
    char *buffer,
    struct bas_DL_vertex *v)
{
  ba0_int_p n = v->number;
  char *action;

  if (v->y == BAV_NOT_A_SYMBOL)
    ba0_sprintf (buffer, "%d", n);
  else
    {
      action = bas_typeof_action_on_Zuple_to_string (v->action);
      if (v->k == BAS_NOT_A_NUMBER)
        ba0_sprintf (buffer, "\"%d %s %y\"", n, action, v->y);
      else if (v->r == BAS_NOT_A_NUMBER)
        ba0_sprintf (buffer, "\"%d %s %y k=%d\"", n, action, v->y, v->k);
      else
        ba0_sprintf (buffer, "\"%d %s %y k=%d (r,d)=(%d,%d)\"", n, action, v->y,
            v->k, v->r, v->deg);
    }
}

static void
bas_dot_aux_DL_tree (
    struct bas_DL_tree *tree,
    ba0_int_p n)
{
  struct bas_DL_vertex *v = tree->vertices.tab[n];
  char src[BA0_BUFSIZE];
  ba0_int_p i;

  bas_dot_vertex_DL_tree (src, v);

  switch (v->consistency)
    {
    case bas_rejected_vertex:
      ba0_printf ("  %s [shape=septagon];\n", src);
      break;
    case bas_uncertain_vertex:
      break;
    case bas_consistent_vertex:
      ba0_printf ("  %s [shape=box];\n", src);
      break;
    case bas_inconsistent_vertex:
      ba0_printf ("  %s [shape=pentagon];\n", src);
      break;
    }

  for (i = 0; i < v->edges.size; i++)
    {
      char dst[BA0_BUFSIZE], lab[BA0_BUFSIZE];
      struct bas_DL_vertex *w = tree->vertices.tab[v->edges.tab[i]->dst];
      char *ident;

      ident = bas_typeof_DL_edge_to_string (v->edges.tab[i]->type);
      ba0_sprintf (lab, "%s", ident);

      bas_dot_vertex_DL_tree (dst, w);

      if (v->edges.tab[i]->type == bas_none_edge)
        ba0_printf ("  %s -\\> %s;\n", src, dst);
      else
        ba0_printf ("  %s -\\> %s [label=%s];\n", src, dst, lab);
    }

  for (i = 0; i < v->edges.size; i++)
    {
      ba0_int_p m = v->edges.tab[i]->dst;
      bas_dot_aux_DL_tree (tree, m);
    }
}

/*
 * texinfo: bas_dot_DL_tree
 * Print @var{tree} as a directed graph, following the syntax 
 * of @code{graphviz/dot}. 
 * Edges are labelled using the encoding given by 
 * @code{bas_typeof_DL_edge_to_string}.
 * The shapes of the vertices are functions of their
 * fields @code{consistency} and @code{argument}.
 * The correspondence is as follows:
 * @verbatim
 * ellipse       bas_uncertain_vertex
 * septagon      bas_rejected_vertex (kappa exceeded)
 * box           bas_consistent_vertex
 * pentagon      bas_inconsistent_vertex
 * @end verbatim
 */


BAS_DLL void
bas_dot_DL_tree (
    struct bas_DL_tree *tree)
{
  ba0_int_p i;

  if (tree->activity == bas_inactive_DL_tree)
    return;

  ba0_printf ("digraph G \\{\n");
  for (i = 0; i < tree->roots.size; i++)
    bas_dot_aux_DL_tree (tree, tree->roots.tab[i]);
  ba0_printf ("\\}\n");
}

/*
 * texinfo: bas_scanf_DL_tree
 * The parsing function for DL trees.
 * It is called by @code{ba0_scanf/%DL_tree}.
 * The read DL tree is verbose.
 */

BAS_DLL void *
bas_scanf_DL_tree (
    void *A)
{
  struct bas_DL_tree *tree;
  ba0_int_p i;

  if (A == (void *) 0)
    tree = bas_new_DL_tree ();
  else
    tree = (struct bas_DL_tree *) A;

  ba0_scanf ("<%t[%d], %t[%DL_vertex]>", &tree->roots, &tree->vertices);

  tree->activity = bas_verbose_DL_tree;

  for (i = 0; i < tree->vertices.size; i++)
    if (tree->vertices.tab[i]->number != i)
      BA0_RAISE_EXCEPTION (BA0_ERRALG);

  tree->number = tree->vertices.size;

  return tree;
}

/*
 * texinfo: bas_printf_DL_tree
 * The printing function for DL trees.
 * It is called by @code{ba0_printf/%DL_tree}.
 */

BAS_DLL void
bas_printf_DL_tree (
    void *A)
{
  struct bas_DL_tree *tree = (struct bas_DL_tree *) A;

  if (tree->activity != bas_inactive_DL_tree)
    ba0_printf ("<%t[%d], %t[%DL_vertex]>", &tree->roots, &tree->vertices);
  else
    ba0_printf ("inactive tree");
}

static char _struct_DL_tree[] = "struct bas_DL_tree";

BAS_DLL ba0_int_p
bas_garbage1_DL_tree (
    void *A,
    enum ba0_garbage_code code)
{
  struct bas_DL_tree *tree = (struct bas_DL_tree *) A;
  ba0_int_p n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (tree, sizeof (struct bas_DL_tree), _struct_DL_tree);
  n += ba0_garbage1 ("%t[%DL_vertex]", &tree->vertices, ba0_embedded);
  return n;
}

BAS_DLL void *
bas_garbage2_DL_tree (
    void *A,
    enum ba0_garbage_code code)
{
  struct bas_DL_tree *tree;

  if (code == ba0_isolated)
    tree = (struct bas_DL_tree *) ba0_new_addr_gc_info (A, _struct_DL_tree);
  else
    tree = (struct bas_DL_tree *) A;
  ba0_garbage2 ("%t[%DL_vertex]", &tree->vertices, ba0_embedded);
  return tree;
}

BAS_DLL void *
bas_copy_DL_tree (
    void *A)
{
  struct bas_DL_tree *tree;

  tree = bas_new_DL_tree ();
  bas_set_DL_tree (tree, (struct bas_DL_tree *) A);
  return tree;
}
