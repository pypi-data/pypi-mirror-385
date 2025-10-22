#if !defined (BAP_INVERT_mpzm_H)
#   define BAP_INVERT_mpzm_H 1

#   include "bap_common.h"
#   include "bap_polynom_mpzm.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mpzm

extern BAP_DLL void bap_numeric_initial_one_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_Euclidean_division_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_Euclid_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_extended_Euclid_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

#   undef BAD_FLAG_mpzm

END_C_DECLS
#endif /* !BAP_INVERT_mpzm_H */
