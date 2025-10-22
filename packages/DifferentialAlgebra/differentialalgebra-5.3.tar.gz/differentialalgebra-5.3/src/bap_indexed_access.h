#if !defined (BAP_INDEXED_ACCESS_H)
#   define BAP_INDEXED_ACCESS_H 1

#   include "bap_common.h"

BEGIN_C_DECLS

/*
 * texinfo: bap_indexed_access
 * This data type permits to define a sequence of non consecutive 
 * monomials in a clot or in a polynomial, in any order. 
 * It is a table of tables of monomial numbers.
 * From a logical point of view, it is a sequence of monomial numbers.
 */

struct bap_indexed_access
{
// the total number of entries allocated to tab
  ba0_int_p alloc;
// the total number of entries used in tab
  ba0_int_p size;
  struct ba0_tableof_tableof_int_p tab;
};


extern BAP_DLL void bap_init_indexed_access (
    struct bap_indexed_access *);

extern BAP_DLL void bap_realloc_indexed_access (
    struct bap_indexed_access *,
    ba0_int_p);

extern BAP_DLL void bap_reverse_indexed_access (
    struct bap_indexed_access *);

extern BAP_DLL ba0_garbage1_function bap_garbage1_indexed_access;

extern BAP_DLL ba0_garbage2_function bap_garbage2_indexed_access;

END_C_DECLS
#endif /* !BAP_INDEXED_ACCESS_H */
