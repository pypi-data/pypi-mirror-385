#include "ba0_exception.h"
#include "ba0_stack.h"
#include "ba0_list.h"
#include "ba0_table.h"
#include "ba0_array.h"
#include "ba0_matrix.h"
#include "ba0_point.h"
#include "ba0_format.h"
#include "ba0_garbage.h"
#include "ba0_global.h"

#define ba0_tab			ba0_global.garbage.tab
#define ba0_user_provided_mark	ba0_global.garbage.user_provided_mark
#define ba0_current		ba0_global.garbage.current
#define ba0_old_free		ba0_global.garbage.old_free

/************************************************************************
 STEP 2

 ba0_tab is an array of pointers to struct ba0_gc_info.
 It is filled with the addresses of the struct ba0_gc_info created at
 step 1. Then it is sorted increasingly. The addresses of the areas
 referred to by the struct ba0_gc_info are compared.
 ************************************************************************/

/*
  Comparison function for sorting
  Indices in cells are compared first, then the addresses.
*/

static int
ba0_compare_tab_elts (
    const void *a,
    const void *b)
{
  struct ba0_gc_info **aa = (struct ba0_gc_info * *) a;
  struct ba0_gc_info **bb = (struct ba0_gc_info * *) b;

  if ((*aa)->old_index_in_cells < (*bb)->old_index_in_cells ||
      ((*aa)->old_index_in_cells == (*bb)->old_index_in_cells &&
          (*aa)->old_addr < (*bb)->old_addr))
    return -1;
  else if ((*aa)->old_index_in_cells == (*bb)->old_index_in_cells &&
      (*aa)->old_addr == (*bb)->old_addr)
    return 0;
  else
    return 1;
}

/*
 * Fills ba0_tab with the addresses of the n struct ba0_gc_info created 
 * at step 1.
 */

static void
ba0_fill_tab (
    ba0_int_p n)
{
  ba0_int_p i;
  struct ba0_mark M;

  M = ba0_current;
  for (i = 0; i < n; i++)
    ba0_tab[i] =
        (struct ba0_gc_info *) ba0_alloc_mark (&M, sizeof (struct ba0_gc_info));
}

/*************************************************************************
 STEP 3

 Copies over ba0_user_provided_mark, which is equal to the mark provided by
 the user, the areas referred to by the struct ba0_gc_info.

 Removes holes between areas.

 The order in memory of the areas is preserved (that's why they are
 addressed through ba0_tab, which is sorted).

 Shared areas are not duplicated.
 *************************************************************************/

static void
ba0_remove_holes_between_areas (
    ba0_int_p n)
{
  struct ba0_gc_info *g, *h;
  ba0_int_p i;
  void *q;

  h = ba0_tab[0];
/*
 * Careful call to ba0_alloc because of overlapping moves
 */
  q = ba0_alloc_but_do_not_set_magic (h->u.size);
  memmove (q, h->old_addr, h->u.size);
  h->u.new_addr = q;
  ba0_alloc_set_magic ();

  for (i = 1; i < n; i++)
    {
      g = h;
      h = ba0_tab[i];
/* 
 * This test avoids duplicating shared areas
 */
      if (g->old_addr == h->old_addr)
        h->u.new_addr = g->u.new_addr;
      else
/*
 * Careful call to ba0_alloc because of overlapping moves
 */
        {
          q = ba0_alloc_but_do_not_set_magic (h->u.size);
          memmove (q, h->old_addr, h->u.size);
          h->u.new_addr = q;
          ba0_alloc_set_magic ();
        }
    }
}

/***********************************************************************
 STEP 1

 Run over the data structures to be garbaged.
 Struct ba0_gc_info * are created for each area.
 ***********************************************************************/

static ba0_int_p ba0_garbage1_list (
    struct ba0_subformat *,
    struct ba0_list *,
    enum ba0_garbage_code code);
static ba0_int_p ba0_garbage1_table (
    struct ba0_subformat *,
    struct ba0_table *,
    enum ba0_garbage_code code);
static ba0_int_p ba0_garbage1_array (
    struct ba0_subformat *,
    struct ba0_array *,
    enum ba0_garbage_code code);
