#include "bav_differential_ring.h"
#include "bav_rank.h"
#include "bav_global.h"

/*
 * texinfo: bav_set_settings_rank
 * Customize to @var{p} the way ranks are printed.
 */

BAV_DLL void
bav_set_settings_rank (
    ba0_printf_function *p)
{
  bav_initialized_global.rank.printf = p ? p : &bav_printf_default_rank;
}

/*
 * texinfo: bav_get_settings_rank
 * Assign to @var{p} the function used for printing ranks.
 */

BAV_DLL void
bav_get_settings_rank (
    ba0_printf_function **p)
{
  if (p)
    *p = bav_initialized_global.rank.printf;
}

/*
 * texinfo: bav_init_rank
 * Dummy constructor.
 */

BAV_DLL void
bav_init_rank (
    struct bav_rank *rg)
{
  rg = (struct bav_rank *) 0;   /* to avoid an annoying warning */
}

/*
 * texinfo: bav_new_rank
 * Allocates a new rank, initialize it and return it.
 */

BAV_DLL struct bav_rank *
bav_new_rank (
    void)
{
  struct bav_rank *rg;

  rg = (struct bav_rank *) ba0_alloc (sizeof (struct bav_rank));
  bav_init_rank (rg);
  return rg;
}

/*
 * texinfo: bav_is_zero_rank
 * Return @code{true} if @var{rg} is the rank of zero.
 */

BAV_DLL bool
bav_is_zero_rank (
    struct bav_rank *rg)
{
  return rg->var == BAV_NOT_A_VARIABLE && rg->deg == -1;
}

/*
 * texinfo: bav_is_constant_rank
 * Return @code{true} if @var{rg} is the rank of a nonzero constant.
 */

BAV_DLL bool
bav_is_constant_rank (
    struct bav_rank *rg)
{
  return rg->deg == 0;
}

/*
 * texinfo: bav_equal_rank
 * Return @code{true} if @var{rg} and @var{sg} are equal.
 */

BAV_DLL bool
bav_equal_rank (
    struct bav_rank *rg,
    struct bav_rank *sg)
{
  return rg->var == sg->var && rg->deg == sg->deg;
}

/*
 * texinfo: bav_lt_rank
 * Return @code{true} if @var{rg} is less than @var{sg}.
 * The rank of zero is lower than any other rank.
 * The rank of nonzero constants is lower than classical ranks.
 * Classical ranks are ordered by comparing first variables
 * with respect to the current ordering and, in case of equality,
 * the degrees.
 */

BAV_DLL bool
bav_lt_rank (
    struct bav_rank *rg,
    struct bav_rank *sg)
{
  bav_Inumber nr, ns;

  if (bav_is_zero_rank (rg))
    return !bav_is_zero_rank (sg);
  if (bav_is_constant_rank (rg))
    return !bav_is_zero_rank (sg) && !bav_is_constant_rank (sg);
  if (bav_is_zero_rank (sg) || bav_is_constant_rank (sg))
    return false;
  nr = bav_variable_number (rg->var);
  ns = bav_variable_number (sg->var);
  if (nr < ns)
    return true;
  else if (nr == ns)
    return rg->deg < sg->deg;
  else
    return false;
}

/*
 * texinfo: bav_gt_rank
 * Return @code{true} if @var{rg} is greater than @var{sg}.
 */

BAV_DLL bool
bav_gt_rank (
    struct bav_rank *rg,
    struct bav_rank *sg)
{
  bav_Inumber nr, ns;

  if (bav_is_zero_rank (sg))
    return !bav_is_zero_rank (rg);
  if (bav_is_constant_rank (sg))
    return !bav_is_zero_rank (rg) && !bav_is_constant_rank (rg);
  if (bav_is_zero_rank (rg) || bav_is_constant_rank (rg))
    return false;
  ns = bav_variable_number (sg->var);
  nr = bav_variable_number (rg->var);
  if (ns < nr)
    return true;
  else if (ns == nr)
    return sg->deg < rg->deg;
  else
    return false;
}

/*
 * texinfo: bav_zero_rank
 * Return the rank of zero.
 */

BAV_DLL struct bav_rank
bav_zero_rank (
    void)
{
  static struct bav_rank rg = { BAV_NOT_A_VARIABLE, (bav_Idegree) - 1 };
  return rg;
}

/*
 * texinfo: bav_constant_rank
 * Return the rank of nonzero constants.
 */

BAV_DLL struct bav_rank
bav_constant_rank (
    void)
{
  static struct bav_rank rg = { BAV_NOT_A_VARIABLE, (bav_Idegree) 0 };
  return rg;
}

/*
 * texinfo: bav_constant_rank2
 * Return the rank of nonzero constant also (with @var{v} encoded
 * in the field @code{var} of the result).
 */

BAV_DLL struct bav_rank
bav_constant_rank2 (
    struct bav_variable *v)
{
  struct bav_rank rg;
  rg.var = v;
  rg.deg = (bav_Idegree) 0;
  return rg;
}

