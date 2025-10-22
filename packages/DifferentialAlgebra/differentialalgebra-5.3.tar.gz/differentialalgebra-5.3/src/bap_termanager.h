#if !defined (BAP_TERMANAGER_H)
#   define BAP_TERMANAGER_H 1

#   include "bap_common.h"

BEGIN_C_DECLS

/*
 * texinfo: bap_zipterm
 * If the term fits in a single @code{ba0_int_p} when compressed
 * then the corresponding @code{bap_zipterm} is the compressed form
 * of the term. If it does not, the corresponding @code{bap_zipterm}
 * is a pointer towards a sufficiently large array of @code{ba0_int_p}.
 */

typedef ba0_int_p bap_zipterm;

/*
 * texinfo: bap_termanager
 * This data type is designed to store the terms of a polynomial
 * (more precisely, of a clot in compressed form.
 */

struct bap_termanager
{
// the total rank of all terms of the clot
  struct bav_term total_rank;
  struct _zipping
  {
// number of ba0_int_p allocated to each zipterm
    ba0_int_p alloc;
// number of ba0_int_p used by each zipterm
    ba0_int_p size;
// the number of allocated entries of nbbits and mask
//      is equal to total_rank.alloc
// nbbits[i] = the number of bits needed to store the degree of 
//      the ith variable in total_rank in any zipterm
// mask[i]   = the binary mask needed to extract this degree
    unsigned char *nbbits;
    unsigned ba0_int_p *mask;
  } zipping;
};


extern BAP_DLL void bap_init_termanager (
    struct bap_termanager *,
    struct bav_term *);

extern BAP_DLL void bap_reset_termanager (
    struct bap_termanager *,
    struct bav_term *,
    bool *);

extern BAP_DLL bool bap_equal_termanager (
    struct bap_termanager *,
    struct bap_termanager *);

extern BAP_DLL void bap_init_set_termanager (
    struct bap_termanager *,
    struct bap_termanager *);

extern BAP_DLL void bap_init_zipterm_array_termanager (
    struct bap_termanager *,
    bap_zipterm *,
    ba0_int_p);

extern BAP_DLL void bap_set_zipterm_zipterm_termanager (
    struct bap_termanager *,
    bap_zipterm *,
    struct bap_termanager *,
    bap_zipterm);

extern BAP_DLL void bap_set_zipterm_term_termanager (
    struct bap_termanager *,
    bap_zipterm *,
    struct bav_term *);

extern BAP_DLL void bap_set_term_zipterm_termanager (
    struct bap_termanager *,
    struct bav_term *,
    bap_zipterm);

extern BAP_DLL ba0_garbage1_function bap_garbage1_termanager;

extern BAP_DLL ba0_garbage2_function bap_garbage2_termanager;

/* 
 * Should be garbage1 and garbage2 functions.
 */

extern BAP_DLL bool bap_worth_garbage_zipterm_termanager (
    struct bap_termanager *);

extern BAP_DLL ba0_int_p bap_garbage1_zipterm_termanager (
    struct bap_termanager *,
    bap_zipterm,
    enum ba0_garbage_code);

extern BAP_DLL bap_zipterm bap_garbage2_zipterm_termanager (
    struct bap_termanager *,
    bap_zipterm,
    enum ba0_garbage_code);

extern BAP_DLL void bap_switch_ring_termanager (
    struct bap_termanager *,
    struct bav_differential_ring *);

END_C_DECLS
#endif /* !BAP_TERMANAGER_H */
