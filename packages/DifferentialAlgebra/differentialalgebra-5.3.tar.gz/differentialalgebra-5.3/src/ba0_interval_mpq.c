#include "ba0_interval_mpq.h"
#include "ba0_stack.h"
#include "ba0_exception.h"
#include "ba0_basic_io.h"
#include "ba0_analex.h"
#include "ba0_scanf.h"
#include "ba0_printf.h"
#include "ba0_garbage.h"
#include "ba0_exception.h"
#include "ba0_double.h"

static ba0__mpq_struct *
maxq (
    ba0_mpq_t a,
    ba0_mpq_t b)
{
  return ba0_mpq_cmp (a, b) < 0 ? (ba0__mpq_struct *) b : (ba0__mpq_struct *) a;
}

static ba0__mpq_struct *
minq (
    ba0_mpq_t a,
    ba0_mpq_t b)
{
  return ba0_mpq_cmp (a, b) < 0 ? (ba0__mpq_struct *) a : (ba0__mpq_struct *) b;
}

/*
 * texinfo: ba0_domain_interval_mpq
 * Return @code{true}.
 */

BA0_DLL bool
ba0_domain_interval_mpq (
    void)
{
  return true;
}

/*
 * texinfo: ba0_init_interval_mpq
 * Initialize @var{R} to the empty interval (constructor).
 */

BA0_DLL void
ba0_init_interval_mpq (
    struct ba0_interval_mpq *R)
{
  ba0_mpq_init (R->a);
  ba0_mpq_init (R->b);
  R->type = ba0_empty_interval;
}

/*
 * texinfo: ba0_new_interval_mpq
 * Allocate an interval, initialize it and return it.
 */

BA0_DLL struct ba0_interval_mpq *
ba0_new_interval_mpq (
    void)
{
  struct ba0_interval_mpq *R;

  R = (struct ba0_interval_mpq *) ba0_alloc (sizeof (struct ba0_interval_mpq));
  ba0_init_interval_mpq (R);
  return R;
}

/*
 * texinfo: ba0_set_interval_mpq_si
 * Assign the closed interval @var{n} to @var{I}.
 */

BA0_DLL void
ba0_set_interval_mpq_si (
    struct ba0_interval_mpq *I,
    ba0_int_p n)
{
  I->type = ba0_closed_interval;
  ba0_mpq_set_si (I->a, n);
  ba0_mpq_set_si (I->b, n);
}

/*
 * texinfo: ba0_set_interval_mpq_ui
 * Assign @var{n} to @var{I}.
 */

BA0_DLL void
ba0_set_interval_mpq_ui (
    struct ba0_interval_mpq *I,
    unsigned ba0_int_p n)
{
  I->type = ba0_closed_interval;
  ba0_mpq_set_ui (I->a, n);
  ba0_mpq_set_ui (I->b, n);
}

/*
 * texinfo: ba0_set_interval_mpq_double
 * Assign @var{d} to @var{I}.
 */

BA0_DLL void
ba0_set_interval_mpq_double (
    struct ba0_interval_mpq *I,
    double d)
{
  I->type = ba0_closed_interval;
  ba0_mpq_set_d (I->a, d);
  ba0_mpq_set_d (I->b, d);
}

/*
 * texinfo: ba0_set_interval_mpq_mpq
 * Assign the interval @math{(a,b)} to @var{I}.
 * The interval is closed if the two bounds are equal, else it is open.
 */

BA0_DLL void
ba0_set_interval_mpq_mpq (
    struct ba0_interval_mpq *I,
    ba0_mpq_t a,
    ba0_mpq_t b)
{
  if (ba0_mpq_cmp (a, b) == 0)
    ba0_set_interval_mpq_type_mpq (I, ba0_closed_interval, a, a);
  else
    ba0_set_interval_mpq_type_mpq (I, ba0_open_interval, a, b);
}

/*
 * texinfo: ba0_set_interval_mpq_type_mpq
 * Assign the interval @math{(a,b)}, of type @var{type}, to @var{I}.
 * Depending on @var{type}, some of the bounds may be irrelevant.
 * If the interval is closed, then the two bounds must be equal.
 * If it is open, then the lower bound must be strictly less than the upper one.
 */

BA0_DLL void
ba0_set_interval_mpq_type_mpq (
    struct ba0_interval_mpq *I,
    enum ba0_typeof_interval type,
    ba0_mpq_t a,
    ba0_mpq_t b)
{
  switch (type)
    {
    case ba0_closed_interval:
      if (a != b)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
      ba0_mpq_set (I->a, a);
      ba0_mpq_set (I->b, a);
      break;
    case ba0_open_interval:
      if (ba0_mpq_cmp (a, b) >= 0)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
      ba0_mpq_set (I->a, a);
      ba0_mpq_set (I->b, b);
      break;
    case ba0_left_infinite_interval:
      ba0_mpq_set (I->b, b);
      break;
    case ba0_right_infinite_interval:
      ba0_mpq_set (I->a, a);
      break;
    case ba0_infinite_interval:
      break;
    case ba0_empty_interval:
      break;
    }
  I->type = type;
}

/*
 * texinfo: ba0_set_interval_mpq
 * Assign @var{J} to @var{I}.
 */

BA0_DLL void
ba0_set_interval_mpq (
    struct ba0_interval_mpq *I,
    struct ba0_interval_mpq *J)
{
  if (I != J)
    {
      ba0_mpq_set (I->a, J->a);
      ba0_mpq_set (I->b, J->b);
      I->type = J->type;
    }
}

/*
 * texinfo: ba0_is_empty_interval_mpq
 * Return @code{true} if @var{I} is empty, else @code{false}.
 */

BA0_DLL bool
ba0_is_empty_interval_mpq (
    struct ba0_interval_mpq *I)
{
  return I->type == ba0_empty_interval;
}

/*
 * texinfo: ba0_is_unbounded_interval_mpq
 * Return @code{true} if, at least, one of the bounds @var{I} is infinite.
 */

BA0_DLL bool
ba0_is_unbounded_interval_mpq (
    struct ba0_interval_mpq *I)
{
  return I->type == ba0_infinite_interval ||
      I->type == ba0_left_infinite_interval ||
      I->type == ba0_right_infinite_interval;
}

/*
 * texinfo: ba0_is_closed_interval_mpq
 * Return @code{true} if @var{I} is closed.
 */

BA0_DLL bool
ba0_is_closed_interval_mpq (
    struct ba0_interval_mpq *I)
{
  return I->type == ba0_closed_interval;
}

