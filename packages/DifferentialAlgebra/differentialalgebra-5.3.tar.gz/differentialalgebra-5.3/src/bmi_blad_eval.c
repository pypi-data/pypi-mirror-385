#include "bmi_indices.h"
#include "bmi_callback.h"
#include "bmi_memory.h"
#include "bmi_options.h"
#include "bmi_exported.h"
#include "bmi_blad_eval.h"
#include "bmi_mesgerr.h"
#include "bmi_gmp.h"

char bmi_mesgerr[BMI_BUFSIZE];

/*
 * Return true if the BLAD libraries are successfully called.
 * In this case, the computation result, an ALGEB, is stored in *result.
 */

static bool
bmi_process_command (
    ALGEB *result,
    struct bmi_options *options,
    struct bmi_callback *callback)
{
  ba0_scanf_function *s;
  ba0_printf_function *f;
  char *jet0_input, *jet0_output;
  char *name;
  volatile bool b;
/*
 * Some other settings may be set in bmi_blad_eval*
 */
  ba0_set_settings_no_oot (true);
  ba0_set_settings_no_oom (true);
  if (strcmp (options->cellsize, BMI_IX_small) == 0)
    ba0_set_settings_stack (0x10000, 0, 0x10000, 0, 0);
  else
    ba0_set_settings_stack (0, 0, 0x10000, 0, 0);
/*
 * Sequence of calls to the BLAD libraries
 * Increasing the default cell size of ba0_analex and the default token_lmax
 * The leading string for parsing orderings is now "ranking"
 */
  bas_restart (options->time_limit, options->memory_limit);
/*
 * If an error occurs in BLAD, an exception is raised, which is
 * caught here. The error message is enhanced with a context string
 * when the error is raised by a parser.
 */
  BA0_TRY
  {
    ba0_set_settings_no_oot (false);
    ba0_set_settings_no_oom (false);
    bmi_check_blad_gmp_allocators (__FILE__, __LINE__);
/*
 * Customize the input notation
 */
#if defined (MAPLE)
    switch (options->input_notation)
      {
      case bmi_jet_notation:
      case bmi_tjet_notation:
        s = &bav_scanf_jet_variable;
        break;
      case bmi_diff_notation:
        s = &bav_scanf_diff_variable;
        break;
      case bmi_udif_notation:
        s = &bav_scanf_inert_diff_variable;
        break;
      case bmi_D_notation:
        s = &bav_scanf_maple_D_variable;
        break;
      default:                 /* to avoid a stupid warning */
        s = 0;
      }
#else
    s = &bav_scanf_python_all_variable;
#endif
/*
 * Customize the output notation
 * For the jet-like output notations, parameters with nonempty 
 *  dependencies must be quoted when printed
 */
    switch (options->output_notation)
      {
      case bmi_jet_notation:
        f = &bav_printf_jet_variable;
        break;
      case bmi_tjet_notation:
        f = &bav_printf_jet_wesb_variable;
        break;
      case bmi_jet0_notation:
        f = &bav_printf_jet0_variable;
        break;
      case bmi_diff_notation:
        f = &bav_printf_diff_variable;
        bav_set_settings_parameter ((char *)0);
        break;
      case bmi_udif_notation:
        f = &bav_printf_inert_diff_variable;
        bav_set_settings_parameter ((char *)0);
        break;
      case bmi_D_notation:
#if defined (MAPLE)
        f = &bav_printf_maple_D_variable;
#else
        f = &bav_printf_diff_variable;
#endif
        break;
      case bmi_Derivative_notation:
        f = &bav_printf_python_Derivative_variable;
        break;
      default:                 /* to avoid a stupid warning */
        f = 0;
      }
    bav_get_settings_variable (0, 0, &jet0_input, &jet0_output, 0);
    bav_set_settings_variable (s, f, jet0_input, jet0_output, 0);
    bav_set_settings_ordering ("ranking");

    bmi_check_blad_gmp_allocators (__FILE__, __LINE__);
/*
 * The string ("NormalForm", "RosenfeldGroebner", ...) representing 
 * the exported function to be called.
 */
    name = bmi_string_op (0, callback);

    bmi_check_blad_gmp_allocators (__FILE__, __LINE__);
/*
 * The call
 */
    *result = bmi_call_exported (name, callback);
    b = true;
  }
  BA0_CATCH
  {
    char *context = ba0_get_context_analex ();
    if (context[0])
      sprintf (bmi_mesgerr, "%s (approx. error location: %s)",
          ba0_global.exception.raised, context);
    else
      sprintf (bmi_mesgerr, "%s", ba0_global.exception.raised);
    b = false;
  }
  BA0_ENDTRY;
/*
 * Exit from BLAD
 */
  bas_terminate (ba0_init_level);
  return b;
}

/*
 * texinfo: bmi_blad_eval
 * The entry point from Maple
 */

