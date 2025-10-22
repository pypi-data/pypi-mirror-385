#if !defined (BMI_BLAD_EVAL_H)
#   define BMI_BLAD_EVAL_H 1

#   include "bmi_common.h"
#   define BMI_BUFSIZE	1024

BEGIN_C_DECLS

extern BMI_DLL ALGEB M_DECL bmi_blad_eval (
    MKernelVector,
    ALGEB);
extern BMI_DLL ALGEB M_DECL bmi_blad_eval_python (
    MKernelVector,
    ALGEB);

END_C_DECLS
#endif /*! BMI_BLAD_EVAL_H */
