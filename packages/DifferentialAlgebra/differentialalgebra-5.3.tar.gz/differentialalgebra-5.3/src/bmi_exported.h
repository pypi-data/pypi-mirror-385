#if !defined (BMI_EXPORTED_H)
#   define BMI_EXPORTED_H 1

/*
 * This module provides the bmi_call_exported function.
 * This function is called by bmi_blad_eval.
 * It calls the exported function that needs to be called.
 *
 * The file bmi_exported.c is the only one to be modified, in order
 * to add a new exported function to the package.
 */

#   include <blad.h>
#   include "bmi_gmp.h"
#   include "bmi_memory.h"
#   include "bmi_rtable.h"
#   include "bmi_callback.h"

BEGIN_C_DECLS

extern ALGEB bmi_call_exported (
    char *,
    struct bmi_callback *);

END_C_DECLS
#endif /*! BMI_EXPORTED_H */
