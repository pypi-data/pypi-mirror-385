#if !defined (BAV_COMMON_H)
#   define BAV_COMMON_H 1

#   include <ba0.h>

/* 
 * The _MSC_VER flag is set if the code is compiled under WINDOWS
 * by using Microsoft Visual C (through Visual Studio 2008).
 *
 * In that case, some specific annotations must be added for DLL exports
 * Beware to the fact that this header file is going to be used either
 * for/while building BLAD or for using BLAD from an outer software.
 *
 * In the first case, functions are exported.
 * In the second one, they are imported.
 *
 * The flag BAV_BLAD_BUILDING must thus be set in the Makefile and passed
 * to the C preprocessor at BAV building time. Do not set it when using BAV.
 *
 * When compiling static libraries under Windows, set BA0_STATIC.
 */

#   if defined (_MSC_VER) && ! defined (BA0_STATIC)
#      if defined (BLAD_BUILDING) || defined (BAV_BLAD_BUILDING)
#         define BAV_DLL  __declspec(dllexport)
#      else
#         define BAV_DLL  __declspec(dllimport)
#      endif
#   else
#      define BAV_DLL
#   endif

/* #   include "bav_mesgerr.h" */

BEGIN_C_DECLS

/*
 * texinfo: bav_Idegree
 * This is the integer type for degrees.
 */

typedef ba0_int_p bav_Idegree;

#   define BAV_MAX_IDEGRE BA0_MAX_INT_P

/*
 * texinfo: bav_Iorder
 * This is the integer type for differentiation orders.
 */

typedef ba0_int_p bav_Iorder;

/*
 * texinfo: bav_Iordering
 * This is the integer type for ordering numbers.
 */

typedef ba0_int_p bav_Iordering;

/*
 * texinfo: bav_Inumber
 * This is the integer type for variable numbers.
 */

typedef ba0_int_p bav_Inumber;

struct bav_tableof_Inumber
{
  ba0_int_p alloc;
  ba0_int_p size;
  bav_Inumber *tab;
};

struct bav_tableof_Iorder
{
  ba0_int_p alloc;
  ba0_int_p size;
  bav_Iorder *tab;
};

struct bav_tableof_Iordering
{
  ba0_int_p alloc;
  ba0_int_p size;
  bav_Iordering *tab;
};

struct bav_tableof_Idegree
{
  ba0_int_p alloc;
  ba0_int_p size;
  bav_Idegree *tab;
};

/* 
 * struct ba0_indexed_string* not recognized by parsers.
 * The function pointer, a buffer and the default value for the pointer
 */

extern BAV_DLL ba0_indexed_string_function bav_unknown_default;

extern BAV_DLL void bav_set_settings_common (
    ba0_indexed_string_function *);

extern BAV_DLL void bav_get_settings_common (
    ba0_indexed_string_function **);

extern BAV_DLL void bav_reset_all_settings (
    void);

struct bav_PFE_settings;

extern BAV_DLL void bav_cancel_PFE_settings (
    struct bav_PFE_settings *);

extern BAV_DLL void bav_restore_PFE_settings (
    struct bav_PFE_settings *);

extern BAV_DLL void bav_restart (
    ba0_int_p,
    ba0_int_p);

extern BAV_DLL void bav_terminate (
    enum ba0_restart_level);

END_C_DECLS
#endif /* !BAV_COMMON_H */
#if !defined (BAV_MESGERR_H)
#   define BAV_MESGERR_H 1

/* #   include "bav_common.h" */

BEGIN_C_DECLS

extern BAV_DLL char BAV_ERRUSY[];

extern BAV_DLL char BAV_ERRDSY[];

extern BAV_DLL char BAV_ERRRIG[];

extern BAV_DLL char BAV_ERRBSD[];

extern BAV_DLL char BAV_ERRPAO[];

extern BAV_DLL char BAV_ERRPAR[];

extern BAV_DLL char BAV_ERRDIF[];

extern BAV_DLL char BAV_ERRDVR[];

extern BAV_DLL char BAV_ERRSPY[];

extern BAV_DLL char BAV_ERRDFV[];

extern BAV_DLL char BAV_ERRBLO[];

extern BAV_DLL char BAV_ERRBOR[];

extern BAV_DLL char BAV_ERRTER[];

extern BAV_DLL char BAV_ERRRGZ[];

extern BAV_DLL char BAV_ERRTEU[];

extern BAV_DLL char BAV_EXEXQO[];

END_C_DECLS
#endif /* !BAV_MESGERR_H */
#if !defined (BAV_SYMBOL_H)
#   define BAV_SYMBOL_H 1

/* #   include "bav_common.h" */

BEGIN_C_DECLS

/*
 * texinfo: bav_typeof_symbol
 * Independent symbols are used to build derivations.
 * Dependent symbols are used to build differential indeterminates.
 * Operator symbols are used to build differential operators.
 * Temporary symbols are used to build temporary variables.
 */

enum bav_typeof_symbol
{
  bav_independent_symbol,
  bav_dependent_symbol,
  bav_operator_symbol,
  bav_temporary_symbol
};

/*
 * texinfo: bav_symbol
 * A @dfn{symbol} mostly is an identifier endowed with a type.
 * Symbols are used to define variables.
 * In the case of an @dfn{independent symbol} or 
 * a @dfn{temporary symbol}, the symbol is associated to a
 * unique corresponding variable.
 * In the case of a @dfn{dependent symbol} or an 
 * @dfn{operator symbol}, the symbol is shared by many different 
 * variables, corresponding to its derivatives.
 *
 * Symbols are not duplicated. 
 * They are allocated in @code{ba0_global.stack.quiet} and
 * stored in the table @code{bav_global.R.syms}.
 *
 * A symbol may be a @dfn{plain symbol} or a symbol which
 * fits a range indexed string. The latter case can only occur
 * if the symbol is dependent.
 *
 * If the symbol is a plain symbol then its field
 * @code{index_in_rigs} contains @code{BA0_NOT_AN_INDEX}
 * and the field @code{subscripts} is empty.
 * If it fits a range indexed string then its field @code{index_in_rigs}
 * contains the index in @code{bav_global.R.rigs} of the radical
 * of its identifier and the field @code{subscripts} contains its
 * subscripts.
 *
 * A symbol may be a parameter or not.
 * Only dependent symbols may be parameters.
 * If the symbol is a parameter then its field @code{index_in_pars} contains
 * the index in @code{bav_global.pars.pars} of its parameter description.
 * If the symbol is not a parameter, its field @code{index_in_pars} contains
 * @code{BA0_NOT_AN_INDEX}.
 */

struct bav_symbol
{
// the identifier of the symbol
  char *ident;
// its type
  enum bav_typeof_symbol type;
// the index of the symbol in bav_global.R.syms
  ba0_int_p index_in_syms;
// if ident fits a range indexed string, an index in bav_global.R.rigs
  ba0_int_p index_in_rigs;
// if ident fits a range indexed string, the table of its subscripts
  struct ba0_tableof_int_p subscripts;
// if the symbol is independent, its index in bav_global.R.ders 
  ba0_int_p derivation_index;
// if the symbol is a parameter, its index in bav_global.R.pars.pars 
  ba0_int_p index_in_pars;
};

#   define BAV_NOT_A_SYMBOL	(struct bav_symbol*)0

struct bav_tableof_symbol
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bav_symbol **tab;
};

