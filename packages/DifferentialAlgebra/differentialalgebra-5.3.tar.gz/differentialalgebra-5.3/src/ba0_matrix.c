#include "ba0_exception.h"
#include "ba0_stack.h"
#include "ba0_matrix.h"

/*
 * texinfo: ba0_init_matrix
 * Initialize @var{M} to the empty matrix (constructor).
 */

BA0_DLL void
ba0_init_matrix (
    struct ba0_matrix *M)
{
  M->alloc = 0;
  M->nrow = 0;
  M->ncol = 0;
  M->entry = (void *) 0;
}

/*
 * texinfo: ba0_reset_matrix
 * Set to zero the number of rows and columns of @var{M}.
 */

BA0_DLL void
ba0_reset_matrix (
    struct ba0_matrix *M)
{
  M->nrow = 0;
  M->ncol = 0;
}

/*
 * texinfo: ba0_realloc_matrix
 * If needed, 
 * reallocs @var{M} so that the matrix can contain @math{n \times m} elements.
 * The fields @code{nrow} and @code{ncol} are updated.
 * Existing elements are kept.
 */

BA0_DLL void
ba0_realloc_matrix (
    struct ba0_matrix *M,
    ba0_int_p n,
    ba0_int_p m)
{
  ba0_int_p new_size, old_size;
  void **new_entry;

  new_size = n * m;
  if (new_size > M->alloc)
    {
      new_entry = (void **) ba0_alloc (sizeof (void *) * new_size);
      old_size = M->nrow * M->ncol;
      memcpy (new_entry, M->entry, old_size * sizeof (void *));
      M->entry = new_entry;
      M->alloc = new_size;
      M->nrow = n;
      M->ncol = m;
    }
}

/*
 * texinfo: ba0_realloc2_matrix
 * Variant of @code{ba0_realloc_matrix}.
 * New elements are initialized with the value returned by
 * @var{new_object}.
 */

BA0_DLL void
ba0_realloc2_matrix (
    struct ba0_matrix *M,
    ba0_int_p n,
    ba0_int_p m,
    ba0_new_function *new_object)
{
  ba0_int_p new_size, old_size, i;
  void **new_entry;

  new_size = n * m;
  if (new_size > M->alloc)
    {
      new_entry = (void **) ba0_alloc (sizeof (void *) * new_size);
      old_size = M->nrow * M->ncol;
      memcpy (new_entry, M->entry, old_size * sizeof (void *));
      for (i = old_size; i < new_size; i++)
        new_entry[i] = (*new_object) ();
      M->entry = new_entry;
      M->alloc = new_size;
      M->nrow = n;
      M->ncol = m;
    }
}

/*
 * texinfo: ba0_new_matrix
 * Allocate a new matrix, apply the constructor over it and return
 * the result
 */

BA0_DLL struct ba0_matrix *
ba0_new_matrix (
    void)
{
  struct ba0_matrix *M;

  M = (struct ba0_matrix *) ba0_alloc (sizeof (struct ba0_matrix));
  ba0_init_matrix (M);
  return M;
}

/*
 * texinfo: ba0_set_matrix
 * Copie @var{B} to @var{A}.
 */

BA0_DLL void
ba0_set_matrix (
    struct ba0_matrix *A,
    struct ba0_matrix *B)
{
  ba0_int_p size;

  if (A != B)
    {
      ba0_realloc_matrix (A, B->nrow, B->ncol);
      size = B->nrow * B->ncol;
      memcpy (A->entry, B->entry, size * sizeof (void *));
      A->nrow = B->nrow;
      A->ncol = B->ncol;
    }
}

/*
 * texinfo: ba0_set_matrix2
 * Variant of the above function.
 * Assignments of elements are performed using @var{set_object}.
 */

