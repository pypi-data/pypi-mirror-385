#if ! defined (BAS_ZUPLE_H)
#   define BAS_ZUPLE_H 1

#   include "bas_common.h"
#   include "bas_Yuple.h"

BEGIN_C_DECLS

/*
 * texinfo: bas_Zuple
 * This data structure is a working data structure used by
 * the @code{bas_Denef_Lipshitz_leaf} function.
 * 
 * This data structure is meaningful with respect to some
 * @code{struct bas_Yuple} data structure, denoted @var{U}
 * in the following text. 
 * 
 * The fields which are tables all have the same size:
 * the number of differential indeterminates for which formal
 * power series solutions are sought (see the field @code{Y} of @var{U}).
 * The @math{i}th entry of any table applies to the @math{i}th
 * differential indeterminate. Some of these entries may remain unused:
 * the ones for which the differential indeterminate is not constrained
 * by any differential polynomial, corresponding to an empty entry
 * in the field @code{ode} of @var{U}.
 * 
 * Let @math{y} denote one of the differential indeterminates
 * for which formal power series solutions are sought
 * and @math{y_i} the coefficients of the sought formal power
 * series solution @math{\bar{\bar{y}}}. 
 * These coefficients are implemented as
 * @emph{subscripted variables} @code{y[i]}.
 * The @math{y} defining ODE i.e. the one which has a derivative
 * of @math{y} for leader is denoted @math{F}.
 * Its separant is denoted @math{S}.
 * The coefficients of the series obtained by evaluating @math{F}
 * at @math{\bar{\bar{y}}} are the non-differential polynomials 
 * @math{F^{(j)}(y_i)}. They are called the @emph{prolongation equations}.
 * 
 * To simplify statements, the table fields of the data structure
 * are described as if they applied to the single differential
 * indeterminate @math{y}.
 * 
 * The field @code{sigma} contains the maximum of the subscripts
 * of the variables @code{y[i]} occurring in the fields @code{C},
 * @code{P} and @code{S}.
 * If undefined, @code{sigma} is equal to @math{-1}.
 * 
 * The field @code{mu} contains the prolongation order for @math{F}.
 * Roughly speaking, the field @code{C} contains the polynomials
 * @math{F^{(j)}(y_i)} for @math{0 \leq j \leq \mu}.
 * Strictly speaking, the above statement is incorrect because @code{C} is a
 * regular differential chain obtained by processing these polynomials
 * by a non-differential regular chain decomposition algorithm.
 * Moreover, before being processed, these polynomials lie in @code{P} and
 * not in @code{C}.
 * 
 * The field @code{zeta} contains the last tried value for the
 * valuation @code{k} of the separant of @math{F}.
 * Its value is bounded by the field @code{kappa} of @var{U}.
 * If undefined, @code{zeta} is equal to @math{-1}.
 * 
 * The field @code{C} contains a regular differential chain obtained
 * by extension of an initial regular differential chain with
 * prolongation equations and other polynomials considered while
 * building the polynomial @math{A(q)}.
 * 
 * The field @code{P} contains the equations waiting for being processed.
 * The polynomials in @code{P} are meant to be processed by a 
 * non-differential regular chain decomposition algorithm in order
 * to extend @code{C}. This process may actually split the 
 * current regular differential chain.
 * After the process, the field @code{P} becomes empty.
 * 
 * The field @code{S} contains the non-differential inequations to be taken into
 * account by the non-differential regular chain decomposition algorithm.
 * It contains polynomials which must be guaranteed to be nonzero in
 * order to guarantee the valuations of the separants of the ODE
 * system (the field @code{k}) and the degrees of the polynomials @math{A(q)}
 * (the fields @code{r} and @code{A}).
 * It is never emptied but its elements may get simplified when
 * @code{C} is updated.
 * 
 * The field @code{k} contains the valuation of the separant of @math{F}
 * i.e. of the series @math{S(\bar{\bar{y}})}.
 * If undefined, it is equal to @math{-1} otherwise, the polynomial
 * @math{S^{(k)}(y_i)} is guaranteed to be nonzero: it is either an element
 * of the base field or stored in the field @code{S}.
 * 
 * The field @code{fn} contains the Hurwitz coefficients of @math{F}
 * with respect to the valuation stored in @code{k}.
 * See the @code{bas_Hurwitz_coeffs} function.
 * This field is undefined if @code{k} is undefined else it 
 * contains @math{k+1} differential polynomials denoted
 * (see [DL84, Lemma 2.2])
 * @display
 * @math{[f_n, f_{n+1}, f_{n+2}, ..., f_{n+k}].}
 * @end display
 * 
 * The field @code{der_fn} contains differential polynomials 
 * involved in the definition of the polynomial @math{A(q)}.
 * It is built incrementally.
 * Successive values of this field are
 * @display
 * @math{[f_n], \quad [f_{n+1}, f_n'], \quad [f_{n+2}, f_{n+1}', f_n''], \quad @dots{}}
 * @end display
 * 
 * The field @code{phi} contains the last tried value for @code{r}.
 * Its value is bounded by the valuation @code{k}.
 * It is equal to the index of the last defined entry of @code{der_fn}.
 * If undefined, @code{phi} is equal to @math{-1}.
 * 
 * The field @code{deg} contains the last tried value for the
 * degree of the polynomial @math{A(q)}.
 * Its value is bounded by @code{phi}.
 * If undefined, @code{deg} is equal to @math{-1}.
 * 
 * The field @code{r} contains the first value of @code{phi} for
 * which a nonzero polynomial @math{A(q)} has been determined.
 * Its value is bounded by the valuation @code{k}.
 * The field @code{deg} then contains the degree of @math{A(q)}.
 * The leading coefficient of @math{A(q)} is either a base field
 * element or stored in the list @code{S} of polynomials which must
 * not vanish.
 * If undefined, @code{r} is equal to @math{-1}.
 *
 * The field @code{coeffs} contains the coefficients of the
 * polynomial @math{A(q)}. It is built using @code{der_fn}.
 * If undefined, it is empty else it involves @math{@code{deg} + 1} elements.
 * Indeed we have
 * @display
 * @math{A(q) = \sum_{i=0}^{@code{deg}}} @code{coeffs}_@math{i} @math{{q \choose i}}
 * @end display
 * 
 * The field @code{A} contains the polynomial @math{A(q)}.
 * Its degree in @math{q} is stored in the field @code{deg}.
 * If undefined it contains @math{0}.
 * 
 * The field @code{roots} contains the positive integer roots
 * of @math{A(q)}, stored by increasing values.
 * 
 * The field @code{gamma} contains either @math{0} is @code{roots}
 * is empty or @math{1} plus the maximal positive integer root
 * of @math{A(q)}.
 * If undefined, it contains @math{-1}.
 * 
 * The field @code{beta} contains the bound @math{2\,k+2+\gamma+r}
 * or @math{-1} if undefined.
 * 
 * The field @code{delta} contains the bound @math{n+2\,k+2+\gamma}
 * where @math{n} denotes the order of @math{F}
 * or @math{-1} if undefined.
 * 
 * The field @code{omega} contains @code{true} if the bounds are
 * considered as correct, @code{false} otherwise.
 * Indeed, when the bound @code{beta} is determined, new prolongation
 * equations are generated which may simplify coefficients of the 
 * polynomial @math{A(q)} thereby increase @code{gamma} hence
 * @code{beta}. In such cases, some computations have to be 
 * done again.
 * If @code{omega} is equal to @code{false} then the coefficients
 * of the polynomial @math{A(q)} are checked and the computation
 * of @code{beta} is possibly restarted.
 * If @code{omega} is equal to @code{true}, the current @code{struct bas_Zuple}
 * is complete and can be transformed into a @code{bas_DLuple}.
 * Eventually, @code{beta} is equal to @code{mu} minus @math{1}.
 *
 * The field @code{number} identifies the current 
 * @code{struct bas_Zuple} in a @code{struct bas_DL_tree}.
 */

