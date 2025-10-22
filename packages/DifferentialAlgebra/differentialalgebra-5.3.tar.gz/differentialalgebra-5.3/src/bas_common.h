#if !defined (BAS_COMMON_H)
#   define BAS_COMMON_H 1

#   include <bad.h>

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
 * The flag BAS_BLAD_BUILDING must thus be set in the Makefile and passed
 * to the C preprocessor at BAS building time. Do not set it when using BAS.
 *
 * When compiling static libraries under Windows, set BA0_STATIC.
 */

#   if defined (_MSC_VER) && ! defined (BA0_STATIC)
#      if defined (BLAD_BUILDING) || defined (BAS_BLAD_BUILDING)
#         define BAS_DLL  __declspec(dllexport)
#      else
#         define BAS_DLL  __declspec(dllimport)
#      endif
#   else
#      define BAS_DLL
#   endif

#   include "bas_mesgerr.h"

/* 
 * For Solaris 8
 */

#   if HAVE_IEEEFP_H
#      include <ieeefp.h>
#   endif

BEGIN_C_DECLS

#   define BAS_NOT_A_NUMBER -1

extern BAS_DLL void bas_reset_all_settings (
    void);

extern BAS_DLL void bas_restart (
    ba0_int_p,
    ba0_int_p);

extern BAS_DLL void bas_terminate (
    enum ba0_restart_level);

END_C_DECLS
#endif /* !BAS_COMMON_H */
