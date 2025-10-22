#if !defined (BAP_POLYSPEC_MPQ_H)
#   define BAP_POLYSPEC_MPQ_H 1

#   include "bap_common.h"
#   include "bap_polynom_mpq.h"
#   include "bap_polynom_mpz.h"
#   include "bap_product_mpq.h"

BEGIN_C_DECLS

extern BAP_DLL void bap_polynom_mpq_to_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_polynom_mpz_to_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_set_polynom_numer_denom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpz *,
    ba0_mpz_t);

extern BAP_DLL void bap_product_mpz_to_mpq (
    struct bap_product_mpq *,
    struct bap_product_mpz *);

extern BAP_DLL void bap_numer_polynom_mpq (
    struct bap_polynom_mpz *,
    ba0_mpz_t,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_denom_polynom_mpq (
    ba0_mpz_t,
    struct bap_polynom_mpq *);

END_C_DECLS
#endif /* !BAP_POLYSPEC_MPQ_H */
