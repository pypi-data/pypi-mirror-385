#if !defined (BAP_GEOBUCKET_mpq_H)
#   define BAP_GEOBUCKET_mpq_H 1

#   include "bap_common.h"
#   include "bap_polynom_mpq.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mpq

/*
 * texinfo: bap_geobucket_mpq
 * A geobucket (JSC (1998) 25, 285-293, Thomas Yan) is a table of polynomials
 * representing the sum of these polynomials. This data structure
 * permits to improve the complexity of the sum of many different
 * polynomials.
 * The polynomial at index @var{i} is a sum of at most @var{2^i} 
 * monomials.
 * The data structure is a duplicate of @code{bap_tableof_polynomial}.
 */

struct bap_geobucket_mpq
{
// number of allocated entries
  ba0_int_p alloc;
// number of used entries
  ba0_int_p size;
// the array
  struct bap_polynom_mpq **tab;
};



extern BAP_DLL void bap_init_geobucket_mpq (
    struct bap_geobucket_mpq *);

extern BAP_DLL void bap_reset_geobucket_mpq (
    struct bap_geobucket_mpq *);

extern BAP_DLL void bap_mul_geobucket_mpq (
    struct bap_geobucket_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_mul_geobucket_numeric_mpq (
    struct bap_geobucket_mpq *,
    ba0_mpq_t);

extern BAP_DLL void bap_add_geobucket_mpq (
    struct bap_geobucket_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_sub_geobucket_mpq (
    struct bap_geobucket_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_set_polynom_geobucket_mpq (
    struct bap_polynom_mpq *,
    struct bap_geobucket_mpq *);

#   undef BAD_FLAG_mpq

END_C_DECLS
#endif /* !BAP_GEOBUCKET_mpq_H */
