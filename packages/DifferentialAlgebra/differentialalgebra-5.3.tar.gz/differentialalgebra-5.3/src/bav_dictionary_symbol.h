#if !defined (BAV_DICTIONARY_SYMBOL_H)
#   define BAV_DICTIONARY_SYMBOL_H 1

#   include "bav_symbol.h"

BEGIN_C_DECLS

/*
 * texinfo: bav_dictionary_symbol
 * This data structure implements dictionaries which map 
 * @code{struct bav_symbol *} to other objects.
 * In this implementation, the values associated to the keys are integers, 
 * which are supposed to be indices in some table of objects of unspecified 
 * type.
 * This data structure actually is as an alias for
 * @code{struct ba0_dictionary}. 
 */

struct bav_dictionary_symbol
{
// each entry contains either -1 or an index in some table of symbols
  struct ba0_tableof_int_p area;
// the shift applied on keys before hashing them
  ba0_int_p shift;
// the base-2 logarithm of the size/alloc field of area if area is nonempty
  ba0_int_p log2_size;
// the number of used entries in area
  ba0_int_p used_entries;
};

extern BAV_DLL void bav_init_dictionary_symbol (
    struct bav_dictionary_symbol *,
    ba0_int_p);

extern BAV_DLL void bav_reset_dictionary_symbol (
    struct bav_dictionary_symbol *);

extern BAV_DLL unsigned ba0_int_p bav_sizeof_dictionary_symbol (
    struct bav_dictionary_symbol *,
    enum ba0_garbage_code);

extern BAV_DLL void bav_set_dictionary_symbol (
    struct bav_dictionary_symbol *,
    struct bav_dictionary_symbol *);

extern BAV_DLL ba0_int_p bav_get_dictionary_symbol (
    struct bav_dictionary_symbol *,
    struct bav_tableof_symbol *,
    struct bav_symbol *);

extern BAV_DLL void bav_add_dictionary_symbol (
    struct bav_dictionary_symbol *,
    struct bav_tableof_symbol *,
    struct bav_symbol *,
    ba0_int_p);

END_C_DECLS
#endif /* !BAV_DICTIONARY_SYMBOL_H */
