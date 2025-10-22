#include "ba0_global.h"
#include "ba0_exception.h"
#include "ba0_stack.h"
#include "ba0_garbage.h"
#include "ba0_string.h"
#include "ba0_basic_io.h"
#include "ba0_analex.h"
#include "ba0_gmp.h"
#include "ba0_scanf.h"
#include "ba0_printf.h"
#include "ba0_table.h"
#include "ba0_indexed_string.h"

static void
ba0_init_indexed_string_indices (
    struct ba0_indexed_string_indices *indices)
{
  indices->po = indices->pf = '\0';
  ba0_init_table ((struct ba0_table *) &indices->Tindex);
}

static void
ba0_reset_indexed_string_indices (
    struct ba0_indexed_string_indices *indices)
{
  indices->po = indices->pf = '\0';
  ba0_reset_table ((struct ba0_table *) &indices->Tindex);
}

static struct ba0_indexed_string_indices *
ba0_new_indexed_string_indices (
    void)
{
  struct ba0_indexed_string_indices *indices;

  indices =
      (struct ba0_indexed_string_indices *) ba0_alloc (sizeof (struct
          ba0_indexed_string_indices));
  ba0_init_indexed_string_indices (indices);
  return indices;
}

static void
ba0_realloc_indexed_string_indices (
    struct ba0_indexed_string_indices *indices,
    ba0_int_p n)
{
  ba0_realloc2_table ((struct ba0_table *) &indices->Tindex, n,
      (ba0_new_function *) & ba0_new_indexed_string);
}

static void
ba0_set_indexed_string_indices (
    struct ba0_indexed_string_indices *dst,
    struct ba0_indexed_string_indices *src)
{
  if (dst != src)
    {
      ba0_reset_indexed_string_indices (dst);
      ba0_realloc_indexed_string_indices (dst, src->Tindex.size);
      dst->po = src->po;
      dst->pf = src->pf;
      while (dst->Tindex.size < src->Tindex.size)
        {
          ba0_set_indexed_string (dst->Tindex.tab[dst->Tindex.size],
              src->Tindex.tab[dst->Tindex.size]);
          dst->Tindex.size += 1;
        }
    }
}

/*
 * Readonly static data
 */

static char _struct_indices[] = "struct indices";
static char _indices_Tindex[] = "indices Tindex";

static ba0_int_p
ba0_garbage1_indexed_string_indices (
    void *z,
    enum ba0_garbage_code code)
{
  struct ba0_indexed_string_indices *ind =
      (struct ba0_indexed_string_indices *) z;
  ba0_int_p i, n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (ind, sizeof (struct ba0_indexed_string_indices),
        _struct_indices);
  if (ind->Tindex.tab)
    {
      n += ba0_new_gc_info (ind->Tindex.tab,
          sizeof (struct ba0_indexed_string *) * ind->Tindex.alloc,
          _indices_Tindex);
      for (i = 0; i < ind->Tindex.alloc; i++)
        n += ba0_garbage1_indexed_string (ind->Tindex.tab[i], ba0_isolated);
    }
  return n;
}

static void *
ba0_garbage2_indexed_string_indices (
    void *z,
    enum ba0_garbage_code code)
{
  struct ba0_indexed_string_indices *ind;
  ba0_int_p i;

  if (code == ba0_isolated)
    ind =
        (struct ba0_indexed_string_indices *) ba0_new_addr_gc_info (z,
        _struct_indices);
  else
    ind = (struct ba0_indexed_string_indices *) z;

  if (ind->Tindex.tab)
    {
      ind->Tindex.tab = (struct ba0_indexed_string * *) ba0_new_addr_gc_info
          (ind->Tindex.tab, _indices_Tindex);
      for (i = 0; i < ind->Tindex.alloc; i++)
        ind->Tindex.tab[i] =
            (struct ba0_indexed_string *)
            ba0_garbage2_indexed_string (ind->Tindex.tab[i], ba0_isolated);
    }
  return ind;
}

/*
 * texinfo: ba0_init_indexed_string
 * Initialize @var{indexed} to the empty indexed string.
 */

BA0_DLL void
ba0_init_indexed_string (
    struct ba0_indexed_string *indexed)
{
  indexed->string = (char *) 0;
  ba0_init_table ((struct ba0_table *) &indexed->Tindic);
}

/*
 * texinfo: ba0_reset_indexed_string
 * Reset @var{indexed} to the empty indexed string.
 */

BA0_DLL void
ba0_reset_indexed_string (
    struct ba0_indexed_string *indexed)
{
  indexed->string = (char *) 0;
  ba0_reset_table ((struct ba0_table *) &indexed->Tindic);
}

