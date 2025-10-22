#include "bad_common.h"
#include "bad_regchain.h"
#include "bad_intersectof_regchain.h"
#include "bad_reduction.h"
#include "bad_regularize.h"
#include "bad_base_field.h"
#include "bad_low_power_theorem.h"
#include "bad_critical_pair.h"
#include "bad_splitting_tree.h"
#include "bad_quadruple.h"
#include "bad_global.h"
#include "bad_stats.h"

/*
 * texinfo: bad_reset_all_settings
 * Reset all settings variables to their default values.
 * This function must be called outside sequences of calls to the library.
 */

BAD_DLL void
bad_reset_all_settings (
    void)
{
  bad_set_settings_reduction (0, 0, 0);
  bad_set_settings_regularize (0);
  bad_set_settings_preparation (0);

  baz_reset_all_settings ();
}

/*
 * texinfo: bad_restart
 * Call the @code{baz_restart} function with the same parameters and define
 * a few more formats. 
 */

BAD_DLL void
bad_restart (
    ba0_int_p time_limit,
    ba0_int_p memory_limit)
{
  enum ba0_restart_level level = ba0_initialized_global.common.restart_level;
  bool no_oom, no_oot;

  ba0_get_settings_no_oot (&no_oot);
  ba0_set_settings_no_oot (true);
  ba0_get_settings_no_oom (&no_oom);
  ba0_set_settings_no_oom (true);

  baz_restart (time_limit, memory_limit);

  switch (level)
    {
    case ba0_init_level:
      ba0_define_format_with_sizelt ("regchain", sizeof (struct bad_regchain),
          &bad_scanf_regchain, &bad_printf_regchain, &bad_garbage1_regchain,
          &bad_garbage2_regchain, &bad_copy_regchain);

      ba0_define_format_with_sizelt ("regchain_equations",
          sizeof (struct bad_regchain), &bad_scanf_regchain,
          &bad_printf_regchain_equations, &bad_garbage1_regchain,
          &bad_garbage2_regchain, &bad_copy_regchain);

      ba0_define_format_with_sizelt ("pretend_regchain",
          sizeof (struct bad_regchain), &bad_scanf_pretend_regchain,
          &bad_printf_regchain, &bad_garbage1_regchain, &bad_garbage2_regchain,
          &bad_copy_regchain);

      ba0_define_format_with_sizelt ("critical_pair",
          sizeof (struct bad_critical_pair), &bad_scanf_critical_pair,
          &bad_printf_critical_pair, &bad_garbage1_critical_pair,
          &bad_garbage2_critical_pair, &bad_copy_critical_pair);

      ba0_define_format_with_sizelt ("splitting_edge",
          sizeof (struct bad_splitting_edge), &bad_scanf_splitting_edge,
          &bad_printf_splitting_edge, &bad_garbage1_splitting_edge,
          &bad_garbage2_splitting_edge, &bad_copy_splitting_edge);

      ba0_define_format_with_sizelt ("splitting_vertex",
          sizeof (struct bad_splitting_vertex), &bad_scanf_splitting_vertex,
          &bad_printf_splitting_vertex, &bad_garbage1_splitting_vertex,
          &bad_garbage2_splitting_vertex, &bad_copy_splitting_vertex);

      ba0_define_format_with_sizelt ("splitting_tree",
          sizeof (struct bad_splitting_tree), &bad_scanf_splitting_tree,
          &bad_printf_splitting_tree, &bad_garbage1_splitting_tree,
          &bad_garbage2_splitting_tree, &bad_copy_splitting_tree);

      ba0_define_format_with_sizelt ("quadruple", sizeof (struct bad_quadruple),
          &bad_scanf_quadruple, &bad_printf_quadruple, &bad_garbage1_quadruple,
          &bad_garbage2_quadruple, &bad_copy_quadruple);

      ba0_define_format_with_sizelt ("intersectof_regchain",
          sizeof (struct bad_intersectof_regchain),
          &bad_scanf_intersectof_regchain, &bad_printf_intersectof_regchain,
          &bad_garbage1_intersectof_regchain,
          &bad_garbage2_intersectof_regchain, &bad_copy_intersectof_regchain);

      ba0_define_format_with_sizelt ("intersectof_regchain_equations",
          sizeof (struct bad_intersectof_regchain),
          &bad_scanf_intersectof_regchain,
          &bad_printf_intersectof_regchain_equations,
          &bad_garbage1_intersectof_regchain,
          &bad_garbage2_intersectof_regchain, &bad_copy_intersectof_regchain);

      ba0_define_format_with_sizelt ("intersectof_pretend_regchain",
          sizeof (struct bad_intersectof_regchain),
          &bad_scanf_intersectof_pretend_regchain,
          &bad_printf_intersectof_regchain, &bad_garbage1_intersectof_regchain,
          &bad_garbage2_intersectof_regchain, &bad_copy_intersectof_regchain);

      ba0_define_format ("preparation_equation", 0,
          &bad_printf_preparation_equation, 0, 0, 0);

      ba0_define_format_with_sizelt ("base_field",
          sizeof (struct bad_base_field), &bad_scanf_base_field,
          &bad_printf_base_field, 0, 0, 0);

    case ba0_reset_level:
    case ba0_done_level:
      break;
    }
  ba0_set_settings_no_oom (no_oom);
  ba0_set_settings_no_oot (no_oot);
}

/*
 * texinfo: bad_terminate
 * Call the @code{bap_terminate} function with the same parameter.
 */

BAD_DLL void
bad_terminate (
    enum ba0_restart_level level)
{
  baz_terminate (level);
}
