#if ! defined (BAZ_REALROOT_MPQ_H)
#   define BAZ_REALROOT_MPQ_H

#   include "baz_common.h"

BEGIN_C_DECLS

/*
 * texinfo: baz_typeof_realroot_interval
 * This data type permits to control the behaviour of algorithms
 * for isolating real roots of univariate polynomials.
 */

enum baz_typeof_realroot_interval
{
// Output intervals whenever they have width < epsilon
  baz_any_interval,
// Output intervals if they are guaranteed to isolate exactly one root
  baz_isolation_interval
};

extern BAZ_DLL void baz_positive_roots_polynom_mpq (
    struct ba0_tableof_interval_mpq *,
    struct bap_polynom_mpq *,
    enum baz_typeof_realroot_interval,
    ba0_mpq_t);

extern BAZ_DLL void baz_positive_integer_roots_polynom_mpq (
    struct ba0_tableof_mpz *,
    struct bap_polynom_mpq *);

extern BAZ_DLL void baz_positive_integer_roots_polynom_mpz (
    struct ba0_tableof_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

END_C_DECLS
#endif /* !BAZ_REALROOT_MPQ_H */
