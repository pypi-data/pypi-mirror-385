#include "ba0_exception.h"
#include "ba0_basic_io.h"
#include "ba0_global.h"

/*
 * OUTPUT
 */

#define ba0_output		ba0_global.basic_io.output
#define ba0_input		ba0_global.basic_io.input

#define ba0_output_stack	ba0_global.basic_io.output_stack
#define ba0_output_sp		ba0_global.basic_io.output_sp

#define ba0_input_stack		ba0_global.basic_io.input_stack
#define ba0_input_sp            ba0_global.basic_io.input_sp

/*
 * texinfo: ba0_record_output
 * Push the current value of the output 
 * in the stack @code{ba0_global.basic_io.output_stack}.
 * Exception @code{BA0_ERRSOV} is raised if the saving stack is full.
 */

BA0_DLL void
ba0_record_output (
    void)
{
  if (ba0_output_sp >= BA0_BASIC_IO_SIZE_STACK)
    BA0_RAISE_EXCEPTION (BA0_ERRSOV);
  ba0_output_stack[ba0_output_sp++] = ba0_output;
}

/*
 * texinfo: ba0_restore_output
 * Pull the top element from the
 * stack @code{ba0_global.basic_io.output_stack}.
 * Exception @code{BA0_ERRSOV} is raised if the saving stack is empty.
 */

BA0_DLL void
ba0_restore_output (
    void)
{
  if (ba0_output_sp <= 0)
    BA0_RAISE_EXCEPTION (BA0_ERRSOV);
  ba0_output = ba0_output_stack[--ba0_output_sp];
}

/*
 * texinfo: ba0_set_output_FILE
 * Make all output functions write in the file @var{f}.
 */

BA0_DLL void
ba0_set_output_FILE (
    FILE *f)
{
  ba0_output.vers = ba0_file_device;
  ba0_output.file_flux = f;
  ba0_output.counter = 0;
}

/*
 * texinfo: ba0_set_output_string
 * Make all output functions write in @var{s}, which must points
 * to a large enough area.
 */

BA0_DLL void
ba0_set_output_string (
    char *s)
{
  ba0_output.vers = ba0_string_device;
  ba0_output.string_flux = s;
  ba0_output.indice = 0;
  s[0] = '\0';
}

/*
 * texinfo: ba0_set_output_counter
 * Make all output functions write on a counter (automatically reset to zero).
 * This function may be used to determine the length of an expression before
 * storing it in a string.
 */

BA0_DLL void
ba0_set_output_counter (
    void)
{
  ba0_output.vers = ba0_counter_device;
  ba0_output.counter = 0;
}

/*
 * texinfo: ba0_output_counter
 * Return the value of the counter.
 */

BA0_DLL ba0_int_p
ba0_output_counter (
    void)
{
  if (ba0_output.vers != ba0_counter_device)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  return ba0_output.counter;
}

/*
 * texinfo: ba0_reset_output
 * Reset the output to its default state (i.e. to @code{stdout}) and
 * @code{ba0_output_line_length} to its default value.
 */

BA0_DLL void
ba0_reset_output (
    void)
{
  ba0_set_output_FILE (stdout);
  ba0_output_sp = 0;
  ba0_output_line_length = BA0_DEFAULT_OUTPUT_LINE_LENGTH;
}

/*
 * texinfo: ba0_put_char
 * Send @var{c} to the output.
 * If the output is a file then newlines may be inserted (see above). 
 */

BA0_DLL void
ba0_put_char (
    char c)
{
  switch (ba0_output.vers)
    {
    case ba0_string_device:
      ba0_output.string_flux[ba0_output.indice++] = c;
      ba0_output.string_flux[ba0_output.indice] = '\0';
      break;
    case ba0_counter_device:
      ba0_output.counter++;
      break;
    case ba0_file_device:
      {
        if (c == '\n')
          {
            ba0_output.counter = 0;
            fputc ('\n', ba0_output.file_flux);
          }
        else if (ba0_output_line_length != 0 &&
            ba0_output.counter + 1 >= ba0_output_line_length)
          {
            ba0_output.counter = 1;
            fputc ('\n', ba0_output.file_flux);
            fputc (c, ba0_output.file_flux);
          }
        else
          {
            ba0_output.counter++;
            fputc (c, ba0_output.file_flux);
          }
      }
    }
}

/*
 * texinfo: ba0_put_string
 * Send the string pointed to by @var{s} to the output.
 * If the output is a file then newlines may be inserted (see above).
 * The string is however not split.
 */

BA0_DLL void
ba0_put_string (
    void *s)
{
  char *z = (char *) s;

  switch (ba0_output.vers)
    {
    case ba0_string_device:
      strcpy (ba0_output.string_flux + ba0_output.indice, z);
      ba0_output.indice += strlen (z);
      break;
    case ba0_counter_device:
      ba0_output.counter += strlen (z);
      break;
    case ba0_file_device:
      {
        int l = (int) strlen (z);
        int i;
        if (ba0_output_line_length != 0 &&
            l + ba0_output.counter >= ba0_output_line_length)
          {
            ba0_output.counter = 0;
            fputc ('\n', ba0_output.file_flux);
          }
        fputs (z, ba0_output.file_flux);
        for (i = 0; z[i] != '\0'; i++)
          if (z[i] == '\n')
            ba0_output.counter = 0;
          else
            ba0_output.counter++;
      }
    }
}

