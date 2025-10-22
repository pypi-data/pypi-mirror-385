#if !defined (BAP_PRODUCT_mpz_H)
#   define BAP_PRODUCT_mpz_H 1

#   include "bap_common.h"
#   include "bap_polynom_mpz.h"

#   define BAD_FLAG_mpz

BEGIN_C_DECLS

/*
 * texinfo: bap_power_mpz
 * This data type implements a polynomial raised to some power.
 */

struct bap_power_mpz
{
  struct bap_polynom_mpz factor;
  bav_Idegree exponent;
};


/*
 * texinfo: bap_product_mpz
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

struct bap_product_mpz
{
// the numerical factor
  ba0_mpz_t num_factor;
// the number of allocated entries of tab
  ba0_int_p alloc;
// the number of used entries
  ba0_int_p size;
// the array of bap_power_mpz
  struct bap_power_mpz *tab;
};

struct bap_tableof_product_mpz
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bap_product_mpz **tab;
};

extern BAP_DLL void bap_init_power_mpz (
    struct bap_power_mpz *);

extern BAP_DLL struct bap_power_mpz *bap_new_power_mpz (
    void);

extern BAP_DLL void bap_set_power_mpz (
    struct bap_power_mpz *,
    struct bap_power_mpz *);

extern BAP_DLL void bap_set_power_polynom_mpz (
    struct bap_power_mpz *,
    struct bap_polynom_mpz *,
    bav_Idegree);

extern BAP_DLL void bap_pow_power_mpz (
    struct bap_power_mpz *,
    struct bap_power_mpz *,
    bav_Idegree);

extern BAP_DLL void bap_init_product_mpz (
    struct bap_product_mpz *);

extern BAP_DLL void bap_init_product_zero_mpz (
    struct bap_product_mpz *);

extern BAP_DLL void bap_realloc_product_mpz (
    struct bap_product_mpz *,
    ba0_int_p);

extern BAP_DLL struct bap_product_mpz *bap_new_product_mpz (
    void);

extern BAP_DLL struct bap_product_mpz *bap_new_product_zero_mpz (
    void);

extern BAP_DLL bool bap_is_zero_product_mpz (
    struct bap_product_mpz *);

extern BAP_DLL bool bap_is_one_product_mpz (
    struct bap_product_mpz *);

extern BAP_DLL bool bap_is_numeric_product_mpz (
    struct bap_product_mpz *);

extern BAP_DLL struct bav_variable * bap_leader_product_mpz (
    struct bap_product_mpz *);

extern BAP_DLL void bap_set_product_zero_mpz (
    struct bap_product_mpz *);

extern BAP_DLL void bap_set_product_one_mpz (
    struct bap_product_mpz *);

extern BAP_DLL void bap_set_product_numeric_mpz (
    struct bap_product_mpz *,
    ba0_mpz_t);

extern BAP_DLL void bap_set_product_polynom_mpz (
    struct bap_product_mpz *,
    struct bap_polynom_mpz *,
    bav_Idegree);

extern BAP_DLL void bap_set_product_mpz (
    struct bap_product_mpz *,
    struct bap_product_mpz *);

extern BAP_DLL void bap_expand_product_mpz (
    struct bap_polynom_mpz *,
    struct bap_product_mpz *);

extern BAP_DLL void bap_mul_product_polynom_mpz (
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bap_polynom_mpz *,
    bav_Idegree);

extern BAP_DLL void bap_neg_product_mpz (
    struct bap_product_mpz *,
    struct bap_product_mpz *);

extern BAP_DLL void bap_mul_product_numeric_mpz (
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    ba0_mpz_t);

extern BAP_DLL void bap_mul_product_term_mpz (
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bav_term *);

extern BAP_DLL void bap_mul_product_mpz (
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bap_product_mpz *);

extern BAP_DLL void bap_pow_product_mpz (
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    bav_Idegree);

extern BAP_DLL void bap_exquo_product_polynom_mpz (
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bap_polynom_mpz *,
    bav_Idegree);

extern BAP_DLL bav_Idegree bap_exponent_product_mpz (
    struct bap_product_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_sort_product_mpz (
    struct bap_product_mpz *,
    struct bap_product_mpz *);

extern BAP_DLL void bap_physort_product_mpz (
    struct bap_product_mpz *);

extern BAP_DLL ba0_scanf_function bap_scanf_product_mpz;

extern BAP_DLL ba0_printf_function bap_printf_product_mpz;

extern BAP_DLL ba0_garbage1_function bap_garbage1_product_mpz;

extern BAP_DLL ba0_garbage2_function bap_garbage2_product_mpz;

extern BAP_DLL ba0_copy_function bap_copy_product_mpz;

END_C_DECLS
#   undef BAD_FLAG_mpz
#endif /* !BAP_PRODUCT_mpz_H */
