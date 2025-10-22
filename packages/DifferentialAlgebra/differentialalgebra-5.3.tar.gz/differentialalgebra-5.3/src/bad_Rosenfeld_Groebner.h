#if !defined (BAD_ROSENFELD_GROEBNER_H)
#   define BAD_ROSENFELD_GROEBNER_H 1

#   include "bad_common.h"
#   include "bad_intersectof_regchain.h"
#   include "bad_base_field.h"
#   include "bad_splitting_control.h"
#   include "bad_splitting_tree.h"

BEGIN_C_DECLS

extern BAD_DLL void bad_Rosenfeld_Groebner (
    struct bad_intersectof_regchain *,
    struct bad_splitting_tree *,
    struct bap_tableof_polynom_mpz *,
    struct bap_tableof_polynom_mpz *,
    struct bad_base_field *,
    struct bad_regchain *,
    struct bad_splitting_control *);

extern BAD_DLL void bad_first_quadruple (
    struct bad_tableof_quadruple *,
    struct bad_attchain *,
    struct bap_tableof_polynom_mpz *,
    struct bap_tableof_polynom_mpz *,
    enum bad_typeof_reduction,
    struct bad_base_field *,
    struct bad_regchain *);

END_C_DECLS
#endif /* !BAD_ROSENFELD_GROEBNER_H */
