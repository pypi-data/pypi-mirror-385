#if !defined (BAP_ADD_POLYNOM_mpz_H)
#   define BAP_ADD_POLYNOM_mpz_H 1

#   include "bap_polynom_mpz.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mpz

extern BAP_DLL void bap_add_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_add_polynom_numeric_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    ba0_mpz_t);

extern BAP_DLL void bap_sub_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_submulmon_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_term *,
    ba0_mpz_t);

extern BAP_DLL void bap_comblin_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    ba0_int_p,
    struct bap_polynom_mpz *,
    ba0_int_p);

extern BAP_DLL void bap_addmulrk_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_rank *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_submulrk_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_rank *,
    struct bap_polynom_mpz *);

#   undef  BAD_FLAG_mpz

END_C_DECLS
#endif /* !BAP_ADD_POLYNOM_mpz_H */
