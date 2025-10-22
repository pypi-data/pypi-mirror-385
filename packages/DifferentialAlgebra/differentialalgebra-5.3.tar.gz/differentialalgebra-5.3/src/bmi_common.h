#if !defined (BMI_COMMON_H)
#   define BMI_COMMON_H 1

/*
 * The _MSC_VER flag is set if the code is compiled under WINDOWS
 * by using Microsoft Visual C (through Visual Studio 2008).
 *
 * In that case, some specific annotations must be added for DLL exports
 * Beware to the fact that this header file is going to be used either
 * for/while building BMI or for using BMI from an outer software.
 *
 * In the first case, functions are exported.
 * In the second one, they are imported.
 *
 * The flag BMI_BUILDING must thus be set in the Makefile and passed
 * to the C preprocessor at BMI building time. Do not set it when using BMI.
 *
 */

#   include <blad.h>

#   if ! defined (BMI_MAPLE)
#      define BMI_BALSA
#      include "config.h"
#      include "bmi_balsa.h"
#   else
#      include <maplec.h>
#   endif

#   if defined (_MSC_VER)
#      if defined (BMI_BUILDING)
#         define BMI_DLL  __declspec(dllexport)
#      else
#         define BMI_DLL  __declspec(dllimport)
#      endif
#   else
#      define BMI_DLL
#   endif

#endif /*! BMI_COMMON_H */