/*
 * texinfo: ba0_is_open_interval_mpq
 * Return @code{true} if @var{I} is open.
 */

BA0_DLL bool
ba0_is_open_interval_mpq (
    struct ba0_interval_mpq *I)
{
  return I->type != ba0_closed_interval && I->type != ba0_empty_interval;
}

/*
 * texinfo: ba0_is_zero_interval_mpq
 * Return @code{true} if @var{I} is the closed interval @math{0}.
 */

BA0_DLL bool
ba0_is_zero_interval_mpq (
    struct ba0_interval_mpq *I)
{
  return I->type == ba0_closed_interval && ba0_mpq_sgn (I->a) == 0;
}

/*
 * texinfo: ba0_is_one_interval_mpq
 * Return @code{true} if @var{I} is the closed interval @math{1}.
 */

BA0_DLL bool
ba0_is_one_interval_mpq (
    struct ba0_interval_mpq *I)
{
  return I->type == ba0_closed_interval && ba0_mpq_cmp_si (I->a, 1, 1) == 0;
}

/*
 * texinfo: ba0_are_equal_interval_mpq
 * Return @code{true} if @var{I} and @var{J} are equal.
 */

BA0_DLL bool
ba0_are_equal_interval_mpq (
    struct ba0_interval_mpq *I,
    struct ba0_interval_mpq *J)
{
  bool b = false;

  if (I->type != J->type)
    return false;
  switch (I->type)
    {
    case ba0_closed_interval:
      b = ba0_mpq_cmp (I->a, J->a) == 0;
      break;
    case ba0_open_interval:
      b = ba0_mpq_cmp (I->a, J->a) == 0 && ba0_mpq_cmp (I->b, J->b) == 0;
      break;
    case ba0_left_infinite_interval:
      b = ba0_mpq_cmp (I->b, J->b) == 0;
      break;
    case ba0_right_infinite_interval:
      b = ba0_mpq_cmp (I->a, J->a) == 0;
      break;
    case ba0_infinite_interval:
      b = true;
      break;
    case ba0_empty_interval:
      b = true;
      break;
    }
  return b;
}

/*
 * texinfo: ba0_contains_zero_interval_mpq
 * Return @code{true} if @var{I} contains @math{0}.
 */

BA0_DLL bool
ba0_contains_zero_interval_mpq (
    struct ba0_interval_mpq *I)
{
  bool b = false;

  switch (I->type)
    {
    case ba0_closed_interval:
      b = ba0_mpq_sgn (I->a) == 0;
      break;
    case ba0_open_interval:
      b = ba0_mpq_sgn (I->a) < 0 && ba0_mpq_sgn (I->b) > 0;
      break;
    case ba0_left_infinite_interval:
      b = ba0_mpq_cmp (I->b, I->b) > 0;
      break;
    case ba0_right_infinite_interval:
      b = ba0_mpq_cmp (I->a, I->a) < 0;
      break;
    case ba0_infinite_interval:
      b = true;
      break;
    case ba0_empty_interval:
      b = false;
      break;
    }
  return b;
}

/*
 * texinfo: ba0_is_positive_interval_mpq
 * Return @code{true} if @var{I} contains positive numbers only.
 */

BA0_DLL bool
ba0_is_positive_interval_mpq (
    struct ba0_interval_mpq *I)
{
  bool b = false;

  switch (I->type)
    {
    case ba0_closed_interval:
      b = ba0_mpq_sgn (I->a) > 0;
      break;
    case ba0_open_interval:
      b = ba0_mpq_sgn (I->a) >= 0;
      break;
    case ba0_left_infinite_interval:
      b = false;
      break;
    case ba0_right_infinite_interval:
      b = ba0_mpq_cmp (I->a, I->a) >= 0;
      break;
    case ba0_infinite_interval:
      b = false;
      break;
    case ba0_empty_interval:
      b = false;
      break;
    }
  return b;
}

/*
 * texinfo: ba0_is_nonnegative_interval_mpq
 * Return @code{true} if @var{I} contains nonnegative numbers only.
 */

BA0_DLL bool
ba0_is_nonnegative_interval_mpq (
    struct ba0_interval_mpq *I)
{
  bool b = false;

  switch (I->type)
    {
    case ba0_closed_interval:
      b = ba0_mpq_sgn (I->a) >= 0;
      break;
    case ba0_open_interval:
      b = ba0_mpq_sgn (I->a) >= 0;
      break;
    case ba0_left_infinite_interval:
      b = false;
      break;
    case ba0_right_infinite_interval:
      b = ba0_mpq_cmp (I->a, I->a) >= 0;
      break;
    case ba0_infinite_interval:
      b = false;
      break;
    case ba0_empty_interval:
      b = false;
      break;
    }
  return b;
}

/*
 * texinfo: ba0_is_negative_interval_mpq
 * Return @code{true} if @var{I} contains negative numbers only.
 */

BA0_DLL bool
ba0_is_negative_interval_mpq (
    struct ba0_interval_mpq *I)
{
  bool b = false;

  switch (I->type)
    {
    case ba0_closed_interval:
      b = ba0_mpq_sgn (I->a) < 0;
      break;
    case ba0_open_interval:
      b = ba0_mpq_sgn (I->b) <= 0;
      break;
    case ba0_left_infinite_interval:
      b = ba0_mpq_sgn (I->b) <= 0;
      break;
    case ba0_right_infinite_interval:
      b = false;
      break;
    case ba0_infinite_interval:
      b = false;
      break;
    case ba0_empty_interval:
      b = false;
      break;
    }
  return b;
}

/*
 * texinfo: ba0_is_nonpositive_interval_mpq
 * Return @code{true} if @var{I} contains nonpositive numbers only.
 */

BA0_DLL bool
ba0_is_nonpositive_interval_mpq (
    struct ba0_interval_mpq *I)
{
  bool b = false;

  switch (I->type)
    {
    case ba0_closed_interval:
      b = ba0_mpq_sgn (I->a) <= 0;
      break;
    case ba0_open_interval:
      b = ba0_mpq_sgn (I->b) <= 0;
      break;
    case ba0_left_infinite_interval:
      b = ba0_mpq_sgn (I->b) <= 0;
      break;
    case ba0_right_infinite_interval:
      b = false;
      break;
    case ba0_infinite_interval:
      b = false;
      break;
    case ba0_empty_interval:
      b = false;
      break;
    }
  return b;
}

