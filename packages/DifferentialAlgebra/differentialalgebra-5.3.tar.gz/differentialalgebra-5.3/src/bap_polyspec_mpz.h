#if !defined (BAP_POLYSPEC_MPZ_H)
#   define BAP_POLYSPEC_MPZ_H 1

#   include "bap_common.h"
#   include "bap_polynom_mpz.h"
#   include "bap_product_mpz.h"
#   include "bap_polynom_mpzm.h"
#   include "bap_product_mpzm.h"
#   include "bap_polynom_mpq.h"

BEGIN_C_DECLS

extern BAP_DLL void bap_polynom_mpq_to_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_maxnorm_polynom_mpz (
    ba0_mpz_t,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_normal_sign_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_numeric_content_polynom_mpz (
    ba0_mpz_t,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_signed_numeric_content_polynom_mpz (
    ba0_mpz_t,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_numeric_primpart_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_normal_numeric_primpart_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_exquo_polynom_numeric_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    ba0_mpz_t);

extern BAP_DLL bool bap_is_numeric_factor_polynom_mpz (
    struct bap_polynom_mpz *,
    ba0_mpz_t,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_replace_initial2_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_separant_and_sepuctum_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_sepuctum_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

END_C_DECLS
#endif /* !BAP_POLYSPEC_MPZ_H */
