#if !defined (BAD_COMMON_H)
#   define BAD_COMMON_H 1

#   include <baz.h>

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
 * The flag BAD_BLAD_BUILDING must thus be set in the Makefile and passed
 * to the C preprocessor at BAD building time. Do not set it when using BAD.
 *
 * When compiling static libraries under Windows, set BA0_STATIC.
 */

#   if defined (_MSC_VER) && ! defined (BA0_STATIC)
#      if defined (BLAD_BUILDING) || defined (BAD_BLAD_BUILDING)
#         define BAD_DLL  __declspec(dllexport)
#      else
#         define BAD_DLL  __declspec(dllimport)
#      endif
#   else
#      define BAD_DLL
#   endif

/* #   include "bad_mesgerr.h" */

#   define BAD_NOT_A_NUMBER -1

BEGIN_C_DECLS
/* 
 * Restart functions
 */
extern BAD_DLL void bad_reset_all_settings (
    void);

extern BAD_DLL void bad_restart (
    ba0_int_p,
    ba0_int_p);

extern BAD_DLL void bad_terminate (
    enum ba0_restart_level);


END_C_DECLS
#endif /* !BAD_COMMON_H */
#if !defined (BAD_MESGERR_H)
#   define BAD_MESGERR_H 1

/* #   include "bad_common.h" */

BEGIN_C_DECLS

extern BAD_DLL char BAD_EXREDZ[];

extern BAD_DLL char BAD_EXNRDZ[];

extern BAD_DLL char BAD_EXRNUL[];

extern BAD_DLL char BAD_EXRDDZ[];

extern BAD_DLL char BAD_EXRCNC[];

extern BAD_DLL char BAD_EXQUNC[];

extern BAD_DLL char BAD_ERRCRI[];

extern BAD_DLL char BAD_ERRDEL[];

extern BAD_DLL char BAD_ERRNAC[];

extern BAD_DLL char BAD_ERRIAC[];

extern BAD_DLL char BAD_ERRCRC[];

extern BAD_DLL char BAD_ERRNRC[];

extern BAD_DLL char BAD_ERRIRC[];

extern BAD_DLL char BAD_ERRMPT[];

extern BAD_DLL char BAD_ERRIBF[];

extern BAD_DLL char BAD_ERRBAS[];

extern BAD_DLL char BAD_ERRBFD[];

extern BAD_DLL char BAD_ERRIND[];

extern BAD_DLL char BAD_ERRIPT[];

extern BAD_DLL char BAD_ERRSFV[];

END_C_DECLS
#endif /* !BAD_MESGERR_H */
#if !defined (BAD_STATS_H)
#   define BAD_STATS_H 1

/* #   include "bad_common.h" */

BEGIN_C_DECLS

extern BAD_DLL void bad_init_stats (
    void);

extern BAD_DLL ba0_printf_function bad_printf_stats;

END_C_DECLS
#endif /* ! BAD_STATS_H */
#if !defined (BAD_ATTCHAIN_H)
#   define BAD_ATTCHAIN_H 1

/* #   include "bad_common.h" */

BEGIN_C_DECLS

/*
 * texinfo: bad_property_attchain
 * This data type permits to describe the properties of regular chains.
 * It is a subtype of @code{bad_attchain}
 */

enum bad_property_attchain
{
// the ideal defined by the chain is differential
  bad_differential_ideal_property,
// the ideal defined by the chain is prime
  bad_prime_ideal_property,
// the chain is coherent (only relevant in the partial differential case)
  bad_coherence_property,
// the chain is autoreduced
  bad_autoreduced_property,
// the chain is squarefree
  bad_squarefree_property,
// the chain elements, viewed as univariate polynomials in their
// leaders, are primitive
  bad_primitive_property,
// the chain is strongly normalized
  bad_normalized_property
};

/*
 * texinfo: bad_attchain
 * This data type is a subtype of @code{bad_regchain}.
 * It permits to define the @dfn{attributes} associated to a regular chain.
 */

struct bad_attchain
{
// the ordering with respect to which the regular chain is defined
  bav_Iordering ordering;
// the properties bitwise encoded over an integer
  ba0_int_p property;
};


extern BAD_DLL void bad_init_attchain (
    struct bad_attchain *);

extern BAD_DLL void bad_reset_attchain (
    struct bad_attchain *);

extern BAD_DLL void bad_set_attchain (
    struct bad_attchain *,
    struct bad_attchain *);

extern BAD_DLL void bad_intersect_attchain (
    struct bad_attchain *,
    struct bad_attchain *);

extern BAD_DLL void bad_set_properties_attchain (
    struct bad_attchain *,
    struct ba0_tableof_string *);

extern BAD_DLL void bad_set_automatic_properties_attchain (
    struct bad_attchain *);

extern BAD_DLL void bad_set_properties_attchain (
    struct bad_attchain *,
    struct ba0_tableof_string *);

extern BAD_DLL void bad_set_property_attchain (
    struct bad_attchain *,
    enum bad_property_attchain);

extern BAD_DLL void bad_clear_property_attchain (
    struct bad_attchain *,
    enum bad_property_attchain);

extern BAD_DLL bool bad_is_a_property_attchain (
    char *,
    enum bad_property_attchain *);

extern BAD_DLL bool bad_has_property_attchain (
    struct bad_attchain *,
    enum bad_property_attchain);

extern BAD_DLL bool bad_defines_a_differential_ideal_attchain (
    struct bad_attchain *);

extern BAD_DLL bool bad_defines_a_prime_ideal_attchain (
    struct bad_attchain *);

extern BAD_DLL void bad_properties_attchain (
    struct ba0_tableof_string *,
    struct bad_attchain *);

extern BAD_DLL bool bad_equal_attchain (
    struct bad_attchain *,
    struct bad_attchain *);

END_C_DECLS
#endif /* !BAD_ATTCHAIN_H */
#if !defined (BAD_REGCHAIN_H)
#   define BAD_REGCHAIN_H 1

/* #   include "bad_common.h" */
/* #   include "bad_attchain.h" */

BEGIN_C_DECLS

struct bad_base_field;

/*
 * texinfo: bad_regchain
 * This data type implements regular chains.
 * Mathematically, a regular chain @math{A} defines an ideal which
 * is either @math{(A):I_A^\infty} in the nondifferential case, or
 * @math{[A]:H_A^\infty} in the differential case.
 *
 * The field @code{number} is used to associate a number to
 * the regular chain, in order to identify it precisely in
 * the @emph{splitting trees} generated by elimination algorithms.
 * If the regular chain is part of a @emph{quadruple}, the number
 * is used also to identify the quadruple.
 *
 * The field @code{attrib} contains the @emph{attributes} of
 * the regular chain: the @emph{ordering} with respect to which
 * the chain is defined plus some properties.
 *
 * The field @code{decision_system} contains the differential
 * polynomials, sorted increasingly with respect to the chain ordering.
 */

struct bad_regchain
{
// the number of the regular chain in a splitting tree
  ba0_int_p number;
// the attributes of the regular chain - including the ordering
  struct bad_attchain attrib;
// the polynomial set, sorted increasingly with respect to the chain ordering
  struct bap_tableof_polynom_mpz decision_system;
};

struct bad_tableof_regchain
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bad_regchain **tab;
};

extern BAD_DLL void bad_init_regchain (
    struct bad_regchain *);

extern BAD_DLL void bad_reset_regchain (
    struct bad_regchain *);

extern BAD_DLL struct bad_regchain *bad_new_regchain (
    void);

extern BAD_DLL void bad_realloc_regchain (
    struct bad_regchain *,
    ba0_int_p);

extern BAD_DLL void bad_set_regchain (
    struct bad_regchain *,
    struct bad_regchain *);

extern BAD_DLL void bad_extend_regchain (
    struct bad_regchain *,
    struct bad_regchain *);

extern BAD_DLL ba0_int_p bad_product_of_leading_degrees_regchain (
    struct bad_regchain *);

extern BAD_DLL void bad_set_regchain_tableof_polynom_mpz (
    struct bad_regchain *,
    struct bap_tableof_polynom_mpz *,
    struct ba0_tableof_string *,
    bool);

extern BAD_DLL void bad_set_regchain_tableof_ratfrac_mpz (
    struct bad_regchain *,
    struct baz_tableof_ratfrac *,
    struct ba0_tableof_string *,
    bool);

extern BAD_DLL void bad_fast_primality_test_regchain (
    struct bad_regchain *);

