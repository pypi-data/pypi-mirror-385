#if !defined (BAP_PARSE_POLYNOM_mpq_H)
#   define BAP_PARSE_POLYNOM_mpq_H 1

#   include "bap_common.h"
#   include "bap_clot_mpq.h"
#   include "bap_sequential_access.h"
#   include "bap_indexed_access.h"
#   include "bap_termstripper.h"
#   include "bap_polynom_mpq.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mpq

extern BAP_DLL ba0_scanf_function bap_scanf_polynom_eqn_mpq;

extern BAP_DLL ba0_scanf_function bap_scanf_expanded_polynom_mpq;

extern BAP_DLL ba0_scanf_function bap_scanf_polynom_mpq;

extern BAP_DLL ba0_scanf_function bap_scanf_simplify_polynom_mpq;

extern BAP_DLL ba0_scanf_function bap_scanf_atomic_polynom_mpq;

extern BAP_DLL ba0_scanf_function bap_scanf_simplify_expanded_polynom_mpq;

extern BAP_DLL ba0_printf_function bap_printf_polynom_mpq;

extern BAP_DLL void bap_simplify_zero_derivatives_of_parameter_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

#   undef  BAD_FLAG_mpq

END_C_DECLS
#endif /* !BAP_PARSE_POLYNOM_mpq_H */
