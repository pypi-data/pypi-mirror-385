#include "ba0_common.h"
#include "ba0_exception.h"
#include "ba0_stack.h"
#include "ba0_basic_io.h"
#include "ba0_analex.h"
#include "ba0_string.h"
#include "ba0_indexed_string.h"
#include "ba0_range_indexed_group.h"
#include "ba0_int_p.h"
#include "ba0_bool.h"
#include "ba0_mint_hp.h"
#include "ba0_gmp.h"
#include "ba0_mpzm.h"
#include "ba0_double.h"
#include "ba0_format.h"
#include "ba0_printf.h"
#include "ba0_interval_mpq.h"
#include "ba0_point.h"
#include "ba0_global.h"

/*
 * Time out + Memory out + Interrupt checking
 *
 * check_interrupt	= the function to be called
 * delay_interrupt      = the length of a time interval between two calls
 *
 * time_limit           = the absolute value of the input time limit (restart)
 * memory_limit         = the input memory limit (restart)
 * switch_on_interrupt  = *check_interrupt should be called
 * within_interrupt     = bool to avoid self interruption
 * before_timeout       = the overall remaining time before timeout
 * previous_time        = the value of time() when interrupt was last called
 */

#define ba0_time_limit          ba0_global.common.time_limit

#define ba0_check_interrupt	ba0_initialized_global.common.check_interrupt
#define ba0_delay_interrupt	ba0_initialized_global.common.delay_interrupt
#define ba0_no_oot		ba0_initialized_global.common.no_oot

#define	ba0_switch_on_interrupt	ba0_global.common.switch_on_interrupt
#define ba0_within_interrupt	ba0_global.common.within_interrupt
#define ba0_before_timeout	ba0_global.common.before_timeout
#define ba0_previous_time	ba0_global.common.previous_time

/*
 * texinfo: ba0_get_version
 * Return the version of the library as a string.
 * This string is made of a major number + dot + a minor number 
 * possibly + dot + a micro number.
 */

BA0_DLL char *
ba0_get_version (
    void)
{
  return BLAD_VERSION;
}

/*
 * texinfo: ba0_reset_all_settings
 * Reset all settings to their default values.
 * Must be called outside sequences of calls to the library.
 */

BA0_DLL void
ba0_reset_all_settings (
    void)
{
  ba0_set_settings_common (0);
  ba0_set_settings_interrupt (0, 0);
  ba0_set_settings_no_oot (0);
  ba0_set_settings_no_oom (0);
  ba0_set_settings_stack (0, 0, 0, 0, 0);
  ba0_set_settings_memory_functions (0, 0);
  ba0_set_settings_gmp (0, 0);
  ba0_set_settings_analex (0, 0);
  ba0_set_settings_value (0);
  ba0_set_settings_range_indexed_group (0, 0, false, false);
}

/*
 * texinfo: ba0_cancel_PFE_settings
 * Fill the fields of @var{P} with the corresponding settings variables.
 * Then cancel the @code{PFE} settings.
 */

BA0_DLL void
ba0_cancel_PFE_settings (
    struct ba0_PFE_settings *P)
{
  ba0_get_settings_gmp (&P->set_memory_functions, &P->Integer_PFE);
  ba0_get_settings_range_indexed_group (&P->oper, &P->infinity,
      &P->rhs_included, &P->quote_PFE);
  ba0_set_settings_gmp (P->set_memory_functions, (char *) 0);
  ba0_set_settings_range_indexed_group (P->oper, P->infinity,
      P->rhs_included, (char *) 0);
}

/*
 * texinfo: ba0_restore_PFE_settings
 * Restore the @code{PFE} settings with the content of @var{P}.
 */

BA0_DLL void
ba0_restore_PFE_settings (
    struct ba0_PFE_settings *P)
{
  ba0_set_settings_gmp (P->set_memory_functions, P->Integer_PFE);
  ba0_set_settings_range_indexed_group (P->oper, P->infinity,
      P->rhs_included, P->quote_PFE);
}