/*
 * texinfo: ba0_new_indexed_string
 * Allocate a new indexed string, initialize it and return it.
 */

BA0_DLL struct ba0_indexed_string *
ba0_new_indexed_string (
    void)
{
  struct ba0_indexed_string *indexed;

  indexed =
      (struct ba0_indexed_string *) ba0_alloc (sizeof (struct
          ba0_indexed_string));
  ba0_init_indexed_string (indexed);
  return indexed;
}

static void
ba0_realloc_indexed_string (
    struct ba0_indexed_string *indexed,
    ba0_int_p n)
{
  ba0_realloc2_table ((struct ba0_table *) &indexed->Tindic, n,
      (ba0_new_function *) & ba0_new_indexed_string_indices);
}

/*
 * texinfo: ba0_set_indexed_string
 * Assign @var{src} to @var{dst}.
 */

BA0_DLL void
ba0_set_indexed_string (
    struct ba0_indexed_string *dst,
    struct ba0_indexed_string *src)
{
  if (dst != src)
    {
      ba0_reset_indexed_string (dst);
      dst->string = ba0_strdup (src->string);
      ba0_realloc_indexed_string (dst, src->Tindic.size);
      while (dst->Tindic.size < src->Tindic.size)
        {
          ba0_set_indexed_string_indices (dst->Tindic.tab[dst->Tindic.size],
              src->Tindic.tab[dst->Tindic.size]);
          dst->Tindic.size += 1;
        }
    }
}

BA0_DLL void *
ba0_copy_indexed_string (
    void *z)
{
  struct ba0_indexed_string *src = (struct ba0_indexed_string *) z;
  struct ba0_indexed_string *dst;

  dst = ba0_new_indexed_string ();
  ba0_set_indexed_string (dst, src);
  return dst;
}

/*
 * Readonly static data
 */

static char _struct_indexed[] = "struct indexed_string";
static char _indexed_Tindic[] = "indexed Tindic";

BA0_DLL ba0_int_p
ba0_garbage1_indexed_string (
    void *z,
    enum ba0_garbage_code code)
{
  struct ba0_indexed_string *ind = (struct ba0_indexed_string *) z;
  ba0_int_p i, n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (ind, sizeof (struct ba0_indexed_string),
        _struct_indexed);
  if (ind->string)
    n += ba0_garbage1_string (ind->string, ba0_isolated);
  if (ind->Tindic.tab)
    {
      n += ba0_new_gc_info (ind->Tindic.tab,
          sizeof (struct ba0_indexed_string_indices *) * ind->Tindic.alloc,
          _indexed_Tindic);
      for (i = 0; i < ind->Tindic.alloc; i++)
        n += ba0_garbage1_indexed_string_indices (ind->Tindic.tab[i],
            ba0_isolated);
    }
  return n;
}

BA0_DLL void *
ba0_garbage2_indexed_string (
    void *z,
    enum ba0_garbage_code code)
{
  struct ba0_indexed_string *ind;
  ba0_int_p i;

  if (code == ba0_isolated)
    ind =
        (struct ba0_indexed_string *) ba0_new_addr_gc_info (z, _struct_indexed);
  else
    ind = (struct ba0_indexed_string *) z;

  if (ind->string)
    ind->string = (char *) ba0_garbage2_string (ind->string, ba0_isolated);
  if (ind->Tindic.tab)
    {
      ind->Tindic.tab =
          (struct ba0_indexed_string_indices *
          *) ba0_new_addr_gc_info (ind->Tindic.tab, _indexed_Tindic);
      for (i = 0; i < ind->Tindic.alloc; i++)
        ind->Tindic.tab[i] =
            (struct ba0_indexed_string_indices *)
            ba0_garbage2_indexed_string_indices (ind->Tindic.tab[i],
            ba0_isolated);
    }
  return ind;
}

/*
 * The important functions
 */

static void
ba0_printf_indexed_string_indices (
    void *z)
{
  struct ba0_indexed_string_indices *indices =
      (struct ba0_indexed_string_indices *) z;
  ba0_int_p i;

  if (indices->po)
    ba0_put_char (indices->po);
  for (i = 0; i < indices->Tindex.size; i++)
    {
      ba0_printf_indexed_string (indices->Tindex.tab[i]);
      if (i < indices->Tindex.size - 1)
        ba0_put_char (',');
    }
  if (indices->pf)
    ba0_put_char (indices->pf);
}

/*
 * texinfo: ba0_printf_indexed_string
 * General printing function for indexed.
 * It is called by @code{ba0_printf/%indexed_string}.
 */

