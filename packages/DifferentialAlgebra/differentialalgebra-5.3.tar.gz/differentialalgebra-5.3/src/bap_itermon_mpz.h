#if !defined (BAP_ITERMON_mpz_H)
#   define BAP_ITERMON_mpz_H 1

#   include "bap_common.h"
#   include "bap_polynom_mpz.h"
#   include "bap_iterator_indexed_access.h"

#   define BAD_FLAG_mpz

BEGIN_C_DECLS

/*
 * texinfo: bap_itermon_mpz
 * This data type implements an iterator of monomials of a
 * differential polynomials, viewed as multivariate polynomial
 * over the numerical coefficients.
 * The monomials of the polynomial may be accessed either in
 * sequential access as in indexed access.
 */

struct bap_itermon_mpz
{
  struct bap_polynom_mpz *poly;       // the polynomial
// an iterator of monomials of poly->clot
  struct bap_itermon_clot_mpz iter;
// an auxiliary data structure if access is indexed
// it provides the current index in poly->ind.tab
  struct bap_iterator_indexed_access iter_ix;
};


extern BAP_DLL void bap_begin_itermon_mpz (
    struct bap_itermon_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_end_itermon_mpz (
    struct bap_itermon_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_close_itermon_mpz (
    struct bap_itermon_mpz *);

extern BAP_DLL void bap_set_itermon_mpz (
    struct bap_itermon_mpz *,
    struct bap_itermon_mpz *);

extern BAP_DLL bool bap_outof_itermon_mpz (
    struct bap_itermon_mpz *);

extern BAP_DLL void bap_next_itermon_mpz (
    struct bap_itermon_mpz *);

extern BAP_DLL void bap_prev_itermon_mpz (
    struct bap_itermon_mpz *);

extern BAP_DLL void bap_goto_itermon_mpz (
    struct bap_itermon_mpz *,
    ba0_int_p);

extern BAP_DLL ba0_mpz_t *bap_coeff_itermon_mpz (
    struct bap_itermon_mpz *);

extern BAP_DLL void bap_term_itermon_mpz (
    struct bav_term *,
    struct bap_itermon_mpz *);

extern BAP_DLL void bap_reductum_itermon_mpz (
    struct bap_itermon_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_seekfirst_itermon_mpz (
    struct bap_itermon_mpz *,
    enum bap_rank_code (*)(struct bav_term *,
        struct bav_term *,
        bav_Inumber),
    struct bav_term *,
    bav_Inumber);

extern BAP_DLL void bap_seeklast_itermon_mpz (
    struct bap_itermon_mpz *,
    enum bap_rank_code (*)(struct bav_term *,
        struct bav_term *,
        bav_Inumber),
    struct bav_term *,
    bav_Inumber);

END_C_DECLS
#   undef  BAD_FLAG_mpz
#endif /* !BAP_ITERMON_mpz_H */
