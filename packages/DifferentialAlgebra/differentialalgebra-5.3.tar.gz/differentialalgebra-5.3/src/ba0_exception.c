#include "ba0_garbage.h"
#include "ba0_copy.h"
#include "ba0_exception.h"
#include "ba0_global.h"

/*
 * texinfo: ba0_reset_exception_extra_stack
 * Empty the exception extra stack.
 */

BA0_DLL void
ba0_reset_exception_extra_stack (
    void)
{
  ba0_global.exception.extra_stack.size = 0;
}

/*
 * texinfo: ba0_push_exception_extra_stack
 * Stack @var{p} and @var{r} in the exception extra stack.
 */

BA0_DLL void
ba0_push_exception_extra_stack (
    ba0_int_p *pointer,
    void (*restore) (ba0_int_p))
{
  ba0_int_p size = ba0_global.exception.extra_stack.size;
  ba0_global.exception.extra_stack.size += 1;

  if (size >= BA0_SIZE_EXCEPTION_EXTRA_STACK)
    BA0_RAISE_EXCEPTION (BA0_ERRSOV);
  ba0_global.exception.extra_stack.tab[size].pointer = pointer;
  ba0_global.exception.extra_stack.tab[size].restore = restore;
}

/*
 * texinfo: ba0_pull_exception_extra_stack
 * Undo the effect of the last call to @code{ba0_push_exception_extra_stack}.
 */

