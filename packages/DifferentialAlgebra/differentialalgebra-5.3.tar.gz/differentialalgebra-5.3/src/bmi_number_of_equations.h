#if !defined (BMI_NUMBER_OF_EQUATIONS)
#   define BMI_NUMBER_OF_EQUATIONS 1

#   include <blad.h>
#   include "bmi_callback.h"

BEGIN_C_DECLS

extern ALGEB bmi_number_of_equations (
    struct bmi_callback *);

END_C_DECLS
#endif /*! BMI_NUMBER_OF_EQUATIONS */