static ba0_int_p ba0_garbage1_matrix (
    struct ba0_subformat *,
    struct ba0_matrix *,
    enum ba0_garbage_code code);
static ba0_int_p ba0_garbage1_value (
    struct ba0_subformat *,
    struct ba0_value *,
    enum ba0_garbage_code code);
static ba0_int_p ba0_garbage1_point (
    struct ba0_subformat *,
    struct ba0_point *,
    enum ba0_garbage_code code);

static ba0_int_p
ba0_garbage1_pointer (
    struct ba0_subformat *f,
    void *objet,
    enum ba0_garbage_code code)
{
  ba0_int_p n = 0;

  if (objet != (void *) 0)
    {
      switch (f->code)
        {
        case ba0_leaf_format:
          n = (*f->u.leaf.garbage1) (objet, code);
          break;
        case ba0_list_format:
          n = ba0_garbage1_list (f->u.node.op->link[0],
              (struct ba0_list *) objet, code);
          break;
        case ba0_table_format:
          n = ba0_garbage1_table (f->u.node.op->link[0],
              (struct ba0_table *) objet, code);
          break;
        case ba0_array_format:
          n = ba0_garbage1_array (f->u.node.op->link[0],
              (struct ba0_array *) objet, code);
          break;
        case ba0_matrix_format:
          n = ba0_garbage1_matrix (f->u.node.op->link[0],
              (struct ba0_matrix *) objet, code);
          break;
        case ba0_value_format:
          n = ba0_garbage1_value (f->u.node.op->link[0],
              (struct ba0_value *) objet, code);
          break;
        case ba0_point_format:
          n = ba0_garbage1_point (f->u.node.op->link[0],
              (struct ba0_point *) objet, code);
          break;
        }
    }
  return n;
}

/*
 * Readonly static data
 */

static char _struct_list[] = "struct list";

static ba0_int_p
ba0_garbage1_list (
    struct ba0_subformat *f,
    struct ba0_list *L,
    enum ba0_garbage_code code)
{
  ba0_int_p n = 0;

  while (L != (struct ba0_list *) 0)
    {
      if (code == ba0_isolated)
        n += ba0_new_gc_info (L, sizeof (struct ba0_list), _struct_list);
      n += ba0_garbage1_pointer (f, L->value, ba0_isolated);
      L = L->next;
    }
  return n;
}

/*
 * Readonly static data
 */

static char _struct_table[] = "struct table";
static char _struct_table_tab[] = "struct table->tab";

static ba0_int_p
ba0_garbage1_table (
    struct ba0_subformat *f,
    struct ba0_table *T,
    enum ba0_garbage_code code)
{
  ba0_int_p i, n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (T, sizeof (struct ba0_table), _struct_table);
  if (T->alloc > 0)
    {
      n += ba0_new_gc_info
          (T->tab, T->alloc * sizeof (void *), _struct_table_tab);
      if (f->code != ba0_leaf_format ||
          f->u.leaf.garbage1 != ba0_empty_garbage1)
        {
          for (i = 0; i < T->size; i++)
            n += ba0_garbage1_pointer (f, T->tab[i], ba0_isolated);
          for (i = T->size; i < T->alloc && T->tab[i] != (void *) 0; i++)
            n += ba0_garbage1_pointer (f, T->tab[i], ba0_isolated);
        }
    }
  return n;
}

/*
 * Readonly static data
 */

static char _struct_point[] = "struct point";
static char _struct_point_tab[] = "struct point->tab";

static ba0_int_p
ba0_garbage1_point (
    struct ba0_subformat *f,
    struct ba0_point *point,
    enum ba0_garbage_code code)
{
  ba0_int_p i, n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (point, sizeof (struct ba0_point), _struct_point);
  if (point->alloc > 0)
    {
      n += ba0_new_gc_info
          (point->tab, point->alloc * sizeof (void *), _struct_point_tab);
      for (i = 0; i < point->alloc; i++)
        n += ba0_garbage1_value (f, point->tab[i], ba0_isolated);
    }
  return n;
}

/*
 * Readonly static data
 */

static char _struct_array[] = "struct array";
static char _struct_array_tab[] = "struct array->tab";

