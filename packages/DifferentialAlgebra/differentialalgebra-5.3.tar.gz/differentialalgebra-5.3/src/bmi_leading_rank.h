#if !defined (BMI_LEADING_RANK_H)
#   define BMI_LEADING_RANK_H 1

#   include <blad.h>
#   include "bmi_callback.h"

BEGIN_C_DECLS

extern ALGEB bmi_leading_rank (
    struct bmi_callback *);
extern ALGEB bmi_leading_rank_list_form (
    struct bmi_callback *);

END_C_DECLS
#endif /*! BMI_LEADING_RANK_H */
