#include "bav_differential_ring.h"
#include "bav_global.h"

/*
 * For dict_str_to_var
 */

static char *
bav_variable_to_identifier (
    void *object)
{
  struct bav_variable *v = (struct bav_variable *) object;
  return v->root->ident;
}

/*
 * For dict_str_to_str
 */

static char *
bav_string_to_identifier (
    void *object)
{
  return (char *) object;
}

/*
 * For dict_str_to_rig
 */

static char *
bav_range_indexed_string_to_identifier (
    void *object)
{
  struct ba0_range_indexed_group *G = (struct ba0_range_indexed_group *) object;
  return G->strs.tab[0];
}

/*
 * texinfo: bav_init_differential_ring
 * Initialize @var{R} to the empty differential ring.
 */

BAV_DLL void
bav_init_differential_ring (
    struct bav_differential_ring *R)
{
  R->empty = true;
  ba0_init_table ((struct ba0_table *) &R->strs);
  ba0_init_table ((struct ba0_table *) &R->rigs);
  ba0_init_table ((struct ba0_table *) &R->syms);
  ba0_init_table ((struct ba0_table *) &R->vars);
  ba0_init_dictionary_string (&R->dict_str_to_str,
      &bav_string_to_identifier, 8);
  ba0_init_dictionary_string (&R->dict_str_to_var,
      &bav_variable_to_identifier, 8);
  ba0_init_dictionary_string (&R->dict_str_to_rig,
      &bav_range_indexed_string_to_identifier, 8);
  ba0_init_table ((struct ba0_table *) &R->ders);
  ba0_init_table ((struct ba0_table *) &R->tmps);
  ba0_init_table ((struct ba0_table *) &R->tmps_in_use);
  R->opra = BA0_NOT_AN_INDEX;
  ba0_init_table ((struct ba0_table *) &R->ords);
  ba0_init_table ((struct ba0_table *) &R->ord_stack);
  bav_init_parameters (&R->pars);
}

/*
 * texinfo: bav_is_empty_differential_ring
 * Return @code{true} if @var{R} is empty.
 */

BAV_DLL bool
bav_is_empty_differential_ring (
    struct bav_differential_ring *R)
{
  return R->empty;
}

/*
 * texinfo: bav_new_differential_ring
 * Allocate a new differential ring and initialize it.
 */

BAV_DLL struct bav_differential_ring *
bav_new_differential_ring (
    void)
{
  struct bav_differential_ring *R =
      ba0_alloc (sizeof (struct bav_differential_ring));
  bav_init_differential_ring (R);
  return R;
}

/*
 * Subfunction of bav_sizeof_differential_ring
 */

static unsigned ba0_int_p
bav_sizeof_variable (
    struct bav_variable *v)
{
  unsigned ba0_int_p size;

  size = ba0_allocated_size (sizeof (struct bav_variable));
  size += ba0_sizeof_table ((struct ba0_table *) &v->number, ba0_embedded);
  size += ba0_sizeof_table ((struct ba0_table *) &v->order, ba0_embedded);
  size += ba0_sizeof_table ((struct ba0_table *) &v->derivative, ba0_embedded);
  return size;
}

/* 
 * texinfo: bav_sizeof_differential_ring
 * Return the overall size of @var{R}: the one which is needed by
 * @code{bav_R_set_differential_ring} to perform a copy of @var{R}.
 * If @var{code} is @code{ba0_embedded} then @var{R} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account.
 */

BAV_DLL unsigned ba0_int_p
bav_sizeof_differential_ring (
    struct bav_differential_ring *R,
    enum ba0_garbage_code code)
{
  unsigned ba0_int_p size;
  ba0_int_p i;

  if (code == ba0_isolated)
    size = ba0_allocated_size (sizeof (struct bav_differential_ring));
  else
    size = 0;
/*
 * strs - strings are counted exactly once: here
 */
  size += ba0_sizeof_tableof_string (&R->strs, ba0_embedded);
/*
 * rigs - strings are supposed to be already copied
 */
  size += ba0_sizeof_tableof_range_indexed_group (&R->rigs, ba0_embedded, true);
/*
 * syms - symbols are counted exactly once: here
 */
  size += ba0_sizeof_table ((struct ba0_table *) &R->syms, ba0_embedded);
  for (i = 0; i < R->syms.size; i++)
    size += bav_sizeof_symbol (R->syms.tab[i], ba0_isolated, true);
/*
 * vars - variables are counted exactly once: here
 */
  size += ba0_sizeof_table ((struct ba0_table *) &R->vars, ba0_embedded);
  for (i = 0; i < R->vars.size; i++)
    size += bav_sizeof_variable (R->vars.tab[i]);
/*
 * the three dictionaries
 */
  size += ba0_sizeof_dictionary_string (&R->dict_str_to_str, ba0_embedded);
  size += ba0_sizeof_dictionary_string (&R->dict_str_to_var, ba0_embedded);
  size += ba0_sizeof_dictionary_string (&R->dict_str_to_rig, ba0_embedded);
/*
 * ders, tmps, tmps_in_use - all tables of ba0_int_p
 */
  size += ba0_sizeof_table ((struct ba0_table *) &R->ders, ba0_embedded);
  size += ba0_sizeof_table ((struct ba0_table *) &R->tmps, ba0_embedded);
  size += ba0_sizeof_table ((struct ba0_table *) &R->tmps_in_use, ba0_embedded);
/*
 * ords - strings, symbols and variables are supposed not to be copied
 */
  size += bav_sizeof_tableof_ordering (&R->ords, ba0_embedded, true);
/*
 * ord_stack - table of bav_Iordering i.e. ba0_int_p
 */
  size += ba0_sizeof_table ((struct ba0_table *) &R->ord_stack, ba0_embedded);
/*
 * pars
 */
  size += bav_sizeof_parameters (&R->pars, ba0_embedded, true);
  return size;
}

/*
 * texinfo: bav_R_set_differential_ring
 * Copy @var{S} into @var{R}.
 * The strings, symbols and variables, which are not duplicated in @var{S},
 * do not get duplicated in @var{R} either.
 * The needed size for the result is the one returned by
 * @code{bav_sizeof_differential_ring}.
 * This function is called from the @code{bmi} library.
 */

BAV_DLL void
bav_R_set_differential_ring (
    struct bav_differential_ring *R,
    struct bav_differential_ring *S)
{
  ba0_int_p i, j, new_alloc;
/*
 * Copy the bool
 */
  R->empty = S->empty;
/*
 * Copy the strings (full copy)
 */
  ba0_set_tableof_string (&R->strs, &S->strs);
/*
 * Copy the range indexed strings
 * 1. Get in T all the radicals of S.rigs
 * 2. For each of them, get its index j in S.strs and replace it 
 *      by R.strs.tab[j]
 */
  ba0_set_tableof_range_indexed_group_with_tableof_string (&R->rigs, &S->rigs,
      &S->dict_str_to_str, &R->strs);
/*
 * Copy the symbols (full copy)
 */
  ba0_realloc2_table ((struct ba0_table *) &R->syms, S->syms.size,
      (ba0_new_function *) & bav_new_symbol);
  for (i = 0; i < S->syms.size; i++)
    {
      struct bav_symbol *dst = R->syms.tab[i];
      struct bav_symbol *src = S->syms.tab[i];

      j = ba0_get_dictionary_string (&S->dict_str_to_str,
          (struct ba0_table *) &R->strs, src->ident);
      if (j == BA0_NOT_AN_INDEX)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);