/*
 * Set the outer interrupt function as well as the delay.
 */

/*
 * texinfo: ba0_set_settings_interrupt
 * Set the @emph{interrupt} function to @var{check}.
 * For any following sequence of calls starting by a call to @code{ba0_restart}
 * with a negative @var{time_limit} value, the @var{check} function will
 * be called at time interval of length @var{delay}.
 * 
 * The whole interrupt mechanism can be cancelled by providing a zero value 
 * for @var{check}.
 * 
 * This function must be modified outside sequences of calls to the library.
 */

BA0_DLL void
ba0_set_settings_interrupt (
    void (*check) (void),
    time_t delay)
{
  ba0_check_interrupt = check;
  ba0_delay_interrupt = delay < 1 ? 1 : delay;
}

/*
 * texinfo: ba0_set_settings_no_oot
 * Set to @var{b} a settings variable which permits to forbid the
 * exception @code{BA0_ERRALR} (out of time).
 * This settings function can be called within sequences of calls
 * to the library, in order to prevent critical code to be
 * interrupted.
 */

BA0_DLL void
ba0_set_settings_no_oot (
    bool b)
{
  ba0_no_oot = b ? b : false;
}

/*
 * texinfo: ba0_get_settings_no_oot
 * Assign to *@var{b}, the value of the settings variable
 * described above.
 */

BA0_DLL void
ba0_get_settings_no_oot (
    bool *b)
{
  if (b)
    *b = ba0_no_oot;
}

/*
 * texinfo: ba0_set_settings_common
 * Assign @var{level} to @code{ba0_initialized_global.common.restart_level}.
 * The parameter may be zero.
 */

BA0_DLL void
ba0_set_settings_common (
    enum ba0_restart_level level)
{
  ba0_initialized_global.common.restart_level = level ? level : ba0_init_level;
}

/*
 * texinfo: ba0_get_settings_interrupt
 * Assign to @var{check} and @var{delay} the current values of the
 * corresponding variables. Parameters may be zero.
 */

BA0_DLL void
ba0_get_settings_interrupt (
    void (**check) (void),
    time_t *delay)
{
  if (check)
    *check = ba0_check_interrupt;
  if (delay)
    *delay = ba0_delay_interrupt;
}

/*
 * texinfo: ba0_get_settings_common
 * Assign @code{ba0_initialized_global.common.restart_level} to *@var{level}.
 * The parameter may be zero.
 */

BA0_DLL void
ba0_get_settings_common (
    enum ba0_restart_level *level)
{
  if (level)
    *level = ba0_initialized_global.common.restart_level;
}

/*
 * This function has two roles:
 * - checking at regular time interval if the user stroke CTRL-C
 * - checking that the overall computation time is not elapsed.
 */

BA0_DLL void
ba0_process_check_interrupt (
    void)
{
  time_t now, delay;
/*
    ba0_nbcalls_interrupt += 1;
*/
/*
 * ba0_time_limit is zero: no check interrupt system
 */
  if (ba0_time_limit == 0 || ba0_within_interrupt)
    return;
/*
 * ba0_time_limit non zero and ba0_before_timeout zero: time out
 */
  ba0_within_interrupt = true;
  if ((!ba0_no_oot) && ba0_before_timeout <= 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALR);
/*
 * Time out handling
 */
  now = time ((time_t *) 0);
  delay = now - ba0_previous_time;
  ba0_before_timeout -= delay;
  ba0_previous_time = now;
/*
 * Interrupt handling
 */
  if (ba0_switch_on_interrupt && delay >= ba0_delay_interrupt)
    {
      if (!ba0_check_interrupt)
        BA0_RAISE_EXCEPTION (BA0_ERRNCI);
/*
	ba0_nbcalls_effective_interrupt += 1;
*/
      (*ba0_check_interrupt) ();
    }
  ba0_within_interrupt = false;
}

