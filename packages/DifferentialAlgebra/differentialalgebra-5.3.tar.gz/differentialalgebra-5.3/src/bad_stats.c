#include "bad_stats.h"
#include "bad_global.h"

/*
 * texinfo: bad_init_stats
 * Reset to zero all counters (see the @code{bad_global.stats} variable). 
 * This function is called by @code{bad_pardi} and 
 * @code{bad_Rosenfeld_Groebner}.
 */

BAD_DLL void
bad_init_stats (
    void)
{
  bad_global.stats.begin = 0;
  bad_global.stats.end = 0;
  bad_global.stats.critical_pairs_processed = 0;
  bad_global.stats.reductions_to_zero = 0;
}

/*
 * texinfo: bad_printf_stats
 * Print the statistics on the standard output.
 * See the @code{bad_global.stats} variable.
 */

BAD_DLL void
bad_printf_stats (
    void *a)
{
  ba0_int_p secs, min;
  a = (void *) 0;

  secs = (ba0_int_p) bad_global.stats.end - (ba0_int_p) bad_global.stats.begin;
  min = secs / 60;
  secs = secs - min * 60;

  ba0_printf ("stats: elapsed time = %d minutes %d seconds\n", min, secs);
  ba0_printf ("stats: critical_pairs_processed = %d, reductions_to_zero = %d\n",
      bad_global.stats.critical_pairs_processed,
      bad_global.stats.reductions_to_zero);
}