      bav_R_set_symbol (dst, src, R->strs.tab[j]);
    }
  R->syms.size = S->syms.size;
/*
 * Copy the variables (full copy). 
 * It is interesting to oversize the table if we are restoring bav_global.R
 */
  if (R != &bav_global.R)
    new_alloc = S->vars.size;
  else if (S->vars.size < 15)
    new_alloc = 30;
  else
    new_alloc = 2 * S->vars.size;

  ba0_realloc2_table ((struct ba0_table *) &R->vars, new_alloc,
      (ba0_new_function *) & bav_new_variable);

  for (i = 0; i < S->vars.size; i++)
    {
      struct bav_variable *dst, *src;

      dst = R->vars.tab[i];
      src = S->vars.tab[i];
      bav_R_set_variable (dst, src, R);
    }
  R->vars.size = S->vars.size;
/*
 * Copy the three dictionaries
 */
  ba0_set_dictionary_string (&R->dict_str_to_str, &S->dict_str_to_str);
  ba0_set_dictionary_string (&R->dict_str_to_var, &S->dict_str_to_var);
  ba0_set_dictionary_string (&R->dict_str_to_rig, &S->dict_str_to_rig);
/*
 * Copy the easy tables (tables of ba0_int_p)
 */
  ba0_set_table ((struct ba0_table *) &R->ders, (struct ba0_table *) &S->ders);
  ba0_set_table ((struct ba0_table *) &R->tmps, (struct ba0_table *) &S->tmps);
  ba0_set_table ((struct ba0_table *) &R->tmps_in_use,
      (struct ba0_table *) &S->tmps_in_use);
/*
 * Copy opra
 */
  R->opra = S->opra;
/*
 * Copy the array of orderings
 */
  bav_R_set_tableof_ordering (&R->ords, &S->ords, R);
/*
 * Copy ord_stack (table of bav_Iordering = ba0_int_p)
 */
  ba0_set_table ((struct ba0_table *) &R->ord_stack,
      (struct ba0_table *) &S->ord_stack);
/*
 * Copy pars
 */
  bav_R_set_parameters (&R->pars, &S->pars, R);
}

/*
 * texinfo: bav_R_ambiguous_symbols
 * Return @code{true} if one of the symbols present in
 * @code{bav_global.R.syms} is an indexed string
 * terminated by an indexed string indices made of a sequence of 
 * independent symbols.
 */

BAV_DLL bool
bav_R_ambiguous_symbols (
    void)
{
  struct bav_symbol *y;
  struct ba0_mark M;
  struct ba0_indexed_string *indexed;
  struct ba0_indexed_string_indices *indices;
  ba0_int_p i;
  bool ambiguous, has_der_indices;

  ambiguous = false;
  ba0_record (&M);
  ba0_record_analex ();
  for (i = 0; i < bav_global.R.syms.size && !ambiguous; i++)
    {
      y = bav_global.R.syms.tab[i];
      ba0_set_analex_string (y->ident);
      ba0_get_token_analex ();
      indexed = ba0_scanf_indexed_string (0);
      has_der_indices =
          ba0_has_trailing_indices_indexed_string (indexed,
          &bav_is_a_derivation);
      if (has_der_indices)
        {
          indices = indexed->Tindic.tab[indexed->Tindic.size - 1];
          if (indices->Tindex.size > 0)
            ambiguous = true;
        }
    }
  ba0_restore_analex ();
  ba0_restore (&M);
  return ambiguous;
}

/*
 * Subfunction of bav_R_create_differential_ring.
 *
 * A symbol and a variable are created using (string, type, index_in_rigs)
 * This function may be called when the first ordering is not yet
 *  set so that we cannot compute numbers.
 *
 * index_in_rigs is BA0_NOT_AN_INDEX if ident is a tacky identifier or an 
 *      actual index in bav_global.R.rigs if ident fits some range
 *      indexed string
 *
 * subscripts = the trailing 'indexed string indices' in numeric form
 *      (if index_in_rigs != BA0_NOT_AN_INDEX) else the zero pointer.
 *
 * nbders is the number of derivations which may not yet be set.
 *      Otherwise, it is bav_global.R.ders.size
 *
 * Called from 
 * - bav_R_create_differential_ring.
 * - bav_R_new_symbol_and_variable for temporary variables or from parsers
 */