extern BAD_DLL void bad_set_number_regchain (
    struct bad_regchain *,
    ba0_int_p);

extern BAD_DLL ba0_int_p bad_get_number_regchain (
    struct bad_regchain *);

extern BAD_DLL void bad_set_property_regchain (
    struct bad_regchain *,
    enum bad_property_attchain);

extern BAD_DLL void bad_clear_property_regchain (
    struct bad_regchain *,
    enum bad_property_attchain);

extern BAD_DLL void bad_set_properties_regchain (
    struct bad_regchain *,
    struct ba0_tableof_string *);

extern BAD_DLL void bad_set_automatic_properties_regchain (
    struct bad_regchain *);

extern BAD_DLL bool bad_has_property_regchain (
    struct bad_regchain *,
    enum bad_property_attchain);

extern BAD_DLL void bad_properties_regchain (
    struct ba0_tableof_string *,
    struct bad_regchain *);

extern BAD_DLL bool bad_defines_a_differential_ideal_regchain (
    struct bad_regchain *);

extern BAD_DLL bool bad_defines_a_prime_ideal_regchain (
    struct bad_regchain *);

extern BAD_DLL void bad_inequations_regchain (
    struct bap_tableof_polynom_mpz *,
    struct bad_regchain *);

extern BAD_DLL void bad_sort_regchain (
    struct bad_regchain *,
    struct bad_regchain *);

extern BAD_DLL bav_Iordering bad_ordering_eliminating_leaders_of_regchain (
    struct bad_regchain *);

extern BAD_DLL bool bad_is_rank_of_regchain (
    struct bav_rank *,
    struct bad_regchain *,
    ba0_int_p *);

extern BAD_DLL bool bad_is_leader_of_regchain (
    struct bav_variable *,
    struct bad_regchain *,
    ba0_int_p *);

extern BAD_DLL bool bad_depends_on_leader_of_regchain (
    struct bap_polynom_mpz *,
    struct bad_regchain *);

extern BAD_DLL void bad_leaders_of_regchain (
    struct bav_tableof_variable *,
    struct bad_regchain *);

extern BAD_DLL bool bad_is_derivative_of_leader_of_regchain (
    struct bav_variable *,
    struct bad_regchain *,
    ba0_int_p *);

extern BAD_DLL void bad_mark_indets_regchain (
    struct bav_dictionary_variable *,
    struct bav_tableof_variable *,
    struct bad_regchain *);

extern BAD_DLL bool bad_is_solved_regchain (
    struct bad_regchain *);

extern BAD_DLL bool bad_is_a_compatible_regchain (
    struct bad_regchain *,
    struct bad_attchain *);

extern BAD_DLL bool bad_is_orthonomic_regchain (
    struct bad_regchain *,
    struct bad_base_field *);

extern BAD_DLL bool bad_is_explicit_regchain (
    struct bad_regchain *);

extern BAD_DLL bool bad_is_zero_regchain (
    struct bad_regchain *);

extern BAD_DLL ba0_int_p bad_codimension_regchain (
    struct bad_regchain *,
    struct bad_base_field *);

extern BAD_DLL unsigned ba0_int_p bad_sizeof_regchain (
    struct bad_regchain *,
    enum ba0_garbage_code);

extern BAD_DLL void bad_switch_ring_regchain (
    struct bad_regchain *,
    struct bav_differential_ring *);

extern BAD_DLL ba0_scanf_function bad_scanf_regchain;

extern BAD_DLL ba0_scanf_function bad_scanf_pretend_regchain;

extern BAD_DLL ba0_printf_function bad_printf_regchain;

extern BAD_DLL ba0_printf_function bad_printf_regchain_equations;

extern BAD_DLL ba0_garbage1_function bad_garbage1_inline_regchain;

extern BAD_DLL ba0_garbage2_function bad_garbage2_inline_regchain;

extern BAD_DLL ba0_garbage1_function bad_garbage1_regchain;

extern BAD_DLL ba0_garbage2_function bad_garbage2_regchain;

extern BAD_DLL ba0_copy_function bad_copy_regchain;

END_C_DECLS
#endif /* !BAD_REGCHAIN_H */
#if !defined (BAD_SPLITTING_CONTROL_H)
#   define BAD_SPLITTING_CONTROL_H 1

/* #   include "bad_common.h" */
/* #   include "bad_regchain.h" */

BEGIN_C_DECLS

/*
 * texinfo: bad_typeof_dimension_lower_bound
 * This data type permits to specify to differential elimination
 * algorithms the type of dimension lower bound to be applied.
 * Such a lower bound permits to cut any branch of the splitting
 * tree leading to regular chains of differential dimension
 * strictly less than the number of input equations.
 * Note that such a strategy is proved in the algebraic case
 * and in the case of a single differential equation.
 * The other cases are conjectural.
 */

enum bad_typeof_dimension_lower_bound
{
// do not take into account any dimension lower bound
  bad_no_dimension_lower_bound,
// apply it in the case of a non-differential system
  bad_algebraic_dimension_lower_bound,
// apply it in the case of an ordinary differential system
  bad_ode_dimension_lower_bound,
// apply it in the case of a partial differential system
  bad_pde_dimension_lower_bound
};

/* 
 * texinfo: bad_splitting_control
 * This data type permits to specify a splitting control strategy
 * to differential elimination algorithms.
 * 
 * The field @code{first_leaf_only} indicates if the differential
 * elimination process must stop at the first consistent regular
 * chain obtained. Default value is @code{false}.
 *
 * The field @code{dimlb} indicates the type of dimension argument
 * that should be taken into account. Default value is
 * @code{bad_algebraic_dimension_lower_bound}.
 *
 * The field @code{apply_dimlb_one_eq} indicates if the case of
 * a single input equation should be considered specifically (provided
 * that @code{dimlb} is different from @code{bad_no_dimension_lower_bound}).
 * If set to @code{true}, branches of the splitting tree leading to
 * regular chains of differential dimension strictly less than the 
 * number of input equations (which is then equal to @math{1}) are discarded.
 * Default value is @code{true}.
 *
 * The field @code{DenefLipshitz} indicates if we are performing the
 * differential elimination stage of @code{bas_DenefLipshitz}. If this
 * is the case, the other @code{first_leaf_only} and @code{apply_dimlb_one_eq}
 * are set to @code{false} and @code{dimlb} is set to 
 * @code{bad_no_dimension_lower_bound}. 
 * Moreover, the inequations are not used to discard quadruples before
 * the final algebraic processing.
 */

struct bad_splitting_control
{
// Stop at the first consistent regular chain (if any)
  bool first_leaf_only;
// Should a dimension lower bound be taken into account ?
  enum bad_typeof_dimension_lower_bound dimlb;
// Should the case of a single input equation be handled specifically?
  bool apply_dimlb_one_eq;
// Are we in the differential elimination stage of the DenefLipshitz algorithm?
  bool DenefLipshitz;
};

struct bad_base_field;

extern BAD_DLL void bad_init_splitting_control (
    struct bad_splitting_control *);

extern BAD_DLL struct bad_splitting_control *bad_new_splitting_control (
    void);

extern BAD_DLL void bad_set_splitting_control (
    struct bad_splitting_control *,
    struct bad_splitting_control *);

extern BAD_DLL void bad_set_first_leaf_only_splitting_control (
    struct bad_splitting_control *,
    bool);

extern BAD_DLL void bad_set_dimension_lower_bound_splitting_control (
    struct bad_splitting_control *,
    enum bad_typeof_dimension_lower_bound,
    bool);

extern BAD_DLL bool bad_apply_dimension_lower_bound_splitting_control (
    struct bad_splitting_control *,
    struct bad_regchain *,
    struct bap_listof_polynom_mpz *,
    struct bad_base_field *,
    bool,
    ba0_int_p *);

extern BAD_DLL void bad_set_DenefLipshitz_splitting_control (
    struct bad_splitting_control *,
    bool);

END_C_DECLS
#endif /* !BAD_SPLITTING_CONTROL_H */
#if ! defined (BAD_QUENCH_MAP_H)
#   define BAD_QUENCH_MAP_H 1

/* #   include "bad_regchain.h" */

BEGIN_C_DECLS

