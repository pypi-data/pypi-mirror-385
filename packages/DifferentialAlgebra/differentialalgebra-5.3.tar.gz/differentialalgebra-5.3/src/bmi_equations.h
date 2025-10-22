#if !defined (BMI_EQUATIONS_H)
#   define BMI_EQUATIONS_H 1

#   include <blad.h>
#   include "bmi_callback.h"

BEGIN_C_DECLS

extern ALGEB bmi_equations (
    struct bmi_callback *);
extern ALGEB bmi_equations_with_criterion (
    struct bmi_callback *);
extern ALGEB bmi_rewrite_rules (
    struct bmi_callback *);
extern ALGEB bmi_rewrite_rules_with_criterion (
    struct bmi_callback *);

END_C_DECLS
#endif /*! BMI_EQUATIONS_H */