static struct bav_variable *
bav_R_create_symbol (
    char *ident,
    enum bav_typeof_symbol type,
    ba0_int_p index_in_rigs,
    struct ba0_tableof_int_p *subscripts,
    ba0_int_p nbders)
{
  struct bav_variable *v;
  struct bav_symbol *y;
  ba0_int_p j;
/*
 * ident should not already be present as a variable identifier
 * the next call may raise Exception BAV_ERRDSY
 */
  ba0_add_dictionary_string (&bav_global.R.dict_str_to_var,
      (struct ba0_table *) &bav_global.R.vars, ident, bav_global.R.vars.size);
/*
 * Register the string - It may already be present in strs as the
 *                       radical of a range indexed string
 */
  j = ba0_get_dictionary_string (&bav_global.R.dict_str_to_str,
      (struct ba0_table *) &bav_global.R.strs, ident);
  if (j == BA0_NOT_AN_INDEX)
    {
      j = bav_global.R.strs.size;

      ba0_add_dictionary_string (&bav_global.R.dict_str_to_str,
          (struct ba0_table *) &bav_global.R.strs, ident, j);

      if (bav_global.R.strs.size == bav_global.R.strs.alloc)
        ba0_realloc2_table
            ((struct ba0_table *) &bav_global.R.strs,
            2 * bav_global.R.strs.alloc + 1,
            (ba0_new_function *) & ba0_not_a_string);

      bav_global.R.strs.tab[j] = ba0_strdup (ident);
      bav_global.R.strs.size += 1;
    }
/*
 * Register the symbol - the string is in strs.tab[j]
 */
  if (bav_global.R.syms.size == bav_global.R.syms.alloc)
    ba0_realloc2_table
        ((struct ba0_table *) &bav_global.R.syms,
        2 * bav_global.R.syms.alloc + 1, (ba0_new_function *) & bav_new_symbol);

  y = bav_global.R.syms.tab[bav_global.R.syms.size];
  y->ident = bav_global.R.strs.tab[j];
  y->type = type;
  y->index_in_syms = bav_global.R.syms.size;
  y->index_in_rigs = index_in_rigs;
  if (subscripts != (struct ba0_tableof_int_p *) 0)
    ba0_set_table ((struct ba0_table *) &y->subscripts,
        (struct ba0_table *) subscripts);
  y->derivation_index = BA0_NOT_AN_INDEX;
  y->index_in_pars = BA0_NOT_AN_INDEX;
/*
 * The case of parameters.
 * The only case to handle is the one of a symbol which fits
 *      some range indexed string.
 * The other case cannot happen since, in this case, the parameter
 *      stored in bav_global.pars.pars is a symbol and must have
 *      been created already!
 */
  if (type == bav_dependent_symbol && index_in_rigs != BA0_NOT_AN_INDEX)
    {
      char *string = bav_global.R.rigs.tab[y->index_in_rigs]->strs.tab[0];
      j = ba0_get_dictionary_string (&bav_global.R.pars.dict,
          (struct ba0_table *) &bav_global.R.pars.pars, string);
      if (j != BA0_NOT_AN_INDEX)
        {
/*
 * The radical of y is the one of a parameter. 
 * We still need to check that the subscripts fit
 */
          struct ba0_range_indexed_group *rig;
          rig = &bav_global.R.pars.pars.tab[j]->rig;
          if (ba0_fit_indices_range_indexed_group (rig, &y->subscripts))
            y->index_in_pars = j;
        }
    }

  bav_global.R.syms.size += 1;
/*
 * Complete the variable registration
 */
  if (bav_global.R.vars.size == bav_global.R.vars.alloc)
    ba0_realloc2_table
        ((struct ba0_table *) &bav_global.R.vars,
        2 * bav_global.R.vars.alloc + 1,
        (ba0_new_function *) & bav_new_variable);

  v = bav_global.R.vars.tab[bav_global.R.vars.size];
  v->root = y;
  v->index_in_vars = bav_global.R.vars.size;
  ba0_reset_table ((struct ba0_table *) &v->number);
  ba0_reset_table ((struct ba0_table *) &v->order);
  ba0_reset_table ((struct ba0_table *) &v->derivative);

  bav_global.R.vars.size += 1;

  switch (type)
    {
    case bav_independent_symbol:
      if (bav_global.R.ders.size == bav_global.R.ders.alloc)
        {
          if (bav_global.R.ders.size == nbders)
            BA0_RAISE_EXCEPTION (BA0_ERRALG);
          ba0_realloc_table ((struct ba0_table *) &bav_global.R.ders, nbders);
        }
      y->derivation_index = bav_global.R.ders.size;
      bav_global.R.ders.tab[bav_global.R.ders.size] = v->index_in_vars;
      bav_global.R.ders.size += 1;
      break;
    case bav_dependent_symbol:
      break;
    case bav_temporary_symbol:
      if (bav_global.R.tmps.size == bav_global.R.tmps.alloc)
        ba0_realloc_table
            ((struct ba0_table *) &bav_global.R.tmps,
            2 * bav_global.R.tmps.alloc + 1);
      if (bav_global.R.tmps_in_use.size == bav_global.R.tmps_in_use.alloc)
        ba0_realloc_table ((struct ba0_table *) &bav_global.R.tmps_in_use,
            2 * bav_global.R.tmps_in_use.alloc + 1);
      bav_global.R.tmps.tab[bav_global.R.tmps.size] = v->index_in_vars;
      bav_global.R.tmps.size += 1;
      bav_global.R.tmps_in_use.tab[bav_global.R.tmps_in_use.size] = 1;
      bav_global.R.tmps_in_use.size += 1;
      break;
    case bav_operator_symbol:
      bav_global.R.opra = v->index_in_vars;
    }

  if (type == bav_dependent_symbol || type == bav_operator_symbol)
    {
      ba0_realloc_table ((struct ba0_table *) &v->order, nbders);
      ba0_realloc2_table
          ((struct ba0_table *) &v->derivative, nbders,
          (ba0_new_function *) & bav_not_a_variable);
      while (v->order.size < nbders)
        {
          v->order.tab[v->order.size++] = 0;
          v->derivative.tab[v->derivative.size++] = BAV_NOT_A_VARIABLE;
        }
    }

  return v;
}

static void
bav_R_create_range_indexed_strings (
    struct ba0_range_indexed_group *G)
{
  struct ba0_range_indexed_group tmp_G;
  struct ba0_mark M;
  ba0_int_p i, j, new_alloc;
/*
 * Register the range indexed string before it is created so that any
 * exception BAV_ERRDSY is raised immediately
 */
  for (i = 0; i < G->strs.size; i++)
    ba0_add_dictionary_string (&bav_global.R.dict_str_to_rig,
        (struct ba0_table *) &bav_global.R.rigs, G->strs.tab[i],
        bav_global.R.rigs.size + i);

  new_alloc = bav_global.R.rigs.size + G->strs.size;
  if (new_alloc > bav_global.R.rigs.alloc)
    {
      new_alloc = 2 * new_alloc + 1;
      ba0_realloc2_table ((struct ba0_table *) &bav_global.R.rigs,
          new_alloc, (ba0_new_function *) & ba0_new_range_indexed_group);
    }
/*
 * Register the strings in bav_global.R.strs.
 * Each of them may already present as a symbol identifier
 */
  for (i = 0; i < G->strs.size; i++)
    {
      char *string = G->strs.tab[i];

      j = ba0_get_dictionary_string (&bav_global.R.dict_str_to_str,
          (struct ba0_table *) &bav_global.R.strs, string);

      if (j == BA0_NOT_AN_INDEX)
        {
          j = bav_global.R.strs.size;

          ba0_add_dictionary_string (&bav_global.R.dict_str_to_str,
              (struct ba0_table *) &bav_global.R.strs, string, j);

          if (bav_global.R.strs.size == bav_global.R.strs.alloc)
            ba0_realloc2_table
                ((struct ba0_table *) &bav_global.R.strs,
                2 * bav_global.R.strs.alloc + 1,
                (ba0_new_function *) & ba0_not_a_string);

          bav_global.R.strs.tab[j] = ba0_strdup (string);
          bav_global.R.strs.size += 1;
        }
    }
/*
 * Fill the rigs table
 */
  ba0_push_another_stack ();
  ba0_record (&M);
/*
 * tmp_G is a range indexed string allocated in a temporary stack.
 * It is used to split the range indexed group G in many different
 *      range indexed strings.
 */
  ba0_init_range_indexed_group (&tmp_G);
  ba0_set_range_indexed_group (&tmp_G, G);
  tmp_G.strs.size = 1;
  ba0_pull_stack ();

  for (i = 0; i < G->strs.size; i++)
    {
      tmp_G.strs.tab[0] = G->strs.tab[i];
      ba0_set_range_indexed_group_with_tableof_string (bav_global.R.
          rigs.tab[bav_global.R.rigs.size], &tmp_G,
          &bav_global.R.dict_str_to_str, &bav_global.R.strs);
      bav_global.R.rigs.size += 1;
    }

  ba0_restore (&M);
}

