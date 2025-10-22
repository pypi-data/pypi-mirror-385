#if ! defined (BAD_QUENCH_MAP_H)
#   define BAD_QUENCH_MAP_H 1

#   include "bad_regchain.h"

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