/*
 * texinfo: ba0_is_less_interval_mpq
 * Return @code{true} if all the elements of @var{X} are less than all
 * the elements of @var{Y}. 
 */

BA0_DLL bool
ba0_is_less_interval_mpq (
    struct ba0_interval_mpq *X,
    struct ba0_interval_mpq *Y)
{
  if (X->type != ba0_closed_interval && X->type != ba0_open_interval)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);
  if (Y->type != ba0_closed_interval && Y->type != ba0_open_interval)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  if (ba0_mpq_cmp (X->b, Y->a) < 0)
    return true;
  else if (ba0_mpq_cmp (X->b, Y->a) == 0)
    return ba0_is_open_interval_mpq (X) || ba0_is_open_interval_mpq (Y);
  else
    return false;
}

/*
 * texinfo: ba0_are_disjoint_interval_mpq
 * Return @code{true} if the intersection of @var{X} and @var{Y} is empty.
 */

BA0_DLL bool
ba0_are_disjoint_interval_mpq (
    struct ba0_interval_mpq *X,
    struct ba0_interval_mpq *Y)
{
  if (ba0_is_empty_interval_mpq (X) || ba0_is_empty_interval_mpq (Y))
    return true;
  else if (X->type == ba0_infinite_interval || Y->type == ba0_infinite_interval)
    return false;
  else if (X->type == ba0_left_infinite_interval)
    {
      if (Y->type == ba0_left_infinite_interval)
        return false;
      else
/*
 * X = [-inf,         Xb]
 * Y =                     [Ya, Yb]
 */
        return ba0_mpq_cmp (X->b, Y->a) <= 0;
    }
  else if (X->type == ba0_right_infinite_interval)
    {
      if (Y->type == ba0_right_infinite_interval)
        return false;
      else
/*
 * X =             [Xa,          inf]
 * Y =   [Ya, Yb]
 */
        return ba0_mpq_cmp (X->a, Y->b) >= 0;
    }
  else if (Y->type == ba0_left_infinite_interval)
/*
 *                       [Xa, Xb]
 * Y = [-inf,        Yb]
 */
    return ba0_mpq_cmp (Y->b, X->a) <= 0;
  else if (Y->type == ba0_right_infinite_interval)
/*
 * X =    [Xa, Xb]
 * Y =                   [Ya,                inf]
 */
    return ba0_mpq_cmp (Y->a, X->b) >= 0;
  else if (X->type == ba0_closed_interval && Y->type == ba0_closed_interval)
    return ba0_mpq_cmp (X->a, Y->a) != 0;
  else if (ba0_mpq_cmp (X->a, Y->a) < 0)
    return ba0_mpq_cmp (X->b, Y->a) <= 0;
  else if (ba0_mpq_cmp (Y->a, X->a) < 0)
    return ba0_mpq_cmp (Y->b, X->a) <= 0;
  else
    return false;
}

/*
 * texinfo: ba0_intersect_interval_mpq
 * Assign the intersection of @var{X} and @var{Y} to @var{I}.
 */

BA0_DLL void
ba0_intersect_interval_mpq (
    struct ba0_interval_mpq *I,
    struct ba0_interval_mpq *X,
    struct ba0_interval_mpq *Y)
{
  if (X->type == ba0_empty_interval || Y->type == ba0_empty_interval)
    ba0_set_interval_mpq_type_mpq
        (I, ba0_empty_interval, (ba0__mpq_struct *) 0, (ba0__mpq_struct *) 0);
  else if (X->type == ba0_infinite_interval)
    {
      if (I != Y)
        ba0_set_interval_mpq (I, Y);
    }
  else if (Y->type == ba0_infinite_interval)
    {
      if (I != X)
        ba0_set_interval_mpq (I, X);
    }
  else if (X->type == ba0_left_infinite_interval)
    {
      if (Y->type == ba0_left_infinite_interval)
/*
 * X = [-inf, Xb]
 * Y = [-inf, Yb]
 */
        ba0_set_interval_mpq_type_mpq
            (I, ba0_left_infinite_interval,
            (ba0__mpq_struct *) 0, minq (X->b, Y->b));
      else if (ba0_mpq_cmp (X->b, Y->a) > 0)
/*
 * X = [-inf,                    Xb]
 * Y =           [Ya,            Yb]
 */
        ba0_set_interval_mpq_type_mpq
            (I, ba0_open_interval, Y->a, minq (X->b, Y->b));
      else
/*
 * X = [-inf,                    Xb]
 * Y =                                 [Ya, Yb]
 */
        ba0_set_interval_mpq_type_mpq
            (I, ba0_empty_interval, (ba0__mpq_struct *) 0,
            (ba0__mpq_struct *) 0);
    }
  else if (X->type == ba0_right_infinite_interval)
    {
      if (Y->type == ba0_right_infinite_interval)
/*
 * X =            [Xa, inf]
 * Y =            [Ya, inf]
 */
        ba0_set_interval_mpq_type_mpq
            (I, ba0_right_infinite_interval,
            maxq (X->a, Y->a), (ba0__mpq_struct *) 0);
      else if (ba0_mpq_cmp (X->a, Y->b) < 0)
/*
 * X =            [Xa,                   inf]
 * Y =            [Ya,     Yb]
 */
        ba0_set_interval_mpq_type_mpq
            (I, ba0_open_interval, minq (X->a, Y->a), Y->b);
      else
/*          
 * X =            [Xa,                   inf]
 * Y =  [Ya, Yb]
 */
        ba0_set_interval_mpq_type_mpq
            (I, ba0_empty_interval, (ba0__mpq_struct *) 0,
            (ba0__mpq_struct *) 0);
    }
  else if (Y->type == ba0_left_infinite_interval)
    {
      if (ba0_mpq_cmp (Y->b, X->a) > 0)
/*
 * X =           [Xa,       Xb]
 * Y = [-inf,               Yb]
 */
        ba0_set_interval_mpq_type_mpq
            (I, ba0_open_interval, X->a, minq (X->b, Y->b));
      else
/*
 * X =                             [Xa,       Xb]
 * Y = [-inf,               Yb]
 */

        ba0_set_interval_mpq_type_mpq
            (I, ba0_empty_interval, (ba0__mpq_struct *) 0,
            (ba0__mpq_struct *) 0);
    }
  else if (Y->type == ba0_right_infinite_interval)
    {
      if (ba0_mpq_cmp (Y->a, X->b) < 0)
/*
 * X =                      [Xa,       Xb]
 * Y =                      [Ya,               inf]
 */
        ba0_set_interval_mpq_type_mpq
            (I, ba0_open_interval, maxq (X->a, Y->a), X->b);
      else
/*
 * X =   [Xa,       Xb]
 * Y =                      [Ya,               inf]
 */
        ba0_set_interval_mpq_type_mpq
            (I, ba0_empty_interval, (ba0__mpq_struct *) 0,
            (ba0__mpq_struct *) 0);
    }
  else
    ba0_set_interval_mpq_mpq (I, maxq (X->a, Y->a), minq (X->b, Y->b));
}

