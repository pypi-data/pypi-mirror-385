#if !defined (BA0_PRINTF_H)
#   define BA0_PRINTF_H 1

#   include "ba0_common.h"
#   include "ba0_format.h"

BEGIN_C_DECLS

extern BA0_DLL void ba0__printf__ (
    struct ba0_format *,
    void **);

extern BA0_DLL void ba0_printf (
    char *,
    ...);

extern BA0_DLL void ba0_sprintf (
    char *,
    char *,
    ...);

extern BA0_DLL void ba0_fprintf (
    FILE *,
    char *,
    ...);

extern BA0_DLL char *ba0_new_printf (
    char *,
    ...);

END_C_DECLS
#endif /* !BA0_PRINTF_H */
