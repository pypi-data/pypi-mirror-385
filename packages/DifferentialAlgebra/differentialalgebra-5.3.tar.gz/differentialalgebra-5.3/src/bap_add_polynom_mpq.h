#if !defined (BAP_ADD_POLYNOM_mpq_H)
#   define BAP_ADD_POLYNOM_mpq_H 1

#   include "bap_polynom_mpq.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mpq

extern BAP_DLL void bap_add_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_add_polynom_numeric_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    ba0_mpq_t);

extern BAP_DLL void bap_sub_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_submulmon_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_term *,
    ba0_mpq_t);

extern BAP_DLL void bap_comblin_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    ba0_int_p,
    struct bap_polynom_mpq *,
    ba0_int_p);

extern BAP_DLL void bap_addmulrk_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_rank *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_submulrk_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_rank *,
    struct bap_polynom_mpq *);

#   undef  BAD_FLAG_mpq

END_C_DECLS
#endif /* !BAP_ADD_POLYNOM_mpq_H */
