#if !defined (BAP_DUCOS_mpz_H)
#   define BAP_DUCOS_mpz_H 1

#   include "bap_common.h"
#   include "bap_polynom_mpz.h"
#   include "bap_product_mpz.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mpz

extern BAP_DLL void bap_muldiv_Lazard_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    bav_Idegree);

extern BAP_DLL void bap_muldiv2_Lazard_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    bav_Idegree);

extern BAP_DLL void bap_muldiv3_Lazard_polynom_mpz (
    struct bap_tableof_polynom_mpz *,
    struct bap_tableof_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    bav_Idegree);

extern BAP_DLL void bap_nsr2_Ducos_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAP_DLL void bap_nsr3_Ducos_polynom_mpz (
    struct bap_tableof_polynom_mpz *,
    struct bap_tableof_polynom_mpz *,
    struct bap_tableof_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAP_DLL void bap_resultant2_Ducos_polynom_mpz (
    struct bap_product_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAP_DLL void bap_lsr3_Ducos_polynom_mpz (
    struct bap_tableof_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

#   undef BAD_FLAG_mpz

END_C_DECLS
#endif /* !BAP_DUCOS_mpz_H */
