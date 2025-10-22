#if !defined (BAP_PARSE_POLYNOM_mpz_H)
#   define BAP_PARSE_POLYNOM_mpz_H 1

#   include "bap_common.h"
#   include "bap_clot_mpz.h"
#   include "bap_sequential_access.h"
#   include "bap_indexed_access.h"
#   include "bap_termstripper.h"
#   include "bap_polynom_mpz.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mpz

extern BAP_DLL ba0_scanf_function bap_scanf_polynom_eqn_mpz;

extern BAP_DLL ba0_scanf_function bap_scanf_expanded_polynom_mpz;

extern BAP_DLL ba0_scanf_function bap_scanf_polynom_mpz;

extern BAP_DLL ba0_scanf_function bap_scanf_simplify_polynom_mpz;

extern BAP_DLL ba0_scanf_function bap_scanf_atomic_polynom_mpz;

extern BAP_DLL ba0_scanf_function bap_scanf_simplify_expanded_polynom_mpz;

extern BAP_DLL ba0_printf_function bap_printf_polynom_mpz;

extern BAP_DLL void bap_simplify_zero_derivatives_of_parameter_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

#   undef  BAD_FLAG_mpz

END_C_DECLS
#endif /* !BAP_PARSE_POLYNOM_mpz_H */
