#include "bav_ordering.h"
#include "bav_differential_ring.h"
#include "bav_global.h"

/*
 * texinfo: bav_set_settings_ordering
 * Set to @var{ordstring} the leading string used for parsing
 * and printing orderings. If zero, this leading string is reset 
 * to its default value: @code{ordering}.
 */

BAV_DLL void
bav_set_settings_ordering (
    char *ordstring)
{
  bav_initialized_global.ordering.string = ordstring ? ordstring : "ordering";
}

/*
 * texinfo: bav_get_settings_ordering
 * Assign to @var{ordstring} the leading string used for 
 * printing orderings.
 */

BAV_DLL void
bav_get_settings_ordering (
    char **ordstring)
{
  if (ordstring)
    *ordstring = bav_initialized_global.ordering.string;
}

/*
 * texinfo: bav_sizeof_ordering
 * Return the size needed to perform a copy of @var{ord}.
 * If @var{code} is @code{ba0_embedded} then @var{ord} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account.
 * If @var{strings_syms_and_vars_not_copied} is @code{true} then
 * the strings, symbols and variables occurring in @var{ord}
 * are supposed not to be copied.
 */

BAV_DLL unsigned ba0_int_p
bav_sizeof_ordering (
    struct bav_ordering *ord,
    enum ba0_garbage_code code,
    bool strings_syms_and_vars_not_copied)
{
  unsigned ba0_int_p size;

  if (!strings_syms_and_vars_not_copied)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  if (code == ba0_isolated)
    size = ba0_allocated_size (sizeof (struct bav_ordering));
  else
    size = 0;
  size += ba0_sizeof_table ((struct ba0_table *) &ord->ders, ba0_embedded);
  size += bav_sizeof_tableof_block (&ord->blocks, ba0_embedded,
      strings_syms_and_vars_not_copied);
  size += bav_sizeof_tableof_typed_ident (&ord->typed_idents, ba0_embedded,
      strings_syms_and_vars_not_copied);
  size += ba0_sizeof_dictionary_typed_string (&ord->dict, ba0_embedded);
  size += bav_sizeof_block (&ord->operator_block, ba0_embedded,
      strings_syms_and_vars_not_copied);
  size += ba0_sizeof_table ((struct ba0_table *) &ord->varmax, ba0_embedded);
  size += ba0_sizeof_table ((struct ba0_table *) &ord->varmin, ba0_embedded);
  return size;
}

/*
 * texinfo: bav_sizeof_tableof_ordering
 * Return the size needed to perform a copy of @var{T}.
 * If @var{code} is @code{ba0_embedded} then @var{T} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account.
 * If @var{strings_syms_and_vars_not_copied} is @code{true} then
 * the strings, symbols and variables occurring in the elements of @var{T}
 * are supposed not to be copied.
 */

BAV_DLL unsigned ba0_int_p
bav_sizeof_tableof_ordering (
    struct bav_tableof_ordering *T,
    enum ba0_garbage_code code,
    bool strings_syms_and_vars_not_copied)
{
  unsigned ba0_int_p size;
  ba0_int_p i;

  if (!strings_syms_and_vars_not_copied)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  size = ba0_sizeof_table ((struct ba0_table *) T, code);
  for (i = 0; i < T->size; i++)
    size += bav_sizeof_ordering (T->tab[i], ba0_isolated,
        strings_syms_and_vars_not_copied);
  return size;
}

/*
 * texinfo: bav_R_set_ordering
 * Copy @var{src} into @var{dst} without performing any string allocation.
 * The strings present in @var{src} are supposed to have copies in @var{R}.
 * Instead of duplicating them, the copies are used.
 * The needed size for the result is the one returned by
 * @code{bav_sizeof_ordering}.
 */