/*
 * Subfunction of bav_R_create_differential_ring
 *
 * The block b may contain identifiers fors symbols or range indexed groups.
 * In the first case, bav_R_create_symbol is called
 * In the second case, bav_R_create_range_indexed_strings is called.
 */

static void
bav_R_create_block_symbols_and_range_indexed_strings (
    struct bav_block *b,
    enum bav_typeof_symbol type,
    ba0_int_p nbders)
{
  ba0_int_p i;
  char *string;

  for (i = 0; i < b->rigs.size; i++)
    if (ba0_is_plain_string_range_indexed_group (b->rigs.tab[i], &string))
      bav_R_create_symbol (string, type, BA0_NOT_AN_INDEX,
          (struct ba0_tableof_int_p *) 0, nbders);
    else
      bav_R_create_range_indexed_strings (b->rigs.tab[i]);
}

/*
 * texinfo: bav_R_create_differential_ring
 * Create in the quiet stack the mathematical differential polynomial 
 * ring over which all orderings will be defined using @var{D}
 * (the derivation list), @var{B} (the block list) and @var{O}
 * (the operator).
 * This function is called when parsing the first ordering in a 
 * sequence of calls to the library but does not define the ordering: 
 * this task is left to a following call to @code{bav_R_new_ordering}.
 * All symbol identifiers occurring in @var{D}, @var{B} and @var{O}
 * lead to new symbols and variables.
 * Exception @code{BA0_ERRALG} is raised if @code{bav_global.R} is
 * not empty.
 * Exceptions @code{BAV_ERRBOR} or @code{BAV_ERRDSY} are raised 
 * in case of a bad ordering.
 */

BAV_DLL void
bav_R_create_differential_ring (
    struct ba0_tableof_string *D,
    struct bav_tableof_block *B,
    struct bav_block *O)
{
  struct ba0_mark M;
  ba0_int_p i;

  if (!bav_is_empty_differential_ring (&bav_global.R))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_stack (&ba0_global.stack.quiet);
  ba0_record (&M);

  BA0_TRY
  {
    for (i = 0; i < D->size; i++)
      bav_R_create_symbol (D->tab[i], bav_independent_symbol,
          BA0_NOT_AN_INDEX, (struct ba0_tableof_int_p *) 0, D->size);
    for (i = 0; i < B->size; i++)
      bav_R_create_block_symbols_and_range_indexed_strings (B->tab[i],
          bav_dependent_symbol, D->size);
    if (O->rigs.size > 1 || (O->rigs.size == 1
            && !ba0_is_plain_string_range_indexed_group (O->rigs.tab[0],
                (char **) 0)))
      BA0_RAISE_EXCEPTION (BAV_ERRBOR);
    if (O->rigs.size == 1)
      bav_R_create_block_symbols_and_range_indexed_strings (O,
          bav_operator_symbol, D->size);
    else
      bav_global.R.opra = BA0_NOT_AN_INDEX;
    bav_global.R.empty = false;
  }
  BA0_CATCH
  {
    ba0_restore (&M);
    bav_init_differential_ring (&bav_global.R);
    BA0_RE_RAISE_EXCEPTION;
  }
  BA0_ENDTRY;

  ba0_pull_stack ();
}


/*
 * Compute the numbers of all variables with respect to ordering r.
 * This function is called when a new ordering has just been created.
 */

static void
bav_R_compute_numbers_all_variables (
    bav_Iordering r)
{
  struct bav_tableof_variable T;
  struct ba0_mark M;
  ba0_int_p i;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_init_table ((struct ba0_table *) &T);
  ba0_set_table ((struct ba0_table *) &T,
      (struct ba0_table *) &bav_global.R.vars);
  ba0_pull_stack ();

  bav_push_ordering (r);
/*
 * Sort T by increasing order
 */
  bav_R_sort_tableof_variable (&T);
  for (i = 0; i < T.size; i++)
    T.tab[i]->number.tab[r] = i;

  bav_pull_ordering ();

  ba0_restore (&M);
}

/*
 * A new variable has just been appended to bav_global.R.vars
 * This function recomputes the numbers of all the variables with
 *  respect to ordering r.
 * It is called by 
 * - bav_R_new_derivative and 
 * - bav_R_new_symbol_and_variable
 */

static void
bav_R_recompute_numbers_after_insertion_of_last_variable (
    bav_Iordering r)
{
  struct bav_variable *v;
  struct bav_variable *w;
  bav_Inumber lower_bound;
  ba0_int_p i;
/*
 * The new variable - which has no number
 */
  v = bav_global.R.vars.tab[bav_global.R.vars.size - 1];

  bav_push_ordering (r);
/*
 * lower_bound = the max of the numbers of the variables less than v
 * increase the number of each variable greater than v
 */
  lower_bound = -1;
  for (i = 0; i < bav_global.R.vars.size - 1; i++)
    {
      int code;

      w = bav_global.R.vars.tab[i];
      code = bav_R_compare_variable (w, v);
      if (code == 0)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
      else if (code < 0)
        {
          if (lower_bound < w->number.tab[r])
            lower_bound = w->number.tab[r];
        }
      else
        w->number.tab[r] += 1;
    }
  v->number.tab[r] = lower_bound + 1;

  bav_pull_ordering ();
}

/*
 * Subfunction of bav_R_new_temporary_variable
 *
 * Increase by 1 the numbers of all variables with respect to ordering r
 */

static void
bav_R_increase_numbers_all_variables (
    bav_Iordering r)
{
  struct bav_variable *v;
  ba0_int_p i;

  for (i = 0; i < bav_global.R.vars.size; i++)
    {
      v = bav_global.R.vars.tab[i];
      v->number.tab[r] += 1;
    }
}

/*
 * texinfo: bav_R_new_temporary_variable
 * Return a new temporary variable.
 * Its symbol has type @code{bav_temporary_symbol}.
 */

BAV_DLL struct bav_variable *
bav_R_new_temporary_variable (
    void)
{
  char string[64];
  struct bav_variable *v;
  ba0_int_p i;
  bool found;
/*
 * Look for an already defined but unused temporary variable
 */
  i = 0;
  found = false;
  while (i < bav_global.R.tmps.size && !found)
    {
      found = bav_global.R.tmps_in_use.tab[i] == 0;
      if (!found)
        i++;
    }

  if (found)
    {
      v = bav_global.R.vars.tab[bav_global.R.tmps.tab[i]];
      bav_global.R.tmps_in_use.tab[i] = 1;
    }
  else
    {
/*
 * Create a new temporary variable
 */
      int k = 0;
/*
 * Look for an unused variable identifier
 */
      do
        {
          sprintf (string, "%s[%d]",
              bav_initialized_global.variable.temp_string, k++);
          i = ba0_get_dictionary_string (&bav_global.R.dict_str_to_var,
              (struct ba0_table *) &bav_global.R.vars, string);
        }
      while (i != BA0_NOT_AN_INDEX);

      v = bav_R_new_symbol_and_variable (string, bav_temporary_symbol,
          BA0_NOT_AN_INDEX, (struct ba0_tableof_int_p *) 0);
    }
  return v;
}

