#if !defined (BAD_COMMON_H)
#   define BAD_COMMON_H 1

#   include <baz.h>

/* 
 * The _MSC_VER flag is set if the code is compiled under WINDOWS
 * by using Microsoft Visual C (through Visual Studio 2008).
 *
 * In that case, some specific annotations must be added for DLL exports
 * Beware to the fact that this header file is going to be used either
 * for/while building BLAD or for using BLAD from an outer software.
 *
 * In the first case, functions are exported.
 * In the second one, they are imported.
 *
 * The flag BAD_BLAD_BUILDING must thus be set in the Makefile and passed
 * to the C preprocessor at BAD building time. Do not set it when using BAD.
 *
 * When compiling static libraries under Windows, set BA0_STATIC.
 */

#   if defined (_MSC_VER) && ! defined (BA0_STATIC)
#      if defined (BLAD_BUILDING) || defined (BAD_BLAD_BUILDING)
#         define BAD_DLL  __declspec(dllexport)
#      else
#         define BAD_DLL  __declspec(dllimport)
#      endif
#   else
#      define BAD_DLL
#   endif

#   include "bad_mesgerr.h"

#   define BAD_NOT_A_NUMBER -1

BEGIN_C_DECLS
/* 
 * Restart functions
 */
extern BAD_DLL void bad_reset_all_settings (
    void);

extern BAD_DLL void bad_restart (
    ba0_int_p,
    ba0_int_p);

extern BAD_DLL void bad_terminate (
    enum ba0_restart_level);


END_C_DECLS
#endif /* !BAD_COMMON_H */
