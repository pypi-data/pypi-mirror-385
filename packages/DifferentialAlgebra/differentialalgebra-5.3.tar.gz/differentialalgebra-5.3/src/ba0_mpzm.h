#if !defined (BA0_MPZM_H)
#   define BA0_MPZM_H 1

#   include "ba0_common.h"
#   include "ba0_macros_mpzm.h"

BEGIN_C_DECLS

struct ba0_tableof_mpzm
{
  ba0_int_p alloc;
  ba0_int_p size;
  ba0__mpz_struct **tab;
};


struct ba0_listof_mpzm
{
  ba0__mpz_struct *value;
  struct ba0_listof_mpzm *next;
};


#   define ba0_mpzm_module_is_prime        ba0_global.mpzm.module_is_prime
#   define ba0_mpzm_module			ba0_global.mpzm.module
#   define ba0_mpzm_half_module		ba0_global.mpzm.half_module
#   define ba0_mpzm_accum			ba0_global.mpzm.accum

extern BA0_DLL void ba0_init_mpzm_module (
    void);

extern BA0_DLL void ba0_reset_mpzm_module (
    void);

extern BA0_DLL bool ba0_domain_mpzm (
    void);

extern BA0_DLL void ba0_mpzm_module_set_ui (
    unsigned ba0_int_p,
    bool);

extern BA0_DLL void ba0_mpzm_module_set (
    ba0_mpz_t,
    bool);

extern BA0_DLL void ba0_mpzm_module_mul (
    ba0_mpz_t);

extern BA0_DLL void ba0_mpzm_module_pow_ui (
    ba0_mpz_t,
    unsigned ba0_int_p,
    bool);

extern BA0_DLL ba0__mpz_struct *ba0_new_mpzm (
    void);

extern BA0_DLL ba0_scanf_function ba0_scanf_mpzm;

extern BA0_DLL ba0_printf_function ba0_printf_mpzm;

extern BA0_DLL ba0_garbage1_function ba0_garbage1_mpzm;

extern BA0_DLL ba0_garbage2_function ba0_garbage2_mpzm;

extern BA0_DLL ba0_copy_function ba0_copy_mpzm;

extern BA0_DLL enum ba0_wang_code ba0_wang_mpzm (
    ba0_mpq_t,
    ba0_mpz_t,
    ba0_mpz_t);

END_C_DECLS
#endif /* !BA0_MPZM_H */
