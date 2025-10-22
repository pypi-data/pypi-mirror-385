#if !defined (BAP_PRODUCT_mint_hp_H)
#   define BAP_PRODUCT_mint_hp_H 1

#   include "bap_common.h"
#   include "bap_polynom_mint_hp.h"

#   define BAD_FLAG_mint_hp

BEGIN_C_DECLS

/*
 * texinfo: bap_power_mint_hp
 * This data type implements a polynomial raised to some power.
 */

struct bap_power_mint_hp
{
  struct bap_polynom_mint_hp factor;
  bav_Idegree exponent;
};


/*
 * texinfo: bap_product_mint_hp
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

struct bap_product_mint_hp
{
// the numerical factor
  ba0_mint_hp_t num_factor;
// the number of allocated entries of tab
  ba0_int_p alloc;
// the number of used entries
  ba0_int_p size;
// the array of bap_power_mint_hp
  struct bap_power_mint_hp *tab;
};

struct bap_tableof_product_mint_hp
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bap_product_mint_hp **tab;
};

extern BAP_DLL void bap_init_power_mint_hp (
    struct bap_power_mint_hp *);

extern BAP_DLL struct bap_power_mint_hp *bap_new_power_mint_hp (
    void);

extern BAP_DLL void bap_set_power_mint_hp (
    struct bap_power_mint_hp *,
    struct bap_power_mint_hp *);

extern BAP_DLL void bap_set_power_polynom_mint_hp (
    struct bap_power_mint_hp *,
    struct bap_polynom_mint_hp *,
    bav_Idegree);

extern BAP_DLL void bap_pow_power_mint_hp (
    struct bap_power_mint_hp *,
    struct bap_power_mint_hp *,
    bav_Idegree);

extern BAP_DLL void bap_init_product_mint_hp (
    struct bap_product_mint_hp *);

extern BAP_DLL void bap_init_product_zero_mint_hp (
    struct bap_product_mint_hp *);

extern BAP_DLL void bap_realloc_product_mint_hp (
    struct bap_product_mint_hp *,
    ba0_int_p);

extern BAP_DLL struct bap_product_mint_hp *bap_new_product_mint_hp (
    void);

extern BAP_DLL struct bap_product_mint_hp *bap_new_product_zero_mint_hp (
    void);

extern BAP_DLL bool bap_is_zero_product_mint_hp (
    struct bap_product_mint_hp *);

extern BAP_DLL bool bap_is_one_product_mint_hp (
    struct bap_product_mint_hp *);

extern BAP_DLL bool bap_is_numeric_product_mint_hp (
    struct bap_product_mint_hp *);

extern BAP_DLL struct bav_variable * bap_leader_product_mint_hp (
    struct bap_product_mint_hp *);

extern BAP_DLL void bap_set_product_zero_mint_hp (
    struct bap_product_mint_hp *);

extern BAP_DLL void bap_set_product_one_mint_hp (
    struct bap_product_mint_hp *);

extern BAP_DLL void bap_set_product_numeric_mint_hp (
    struct bap_product_mint_hp *,
    ba0_mint_hp_t);

extern BAP_DLL void bap_set_product_polynom_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_polynom_mint_hp *,
    bav_Idegree);

extern BAP_DLL void bap_set_product_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_product_mint_hp *);

extern BAP_DLL void bap_expand_product_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_product_mint_hp *);

extern BAP_DLL void bap_mul_product_polynom_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_product_mint_hp *,
    struct bap_polynom_mint_hp *,
    bav_Idegree);

extern BAP_DLL void bap_neg_product_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_product_mint_hp *);

extern BAP_DLL void bap_mul_product_numeric_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_product_mint_hp *,
    ba0_mint_hp_t);

extern BAP_DLL void bap_mul_product_term_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_product_mint_hp *,
    struct bav_term *);

extern BAP_DLL void bap_mul_product_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_product_mint_hp *,
    struct bap_product_mint_hp *);

extern BAP_DLL void bap_pow_product_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_product_mint_hp *,
    bav_Idegree);

extern BAP_DLL void bap_exquo_product_polynom_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_product_mint_hp *,
    struct bap_polynom_mint_hp *,
    bav_Idegree);

extern BAP_DLL bav_Idegree bap_exponent_product_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_sort_product_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_product_mint_hp *);

extern BAP_DLL void bap_physort_product_mint_hp (
    struct bap_product_mint_hp *);

extern BAP_DLL ba0_scanf_function bap_scanf_product_mint_hp;

extern BAP_DLL ba0_printf_function bap_printf_product_mint_hp;

extern BAP_DLL ba0_garbage1_function bap_garbage1_product_mint_hp;

extern BAP_DLL ba0_garbage2_function bap_garbage2_product_mint_hp;

extern BAP_DLL ba0_copy_function bap_copy_product_mint_hp;

END_C_DECLS
#   undef BAD_FLAG_mint_hp
#endif /* !BAP_PRODUCT_mint_hp_H */
