#if !defined (BAP_ADD_POLYNOM_mint_hp_H)
#   define BAP_ADD_POLYNOM_mint_hp_H 1

#   include "bap_polynom_mint_hp.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mint_hp

extern BAP_DLL void bap_add_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_add_polynom_numeric_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    ba0_mint_hp_t);

extern BAP_DLL void bap_sub_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_submulmon_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_term *,
    ba0_mint_hp_t);

extern BAP_DLL void bap_comblin_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    ba0_int_p,
    struct bap_polynom_mint_hp *,
    ba0_int_p);

extern BAP_DLL void bap_addmulrk_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_rank *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_submulrk_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_rank *,
    struct bap_polynom_mint_hp *);

#   undef  BAD_FLAG_mint_hp

END_C_DECLS
#endif /* !BAP_ADD_POLYNOM_mint_hp_H */
