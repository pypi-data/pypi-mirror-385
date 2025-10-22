#if !defined (BAP_ITERKOEFF_mint_hp_H)
#   define BAP_ITERKOEFF_mint_hp_H 1

#   include "bap_common.h"
#   include "bap_polynom_mint_hp.h"
#   include "bap_itermon_mint_hp.h"

#   define BAD_FLAG_mint_hp

BEGIN_C_DECLS

/*
 * texinfo: bap_itercoeff_mint_hp
 * This data type implements an iterator of coefficients of a 
 * differential polynomials, with respect to a given variable.
 * Let @var{A} be a polynomial and @math{X = x_1 < \cdots < x_n} be 
 * the alphabet of the variables it depends on. 
 * Let @math{1 \leq i \leq n} be an index.
 * The iterator permits to extract the coefficients of @var{A}, viewed as 
 * a polynomial over the alphabet @math{x_i, \ldots, x_n}, with 
 * coefficients in the ring of the polynomials over the alphabet 
 * @math{x_1, \ldots, x_{i-1}}.
 */

struct bap_itercoeff_mint_hp
{
  struct bap_polynom_mint_hp *poly;       // the polynomial
  struct bav_variable *last_variable;   // the lowest variable among the terms
// debut is set on the first monomial of the current coefficient
  struct bap_itermon_mint_hp debut;
// fin is set on the last monomial of the current coefficient
  struct bap_itermon_mint_hp fin;
  bool outof;                   // true if the iterator is outside the polynomial
};


extern BAP_DLL void bap_begin_itercoeff_mint_hp (
    struct bap_itercoeff_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

extern BAP_DLL void bap_end_itercoeff_mint_hp (
    struct bap_itercoeff_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

extern BAP_DLL bool bap_outof_itercoeff_mint_hp (
    struct bap_itercoeff_mint_hp *);

extern BAP_DLL void bap_close_itercoeff_mint_hp (
    struct bap_itercoeff_mint_hp *);

extern BAP_DLL void bap_next_itercoeff_mint_hp (
    struct bap_itercoeff_mint_hp *);

extern BAP_DLL void bap_prev_itercoeff_mint_hp (
    struct bap_itercoeff_mint_hp *);

extern BAP_DLL void bap_term_itercoeff_mint_hp (
    struct bav_term *,
    struct bap_itercoeff_mint_hp *);

extern BAP_DLL void bap_coeff_itercoeff_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_itercoeff_mint_hp *);

extern BAP_DLL void bap_seek_coeff_itercoeff_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_itercoeff_mint_hp *,
    struct bav_term *);

extern BAP_DLL void bap_split_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_term *);

END_C_DECLS
#   undef  BAD_FLAG_mint_hp
#endif /* !BAP_ITERKOEFF_mint_hp_H */
