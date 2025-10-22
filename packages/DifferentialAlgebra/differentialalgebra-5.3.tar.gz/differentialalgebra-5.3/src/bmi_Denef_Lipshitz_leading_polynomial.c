#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_Denef_Lipshitz_leading_polynomial.h"

/*
 * EXPORTED
 * DenefLipshitzLeadingPolynomial (DLuple)
 *
 * Return a string "{ y : (polynomial for y, n + 2*k + 2 - r, 2*k + 2),
 *                    z : (polynomial for z, n + 2*k + 2 - r, 2*k + 2) }"
 */

ALGEB 
bmi_Denef_Lipshitz_leading_polynomial (
    struct bmi_callback *callback)
{
  struct bas_DLuple DL;

  struct bav_tableof_variable leaders;
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

  ba0_init_table ((struct ba0_table *) &leaders);
  bad_leaders_of_regchain (&leaders, &DL.C);

  ba0_record_output ();
  BA0_TRY
  {
    ba0_set_output_counter ();
    ba0_put_char ('{');
    for (i = 0; i < DL.Y.size; i++)
      {
        ba0_int_p nb_diff, var_index;
        
        nb_diff = 2 * DL.k.tab[i] + 2;
        var_index = DL.order.tab[i] + nb_diff - DL.r.tab[i];

        if (i > 0)
          ba0_printf (", ");
        ba0_printf (" %y : (%Qz, %d, %d)", DL.Y.tab[i], DL.A.tab[i], 
              var_index, nb_diff);
      }
    ba0_put_char ('}');

    buffer = ba0_persistent_malloc (ba0_output_counter () + 1);
    ba0_set_output_string (buffer);

// Same code as above

    ba0_put_char ('{');
    for (i = 0; i < DL.Y.size; i++)
      {
        ba0_int_p j, nb_diff, var_index = 0;
        bool found = false;

        for (j = 0; j < leaders.size && !found; j++)
          {
            if (leaders.tab[j]->root == DL.Y.tab[i])
              {
                found = true;
                var_index = bav_order_variable (leaders.tab[j], DL.x);
              }
          }

        nb_diff = 2 * DL.k.tab[i] + 2;
        var_index += nb_diff - DL.r.tab[i];

        if (i > 0)
          ba0_printf (", ");
        ba0_printf (" %y : (%Qz, %d, %d)", DL.Y.tab[i], DL.A.tab[i], 
              var_index, nb_diff);
      }
    ba0_put_char ('}');

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