extern BAV_DLL void bav_set_settings_symbol (
    ba0_scanf_function *,
    ba0_printf_function *,
    char *);

extern BAV_DLL void bav_get_settings_symbol (
    ba0_scanf_function **,
    ba0_printf_function **,
    char **);

extern BAV_DLL void bav_init_symbol (
    struct bav_symbol *);

extern BAV_DLL struct bav_symbol *bav_new_symbol (
    void);

extern BAV_DLL struct bav_symbol *bav_not_a_symbol (
    void);

extern BAV_DLL unsigned ba0_int_p bav_sizeof_symbol (
    struct bav_symbol *,
    enum ba0_garbage_code,
    bool);

extern BAV_DLL void bav_R_set_symbol (
    struct bav_symbol *,
    struct bav_symbol *,
    char *);

extern BAV_DLL bool bav_is_a_derivation (
    char *);

extern BAV_DLL bool bav_is_subscripted_symbol (
    struct bav_symbol *);

extern BAV_DLL ba0_int_p bav_subscript_of_symbol (
    struct bav_symbol *);

extern BAV_DLL ba0_scanf_function bav_scanf_symbol;

extern BAV_DLL ba0_scanf_function bav_scanf_default_symbol;

extern BAV_DLL ba0_scanf_function bav_scanf2_symbol;

extern BAV_DLL ba0_printf_function bav_printf_symbol;

extern BAV_DLL ba0_printf_function bav_printf_default_symbol;

extern BAV_DLL ba0_printf_function bav_printf_numbered_symbol;

struct bav_differential_ring;

extern BAV_DLL struct bav_symbol *bav_switch_ring_symbol (
    struct bav_symbol *,
    struct bav_differential_ring *);

END_C_DECLS
#endif /* ! BAV_SYMBOL_H */
#if !defined (BAV_DICTIONARY_SYMBOL_H)
#   define BAV_DICTIONARY_SYMBOL_H 1

/* #   include "bav_symbol.h" */

BEGIN_C_DECLS

/*
 * texinfo: bav_dictionary_symbol
 * This data structure implements dictionaries which map 
 * @code{struct bav_symbol *} to other objects.
 * In this implementation, the values associated to the keys are integers, 
 * which are supposed to be indices in some table of objects of unspecified 
 * type.
 * This data structure actually is as an alias for
 * @code{struct ba0_dictionary}. 
 */

struct bav_dictionary_symbol
{
// each entry contains either -1 or an index in some table of symbols
  struct ba0_tableof_int_p area;
// the shift applied on keys before hashing them
  ba0_int_p shift;
// the base-2 logarithm of the size/alloc field of area if area is nonempty
  ba0_int_p log2_size;
// the number of used entries in area
  ba0_int_p used_entries;
};

extern BAV_DLL void bav_init_dictionary_symbol (
    struct bav_dictionary_symbol *,
    ba0_int_p);

extern BAV_DLL void bav_reset_dictionary_symbol (
    struct bav_dictionary_symbol *);

extern BAV_DLL unsigned ba0_int_p bav_sizeof_dictionary_symbol (
    struct bav_dictionary_symbol *,
    enum ba0_garbage_code);

extern BAV_DLL void bav_set_dictionary_symbol (
    struct bav_dictionary_symbol *,
    struct bav_dictionary_symbol *);

extern BAV_DLL ba0_int_p bav_get_dictionary_symbol (
    struct bav_dictionary_symbol *,
    struct bav_tableof_symbol *,
    struct bav_symbol *);

extern BAV_DLL void bav_add_dictionary_symbol (
    struct bav_dictionary_symbol *,
    struct bav_tableof_symbol *,
    struct bav_symbol *,
    ba0_int_p);

END_C_DECLS
#endif /* !BAV_DICTIONARY_SYMBOL_H */
#if !defined (BAV_PARAMETER_H)
#   define BAV_PARAMETER_H 1

/* #   include "bav_symbol.h" */

BEGIN_C_DECLS

/*
 * texinfo: bav_parameter
 * This data structure permits to represent a @dfn{parameter} i.e. a dependent
 * symbol / order zero dependent variable for which some derivatives
 * are supposed to simplify to zero (the notion of parameter is here
 * more general than the usual one).
 *
 * A parameter may be a @dfn{plain parameter} or a parameter which
 * fits a range indexed group.
 * If the parameter is a plain one, then its identifier is the identifier 
 * of a dependent symbol / order zero dependent variable. 
 * If it fits a range indexed group, it describes a set of parameters 
 * which is made of all the symbols which fit the group.
 *
 * The field @code{dependencies} contains the derivation indices of the
 * derivations / independent variables the parameter depends on. 
 * If this field is empty, every derivative of the parameter is zero.
 * The order of appearance of the derivations in this field is followed
 * by some printing functions.
 */

struct bav_parameter
{
// the range indexed group which describes the parameter identifiers
  struct ba0_range_indexed_group rig;
// the table of the derivation indices the parameter depends on
  struct ba0_tableof_int_p dependencies;
};

struct bav_tableof_parameter
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bav_parameter **tab;
};

struct bav_variable;

extern BAV_DLL void bav_set_settings_parameter (
    char *);

extern BAV_DLL void bav_get_settings_parameter (
    char * *);

extern BAV_DLL void bav_init_parameter (
    struct bav_parameter *);

extern BAV_DLL struct bav_parameter *bav_new_parameter (
    void);

extern BAV_DLL void bav_set_parameter (
    struct bav_parameter *,
    struct bav_parameter *);

extern BAV_DLL void bav_set_parameter_with_tableof_string (
    struct bav_parameter *,
    struct bav_parameter *,
    struct ba0_dictionary_string *,
    struct ba0_tableof_string *);

extern BAV_DLL void bav_set_tableof_parameter_with_tableof_string (
    struct bav_tableof_parameter *,
    struct bav_tableof_parameter *,
    struct ba0_dictionary_string *,
    struct ba0_tableof_string *);

extern BAV_DLL unsigned ba0_int_p bav_sizeof_parameter (
    struct bav_parameter *,
    enum ba0_garbage_code,
    bool);

extern BAV_DLL unsigned ba0_int_p bav_sizeof_tableof_parameter (
    struct bav_tableof_parameter *,
    enum ba0_garbage_code,
    bool);

extern BAV_DLL bool bav_is_a_parameter (
    struct bav_symbol *,
    struct bav_parameter **);

extern BAV_DLL void bav_annihilating_derivations_of_parameter (
    struct bav_tableof_symbol *,
    struct bav_parameter *);

extern BAV_DLL bool bav_is_constant_variable (
    struct bav_variable *,
    struct bav_symbol *);

extern BAV_DLL bool bav_is_zero_derivative_of_parameter (
    struct bav_variable *);

extern BAV_DLL void *bav_scanf_parameter (
    void *z);

extern BAV_DLL void bav_printf_parameter_dependencies (
    struct bav_parameter *);

extern BAV_DLL void bav_printf_parameter (
    void *z);

END_C_DECLS
#endif /* ! extern BAV_PARAMETER_H */
#if !defined (BAV_PARAMETERS_H)
#   define BAV_PARAMETERS_H

/* #   include "bav_parameter.h" */

BEGIN_C_DECLS