/*
 * texinfo: bav_R_new_symbol_and_variable
 * This low level function creates a new symbol and the corresponding
 * new variable using @var{ident}, @var{type}, @var{index_in_rigs}
 * and @var{subscripts}.
 * If @var{index_in_rigs} is not @code{BA0_NOT_AN_INDEX} then
 * the trailing indexed string indices of @var{ident} forms a 
 * sequence of integers, which is stored in numeric form in
 * @var{subscripts}. Otherwise, @var{subscripts} may be zero.
 * The function is called from the parsers and by 
 * @code{bav_R_new_temporary_variable}.
 */

BAV_DLL struct bav_variable *
bav_R_new_symbol_and_variable (
    char *ident,
    enum bav_typeof_symbol type,
    ba0_int_p index_in_rigs,
    struct ba0_tableof_int_p *subscripts)
{
  struct bav_variable *v;
  bav_Iordering r;

  ba0_push_stack (&ba0_global.stack.quiet);
/*
 * The call to bav_R_create_symbol creates the symbol and the variable
 *      but without its number table.
 */
  v = bav_R_create_symbol (ident, type, index_in_rigs,
      subscripts, bav_global.R.ders.size);
/*
 * Create the missing number array
 */
  ba0_realloc_table ((struct ba0_table *) &v->number, bav_global.R.ords.alloc);
  v->number.size = bav_global.R.ords.size;

  ba0_pull_stack ();

  if (type == bav_temporary_symbol)
    {
/*
 * The new temporary variable v is lower than any other variable.
 * Thus it receives number 0 with respect to all orderings while
 *      all other variables get their number increased by one.
 */
      for (r = 0; r < bav_global.R.ords.size; r++)
        {
          bav_R_increase_numbers_all_variables (r);
          v->number.tab[r] = 0;
        }
    }
  else
    {
      for (r = 0; r < bav_global.R.ords.size; r++)
        bav_R_recompute_numbers_after_insertion_of_last_variable (r);
    }

  return v;
}

/*
 * texinfo: bav_R_free_temporary_variable
 * Declare the temporary variable @var{v} as logically free.
 * The next call to @code{bav_R_new_temporary_variable}
 * may then return @var{v} instead of creating some new symbol.
 */

BAV_DLL void
bav_R_free_temporary_variable (
    struct bav_variable *v)
{
  ba0_int_p i;
  bool found;

  if (v->root->type != bav_temporary_symbol)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  i = 0;
  found = false;
  while (i < bav_global.R.tmps.size && !found)
    {
      found = bav_global.R.tmps.tab[i] == v->index_in_vars;
      if (!found)
        i += 1;
    }
  if (!found)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  bav_global.R.tmps_in_use.tab[i] = 0;
}

/*
 * Subfunction of bav_R_check_new_ranking
 *
 * Check that all the strings occurring in the block b can
 * be converted to a symbol of type type.
 */

static void
bav_R_check_block_new_ranking (
    struct bav_block *b,
    enum bav_typeof_symbol type)
{
  ba0_int_p i;
  char *string;

  for (i = 0; i < b->rigs.size; i++)
    if (ba0_is_plain_string_range_indexed_group (b->rigs.tab[i], &string))
      {
        struct bav_symbol *y = bav_R_string_to_existing_symbol (string);
        if (y == BAV_NOT_A_SYMBOL)
          BA0_RAISE_EXCEPTION (BAV_ERRUSY);
        if (y->type != type)
          BA0_RAISE_EXCEPTION (BAV_ERRBOR);
      }
    else
      {
        struct ba0_range_indexed_group *g = b->rigs.tab[i];
        ba0_int_p j, k;

        for (j = 0; j < g->strs.size; j++)
          {
            k = ba0_get_dictionary_string (&bav_global.R.dict_str_to_rig,
                (struct ba0_table *) &bav_global.R.rigs, g->strs.tab[j]);
            if (k == BA0_NOT_AN_INDEX)
              BA0_RAISE_EXCEPTION (BA0_ERRALG);
            if (!ba0_compatible_indices_range_indexed_group (g,
                    bav_global.R.rigs.tab[k]))
              BA0_RAISE_EXCEPTION (BAV_ERRRIG);
          }
      }
}

/*
 * Subfunction of bav_R_new_ranking
 *
 * Check the consistency of the new ranking.
 * In case of an error, an exception is raised.
 */

static void
bav_R_check_new_ranking (
    struct ba0_tableof_string *D,
    struct bav_tableof_block *B,
    struct bav_block *O)
{
  struct bav_symbol *y;
  ba0_int_p i;
  bool first_ranking;
/*
 * First the tests which hold even for the very first ranking
 */
  if (bav_is_empty_differential_ring (&bav_global.R))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (D->size != bav_global.R.ders.size)
    BA0_RAISE_EXCEPTION (BAV_ERRBOR);
/*
 * One still needs to check that symbols and radicals of range indexed
 * strings are not duplicated - to be done
 */
  if ((O->rigs.size == 0 && bav_global.R.opra >= 0) ||
      (O->rigs.size == 1 && bav_global.R.opra == BA0_NOT_AN_INDEX)
      || O->rigs.size > 1)
    BA0_RAISE_EXCEPTION (BAV_ERRBOR);

  first_ranking = bav_global.R.ords.size == 0;
/*
 * Functions such as bav_R_string_to_existing_symbol do not
 *      work when a first ordering has not yet been created
 */
  if (!first_ranking)
    {
      for (i = 0; i < D->size; i++)
        {
          y = bav_R_string_to_existing_symbol (D->tab[i]);
          if (y == BAV_NOT_A_SYMBOL)
            BA0_RAISE_EXCEPTION (BAV_ERRUSY);
          if (y->type != bav_independent_symbol)
            BA0_RAISE_EXCEPTION (BAV_ERRBOR);
        }

      for (i = 0; i < B->size; i++)
        bav_R_check_block_new_ranking (B->tab[i], bav_dependent_symbol);
      if (O->rigs.size == 1)
        bav_R_check_block_new_ranking (O, bav_operator_symbol);
    }
}

static bav_Iordering
bav_R_create_new_ranking (
    struct ba0_tableof_string *D,
    struct bav_tableof_block *B,
    struct bav_block *O)
{
  struct bav_ordering *ord;
  struct bav_symbol *y;
  ba0_int_p i;

