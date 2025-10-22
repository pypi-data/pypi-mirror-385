#if ! defined (BAZ_FACTOR_POLYNOM_MPQ_H)
#   define BAZ_FACTOR_POLYNOM_MPQ_H 1

#   include "baz_common.h"

BEGIN_C_DECLS

extern BAZ_DLL void baz_factor_polynom_mpq (
    struct bap_product_mpq *,
    struct bap_polynom_mpq *);

END_C_DECLS
#endif /* !BAZ_FACTOR_POLYNOM_MPQ_H */
