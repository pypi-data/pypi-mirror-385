#if !defined (BAP_ADD_POLYNOM_mpzm_H)
#   define BAP_ADD_POLYNOM_mpzm_H 1

#   include "bap_polynom_mpzm.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mpzm

extern BAP_DLL void bap_add_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_add_polynom_numeric_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    ba0_mpzm_t);

extern BAP_DLL void bap_sub_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_submulmon_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_term *,
    ba0_mpzm_t);

extern BAP_DLL void bap_comblin_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    ba0_int_p,
    struct bap_polynom_mpzm *,
    ba0_int_p);

extern BAP_DLL void bap_addmulrk_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_rank *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_submulrk_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_rank *,
    struct bap_polynom_mpzm *);

#   undef  BAD_FLAG_mpzm

END_C_DECLS
#endif /* !BAP_ADD_POLYNOM_mpzm_H */