/*
 * texinfo: ba0_put_int_p
 * Print @var{n} in base 10 and send the string to the output.
 */

BA0_DLL void
ba0_put_int_p (
    ba0_int_p n)
{
  char buffer[4 * BA0_NBBITS_INT_P];
  sprintf (buffer, BA0_FORMAT_INT_P, n);
  ba0_put_string (buffer);
}

/*
 * texinfo: ba0_put_hexint_p
 * Print @var{n} in base @math{16} and send the string to the output.
 */

BA0_DLL void
ba0_put_hexint_p (
    ba0_int_p n)
{
  char buffer[4 * BA0_NBBITS_INT_P];
  sprintf (buffer, BA0_FORMAT_HEXINT_P, n);
  ba0_put_string (buffer);
}

/*
 * INPUT
 */

/*
 * texinfo: ba0_record_input
 * Push the current value of the input in the stack
 * @code{ba0_global.basic_io.input_stack}.
 * Exception @code{BA0_ERRSOV} is raised if the saving stack is full.
 */

BA0_DLL void
ba0_record_input (
    void)
{
  if (ba0_input_sp >= BA0_BASIC_IO_SIZE_STACK)
    BA0_RAISE_EXCEPTION (BA0_ERRSOV);
  ba0_input_stack[ba0_input_sp++] = ba0_input;
}

/*
 * texinfo: ba0_restore_input
 * Pull the top element from the stack
 * @code{ba0_global.basic_io.input_stack}.
 * Exception @code{BA0_ERRSOV} is raised if the saving stack is empty.
 */

BA0_DLL void
ba0_restore_input (
    void)
{
  if (ba0_input_sp <= 0)
    BA0_RAISE_EXCEPTION (BA0_ERRSOV);
  ba0_input = ba0_input_stack[--ba0_input_sp];
}

/*
 * texinfo: ba0_set_input_FILE
 * Make all input functions read in the file @var{f}.
 */

BA0_DLL void
ba0_set_input_FILE (
    FILE *f)
{
  ba0_input.from = ba0_file_device;
  ba0_input.file_flux = f;
}

/*
 * texinfo: ba0_set_input_string
 * Make all input functions read in the string @var{s}.
 */

BA0_DLL void
ba0_set_input_string (
    char *s)
{
  ba0_input.from = ba0_string_device;
  ba0_input.string_flux = s;
  ba0_input.indice = 0;
}

/*
 * texinfo: ba0_reset_input
 * Reset the input to its initial state (i.e. from @code{stdin}).
 */

BA0_DLL void
ba0_reset_input (
    void)
{
  ba0_set_input_FILE (stdin);
  ba0_input_sp = 0;
}

static int
_mygetc (
    void)
{
  int c = '\0';

  switch (ba0_input.from)
    {
    case ba0_file_device:
      c = fgetc (ba0_input.file_flux);
      break;
    case ba0_counter_device:
      BA0_RAISE_EXCEPTION (BA0_ERRALG);
      break;
    case ba0_string_device:
      if (ba0_input.string_flux[ba0_input.indice] == '\0')
        c = EOF;
      else
        c = (unsigned int) ba0_input.string_flux[ba0_input.indice++];
    }
  return c;
}

/*
 * texinfo: ba0_isatty_input
 * Return @code{true} if the input is a @emph{tty}, @code{false} otherwise.
 */

BA0_DLL bool
ba0_isatty_input (
    void)
{
  return (ba0_input.from == ba0_file_device &&
      ba0_isatty (ba0_fileno (ba0_input.file_flux)));
}

/*
   Reads a character.
   A trailing slash at the end of the line is skipped together with all
	the following spaces.
*/

/*
 * texinfo: ba0_get_char
 * Read a character on the input.
 * Returns @code{EOF} when the end of the input stream is reached.
 * Backslashes and all the spaces that follow them are skipped.
 */

BA0_DLL int
ba0_get_char (
    void)
{
  int c = _mygetc ();
  if (c == '\\')
    do
      c = _mygetc ();
    while (c != EOF && isspace (c));
  return c;
}

/*
   Replaces c on the input stream.
   If the input stream is a string, this operation must not modify
   the stream (i.e. one cannot unget a character which was not read).
   Exception BA0_ERRALG is raised otherwise.
   This exception is also raised if too many characters are ungot.
*/

/*
 * texinfo: ba0_unget_char
 * Replace @var{c} on the input.
 * If the input is a string, this operation must not modify
 * the stream (i.e. one cannot unget a character which was not read).
 * Exception @code{BA0_ERRALG} is raised otherwise.
 * This exception is also raised if too many characters are ungot.
 */

BA0_DLL void
ba0_unget_char (
    int c)
{
  switch (ba0_input.from)
    {
    case ba0_file_device:
      if (c != EOF)
        ungetc (c, ba0_input.file_flux);
      break;
    case ba0_counter_device:
      BA0_RAISE_EXCEPTION (BA0_ERRALG);
      break;
    case ba0_string_device:
      if (ba0_input.indice == 0)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
      else if (c != EOF)
        {
          if (c != ba0_input.string_flux[ba0_input.indice - 1])
            BA0_RAISE_EXCEPTION (BA0_ERRALG);
          else
            ba0_input.indice--;
        }
    }
}
