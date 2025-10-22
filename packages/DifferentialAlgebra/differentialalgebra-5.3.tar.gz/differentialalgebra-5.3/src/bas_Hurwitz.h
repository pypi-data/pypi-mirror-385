#if ! defined (BAS_HURWITZ_H)
#   define BAS_HURWITZ_H 1

#   include "bas_common.h"

BEGIN_C_DECLS

extern BAS_DLL void bas_Hurwitz_coeffs (
    struct bap_tableof_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    ba0_int_p,
    struct bav_symbol *);

END_C_DECLS
#endif /* !BAS_HURWITZ_H */
