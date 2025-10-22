#if ! defined (BAD_RESULTANT_H)
#   define BAD_RESULTANT_H 1

#   include "bad_regchain.h"

BEGIN_C_DECLS

extern BAD_DLL void bad_resultant_mod_regchain (
    struct bap_product_mpz *,
    struct bap_polynom_mpz *,
    struct bad_regchain *);

END_C_DECLS
#endif /* BAD_RESULTANT_H */