BAV_DLL void
bav_R_set_ordering (
    struct bav_ordering *dst,
    struct bav_ordering *src,
    struct bav_differential_ring *R)
{
  ba0_int_p i;
/*
 * The table of symbols ders - the symbols are not duplicated
 */
  ba0_realloc_table ((struct ba0_table *) &dst->ders, src->ders.size);
  for (i = 0; i < src->ders.size; i++)
    dst->ders.tab[i] = R->syms.tab[src->ders.tab[i]->index_in_syms];
  dst->ders.size = src->ders.size;
/*
 * The table of blocks - the strings are not duplicated
 */
  bav_R_set_tableof_block (&dst->blocks, &src->blocks, R);
/*
 * The table of typed ident - the strings are not copied
 */
  bav_R_set_tableof_typed_ident (&dst->typed_idents, &src->typed_idents, R);
  ba0_set_dictionary_typed_string (&dst->dict, &src->dict);
/*
 * The operator_block - the strings are not duplicated
 */
  bav_R_set_block (&dst->operator_block, &src->operator_block, R);
/*
 * The table varmax - the variables are not duplicated
 */
  ba0_realloc_table ((struct ba0_table *) &dst->varmax, src->varmax.size);
  for (i = 0; i < src->varmax.size; i++)
    dst->varmax.tab[i] = R->vars.tab[src->varmax.tab[i]->index_in_vars];
  dst->varmax.size = src->varmax.size;
/*
 * The table varmin - the variables are not duplicated
 */
  ba0_realloc_table ((struct ba0_table *) &dst->varmin, src->varmin.size);
  for (i = 0; i < src->varmin.size; i++)
    dst->varmin.tab[i] = R->vars.tab[src->varmin.tab[i]->index_in_vars];
  dst->varmin.size = src->varmin.size;
}

/*
 * texinfo: bav_R_set_tableof_ordering
 * Copy @var{src} into @var{dst} by calling
 * @code{bav_R_set_ordering}. See this function.
 */

BAV_DLL void
bav_R_set_tableof_ordering (
    struct bav_tableof_ordering *dst,
    struct bav_tableof_ordering *src,
    struct bav_differential_ring *R)
{
  ba0_int_p i;

  ba0_realloc2_table ((struct ba0_table *) dst, src->size,
      (ba0_new_function *) & bav_new_ordering);
  for (i = 0; i < src->size; i++)
    bav_R_set_ordering (dst->tab[i], src->tab[i], R);
  dst->size = src->size;
}

static char *
typed_ident_to_ident (
    void *object)
{
  struct bav_typed_ident *tid = (struct bav_typed_ident *) object;
  return tid->ident;
}

static ba0_int_p
typed_ident_to_type (
    void *object)
{
  struct bav_typed_ident *tid = (struct bav_typed_ident *) object;
  return tid->type;
}

/*
 * texinfo: bav_init_ordering
 * Initialize @var{o} to the empty ordering.
 */

BAV_DLL void
bav_init_ordering (
    struct bav_ordering *o)
{
  ba0_init_table ((struct ba0_table *) &o->ders);
  ba0_init_table ((struct ba0_table *) &o->blocks);
  ba0_init_table ((struct ba0_table *) &o->typed_idents);
  ba0_init_dictionary_typed_string (&o->dict, &typed_ident_to_ident,
      &typed_ident_to_type, 8);
  bav_init_block (&o->operator_block);
  ba0_init_table ((struct ba0_table *) &o->varmax);
  ba0_init_table ((struct ba0_table *) &o->varmin);
}

/*
 * texinfo: bav_reset_ordering
 * Empty the ordering @var{o}.
 */

BAV_DLL void
bav_reset_ordering (
    struct bav_ordering *o)
{
  ba0_reset_table ((struct ba0_table *) &o->ders);
  ba0_reset_table ((struct ba0_table *) &o->blocks);
  ba0_reset_table ((struct ba0_table *) &o->typed_idents);
  ba0_reset_dictionary_typed_string (&o->dict);
  bav_reset_block (&o->operator_block);
  ba0_reset_table ((struct ba0_table *) &o->varmax);
  ba0_reset_table ((struct ba0_table *) &o->varmin);
}

/*
 * texinfo: bav_new_ordering
 * Allocate a new ordering in the current stack, initialize it and
 * return it.
 */

BAV_DLL struct bav_ordering *
bav_new_ordering (
    void)
{
  struct bav_ordering *o;

  o = (struct bav_ordering *) ba0_alloc (sizeof (struct bav_ordering));
  bav_init_ordering (o);
  return o;
}

/*
 * texinfo: bav_set_ordering
 * Assign @var{S} to @var{R}.
 * The two orderings share their @code{blocks} field.
 */

