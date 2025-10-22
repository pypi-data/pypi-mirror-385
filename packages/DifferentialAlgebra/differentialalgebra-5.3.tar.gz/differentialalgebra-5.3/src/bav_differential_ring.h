#if !defined (BAV_DIFFERENTIAL_RING_H)
#   define BAV_DIFFERENTIAL_RING_H 1

#   include "bav_common.h"
#   include "bav_block.h"
#   include "bav_symbol.h"
#   include "bav_variable.h"
#   include "bav_operator.h"
#   include "bav_parameters.h"
#   include "bav_ordering.h"

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
