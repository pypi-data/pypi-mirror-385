#if ! defined (BA0_MINT_HP_H)
#   define BA0_MINT_HP_H 1

#   include "ba0_common.h"
#   include "ba0_gmp.h"
#   include "ba0_macros_mint_hp.h"
#   include "ba0_macros_mpq.h"

BEGIN_C_DECLS

struct ba0_tableof_mint_hp
{
  ba0_int_p alloc;
  ba0_int_p size;
  ba0_int_p **tab;              /* not ba0_mint_hp ! */
};


struct ba0_listof_mint_hp
{
  ba0_int_p value;              /* not ba0_mint_hp ! */
  struct ba0_listof_mint_hp *next;
};


#   define ba0_mint_hp_module		ba0_global.mint_hp.module
#   define ba0_mint_hp_module_is_prime	ba0_global.mint_hp.module_is_prime

extern BA0_DLL void ba0_reset_mint_hp_module (
    void);

extern BA0_DLL bool ba0_domain_mint_hp (
    void);

extern BA0_DLL void ba0_mint_hp_module_set (
    ba0_mint_hp,
    bool);

extern BA0_DLL ba0_mint_hp ba0_pow_mint_hp (
    ba0_mint_hp,
    ba0_int_p);

extern BA0_DLL ba0_scanf_function ba0_scanf_mint_hp;

extern BA0_DLL ba0_printf_function ba0_printf_mint_hp;

extern BA0_DLL ba0_mint_hp ba0_invert_mint_hp (
    ba0_mint_hp);

extern BA0_DLL enum ba0_wang_code ba0_wang_mint_hp (
    ba0_mpq_t,
    ba0_mint_hp,
    ba0_int_hp *);

END_C_DECLS
#endif /* !BA0_MINT_HP_H */
