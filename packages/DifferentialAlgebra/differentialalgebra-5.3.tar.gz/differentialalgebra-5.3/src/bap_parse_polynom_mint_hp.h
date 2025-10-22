#if !defined (BAP_PARSE_POLYNOM_mint_hp_H)
#   define BAP_PARSE_POLYNOM_mint_hp_H 1

#   include "bap_common.h"
#   include "bap_clot_mint_hp.h"
#   include "bap_sequential_access.h"
#   include "bap_indexed_access.h"
#   include "bap_termstripper.h"
#   include "bap_polynom_mint_hp.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mint_hp

extern BAP_DLL ba0_scanf_function bap_scanf_polynom_eqn_mint_hp;

extern BAP_DLL ba0_scanf_function bap_scanf_expanded_polynom_mint_hp;

extern BAP_DLL ba0_scanf_function bap_scanf_polynom_mint_hp;

extern BAP_DLL ba0_scanf_function bap_scanf_simplify_polynom_mint_hp;

extern BAP_DLL ba0_scanf_function bap_scanf_atomic_polynom_mint_hp;

extern BAP_DLL ba0_scanf_function bap_scanf_simplify_expanded_polynom_mint_hp;

extern BAP_DLL ba0_printf_function bap_printf_polynom_mint_hp;

extern BAP_DLL void bap_simplify_zero_derivatives_of_parameter_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

#   undef  BAD_FLAG_mint_hp

END_C_DECLS
#endif /* !BAP_PARSE_POLYNOM_mint_hp_H */
