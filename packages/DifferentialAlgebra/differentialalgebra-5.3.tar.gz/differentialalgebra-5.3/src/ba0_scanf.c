#include "ba0_exception.h"
#include "ba0_stack.h"
#include "ba0_list.h"
#include "ba0_table.h"
#include "ba0_array.h"
#include "ba0_matrix.h"
#include "ba0_point.h"
#include "ba0_format.h"
#include "ba0_scanf.h"
#include "ba0_basic_io.h"
#include "ba0_analex.h"
#include "ba0_int_p.h"
#include "ba0_bool.h"
#include "ba0_global.h"

/*
   The format f describes the type of the elements of the list
   po = opening bracket
   pf = closing bracket
   struct_list_in_another_stack : if true then the struct ba0_list are 
   allocated in another stack than the list values. This is useful for parsing 
   tables. If false then the list gets allocated in the current stack.
 */

static struct ba0_list *
ba0_scanf_list (
    struct ba0_format *f,
    char po,
    char pf,
    bool struct_list_in_another_stack)
{
  char delimiteur[] = " ";
  struct ba0_list *L = (struct ba0_list *) 0;

  delimiteur[0] = po;
  if (!ba0_sign_token_analex (delimiteur))
    BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);

  ba0_get_token_analex ();
  delimiteur[0] = pf;
  if (ba0_sign_token_analex (delimiteur))
    return L;

  for (;;)
    {
      void *value;
/*
   Lists of ba0_int_p are a special case :
   We want the integers to be stored in the pointers.
*/
      if (f->linknmb > 0)
        {
          if (f->link[0]->u.leaf.scanf == &ba0_scanf_int_p)
            ba0_scanf_int_p (&value);
          else if (f->link[0]->u.leaf.scanf == &ba0_scanf_hexint_p)
            ba0_scanf_hexint_p (&value);
          else if (f->link[0]->u.leaf.scanf == &ba0_scanf_bool)
            ba0_scanf_bool (&value);
          else
            ba0__scanf__ (f, &value, false);
        }
      else
        ba0__scanf__ (f, &value, false);
      if (struct_list_in_another_stack)
        {
          ba0_push_another_stack ();
          L = ba0_cons_list (value, L);
          ba0_pull_stack ();
        }
      else
        L = ba0_cons_list (value, L);
      ba0_get_token_analex ();
      if (!ba0_sign_token_analex (","))
        break;
      ba0_get_token_analex ();
    }

  if (!ba0_sign_token_analex (delimiteur))
    BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);

  return ba0_reverse_list (L);
}

static struct ba0_table *
ba0_scanf_table (
    struct ba0_format *f,
    char po,
    char pf,
    struct ba0_table *T)
{
  struct ba0_list *L;
  struct ba0_mark M;
/*
   A table is parsed as a list.
   A mark is set in another stack before parsing the list
*/
  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_pull_stack ();

  L = ba0_scanf_list (f, po, pf, true);

  if (T == (struct ba0_table *) 0)
    T = ba0_new_table ();
  ba0_set_table_list (T, L);
/*
   The struct ba0_list are freed
*/
  ba0_restore (&M);

  return T;
}

/*
   There is some waste of memory.
   It could be saved by applying the garbage collector but this would
   force the user to write a garbage collector in order to parse arrays.
*/

static struct ba0_array *
ba0_scanf_array (
    struct ba0_format *f,
    char po,
    char pf,
    struct ba0_array *A)
{
  struct ba0_list *L;
  ba0_int_p sizelt, length, i;
  struct ba0_mark M;
/*
   An array is parsed as a list.
   A mark is set in another stack before parsing the list
*/
  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_pull_stack ();