/*
 * texinfo: bav_parameters
 * This data type is only used to form the field @code{pars}
 * of the @code{bav_differential_ring} structure. It handles
 * the parameters of the differential ring.
 *
 * The field @code{pars} contains the table of all parameters.
 * Each range indexed group occurring in any element of the
 * table actually is a range indexed string i.e. has a single radical.
 *
 * The field @code{dict} maps strings to non-plain parameters in @code{pars}. 
 * The keys are the radicals of the range indexed strings. 
 * The dictionary does not contain any entry corresponding to plain parameters.
 */

struct bav_parameters
{
// maps strings to radicals of range indexed strings for non-plain parameters
  struct ba0_dictionary_string dict;
// the table of parameters - range indexed groups are range indexed strings
  struct bav_tableof_parameter pars;
};

extern BAV_DLL void bav_init_parameters (
    struct bav_parameters *);

extern BAV_DLL unsigned ba0_int_p bav_sizeof_parameters (
    struct bav_parameters *,
    enum ba0_garbage_code,
    bool);

extern BAV_DLL void bav_R_set_parameters (
    struct bav_parameters *,
    struct bav_parameters *,
    struct bav_differential_ring *);

extern BAV_DLL void bav_R_set_parameters_tableof_parameter (
    struct bav_parameters *,
    struct bav_tableof_parameter *);

END_C_DECLS
#endif /* !BAV_PARAMETERS_H */
#if !defined (BAV_VARIABLE_H)
#   define BAV_VARIABLE_H 1

/* #   include "bav_common.h" */
/* #   include "bav_symbol.h" */

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
#if !defined (BAV_DICTIONARY_VARIABLE_H)
#   define BAV_DICTIONARY_VARIABLE_H 1

/* #   include "bav_variable.h" */

BEGIN_C_DECLS

/*
 * texinfo: bav_dictionary_variable
 * This data structure implements dictionaries which map 
 * @code{struct bav_variable *} to other objects.
 * In this implementation, the values associated to the keys are integers, 
 * which are supposed to be indices in some table of objects of unspecified 
 * type.
 * This data structure actually is as an alias for
 * @code{struct ba0_dictionary}. 
 */

struct bav_dictionary_variable
{
// each entry contains either -1 or an index in some table of variables
  struct ba0_tableof_int_p area;
// the shift applied on keys before hashing them
  ba0_int_p shift;
// the base-2 logarithm of the size/alloc field of area if area is nonempty
  ba0_int_p log2_size;
// the number of used entries in area
  ba0_int_p used_entries;
};

extern BAV_DLL void bav_init_dictionary_variable (
    struct bav_dictionary_variable *,
    ba0_int_p);

extern BAV_DLL void bav_reset_dictionary_variable (
    struct bav_dictionary_variable *);

extern BAV_DLL unsigned ba0_int_p bav_sizeof_dictionary_variable (
    struct bav_dictionary_variable *,
    enum ba0_garbage_code);

extern BAV_DLL void bav_set_dictionary_variable (
    struct bav_dictionary_variable *,
    struct bav_dictionary_variable *);

extern BAV_DLL ba0_int_p bav_get_dictionary_variable (
    struct bav_dictionary_variable *,
    struct bav_tableof_variable *,
    struct bav_variable *);

extern BAV_DLL void bav_add_dictionary_variable (
    struct bav_dictionary_variable *,
    struct bav_tableof_variable *,
    struct bav_variable *,
    ba0_int_p);

END_C_DECLS
#endif /* !BAV_DICTIONARY_VARIABLE_H */
#if !defined (BAV_OPERATOR_H)
#   define BAV_OPERATOR_H 1

/* #   include "bav_common.h" */
/* #   include "bav_variable.h" */


BEGIN_C_DECLS

END_C_DECLS
#endif /* !BAV_OPERATOR_H */
#if !defined (BAV_SUBRANKING_H)
#   define BAV_SUBRANKING_H 1

/* #   include "bav_common.h" */
/* #   include "bav_variable.h" */
/* #   include "bav_typed_ident.h" */


BEGIN_C_DECLS

/*
 * texinfo: bav_subranking
 * This data type implements subrankings.
 * A @dfn{subranking} permits to
 * compare derivatives of differential indeterminates.
 * Subrankings form a subtype of the @code{bav_block} data type.
 *
 * There are five predefined subrankings:
 * @code{lex}, @code{grlexA}, @code{grlexB}, @code{degrevlexA}
 * and @code{degrevlexB}.
 * The difference between them is actually only meaningful in the case of
 * partial derivatives.
 * Consider two different derivatives @math{u = \theta\,y} and 
 * @math{v = \phi\,z} to be compared.
 * View the @dfn{derivative operators} @math{\theta,\phi} as power products 
 * of derivations. 
 *
 * Among themselves, differential indeterminates are ordered by their
 * order of appearance in the block.
 * Among themselves, derivations are ordered by their order of
 * appearance in the derivation list:
 * this permits to compare derivative operators.
 * For details, see the @code{bav_ordering} data structure.
 *
 * In the @code{lex} ordering, derivative operators 
 * are first compared with respect to the lexicographic order; in case
 * of equality, differential indeterminates are compared.
 *
 * In all other subrankings, derivative operators are first compared
 * with respect to their total order. In the sequel, it is assumed
 * that @math{\theta} and @math{\phi} have the same total order.
 *
 * In the @code{grlexA} and @code{degrevlexA} subrankings, 
 * the second comparison criterion is given by the differential 
 * indeterminates i.e. @math{u > v} if @math{y > z}.
 * In the case of equality, the derivative operators are compared
 * either with respect to the lexicographic ordering (@code{grlexA})
 * or with respect to the reverse lexicographic ordering (@code{degrevlexA}).
 *
 * In the @code{grlexB} and @code{degrevlexB} subrankings, 
 * the second comparison criterion is given by the derivative operators,
 * which are compared either with respect to the lexicographic ordering 
 * (@code{grlexB}) or with respect to the reverse lexicographic ordering 
 * (@code{degrevlexB}). In the case of equality, the differential 
 * indeterminates are compared.
 *
 * To each subranking, a comparison function @code{inf} is associated.
 * This function is called when a new ordering or a new variable are
 * created. It is involved in the comparison process of two variables,
 * in order to determine their numbers, with respect to some ordering
 * @var{ord}.
 *
 * This function takes as input two different variables @var{v} and @var{w}
 * belonging to some same block of @var{ord}, their typed ident
 * @var{tid_v} and @var{tid_w}, picked 
 * from the @code{typed_idents} field of @var{ord} and the address
 * of the @code{ders} field of @var{ord}. It returns @code{true} if 
 * @math{v < w} with respect to the subranking (hence the ordering),
 * @code{false} otherwise.
 */

struct bav_typed_ident;

struct bav_subranking
{
// The identifier of the subranking (grlexA, degrevlexB, ...)
// This identifier is a readonly global string.
  char *ident;
  bool (
      *inf) (
      struct bav_variable * v,
      struct bav_variable * w,
      struct bav_typed_ident * tid_v,
      struct bav_typed_ident * tid_w,
      struct bav_tableof_symbol * ders);
};

extern BAV_DLL bool bav_is_subranking (
    char *,
    struct bav_subranking **);

END_C_DECLS
#endif /* !BAV_SUBRANKING_H */
#if !defined (BAV_BLOCK_H)
#   define BAV_BLOCK_H 1

/* #   include "bav_common.h" */
/* #   include "bav_symbol.h" */
/* #   include "bav_subranking.h" */

BEGIN_C_DECLS