BAV_DLL void
bav_set_ordering (
    struct bav_ordering *R,
    struct bav_ordering *S)
{
  ba0_int_p i;

  ba0_set_table ((struct ba0_table *) &R->ders, (struct ba0_table *) &S->ders);

  ba0_reset_table ((struct ba0_table *) &R->blocks);
  ba0_realloc2_table ((struct ba0_table *) &R->blocks, S->blocks.size,
      (ba0_new_function *) & bav_new_block);
  for (i = 0; i < S->blocks.size; i++)
    {
      R->blocks.tab[i]->subr = S->blocks.tab[i]->subr;
      ba0_set_table ((struct ba0_table *) &R->blocks.tab[i]->rigs,
          (struct ba0_table *) &S->blocks.tab[i]->rigs);
    }
  R->blocks.size = S->blocks.size;

  ba0_reset_table ((struct ba0_table *) &R->typed_idents);
  ba0_realloc2_table ((struct ba0_table *) &R->typed_idents,
      S->typed_idents.size, (ba0_new_function *) & bav_new_typed_ident);

  ba0_set_dictionary_typed_string (&R->dict, &S->dict);

  R->operator_block.subr = S->operator_block.subr;
  ba0_set_table ((struct ba0_table *) &R->operator_block.rigs,
      (struct ba0_table *) &S->operator_block.rigs);

  ba0_set_table ((struct ba0_table *) &R->varmax,
      (struct ba0_table *) &S->varmax);
  ba0_set_table ((struct ba0_table *) &R->varmin,
      (struct ba0_table *) &S->varmin);
}

/*
 * texinfo: bav_scanf_ordering
 * The general parsing function for orderings.
 * It can be called by @code{ba0_scanf/%ordering}.
 * Parsing the first ordering creates the mathematical differential ring.
 * The parsing grammar is the following.
 * @verbatim
 * ORDERING ::= START-KEYWORD "(" [FIRST-GROUP] ["," SECOND-GROUP] ")"
 * START-KEYWORD ::= ordering | DifferentialRing
 * FIRST-GROUP   ::= derivations = %t[%six] ["," FIRST_GROUP]
 *               ::= blocks = %t[%b] ["," FIRST_GROUP]
 *               ::= operator = %b ["," FIRST_GROUP]
 * SECOND-GROUP  ::= varmax = %t[%v] ["," SECOND-GROUP]
 *               ::= varmin = %t[%v] ["," SECOND-GROUP]
 *               ::= parameters = %t[%param] ["," SECOND-GROUP]
 * @end verbatim
 * Each keyword of each group must occur at most once.
 *
 * The @code{parameters = [...]} argument permits to define the
 * parameters of the mathematical differential ring. Though it is
 * slightly inconsistent to define parameters with orderings, their
 * definition has been inserted here for a tighter relationship
 * with the user interfaces of the @code{DifferentialAlgebra} packages.
 * This argument is used only when creating the first ordering (hence
 * the mathematical differential ring). For further orderings, it is
 * ignored and needs not be provided.
 *
 * Exception @code{BAV_ERRBOR} is raised in case of an error.
 */