/*
 * texinfo: bad_quench_map
 * This data type describes the properties currently satisfied by a 
 * triangular set. It drives the process carried out 
 * by @code{bad_quench_regchain} and is updated after each
 * elementary operation performed over the triangular set.
 * Each field is associated to a property of the triangular set
 * under consideration.
 *
 * A property can be @dfn{inactive} (if not desired by the set)
 * or @dfn{active}. In this second case, it can be satisfied 
 * by some elements of the triangular set or not.
 *
 * Properties are encoded by a table of booleans. 
 * For a given property @code{prop}, 
 * @itemize
 * @item if the field @code{prop.size} is zero
 * then the property is inactive ;
 * @item if it is nonzero then @code{prop.tab[k]} is @code{true}
 * if and only if the property holds for the @var{k}th 
 * element of the triangular set.
 * @end itemize
 */

struct bad_quench_map
{
// the number of elements of the triangular set being processed
  ba0_int_p nb_max_elem;
// the triangular set is partially autoreduced
  struct ba0_tableof_int_p partially_autoreduced;
// the triangular set is a regular chain
  struct ba0_tableof_int_p regular;
// the triangular set elements satisfy bad_primitive_property
  struct ba0_tableof_int_p primitive;
// the triangular set satisfies bad_autoreduced_property
  struct ba0_tableof_int_p autoreduced;
// the triangular set satisfies bad_squarefree_property
  struct ba0_tableof_int_p squarefree;
// the triangular set satisfies bad_normalized_property
  struct ba0_tableof_int_p normalized;
};

extern BAD_DLL void bad_init_quench_map (
    struct bad_quench_map *,
    struct bad_regchain *);

extern BAD_DLL void bad_init_from_complete_quench_map (
    struct bad_quench_map *,
    ba0_int_p,
    struct bad_regchain *);

extern BAD_DLL void bad_set_property_quench_map (
    struct ba0_tableof_int_p *,
    bool);

extern BAD_DLL void bad_set_all_properties_quench_map (
    struct bad_quench_map *,
    bool);

extern BAD_DLL void bad_inactivate_property_quench_map (
    struct ba0_tableof_int_p *);

extern BAD_DLL void bad_fully_reduced_polynom_quench_map (
    struct bad_quench_map *,
    ba0_int_p);

extern BAD_DLL void bad_partially_reduced_polynom_quench_map (
    struct bad_quench_map *,
    ba0_int_p);

extern BAD_DLL void bad_is_an_already_satisfied_property_quench_map (
    struct ba0_tableof_int_p *,
    ba0_int_p);

extern BAD_DLL bool bad_address_property_quench_map (
    struct ba0_tableof_int_p *,
    ba0_int_p);

extern BAD_DLL void bad_primitive_polynom_quench_map (
    struct bad_quench_map *,
    ba0_int_p);

extern BAD_DLL void bad_normalized_polynom_quench_map (
    struct bad_quench_map *,
    ba0_int_p);

extern BAD_DLL void bad_pseudo_divided_polynom_quench_map (
    struct bad_quench_map *,
    ba0_int_p);

extern BAD_DLL void bad_init_set_quench_map (
    struct bad_quench_map *,
    struct bad_quench_map *);

extern BAD_DLL ba0_int_p bad_first_index_quench_map (
    struct bad_quench_map *);

extern BAD_DLL void bad_printf_quench_map (
    struct bad_quench_map *);

END_C_DECLS
#endif /* !BAD_QUENCH_MAP_H */
#if !defined (BAD_QUENCH_REGCHAIN_H)
#   define BAD_QUENCH_REGCHAIN_H 1

/* #   include "bad_common.h" */
/* #   include "bad_attchain.h" */
/* #   include "bad_regchain.h" */
/* #   include "bad_quench_map.h" */

BEGIN_C_DECLS

struct bad_base_field;
struct bad_intersectof_regchain;

extern BAD_DLL void bad_quench_regchain (
    struct bad_regchain *,
    struct bad_quench_map *,
    struct bav_tableof_term *,
    bool *,
    struct bad_regchain *,
    struct bad_base_field *,
    struct bap_polynom_mpz **);

extern BAD_DLL void bad_quench_and_handle_exceptions_regchain (
    struct bad_intersectof_regchain *,
    struct bad_quench_map *,
    struct bav_tableof_term *,
    bool *,
    struct bad_regchain *,
    struct bad_base_field *);

extern BAD_DLL void bad_handle_splitting_exceptions_regchain (
    struct bad_intersectof_regchain *,
    struct bad_quench_map *,
    struct bav_tableof_term *,
    bool *,
    struct bap_polynom_mpz *,
    struct bad_regchain *,
    char *,
    struct bad_base_field *);

END_C_DECLS
#endif /* !BAD_QUENCH_REGCHAIN_H */
#if !defined (BAD_BASE_FIELD_H)
#   define BAD_BASE_FIELD_H 1

/* #   include "bad_common.h" */
/* #   include "bad_regchain.h" */

BEGIN_C_DECLS

/*
 * texinfo: bad_base_field
 * This data structure implements base fields for polynomials, regular
 * chains. They are used by elimination methods.
 * Base fields are presented by generators and relations.
 * 
 * The field @code{first_block_index} contains the index
 * of the first block which contains generators, in the table of blocks of 
 * the current ordering.
 * The rule is that any dependent variable which belongs to the same block
 * or to any lower block belongs to the base field.
 * If no generator has been specified, the base field is defined as
 * the field of the rational fractions in the independent variables and
 * the field @code{first_block_index} contains @code{BA0_NOT_AN_INDEX}.
 *
 * Base fields are seen to be defined with respect to some ordering.
 * There is a restriction on orderings with respect to which base
 * fields can be defined: they must not involve @code{varmax} variables.
 *
 * A base field is differential if its @code{relations} field 
 * holds the @code{bad_differential_ideal_property}.
 */

struct bad_base_field
{
// indicate if the polynomials which are going to be tested
// zero or nonzero may supposed to be reduced with respect to relations
  bool assume_reduced;
// the first block index containing generators
  ba0_int_p first_block_index;
// the base field defining equations - the corresponding ideal must be prime.
  struct bad_regchain relations;
};


extern BAD_DLL void bad_init_base_field (
    struct bad_base_field *);

extern BAD_DLL struct bad_base_field *bad_new_base_field (
    void);

extern BAD_DLL bool bad_is_differential_base_field (
    struct bad_base_field *);

extern BAD_DLL void bad_set_base_field (
    struct bad_base_field *,
    struct bad_base_field *);

extern BAD_DLL void bad_base_field_generators (
    struct ba0_tableof_range_indexed_group *,
    struct bad_base_field *);

extern BAD_DLL void bad_set_base_field_relations_properties (
    struct bad_regchain *,
    bool);

extern BAD_DLL void bad_set_base_field_generators_and_relations (
    struct bad_base_field *,
    struct ba0_tableof_range_indexed_group *,
    struct bad_regchain *,
    bool);

extern BAD_DLL bool bad_is_a_compatible_base_field (
    struct bad_base_field *,
    struct bad_attchain *);

extern BAD_DLL bool bad_member_variable_base_field (
    struct bav_variable *,
    struct bad_base_field *);

extern BAD_DLL ba0_int_p bad_number_of_elements_over_base_field_regchain (
    struct bad_regchain *,
    struct bad_base_field *);

extern BAD_DLL bool bad_member_nonzero_polynom_base_field (
    struct bap_polynom_mpz *,
    struct bad_base_field *);

extern BAD_DLL bool bad_member_polynom_base_field (
    struct bap_polynom_mpz *,
    struct bad_base_field *);

extern BAD_DLL bool bad_member_product_base_field (
    struct bap_product_mpz *,
    struct bad_base_field *);

extern BAD_DLL void bad_remove_product_factors_base_field (
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bad_base_field *);

extern BAD_DLL void bad_tag_product_factors_base_field (
    struct bap_product_mpz *,
    struct ba0_tableof_bool *,
    struct bad_base_field *);

extern BAD_DLL ba0_scanf_function bad_scanf_base_field;

extern BAD_DLL ba0_printf_function bad_printf_base_field;

END_C_DECLS
#endif /* ! BAD_BASE_FIELD_H */
#if !defined (BAD_INTERSECTOF_REGCHAIN_H)
#   define BAD_INTERSECTOF_REGCHAIN_H 1

/* #   include "bad_common.h" */
/* #   include "bad_regchain.h" */
/* #   include "bad_reduction.h" */
/* #   include "bad_base_field.h" */

BEGIN_C_DECLS

/*
 * texinfo: bad_intersectof_regchain
 * This data structure mostly is a table a regular chain.
 * Mathematically, the ideal that it represents is the intersection
 * of the ideals defined by the chains.
 */

