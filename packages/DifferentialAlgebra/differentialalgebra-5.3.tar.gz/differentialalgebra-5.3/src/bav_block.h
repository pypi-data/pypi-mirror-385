#if !defined (BAV_BLOCK_H)
#   define BAV_BLOCK_H 1

#   include "bav_common.h"
#   include "bav_symbol.h"
#   include "bav_subranking.h"

BEGIN_C_DECLS

/*
 * texinfo: bav_block
 * A @dfn{block} is a list of range indexed groups defining differential
 * indeterminates (possibly also a single differential operator) 
 * ordered with respect to some common subranking. See the description 
 * of the data types @code{bav_subranking} and @code{bav_ordering}.
 */

struct bav_block
{
// the subranking which applies to the block
  struct bav_subranking *subr;
// the table of the range indexed groups of the block
  struct ba0_tableof_range_indexed_group rigs;
};

#   define BAV_NOT_A_BLOCK (struct bav_block*)0

struct bav_tableof_block
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bav_block **tab;
};

extern BAV_DLL void bav_init_block (
    struct bav_block *);

extern BAV_DLL void bav_reset_block (
    struct bav_block *);

extern BAV_DLL struct bav_block *bav_new_block (
    void);

extern BAV_DLL unsigned ba0_int_p bav_sizeof_block (
    struct bav_block *,
    enum ba0_garbage_code,
    bool);

extern BAV_DLL unsigned ba0_int_p bav_sizeof_tableof_block (
    struct bav_tableof_block *,
    enum ba0_garbage_code,
    bool);

struct bav_differential_ring;

extern BAV_DLL void bav_R_set_block (
    struct bav_block *,
    struct bav_block *,
    struct bav_differential_ring *);

extern BAV_DLL void bav_R_set_tableof_block (
    struct bav_tableof_block *,
    struct bav_tableof_block *,
    struct bav_differential_ring *);

extern BAV_DLL bool bav_is_empty_block (
    struct bav_block *);

extern BAV_DLL ba0_scanf_function bav_scanf_block;

extern BAV_DLL ba0_printf_function bav_printf_block;

END_C_DECLS
#endif /* !BAV_BLOCK_H */
