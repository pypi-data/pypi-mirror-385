#include "ba0_stack.h"
#include "ba0_exception.h"
#include "ba0_analex.h"
#include "ba0_global.h"

/*
 * A magic number used to check memory overflow
 */

#ifdef BA0_MEMCHECK
#   ifdef BA0_64BITS
static ba0_int_p magic = 0x3352074971119021;
#   else
static ba0_int_p magic = 0x33520749;
#   endif
#endif

#define system_malloc	ba0_initialized_global.stack.system_malloc
#define system_free	ba0_initialized_global.stack.system_free
#define no_oom		ba0_initialized_global.malloc.no_oom

/*
 * Every call to malloc should go through the following function.
 */

/*
 * texinfo: ba0_malloc
 * Allocate at least @var{n} bytes by calling the system @code{malloc}.
 * The allocated memory is eventually freed by a call to @code{ba0_free}
 * issued by @code{ba0_terminate}.
 * This function (and the next one) are the only one allowed to call 
 * the system @code{malloc}. They are also the only ones which check 
 * the memory limit. They may raise exception @code{BA0_ERROOM}.
 */

BA0_DLL void *
ba0_malloc (
    ba0_int_p n)
{
  void *m;

  if (no_oom == false
      && n + ba0_malloc_counter > ba0_global.common.memory_limit)
    BA0_RAISE_EXCEPTION (BA0_ERROOM);
  m = (*system_malloc) (n);
  if (m == (void *) 0)
    BA0_RAISE_EXCEPTION (BA0_ERROOM);
  ba0_malloc_counter += n;
  ba0_malloc_nbcalls += 1;
  return m;
}

/*
 * texinfo: ba0_persistent_malloc
 * Allocate at least @var{n} bytes by calling the system @code{malloc}.
 * The allocated memory is not freed by any call to @code{ba0_free}
 * issued by @code{ba0_terminate}.
 * Exception @code{BA0_ERROOM} may be raised.
 * This function is designed to allocate areas which should be kept
 * after calling @code{ba0_terminate}. See @code{ba0_new_printf}.
 */

BA0_DLL void *
ba0_persistent_malloc (
    ba0_int_p n)
{
  void *m;

  if (no_oom == false
      && n + ba0_malloc_counter > ba0_global.common.memory_limit)
    BA0_RAISE_EXCEPTION (BA0_ERROOM);
  m = (*system_malloc) (n);
  if (m == (void *) 0)
    BA0_RAISE_EXCEPTION (BA0_ERROOM);
  return m;
}

/*
 * texinfo: ba0_free
 * Free the area pointed to by @var{p}, which is assumed to be allocated
 * through @code{ba0_malloc}.
 */

BA0_DLL void
ba0_free (
    void *p)
{
  ba0_malloc_nbcalls -= 1;
  (*system_free) (p);
}

/*
 * texinfo: ba0_set_settings_no_oom
 * Set to @var{b} a settings variable which permits to forbid the
 * exception @code{BA0_ERROOM} (out of memory) when possible.
 * This settings function can be called within sequences of calls
 * to the library, in order to prevent critical code to be
 * interrupted.
 */

BA0_DLL void
ba0_set_settings_no_oom (
    bool b)
{
  no_oom = b ? b : false;
}

/*
 * texinfo: ba0_get_settings_no_oom
 * Assign to *@var{b}, the value of the settings variable
 * described above.
 */

BA0_DLL void
ba0_get_settings_no_oom (
    bool *b)
{
  if (b)
    *b = no_oom;
}

/*
 * To be called before ba0_restart !
 */

/*
 * texinfo: ba0_set_settings_memory_functions
 * Make the three above function call @var{malloc} and @var{free}
 * instead of the system @code{malloc} and @code{free} functions.
 */

BA0_DLL void
ba0_set_settings_memory_functions (
    void *(*m) (size_t),
    void (*f) (void *))
{
  system_malloc = m ? m : &malloc;
  system_free = f ? f : &free;
}

/*
 * texinfo: ba0_get_settings_memory_functions
 * Assign to @var{malloc} and @var{free} the addresses of the 
 * functions called by @code{ba0_malloc} and @code{ba0_free} for
 * allocating and freeing memory. 
 */

