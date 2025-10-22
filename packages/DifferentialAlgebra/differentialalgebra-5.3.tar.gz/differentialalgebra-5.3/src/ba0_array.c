#include "ba0_stack.h"
#include "ba0_exception.h"
#include "ba0_array.h"

/*
 * texinfo: ba0_init_array
 * Initialize @var{A} to the empty array (constructor).
 */

BA0_DLL void
ba0_init_array (
    struct ba0_array *A)
{
  A->alloc = 0;
  A->size = 0;
  A->tab = (char *) 0;
  A->sizelt = 0;
}

/*
 * texinfo: ba0_reset_array
 * Set to zero the number of used elements of @var{A}.
 */

BA0_DLL void
ba0_reset_array (
    struct ba0_array *A)
{
  A->size = 0;
}

BA0_DLL struct ba0_array *
ba0_new_array (
    void)
{
  struct ba0_array *A;

  A = (struct ba0_array *) ba0_alloc (sizeof (struct ba0_array));
  ba0_init_array (A);
  return A;
}

/*
 * texinfo: ba0_realloc_array
 * Realloc the array if needed so that it can receive at least
 * @var{n} elements of size @var{sizelt}. 
 * Exception @code{BA0_ERRALG} is raised if @var{sizelt} is zero.
 */

BA0_DLL void
ba0_realloc_array (
    struct ba0_array *A,
    ba0_int_p n,
    ba0_int_p sizelt)
{
  char *tab;

  if (sizelt == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (n * sizelt > A->alloc * A->sizelt)
    {
      tab = (char *) ba0_alloc (sizelt * n);
      memcpy (tab, A->tab, A->size * sizelt);
      A->tab = tab;
      A->alloc = n;
    }
  else
    A->alloc = (A->alloc * A->sizelt) / sizelt;
  A->sizelt = sizelt;
}

/*
 * texinfo: ba0_realloc2_array
 * Variant of the above function. 
 * Only the newly allocated objects are initialized using @var{init_objet}. 
 * Exception @code{BA0_ERRALG} is raised if @var{sizelt} is zero.
 */

BA0_DLL void
ba0_realloc2_array (
    struct ba0_array *A,
    ba0_int_p n,
    ba0_int_p sizelt,
    ba0_init_function *init_objet)
{
  char *tab;
  ba0_int_p i;

  if (sizelt == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (n * sizelt > A->alloc * A->sizelt)
    {
      tab = (char *) ba0_alloc (sizelt * n);
      memcpy (tab, A->tab, A->size * sizelt);
      for (i = A->size; i < n; i++)
        (*init_objet) (tab + i * sizelt);
      A->tab = tab;
      A->alloc = n;
    }
  else
    A->alloc = (A->alloc * A->sizelt) / sizelt;
  A->sizelt = sizelt;
}

/*
 * texinfo: ba0_delete_array
 * Remove the @var{i}th element of @var{A}.
 * Exception @code{BA0_ERRALG} is raised if @var{i} is greater than
 * the number of used elements of @var{A}.
 */

BA0_DLL void
ba0_delete_array (
    struct ba0_array *A,
    ba0_int_p i)
{
  struct ba0_mark M;
  char *x;

  if (i == A->size)
    A->size--;
  else if (i < A->size)
    {
      ba0_record (&M);
      x = (char *) ba0_alloc (A->sizelt);
      memcpy (x, A->tab + i * A->sizelt, A->sizelt);
      memmove (A->tab + i * A->sizelt, A->tab + (i + 1) * A->sizelt,
          (A->size - i - 1) * A->sizelt);
      memcpy (A->tab + (A->size - 1) * A->sizelt, x, A->sizelt);
      A->size--;
      ba0_restore (&M);
    }
  else
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
}

/*
 * texinfo: ba0_reverse_array
 * Assign to @var{A} the array @var{U} with elements in reverse order.
 */

BA0_DLL void
ba0_reverse_array (
    struct ba0_array *A,
    struct ba0_array *U)
{
  struct ba0_mark M;
  ba0_int_p i, j;
  char *x;

  if (U->sizelt == 0)
    ba0_reset_array (A);
  else if (A == U)
    {
      ba0_record (&M);
      x = (char *) ba0_alloc (A->sizelt);
      for (i = 0, j = A->size - 1; i < j; i++, j--)
        {
          memcpy (x, A->tab + i * A->sizelt, A->sizelt);
          memcpy (A->tab + i * A->sizelt, A->tab + j * A->sizelt, A->sizelt);
          memcpy (A->tab + j * A->sizelt, x, A->sizelt);
        }
      ba0_restore (&M);
    }
  else
    {
      ba0_reset_array (A);
      ba0_realloc_array (A, U->size, U->sizelt);
      A->size = U->size;
      for (i = 0, j = U->size - 1; j >= 0; i++, j--)
        memcpy (A->tab + i * A->sizelt, U->tab + j * A->sizelt, A->sizelt);
    }
}

/*
 * texinfo: ba0_concat_array
 * 		(struct ba0_array * @var{A}, struct ba0_array * @var{U}, struct ba0_array * @var{V})
 * Assigns to @var{A} the result of the concatenation of @var{U} and @var{V}.
 * Exception @code{BA0_ERRALG} is raised  if
 * @var{U} and @var{V} contain element of different sizes.
 */

BA0_DLL void
ba0_concat_array (
    struct ba0_array *A,
    struct ba0_array *U,
    struct ba0_array *V)
{
  if (U->sizelt != V->sizelt)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (U->sizelt == 0)
    ba0_reset_array (A);
  else
    {
      ba0_realloc_array (A, U->size + V->size, U->sizelt);
      memmove (A->tab + U->size * U->sizelt, V->tab, U->sizelt * V->size);
      if (A != U)
        memmove (A->tab, U->tab, U->sizelt * U->size);
      A->size = U->size + V->size;
    }
}

/*
 * texinfo: ba0_set_array
 * Assign @var{U} to @var{A}.
 */

BA0_DLL void
ba0_set_array (
    struct ba0_array *A,
    struct ba0_array *U)
{
  if (U->sizelt == 0)
    ba0_reset_array (A);
  else if (A != U)
    {
      A->size = 0;
      ba0_realloc_array (A, U->size, U->sizelt);
      memcpy (A->tab, U->tab, U->size * U->sizelt);
      A->size = U->size;
    }
}
