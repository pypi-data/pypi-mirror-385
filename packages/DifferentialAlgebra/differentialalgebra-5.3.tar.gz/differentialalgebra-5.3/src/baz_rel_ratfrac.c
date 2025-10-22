#include "baz_rel_ratfrac.h"

/*
 * texinfo: baz_init_rel_ratfrac
 * Initialize @var{R} to zero.
 */

BAZ_DLL void
baz_init_rel_ratfrac (
    struct baz_rel_ratfrac *R)
{
  baz_init_ratfrac (&R->lhs);
  baz_init_ratfrac (&R->rhs);
  R->op = baz_none_relop;
}

/*
 * texinfo: baz_new_rel_ratfrac
 * Allocate a new @code{struct baz_rel_ratfrac *}, initialize it and return it.
 */

BAZ_DLL struct baz_rel_ratfrac *
baz_new_rel_ratfrac (
    void)
{
  struct baz_rel_ratfrac *R;

  R = (struct baz_rel_ratfrac *) ba0_alloc (sizeof (struct baz_rel_ratfrac));
  baz_init_rel_ratfrac (R);
  return R;
}

/*
 * texinfo: baz_set_rel_ratfrac
 * Assign @var{src} to @var{dst}.
 */

BAZ_DLL void
baz_set_rel_ratfrac (
    struct baz_rel_ratfrac *dst,
    struct baz_rel_ratfrac *src)
{
  if (dst != src)
    {
      baz_set_ratfrac (&dst->lhs, &src->lhs);
      baz_set_ratfrac (&dst->rhs, &src->rhs);
      dst->op = src->op;
    }
}

/*
 * texinfo: baz_set_ratfrac_rel_ratfrac
 * Subtract the right handside from the left handside of @var{R} and assign
 * the result to @var{Q}.
 */

BAZ_DLL void
baz_set_ratfrac_rel_ratfrac (
    struct baz_ratfrac *Q,
    struct baz_rel_ratfrac *R)
{
  baz_sub_ratfrac (Q, &R->lhs, &R->rhs);
}

/*
 * Read a relational operator starting at the current token. Possibly none.
 * After reading, the current token is the last one of the operator.
 * If no relational operator, one token is ungot.
 */

static enum baz_typeof_relop
baz_scanf_relop (
    void)
{
  enum baz_typeof_relop op;

  op = baz_none_relop;

  if (ba0_sign_token_analex ("="))
    {
      ba0_get_token_analex ();
      if (!ba0_sign_token_analex ("="))
        ba0_unget_token_analex (1);
      op = baz_equal_relop;
    }
  else if (ba0_sign_token_analex ("!"))
    {
      ba0_get_token_analex ();
      if (ba0_sign_token_analex ("="))
        op = baz_not_equal_relop;
      else
        ba0_unget_token_analex (1);
    }
  else if (ba0_sign_token_analex (">"))
    {
      ba0_get_token_analex ();
      if (ba0_sign_token_analex ("="))
        op = baz_greater_or_equal_relop;
      else
        {
          ba0_unget_token_analex (1);
          op = baz_greater_relop;
        }
    }
  else if (ba0_sign_token_analex ("<"))
    {
      ba0_get_token_analex ();
      if (ba0_sign_token_analex ("="))
        op = baz_less_or_equal_relop;
      else if (ba0_sign_token_analex (">"))
        op = baz_not_equal_relop;
      else
        {
          ba0_unget_token_analex (1);
          op = baz_less_relop;
        }
    }
  else
    ba0_unget_token_analex (1);
  return op;
}

/*
 * texinfo: baz_scanf_rel_ratfrac
 * Parsing function for @code{struct baz_rel_ratfrac *}.
 * This function is called by @code{ba0_scanf/%relQz}.
 */