/*
 * texinfo: ba0_member_interval_mpq
 * Return @code{true} if @var{q} belongs to @var{X}.
 */

BA0_DLL bool
ba0_member_interval_mpq (
    ba0_mpq_t q,
    struct ba0_interval_mpq *X)
{
  int code;

  if (ba0_is_empty_interval_mpq (X))
    return false;

  if (X->type != ba0_closed_interval && X->type != ba0_open_interval)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  code = ba0_mpq_cmp (q, X->a);
  if (code < 0)
    return false;
  if (code == 0)
    return ba0_is_closed_interval_mpq (X);
  code = ba0_mpq_cmp (q, X->b);
  if (code > 0)
    return false;
  if (code == 0)
    return ba0_is_closed_interval_mpq (X);
  return true;
}

/*
 * texinfo: ba0_is_subset_interval_mpq
 * Return @code{true} if @var{X} is a subset of @var{Y}.
 */

BA0_DLL bool
ba0_is_subset_interval_mpq (
    struct ba0_interval_mpq *X,
    struct ba0_interval_mpq *Y)
{
  if (ba0_is_empty_interval_mpq (X))
    return true;
  else if (ba0_is_empty_interval_mpq (Y))
    return false;

  if (X->type != ba0_closed_interval && X->type != ba0_open_interval)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);
  if (Y->type != ba0_closed_interval && Y->type != ba0_open_interval)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  if (ba0_mpq_cmp (X->a, Y->a) < 0)
    return false;
  else if (ba0_mpq_cmp (X->a, Y->a) == 0)
    {
      if (ba0_is_closed_interval_mpq (X))
        return ba0_is_closed_interval_mpq (Y);
      else
/*
 * a == c < b
 */
        return ba0_mpq_cmp (X->b, Y->b) <= 0;
    }
  else if (ba0_mpq_cmp (X->b, Y->b) < 0)
    return true;
  else if (ba0_mpq_cmp (X->b, Y->b) <= 0)
/*
 * c < a <= b == d
 */
    return !ba0_is_closed_interval_mpq (X);
  else
    return false;
}

/*
 * Enumerate the following fractions (starting at k = 0)
 *
 *   1  1  2  1  2  3  4  1  2  3  4  5 
 *   -, -, -, -, -, -, -, -, -, -, -, -, ...
 *   2  3  3  5  5  5  7  7  7  7  7  7
 */

static void
kth_fraction (
    ba0_mpq_t f,
    ba0_int_p k)
{
  static ba0_int_p primes[] =
      { 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41 };
  ba0_int_p i, n, numer, denom;

  i = 0;
  n = 0;
  while (k - n >= primes[i] - 1)
    {
      n += primes[i] - 1;
      i += 1;
      if (i >= (ba0_int_p) (sizeof (primes) / sizeof (primes[0])))
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
    }
  numer = k - n + 1;
  denom = primes[i];
  ba0_mpq_set_si_si (f, numer, denom);
}

/*
 * texinfo: ba0_element_interval_mpq
 * Assign to @var{q} some element (the @var{k}th) of @var{I}.
 * If @var{I} is closed then @var{k} must be @math{0}.
 * If @var{I} contains infinitely many elements, then, for each value of @var{k},
 * a different element of @var{I} is assigned to @var{q}.
 */

BA0_DLL void
ba0_element_interval_mpq (
    ba0_mpq_t q,
    struct ba0_interval_mpq *I,
    unsigned ba0_int_p k)
{
  struct ba0_mark M;
  ba0_mpq_t s, t;
/*
 * the case of interval_mpqs of the form [a,a]
 */
  if (ba0_is_closed_interval_mpq (I))
    {
      if (k != 0)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
      ba0_mpq_set (q, I->a);
    }
  else if (ba0_is_unbounded_interval_mpq (I))
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);
  else
    {
      ba0_push_another_stack ();
      ba0_record (&M);

      ba0_mpq_init (s);
      ba0_mpq_init (t);
      ba0_mpq_sub (s, I->b, I->a);
      kth_fraction (t, k);
      ba0_mpq_mul (t, t, s);

      ba0_pull_stack ();
      ba0_mpq_add (q, I->a, t);
      ba0_restore (&M);
    }
}

/*
 * texinfo: ba0_middle_interval_mpq
 * Assign to @var{q} the middle of @var{I}.
 */

BA0_DLL void
ba0_middle_interval_mpq (
    ba0_mpq_t q,
    struct ba0_interval_mpq *I)
{
  ba0_element_interval_mpq (q, I, 0);
}

/*
 * texinfo: ba0_middle_interval_mpq_double
 * Return the middle of @var{I}, as a @code{double}.
 */

BA0_DLL double
ba0_middle_interval_mpq_double (
    struct ba0_interval_mpq *I)
{
  if (I->type != ba0_closed_interval && I->type != ba0_open_interval)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);
  return ((ba0_mpq_get_d (I->a) + ba0_mpq_get_d (I->b)) / 2.0);
}

/*
 * texinfo: ba0_width_interval_mpq
 * Assign to @var{q} the width of @var{I}.
 */

BA0_DLL void
ba0_width_interval_mpq (
    ba0_mpq_t q,
    struct ba0_interval_mpq *I)
{
  if (I->type != ba0_closed_interval && I->type != ba0_open_interval)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);
  if (I->type == ba0_closed_interval)
    ba0_mpq_set_si (q, 0);
  else
    ba0_mpq_sub (q, I->b, I->a);
}

/*
 * texinfo: ba0_width_interval_mpq_double
 * Return the width of @var{I}, as a @code{double}.
 */

BA0_DLL double
ba0_width_interval_mpq_double (
    struct ba0_interval_mpq *I)
{
  if (ba0_is_empty_interval_mpq (I))
    return 0.0;
  else if (ba0_is_unbounded_interval_mpq (I))
    return ba0_atof ("inf");
  else
    return ba0_mpq_get_d (I->b) - ba0_mpq_get_d (I->a);
}