static void
ba0_set_memory_time_and_interrupt (
    ba0_int_p time_limit,
    ba0_int_p memory_limit)
{
/*
 * Memory
 */
#define ONE_MEGA_BYTE	0x100000
  if (memory_limit == 0 || memory_limit * ONE_MEGA_BYTE < 0)
    ba0_global.common.memory_limit = BA0_MAX_INT_P;
  else
    ba0_global.common.memory_limit = memory_limit * ONE_MEGA_BYTE;
/*
 * Time and interrupt
 * Negative time: switch on interrupt
 */
  ba0_within_interrupt = false;
  if (time_limit < 0)
    {
      ba0_time_limit = -time_limit;
      ba0_switch_on_interrupt = true;
    }
  else
    {
      ba0_time_limit = time_limit;
      ba0_switch_on_interrupt = false;
    }
  ba0_previous_time = time ((time_t *) 0);
  ba0_before_timeout = ba0_time_limit;
}

/*
 * texinfo: ba0_restart
 * 
 * The parameter @var{memory_limit} provides the maximal number of megabytes
 * authorized for the coming sequence of calls. The value may be augmented
 * to the minimal reasonable value if it is too small.
 * A value zero means no limit.
 * If the bound is reached, the exception @code{BA0_ERROOM} is raised.
 * 
 * The parameter @var{time_limit} is a number of seconds.
 * If it is nonnegative then, it provides the maximal number of seconds
 * authorized for the coming sequence of calls. 
 * A value zero means no limit.
 * If the bound is reached, the exception @code{BA0_ERRALR} is raised.
 * 
 * If @var{time_limit} is negative, then its opposite provides the maximal 
 * number of seconds authorized for the coming sequence of calls.
 * Moreover, an interrupt function is called at fixed time intervals 
 * (see @code{ba0_set_settings_interrupt}).
 * 
 * This function initializes and resets all non settings global variables.
 * In particular, it redirects the @code{GMP} memory management functions so 
 * that they allocate memory in the BLAD stacks. 
 */