BAV_DLL void *
bav_scanf_ordering (
    void *z)
{
  struct ba0_tableof_string *D;
  struct bav_tableof_block *B;
  struct bav_block *O;
  struct bav_tableof_variable *Vmax, *Vmin;
  struct bav_tableof_parameter *P;
  bav_Iordering r;
  struct ba0_mark M;
  ba0_int_p i;
  bool derivations, blocks, operator, varmax, varmin, parameters, R_was_empty;

  ba0_push_another_stack ();
  ba0_record (&M);
/*
 * START-KEYWORD
 */
  if (ba0_type_token_analex () != ba0_string_token ||
      (ba0_strcasecmp (ba0_value_token_analex (),
              bav_initialized_global.ordering.string) != 0 &&
          ba0_strcasecmp (ba0_value_token_analex (), "DifferentialRing") != 0))
    BA0_RAISE_PARSER_EXCEPTION (BAV_ERRBOR);
/*
 * Opening parenthesis
 */
  ba0_get_token_analex ();
  if (!ba0_sign_token_analex ("("))
    BA0_RAISE_PARSER_EXCEPTION (BAV_ERRBOR);
  ba0_get_token_analex ();

  D = (struct ba0_tableof_string *) ba0_new_table ();
  B = (struct bav_tableof_block *) ba0_new_table ();
  O = bav_new_block ();
/*
 * FIRST-GROUP
 */
  do
    {
      derivations = blocks = operator = false;
      if (ba0_type_token_analex () == ba0_string_token)
        {
          if (ba0_strcasecmp (ba0_value_token_analex (), "derivations") == 0)
            derivations = true;
          else if (ba0_strcasecmp (ba0_value_token_analex (), "blocks") == 0 ||
              ba0_strcasecmp (ba0_value_token_analex (), "ranking") == 0)
            blocks = true;
          else if (ba0_strcasecmp (ba0_value_token_analex (), "operator") == 0)
            operator = true;
        }

      if (derivations || blocks || operator)
        {
          ba0_get_token_analex ();
          if (!ba0_sign_token_analex ("="))
            BA0_RAISE_PARSER_EXCEPTION (BAV_ERRBOR);
          ba0_get_token_analex ();
        }

      BA0_TRY
      {
        if (derivations)
          {
            if (D->size > 0)
              BA0_RAISE_PARSER_EXCEPTION (BAV_ERRBOR);
            ba0_scanf ("%t[%six]", D);
          }
        else if (blocks)
          {
            if (B->size > 0)
              BA0_RAISE_PARSER_EXCEPTION (BAV_ERRBOR);
            ba0_scanf ("%t[%b]", B);

            i = 0;
            while (i < B->size)
              {
                if (bav_is_empty_block (B->tab[i]))
                  ba0_delete_table ((struct ba0_table *) B, i);
                else
                  i += 1;
              }
          }
        else if (operator)
          {
            if (O->rigs.size > 0)
              BA0_RAISE_PARSER_EXCEPTION (BAV_ERRBOR);
            ba0_scanf ("%b", O);
          }

        if (derivations || blocks || operator)
          {
            ba0_get_token_analex ();
            if (ba0_sign_token_analex (","))
              ba0_get_token_analex ();
          }
      }
      BA0_CATCH
      {
        if (ba0_global.exception.raised == BA0_ERROOM ||
            ba0_global.exception.raised == BA0_ERRALR)
          BA0_RE_RAISE_EXCEPTION;
        BA0_RAISE_EXCEPTION (BAV_ERRBOR);
      }
      BA0_ENDTRY;
    }
  while (derivations || blocks || operator);
/*
 * FIRST-GROUP is over. 
 * In the case of the first ordering, the mathematical ring is created
 */
  if (bav_is_empty_differential_ring (&bav_global.R))
    {
      R_was_empty = true;
      BA0_TRY
      {
        bav_R_create_differential_ring ((struct ba0_tableof_string *) D,
            (struct bav_tableof_block *) B, O);
      }
      BA0_CATCH
      {
        bav_init_differential_ring (&bav_global.R);
        BA0_RE_RAISE_EXCEPTION;
      }
      BA0_ENDTRY;
    }
  else
    R_was_empty = false;
/*
 * In any case we can endow the mathematical ring a first or a new ranking
 */
  r = bav_R_new_ranking ((struct ba0_tableof_string *) D,
      (struct bav_tableof_block *) B, O);
/*
 * Observe that r is not the current ordering but we can read variables
 */
  Vmax = (struct bav_tableof_variable *) ba0_new_table ();
  Vmin = (struct bav_tableof_variable *) ba0_new_table ();
  P = (struct bav_tableof_parameter *) ba0_new_table ();
/*
 * SECOND-GROUP
 */
  do
    {
      varmax = varmin = parameters = false;
      if (ba0_type_token_analex () == ba0_string_token)
        {
          if (ba0_strcasecmp (ba0_value_token_analex (), "varmax") == 0)
            varmax = true;
          else if (ba0_strcasecmp (ba0_value_token_analex (), "varmin") == 0)
            varmin = true;
          else if (ba0_strcasecmp (ba0_value_token_analex (),
                  "parameters") == 0)
            parameters = true;
        }

      BA0_TRY
      {
        if (varmax || varmin || parameters)
          {
            ba0_get_token_analex ();
            if (!ba0_sign_token_analex ("="))
              BA0_RAISE_PARSER_EXCEPTION (BAV_ERRBOR);
            ba0_get_token_analex ();
          }

        if (varmax)
          {
            if (Vmax->size > 0)
              BA0_RAISE_PARSER_EXCEPTION (BAV_ERRBOR);

            ba0_scanf ("%t[%v]", Vmax);
          }
        else if (varmin)
          {
            if (Vmin->size > 0)
              BA0_RAISE_PARSER_EXCEPTION (BAV_ERRBOR);

            ba0_scanf ("%t[%v]", Vmin);
          }
        else if (parameters)
          {
            if (P->size > 0)
              BA0_RAISE_PARSER_EXCEPTION (BAV_ERRBOR);

            ba0_scanf ("%t[%param]", P);
          }

        if (varmax || varmin || parameters)
          {
            ba0_get_token_analex ();
            if (ba0_sign_token_analex (","))
              ba0_get_token_analex ();
          }
      }
      BA0_CATCH
      {
        BA0_RE_RAISE_EXCEPTION;
      }
      BA0_ENDTRY;
    }
  while (varmax || varmin || parameters);
/*
 * Closing parenthesis
 */
  if (!ba0_sign_token_analex (")"))
    BA0_RAISE_PARSER_EXCEPTION (BAV_ERRBOR);
/*
 * Apply the varmax and varmin operations over r
 */
  bav_push_ordering (r);
  for (i = Vmax->size - 1; i >= 0; i--)
    bav_R_set_maximal_variable (Vmax->tab[i]);
  for (i = Vmin->size - 1; i >= 0; i--)
    bav_R_set_minimal_variable (Vmin->tab[i]);
  bav_pull_ordering ();
/*
 * Build the parameters of the ring - only in the case of the first ordering
 */
  if (R_was_empty)
    bav_R_set_parameters_tableof_parameter (&bav_global.R.pars, P);

  ba0_restore (&M);
  ba0_pull_stack ();

  if (z != (void *) 0)
    *(bav_Iordering *) z = r;

  return (void *) r;
}

