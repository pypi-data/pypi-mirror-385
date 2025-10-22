#if !defined (BAD_ATTCHAIN_H)
#   define BAD_ATTCHAIN_H 1

#   include "bad_common.h"

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
