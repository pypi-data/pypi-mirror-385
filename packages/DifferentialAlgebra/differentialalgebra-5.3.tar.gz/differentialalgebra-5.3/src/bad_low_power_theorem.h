#if !defined (BAD_LOW_POWER_THEOREM_H)
#   define BAD_LOW_POWER_THEOREM_H 1

#   include "bad_common.h"
#   include "bad_regchain.h"
#   include "bad_intersectof_regchain.h"
#   include "bad_base_field.h"

BEGIN_C_DECLS
#   define BAD_ZSTRING	"z%d"
extern BAD_DLL void bad_set_settings_preparation (
    char *);

extern BAD_DLL void bad_get_settings_preparation (
    char **);

/* 
 * texinfo: bad_preparation_term
 * This data type implements one term in a preparation equation.
 * Denote @math{A = A_1, \ldots, A_r} a differential regular chain.
 * Introduce @math{r} differential indeterminates @math{z_1, \ldots, z_r}.
 * A @code{bad_preparation_term} represents a sequence of terms on the 
 * derivatives of the @math{z_i}. All fields have the same size.
 */

struct bad_preparation_term
{
// z[i] = an index in the range [0, ..., r-1]
  struct ba0_tableof_int_p z;
// theta[i] = a power product of derivations = a derivation operator
  struct bav_tableof_term theta;
// deg[i] = a degree
  struct bav_tableof_Idegree deg;
};


struct bad_tableof_preparation_term
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bad_preparation_term **tab;
};


/* 
 * texinfo: bad_preparation_equation
 * This data type implements preparation equations (Kolchin, IV, 13).
 * Given @math{F} and @math{A = A_1, \ldots, A_r} a preparation
 * equation mostly represents @math{H\,F} as the sum of the
 * pairwise products of the coefficients by the terms modulo @math{(z_i = A_i)}.
 */

struct bad_preparation_equation
{
// power product of initials and separants
  struct bap_product_mpz H;
// the coefficients (reduced and regular w.r.t. A)
  struct bap_tableof_polynom_mpz coeffs;
// the terms
  struct bad_tableof_preparation_term terms;
// the polynomial for which the preparation equation is defined
  struct bap_polynom_mpz *F;
// the denominator of a rational number (to handle
// polynomials with rational number coefficients)
  ba0__mpz_struct *denom;
// the regular chain A
  struct bad_regchain *A;
// the base field - its elements are on the bottom of A
  struct bad_base_field *K;
};


extern BAD_DLL void bad_init_preparation_equation (
    struct bad_preparation_equation *);

extern BAD_DLL struct bad_preparation_equation *bad_new_preparation_equation (
    void);

extern BAD_DLL void bad_set_preparation_equation_polynom (
    struct bad_preparation_equation *,
    struct bap_polynom_mpz *,
    ba0_mpz_t,
    struct bad_regchain *,
    struct bad_base_field *,
    struct bap_polynom_mpz **);

extern BAD_DLL void bad_check_preparation_equation (
    struct bad_preparation_equation *);

extern BAD_DLL ba0_printf_function bad_printf_preparation_equation;

extern BAD_DLL void bad_preparation_congruence (
    ba0_int_p *,
    bav_Idegree *,
    struct bad_preparation_equation *);

extern BAD_DLL bool bad_low_power_theorem_condition_to_be_a_component (
    struct bad_preparation_equation *E);

extern BAD_DLL void bad_low_power_theorem_simplify_intersectof_regchain (
    struct bad_intersectof_regchain *,
    struct bad_intersectof_regchain *,
    struct bad_base_field *);

END_C_DECLS
#endif /* !BAD_LOW_POWER_THEOREM_H */
