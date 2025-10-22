#if !defined (BAP_CREATOR_mpzm_H)
#   define BAP_CREATOR_mpzm_H 1

#   include "bap_common.h"
#   include "bap_clot_mpzm.h"
#   include "bap_polynom_mpzm.h"

#   define BAD_FLAG_mpzm

BEGIN_C_DECLS

/*
 * texinfo: bap_creator_mpzm
 * This data type permits to create a polynomial from scratch
 * by giving, in decreasing order, its terms and numerical
 * coefficients.
 */

struct bap_creator_mpzm
{
// the polynomial to create
  struct bap_polynom_mpzm *poly;
// a creator for the clot of the polynomial
  struct bap_creator_clot_mpzm crea;
// the type of the total rank provided when initializing the process
  enum bap_typeof_total_rank type;
};


extern BAP_DLL void bap_begin_creator_mpzm (
    struct bap_creator_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_term *,
    enum bap_typeof_total_rank,
    ba0_int_p);

extern BAP_DLL void bap_append_creator_mpzm (
    struct bap_creator_mpzm *,
    struct bap_polynom_mpzm *,
    ba0_int_p);

extern BAP_DLL void bap_write_creator_mpzm (
    struct bap_creator_mpzm *,
    struct bav_term *,
    ba0_mpzm_t);

extern BAP_DLL void bap_write_neg_creator_mpzm (
    struct bap_creator_mpzm *,
    struct bav_term *,
    ba0_mpzm_t);

extern BAP_DLL bool bap_is_write_allable_creator_mpzm (
    struct bap_creator_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_write_all_creator_mpzm (
    struct bap_creator_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_write_neg_all_creator_mpzm (
    struct bap_creator_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_write_mul_all_creator_mpzm (
    struct bap_creator_mpzm *,
    struct bap_polynom_mpzm *,
    ba0_mpzm_t);

#   if defined BAD_FLAG_mpz

extern BAP_DLL void bap_write_exquo_all_creator_mpz (
    struct bap_creator_mpz *,
    struct bap_polynom_mpz *,
    ba0_mpz_t);

#   endif

extern BAP_DLL void bap_close_creator_mpzm (
    struct bap_creator_mpzm *);

END_C_DECLS
#   undef  BAD_FLAG_mpzm
#endif /* !BAP_CREATOR_mpzm_H */
