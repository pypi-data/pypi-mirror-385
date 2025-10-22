#if !defined (BAP_MUL_POLYNOM_mint_hp_H)
#   define BAP_MUL_POLYNOM_mint_hp_H 1

#   include "bap_polynom_mint_hp.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mint_hp

extern BAP_DLL void bap_neg_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_mul_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_mul_polynom_variable_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_mul_polynom_term_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_term *);

extern BAP_DLL void bap_mul_polynom_monom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    ba0_mint_hp_t,
    struct bav_term *);

extern BAP_DLL void bap_mul_polynom_numeric_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    ba0_mint_hp_t);

extern BAP_DLL void bap_mul_polynom_value_int_p_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_value_int_p *);

extern BAP_DLL void bap_pow_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    bav_Idegree);

#   undef  BAD_FLAG_mint_hp

END_C_DECLS
#endif /* !BAP_MUL_POLYNOM_mint_hp_H */