BA0_DLL void
ba0_printf_indexed_string (
    void *z)
{
  struct ba0_indexed_string *indexed = (struct ba0_indexed_string *) z;
  ba0_int_p i;

  if (indexed->string)
    ba0_put_string (indexed->string);
  for (i = 0; i < indexed->Tindic.size; i++)
    ba0_printf_indexed_string_indices (indexed->Tindic.tab[i]);
}

/*
 * texinfo: ba0_indexed_string_to_string
 * Print @var{indexed} into a string (allocated by @code{ba0_alloc})
 * and return this string.
 */

BA0_DLL char *
ba0_indexed_string_to_string (
    struct ba0_indexed_string *indexed)
{
  char *string;
  ba0_record_output ();
  ba0_set_output_counter ();
  ba0_printf_indexed_string (indexed);
  string = (char *) ba0_alloc (ba0_output_counter () + 1);
  ba0_set_output_string (string);
  ba0_printf_indexed_string (indexed);
  ba0_restore_output ();
  return string;
}

/*
 * texinfo: ba0_stripped_indexed_string_to_string
 * Apply @code{ba0_indexed_string_to_string} to the indexed
 * string obtained by removing the trailing indexed string
 * indices from @var{indexed} and return the result.
 */

BA0_DLL char *
ba0_stripped_indexed_string_to_string (
    struct ba0_indexed_string *indexed)
{
  char *string;

  if (indexed->Tindic.size == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  indexed->Tindic.size -= 1;
  string = ba0_indexed_string_to_string (indexed);
  indexed->Tindic.size += 1;
  return string;
}

/*
 * texinfo: ba0_has_empty_trailing_indices_indexed_string
 * Return @code{true} if @var{indexed} has an empty last
 * indexed string indices the opening parenthesis of which
 * is different from @var{avoid}.
 */

BA0_DLL bool
ba0_has_empty_trailing_indices_indexed_string (
    struct ba0_indexed_string *indexed,
    char avoid)
{
  bool b = false;
  if (indexed->Tindic.size > 0)
    {
      struct ba0_indexed_string_indices *trailing =
          indexed->Tindic.tab[indexed->Tindic.size - 1];

      b = trailing->Tindex.size == 0 && trailing->po != avoid;
    }
  return b;
}

/*
 * texinfo: ba0_has_trailing_indices_indexed_string
 * Return @code{true} if @var{indexed} has at least one
 * indexed string indices and each element of the last sequence of
 * indices satisfies @var{predicate}.
 */

BA0_DLL bool
ba0_has_trailing_indices_indexed_string (
    struct ba0_indexed_string *indexed,
    bool (*predicate) (char *))
{
  struct ba0_mark M;
  bool b = false;

  ba0_record (&M);
  if (indexed->Tindic.size > 0)
    {
      struct ba0_indexed_string_indices *indices =
          indexed->Tindic.tab[indexed->Tindic.size - 1];
      ba0_int_p i;

      b = true;
      for (i = 0; i < indices->Tindex.size && b; i++)
        {
          struct ba0_indexed_string *idx = indices->Tindex.tab[i];
          char *string = ba0_indexed_string_to_string (idx);
          b = predicate (string);
        }
    }
  ba0_restore (&M);
  return b;
}

/*
 * Subfunction of ba0_has_numeric_trailing_indices_indexed_string
 */

static bool
is_integer (
    char *string,
    ba0_int_p *d)
{
  int i = 0;
  while (isspace ((int) string[i]))
    i += 1;
  if (string[i] == '-')
    i += 1;
  while (isspace ((int) string[i]))
    i += 1;
  while (isdigit ((int) string[i]))
    i += 1;
  if (string[i] != '\0')
    return false;
  sscanf (string, BA0_FORMAT_INT_P, d);
  return true;
}

/*
 * texinfo: ba0_has_numeric_trailing_indices_indexed_string
 * Return @code{true} if the trailing indexed string indices
 * of @var{indexed} exists, is nonempty and involves signed integer 
 * numbers only.
 * If so and @var{indices} is nonzero then @var{indices} is
 * assigned the corresponding table of integers.
 */

BA0_DLL bool
ba0_has_numeric_trailing_indices_indexed_string (
    struct ba0_indexed_string *indexed,
    struct ba0_tableof_int_p *indices)
{
  bool b = false;
  if (indexed->Tindic.size > 0)
    {
      struct ba0_indexed_string_indices *trailing =
          indexed->Tindic.tab[indexed->Tindic.size - 1];

      if (trailing->Tindex.size > 0)
        {
          ba0_int_p i;

          if (indices)
            ba0_realloc_table ((struct ba0_table *) indices,
                trailing->Tindex.size);

          b = true;
          for (i = 0; i < trailing->Tindex.size && b; i++)
            {
              ba0_int_p d;

              if (trailing->Tindex.tab[i]->Tindic.size == 0 &&
                  is_integer (trailing->Tindex.tab[i]->string, &d))
                {
                  if (indices)
                    indices->tab[i] = d;
                }
              else
                b = false;
            }
          if (indices)
            indices->size = trailing->Tindex.size;
        }
    }
  return b;
}

static struct ba0_indexed_string *ba0_scanf_general_indexed_string (
    struct ba0_indexed_string *,
    ba0_int_p *);

/*
 * Read one 'indexed string indices'.
 */

static struct ba0_indexed_string_indices *
ba0_scanf_indexed_string_indices (
    struct ba0_indexed_string_indices *indices)
{
  struct ba0_indexed_string *indexed;

