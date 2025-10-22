#include "bmi_exported.h"
#include "bmi_mesgerr.h"
#include "bmi_indices.h"
#include "bmi_frozen_symbols.h"

/*
 * Called as an EXPORTED function
 * However, this function is not exported, in the sense that it is not
 * available at the user-interface level.
 *
 * FrozenSymbols (sequence of symbols)
 *
 * Returns the list of the indices of the symbols which should be frozen,
 * since they cannot be parsed as ba0_indexed_string_as_a_string.
 */

ALGEB
bmi_frozen_symbols (
    struct bmi_callback *callback)
{
  struct ba0_tableof_string T;
  struct ba0_tableof_int_p U;
  ba0_int_p nargs, j;
  volatile ba0_int_p i;
  struct ba0_indexed_string indexed;

  nargs = bmi_nops (callback);

  ba0_init_table ((struct ba0_table *) &T);
  ba0_realloc_table ((struct ba0_table *) &T, nargs);

  ba0_init_table ((struct ba0_table *) &U);
  ba0_realloc_table ((struct ba0_table *) &U, nargs);

  for (i = 1; i <= nargs; i++)
    {
      T.tab[T.size] = bmi_string_op (i, callback);
      T.size += 1;
/*
 * If the parsing raises an error, the symbol should be frozen
 */
      BA0_TRY
      {
        ba0_init_indexed_string (&indexed);
        ba0_sscanf2 (T.tab[T.size - 1], "%indexed_string", &indexed);
      }
      BA0_CATCH
      {
        U.tab[U.size] = i;
        U.size += 1;
/*
ba0_printf ("mesgerr = %s\n", ba0_mesgerr);
*/
        continue;
      }
      BA0_ENDTRY;
/*
 * If the read symbol is not the complete symbol, it should be frozen
 */
      if (strcmp (ba0_indexed_string_to_string (&indexed), T.tab[T.size - 1]) != 0)
        {
          U.tab[U.size] = i;
          U.size += 1;
/*
ba0_printf ("not completely read: %s, %s\n", 
			ba0_indexed_string_to_string (&indexed), T.tab [T.size-1]);
*/
          continue;
        }
/*
 * If the symbol was already read, it should be frozen (mixed globals and
 * exported locals)
 */
      for (j = 0; j < T.size - 1; j++)
        {
          if (strcmp (T.tab[T.size - 1], T.tab[j]) == 0)
            {
              U.tab[U.size] = i;
              U.size += 1;
/*
ba0_printf ("already met at index %d\n", j+1);
*/
              continue;
            }
        }
    }

  {
    char *stres;
    ALGEB res;
    stres = ba0_new_printf ("%t[%d]", &U);
    bmi_push_maple_gmp_allocators ();
#if ! defined (BMI_BALSA)
    res = EvalMapleStatement (callback->kv, stres);
#else
    res = bmi_balsa_new_string (stres);
#endif
    bmi_pull_maple_gmp_allocators ();
    return res;
  }
}