/*
 * texinfo: bav_block
 * A @dfn{block} is a list of range indexed groups defining differential
 * indeterminates (possibly also a single differential operator) 
 * ordered with respect to some common subranking. See the description 
 * of the data types @code{bav_subranking} and @code{bav_ordering}.
 */

struct bav_block
{
// the subranking which applies to the block
  struct bav_subranking *subr;
// the table of the range indexed groups of the block
  struct ba0_tableof_range_indexed_group rigs;
};

#   define BAV_NOT_A_BLOCK (struct bav_block*)0

struct bav_tableof_block
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bav_block **tab;
};

extern BAV_DLL void bav_init_block (
    struct bav_block *);

extern BAV_DLL void bav_reset_block (
    struct bav_block *);

extern BAV_DLL struct bav_block *bav_new_block (
    void);

extern BAV_DLL unsigned ba0_int_p bav_sizeof_block (
    struct bav_block *,
    enum ba0_garbage_code,
    bool);

extern BAV_DLL unsigned ba0_int_p bav_sizeof_tableof_block (
    struct bav_tableof_block *,
    enum ba0_garbage_code,
    bool);

struct bav_differential_ring;

extern BAV_DLL void bav_R_set_block (
    struct bav_block *,
    struct bav_block *,
    struct bav_differential_ring *);

extern BAV_DLL void bav_R_set_tableof_block (
    struct bav_tableof_block *,
    struct bav_tableof_block *,
    struct bav_differential_ring *);

extern BAV_DLL bool bav_is_empty_block (
    struct bav_block *);

extern BAV_DLL ba0_scanf_function bav_scanf_block;

extern BAV_DLL ba0_printf_function bav_printf_block;

END_C_DECLS
#endif /* !BAV_BLOCK_H */
#if !defined (BAV_TYPED_IDENT_H)
#   define BAV_TYPED_IDENT_H 1

/* #   include "bav_common.h" */

BEGIN_C_DECLS

/*
 * texinfo: bav_typeof_ident
 * This data type is a subtype of @code{bav_typed_ident}.
 */

enum bav_typeof_ident
{
// The identifier is a plain string
  bav_plain_ident,
// The identifier is the radical of a range indexed string
  bav_range_indexed_string_radical_ident
};

/*
 * texinfo: bav_typed_ident
 * This data structure permits to associate a table of indices
 * to typed identifiers. 
 * As a substructure of @code{bav_ordering}, it associates to
 * any typed identifier three indices: the index of the block which
 * contains the identifier; the index of the identifier within
 * the block; the index of the identifier in the group (this last
 * index is only meaningful if the type is 
 * @code{bav_range_indexed_string_radical_ident}).
 */

struct bav_typed_ident
{
// the string - possibly (char *)0
  char *ident;
// its type
  enum bav_typeof_ident type;
// the indices associated to the typed ident
  struct ba0_tableof_int_p indices;
};

struct bav_tableof_typed_ident
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bav_typed_ident **tab;
};

struct bav_symbol;
struct bav_block;
struct bav_tableof_block;

extern BAV_DLL void bav_init_typed_ident (
    struct bav_typed_ident *);

extern BAV_DLL struct bav_typed_ident *bav_new_typed_ident (
    void);

extern BAV_DLL unsigned ba0_int_p bav_sizeof_typed_ident (
    struct bav_typed_ident *,
    enum ba0_garbage_code,
    bool);

extern BAV_DLL unsigned ba0_int_p bav_sizeof_tableof_typed_ident (
    struct bav_tableof_typed_ident *,
    enum ba0_garbage_code,
    bool);

struct bav_differential_ring;

extern BAV_DLL void bav_R_set_typed_ident (
    struct bav_typed_ident *,
    struct bav_typed_ident *,
    struct bav_differential_ring *);

extern BAV_DLL void bav_R_set_tableof_typed_ident (
    struct bav_tableof_typed_ident *,
    struct bav_tableof_typed_ident *,
    struct bav_differential_ring *);

extern BAV_DLL void bav_R_append_tableof_typed_ident_block (
    struct bav_tableof_typed_ident *,
    ba0_int_p,
    struct bav_block *,
    struct bav_differential_ring *);

extern BAV_DLL void bav_R_set_tableof_typed_ident_tableof_block (
    struct bav_tableof_typed_ident *,
    struct bav_tableof_block *,
    struct bav_differential_ring *);

extern BAV_DLL ba0_int_p bav_get_typed_ident_from_symbol (
    struct ba0_dictionary_typed_string *,
    struct bav_tableof_typed_ident *,
    struct bav_symbol *);

END_C_DECLS
#endif /* !BAV_TYPED_IDENT_H */
#if !defined (BAV_ORDERING_H)
#   define BAV_ORDERING_H 1

/* #   include "bav_common.h" */
/* #   include "bav_symbol.h" */
/* #   include "bav_block.h" */
/* #   include "bav_variable.h" */
/* #   include "bav_operator.h" */
/* #   include "bav_typed_ident.h" */

BEGIN_C_DECLS

