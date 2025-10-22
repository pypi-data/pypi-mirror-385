#if !defined (BAI_COMMON_H)
#   define BAI_COMMON_H 1

#   include <bas.h>

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
 * The flag BAI_BLAD_BUILDING must thus be set in the Makefile and passed
 * to the C preprocessor at BAI building time. Do not set it when using BAI.
 *
 * When compiling static libraries under Windows, set BA0_STATIC.
 */

#   if defined (_MSC_VER) && ! defined (BA0_STATIC)
#      if defined (BLAD_BUILDING) || defined (BAI_BLAD_BUILDING)
#         define BAI_DLL  __declspec(dllexport)
#      else
#         define BAI_DLL  __declspec(dllimport)
#      endif
#   else
#      define BAI_DLL
#   endif

#   include "bai_mesgerr.h"

/* 
 * For Solaris 8
 */

#   if HAVE_IEEEFP_H
#      include <ieeefp.h>
#   endif

BEGIN_C_DECLS

extern BAI_DLL void bai_reset_all_settings (
    void);

extern BAI_DLL void bai_restart (
    ba0_int_p,
    ba0_int_p);

extern BAI_DLL void bai_terminate (
    enum ba0_restart_level);

END_C_DECLS
#endif /* !BAI_COMMON_H */
