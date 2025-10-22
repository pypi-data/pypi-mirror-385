#if !defined (BAP_GEOBUCKET_mpz_H)
#   define BAP_GEOBUCKET_mpz_H 1

#   include "bap_common.h"
#   include "bap_polynom_mpz.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mpz

/*
 * texinfo: bap_geobucket_mpz
 * A geobucket (JSC (1998) 25, 285-293, Thomas Yan) is a table of polynomials
 * representing the sum of these polynomials. This data structure
 * permits to improve the complexity of the sum of many different
 * polynomials.
 * The polynomial at index @var{i} is a sum of at most @var{2^i} 
 * monomials.
 * The data structure is a duplicate of @code{bap_tableof_polynomial}.
 */

struct bap_geobucket_mpz
{
// number of allocated entries
  ba0_int_p alloc;
// number of used entries
  ba0_int_p size;
// the array
  struct bap_polynom_mpz **tab;
};



extern BAP_DLL void bap_init_geobucket_mpz (
    struct bap_geobucket_mpz *);

extern BAP_DLL void bap_reset_geobucket_mpz (
    struct bap_geobucket_mpz *);

extern BAP_DLL void bap_mul_geobucket_mpz (
    struct bap_geobucket_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_mul_geobucket_numeric_mpz (
    struct bap_geobucket_mpz *,
    ba0_mpz_t);

extern BAP_DLL void bap_add_geobucket_mpz (
    struct bap_geobucket_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_sub_geobucket_mpz (
    struct bap_geobucket_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_set_polynom_geobucket_mpz (
    struct bap_polynom_mpz *,
    struct bap_geobucket_mpz *);

#   undef BAD_FLAG_mpz

END_C_DECLS
#endif /* !BAP_GEOBUCKET_mpz_H */