  if (f->linknmb == 0 || f->link[0]->u.leaf.sizelt < 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  L = ba0_scanf_list (f, po, pf, true);
  length = ba0_length_list (L);

  if (A == (struct ba0_array *) 0)
    A = ba0_new_array ();
  sizelt = f->link[0]->u.leaf.sizelt;
  ba0_realloc_array (A, length, sizelt);
/*
   Machine integers are a special case. They are stored in list pointers.
*/
  if (f->link[0]->u.leaf.scanf == &ba0_scanf_int_p ||
      f->link[0]->u.leaf.scanf == &ba0_scanf_hexint_p ||
      f->link[0]->u.leaf.scanf == &ba0_scanf_bool)
    {
      for (i = 0; i < length; i++)
        {
          memcpy (A->tab + i * sizelt, &L->value, sizelt);
          L = L->next;
        }
    }
  else
    {
      for (i = 0; i < length; i++)
        {
          memcpy (A->tab + i * sizelt, L->value, sizelt);
          L = L->next;
        }
    }
  A->size = length;
/*
   The struct ba0_list are freed
*/
  ba0_restore (&M);

  return A;
}

static struct ba0_value *
ba0_scanf_value (
    struct ba0_format *f,
    char po,
    char pf,
    struct ba0_value *value)
{
  if (ba0_global.format.scanf_value_var == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  if (value == (struct ba0_value *) 0)
    value = ba0_new_value ();
  (*ba0_global.format.scanf_value_var) (&value->var);
  ba0_get_token_analex ();
// The parser accepts both '=' and ':' 
  if (!ba0_sign_token_analex (ba0_initialized_global.value.equal_sign) &&
      !ba0_sign_token_analex ("=") && !ba0_sign_token_analex (":"))
    BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
  ba0_get_token_analex ();
  if (f->linknmb > 0)
    {
      if (f->link[0]->u.leaf.scanf == &ba0_scanf_int_p)
        ba0_scanf_int_p (&value->value);
      else if (f->link[0]->u.leaf.scanf == &ba0_scanf_hexint_p)
        ba0_scanf_hexint_p (&value->value);
      else if (f->link[0]->u.leaf.scanf == &ba0_scanf_bool)
        ba0_scanf_bool (&value->value);
      else
        ba0__scanf__ (f, &value->value, false);
    }
  else
    ba0__scanf__ (f, &value->value, false);
  return value;
}

static struct ba0_list *
ba0_scanf_listof_value (
    struct ba0_format *f,
    char po,
    char pf,
    bool struct_list_in_another_stack)
{
  char delimiteur[] = " ";
  struct ba0_list *L = (struct ba0_list *) 0;

  delimiteur[0] = po;
  if (!ba0_sign_token_analex (delimiteur))
    BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);

  ba0_get_token_analex ();
  delimiteur[0] = pf;
  if (ba0_sign_token_analex (delimiteur))
    return L;

  for (;;)
    {
      struct ba0_value *res;
      res = ba0_scanf_value (f, po, pf, (struct ba0_value *) 0);

      if (struct_list_in_another_stack)
        {
          ba0_push_another_stack ();
          L = ba0_cons_list (res, L);
          ba0_pull_stack ();
        }
      else
        L = ba0_cons_list (res, L);

      ba0_get_token_analex ();
      if (!ba0_sign_token_analex (","))
        break;
      ba0_get_token_analex ();
    }

  if (!ba0_sign_token_analex (delimiteur))
    BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);

  return ba0_reverse_list (L);
}

static struct ba0_point *
ba0_scanf_point (
    struct ba0_format *f,
    char po,
    char pf,
    struct ba0_point *point)
{
  struct ba0_list *L;
  struct ba0_mark M;
/*
   A table is parsed as a list.
   A mark is set in another stack before parsing the list
*/
  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_pull_stack ();

  L = ba0_scanf_listof_value (f, po, pf, true);

  if (point == (struct ba0_point *) 0)
    point = ba0_new_point ();
  ba0_set_table_list ((struct ba0_table *) point, L);
  ba0_sort_point (point, point);
  if (ba0_is_ambiguous_point (point))
    BA0_RAISE_EXCEPTION (BA0_ERRAMB);
/*
   The struct ba0_list are freed
*/
  ba0_restore (&M);

  return point;
}

/*
   If struct_list_in_another_stack then the struct ba0_list of the outer
   list and the inner list are allocated in another stack than the current one.
*/

static struct ba0_list *
ba0_scanf_listof_list (
    struct ba0_format *f,
    char po,
    char pf,
    bool struct_list_in_another_stack)
{
  char delimiteur[] = " ";
  struct ba0_list *L = (struct ba0_list *) 0;

  delimiteur[0] = po;
  if (!ba0_sign_token_analex (delimiteur))
    BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);

  ba0_get_token_analex ();
  delimiteur[0] = pf;
  if (ba0_sign_token_analex (delimiteur))
    return L;

  for (;;)
    {
      struct ba0_list *res;
      res = ba0_scanf_list (f, po, pf, struct_list_in_another_stack);

      if (struct_list_in_another_stack)
        {
          ba0_push_another_stack ();
          L = ba0_cons_list (res, L);
          ba0_pull_stack ();
        }
      else
        L = ba0_cons_list (res, L);

      ba0_get_token_analex ();
      if (!ba0_sign_token_analex (","))
        break;
      ba0_get_token_analex ();
    }

  if (!ba0_sign_token_analex (delimiteur))
    BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);

  return ba0_reverse_list (L);
}