  ba0_push_stack (&ba0_global.stack.quiet);
/*
 * If bav_global.R.ords is resized then so is v->number for any variable v.
 */
  if (bav_global.R.ords.size == bav_global.R.ords.alloc)
    {
      ba0_realloc2_table
          ((struct ba0_table *) &bav_global.R.ords,
          2 * bav_global.R.ords.alloc + 1,
          (ba0_new_function *) & bav_new_ordering);
      for (i = 0; i < bav_global.R.vars.size; i++)
        ba0_realloc_table
            ((struct ba0_table *) &bav_global.R.vars.tab[i]->number,
            bav_global.R.ords.alloc);
    }
/*
 * There should only be memory allocation failures. Anyway ...
 */
  BA0_TRY
  {
    ord = bav_global.R.ords.tab[bav_global.R.ords.size++];
    bav_reset_ordering (ord);

    for (i = 0; i < bav_global.R.vars.size; i++)
      bav_global.R.vars.tab[i]->number.size = bav_global.R.ords.size;

    ba0_realloc_table ((struct ba0_table *) &ord->ders, D->size);
    while (ord->ders.size < D->size)
      {
        y = bav_R_string_to_existing_symbol (D->tab[ord->ders.size]);
        ord->ders.tab[ord->ders.size++] = y;
      }
/*
 * The strings present in B are not copied: the ones present in 
 *  bav_global.R are used
 */
    bav_R_set_tableof_block (&ord->blocks, B, &bav_global.R);
    bav_R_set_tableof_typed_ident_tableof_block (&ord->typed_idents,
        &ord->blocks, &bav_global.R);
    for (i = 0; i < ord->typed_idents.size; i++)
      ba0_add_dictionary_typed_string (&ord->dict,
          (struct ba0_table *) &ord->typed_idents,
          ord->typed_idents.tab[i]->ident, ord->typed_idents.tab[i]->type, i);

    if (O->rigs.size == 1)
      bav_R_set_block (&ord->operator_block, O, &bav_global.R);

    bav_R_compute_numbers_all_variables (bav_global.R.ords.size - 1);
  }
  BA0_CATCH
  {
/*
 * Annihilate the new ordering in the case of a failure.
 */
    bav_global.R.ords.size -= 1;
    for (i = 0; i < bav_global.R.vars.size; i++)
      bav_global.R.vars.tab[i]->number.size = bav_global.R.ords.size;

    BA0_RE_RAISE_EXCEPTION;
  }
  BA0_ENDTRY;

  ba0_pull_stack ();
  return bav_global.R.ords.size - 1;
}

/*
 * texinfo: bav_R_new_ranking.
 * Create a new ranking, store it in @code{bav_global.R} and return the
 * index in @code{bav_global.R.ords} which identifies it.
 * This function is called by @code{bav_scanf_ordering}.
 */

BAV_DLL bav_Iordering
bav_R_new_ranking (
    struct ba0_tableof_string *D,
    struct bav_tableof_block *B,
    struct bav_block *O)
{
  bav_Iordering r;

  bav_R_check_new_ranking (D, B, O);
  r = bav_R_create_new_ranking (D, B, O);
  return r;
}

/*
 * texinfo: bav_R_add_block_to_all_orderings
 * Add the block @var{B} to all the orderings of @code{bav_global.R}
 * with block number equal to @var{block_number}.
 * The block number is restricted to the values @math{0} (the new
 * block is higher than any other block) or @math{-1} (the new
 * block is lower than any other block).
 */

BAV_DLL void
bav_R_add_block_to_all_orderings (
    struct bav_block *B,
    ba0_int_p block_number)
{
  ba0_int_p i, old_size;

  if (block_number != -1)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  ba0_push_stack (&ba0_global.stack.quiet);
/*
 * First create all symbols and variables from the block.
 * The call to bav_R_create_block_symbols_and_range_indexed_strings
 *      does not handle the number fields of the new variables.
 * These number fields are thus reallocated afterwards
 */
  old_size = bav_global.R.vars.size;

  bav_R_create_block_symbols_and_range_indexed_strings (B,
      bav_dependent_symbol, bav_global.R.ders.size);

  for (i = old_size; i < bav_global.R.vars.size; i++)
    {
      struct bav_variable *v = bav_global.R.vars.tab[i];
      ba0_realloc_table ((struct ba0_table *) &v->number,
          bav_global.R.ords.size);
      v->number.size = v->number.alloc;
    }
/*
 * Add the new block to each ordering
 */
  for (i = 0; i < bav_global.R.ords.size; i++)
    {
      struct bav_ordering *ord;
      ba0_int_p numb, j;

      ord = bav_global.R.ords.tab[i];

      if (block_number == 0)
        numb = 0;
      else
        numb = ord->blocks.size;

      if (ord->blocks.size == ord->blocks.alloc)
        {
          ba0_int_p new_alloc = 2 * ord->blocks.alloc + 1;

          ba0_realloc2_table ((struct ba0_table *) &ord->blocks,
              new_alloc, (ba0_new_function *) & bav_new_block);
        }
      bav_R_set_block (ord->blocks.tab[ord->blocks.size], B, &bav_global.R);
      ord->blocks.size += 1;

      old_size = ord->typed_idents.size;
      bav_R_append_tableof_typed_ident_block (&ord->typed_idents, numb,
          ord->blocks.tab[ord->blocks.size - 1], &bav_global.R);
      for (j = old_size; j < ord->typed_idents.size; j++)
        ba0_add_dictionary_typed_string (&ord->dict,
            (struct ba0_table *) &ord->typed_idents,
            ord->typed_idents.tab[j]->ident, ord->typed_idents.tab[j]->type, j);

      bav_R_compute_numbers_all_variables (i);
    }

  ba0_pull_stack ();
}

/*
 * texinfo: bav_R_copy_ordering
 * Duplicate an already existing ordering and return its identifier.
 * The two orderings share their @code{blocks} field.
 */