struct bad_intersectof_regchain
{
  struct bad_attchain attrib;
  struct bad_tableof_regchain inter;
};


extern BAD_DLL void bad_init_intersectof_regchain (
    struct bad_intersectof_regchain *);

extern BAD_DLL void bad_reset_intersectof_regchain (
    struct bad_intersectof_regchain *);

extern BAD_DLL struct bad_intersectof_regchain *bad_new_intersectof_regchain (
    void);

extern BAD_DLL void bad_realloc_intersectof_regchain (
    struct bad_intersectof_regchain *,
    ba0_int_p);

extern BAD_DLL void bad_set_intersectof_regchain_regchain (
    struct bad_intersectof_regchain *,
    struct bad_regchain *);

extern BAD_DLL void bad_append_intersectof_regchain_regchain (
    struct bad_intersectof_regchain *,
    struct bad_regchain *);

extern BAD_DLL void bad_append_intersectof_regchain (
    struct bad_intersectof_regchain *,
    struct bad_intersectof_regchain *);

extern BAD_DLL void bad_set_intersectof_regchain (
    struct bad_intersectof_regchain *,
    struct bad_intersectof_regchain *);

extern BAD_DLL void bad_set_property_intersectof_regchain (
    struct bad_intersectof_regchain *,
    enum bad_property_attchain);

extern BAD_DLL void bad_clear_property_intersectof_regchain (
    struct bad_intersectof_regchain *,
    enum bad_property_attchain);

extern BAD_DLL void bad_set_properties_intersectof_regchain (
    struct bad_intersectof_regchain *,
    struct ba0_tableof_string *);

extern BAD_DLL void bad_set_automatic_properties_intersectof_regchain (
    struct bad_intersectof_regchain *);

extern BAD_DLL bool bad_has_property_intersectof_regchain (
    struct bad_intersectof_regchain *,
    enum bad_property_attchain);

extern BAD_DLL void bad_properties_intersectof_regchain (
    struct ba0_tableof_string *,
    struct bad_intersectof_regchain *);

extern BAD_DLL struct bad_regchain *bad_get_regchain_intersectof_regchain (
    struct bad_intersectof_regchain *,
    ba0_int_p);

extern BAD_DLL void bad_sort_intersectof_regchain (
    struct bad_intersectof_regchain *,
    struct bad_intersectof_regchain *);

extern BAD_DLL void bad_remove_redundant_components_intersectof_regchain (
    struct bad_intersectof_regchain *,
    struct bad_intersectof_regchain *,
    struct bad_base_field *);

extern BAD_DLL void bad_fast_primality_test_intersectof_regchain (
    struct bad_intersectof_regchain *);

extern BAD_DLL ba0_scanf_function bad_scanf_intersectof_regchain;

extern BAD_DLL ba0_scanf_function bad_scanf_intersectof_pretend_regchain;

extern BAD_DLL ba0_printf_function bad_printf_intersectof_regchain;

extern BAD_DLL ba0_printf_function bad_printf_intersectof_regchain_equations;

extern BAD_DLL ba0_garbage1_function bad_garbage1_intersectof_regchain;

extern BAD_DLL ba0_garbage2_function bad_garbage2_intersectof_regchain;

extern BAD_DLL ba0_copy_function bad_copy_intersectof_regchain;

END_C_DECLS
#endif /* !BAD_INTERSECTOF_REGCHAIN_H */
#if !defined (BAD_REDUCTION_H)
#   define BAD_REDUCTION_H 1

/* #   include "bad_common.h" */
/* #   include "bad_regchain.h" */
/* #   include "bad_base_field.h" */

BEGIN_C_DECLS

/*
 * texinfo: bad_typeof_reduction
 * This data type permits to specify to reduction algorithms
 * the type of reduction to be performed.
 */

enum bad_typeof_reduction
{
  bad_full_reduction,
  bad_partial_reduction,
// no derivation is performed
  bad_algebraic_reduction
};

/*
 * texinfo: bad_typeof_derivative_to_reduce
 * This data type permits to indicate to reduction algorithms if
 * all derivatives have to be reduced or if the leading derivative
 * has to be preserved.
 */

enum bad_typeof_derivative_to_reduce
{
  bad_all_derivatives_to_reduce,
  bad_all_but_leader_to_reduce
};

/*
 * texinfo: bad_typeof_reduction_strategy
 * This data type permits to choose the method carried out by
 * the reduction algorithm.
 */

enum bad_typeof_reduction_strategy
{
// the polynomial to be reduced is factored/easy then reduction is performed factorwise and 
// gcd are computed to reduce power products of initial and separants involved in the process
// - default value
  bad_gcd_prem_and_factor_reduction_strategy,
// basic strategy
  bad_prem_reduction_strategy,
// a change of ordering is performed first in order
// to reduce polynomials coefficient per coefficient
  bad_prem_and_change_of_ordering_reduction_strategy,
};

/*
 * texinfo: bad_typeof_redzero_strategy
 * This data type permits to choose the method carried out by
 * the algorithms designed for testing if a differential polynomial
 * gets reduced to zero or not.
 */

enum bad_typeof_redzero_strategy
{
// the result is guaranteed - default value
  bad_deterministic_using_probabilistic_redzero_strategy,
// perform reduction and test if the result is zero
  bad_deterministic_redzero_strategy,
// the result is not guaranteed
  bad_probabilistic_redzero_strategy
};

/*
 * texinfo: bad_typeof_inclusion_test_result
 * This data type provides a return code after an inclusion
 * test between ideals presented by regular chains.
 */

enum bad_typeof_inclusion_test_result
{
  bad_inclusion_test_positive,
  bad_inclusion_test_negative,
  bad_inclusion_test_uncertain
};

extern BAD_DLL void bad_set_settings_reduction (
    enum bad_typeof_reduction_strategy,
    enum bad_typeof_redzero_strategy,
    ba0_int_p);

extern BAD_DLL void bad_get_settings_reduction (
    enum bad_typeof_reduction_strategy *,
    enum bad_typeof_redzero_strategy *,
    ba0_int_p *);

extern BAD_DLL void bad_reset_theta (
    struct bav_tableof_term *,
    struct bad_regchain *);

extern BAD_DLL void bad_reduce_easy_polynom_by_regchain (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bad_regchain *,
    enum bad_typeof_reduction);

extern BAD_DLL void bad_ensure_nonzero_initial_mod_regchain (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bad_regchain *,
    enum bad_typeof_reduction);

extern BAD_DLL void bad_reduce_polynom_by_regchain (
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bav_tableof_term *,
    struct bap_polynom_mpz *,
    struct bad_regchain *,
    enum bad_typeof_reduction,
    enum bad_typeof_derivative_to_reduce);

extern BAD_DLL void bad_reduce_product_by_regchain (
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bav_tableof_term *,
    struct bap_product_mpz *,
    struct bad_regchain *,
    enum bad_typeof_reduction,
    enum bad_typeof_derivative_to_reduce);

extern BAD_DLL bool bad_is_a_reduced_to_zero_polynom_by_regchain (
    struct bap_polynom_mpz *,
    struct bad_regchain *,
    enum bad_typeof_reduction);

extern BAD_DLL enum bad_typeof_inclusion_test_result bad_is_included_regchain (
    struct bad_regchain *,
    struct bad_regchain *,
    struct bad_base_field *);

extern BAD_DLL bool bad_is_a_reducible_polynom_by_regchain (
    struct bap_polynom_mpz *,
    struct bad_regchain *,
    enum bad_typeof_reduction,
    enum bad_typeof_derivative_to_reduce,
    struct bav_rank *,
    ba0_int_p *);

extern BAD_DLL bool bad_is_a_reducible_product_by_regchain (
    struct bap_product_mpz *,
    struct bad_regchain *,
    enum bad_typeof_reduction,
    enum bad_typeof_derivative_to_reduce,
    ba0_int_p *);

extern BAD_DLL bool bad_is_a_partially_reduced_polynom_wrt_regchain (
    struct bap_polynom_mpz *,
    struct bad_regchain *);

END_C_DECLS
#endif /* !BAD_REDUCTION_H */
#if ! defined (BAD_SELECTION_STRATEGY)
#   define BAD_SELECTION_STRATEGY 1

/* #   include "bad_common.h" */

BEGIN_C_DECLS

/*
 * texinfo: bad_typeof_selection_strategy
 * This data type is used to specify a strategy, carried out by
 * differential elimination algorithm, in order to select the next
 * polynomial to process.
 */

