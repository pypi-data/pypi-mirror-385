#if ! defined (BAS_YUPLE_H)
#   define BAS_YUPLE_H 1

#   include "bas_common.h"

BEGIN_C_DECLS

/*
 * texinfo: bas_Yuple
 * The data type is used by the @code{bas_Denef_Lipshitz} algorithm.
 * It contains the part of the data related to the differential
 * indeterminates @var{y} for which formal power series are sought
 * and to their defining differential equations.
 * 
 * The field @code{Y} contains the table of the differential indeterminates.
 *
 * The other fields which are tables all have the same size as @code{Y}.
 * The @math{i}th entry of any table applies to the @math{i}th
 * differential indeterminate. Some of these entries may remain unused:
 * the ones for which the differential indeterminate have no defining equation.
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
 * @math{F^{(j)}(y_i)}. They are called the @dfn{prolongation equations}.
 *
 * To simplify statements, the table fields of the data structure
 * are described as if they applied to the single differential
 * indeterminate @math{y}.
 *
 * The field @code{dict_Y} permits to map @var{y} to its index in @code{Y}.
 * 
 * The field @code{Ybar} contains the prolongation pattern which
 * permits to evaluate derivatives of @var{y}
 * to subscripted variables, possibly multiplied by some coefficient.
 * Assume for instance that @code{Ybar} the second derivative derivative 
 * @math{\ddot y} gets evaluated to @math{y_2}. Then @code{Ybar}
 * defines a map which associates the subscripted variable @code{y[2]}
 * to the variable @code{y[x,x]}.
 * 
 * The field @code{point} is an evaluation point defined by @code{Ybar},
 * which is involved in the evaluation process mentioned above.
 * 
 * All the subscripted variables generated from @var{y}
 * have different symbols but all these 
 * symbols share the same @code{index_in_rigs} field.
 * 
 * The field @code{R} contains the value of the @code{index_in_rigs} field
 * of the subscripted variables associated to @var{y}.
 * 
 * The field @code{dict_R} permits to map any @code{index_in_rigs} to its
 * index in @code{R} hence to the index of the corresponding
 * differential indeterminate in @code{Y}.
 * 
 * The field @code{ozs} contains the subscript associated to 
 * the order zero derivative of @var{y}.
 *
 * The field @code{kappa} contains an upper bound on the valuation
 * of the separant of the @var{y}-defining ODE. 
 * More precisely, it is the smallest integer such that
 * @math{S^{(k)}(y_i)} is nonzero.
 * If undefined, it is equal to @math{-1}.
 * 
 * The field @code{ode} is a table containing derivatives of @math{F}.
 * If undefined it contains the empty table.
 * Otherwise, it contains at least @math{F}.
 * 
 * The field @code{order} contains the order of the leader of @math{F}.
 * 
 * The field @code{sep} is a table containing derivatives of @math{S}.
 * If undefined it contains the empty table.
 * Otherwise, it contains at least @math{S}.
 * 
 * The field @code{S} is the list of the inequations provided
 * by the user and which apply to constant polynomials with respect
 * to the derivation.
 * These inequations, which include in particular
 * constraints on the subscripted variables associated to differential
 * indeterminates, are provided to the regular chain decomposition method.
 *
 * The field @code{binomials} contains binomial polynomials involved
 * in the computation process of the polynomials @math{A(q)}.
 * See the @code{struct bas_Zuple} data structure.
 * 
 * The field @code{q} contains the variable to be used in the context
 * of Hurwitz formula. It stands for a number of differentiations.
 * 
 * The field @code{x} contains the independent variable.
 */

struct bas_Yuple
{
  struct bav_tableof_symbol Y;
  struct bav_dictionary_symbol dict_Y;

  struct baz_prolongation_pattern Ybar;
  struct baz_point_ratfrac point;

  struct ba0_tableof_int_p R;
  struct ba0_dictionary dict_R;

  struct ba0_tableof_int_p ozs;

  struct ba0_tableof_int_p kappa;

  struct bap_tableof_tableof_polynom_mpz ode;
  struct ba0_tableof_int_p order;

  struct bap_tableof_tableof_polynom_mpz sep;

  struct bap_listof_polynom_mpz *S;

  struct bap_tableof_polynom_mpq binomials;

  struct bav_variable *q;
  struct bav_symbol *x;
};

extern BAS_DLL void bas_init_Yuple (
    struct bas_Yuple *);

extern BAS_DLL struct bas_Yuple *bas_new_Yuple (
    void);

extern BAS_DLL void bas_set_Yuple (
    struct bas_Yuple *,
    struct bas_Yuple *);

extern BAS_DLL void bas_set_Y_Ybar_Yuple (
    struct bas_Yuple *,
    struct bav_tableof_symbol *,
    struct baz_prolongation_pattern *,
    struct bap_tableof_polynom_mpz *,
    struct bav_variable *,
    struct bav_symbol *);

extern BAS_DLL void bas_set_ode_Yuple (
    struct bas_Yuple *,
    struct bad_regchain *,
    struct bad_base_field *);

extern BAS_DLL void bas_prolongate_binomials_Yuple (
    struct bas_Yuple *,
    ba0_int_p);

extern BAS_DLL ba0_scanf_function bas_scanf_Yuple;

extern BAS_DLL ba0_printf_function bas_printf_Yuple;

extern BAS_DLL ba0_garbage1_function bas_garbage1_Yuple;

extern BAS_DLL ba0_garbage2_function bas_garbage2_Yuple;

extern BAS_DLL ba0_copy_function bas_copy_Yuple;

END_C_DECLS
#endif /* !BAS_YUPLE_H */
