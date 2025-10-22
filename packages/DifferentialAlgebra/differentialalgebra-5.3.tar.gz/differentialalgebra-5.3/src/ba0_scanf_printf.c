#include "ba0_exception.h"
#include "ba0_stack.h"
#include "ba0_format.h"
#include "ba0_basic_io.h"
#include "ba0_analex.h"
#include "ba0_scanf.h"
#include "ba0_printf.h"
#include "ba0_scanf_printf.h"
#include "ba0_global.h"

/*
 * texinfo: ba0_scanf_printf
 * 
 * Kind of a pipeline using formats.
 * The objects corresponding to @var{pf} are printed in a buffer following
 * the @var{pf} format. They are then read into the objects corresponding
 * to @var{sf} using this format.
 * Example. Assume @var{P} is a differential polynomial, @var{u} is a dependent
 * variable and @var{x} a derivation. The following instruction sets @var{P} to
 * @math{u_x^2 - 4u}.
 * @example
 * ba0_scanf_printf ("%Az", "%v[%y]^2 - 4*%v", P, u, x, u);
 * @end example
 */

BA0_DLL void
ba0_scanf_printf (
    char *sf,
    char *pf,
    ...)
{
  struct ba0_format *sformat, *pformat;
  void **sobjet, **pobjet;
  va_list arg;
  ba0_int_p i;
  char *buffer = (char *) 0;
  struct ba0_mark M;

  sformat = ba0_get_format (sf);
  pformat = ba0_get_format (pf);

  ba0_push_another_stack ();
  ba0_record (&M);

  sobjet = (void **) ba0_alloc (sizeof (void *) * sformat->linknmb);
  pobjet = (void **) ba0_alloc (sizeof (void *) * pformat->linknmb);

  va_start (arg, pf);
  for (i = 0; i < sformat->linknmb; i++)
    sobjet[i] = va_arg (arg, void *);
  for (i = 0; i < pformat->linknmb; i++)
    pobjet[i] = va_arg (arg, void *);
  va_end (arg);

  ba0_record_output ();

  BA0_TRY
  {
    ba0_set_output_counter ();
    ba0__printf__ (pformat, pobjet);
    buffer = (char *) ba0_alloc (ba0_output_counter () + 1);
    ba0_set_output_string (buffer);
    ba0__printf__ (pformat, pobjet);
    ba0_restore_output ();
  }
  BA0_CATCH
  {
    ba0_restore_output ();
    BA0_RE_RAISE_EXCEPTION;
  }
  BA0_ENDTRY;

  ba0_pull_stack ();

  ba0_record_analex ();
  ba0_set_analex_string (buffer);

  BA0_TRY
  {
    ba0_get_token_analex ();
    ba0__scanf__ (sformat, sobjet, true);
    ba0_restore_analex ();
  }
  BA0_CATCH
  {
    ba0_restore_analex ();
    BA0_RE_RAISE_EXCEPTION;
  }
  BA0_ENDTRY;

  ba0_restore (&M);
}
