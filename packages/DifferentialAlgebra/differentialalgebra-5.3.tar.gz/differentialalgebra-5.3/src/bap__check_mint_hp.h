#if !defined (BAP__CHECK_mint_hp_H)
#   define BAP__CHECK_mint_hp_H 1

#   include "bap_common.h"
#   include "bap_polynom_mint_hp.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mint_hp

extern BAP_DLL void bap__check_ordering_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap__check_compatible_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

#   undef BAD_FLAG_mint_hp

END_C_DECLS
#endif /* !BAP__CHECK_mint_hp_H */