BA0_DLL void
ba0_get_settings_memory_functions (
    void *(**m) (size_t),
    void (**f) (void *))
{
  if (m)
    *m = system_malloc;
  if (f)
    *f = system_free;
}

/*
 * Return the smallest integer m greater than or equal to n such that
 * m is a multiple of BA0_ALIGN (memory alignment).
 */

/*
 * texinfo: ba0_ceil_align
 * Round @var{size} in order to get a multiple of the @code{BA0_ALIGN} constant.
 */

BA0_DLL unsigned ba0_int_p
ba0_ceil_align (
    unsigned ba0_int_p n)
{
  return (n + BA0_ALIGN - 1) & -BA0_ALIGN;
}

/*
 * Local function, used by ba0_memory_left_in_cell
 */

static unsigned ba0_int_p
ba0_floor_align (
    unsigned ba0_int_p n)
{
  return n & -BA0_ALIGN;
}

/*
 * Return the size actually allocated by ba0_alloc.
 * Beware to the fact that, on some architectures, 
 * 		BA0_ALIGN > sizeof (ba0_int_p)
 */

/*
 * texinfo: ba0_allocated_size
 * Return the number of bytes that @code{ba0_alloc} would allocate for
 * @var{size} bytes. 
 */

BA0_DLL unsigned ba0_int_p
ba0_allocated_size (
    unsigned ba0_int_p n)
{
  n = ba0_ceil_align (n);
#if defined (BA0_MEMCHECK)
  n += BA0_ALIGN;
#endif
  return n;
}

/*************************************************************
 * STACKS SETTINGS
 *************************************************************/

#define ba0_sizeof_main_cell	ba0_initialized_global.stack.sizeof_main_cell
#define ba0_sizeof_quiet_cell	ba0_initialized_global.stack.sizeof_quiet_cell
#define ba0_sizeof_analex_cell	ba0_initialized_global.stack.sizeof_analex_cell
#define ba0_nb_cells_per_stack	ba0_initialized_global.stack.nb_cells_per_stack
#define ba0_sizeof_stack_of_stack	ba0_initialized_global.stack.sizeof_stack_of_stack

/*
 * texinfo: ba0_set_settings_stack
 * Set the initial default 
 * cell sizes of @code{ba0_global.stack.main} and @code{ba0_global.stack.second}
 * to @var{main}, those of @code{ba0_global.stack.quiet} and @code{ba0_global.stack.format}
 * to @var{quiet} and those of @code{ba0_global.stack.analex} to @var{analex}. 
 * Set the initial number of cells per stack to @var{nbcells}.
 * Set the initial size of the stack of stacks to @var{sizess}.
 * If one of these arguments is zero, a default value is used.
 */

BA0_DLL void
ba0_set_settings_stack (
    ba0_int_p main,
    ba0_int_p quiet,
    ba0_int_p analex,
    ba0_int_p nbcells,
    ba0_int_p sizess)
{
  main = ba0_ceil_align (main);
  quiet = ba0_ceil_align (quiet);
  analex = ba0_ceil_align (analex);

  ba0_sizeof_main_cell = main ? main : BA0_SIZE_CELL_MAIN_STACK;
  ba0_sizeof_quiet_cell = quiet ? quiet : BA0_SIZE_CELL_QUIET_STACK;
  ba0_sizeof_analex_cell = analex ? analex : BA0_SIZE_CELL_ANALEX_STACK;
  ba0_nb_cells_per_stack = nbcells ? nbcells : BA0_NB_CELLS_PER_STACK;
  ba0_sizeof_stack_of_stack = sizess ? sizess : BA0_SIZE_STACK_OF_STACK;
}

/*
 * texinfo: ba0_get_settings_stack
 * Assign to *@var{main}, *@var{quiet} and *@var{analex} the current values used
 * for allocating cell sizes. Assign to @var{nbcells} the number
 * of cells per stack and to @var{sizess} the size of the stack of stacks.
 * The pointers are allowed to be zero.
 */

BA0_DLL void
ba0_get_settings_stack (
    ba0_int_p *main,
    ba0_int_p *quiet,
    ba0_int_p *analex,
    ba0_int_p *nbcells,
    ba0_int_p *sizess)
{
  if (main)
    *main = ba0_sizeof_main_cell;
  if (quiet)
    *quiet = ba0_sizeof_quiet_cell;
  if (analex)
    *analex = ba0_sizeof_analex_cell;
  if (nbcells)
    *nbcells = ba0_nb_cells_per_stack;
  if (sizess)
    *sizess = ba0_sizeof_stack_of_stack;
}