/*
 * texinfo: bav_scanf_rank
 * The function called for parsing ranks.
 * It is called by @code{ba0_scanf/%rank}.
 * The character @code{0} denotes the rank of zero.
 * Any positive integer denotes the rank of nonzero constants.
 * Exponentiation can be denoted @code{^} or @code{**}.
 * A variable to a zero exponent yields the rank of nonzero constants.
 * Exponents may be negative.
 */

BAV_DLL void *
bav_scanf_rank (
    void *z)
{
  struct bav_rank *rg;
  bool exponent;

  if (z == (void *) 0)
    rg = bav_new_rank ();
  else
    rg = (struct bav_rank *) z;

  if (ba0_type_token_analex () == ba0_integer_token)
    {
      if (strcmp (ba0_value_token_analex (), "0") == 0)
        *rg = bav_zero_rank ();
      else
        *rg = bav_constant_rank ();
    }
  else
    {
      ba0_scanf ("%v", &rg->var);
      ba0_get_token_analex ();

      exponent = false;
      if (ba0_sign_token_analex ("^"))
        exponent = true;
      else if (ba0_sign_token_analex ("*"))
        {
          ba0_get_token_analex ();
          if (ba0_sign_token_analex ("*"))
            exponent = true;
          else
            ba0_unget_token_analex (1);
        }

      if (exponent)
        {
          ba0_get_token_analex ();
          if (ba0_sign_token_analex ("("))
            ba0_scanf ("(%d)", &rg->deg);
          else if (ba0_type_token_analex () == ba0_integer_token)
            rg->deg = (bav_Idegree) atoi (ba0_value_token_analex ());
          else
            BA0_RAISE_PARSER_EXCEPTION (BAV_ERRTER);
          if (rg->deg == 0)
            BA0_RAISE_PARSER_EXCEPTION (BAV_ERRTER);
        }
      else
        {
          ba0_unget_token_analex (1);
          rg->deg = 1;
        }
    }
  return rg;
}

/*
 * texinfo: bav_printf_default_rank
 * The default function for printing ranks.
 * It can be customized by modifying
 * @code{bav_initialized_global.rank.printf}.
 * It is called by @code{ba0_printf/%rank}.
 * Exponentiation is denoted using @code{^}.
 */

BAV_DLL void
bav_printf_default_rank (
    void *z)
{
  struct bav_rank *rg = (struct bav_rank *) z;

  if (bav_is_zero_rank (rg))
    ba0_printf ("0");
  else if (bav_is_constant_rank (rg))
    ba0_printf ("1");
  else if (rg->deg == 1)
    ba0_printf ("%v", rg->var);
  else if (rg->deg > 0)
    ba0_printf ("%v^%d", rg->var, rg->deg);
  else
    ba0_printf ("%v^(%d)", rg->var, rg->deg);
}

/*
 * texinfo: bav_printf_stars_rank
 * A function for printing ranks.
 * Exponentiation is denoted using @code{**}.
 */

BAV_DLL void
bav_printf_stars_rank (
    void *z)
{
  struct bav_rank *rg = (struct bav_rank *) z;

  if (bav_is_zero_rank (rg))
    ba0_printf ("0");
  else if (bav_is_constant_rank (rg))
    ba0_printf ("1");
  else if (rg->deg == 1)
    ba0_printf ("%v", rg->var);
  else if (rg->deg > 0)
    ba0_printf ("%v**%d", rg->var, rg->deg);
  else
    ba0_printf ("%v**(%d)", rg->var, rg->deg);
}

/*
 * texinfo: bav_printf_list_rank
 * A function for printing ranks.
 * Ranks are printed as a list @code{[variable, degree]}.
 */

BAV_DLL void
bav_printf_list_rank (
    void *z)
{
  struct bav_rank *rg = (struct bav_rank *) z;

  if (bav_is_zero_rank (rg))
    ba0_printf ("[0, 0]");
  else if (bav_is_constant_rank (rg))
    {
      if (rg->var == BAV_NOT_A_VARIABLE)
        ba0_printf ("[1, 0]");
      else
        ba0_printf ("[%v, 0]", rg->var);
    }
  else
    ba0_printf ("[%v, %d]", rg->var, rg->deg);
}

BAV_DLL void
bav_printf_rank (
    void *z)
{
  if ((bav_initialized_global.rank.printf) != (ba0_printf_function *) 0)
    (*bav_initialized_global.rank.printf) (z);
  else
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
}

/*
 * texinfo: bav_compare_rank
 * A comparison function for sorting tables of ranks
 * in decreasing order, using @code{qsort}.
 * This function is used to sort terms.
 */

BAV_DLL int
bav_compare_rank (
    const void *x,
    const void *y)
{
  struct bav_rank *r = (struct bav_rank *) x;
  struct bav_rank *s = (struct bav_rank *) y;
  bav_Inumber n, m;

  if (r->var == s->var && r->deg == s->deg)
    return 0;

  n = bav_variable_number (r->var);
  m = bav_variable_number (s->var);

  return (n < m || (n == m && r->deg < s->deg)) ? 1 : -1;
}
