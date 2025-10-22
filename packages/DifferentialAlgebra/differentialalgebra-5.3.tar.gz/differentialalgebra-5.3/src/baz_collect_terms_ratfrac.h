#if ! defined (BAZ_COLLECT_TERMS_RATFRAC_H)
#   define BAZ_COLLECT_TERMS_RATFRAC_H 1

#   include "baz_ratfrac.h"

BEGIN_C_DECLS

extern BAZ_DLL void baz_collect_terms_tableof_ratfrac (
    struct baz_tableof_ratfrac *,
    struct baz_tableof_ratfrac *,
    struct baz_tableof_ratfrac *,
    struct baz_tableof_ratfrac *);

END_C_DECLS
#endif /*! BAZ_COLLECT_TERMS_RATFRAC_H */
