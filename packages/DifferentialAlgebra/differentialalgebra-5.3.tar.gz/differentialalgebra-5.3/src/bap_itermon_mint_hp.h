#if !defined (BAP_ITERMON_mint_hp_H)
#   define BAP_ITERMON_mint_hp_H 1

#   include "bap_common.h"
#   include "bap_polynom_mint_hp.h"
#   include "bap_iterator_indexed_access.h"

#   define BAD_FLAG_mint_hp

BEGIN_C_DECLS

/*
 * texinfo: bap_itermon_mint_hp
 * This data type implements an iterator of monomials of a
 * differential polynomials, viewed as multivariate polynomial
 * over the numerical coefficients.
 * The monomials of the polynomial may be accessed either in
 * sequential access as in indexed access.
 */

struct bap_itermon_mint_hp
{
  struct bap_polynom_mint_hp *poly;       // the polynomial
// an iterator of monomials of poly->clot
  struct bap_itermon_clot_mint_hp iter;
// an auxiliary data structure if access is indexed
// it provides the current index in poly->ind.tab
  struct bap_iterator_indexed_access iter_ix;
};


extern BAP_DLL void bap_begin_itermon_mint_hp (
    struct bap_itermon_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_end_itermon_mint_hp (
    struct bap_itermon_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_close_itermon_mint_hp (
    struct bap_itermon_mint_hp *);

extern BAP_DLL void bap_set_itermon_mint_hp (
    struct bap_itermon_mint_hp *,
    struct bap_itermon_mint_hp *);

extern BAP_DLL bool bap_outof_itermon_mint_hp (
    struct bap_itermon_mint_hp *);

extern BAP_DLL void bap_next_itermon_mint_hp (
    struct bap_itermon_mint_hp *);

extern BAP_DLL void bap_prev_itermon_mint_hp (
    struct bap_itermon_mint_hp *);

extern BAP_DLL void bap_goto_itermon_mint_hp (
    struct bap_itermon_mint_hp *,
    ba0_int_p);

extern BAP_DLL ba0_mint_hp_t *bap_coeff_itermon_mint_hp (
    struct bap_itermon_mint_hp *);

extern BAP_DLL void bap_term_itermon_mint_hp (
    struct bav_term *,
    struct bap_itermon_mint_hp *);

extern BAP_DLL void bap_reductum_itermon_mint_hp (
    struct bap_itermon_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_seekfirst_itermon_mint_hp (
    struct bap_itermon_mint_hp *,
    enum bap_rank_code (*)(struct bav_term *,
        struct bav_term *,
        bav_Inumber),
    struct bav_term *,
    bav_Inumber);

extern BAP_DLL void bap_seeklast_itermon_mint_hp (
    struct bap_itermon_mint_hp *,
    enum bap_rank_code (*)(struct bav_term *,
        struct bav_term *,
        bav_Inumber),
    struct bav_term *,
    bav_Inumber);

END_C_DECLS
#   undef  BAD_FLAG_mint_hp
#endif /* !BAP_ITERMON_mint_hp_H */