struct bas_Zuple
{
  struct ba0_tableof_int_p sigma;

  struct ba0_tableof_int_p mu;

  struct ba0_tableof_int_p zeta;

  struct bad_regchain C;
  struct bap_listof_polynom_mpz *P;
  struct bap_listof_polynom_mpz *S;

  struct ba0_tableof_int_p k;
  struct bap_tableof_tableof_polynom_mpz fn;
  struct bap_tableof_tableof_polynom_mpz der_fn;

  struct ba0_tableof_int_p phi;
  struct ba0_tableof_int_p deg;
  struct ba0_tableof_int_p r;

  struct baz_tableof_tableof_ratfrac coeffs;
  struct baz_tableof_ratfrac A;
  struct ba0_tableof_tableof_mpz roots;
  struct ba0_tableof_int_p gamma;
  struct ba0_tableof_int_p beta;
  struct ba0_tableof_int_p delta;

  struct ba0_tableof_int_p omega;

  ba0_int_p number;
};

struct bas_tableof_Zuple
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bas_Zuple **tab;
};

/*
 * texinfo: bas_typeof_action_on_Zuple
 * This data type is used to determine which action needs be
 * undertaken over a given Zuple.
 */

enum bas_typeof_action_on_Zuple
{
  bas_nothing_to_do_Zuple,
  bas_discard_Zuple,
  bas_k_to_secure_Zuple,
  bas_r_to_secure_Zuple,
  bas_beta_to_compute_Zuple,
  bas_A_to_specialize_and_beta_to_recompute_Zuple
};

