#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_Denef_Lipshitz_series.h"

/*
 * EXPORTED
 * DenefLipshitzSeries (vars, DLuple)
 *
 * vars is a list of subscripted variables such as y[6], z[8], ...
 * DLuple is a DLuple
 *
 * Return a string "{ y : series_for_y, z : series_for_z }"
 */

ALGEB 
bmi_Denef_Lipshitz_series (
    struct bmi_callback *callback)
{
  char *str_vars;

  struct bas_DLuple DL;
  struct baz_tableof_tableof_ratfrac T;
  struct bav_tableof_variable vars;

  ba0_int_p i;
  char *buffer;
  ALGEB result;

  if (bmi_nops (callback) == 2)
    {
      if (!bmi_is_table_op (2, callback))
        BA0_RAISE_EXCEPTION (BMI_ERRDLUP);

      bmi_set_ordering_and_DLuple (&DL, 2, callback, __FILE__, __LINE__);
    }
  else
    BA0_RAISE_EXCEPTION (BMI_ERRNOPS);

  str_vars = bmi_string_op (1, callback);

  ba0_init_table ((struct ba0_table *) &vars);
  ba0_sscanf2 (str_vars, "%t[%v]", &vars);

  bas_prolongate_DLuple (&DL, &DL, &vars);

  ba0_init_table ((struct ba0_table *) &T);
  bas_series_coefficients_DLuple (&T, &DL);

  ba0_record_output ();
  BA0_TRY
  {
    ba0_set_output_counter ();
    ba0_put_char ('{');
    for (i = 0; i < DL.Y.size; i++)
      {
        struct baz_tableof_ratfrac *Ti = T.tab[i];
        ba0_int_p j;

        if (i > 0)
          ba0_printf (", ");
        ba0_printf (" %y : ", DL.Y.tab[i]);
        if (Ti->size == 0)
          ba0_printf ("0");
        else
          ba0_printf ("%Qz", Ti->tab[0]);
        for (j = 1; j < Ti->size; j++)
          ba0_printf (" + (%Qz)*%y**%d", Ti->tab[j], DL.x, j);
      }
    ba0_put_char ('}');

    buffer = ba0_persistent_malloc (ba0_output_counter () + 1);
    ba0_set_output_string (buffer);

    ba0_put_char ('{');
    for (i = 0; i < DL.Y.size; i++)
      {
        struct baz_tableof_ratfrac *Ti = T.tab[i];
        ba0_int_p j;

        if (i > 0)
          ba0_printf (", ");
        ba0_printf (" %y : ", DL.Y.tab[i]);
        if (Ti->size == 0)
          ba0_printf ("0");
        else
          ba0_printf ("%Qz", Ti->tab[0]);
        for (j = 1; j < Ti->size; j++)
          ba0_printf (" + (%Qz)*%y**%d", Ti->tab[j], DL.x, j);
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
