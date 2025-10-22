#if !defined (BAD_REDUCED_FORM_H)
#   define BAD_REDUCED_FORM_H 1

#   include "bad_common.h"
#   include "bad_regchain.h"
#   include "bad_intersectof_regchain.h"

BEGIN_C_DECLS

extern BAD_DLL void bad_reduced_form_polynom_mod_regchain (
    struct baz_ratfrac *,
    struct bap_polynom_mpz *,
    struct bav_variable *,
    struct bad_regchain *);

extern BAD_DLL void bad_reduced_form_polynom_mod_intersectof_regchain (
    struct baz_tableof_ratfrac *,
    struct bap_polynom_mpz *,
    struct bav_variable *,
    struct bad_intersectof_regchain *);

END_C_DECLS
#endif /* !BAD_REDUCED_FORM_H */
