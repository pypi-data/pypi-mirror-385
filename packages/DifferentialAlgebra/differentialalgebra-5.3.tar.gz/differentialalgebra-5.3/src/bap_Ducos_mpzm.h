#if !defined (BAP_DUCOS_mpzm_H)
#   define BAP_DUCOS_mpzm_H 1

#   include "bap_common.h"
#   include "bap_polynom_mpzm.h"
#   include "bap_product_mpzm.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mpzm

extern BAP_DLL void bap_muldiv_Lazard_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    bav_Idegree);

extern BAP_DLL void bap_muldiv2_Lazard_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    bav_Idegree);

extern BAP_DLL void bap_muldiv3_Lazard_polynom_mpzm (
    struct bap_tableof_polynom_mpzm *,
    struct bap_tableof_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    bav_Idegree);

extern BAP_DLL void bap_nsr2_Ducos_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *);

extern BAP_DLL void bap_nsr3_Ducos_polynom_mpzm (
    struct bap_tableof_polynom_mpzm *,
    struct bap_tableof_polynom_mpzm *,
    struct bap_tableof_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *);

extern BAP_DLL void bap_resultant2_Ducos_polynom_mpzm (
    struct bap_product_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *);

extern BAP_DLL void bap_lsr3_Ducos_polynom_mpzm (
    struct bap_tableof_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *);

#   undef BAD_FLAG_mpzm

END_C_DECLS
#endif /* !BAP_DUCOS_mpzm_H */