enum bad_typeof_selection_strategy
{
// plain polynomials are preferred to polynomials arising from critical pairs
  bad_equation_first_selection_strategy,
// polynomials with lower leaders are preferred
  bad_lower_leader_first_selection_strategy
};

/*
 * texinfo: bad_selection_strategy
 * This data type specifies a strategy, carried out by
 * differential elimination algorithm, in order to select the next
 * polynomial to process.
 */

struct bad_selection_strategy
{
  enum bad_typeof_selection_strategy strategy;
// a penalty used to penalize some critical pairs
  ba0_int_p penalty;
};


extern BAD_DLL void bad_init_selection_strategy (
    struct bad_selection_strategy *);

extern BAD_DLL struct bad_selection_strategy *bad_new_selection_strategy (
    void);

extern BAD_DLL void bad_set_strategy_selection_strategy (
    struct bad_selection_strategy *,
    enum bad_typeof_selection_strategy);

extern BAD_DLL void bad_set_penalty_selection_strategy (
    struct bad_selection_strategy *,
    ba0_int_p);

extern BAD_DLL void bad_double_penalty_selection_strategy (
    struct bad_selection_strategy *);

END_C_DECLS
#endif
#if !defined (BAD_CRITICAL_PAIR_H)
#   define BAD_CRITICAL_PAIR_H 1

/* #   include "bad_common.h" */
/* #   include "bad_selection_strategy.h" */

BEGIN_C_DECLS

/*
 * texinfo: bad_typeof_critical_pair
 * This data type permits to tag critical pairs in order to
 * process the most important ones before the other ones.
 * The default tag is @code{bad_normal_critical_pair}.
 * The tag @code{bad_rejected_easy_critical_pair} corresponds
 * to critical pairs @math{\{p_1, p_2\}} which are not reduction
 * critical pairs and such that neither @var{p_1} nor @var{p_2}
 * occurs in the field @code{A} of the current quadruple.
 */

enum bad_typeof_critical_pair
{
// default tag
  bad_normal_critical_pair,
// this tag indicates a lower priority
  bad_rejected_easy_critical_pair
};

/*
 * texinfo: bad_critical_pair
 * This data type implements critical pairs.
 * A pair @math{\{ p_1, p_2 \}} of differential polynomials is said to 
 * be a @dfn{critical pair} if the leaders of @math{p_1} and @math{p_2} 
 * are derivatives of some same differential indeterminate @math{u}.
 * Denote @math{\theta_1 u} the leading derivative of @math{p_1} and 
 *        @math{\theta_2 u} the one of @math{p_2}. 
 *
 * Denote @math{\theta_{12} = lcm{(\theta_1, \theta_2)}}. 
 *
 * If @math{\theta_{12} = \theta_1} or @math{\theta_{12} = \theta_2} 
 *      then the pair is called a @dfn{reduction critical pair}
 *      and the corresponding @math{\Delta}-polynomial is
 *      @math{\Delta (p_1, p_2) = prem (p_2, (\theta_{12}/{\theta_1}) p_1)}
 *
 * If the critical pair is not a reduction one then the
 *      corresponding @math{\Delta}-polynomial is
 *      @math{\Delta (p_1, p_2) = s_2 \, ({\theta_{12}}/{\theta_1}) p_1 
 *                              - s_1 \, ({\theta_{12}}/{\theta_2}) p_2}
 *      where @math{s_1} and @math{s_2} denote the separants of
 *      @math{p_1} and @math{p_2}.
 */

struct bad_critical_pair
{
  enum bad_typeof_critical_pair tag;
  struct bap_polynom_mpz p;
  struct bap_polynom_mpz q;
};


struct bad_listof_critical_pair
{
  struct bad_critical_pair *value;
  struct bad_listof_critical_pair *next;
};


extern BAD_DLL void bad_init_critical_pair (
    struct bad_critical_pair *);

extern BAD_DLL struct bad_critical_pair *bad_new_critical_pair (
    void);

extern BAD_DLL struct bad_critical_pair *bad_new_critical_pair_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAD_DLL void bad_set_critical_pair (
    struct bad_critical_pair *,
    struct bad_critical_pair *);

extern BAD_DLL void bad_set_critical_pair_polynom_mpz (
    struct bad_critical_pair *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAD_DLL void bad_delta_polynom_critical_pair (
    struct bap_polynom_mpz *,
    struct bad_critical_pair *);

extern BAD_DLL void bad_thetas_and_leaders_critical_pair (
    struct bav_tableof_term *,
    struct bav_tableof_variable *,
    struct bad_critical_pair *);

extern BAD_DLL bool bad_is_a_reduction_critical_pair (
    struct bad_critical_pair *,
    struct bav_variable **);

extern BAD_DLL bool bad_is_an_algebraic_critical_pair (
    struct bad_critical_pair *);

extern BAD_DLL bool bad_is_a_simpler_critical_pair (
    struct bad_critical_pair *,
    struct bad_critical_pair *,
    struct bad_selection_strategy *);

extern BAD_DLL bool bad_is_a_listof_rejected_critical_pair (
    struct bad_listof_critical_pair *);

extern BAD_DLL ba0_scanf_function bad_scanf_critical_pair;

extern BAD_DLL ba0_printf_function bad_printf_critical_pair;

extern BAD_DLL ba0_garbage1_function bad_garbage1_critical_pair;

extern BAD_DLL ba0_garbage2_function bad_garbage2_critical_pair;

extern BAD_DLL ba0_copy_function bad_copy_critical_pair;

END_C_DECLS
#endif /* !BAD_CRITICAL_PAIR_H */
#if !defined (BAD_SPLITTING_EDGE)
#   define BAD_SPLITTING_EDGE 1

/* #   include "bad_common.h" */

BEGIN_C_DECLS

/*
 * texinfo: bad_typeof_splitting_edge
 * This data type is a subtype of @code{bad_splitting_edge}.
 * It permits to associate a type to an edge in the splitting tree
 * generated by @code{bad_Rosenfeld_Groebner}.
 */

enum bad_typeof_splitting_edge
{
// not an edge
  bad_none_edge,
// critical pair leading to a non trivial differential polynomial
  bad_critical_pair_edge,
  bad_critical_pair_novar_edge, // result is a base field element
// reduction to zero
  bad_redzero_edge,
// splittings introducing an inequation at each edge
  bad_first_edge,               // processing the initial equations
  bad_factor_edge,              // plain factorization
  bad_initial_edge,             // initial
  bad_separant_edge,            // separant
// splittings not introducing inequations
  bad_regularize_edge,          // complete
  bad_reg_characteristic_edge   // reg_characteristic
};

/*
 * texinfo: bad_splitting_edge
 * This data type is a subtype of @code{bad_splitting_vertex}.
 * It permits to describe an edge of the splitting tree
 * generated by a differential elimination algorithm. 
 *
 * The fields @code{src} and @code{dst} contain the @emph{numbers}
 * of the vertices connected by the edge.
 *
 * For some values of the @code{type} field, the leader of the
 * involved polynomial is stored in the @code{leader} field.
 * Similarly, for some values of the @code{type} field, a
 * multiplicity information is stored in the
 * @code{multiplicity} field.
 */

struct bad_splitting_edge
{
// the type of the edge
  enum bad_typeof_splitting_edge type;
// the number of the source vertex
  ba0_int_p src;
// the number of the target vertex
  ba0_int_p dst;
// the leader of the differential polynomial (bad_separant_edge)
  struct bav_variable *leader;
// the multiplicity of the factor (bad_separant_edge)
  ba0_int_p multiplicity;
};

struct bad_tableof_splitting_edge
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bad_splitting_edge **tab;
};

extern BAD_DLL void bad_init_splitting_edge (
    struct bad_splitting_edge *);

extern BAD_DLL struct bad_splitting_edge *bad_new_splitting_edge (
    void);

extern BAD_DLL char *bad_typeof_splitting_edge_to_string (
    enum bad_typeof_splitting_edge);

extern BAD_DLL void bad_set_splitting_edge (
    struct bad_splitting_edge *,
    struct bad_splitting_edge *);

extern BAD_DLL bool bad_has_var_typeof_splitting_edge (
    enum bad_typeof_splitting_edge);

extern BAD_DLL bool bad_has_multiplicity_typeof_splitting_edge (
    enum bad_typeof_splitting_edge);

extern BAD_DLL bool bad_inequation_producing_splitting_edge (
    enum bad_typeof_splitting_edge);