static struct ba0_matrix *
ba0_scanf_matrix (
    struct ba0_format *f,
    char po,
    char pf,
    struct ba0_matrix *M)
{
  struct ba0_list *L, *LL;
  ba0_int_p m, n, o, i, j;
  struct ba0_mark mark;
/*
   A matrix is parsed as a list of lists.
   A mark is set in another stack before parsing the list
*/
  ba0_push_another_stack ();
  ba0_record (&mark);
  ba0_pull_stack ();

  L = ba0_scanf_listof_list (f, po, pf, true);

  n = ba0_length_list (L);
  m = 0;
  for (LL = L; LL != (struct ba0_list *) 0; LL = LL->next)
    {
      o = ba0_length_list ((struct ba0_list *) LL->value);
      m = BA0_MAX (m, o);
    }
  if (M == (struct ba0_matrix *) 0)
    M = ba0_new_matrix ();
  ba0_realloc_matrix (M, n, m);
  M->nrow = n;
  M->ncol = m;
  for (i = 0; i < n; i++)
    {
      LL = (struct ba0_list *) L->value;
      for (j = 0; j < m; j++)
        {
          BA0_MAT (M, i, j) = LL->value;
          LL = LL->next;
        }
      L = L->next;
    }
/*
   The struct ba0_list are freed
*/
  ba0_restore (&mark);

  return M;
}

/*
   If toplevel is true
	Then tabres contains the addresses of the variables which must
	receive the read data. These variables are assumed to be initialized.
   If toplevel is false
	Then the read data are stored directly in the tabres entries. 
	The read data are stored in newly allocated areas.
 */

BA0_DLL void
ba0__scanf__ (
    struct ba0_format *f,
    void **tabres,
    bool toplevel)
{
  static char buffer[256];
  ba0_int_p i = 0, j = 0;
  bool backslash = false;

  ba0_unget_token_analex (1);
  while (isspace ((int) f->text[i]))
    i++;
  while (f->text[i] != '\0')
    {
      ba0_get_token_analex ();
      if (backslash || isalpha ((int) f->text[i]))
        {
          char *q = buffer;
          while (f->text[i] != '\0' &&
              (backslash || isalnum ((int) f->text[i]) || f->text[i] == '_'))
            {
              if (backslash || f->text[i] != '\\')
                *q++ = f->text[i];
              backslash = !backslash && f->text[i] == '\\';
              i += 1;
            }
          *q = '\0';
          if (ba0_type_token_analex () != ba0_string_token ||
              strcmp (ba0_value_token_analex (), buffer) != 0)
            BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
        }
      else if (f->text[i] != '%')
        {
          while (!backslash && f->text[i] == '\\')
            {
              backslash = !backslash && f->text[i] == '\\';
              i += 1;
            }
          if (f->text[i] == '\0')
            BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
          buffer[0] = f->text[i];
          backslash = !backslash && f->text[i] == '\\';
          buffer[1] = '\0';
          i += 1;
          if (!ba0_sign_token_analex (buffer))
            BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
        }
      else
        {
          i++;
          switch (f->link[j]->code)
            {
            case ba0_leaf_format:
              if (toplevel)
                (*f->link[j]->u.leaf.scanf) (tabres[j]);
              else
                tabres[j] = (*f->link[j]->u.leaf.scanf) ((void *) 0);
              break;
            case ba0_list_format:
              if (toplevel)
                *(struct ba0_list * *) tabres[j] =
                    ba0_scanf_list (f->link[j]->u.node.op,
                    f->link[j]->u.node.po, f->link[j]->u.node.pf, false);
              else
                tabres[j] = ba0_scanf_list (f->link[j]->u.node.op,
                    f->link[j]->u.node.po, f->link[j]->u.node.pf, false);
              break;
            case ba0_table_format:
              if (toplevel)
                ba0_scanf_table (f->link[j]->u.node.op,
                    f->link[j]->u.node.po,
                    f->link[j]->u.node.pf, (struct ba0_table *) tabres[j]);
              else
                tabres[j] = ba0_scanf_table (f->link[j]->u.node.op,
                    f->link[j]->u.node.po,
                    f->link[j]->u.node.pf, (struct ba0_table *) 0);
              break;
            case ba0_array_format:
              if (toplevel)
                ba0_scanf_array (f->link[j]->u.node.op,
                    f->link[j]->u.node.po,
                    f->link[j]->u.node.pf, (struct ba0_array *) tabres[j]);
              else
                tabres[j] = ba0_scanf_array (f->link[j]->u.node.op,
                    f->link[j]->u.node.po,
                    f->link[j]->u.node.pf, (struct ba0_array *) 0);
              break;
            case ba0_matrix_format:
              if (toplevel)
                ba0_scanf_matrix (f->link[j]->u.node.op,
                    f->link[j]->u.node.po,
                    f->link[j]->u.node.pf, (struct ba0_matrix *) tabres[j]);
              else
                tabres[j] = ba0_scanf_matrix (f->link[j]->u.node.op,
                    f->link[j]->u.node.po,
                    f->link[j]->u.node.pf, (struct ba0_matrix *) 0);
              break;
            case ba0_value_format:
              if (toplevel)
                ba0_scanf_value (f->link[j]->u.node.op,
                    f->link[j]->u.node.po,
                    f->link[j]->u.node.pf, (struct ba0_value *) tabres[j]);
              else
                tabres[j] = ba0_scanf_value (f->link[j]->u.node.op,
                    f->link[j]->u.node.po,
                    f->link[j]->u.node.pf, (struct ba0_value *) 0);
              break;
            case ba0_point_format:
              if (toplevel)
                ba0_scanf_point (f->link[j]->u.node.op,
                    f->link[j]->u.node.po,
                    f->link[j]->u.node.pf, (struct ba0_point *) tabres[j]);
              else
                tabres[j] = ba0_scanf_point (f->link[j]->u.node.op,
                    f->link[j]->u.node.po,
                    f->link[j]->u.node.pf, (struct ba0_point *) 0);
              break;
            }
          j++;
        }
      while (isspace ((int) f->text[i]))
        i++;
    }
}