/*
 * texinfo: ba0_abs_interval_mpq
 * Assign @math{|X|} to @var{I}.
 */

BA0_DLL void
ba0_abs_interval_mpq (
    struct ba0_interval_mpq *I,
    struct ba0_interval_mpq *X)
{
  struct ba0_mark M;
  ba0_mpq_t a, b;

  if (X->type != ba0_closed_interval && X->type != ba0_open_interval)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  if (ba0_mpq_sgn (X->a) >= 0)
    ba0_set_interval_mpq (I, X);
  else if (ba0_mpq_sgn (X->b) <= 0)
    {
      ba0_push_another_stack ();
      ba0_record (&M);
      ba0_mpq_init (a);
      ba0_mpq_init (b);
      ba0_mpq_neg (a, X->b);
      ba0_mpq_neg (b, X->a);
      ba0_pull_stack ();
      ba0_set_interval_mpq_mpq (I, a, b);
      ba0_restore (&M);
    }
  else
    {
      ba0_push_another_stack ();
      ba0_record (&M);
      ba0_mpq_init (a);
      ba0_mpq_init (b);
      ba0_mpq_neg (b, X->a);
      ba0_pull_stack ();
      ba0_set_interval_mpq_mpq (I, a, maxq (b, X->b));
      ba0_restore (&M);
    }
}

/*
 * texinfo: ba0_neg_interval_mpq
 * Assign @math{-X} to @var{I}.
 */

BA0_DLL void
ba0_neg_interval_mpq (
    struct ba0_interval_mpq *I,
    struct ba0_interval_mpq *X)
{
  struct ba0_mark M;
  ba0_mpq_t a, b;

  if (X->type != ba0_closed_interval && X->type != ba0_open_interval)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mpq_init (a);
  ba0_mpq_init (b);
  ba0_mpq_neg (a, X->b);
  ba0_mpq_neg (b, X->a);
  ba0_pull_stack ();
  ba0_set_interval_mpq_mpq (I, a, b);
  ba0_restore (&M);
}

/*
 * texinfo: ba0_add_interval_mpq
 * Assign @math{X+Y} to @math{I}.
 */

BA0_DLL void
ba0_add_interval_mpq (
    struct ba0_interval_mpq *I,
    struct ba0_interval_mpq *X,
    struct ba0_interval_mpq *Y)
{
  struct ba0_mark M;
  ba0_mpq_t a, b;

  if (X->type != ba0_closed_interval && X->type != ba0_open_interval)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);
  if (Y->type != ba0_closed_interval && Y->type != ba0_open_interval)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mpq_init (a);
  ba0_mpq_init (b);
  ba0_mpq_add (a, X->a, Y->a);
  ba0_mpq_add (b, X->b, Y->b);
  ba0_mpq_canonicalize (a);
  ba0_mpq_canonicalize (b);
  ba0_pull_stack ();
  ba0_set_interval_mpq_mpq (I, a, b);
  ba0_restore (&M);
}

/*
 * texinfo: ba0_add_interval_mpq_mpq
 * Assign @math{Y+k} to @math{X}.
 */

BA0_DLL void
ba0_add_interval_mpq_mpq (
    struct ba0_interval_mpq *X,
    struct ba0_interval_mpq *Y,
    ba0_mpq_t k)
{
  struct ba0_mark M;
  ba0_mpq_t a, b;

  if (Y->type != ba0_closed_interval && Y->type != ba0_open_interval)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mpq_init (a);
  ba0_mpq_init (b);
  ba0_mpq_add (a, Y->a, k);
  ba0_mpq_add (b, Y->b, k);
  ba0_mpq_canonicalize (a);
  ba0_mpq_canonicalize (b);
  ba0_pull_stack ();
  ba0_set_interval_mpq_mpq (X, a, b);
  ba0_restore (&M);
}

/*
 * texinfo: ba0_sub_interval_mpq
 * Assign @math{X-Y} to @math{I}.
 */

BA0_DLL void
ba0_sub_interval_mpq (
    struct ba0_interval_mpq *I,
    struct ba0_interval_mpq *X,
    struct ba0_interval_mpq *Y)
{
  struct ba0_mark M;
  ba0_mpq_t a, b;

  if (X->type != ba0_closed_interval && X->type != ba0_open_interval)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);
  if (Y->type != ba0_closed_interval && Y->type != ba0_open_interval)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mpq_init (a);
  ba0_mpq_init (b);
  ba0_mpq_sub (a, X->a, Y->b);
  ba0_mpq_sub (b, X->b, Y->a);
  ba0_mpq_canonicalize (a);
  ba0_mpq_canonicalize (b);
  ba0_pull_stack ();
  ba0_set_interval_mpq_mpq (I, a, b);
  ba0_restore (&M);
}

/*
 * texinfo: ba0_sub_mpq_interval_mpq
 * Assign @math{q-Y} to @math{I}.
 */

BA0_DLL void
ba0_sub_mpq_interval_mpq (
    struct ba0_interval_mpq *I,
    ba0_mpq_t k,
    struct ba0_interval_mpq *Y)
{
  struct ba0_mark M;
  ba0_mpq_t a, b;

  if (Y->type != ba0_closed_interval && Y->type != ba0_open_interval)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mpq_init (a);
  ba0_mpq_init (b);
  ba0_mpq_sub (a, k, Y->a);
  ba0_mpq_sub (b, k, Y->b);
  ba0_mpq_canonicalize (a);
  ba0_mpq_canonicalize (b);
  ba0_pull_stack ();
  ba0_set_interval_mpq_mpq (I, a, b);
  ba0_restore (&M);
}


/*
 * texinfo: ba0_sub_interval_mpq_mpq
 * Assign @math{X-k} to @math{I}.
 */

BA0_DLL void
ba0_sub_interval_mpq_mpq (
    struct ba0_interval_mpq *I,
    struct ba0_interval_mpq *X,
    ba0_mpq_t k)
{
  struct ba0_mark M;
  ba0_mpq_t a, b;

  if (X->type != ba0_closed_interval && X->type != ba0_open_interval)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mpq_init (a);
  ba0_mpq_init (b);
  ba0_mpq_sub (a, X->a, k);
  ba0_mpq_sub (b, X->b, k);
  ba0_mpq_canonicalize (a);
  ba0_mpq_canonicalize (b);
  ba0_pull_stack ();
  ba0_set_interval_mpq_mpq (I, a, b);
  ba0_restore (&M);
}

