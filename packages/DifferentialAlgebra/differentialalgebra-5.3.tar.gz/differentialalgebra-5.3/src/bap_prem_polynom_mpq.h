#if !defined (BAP_PREM_POLYNOM_mpq_H)
#   define BAP_PREM_POLYNOM_mpq_H 1

#   include "bap_polynom_mpq.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mpq

extern BAP_DLL bool bap_is_numeric_factor_polynom_mpq (
    struct bap_polynom_mpq *,
    ba0_mpq_t,
    struct bap_polynom_mpq *);

extern BAP_DLL bool bap_is_variable_factor_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bav_variable *,
    bav_Idegree *);

extern BAP_DLL bool bap_is_factor_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL bool bap_is_factor_tableof_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_tableof_polynom_mpq *);

extern BAP_DLL void bap_exquo_polynom_term_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_term *);

extern BAP_DLL void bap_exquo_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

struct bap_product_mpq;

extern BAP_DLL void bap_exquo_polynom_product_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_product_mpq *);

extern BAP_DLL void bap_pseudo_division_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    bav_Idegree *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL void bap_prem_polynom_mpq (
    struct bap_polynom_mpq *,
    bav_Idegree *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL void bap_pquo_polynom_mpq (
    struct bap_polynom_mpq *,
    bav_Idegree *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL void bap_rem_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

#   undef  BAD_FLAG_mpq

END_C_DECLS
#endif /* !BAP_PREM_POLYNOM_mpq_H */
