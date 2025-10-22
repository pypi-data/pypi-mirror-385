#if !defined (BAP__CHECK_mpzm_H)
#   define BAP__CHECK_mpzm_H 1

#   include "bap_common.h"
#   include "bap_polynom_mpzm.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mpzm

extern BAP_DLL void bap__check_ordering_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap__check_compatible_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

#   undef BAD_FLAG_mpzm

END_C_DECLS
#endif /* !BAP__CHECK_mpzm_H */