  if (indices != (struct ba0_indexed_string_indices *) 0)
    ba0_reset_indexed_string_indices (indices);
  else
    indices = ba0_new_indexed_string_indices ();

  if (!ba0_sign_token_analex ("[") && !ba0_sign_token_analex ("("))
    BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);

  if (ba0_sign_token_analex ("["))
    {
      indices->po = '[';
      indices->pf = ']';
    }
  else
    {
      indices->po = '(';
      indices->pf = ')';
    }
  ba0_get_token_analex ();
  for (;;)
    {
      if (indices->Tindex.size >= indices->Tindex.alloc)
        ba0_realloc_indexed_string_indices (indices,
            2 * indices->Tindex.size + 1);
      indexed =
          ba0_scanf_general_indexed_string (indices->Tindex.tab[indices->
              Tindex.size], (ba0_int_p *) 0);

      if (indexed == (struct ba0_indexed_string *) 0)
        break;

      indices->Tindex.size += 1;
      ba0_get_token_analex ();
      if (!ba0_sign_token_analex (","))
        break;
      ba0_get_token_analex ();
    }
  if ((indices->po == '[' && !ba0_sign_token_analex ("]")) ||
      (indices->po == '(' && !ba0_sign_token_analex (")")))
    BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);

  return indices;
}

/*
 * Read 'indexed string indices' ... 'indexed string indices'
 * At least once
 */

static void
ba0_scanf_tableof_indexed_string_indices (
    struct ba0_indexed_string *indexed,
    ba0_int_p *counter)
{
  while ((ba0_sign_token_analex ("[") || ba0_sign_token_analex ("(")))
    {

      if (counter != (ba0_int_p *) 0)
        *counter = ba0_get_counter_analex ();

      if (indexed->Tindic.size >= indexed->Tindic.alloc)
        ba0_realloc_indexed_string (indexed, 2 * indexed->Tindic.size + 1);
      ba0_scanf_indexed_string_indices
          (indexed->Tindic.tab[indexed->Tindic.size]);
      indexed->Tindic.size += 1;
      ba0_get_token_analex ();
    }
  ba0_unget_token_analex (1);
}

/*
 * Read zero or one indexed string.
 *
 * Return the zero pointer if no indexed string is read.
 */

static struct ba0_indexed_string *
ba0_scanf_general_indexed_string (
    struct ba0_indexed_string *indexed,
    ba0_int_p *counter)
{
  struct ba0_mark M;
  ba0_mpz_t n;

  if (indexed != (struct ba0_indexed_string *) 0)
    ba0_reset_indexed_string (indexed);
  else
    indexed = ba0_new_indexed_string ();

  if (ba0_type_token_analex () == ba0_string_token)
    {
      indexed->string = ba0_scanf_string (0);
      ba0_get_token_analex ();
      if (ba0_sign_token_analex ("[") || ba0_sign_token_analex ("("))
        ba0_scanf_tableof_indexed_string_indices (indexed, counter);
      else
        ba0_unget_token_analex (1);
    }
  else if (ba0_type_token_analex () == ba0_integer_token ||
      ba0_sign_token_analex ("-"))
    {
      ba0_push_another_stack ();
      ba0_record (&M);
      ba0_mpz_init (n);
      ba0_scanf ("%z", n);
      ba0_record_output ();
      ba0_set_output_counter ();
      ba0_printf ("%z", n);
      ba0_pull_stack ();
      indexed->string = (char *) ba0_alloc (ba0_output_counter () + 1);
      ba0_restore_output ();
      ba0_sprintf (indexed->string, "%z", n);
      ba0_restore (&M);
    }
  else if (ba0_sign_token_analex ("[") || ba0_sign_token_analex ("("))
    ba0_scanf_tableof_indexed_string_indices (indexed, counter);
  else
    indexed = (struct ba0_indexed_string *) 0;

  return indexed;
}

