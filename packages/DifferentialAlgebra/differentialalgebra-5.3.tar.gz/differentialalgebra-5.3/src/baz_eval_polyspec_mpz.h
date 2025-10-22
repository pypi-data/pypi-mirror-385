#if ! defined (BAZ_EVAL_POLYSPEC_MPZ_H)
#   define BAZ_EVAL_POLYSPEC_MPZ_H 1

#   include "baz_common.h"
#   include "baz_point_ratfrac.h"

BEGIN_C_DECLS

extern BAZ_DLL void baz_eval_to_ratfrac_at_point_ratfrac_polynom_mpz (
    struct baz_ratfrac *,
    struct bap_polynom_mpz *,
    struct baz_point_ratfrac *);

END_C_DECLS
#endif /* !BAZ_EVAL_POLYSPEC_MPZ_H */
