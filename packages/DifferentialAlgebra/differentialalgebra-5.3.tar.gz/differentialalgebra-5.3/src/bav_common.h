#if !defined (BAV_COMMON_H)
#   define BAV_COMMON_H 1

#   include <ba0.h>

/* 
 * The _MSC_VER flag is set if the code is compiled under WINDOWS
 * by using Microsoft Visual C (through Visual Studio 2008).
 *
 * In that case, some specific annotations must be added for DLL exports
 * Beware to the fact that this header file is going to be used either
 * for/while building BLAD or for using BLAD from an outer software.
 *
 * In the first case, functions are exported.
 * In the second one, they are imported.
 *
 * The flag BAV_BLAD_BUILDING must thus be set in the Makefile and passed
 * to the C preprocessor at BAV building time. Do not set it when using BAV.
 *
 * When compiling static libraries under Windows, set BA0_STATIC.
 */

#   if defined (_MSC_VER) && ! defined (BA0_STATIC)
#      if defined (BLAD_BUILDING) || defined (BAV_BLAD_BUILDING)
#         define BAV_DLL  __declspec(dllexport)
#      else
#         define BAV_DLL  __declspec(dllimport)
#      endif
#   else
#      define BAV_DLL
#   endif

#   include "bav_mesgerr.h"

BEGIN_C_DECLS

/*
 * texinfo: bav_Idegree
 * This is the integer type for degrees.
 */

typedef ba0_int_p bav_Idegree;

#   define BAV_MAX_IDEGRE BA0_MAX_INT_P

/*
 * texinfo: bav_Iorder
 * This is the integer type for differentiation orders.
 */

typedef ba0_int_p bav_Iorder;

/*
 * texinfo: bav_Iordering
 * This is the integer type for ordering numbers.
 */

typedef ba0_int_p bav_Iordering;

/*
 * texinfo: bav_Inumber
 * This is the integer type for variable numbers.
 */

typedef ba0_int_p bav_Inumber;

struct bav_tableof_Inumber
{
  ba0_int_p alloc;
  ba0_int_p size;
  bav_Inumber *tab;
};

struct bav_tableof_Iorder
{
  ba0_int_p alloc;
  ba0_int_p size;
  bav_Iorder *tab;
};

struct bav_tableof_Iordering
{
  ba0_int_p alloc;
  ba0_int_p size;
  bav_Iordering *tab;
};

struct bav_tableof_Idegree
{
  ba0_int_p alloc;
  ba0_int_p size;
  bav_Idegree *tab;
};

/* 
 * struct ba0_indexed_string* not recognized by parsers.
 * The function pointer, a buffer and the default value for the pointer
 */

extern BAV_DLL ba0_indexed_string_function bav_unknown_default;

extern BAV_DLL void bav_set_settings_common (
    ba0_indexed_string_function *);

extern BAV_DLL void bav_get_settings_common (
    ba0_indexed_string_function **);

extern BAV_DLL void bav_reset_all_settings (
    void);

struct bav_PFE_settings;

extern BAV_DLL void bav_cancel_PFE_settings (
    struct bav_PFE_settings *);

extern BAV_DLL void bav_restore_PFE_settings (
    struct bav_PFE_settings *);

extern BAV_DLL void bav_restart (
    ba0_int_p,
    ba0_int_p);

extern BAV_DLL void bav_terminate (
    enum ba0_restart_level);

END_C_DECLS
#endif /* !BAV_COMMON_H */
