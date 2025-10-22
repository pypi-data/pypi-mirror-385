#if !defined (BAP_PREM_POLYNOM_mpz_H)
#   define BAP_PREM_POLYNOM_mpz_H 1

#   include "bap_polynom_mpz.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mpz

extern BAP_DLL bool bap_is_numeric_factor_polynom_mpz (
    struct bap_polynom_mpz *,
    ba0_mpz_t,
    struct bap_polynom_mpz *);

extern BAP_DLL bool bap_is_variable_factor_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bav_variable *,
    bav_Idegree *);

extern BAP_DLL bool bap_is_factor_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL bool bap_is_factor_tableof_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_tableof_polynom_mpz *);

extern BAP_DLL void bap_exquo_polynom_term_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_term *);

extern BAP_DLL void bap_exquo_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

struct bap_product_mpz;

extern BAP_DLL void bap_exquo_polynom_product_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_product_mpz *);

extern BAP_DLL void bap_pseudo_division_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    bav_Idegree *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAP_DLL void bap_prem_polynom_mpz (
    struct bap_polynom_mpz *,
    bav_Idegree *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAP_DLL void bap_pquo_polynom_mpz (
    struct bap_polynom_mpz *,
    bav_Idegree *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAP_DLL void bap_rem_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

#   undef  BAD_FLAG_mpz

END_C_DECLS
#endif /* !BAP_PREM_POLYNOM_mpz_H */
