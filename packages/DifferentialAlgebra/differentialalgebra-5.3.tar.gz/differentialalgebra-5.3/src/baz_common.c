#include "baz_common.h"
#include "baz_ratfrac.h"
#include "baz_rel_ratfrac.h"
#include "baz_gcd_polynom_mpz.h"
#include "baz_prolongation_pattern.h"

/*
 * texinfo: baz_reset_all_settings
 * Reset all settings variables to their default values.
 * This function must be called outside sequences of calls to the library.
 */

BAZ_DLL void
baz_reset_all_settings (
    void)
{
  bap_reset_all_settings ();
}

/*
 * texinfo: baz_restart
 * Call the @code{bap_restart} function with the same parameters and defines
 * a few more formats. 
 */

BAZ_DLL void
baz_restart (
    ba0_int_p time_limit,
    ba0_int_p memory_limit)
{
  enum ba0_restart_level level = ba0_initialized_global.common.restart_level;
  bool no_oom, no_oot;

  ba0_get_settings_no_oot (&no_oot);
  ba0_set_settings_no_oot (true);
  ba0_get_settings_no_oom (&no_oom);
  ba0_set_settings_no_oom (true);

  bap_restart (time_limit, memory_limit);

  switch (level)
    {
    case ba0_init_level:
      ba0_define_format_with_sizelt ("Qz", sizeof (struct baz_ratfrac),
          &baz_scanf_ratfrac, &baz_printf_ratfrac, &baz_garbage1_ratfrac,
          &baz_garbage2_ratfrac, &baz_copy_ratfrac);

      ba0_define_format_with_sizelt ("simplify_Qz", sizeof (struct baz_ratfrac),
          &baz_scanf_simplify_ratfrac, &baz_printf_ratfrac,
          &baz_garbage1_ratfrac, &baz_garbage2_ratfrac, &baz_copy_ratfrac);

      ba0_define_format_with_sizelt ("expanded_Qz", sizeof (struct baz_ratfrac),
          &baz_scanf_expanded_ratfrac, &baz_printf_ratfrac,
          &baz_garbage1_ratfrac, &baz_garbage2_ratfrac, &baz_copy_ratfrac);

      ba0_define_format_with_sizelt ("simplify_expanded_Qz",
          sizeof (struct baz_ratfrac), &baz_scanf_simplify_expanded_ratfrac,
          &baz_printf_ratfrac, &baz_garbage1_ratfrac, &baz_garbage2_ratfrac,
          &baz_copy_ratfrac);

      ba0_define_format_with_sizelt ("relQz", sizeof (struct baz_rel_ratfrac),
          &baz_scanf_rel_ratfrac, &baz_printf_rel_ratfrac,
          &baz_garbage1_rel_ratfrac, &baz_garbage2_rel_ratfrac,
          &baz_copy_rel_ratfrac);

      ba0_define_format_with_sizelt ("gcd_data", sizeof (struct baz_gcd_data),
          0, &baz_printf_gcd_data, 0, 0, 0);

      ba0_define_format_with_sizelt ("prolongation_pattern",
          sizeof (struct baz_prolongation_pattern),
          &baz_scanf_prolongation_pattern, &baz_printf_prolongation_pattern, 0,
          0, 0);

    case ba0_reset_level:
    case ba0_done_level:
      break;
    }
  ba0_set_settings_no_oom (no_oom);
  ba0_set_settings_no_oot (no_oot);
}

/*
 * texinfo: baz_terminate
 * Call the @code{bap_terminate} function with the same parameter.
 */

BAZ_DLL void
baz_terminate (
    enum ba0_restart_level level)
{
  bap_terminate (level);
}
