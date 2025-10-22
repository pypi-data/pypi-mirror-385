#if !defined (BAP__CHECK_mpq_H)
#   define BAP__CHECK_mpq_H 1

#   include "bap_common.h"
#   include "bap_polynom_mpq.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mpq

extern BAP_DLL void bap__check_ordering_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL void bap__check_compatible_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

#   undef BAD_FLAG_mpq

END_C_DECLS
#endif /* !BAP__CHECK_mpq_H */
