#if !defined (BAP_COMMON_H)
#   define BAP_COMMON_H 1

#   include <bav.h>

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
 * The flag BAP_BLAD_BUILDING must thus be set in the Makefile and passed
 * to the C preprocessor at BAP building time. Do not set it when using BAP.
 *
 * When compiling static libraries under Windows, set BA0_STATIC.
 */

#   if defined (_MSC_VER) && ! defined (BA0_STATIC)
#      if defined (BLAD_BUILDING) || defined (BAP_BLAD_BUILDING)
#         define BAP_DLL  __declspec(dllexport)
#      else
#         define BAP_DLL  __declspec(dllimport)
#      endif
#   else
#      define BAP_DLL
#   endif

#   include "bap_mesgerr.h"

BEGIN_C_DECLS

/*
 * texinfo: bap_composite_number
 * This data structure aims at numbering elements which belong to
 * a sequence of elements implemented by means of tables of tables. 
 * Assume an element lies in @code{T->tab[i]->tab[j]}. Then 
 * @code{primary} is equal to @math{i}, 
 * @code{secondary} is equal to @math{j} and 
 * @code{combined}, the index of the element in the sequence, 
 * is equal to @math{j} plus the sum, for @math{0 \leq k < i} of 
 * @code{T->tab[k]->size}.
 */

struct bap_composite_number
{
  ba0_int_p primary;
  ba0_int_p secondary;
  ba0_int_p combined;
};

/*
 * texinfo: bap_typeof_monom_access
 * This data type permits to indicate the access which applies
 * to a polynomial.
 */

enum bap_typeof_monom_access
{
  bap_sequential_monom_access,
  bap_indexed_monom_access
};

/*
 * texinfo: bap_typeof_total_rank
 * This data type provides information on a @code{total_rank} field
 * while creating a polynomial, monomial per monomial.
 */

enum bap_typeof_total_rank
{
  bap_exact_total_rank,
  bap_approx_total_rank
};

/*
 * texinfo: bap_rank_code
 * This data type is used as return code for comparing ranks.
 */

enum bap_rank_code
{
  bap_rank_too_low,
  bap_rank_ok,
  bap_rank_too_high
};

extern BAP_DLL void bap_reset_all_settings (
    void);

extern BAP_DLL void bap_restart (
    ba0_int_p,
    ba0_int_p);

extern BAP_DLL void bap_terminate (
    enum ba0_restart_level);

extern BAP_DLL ba0_int_p bap_ceil_log2 (
    ba0_int_p);

END_C_DECLS
#endif /* !BAP_COMMON_H */