static ba0_int_p
ba0_garbage1_array (
    struct ba0_subformat *f,
    struct ba0_array *A,
    enum ba0_garbage_code code)
{
  ba0_int_p i, n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (A, sizeof (struct ba0_array), _struct_array);
  if (A->alloc > 0)
    {
      if (f->code != ba0_leaf_format ||
          f->u.leaf.garbage1 != ba0_empty_garbage1)
        {
          n += ba0_new_gc_info
              (A->tab, A->alloc * A->sizelt, _struct_array_tab);
          for (i = 0; i < A->alloc; i++)
            n += ba0_garbage1_pointer (f, A->tab + i * A->sizelt, ba0_embedded);
        }
      else
        {
          n += ba0_new_gc_info
              (A->tab, A->alloc * A->sizelt, _struct_array_tab);
        }
    }
  return n;
}

/*
 * Readonly static data
 */

static char _struct_matrix[] = "struct ba0_matrix";
static char _struct_matrix_ntry[] = "struct ba0_matrix->entry";

static ba0_int_p
ba0_garbage1_matrix (
    struct ba0_subformat *f,
    struct ba0_matrix *T,
    enum ba0_garbage_code code)
{
  ba0_int_p i, n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (T, sizeof (struct ba0_matrix), _struct_matrix);
  if (T->alloc > 0)
    {
      n += ba0_new_gc_info
          (T->entry, T->alloc * sizeof (void *), _struct_matrix_ntry);
      for (i = 0; i < T->alloc; i++)
        n += ba0_garbage1_pointer (f, T->entry[i], ba0_isolated);
    }
  return n;
}

static char _struct_value[] = "struct ba0_value";

static ba0_int_p
ba0_garbage1_value (
    struct ba0_subformat *f,
    struct ba0_value *value,
    enum ba0_garbage_code code)
{
  ba0_int_p n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (value, sizeof (struct ba0_value), _struct_value);
  n += ba0_garbage1_pointer (f, value->value, ba0_isolated);
  return n;
}

/***********************************************************************
 STEP 4

 Run over the garbaged data structure in order to update internal pointers.

 Runs therefore over the areas exactly in the same order as in step 1.
 The right new addresses of the areas are obtained by running at the same
 time over the struct ba0_gc_info created at step 1: they are stored
 in the new_addr fields.
 ***********************************************************************/

static struct ba0_list *ba0_garbage2_list (
    struct ba0_subformat *,
    struct ba0_list *,
    enum ba0_garbage_code code);
static struct ba0_table *ba0_garbage2_table (
    struct ba0_subformat *,
    struct ba0_table *,
    enum ba0_garbage_code code);
static struct ba0_array *ba0_garbage2_array (
    struct ba0_subformat *,
    struct ba0_array *,
    enum ba0_garbage_code code);
static struct ba0_matrix *ba0_garbage2_matrix (
    struct ba0_subformat *,
    struct ba0_matrix *,
    enum ba0_garbage_code code);
static struct ba0_value *ba0_garbage2_value (
    struct ba0_subformat *,
    struct ba0_value *,
    enum ba0_garbage_code code);
static struct ba0_point *ba0_garbage2_point (
    struct ba0_subformat *,
    struct ba0_point *,
    enum ba0_garbage_code code);

static void *
ba0_garbage2_pointer (
    struct ba0_subformat *f,
    void *objet,
    enum ba0_garbage_code code)
{
  if (objet != (void *) 0)
    {
      switch (f->code)
        {
        case ba0_leaf_format:
          objet = (*f->u.leaf.garbage2) (objet, code);
          break;
        case ba0_list_format:
          objet =
              ba0_garbage2_list (f->u.node.op->link[0],
              (struct ba0_list *) objet, code);
          break;
        case ba0_table_format:
          objet = ba0_garbage2_table
              (f->u.node.op->link[0], (struct ba0_table *) objet, code);
          break;
        case ba0_array_format:
          objet = ba0_garbage2_array
              (f->u.node.op->link[0], (struct ba0_array *) objet, code);
          break;
        case ba0_matrix_format:
          objet = ba0_garbage2_matrix
              (f->u.node.op->link[0], (struct ba0_matrix *) objet, code);
          break;
        case ba0_value_format:
          objet = ba0_garbage2_value
              (f->u.node.op->link[0], (struct ba0_value *) objet, code);
          break;
        case ba0_point_format:
          objet = ba0_garbage2_point
              (f->u.node.op->link[0], (struct ba0_point *) objet, code);
          break;
        }
    }
  return objet;
}