extern BAD_DLL struct bav_symbol *bad_leader_symbol_splitting_edge (
    struct bad_splitting_edge *);

extern BAD_DLL void bad_set_tsdvm_splitting_edge (
    struct bad_splitting_edge *,
    enum bad_typeof_splitting_edge,
    ba0_int_p,
    ba0_int_p,
    struct bav_variable *,
    ba0_int_p);

extern BAD_DLL ba0_scanf_function bad_scanf_splitting_edge;

extern BAD_DLL ba0_printf_function bad_printf_splitting_edge;

extern BAD_DLL ba0_garbage1_function bad_garbage1_splitting_edge;

extern BAD_DLL ba0_garbage2_function bad_garbage2_splitting_edge;

extern BAD_DLL ba0_copy_function bad_copy_splitting_edge;

END_C_DECLS
#endif
#if !defined (BAD_SPLITTING_VERTEX_H)
#   define BAD_SPLITTING_VERTEX_H 1

/* #   include "bad_splitting_edge.h" */

BEGIN_C_DECLS

/*
 * texinfo: bad_shapeof_splitting_vertex
 * This data type is a subtype of @code{bad_splitting_vertex}.
 * It permits to associate a @emph{shape} to a vertex.
 * @itemize
 * @item    parallelogram vertices correspond to vertices which
 * are rejected by means of a dimension argument
 * @item    triangle vertices correspond to vertices which are
 * discarded because a new equation is incompatible with some
 * existing inequation
 * @item    box vertices correspond to output regular differential chains
 * @item    hexagon vertices correspond to systems handled by the
 * @emph{regCharacteristic} algorithm
 * @item    ellipse vertices correspond to any other case.
 * @end itemize
 */

enum bad_shapeof_splitting_vertex
{
  bad_parallelogram_vertex,
  bad_triangle_vertex,
  bad_box_vertex,
  bad_ellipse_vertex,
  bad_hexagon_vertex
};

/*
 * texinfo: bad_splitting_vertex
 * This data type is a subtype of @code{bad_splitting_tree}.
 * It permits to describe one vertex of the tree.
 * Each vertex corresponds to a quadruple / regular chain, which
 * is identified by its @emph{number}.
 *
 * The field @code{number} contains the number of the vertex.
 *
 * The field @code{is_first} indicates if the vertex is a @dfn{first}
 * vertex. First vertices play a special role in elimination methods
 * for they provide bounds which permit to discard quadruples
 * by means of a dimension argument.
 *
 * The field @code{edges} contains the table of the edges starting
 * from the vertex towards other vertices of the splitting tree.
 * This table is sorted by increasing @code{dst} number.
 *
 * The field @code{shape} contains the shape of the vertex.
 *
 * The fields @code{thetas} and @code{leaders} are only meaningful
 * if the successors of the vertex in the splitting tree were
 * obtained by a process involving a differential reduction step.
 * In such a case, @code{leaders} contains the leaders of the
 * regular differential chain used to performed the reduction while
 * @code{thetas} contains the least common multiple of the derivative
 * operators applied to these regular differential chain elements
 * by the reduction. Both tables have the same size and there is a
 * one-to-one correspondence between there elements.
 *
 * The field @code{discarded_branch} indicates if a possible branch,
 * starting from the vertex, was discarded because of the presence
 * of differential inequations.
 */

struct bad_splitting_vertex
{
// the number of the vertex which is also the number of the quadruple
  ba0_int_p number;
// indicate if the vertex is a ``first'' vertex
  bool is_first;
// the shape of the vertex
  enum bad_shapeof_splitting_vertex shape;
// the edges towards the children of the vertex
  struct bad_tableof_splitting_edge edges;
// the derivative operators involved in a reduction process (if applicable)
  struct bav_tableof_term thetas;
// the leaders of the polynomials they have applied to (if applicable)
  struct bav_tableof_variable leaders;
};

struct bad_tableof_splitting_vertex
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bad_splitting_vertex **tab;
};

extern BAD_DLL void bad_init_splitting_vertex (
    struct bad_splitting_vertex *);

extern BAD_DLL struct bad_splitting_vertex *bad_new_splitting_vertex (
    void);

extern BAD_DLL void bad_reset_splitting_vertex (
    struct bad_splitting_vertex *,
    ba0_int_p);

extern BAD_DLL void bad_set_splitting_vertex (
    struct bad_splitting_vertex *,
    struct bad_splitting_vertex *);

extern BAD_DLL void bad_merge_thetas_leaders_splitting_vertex (
    struct bad_splitting_vertex *,
    struct bav_tableof_term *,
    struct bav_tableof_variable *);

extern BAD_DLL char *bad_shapeof_splitting_vertex_to_string (
    enum bad_shapeof_splitting_vertex);

extern BAD_DLL ba0_scanf_function bad_scanf_splitting_vertex;

extern BAD_DLL ba0_printf_function bad_printf_splitting_vertex;

extern BAD_DLL ba0_garbage1_function bad_garbage1_splitting_vertex;

extern BAD_DLL ba0_garbage2_function bad_garbage2_splitting_vertex;

extern BAD_DLL ba0_copy_function bad_copy_splitting_vertex;


END_C_DECLS
#endif /* !BAD_SPLITTING_VERTEX_H */
#if !defined (BAD_SPLITTING_TREE_H)
#   define BAD_SPLITTING_TREE_H 1

/* #   include "bad_splitting_vertex.h" */

BEGIN_C_DECLS

/*
 * texinfo: bad_activity_level_splitting_tree
 * This data type is a subtype of @code{bad_splitting_tree}.
 */

enum bad_activity_level_splitting_tree
{
// the splitting tree is not generated
  bad_inactive_splitting_tree,
// the splitting tree is generated
  bad_quiet_splitting_tree,
// the splitting tree is generated and messages are printed
  bad_verbose_splitting_tree
};

/*
 * texinfo: bad_splitting_tree
 * This data type permits to describe the splitting tree generated by a
 * differential elimination algorithm.
 *
 * The field @code{vertices} contains the table of the tree vertices.
 * Each vertex is associated to one quadruple / regular chain, identified
 * by its @emph{number}. This @emph{number} is moreover equal to
 * the index of the vertex in the table. 
 *
 * The first entry of @code{vertices}, with @emph{number} zero,
 * is the @dfn{root vertex}. It does not correspond to any
 * actual quadruple / regular chain. It permits to handle
 * systems which have many different @emph{first} vertices.
 * First vertices play a special role in differential elimination methods
 * because they provide bounds which permit to discard quadruples
 * by means of a dimension argument.
 *
 * The field @code{number} contains the next free vertex number.
 * It may be greater than the @code{alloc} field of the @code{vertices}
 * table.
 *
 * The field @code{activity} provides the level of activity of the
 * tree. It may have three values:
 * @itemize
 * @item @code{bad_inactive_splitting_tree} then at most one vertex
 * is allocated to @code{vertices}: the @emph{root} vertex
 * @item @code{bad_quiet_splitting_tree} then the splitting tree
 * is generated
 * @item @code{bad_verbose_splitting_tree} same as above but the
 * differential elimination algorithm which builds the tree
 * may print some data on the standard output.
 * @end itemize
 */

struct bad_splitting_tree
{
  enum bad_activity_level_splitting_tree activity;
// the table of vertices
  struct bad_tableof_splitting_vertex vertices;
// the next free vertex number
  ba0_int_p number;
};

extern BAD_DLL void bad_init_splitting_tree (
    struct bad_splitting_tree *);

extern BAD_DLL struct bad_splitting_tree *bad_new_splitting_tree (
    void);

extern BAD_DLL void bad_reset_splitting_tree (
    struct bad_splitting_tree *,
    enum bad_activity_level_splitting_tree);

extern BAD_DLL void bad_set_splitting_tree (
    struct bad_splitting_tree *,
    struct bad_splitting_tree *);

extern BAD_DLL ba0_int_p bad_next_number_splitting_tree (
    struct bad_splitting_tree *);

extern BAD_DLL struct bad_splitting_vertex *bad_ith_vertex_splitting_tree (
    struct bad_splitting_tree *,
    ba0_int_p);

extern BAD_DLL bool bad_is_first_vertex_splitting_tree (
    struct bad_splitting_tree *,
    ba0_int_p);

extern BAD_DLL void bad_set_first_vertex_splitting_tree (
    struct bad_splitting_tree *,
    ba0_int_p,
    bool);

