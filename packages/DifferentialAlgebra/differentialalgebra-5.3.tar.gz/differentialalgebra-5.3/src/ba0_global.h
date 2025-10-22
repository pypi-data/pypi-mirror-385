#if ! defined (BA0_GLOBAL_H)
#   define BA0_GLOBAL_H 1

#   include "ba0_common.h"
#   include "ba0_exception.h"
#   include "ba0_garbage.h"
#   include "ba0_stack.h"
#   include "ba0_format.h"
#   include "ba0_basic_io.h"
#   include "ba0_analex.h"
#   include "ba0_gmp.h"
#   include "ba0_point.h"
#   include "ba0_range_indexed_group.h"
#   include "ba0_dictionary_string.h"

BEGIN_C_DECLS

/* 
 * texinfo: ba0_global
 * This data type is used for a single global variable.
 * Each field aims at customizing the behaviour of the @code{ba0} library.
 */

struct ba0_global
{
  struct
  {
/* 
 * Deprecated control for printing in LaTeX.
 * Used in ba0, bav and bap.
 */
    bool LaTeX;
/* 
 * Time out + Memory out + Interrupt checking
 *
 * time_limit           = the absolute value of the input time limit (restart)
 * memory_limit         = the input memory limit (restart)
 * switch_on_interrupt  = *check_interrupt should be called
 * within_interrupt     = bool to avoid self interruption
 * delay_interrupt      = the length of a time interval between two calls
 * before_timeout       = the overall remaining time before timeout
 * previous_time        = the value of time() when interrupt was last called
 */
    ba0_int_p time_limit;       /* local to ba0_common */
    ba0_int_p memory_limit;     /* local to ba0_common and ba0_stack */
    bool switch_on_interrupt;   /* local to ba0_common */
    bool within_interrupt;      /* local to ba0_common */
    time_t before_timeout;      /* local to ba0_common */
    time_t previous_time;       /* local to ba0_common */
  } common;
  struct
  {
/* 
 * The error/exception message.
 * Only set when raising an exception. Read everywhere.
 */
    char *raised;
    char mesg_cerr[BA0_BUFSIZE];
/* 
 * The stack of exception catching points.
 * Only set by the exception setting/raising MACROS.
 */
    struct
    {
      struct ba0_exception tab[BA0_SIZE_EXCEPTION_STACK];
      ba0_int_p size;
    } stack;
/* 
 * The stack of extra variables to be saved/restored when setting
 *      an exception point/raising an exception.
 * The field pointer points to the extra variable to be restored.
 * If the field restore is nonzero then it points to a function which is
 *      called in order to restore the extra variable with the value passed
 *      as a parameter.
 * The saved value is stored in a local variable at the catching point.
 */
    struct
    {
      struct
      {
        ba0_int_p *pointer;
        void (
            *restore) (
            ba0_int_p);
      } tab[BA0_SIZE_EXCEPTION_EXTRA_STACK];
      ba0_int_p size;
    } extra_stack;
/* 
 * bool to avoid self interruption
 */
    bool within_push_exception;
/*
 * A log fifo for debugging purposes
 * The entries of tab provide the sequence of file/line/exception raised
 *      since the last exception catching point was set.
 * The field qp contains the first free entry in tab
 */
    struct
    {
      struct
      {
        char *file;
        int line;
        char *raised;
      } tab[BA0_SIZE_EXCEPTION_LOG];
      ba0_int_p qp;
    } log;
  } exception;
  struct
  {
/* 
 * The garbage collector
 * tab                = an array for old->new addresses of areas
 * user_provided_mark = the mark M provided by garbage (format, M, ...)
 * ba0_current        = a running mark on struct ba0_gc_info(s)
 * old_free           = the value of the free pointer when garbage is called.
 *
 * All local to ba0_garbage. 
 * The values kept between two calls to ba0_garbage are meaningless.
 */
    struct ba0_gc_info **tab;
    struct ba0_mark user_provided_mark;
    struct ba0_mark current;
    struct ba0_mark old_free;
  } garbage;
  struct
  {
/* 
 * The predefined stacks. Used everywhere.
 */
    struct ba0_stack main;
    struct ba0_stack second;
    struct ba0_stack analex;
    struct ba0_stack quiet;
    struct ba0_stack format;
/* 
 * The current stack is the one on the top of stack_of_stacks.
 */
    struct ba0_tableof_stack stack_of_stacks;
/* 
 * For stats and debugging purposes.
 * Local to ba0_common, ba0_stack and ba0_analex.
 */
    ba0_int_p alloc_counter;
    ba0_int_p malloc_counter;
    ba0_int_p malloc_nbcalls;
  } stack;
  struct
  {
/* 
 * leaf_subformat = The formats defined by the library, such as %s, %d ...
 *                  Non-leaf formats are %t (tables) or %l (lists), .
 * htable         = The H-table of all the encountered formats.
 *                  Its size is a prime number. 
 * nbelem_htable  = The number of its elements.
 *
 * All are local to ba0_format.
 */
    struct ba0_tableof_pair leaf_subformat;
    struct ba0_tableof_pair htable;
    ba0_int_p nbelem_htable;
/* 
 * Management of the variables (scanf, printf) for the %value format.
 * Eventually, these pointers will point to bav_scanf_variable and
 * bav_printf_variable ... whenever these functions are defined (in bav).
 * Meanwhile, calling them raises BA0_ERRNYP
 */
    ba0_scanf_function *scanf_value_var;
    ba0_printf_function *printf_value_var;
  } format;
  struct
  {
/* 
 * output, input      = descriptions of the device in use.
 * output_line_length = to insert carriage returns. 
 *                      Reset by ba0_restart. Can be modified at runtime.
 *
 * All variables (except output_line_length) are local to ba0_basic_io.
 */
    struct ba0_output_device output_stack[BA0_BASIC_IO_SIZE_STACK];
    ba0_int_p output_sp;
    struct ba0_output_device output;
    ba0_int_p output_line_length;

