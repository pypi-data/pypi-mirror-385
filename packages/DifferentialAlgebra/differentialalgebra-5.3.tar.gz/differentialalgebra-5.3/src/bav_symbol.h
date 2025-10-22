#if !defined (BAV_SYMBOL_H)
#   define BAV_SYMBOL_H 1

#   include "bav_common.h"

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
