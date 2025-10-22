#if !defined (BA0_DICTIONARY_H)
#   define BA0_DICTIONARY_H 1

#   include "ba0_common.h"
#   include "ba0_int_p.h"
#   include "ba0_table.h"

BEGIN_C_DECLS

/*
 * texinfo: ba0_dictionary
 * This data structure implements generic dictionaries which map 
 * @code{void *} pointers or @code{ba0_int_p} to other objects.
 * In this implementation, the values associated to the keys are integers, 
 * which are supposed to be indices in some table of objects of unspecified 
 * type.
 * It is implemented using the double hash strategy.
 * The entries of the field @code{area} contain either @math{-1} or 
 * the index, in some unspecified table, of some object.
 * The size of @code{area} is a power of two given by @code{log2_size}.
 *
 * For computing hash values, keys are first shifted @code{shift} bits
 * to the right. For a dictionary of integers @code{shift} should be zero.
 * For a dictionary of pointers to objects of type @var{T}, 
 * @code{shift} should be the highest exponent @math{e} such that 
 * @math{2^e} is less than or equal to the size in bytes of
 * the objects to type @var{T}.
 */

struct ba0_dictionary
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

extern BA0_DLL void ba0_init_dictionary (
    struct ba0_dictionary *,
    ba0_int_p,
    ba0_int_p);

extern BA0_DLL void ba0_reset_dictionary (
    struct ba0_dictionary *);

extern BA0_DLL unsigned ba0_int_p ba0_sizeof_dictionary (
    struct ba0_dictionary *,
    enum ba0_garbage_code);

extern BA0_DLL void ba0_set_dictionary (
    struct ba0_dictionary *,
    struct ba0_dictionary *);

extern BA0_DLL ba0_int_p ba0_get_dictionary (
    struct ba0_dictionary *,
    struct ba0_table *,
    void *);

extern BA0_DLL void ba0_add_dictionary (
    struct ba0_dictionary *,
    struct ba0_table *,
    void *,
    ba0_int_p);

END_C_DECLS
#endif /* !BA0_DICTIONARY_H */
