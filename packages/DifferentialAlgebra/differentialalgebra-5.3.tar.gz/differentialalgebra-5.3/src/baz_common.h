#if ! defined (BAZ_COMMON_H)
#   define BAZ_COMMON_H 1

#   include <bap.h>

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
 * The flag BAZ_BLAD_BUILDING must thus be set in the Makefile and passed
 * to the C preprocessor at BAP building time. Do not set it when using BAP.
 *
 * When compiling static libraries under Windows, set BA0_STATIC.
 */

#   if defined (_MSC_VER) && ! defined (BA0_STATIC)
#      if defined (BLAD_BUILDING) || defined (BAZ_BLAD_BUILDING)
#         define BAZ_DLL  __declspec(dllexport)
#      else
#         define BAZ_DLL  __declspec(dllimport)
#      endif
#   else
#      define BAZ_DLL
#   endif

#   include "baz_mesgerr.h"

BEGIN_C_DECLS

extern BAZ_DLL void baz_reset_all_settings (
    void);

extern BAZ_DLL void baz_restart (
    ba0_int_p,
    ba0_int_p);

extern BAZ_DLL void baz_terminate (
    enum ba0_restart_level);

END_C_DECLS
#endif /* !BAZ_COMMON_H */
