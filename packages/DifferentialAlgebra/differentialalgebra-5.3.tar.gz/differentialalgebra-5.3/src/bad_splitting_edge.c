#include "bad_splitting_edge.h"

/*
 * texinfo: bad_init_splitting_edge
 * Initialize @var{E}.
 */

BAD_DLL void
bad_init_splitting_edge (
    struct bad_splitting_edge *E)
{
  E->type = bad_none_edge;
  E->src = BAD_NOT_A_NUMBER;
  E->dst = BAD_NOT_A_NUMBER;
  E->leader = BAV_NOT_A_VARIABLE;
  E->multiplicity = 0;
}

/*
 * texinfo: bad_new_splitting_edge
 * Allocate a new edge, initialize it and return it.
 */

BAD_DLL struct bad_splitting_edge *
bad_new_splitting_edge (
    void)
{
  struct bad_splitting_edge *E;

  E = (struct bad_splitting_edge *) ba0_alloc (sizeof (struct
          bad_splitting_edge));
  bad_init_splitting_edge (E);
  return E;
}

/*
 * texinfo: bad_set_splitting_edge
 * Assign @var{F} to @var{E}.
 */

BAD_DLL void
bad_set_splitting_edge (
    struct bad_splitting_edge *E,
    struct bad_splitting_edge *F)
{
  if (E != F)
    {
      E->type = F->type;
      E->src = F->src;
      E->dst = F->dst;
      E->leader = F->leader;
      E->multiplicity = F->multiplicity;
    }
}

/*
 * texinfo: bad_set_tsdvm_splitting_edge
 * Assign @var{type}, @var{src} and @var{dst} to the corresponding 
 * fields of @var{E}. Store @var{src_var} and @var{dst_var} in
 * the two first entries of the field @code{leaders} of @var{E}.
 */

BAD_DLL void
bad_set_tsdvm_splitting_edge (
    struct bad_splitting_edge *E,
    enum bad_typeof_splitting_edge type,
    ba0_int_p src,
    ba0_int_p dst,
    struct bav_variable *leader,
    ba0_int_p multiplicity)
{
  E->type = type;
  E->src = src;
  E->dst = dst;
  E->leader = leader;
  E->multiplicity = multiplicity;
}

/*
 * readonly data
 */

static struct
{
  enum bad_typeof_splitting_edge type;
  char *ident;
} bad_cases[] = { {bad_none_edge, "xxx"},
{bad_critical_pair_edge, "cri"},
{bad_critical_pair_novar_edge, "crik"},
{bad_redzero_edge, "rdz"},
{bad_first_edge, "frst"},
{bad_factor_edge, "fact"},
{bad_initial_edge, "ini"},
{bad_separant_edge, "sep"},
{bad_regularize_edge, "regu"},
{bad_reg_characteristic_edge, "regc"}
};

/*
 * texinfo: bad_typeof_splitting_edge_to_string
 * Return a string encoding for @var{type}.
 * The encoding is given by the following table
 * @verbatim
 * "xxx"  bad_none_edge
 * "cri"  bad_critical_pair_edge
 * "crik" bad_critical_pair_novar_edge
 * "rdz"  bad_redzero_edge
 * "frst" bad_first_edge
 * "fact" bad_factor_edge
 * "ini"  bad_initial_edge
 * "sep"  bad_separant_edge
 * "regu" bad_regularize_edge
 * "regc" bad_reg_characteristic_edge
 * @end verbatim
 */

BAD_DLL char *
bad_typeof_splitting_edge_to_string (
    enum bad_typeof_splitting_edge type)
{
  bool found = false;
  ba0_int_p n = (ba0_int_p) (sizeof (bad_cases) / sizeof (bad_cases[0]));
  ba0_int_p i = 0;

  while (i < n && !found)
    {
      if (type == bad_cases[i].type)
        found = true;
      else
        i += 1;
    }
  if (!found)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  return bad_cases[i].ident;
}

/*
 * texinfo: bad_has_var_typeof_splitting_edge
 * Return @code{true} if the @code{leader} field should be 
 * different from @code{BAV_NOT_A_VARIABLE}
 * for an edge of type @var{type}.
 */

BAD_DLL bool
bad_has_var_typeof_splitting_edge (
    enum bad_typeof_splitting_edge type)
{
  return type == bad_separant_edge;
}

/*
 * texinfo: bad_has_multiplicity_typeof_splitting_edge
 * Return @code{true} if the @code{mult} field is meaningful
 * for an edge of type @var{type}.
 */

BAD_DLL bool
bad_has_multiplicity_typeof_splitting_edge (
    enum bad_typeof_splitting_edge type)
{
  return type == bad_factor_edge;
}

