#if ! defined (BA0_MESGERR_H)
#   define BA0_MESGERR_H

#   include "ba0_common.h"

BEGIN_C_DECLS
/* 
 * A bug is discovered in the library (should not happen error).
 *  Repair: fix the bug.
 */
extern BA0_DLL char BA0_ERRALG[];

extern BA0_DLL char BA0_ERRNYP[];

extern BA0_DLL char BA0_ERRNCE[];

/* 
 * Memory problems.
 * Repair: reconfigure the library (resize some constants).
 */

extern BA0_DLL char BA0_ERROOM[];

extern BA0_DLL char BA0_ERRSOV[];

extern BA0_DLL char BA0_ERRMFR[];

/* 
 * Giving up computations because of a signal.
 */

extern BA0_DLL char BA0_ERRSIG[];

extern BA0_DLL char BA0_ERRALR[];

extern BA0_DLL char BA0_ERRNCI[];

/* 
 * Mathematical errors
 */

extern BA0_DLL char BA0_ERRIVZ[];

extern BA0_DLL char BA0_ERRDDZ[];

extern BA0_DLL char BA0_EXWRNT[];

extern BA0_DLL char BA0_EXWDDZ[];

extern BA0_DLL char BA0_ERRMAT[];

extern BA0_DLL char BA0_ERRNIL[];

extern BA0_DLL char BA0_ERRZCI[];

/* 
 * Parser errors
 */

extern BA0_DLL char BA0_ERREOF[];

extern BA0_DLL char BA0_ERRSYN[];

extern BA0_DLL char BA0_ERRSTR[];

extern BA0_DLL char BA0_ERRINT[];

extern BA0_DLL char BA0_ERRBOOL[];

extern BA0_DLL char BA0_ERRFLT[];

extern BA0_DLL char BA0_ERRRAT[];

extern BA0_DLL char BA0_ERRAMB[];

/*
 * Other errors
 */

extern BA0_DLL char BA0_ERRKEY[];

END_C_DECLS
#endif /* !BA0_MESGERR_H */