BAZ_DLL void *
baz_scanf_rel_ratfrac (
    void *A)
{
  struct baz_rel_ratfrac *R = (struct baz_rel_ratfrac *) A;

  if (A == (struct baz_rel_ratfrac *) 0)
    R = baz_new_rel_ratfrac ();

  if (ba0_type_token_analex () == ba0_string_token
      && (strcmp (ba0_value_token_analex (), "Eq") == 0
          || strcmp (ba0_value_token_analex (), "Ne") == 0))
    {
      if (strcmp (ba0_value_token_analex (), "Eq") == 0)
        R->op = baz_equal_relop;
      else
        R->op = baz_not_equal_relop;
/* Sympy Eq(lhs,rhs), Ne(lhs,rhs) */
      ba0_get_token_analex ();
      if (!ba0_sign_token_analex ("("))
        BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
      ba0_get_token_analex ();
      baz_scanf_ratfrac (&R->lhs);
      ba0_get_token_analex ();
      if (!ba0_sign_token_analex (","))
        BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
      ba0_get_token_analex ();
      baz_scanf_ratfrac (&R->rhs);
      ba0_get_token_analex ();
      if (!ba0_sign_token_analex (")"))
        BA0_RAISE_PARSER_EXCEPTION (BA0_ERRSYN);
    }
  else
    {
      baz_scanf_ratfrac (&R->lhs);

      ba0_get_token_analex ();
      R->op = baz_scanf_relop ();
      if (R->op != baz_none_relop)
        {
          ba0_get_token_analex ();
          baz_scanf_ratfrac (&R->rhs);
        }
    }

  return R;
}

/*
 * texinfo: baz_printf_rel_ratfrac
 * Printing function for @code{struct baz_rel_ratfrac *}.
 * This function is called by @code{ba0_printf/%relQz}.
 */

BAZ_DLL void
baz_printf_rel_ratfrac (
    void *A)
{
  struct baz_rel_ratfrac *R = (struct baz_rel_ratfrac *) A;

  baz_printf_ratfrac (&R->lhs);
  if (R->op != baz_none_relop)
    {
      switch (R->op)
        {
        case baz_none_relop:
        case baz_equal_relop:
          ba0_put_string (" == ");
          break;
        case baz_not_equal_relop:
          ba0_put_string (" != ");
          break;
        case baz_greater_relop:
          ba0_put_string (" > ");
          break;
        case baz_greater_or_equal_relop:
          ba0_put_string (" >= ");
          break;
        case baz_less_relop:
          ba0_put_string (" < ");
          break;
        case baz_less_or_equal_relop:
          ba0_put_string (" <= ");
          break;
        }
      baz_printf_ratfrac (&R->rhs);
    }
}

/*
 * Readonly static data
 */

static char _struct_rel_ratfrac[] = "struct baz_rel_ratfrac";

BAZ_DLL ba0_int_p
baz_garbage1_rel_ratfrac (
    void *A,
    enum ba0_garbage_code code)
{
  struct baz_rel_ratfrac *R = (struct baz_rel_ratfrac *) A;
  ba0_int_p n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (R, sizeof (struct baz_rel_ratfrac),
        _struct_rel_ratfrac);

  n += baz_garbage1_ratfrac (&R->lhs, ba0_embedded);
  n += baz_garbage1_ratfrac (&R->rhs, ba0_embedded);

  return n;
}

BAZ_DLL void *
baz_garbage2_rel_ratfrac (
    void *A,
    enum ba0_garbage_code code)
{
  struct baz_rel_ratfrac *R;

  if (code == ba0_isolated)
    R = ba0_new_addr_gc_info (A, _struct_rel_ratfrac);
  else
    R = (struct baz_rel_ratfrac *) A;

  baz_garbage2_ratfrac (&R->lhs, ba0_embedded);
  baz_garbage2_ratfrac (&R->rhs, ba0_embedded);
  return R;
}

BAZ_DLL void *
baz_copy_rel_ratfrac (
    void *A)
{
  struct baz_rel_ratfrac *B;

  B = baz_new_rel_ratfrac ();
  baz_set_rel_ratfrac (B, (struct baz_rel_ratfrac *) A);
  return B;
}
