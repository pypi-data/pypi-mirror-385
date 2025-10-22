#if !defined (BAV_VARIABLE_H)
#   define BAV_VARIABLE_H 1

#   include "bav_common.h"
#   include "bav_symbol.h"

BEGIN_C_DECLS

struct bav_variable;

struct bav_tableof_variable
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bav_variable **tab;
};

struct bav_tableof_tableof_variable
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bav_tableof_variable **tab;
};

/*
 * texinfo: bav_variable
 * A @dfn{variable} is a basic objects which permits to form terms and
 * polynomials. A variable which is not a proper derivative of
 * some differential indeterminate is said to be a @dfn{radical variable}
 * (this includes independent variables, order zero derivatives).
 * Variables are allocated in @code{ba0_global.stack.quiet} and
 * are stored in the array @code{bav_global.R.vars}.
 *
 * The field @code{number} contains the number of the variable
 * with respect to each ordering occurring in @code{bav_global.R.ords}.
 * The greater the number, the greater the variables.
 * Numbers change when new variables are created
 * (by differentiation of existing variables).
 *
 * The fields @code{order} and @code{derivative} are only meaningful
 * for derivatives of differential indeterminates.
 * The sizes of these tables are equal to the number of derivations.
 * The @math{i}th entry of each of these tables is associated to
 * the @math{i}th derivation i.e. the @math{i}th element of the
 * table @code{bav_global.R.ders}.
 */

struct bav_variable
{
// the symbol at the root of the variable
  struct bav_symbol *root;
// the index of the variable in bav_global.R.vars
  ba0_int_p index_in_vars;
// the size of number is equal to bav_global.R.ords.size
  struct bav_tableof_Inumber number;
// the two next fields are for derivatives of differential indeterminates
// or differential operators. Their size is equal to bav_global.R.ders.size
  struct bav_tableof_Iorder order;
  struct bav_tableof_variable derivative;
};


#   define BAV_NOT_A_VARIABLE	BA0_NOT_A_VARIABLE
#   define BAV_TEMP_STRING		"_"
#   define BAV_JET0_INPUT_STRING      "_"
#   define BAV_JET0_OUTPUT_STRING     "_"

struct bav_term;

struct bav_tableof_parameter;

extern BAV_DLL void bav_set_settings_variable (
    ba0_scanf_function *,
    ba0_printf_function *,
    char *,
    char *,
    char *);

extern BAV_DLL void bav_get_settings_variable (
    ba0_scanf_function **,
    ba0_printf_function **,
    char **,
    char **,
    char **);

extern BAV_DLL struct bav_variable *bav_new_variable (
    void);

extern BAV_DLL struct bav_variable *bav_not_a_variable (
    void);

extern BAV_DLL void bav_R_set_variable (
    struct bav_variable *,
    struct bav_variable *,
    struct bav_differential_ring *);

extern BAV_DLL bav_Iorder bav_order_variable (
    struct bav_variable *,
    struct bav_symbol *);

extern BAV_DLL bav_Iorder bav_total_order_variable (
    struct bav_variable *);

extern BAV_DLL struct bav_variable *bav_diff_variable (
    struct bav_variable *,
    struct bav_symbol *);

extern BAV_DLL struct bav_variable *bav_diff2_variable (
    struct bav_variable *,
    struct bav_term *);

extern BAV_DLL struct bav_variable *bav_int_variable (
    struct bav_variable *,
    struct bav_symbol *);

extern BAV_DLL enum bav_typeof_symbol bav_symbol_type_variable (
    struct bav_variable *);

extern BAV_DLL struct bav_variable *bav_order_zero_variable (
    struct bav_variable *);

extern BAV_DLL struct bav_variable *bav_lcd_variable (
    struct bav_variable *,
    struct bav_variable *);

extern BAV_DLL bool bav_disjoint_variables (
    struct bav_variable *,
    struct bav_variable *);

extern BAV_DLL bool bav_is_derivative (
    struct bav_variable *,
    struct bav_variable *);

extern BAV_DLL bool bav_is_proper_derivative (
    struct bav_variable *,
    struct bav_variable *);

extern BAV_DLL bool bav_is_d_derivative (
    struct bav_variable *,
    struct bav_variable *,
    struct bav_symbol *);

extern BAV_DLL struct bav_variable *bav_derivation_between_derivatives (
    struct bav_variable *,
    struct bav_variable *);

extern BAV_DLL void bav_operator_between_derivatives (
    struct bav_term *,
    struct bav_variable *,
    struct bav_variable *);

extern BAV_DLL struct bav_variable *bav_next_derivative (
    struct bav_variable *,
    struct bav_tableof_variable *);

extern BAV_DLL ba0_mint_hp bav_random_eval_variable_to_mint_hp (
    struct bav_variable *);

extern BAV_DLL struct bav_variable *bav_indexed_string_to_variable (
    struct ba0_indexed_string *);

#   define BAV_jet_FLAG          1
#   define BAV_tjet_FLAG         2
#   define BAV_jet0_FLAG         4
#   define BAV_diff_FLAG         8
#   define BAV_inert_diff_FLAG  16
#   define BAV_Derivative_FLAG  32
#   define BAV_D_FLAG           64

extern BAV_DLL ba0_scanf_function bav_scanf_jet_variable;

extern BAV_DLL ba0_scanf_function bav_scanf_jet0_variable;

extern BAV_DLL ba0_scanf_function bav_scanf_diff_variable;

extern BAV_DLL ba0_scanf_function bav_scanf_inert_diff_variable;

extern BAV_DLL ba0_scanf_function bav_scanf_python_D_variable;

extern BAV_DLL ba0_scanf_function bav_scanf_maple_D_variable;

extern BAV_DLL ba0_scanf_function bav_scanf_python_all_variable;

extern BAV_DLL ba0_scanf_function bav_scanf_maple_all_variable;

extern BAV_DLL ba0_scanf_function bav_scanf_python_Derivative_variable;

extern BAV_DLL void bav_reset_notations (
    void);

extern BAV_DLL ba0_int_p bav_get_notations (
    void);

extern BAV_DLL ba0_printf_function bav_printf_jet_variable;

extern BAV_DLL ba0_printf_function bav_printf_jet_wesb_variable;

extern BAV_DLL ba0_printf_function bav_printf_jet0_variable;

extern BAV_DLL ba0_printf_function bav_printf_LaTeX_variable;

extern BAV_DLL ba0_printf_function bav_printf_diff_variable;

extern BAV_DLL ba0_printf_function bav_printf_inert_diff_variable;

extern BAV_DLL ba0_printf_function bav_printf_maple_D_variable;

extern BAV_DLL ba0_printf_function bav_printf_python_Derivative_variable;

extern BAV_DLL ba0_scanf_function bav_scanf_variable;

extern BAV_DLL ba0_printf_function bav_printf_variable;

extern BAV_DLL ba0_cmp_function bav_gt_index_variable;

extern BAV_DLL ba0_cmp_function bav_gt_variable;

extern BAV_DLL void bav_sort_tableof_variable (
    struct bav_tableof_variable *,
    enum ba0_sort_mode);

extern BAV_DLL void bav_independent_variables (
    struct bav_tableof_variable *);

struct bav_differential_ring;

extern BAV_DLL struct bav_variable *bav_switch_ring_variable (
    struct bav_variable *,
    struct bav_differential_ring *);

END_C_DECLS
#endif /* !BAV_VARIABLE_H */
