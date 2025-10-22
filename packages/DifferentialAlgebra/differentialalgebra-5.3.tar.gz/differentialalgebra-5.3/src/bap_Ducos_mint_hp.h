#if !defined (BAP_DUCOS_mint_hp_H)
#   define BAP_DUCOS_mint_hp_H 1

#   include "bap_common.h"
#   include "bap_polynom_mint_hp.h"
#   include "bap_product_mint_hp.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mint_hp

extern BAP_DLL void bap_muldiv_Lazard_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    bav_Idegree);

extern BAP_DLL void bap_muldiv2_Lazard_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    bav_Idegree);

extern BAP_DLL void bap_muldiv3_Lazard_polynom_mint_hp (
    struct bap_tableof_polynom_mint_hp *,
    struct bap_tableof_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    bav_Idegree);

extern BAP_DLL void bap_nsr2_Ducos_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

extern BAP_DLL void bap_nsr3_Ducos_polynom_mint_hp (
    struct bap_tableof_polynom_mint_hp *,
    struct bap_tableof_polynom_mint_hp *,
    struct bap_tableof_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

extern BAP_DLL void bap_resultant2_Ducos_polynom_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

extern BAP_DLL void bap_lsr3_Ducos_polynom_mint_hp (
    struct bap_tableof_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

#   undef BAD_FLAG_mint_hp

END_C_DECLS
#endif /* !BAP_DUCOS_mint_hp_H */
