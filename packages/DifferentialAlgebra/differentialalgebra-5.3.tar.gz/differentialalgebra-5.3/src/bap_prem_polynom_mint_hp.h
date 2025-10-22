#if !defined (BAP_PREM_POLYNOM_mint_hp_H)
#   define BAP_PREM_POLYNOM_mint_hp_H 1

#   include "bap_polynom_mint_hp.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mint_hp

extern BAP_DLL bool bap_is_numeric_factor_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    ba0_mint_hp_t,
    struct bap_polynom_mint_hp *);

extern BAP_DLL bool bap_is_variable_factor_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bav_variable *,
    bav_Idegree *);

extern BAP_DLL bool bap_is_factor_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL bool bap_is_factor_tableof_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_tableof_polynom_mint_hp *);

extern BAP_DLL void bap_exquo_polynom_term_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_term *);

extern BAP_DLL void bap_exquo_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

struct bap_product_mint_hp;

extern BAP_DLL void bap_exquo_polynom_product_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_product_mint_hp *);

extern BAP_DLL void bap_pseudo_division_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    bav_Idegree *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

extern BAP_DLL void bap_prem_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    bav_Idegree *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

extern BAP_DLL void bap_pquo_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    bav_Idegree *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

extern BAP_DLL void bap_rem_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

#   undef  BAD_FLAG_mint_hp

END_C_DECLS
#endif /* !BAP_PREM_POLYNOM_mint_hp_H */