/*
   ba0_scanf (format-string, address1, ..., addressk)
   The current token should be the first token to be read.
*/

/*
 * texinfo: ba0_scanf
 * Variant of @code{scanf} using formats. Many exception may be raised.
 * Here is an example. The succession of tokens read on the format
 * must match the ones read on the lexical analyzer. The function
 * expects a list of strings and a table of blocks. 
 * @example
 * ba0_scanf ("ring (ders = %l[%s], ranking = %t[%b]);", &ls, &lb);
 * @end example
 * Classical trap: 
 * before calling @code{ba0_scanf}, the first token of the expression
 * to be read must be the current token. After termination of @code{ba0_scanf}, 
 * the current token is the last token of the expression.
 */

BA0_DLL void
ba0_scanf (
    char *s,
    ...)
{
  struct ba0_format *f;
  va_list arg;
  void **tabres;
  ba0_int_p i;
  struct ba0_mark M;

  f = ba0_get_format (s);

  ba0_push_another_stack ();
  ba0_record (&M);

  tabres = (void **) ba0_alloc (sizeof (void *) * f->linknmb);

  ba0_pull_stack ();

  va_start (arg, s);
  for (i = 0; i < f->linknmb; i++)
    tabres[i] = va_arg (arg, void *);
  va_end (arg);

  ba0__scanf__ (f, tabres, true);

  ba0_restore (&M);
}

/*
   Variant of the above one, which reads the first token to be read.
*/

/*
 * texinfo: ba0_scanf2
 * Variant of the above function, a bit more user friendly, which
 * loads the first token of the expression
 * to be read and then calls @code{ba0_scanf}.
 */

BA0_DLL void
ba0_scanf2 (
    char *s,
    ...)
{
  struct ba0_format *f;
  va_list arg;
  void **tabres;
  ba0_int_p i;
  struct ba0_mark M;

  f = ba0_get_format (s);

  ba0_push_another_stack ();
  ba0_record (&M);

  tabres = (void **) ba0_alloc (sizeof (void *) * f->linknmb);

  ba0_pull_stack ();

  va_start (arg, s);
  for (i = 0; i < f->linknmb; i++)
    tabres[i] = va_arg (arg, void *);
  va_end (arg);

  ba0_get_token_analex ();

  ba0__scanf__ (f, tabres, true);

  ba0_restore (&M);
}

/*
   Variant of ba0_scanf
*/

/*
 * texinfo: ba0_sscanf
 * Read in @var{buffer}. Same remarks as @code{ba0_scanf}.
 */

