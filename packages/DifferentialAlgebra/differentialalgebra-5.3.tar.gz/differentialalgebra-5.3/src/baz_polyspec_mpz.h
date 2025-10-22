#if ! defined (BAZ_POLYSPEC_MPZ_H)
#   define BAZ_POLYSPEC_MPZ_H 1

#   include "baz_common.h"

BEGIN_C_DECLS

extern BAZ_DLL void baz_genpoly_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    ba0_mpz_t,
    struct bav_variable *);

extern BAZ_DLL void baz_yet_another_point_int_p_mpz (
    struct bav_point_int_p *,
    struct bap_tableof_polynom_mpz *,
    struct bap_product_mpz *,
    struct bav_variable *);

struct baz_ideal_lifting
{
  struct bap_polynom_mpz *A;
  struct bap_polynom_mpz *initial;
  struct bap_product_mpz factors_initial;
  struct bap_product_mpzm factors_mod_point;
  struct bav_point_int_p point;
  ba0_mpz_t p;
  ba0_int_p l;
};


extern BAZ_DLL void baz_HL_init_ideal_lifting (
    struct baz_ideal_lifting *);

extern BAZ_DLL void baz_HL_printf_ideal_lifting (
    void *);

extern BAZ_DLL void baz_HL_integer_divisors (
    ba0_mpz_t *,
    struct baz_ideal_lifting *,
    ba0_mpz_t *);

extern BAZ_DLL void baz_HL_end_redistribute (
    struct baz_ideal_lifting *,
    ba0_mpz_t *,
    struct bap_polynom_mpz *,
    ba0_mpz_t);

extern BAZ_DLL void baz_HL_begin_redistribute (
    struct baz_ideal_lifting *,
    ba0_mpz_t *,
    struct bap_polynom_mpz *,
    ba0_mpz_t);

extern BAZ_DLL void baz_HL_redistribute_the_factors_of_the_initial (
    struct baz_ideal_lifting *);

extern BAZ_DLL void baz_HL_ideal_Hensel_lifting (
    struct bap_product_mpz *,
    struct baz_ideal_lifting *);

extern BAZ_DLL void baz_monomial_reduce_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    ba0_mpz_t,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAZ_DLL void baz_gcd_pseudo_division_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_product_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAZ_DLL void baz_gcd_prem_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_product_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAZ_DLL void baz_gcd_pquo_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_product_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

END_C_DECLS
#endif /* !BAZ_POLYSPEC_MPZ_H */