BA0_DLL void
ba0_set_matrix2 (
    struct ba0_matrix *A,
    struct ba0_matrix *B,
    ba0_new_function *new_object,
    ba0_binary_operation *set_object)
{
  ba0_int_p i, size;

  if (A != B)
    {
      ba0_realloc2_matrix (A, B->nrow, B->ncol, new_object);
      size = B->nrow * B->ncol;
      for (i = 0; i < size; i++)
        (*set_object) (A->entry[i], B->entry[i]);
      A->nrow = B->nrow;
      A->ncol = B->ncol;
    }
}

/*
 * texinfo: ba0_set_matrix_unity
 * Assign the unit matrix of size @math{n \times n} to @var{A}.
 */

BA0_DLL void
ba0_set_matrix_unity (
    struct ba0_matrix *A,
    ba0_int_p n,
    ba0_new_function *new_object,
    ba0_unary_operation *set_object_zero,
    ba0_unary_operation *set_object_one)
{
  ba0_int_p i, j;

  ba0_reset_matrix (A);
  ba0_realloc2_matrix (A, n, n, new_object);
  A->nrow = n;
  A->ncol = n;
  for (i = 0; i < n; i++)
    {
      for (j = 0; j < i; j++)
        (*set_object_zero) (BA0_MAT (A, i, j));
      (*set_object_one) (BA0_MAT (A, i, i));
      for (j = i + 1; j < n; j++)
        (*set_object_zero) (BA0_MAT (A, i, j));
    }
}

/*
 * texinfo: ba0_is_zero_matrix
 * @end deftypefun
 * 
 * @deftypefun bool ba0_is_unity_matrix (struct ba0_matrix * @var{A}, ba0_unary_predicate* @var{is_zero_object}, ba0_unary_predicate* @var{is_one_object})
 */

BA0_DLL bool
ba0_is_zero_matrix (
    struct ba0_matrix *A,
    ba0_unary_predicate *is_zero_object)
{
  ba0_int_p i, size;
  bool zero;

  size = A->nrow * A->ncol;
  zero = true;

  for (i = 0; i < size && zero; i++)
    zero = (*is_zero_object) (A->entry[i]);

  return zero;
}

BA0_DLL bool
ba0_is_unity_matrix (
    struct ba0_matrix *A,
    ba0_unary_predicate *is_zero_object,
    ba0_unary_predicate *is_one_object)
{
  ba0_int_p i, j;
  bool unity;

  unity = true;
  for (i = 0; i < A->nrow && unity; i++)
    for (j = 0; j < A->ncol && unity; j++)
      if (i == j)
        unity = (*is_one_object) (BA0_MAT (A, i, j));
      else
        unity = (*is_zero_object) (BA0_MAT (A, i, j));

  return unity;
}

/*
 * texinfo: ba0_swap_rows_matrix
 * Swap the rows @var{i} and @var{j} of @var{M}.
 * In place function.
 * Exception @code{BA0_ERRALG} is raised if @var{i} or @var{j} are negative
 * or greater than the number of rows of @var{M}.
 */

BA0_DLL void
ba0_swap_rows_matrix (
    struct ba0_matrix *A,
    ba0_int_p i,
    ba0_int_p j)
{
  ba0_int_p k;

  if (i < 0 || i >= A->nrow || j < 0 || j >= A->nrow)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  if (i != j)
    {
      for (k = 0; k < A->ncol; k++)
        {
          BA0_SWAP (void *,
              BA0_MAT (A,
                  i,
                  k),
              BA0_MAT (A,
                  j,
                  k));
        }
    }
}

/*
 * texinfo: ba0_swap_columns_matrix
 * Swap the columns @var{i} and @var{j} of @var{M}.
 * In place function.
 * Exception @code{BA0_ERRALG} is raised if @var{i} or @var{j} are negative
 * or greater than the number of columns of @var{M}.
 */

