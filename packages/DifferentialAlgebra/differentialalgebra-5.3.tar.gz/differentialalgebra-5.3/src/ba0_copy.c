#include "ba0_exception.h"
#include "ba0_stack.h"
#include "ba0_format.h"
#include "ba0_list.h"
#include "ba0_table.h"
#include "ba0_array.h"
#include "ba0_matrix.h"
#include "ba0_point.h"
#include "ba0_copy.h"

static struct ba0_list *this_copy_list (
    struct ba0_format *,
    struct ba0_list *);
static struct ba0_table *ba0_copy_table (
    struct ba0_format *,
    struct ba0_table *);
static struct ba0_array *ba0_copy_array (
    struct ba0_format *,
    struct ba0_array *);
static struct ba0_matrix *ba0_copy_matrix (
    struct ba0_format *,
    struct ba0_matrix *);
static struct ba0_value *ba0_copy_value (
    struct ba0_format *,
    struct ba0_value *);
static struct ba0_point *ba0_copy_point (
    struct ba0_format *,
    struct ba0_point *);

static void *
ba0_copy_pointer (
    struct ba0_format *f,
    void *o)
{
  if (o != (void *) 0)
    {
      switch (f->link[0]->code)
        {
        case ba0_leaf_format:
          return (*f->link[0]->u.leaf.copy) (o);
        case ba0_list_format:
          return this_copy_list (f->link[0]->u.node.op, (struct ba0_list *) o);
        case ba0_table_format:
          return ba0_copy_table (f->link[0]->u.node.op, (struct ba0_table *) o);
        case ba0_array_format:
          return ba0_copy_array (f->link[0]->u.node.op, (struct ba0_array *) o);
        case ba0_matrix_format:
          return ba0_copy_matrix (f->link[0]->u.node.op,
              (struct ba0_matrix *) o);
        case ba0_value_format:
          return ba0_copy_value (f->link[0]->u.node.op, (struct ba0_value *) o);
        case ba0_point_format:
          return ba0_copy_point (f->link[0]->u.node.op, (struct ba0_point *) o);
        }
    }
  return (void *) 0;
}

static struct ba0_list *
this_copy_list (
    struct ba0_format *f,
    struct ba0_list *L)
{
  struct ba0_list *M;

  M = (struct ba0_list *) 0;
  while (L != (struct ba0_list *) 0)
    {
      M = ba0_cons_list (ba0_copy_pointer (f, L->value), M);
      L = L->next;
    }
  M = ba0_reverse_list (M);
  return M;
}

static struct ba0_table *
ba0_copy_table (
    struct ba0_format *f,
    struct ba0_table *t)
{
  struct ba0_table *u;
  ba0_int_p i;

  u = ba0_new_table ();
  ba0_realloc_table (u, t->size);
  u->size = t->size;
  for (i = 0; i < u->size; i++)
    u->tab[i] = ba0_copy_pointer (f, t->tab[i]);
  return u;
}

static struct ba0_value *
ba0_copy_value (
    struct ba0_format *f,
    struct ba0_value *value)
{
  struct ba0_value *newval;

  newval = ba0_new_value ();
  newval->var = value->var;
  newval->value = ba0_copy_pointer (f, value->value);
  return newval;
}

static struct ba0_point *
ba0_copy_point (
    struct ba0_format *f,
    struct ba0_point *point)
{
  struct ba0_point *newpnt;
  ba0_int_p i;

  newpnt = ba0_new_point ();
  ba0_realloc_table ((struct ba0_table *) newpnt, point->size);
  newpnt->size = point->size;
  for (i = 0; i < newpnt->size; i++)
    newpnt->tab[i] = ba0_copy_value (f, point->tab[i]);
  return newpnt;
}

static struct ba0_array *
ba0_copy_array (
    struct ba0_format *f,
    struct ba0_array *A)
{
  struct ba0_array *u;
  ba0_int_p i;
  void *x;

  u = ba0_new_array ();
  ba0_realloc_array (u, A->size, A->sizelt);
  u->size = A->size;
  for (i = 0; i < u->size; i++)
    {
      x = ba0_copy_pointer (f, A->tab + i * A->sizelt);
      memcpy (u->tab + i * A->sizelt, x, A->sizelt);
    }
  return u;
}

static struct ba0_matrix *
ba0_copy_matrix (
    struct ba0_format *f,
    struct ba0_matrix *M)
{
  struct ba0_matrix *N;
  ba0_int_p i, size;

  size = M->nrow * M->ncol;
  N = ba0_new_matrix ();
  ba0_realloc_matrix (N, M->nrow, M->ncol);
  for (i = 0; i < size; i++)
    N->entry[i] = ba0_copy_pointer (f, M->entry[i]);
  return N;
}

/*
   Returns a copy of the the object o the format of which is described by s.
*/

BA0_DLL void *
ba0_copy (
    char *s,
    void *o)
{
  struct ba0_format *f = ba0_get_format (s);

  return ba0_copy_pointer (f, o);
}
