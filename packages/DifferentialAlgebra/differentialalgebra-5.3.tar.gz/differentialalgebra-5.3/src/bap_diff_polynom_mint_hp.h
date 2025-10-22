#if !defined (BAP_DIFF_POLYNOM_mint_hp_H)
#   define BAP_DIFF_POLYNOM_mint_hp_H 1

#   include "bap_common.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mint_hp
extern BAP_DLL bool bap_is_constant_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bav_symbol *);

extern BAP_DLL bool bap_is_polynomial_with_constant_coefficients_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bav_variable *,
    struct bav_symbol *);

extern BAP_DLL bool bap_is_independent_polynom_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_diff_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_symbol *);

extern BAP_DLL void bap_diff2_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_term *);

extern BAP_DLL void bap_involved_derivations_polynom_mint_hp (
    struct bav_tableof_variable *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_involved_parameters_polynom_mint_hp (
    struct bav_dictionary_symbol *,
    struct bav_tableof_symbol *,
    struct bap_polynom_mint_hp *);

#   undef  BAD_FLAG_mint_hp

END_C_DECLS
#endif /* !BAP_DIFF_POLYNOM_mint_hp_H */
