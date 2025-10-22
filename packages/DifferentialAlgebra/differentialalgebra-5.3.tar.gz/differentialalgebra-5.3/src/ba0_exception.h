#if !defined (BA0_EXCEPTION_H)
#   define BA0_EXCEPTION_H

#   include "ba0_common.h"
#   include "ba0_stack.h"
#   include "ba0_analex.h"
#   include "ba0_mesgerr.h"

BEGIN_C_DECLS

/*
 * Depending on the architecture, the implementation differs.
 * It is simpler to bundle jmpbuf in a struct
 */

struct ba0_jmp_buf_struct
{
  ba0_jmp_buf data;
};

/* 
 * Used by ba0_global.exception
 * The size of the exception stack.
 * The size of the exception log fifo.
 * The size of the extra stack is used also in ba0_exception_code
 */

#   define BA0_SIZE_EXCEPTION_STACK	100
#   define BA0_SIZE_EXCEPTION_LOG	10
#   define	BA0_SIZE_EXCEPTION_EXTRA_STACK 10

/* 
 * texinfo: ba0_exception
 * This data type implements the data stored in the entries of
 * @code{ba0_global.exception.stack}. These entries are filled when an
 * exception catching point is set. They are used for restoring
 * values when an exception is caught.
 */

struct ba0_exception
{
  struct ba0_jmp_buf_struct jmp_b;      // for setjmp/longjmp
// a pointer to the local variable __code__ set by BA0_TRY
  struct ba0_exception_code *code;
};

/* 
 * texinfo: ba0_exception_code
 * The data type for local variables @code{__code__} set by @code{BA0_TRY}.
 */

struct ba0_exception_code
{
// a copy of ba0_global.exception.stack.size for debugging purpose
  ba0_int_p exception_stack_size;
  bool cancelled;               // set to true by BA0_ENDTRY
  int jmp_code;                 // the returned value of setjmp
// values recorded when an exception catching point is set
  struct ba0_mark main;         // the free pointer of the main stack
  struct ba0_mark second;       // the one of the second stack
  ba0_int_p stack_of_stacks_size;       // the field size of the stack of stacks
// values of extra variables to be saved/restored
// the pointers to the variables are in ba0_global.exception.extra_stack
  struct
  {
    ba0_int_p tab[BA0_SIZE_EXCEPTION_EXTRA_STACK];
    ba0_int_p size;
  } extra_stack;
};

/* 
 * The macros for throwing exceptions
 */

#   define BA0_RAISE_EXCEPTION(msg) ba0_raise_exception (__FILE__, __LINE__, msg)

#   define BA0_RE_RAISE_EXCEPTION ba0_raise_exception (__FILE__, __LINE__, ba0_global.exception.raised)

#   define BA0_RAISE_PARSER_EXCEPTION(msg) do { \
    ba0_write_context_analex ();	      \
    ba0_raise_exception (__FILE__, __LINE__, msg); \
    } while (0)

#   define BA0_RAISE_EXCEPTION2(msg,f,o) \
	ba0_raise_exception2 (__FILE__, __LINE__, msg, f, (void **) o)

#   define BA0_CERR(msg) ba0_cerr (__FILE__, __LINE__, msg)

#   define BA0_ASSERT(condition) do { \
      if (!(condition)) BA0_RAISE_EXCEPTION (BA0_ERRALG) ; \
    } while (0)

/*
 * The macros for catching exceptions
 */

#   define BA0_TRY \
    { \
      struct ba0_exception_code __code__; \
      ba0_push_exception (&__code__);			\
      __code__.jmp_code = ba0_setjmp (ba0_global.exception.stack.tab [ba0_global.exception.stack.size-1].jmp_b.data,1);\
      if (ba0_exception_is_set (&__code__))

#   define BA0_CANCEL_EXCEPTION \
      ba0_pull_exception (&__code__);

#   define BA0_CATCH else

#   define BA0_ENDTRY \
      ba0_pull_exception (&__code__); \
    }

extern BA0_DLL void ba0_reset_exception_extra_stack (
    void);

extern BA0_DLL void ba0_push_exception_extra_stack (
    ba0_int_p *,
    void (*)(ba0_int_p));

extern BA0_DLL void ba0_pull_exception_extra_stack (
    void);

extern BA0_DLL void ba0_reset_exception (
    void);

extern BA0_DLL void ba0_push_exception (
    struct ba0_exception_code *);

extern BA0_DLL void ba0_pull_exception (
    struct ba0_exception_code *);

extern BA0_DLL bool ba0_exception_is_raised (
    struct ba0_exception_code *);

extern BA0_DLL bool ba0_exception_is_set (
    struct ba0_exception_code *);

extern BA0_DLL void ba0_raise_exception (
    char *,
    int,
    char *);

extern BA0_DLL void ba0_raise_exception2 (
    char *,
    int,
    char *,
    char *,
    void **);

extern BA0_DLL void ba0_cerr (
    char *,
    int,
    char *);

END_C_DECLS
#endif /* !BA0_EXCEPTION_H */
