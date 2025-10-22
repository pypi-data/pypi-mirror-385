#if !defined (BAZ_PROLONGATION_PATTERN_H)
#   define BAZ_PROLONGATION_PATTERN_H

#   include "baz_common.h"

BEGIN_C_DECLS

/*
 * texinfo: baz_prolongation_pattern
 * This data type implements patterns for prolongating points.
 * Here is an example of pattern:
 * @verbatim
 * R       = DifferentialRing (derivations = [x], blocks = [y,z])
 * pattern = { y[(x,k)] : 'y[k]/factorial(k)' }
 * @end verbatim
 * Every derivative of @var{y} matches the pattern.
 * The pattern associates @math{y_k / k!} to the @var{k}th derivative
 * of @var{y} for every nonnegative integer @var{k}.
 *
 * The field @code{dict} 
 * only aims at speeding up the evaluation of replacement values.
 * It is provided to the substitution dictionary of the 
 * lexical analyzer.
 */

struct baz_prolongation_pattern
{
// The dependent variables (such as "y") matching the pattern
  struct bav_tableof_symbol deps;
// The identifiers denoting the orders of derivation (such as "k")
// The table follows the order provided by bav_global.R.ders
  struct ba0_tableof_string idents;
// The replacement values (such as "y[k]/factorial(k)")
  struct ba0_tableof_string exprs;
// A dictionary which maps identifiers (such as "k") to the corresponding 
//      entry in idents (used by the substitution dictionary)
  struct ba0_dictionary_string dict;
};

extern BAZ_DLL void baz_set_settings_prolongation_pattern (
    char *);

extern BAZ_DLL void baz_get_settings_prolongation_pattern (
    char **);

extern BAZ_DLL void baz_init_prolongation_pattern (
    struct baz_prolongation_pattern *);

extern BAZ_DLL void baz_reset_prolongation_pattern (
    struct baz_prolongation_pattern *);

extern BAZ_DLL struct baz_prolongation_pattern *baz_new_prolongation_pattern (
    void);

extern BAZ_DLL void baz_set_prolongation_pattern (
    struct baz_prolongation_pattern *,
    struct baz_prolongation_pattern *);

extern BAZ_DLL void baz_variable_mapping_prolongation_pattern (
    struct bav_tableof_variable *,
    struct bav_tableof_variable *,
    struct baz_prolongation_pattern *);

extern BAZ_DLL unsigned ba0_int_p baz_sizeof_prolongation_pattern (
    struct baz_prolongation_pattern *,
    enum ba0_garbage_code);

extern BAZ_DLL void baz_switch_ring_prolongation_pattern (
    struct baz_prolongation_pattern *,
    struct bav_differential_ring *);

extern BAZ_DLL ba0_scanf_function baz_scanf_prolongation_pattern;

extern BAZ_DLL ba0_printf_function baz_printf_prolongation_pattern;

END_C_DECLS
#endif /* !BAZ_PROLONGATION_PATTERN_H */
