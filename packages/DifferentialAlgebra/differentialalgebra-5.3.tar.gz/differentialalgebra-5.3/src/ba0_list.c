#include "ba0_exception.h"
#include "ba0_stack.h"
#include "ba0_list.h"

/***************************************************************************
 SPLIT-MERGE SORT - IN PLACE MERGE.
 ***************************************************************************/

/* merging two sorted non empty lists */

static struct ba0_list *
merge (
    struct ba0_list *L,
    struct ba0_list *M,
    ba0_cmp_function *f)
{
  struct ba0_list *resultat, *p, *q, *r;

  if ((*f) (L->value, M->value))
    {
      resultat = r = L;
      p = L->next;
      q = M;
    }
  else
    {
      resultat = r = M;
      p = M->next;
      q = L;
    }

/* r = last cons of the resulting list
   p, q, first cons among the ones which still need to be processed
*/

  while (p != (struct ba0_list *) 0 && q != (struct ba0_list *) 0)
    {
      if ((*f) (p->value, q->value))
        {
          r->next = p;
          p = p->next;
        }
      else
        {
          r->next = q;
          q = q->next;
        }
      r = r->next;
    }

  if (p != (struct ba0_list *) 0)
    r->next = p;
  else
    r->next = q;

  return resultat;
}

/*
 * Split and merge in place sort.
 * If f (a,b) = a > b then the list is sorted by decreasing order.
 */

/*
 * texinfo: ba0_sort_list
 * Sort the list in place and returns its head.
 * if @math{f (a,b) \Leftrightarrow a > b} then the list is sorted by
 * increasing order.
 */

BA0_DLL struct ba0_list *
ba0_sort_list (
    struct ba0_list *L,
    ba0_cmp_function *f)
{
  struct ba0_list *L1, *L2, *p, *q, *r;

  if (L == (struct ba0_list *) 0 || L->next == (struct ba0_list *) 0)
    return L;

  L1 = L;
  L2 = L->next;
  p = L1;
  q = L2;
  r = q->next;

/*  Loop invariant
    +---+---+     +---+---+
    |   |   | --> |   |   | --> r (event. NULL)
    +---+---+     +---+---+
        p             q
*/

  for (;;)
    {
      p->next = r;
      if (r == (struct ba0_list *) 0)
        break;
      p = r;
      r = r->next;
      q->next = r;
      if (r == (struct ba0_list *) 0)
        break;
      q = r;
      r = r->next;
    }

  L1 = ba0_sort_list (L1, f);
  L2 = ba0_sort_list (L2, f);

  return merge (L1, L2, f);
}

/* merging two sorted non empty lists */

static struct ba0_list *
merge2 (
    struct ba0_list *L,
    struct ba0_list *M,
    ba0_cmp2_function *f,
    void *data)
{
  struct ba0_list *resultat, *p, *q, *r;

  if ((*f) (L->value, M->value, data))
    {
      resultat = r = L;
      p = L->next;
      q = M;
    }
  else
    {
      resultat = r = M;
      p = M->next;
      q = L;
    }

/* r = last cons of the resulting list
   p, q, first cons among the ones which still need to be processed
*/

  while (p != (struct ba0_list *) 0 && q != (struct ba0_list *) 0)
    {
      if ((*f) (p->value, q->value, data))
        {
          r->next = p;
          p = p->next;
        }
      else
        {
          r->next = q;
          q = q->next;
        }
      r = r->next;
    }

  if (p != (struct ba0_list *) 0)
    r->next = p;
  else
    r->next = q;

  return resultat;
}

/*
 * Split and merge in place sort.
 * If f (a,b) = a > b then the list is sorted by decreasing order.
 */

/*
 * texinfo: ba0_sort2_list
 * ort the list in place and returns its head.
 * if @math{f (a,b,data) \Leftrightarrow a > b} then the list is sorted by
 * increasing order.
 */

