#if !defined (BAP_DIFF_POLYNOM_mpz_H)
#   define BAP_DIFF_POLYNOM_mpz_H 1

#   include "bap_common.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mpz
extern BAP_DLL bool bap_is_constant_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bav_symbol *);

extern BAP_DLL bool bap_is_polynomial_with_constant_coefficients_mpz (
    struct bap_polynom_mpz *,
    struct bav_variable *,
    struct bav_symbol *);

extern BAP_DLL bool bap_is_independent_polynom_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_diff_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_symbol *);

extern BAP_DLL void bap_diff2_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_term *);

extern BAP_DLL void bap_involved_derivations_polynom_mpz (
    struct bav_tableof_variable *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_involved_parameters_polynom_mpz (
    struct bav_dictionary_symbol *,
    struct bav_tableof_symbol *,
    struct bap_polynom_mpz *);

#   undef  BAD_FLAG_mpz

END_C_DECLS
#endif /* !BAP_DIFF_POLYNOM_mpz_H */
