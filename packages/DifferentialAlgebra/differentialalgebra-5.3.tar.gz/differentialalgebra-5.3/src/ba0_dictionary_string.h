#if !defined (BA0_DICTIONARY_STRING_H)
#   define BA0_DICTIONARY_STRING_H 1

#   include "ba0_common.h"
#   include "ba0_int_p.h"
#   include "ba0_table.h"

BEGIN_C_DECLS

/*
 * texinfo: ba0_dictionary_string
 * This data structure implements generic dictionaries which map strings
 * to other objects. In this implementation, the values associated
 * to the keys are integers, which are supposed to be indices in some 
 * table of objects of unspecified type.
 * It is implemented using the double hash strategy.
 * The entries of the field @code{area} contain either @math{-1} or 
 * the index, in some unspecified table, of some object.
 * The size of @code{area} is a power of two given by @code{log2_size}.
 */

struct ba0_dictionary_string
{
// each entry contains either -1 or an index in some table of variables
  struct ba0_tableof_int_p area;
// the base-2 logarithm of the size/alloc field of area if area is nonempty
  ba0_int_p log2_size;
// the number of used entries in area
  ba0_int_p used_entries;
// a function which associates an identifier to an object
  char *(
      *object_to_ident) (
      void *);
};

extern BA0_DLL void ba0_init_dictionary_string (
    struct ba0_dictionary_string *,
    char *(*)(void *),
    ba0_int_p);

extern BA0_DLL void ba0_reset_dictionary_string (
    struct ba0_dictionary_string *);

extern BA0_DLL unsigned ba0_int_p ba0_sizeof_dictionary_string (
    struct ba0_dictionary_string *,
    enum ba0_garbage_code);

extern BA0_DLL void ba0_set_dictionary_string (
    struct ba0_dictionary_string *,
    struct ba0_dictionary_string *);

extern BA0_DLL ba0_int_p ba0_get_dictionary_string (
    struct ba0_dictionary_string *,
    struct ba0_table *,
    char *);

extern BA0_DLL void ba0_add_dictionary_string (
    struct ba0_dictionary_string *,
    struct ba0_table *,
    char *,
    ba0_int_p);

END_C_DECLS
#endif /* !BA0_DICTIONARY_STRING_H */