BA0_DLL struct ba0_list *
ba0_sort2_list (
    struct ba0_list *L,
    ba0_cmp2_function *f,
    void *data)
{
  struct ba0_list *L1, *L2, *p, *q, *r;

  if (L == (struct ba0_list *) 0 || L->next == (struct ba0_list *) 0)
    return L;

  L1 = L;
  L2 = L->next;
  p = L1;
  q = L2;
  r = q->next;

/*  Loop invariant
    +---+---+     +---+---+
    |   |   | --> |   |   | --> r (event. NULL)
    +---+---+     +---+---+
        p             q
*/

  for (;;)
    {
      p->next = r;
      if (r == (struct ba0_list *) 0)
        break;
      p = r;
      r = r->next;
      q->next = r;
      if (r == (struct ba0_list *) 0)
        break;
      q = r;
      r = r->next;
    }

  L1 = ba0_sort2_list (L1, f, data);
  L2 = ba0_sort2_list (L2, f, data);

  return merge2 (L1, L2, f, data);
}

/*
 * Removes from L the elements not satisfying f
 */

/*
 * texinfo: ba0_select_list
 * Remove from the list the elements which do not satisfy @var{f}.
 * In place function.
 */

BA0_DLL struct ba0_list *
ba0_select_list (
    struct ba0_list *L,
    ba0_unary_predicate *f)
{
  struct ba0_list *Head = L;
  struct ba0_list *prec = (struct ba0_list *) 0;
  struct ba0_list *cour = L;

  while (cour != (struct ba0_list *) 0)
    {
      if ((*f) (cour->value))
        {
          prec = cour;
          cour = cour->next;
        }
      else if (prec == (struct ba0_list *) 0)
        Head = cour = cour->next;
      else
        prec->next = cour = cour->next;
    }

  return Head;
}

/*
 * Removes from~$L$ the elements satisfying~$f$.
 */

/*
 * texinfo: ba0_delete_list
 * Remove from the list the elements which satisfy @var{f}.
 * In place function.
 */

BA0_DLL struct ba0_list *
ba0_delete_list (
    struct ba0_list *L,
    ba0_unary_predicate *f)
{
  struct ba0_list *Head = L;
  struct ba0_list *prec = (struct ba0_list *) 0;
  struct ba0_list *cour = L;

  while (cour != (struct ba0_list *) 0)
    {
      if (!(*f) (cour->value))
        {
          prec = cour;
          cour = cour->next;
        }
      else if (prec == (struct ba0_list *) 0)
        Head = cour = cour->next;
      else
        prec->next = cour = cour->next;
    }

  return Head;
}

/*
 * If f (a, b) = a > b and L is sorted by decreasing order then p
 * is inserted in L at the right place.
 */

/*
 * texinfo: ba0_insert_list
 * If @math{f (a, b) = a > b} and the list i sorted in decreasing order then
 * @var{p} is inserted at the right place.
 */

BA0_DLL struct ba0_list *
ba0_insert_list (
    void *p,
    struct ba0_list *L,
    ba0_cmp_function *f)
{
  struct ba0_list *prec, *cour;

  if (L == (struct ba0_list *) 0 || (*f) (p, L->value))
    return ba0_cons_list (p, L);

  prec = L;
  cour = prec->next;
  while (cour != (struct ba0_list *) 0 && !(*f) (p, cour->value))
    {
      prec = cour;
      cour = cour->next;
    }
  prec->next = ba0_cons_list (p, cour);
  return L;
}

/*
 * If f (a, b, data) = a > b and L is sorted by decreasing order then p
 * is inserted in L at the right place.
 */

/*
 * texinfo: ba0_insert2_list
 * If @math{f (a, b,data) = a > b} and the list i sorted in decreasing order then
 * @var{p} is inserted at the right place.
 */