/*
 * texinfo: bav_ordering
 * This data type is a subtype of @code{bav_differential_ring}
 * used to describe orderings. 
 * In differential algebra, derivatives of differential indeterminates
 * are ordered with respect to a @dfn{ranking}. In the software, the
 * notion of ranking is generalized to the one of @dfn{ordering}, to take
 * into account independent variables, temporary variables or derivatives 
 * temporarily considered as maximal or minimal variables.
 * The simplest method to define an ordering in the @code{bav} library
 * consists in using the parser. Let us thus have a look to a few
 * different definitions of orderings, accepted by the parser.
 * @verbatim
 * 1. ordering (derivations = [t], blocks = [[u,v], grlexB[w]])
 * 2. ordering (derivations = [], blocks = [w,v,u])
 * 3. ordering (derivations = [x,y], blocks = [degrevlexA[u]],
 *              operator = [D], varmax = [u[x,x]])
 * 4. ordering (derivations = [x,y], blocks = [degrevlexB[u],v], 
 *              varmax = [u[x],u[x,x,x]], varmin = [u[x,x]])
 * @end verbatim
 * An ordering is first defined by a list of blocks @math{[b_1,\ldots,b_n]}.
 * Leftmost blocks are considered as greater than rightmost ones i.e.
 * every derivative of any differential indeterminate present in @math{b_i}
 * is greater than any derivative of any differential indeterminate present 
 * in @math{b_{i+k}} (with @math{k > 0}).
 * In Example 1, we have @math{v_t > w_{t,t,t}}.
 * In Example 2, we have @math{w > v > u}.
 *
 * Within a fixed block, derivatives are ordered with respect to a 
 * @dfn{subranking} (see the description of the data 
 * type @code{bav_subranking}).
 * The default subranking is @code{grlexA}.
 * Other subrankings such as @code{grlexB}, @code{degrevlexA} or
 * @code{degrevlexB} appear in the above examples.
 * Subrankings are only meaningful in the partial case.
 * In the ordinary case everything simplifies as follows.
 * Consider a block @math{[u_1,\ldots,u_n]} of differential indeterminates.
 * Derivatives of the @math{u_i} are first compared with respect to their
 * @dfn{order}. In the case of two derivatives with the same order,
 * leftmost differential indeterminates are considered as greater than 
 * rightmost ones. 
 * 
 * Independent variables / derivations are considered as lower than derivatives.
 * In the partial case, leftmost derivations are considered as greater
 * than rightmost ones, in the list of derivations.
 * In Examples 3 and 4, we have @math{x > y}.
 *
 * The orderings defined so far mostly are rankings (slightly generalized
 * to cover the case of independent variables). They are suitable for
 * differential elimination algorithms. However, it is also sometimes
 * useful to use orderings which are not rankings by specifying 
 * variables considered as greater than or lower than any other variable
 * (such orderings should only be used when no differentiation process
 * is involved). This is achieved by means of the @code{varmax} and the
 * @code{varmin} lists.
 * In Example 3, @math{u_{x,x}} is greater than any other variable.
 * In Example 4, @math{u_x} and @math{u_{x,x,x}} are greater than
 * any other variable. Moreover @math{u_x > u_{x,x,x}} and @math{u_{x,x}}
 * is lower than any other variable.
 *
 * In principle, it is also possible to define a @dfn{differential operator}.
 * Derivatives of the differential operator are ordered as variables,
 * using a block description. Any derivative of the differential operator is
 * greater than any derivative of any differential indeterminate.
 * However, derivatives listed in the @code{varmax} list are considered
 * as greater than derivatives of the differential operator.
 * 
 * It is moreover possible to define temporary variables.
 * These variables are considered as lower than any other variable.
 * Among themselves, temporary variables are ordered according
 * to some session dependent unspecified ordering.
 * These temporary variables are handled in the @code{bav_differential_ring}
 * data structure.
 *
 * The fields @code{typed_ident} and @code{dict} permit to associate
 * a triple @math{(i,j,k)} of indices to a typed identifier @var{ident}. 
 * They are used for computing variable numbers.
 * The first index @math{i} is the block number of @var{ident} in the sense
 * that @var{ident} belongs to the @math{i}th entry of the @code{blocks}
 * table. The second index @math{j} is the index of @var{ident} within
 * the @math{i}th block.
 * The third index @math{k} is is meaningful in the case of range indexed 
 * groups which are not plain strings. It gives the index of @var{ident}
 * in the group.
 * Consider the following example, featuring a table of two blocks.
 * @verbatim
 * blocks = [[z], [(y,z)[inf:-1], t, (u)[3:5]]]
 * @end verbatim
 * Then the @code{typed_ident} field contains the three following entries:
 * @verbatim
 * typed_ident = [
 *  ['z', bav_plain_ident, 0, 0, -1],
 *  ['y', bav_range_indexed_string_radical_ident, 1, 0, 0], 
 *  ['z', bav_range_indexed_string_radical_ident, 1, 0, 1],
 *  ['t', bav_plain_ident, 1, 1, -1],
 *  ['u', bav_range_indexed_string_radical_ident, 1, 2, 0]]
 * @end verbatim
 */

struct bav_ordering
{
// the table of derivations - the order matters for some subrankings
  struct bav_tableof_symbol ders;
// the table of blocks
  struct bav_tableof_block blocks;
// the array of typed ident and its associated dictionary.
  struct bav_tableof_typed_ident typed_idents;
  struct ba0_dictionary_typed_string dict;
// the block for the differential operator - if any
  struct bav_block operator_block;
// the variables set as maximal variables
  struct bav_tableof_variable varmax;
// the variables set as minimal variables
  struct bav_tableof_variable varmin;
};

struct bav_tableof_ordering
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bav_ordering **tab;
};

struct bav_parameter;

extern BAV_DLL void bav_set_settings_ordering (
    char *);

extern BAV_DLL void bav_get_settings_ordering (
    char **);

extern BAV_DLL unsigned ba0_int_p bav_sizeof_ordering (
    struct bav_ordering *,
    enum ba0_garbage_code,
    bool);

extern BAV_DLL unsigned ba0_int_p bav_sizeof_tableof_ordering (
    struct bav_tableof_ordering *,
    enum ba0_garbage_code,
    bool);

extern BAV_DLL void bav_R_set_ordering (
    struct bav_ordering *,
    struct bav_ordering *,
    struct bav_differential_ring *);

extern BAV_DLL void bav_R_set_tableof_ordering (
    struct bav_tableof_ordering *,
    struct bav_tableof_ordering *,
    struct bav_differential_ring *);

extern BAV_DLL void bav_init_ordering (
    struct bav_ordering *);

extern BAV_DLL void bav_reset_ordering (
    struct bav_ordering *);

extern BAV_DLL struct bav_ordering *bav_new_ordering (
    void);

extern BAV_DLL void bav_set_ordering (
    struct bav_ordering *,
    struct bav_ordering *);

extern BAV_DLL ba0_scanf_function bav_scanf_ordering;

extern BAV_DLL ba0_printf_function bav_printf_ordering;

extern BAV_DLL int bav_R_compare_variable (
    struct bav_variable *,
    struct bav_variable *);

extern BAV_DLL void bav_block_sort_tableof_variable (
    struct bav_tableof_tableof_variable *,
    struct bav_tableof_variable *,
    struct bav_tableof_variable *);

extern BAV_DLL void bav_R_sort_tableof_variable (
    struct bav_tableof_variable *);

extern BAV_DLL void bav_R_lower_block_range_indexed_strings (
    struct ba0_tableof_range_indexed_group *,
    ba0_int_p);

extern BAV_DLL ba0_int_p bav_block_index_symbol (
    struct bav_symbol *);

extern BAV_DLL ba0_int_p bav_block_index_range_indexed_group (
    struct ba0_range_indexed_group *);

extern BAV_DLL ba0_int_p bav_block_index_parameter (
    struct bav_parameter *);

extern BAV_DLL bool bav_has_varmax_current_ordering (
    void);

END_C_DECLS
#endif /* !BAV_ORDERING_H */
#if !defined (BAV_DIFFERENTIAL_RING_H)
#   define BAV_DIFFERENTIAL_RING_H 1

/* #   include "bav_common.h" */
/* #   include "bav_block.h" */
/* #   include "bav_symbol.h" */
/* #   include "bav_variable.h" */
/* #   include "bav_operator.h" */
/* #   include "bav_parameters.h" */
/* #   include "bav_ordering.h" */

BEGIN_C_DECLS

/*
 * texinfo: bav_differential_ring
 * This data type implements one mathematical differential ring
 * endowed with many different orderings. It is completely
 * stored in @code{ba0_global.stack.quiet} (the quiet stack).
 *
 * The field @code{strs} contains all the strings used as identifiers
 * of symbols or as radicals of range indexed strings. Note 1: identifiers of
 * symbols involve identifiers of variables which fit range indexed strings.
 * Note 2: the same string may be both the radical of a range indexed string
 * and the identifier of a differential indeterminate.
 *
 * The @code{syms} table contains all the symbols. 
 * The @code{vars} table contains all the variables.
 *
 * The dictionary @code{dict_str_to_var} maps strings to variables
 * of the @code{vars} table.
 * Only the radical variables are stored in this dictionary.
 *
 * The dictionary @code{dict_str_to_rig} maps strings to range indexed
 * strings of the @code{rigs} table. The keys are the radicals of the
 * range indexed strings.
 *
 * The table @code{ders} contains the indices in @code{vars} of the
 * derivations / independent variables. The index in @code{ders}
 * of a derivation is called its @dfn{derivation index}.
 * This table thus maps derivation indices to the corresponding
 * independent variables.
 *
 * The field @code{ords} contains all the defined orderings.
 * They all refer to the same mathematical differential ring
 * hence must order the same set of symbols.
 * It actually associates an index to each ordering and permits
 * to interpret the table @code{number} of the variables.
 *
 * The field @code{ord_stack} implements a stack of indices
 * in @code{ords}. Its top element is the @dfn{current ordering}.
 *
 * The field @code{pars} contains the description of the parameters
 * of the differential ring i.e. dependent symbols some derivatives
 * of which simplifying to zero.
 *
 * Many functions of the @code{bav} library hold identifiers
 * starting with @code{bav_R}. These are low level functions,
 * performing critical operations of the @code{bav_global.R}
 * structure.
 */

