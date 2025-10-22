#if !defined (BAD_INVERT_H)
#   define BAD_INVERT_H 1

#   include "bad_common.h"
#   include "bad_regchain.h"
#   include "bad_quadruple.h"
#   include "bad_base_field.h"

BEGIN_C_DECLS

extern BAD_DLL void bad_invert_polynom_mod_regchain (
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bap_polynom_mpz *,
    struct bad_regchain *,
    struct bad_base_field *,
    struct bap_polynom_mpz *volatile *);

extern BAD_DLL void bad_invert_product_mod_regchain (
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bad_regchain *,
    struct bad_base_field *,
    struct bap_polynom_mpz *volatile *);

extern BAD_DLL void bad_iterated_lsr3_product_mod_regchain (
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bad_regchain *);

END_C_DECLS
#endif /* !BAD_INVERT_H */