struct bas_DL_tree;

extern BAS_DLL void bas_init_Zuple (
    struct bas_Zuple *);

extern BAS_DLL struct bas_Zuple *bas_new_Zuple (
    void);

extern BAS_DLL void bas_set_Yuple_Zuple (
    struct bas_tableof_Zuple *,
    struct ba0_tableof_int_p *,
    struct bas_Yuple *,
    struct bas_DL_tree *,
    struct bap_tableof_polynom_mpz *,
    struct bad_regchain *,
    struct bad_base_field *,
    struct bav_tableof_variable *);

extern BAS_DLL void bas_set_but_change_regchain_Zuple (
    struct bas_Zuple *,
    struct bas_Zuple *,
    struct bad_regchain *);

extern BAS_DLL void bas_set_Zuple (
    struct bas_Zuple *,
    struct bas_Zuple *);

extern BAS_DLL void bas_set_number_Zuple (
    struct bas_Zuple *,
    ba0_int_p);

extern BAS_DLL char *bas_typeof_action_on_Zuple_to_string (
    enum bas_typeof_action_on_Zuple);

extern BAS_DLL enum bas_typeof_action_on_Zuple bas_get_action_on_Zuple (
    struct bas_Zuple *,
    struct bas_Yuple *);

extern BAS_DLL void bas_secure_k_Zuple (
    struct bas_tableof_Zuple *,
    struct ba0_tableof_int_p *,
    struct bas_Yuple *,
    struct bas_DL_tree *,
    struct bad_base_field *);

extern BAS_DLL void bas_secure_r_Zuple (
    struct bas_tableof_Zuple *,
    struct ba0_tableof_int_p *,
    struct bas_Yuple *,
    struct bas_DL_tree *,
    struct bad_base_field *);

extern BAS_DLL void bas_compute_beta_Zuple (
    struct bas_tableof_Zuple *,
    struct ba0_tableof_int_p *,
    struct bas_Yuple *,
    struct bas_DL_tree *,
    struct bad_base_field *);

extern BAS_DLL void bas_specialize_A_and_recompute_beta_Zuple (
    struct bas_tableof_Zuple *,
    struct ba0_tableof_int_p *,
    struct bas_Yuple *,
    struct bas_DL_tree *,
    struct bad_base_field *);

extern BAS_DLL ba0_scanf_function bas_scanf_Zuple;

extern BAS_DLL ba0_printf_function bas_printf_Zuple;

extern BAS_DLL ba0_garbage1_function bas_garbage1_Zuple;

extern BAS_DLL ba0_garbage2_function bas_garbage2_Zuple;

extern BAS_DLL ba0_copy_function bas_copy_Zuple;


END_C_DECLS
#endif /* !BAS_ZUPLE_H */
