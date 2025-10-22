#if !defined (BA0_INDEXED_STRING_H)
#   define BA0_INDEXED_STRING_H 1

#   include "ba0_common.h"

/*
 * blad_indent: -l120
 */

BEGIN_C_DECLS

struct ba0_indexed_string;

struct ba0_indexed_string_indices;

struct ba0_tableof_indexed_string
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct ba0_indexed_string **tab;
};

struct ba0_tableof_indexed_string_indices
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct ba0_indexed_string_indices **tab;
};


/*
 * texinfo: ba0_indexed_string_indices
 * This data type is a subtype of @code{struct ba0_indexed_string}.
 * It permits to store @dfn{indexed string indices}.
 */

struct ba0_indexed_string_indices
{
// the opening and closing parenthesis
  char po, pf;
  struct ba0_tableof_indexed_string Tindex;
};


/*
 * texinfo: ba0_indexed_string
 * This data type permits to represent @dfn{indexed strings}
 * which are strings endowed with indexed string indices.
 * It is used for parsing symbols and variables.
 * Here are a few examples of indexed strings accepted by parsers:
 * @code{u}, @code{u[1]}, @code{u[[1],-4,[[3]]]}, @code{u[x[e]]}.
 * @verbatim
 * INDEXED ::= string INDICES ... INDICES              (*)
 *         ::= signed integer INDICES ... INDICES
 *         ::= INDICES ... INDICES
 *
 * INDICES ::= (INDEXED, ..., INDEXED)
 *         ::= [INDEXED, ..., INDEXED]
 *
 * (*) At top level, this form is the only one accepted.
 * @end verbatim
 */

struct ba0_indexed_string
{
// the string or the signed integer as a string or (char *)0
  char *string;
// the table of the indexed string indices
  struct ba0_tableof_indexed_string_indices Tindic;
};


typedef void ba0_indexed_string_function (
    struct ba0_indexed_string *);

extern BA0_DLL void ba0_init_indexed_string (
    struct ba0_indexed_string *);

extern BA0_DLL void ba0_reset_indexed_string (
    struct ba0_indexed_string *);

extern BA0_DLL struct ba0_indexed_string *ba0_new_indexed_string (
    void);

extern BA0_DLL void ba0_set_indexed_string (
    struct ba0_indexed_string *,
    struct ba0_indexed_string *);

extern BA0_DLL char *ba0_indexed_string_to_string (
    struct ba0_indexed_string *);

extern BA0_DLL char *ba0_stripped_indexed_string_to_string (
    struct ba0_indexed_string *);

extern BA0_DLL bool ba0_has_empty_trailing_indices_indexed_string (
    struct ba0_indexed_string *,
    char);

extern BA0_DLL bool ba0_has_trailing_indices_indexed_string (
    struct ba0_indexed_string *,
    bool (*)(char *));

extern BA0_DLL bool ba0_has_numeric_trailing_indices_indexed_string (
    struct ba0_indexed_string *,
    struct ba0_tableof_int_p *);

extern BA0_DLL ba0_garbage1_function ba0_garbage1_indexed_string;

extern BA0_DLL ba0_garbage2_function ba0_garbage2_indexed_string;

extern BA0_DLL ba0_copy_function ba0_copy_indexed_string;

extern BA0_DLL ba0_printf_function ba0_printf_indexed_string;

/* 
 * The first one returns the struct ba0_indexed_string* data structure
 * The second one converts the data structure into a string
 */

extern BA0_DLL ba0_scanf_function ba0_scanf_indexed_string;

extern BA0_DLL ba0_scanf_function ba0_scanf_indexed_string_as_a_string;

extern BA0_DLL struct ba0_indexed_string *ba0_scanf_indexed_string_with_counter (
    struct ba0_indexed_string *,
    ba0_int_p *);

END_C_DECLS
#endif /* !BA0_INDEXED_STRING_H */
