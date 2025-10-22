#if !defined (BAV_TYPED_IDENT_H)
#   define BAV_TYPED_IDENT_H 1

#   include "bav_common.h"

BEGIN_C_DECLS

/*
 * texinfo: bav_typeof_ident
 * This data type is a subtype of @code{bav_typed_ident}.
 */

enum bav_typeof_ident
{
// The identifier is a plain string
  bav_plain_ident,
// The identifier is the radical of a range indexed string
  bav_range_indexed_string_radical_ident
};

/*
 * texinfo: bav_typed_ident
 * This data structure permits to associate a table of indices
 * to typed identifiers. 
 * As a substructure of @code{bav_ordering}, it associates to
 * any typed identifier three indices: the index of the block which
 * contains the identifier; the index of the identifier within
 * the block; the index of the identifier in the group (this last
 * index is only meaningful if the type is 
 * @code{bav_range_indexed_string_radical_ident}).
 */

struct bav_typed_ident
{
// the string - possibly (char *)0
  char *ident;
// its type
  enum bav_typeof_ident type;
// the indices associated to the typed ident
  struct ba0_tableof_int_p indices;
};

struct bav_tableof_typed_ident
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bav_typed_ident **tab;
};

struct bav_symbol;
struct bav_block;
struct bav_tableof_block;

extern BAV_DLL void bav_init_typed_ident (
    struct bav_typed_ident *);

extern BAV_DLL struct bav_typed_ident *bav_new_typed_ident (
    void);

extern BAV_DLL unsigned ba0_int_p bav_sizeof_typed_ident (
    struct bav_typed_ident *,
    enum ba0_garbage_code,
    bool);

extern BAV_DLL unsigned ba0_int_p bav_sizeof_tableof_typed_ident (
    struct bav_tableof_typed_ident *,
    enum ba0_garbage_code,
    bool);

struct bav_differential_ring;

extern BAV_DLL void bav_R_set_typed_ident (
    struct bav_typed_ident *,
    struct bav_typed_ident *,
    struct bav_differential_ring *);

extern BAV_DLL void bav_R_set_tableof_typed_ident (
    struct bav_tableof_typed_ident *,
    struct bav_tableof_typed_ident *,
    struct bav_differential_ring *);

extern BAV_DLL void bav_R_append_tableof_typed_ident_block (
    struct bav_tableof_typed_ident *,
    ba0_int_p,
    struct bav_block *,
    struct bav_differential_ring *);

extern BAV_DLL void bav_R_set_tableof_typed_ident_tableof_block (
    struct bav_tableof_typed_ident *,
    struct bav_tableof_block *,
    struct bav_differential_ring *);

extern BAV_DLL ba0_int_p bav_get_typed_ident_from_symbol (
    struct ba0_dictionary_typed_string *,
    struct bav_tableof_typed_ident *,
    struct bav_symbol *);

END_C_DECLS
#endif /* !BAV_TYPED_IDENT_H */