/*
 * texinfo: ba0_mul_interval_mpq
 * Assign @math{X \times Y} to @math{I}.
 */

BA0_DLL void
ba0_mul_interval_mpq (
    struct ba0_interval_mpq *I,
    struct ba0_interval_mpq *X,
    struct ba0_interval_mpq *Y)
{
  struct ba0_mark M;
  ba0_mpq_t ac, ad, bc, bd;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mpq_init (ac);
  ba0_mpq_init (ad);
  ba0_mpq_init (bc);
  ba0_mpq_init (bd);

  if (X->type != ba0_closed_interval && X->type != ba0_open_interval)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);
  if (Y->type != ba0_closed_interval && Y->type != ba0_open_interval)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  if (ba0_is_zero_interval_mpq (X) || ba0_is_zero_interval_mpq (Y))
    ba0_set_interval_mpq_si (I, 0);
  else if (ba0_mpq_sgn (X->a) >= 0)
    {
      if (ba0_mpq_sgn (Y->a) >= 0)
        {
          ba0_mpq_mul (ac, X->a, Y->a);
          ba0_mpq_canonicalize (ac);
          ba0_mpq_mul (bd, X->b, Y->b);
          ba0_mpq_canonicalize (bd);
          ba0_pull_stack ();
          ba0_set_interval_mpq_mpq (I, ac, bd);
        }
      else if (ba0_mpq_sgn (Y->b) <= 0)
        {
          ba0_mpq_mul (bc, X->b, Y->a);
          ba0_mpq_canonicalize (bc);
          ba0_mpq_mul (ad, X->a, Y->b);
          ba0_mpq_canonicalize (ad);
          ba0_pull_stack ();
          ba0_set_interval_mpq_mpq (I, bc, ad);
        }
      else
        {
          ba0_mpq_mul (bc, X->b, Y->a);
          ba0_mpq_canonicalize (bc);
          ba0_mpq_mul (bd, X->b, Y->b);
          ba0_mpq_canonicalize (bd);
          ba0_pull_stack ();
          ba0_set_interval_mpq_mpq (I, bc, bd);
        }
    }
  else if (ba0_mpq_sgn (X->b) <= 0)
    {
      if (ba0_mpq_sgn (Y->a) >= 0)
        {
          ba0_mpq_mul (ad, X->a, Y->b);
          ba0_mpq_canonicalize (ad);
          ba0_mpq_mul (bc, X->b, Y->a);
          ba0_mpq_canonicalize (bc);
          ba0_pull_stack ();
          ba0_set_interval_mpq_mpq (I, ad, bc);
        }
      else if (ba0_mpq_sgn (Y->b) <= 0)
        {
          ba0_mpq_mul (bd, X->b, Y->b);
          ba0_mpq_canonicalize (bd);
          ba0_mpq_mul (ac, X->a, Y->a);
          ba0_mpq_canonicalize (ac);
          ba0_pull_stack ();
          ba0_set_interval_mpq_mpq (I, bd, ac);
        }
      else
        {
          ba0_mpq_mul (ad, X->a, Y->b);
          ba0_mpq_canonicalize (ad);
          ba0_mpq_mul (ac, X->a, Y->a);
          ba0_mpq_canonicalize (ac);
          ba0_pull_stack ();
          ba0_set_interval_mpq_mpq (I, ad, ac);
        }
    }
  else
    {
      if (ba0_mpq_sgn (Y->a) >= 0)
        {
          ba0_mpq_mul (ad, X->a, Y->b);
          ba0_mpq_canonicalize (ad);
          ba0_mpq_mul (bd, X->b, Y->b);
          ba0_mpq_canonicalize (bd);
          ba0_pull_stack ();
          ba0_set_interval_mpq_mpq (I, ad, bd);
        }
      else if (ba0_mpq_sgn (Y->b) <= 0)
        {
          ba0_mpq_mul (bc, X->b, Y->a);
          ba0_mpq_canonicalize (bc);
          ba0_mpq_mul (ac, X->a, Y->a);
          ba0_mpq_canonicalize (ac);
          ba0_pull_stack ();
          ba0_set_interval_mpq_mpq (I, bc, ac);
        }
      else
        {
          ba0_mpq_mul (bc, X->b, Y->a);
          ba0_mpq_canonicalize (bc);
          ba0_mpq_mul (ad, X->a, Y->b);
          ba0_mpq_canonicalize (ad);
          ba0_mpq_mul (ac, X->a, Y->a);
          ba0_mpq_canonicalize (ac);
          ba0_mpq_mul (bd, X->b, Y->b);
          ba0_mpq_canonicalize (bd);
          ba0_pull_stack ();
          ba0_set_interval_mpq_mpq (I, minq (bc, ad), maxq (ac, bd));
        }
    }
  ba0_restore (&M);
}

/*
 * texinfo: ba0_mul_interval_mpq_mpq
 * Assign @math{X \times k} to @math{I}.
 */

BA0_DLL void
ba0_mul_interval_mpq_mpq (
    struct ba0_interval_mpq *I,
    struct ba0_interval_mpq *X,
    ba0_mpq_t k)
{
  struct ba0_mark M;
  ba0_mpq_t a, b;

  if (X->type != ba0_closed_interval && X->type != ba0_open_interval)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  if (ba0_mpq_sgn (k) == 0)
    ba0_set_interval_mpq_si (I, 0);
  else
    {
      ba0_push_another_stack ();
      ba0_record (&M);
      ba0_mpq_init (a);
      ba0_mpq_init (b);
      if (ba0_mpq_sgn (k) > 0)
        {
          ba0_mpq_mul (a, X->a, k);
          ba0_mpq_mul (b, X->b, k);
        }
      else
        {
          ba0_mpq_mul (a, X->b, k);
          ba0_mpq_mul (b, X->a, k);
        }
      ba0_mpq_canonicalize (a);
      ba0_mpq_canonicalize (b);
      ba0_pull_stack ();
      ba0_set_interval_mpq_mpq (I, a, b);
      ba0_restore (&M);
    }
}

/*
 * texinfo: ba0_mul_interval_mpq_si
 * Assign @math{X \times n} to @math{I}.
 */

BA0_DLL void
ba0_mul_interval_mpq_si (
    struct ba0_interval_mpq *I,
    struct ba0_interval_mpq *X,
    ba0_int_p n)
{
  struct ba0_mark M;
  ba0_mpq_t q;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mpq_init (q);
  ba0_mpq_set_si (q, n);
  ba0_pull_stack ();
  ba0_mul_interval_mpq_mpq (I, X, q);
  ba0_restore (&M);
}

