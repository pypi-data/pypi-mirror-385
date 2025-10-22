#if !defined (BAP_ITERKOEFF_mpz_H)
#   define BAP_ITERKOEFF_mpz_H 1

#   include "bap_common.h"
#   include "bap_polynom_mpz.h"
#   include "bap_itermon_mpz.h"

#   define BAD_FLAG_mpz

BEGIN_C_DECLS

/*
 * texinfo: bap_itercoeff_mpz
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

struct bap_itercoeff_mpz
{
  struct bap_polynom_mpz *poly;       // the polynomial
  struct bav_variable *last_variable;   // the lowest variable among the terms
// debut is set on the first monomial of the current coefficient
  struct bap_itermon_mpz debut;
// fin is set on the last monomial of the current coefficient
  struct bap_itermon_mpz fin;
  bool outof;                   // true if the iterator is outside the polynomial
};


extern BAP_DLL void bap_begin_itercoeff_mpz (
    struct bap_itercoeff_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAP_DLL void bap_end_itercoeff_mpz (
    struct bap_itercoeff_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAP_DLL bool bap_outof_itercoeff_mpz (
    struct bap_itercoeff_mpz *);

extern BAP_DLL void bap_close_itercoeff_mpz (
    struct bap_itercoeff_mpz *);

extern BAP_DLL void bap_next_itercoeff_mpz (
    struct bap_itercoeff_mpz *);

extern BAP_DLL void bap_prev_itercoeff_mpz (
    struct bap_itercoeff_mpz *);

extern BAP_DLL void bap_term_itercoeff_mpz (
    struct bav_term *,
    struct bap_itercoeff_mpz *);

extern BAP_DLL void bap_coeff_itercoeff_mpz (
    struct bap_polynom_mpz *,
    struct bap_itercoeff_mpz *);

extern BAP_DLL void bap_seek_coeff_itercoeff_mpz (
    struct bap_polynom_mpz *,
    struct bap_itercoeff_mpz *,
    struct bav_term *);

extern BAP_DLL void bap_split_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_term *);

END_C_DECLS
#   undef  BAD_FLAG_mpz
#endif /* !BAP_ITERKOEFF_mpz_H */
