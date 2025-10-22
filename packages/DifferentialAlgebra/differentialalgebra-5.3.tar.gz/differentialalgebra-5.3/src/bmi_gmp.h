#if !defined (BMI_GMP_H)
#   define BMI_GMP_H 1

/*
 * This module manages the memory allocators of the GMP library.
 *
 * Indeed, when BLAD performs a computation, the BLAD GMP allocators
 * should be on. When MAPLE performs a computatiion, the MAPLE GMP
 * allocators should be on.
 *
 * Todo: simplify this overly complicated system which was designed
 * before the embedding of mini-gmp in BLAD
 */

#   include "bmi_common.h"

BEGIN_C_DECLS

extern void bmi_init_gmp_allocators_management (
    MKernelVector);
extern void bmi_push_maple_gmp_allocators (
    void);
extern void bmi_pull_maple_gmp_allocators (
    void);

extern void bmi_check_blad_gmp_allocators (
    char *,
    int);
extern void bmi_check_maple_gmp_allocators (
    char *,
    int);
extern void bmi_check_gmp_sp (
    void);

extern void bmi_push_blad_gmp_allocators (
    void);
extern void bmi_pull_blad_gmp_allocators (
    void);

END_C_DECLS
#endif /* !BMI_GMP_H */
