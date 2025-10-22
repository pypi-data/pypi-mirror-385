#if !defined (BAV_GLOBAL_H)
#   define BAV_GLOBAL_H 1

#   include "bav_common.h"
#   include "bav_differential_ring.h"
#   include "bav_term.h"


BEGIN_C_DECLS

struct bav_global
{
  struct
  {
/* 
 * Receives the faulty string when an unknown variable/symbol is parsed
 */
    char unknown[BA0_BUFSIZE];
  } common;
  struct bav_differential_ring R;
  struct
  {
/*
 * Flags indicating which input notation was used
 */
    ba0_int_p notations;
/* 
 * "diff" or "Diff" to display derivatives
 */
    char *diff_string;
  } variable;
  struct
  {
/* 
 * Comparison functions w.r.t. term orderings
 */
    enum ba0_compare_code (
        *compare) (
        struct bav_term *,
        struct bav_term *);
    enum ba0_compare_code (
        *compare_stripped) (
        struct bav_term *,
        struct bav_term *,
        bav_Inumber);
  } term_ordering;
};

struct bav_initialized_global
{
  struct
  {
/* 
 * Function called when an unknown symbol/variable/parameter is parsed.
 * Default bav_unknown_default
 */
    ba0_indexed_string_function *unknown;
  } common;
  struct
  {
/* 
 * Functions pointers for customizing symbol parsing and printing
 */
    ba0_scanf_function *scanf;
    ba0_printf_function *printf;
/*
 * If IndexedBase_PFE is not (char *)0, the radical z of every symbol
 * z[something] which fits some range indexed group is printed 
 * IndexedBase_PFE('z') leading to a symbol IndexedBase_PFE('z')[something].
 * This mechanism prevents some evaluation failures in Python. Default 0
 */
    char *IndexedBase_PFE;
  } symbol;
  struct
  {
/*
 * If Function_PFE is not (char *)0, every parameter p with nonempty
 * dependencies is printed Function_PFE('p')(dependencies).
 * This mechanism prevents some evaluation failures in Python. Default 0.
 */
    char *Function_PFE;
  } parameter;
  struct
  {
/* 
 * Functions pointers for customizing variable parsing and printing
 */
    ba0_scanf_function *scanf;
    ba0_printf_function *printf;
/*
 * The strings which stand for no derivation in the jet0 notation
 */
    char *jet0_input_string;
    char *jet0_output_string;
/* 
 * The prefix of temporary variables
 */
    char *temp_string;
  } variable;
  struct
  {
/* 
 * Function pointer for customizing the way ranks are printed.
 */
    ba0_printf_function *printf;
  } rank;
  struct
  {
/* 
 * The string for displaying orderings
 */
    char *string;
  } ordering;
};

extern BAV_DLL struct bav_global bav_global;

extern BAV_DLL struct bav_initialized_global bav_initialized_global;

/*
 * texinfo: bav_PFE_settings
 * This data structure is used to store copies of the settings variables
 * contained in the fields of @code{bav_initialized_global} which
 * contain @code{PFE} variables.
 */

struct bav_PFE_settings
{
  struct ba0_PFE_settings ba0;
  ba0_scanf_function *scanf;
  ba0_printf_function *printf;
  char *IndexedBase_PFE;
  char *Function_PFE;
};

END_C_DECLS
#endif /* !BAV_GLOBAL_H */