/**********************************************************************
 STACKS
 **********************************************************************/

static void ba0_set_mark (
    struct ba0_mark *,
    struct ba0_stack *,
    ba0_int_p,
    void *address,
    unsigned ba0_int_p);

/*
   For debugging purpose.
   Returns true if p points to an area located in the used part of H.
*/

/*
 * texinfo: ba0_in_stack
 * Return @code{true} if @var{p} is pointing
 * somewhere in @var{H} and @code{false} otherwise.
 */

BA0_DLL bool
ba0_in_stack (
    void *p,
    struct ba0_stack *H)
{
  return ba0_cell_index_mark (p, &H->free) != -1;
}

/*
 * Used by ba0_raise_exception2.
 * Return the stack in which p points to.
 * Does not investigate all the stacks.
 */

/*
 * texinfo: ba0_which_stack
 * Return the address of the stack where @var{p} is pointing.
 * Return zero if not found.
 * This function only looks in @code{ba0_global.stack.main}, 
 * @code{ba0_global.stack.second} and
 * @code{ba0_global.stack.quiet}.
 */

BA0_DLL struct ba0_stack *
ba0_which_stack (
    void *p)
{
  if (ba0_in_stack (p, &ba0_global.stack.main))
    return &ba0_global.stack.main;
  else if (ba0_in_stack (p, &ba0_global.stack.second))
    return &ba0_global.stack.second;
  else if (ba0_in_stack (p, &ba0_global.stack.quiet))
    return &ba0_global.stack.quiet;
  else
    return (struct ba0_stack *) 0;
}

/*
 * Return the current stack
 */

/*
 * texinfo: ba0_current_stack
 * Return a pointer to the current stack.
 */

BA0_DLL struct ba0_stack *
ba0_current_stack (
    void)
{
  return ba0_global.stack.stack_of_stacks.tab[ba0_global.stack.stack_of_stacks.
      size - 1];
}

/*
 * For information.
 * Return the maximum allocated memory in the stack H
 */

/*
 * texinfo: ba0_max_alloc_stack
 * Return the maximal number of bytes which has been used in @var{H}.
 */

BA0_DLL unsigned ba0_int_p
ba0_max_alloc_stack (
    struct ba0_stack *H)
{
  unsigned ba0_int_p sum;
  ba0_int_p i;

  sum = 0;
  for (i = 0; i <= H->max_alloc.index_in_cells; i++)
    sum += H->sizes.tab[i];
  sum -= H->max_alloc.memory_left;
  return sum;
}

/*
 * Initializes H
 * Called by ba0_restart. 
*/

/*
 * texinfo: ba0_init_stack
 * Initialize the stack @var{H}. 
 * The field @code{resizable} is set to true.
 */

BA0_DLL void
ba0_init_stack (
    struct ba0_stack *H)
{
  if (H == &ba0_global.stack.main)
    {
      H->default_size = ba0_sizeof_main_cell;
      H->ident = "main";
    }
  else if (H == &ba0_global.stack.second)
    {
      H->default_size = ba0_sizeof_main_cell;
      H->ident = "second";
    }
  else if (H == &ba0_global.stack.analex)
    {
      H->default_size = ba0_sizeof_analex_cell;
      H->ident = "analex";
    }
  else if (H == &ba0_global.stack.quiet)
    {
      H->default_size = ba0_sizeof_quiet_cell;
      H->ident = "quiet";
    }
  else if (H == &ba0_global.stack.format)
    {
      H->default_size = ba0_sizeof_quiet_cell;
      H->ident = "format";
    }
  else
    {
      H->default_size = ba0_sizeof_quiet_cell;
      H->ident = "a non predefined stack";
    }

  ba0_init_table (&H->cells);
  ba0_init_table ((struct ba0_table *) &H->sizes);
  ba0_re_malloc_table (&H->cells, ba0_nb_cells_per_stack);
  ba0_re_malloc_table ((struct ba0_table *) &H->sizes, ba0_nb_cells_per_stack);

  H->resizable = true;

