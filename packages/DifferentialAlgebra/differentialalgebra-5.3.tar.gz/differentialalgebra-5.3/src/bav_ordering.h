#if !defined (BAV_ORDERING_H)
#   define BAV_ORDERING_H 1

#   include "bav_common.h"
#   include "bav_symbol.h"
#   include "bav_block.h"
#   include "bav_variable.h"
#   include "bav_operator.h"
#   include "bav_typed_ident.h"

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
