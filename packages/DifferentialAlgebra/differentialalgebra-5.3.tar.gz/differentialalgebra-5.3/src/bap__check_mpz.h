#if !defined (BAP__CHECK_mpz_H)
#   define BAP__CHECK_mpz_H 1

#   include "bap_common.h"
#   include "bap_polynom_mpz.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mpz

extern BAP_DLL void bap__check_ordering_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL void bap__check_compatible_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

#   undef BAD_FLAG_mpz

END_C_DECLS
#endif /* !BAP__CHECK_mpz_H */