/*
 * texinfo: bav_printf_ordering
 * The printing function for orderings.
 * It is called by @code{ba0_printf/%ordering}.
 */

BAV_DLL void
bav_printf_ordering (
    void *z)
{
  bav_Iordering r = (bav_Iordering) z;
  struct bav_ordering *O;
  struct ba0_mark M;

  ba0_record (&M);

  bav_push_ordering (r);

  O = bav_global.R.ords.tab[bav_current_ordering ()];

  ba0_printf ("%s ", bav_initialized_global.ordering.string);

  ba0_put_char ('(');
  ba0_printf ("derivations = %t[%y]", &O->ders);
  ba0_printf (", blocks = %t[%b]", &O->blocks);
  if (O->operator_block.rigs.size > 0)
    ba0_printf (", operator = %b", &O->operator_block);
  if (O->varmax.size != 0)
    ba0_printf (", varmax = %t[%v]", &O->varmax);
  if (O->varmin.size != 0)
    ba0_printf (", varmin = %t[%v]", &O->varmin);
  if (bav_global.R.pars.pars.size > 0)
    ba0_printf (", parameters = %t[%param]", &bav_global.R.pars.pars);
  ba0_put_char (')');

  bav_pull_ordering ();
  ba0_restore (&M);
}

/*
 * texinfo: bav_block_sort_tableof_variable
 * Assign each variable present in @var{X} to a table of @var{T}
 * or to @var{R}. Dependent variables which are moreover not present in
 * the @code{varmax} or @code{varmin} fields of the current ordering
 * are assigned to a table of @var{T}. The other variables are 
 * assigned to @var{R}. Each entry of @var{T} is assigned variables
 * which belong to the same block of the current ordering.
 * Leftmost blocks are higher than rightmost ones.
 * The entries of @var{T} are nonempty and are sorted in decreasing order.
 */

BAV_DLL void
bav_block_sort_tableof_variable (
    struct bav_tableof_tableof_variable *T,
    struct bav_tableof_variable *R,
    struct bav_tableof_variable *X)
{
  struct bav_ordering *O;
  ba0_int_p i;

  if (X == R)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  O = bav_global.R.ords.tab[bav_current_ordering ()];

