#include "baz_global.h"
#include "baz_prolongation_pattern.h"
#include "baz_point_ratfrac.h"
#include "baz_eval_polyspec_mpz.h"

/*
 * texinfo: baz_set_settings_prolongation_pattern
 * Assign @var{lhs_quotes} to the corresponding setting variable.
 */

BAZ_DLL void
baz_set_settings_prolongation_pattern (
    char *lhs_quotes)
{
  baz_initialized_global.prolongation_pattern.lhs_quotes = lhs_quotes;
}

/*
 * texinfo: baz_get_settings_prolongation_pattern
 * Assign to *@var{lhs_quotes} the value of the corresponding setting
 * variable. The argument may be zero.
 */

BAZ_DLL void
baz_get_settings_prolongation_pattern (
    char **lhs_quotes)
{
  if (lhs_quotes)
    *lhs_quotes = baz_initialized_global.prolongation_pattern.lhs_quotes;
}

static char *
identifier (
    void *object)
{
  if (object == (void *) 0)
    return "";
  else
    return (char *) object;
}

/*
 * texinfo: baz_init_prolongation_pattern
 * Initialize @var{pattern} to the empty pattern.
 */

BAZ_DLL void
baz_init_prolongation_pattern (
    struct baz_prolongation_pattern *pattern)
{
  if (bav_is_empty_differential_ring (&bav_global.R))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_init_table ((struct ba0_table *) &pattern->deps);
  ba0_init_table ((struct ba0_table *) &pattern->idents);
  ba0_init_table ((struct ba0_table *) &pattern->exprs);
  ba0_realloc_table ((struct ba0_table *) &pattern->idents,
      bav_global.R.ders.size);
  pattern->idents.size = pattern->idents.alloc;

  ba0_init_dictionary_string (&pattern->dict, &identifier, 8);
  baz_reset_prolongation_pattern (pattern);
}

/*
 * texinfo: baz_reset_prolongation_pattern
 * Reset @var{pattern} to the empty pattern.
 */

BAZ_DLL void
baz_reset_prolongation_pattern (
    struct baz_prolongation_pattern *pattern)
{
  ba0_int_p i;

  ba0_reset_table ((struct ba0_table *) &pattern->deps);
  for (i = 0; i < pattern->idents.size; i++)
    pattern->idents.tab[i] = (char *) 0;
  for (i = 0; i < pattern->exprs.size; i++)
    pattern->exprs.tab[i] = (char *) 0;
  ba0_reset_table ((struct ba0_table *) &pattern->exprs);
  ba0_reset_dictionary_string (&pattern->dict);
}

/*
 * texinfo: baz_new_prolongation_pattern
 * Allocate a new prolongation pattern, initialize it and return it.
 */

BAZ_DLL struct baz_prolongation_pattern *
baz_new_prolongation_pattern (
    void)
{
  struct baz_prolongation_pattern *pattern;

  pattern =
      (struct baz_prolongation_pattern *) ba0_alloc (sizeof (struct
          baz_prolongation_pattern));
  baz_init_prolongation_pattern (pattern);
  return pattern;
}

BAZ_DLL void
baz_set_prolongation_pattern (
    struct baz_prolongation_pattern *dst,
    struct baz_prolongation_pattern *src)
{
  if (src != dst)
    {
      ba0_set_table ((struct ba0_table *) &dst->deps,
          (struct ba0_table *) &src->deps);
      ba0_set_tableof_string (&dst->idents, &src->idents);
      ba0_set_tableof_string (&dst->exprs, &src->exprs);
      ba0_set_dictionary_string (&dst->dict, &src->dict);
    }
}

/*
 * texinfo: baz_sizeof_prolongation_pattern
 * Return the size of the memory needed to perform a copy of @var{P}.
 * If @var{code} is @code{ba0_embedded} then @var{P} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account.
 */

BAZ_DLL unsigned ba0_int_p
baz_sizeof_prolongation_pattern (
    struct baz_prolongation_pattern *P,
    enum ba0_garbage_code code)
{
  unsigned ba0_int_p size;

  if (code == ba0_isolated)
    size = ba0_allocated_size (sizeof (struct baz_prolongation_pattern));
  else
    size = 0;