BA0_DLL void
ba0_sscanf (
    char *buffer,
    char *s,
    ...)
{
  struct ba0_format *f;
  va_list arg;
  void **tabres;
  ba0_int_p i;
  struct ba0_mark M;

  f = ba0_get_format (s);

  ba0_push_another_stack ();
  ba0_record (&M);

  tabres = (void **) ba0_alloc (sizeof (void *) * f->linknmb);

  ba0_pull_stack ();

  va_start (arg, s);
  for (i = 0; i < f->linknmb; i++)
    tabres[i] = va_arg (arg, void *);
  va_end (arg);

  ba0_record_analex ();
  ba0_set_analex_string (buffer);

  BA0_TRY
  {
    ba0__scanf__ (f, tabres, true);
    ba0_restore_analex ();
  }
  BA0_CATCH
  {
    ba0_restore_analex ();
    BA0_RE_RAISE_EXCEPTION;
  }
  BA0_ENDTRY;
  ba0_restore (&M);
}

/*
   Variant of ba0_scanf2
*/

/*
 * texinfo: ba0_sscanf2
 * Read in @var{buffer}. Same remarks as @code{ba0_scanf2}.
 */

BA0_DLL void
ba0_sscanf2 (
    char *buffer,
    char *s,
    ...)
{
  struct ba0_format *f;
  va_list arg;
  void **tabres;
  ba0_int_p i;
  struct ba0_mark M;

  f = ba0_get_format (s);

  ba0_push_another_stack ();
  ba0_record (&M);

  tabres = (void **) ba0_alloc (sizeof (void *) * f->linknmb);

  ba0_pull_stack ();

  va_start (arg, s);
  for (i = 0; i < f->linknmb; i++)
    tabres[i] = va_arg (arg, void *);
  va_end (arg);

  ba0_record_analex ();
  ba0_set_analex_string (buffer);

  BA0_TRY
  {
    ba0_get_token_analex ();
    ba0__scanf__ (f, tabres, true);
    ba0_restore_analex ();
  }
  BA0_CATCH
  {
    ba0_restore_analex ();
    BA0_RE_RAISE_EXCEPTION;
  }
  BA0_ENDTRY;
  ba0_restore (&M);
}

/*
 * texinfo: ba0_fscanf
 * Read in @var{file}. Same remarks as @code{ba0_scanf}.
 */

BA0_DLL void
ba0_fscanf (
    FILE *file,
    char *s,
    ...)
{
  struct ba0_format *f;
  va_list arg;
  void **tabres;
  ba0_int_p i;
  struct ba0_mark M;

  f = ba0_get_format (s);

  ba0_push_another_stack ();
  ba0_record (&M);

  tabres = (void **) ba0_alloc (sizeof (void *) * f->linknmb);

  ba0_pull_stack ();

  va_start (arg, s);
  for (i = 0; i < f->linknmb; i++)
    tabres[i] = va_arg (arg, void *);
  va_end (arg);

  ba0_record_analex ();
  ba0_set_analex_FILE (file);

  BA0_TRY
  {
    ba0__scanf__ (f, tabres, true);
    ba0_restore_analex ();
  }
  BA0_CATCH
  {
    ba0_restore_analex ();
    BA0_RE_RAISE_EXCEPTION;
  }
  BA0_ENDTRY;
  ba0_restore (&M);
}

/*
 * texinfo: ba0_fscanf2
 * Read in @var{file}. Same remarks as @code{ba0_scanf2}.
 */

BA0_DLL void
ba0_fscanf2 (
    FILE *file,
    char *s,
    ...)
{
  struct ba0_format *f;
  va_list arg;
  void **tabres;
  ba0_int_p i;
  struct ba0_mark M;

  f = ba0_get_format (s);

  ba0_push_another_stack ();
  ba0_record (&M);

  tabres = (void **) ba0_alloc (sizeof (void *) * f->linknmb);

  ba0_pull_stack ();

  va_start (arg, s);
  for (i = 0; i < f->linknmb; i++)
    tabres[i] = va_arg (arg, void *);
  va_end (arg);

  ba0_record_analex ();
  ba0_set_analex_FILE (file);

  BA0_TRY
  {
    ba0_get_token_analex ();
    ba0__scanf__ (f, tabres, true);
    ba0_restore_analex ();
  }
  BA0_CATCH
  {
    ba0_restore_analex ();
    BA0_RE_RAISE_EXCEPTION;
  }
  BA0_ENDTRY;
  ba0_restore (&M);
}
