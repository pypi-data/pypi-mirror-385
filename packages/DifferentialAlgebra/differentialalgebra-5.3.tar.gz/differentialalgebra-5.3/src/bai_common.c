#include "bai_common.h"
#include "bai_odex.h"

/*
 * texinfo: bai_reset_all_settings
 * Reset all settings variables to their default values.
 * This function must be called outside sequences of calls to the library.
 */

BAI_DLL void
bai_reset_all_settings (
    void)
{
  bas_reset_all_settings ();
}

/*
 * texinfo: bai_restart
 * Call the @code{bas_restart} function with the same parameters
 */

BAI_DLL void
bai_restart (
    ba0_int_p time_limit,
    ba0_int_p memory_limit)
{
  enum ba0_restart_level level = ba0_initialized_global.common.restart_level;
  bool no_oom, no_oot;

  ba0_get_settings_no_oot (&no_oot);
  ba0_set_settings_no_oot (true);
  ba0_get_settings_no_oom (&no_oom);
  ba0_set_settings_no_oom (true);

  bas_restart (time_limit, memory_limit);

  switch (level)
    {
    case ba0_init_level:

      ba0_define_format_with_sizelt ("odex", sizeof (struct bai_odex_system),
          &bai_scanf_odex_system, &bai_printf_odex_system,
          &bai_garbage1_odex_system, &bai_garbage2_odex_system,
          &bai_copy_odex_system);

    case ba0_reset_level:
    case ba0_done_level:
      break;
    }
  ba0_set_settings_no_oom (no_oom);
  ba0_set_settings_no_oot (no_oot);
}

/*
 * texinfo: bai_terminate
 * Call the @code{bas_terminate} function with the same parameter.
 */

BAI_DLL void
bai_terminate (
    enum ba0_restart_level level)
{
  bas_terminate (level);
}