  ba0_realloc2_table ((struct ba0_table *) T, O->typed_idents.size,
      (ba0_new_function *) & ba0_new_table);

  for (i = 0; i < O->typed_idents.size; i++)
    ba0_reset_table ((struct ba0_table *) T->tab[i]);
  T->size = O->typed_idents.size;

  ba0_reset_table ((struct ba0_table *) R);

  for (i = 0; i < X->size; i++)
    {
      struct bav_variable *v = X->tab[i];
      if (bav_symbol_type_variable (v) != bav_dependent_symbol ||
          ba0_member_table (v, (struct ba0_table *) &O->varmax) ||
          ba0_member_table (v, (struct ba0_table *) &O->varmin))
        {
          if (R->size == R->alloc)
            {
              ba0_int_p new_alloc = 2 * R->alloc + 1;
              ba0_realloc_table ((struct ba0_table *) R, new_alloc);
            }
          R->tab[R->size] = v;
          R->size += 1;
        }
      else
        {
          struct bav_tableof_variable *U;
          struct bav_typed_ident *tid;
          ba0_int_p j, k;

          j = bav_get_typed_ident_from_symbol (&O->dict, &O->typed_idents,
              v->root);
          if (j == BA0_NOT_AN_INDEX)
            BA0_RAISE_EXCEPTION (BA0_ERRALG);
          tid = O->typed_idents.tab[j];
          k = tid->indices.tab[0];

          U = T->tab[k];
          if (U->size == U->alloc)
            {
              ba0_int_p new_alloc = 2 * U->alloc + 1;
              ba0_realloc_table ((struct ba0_table *) U, new_alloc);
            }
          U->tab[U->size] = v;
          U->size += 1;
        }
    }

  i = 0;
  while (i < T->size)
    {
      if (T->tab[i]->size == 0)
        ba0_delete_table ((struct ba0_table *) T, i);
      else
        {
          bav_sort_tableof_variable (T->tab[i], ba0_descending_mode);
          i += 1;
        }
    }
  bav_sort_tableof_variable (R, ba0_descending_mode);
}

/*
 * texinfo: bav_R_compare_variable
 * Return @math{-1}, @math{0} or @math{1} if @math{v < w},
 * @math{v = w} or @math{v > w} with respect to the current ordering. 
 * This low level function should only be used when the numbers of
 * the variables with respect to the current ordering are not yet
 * computed.
 */

BAV_DLL int
bav_R_compare_variable (
    struct bav_variable *v,
    struct bav_variable *w)
{
  struct bav_ordering *O;
  struct bav_typed_ident *tid_v, *tid_w;
  ba0_int_p i, v_first_index, w_first_index;
  bool v_gt_w = false, found;
/*
 * Equality
 */
  if (v == w)
    return 0;

  O = bav_global.R.ords.tab[bav_current_ordering ()];
/*
 * First check if v or w belongs to varmax or varmin
 */
  found = false;
  i = 0;
  while (!found && i < O->varmax.size)
    {
      found = O->varmax.tab[i] == v || O->varmax.tab[i] == w;
      if (!found)
        i += 1;
    }
  if (found)
    {
      v_gt_w = O->varmax.tab[i] == v;
      return v_gt_w ? 1 : -1;
    }

