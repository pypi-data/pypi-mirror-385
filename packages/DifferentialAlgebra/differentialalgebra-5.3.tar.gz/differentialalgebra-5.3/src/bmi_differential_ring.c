#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_differential_ring.h"


/**********************************************************************
 * DIFFERENTIAL RING
 **********************************************************************/

/*
 * EXPORTED
 * DifferentialRing 
 * DifferentialRing (derivations, blocks, parameters)
 *     ordering (derivations, blocks) must be valid
 *     parameters must be a list of dependent symbols.
 * Returns the ordering.
 */

ALGEB
bmi_differential_ring (
    struct bmi_callback *callback)
{
  char *derivations, *blocks, *parameters;
  bav_Iordering r;

  bmi_check_blad_gmp_allocators (__FILE__, __LINE__);

  if (bmi_nops (callback) != 3)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);

  bmi_check_blad_gmp_allocators (__FILE__, __LINE__);

  derivations = bmi_string_op (1, callback);
  blocks = bmi_string_op (2, callback);
  parameters = bmi_string_op (3, callback);

  bmi_check_blad_gmp_allocators (__FILE__, __LINE__);

  ba0_scanf_printf
      ("%ordering", "ranking (derivations = %s, blocks = %s, parameters = %s)",
      &r, derivations, blocks, parameters);
  if (bav_R_ambiguous_symbols ())
    BA0_RAISE_EXCEPTION (BAV_ERRPAO);
  bmi_check_blad_gmp_allocators (__FILE__, __LINE__);

  bav_push_ordering (r);
  {
    ALGEB res;
    res = bmi_rtable_differential_ring (callback->kv, __FILE__, __LINE__);
#if defined (BMI_BALSA)
/*
 * In BALSA, we return the whole table, not the mere rtable !
 */
    res = bmi_balsa_new_differential_ring (res);
#endif
    return res;
  }
}
