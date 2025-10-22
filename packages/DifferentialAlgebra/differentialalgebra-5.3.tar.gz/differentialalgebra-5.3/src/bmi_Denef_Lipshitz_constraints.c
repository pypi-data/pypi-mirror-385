#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_Denef_Lipshitz_constraints.h"

/*
 * EXPORTED
 * DenefLipshitzConstraints (DLuple)
 *
 * Return a string "[ Eq(poly,0), ..., Ne(poly,0) ]"
 */

ALGEB 
bmi_Denef_Lipshitz_constraints (
    struct bmi_callback *callback)
{
  struct bas_DLuple DL;

  struct bap_listof_polynom_mpz *L;
  ba0_int_p i;
  char *buffer;
  ALGEB result;

  if (bmi_nops (callback) == 1)
    {
      if (!bmi_is_table_op (1, callback))
        BA0_RAISE_EXCEPTION (BMI_ERRDLUP);

      bmi_set_ordering_and_DLuple (&DL, 1, callback, __FILE__, __LINE__);
    }
  else
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);

  ba0_record_output ();
  BA0_TRY
  {
    ba0_set_output_counter ();
    ba0_put_char ('[');
    for (i = 0; i < DL.C.decision_system.size; i++)
      {
        struct bap_polynom_mpz *poly = DL.C.decision_system.tab[i];
        if (i > 0)
          ba0_printf (", ");
        ba0_printf ("Eq(%Az,0)", poly);
      }
    for (L = DL.S; L != (struct bap_listof_polynom_mpz *)0; L = L->next)
      ba0_printf (", Ne(%Az,0)", L->value);
    ba0_put_char (']');

    buffer = ba0_persistent_malloc (ba0_output_counter () + 1);
    ba0_set_output_string (buffer);

    ba0_put_char ('[');
    for (i = 0; i < DL.C.decision_system.size; i++)
      {
        struct bap_polynom_mpz *poly = DL.C.decision_system.tab[i];
        if (i > 0)
          ba0_printf (", ");
        ba0_printf ("Eq(%Az,0)", poly);
      }
    for (L = DL.S; L != (struct bap_listof_polynom_mpz *)0; L = L->next)
      ba0_printf (", Ne(%Az,0)", L->value);
    ba0_put_char (']');

    ba0_restore_output ();
  }
  BA0_CATCH
  {
    ba0_restore_output ();
    BA0_RE_RAISE_EXCEPTION;
  }
  BA0_ENDTRY;

  bmi_push_maple_gmp_allocators ();
  result = bmi_balsa_new_string (buffer);
  bmi_pull_maple_gmp_allocators ();
  return result;
}