  ba0_set_mark (&H->free, H, -1, (void *) 0, 0);
  H->max_alloc = H->free;
  H->nb_calls_to_alloc = 0;
#if defined (BA0_MEMCHECK)
  H->bound = &magic;
#endif
}

/*
 * texinfo: ba0_init_one_cell_stack
 * Initialize the stack @var{H} with the cell @var{cell}, which is 
 * assumed to have size @var{cell_size}. This stack can afterwards be used
 * as any other stack. The stack has its field @code{resizable}
 * set to false, so that, if an extra cell needs to be allocated, then
 * the exception @code{BA0_ERROOM} is raised.
 */

BA0_DLL void
ba0_init_one_cell_stack (
    struct ba0_stack *H,
    char *ident,
    void *cell,
    ba0_int_p cell_size)
{
  H->ident = ident;

  ba0_init_table (&H->cells);
  ba0_init_table ((struct ba0_table *) &H->sizes);

  ba0_re_malloc_table (&H->cells, 1);
  ba0_re_malloc_table ((struct ba0_table *) &H->sizes, 1);

  H->cells.tab[0] = cell;
  H->cells.size = 1;

  H->sizes.tab[0] = cell_size;
  H->sizes.size = 1;

  H->default_size = cell_size;

  H->resizable = false;

  ba0_set_mark (&H->free, H, -1, (void *) 0, 0);
  H->max_alloc = H->free;

  H->nb_calls_to_alloc = 0;
#if defined (BA0_MEMCHECK)
  H->bound = &magic;
#endif
}

/*
 * texinfo: ba0_clear_one_cell_stack
 * Free the arrays @code{cells.tab} and @code{sizes.tab} the
 * stack @var{H} but does not free the unique cell of @var{H}.
 */

BA0_DLL void
ba0_clear_one_cell_stack (
    struct ba0_stack *H)
{
  ba0_free (H->cells.tab);
  ba0_free (H->sizes.tab);
}

/*
 * Logically frees H
 */

/*
 * texinfo: ba0_reset_stack
 * Empty the stack @var{H} but does not free the allocated cells.
 */

BA0_DLL void
ba0_reset_stack (
    struct ba0_stack *H)
{
  ba0_set_mark (&H->free, H, -1, (void *) 0, 0);
#if defined (BA0_MEMCHECK)
  H->bound = &magic;
#endif
}

/*
 * Logically frees the content of the current cell of H
 */

/*
 * texinfo: ba0_reset_cell_stack
 * Empty the current cell of the stack @var{H}.
 */