/*
   Embedded lists only work if the structure which involved the list
   is not moved by the garbage collector. Otherwise next pointers get
   corrupted.
*/

static struct ba0_list *
ba0_garbage2_list (
    struct ba0_subformat *f,
    struct ba0_list *Head,
    enum ba0_garbage_code code)
{
  struct ba0_list *L;

  L = Head = (struct ba0_list *) ba0_new_addr_gc_info (Head, _struct_list);

  while (L != (struct ba0_list *) 0)
    {
      L->value = ba0_garbage2_pointer (f, L->value, ba0_isolated);
      if (L->next != (struct ba0_list *) 0)
        {
          if (code == ba0_isolated)
            L = L->next =
                (struct ba0_list *) ba0_new_addr_gc_info (L->next,
                _struct_list);
          else
            L = L->next;
        }
      else
        L = L->next = (struct ba0_list *) 0;
    }

  return Head;
}

static struct ba0_table *
ba0_garbage2_table (
    struct ba0_subformat *f,
    struct ba0_table *T,
    enum ba0_garbage_code code)
{
  ba0_int_p i;

  if (code == ba0_isolated)
    T = (struct ba0_table *) ba0_new_addr_gc_info (T, _struct_table);

  if (T->alloc > 0)
    {
      T->tab = (void **) ba0_new_addr_gc_info (T->tab, _struct_table_tab);
      if (f->code != ba0_leaf_format
          || f->u.leaf.garbage1 != ba0_empty_garbage1)
        {
          for (i = 0; i < T->size; i++)
            T->tab[i] = ba0_garbage2_pointer (f, T->tab[i], ba0_isolated);
          for (i = T->size; i < T->alloc && T->tab[i] != (void *) 0; i++)
            T->tab[i] = ba0_garbage2_pointer (f, T->tab[i], ba0_isolated);
        }
    }
  return T;
}

static struct ba0_point *
ba0_garbage2_point (
    struct ba0_subformat *f,
    struct ba0_point *point,
    enum ba0_garbage_code code)
{
  ba0_int_p i;

  if (code == ba0_isolated)
    point = (struct ba0_point *) ba0_new_addr_gc_info (point, _struct_point);

  if (point->alloc > 0)
    {
      point->tab =
          (struct ba0_value * *) ba0_new_addr_gc_info (point->tab,
          _struct_point_tab);
      for (i = 0; i < point->alloc; i++)
        point->tab[i] = (struct ba0_value *) ba0_garbage2_value
            (f, point->tab[i], ba0_isolated);
    }
  return point;
}

static struct ba0_value *
ba0_garbage2_value (
    struct ba0_subformat *f,
    struct ba0_value *value,
    enum ba0_garbage_code code)
{
  if (code == ba0_isolated)
    value = (struct ba0_value *) ba0_new_addr_gc_info (value, _struct_value);
  value->value = ba0_garbage2_pointer (f, value->value, ba0_isolated);
  return value;
}

static struct ba0_array *
ba0_garbage2_array (
    struct ba0_subformat *f,
    struct ba0_array *A,
    enum ba0_garbage_code code)
{
  ba0_int_p i;

  if (code == ba0_isolated)
    A = (struct ba0_array *) ba0_new_addr_gc_info (A, _struct_array);

  if (A->alloc > 0)
    {
      A->tab = (void *) ba0_new_addr_gc_info (A->tab, _struct_array_tab);
      if (f->code != ba0_leaf_format
          || f->u.leaf.garbage1 != ba0_empty_garbage1)
        {
          for (i = 0; i < A->alloc; i++)
            ba0_garbage2_pointer (f, A->tab + i * A->sizelt, ba0_embedded);
        }
    }
  return A;
}

static struct ba0_matrix *
ba0_garbage2_matrix (
    struct ba0_subformat *f,
    struct ba0_matrix *T,
    enum ba0_garbage_code code)
{
  ba0_int_p i;

