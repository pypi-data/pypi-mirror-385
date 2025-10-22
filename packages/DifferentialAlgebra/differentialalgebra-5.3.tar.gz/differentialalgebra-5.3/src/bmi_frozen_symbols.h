#if !defined (BMI_FROZEN_SYMBOLS_H)
#   define BMI_FROZEN_SYMBOLS_H 1

#   include <blad.h>
#   include "bmi_callback.h"

/*
 * This function is called as an exported function.
 * However, it is not exported.
 */

BEGIN_C_DECLS

extern ALGEB bmi_frozen_symbols (
    struct bmi_callback *);

END_C_DECLS
#endif /*! BMI_FROZEN_SYMBOLS_H */
