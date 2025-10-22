#if !defined (BAP_ITERATOR_INDEX_H)
#   define BAP_ITERATOR_INDEX_H 1

#   include "bap_common.h"
#   include "bap_indexed_access.h"

BEGIN_C_DECLS

/*
 * texinfo: bap_iterator_indexed_access
 * This data structure implements an iterator over 
 * a @code{bap_indexed_access} structure.
 */

struct bap_iterator_indexed_access
{
  struct bap_indexed_access *ind;       // the structure being read
  struct bap_composite_number num;      // the current index
};


extern BAP_DLL void bap_begin_iterator_indexed_access (
    struct bap_iterator_indexed_access *,
    struct bap_indexed_access *);

extern BAP_DLL void bap_end_iterator_indexed_access (
    struct bap_iterator_indexed_access *,
    struct bap_indexed_access *);

extern BAP_DLL bool bap_outof_iterator_indexed_access (
    struct bap_iterator_indexed_access *);

extern BAP_DLL void bap_next_iterator_indexed_access (
    struct bap_iterator_indexed_access *);

extern BAP_DLL void bap_prev_iterator_indexed_access (
    struct bap_iterator_indexed_access *);

extern BAP_DLL void bap_goto_iterator_indexed_access (
    struct bap_iterator_indexed_access *,
    ba0_int_p);

extern BAP_DLL ba0_int_p bap_index_iterator_indexed_access (
    struct bap_iterator_indexed_access *);

extern BAP_DLL ba0_int_p bap_read_iterator_indexed_access (
    struct bap_iterator_indexed_access *);

extern BAP_DLL void bap_swapindex_iterator_indexed_access (
    struct bap_iterator_indexed_access *,
    struct bap_iterator_indexed_access *);

extern BAP_DLL void bap_set_iterator_indexed_access (
    struct bap_iterator_indexed_access *,
    struct bap_iterator_indexed_access *);


/*
 * texinfo: bap_creator_indexed_access
 * This data structure permits to rewrite the content of a
 * @code{bap_indexed_access} structure, provided that the
 * already allocated tables are large enough.
 */

struct bap_creator_indexed_access
{
  struct bap_indexed_access *ind;       // the structure being rewritten
  struct bap_composite_number num;      // the current index
};


extern BAP_DLL void bap_begin_creator_indexed_access (
    struct bap_creator_indexed_access *,
    struct bap_indexed_access *);

extern BAP_DLL void bap_write_creator_indexed_access (
    struct bap_creator_indexed_access *,
    ba0_int_p);

extern BAP_DLL void bap_close_creator_indexed_access (
    struct bap_creator_indexed_access *);

END_C_DECLS
#endif /* !BAP_ITERATOR_INDEX_H */