extern BAD_DLL void bad_set_vertex_shape_splitting_tree (
    struct bad_splitting_tree *,
    ba0_int_p,
    enum bad_shapeof_splitting_vertex);

extern BAD_DLL void bad_merge_thetas_leaders_vertex_splitting_tree (
    struct bad_splitting_tree *,
    ba0_int_p,
    struct bav_tableof_term *,
    struct bav_tableof_variable *);

extern BAD_DLL void bad_add_edge_splitting_tree (
    struct bad_splitting_tree *,
    enum bad_typeof_splitting_edge,
    ba0_int_p,
    ba0_int_p,
    struct bav_variable *,
    ba0_int_p);

extern BAD_DLL void bad_add_edge_novar_splitting_tree (
    struct bad_splitting_tree *,
    enum bad_typeof_splitting_edge,
    ba0_int_p,
    ba0_int_p);

extern BAD_DLL void bad_dot_splitting_tree (
    struct bad_splitting_tree *);

extern BAD_DLL ba0_scanf_function bad_scanf_splitting_tree;

extern BAD_DLL ba0_printf_function bad_printf_splitting_tree;

extern BAD_DLL ba0_garbage1_function bad_garbage1_splitting_tree;

extern BAD_DLL ba0_garbage2_function bad_garbage2_splitting_tree;

extern BAD_DLL ba0_copy_function bad_copy_splitting_tree;

END_C_DECLS
#endif /* !BAD_SPLITTING_TREE_H */
#if !defined (BAD_QUADRUPLE_H)
#   define BAD_QUADRUPLE_H 1

/* #   include "bad_common.h" */
/* #   include "bad_regchain.h" */
/* #   include "bad_intersectof_regchain.h" */
/* #   include "bad_selection_strategy.h" */
/* #   include "bad_critical_pair.h" */
/* #   include "bad_base_field.h" */

BEGIN_C_DECLS

/* 
 * texinfo: bad_quadruple
 * This data type implements quadruples 
 *      @math{G = \langle A,\, D,\, P,\, S \rangle},
 * which are processed by the RosenfeldGroebner algorithm.
 *
 * The field @code{A} contains a regular differential chain.
 *
 * The field @code{D} contains the list of the critical pairs
 * to be processed.
 *
 * The field @code{P} contains the list of the differential polynomials
 * to be processed.
 *
 * The field @code{S} contains a list of inequations.
 *
 * Quadruples are identified in splitting trees by a @emph{number}
 * which is held by the @code{number} field of @code{A}.
 *
 * The RosenfeldGroebner algorithm starts with
 *      @math{G = \langle \emptyset,\, \emptyset,\, P_0,\, S_0 \rangle}
 * where @math{P_0} and @math{S_0} are the input lists of equations 
 * and inequations. It computes a finite set of quadruples containing
 * regular systems i.e. of the form
 *      @math{G = \langle A,\, \emptyset,\, \emptyset,\, S \rangle}
 * and @var{S} partially reduced with respect to @var{A}.
 * These regular systems are then processed by the regCharacteristic
 * algorithm to produce a finite set of regular differential chains.
 */

struct bad_quadruple
{
// the (somehow) already processed differential polynomials
  struct bad_regchain A;
// the list of critical pairs waiting to be processed
  struct bad_listof_critical_pair *D;
// the list of differential polynomials waiting to be processed
  struct bap_listof_polynom_mpz *P;
// the list of inequations (different from zero) 
  struct bap_listof_polynom_mpz *S;
};

struct bad_tableof_quadruple
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bad_quadruple **tab;
};

struct bad_listof_quadruple
{
  struct bad_quadruple *value;
  struct bad_listof_quadruple *next;
};

struct bad_splitting_tree;

extern BAD_DLL void bad_init_quadruple (
    struct bad_quadruple *);

extern BAD_DLL struct bad_quadruple *bad_new_quadruple (
    void);

extern BAD_DLL void bad_set_number_quadruple (
    struct bad_quadruple *,
    ba0_int_p);

extern BAD_DLL void bad_set_next_number_quadruple (
    struct bad_quadruple *,
    struct bad_splitting_tree *);

extern BAD_DLL ba0_int_p bad_get_number_quadruple (
    struct bad_quadruple *);

extern BAD_DLL void bad_set_quadruple (
    struct bad_quadruple *,
    struct bad_quadruple *);

extern BAD_DLL void bad_mark_indets_quadruple (
    struct bav_dictionary_variable *,
    struct bav_tableof_variable *,
    struct bad_quadruple *);

extern BAD_DLL void bad_extend_quadruple_regchain (
    struct bad_quadruple *,
    struct bad_regchain *,
    struct bad_base_field *);

extern BAD_DLL void bad_insert_in_P_quadruple (
    struct bad_quadruple *,
    struct bad_quadruple *,
    struct bap_polynom_mpz *);

extern BAD_DLL void bad_insert_in_S_quadruple (
    struct bad_quadruple *,
    struct bad_quadruple *,
    struct bap_polynom_mpz *);

extern BAD_DLL struct bap_listof_polynom_mpz *bad_insert_in_listof_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_listof_polynom_mpz *);

extern BAD_DLL struct bap_listof_polynom_mpz *bad_delete_from_listof_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_listof_polynom_mpz *,
    bool *);

extern BAD_DLL void bad_preprocess_equation_quadruple (
    struct bap_product_mpz *,
    struct bap_tableof_polynom_mpz *,
    struct bap_tableof_product_mpz *,
    bool *,
    struct bad_quadruple *,
    struct bad_base_field *);

extern BAD_DLL void bad_report_simplification_of_inequations_quadruple (
    struct bad_tableof_quadruple *,
    struct bap_tableof_polynom_mpz *,
    struct bap_tableof_product_mpz *);

extern BAD_DLL void bad_split_on_factors_of_equations_quadruple (
    struct bad_tableof_quadruple *,
    struct bad_splitting_tree *,
    struct bap_product_mpz *,
    struct ba0_tableof_bool *,
    struct bap_polynom_mpz *);

extern BAD_DLL bool bad_simplify_and_store_in_P_quadruple (
    struct bad_quadruple *,
    bool *,
    struct bap_polynom_mpz *,
    struct bad_base_field *);

extern BAD_DLL bool bad_simplify_and_store_in_S_quadruple (
    struct bad_quadruple *,
    bool *,
    struct bap_polynom_mpz *,
    struct bad_base_field *);

extern BAD_DLL void bad_pick_and_remove_quadruple (
    struct bap_polynom_mpz *,
    struct bad_quadruple *,
    struct bad_critical_pair **,
    struct bad_selection_strategy *);

extern BAD_DLL void bad_reg_characteristic_quadruple (
    struct bad_intersectof_regchain *,
    struct bad_quadruple *,
    struct bad_regchain *,
    struct bad_base_field *);

extern BAD_DLL void bad_complete_quadruple (
    struct bad_tableof_quadruple *,
    struct bav_tableof_term *,
    bool *,
    struct bad_splitting_tree *,
    struct bap_polynom_mpz *,
    struct bad_regchain *,
    struct bad_base_field *,
    struct bad_selection_strategy *);

extern BAD_DLL ba0_scanf_function bad_scanf_quadruple;

extern BAD_DLL ba0_printf_function bad_printf_quadruple;

extern BAD_DLL ba0_garbage1_function bad_garbage1_quadruple;

extern BAD_DLL ba0_garbage2_function bad_garbage2_quadruple;

extern BAD_DLL ba0_copy_function bad_copy_quadruple;

END_C_DECLS
#endif /* !BAD_QUADRUPLE_H */
#if !defined (BAD_REGULARIZE_H)
#   define BAD_REGULARIZE_H 1

/* #   include "bad_common.h" */
/* #   include "bad_regchain.h" */
/* #   include "bad_base_field.h" */
/* #   include "bad_quadruple.h" */

BEGIN_C_DECLS

/*
 * texinfo: bad_typeof_regularize_strategy
 * This data type permits to indicate to regularization algorithms
 * the strategy to be carried out. All tests are based on 
 * pseudoremainder sequence computations.
 */

enum bad_typeof_regularize_strategy
{
// Lionel Ducos algorithm is applied
  bad_subresultant_regularize_strategy = 1,
// pseudoremainders are computed using baz_gcd_pseudo_division_polynom_mpz
  bad_gcd_prem_regularize_strategy,
// pseudoremainders are computed factor per factor using
//  baz_gcd_pseudo_division_polynom_mpz
  bad_gcd_prem_and_factor_regularize_strategy
};

