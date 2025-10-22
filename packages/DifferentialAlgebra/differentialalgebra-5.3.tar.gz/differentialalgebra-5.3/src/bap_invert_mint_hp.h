#if !defined (BAP_INVERT_mint_hp_H)
#   define BAP_INVERT_mint_hp_H 1

#   include "bap_common.h"
#   include "bap_polynom_mint_hp.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mint_hp

extern BAP_DLL void bap_numeric_initial_one_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_Euclidean_division_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_Euclid_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_extended_Euclid_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

#   undef BAD_FLAG_mint_hp

END_C_DECLS
#endif /* !BAP_INVERT_mint_hp_H */
