#include "bas_common.h"
#include "bas_Yuple.h"
#include "bas_Zuple.h"
#include "bas_DL_tree.h"
#include "bas_DLuple.h"

/*
 * texinfo: bas_reset_all_settings
 * Reset all settings variables to their default values.
 * This function must be called outside sequences of calls to the library.
 */

BAS_DLL void
bas_reset_all_settings (
    void)
{
  bad_reset_all_settings ();
}

/*
 * texinfo: bas_restart
 * Call the @code{bas_restart} function with the same parameters
 */

BAS_DLL void
bas_restart (
    ba0_int_p time_limit,
    ba0_int_p memory_limit)
{
  enum ba0_restart_level level = ba0_initialized_global.common.restart_level;
  bool no_oom, no_oot;

  ba0_get_settings_no_oot (&no_oot);
  ba0_set_settings_no_oot (true);
  ba0_get_settings_no_oom (&no_oom);
  ba0_set_settings_no_oom (true);

  bad_restart (time_limit, memory_limit);

  switch (level)
    {
    case ba0_init_level:

      ba0_define_format_with_sizelt ("Yuple", sizeof (struct bas_Yuple),
          0, &bas_printf_Yuple, 0, 0, &bas_copy_Yuple);

      ba0_define_format_with_sizelt ("Zuple", sizeof (struct bas_Zuple),
          0, &bas_printf_Zuple, 0, 0, 0);

      ba0_define_format_with_sizelt ("DLuple", sizeof (struct bas_DLuple),
          &bas_scanf_DLuple, &bas_printf_DLuple, 0, 0, 0);

      ba0_define_format_with_sizelt ("stripped_DLuple",
          sizeof (struct bas_DLuple),
          &bas_scanf_DLuple, &bas_printf_stripped_DLuple, 0, 0, 0);

      ba0_define_format_with_sizelt ("DL_edge", sizeof (struct bas_DL_edge),
          0, &bas_printf_DL_edge,
          &bas_garbage1_DL_edge, &bas_garbage2_DL_edge, &bas_copy_DL_edge);

      ba0_define_format_with_sizelt ("DL_vertex", sizeof (struct bas_DL_vertex),
          0, &bas_printf_DL_vertex,
          &bas_garbage1_DL_vertex, &bas_garbage2_DL_vertex,
          &bas_copy_DL_vertex);

      ba0_define_format_with_sizelt ("DL_tree", sizeof (struct bas_DL_tree),
          0, &bas_printf_DL_tree,
          &bas_garbage1_DL_tree, &bas_garbage2_DL_tree, &bas_copy_DL_tree);

    case ba0_reset_level:
    case ba0_done_level:
      break;
    }
  ba0_set_settings_no_oom (no_oom);
  ba0_set_settings_no_oot (no_oot);
}

/*
 * texinfo: bas_terminate
 * Call the @code{bas_terminate} function with the same parameter.
 */

BAS_DLL void
bas_terminate (
    enum ba0_restart_level level)
{
  bad_terminate (level);
}
