#if ! defined (BAZ_GCD_POLYNOM_MPZ_H)
#   define BAZ_GCD_POLYNOM_MPZ_H 1

#   include "baz_common.h"

BEGIN_C_DECLS

struct baz_factored_polynom_mpz
{
  struct bap_product_mpz outer;
  struct bap_polynom_mpz poly;
};

struct baz_tableof_factored_polynom_mpz
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct baz_factored_polynom_mpz **tab;
};

struct baz_gcd_data
{
  bool proved_relatively_prime;
  struct bap_product_mpz common;
  struct baz_tableof_factored_polynom_mpz F;
};

extern BAZ_DLL ba0_printf_function baz_printf_gcd_data;

extern BAZ_DLL void baz_gcd_univariate_tableof_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_tableof_polynom_mpz *);

extern BAZ_DLL void baz_gcdheu_tableof_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_tableof_polynom_mpz *,
    ba0_int_p);

extern BAZ_DLL void baz_extended_Zassenhaus_gcd_tableof_polynom_mpz (
    struct bap_product_mpz *,
    struct bap_tableof_polynom_mpz *,
    bool);

extern BAZ_DLL void baz_gcd_tableof_polynom_mpz (
    struct bap_product_mpz *,
    struct bap_tableof_polynom_mpz *,
    bool);

extern BAZ_DLL void baz_gcd_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAZ_DLL void baz_content_tableof_polynom_mpz (
    struct bap_product_mpz *,
    struct bap_tableof_polynom_mpz *,
    struct bav_variable *,
    bool);

extern BAZ_DLL void baz_content_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAZ_DLL void baz_primpart_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAZ_DLL void baz_Yun_polynom_mpz (
    struct bap_product_mpz *,
    struct bap_polynom_mpz *,
    bool);

extern BAZ_DLL void baz_squarefree_polynom_mpz (
    struct bap_product_mpz *,
    struct bap_polynom_mpz *);

extern BAZ_DLL void baz_factor_easy_polynom_mpz (
    struct bap_product_mpz *,
    struct ba0_tableof_bool *,
    struct bap_polynom_mpz *,
    struct bap_listof_polynom_mpz *);

extern BAZ_DLL void baz_factor_easy_product_mpz (
    struct bap_product_mpz *,
    struct ba0_tableof_bool *,
    struct bap_product_mpz *,
    struct bap_listof_polynom_mpz *);

END_C_DECLS
#endif /* ! BAZ_GCD_POLYNOM_MPZ_H */
