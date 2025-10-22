#if !defined (BAP_PREM_POLYNOM_mpzm_H)
#   define BAP_PREM_POLYNOM_mpzm_H 1

#   include "bap_polynom_mpzm.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mpzm

extern BAP_DLL bool bap_is_numeric_factor_polynom_mpzm (
    struct bap_polynom_mpzm *,
    ba0_mpzm_t,
    struct bap_polynom_mpzm *);

extern BAP_DLL bool bap_is_variable_factor_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bav_variable *,
    bav_Idegree *);

extern BAP_DLL bool bap_is_factor_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL bool bap_is_factor_tableof_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_tableof_polynom_mpzm *);

extern BAP_DLL void bap_exquo_polynom_term_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_term *);

extern BAP_DLL void bap_exquo_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

struct bap_product_mpzm;

extern BAP_DLL void bap_exquo_polynom_product_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_product_mpzm *);

extern BAP_DLL void bap_pseudo_division_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    bav_Idegree *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *);

extern BAP_DLL void bap_prem_polynom_mpzm (
    struct bap_polynom_mpzm *,
    bav_Idegree *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *);

extern BAP_DLL void bap_pquo_polynom_mpzm (
    struct bap_polynom_mpzm *,
    bav_Idegree *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *);

extern BAP_DLL void bap_rem_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *);

#   undef  BAD_FLAG_mpzm

END_C_DECLS
#endif /* !BAP_PREM_POLYNOM_mpzm_H */
