#if !defined (BAP_PARSE_POLYNOM_mpzm_H)
#   define BAP_PARSE_POLYNOM_mpzm_H 1

#   include "bap_common.h"
#   include "bap_clot_mpzm.h"
#   include "bap_sequential_access.h"
#   include "bap_indexed_access.h"
#   include "bap_termstripper.h"
#   include "bap_polynom_mpzm.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mpzm

extern BAP_DLL ba0_scanf_function bap_scanf_polynom_eqn_mpzm;

extern BAP_DLL ba0_scanf_function bap_scanf_expanded_polynom_mpzm;

extern BAP_DLL ba0_scanf_function bap_scanf_polynom_mpzm;

extern BAP_DLL ba0_scanf_function bap_scanf_simplify_polynom_mpzm;

extern BAP_DLL ba0_scanf_function bap_scanf_atomic_polynom_mpzm;

extern BAP_DLL ba0_scanf_function bap_scanf_simplify_expanded_polynom_mpzm;

extern BAP_DLL ba0_printf_function bap_printf_polynom_mpzm;

extern BAP_DLL void bap_simplify_zero_derivatives_of_parameter_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

#   undef  BAD_FLAG_mpzm

END_C_DECLS
#endif /* !BAP_PARSE_POLYNOM_mpzm_H */
