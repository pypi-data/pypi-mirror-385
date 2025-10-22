#if !defined (BAP_GEOBUCKET_mpzm_H)
#   define BAP_GEOBUCKET_mpzm_H 1

#   include "bap_common.h"
#   include "bap_polynom_mpzm.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mpzm

/*
 * texinfo: bap_geobucket_mpzm
 * A geobucket (JSC (1998) 25, 285-293, Thomas Yan) is a table of polynomials
 * representing the sum of these polynomials. This data structure
 * permits to improve the complexity of the sum of many different
 * polynomials.
 * The polynomial at index @var{i} is a sum of at most @var{2^i} 
 * monomials.
 * The data structure is a duplicate of @code{bap_tableof_polynomial}.
 */

struct bap_geobucket_mpzm
{
// number of allocated entries
  ba0_int_p alloc;
// number of used entries
  ba0_int_p size;
// the array
  struct bap_polynom_mpzm **tab;
};



extern BAP_DLL void bap_init_geobucket_mpzm (
    struct bap_geobucket_mpzm *);

extern BAP_DLL void bap_reset_geobucket_mpzm (
    struct bap_geobucket_mpzm *);

extern BAP_DLL void bap_mul_geobucket_mpzm (
    struct bap_geobucket_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_mul_geobucket_numeric_mpzm (
    struct bap_geobucket_mpzm *,
    ba0_mpzm_t);

extern BAP_DLL void bap_add_geobucket_mpzm (
    struct bap_geobucket_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_sub_geobucket_mpzm (
    struct bap_geobucket_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_set_polynom_geobucket_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_geobucket_mpzm *);

#   undef BAD_FLAG_mpzm

END_C_DECLS
#endif /* !BAP_GEOBUCKET_mpzm_H */