/*
 * texinfo: bad_inequation_producing_splitting_edge
 * Return @code{true} if the edges of type @var{type}
 * are associated to splittings which generate inequations
 */

BAD_DLL bool
bad_inequation_producing_splitting_edge (
    enum bad_typeof_splitting_edge type)
{
  enum bad_typeof_splitting_edge T[] = { bad_first_edge, bad_factor_edge,
    bad_initial_edge, bad_separant_edge
  };

  ba0_int_p i, n = (ba0_int_p) (sizeof (T) / sizeof (T[0]));
  bool found = false;

  for (i = 0; i < n && !found; i++)
    found = type == T[i];

  return found;
}

/*
 * texinfo: bad_leader_symbol_splitting_edge
 * Return the symbol of the @code{leader} field of @var{E}.
 * Exception @code{BA0_ERRALG} is raised if the @code{leader} field
 * of @var{E} is @code{BAV_NOT_A_SYMBOL}.
 */

BAD_DLL struct bav_symbol *
bad_leader_symbol_splitting_edge (
    struct bad_splitting_edge *E)
{
  if (!bad_has_var_typeof_splitting_edge (E->type))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  return E->leader->root;
}

/*
 * texinfo: bad_scanf_splitting_edge
 * The parsing function for splitting edges.
 * It is called by @code{ba0_scanf/%splitting_edge}.
 * The expected syntax is 
 * @code{<type, src, dst>} or
 * @code{<type, src, dst, leader, multiplicity>}.
 */

BAD_DLL void *
bad_scanf_splitting_edge (
    void *A)
{
  struct bad_splitting_edge *E;
  enum bad_typeof_splitting_edge type = bad_none_edge;
  struct bav_variable *leader;
  ba0_int_p i, src, dst, n, multiplicity;
  char buffer[BA0_BUFSIZE];
  bool found;

  if (A == (void *) 0)
    E = bad_new_splitting_edge ();
  else
    E = (struct bad_splitting_edge *) A;

  if (!ba0_sign_token_analex ("<"))
    BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
  ba0_get_token_analex ();
  ba0_scanf ("%s, %d, %d", buffer, &src, &dst);

  found = false;
  i = 0;
  n = (ba0_int_p) (sizeof (bad_cases) / sizeof (bad_cases[0]));
  while (!found && i < n)
    {
      found = ba0_strcasecmp (buffer, bad_cases[i].ident) == 0;
      if (!found)
        i += 1;
    }
  if (found)
    type = bad_cases[i].type;
  else
    BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);

  ba0_get_token_analex ();
  if (bad_has_var_typeof_splitting_edge (type))
    ba0_scanf (", %v, %d", &leader, &multiplicity);
  else
    {
      leader = BAV_NOT_A_VARIABLE;
      multiplicity = 0;
    }

  ba0_get_token_analex ();
  if (!ba0_sign_token_analex (">"))
    BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);

  bad_set_tsdvm_splitting_edge (E, type, src, dst, leader, multiplicity);

  return E;
}

/*
 * texinfo: bad_printf_splitting_edge
 * The printing function for splitting edges.
 * It is called by @code{ba0_printf/%splitting_edge}.
 */

BAD_DLL void
bad_printf_splitting_edge (
    void *A)
{
  struct bad_splitting_edge *E = (struct bad_splitting_edge *) A;
  char *ident = bad_typeof_splitting_edge_to_string (E->type);

  if (bad_has_var_typeof_splitting_edge (E->type))
    ba0_printf ("<%s, %d, %d, %v, %d>", ident, E->src, E->dst, E->leader,
        E->multiplicity);
}

static char _struct_splitting_edge[] = "struct bad_splitting_edge";

static char _struct_splitting_edge_leaders[] =
    "struct bad_splitting_edge.leaders";

BAD_DLL ba0_int_p
bad_garbage1_splitting_edge (
    void *A,
    enum ba0_garbage_code code)
{
  struct bad_splitting_edge *E = (struct bad_splitting_edge *) A;
  ba0_int_p n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (E, sizeof (struct bad_splitting_edge),
        _struct_splitting_edge);
  return n;
}

BAD_DLL void *
bad_garbage2_splitting_edge (
    void *A,
    enum ba0_garbage_code code)
{
  struct bad_splitting_edge *E;

  if (code == ba0_isolated)
    E = (struct bad_splitting_edge *) ba0_new_addr_gc_info (A,
        _struct_splitting_edge);
  else
    E = (struct bad_splitting_edge *) A;

  return E;
}

BAD_DLL void *
bad_copy_splitting_edge (
    void *A)
{
  struct bad_splitting_edge *E;

  E = bad_new_splitting_edge ();
  bad_set_splitting_edge (E, (struct bad_splitting_edge *) A);
  return E;
}