BA0_DLL void
ba0_restart (
    ba0_int_p time_limit,
    ba0_int_p memory_limit)
{
  bool no_oom, no_oot;

  ba0_get_settings_no_oot (&no_oot);
  ba0_set_settings_no_oot (true);
  ba0_get_settings_no_oom (&no_oom);
  ba0_set_settings_no_oom (true);
/*
    ba0_start_time = time ((time_t*)0);
    ba0_nbcalls_effective_interrupt = 0;
    ba0_nbcalls_interrupt = 0;
*/
  ba0_set_memory_time_and_interrupt (time_limit, memory_limit);

  switch (ba0_initialized_global.common.restart_level)
    {
    case ba0_init_level:
      ba0_alloc_counter = 0;
      ba0_malloc_counter = 0;
      ba0_malloc_nbcalls = 0;
      ba0_init_stack (&ba0_global.stack.main);
      ba0_init_stack (&ba0_global.stack.second);
      ba0_init_stack (&ba0_global.stack.quiet);
      ba0_init_stack (&ba0_global.stack.format);
      ba0_init_stack (&ba0_global.stack.analex);
      ba0_init_stack_of_stacks ();
      ba0_init_analex ();
/*
 * ba0_init_mpzm_module calls the gmp memory functions
 */
      ba0_record_gmp_memory_functions ();
      (*ba0_initialized_global.gmp.set_memory_functions)
          (ba0_gmp_alloc, ba0_gmp_realloc, ba0_gmp_free);
      ba0_init_mpzm_module ();
      ba0_restore_gmp_memory_functions ();

      ba0_initialize_format ();

      ba0_define_format_with_sizelt ("d", sizeof (ba0_int_p),
          &ba0_scanf_int_p, &ba0_printf_int_p,
          (ba0_garbage1_function *) 0,
          (ba0_garbage2_function *) 0, (ba0_copy_function *) 0);

      ba0_define_format_with_sizelt ("bool", sizeof (ba0_bool),
          &ba0_scanf_bool, &ba0_printf_bool,
          (ba0_garbage1_function *) 0,
          (ba0_garbage2_function *) 0, (ba0_copy_function *) 0);

      ba0_define_format_with_sizelt ("x", sizeof (ba0_int_p),
          &ba0_scanf_hexint_p, &ba0_printf_hexint_p,
          (ba0_garbage1_function *) 0,
          (ba0_garbage2_function *) 0, (ba0_copy_function *) 0);

      ba0_define_format_with_sizelt ("s", -1,
          &ba0_scanf_string, &ba0_printf_string,
          &ba0_garbage1_string, &ba0_garbage2_string, &ba0_copy_string);
/*
 * Indexed strings converted into strings
 */
      ba0_define_format_with_sizelt ("six", -1,
          &ba0_scanf_indexed_string_as_a_string,
          &ba0_printf_string,
          &ba0_garbage1_string, &ba0_garbage2_string, &ba0_copy_string);
/*
 * Indexed strings "as is"
 */
      ba0_define_format_with_sizelt ("indexed_string", -1,
          &ba0_scanf_indexed_string,
          &ba0_printf_indexed_string,
          &ba0_garbage1_indexed_string, &ba0_garbage2_indexed_string,
          &ba0_copy_indexed_string);
/*
 * Range indexed groups
 */
      ba0_define_format_with_sizelt ("range_indexed_group", -1,
          &ba0_scanf_range_indexed_group,
          &ba0_printf_range_indexed_group,
          &ba0_garbage1_range_indexed_group, &ba0_garbage2_range_indexed_group,
          &ba0_copy_range_indexed_group);

      ba0_define_format_with_sizelt ("z", sizeof (ba0_mpz_t),
          &ba0_scanf_mpz, &ba0_printf_mpz,
          &ba0_garbage1_mpz, &ba0_garbage2_mpz, &ba0_copy_mpz);

      ba0_define_format_with_sizelt ("q", sizeof (ba0_mpq_t),
          &ba0_scanf_mpq, &ba0_printf_mpq,
          &ba0_garbage1_mpq, &ba0_garbage2_mpq, &ba0_copy_mpq);

      ba0_define_format_with_sizelt ("zm", sizeof (ba0_mpz_t),
          &ba0_scanf_mpzm, &ba0_printf_mpzm,
          &ba0_garbage1_mpzm, &ba0_garbage2_mpzm, &ba0_copy_mpzm);

      ba0_define_format_with_sizelt ("im", sizeof (ba0_mint_hp),
          &ba0_scanf_mint_hp, &ba0_printf_mint_hp,
          (ba0_garbage1_function *) 0,
          (ba0_garbage2_function *) 0, (ba0_copy_function *) 0);

      ba0_define_format_with_sizelt ("le", sizeof (double),
          &ba0_scanf_double, &ba0_printf_double,
          &ba0_garbage1_double, &ba0_garbage2_double, &ba0_copy_double);

      ba0_define_format_with_sizelt ("qi",
          sizeof (struct ba0_interval_mpq),
          &ba0_scanf_interval_mpq,
          &ba0_printf_interval_mpq,
          &ba0_garbage1_interval_mpq,
          &ba0_garbage2_interval_mpq, &ba0_copy_interval_mpq);
    case ba0_reset_level:
      ba0_reset_stack_of_stacks ();
/*
 * Save the existing pointers
 * Replace them by pointers using the BLAD memory management system
 */
      ba0_record_gmp_memory_functions ();
      (*ba0_initialized_global.gmp.set_memory_functions)
          (ba0_gmp_alloc, ba0_gmp_realloc, ba0_gmp_free);

      ba0_reset_exception_extra_stack ();
      ba0_reset_exception ();

      ba0_reset_output ();
      ba0_reset_analex ();

      ba0_reset_mint_hp_module ();
      ba0_reset_mpzm_module ();

      ba0_global.common.LaTeX = false;
    case ba0_done_level:
      break;
    }
  ba0_set_settings_no_oom (no_oom);
  ba0_set_settings_no_oot (no_oot);
}