struct bav_differential_ring
{
// true if the differential ring is empty
  bool empty;
// the table of all ident of symbols, radicals of range indexed strings
  struct ba0_tableof_string strs;
// the table of the range indexed strings
  struct ba0_tableof_range_indexed_group rigs;
// the table of symbols
  struct bav_tableof_symbol syms;
// the table of variables
  struct bav_tableof_variable vars;
// maps strings to strings in strs
  struct ba0_dictionary_string dict_str_to_str;
// maps strings to variables in vars
  struct ba0_dictionary_string dict_str_to_var;
// maps strings (radicals) to range indexed strings in rigs
  struct ba0_dictionary_string dict_str_to_rig;
// the indices in vars of the derivations 
  struct ba0_tableof_int_p ders;
// the indices in vars of the temporary variables 
  struct ba0_tableof_int_p tmps;
// tmps_in_use[i] is nonzero iff tmps[i] is in use
  struct ba0_tableof_int_p tmps_in_use;
//  -1 or the index in vars of the symbol used for differential operators
  ba0_int_p opra;
// all the defined orderings
  struct bav_tableof_ordering ords;
// a stack of indices in ords
  struct bav_tableof_Iordering ord_stack;
// the parameters
  struct bav_parameters pars;
};


extern BAV_DLL void bav_init_differential_ring (
    struct bav_differential_ring *);

extern BAV_DLL struct bav_differential_ring *bav_new_differential_ring (
    void);

extern BAV_DLL unsigned ba0_int_p bav_sizeof_differential_ring (
    struct bav_differential_ring *,
    enum ba0_garbage_code);

extern BAV_DLL bool bav_is_empty_differential_ring (
    struct bav_differential_ring *);

extern BAV_DLL void bav_R_set_differential_ring (
    struct bav_differential_ring *,
    struct bav_differential_ring *);

extern BAV_DLL void bav_R_create_differential_ring (
    struct ba0_tableof_string *,
    struct bav_tableof_block *,
    struct bav_block *);

extern BAV_DLL bav_Iordering bav_R_new_ranking (
    struct ba0_tableof_string *,
    struct bav_tableof_block *,
    struct bav_block *);

extern BAV_DLL void bav_R_add_block_to_all_orderings (
    struct bav_block *,
    ba0_int_p);

extern BAV_DLL bool bav_R_ambiguous_symbols (
    void);

extern BAV_DLL bav_Iordering bav_R_copy_ordering (
    bav_Iordering);

extern BAV_DLL struct bav_variable *bav_R_new_symbol_and_variable (
    char *,
    enum bav_typeof_symbol,
    ba0_int_p,
    struct ba0_tableof_int_p *);

extern BAV_DLL struct bav_variable *bav_R_new_temporary_variable (
    void);

extern BAV_DLL void bav_R_free_temporary_variable (
    struct bav_variable *);

extern BAV_DLL void bav_R_set_maximal_variable (
    struct bav_variable *);

extern BAV_DLL void bav_R_set_minimal_variable (
    struct bav_variable *);

extern BAV_DLL void bav_R_swap_ordering (
    bav_Iordering,
    bav_Iordering);

extern BAV_DLL void bav_R_free_ordering (
    bav_Iordering);

extern BAV_DLL void bav_R_restore_ords_size (
    ba0_int_p);

extern BAV_DLL void bav_push_ordering (
    bav_Iordering);

extern BAV_DLL void bav_pull_ordering (
    void);

extern BAV_DLL bav_Iordering bav_current_ordering (
    void);

extern BAV_DLL bav_Inumber bav_variable_number (
    struct bav_variable *);

extern BAV_DLL struct bav_variable *bav_smallest_greater_variable (
    struct bav_variable *);

extern BAV_DLL bav_Inumber bav_R_symbol_block_number (
    struct bav_symbol *,
    ba0_int_p *);

extern BAV_DLL struct bav_variable *bav_R_new_derivative (
    struct bav_variable *,
    struct bav_symbol *);

extern BAV_DLL struct bav_variable *bav_symbol_to_variable (
    struct bav_symbol *);

extern BAV_DLL struct bav_symbol *bav_R_string_to_existing_symbol (
    char *);

extern BAV_DLL struct bav_symbol *bav_R_string_to_existing_derivation (
    char *);

extern BAV_DLL struct bav_variable *bav_R_string_to_existing_variable (
    char *);

extern BAV_DLL struct bav_variable *bav_derivation_index_to_derivation (
    ba0_int_p);

END_C_DECLS
#endif /* !BAV_DIFFERENTIAL_RING_H */
#if !defined (BAV_POINT_H)
#   define BAV_POINT_H

/* #   include "bav_common.h" */

BEGIN_C_DECLS

extern BAV_DLL bool bav_is_differentially_ambiguous_point (
    struct ba0_point *);

extern BAV_DLL void bav_delete_independent_values_point (
    struct ba0_point *,
    struct ba0_point *);

END_C_DECLS
#endif /* !BAV_POINT */
#if !defined (BAV_POINT_INT_P_H)
#   define BAV_POINT_INT_P_H 1

/* #   include "bav_common.h" */
/* #   include "bav_variable.h" */

BEGIN_C_DECLS

/*
 * texinfo: bav_value_int_p
 * This data type permits to associate a @code{ba0_int_p} value
 * to a variable. It can be parsed and printed using the
 * format @code{%value(%d)}.
 */

struct bav_value_int_p
{
  struct bav_variable *var;
  ba0_int_p value;
};


/*
 * texinfo: bav_point_int_p
 * This data type is a particular case of the type @code{struct ba0_point}.
 * It permits to associate @code{ba0_int_p} values to
 * many different variables. 
 * Many functions assume the @code{tab} field to be sorted
 * (see @code{ba0_sort_point}).
 * They can be parsed using @code{ba0_scanf/%point(%d)} and
 * printed by @code{ba0_printf/%point(%d)}.
 */

struct bav_point_int_p
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bav_value_int_p **tab;
};


END_C_DECLS
#endif /* !BAV_POINT_INT_P_H */
#if !defined (BAV_POINT_INTERVAL_MPQ_H)
#   define BAV_POINT_INTERVAL_MPQ_H 1

/* #   include "bav_common.h" */
/* #   include "bav_variable.h" */

BEGIN_C_DECLS

/*
 * texinfo: bav_value_interval_mpq
 * This data type associates an interval with @code{mpq_t} ends
 * to a variable. It can be parsed and printed using the
 * format @code{%value(%qi)}.
 */

struct bav_value_interval_mpq
{
  struct bav_variable *var;
  struct ba0_interval_mpq *value;
};


/* In the next one, all variables might be equal */

struct bav_tableof_value_interval_mpq
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bav_value_interval_mpq **tab;
};



