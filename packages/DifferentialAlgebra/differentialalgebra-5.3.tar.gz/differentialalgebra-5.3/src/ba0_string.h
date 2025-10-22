#if !defined (BA0_STRING_H)
#   define BA0_STRING_H 1

#   include "ba0_common.h"

BEGIN_C_DECLS

struct ba0_tableof_string
{
  ba0_int_p alloc;
  ba0_int_p size;
  char **tab;
};

struct ba0_matrixof_string
{
  ba0_int_p alloc;
  ba0_int_p nrow;
  ba0_int_p ncol;
  char **entry;
};

struct ba0_listof_string
{
  char *value;
  struct ba0_listof_string *next;
};

struct ba0_tableof_tableof_string
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct ba0_tableof_string **tab;
};

extern BA0_DLL char *ba0_not_a_string (
    void);

extern BA0_DLL char *ba0_new_string (
    void);

extern BA0_DLL char *ba0_strdup (
    char *);

extern BA0_DLL char *ba0_strcat (
    struct ba0_tableof_string *);

/* 
 * redefined since they are not ANSI */

extern BA0_DLL int ba0_strcasecmp (
    char *,
    char *);

extern BA0_DLL int ba0_strncasecmp (
    char *,
    char *,
    size_t);

extern BA0_DLL ba0_scanf_function ba0_scanf_string;

extern BA0_DLL ba0_printf_function ba0_printf_string;

extern BA0_DLL ba0_garbage1_function ba0_garbage1_string;

extern BA0_DLL ba0_garbage2_function ba0_garbage2_string;

extern BA0_DLL ba0_copy_function ba0_copy_string;

extern BA0_DLL void ba0_set_tableof_string (
    struct ba0_tableof_string *,
    struct ba0_tableof_string *);

extern BA0_DLL bool ba0_member2_tableof_string (
    char *,
    struct ba0_tableof_string *,
    ba0_int_p *);

extern BA0_DLL unsigned ba0_int_p ba0_sizeof_tableof_string (
    struct ba0_tableof_string *,
    enum ba0_garbage_code);

END_C_DECLS
#endif /* !BA0_STRING_H */
