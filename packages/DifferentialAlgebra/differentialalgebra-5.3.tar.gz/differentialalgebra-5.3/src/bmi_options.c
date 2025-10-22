#include <blad.h>
#include "bmi_indices.h"
#include "bmi_mesgerr.h"
#include "bmi_options.h"

void
bmi_init_options (
    struct bmi_options *options)
{
  memset (options, 0, sizeof (struct bmi_options));
  strcpy (options->cellsize, BMI_IX_large);
  options->input_notation = options->output_notation = bmi_jet_notation;
}

void
bmi_clear_options (
    struct bmi_options *options)
{
  memset (options, 0, sizeof (struct bmi_options));
}

/*
 * Return arg from "jet(arg)"
 * arg may either be a non-empty string starting with [A-Z_]
 *                or a signed integer
 * There may be spaces around the parentheses.
 * There may even not be parentheses at all.
 *
 * Return 0 if unsuccessful
 * If successful, then *is_number is set to true/false depending on arg
 * The returned string is dynamically allocated
 */

static char *
get_jet0_argument (
    char *s,
    bool *is_number)
{
  int i, j, k;
  bool parentheses, minus_sign;
  char *r;

  i = BMI_jet_LENGTH;
  while (isspace ((int) (s[i] & 0x7f)))
    i += 1;

  if (s[i] == '(')
    {
      i += 1;
      while (isspace ((int) (s[i] & 0x7f)))
        i += 1;
      parentheses = true;
    }
  else
    parentheses = false;

  j = i;

  if (s[j] == '-')
    {
      j += 1;
      minus_sign = true;
    }
  else
    minus_sign = false;

  if (isdigit ((int) (s[j] & 0x7f)))
    {
      j += 1;
      *is_number = true;
    }
  else
    *is_number = false;

  if (minus_sign && !*is_number)
    return false;

  if (*is_number)
    while (isdigit ((int) (s[j] & 0x7f)))
      j += 1;
  else
    while (isalnum ((int) (s[j] & 0x7f)) || s[j] == '_')
      j += 1;

  if (j == i)
    return (char *) 0;

  if (parentheses)
    {
      k = j;
      while (isspace ((int) (s[k] & 0x7f)))
        k += 1;
      if (s[k] != ')')
        return (char *) 0;
    }

  r = (char *) malloc (j - i + 1);
  strncpy (r, s + i, j - i);
  r[j - i] = '\0';

  return r;
}

/*
 * Convert a notation from string to enum bmi_typeof_notation.
 * In case of the jet(arg) notation, call bav_set_settings_variable
 *  to change the string used in the jet notation 
 */

static bool
bmi_set_typeof_notation (
    enum bmi_typeof_notation *type,
    char *s,
    bool input)
{
  bool b;

  b = true;
  if (strcmp (s, BMI_IX_jet) == 0)
    *type = bmi_jet_notation;
  else if (strcmp (s, BMI_IX_tjet) == 0)
    *type = bmi_tjet_notation;
  else if (strncmp (s, BMI_IX_jet0, BMI_jet_LENGTH) == 0)
    {
      bool is_number;
      char *arg = get_jet0_argument (s, &is_number);

      if (arg == (char *) 0)
        b = false;
      else
        {
          char *jet0_input, *jet0_output;

          bav_get_settings_variable (0, 0, &jet0_input, &jet0_output, 0);
          if (input)
            bav_set_settings_variable (0, 0, arg, jet0_output, 0);
          else if (is_number)
            bav_set_settings_variable (0, 0, jet0_input, arg, 0);
          else
            {
/*
 * Case: output + symbolic arg
 * Protect arg
 */
              char *arg2 = (char *) malloc (strlen (arg) + 20);
              sprintf (arg2, "sympy.Symbol('%s')", arg);
              free (arg);
              bav_set_settings_variable (0, 0, jet0_input, arg2, 0);
            }
          *type = bmi_jet0_notation;
        }
    }
  else if (strcmp (s, BMI_IX_diff) == 0)
    *type = bmi_diff_notation;
  else if (strcmp (s, BMI_IX_udif) == 0)
    *type = bmi_udif_notation;
  else if (strcmp (s, BMI_IX_D) == 0)
    *type = bmi_D_notation;
  else if (strcmp (s, BMI_IX_Derivative) == 0)
    *type = bmi_Derivative_notation;
  else
    b = false;

  return b;
}

/*
 * blad_eval (Rosenfeld_Groebner (...), notation=diff, memory=100)
 * options = args[0], ..., args[nargs-1]
 */

bool
bmi_set_options (
    struct bmi_options *options,
    struct bmi_callback *callback,
    ALGEB *args,
    long nargs)
{
#if defined (BMI_MEMCHECK)
  if (nargs < 5)
    {
      fprintf (stderr, "bmi fatal error: bad nargs value (%ld)\n", nargs);
      exit (1);
    }
#endif
/*
 * Input_notation
 */
  bmi_set_callback_ALGEB (callback, args[0]);
  if (!bmi_set_typeof_notation
      (&options->input_notation, bmi_string_op (1, callback), true))
    return false;
/*
 * Output_notation
 */
  bmi_set_callback_ALGEB (callback, args[1]);
  if (!bmi_set_typeof_notation
      (&options->output_notation, bmi_string_op (1, callback), false))
    return false;
/*
 * Time_limit
 * Minus sign to call ba0_check_interrupt
 */
  bmi_set_callback_ALGEB (callback, args[2]);
  options->time_limit = -atoi (bmi_string_op (1, callback));
  if (options->time_limit == 0)
    options->time_limit = -LONG_MAX;
/*
 * Memory_limit
 */
  bmi_set_callback_ALGEB (callback, args[3]);
  options->memory_limit = atoi (bmi_string_op (1, callback));
/*
 * Cell_size
 */
  bmi_set_callback_ALGEB (callback, args[4]);
  strcpy (options->cellsize, bmi_string_op (1, callback));

  return true;
}
