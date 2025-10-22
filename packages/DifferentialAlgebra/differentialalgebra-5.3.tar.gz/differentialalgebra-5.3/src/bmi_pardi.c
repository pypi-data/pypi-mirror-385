#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_pardi.h"

#define DOPRINT
#undef DOPRINT

/*
 * EXPORTED
 * Pardi (regchain, differential ring, prime)
 */

ALGEB
bmi_pardi (
    struct bmi_callback *callback)
{
  struct bad_regchain C, Cbar;
  bav_Iordering r, rbar;
  struct ba0_tableof_string properties;
  struct ba0_mark M;
  char *bar_ordering;
  bool prime;

  if (bmi_nops (callback) != 3)
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);
  if (!bmi_is_regchain_op (1, callback))
    BA0_RAISE_EXCEPTION (BMI_ERRREGC);
#if defined (DOPRINT)
  printf ("bmi_pardi 1\n");
#endif
/*
 * The input regchain and its ordering
 */
  r = bmi_set_ordering_and_regchain (&C, 1, callback, __FILE__, __LINE__);
/*
 * The target ordering.
 * An exception may be raised while parsing it.
 * It is reformulated in BMI_ERRPRNK.
 */

  bar_ordering = bmi_string_op (2, callback);

  BA0_TRY
  {
    ba0_sscanf2 (bar_ordering, "%ordering", &rbar);
  }
  BA0_CATCH
  {
    if (ba0_global.exception.raised == BA0_ERROOM ||
        ba0_global.exception.raised == BA0_ERRALR)
      BA0_RE_RAISE_EXCEPTION;
    BA0_RAISE_EXCEPTION (BMI_ERRPRNK);
  }
  BA0_ENDTRY;
/*
 * The primality issue.
 * The chain may have the prime attribute, may be obviously prime or may
 * be assumed to be prime. Otherwise, exception BMI_ERRPARD is raised.
 *
 * The resulting chain will have the prime attribute.
 */
#if defined (DOPRINT)
  printf ("bmi_pardi 2\n");
#endif
  prime = bmi_bool_op (3, callback);
  if (!prime &&
      !bad_defines_a_prime_ideal_regchain (&C) &&
      !bad_is_explicit_regchain (&C))
    BA0_RAISE_EXCEPTION (BMI_ERRPARD);
  bad_set_property_attchain (&C.attrib, bad_prime_ideal_property);

  ba0_init_table ((struct ba0_table *) &properties);
  bad_properties_attchain (&properties, &C.attrib);
#if defined (DOPRINT)
  printf ("bmi_pardi 3\n");
#endif
/*
 * Call to PARDI
 */
  bad_set_settings_reduction (0, bad_probabilistic_redzero_strategy, 0);

  ba0_record (&M);
  bad_init_regchain (&Cbar);
  bad_set_properties_regchain (&Cbar, &properties);
  bad_pardi (&Cbar, rbar, &C);
/*
 * A complete change of ring is performed on the result.
 */
#if defined (DOPRINT)
  printf ("bmi_pardi 4\n");
#endif
  {
    struct bav_PFE_settings bav;
    struct bad_regchain Chat;
    bav_Iordering rhat;
    char *bar_C;
    ALGEB res;

    bav_cancel_PFE_settings (&bav);
    bar_C = ba0_new_printf ("%regchain", &Cbar);
    bav_restore_PFE_settings (&bav);

#if defined (DOPRINT)
    printf ("bmi_pardi 4.1: %s\n", bar_C);
#endif

    bav_init_differential_ring (&bav_global.R);
    ba0_sscanf2 (bar_ordering, "%ordering", &rhat);
    bav_push_ordering (rhat);
#if defined (DOPRINT)
    printf ("bmi_pardi 4.2\n");
#endif
    bad_init_regchain (&Chat);
    ba0_sscanf2 (bar_C, "%pretend_regchain", &Chat);

    res = bmi_rtable_regchain (callback->kv, &Chat, __FILE__, __LINE__);
/*
 * In BALSA, one returns the whole table, not just the rtable
 */
#if defined (BMI_SYMPY)
    res = bmi_balsa_new_regchain (res);
#elif defined (BMI_SAGE)
    res = bmi_balsa_new_regchain (res);
    bav_set_settings_variable (s, p, (char *) 0, (char *) 0, (char *) 0);
#endif
#if defined (DOPRINT)
    printf ("bmi_pardi 5\n");
#endif
    return res;
  }
}
