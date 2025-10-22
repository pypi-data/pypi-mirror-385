#if !defined (BAP_MUL_POLYNOM_mpzm_H)
#   define BAP_MUL_POLYNOM_mpzm_H 1

#   include "bap_polynom_mpzm.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mpzm

extern BAP_DLL void bap_neg_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_mul_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_mul_polynom_variable_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_mul_polynom_term_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_term *);

extern BAP_DLL void bap_mul_polynom_monom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    ba0_mpzm_t,
    struct bav_term *);

extern BAP_DLL void bap_mul_polynom_numeric_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    ba0_mpzm_t);

extern BAP_DLL void bap_mul_polynom_value_int_p_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_value_int_p *);

extern BAP_DLL void bap_pow_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    bav_Idegree);

#   undef  BAD_FLAG_mpzm

END_C_DECLS
#endif /* !BAP_MUL_POLYNOM_mpzm_H */