/*
 * texinfo: bav_point_interval_mpq
 * This data type is a particular case of the type @code{struct ba0_point}.
 * It permits to associate @code{ba0_interval_mpq} values to
 * many different variables.
 * They can be parsed by @code{ba0_scanf/%point(%qi)} and printed
 * by @code{ba0_printf/%point(%qi)}.
 * Many functions assume the @code{tab} field to be sorted
 * (see @code{ba0_sort_point}).
 */

struct bav_point_interval_mpq
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bav_value_interval_mpq **tab;
};


struct bav_tableof_point_interval_mpq
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bav_point_interval_mpq **tab;
};


extern BAV_DLL struct bav_value_interval_mpq *bav_new_value_interval_mpq (
    void);

extern BAV_DLL void bav_set_value_interval_mpq (
    struct bav_value_interval_mpq *,
    struct bav_value_interval_mpq *);

extern BAV_DLL void bav_init_point_interval_mpq (
    struct bav_point_interval_mpq *);

extern BAV_DLL struct bav_point_interval_mpq *bav_new_point_interval_mpq (
    void);

extern BAV_DLL void bav_realloc_point_interval_mpq (
    struct bav_point_interval_mpq *,
    ba0_int_p);

extern BAV_DLL void bav_set_point_interval_mpq (
    struct bav_point_interval_mpq *,
    struct bav_point_interval_mpq *);

extern BAV_DLL void bav_set_coord_point_interval_mpq (
    struct bav_point_interval_mpq *,
    struct bav_variable *,
    struct ba0_interval_mpq *);

extern BAV_DLL void bav_intersect_coord_point_interval_mpq (
    struct bav_point_interval_mpq *,
    struct bav_point_interval_mpq *,
    struct bav_variable *,
    struct ba0_interval_mpq *);

extern BAV_DLL void bav_intersect_point_interval_mpq (
    struct bav_point_interval_mpq *,
    struct bav_point_interval_mpq *,
    struct bav_point_interval_mpq *);

extern BAV_DLL bool bav_is_empty_point_interval_mpq (
    struct bav_point_interval_mpq *);

extern BAV_DLL void bav_bisect_point_interval_mpq (
    struct bav_tableof_point_interval_mpq *,
    struct bav_point_interval_mpq *,
    ba0_int_p);

extern BAV_DLL void bav_set_tableof_point_interval_mpq (
    struct bav_tableof_point_interval_mpq *,
    struct bav_tableof_point_interval_mpq *);

END_C_DECLS
#endif /* !BAV_POINT_INTERVAL_MPQ_H */
#if !defined (BAV_RANK_H)
#   define BAV_RANK_H 1

/* #   include "bav_common.h" */
/* #   include "bav_variable.h" */

BEGIN_C_DECLS

/*
 * texinfo: bav_rank
 * A @dfn{rank} is a variable raised to some degree.
 * Some special ranks are also defined such as the
 * rank of zero and the one of nonzero constants.
 * The rank of zero is encoded by 
 * (@code{BAV_NOT_A_VARIABLE}, @math{-1}).
 * The rank of nonzero constants is encoded by a field @code{deg}
 * equal to @math{0} (the field @code{var} is unspecified).
 */

struct bav_rank
{
// possibly BAV_NOT_A_VARIABLE
  struct bav_variable *var;
// possibly zero or a negative integer
  bav_Idegree deg;
};


extern BAV_DLL void bav_init_rank (
    struct bav_rank *);

extern BAV_DLL struct bav_rank *bav_new_rank (
    void);

extern BAV_DLL bool bav_is_zero_rank (
    struct bav_rank *);

extern BAV_DLL bool bav_is_constant_rank (
    struct bav_rank *);

extern BAV_DLL bool bav_lt_rank (
    struct bav_rank *,
    struct bav_rank *);

extern BAV_DLL bool bav_gt_rank (
    struct bav_rank *,
    struct bav_rank *);

extern BAV_DLL bool bav_equal_rank (
    struct bav_rank *,
    struct bav_rank *);

extern BAV_DLL int bav_compare_rank (
    const void *,
    const void *);

extern BAV_DLL struct bav_rank bav_zero_rank (
    void);

extern BAV_DLL struct bav_rank bav_constant_rank (
    void);

extern BAV_DLL struct bav_rank bav_constant_rank2 (
    struct bav_variable *);

extern BAV_DLL void bav_set_settings_rank (
    ba0_printf_function *);

extern BAV_DLL void bav_get_settings_rank (
    ba0_printf_function **);

extern BAV_DLL ba0_scanf_function bav_scanf_rank;

extern BAV_DLL ba0_printf_function bav_printf_rank;

extern BAV_DLL ba0_printf_function bav_printf_default_rank;

extern BAV_DLL ba0_printf_function bav_printf_stars_rank;

extern BAV_DLL ba0_printf_function bav_printf_list_rank;

struct bav_tableof_rank
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bav_rank **tab;
};


END_C_DECLS
#endif /* !BAV_RANK_H */
#if !defined (BAV_TERM_H)
#   define BAV_TERM_H 1

/* #   include "bav_common.h" */
/* #   include "bav_rank.h" */
/* #   include "bav_point_int_p.h" */
/* #   include "bav_parameter.h" */
/* #   include "bav_point_interval_mpq.h" */

BEGIN_C_DECLS

/*
 * texinfo: bav_term
 * A @dfn{term} is a product of ranks (the ranks of zero and of nonzero
 * constants are forbidden) sorted by decreasing order with respect to the
 * current ordering.
 * The empty product encodes the term @math{1}.
 * The leading rank of a nonempty product is the leading rank of the term.
 */

struct bav_term
{
// number of entries allocated to rg
  ba0_int_p alloc;
// number of entries used in rg
  ba0_int_p size;
// the array of ranks, by decreasing order with respect to the current ordering
  struct bav_rank *rg;
};

struct bav_listof_term
{
  struct bav_term *value;
  struct bav_listof_term *next;
};

struct bav_tableof_term
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bav_term **tab;
};

extern BAV_DLL void bav_realloc_term (
    struct bav_term *,
    ba0_int_p);

extern BAV_DLL void bav_init_term (
    struct bav_term *);

extern BAV_DLL struct bav_term *bav_new_term (
    void);

extern BAV_DLL void bav_set_term_one (
    struct bav_term *);

extern BAV_DLL void bav_set_term_variable (
    struct bav_term *,
    struct bav_variable *,
    bav_Idegree);

extern BAV_DLL void bav_set_term_rank (
    struct bav_term *,
    struct bav_rank *);

extern BAV_DLL void bav_set_term (
    struct bav_term *,
    struct bav_term *);

extern BAV_DLL void bav_set_tableof_term (
    struct bav_tableof_term *,
    struct bav_tableof_term *);

extern BAV_DLL void bav_lcm_tableof_term (
    struct bav_tableof_term *,
    struct bav_tableof_term *,
    struct bav_tableof_term *);

extern BAV_DLL void bav_shift_term (
    struct bav_term *,
    struct bav_term *);

extern BAV_DLL void bav_strip_term (
    struct bav_term *,
    struct bav_term *,
    bav_Inumber);

extern BAV_DLL bool bav_is_one_term (
    struct bav_term *);

extern BAV_DLL struct bav_variable *bav_leader_term (
    struct bav_term *);

extern BAV_DLL bav_Idegree bav_leading_degree_term (
    struct bav_term *);