BAV_DLL bav_Iordering
bav_R_copy_ordering (
    bav_Iordering r)
{
  struct bav_variable *v;
  ba0_int_p i;

  if (bav_is_empty_differential_ring (&bav_global.R) || r < 0
      || r >= bav_global.R.ords.size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_stack (&ba0_global.stack.quiet);
/*
 * If bav_global.R.ords is resized then so is v->number for any variable v.
 */
  if (bav_global.R.ords.size == bav_global.R.ords.alloc)
    {
      ba0_realloc2_table
          ((struct ba0_table *) &bav_global.R.ords,
          2 * bav_global.R.ords.alloc + 1,
          (ba0_new_function *) & bav_new_ordering);
      for (i = 0; i < bav_global.R.vars.size; i++)
        ba0_realloc_table
            ((struct ba0_table *) &bav_global.R.vars.tab[i]->number,
            bav_global.R.ords.alloc);
    }

  bav_set_ordering (bav_global.R.ords.tab[bav_global.R.ords.size],
      bav_global.R.ords.tab[r]);

  bav_global.R.ords.size++;
  for (i = 0; i < bav_global.R.vars.size; i++)
    {
      v = bav_global.R.vars.tab[i];
      v->number.tab[v->number.size++] = v->number.tab[r];
    }

  ba0_pull_stack ();

  return bav_global.R.ords.size - 1;
}

/*
 * texinfo: bav_R_free_ordering
 * Free the ordering @var{r}.
 * This function requires that @var{r} is the index of the
 * last created ordering.
 */

BAV_DLL void
bav_R_free_ordering (
    bav_Iordering r)
{
  ba0_int_p i;

  if (bav_global.R.ords.size == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (r == bav_global.R.ords.size - 1)
    {
      bav_global.R.ords.size -= 1;
      for (i = 0; i < bav_global.R.vars.size; i++)
        bav_global.R.vars.tab[i]->number.size -= 1;
    }
  else
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);
}

/*
 * texinfo: bav_R_restore_ords_size
 * This function is automatically called when an exception is raised.
 * It frees all the orderings that were created after the exception
 * point was set. See @code{ba0_global.exception.extra_stack}.
 */

BAV_DLL void
bav_R_restore_ords_size (
    ba0_int_p size)
{
  if (size > bav_global.R.ords.size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  while (bav_global.R.ords.size > size)
    bav_R_free_ordering (bav_global.R.ords.size - 1);
}

/*
 * Return @code{true} if @var{r} corresponds to an existing ordering.
 */

static bool
bav_exists_ordering (
    bav_Iordering r)
{
  return r >= 0 && r < bav_global.R.ords.size;
}

/*
 * texinfo: bav_R_swap_ordering
 * Swap the orderings @var{r} and @var{rbar}.
 * This function may be useful to free an ordering which is not the last
 * created one (see @code{bav_R_free_ordering}).
 */

BAV_DLL void
bav_R_swap_ordering (
    bav_Iordering r,
    bav_Iordering rbar)
{
  struct bav_variable *v;
  ba0_int_p i;

  if (!bav_exists_ordering (r) || !bav_exists_ordering (rbar))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  BA0_SWAP (struct bav_ordering *,
      bav_global.R.ords.tab[r],
      bav_global.R.ords.tab[rbar]);

  for (i = 0; i < bav_global.R.vars.size; i++)
    {
      v = bav_global.R.vars.tab[i];
      BA0_SWAP (bav_Inumber, v->number.tab[r], v->number.tab[rbar]);
    }
}

/*
 * texinfo: bav_push_ordering
 * Push @var{r} on the top of the ordering stack
 * @code{bav_global.R.ord_stack}.
 * The ordering @var{r} becomes the current ordering.
 */

BAV_DLL void
bav_push_ordering (
    bav_Iordering r)
{
  if (!bav_exists_ordering (r))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (bav_global.R.ord_stack.size == bav_global.R.ord_stack.alloc)
    {
      ba0_push_stack (&ba0_global.stack.quiet);
      ba0_realloc_table
          ((struct ba0_table *) &bav_global.R.ord_stack,
          2 * bav_global.R.ord_stack.alloc + 1);
      ba0_pull_stack ();
    }
  bav_global.R.ord_stack.tab[bav_global.R.ord_stack.size++] = r;
}

/*
 * texinfo: bav_pull_ordering
 * Undo the last call to @code{bav_push_ordering}.
 */

BAV_DLL void
bav_pull_ordering (
    void)
{
  if (bav_global.R.ord_stack.size == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  bav_global.R.ord_stack.size -= 1;
}

/*
 * texinfo: bav_current_ordering
 * Return the current ordering.
 */

BAV_DLL bav_Inumber
bav_current_ordering (
    void)
{
  if (bav_global.R.ord_stack.size == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  return bav_global.R.ord_stack.tab[bav_global.R.ord_stack.size - 1];
}

/*
 * texinfo: bav_R_new_derivative
 * Return the derivative of @var{v} with respect to @var{d} assuming this
 * derivative is not already stored in the @code{derivative} field of
 * @var{v}. 
 * This low level function is called by @code{bav_diff_variable}.
 */

BAV_DLL struct bav_variable *
bav_R_new_derivative (
    struct bav_variable *v,
    struct bav_symbol *d)
{
  struct bav_variable *w = BAV_NOT_A_VARIABLE;
  bav_Iordering r;
  ba0_int_p i;

  if (bav_is_empty_differential_ring (&bav_global.R)
      || (v->root->type != bav_dependent_symbol
          && v->root->type != bav_operator_symbol))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
/*
 * First check if the derivative is already present in bav_global.R.vars
 * This case may only occur in the partial case
 */
  if (bav_global.R.ders.size > 1)
    {
      for (i = 0; i < bav_global.R.vars.size; i++)
        if (bav_global.R.vars.tab[i]->root->type != bav_independent_symbol
            && bav_is_d_derivative (bav_global.R.vars.tab[i], v, d))
          return bav_global.R.vars.tab[i];
    }
/*
 * Let us create it.
 */
  ba0_push_stack (&ba0_global.stack.quiet);

  if (bav_global.R.vars.size == bav_global.R.vars.alloc)
    ba0_realloc2_table
        ((struct ba0_table *) &bav_global.R.vars,
        2 * bav_global.R.vars.alloc + 1,
        (ba0_new_function *) & bav_new_variable);

  BA0_TRY
  {
    w = bav_global.R.vars.tab[bav_global.R.vars.size++];

    w->root = v->root;
    w->index_in_vars = bav_global.R.vars.size - 1;
    ba0_realloc_table ((struct ba0_table *) &w->number,
        bav_global.R.ords.alloc);
    ba0_realloc_table ((struct ba0_table *) &w->order, bav_global.R.ders.alloc);
    ba0_realloc2_table ((struct ba0_table *) &w->derivative,
        bav_global.R.ders.alloc, (ba0_new_function *) & bav_not_a_variable);
/*
 * Update the order field of w
 */
    for (i = 0; i < v->order.size; i++)
      w->order.tab[i] = v->order.tab[i];
    w->order.tab[d->derivation_index] += 1;
    w->order.size = v->order.size;
/*
 * Update the derivative field of w
 */
    for (i = 0; i < v->derivative.size; i++)
      {
        if (v->derivative.tab[i] == BAV_NOT_A_VARIABLE)
          w->derivative.tab[i] = BAV_NOT_A_VARIABLE;
        else
          {
            struct bav_variable *x = v->derivative.tab[i];
            w->derivative.tab[i] = x->derivative.tab[d->derivation_index];
          }
      }
    w->derivative.size = v->derivative.size;
/*
 * Recompute all numbers with respect to all orderings
 */
    w->number.size = bav_global.R.ords.size;
    for (r = 0; r < bav_global.R.ords.size; r++)
      bav_R_recompute_numbers_after_insertion_of_last_variable (r);
/*
 * We must not store w in bav_global.dict_str_to_var because
 *  w has positive order and only zero order dependent or operator
 *  variables are stored in this dictionary.
 */
  }
  BA0_CATCH
  {
    bav_global.R.vars.size -= 1;
    BA0_RE_RAISE_EXCEPTION;
  }
  BA0_ENDTRY;
  ba0_pull_stack ();
  return w;
}

/*
 * texinfo: bav_symbol_to_variable
 * Convert the symbol @var{y} to a variable.
 */

BAV_DLL struct bav_variable *
bav_symbol_to_variable (
    struct bav_symbol *y)
{
  struct bav_variable *v = BAV_NOT_A_VARIABLE;
  ba0_int_p j;

  switch (y->type)
    {
    case bav_independent_symbol:
      v = bav_global.R.vars.tab[bav_global.R.ders.tab[y->derivation_index]];
      break;
    case bav_operator_symbol:
      v = bav_global.R.vars.tab[bav_global.R.opra];
      break;
    case bav_dependent_symbol:
    case bav_temporary_symbol:
      j = ba0_get_dictionary_string (&bav_global.R.dict_str_to_var,
          (struct ba0_table *) &bav_global.R.vars, y->ident);
      if (j == BA0_NOT_AN_INDEX)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
      v = bav_global.R.vars.tab[j];
    }
  return v;
}

/*
 * texinfo: bav_R_string_to_existing_symbol
 * Convert @var{s} to an existing symbol.
 * Return @code{BAV_NOT_A_SYMBOL} if the symbol does not exist.
 */

BAV_DLL struct bav_symbol *
bav_R_string_to_existing_symbol (
    char *s)
{
  struct bav_variable *v;
  ba0_int_p j;

  j = ba0_get_dictionary_string (&bav_global.R.dict_str_to_var,
      (struct ba0_table *) &bav_global.R.vars, s);
  if (j == BA0_NOT_AN_INDEX)
    return BAV_NOT_A_SYMBOL;
  v = bav_global.R.vars.tab[j];
  return v->root;
}

/*
 * texinfo: bav_R_string_to_existing_derivation
 * Convert @var{s} to an existing independent symbol.
 * Return @code{BAV_NOT_A_SYMBOL} if the symbol does not exist.
 */

BAV_DLL struct bav_symbol *
bav_R_string_to_existing_derivation (
    char *s)
{
  ba0_int_p i;
  struct bav_variable *v;
  struct bav_symbol *y;

  for (i = 0; i < bav_global.R.ders.size; i++)
    {
      v = bav_global.R.vars.tab[bav_global.R.ders.tab[i]];
      y = v->root;
      if (strcmp (s, y->ident) == 0)
        return y;
    }
  return BAV_NOT_A_SYMBOL;
}

/*
 * texinfo: bav_R_string_to_existing_variable
 * Convert @var{s} to an existing variable.
 * Return @code{BAV_NOT_A_VARIABLE} if the variable does not exist.
 */

BAV_DLL struct bav_variable *
bav_R_string_to_existing_variable (
    char *s)
{
  struct bav_variable *v;
  ba0_int_p j;

  j = ba0_get_dictionary_string (&bav_global.R.dict_str_to_var,
      (struct ba0_table *) &bav_global.R.vars, s);
  if (j == BA0_NOT_AN_INDEX)
    v = BAV_NOT_A_VARIABLE;
  else
    v = bav_global.R.vars.tab[j];
  return v;
}

/*
 * texinfo: bav_derivation_index_to_derivation
 * Return the variable corresponding to the derivation index @var{k} i.e.
 * the variable which has index @var{k} in @code{bav_global.R.ders}.
 */

BAV_DLL struct bav_variable *
bav_derivation_index_to_derivation (
    ba0_int_p k)
{
  if (k < 0 || k > bav_global.R.ders.size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  return bav_global.R.vars.tab[bav_global.R.ders.tab[k]];
}

/*
 * texinfo: bav_variable_number
 * Return the number of @var{v} with respect to the current ordering.
 */

BAV_DLL bav_Iordering
bav_variable_number (
    struct bav_variable *v)
{
  return v->number.tab[bav_current_ordering ()];
}

/*
 * texinfo: bav_smallest_greater_variable
 * Return the smallest variable strictly greater than @var{v}
 * with respect to the current ordering. 
 * Return @code{BAV_NOT_A_VARIABLE} if it does not exist.
 */

BAV_DLL struct bav_variable *
bav_smallest_greater_variable (
    struct bav_variable *v)
{
  struct bav_variable *u, *w;
  ba0_int_p i, n;

  n = bav_variable_number (v) + 1;
  u = BAV_NOT_A_VARIABLE;
  for (i = 0; i < bav_global.R.vars.size && u == BAV_NOT_A_VARIABLE; i++)
    {
      w = bav_global.R.vars.tab[i];
      if (bav_variable_number (w) == n)
        u = w;
    }
  return u;
}

/*
 * texinfo: bav_R_set_maximal_variable
 * Change the current ordering in such a way that @var{v} becomes
 * the greatest variable (insert @var{v} at the beginning of the
 * field @code{varmax} of the current ordering).
 * The ordering between other variables is left unchanged.
 */

BAV_DLL void
bav_R_set_maximal_variable (
    struct bav_variable *v)
{
  ba0_int_p i;
  bav_Inumber *p, *q;
  struct bav_ordering *O;

  O = bav_global.R.ords.tab[bav_current_ordering ()];

  ba0_push_stack (&ba0_global.stack.quiet);
  if (O->varmax.size == O->varmax.alloc)
    ba0_realloc2_table
        ((struct ba0_table *) &O->varmax, 2 * O->varmax.alloc + 1,
        (ba0_new_function *) & bav_not_a_variable);
  ba0_pull_stack ();

  p = &v->number.tab[bav_current_ordering ()];
  for (i = 0; i < bav_global.R.vars.size; i++)
    {
      q = &bav_global.R.vars.tab[i]->number.tab[bav_current_ordering ()];
      if (*q > *p)
        *q -= 1;
    }
  (*p) = bav_global.R.vars.size - 1;

  memmove (O->varmax.tab + 1, O->varmax.tab,
      O->varmax.size * sizeof (struct bav_variable *));
  O->varmax.size++;
  O->varmax.tab[0] = v;
}

/*
 * texinfo: bav_R_set_minimal_variable
 * Change the current ordering in such a way that @var{v} becomes
 * the lowest variable (insert @var{v} at the end of the
 * field @code{varmin} of the current ordering).
 * The ordering between other variables is left unchanged.
 */

BAV_DLL void
bav_R_set_minimal_variable (
    struct bav_variable *v)
{
  ba0_int_p i;
  bav_Inumber *p, *q;
  struct bav_ordering *O;

  O = bav_global.R.ords.tab[bav_current_ordering ()];

  ba0_push_stack (&ba0_global.stack.quiet);
  if (O->varmin.size == O->varmin.alloc)
    ba0_realloc2_table
        ((struct ba0_table *) &O->varmin, 2 * O->varmin.alloc + 1,
        (ba0_new_function *) & bav_not_a_variable);
  ba0_pull_stack ();

  p = &v->number.tab[bav_current_ordering ()];
  for (i = 0; i < bav_global.R.vars.size; i++)
    {
      q = &bav_global.R.vars.tab[i]->number.tab[bav_current_ordering ()];
      if (*q < *p)
        *q += 1;
    }
  (*p) = 0;

  O->varmin.tab[O->varmin.size] = v;
  O->varmin.size++;
}
