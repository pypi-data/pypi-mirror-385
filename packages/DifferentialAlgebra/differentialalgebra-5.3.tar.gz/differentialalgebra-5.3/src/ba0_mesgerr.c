#include "ba0_mesgerr.h"

/* A bug is discovered in the library (should not happen error).
   Repair: fix the bug.
*/
BA0_DLL char BA0_ERRALG[] = "runtime error";
BA0_DLL char BA0_ERRNYP[] = "not yet implemented";
BA0_DLL char BA0_ERRNCE[] = "uncaught exception";

/* Memory problems.
   Repair: reconfigure the library (resize memory of stacks)
*/
BA0_DLL char BA0_ERROOM[] = "out of memory error";
BA0_DLL char BA0_ERRSOV[] = "stack overflow error";
BA0_DLL char BA0_ERRMFR[] = "all the malloc(ed) memory is not freed";

/* Giving up computations because of a signal.
*/
BA0_DLL char BA0_ERRSIG[] = "interrupt";
BA0_DLL char BA0_ERRALR[] = "out of time error";
BA0_DLL char BA0_ERRNCI[] = "check interrupt switched on with no handler";

/* Mathematical errors
*/
BA0_DLL char BA0_ERRIVZ[] = "division by zero";
BA0_DLL char BA0_ERRDDZ[] = "inversion of a zero divisor";
BA0_DLL char BA0_EXWRNT[] = "Wang's algorithm: rational number not found";
BA0_DLL char BA0_EXWDDZ[] = "Wang's algorithm: inversion of a zero divisor";
BA0_DLL char BA0_ERRMAT[] = "sizes of matrices are incompatible";
BA0_DLL char BA0_ERRNIL[] = "non empty list expected";
BA0_DLL char BA0_ERRZCI[] = "zero containing interval unexpected";

/* Parser errors
*/
BA0_DLL char BA0_ERREOF[] = "EOF read";
BA0_DLL char BA0_ERRSYN[] = "syntax error";
BA0_DLL char BA0_ERRSTR[] = "string expected";
BA0_DLL char BA0_ERRINT[] = "integer expected";
BA0_DLL char BA0_ERRBOOL[] = "bool expected";
BA0_DLL char BA0_ERRFLT[] = "floating point number expected";
BA0_DLL char BA0_ERRRAT[] = "numerical denominator expected";
BA0_DLL char BA0_ERRAMB[] = "point with pairwise distinct variables expected";

/*
 * Other errors
 */

BA0_DLL char BA0_ERRKEY[] = "non already existing key expected";