BA0_DLL void
ba0_swap_columns_matrix (
    struct ba0_matrix *A,
    ba0_int_p i,
    ba0_int_p j)
{
  ba0_int_p k;

  if (i < 0 || i >= A->ncol || j < 0 || j >= A->ncol)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  if (i != j)
    {
      for (k = 0; k < A->nrow; k++)
        {
          BA0_SWAP (void *,
              BA0_MAT (A,
                  k,
                  i),
              BA0_MAT (A,
                  k,
                  j));
        }
    }
}

/*
 * texinfo: ba0_add_matrix
 * Assign @math{A + B} to @var{R}.
 * The @var{add_object} function applies to matrix elements and is
 * supposed to assign the sum of its two last parameters to the first one.
 * Exception @code{BA0_ERRALG} is raised if @var{A} and @var{B} have 
 * incompatible dimensions.
 */

BA0_DLL void
ba0_add_matrix (
    struct ba0_matrix *R,
    struct ba0_matrix *A,
    struct ba0_matrix *B,
    ba0_new_function *new_object,
    ba0_ternary_operation *add_object)
{
  ba0_int_p n, m;
  ba0_int_p i, j;

  if (A->nrow != B->nrow || A->ncol != B->ncol)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  n = A->nrow;
  m = A->ncol;
  ba0_reset_matrix (R);
  ba0_realloc2_matrix (R, n, m, new_object);
  R->nrow = n;
  R->ncol = m;
  for (i = 0; i < n; i++)
    for (j = 0; j < m; j++)
      (*add_object) (BA0_MAT (R, i, j), BA0_MAT (A, i, j), BA0_MAT (B, i, j));
}

/*
 * texinfo: ba0_mul_matrix
 * Assign @math{A \, B} to @var{R}.
 * The functions @var{set_object} and @var{mul_object} are supposed to apply
 * to matrix elements.
 * The @var{set_object} function 
 * is supposed to assign its second argument to the first one.
 * The @var{mul_object} function is
 * supposed to assign the product of its two last parameters to the first one.
 * Exception @code{BA0_ERRALG} is raised if @var{A} and @var{B} have
 * incompatible dimensions.
 */

BA0_DLL void
ba0_mul_matrix (
    struct ba0_matrix *R,
    struct ba0_matrix *A,
    struct ba0_matrix *B,
    ba0_new_function *new_object,
    ba0_unary_operation *set_object_zero,
    ba0_binary_operation *set_object,
    ba0_ternary_operation *add_object,
    ba0_ternary_operation *mul_object)
{
  ba0_int_p i, j, k;
  struct ba0_mark M;
  void *z;

  if (A->ncol != B->nrow)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (A == R || B == R)
    {
      struct ba0_matrix *S;

      ba0_push_another_stack ();
      ba0_record (&M);
      S = ba0_new_matrix ();
      ba0_mul_matrix (S, A, B, new_object, set_object_zero, set_object,
          add_object, mul_object);
      ba0_pull_stack ();
      ba0_set_matrix2 (R, S, new_object, set_object);

      ba0_restore (&M);
      return;
    }

  ba0_reset_matrix (R);
  ba0_realloc2_matrix (R, A->nrow, B->ncol, new_object);
  R->nrow = A->nrow;
  R->ncol = B->ncol;

  ba0_push_another_stack ();
  ba0_record (&M);
  z = (*new_object) ();

  for (i = 0; i < R->nrow; i++)
    {
      for (j = 0; j < R->ncol; j++)
        {
          ba0_pull_stack ();
          (*set_object_zero) (BA0_MAT (R, i, j));
          ba0_push_another_stack ();
          for (k = 0; k < A->ncol; k++)
            {
              (*mul_object) (z, BA0_MAT (A, i, k), BA0_MAT (B, k, j));
              ba0_pull_stack ();
              (*add_object) (BA0_MAT (R, i, j), BA0_MAT (R, i, j), z);
              ba0_push_another_stack ();
            }
        }
    }

  ba0_pull_stack ();
  ba0_restore (&M);
}