  if (code == ba0_isolated)
    T = (struct ba0_matrix *) ba0_new_addr_gc_info (T, _struct_matrix);

  if (T->alloc > 0)
    {
      T->entry = (void **) ba0_new_addr_gc_info (T->entry, _struct_matrix_ntry);
      for (i = 0; i < T->alloc; i++)
        T->entry[i] = ba0_garbage2_pointer (f, T->entry[i], ba0_isolated);
    }
  return T;
}

/*
   This function is called by a garbage1 function.
   It is thus used at step 1.

   old_addr is the address if an area.
   If this area lies below ba0_user_provided_mark which is the mark provided by
   the user, then nothing is done. Otherwise, a struct ba0_gc_info is
   created with the relevant information.

   Returns the number of struct ba0_gc_info created (0 or 1).
*/

BA0_DLL ba0_int_p
ba0_new_gc_info (
    void *old_addr,
    unsigned ba0_int_p size,
    char *text)
{
  ba0_int_p old_index_in_cells;
  struct ba0_gc_info *g;

  old_index_in_cells = ba0_cell_index_mark (old_addr, &ba0_old_free);
  if (old_index_in_cells < 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  if (ba0_user_provided_mark.index_in_cells < old_index_in_cells ||
      (ba0_user_provided_mark.index_in_cells == old_index_in_cells &&
          (unsigned ba0_int_p) ba0_user_provided_mark.address <=
          (unsigned ba0_int_p) old_addr))
    {
      g = (struct ba0_gc_info *) ba0_alloc (sizeof (struct ba0_gc_info));
      g->old_index_in_cells = old_index_in_cells;
      g->old_addr = old_addr;
      g->u.size = size;
      g->text = text;
      return 1;
    }
  else
    return 0;
}

/*
  This function is called by garbage2 function. It is thus used at step 4.

  old_addr is the old address of an area.
  If old_addr points below ba0_user_provided_mark, which is the mark provided
  by the user, then old_addr is returned. Otherwise, the next struct
  struct ba0_gc_info * is read. Its new_addr field provides the new address of
  the area. This field is returned.

  The parameter text is used for debugging, to make sure that areas fit.
*/

BA0_DLL void *
ba0_new_addr_gc_info (
    void *old_addr,
    char *text)
{
  struct ba0_gc_info *g;
  ba0_int_p old_index_in_cells;

  old_index_in_cells = ba0_cell_index_mark (old_addr, &ba0_old_free);
  if (old_index_in_cells < 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  if (ba0_user_provided_mark.index_in_cells > old_index_in_cells ||
      (ba0_user_provided_mark.index_in_cells == old_index_in_cells &&
          (unsigned ba0_int_p) ba0_user_provided_mark.address >
          (unsigned ba0_int_p) old_addr))
    return old_addr;

  g = (struct ba0_gc_info *) ba0_alloc_mark (&ba0_current,
      sizeof (struct ba0_gc_info));

  if (text != g->text)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  return g->u.new_addr;
}

/*
 * Implementation of Faug\`ere's garbage collector.
 * 
 * Dots hide addresses of variables pointing to objects described by~$s$.
 * Compacts above~$M$ all the subobjects the addresses of which are above~$M$.
 * Does not move the subobjects the addresses of which are below~$M$.
 * Every memory area not used by the subobjects and above~$M$ is considered
 * as free. The free pointer is updated. The new addresses of the objects
 * are stored in the variables.
 * 
 * It is assumed that all the subobjects lie in the current stack
 * and that the mark~$M$ points inside this stack.
 * Some subobjects can be shared but circular lists are not allowed.
 * Shared subobjects remain shared after garbage collection.
 * Objects do not use more memory after garbage collection than before.
 * 
 * The algorithm is the following.
 *
 * The {\tt garbage1} functions are called.
 * They store in {\tt struct ba0_gc_info} records the addresses 
 * (field {\tt old_addr}) and the sizes of every subobject lying above~$M$. 
 * These records are allocated in the free memory of the current stack. 
 * At the end of this pass, the number~$n$ of the subobjects is known.
 *
 * Allocation of an array of~$n$ pointers to {\tt struct ba0_gc_info}.
 * This array is filled with the addresses of the records
 * created at the former pass then sorted by increasing address of
 * subobject.
 *
 * The free pointer is set in~$M$.
 * The array created at the second pass is used to copy the
 * subobjects in the free memory (just above~$M$). The free pointer
 * is continuously updated. The new addresses of the subobjects are
 * stored in the fields {\tt new_addr}. Remarks.
 *
 * + The order of the subobjects in memory is preserved.
 * One thereby avoids a knapsack problem.
 *
 * + Shared subobjects are easily recognized and not duplicated.
 *
 * + Pointers inside subobjects are incorrect.
 *
 * The {\tt garbage2} functions are called following exactly the
 * same sequence as the {\tt garbage1} ones. They update pointers inside
 * subobjects using the fields {\tt new_addr}, running sequentially
 * over the records created at the first pass (and not the sorted array~!).
 * 
 * Remark. For dynamical data structures (tables, polynomials \dots)
 * all the objects of index between $0$ and $\mbox{\tt ba0_alloc}  - 1$
 * are submitted to garbage collection. Not only the ones between~$0$
 * and $\mbox{\tt size} - 1$.
 */

/*
 * texinfo: ba0_garbage
 * The front-end function for garbage collection.
 */

BA0_DLL void
ba0_garbage (
    char *s,
    struct ba0_mark *M,
    ...)
{
  struct ba0_format *f;
  va_list arg;
  ba0_int_p i, n;

/*
   ba0_user_provided_mark is the mark provided by the user.
   It points to the bottom of the struct ba0_gc_info created at step 1.
   
   ba0_current is a "running" mark on the struct ba0_gc_info created at step 1.
   
   ba0_old_free contains the value of the free pointer when the garbage
   collector is called. 
*/
  ba0_user_provided_mark = *M;
  ba0_record (&ba0_current);
  ba0_record (&ba0_old_free);
  f = ba0_get_format (s);
/*
   step 1
   n receives the number of struct ba0_gc_info created at step 1
*/
  n = 0;
  va_start (arg, M);
  for (i = 0; i < f->linknmb; i++)
    {
      void *objet = *va_arg (arg, void **);
      n += ba0_garbage1_pointer (f->link[i], objet, ba0_isolated);
    }
  if (n > 0)
    {
/*
   step 2
*/
      ba0_tab =
          (struct ba0_gc_info * *) ba0_alloc (sizeof (struct ba0_gc_info *) *
          n);
      ba0_fill_tab (n);
      qsort (ba0_tab, n, sizeof (struct ba0_gc_info *), &ba0_compare_tab_elts);
/*
   step 3
*/
      ba0_restore (&ba0_user_provided_mark);
      ba0_remove_holes_between_areas (n);
/*
   step 4
*/
      va_start (arg, M);
      for (i = 0; i < f->linknmb; i++)
        {
          void **ptr = va_arg (arg, void **);
          *ptr = ba0_garbage2_pointer (f->link[i], *ptr, ba0_isolated);
        }
    }
  va_end (arg);
}

/*
 * Applies the convenient {\tt garbage1} function over $\ast\mbox{\em objet}$
 * the type of which is described by~$s$. This function is only needed
 * to write {\tt garbage1} functions for structures which involve lists,
 * tables, matrices \dots
-*/

BA0_DLL ba0_int_p
ba0_garbage1 (
    char *s,
    void *objet,
    enum ba0_garbage_code code)
{
  struct ba0_format *f;

  f = ba0_get_format (s);
  return ba0_garbage1_pointer (f->link[0], objet, code);
}

/*
 * Applies the convenient {\tt garbage2} function over $\ast\mbox{\em objet}$
 * the type of which is described by~$s$. This function is only needed
 * to write {\tt garbage2} functions for structures which involve lists,
 * tables, matrices \dots
 */

BA0_DLL void *
ba0_garbage2 (
    char *s,
    void *objet,
    enum ba0_garbage_code code)
{
  struct ba0_format *f;

  f = ba0_get_format (s);
  return ba0_garbage2_pointer (f->link[0], objet, code);
}