    struct ba0_input_device input_stack[BA0_BASIC_IO_SIZE_STACK];
    ba0_int_p input_sp;
    struct ba0_input_device input;
  } basic_io;
  struct
  {
/* 
 * analex           = the FIFO of tokens
 * analex_save      = permits to record/restore analex (up to some point)
 * analex_save_full = indicates if analex_save is used
 * context          = an elaborated error message for parser errors
 *
 * subs_dict        = a pointer to a dictionary for performing token substitutions
 * subs_keys        = a pointer to the table which contains the dictionary keys
 * subs_vals        = a pointer to the table which contains the dictionary values
 */
    bool analex_save_full;
    struct ba0_analex_token_fifo analex;
    struct ba0_analex_token_fifo analex_save;

    char context[BA0_CONTEXT_LMAX];

    struct ba0_dictionary_string *subs_dict;
    struct ba0_tableof_string *subs_keys;
    struct ba0_tableof_string *subs_vals;
  } analex;
  struct
  {
/* 
 * These variables receive the values of the GMP memory functions before 
 * they get modified by BLAD.
 *
 * Set by ba0_restart. Read by ba0_terminate.
 * Set by ba0_process_check_interrupt before calling *check_interrupt
 * and restored afterwards.
 */
    bool alloc_function_called;
    void *(
        *alloc_function) (
        size_t);
    void *(
        *realloc_function) (
        void *,
        size_t,
        size_t);
    void (
        *free_function) (
        void *,
        size_t);
  } gmp;
  struct
  {
/* 
 * For computing in Z / module Z. Read everywhere.
 */
    bool module_is_prime;
    unsigned ba0_int_hp module;
  } mint_hp;
  struct
  {
/* 
 * For computing in Z / module Z with a GMP module. Read everywhere.
 */
    bool module_is_prime;
    ba0_mpz_t module;
    ba0_mpz_t half_module;
    ba0_mpz_t accum;
  } mpzm;
};

/*
 * texinfo: ba0_initialized_global
 * This data type is used by a single global variable.
 * It is decomposed into fields.
 * The values it contains permit to tune the library behaviour.
 */

struct ba0_initialized_global
{
  struct
  {
/* 
 * The only settings variable which is modified by ba0_restart/ba0_terminate.
 * Set by ba0_terminate. Read by all ba__restart functions.
 */
    enum ba0_restart_level restart_level;
/* 
 * check_interrupt = the pointer to the external check interrupt function,
 *                   called by ba0_process_check_interrupt.
 * delay_interrupt = the delay (in sec.) between two calls to *check_interrupt.
 * no_oot          = if true, ERRALR is disabled.
 */
    void (
        *check_interrupt) (
        void);
    time_t delay_interrupt;
    bool no_oot;
  } common;
  struct
  {
/* 
 * If true, the BLAD memory limit does not raise BA0_ERROOM.
 * Temporarily modified by all blad_restart functions.
 */
    bool no_oom;
  } malloc;
  struct
  {
    ba0_int_p sizeof_main_cell;
    ba0_int_p sizeof_quiet_cell;
    ba0_int_p sizeof_analex_cell;
    ba0_int_p nb_cells_per_stack;
    ba0_int_p sizeof_stack_of_stack;
/* 
 * Pointers to the functions that are called by BLAD for allocating/freeing
 * memory (mostly cells in stacks).
 */
    void *(
        *system_malloc) (
        size_t);
    void (
        *system_free) (
        void *);
  } stack;
  struct
  {
    ba0_set_memory_functions_function *set_memory_functions;
/*
 * If Integer_PFE is not (char *)0, every mpz_t z is printed Integer_PFE(z).
 * This mechanism prevents floating point evaluation of rational numbers
 *  in Python. Default value is (char *)0
 */
    char *Integer_PFE;
  } gmp;
  struct
  {
/* 
 * nb_tokens = the number of tokens in the analex FIFO
 * quotes    = a string containing the characters that can be used
 *              for quoting tokens
 */
    ba0_int_p nb_tokens;
    char *quotes;
  } analex;
  struct
  {
/*
 * The operator used for separating variable from values. Default "="
 */
    char *equal_sign;
  } value;
  struct
  {
/*
 * oper     = the range operator
 * infinity = the symbol for infinity
 * rhs_included = determines whether the right-hand side of range 
 *                indices should be included or not in the ranges
 * quote_PFE = if set to true, the range indexed groups which are not plain 
 *                strings are quoted when printed; this mechanism prevents 
 *                from evaluation failures in Python; default (char *)0
 */
    char *oper;
    char *infinity;
    bool rhs_included;
    bool quote_PFE;
  } range_indexed_group;
};

extern BA0_DLL struct ba0_global ba0_global;

extern BA0_DLL struct ba0_initialized_global ba0_initialized_global;

/*
 * texinfo: ba0_PFE_settings
 * This data structure is used to store copies of the settings variables
 * contained in the fields of @code{ba0_initialized_global} which
 * contain @code{PFE} variables.
 */

struct ba0_PFE_settings
{
  ba0_set_memory_functions_function *set_memory_functions;
  char *Integer_PFE;
  char *oper;
  char *infinity;
  bool rhs_included;
  bool quote_PFE;
};

END_C_DECLS
#endif /* !BA0_GLOBAL_H */