  found = false;
  i = O->varmin.size - 1;
  while (!found && i >= 0)
    {
      found = O->varmin.tab[i] == v || O->varmin.tab[i] == w;
      if (!found)
        i -= 1;
    }
  if (found)
    {
      v_gt_w = O->varmin.tab[i] == w;
      return v_gt_w ? 1 : -1;
    }
/*
 * Then compare the types of v and w
 * If the types are equal, compare the block index
 * If they have the same block index, go to subranking
 */
  switch (v->root->type)
    {
    case bav_operator_symbol:
      switch (w->root->type)
        {
        case bav_operator_symbol:
          v_gt_w = O->operator_block.subr->inf (w, v,
              (struct bav_typed_ident *) 0,
              (struct bav_typed_ident *) 0, &O->ders);
          break;
        case bav_independent_symbol:
        case bav_dependent_symbol:
        case bav_temporary_symbol:
          v_gt_w = true;
        }
      break;
    case bav_dependent_symbol:
      switch (w->root->type)
        {
        case bav_operator_symbol:
          v_gt_w = false;
          break;
        case bav_dependent_symbol:

          i = bav_get_typed_ident_from_symbol (&O->dict, &O->typed_idents,
              v->root);
          if (i == BA0_NOT_AN_INDEX)
            BA0_RAISE_EXCEPTION (BA0_ERRALG);
          tid_v = O->typed_idents.tab[i];

          i = bav_get_typed_ident_from_symbol (&O->dict, &O->typed_idents,
              w->root);
          if (i == BA0_NOT_AN_INDEX)
            BA0_RAISE_EXCEPTION (BA0_ERRALG);
          tid_w = O->typed_idents.tab[i];

          v_first_index = tid_v->indices.tab[0];
          w_first_index = tid_w->indices.tab[0];

          if (v_first_index < w_first_index)
            v_gt_w = true;
          else if (v_first_index > w_first_index)
            v_gt_w = false;
          else
            v_gt_w = O->blocks.tab[v_first_index]->subr->inf
                (w, v, tid_w, tid_v, &O->ders);
          break;
        case bav_independent_symbol:
        case bav_temporary_symbol:
          v_gt_w = true;
        }
      break;
    case bav_independent_symbol:
      switch (w->root->type)
        {
        case bav_operator_symbol:
        case bav_dependent_symbol:
          v_gt_w = false;
          break;
        case bav_independent_symbol:
          found = false;
          i = 0;
          while (!found && i < O->ders.size)
            {
              found = O->ders.tab[i] == v->root || O->ders.tab[i] == w->root;
              if (!found)
                i++;
            }
          if (i == O->ders.size)
            BA0_RAISE_EXCEPTION (BA0_ERRALG);
          v_gt_w = O->ders.tab[i] == v->root;
          break;
        case bav_temporary_symbol:
          v_gt_w = true;
        }
      break;
    case bav_temporary_symbol:
      switch (w->root->type)
        {
        case bav_operator_symbol:
        case bav_dependent_symbol:
        case bav_independent_symbol:
          v_gt_w = false;
          break;
        case bav_temporary_symbol:
          v_gt_w = v->root->ident < w->root->ident;
          break;
        }
    }
  return v_gt_w ? 1 : -1;
}

/*
 * Variant of the above function, suited for qsort
 */

static int
bav_R_compare_variable_qsort (
    struct bav_variable **v,
    struct bav_variable **w)
{
  return bav_R_compare_variable (*v, *w);
}

/*
 * texinfo: bav_R_sort_tableof_variable
 * Sort @var{T} by increasing order with respect to the current
 * ordering. This low level function should only be used when the numbers of
 * the variables with respect to the current ordering are not yet
 * computed.
 */

BAV_DLL void
bav_R_sort_tableof_variable (
    struct bav_tableof_variable *T)
{
  qsort (T->tab, T->size, sizeof (struct bav_variable *),
      (int (*)(const void *, const void *)) &bav_R_compare_variable_qsort);
}

/*
 * texinfo: bav_R_lower_block_variables_and_range_indexed_strings
 * Assign to @var{V} all the differential indeterminates with plain
 * symbols which belong to blocks are lower than or equal to the one
 * with index @var{first_index} in the current ordering. 
 * Assign to @var{G} all the range indexed strings which belong to
 * the same blocks.
 */

BAV_DLL void
bav_R_lower_block_range_indexed_strings (
    struct ba0_tableof_range_indexed_group *G,
    ba0_int_p first_index)
{
  struct bav_ordering *ord;
  struct bav_typed_ident *tid;
  bav_Iordering r;
  ba0_int_p j, k, n;

  ba0_reset_table ((struct ba0_table *) G);

  if (first_index == BA0_NOT_AN_INDEX)
    return;

  r = bav_current_ordering ();
  ord = bav_global.R.ords.tab[r];
/*
 * We do not use the fact that ord->typed_idents is sorted since
 *      this is not explicit in its specification
 */
  n = 0;
  for (j = 0; j < ord->typed_idents.size; j++)
    {
      struct bav_typed_ident *tid = ord->typed_idents.tab[j];
      if (tid->indices.tab[0] >= first_index)
        n += 1;
    }

  ba0_realloc2_table ((struct ba0_table *) G, n,
      (ba0_new_function *) & ba0_new_range_indexed_group);

  for (j = 0; j < ord->typed_idents.size; j++)
    {
      tid = ord->typed_idents.tab[j];
      if (tid->indices.tab[0] >= first_index)
        {
          if (tid->type == bav_plain_ident)
            {
              ba0_set_range_indexed_group_string (G->tab[G->size], tid->ident);
              G->size += 1;
            }
          else
            {
              k = ba0_get_dictionary_string (&bav_global.R.dict_str_to_rig,
                  (struct ba0_table *) &bav_global.R.rigs, tid->ident);
              if (k == BA0_NOT_AN_INDEX)
                BA0_RAISE_EXCEPTION (BA0_ERRALG);
              ba0_set_range_indexed_group (G->tab[G->size],
                  bav_global.R.rigs.tab[k]);
              G->size += 1;
            }
        }
    }
}

