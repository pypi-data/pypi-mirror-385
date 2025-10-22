#if !defined (BAD_BASE_FIELD_H)
#   define BAD_BASE_FIELD_H 1

#   include "bad_common.h"
#   include "bad_regchain.h"

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