BA0_DLL struct ba0_list *
ba0_insert2_list (
    void *p,
    struct ba0_list *L,
    ba0_cmp2_function *f,
    void *data)
{
  struct ba0_list *prec, *cour;

  if (L == (struct ba0_list *) 0 || (*f) (p, L->value, data))
    return ba0_cons_list (p, L);

  prec = L;
  cour = prec->next;
  while (cour != (struct ba0_list *) 0 && !(*f) (p, cour->value, data))
    {
      prec = cour;
      cour = cour->next;
    }
  prec->next = ba0_cons_list (p, cour);
  return L;
}

/***************************************************************************
 SOME BASIC LIST FUNCTIONS
 ***************************************************************************/

/*
 * texinfo: ba0_member_list
 * Return @code{true} is @var{p} belongs to @var{L}.
 */

BA0_DLL bool
ba0_member_list (
    void *p,
    struct ba0_list *L)
{
  while (L != (struct ba0_list *) 0)
    {
      if (L->value == p)
        return true;
      L = L->next;
    }
  return false;
}

/*
 * texinfo: ba0_last_list
 * Return the last element of @var{L}.
 * Exception @code{BA0_ERRNIL} is raised if @var{L} is empty.
 */

BA0_DLL void *
ba0_last_list (
    struct ba0_list *L)
{
  if (L == (struct ba0_list *) 0)
    BA0_RAISE_EXCEPTION (BA0_ERRNIL);
  while (L->next != (struct ba0_list *) 0)
    L = L->next;
  return L->value;
}

/*
 * Returns L minus its last element. Error BA0_ERRNIL if L is empty.
 */

/*
 * texinfo: ba0_butlast_list
 * Remove the last element from @var{L}.
 * In place function.
 * Exception @code{BA0_ERRNIL} is raised if @var{L} is empty.
 */

BA0_DLL struct ba0_list *
ba0_butlast_list (
    struct ba0_list *L)
{
  struct ba0_list *prec, *cour;

  if (L == (struct ba0_list *) 0)
    BA0_RAISE_EXCEPTION (BA0_ERRNIL);
  if (L->next == (struct ba0_list *) 0)
    return (struct ba0_list *) 0;
  prec = L;
  cour = L->next;
  while (cour->next != (struct ba0_list *) 0)
    {
      prec = cour;
      cour = cour->next;
    }
  prec->next = (struct ba0_list *) 0;
  return L;
}

/*
 * Returns a copy of L.  Only the ``cons'' are duplicated.
 */

/*
 * texinfo: ba0_copy_list
 * Return a copy of @var{L}.
 */

BA0_DLL struct ba0_list *
ba0_copy_list (
    struct ba0_list *L)
{
  struct ba0_list *p, *q;

  if (L == (struct ba0_list *) 0)
    return L;
  p = q = (struct ba0_list *) ba0_alloc (sizeof (struct ba0_list));
  q->value = L->value;
  L = L->next;
  while (L != (struct ba0_list *) 0)
    {
      q->next = (struct ba0_list *) ba0_alloc (sizeof (struct ba0_list));
      q = q->next;
      q->value = L->value;
      L = L->next;
    }
  q->next = (struct ba0_list *) 0;
  return p;
}

/*
 * Inserts v at the beginning of L.
 */

/*
 * texinfo: ba0_cons_list
 * Insert @var{v} at the beginning of @var{L}.
 */

BA0_DLL struct ba0_list *
ba0_cons_list (
    void *v,
    struct ba0_list *L)
{
  struct ba0_list *p = (struct ba0_list *) ba0_alloc (sizeof (struct ba0_list));
  p->value = v;
  p->next = L;
  return p;
}

/*
 * Appends v at the end of L. L is modified.
 */

/*
 * texinfo: ba0_endcons_list
 * Append @var{v} at the end of the list.
 * In place function.
 */

BA0_DLL struct ba0_list *
ba0_endcons_list (
    void *v,
    struct ba0_list *L)
{
  struct ba0_list *p = (struct ba0_list *) ba0_alloc (sizeof (struct ba0_list));
  struct ba0_list *q;

  p->value = v;
  p->next = (struct ba0_list *) 0;
  if (L == (struct ba0_list *) 0)
    return p;
  for (q = L; q->next != (struct ba0_list *) 0; q = q->next);
  q->next = p;
  return L;
}