/*
 * texinfo: bav_block_index_symbol
 * Return the block index @var{y} belongs to in the table of blocks
 * of the current ordering.
 */

BAV_DLL ba0_int_p
bav_block_index_symbol (
    struct bav_symbol *y)
{
  struct bav_ordering *ord;
  bav_Iordering r;
  ba0_int_p k;

  r = bav_current_ordering ();
  ord = bav_global.R.ords.tab[r];

  if (y->index_in_rigs == BA0_NOT_AN_INDEX)
    k = ba0_get_dictionary_typed_string (&ord->dict,
        (struct ba0_table *) &ord->typed_idents, y->ident, bav_plain_ident);
  else
    {
      char *ident = bav_global.R.rigs.tab[y->index_in_rigs]->strs.tab[0];
      k = ba0_get_dictionary_typed_string (&ord->dict,
          (struct ba0_table *) &ord->typed_idents, ident,
          bav_range_indexed_string_radical_ident);
    }
  if (k == BA0_NOT_AN_INDEX)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  return ord->typed_idents.tab[k]->indices.tab[0];
}

/*
 * texinfo: bav_block_index_range_indexed_group
 * Return the lowest block index the range indexed strings of @var{rig} 
 * belong to in the table of blocks of the current ordering.
 * Return @code{BA0_NOT_AN_INDEX} if one of the range indexed strings
 * is not recognized.
 */

BAV_DLL ba0_int_p
bav_block_index_range_indexed_group (
    struct ba0_range_indexed_group *rig)
{
  struct bav_ordering *ord;
  bav_Iordering r;
  ba0_int_p i, j, k;
  char *string;

  r = bav_current_ordering ();
  ord = bav_global.R.ords.tab[r];

  if (ba0_is_plain_string_range_indexed_group (rig, &string))
    k = ba0_get_dictionary_typed_string (&ord->dict,
        (struct ba0_table *) &ord->typed_idents, string, bav_plain_ident);
  else
    {
      k = BA0_NOT_AN_INDEX;
      for (i = 0; i < rig->strs.size; i++)
        {
          j = ba0_get_dictionary_typed_string (&ord->dict,
              (struct ba0_table *) &ord->typed_idents, rig->strs.tab[i],
              bav_range_indexed_string_radical_ident);
          if (k == BA0_NOT_AN_INDEX || k > j)
            k = j;
        }
    }
  if (k == BA0_NOT_AN_INDEX)
    return BA0_NOT_AN_INDEX;
  else
    return ord->typed_idents.tab[k]->indices.tab[0];
}

/*
 * texinfo: bav_block_index_parameter
 * Return the block index @var{p} belongs to in the table of blocks
 * of the current ordering. Return @code{BA0_NOT_AN_INDEX} if 
 * the parameter is not recognized.
 */

BAV_DLL ba0_int_p
bav_block_index_parameter (
    struct bav_parameter *p)
{
  return bav_block_index_range_indexed_group (&p->rig);
}

/*
 * texinfo: bav_has_varmax_current_ordering
 * Return @code{true} if the current ordering involves a @code{varmax}
 * definition.
 */

BAV_DLL bool
bav_has_varmax_current_ordering (
    void)
{
  struct bav_ordering *ord;
  bav_Iordering r;

  r = bav_current_ordering ();
  ord = bav_global.R.ords.tab[r];
  return ord->varmax.size > 0;
}
