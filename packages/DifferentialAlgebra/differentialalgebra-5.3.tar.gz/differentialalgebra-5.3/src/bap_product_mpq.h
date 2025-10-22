#if !defined (BAP_PRODUCT_mpq_H)
#   define BAP_PRODUCT_mpq_H 1

#   include "bap_common.h"
#   include "bap_polynom_mpq.h"

#   define BAD_FLAG_mpq

BEGIN_C_DECLS

/*
 * texinfo: bap_power_mpq
 * This data type implements a polynomial raised to some power.
 */

struct bap_power_mpq
{
  struct bap_polynom_mpq factor;
  bav_Idegree exponent;
};


/*
 * texinfo: bap_product_mpq
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

struct bap_product_mpq
{
// the numerical factor
  ba0_mpq_t num_factor;
// the number of allocated entries of tab
  ba0_int_p alloc;
// the number of used entries
  ba0_int_p size;
// the array of bap_power_mpq
  struct bap_power_mpq *tab;
};

struct bap_tableof_product_mpq
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bap_product_mpq **tab;
};

extern BAP_DLL void bap_init_power_mpq (
    struct bap_power_mpq *);

extern BAP_DLL struct bap_power_mpq *bap_new_power_mpq (
    void);

extern BAP_DLL void bap_set_power_mpq (
    struct bap_power_mpq *,
    struct bap_power_mpq *);

extern BAP_DLL void bap_set_power_polynom_mpq (
    struct bap_power_mpq *,
    struct bap_polynom_mpq *,
    bav_Idegree);

extern BAP_DLL void bap_pow_power_mpq (
    struct bap_power_mpq *,
    struct bap_power_mpq *,
    bav_Idegree);

extern BAP_DLL void bap_init_product_mpq (
    struct bap_product_mpq *);

extern BAP_DLL void bap_init_product_zero_mpq (
    struct bap_product_mpq *);

extern BAP_DLL void bap_realloc_product_mpq (
    struct bap_product_mpq *,
    ba0_int_p);

extern BAP_DLL struct bap_product_mpq *bap_new_product_mpq (
    void);

extern BAP_DLL struct bap_product_mpq *bap_new_product_zero_mpq (
    void);

extern BAP_DLL bool bap_is_zero_product_mpq (
    struct bap_product_mpq *);

extern BAP_DLL bool bap_is_one_product_mpq (
    struct bap_product_mpq *);

extern BAP_DLL bool bap_is_numeric_product_mpq (
    struct bap_product_mpq *);

extern BAP_DLL struct bav_variable * bap_leader_product_mpq (
    struct bap_product_mpq *);

extern BAP_DLL void bap_set_product_zero_mpq (
    struct bap_product_mpq *);

extern BAP_DLL void bap_set_product_one_mpq (
    struct bap_product_mpq *);

extern BAP_DLL void bap_set_product_numeric_mpq (
    struct bap_product_mpq *,
    ba0_mpq_t);

extern BAP_DLL void bap_set_product_polynom_mpq (
    struct bap_product_mpq *,
    struct bap_polynom_mpq *,
    bav_Idegree);

extern BAP_DLL void bap_set_product_mpq (
    struct bap_product_mpq *,
    struct bap_product_mpq *);

extern BAP_DLL void bap_expand_product_mpq (
    struct bap_polynom_mpq *,
    struct bap_product_mpq *);

extern BAP_DLL void bap_mul_product_polynom_mpq (
    struct bap_product_mpq *,
    struct bap_product_mpq *,
    struct bap_polynom_mpq *,
    bav_Idegree);

extern BAP_DLL void bap_neg_product_mpq (
    struct bap_product_mpq *,
    struct bap_product_mpq *);

extern BAP_DLL void bap_mul_product_numeric_mpq (
    struct bap_product_mpq *,
    struct bap_product_mpq *,
    ba0_mpq_t);

extern BAP_DLL void bap_mul_product_term_mpq (
    struct bap_product_mpq *,
    struct bap_product_mpq *,
    struct bav_term *);

extern BAP_DLL void bap_mul_product_mpq (
    struct bap_product_mpq *,
    struct bap_product_mpq *,
    struct bap_product_mpq *);

extern BAP_DLL void bap_pow_product_mpq (
    struct bap_product_mpq *,
    struct bap_product_mpq *,
    bav_Idegree);

extern BAP_DLL void bap_exquo_product_polynom_mpq (
    struct bap_product_mpq *,
    struct bap_product_mpq *,
    struct bap_polynom_mpq *,
    bav_Idegree);

extern BAP_DLL bav_Idegree bap_exponent_product_mpq (
    struct bap_product_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_sort_product_mpq (
    struct bap_product_mpq *,
    struct bap_product_mpq *);

extern BAP_DLL void bap_physort_product_mpq (
    struct bap_product_mpq *);

extern BAP_DLL ba0_scanf_function bap_scanf_product_mpq;

extern BAP_DLL ba0_printf_function bap_printf_product_mpq;

extern BAP_DLL ba0_garbage1_function bap_garbage1_product_mpq;

extern BAP_DLL ba0_garbage2_function bap_garbage2_product_mpq;

extern BAP_DLL ba0_copy_function bap_copy_product_mpq;

END_C_DECLS
#   undef BAD_FLAG_mpq
#endif /* !BAP_PRODUCT_mpq_H */
