#if !defined (BA0_FORMAT_H)
#   define BA0_FORMAT_H 1

#   include "ba0_common.h"

BEGIN_C_DECLS

/* 
 * The size of the H-Table for formats.
 * Should be a prime number.
 */

#   define BA0_SIZE_HTABLE_FORMAT      8009

/*
 * texinfo: ba0_typeof_format
 * This data type is a subtype of @code{ba0_subformat}.
 */

enum ba0_typeof_format
{
  ba0_leaf_format,
  ba0_table_format,
  ba0_list_format,
  ba0_matrix_format,
  ba0_array_format,
  ba0_value_format,
  ba0_point_format
};

struct ba0_format;

/*
 * texinfo: ba0_subformat
 * This data type is a subtype of @code{ba0_format}.
 * An element of this type describes a @code{%something}
 * substring of a format. Such substrings may have parameters.
 * Examples are: @code{%t[%v]} (tables of variables), 
 * @code{%l[%t[%z]]} (lists of tables of big integers).
 */

struct ba0_subformat
{
// The type of the subformat
  enum ba0_typeof_format code;
  union
  {
// If type is different from ba0_leaf_format
    struct _node
    {
// The format
      struct ba0_format *op;
// The opening parenthesis of the subformat parameter
      char po;
// The closing parenthesis
      char pf;
    } node;
// If type is ba0_leaf_format
    struct _leaf
    {
// The size of one data structure associated to the type
// and pointers towards associated functions
      ba0_int_p sizelt;
      ba0_scanf_function *scanf;
      ba0_printf_function *printf;
      ba0_garbage1_function *garbage1;
      ba0_garbage2_function *garbage2;
      ba0_copy_function *copy;
    } leaf;
  } u;
};


/*
 * texinfo: ba0_format
 * This data type describes a format, which is a string that can
 * be passed to functions such as @code{ba0_scanf}, @code{ba0_printf},
 * @code{ba0_copy} or @code{ba0_garbage}. Examples are:
 * @code{"poly = %Az\n"} or @code{"%t[%v], %qi"}.
 *
 * The subformats @code{%something} which occur in such strings
 * are preprocessed. 
 *
 * Each format is stored in a hash table of
 * formats, stored in the format stack whenever it is encountered.
 * Note that the addresses of the strings are hashed, not the
 * strings themselves.
 */

struct ba0_format
{
// the string
  char *text;
// an array of pointers towards the subformats of the string
  struct ba0_subformat **link;
// the number of subformats and the size of link
  ba0_int_p linknmb;
};


extern BA0_DLL void ba0_initialize_format (
    void);

extern BA0_DLL void ba0_define_format (
    char *,
    ba0_scanf_function *,
    ba0_printf_function *,
    ba0_garbage1_function *,
    ba0_garbage2_function *,
    ba0_copy_function *);

extern BA0_DLL void ba0_define_format_with_sizelt (
    char *,
    ba0_int_p,
    ba0_scanf_function *,
    ba0_printf_function *,
    ba0_garbage1_function *,
    ba0_garbage2_function *,
    ba0_copy_function *);

extern BA0_DLL struct ba0_format *ba0_get_format (
    char *);

extern BA0_DLL ba0_garbage1_function ba0_empty_garbage1;

extern BA0_DLL ba0_garbage2_function ba0_empty_garbage2;

struct ba0_pair
{
  char *identificateur;
  void *value;
};

struct ba0_tableof_pair
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct ba0_pair **tab;
};

END_C_DECLS
#endif /* !BA0_FORMAT_H */
