#include "ba0_int_p.h"
#include "ba0_exception.h"
#include "ba0_stack.h"
#include "ba0_list.h"
#include "ba0_table.h"
#include "ba0_array.h"
#include "ba0_matrix.h"
#include "ba0_point.h"
#include "ba0_format.h"
#include "ba0_printf.h"
#include "ba0_basic_io.h"
#include "ba0_global.h"

static void ba0_printf_list (
    struct ba0_format *,
    char,
    char,
    struct ba0_list *);
static void ba0_printf_table (
    struct ba0_format *,
    char,
    char,
    struct ba0_table *);
static void ba0_printf_array (
    struct ba0_format *,
    char,
    char,
    struct ba0_array *);
static void ba0_printf_matrix (
    struct ba0_format *,
    char,
    char,
    struct ba0_matrix *);
static void ba0_printf_value (
    struct ba0_format *,
    char,
    char,
    struct ba0_value *);
static void ba0_printf_point (
    struct ba0_format *,
    char,
    char,
    struct ba0_point *);

/*
 * Backslashes in the text protect the next character and are not printed,
 * unless protected by another backslash.
 */

BA0_DLL void
ba0__printf__ (
    struct ba0_format *f,
    void **objet)
{
  int i, j;
  bool backslash;

  if (f == (struct ba0_format *) 0)
    return;

  for (i = 0, j = 0, backslash = false; f->text[i] != '\0'; i++)
    {
      if (f->text[i] == '%' && !backslash)
        {
          switch (f->link[j]->code)
            {
            case ba0_leaf_format:
              (*f->link[j]->u.leaf.printf) (*objet++);
              break;
            case ba0_list_format:
              ba0_printf_list (f->link[j]->u.node.op,
                  f->link[j]->u.node.po,
                  f->link[j]->u.node.pf, (struct ba0_list *) *objet++);
              break;
            case ba0_table_format:
              ba0_printf_table (f->link[j]->u.node.op,
                  f->link[j]->u.node.po,
                  f->link[j]->u.node.pf, (struct ba0_table *) *objet++);
              break;
            case ba0_array_format:
              ba0_printf_array (f->link[j]->u.node.op,
                  f->link[j]->u.node.po,
                  f->link[j]->u.node.pf, (struct ba0_array *) *objet++);
              break;
            case ba0_matrix_format:
              ba0_printf_matrix (f->link[j]->u.node.op,
                  f->link[j]->u.node.po,
                  f->link[j]->u.node.pf, (struct ba0_matrix *) *objet++);
              break;
            case ba0_value_format:
              ba0_printf_value (f->link[j]->u.node.op,
                  f->link[j]->u.node.po,
                  f->link[j]->u.node.pf, (struct ba0_value *) *objet++);
              break;
            case ba0_point_format:
              ba0_printf_point (f->link[j]->u.node.op,
                  f->link[j]->u.node.po,
                  f->link[j]->u.node.pf, (struct ba0_point *) *objet++);
              break;
            }
          j++;
        }
      else
        {
          if (backslash || f->text[i] != '\\')
            ba0_put_char (f->text[i]);
          backslash = !backslash && f->text[i] == '\\';
        }
    }
}

static void
ba0_printf_value (
    struct ba0_format *f,
    char po,
    char pf,
    struct ba0_value *value)
{
  if (ba0_global.format.printf_value_var == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);
  (*ba0_global.format.printf_value_var) (value->var);
  ba0_put_char (' ');
  ba0_put_string (ba0_initialized_global.value.equal_sign);
  ba0_put_char (' ');
  ba0__printf__ (f, &value->value);
}

static void
ba0_printf_list (
    struct ba0_format *f,
    char po,
    char pf,
    struct ba0_list *L)
{
  bool deja = false;

  ba0_put_char (po);
  while (L != (struct ba0_list *) 0)
    {
      if (deja)
        {
          if (ba0_global.common.LaTeX)
            ba0_put_string (",\\, ");
          else
            ba0_put_string (", ");
        }
      else
        deja = true;
      ba0__printf__ (f, &L->value);
      L = L->next;
    }
  ba0_put_char (pf);
}

static void
ba0_printf_table (
    struct ba0_format *f,
    char po,
    char pf,
    struct ba0_table *T)
{
  ba0_int_p i;

  ba0_put_char (po);
  for (i = 0; i < T->size - 1; i++)
    {
      ba0__printf__ (f, &T->tab[i]);
      if (ba0_global.common.LaTeX)
        ba0_put_string (",\\, ");
      else
        ba0_put_string (", ");
    }
  if (T->size > 0)
    ba0__printf__ (f, &T->tab[T->size - 1]);
  ba0_put_char (pf);
}

static void
ba0_printf_point (
    struct ba0_format *f,
    char po,
    char pf,
    struct ba0_point *point)
{
  ba0_int_p i;

  ba0_put_char (po);
  for (i = 0; i < point->size - 1; i++)
    {
      ba0_printf_value (f, po, pf, point->tab[i]);
      if (ba0_global.common.LaTeX)
        ba0_put_string (",\\, ");
      else
        ba0_put_string (", ");
    }
  if (point->size > 0)
    ba0_printf_value (f, po, pf, point->tab[point->size - 1]);
  ba0_put_char (pf);
}