/*
 * texinfo: ba0_mul_interval_mpq_ui
 * Assign @math{X \times n} to @math{I}.
 */

BA0_DLL void
ba0_mul_interval_mpq_ui (
    struct ba0_interval_mpq *I,
    struct ba0_interval_mpq *X,
    unsigned ba0_int_p n)
{
  struct ba0_mark M;
  ba0_mpq_t q;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mpq_init (q);
  ba0_mpq_set_ui (q, n);
  ba0_pull_stack ();
  ba0_mul_interval_mpq_mpq (I, X, q);
  ba0_restore (&M);
}

/*
 * texinfo: ba0_pow_interval_mpq
 * Assign @math{X^n} to @math{I}.
 */

BA0_DLL void
ba0_pow_interval_mpq (
    struct ba0_interval_mpq *I,
    struct ba0_interval_mpq *X,
    ba0_int_p n)
{
  struct ba0_mark M;
  ba0_mpq_t a, b, zero;

  if (X->type != ba0_closed_interval && X->type != ba0_open_interval)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  if (n == 0)
    ba0_set_interval_mpq_si (I, 1);
  else
    {
      ba0_push_another_stack ();
      ba0_record (&M);
      ba0_mpq_init (a);
      ba0_mpq_init (b);

      if (ba0_mpq_sgn (X->a) >= 0 || (ba0_int_p) n % 2 == 1)
        {
          ba0_mpz_pow_ui
              (ba0_mpq_numref (a), ba0_mpq_numref (X->a),
              (unsigned ba0_int_p) n);
          ba0_mpz_pow_ui (ba0_mpq_denref (a), ba0_mpq_denref (X->a),
              (unsigned ba0_int_p) n);
          ba0_mpz_pow_ui (ba0_mpq_numref (b), ba0_mpq_numref (X->b),
              (unsigned ba0_int_p) n);
          ba0_mpz_pow_ui (ba0_mpq_denref (b), ba0_mpq_denref (X->b),
              (unsigned ba0_int_p) n);
          ba0_pull_stack ();
          ba0_set_interval_mpq_mpq (I, a, b);
        }
      else if (ba0_mpq_sgn (X->b) <= 0)
        {
          ba0_mpq_neg (a, X->a);
          ba0_mpq_neg (b, X->b);
          ba0_mpz_pow_ui
              (ba0_mpq_numref (a), ba0_mpq_numref (a), (unsigned ba0_int_p) n);
          ba0_mpz_pow_ui (ba0_mpq_denref (a), ba0_mpq_denref (a),
              (unsigned ba0_int_p) n);
          ba0_mpz_pow_ui (ba0_mpq_numref (b), ba0_mpq_numref (b),
              (unsigned ba0_int_p) n);
          ba0_mpz_pow_ui (ba0_mpq_denref (b), ba0_mpq_denref (b),
              (unsigned ba0_int_p) n);
          ba0_pull_stack ();
          ba0_set_interval_mpq_mpq (I, b, a);
        }
      else
        {
          ba0_mpz_pow_ui
              (ba0_mpq_numref (a), ba0_mpq_numref (X->a),
              (unsigned ba0_int_p) n);
          ba0_mpz_pow_ui (ba0_mpq_denref (a), ba0_mpq_denref (X->a),
              (unsigned ba0_int_p) n);
          ba0_mpq_neg (b, X->b);
          ba0_mpz_pow_ui
              (ba0_mpq_numref (b), ba0_mpq_numref (b), (unsigned ba0_int_p) n);
          ba0_mpz_pow_ui (ba0_mpq_denref (b), ba0_mpq_denref (b),
              (unsigned ba0_int_p) n);
          ba0_mpq_init (zero);
          ba0_pull_stack ();
          ba0_set_interval_mpq_mpq (I, zero, maxq (a, b));
        }
      ba0_restore (&M);
    }
}

/*
 * texinfo: ba0_pow_interval_mpq_mpq
 * Assign @math{q^n} to @math{I}.
 */

BA0_DLL void
ba0_pow_interval_mpq_mpq (
    struct ba0_interval_mpq *I,
    ba0_mpq_t q,
    ba0_int_p n)
{
  ba0_set_interval_mpq_mpq (I, q, q);
  ba0_pow_interval_mpq (I, I, n);
}

static void
union_overlapping_interval_mpq (
    struct ba0_interval_mpq *I,
    struct ba0_interval_mpq *X,
    struct ba0_interval_mpq *Y)
{
  ba0_set_interval_mpq_mpq (I, minq (X->a, Y->a), maxq (X->b, Y->b));
}

/*
 * texinfo: ba0_div_interval_mpq
 * Assign @math{X/Y} to @var{F}. 
 * The result is either a single interval or a union of two disjoint intervals
 * (when @var{Y} contains @math{0}).
 * These resulting intervals are stored in @var{F}.
 */

BA0_DLL void
ba0_div_interval_mpq (
    struct ba0_tableof_interval_mpq *F,
    struct ba0_interval_mpq *X,
    struct ba0_interval_mpq *Y)
{
  struct ba0_mark M;
  struct ba0_interval_mpq R, S;
  ba0_mpq_t a, b;

  if (X->type != ba0_closed_interval && X->type != ba0_open_interval)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);
  if (Y->type != ba0_closed_interval && Y->type != ba0_open_interval)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  ba0_reset_table ((struct ba0_table *) F);
  ba0_realloc2_table ((struct ba0_table *) F, 2,
      (ba0_new_function *) & ba0_new_interval_mpq);

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_init_interval_mpq (&R);
  ba0_init_interval_mpq (&S);
  ba0_mpq_init (a);
  ba0_mpq_init (b);

  if (!ba0_contains_zero_interval_mpq (Y))
    {
      ba0_mpq_invert (a, Y->b);
      ba0_mpq_invert (b, Y->a);
      ba0_set_interval_mpq_mpq (&R, a, b);
      ba0_pull_stack ();
      ba0_mul_interval_mpq (F->tab[0], X, &R);
      F->size = 1;
    }
  else if (!ba0_is_zero_interval_mpq (Y) && !ba0_contains_zero_interval_mpq (X))
    {
      ba0_mpq_invert (b, Y->a);
      ba0_set_interval_mpq_type_mpq (&R, ba0_left_infinite_interval, b, b);
      ba0_mul_interval_mpq (&R, X, &R);
      ba0_mpq_invert (a, Y->b);
      ba0_set_interval_mpq_type_mpq (&S, ba0_right_infinite_interval, a, a);
      ba0_mul_interval_mpq (&S, X, &S);
      if (ba0_are_disjoint_interval_mpq (&R, &S))
        {
          ba0_pull_stack ();
          ba0_set_interval_mpq (F->tab[0], &R);
          ba0_set_interval_mpq (F->tab[1], &S);
          F->size = 2;
        }
      else
        {
/*
 * May only happen if X is open
 */
          ba0_pull_stack ();
          union_overlapping_interval_mpq (F->tab[0], &R, &S);
          F->size = 1;
        }
    }
  else
    {
/*
 * X / 0 gives ]-INFINITY, INFINITY[
 * If X and Y both contain zero, then ]-INFINITY, INFINITY[
 */
      ba0_pull_stack ();
      ba0_set_interval_mpq_type_mpq (F->tab[0], ba0_infinite_interval, a, a);
      F->size = 1;
    }
  ba0_restore (&M);
}

