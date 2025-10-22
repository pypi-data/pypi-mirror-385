#if ! defined (BAZ_FACTOR_POLYNOM_MPZ_H)
#   define BAZ_FACTOR_POLYNOM_MPZ_H 1

#   include "baz_common.h"

BEGIN_C_DECLS

extern BAZ_DLL void baz_factor_polynom_mpz (
    struct bap_product_mpz *,
    struct bap_polynom_mpz *);

END_C_DECLS
#endif /* ! BAZ_FACTOR_POLYNOM_MPZ_H */