/*
 * Reverts L. L is modified.
 */

/*
 * texinfo: ba0_reverse_list
 * Return and returns @var{L}. In place function.
 */

BA0_DLL struct ba0_list *
ba0_reverse_list (
    struct ba0_list *L)
{
  struct ba0_list *prec, *cour, *succ;

  if (L == (struct ba0_list *) 0)
    return L;

  prec = (struct ba0_list *) 0;
  cour = L;
  while (cour != (struct ba0_list *) 0)
    {
      succ = cour->next;
      cour->next = prec;
      prec = cour;
      cour = succ;
    }
  return prec;
}

/*
 * Appends L2 to L1. L1 is modified.
 */

/*
 * texinfo: ba0_concat_list
 * Append @var{L2} to @var{L1}. In place function.
 */

BA0_DLL struct ba0_list *
ba0_concat_list (
    struct ba0_list *L1,
    struct ba0_list *L2)
{
  struct ba0_list *p;

  if (L1 == (struct ba0_list *) 0)
    return L2;
  for (p = L1; p->next != (struct ba0_list *) 0; p = p->next);
  p->next = L2;
  return L1;
}

/* 
 * Returns the number of elements of L. 
 */

/*
 * texinfo: ba0_length_list
 * Return the number of elements of @var{L}.
 */

BA0_DLL ba0_int_p
ba0_length_list (
    struct ba0_list *L)
{
  ba0_int_p i;

  for (i = 0; L != (struct ba0_list *) 0; L = L->next)
    i++;
  return i;
}

/* 
 * Returns L[i]. Indices start at zero.
 */

/*
 * texinfo: ba0_ith_list
 * Return the @var{i}th element of the list.
 * The first one has index zero.
 * Exception @code{BA0_ERRNIL} is raised if @var{i} exceeds the number
 * of elements of @var{L}.
 */

BA0_DLL void *
ba0_ith_list (
    struct ba0_list *L,
    ba0_int_p i)
{
  while (i != 0)
    {
      if (L == (struct ba0_list *) 0)
        BA0_RAISE_EXCEPTION (BA0_ERRNIL);
      L = L->next;
      i -= 1;
    }
  return L->value;
}

/*
 * Returns [f(L[0]), ..., f(L[n])] where n = |L|-1.
 */

/*
 * texinfo: ba0_map_list
 * Denote the list @math{(a_0,\ldots,a_n)}.
 * Returns the list @math{(f(a_0),\ldots,f(a_n))}.
 * In place function.
 */

BA0_DLL struct ba0_list *
ba0_map_list (
    ba0_unary_function *f,
    struct ba0_list *L)
{
  struct ba0_list *p;

  for (p = L; p != (struct ba0_list *) 0; p = p->next)
    p->value = (*f) (p->value);
  return L;
}

/*
 * Performs a rotation on L [0 .. k] so that L[k] appears at the head of L.
 * Indices start at 0.
 */

/*
 * texinfo: ba0_move_to_head_list
 * Perform a rotation on the @math{i+1} first elements of @var{L} so that
 * the former @var{i}th element of  @var{L} occurs at the beginning of @var{L}.
 * In place function.
 * Exception @code{BA0_ERRNIL} is raised if @var{L} is empty.
 */

BA0_DLL void
ba0_move_to_head_list (
    struct ba0_list *L,
    ba0_int_p k)
{
  struct ba0_list *M;
  void *v;
  ba0_int_p i;

  M = L;
  i = 0;
  while (i < k && M != (struct ba0_list *) 0)
    {
      M = M->next;
      i += 1;
    }
  if (M == (struct ba0_list *) 0)
    BA0_RAISE_EXCEPTION (BA0_ERRNIL);
  else if (L != M)
    {
      v = M->value;
      while (L != M)
        {
          BA0_SWAP (void *,
              v,
              L->value);
          L = L->next;
        }
      L->value = v;
    }
}