static void
ba0_printf_array (
    struct ba0_format *f,
    char po,
    char pf,
    struct ba0_array *A)
{
  ba0_int_p i;
  void *z;
/*
  The special case of array of machine integers
*/
  if (f->linknmb > 0 &&
      (f->link[0]->u.leaf.scanf == ba0_scanf_int_p ||
          f->link[0]->u.leaf.scanf == ba0_scanf_hexint_p))
    {
      struct ba0_table T;
      T.alloc = A->alloc;
      T.size = A->size;
      T.tab = (void **) A->tab;
      ba0_printf_table (f, po, pf, &T);
      return;
    }
/*
  The general case
*/
  ba0_put_char (po);
  for (i = 0; i < A->size - 1; i++)
    {
      z = (void *) (A->tab + i * A->sizelt);
      ba0__printf__ (f, &z);
      if (ba0_global.common.LaTeX)
        ba0_put_string (",\\, ");
      else
        ba0_put_string (", ");
    }
  if (A->size > 0)
    {
      z = (void *) (A->tab + (A->size - 1) * A->sizelt);
      ba0__printf__ (f, &z);
    }
  ba0_put_char (pf);
}

static void
ba0_printf_matrix (
    struct ba0_format *f,
    char po,
    char pf,
    struct ba0_matrix *M)
{
  ba0_int_p i, j;

  ba0_put_char (po);
  for (i = 0; i < M->nrow; i++)
    {
      ba0_put_char (po);
      for (j = 0; j < M->ncol - 1; j++)
        {
          ba0__printf__ (f, &BA0_MAT (M, i, j));
          if (ba0_global.common.LaTeX)
            ba0_put_string (",\\, ");
          else
            ba0_put_string (", ");
        }
      if (M->ncol > 0)
        ba0__printf__ (f, &BA0_MAT (M, i, M->ncol - 1));
      ba0_put_char (pf);
      if (i < M->nrow - 1)
        {
          if (ba0_global.common.LaTeX)
            ba0_put_string (",\\, ");
          else
            ba0_put_string (", ");
        }
    }
  ba0_put_char (pf);
}

/*
 * texinfo: ba0_printf
 * Variant of @code{printf}.
 */

BA0_DLL void
ba0_printf (
    char *s,
    ...)
{
  struct ba0_format *f = ba0_get_format (s);
  void **objet;
  va_list arg;
  ba0_int_p i;
  struct ba0_mark M;

  ba0_record (&M);
  objet = (void **) ba0_alloc (sizeof (void *) * f->linknmb);
  va_start (arg, s);
  for (i = 0; i < f->linknmb; i++)
    objet[i] = va_arg (arg, void *);
  va_end (arg);
  ba0__printf__ (f, objet);
  ba0_restore (&M);
}

/*
 * texinfo: ba0_new_printf
 * Print the expressions in a dynamically allocated 
 * (through @code{ba0_persistent_malloc}) string of the right length 
 * and returns it. The string still exists after executing
 * @code{ba0_terminate}.
 */

BA0_DLL char *
ba0_new_printf (
    char *s,
    ...)
{
  struct ba0_format *f = ba0_get_format (s);
  void **objet;
  va_list arg;
  ba0_int_p i;
  struct ba0_mark M;
  char *buffer = (char *) 0;

  ba0_record (&M);
  objet = (void **) ba0_alloc (sizeof (void *) * f->linknmb);
  va_start (arg, s);
  for (i = 0; i < f->linknmb; i++)
    objet[i] = va_arg (arg, void *);
  va_end (arg);

  ba0_record_output ();

  BA0_TRY
  {
    ba0_set_output_counter ();
    ba0__printf__ (f, objet);
    buffer = ba0_persistent_malloc (ba0_output_counter () + 1);
    ba0_set_output_string (buffer);
    ba0__printf__ (f, objet);
    ba0_restore_output ();
  }
  BA0_CATCH
  {
    ba0_restore_output ();
    BA0_RE_RAISE_EXCEPTION;
  }
  BA0_ENDTRY;

  ba0_restore (&M);
  return buffer;
}

/*
 * texinfo: ba0_sprintf
 * Variant of @code{sprintf}. Print in @var{buffer}.
 */

BA0_DLL void
ba0_sprintf (
    char *buffer,
    char *s,
    ...)
{
  struct ba0_format *f = ba0_get_format (s);
  void **objet;
  va_list arg;
  ba0_int_p i;
  struct ba0_mark M;

  ba0_record (&M);
  objet = (void **) ba0_alloc (sizeof (void *) * f->linknmb);
  va_start (arg, s);
  for (i = 0; i < f->linknmb; i++)
    objet[i] = va_arg (arg, void *);
  va_end (arg);

  ba0_record_output ();
  ba0_set_output_string (buffer);

  BA0_TRY
  {
    ba0__printf__ (f, objet);
    ba0_restore_output ();
  }
  BA0_CATCH
  {
    ba0_restore_output ();
    BA0_RE_RAISE_EXCEPTION;
  }
  BA0_ENDTRY;
  ba0_restore (&M);
}

/*
 * texinfo: ba0_fprintf
 * Variant of @code{fprintf}. Print in @var{file}.
 */

BA0_DLL void
ba0_fprintf (
    FILE *file,
    char *s,
    ...)
{
  struct ba0_format *f = ba0_get_format (s);
  void **objet;
  va_list arg;
  ba0_int_p i;
  struct ba0_mark M;

  ba0_record (&M);
  objet = (void **) ba0_alloc (sizeof (void *) * f->linknmb);
  va_start (arg, s);
  for (i = 0; i < f->linknmb; i++)
    objet[i] = va_arg (arg, void *);
  va_end (arg);

  ba0_record_output ();
  ba0_set_output_FILE (file);

  BA0_TRY
  {
    ba0__printf__ (f, objet);
    ba0_restore_output ();
  }
  BA0_CATCH
  {
    ba0_restore_output ();
    BA0_RE_RAISE_EXCEPTION;
  }
  BA0_ENDTRY;
  ba0_restore (&M);
}
