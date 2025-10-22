#include "bas_DL_edge.h"

/*
 * texinfo: bas_init_DL_edge
 * Initialize @var{E}.
 */

BAS_DLL void
bas_init_DL_edge (
    struct bas_DL_edge *E)
{
  E->type = bas_none_edge;
  E->src = BAS_NOT_A_NUMBER;
  E->dst = BAS_NOT_A_NUMBER;
}

/*
 * texinfo: bas_new_DL_edge
 * Allocate a new edge, initialize it and return it.
 */

BAS_DLL struct bas_DL_edge *
bas_new_DL_edge (
    void)
{
  struct bas_DL_edge *E;

  E = (struct bas_DL_edge *) ba0_alloc (sizeof (struct bas_DL_edge));
  bas_init_DL_edge (E);
  return E;
}

/*
 * texinfo: bas_set_DL_edge
 * Assign @var{F} to @var{E}.
 */

BAS_DLL void
bas_set_DL_edge (
    struct bas_DL_edge *E,
    struct bas_DL_edge *F)
{
  if (E != F)
    *E = *F;
}

/*
 * texinfo: bas_set_tsd_DL_edge
 * Assign @var{src}, @var{dst} and @var{type} to the corresponding
 * fields of @var{E}.
 */

BAS_DLL void
bas_set_tsd_DL_edge (
    struct bas_DL_edge *E,
    enum bas_typeof_DL_edge type,
    ba0_int_p src,
    ba0_int_p dst)
{
  E->type = type;
  E->src = src;
  E->dst = dst;
}

/*
 * readonly data
 */

static struct
{
  enum bas_typeof_DL_edge type;
  char *ident;
} bas_cases[] = { {bas_none_edge, "xxx"},
{bas_vanishing_edge, "van"},
{bas_non_vanishing_edge, "nvn"},
{bas_RG_edge, "RG"}
};

/*
 * texinfo: bas_typeof_DL_edge_to_string
 * Return a string encoding for @var{type}.
 * The encoding is given by the following table
 * @verbatim
 *       bas_none_edge
 * "van" bas_vanishing_edge
 * "nvn" bas_non_vanishing_edge
 * "RG"  bas_RG_edge
 * @end verbatim
 */

BAS_DLL char *
bas_typeof_DL_edge_to_string (
    enum bas_typeof_DL_edge type)
{
  bool found = false;
  ba0_int_p n = sizeof (bas_cases) / sizeof (bas_cases[0]);
  ba0_int_p i = 0;

  while (i < n && !found)
    {
      if (type == bas_cases[i].type)
        found = true;
      else
        i += 1;
    }
  if (!found)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  return bas_cases[i].ident;
}

/*
 * texinfo: bas_printf_DL_edge
 * The printing function for DL edges.
 * It is called by @code{ba0_printf/%DL_edge}.
 */

BAS_DLL void
bas_printf_DL_edge (
    void *A)
{
  struct bas_DL_edge *E = (struct bas_DL_edge *) A;
  char *ident = bas_typeof_DL_edge_to_string (E->type);

  ba0_printf ("<%s, %d, %d>", ident, E->src, E->dst);
}

static char _struct_DL_edge[] = "struct bas_DL_edge";

BAS_DLL ba0_int_p
bas_garbage1_DL_edge (
    void *A,
    enum ba0_garbage_code code)
{
  struct bas_DL_edge *E = (struct bas_DL_edge *) A;
  ba0_int_p n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (E, sizeof (struct bas_DL_edge), _struct_DL_edge);
  return n;
}

BAS_DLL void *
bas_garbage2_DL_edge (
    void *A,
    enum ba0_garbage_code code)
{
  struct bas_DL_edge *E;

  if (code == ba0_isolated)
    E = (struct bas_DL_edge *) ba0_new_addr_gc_info (A, _struct_DL_edge);
  else
    E = (struct bas_DL_edge *) A;

  return E;
}

BAS_DLL void *
bas_copy_DL_edge (
    void *A)
{
  struct bas_DL_edge *E;

  E = bas_new_DL_edge ();
  bas_set_DL_edge (E, (struct bas_DL_edge *) A);
  return E;
}
