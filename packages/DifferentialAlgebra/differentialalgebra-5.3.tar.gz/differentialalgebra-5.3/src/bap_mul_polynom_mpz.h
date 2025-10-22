#if !defined (BAP_MUL_POLYNOM_mpz_H)
#   define BAP_MUL_POLYNOM_mpz_H 1

#   include "bap_polynom_mpz.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mpz

extern BAP_DLL void bap_neg_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_mul_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_mul_polynom_variable_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_mul_polynom_term_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_term *);

extern BAP_DLL void bap_mul_polynom_monom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    ba0_mpz_t,
    struct bav_term *);

extern BAP_DLL void bap_mul_polynom_numeric_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    ba0_mpz_t);

extern BAP_DLL void bap_mul_polynom_value_int_p_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_value_int_p *);

extern BAP_DLL void bap_pow_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    bav_Idegree);

#   undef  BAD_FLAG_mpz

END_C_DECLS
#endif /* !BAP_MUL_POLYNOM_mpz_H */
