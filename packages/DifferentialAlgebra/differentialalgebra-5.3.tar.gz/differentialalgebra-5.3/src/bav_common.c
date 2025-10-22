#include "bav_common.h"
#include "bav_block.h"
#include "bav_symbol.h"
#include "bav_parameter.h"
#include "bav_variable.h"
#include "bav_ordering.h"
#include "bav_differential_ring.h"
#include "bav_point_int_p.h"
#include "bav_rank.h"
#include "bav_term.h"
#include "bav_term_ordering.h"
#include "bav_global.h"

/*
 * texinfo: bav_reset_all_settings
 * Reset all settings variables to their default values.
 * This function must be called outside sequences of calls to the library.
 */

BAV_DLL void
bav_reset_all_settings (
    void)
{
  bav_set_settings_common (0);
  bav_set_settings_symbol (0, 0, (char *) 0);
  bav_set_settings_parameter (false);
  bav_set_settings_variable (0, 0, 0, 0, 0);
  bav_set_settings_rank (0);
  bav_set_settings_ordering (0);

  ba0_reset_all_settings ();
}

/*
 * texinfo: bav_unknown_default
 * The default function called when a @code{struct ba0_indexed_string *} 
 * is not recognized.
 * The parameter @var{s} is copied to @code{bav_global.common.unknown}.
 */

BAV_DLL void
bav_unknown_default (
    struct ba0_indexed_string *s)
{
  char *t;

  t = ba0_indexed_string_to_string (s);
  strncpy (bav_global.common.unknown, t, BA0_BUFSIZE - 1);
}

/*
 * texinfo: bav_set_settings_common
 * Set @code{bav_custom_unknown} to @var{u} if it is nonzero else
 * set it to @code{bav_unknown_default}.
 */

BAV_DLL void
bav_set_settings_common (
    ba0_indexed_string_function *u)
{
  bav_initialized_global.common.unknown = u ? u : &bav_unknown_default;
}

/*
 * texinfo: bav_get_settings_common
 * Set @var{u} to @code{bav_custom_unknown}.
 * The parameter @var{u} may be zero.
 */

BAV_DLL void
bav_get_settings_common (
    ba0_indexed_string_function **u)
{
  if (u)
    *u = bav_initialized_global.common.unknown;
}

/*
 * texinfo: bav_cancel_PFE_settings
 * Fill the fields of @var{P} with the corresponding settings variables.
 * Then cancel the @code{PFE} settings.
 */

BAV_DLL void
bav_cancel_PFE_settings (
    struct bav_PFE_settings *P)
{
  ba0_cancel_PFE_settings (&P->ba0);
  bav_get_settings_symbol (&P->scanf, &P->printf, &P->IndexedBase_PFE);
  bav_get_settings_parameter (&P->Function_PFE);
  bav_set_settings_symbol (P->scanf, P->printf, (char *) 0);
  bav_set_settings_parameter ((char *) 0);
}

/*
 * texinfo: bav_restore_PFE_settings
 * Restore the @code{PFE} settings with the content of @var{P}.
 */

BAV_DLL void
bav_restore_PFE_settings (
    struct bav_PFE_settings *P)
{
  ba0_restore_PFE_settings (&P->ba0);
  bav_set_settings_symbol (P->scanf, P->printf, P->IndexedBase_PFE);
  bav_set_settings_parameter (P->Function_PFE);
}

/*
 * texinfo: bav_restart
 * Call @code{ba0_restart} with the same parameters. Define a few more formats.
 * Push the address of @code{bav_global.R.ord_stack.size} which defines the
 * so called @dfn{current ordering} in the exception extra stack.
 */

BAV_DLL void
bav_restart (
    ba0_int_p time_limit,
    ba0_int_p memory_limit)
{
  enum ba0_restart_level level = ba0_initialized_global.common.restart_level;
  bool no_oom, no_oot;

  ba0_get_settings_no_oot (&no_oot);
  ba0_set_settings_no_oot (true);
  ba0_get_settings_no_oom (&no_oom);
  ba0_set_settings_no_oom (true);

  ba0_restart (time_limit, memory_limit);

  switch (level)
    {
    case ba0_init_level:
      ba0_define_format ("ordering",
          &bav_scanf_ordering,
          &bav_printf_ordering,
          (ba0_garbage1_function *) 0,
          (ba0_garbage2_function *) 0, (ba0_copy_function *) 0);

      ba0_define_format ("b", &bav_scanf_block,
          &bav_printf_block,
          (ba0_garbage1_function *) - 1,
          (ba0_garbage2_function *) - 1, (ba0_copy_function *) - 1);

      ba0_define_format ("y", &bav_scanf_symbol,
          &bav_printf_symbol,
          (ba0_garbage1_function *) 0,
          (ba0_garbage2_function *) 0, (ba0_copy_function *) 0);

      ba0_define_format ("v", &bav_scanf_variable,
          &bav_printf_variable,
          (ba0_garbage1_function *) 0,
          (ba0_garbage2_function *) 0, (ba0_copy_function *) 0);

      ba0_define_format ("rank",
          &bav_scanf_rank, &bav_printf_rank,
          (ba0_garbage1_function *) 0,
          (ba0_garbage2_function *) 0, (ba0_copy_function *) 0);

      ba0_define_format_with_sizelt
          ("term", sizeof (struct bav_term),
          &bav_scanf_term,
          &bav_printf_term,
          &bav_garbage1_term, &bav_garbage2_term, &bav_copy_term);

      ba0_define_format_with_sizelt
          ("param", sizeof (struct bav_parameter),
          &bav_scanf_parameter,
          &bav_printf_parameter,
          (ba0_garbage1_function *) 0,
          (ba0_garbage2_function *) 0, (ba0_copy_function *) 0);

      ba0_global.format.scanf_value_var = &bav_scanf_variable;
      ba0_global.format.printf_value_var = &bav_printf_variable;

    case ba0_reset_level:
      ba0_push_exception_extra_stack
          (&bav_global.R.ord_stack.size, (void (*)(ba0_int_p)) 0);
      ba0_push_exception_extra_stack
          (&bav_global.R.ords.size, &bav_R_restore_ords_size);
      bav_init_differential_ring (&bav_global.R);
      bav_set_term_ordering ("lex");
    case ba0_done_level:
      break;
    }
  ba0_set_settings_no_oom (no_oom);
  ba0_set_settings_no_oot (no_oot);
}

/*
 * texinfo: bav_terminate
 * Call @code{ba0_terminate} with the same parameter.
 */

BAV_DLL void
bav_terminate (
    enum ba0_restart_level level)
{
  ba0_terminate (level);
}