  size += ba0_sizeof_table ((struct ba0_table *) &P->deps, ba0_embedded);
  size += ba0_sizeof_tableof_string (&P->idents, ba0_embedded);
  size += ba0_sizeof_tableof_string (&P->exprs, ba0_embedded);
  size += ba0_sizeof_dictionary_string (&P->dict, ba0_embedded);
  return size;
}

/*
 * baz_switch_ring_prolongation_pattern
 * This low level function should be used in conjunction with
 * @code{bav_set_differential_ring}: if @var{R} is a ring obtained by
 * application of @code{bav_set_differential_ring}
 * to the ring @var{P} refers to, then this function makes @var{P}
 * refer to @var{R}.
 */

BAZ_DLL void
baz_switch_ring_prolongation_pattern (
    struct baz_prolongation_pattern *P,
    struct bav_differential_ring *R)
{
  ba0_int_p i;

  for (i = 0; i < P->deps.size; i++)
    P->deps.tab[i] = bav_switch_ring_symbol (P->deps.tab[i], R);
}

/*
 * texinfo: baz_variable_mapping_prolongation_pattern
 * Assign to @var{dst} all the variables obtained by evaluating @var{src} 
 * using @var{pattern}.
 */

BAZ_DLL void
baz_variable_mapping_prolongation_pattern (
    struct bav_tableof_variable *dst,
    struct bav_tableof_variable *src,
    struct baz_prolongation_pattern *pattern)
{
  struct baz_point_ratfrac point;
  struct baz_ratfrac Q;
  struct bap_polynom_mpz P;
  struct bav_dictionary_variable dict;
  struct bav_tableof_variable X;
  struct ba0_mark M;
  ba0_int_p i;

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_init_point ((struct ba0_point *) &point);
  for (i = 0; i < src->size; i++)
    baz_prolongate_point_ratfrac_using_pattern_variable (&point, &point,
        pattern, src->tab[i]);

  bav_init_dictionary_variable (&dict, 6);
  ba0_init_table ((struct ba0_table *) &X);

  bap_init_polynom_mpz (&P);
  baz_init_ratfrac (&Q);
  for (i = 0; i < src->size; i++)
    {
      bap_set_polynom_variable_mpz (&P, src->tab[i], 1);
      baz_eval_to_ratfrac_at_point_ratfrac_polynom_mpz (&Q, &P, &point);
      baz_mark_indets_ratfrac (&dict, &X, &Q);
    }

  ba0_pull_stack ();
  ba0_set_table ((struct ba0_table *) dst, (struct ba0_table *) &X);
  ba0_restore (&M);
}

/*
 * texinfo: baz_printf_prolongation_pattern
 * The general printing function for prolongation patterns.
 * It can be called through @code{ba0_printf/%prolongation_pattern}.
 */

BAZ_DLL void
baz_printf_prolongation_pattern (
    void *P)
{
  struct baz_prolongation_pattern *pattern =
      (struct baz_prolongation_pattern *) P;

  ba0_put_char ('{');
  if (pattern->deps.size > 0)
    {
      ba0_int_p i;

      for (i = 0; i < pattern->deps.size; i++)
        {
          ba0_int_p j;
          bool yet;

          if (i > 0)
            ba0_put_string (", ");
          bav_printf_symbol (pattern->deps.tab[i]);
          ba0_put_char ('[');
          yet = false;
          for (j = 0; j < pattern->idents.size; j++)
            {
              if (pattern->idents.tab[j] != (char *) 0)
                {
                  struct bav_variable *x;

                  if (yet)
                    ba0_put_char (',');
                  x = bav_derivation_index_to_derivation (j);
                  if (baz_initialized_global.prolongation_pattern.lhs_quotes)
                    ba0_put_char (baz_initialized_global.prolongation_pattern.
                        lhs_quotes[0]);
                  ba0_put_char ('(');
                  bav_printf_variable (x);
                  ba0_put_char (',');
                  ba0_put_string (pattern->idents.tab[j]);
                  ba0_put_char (')');
                  if (baz_initialized_global.prolongation_pattern.lhs_quotes)
                    ba0_put_char (baz_initialized_global.prolongation_pattern.
                        lhs_quotes[0]);
                  yet = true;
                }
            }
          ba0_put_string ("] : \'");
          ba0_put_string (pattern->exprs.tab[i]);
          ba0_put_char ('\'');
        }
    }
  ba0_put_char ('}');
}

