#if !defined (BAV_PARAMETER_H)
#   define BAV_PARAMETER_H 1

#   include "bav_symbol.h"

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
