#if !defined (BAP_DIFF_POLYNOM_mpq_H)
#   define BAP_DIFF_POLYNOM_mpq_H 1

#   include "bap_common.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mpq
extern BAP_DLL bool bap_is_constant_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bav_symbol *);

extern BAP_DLL bool bap_is_polynomial_with_constant_coefficients_mpq (
    struct bap_polynom_mpq *,
    struct bav_variable *,
    struct bav_symbol *);

extern BAP_DLL bool bap_is_independent_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_diff_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_symbol *);

extern BAP_DLL void bap_diff2_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_term *);

extern BAP_DLL void bap_involved_derivations_polynom_mpq (
    struct bav_tableof_variable *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_involved_parameters_polynom_mpq (
    struct bav_dictionary_symbol *,
    struct bav_tableof_symbol *,
    struct bap_polynom_mpq *);

#   undef  BAD_FLAG_mpq

END_C_DECLS
#endif /* !BAP_DIFF_POLYNOM_mpq_H */