extern BAV_DLL bav_Idegree bav_total_degree_term (
    struct bav_term *);

extern BAV_DLL bav_Idegree bav_degree_term (
    struct bav_term *,
    struct bav_variable *);

extern BAV_DLL bav_Iorder bav_total_order_term (
    struct bav_term *);

extern BAV_DLL bav_Idegree bav_maximal_degree_term (
    struct bav_term *);

extern BAV_DLL struct bav_rank bav_leading_rank_term (
    struct bav_term *);

extern BAV_DLL bool bav_disjoint_term (
    struct bav_term *,
    struct bav_term *);

extern BAV_DLL bool bav_equal_term (
    struct bav_term *,
    struct bav_term *);

extern BAV_DLL bool bav_gt_term (
    struct bav_term *,
    struct bav_term *);

extern BAV_DLL bool bav_lt_term (
    struct bav_term *,
    struct bav_term *);

extern BAV_DLL void bav_sort_term (
    struct bav_term *);

extern BAV_DLL void bav_sort_tableof_term (
    struct bav_tableof_term *);

extern BAV_DLL void bav_lcm_term (
    struct bav_term *,
    struct bav_term *,
    struct bav_term *);

extern BAV_DLL void bav_gcd_term (
    struct bav_term *,
    struct bav_term *,
    struct bav_term *);

extern BAV_DLL void bav_mul_term (
    struct bav_term *,
    struct bav_term *,
    struct bav_term *);

extern BAV_DLL void bav_mul_term_rank (
    struct bav_term *,
    struct bav_term *,
    struct bav_rank *);

extern BAV_DLL void bav_mul_term_variable (
    struct bav_term *,
    struct bav_term *,
    struct bav_variable *,
    bav_Idegree);

extern BAV_DLL void bav_pow_term (
    struct bav_term *,
    struct bav_term *,
    bav_Idegree);

extern BAV_DLL void bav_exquo_term (
    struct bav_term *,
    struct bav_term *,
    struct bav_term *);

extern BAV_DLL void bav_exquo_term_variable (
    struct bav_term *,
    struct bav_term *,
    struct bav_variable *,
    bav_Idegree);

extern BAV_DLL bool bav_is_factor_term (
    struct bav_term *,
    struct bav_term *,
    struct bav_term *);

extern BAV_DLL void bav_diff_term (
    struct bav_term *,
    struct bav_term *,
    struct bav_symbol *);

extern BAV_DLL void bav_set_term_tableof_variable (
    struct bav_term *,
    struct bav_tableof_variable *,
    struct ba0_tableof_int_p *);

extern BAV_DLL void bav_term_at_point_int_p (
    ba0_mpz_t,
    struct bav_term *,
    struct bav_point_int_p *);

extern BAV_DLL void bav_term_at_point_interval_mpq (
    struct ba0_interval_mpq *,
    struct bav_term *,
    struct bav_point_interval_mpq *);

extern BAV_DLL ba0_garbage1_function bav_garbage1_term;

extern BAV_DLL ba0_garbage2_function bav_garbage2_term;

extern BAV_DLL ba0_scanf_function bav_scanf_term;

extern BAV_DLL ba0_printf_function bav_printf_term;

extern BAV_DLL ba0_copy_function bav_copy_term;

struct bav_differential_ring;

extern BAV_DLL void bav_switch_ring_term (
    struct bav_term *,
    struct bav_differential_ring *);

extern BAV_DLL bool bav_depends_on_zero_derivatives_of_parameter_term (
    struct bav_term *);

END_C_DECLS
#endif /* !BAV_TERM_H */
#if !defined (BAV_TERM_ORDERING_H)
#   define BAV_TERM_ORDERING_H 1

/* #   include "bav_term.h" */

BEGIN_C_DECLS

extern BAV_DLL enum ba0_compare_code bav_compare_term (
    struct bav_term *,
    struct bav_term *);

extern BAV_DLL enum ba0_compare_code bav_compare_stripped_term (
    struct bav_term *,
    struct bav_term *,
    bav_Inumber);

extern BAV_DLL void bav_set_term_ordering (
    char *);

END_C_DECLS
#endif /* !BAV_TERM_ORDERING_H */
#if !defined (BAV_GLOBAL_H)
#   define BAV_GLOBAL_H 1

/* #   include "bav_common.h" */
/* #   include "bav_differential_ring.h" */
/* #   include "bav_term.h" */


BEGIN_C_DECLS

struct bav_global
{
  struct
  {
/* 
 * Receives the faulty string when an unknown variable/symbol is parsed
 */
    char unknown[BA0_BUFSIZE];
  } common;
  struct bav_differential_ring R;
  struct
  {
/*
 * Flags indicating which input notation was used
 */
    ba0_int_p notations;
/* 
 * "diff" or "Diff" to display derivatives
 */
    char *diff_string;
  } variable;
  struct
  {
/* 
 * Comparison functions w.r.t. term orderings
 */
    enum ba0_compare_code (
        *compare) (
        struct bav_term *,
        struct bav_term *);
    enum ba0_compare_code (
        *compare_stripped) (
        struct bav_term *,
        struct bav_term *,
        bav_Inumber);
  } term_ordering;
};

struct bav_initialized_global
{
  struct
  {
/* 
 * Function called when an unknown symbol/variable/parameter is parsed.
 * Default bav_unknown_default
 */
    ba0_indexed_string_function *unknown;
  } common;
  struct
  {
/* 
 * Functions pointers for customizing symbol parsing and printing
 */
    ba0_scanf_function *scanf;
    ba0_printf_function *printf;
/*
 * If IndexedBase_PFE is not (char *)0, the radical z of every symbol
 * z[something] which fits some range indexed group is printed 
 * IndexedBase_PFE('z') leading to a symbol IndexedBase_PFE('z')[something].
 * This mechanism prevents some evaluation failures in Python. Default 0
 */
    char *IndexedBase_PFE;
  } symbol;
  struct
  {
/*
 * If Function_PFE is not (char *)0, every parameter p with nonempty
 * dependencies is printed Function_PFE('p')(dependencies).
 * This mechanism prevents some evaluation failures in Python. Default 0.
 */
    char *Function_PFE;
  } parameter;
  struct
  {
/* 
 * Functions pointers for customizing variable parsing and printing
 */
    ba0_scanf_function *scanf;
    ba0_printf_function *printf;
/*
 * The strings which stand for no derivation in the jet0 notation
 */
    char *jet0_input_string;
    char *jet0_output_string;
/* 
 * The prefix of temporary variables
 */
    char *temp_string;
  } variable;
  struct
  {
/* 
 * Function pointer for customizing the way ranks are printed.
 */
    ba0_printf_function *printf;
  } rank;
  struct
  {
/* 
 * The string for displaying orderings
 */
    char *string;
  } ordering;
};

extern BAV_DLL struct bav_global bav_global;

extern BAV_DLL struct bav_initialized_global bav_initialized_global;

/*
 * texinfo: bav_PFE_settings
 * This data structure is used to store copies of the settings variables
 * contained in the fields of @code{bav_initialized_global} which
 * contain @code{PFE} variables.
 */

struct bav_PFE_settings
{
  struct ba0_PFE_settings ba0;
  ba0_scanf_function *scanf;
  ba0_printf_function *printf;
  char *IndexedBase_PFE;
  char *Function_PFE;
};

END_C_DECLS
#endif /* !BAV_GLOBAL_H */