/*
 * texinfo: bad_typeof_Euclid
 * This data type permits to control the type of extended Euclidean
 * algorithm to be performed.
 */

enum bad_typeof_Euclid
{
  bad_basic_Euclid,
  bad_half_extended_Euclid,
  bad_extended_Euclid
};

/*
 * texinfo: bad_typeof_context
 * This data type indicates to regularization methods the context
 * from which they are called.
 */

enum bad_typeof_context
{
// from an algebraic inverse computation
  bad_inverse_context,
// from the PARDI algorithm (change of ordering on regular chains)
  bad_pardi_context,
// from the RosenfeldGroebner algorithm
  bad_rg_context
};

extern BAD_DLL void bad_set_settings_regularize (
    enum bad_typeof_regularize_strategy);

extern BAD_DLL void bad_get_settings_regularize (
    enum bad_typeof_regularize_strategy *);

extern BAD_DLL void bad_Euclid_mod_regchain (
    struct bap_tableof_tableof_polynom_mpz *,
    struct bad_tableof_quadruple *,
    enum bad_typeof_Euclid,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *,
    bool,
    bool,
    struct bad_regchain *,
    struct bad_base_field *,
    struct bap_polynom_mpz **);

extern BAD_DLL void bad_check_regularity_polynom_mod_regchain (
    struct bap_polynom_mpz *,
    struct bad_regchain *,
    struct bad_base_field *,
    struct bap_polynom_mpz **);

extern BAD_DLL void bad_reg_characteristic_regchain (
    struct bad_intersectof_regchain *,
    struct bap_listof_polynom_mpz *,
    struct bad_regchain *,
    struct bad_base_field *);

extern BAD_DLL void bad_normal_form_polynom_mod_regchain (
    struct baz_ratfrac *,
    struct bap_polynom_mpz *,
    struct bad_regchain *,
    struct bap_polynom_mpz **);

extern BAD_DLL void bad_normal_form_ratfrac_mod_regchain (
    struct baz_ratfrac *,
    struct baz_ratfrac *,
    struct bad_regchain *,
    struct bap_polynom_mpz **);

extern BAD_DLL void bad_normal_form_ratfrac_mod_intersectof_regchain (
    struct baz_tableof_ratfrac *,
    struct baz_ratfrac *,
    struct bad_intersectof_regchain *,
    struct bap_polynom_mpz **);

extern BAD_DLL void bad_normal_form_handling_exceptions_ratfrac_mod_regchain (
    struct baz_tableof_ratfrac *,
    struct bad_intersectof_regchain *,
    struct bad_intersectof_regchain *,
    struct baz_ratfrac *);

END_C_DECLS
#endif /* !BAD_REGULARIZE_H */
#if ! defined (BAD_RESULTANT_H)
#   define BAD_RESULTANT_H 1

/* #   include "bad_regchain.h" */

BEGIN_C_DECLS

extern BAD_DLL void bad_resultant_mod_regchain (
    struct bap_product_mpz *,
    struct bap_polynom_mpz *,
    struct bad_regchain *);

END_C_DECLS
#endif /* BAD_RESULTANT_H */
#if !defined (BAD_INVERT_H)
#   define BAD_INVERT_H 1

/* #   include "bad_common.h" */
/* #   include "bad_regchain.h" */
/* #   include "bad_quadruple.h" */
/* #   include "bad_base_field.h" */

BEGIN_C_DECLS

extern BAD_DLL void bad_invert_polynom_mod_regchain (
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bap_polynom_mpz *,
    struct bad_regchain *,
    struct bad_base_field *,
    struct bap_polynom_mpz *volatile *);

extern BAD_DLL void bad_invert_product_mod_regchain (
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bad_regchain *,
    struct bad_base_field *,
    struct bap_polynom_mpz *volatile *);

extern BAD_DLL void bad_iterated_lsr3_product_mod_regchain (
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bad_regchain *);

END_C_DECLS
#endif /* !BAD_INVERT_H */
#if !defined (BAD_REDUCED_FORM_H)
#   define BAD_REDUCED_FORM_H 1

/* #   include "bad_common.h" */
/* #   include "bad_regchain.h" */
/* #   include "bad_intersectof_regchain.h" */

BEGIN_C_DECLS

extern BAD_DLL void bad_reduced_form_polynom_mod_regchain (
    struct baz_ratfrac *,
    struct bap_polynom_mpz *,
    struct bav_variable *,
    struct bad_regchain *);

extern BAD_DLL void bad_reduced_form_polynom_mod_intersectof_regchain (
    struct baz_tableof_ratfrac *,
    struct bap_polynom_mpz *,
    struct bav_variable *,
    struct bad_intersectof_regchain *);

END_C_DECLS
#endif /* !BAD_REDUCED_FORM_H */
#if !defined (BAD_LOW_POWER_THEOREM_H)
#   define BAD_LOW_POWER_THEOREM_H 1

/* #   include "bad_common.h" */
/* #   include "bad_regchain.h" */
/* #   include "bad_intersectof_regchain.h" */
/* #   include "bad_base_field.h" */

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
#if !defined (BAD_PARDI_H)
#   define BAD_PARDI_H 1

/* #   include "bad_common.h" */
/* #   include "bad_regchain.h" */

BEGIN_C_DECLS

extern BAD_DLL void bad_pardi (
    struct bad_regchain *,
    bav_Iordering,
    struct bad_regchain *);

END_C_DECLS
#endif /* !BAD_PARDI_H */
#if !defined (BAD_ROSENFELD_GROEBNER_H)
#   define BAD_ROSENFELD_GROEBNER_H 1

/* #   include "bad_common.h" */
/* #   include "bad_intersectof_regchain.h" */
/* #   include "bad_base_field.h" */
/* #   include "bad_splitting_control.h" */
/* #   include "bad_splitting_tree.h" */

BEGIN_C_DECLS

extern BAD_DLL void bad_Rosenfeld_Groebner (
    struct bad_intersectof_regchain *,
    struct bad_splitting_tree *,
    struct bap_tableof_polynom_mpz *,
    struct bap_tableof_polynom_mpz *,
    struct bad_base_field *,
    struct bad_regchain *,
    struct bad_splitting_control *);

extern BAD_DLL void bad_first_quadruple (
    struct bad_tableof_quadruple *,
    struct bad_attchain *,
    struct bap_tableof_polynom_mpz *,
    struct bap_tableof_polynom_mpz *,
    enum bad_typeof_reduction,
    struct bad_base_field *,
    struct bad_regchain *);

END_C_DECLS
#endif /* !BAD_ROSENFELD_GROEBNER_H */
#if !defined (BAD_GLOBAL_H)
#   define BAD_GLOBAL_H 1

/* #   include "bad_common.h" */
/* #   include "bad_reduction.h" */
/* #   include "bad_regularize.h" */
/* #   include "bad_low_power_theorem.h" */

BEGIN_C_DECLS

struct bad_global
{
  struct
  {
/* 
 * Local variable to bad_reduction.
 * Used to pass some extra information to a subfunction in
 * bad_random_eval_variables_under_the_stairs
 * Its value is meaningless between two calls to this function.
 */
    struct bav_tableof_variable *stairs;
  } reduction;
  struct
  {
/* 
 * Statistical information set by bad_Rosenfeld_Groebner and bad_pardi
 */
    time_t begin;
    time_t end;
    ba0_int_p critical_pairs_processed;
    ba0_int_p reductions_to_zero;
  } stats;
};

struct bad_initialized_global
{
  struct
  {
/* 
 * reduction_strategy = the type of reduction strategy applied
 * redzero_strategy   = the type of reduction test to zero applied
 * number_of_redzero_tries = tuning for probabilistic methods
 * Local to bad_reduction.
 */
    enum bad_typeof_reduction_strategy reduction_strategy;
    enum bad_typeof_redzero_strategy redzero_strategy;
    ba0_int_p number_of_redzero_tries;
  } reduction;
  struct
  {
/* 
 * strategy = the type of regularization strategy applied
 * Local to bad_regularize.
 */
    enum bad_typeof_regularize_strategy strategy;
  } regularize;
  struct
  {
/*
 * The string used for denoting differential regular chain elements
 * in the context of preparation equations (cf. Low Power Theorem).
 */
    char *zstring;
  } preparation;
};

extern BAD_DLL struct bad_global bad_global;

extern BAD_DLL struct bad_initialized_global bad_initialized_global;

END_C_DECLS
#endif /* !BAD_GLOBAL_H */