/*
 * texinfo: baz_scanf_prolongation_pattern
 * The general parser for prolongation patterns.
 * It can be called through @code{ba0_scanf/%prolongation_pattern}.
 * The expected syntax is described by the following example:
 * @verbatim
 * { 
 *   y[(x,k),(t,l)]:'y[k,l]/(factorial(k)*factorial(l))',
 *   z[(x,k),(t,l)]:'factorial(k)*z[k]'
 * }
 * @end verbatim
 * Observe that the identifiers @var{k} and @var{l} associated
 * to the two derivations must be the same for each dependent
 * variable.
 */

BAZ_DLL void *
baz_scanf_prolongation_pattern (
    void *P)
{
  struct baz_prolongation_pattern *pattern;

  if (P == (void *) 0)
    pattern = baz_new_prolongation_pattern ();
  else
    {
      pattern = (struct baz_prolongation_pattern *) P;
      baz_reset_prolongation_pattern (pattern);
    }

  if (!ba0_sign_token_analex ("{"))
    BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
  ba0_get_token_analex ();

  while (!ba0_sign_token_analex ("}"))
    {
      struct bav_symbol *y;
      ba0_int_p i;

      y = bav_scanf2_symbol ((void *) 0);
      if (y == BAV_NOT_A_SYMBOL || y->type != bav_dependent_symbol)
        BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
      for (i = 0; i < pattern->deps.size; i++)
        {
          if (pattern->deps.tab[i] == y)
            BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
        }
      if (pattern->deps.size == pattern->deps.alloc)
        {
          ba0_int_p new_alloc = 2 * pattern->deps.alloc + 1;
          ba0_realloc_table ((struct ba0_table *) &pattern->deps, new_alloc);
        }
      pattern->deps.tab[pattern->deps.size] = y;
      pattern->deps.size += 1;
/*
 * The generic derivative
 */
      ba0_get_token_analex ();
      if (!ba0_sign_token_analex ("["))
        BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
      ba0_get_token_analex ();

      while (!ba0_sign_token_analex ("]"))
        {
          struct bav_symbol *x;
          ba0_int_p j;
          char *ident;
/*
 * ( derivation, string )
 */
          if (!ba0_sign_token_analex ("("))
            BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
          ba0_get_token_analex ();

          x = bav_scanf_symbol ((void *) 0);
          if (x == BAV_NOT_A_SYMBOL || x->type != bav_independent_symbol)
            BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);

          j = x->derivation_index;

          ba0_get_token_analex ();
          if (!ba0_sign_token_analex (","))
            BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);

          ba0_get_token_analex ();
          if (ba0_type_token_analex () != ba0_string_token)
            BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
          ident = ba0_value_token_analex ();
          if (pattern->idents.tab[j] == (char *) 0)
            {
              pattern->idents.tab[j] = ba0_strdup (ident);
              ba0_add_dictionary_string (&pattern->dict,
                  (struct ba0_table *) &pattern->idents,
                  pattern->idents.tab[j], j);
            }
          else if (strcmp (pattern->idents.tab[j], ident) != 0)
            BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);

          ba0_get_token_analex ();
          if (!ba0_sign_token_analex (")"))
            BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);

          ba0_get_token_analex ();
          if (ba0_sign_token_analex (","))
            {
              ba0_get_token_analex ();
              if (ba0_sign_token_analex ("]"))
                BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
            }
          else if (!ba0_sign_token_analex ("]"))
            BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
        }

      ba0_get_token_analex ();
      if (!ba0_sign_token_analex (":"))
        BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
      ba0_get_token_analex ();
/*
 * The corresponding expr (assumed to be a quoted single string)
 */
      if (ba0_type_token_analex () != ba0_string_token)
        BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
      if (pattern->exprs.size == pattern->exprs.alloc)
        {
          ba0_int_p new_alloc = 2 * pattern->deps.alloc + 1;
          ba0_realloc_table ((struct ba0_table *) &pattern->exprs, new_alloc);
        }
      pattern->exprs.tab[pattern->exprs.size] =
          ba0_strdup (ba0_value_token_analex ());
      pattern->exprs.size += 1;

      if (pattern->exprs.size != pattern->deps.size)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);

      ba0_get_token_analex ();
      if (ba0_sign_token_analex (","))
        {
          ba0_get_token_analex ();
          if (ba0_sign_token_analex ("}"))
            BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
        }
      else if (!ba0_sign_token_analex ("}"))
        BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
    }
  return pattern;
}