BMI_DLL ALGEB M_DECL
bmi_blad_eval (
    MKernelVector kv,
    ALGEB args)
{
  struct bmi_options options;
  struct bmi_callback *callback;
  long nargs;
  ALGEB result;
  bool b;

#if defined (PRINT)
  fprintf (stderr, "call to BLAD\n");
#endif
/*
 * args is a sequence and one should not apply op and nops over it.
 */
  nargs = (long) MapleNumArgs (kv, args);
  if (nargs < 1)
    {
      MapleRaiseError (kv, BMI_ERRNARGS);
      return (ALGEB) 0;
    }
/*
 * Call this one first 
 */
  bas_reset_all_settings ();
/*
 * Initialize the memory management data structure 
 * Returns a callback for calling MAPLE.
 */
  callback = bmi_init_memory (kv);
/*
 * Process the options
 */
  bmi_init_options (&options);
  if (!bmi_set_options (&options, callback, (ALGEB *) args + 2, nargs - 1))
    {
      bmi_clear_options (&options);
      bmi_clear_memory ();
      MapleRaiseError (kv, BMI_ERROPTS);
      return (ALGEB) 0;
    }
/*
 * Process the command
 */
  result = (ALGEB) 0;
  bmi_set_callback_ALGEB (callback, ((ALGEB *) args)[1]);
  b = bmi_process_command (&result, &options, callback);
/*
 * Clear the data structure 
 */
  bmi_clear_options (&options);
  bmi_clear_memory ();
/*
 * if b is false then result is not set.
 */
  if (!b)
    {
#if defined (BMI_MEMCHECK)
      if (result)
        {
          fprintf (stderr, "bmi fatal error: NULL expected\n");
          exit (1);
        }
#endif
      MapleRaiseError (kv, bmi_mesgerr);
      return (ALGEB) 0;
    }

  MapleGcAllow (kv, result);

  bmi_check_maple_gmp_allocators (__FILE__, __LINE__);
  bmi_check_gmp_sp ();
  bmi_check_error_sp ();

  return result;
}

/*
 * texinfo: bmi_blad_eval_python
 * The main entry point for Sagemath / Python
 * This function is called from the entry points of bmi_dapyx.c
 *  through the bmi_dapyx.c:eval function
 */

BMI_DLL ALGEB M_DECL
bmi_blad_eval_python (
    MKernelVector kv,
    ALGEB args)
{
  struct bmi_options options;
  struct bmi_callback *callback;
  long nargs;
  ALGEB result;
  bool b;
/*
 * args is a sequence and one should not apply op and nops over it.
 */
  nargs = (long) MapleNumArgs (kv, args);
  if (nargs < 1)
    {
      MapleRaiseError (kv, BMI_ERRNARGS);
      return (ALGEB) 0;
    }
/*
 * Call this one first 
 */
  bas_reset_all_settings ();
/*
 * Protect rational numbers from floating point evaluation
 */
  {
    ba0_set_memory_functions_function *set;
    ba0_get_settings_gmp (&set, 0);
    ba0_set_settings_gmp (set, "Integer");
  }
/*
 * Range indexed groups are denoted in the Python style 0:oo
 * They need be quoted when printed
 */
  ba0_set_settings_range_indexed_group (":", "oo", false, true); 
/*
 * Radicals of symbols which fit range indexed groups need be protected too
 */
  {
    ba0_scanf_function *scanf_symbol;
    ba0_printf_function *printf_symbol;
    bav_get_settings_symbol (&scanf_symbol, &printf_symbol, (char **)0);
    bav_set_settings_symbol (scanf_symbol, printf_symbol, "sympy.IndexedBase");
  }
/*
 * Parameters need be protected too
 */
  bav_set_settings_parameter ("sympy.Function");
/*
 * Ranks must be printed with the ** exponentiation operator
 */
  bav_set_settings_rank (&bav_printf_stars_rank);
/*
 * Lhs of prolongation patterns must be quoted
 */
  baz_set_settings_prolongation_pattern ("'");
/*
 * Initialize the memory management data structure 
 * The returned callback permits to query BALSA
 */
  callback = bmi_init_memory (kv);
/*
 * Process the options
 * In the case of the jet0 notation, a call to bav_set_settings_variable 
 *  is performed
 *
 * This part should be simplified since we are now calling
 *  bav_scanf_python_all_variable whatever the input notation
 */
  bmi_init_options (&options);
  if (!bmi_set_options (&options, callback, (ALGEB *) args + 2, nargs - 1))
    {
      bmi_clear_options (&options);
      bmi_clear_memory ();
      MapleRaiseError (kv, BMI_ERROPTS);
      return (ALGEB) 0;
    }
/*
 * Process the command
 */
  result = (ALGEB) 0;
  bmi_set_callback_ALGEB (callback, ((ALGEB *) args)[1]);
  b = bmi_process_command (&result, &options, callback);
/*
 * Clear the data structure 
 */
  bmi_clear_options (&options);
  bmi_clear_memory ();
/*
 * if b is false then result is not set.
 */
  if (!b)
    {
#if defined (BMI_MEMCHECK)
      if (result)
        {
          fprintf (stderr, "bmi fatal error: NULL expected\n");
          exit (1);
        }
#endif
      MapleRaiseError (kv, bmi_mesgerr);
      return (ALGEB) 0;
    }

  MapleGcAllow (kv, result);

  bmi_check_maple_gmp_allocators (__FILE__, __LINE__);
  bmi_check_gmp_sp ();
  bmi_check_error_sp ();

  return result;
}
