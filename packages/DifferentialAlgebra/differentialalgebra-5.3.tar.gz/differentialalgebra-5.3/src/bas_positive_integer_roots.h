#if ! defined (BAS_POSITIVE_INTEGER_ROOTS_H)
#   define BAS_POSITIVE_INTEGER_ROOTS_H 1

#   include "bas_common.h"

BEGIN_C_DECLS

extern BAS_DLL void bas_nonnegative_integer_roots (
    struct ba0_tableof_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *,
    struct bad_regchain *);

END_C_DECLS
#endif /* !BAS_POSITIVE_INTEGER_ROOTS_H */
