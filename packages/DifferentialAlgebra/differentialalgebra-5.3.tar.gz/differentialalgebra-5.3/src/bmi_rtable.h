#if !defined (BMI_RTABLE_H)
#   define BMI_RTABLE_H 1

/*
 * To reduce the communication overhead between MAPLE and BLAD, one avoids
 * parsing data, as much as possible.
 *
 * Some data are thus stored, in BLAD internal form, in MAPLE rtables.
 *
 * This module permits to create these rtables and to extract the data from rtables.
 */

#   include "bmi_common.h"
#   include "bmi_callback.h"

BEGIN_C_DECLS

extern ALGEB bmi_rtable_differential_ring (
    MKernelVector,
    char *,
    int);

extern ALGEB bmi_rtable_regchain (
    MKernelVector,
    struct bad_regchain *,
    char *,
    int);

extern ALGEB bmi_rtable_DLuple (
    MKernelVector,
    struct bas_DLuple *,
    char *,
    int);

extern bav_Iordering bmi_set_ordering (
    long,
    struct bmi_callback *,
    char *,
    int);

extern bav_Iordering bmi_set_ordering_and_regchain (
    struct bad_regchain *,
    long,
    struct bmi_callback *,
    char *,
    int);

extern bav_Iordering bmi_set_ordering_and_DLuple (
    struct bas_DLuple *,
    long,
    struct bmi_callback *,
    char *,
    int);

extern bav_Iordering bmi_set_ordering_and_intersectof_regchain (
    struct bad_intersectof_regchain *,
    long,
    struct bmi_callback *,
    char *,
    int);

END_C_DECLS
#endif /* !BMI_RTABLE_H */