BA0_DLL void
ba0_pull_exception_extra_stack (
    void)
{
  ba0_global.exception.extra_stack.size -= 1;
  ba0_int_p size = ba0_global.exception.extra_stack.size;

  if (size < 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
}

static void
ba0_reset_exception_log (
    void)
{
  memset (ba0_global.exception.log.tab, 0,
      sizeof (ba0_global.exception.log.tab));
  ba0_global.exception.log.qp = 0;
}

/*
 * texinfo: ba0_reset_exception
 * Empty the stack of exception catching points.
 */

BA0_DLL void
ba0_reset_exception (
    void)
{
  ba0_global.exception.stack.size = 0;
  ba0_global.exception.within_push_exception = false;
  ba0_reset_exception_log ();
}

/*
 * texinfo: ba0_push_exception
 * Set an exception catching point.
 * This function is called by @code{BA0_TRY} and stores some information
 * in the local variable @var{code} and some other information in
 * the exception stack stored in @code{ba0_global.exception}.
 * The exception log is reset.
 */

BA0_DLL void
ba0_push_exception (
    struct ba0_exception_code *code)
{
  if (ba0_global.exception.within_push_exception)
    {
      ba0_global.exception.within_push_exception = false;
      BA0_CERR (BA0_ERRALG);
    }
  ba0_global.exception.within_push_exception = true;

  ba0_reset_exception_log ();

  if (ba0_global.exception.stack.size >= BA0_SIZE_EXCEPTION_STACK)
    {
      ba0_global.exception.within_push_exception = false;
      BA0_CERR (BA0_ERRSOV);
    }

  ba0_push_stack (&ba0_global.stack.main);
  ba0_record (&code->main);
  ba0_pull_stack ();

  ba0_push_stack (&ba0_global.stack.second);
  ba0_record (&code->second);
  ba0_pull_stack ();

  code->stack_of_stacks_size = ba0_global.stack.stack_of_stacks.size;

  ba0_global.exception.stack.tab[ba0_global.exception.stack.size].code = code;

  for (int i = 0; i < ba0_global.exception.extra_stack.size; i++)
    code->extra_stack.tab[i] = *ba0_global.exception.extra_stack.tab[i].pointer;
  code->extra_stack.size = ba0_global.exception.extra_stack.size;

  ba0_global.exception.stack.size += 1;

  code->exception_stack_size = ba0_global.exception.stack.size;
  code->cancelled = false;

  ba0_global.exception.within_push_exception = false;
}


/*
 * texinfo: ba0_pull_exception
 * Undo the last call to @code{BA0_PUSH_EXCEPTION}.
 * Check for debugging purpose that the value of the exception stack
 * pointer is correct.
 */

BA0_DLL void
ba0_pull_exception (
    struct ba0_exception_code *code)
{
  if (code->cancelled)
    return;

  if (ba0_global.exception.stack.size != code->exception_stack_size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  ba0_global.exception.stack.size -= 1;
  code->cancelled = true;
}

/*
 * texinfo: ba0_exception_is_set
 * Return @code{true} if the exception catching point has just been set
 * and @code{false} otherwise.
 */

BA0_DLL bool
ba0_exception_is_set (
    struct ba0_exception_code *code)
{
  return code->jmp_code == 0;
}

/*
 * texinfo: ba0_exception_is_raised
 * Return @code{true} if the exception catching point is catching an exception
 * and @code{false} otherwise.
 */

BA0_DLL bool
ba0_exception_is_raised (
    struct ba0_exception_code *code)
{
  return code->jmp_code != 0;
}

/*
 * texinfo: ba0_raise_exception
 * Raise exception @var{raised} from file @var{file} at line @var{line}.
 * These data are queued in the exception log of @code{ba0_global.exception}.
 * Exceptions @code{BA0_ERRALG} or @code{BA0_ERRNYP} cause an extra error
 * message of @code{stderr}.
 */

BA0_DLL void
ba0_raise_exception (
    char *file,
    int line,
    char *raised)
{
  ba0_int_p i, sp, qp;

  if (ba0_global.exception.log.qp >= BA0_SIZE_EXCEPTION_LOG - 1)
    {
      ba0_int_p i = 0;
      ba0_int_p j = (BA0_SIZE_EXCEPTION_LOG + 1) / 2;
      while (j < BA0_SIZE_EXCEPTION_LOG)
        {
          ba0_global.exception.log.tab[i] = ba0_global.exception.log.tab[j];
          memset (&ba0_global.exception.log.tab[j], 0,
              sizeof (ba0_global.exception.log.tab[j]));
          i += 1;
          j += 1;
        }
      ba0_global.exception.log.qp = i;
    }
  qp = ba0_global.exception.log.qp;
  ba0_global.exception.log.tab[qp].file = file;
  ba0_global.exception.log.tab[qp].line = line;
  ba0_global.exception.log.tab[qp].raised = raised;
  ba0_global.exception.log.qp += 1;

  if (raised == BA0_ERRALG || raised == BA0_ERRNYP)
    fprintf (stderr, "trapped '%s' at file: %s:%d\n", raised, file, line);

  ba0_global.exception.stack.size -= 1;
  sp = ba0_global.exception.stack.size;

  if (sp < 0)
    {
      sprintf (ba0_global.exception.mesg_cerr, "%s (%s)", BA0_ERRNCE, raised);
      BA0_CERR (ba0_global.exception.mesg_cerr);
    }

  struct ba0_exception_code *code = ba0_global.exception.stack.tab[sp].code;

  ba0_global.exception.raised = raised;

  ba0_restore (&code->main);
  ba0_restore (&code->second);

  ba0_global.stack.stack_of_stacks.size = code->stack_of_stacks_size;

  code->cancelled = true;

  for (i = 0; i < ba0_global.exception.extra_stack.size; i++)
    {
      ba0_int_p *pointer = ba0_global.exception.extra_stack.tab[i].pointer;
      void (
          *restore) (
          ba0_int_p) = ba0_global.exception.extra_stack.tab[i].restore;
      if (restore == 0)
        *pointer = code->extra_stack.tab[i];
      else
        (*restore) (code->extra_stack.tab[i]);
    }

  ba0_longjmp (ba0_global.exception.stack.tab[sp].jmp_b.data, 1);
}

/*
 * texinfo: ba0_raise_exception2
 * Variant of @code{ba0_raise_exception}.
 * See the macro @code{BA0_RAISE_EXCEPTION2}.
 */

BA0_DLL void
ba0_raise_exception2 (
    char *file,
    int line,
    char *raised,
    char *f,
    void **o)
{
  struct ba0_stack *H;
  struct ba0_stack *Hbar;
  ba0_int_p i, sp, qp;

  if (ba0_global.exception.log.qp >= BA0_SIZE_EXCEPTION_LOG - 1)
    {
      ba0_int_p i = 0;
      ba0_int_p j = (BA0_SIZE_EXCEPTION_LOG + 1) / 2;
      while (j < BA0_SIZE_EXCEPTION_LOG)
        {
          ba0_global.exception.log.tab[i] = ba0_global.exception.log.tab[j];
          memset (&ba0_global.exception.log.tab[j], 0,
              sizeof (ba0_global.exception.log.tab[j]));
          i += 1;
          j += 1;
        }
      ba0_global.exception.log.qp = i;
    }
  qp = ba0_global.exception.log.qp;
  ba0_global.exception.log.tab[qp].file = file;
  ba0_global.exception.log.tab[qp].line = line;
  ba0_global.exception.log.tab[qp].raised = raised;
  ba0_global.exception.log.qp += 1;

  ba0_global.exception.stack.size -= 1;
  sp = ba0_global.exception.stack.size;

  if (sp < 0)
    {
      sprintf (ba0_global.exception.mesg_cerr, "%s (%s)", BA0_ERRNCE, raised);
      BA0_CERR (ba0_global.exception.mesg_cerr);
    }

  struct ba0_exception_code *code = ba0_global.exception.stack.tab[sp].code;

  ba0_global.exception.raised = raised;

  H = ba0_which_stack (*o);
  if (H != &ba0_global.stack.main && H != &ba0_global.stack.second)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  Hbar = ba0_global.stack.stack_of_stacks.tab[code->stack_of_stacks_size - 1];
/*
 * H    = the stack which contains the object *o to be returned
 * Hbar = the stack which is going to be the current stack
 *        at the exception catching point
 */
  if (Hbar == &ba0_global.stack.main)
    {
      if (Hbar == H)
        {
          ba0_garbage (f, &code->main, o);
          ba0_restore (&code->second);
        }
      else
        {
          ba0_restore (&code->main);
          ba0_push_stack (Hbar);
          *o = ba0_copy (f, *o);
          ba0_restore (&code->second);
        }
    }
  else
    {
      if (Hbar == H)
        {
          ba0_garbage (f, &code->second, o);
          ba0_restore (&code->main);
        }
      else
        {
          ba0_restore (&code->second);
          ba0_push_stack (Hbar);
          *o = ba0_copy (f, *o);
          ba0_restore (&code->main);
        }
    }

  ba0_global.stack.stack_of_stacks.size = code->stack_of_stacks_size;

  code->cancelled = true;

  for (i = 0; i < ba0_global.exception.extra_stack.size; i++)
    {
      ba0_int_p *pointer = ba0_global.exception.extra_stack.tab[i].pointer;
      void (
          *restore) (
          ba0_int_p) = ba0_global.exception.extra_stack.tab[i].restore;
      if (restore == 0)
        *pointer = code->extra_stack.tab[i];
      else
        (*restore) (code->extra_stack.tab[i]);
    }

  ba0_longjmp (ba0_global.exception.stack.tab[sp].jmp_b.data, 1);
}

/*
 * texinfo: ba0_cerr
 * The @code{abort} function.
 * The exception log is dumped on @code{stderr}.
 */

BA0_DLL void
ba0_cerr (
    char *fname,
    int line,
    char *raised)
{
  ba0_int_p i;

  fprintf (stderr, "Error in file %s:%d\n%s\n", fname, line, raised);
  fprintf (stderr, "Exception log (from most recent to oldest):\n");
  for (i = 0; i < ba0_global.exception.log.qp; i++)
    {
      fprintf (stderr, "    ");
      fprintf (stderr, "file: %s:%d (%s)\n",
          ba0_global.exception.log.tab[i].file,
          ba0_global.exception.log.tab[i].line,
          ba0_global.exception.log.tab[i].raised);
    }
  exit (1);
}
