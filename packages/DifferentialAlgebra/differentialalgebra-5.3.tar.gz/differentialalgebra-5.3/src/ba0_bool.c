#include "ba0_exception.h"
#include "ba0_stack.h"
#include "ba0_bool.h"
#include "ba0_basic_io.h"
#include "ba0_analex.h"

/*
 * texinfo: ba0_scanf_bool
 * General parsing functions for bools.
 * It can be called using @code{ba0_scanf/%bool}.
 * The bool can be entered as an @code{int}: 
 * a nonzero value is @code{true} while zero is @code{false}. 
 * It can also be entered as @code{true} or @code{false}.
 * Exception @code{BA0_ERRBOOL} is raised in case of a syntax error.
 */

BA0_DLL void *
ba0_scanf_bool (
    void *z)
{
  char *p;
  ba0_bool *e;

  if (z == (void *) 0)
    e = (ba0_bool *) ba0_alloc (sizeof (ba0_bool));
  else
    e = (ba0_bool *) z;

  p = ba0_value_token_analex ();

  if (ba0_type_token_analex () == ba0_integer_token)
    {
      ba0_int_p x;
      sscanf (p, BA0_FORMAT_INT_P, &x);
      if (x != 0)
        *e = true;
      else
        *e = false;
    }
  else if (ba0_type_token_analex () == ba0_string_token)
    {
      if (ba0_strcasecmp (p, "true") == 0)
        *e = true;
      else if (ba0_strcasecmp (p, "false") == 0)
        *e = false;
      else
        BA0_RAISE_PARSER_EXCEPTION (BA0_ERRBOOL);
    }
  else
    BA0_RAISE_PARSER_EXCEPTION (BA0_ERRINT);

  return e;
}

/*
 * texinfo: ba0_printf_bool
 * General printing function for machine integers.
 * It can be called using @code{ba0_printf/%bool}.
 * The bool is printed as @code{true} or @code{false}.
 */

BA0_DLL void
ba0_printf_bool (
    void *z)
{
  ba0_bool b = (ba0_bool) z;
  if (b)
    ba0_put_string ("true");
  else
    ba0_put_string ("false");
}