/*
    Clears the resources of the library in such a way that it can be
    later reinitialized at level: level.
    
    If the value of level is ba0_done_level, the timer is switched off.
    If the value is ba0_reset_level or lower then the all the
    cells allocated by the stacks (excepted the format and the output stack)
    are freed. 
    
    The GMP memory functions and the SIGINT signal are restored to their 
    recorded values.
    
    If the value is ba0_init_level or lower then all the memory allocated
    by all the stacks are freed (excepted the cell used by the output stack).
    
    The ba0_initialized_global.common.restart_level variable is set to: level.
*/

/*
 * texinfo: ba0_terminate
 * A call to this function terminates a sequence of calls to the @code{ba0}
 * library. The parameter @var{level} permits to control the level of cleaning
 * of the resources used by the library (an usual value is @code{ba0_init_level}).
 * The value of the parameter is stored in the global variable 
 * @code{ba0_initialized_global.common.restart_level} which will be used by @code{ba0_restart} 
 * at the next call.
 * 
 * @itemize @bullet
 * @item @code{ba0_done_level}
 * 
 * Does not perform anything.
 * 
 * @item @code{ba0_reset_level}
 * 
 * Empties the stacks @code{ba0_global.stack.main}, @code{ba0_global.stack.second}, 
 * @code{ba0_global.stack.quiet} and @code{ba0_global.stack.analex} and resets the
 * @code{GMP} memory management functions to the values they had before
 * the call to @code{ba0_restart}.
 * 
 * @item @code{ba0_init_level}
 * 
 * Frees all the resources used by the sequence of calls.
 * @end itemize
 * If the total number of calls to @code{ba0_free} is different from
 * the total number of calls to @code{ba0_malloc} then the exception
 * @code{BA0_ERRMFR} is raised.
 */

BA0_DLL void
ba0_terminate (
    enum ba0_restart_level level)
{
  bool no_oot;
/*
    time_t t, u;

    t = time ((time_t*)0);
    u = t - ba0_start_time;
    fprintf (stderr,
	"sec = %ld, calls/sec = %f, eff. calls/sec = %f\n",
	u,
	(double)ba0_nbcalls_interrupt/(double)(u ? u : 1),
	(double)ba0_nbcalls_effective_interrupt/(double)(u ? u : 1));
*/
  ba0_get_settings_no_oot (&no_oot);
  ba0_set_settings_no_oot (true);
  if (level <= ba0_reset_level)
    {
      ba0_clear_cells_stack (&ba0_global.stack.main);
      ba0_clear_cells_stack (&ba0_global.stack.second);
      ba0_clear_cells_stack (&ba0_global.stack.quiet);
      ba0_clear_cells_stack (&ba0_global.stack.analex);

      ba0_restore_gmp_memory_functions ();
    }
  if (level == ba0_init_level)
    {
      ba0_clear_stack (&ba0_global.stack.main);
      ba0_clear_stack (&ba0_global.stack.second);
      ba0_clear_stack (&ba0_global.stack.quiet);
      ba0_clear_stack (&ba0_global.stack.analex);
      ba0_clear_stack (&ba0_global.stack.format);
      ba0_clear_stack_of_stacks ();
      ba0_clear_analex ();
/*
 * All the allocated memory (ba0_malloc) must be freed.
 * Apart the one allocated by ba0_persistent_malloc.
 */
      if (ba0_malloc_nbcalls != 0)
        BA0_RAISE_EXCEPTION (BA0_ERRMFR);
    }
  ba0_set_settings_no_oot (no_oot);
  ba0_initialized_global.common.restart_level = level;
}
