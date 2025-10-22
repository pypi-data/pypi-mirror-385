#if ! defined (BAZ_RATBILGE_H)
#   define BAZ_RATBILGE_H 1

#   include "baz_ratfrac.h"

BEGIN_C_DECLS

extern BAZ_DLL void baz_rat_bilge_mpz (
    struct baz_ratfrac *,
    struct baz_ratfrac *,
    struct baz_ratfrac *,
    struct bav_symbol *);

END_C_DECLS
#endif