BA0_DLL void
ba0_reset_cell_stack (
    struct ba0_stack *H)
{
  if (H->cells.size == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  ba0_set_mark (&H->free, H, H->free.index_in_cells,
      H->cells.tab[H->free.index_in_cells],
      H->sizes.tab[H->free.index_in_cells]);
}

/*
 * Physically frees the cells
 * Called by ba0_terminate. 
 */

/*
 * texinfo: ba0_clear_cells_stack
 * Empty the stack @var{H} and frees the allocated cells.
 */

BA0_DLL void
ba0_clear_cells_stack (
    struct ba0_stack *H)
{
  ba0_reset_stack (H);
  while (H->cells.size > 0)
    {
      ba0_free (H->cells.tab[H->cells.size - 1]);
      H->cells.tab[H->cells.size - 1] = (void *) 0;
      ba0_malloc_counter -= H->sizes.tab[H->sizes.size - 1];
      H->cells.size -= 1;
      H->sizes.size -= 1;
    }
}

/*
 * Free the cells and the arrays H->cells.tab and H->sizes.tab
 */

/*
 * texinfo: ba0_clear_stack
 * Empty the stack @var{H}, free the allocated cells and
 * the arrays @code{cells.tab} and @code{sizes.tab} of stack @var{H}.
 */

BA0_DLL void
ba0_clear_stack (
    struct ba0_stack *H)
{
  ba0_clear_cells_stack (H);
  ba0_free (H->cells.tab);
  ba0_free (H->sizes.tab);
  ba0_malloc_counter -= H->cells.alloc * sizeof (void *);
  ba0_malloc_counter -= H->sizes.alloc * sizeof (ba0_int_p);
}

/*
 * Subfunction of ba0_alloc.
 * Allocates at least n bytes in the current stack.
 * An extra area is appended to the allocated n bytes to store a magic number.
 * The magic number is *not* stored.
 */

static void *ba0_alloc_but_do_not_set_magic_mark (
    struct ba0_mark *,
    unsigned ba0_int_p);

BA0_DLL void *
ba0_alloc_but_do_not_set_magic (
    unsigned ba0_int_p n)
{
  struct ba0_stack *H;
  void *m;

  H = ba0_current_stack ();
#if defined (BA0_MEMCHECK)
  if (*H->bound != magic)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  n += BA0_ALIGN;
#endif
  n = ba0_ceil_align (n);

  m = ba0_alloc_but_do_not_set_magic_mark (&H->free, n);

  H->nb_calls_to_alloc++;
  ba0_alloc_counter += n;

  if (H->free.index_in_cells > H->max_alloc.index_in_cells ||
      (H->free.index_in_cells == H->max_alloc.index_in_cells &&
          (unsigned ba0_int_p) H->free.address >
          (unsigned ba0_int_p) H->max_alloc.address))
    H->max_alloc = H->free;
#if defined (BA0_MEMCHECK)
  H->bound = (ba0_int_p *) (void *) ((unsigned ba0_int_p) m + n - BA0_ALIGN);
#endif
  return m;
}

/*
 * Subfunction of ba0_alloc
 */

BA0_DLL void
ba0_alloc_set_magic (
    void)
{
#if defined (BA0_MEMCHECK)
  struct ba0_stack *H;
  H = ba0_current_stack ();
  *H->bound = magic;
#endif
}

/*
 * Allocates n bytes (+ magic number) in the current stack.
 */

/*
 * texinfo: ba0_alloc
 * Allocate @var{n} bytes in the current stack.
 * The number @var{n} must be nonzero. 
 * A mechanism is implemented which ensures that memory is always aligned.
 * Moreover, the function allocates a bit more memory than @var{n} bytes
 * and stores a magic number at the tail of the @var{n} bytes. 
 * This magic number is used to detect at runtime pointers running out of 
 * allocated data: the next call to the function will check that the 
 * stored magic numbered is not erased. If it is, an exception is raised.
 */

BA0_DLL void *
ba0_alloc (
    unsigned ba0_int_p n)
{
  void *p;

  p = ba0_alloc_but_do_not_set_magic (n);
  ba0_alloc_set_magic ();
  return p;
}

/*
 * Returns the amount of memory that could be allocated in the
 * current stack without moving to the next cell.
 */

/*
 * texinfo: ba0_memory_left_in_cell
 * Return the amount of memory that could be allocated in the current
 * stack without moving the free pointer to the next cell. 
 */

BA0_DLL unsigned ba0_int_p
ba0_memory_left_in_cell (
    void)
{
  struct ba0_stack *H;
  unsigned ba0_int_p available;

  H = ba0_current_stack ();
  available = ba0_floor_align (H->free.memory_left);
#if defined (BA0_MEMCHECK)
  if (available >= BA0_ALIGN)
    available -= BA0_ALIGN;
#endif
  return available;
}


/*
 * Specific array allocation for polynomials.
 * If the array does not fit in the current cell, then its size is decreased.
 */

/*
 * texinfo: ba0_t2_alloc
 * 
 * Variant of the above function. 
 * Two arrays of the same number of elements @var{tc} and @var{tt} 
 * must be allocated. The desired number of elements is @var{n} which
 * may be decreased if any of the arrays does not fit in a cell.
 * The actual number of allocated elements is stored in @var{m}.
 * The elements of the arrays have respective sizes @var{sc} and @var{st}.
 */

BA0_DLL void
ba0_t2_alloc (
    unsigned ba0_int_p sc,
    unsigned ba0_int_p st,
    unsigned ba0_int_p n,
    void **tc,
    void **tt,
    unsigned ba0_int_p *m)
{
  struct ba0_stack *H;
  unsigned ba0_int_p cell_size;

  H = ba0_current_stack ();
  if (n == 0 || sc == 0 || st == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (sc < st)
    {
      BA0_SWAP (ba0_int_p, sc, st);
      BA0_SWAP (void **,
          tc,
          tt);
    }

  cell_size = H->sizes.tab[H->sizes.size - 1];

  if (2 * n * sc <= H->free.memory_left)
    *m = n;
  else if (H->free.memory_left > cell_size / 128)
    *m = H->free.memory_left / (2 * sc);
  else
    {
      *m = cell_size / (2 * sc);
      *m = BA0_MIN (n, *m);
    }

  *tc = ba0_alloc (*m * sc);
  *tt = ba0_alloc (*m * st);
}

/*
 * Variant of the above one.
 */

/*
 * texinfo: ba0_t1_alloc
 * 
 * One wishes to allocate an array @var{te} of @var{n} elements.
 * Each element has size @var{se}.
 * It may happen that @var{n} is too large to stand in a cell.
 * This function decreases @var{n} if needed.
 * The number of elements actually allocated is stored in @var{m}.
 */

BA0_DLL void
ba0_t1_alloc (
    unsigned ba0_int_p se,
    unsigned ba0_int_p n,
    void **te,
    unsigned ba0_int_p *m)
{
  struct ba0_stack *H;
  unsigned ba0_int_p cell_size;

  H = ba0_current_stack ();
  if (n == 0 || se == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  cell_size = H->sizes.tab[H->sizes.size - 1];

  if (n * se <= H->free.memory_left)
    *m = n;
  else if (H->free.memory_left > cell_size / 128)
    *m = H->free.memory_left / se;
  else
    {
      *m = cell_size / se;
      *m = BA0_MIN (n, *m);
    }

  *te = ba0_alloc (*m * se);
}

/**********************************************************************
 THE STACK OF STACKS
 **********************************************************************/

/*
 * texinfo: ba0_init_stack_of_stacks
 * Initialize the stack of stacks array.
 */

BA0_DLL void
ba0_init_stack_of_stacks (
    void)
{
  ba0_init_table ((struct ba0_table *) &ba0_global.stack.stack_of_stacks);
  ba0_re_malloc_table ((struct ba0_table *) &ba0_global.stack.stack_of_stacks,
      ba0_sizeof_stack_of_stack);
  ba0_reset_stack_of_stacks ();
}

/*
 * texinfo: ba0_reset_stack_of_stacks
 * Reset @code{ba0_global.stack.stack_of_stacks} and push @code{ba0_global.stack.main}
 * which then becomes the current stack.
 */

BA0_DLL void
ba0_reset_stack_of_stacks (
    void)
{
  ba0_global.stack.stack_of_stacks.tab[0] = &ba0_global.stack.main;
  ba0_global.stack.stack_of_stacks.size = 1;
}

/*
 * texinfo: ba0_clear_stack_of_stacks
 * Free the area allocated to @code{ba0_global.stack.stack_of_stacks}.
 */

BA0_DLL void
ba0_clear_stack_of_stacks (
    void)
{
  ba0_free (ba0_global.stack.stack_of_stacks.tab);
  ba0_malloc_counter -=
      sizeof (struct ba0_stack *) * ba0_global.stack.stack_of_stacks.alloc;
}

/*
 * After this call, H becomes the current stack.
 */

/*
 * texinfo: ba0_push_stack
 * Push the stack @var{H} on the top of @code{ba0_global.stack.stack_of_stacks}.
 * Then @var{H} becomes the new current stack.
 */

BA0_DLL void
ba0_push_stack (
    struct ba0_stack *H)
{
  if (ba0_global.stack.stack_of_stacks.size ==
      ba0_global.stack.stack_of_stacks.alloc)
    ba0_re_malloc_table ((struct ba0_table *) &ba0_global.stack.stack_of_stacks,
        2 * ba0_global.stack.stack_of_stacks.alloc);
  ba0_global.stack.stack_of_stacks.tab[ba0_global.stack.stack_of_stacks.size] =
      H;
  ba0_global.stack.stack_of_stacks.size += 1;
}

/*
 * texinfo: ba0_pull_stack
 * Undo the previous call to @code{ba0_push_stack}.
 */

BA0_DLL void
ba0_pull_stack (
    void)
{
  ba0_global.stack.stack_of_stacks.size -= 1;
  if (ba0_global.stack.stack_of_stacks.size < 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
}

/*
 * texinfo: ba0_push_another_stack
 * Push on the top of the stack of stacks a stack which is different from
 * the current one. The chosen stack is either @code{ba0_global.stack.main}
 * of @code{ba0_global.stack.second}.
 */

BA0_DLL void
ba0_push_another_stack (
    void)
{
  if (ba0_global.stack.stack_of_stacks.tab[ba0_global.stack.stack_of_stacks.
          size - 1] != &ba0_global.stack.main)
    ba0_push_stack (&ba0_global.stack.main);
  else
    ba0_push_stack (&ba0_global.stack.second);
}

/**********************************************************************
   MARKS
 **********************************************************************/

/*
 * A mark is essentially a pointer in a stack.
 */

static void
ba0_set_mark (
    struct ba0_mark *M,
    struct ba0_stack *H,
    ba0_int_p index_in_cells,
    void *address,
    unsigned ba0_int_p memory_left)
{
  M->stack = H;
  M->index_in_cells = index_in_cells;
  M->address = address;
  M->memory_left = memory_left;
}

/*
 * texinfo: ba0_cell_index_mark
 * The pointer @var{p} is assumed to point in the stack referred to by @var{M}.
 * The function returns the index, in the @code{cells} array, of the cell
 * @var{p} points to. The function searches between the beginning of the stack and
 * @var{M}. Returns @math{-1} if not found.
 */

BA0_DLL ba0_int_p
ba0_cell_index_mark (
    void *p,
    struct ba0_mark *M)
{
  struct ba0_stack *H = M->stack;
  unsigned ba0_int_p deb, fin;
  ba0_int_p i;

  for (i = 0; i < M->index_in_cells; i++)
    {
      deb = (unsigned ba0_int_p) H->cells.tab[i];
      fin = deb + H->sizes.tab[i];
/* <= fin rather than < fin. Bug in bap/tests/gcd6 */
      if ((unsigned ba0_int_p) p >= deb && (unsigned ba0_int_p) p <= fin)
        return i;
    }
  deb = (unsigned ba0_int_p) H->cells.tab[M->index_in_cells];
  fin = (unsigned ba0_int_p) M->address;
  if ((unsigned ba0_int_p) p >= deb && (unsigned ba0_int_p) p <= fin)
    return i;
  return -1;
}

/*
 * M is pointing to a cell which is full. Move M to the next cell.
 */

static void
ba0_move_to_next_cell_mark (
    struct ba0_mark *M)
{
  struct ba0_stack *H = M->stack;

  if (M->index_in_cells + 1 == H->cells.size)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  M->index_in_cells += 1;
  M->address = H->cells.tab[M->index_in_cells];
  M->memory_left = H->sizes.tab[M->index_in_cells];
}

/*
 * If M is the free pointer of a stack, allocates n bytes of memory.
 * The number n is assumed to be already aligned.
 * If needed, the default_size of the stack is increased.
 *
 * This function is sometimes called also with marks which are not
 * not free pointers of stacks. 
 */

static void *
ba0_alloc_but_do_not_set_magic_mark (
    struct ba0_mark *M,
    unsigned ba0_int_p n)
{
  struct ba0_stack *H;
  void *m;

  m = M->address;
  if (n <= M->memory_left)
    {
      M->address = (void *) ((unsigned ba0_int_p) m + n);
      M->memory_left -= n;
    }
  else
    {
      H = M->stack;
/*
 * If ba0_move_to_next_cell_mark does not allocate, let us do it.
 */
      if (M->index_in_cells + 1 < H->cells.size)
        ba0_move_to_next_cell_mark (M);
/*
 * Let us skip all cells (without allocating) which are too small
 */
      while (M->index_in_cells + 1 < H->cells.size && n > M->memory_left)
        ba0_move_to_next_cell_mark (M);
/*
 * Either we have found a large enough cell or ... we have not
 */
      if (n > M->memory_left)
        {
          if (!H->resizable)
            BA0_RAISE_EXCEPTION (BA0_ERROOM);
/*
 * No already allocated cell is large enough
 */
          if (n >= H->default_size)
            {
/*
 * Increase the default size if needed
 */
              H->default_size = n;
            }
/*
 * Resize the tables cells and sizes if needed
 */
          if (H->cells.size == H->cells.alloc)
            {
              ba0_re_malloc_table ((struct ba0_table *) &H->cells,
                  2 * H->cells.alloc);
              ba0_re_malloc_table ((struct ba0_table *) &H->sizes,
                  2 * H->sizes.alloc);
            }
/*
 * Allocate a cell large enough
 */
          H->cells.tab[H->cells.size] = ba0_malloc (H->default_size);
          H->sizes.tab[H->sizes.size] = H->default_size;
          H->cells.size += 1;
          H->sizes.size += 1;
/*
 * The next cell exists and is large enough
 */
          ba0_move_to_next_cell_mark (M);
        }
/*
 * The current cell is large enough
 */
      m = M->address;
      M->address = (void *) ((unsigned ba0_int_p) m + n);
      M->memory_left -= n;
    }
  return m;
}

/*
 * texinfo: ba0_alloc_mark
 * Simulate an allocation of @var{n} bytes by @code{ba0_alloc} assuming
 * that the free pointer is @var{M}. Move @var{M} to the new value of
 * the free pointer.
 */

BA0_DLL void *
ba0_alloc_mark (
    struct ba0_mark *M,
    unsigned ba0_int_p n)
{
  void *m;
  n = ba0_allocated_size (n);
  m = ba0_alloc_but_do_not_set_magic_mark (M, n);
  return m;
}

/*
   Performs a rotation between some cells of the current stack :

   Let n = cells.size - 1

            -----------------------------------------
   Before : | 0 | 1 | ... | i-1 | i | i+1 | ... | n |
            -----------------------------------------

            -----------------------------------------
   After  : | 0 | 1 | ... | i-1 | i+1 | ... | n | i |
            -----------------------------------------

   The index i must be strictly less than the index of the free pointer.

   Use with care. Marks pointing to the current stack may become corrupted.
   Only used by the lexical analyzer which makes use of fifo.
*/

/*
 * texinfo: ba0_rotate_cells
 * Perform a rotation between the cells of the current stack located
 * at indices greater than or equal to @var{i}. The cell number @var{i}
 * gets located at the end of the cells table. The index @var{i} must
 * be strictly less than the index of the free pointer.
 * This function should be used with a lot of care.
 * It is called by the lexical analyzer.
 */

BA0_DLL void
ba0_rotate_cells (
    ba0_int_p i)
{
  struct ba0_stack *H;
  void *cell;
  unsigned ba0_int_p size;

  H = ba0_current_stack ();
  if (H->cells.size <= i || H->free.index_in_cells <= i)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  cell = H->cells.tab[i];
  memmove (H->cells.tab + i, H->cells.tab + i + 1,
      (H->cells.size - i - 1) * sizeof (void *));
  H->cells.tab[H->cells.size - 1] = cell;

  size = H->sizes.tab[i];
  memmove (H->sizes.tab + i, H->sizes.tab + i + 1,
      (H->sizes.size - i - 1) * sizeof (ba0_int_p));
  H->sizes.tab[H->sizes.size - 1] = size;

  H->free.index_in_cells -= 1;
  H->max_alloc.index_in_cells -= 1;
}

/*
 * texinfo: ba0_record
 * Record in @var{M} the value of the free pointer of the current stack.
 */

BA0_DLL void
ba0_record (
    struct ba0_mark *M)
{
  struct ba0_stack *H;

  H = ba0_current_stack ();
  ba0_process_check_interrupt ();
  *M = H->free;
}

/*
 * texinfo: ba0_restore
 * Restore the value of the free pointer which was stored in @var{M}
 * by a previous call to @code{ba0_record}.
 */

BA0_DLL void
ba0_restore (
    struct ba0_mark *M)
{
  struct ba0_stack *H = M->stack;

  if (M->index_in_cells > H->free.index_in_cells ||
      (M->index_in_cells == H->free.index_in_cells &&
          (unsigned ba0_int_p) M->address >
          (unsigned ba0_int_p) H->free.address))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  H->free = *M;
}

/*
 * texinfo: ba0_range_mark
 * Return the amount of memory enclosed between the two marks.
 * The mark @var{A} is assumed pointing to an area before the mark @var{B}.
 */

BA0_DLL unsigned ba0_int_p
ba0_range_mark (
    struct ba0_mark *A,
    struct ba0_mark *B)
{
  struct ba0_mark M;
  unsigned ba0_int_p range;

  if (A->stack != B->stack || A->index_in_cells > B->index_in_cells)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  M = *A;
  range = 0;
  while (M.index_in_cells < B->index_in_cells)
    {
      range += M.memory_left;
      ba0_move_to_next_cell_mark (&M);
    }
  range += (M.memory_left - B->memory_left);
  return range;
}
