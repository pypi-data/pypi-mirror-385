#if !defined (BAP_CREATOR_mpz_H)
#   define BAP_CREATOR_mpz_H 1

#   include "bap_common.h"
#   include "bap_clot_mpz.h"
#   include "bap_polynom_mpz.h"

#   define BAD_FLAG_mpz

BEGIN_C_DECLS

/*
 * texinfo: bap_creator_mpz
 * This data type permits to create a polynomial from scratch
 * by giving, in decreasing order, its terms and numerical
 * coefficients.
 */

struct bap_creator_mpz
{
// the polynomial to create
  struct bap_polynom_mpz *poly;
// a creator for the clot of the polynomial
  struct bap_creator_clot_mpz crea;
// the type of the total rank provided when initializing the process
  enum bap_typeof_total_rank type;
};


extern BAP_DLL void bap_begin_creator_mpz (
    struct bap_creator_mpz *,
    struct bap_polynom_mpz *,
    struct bav_term *,
    enum bap_typeof_total_rank,
    ba0_int_p);

extern BAP_DLL void bap_append_creator_mpz (
    struct bap_creator_mpz *,
    struct bap_polynom_mpz *,
    ba0_int_p);

extern BAP_DLL void bap_write_creator_mpz (
    struct bap_creator_mpz *,
    struct bav_term *,
    ba0_mpz_t);

extern BAP_DLL void bap_write_neg_creator_mpz (
    struct bap_creator_mpz *,
    struct bav_term *,
    ba0_mpz_t);

extern BAP_DLL bool bap_is_write_allable_creator_mpz (
    struct bap_creator_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_write_all_creator_mpz (
    struct bap_creator_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_write_neg_all_creator_mpz (
    struct bap_creator_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_write_mul_all_creator_mpz (
    struct bap_creator_mpz *,
    struct bap_polynom_mpz *,
    ba0_mpz_t);

#   if defined BAD_FLAG_mpz

extern BAP_DLL void bap_write_exquo_all_creator_mpz (
    struct bap_creator_mpz *,
    struct bap_polynom_mpz *,
    ba0_mpz_t);

#   endif

extern BAP_DLL void bap_close_creator_mpz (
    struct bap_creator_mpz *);

END_C_DECLS
#   undef  BAD_FLAG_mpz
#endif /* !BAP_CREATOR_mpz_H */
