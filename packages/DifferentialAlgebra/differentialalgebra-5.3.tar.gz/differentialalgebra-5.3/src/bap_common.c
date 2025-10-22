#include "bap_common.h"
#include "bap_polynom_mpz.h"
#include "bap_polynom_mpzm.h"
#include "bap_polynom_mpq.h"
#include "bap_polynom_mint_hp.h"
#include "bap_parse_polynom_mpz.h"
#include "bap_parse_polynom_mpzm.h"
#include "bap_parse_polynom_mpq.h"
#include "bap_parse_polynom_mint_hp.h"
#include "bap_product_mpz.h"
#include "bap_product_mpzm.h"
#include "bap_product_mpq.h"
#include "bap_product_mint_hp.h"

/*
 * texinfo: bap_reset_all_settings
 * Reset all settings variables to their default values.
 * This function must be called outside sequences of calls to the library.
 */

BAP_DLL void
bap_reset_all_settings (
    void)
{
  bav_reset_all_settings ();
}

BAP_DLL ba0_int_p
bap_ceil_log2 (
    ba0_int_p s)
{
  ba0_int_p i, n;

  i = 0;
  n = 1;
  while (n < s)
    {
      n <<= 1;
      i += 1;
    }
  return i;
}

/*
 * texinfo: bap_restart
 * Call the @code{bav_restart} function with the same parameters and defines
 * a few more formats. 
 */

BAP_DLL void
bap_restart (
    ba0_int_p time_limit,
    ba0_int_p memory_limit)
{
  enum ba0_restart_level level = ba0_initialized_global.common.restart_level;
  bool no_oom, no_oot;

  ba0_get_settings_no_oot (&no_oot);
  ba0_set_settings_no_oot (true);
  ba0_get_settings_no_oom (&no_oom);
  ba0_set_settings_no_oom (true);

  bav_restart (time_limit, memory_limit);

  switch (level)
    {
    case ba0_init_level:
      ba0_define_format_with_sizelt ("Az", sizeof (struct bap_polynom_mpz),
          &bap_scanf_polynom_mpz, &bap_printf_polynom_mpz,
          &bap_garbage1_polynom_mpz, &bap_garbage2_polynom_mpz,
          &bap_copy_polynom_mpz);

      ba0_define_format_with_sizelt ("simplify_Az",
          sizeof (struct bap_polynom_mpz), &bap_scanf_simplify_polynom_mpz,
          &bap_printf_polynom_mpz, &bap_garbage1_polynom_mpz,
          &bap_garbage2_polynom_mpz, &bap_copy_polynom_mpz);

      ba0_define_format_with_sizelt ("expanded_Az",
          sizeof (struct bap_polynom_mpz), &bap_scanf_expanded_polynom_mpz,
          &bap_printf_polynom_mpz, &bap_garbage1_polynom_mpz,
          &bap_garbage2_polynom_mpz, &bap_copy_polynom_mpz);

      ba0_define_format_with_sizelt ("simplify_expanded_Az",
          sizeof (struct bap_polynom_mpz),
          &bap_scanf_simplify_expanded_polynom_mpz, &bap_printf_polynom_mpz,
          &bap_garbage1_polynom_mpz, &bap_garbage2_polynom_mpz,
          &bap_copy_polynom_mpz);

      ba0_define_format_with_sizelt ("Azm", sizeof (struct bap_polynom_mpzm),
          &bap_scanf_polynom_mpzm, &bap_printf_polynom_mpzm,
          &bap_garbage1_polynom_mpzm, &bap_garbage2_polynom_mpzm,
          &bap_copy_polynom_mpzm);

      ba0_define_format_with_sizelt ("Aq", sizeof (struct bap_polynom_mpq),
          &bap_scanf_polynom_mpq, &bap_printf_polynom_mpq,
          &bap_garbage1_polynom_mpq, &bap_garbage2_polynom_mpq,
          &bap_copy_polynom_mpq);

      ba0_define_format_with_sizelt ("simplify_Aq",
          sizeof (struct bap_polynom_mpq), &bap_scanf_simplify_polynom_mpq,
          &bap_printf_polynom_mpq, &bap_garbage1_polynom_mpq,
          &bap_garbage2_polynom_mpq, &bap_copy_polynom_mpq);

      ba0_define_format_with_sizelt ("expanded_Aq",
          sizeof (struct bap_polynom_mpq), &bap_scanf_expanded_polynom_mpq,
          &bap_printf_polynom_mpq, &bap_garbage1_polynom_mpq,
          &bap_garbage2_polynom_mpq, &bap_copy_polynom_mpq);

      ba0_define_format_with_sizelt ("simplify_expanded_Aq",
          sizeof (struct bap_polynom_mpq),
          &bap_scanf_simplify_expanded_polynom_mpq, &bap_printf_polynom_mpq,
          &bap_garbage1_polynom_mpq, &bap_garbage2_polynom_mpq,
          &bap_copy_polynom_mpq);

      ba0_define_format_with_sizelt ("Aim", sizeof (struct bap_polynom_mint_hp),
          &bap_scanf_polynom_mint_hp, &bap_printf_polynom_mint_hp,
          &bap_garbage1_polynom_mint_hp, &bap_garbage2_polynom_mint_hp,
          &bap_copy_polynom_mint_hp);

      ba0_define_format_with_sizelt ("Pz", sizeof (struct bap_product_mpz),
          &bap_scanf_product_mpz, &bap_printf_product_mpz,
          &bap_garbage1_product_mpz, &bap_garbage2_product_mpz,
          &bap_copy_product_mpz);

      ba0_define_format_with_sizelt ("Pzm", sizeof (struct bap_product_mpzm),
          &bap_scanf_product_mpzm, &bap_printf_product_mpzm,
          &bap_garbage1_product_mpzm, &bap_garbage2_product_mpzm,
          &bap_copy_product_mpzm);

      ba0_define_format_with_sizelt ("Pq", sizeof (struct bap_product_mpq),
          &bap_scanf_product_mpq, &bap_printf_product_mpq,
          &bap_garbage1_product_mpq, &bap_garbage2_product_mpq,
          &bap_copy_product_mpq);

      ba0_define_format_with_sizelt ("Pim", sizeof (struct bap_product_mint_hp),
          &bap_scanf_product_mint_hp, &bap_printf_product_mint_hp,
          &bap_garbage1_product_mint_hp, &bap_garbage2_product_mint_hp,
          &bap_copy_product_mint_hp);

    case ba0_reset_level:
    case ba0_done_level:
      break;
    }
  ba0_set_settings_no_oom (no_oom);
  ba0_set_settings_no_oot (no_oot);
}

/*
 * texinfo: bap_terminate
 * Call the @code{bav_terminate} function with the same parameter.
 */

BAP_DLL void
bap_terminate (
    enum ba0_restart_level level)
{
  bav_terminate (level);
}
