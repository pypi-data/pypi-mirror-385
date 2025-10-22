#if !defined (BA0_GARBAGE_H)
#   define BA0_GARBAGE_H 1

#   include "ba0_common.h"
#   include "ba0_stack.h"
#   include "ba0_list.h"
#   include "ba0_table.h"
#   include "ba0_format.h"

/* Garbage collector of J.-C. Faugere */

BEGIN_C_DECLS

/*
 * texinfo: ba0_gc_info
 * Structures of this data type are created by @code{ba0_garbage1_function}
 * and read by @code{ba0_garbage2_function} functions. They permit to
 * move data structures involving pointers.
 */

struct ba0_gc_info
{
// the index of the stack cell which contains the garbaged data structure
  ba0_int_p old_index_in_cells;
// the old address of the data structure
  void *old_addr;
  union
  {
// the size in bytes of the data structure (set at garbage1 pass)
    unsigned ba0_int_p size;
// the new address of the data structure (set at garbage2 pass)
    void *new_addr;
  } u;
// a readonly string describing the structure for debugging purposes
  char *text;
};


extern BA0_DLL void ba0_garbage (
    char *,
    struct ba0_mark *,
    ...);

extern BA0_DLL ba0_int_p ba0_garbage1 (
    char *,
    void *,
    enum ba0_garbage_code);

extern BA0_DLL void *ba0_garbage2 (
    char *,
    void *,
    enum ba0_garbage_code);

extern BA0_DLL ba0_int_p ba0_new_gc_info (
    void *,
    unsigned ba0_int_p,
    char *);

extern BA0_DLL void *ba0_new_addr_gc_info (
    void *,
    char *);

END_C_DECLS
#endif /* !BA0_GARBAGE_H */