/*
 * texinfo: ba0_div_mpq_interval_mpq
 * Assign @math{k/Y} to @var{F}. 
 * The result is either a single interval or a union of two disjoint intervals
 * (when @var{Y} contains @math{0}).
 * These resulting intervals are stored in @var{F}.
 */

BA0_DLL void
ba0_div_mpq_interval_mpq (
    struct ba0_tableof_interval_mpq *F,
    ba0_mpq_t k,
    struct ba0_interval_mpq *Y)
{
  struct ba0_interval_mpq R;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_init_interval_mpq (&R);
  ba0_set_interval_mpq_mpq (&R, k, k);
  ba0_pull_stack ();
  ba0_div_interval_mpq (F, &R, Y);
  ba0_restore (&M);
}

/*
 * texinfo: ba0_div_interval_mpq_mpq
 * Assign @math{Y/k} to @var{X}.
 */

BA0_DLL void
ba0_div_interval_mpq_mpq (
    struct ba0_interval_mpq *X,
    struct ba0_interval_mpq *Y,
    ba0_mpq_t k)
{
  struct ba0_interval_mpq R;
  struct ba0_mark M;
  ba0_mpq_t q;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_init_interval_mpq (&R);
  ba0_mpq_init (q);
  ba0_mpq_invert (q, k);
  ba0_set_interval_mpq_mpq (&R, q, q);
  ba0_pull_stack ();
  ba0_mul_interval_mpq (X, Y, &R);
  ba0_restore (&M);
}

/*
 * texinfo: ba0_scanf_interval_mpq
 * Parsing function for intervals.
 * Allowed intervals are either @code{empty}, a rational number
 * or a pair of rational numbers @math{[a,b]} with @math{a \leq b}.
 * In this last case, if @math{a=b} the interval is closed else
 * it is open.
 * This function is called by @code{ba0_scanf/%qi}.
 */

BA0_DLL void *
ba0_scanf_interval_mpq (
    void *z)
{
  struct ba0_interval_mpq *R;
  struct ba0_mark M;
  ba0_mpq_t a, b;

  if (z == (void *) 0)
    R = ba0_new_interval_mpq ();
  else
    R = (struct ba0_interval_mpq *) z;

  if (ba0_type_token_analex () == ba0_string_token &&
      strcmp (ba0_value_token_analex (), "empty") == 0)
    ba0_set_interval_mpq_type_mpq
        (R, ba0_empty_interval, (ba0__mpq_struct *) 0, (ba0__mpq_struct *) 0);
  else if (ba0_sign_token_analex ("["))
    {
      ba0_push_another_stack ();
      ba0_record (&M);
      ba0_mpq_init (a);
      ba0_mpq_init (b);
      ba0_scanf ("[%q, %q]", a, b);
      ba0_pull_stack ();
      ba0_set_interval_mpq_mpq (R, a, b);
      ba0_restore (&M);
    }
  else
    {
      ba0_push_another_stack ();
      ba0_record (&M);
      ba0_mpq_init (a);
      ba0_scanf ("%q", a);
      ba0_pull_stack ();
      ba0_set_interval_mpq_mpq (R, a, a);
      ba0_restore (&M);
    }

  return R;
}

/*
 * texinfo: ba0_printf_interval_mpq
 * The general printing function for intervals.
 * It is called by @code{ba0_printf/%qi}.
 */

BA0_DLL void
ba0_printf_interval_mpq (
    void *z)
{
  struct ba0_interval_mpq *R = (struct ba0_interval_mpq *) z;

  switch (R->type)
    {
    case ba0_closed_interval:
      ba0_printf ("%q", R->a);
      break;
    case ba0_open_interval:
      ba0_printf ("[%q, %q]", R->a, R->b);
      break;
    case ba0_infinite_interval:
      ba0_printf ("[-inf, inf]");
      break;
    case ba0_left_infinite_interval:
      ba0_printf ("[-inf, %q]", R->b);
      break;
    case ba0_right_infinite_interval:
      ba0_printf ("[%q, inf]", R->a);
      break;
    case ba0_empty_interval:
      ba0_printf ("empty");
      break;
    }
}

static char _interval_mpq[] = "interval_mpq";

BA0_DLL ba0_int_p
ba0_garbage1_interval_mpq (
    void *z,
    enum ba0_garbage_code code)
{
  struct ba0_interval_mpq *R = (struct ba0_interval_mpq *) z;
  ba0_int_p n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (R, sizeof (struct ba0_interval_mpq), _interval_mpq);
  n += ba0_garbage1_mpq (R->a, ba0_embedded);
  n += ba0_garbage1_mpq (R->b, ba0_embedded);
  return n;
}

BA0_DLL void *
ba0_garbage2_interval_mpq (
    void *z,
    enum ba0_garbage_code code)
{
  struct ba0_interval_mpq *R;

  if (code == ba0_isolated)
    R = (struct ba0_interval_mpq *) ba0_new_addr_gc_info (z, _interval_mpq);
  else
    R = (struct ba0_interval_mpq *) z;
  ba0_garbage2_mpq (R->a, ba0_embedded);
  ba0_garbage2_mpq (R->b, ba0_embedded);
  return R;
}

BA0_DLL void *
ba0_copy_interval_mpq (
    void *z)
{
  struct ba0_interval_mpq *R;

  R = ba0_new_interval_mpq ();
  ba0_set_interval_mpq (R, (struct ba0_interval_mpq *) z);
  return R;
}