/*
 * ba0_scanf2_indexed_string
 * An auxiliary parsing function for indexed strings.
 * Read one indexed string starting by a string and store 
 * it in @var{indexed}.
 *
 * Exception @code{BA0_ERRSYN} can be raised.
 * Note: if @var{indexed} is nonzero, it may be left corrupted
 * in case of such an exception.
 */

static struct ba0_indexed_string *
ba0_scanf2_indexed_string (
    struct ba0_indexed_string *indexed,
    ba0_int_p *counter)
{
  struct ba0_indexed_string *result = (struct ba0_indexed_string *) 0;

  ba0_set_memory_functions_function *set_memory_functions;
  char *Integer_PFE;

  if (ba0_type_token_analex () != ba0_string_token)
    BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);

  ba0_get_settings_gmp (&set_memory_functions, &Integer_PFE);
  ba0_set_settings_gmp (set_memory_functions, 0);

  BA0_TRY
  {
    result = ba0_scanf_general_indexed_string (indexed, counter);
    ba0_set_settings_gmp (set_memory_functions, Integer_PFE);
  }
  BA0_CATCH
  {
    ba0_set_settings_gmp (set_memory_functions, Integer_PFE);
    BA0_RE_RAISE_EXCEPTION;
  }
  BA0_ENDTRY;
  return result;
}

/*
 * texinfo: ba0_scanf_indexed_string
 * The general parsing function for indexed.
 * It is called by @code{ba0_scanf/%indexed_string}.
 * Return the result as a @code{struct ba0_indexed_string *}.
 * Store it in *@var{z} if this parameter is nonzero.
 */

BA0_DLL void *
ba0_scanf_indexed_string (
    void *z)
{
  struct ba0_indexed_string *ind, *z_ind;
/*
 * If a syntax error is raised in ba0_scanf2_indexed_string
 * then its first argument might be corrupted. 
 * The following formulation prevents the corruption of z
 */
  ind = ba0_new_indexed_string ();
  ba0_scanf2_indexed_string (ind, (ba0_int_p *) 0);

  if (z != (void *) 0)
    {
      z_ind = (struct ba0_indexed_string *) z;
      ba0_set_indexed_string (z_ind, ind);
    }
  else
    z_ind = ind;

  return z_ind;
}

/*
 * texinfo: ba0_scanf_indexed_string_with_counter
 * Variant of @code{ba0_scanf_indexed_string} which assigns
 * to *@var{counter} the argument for @code{ba0_unget_token_analex}
 * in order to put back on the lexical analyzer fifo all the tokens
 * which led to the last indexed string indices of the returned
 * indexed string. The content of *@var{counter} is meaningless
 * if the returned indexed string does not involve any indexed
 * string indices.
 */

BA0_DLL struct ba0_indexed_string *
ba0_scanf_indexed_string_with_counter (
    struct ba0_indexed_string *indexed,
    ba0_int_p *counter)
{
  struct ba0_indexed_string *ind;
  ba0_int_p aux_counter = 0;

  ind = ba0_new_indexed_string ();
  ba0_scanf2_indexed_string (ind, &aux_counter);

  if (counter != (ba0_int_p *) 0)
    *counter = ba0_get_counter_analex () - aux_counter;

  if (indexed != (struct ba0_indexed_string *) 0)
    ba0_set_indexed_string (indexed, ind);
  else
    indexed = ind;

  return indexed;
}

/*
 * texinfo: ba0_scanf_indexed_string_as_a_string
 * Parsing function which can be called by @code{ba0_scanf/%six}.
 * Call @code{ba0_scanf_indexed_string} 
 * but return the result as a plain string.
 * Store it in *@var{z} if this parameter is nonzero.
 */

BA0_DLL void *
ba0_scanf_indexed_string_as_a_string (
    void *z)
{
  char *result;
  struct ba0_indexed_string *indexed;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  indexed = ba0_scanf2_indexed_string ((struct ba0_indexed_string *) 0,
      (ba0_int_p *) 0);
  ba0_pull_stack ();

  if (z != (void *) 0)
    result = (char *) z;
  else
    {
      ba0_record_output ();
      ba0_set_output_counter ();
      ba0_printf_indexed_string (indexed);
      result = (char *) ba0_alloc (ba0_output_counter () + 1);
      ba0_restore_output ();
    }
  ba0_record_output ();
  ba0_set_output_string (result);
  ba0_printf_indexed_string (indexed);
  ba0_restore_output ();
  ba0_restore (&M);
  return result;
}
