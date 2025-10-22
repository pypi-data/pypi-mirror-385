#if !defined (BMI_MEMORY_H)
#   define BMI_MEMORY_H 1

#   include "bmi_callback.h"

BEGIN_C_DECLS

extern struct bmi_callback *bmi_init_memory (
    MKernelVector);
extern void bmi_clear_memory (
    void);

extern void bmi_check_error_sp (
    void);

END_C_DECLS
#endif /* !BMI_MEMORY_H */
