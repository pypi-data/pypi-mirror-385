#if !defined (BAP_MUL_POLYNOM_mpq_H)
#   define BAP_MUL_POLYNOM_mpq_H 1

#   include "bap_polynom_mpq.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mpq

extern BAP_DLL void bap_neg_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_mul_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_mul_polynom_variable_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_mul_polynom_term_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_term *);

extern BAP_DLL void bap_mul_polynom_monom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    ba0_mpq_t,
    struct bav_term *);

extern BAP_DLL void bap_mul_polynom_numeric_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    ba0_mpq_t);

extern BAP_DLL void bap_mul_polynom_value_int_p_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_value_int_p *);

extern BAP_DLL void bap_pow_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    bav_Idegree);

#   undef  BAD_FLAG_mpq

END_C_DECLS
#endif /* !BAP_MUL_POLYNOM_mpq_H */
