#if ! defined (BAZ_PROSPEC_MPZ_H)
#   define BAZ_PROSPEC_MPZ_H 1

#   include "baz_common.h"

BEGIN_C_DECLS

extern BAZ_DLL void baz_factor_numeric_content_product_mpz (
    struct bap_product_mpz *,
    struct bap_product_mpz *);

extern BAZ_DLL void baz_gcd_product_mpz (
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bap_product_mpz *);

END_C_DECLS
#endif /* !BAZ_PROSPEC_MPZ_H */
