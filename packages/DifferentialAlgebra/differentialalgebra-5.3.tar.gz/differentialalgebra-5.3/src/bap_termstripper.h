#if !defined (BAP_TERMSTRIPPER_H)
#   define BAP_TERMSTRIPPER_H 1

#   include "bap_common.h"

#   define BAP_TERMSTRIPPER_SIZE 3

BEGIN_C_DECLS

/* 
 * texinfo: bap_termstripper
 * This data type is involved in the process of taking coefficients of 
 * polynomials w.r.t. any variable. 
 *
 * It aims at stripping terms i.e. at cutting, in terms, all ranks 
 * which depend on variables strictly greater than a given variable.
 * The ordering w.r.t. which variables are compared is often not
 * the ordering of the clot. A stripping operation is thus described
 * by a pair (@code{variable}, @code{ordering}).
 *
 * The variable is allowed to be @code{BAV_NOT_A_VARIABLE} (i.e. @math{0}).
 * In that case, all variables are cut.
 * It is allowed to be @math{-1}. In that case, no variables are cut.
 *
 * It happens that a polynomial is obtained by performing a sequence
 * of stripping operations. This sequence, which is necessary to
 * recover the right stripped terms, is recorded.
 */

struct bap_termstripper
{
// the number of stripping operations recorded in tab
  ba0_int_p size;
  struct _tab
  {
    bav_Iordering ordering;
    struct bav_variable *varmax;
  } tab[BAP_TERMSTRIPPER_SIZE];
};


extern BAP_DLL void bap_init_set_termstripper (
    struct bap_termstripper *,
    struct bav_variable *,
    bav_Iordering);

extern BAP_DLL void bap_set_termstripper (
    struct bap_termstripper *,
    struct bap_termstripper *);

extern BAP_DLL void bap_change_ordering_termstripper (
    struct bap_termstripper *,
    bav_Iordering);

extern BAP_DLL void bap_change_variable_termstripper (
    struct bap_termstripper *,
    struct bav_variable *);

extern BAP_DLL void bap_append_termstripper (
    struct bap_termstripper *,
    struct bav_variable *,
    bav_Iordering);

extern BAP_DLL bool bap_identity_termstripper (
    struct bap_termstripper *,
    bav_Iordering);

extern BAP_DLL void bap_strip_term_termstripper (
    struct bav_term *,
    bav_Iordering,
    struct bap_termstripper *);

extern BAP_DLL void bap_switch_ring_termstripper (
    struct bap_termstripper *,
    struct bav_differential_ring *);

END_C_DECLS
#endif /* !BAP_TERMSTRIPPER_H */
