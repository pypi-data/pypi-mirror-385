#if !defined (BA0_SCANF_H)
#   define BA0_SCANF_H 1

#   include "ba0_common.h"
#   include "ba0_format.h"

BEGIN_C_DECLS

extern BA0_DLL void ba0__scanf__ (
    struct ba0_format *,
    void **,
    bool);

extern BA0_DLL void ba0_scanf (
    char *,
    ...);

extern BA0_DLL void ba0_scanf2 (
    char *,
    ...);

extern BA0_DLL void ba0_sscanf (
    char *,
    char *,
    ...);

extern BA0_DLL void ba0_sscanf2 (
    char *,
    char *,
    ...);

extern BA0_DLL void ba0_fscanf (
    FILE *,
    char *,
    ...);

extern BA0_DLL void ba0_fscanf2 (
    FILE *,
    char *,
    ...);

END_C_DECLS
#endif /* !BA0_SCANF_H */
