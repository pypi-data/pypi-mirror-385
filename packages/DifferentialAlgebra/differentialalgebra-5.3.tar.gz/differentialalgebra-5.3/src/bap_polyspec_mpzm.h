#if !defined (BAP_POLYSPEC_MPZM_H)
#   define BAP_POLYSPEC_MPZM_H 1

#   include "bap_common.h"
#   include "bap_polynom_mpz.h"
#   include "bap_polynom_mpzm.h"
#   include "bap_polynom_mpq.h"
#   include "bap_polynom_mint_hp.h"
#   include "bap_product_mpz.h"
#   include "bap_product_mpzm.h"

BEGIN_C_DECLS

extern BAP_DLL void bap_polynom_mpq_to_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_polynom_mpz_to_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_polynom_mint_hp_to_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_mods_polynom_mpzm (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_mods_product_mpzm (
    struct bap_product_mpz *,
    struct bap_product_mpzm *);

extern BAP_DLL void bap_Bezout_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    ba0_mpz_t,
    bav_Idegree);

extern BAP_DLL void bap_coeftayl_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_value_int_p *,
    bav_Idegree);

extern BAP_DLL void bap_quorem_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_rank *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_uni_Diophante_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_product_mpzm *,
    struct bav_rank *,
    ba0_mpz_t,
    bav_Idegree);

extern BAP_DLL void bap_multi_Diophante_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_product_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_point_int_p *,
    bav_Idegree,
    ba0_mpz_t,
    bav_Idegree);

END_C_DECLS
#endif /* !BAP_POLYSPEC_MPZM_H */
