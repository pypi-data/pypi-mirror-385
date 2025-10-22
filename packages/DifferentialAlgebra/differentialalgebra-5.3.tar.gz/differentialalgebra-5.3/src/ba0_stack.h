#if !defined (BA0_STACK_H)
#   define BA0_STACK_H

#   include "ba0_common.h"
#   include "ba0_table.h"
#   include "ba0_int_p.h"

BEGIN_C_DECLS

/*
 * texinfo: ba0_mark
 * The data structure @code{ba0_mark} implements marks.
 * From the user point of view, a @dfn{mark} is a pointer in a stack.
 * Marks are used for garbage collection.
 */

struct ba0_mark
{
// the stack the address belongs to
  struct ba0_stack *stack;      // the stack the address belongs to 
// the index of the stack cell the address belongs to
  ba0_int_p index_in_cells;
  void *address;                // the address
// the number of free bytes in the cell, after the mark
  unsigned ba0_int_p memory_left;
};

/* texinfo: ba0_stack
 * The data structure @code{ba0_stack} mplements stacks.
 * From the user point of view, a stack is a huge piece of memory in
 * which memory allocation is possible.
 * A stack is implemented as an array of cells.
 * Cells are blocks of memory allocated in the process heap via
 * @code{ba0_alloc}.
 */

struct ba0_stack
{
// the identifier (nickname) of the stack
  char *ident;
// the array of cells and the corresponding array of cell sizes
  struct ba0_table cells;
  struct ba0_tableof_unsigned_int_p sizes;
// the default size of cells (may increase during computations)
  unsigned ba0_int_p default_size;
// default value is true (if false, cell sizes do not increase)
  bool resizable;
// the border between the used and the free parts of the stack
  struct ba0_mark free;
// the max address reached by the free pointer
  struct ba0_mark max_alloc;
// counts the number of allocations in the process heap
  ba0_int_p nb_calls_to_alloc;
// for debugging purposes
  ba0_int_p *bound;
};

struct ba0_tableof_stack
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct ba0_stack **tab;
};


/* 
 * Some default values
 */

#   define BA0_SIZE_CELL_MAIN_STACK   0x20000
#   define BA0_SIZE_CELL_QUIET_STACK  0x20000
#   define BA0_SIZE_CELL_ANALEX_STACK 0x10000
#   define BA0_NB_CELLS_PER_STACK       0x100
#   define BA0_SIZE_STACK_OF_STACK      0x100

extern BA0_DLL void ba0_set_settings_no_oom (
    bool);

extern BA0_DLL void ba0_get_settings_no_oom (
    bool *);

extern BA0_DLL void ba0_set_settings_stack (
    ba0_int_p,
    ba0_int_p,
    ba0_int_p,
    ba0_int_p,
    ba0_int_p);

extern BA0_DLL void ba0_get_settings_stack (
    ba0_int_p *,
    ba0_int_p *,
    ba0_int_p *,
    ba0_int_p *,
    ba0_int_p *);

extern BA0_DLL void ba0_init_stack_of_stacks (
    void);

extern BA0_DLL void ba0_reset_stack_of_stacks (
    void);

extern BA0_DLL void ba0_clear_stack_of_stacks (
    void);

#   define ba0_alloc_counter	ba0_global.stack.alloc_counter
#   define ba0_malloc_counter	ba0_global.stack.malloc_counter
#   define ba0_malloc_nbcalls	ba0_global.stack.malloc_nbcalls

extern BA0_DLL void ba0_set_settings_memory_functions (
    void *(*)(size_t),
    void (*)(void *));

extern BA0_DLL void ba0_get_settings_memory_functions (
    void *(**)(size_t),
    void (**)(void *));

extern BA0_DLL unsigned ba0_int_p ba0_ceil_align (
    unsigned ba0_int_p);

extern BA0_DLL unsigned ba0_int_p ba0_allocated_size (
    unsigned ba0_int_p);

extern BA0_DLL void *ba0_malloc (
    ba0_int_p);

extern BA0_DLL void *ba0_persistent_malloc (
    ba0_int_p);

extern BA0_DLL void ba0_free (
    void *);

extern BA0_DLL ba0_int_p ba0_cell_index_mark (
    void *,
    struct ba0_mark *);

extern BA0_DLL bool ba0_in_stack (
    void *,
    struct ba0_stack *);

extern BA0_DLL struct ba0_stack *ba0_which_stack (
    void *);

extern BA0_DLL struct ba0_stack *ba0_current_stack (
    void);

extern BA0_DLL unsigned ba0_int_p ba0_max_alloc_stack (
    struct ba0_stack *);

extern BA0_DLL void ba0_push_stack (
    struct ba0_stack *);

extern BA0_DLL void ba0_pull_stack (
    void);

extern BA0_DLL void ba0_push_another_stack (
    void);

extern BA0_DLL void ba0_init_stack (
    struct ba0_stack *);

extern BA0_DLL void ba0_init_one_cell_stack (
    struct ba0_stack *,
    char *,
    void *,
    ba0_int_p);

extern BA0_DLL void ba0_reset_stack (
    struct ba0_stack *);

extern BA0_DLL void ba0_reset_cell_stack (
    struct ba0_stack *);

extern BA0_DLL void ba0_clear_cells_stack (
    struct ba0_stack *);

extern BA0_DLL void ba0_clear_one_cell_stack (
    struct ba0_stack *);

extern BA0_DLL void ba0_clear_stack (
    struct ba0_stack *);

extern BA0_DLL void *ba0_alloc_but_do_not_set_magic (
    unsigned ba0_int_p);

extern BA0_DLL void ba0_alloc_set_magic (
    void);

extern BA0_DLL void *ba0_alloc (
    unsigned ba0_int_p);

extern BA0_DLL unsigned ba0_int_p ba0_memory_left_in_cell (
    void);

extern BA0_DLL void ba0_t1_alloc (
    unsigned ba0_int_p,
    unsigned ba0_int_p,
    void **,
    unsigned ba0_int_p *);

extern BA0_DLL void ba0_t2_alloc (
    unsigned ba0_int_p,
    unsigned ba0_int_p,
    unsigned ba0_int_p,
    void **,
    void **,
    unsigned ba0_int_p *);

extern BA0_DLL void ba0_rotate_cells (
    ba0_int_p);

extern BA0_DLL void *ba0_alloc_mark (
    struct ba0_mark *,
    unsigned ba0_int_p);

extern BA0_DLL void ba0_record (
    struct ba0_mark *);

extern BA0_DLL void ba0_restore (
    struct ba0_mark *);

extern BA0_DLL unsigned ba0_int_p ba0_range_mark (
    struct ba0_mark *,
    struct ba0_mark *);

END_C_DECLS
#endif /* !BA0_STACK_H */
