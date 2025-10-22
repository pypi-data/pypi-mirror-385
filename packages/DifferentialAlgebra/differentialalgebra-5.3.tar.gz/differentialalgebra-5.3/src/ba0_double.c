#include "ba0_double.h"
#include "ba0_mesgerr.h"
#include "ba0_basic_io.h"
#include "ba0_analex.h"
#include "ba0_garbage.h"
#include "ba0_exception.h"
#include "ba0_string.h"
#include "ba0_array.h"

/*
 * texinfo: ba0_new_double
 * Allocate a @code{double} in the current stack and return its address.
 */

BA0_DLL ba0_double
ba0_new_double (
    void)
{
  return (ba0_double) ba0_alloc (sizeof (double));
}

/*
 * texinfo: ba0_scanf_double
 * The general parsing function for doubles.
 * It can be called via @code{ba0_scanf/%le}.
 * Abnormal doubles such as @code{inf} and @code{nan} are allowed.
 */

BA0_DLL void *
ba0_scanf_double (
    void *z)
{
  struct ba0_mark M;
  struct ba0_tableof_string tokseq;
  ba0_int_p nbtokens;
  ba0_double e;
  bool normal, minus_sign;
  char *p;

  ba0_get_settings_analex (&nbtokens, 0);
  if (nbtokens < 10)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_init_table ((struct ba0_table *) &tokseq);
  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_realloc_table ((struct ba0_table *) &tokseq, 10);
  ba0_pull_stack ();

  if (z == (void *) 0)
    e = (ba0_double) ba0_alloc (sizeof (double));
  else
    e = (ba0_double) z;
/*
 * Possibly start with a minus sign.
 */
  if (ba0_sign_token_analex ("-"))
    {
      ba0_get_token_analex ();
      minus_sign = true;
    }
  else
    {
      if (ba0_sign_token_analex ("+"))
        ba0_get_token_analex ();
      minus_sign = false;
    }
/*
 * Possibly a non normal double
 */
  if (ba0_type_token_analex () == ba0_string_token)
    {
      tokseq.tab[tokseq.size] = ba0_value_token_analex ();
      tokseq.size += 1;
      normal = false;
    }
  else
    normal = true;
/*
 * Possibly a non empty integer part
 * Spaces are authorized between the minus sign and what follows.
 */
  if (normal && ba0_type_token_analex () == ba0_integer_token)
    {
      tokseq.tab[tokseq.size] = ba0_value_token_analex ();
      tokseq.size += 1;
      ba0_get_token_analex ();
    }
/*
 * Possibly a dot plus a possible fractional part
 */
  if (normal &&
      (tokseq.size == 0 || !ba0_spaces_before_token_analex ()) &&
      ba0_sign_token_analex ("."))
    {
      tokseq.tab[tokseq.size] = ".";
      tokseq.size += 1;
      ba0_get_token_analex ();
      if (!ba0_spaces_before_token_analex () &&
          ba0_type_token_analex () == ba0_integer_token)
        {
          tokseq.tab[tokseq.size] = ba0_value_token_analex ();
          tokseq.size += 1;
          ba0_get_token_analex ();
        }
    }
/*
 * There must be a mantissa
 */
  if (normal && tokseq.size == 0)
    BA0_RAISE_PARSER_EXCEPTION (BA0_ERRFLT);
/*
 * Possibly an exponent
 */
  if (normal)
    {
      p = ba0_value_token_analex ();
      if (!ba0_spaces_before_token_analex () &&
          (p[0] == 'e' || p[0] == 'E' || p[0] == '@') &&
          (p[1] == '\0' || isdigit ((int) p[1])))
        {
          tokseq.tab[tokseq.size] = "e";
          tokseq.size += 1;
          if (isdigit ((int) p[1]))
            {
              ba0_int_p i;
              i = 2;
              while (isdigit ((int) p[i]))
                i++;
              if (p[i] == '\0')
                ba0_unget_given_token_analex (p + 1, ba0_integer_token, false);
              else
                {
                  ba0_push_another_stack ();
                  p = ba0_strdup (p);
                  ba0_pull_stack ();
                  ba0_unget_given_token_analex (p + i, ba0_string_token, false);
                  p[i] = '\0';
                  ba0_unget_given_token_analex
                      (p + 1, ba0_integer_token, false);
                }
            }

          ba0_get_token_analex ();
          if (!ba0_spaces_before_token_analex () &&
              ba0_type_token_analex () == ba0_integer_token)
            {
              tokseq.tab[tokseq.size] = ba0_value_token_analex ();
              tokseq.size += 1;
            }
          else if (!ba0_spaces_before_token_analex () &&
              (ba0_sign_token_analex ("+") || ba0_sign_token_analex ("-")))
            {
              tokseq.tab[tokseq.size] = ba0_value_token_analex ();
              tokseq.size += 1;
              ba0_get_token_analex ();
              if (ba0_spaces_before_token_analex () ||
                  ba0_type_token_analex () != ba0_integer_token)
                BA0_RAISE_PARSER_EXCEPTION (BA0_ERRFLT);
              tokseq.tab[tokseq.size] = ba0_value_token_analex ();
              tokseq.size += 1;
            }
          else
            BA0_RAISE_PARSER_EXCEPTION (BA0_ERRFLT);
        }
      else
        ba0_unget_token_analex (1);
    }

  ba0_push_another_stack ();
  p = ba0_strcat (&tokseq);
  ba0_pull_stack ();
#if defined (_MSC_VER)
  *e = ba0_atof (p);
#else
  *e = atof (p);
#endif
  if (minus_sign)
    {
#if defined (_MSC_VER)
      if (ba0_isnan (*e))
#else
      if (isnan (*e))
#endif
        BA0_RAISE_PARSER_EXCEPTION (BA0_ERRFLT);
      *e = -*e;
    }
  ba0_restore (&M);
  return e;
}

