#if !defined (BAP_PRODUCT_mpzm_H)
#   define BAP_PRODUCT_mpzm_H 1

#   include "bap_common.h"
#   include "bap_polynom_mpzm.h"

#   define BAD_FLAG_mpzm

BEGIN_C_DECLS

/*
 * texinfo: bap_power_mpzm
 * This data type implements a polynomial raised to some power.
 */

struct bap_power_mpzm
{
  struct bap_polynom_mpzm factor;
  bav_Idegree exponent;
};


/*
 * texinfo: bap_product_mpzm
 * This data type implements products of polynomials of the form
 * @math{c \, f_1^{a_1} \cdots f_t^{a_t}}
 * where @var{c} is the @dfn{numerical factor} of the product, 
 * the @math{f_i} are non numerical polynomials, not necessarily 
 * irreducible and not even necessarily pairwise distinct. 
 * The exponents @math{a_i} are allowed to be zero. 
 * The product one is coded by @math{c = 1} and @math{t = 0}. 
 * The product zero is coded by @math{c = 0}.  
 * Observe that in the context of rings which are not domains, 
 * zero and one are not necessarily automatically recognized.
 */

struct bap_product_mpzm
{
// the numerical factor
  ba0_mpzm_t num_factor;
// the number of allocated entries of tab
  ba0_int_p alloc;
// the number of used entries
  ba0_int_p size;
// the array of bap_power_mpzm
  struct bap_power_mpzm *tab;
};

struct bap_tableof_product_mpzm
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bap_product_mpzm **tab;
};

extern BAP_DLL void bap_init_power_mpzm (
    struct bap_power_mpzm *);

extern BAP_DLL struct bap_power_mpzm *bap_new_power_mpzm (
    void);

extern BAP_DLL void bap_set_power_mpzm (
    struct bap_power_mpzm *,
    struct bap_power_mpzm *);

extern BAP_DLL void bap_set_power_polynom_mpzm (
    struct bap_power_mpzm *,
    struct bap_polynom_mpzm *,
    bav_Idegree);

extern BAP_DLL void bap_pow_power_mpzm (
    struct bap_power_mpzm *,
    struct bap_power_mpzm *,
    bav_Idegree);

extern BAP_DLL void bap_init_product_mpzm (
    struct bap_product_mpzm *);

extern BAP_DLL void bap_init_product_zero_mpzm (
    struct bap_product_mpzm *);

extern BAP_DLL void bap_realloc_product_mpzm (
    struct bap_product_mpzm *,
    ba0_int_p);

extern BAP_DLL struct bap_product_mpzm *bap_new_product_mpzm (
    void);

extern BAP_DLL struct bap_product_mpzm *bap_new_product_zero_mpzm (
    void);

extern BAP_DLL bool bap_is_zero_product_mpzm (
    struct bap_product_mpzm *);

extern BAP_DLL bool bap_is_one_product_mpzm (
    struct bap_product_mpzm *);

extern BAP_DLL bool bap_is_numeric_product_mpzm (
    struct bap_product_mpzm *);

extern BAP_DLL struct bav_variable * bap_leader_product_mpzm (
    struct bap_product_mpzm *);

extern BAP_DLL void bap_set_product_zero_mpzm (
    struct bap_product_mpzm *);

extern BAP_DLL void bap_set_product_one_mpzm (
    struct bap_product_mpzm *);

extern BAP_DLL void bap_set_product_numeric_mpzm (
    struct bap_product_mpzm *,
    ba0_mpzm_t);

extern BAP_DLL void bap_set_product_polynom_mpzm (
    struct bap_product_mpzm *,
    struct bap_polynom_mpzm *,
    bav_Idegree);

extern BAP_DLL void bap_set_product_mpzm (
    struct bap_product_mpzm *,
    struct bap_product_mpzm *);

extern BAP_DLL void bap_expand_product_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_product_mpzm *);

extern BAP_DLL void bap_mul_product_polynom_mpzm (
    struct bap_product_mpzm *,
    struct bap_product_mpzm *,
    struct bap_polynom_mpzm *,
    bav_Idegree);

extern BAP_DLL void bap_neg_product_mpzm (
    struct bap_product_mpzm *,
    struct bap_product_mpzm *);

extern BAP_DLL void bap_mul_product_numeric_mpzm (
    struct bap_product_mpzm *,
    struct bap_product_mpzm *,
    ba0_mpzm_t);

extern BAP_DLL void bap_mul_product_term_mpzm (
    struct bap_product_mpzm *,
    struct bap_product_mpzm *,
    struct bav_term *);

extern BAP_DLL void bap_mul_product_mpzm (
    struct bap_product_mpzm *,
    struct bap_product_mpzm *,
    struct bap_product_mpzm *);

extern BAP_DLL void bap_pow_product_mpzm (
    struct bap_product_mpzm *,
    struct bap_product_mpzm *,
    bav_Idegree);

extern BAP_DLL void bap_exquo_product_polynom_mpzm (
    struct bap_product_mpzm *,
    struct bap_product_mpzm *,
    struct bap_polynom_mpzm *,
    bav_Idegree);

extern BAP_DLL bav_Idegree bap_exponent_product_mpzm (
    struct bap_product_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_sort_product_mpzm (
    struct bap_product_mpzm *,
    struct bap_product_mpzm *);

extern BAP_DLL void bap_physort_product_mpzm (
    struct bap_product_mpzm *);

extern BAP_DLL ba0_scanf_function bap_scanf_product_mpzm;

extern BAP_DLL ba0_printf_function bap_printf_product_mpzm;

extern BAP_DLL ba0_garbage1_function bap_garbage1_product_mpzm;

extern BAP_DLL ba0_garbage2_function bap_garbage2_product_mpzm;

extern BAP_DLL ba0_copy_function bap_copy_product_mpzm;

END_C_DECLS
#   undef BAD_FLAG_mpzm
#endif /* !BAP_PRODUCT_mpzm_H */
