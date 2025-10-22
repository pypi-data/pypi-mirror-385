#include "ba0_exception.h"
#include "ba0_stack.h"
#include "ba0_int_p.h"
#include "ba0_basic_io.h"
#include "ba0_analex.h"

/*
 * texinfo: ba0_log2_int_p
 * Return the largest nonnegative integer @var{e} such that 
 * @math{2^e \leq \var{size}}. Return zero if @var{size} is not positive.
 */

BA0_DLL ba0_int_p
ba0_log2_int_p (
    ba0_int_p size)
{
  ba0_int_p n = 1, log2_n = 0;
  while (n <= size)
    {
      n <<= 1;
      log2_n += 1;
    }
  return log2_n - 1;
}

/*
 * texinfo: ba0_scanf_int_p
 * General parsing functions for machine integers.
 * It can be called using @code{ba0_scanf/%d}.
 */

BA0_DLL void *
ba0_scanf_int_p (
    void *z)
{
  char *p;
  ba0_int_p *e;
  bool oppose;

  if (z == (void *) 0)
    e = (ba0_int_p *) ba0_alloc (sizeof (ba0_int_p));
  else
    e = (ba0_int_p *) z;

  if (ba0_sign_token_analex ("-"))
    {
      ba0_get_token_analex ();
      oppose = true;
    }
  else
    oppose = false;

  if (ba0_type_token_analex () != ba0_integer_token)
    BA0_RAISE_PARSER_EXCEPTION (BA0_ERRINT);

  p = ba0_value_token_analex ();
  sscanf (p, BA0_FORMAT_INT_P, e);
  if (oppose)
    *e = -*e;
  return e;
}

/*
 * texinfo: ba0_printf_int_p
 * General printing function for machine integers.
 * It can be called using @code{ba0_printf/%d}.
 */

BA0_DLL void
ba0_printf_int_p (
    void *z)
{
  ba0_put_int_p ((ba0_int_p) z);
}

/*
 * texinfo: ba0_scanf_hexint_p
 * General parsing fuunction for machine integers in 
 * hexadecimal notation.
 * It can be called using @code{ba0_scanf/%x}.
 */

BA0_DLL void *
ba0_scanf_hexint_p (
    void *z)
{
  BA0_RAISE_EXCEPTION (BA0_ERRNYP);
  return z;
}

/*
 * texinfo: ba0_printf_hexint_p
 * General printing function for machine integers in 
 * hexadecimal notation.
 * It can be called using @code{ba0_printf/%x}.
 */

BA0_DLL void
ba0_printf_hexint_p (
    void *z)
{
  ba0_put_hexint_p ((ba0_int_p) z);
}