/*
 * texinfo: ba0_printf_double
 * The general printing function for doubles.
 * It can be called via @code{ba0_printf/%le}.
 */

BA0_DLL void
ba0_printf_double (
    void *z)
{
  double f;
  char buffer[64];
  ba0_int_p i;

  f = *(ba0_double) z;
/*
 * To avoid these stupid -0.0 !
 */
  if (f == 0.0)
    f = 0.0;
  sprintf (buffer, "%f", f);
  i = strlen (buffer) - 1;
  while (i > 0 && buffer[i] == '0')
    {
      buffer[i] = '\0';
      i -= 1;
    }
  ba0_put_string (buffer);
}

/*
 * Readonly static data
 */

static char _double[] = "double";

BA0_DLL ba0_int_p
ba0_garbage1_double (
    void *z,
    enum ba0_garbage_code code)
{
  if (code == ba0_isolated)
    {
      ba0_new_gc_info (z, sizeof (double), _double);
      return 1;
    }
  else
    return 0;
}

BA0_DLL void *
ba0_garbage2_double (
    void *z,
    enum ba0_garbage_code code)
{
  if (code == ba0_isolated)
    return ba0_new_addr_gc_info (z, _double);
  else
    return z;
}

BA0_DLL void *
ba0_copy_double (
    void *z)
{
  ba0_double e;

  e = ba0_new_double ();
  *e = *(ba0_double) z;
  return e;
}

/*
 * Suggested by Alexander Ocher
 */

/*
 * texinfo: ba0_isnan
 * Return @code{true} if @var{x} is @code{nan} else @code{false}.
 */

BA0_DLL int
ba0_isnan (
    double x)
{
  volatile double temp = x;
  return temp != x;
}

/*
 * texinfo: ba0_isinf
 * Return @code{true} if @var{x} is @code{inf} or @code{-inf} else @code{false}.
 */

BA0_DLL int
ba0_isinf (
    double x)
{
  volatile double temp = x;
  if ((temp == x) && ((temp - x) != 0.0))
    return (x < 0.0 ? -1 : 1);
  else
    return 0;
}

/*
 * texinfo: ba0_atof
 * Convert the string @var{s} into a double.
 * The string @var{s} may contain @code{nan}, @code{inf} or @code{-inf}.
 * Errors are not detected.
 */

BA0_DLL double
ba0_atof (
    char *s)
{
/*
  static unsigned char nan[] =
      { 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff };
   Problem of endianness.

    static unsigned char posinf [] = 
                { 0x7f, 0xf0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 }; 
    static unsigned char neginf [] = 
                { 0x7f, 0xf0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 }; 
 */
  if (ba0_strncasecmp (s, "nan", 3) == 0)
    return NAN;
  else if (ba0_strncasecmp (s, "inf", 3) == 0)
    return INFINITY;
  else if (ba0_strncasecmp (s, "-inf", 4) == 0)
    return -INFINITY;
  else
    return atof (s);
}

/*
 * texinfo: ba0_sizeof_arrayof_double
 * Return the size needed to perform a copy of @var{A}.
 * If @var{code} is @code{ba0_embedded} then @var{A} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account.
 */

BA0_DLL unsigned ba0_int_p
ba0_sizeof_arrayof_double (
    struct ba0_arrayof_double *A,
    enum ba0_garbage_code code)
{
  unsigned ba0_int_p size;

  if (code == ba0_isolated)
    size = ba0_allocated_size (sizeof (struct ba0_arrayof_double));
  else
    size = 0;
  if (A->size > 0)
    size += ba0_allocated_size (A->size * sizeof (double));
  return size;
}
