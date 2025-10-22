#if !defined (BAP_SEQUENTIAL_ACCESS_H)
#   define BAP_SEQUENTIAL_ACCESS_H 1

#   include "bap_common.h"

BEGIN_C_DECLS

/*
 * texinfo: bap_sequential_access
 * This data type permits to define a subsequence of monomials in a clot. 
 */

struct bap_sequential_access
{
// the index of the first monomial of the subsequence
  ba0_int_p first;
// the index of the first monomial following the subsequence
  ba0_int_p after;
};


END_C_DECLS
#endif /* !BAP_SEQUENTIAL_ACCESS_H */
