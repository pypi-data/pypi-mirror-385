#if !defined (BA0_SMALL_P_H)
#   define BA0_SMALL_P_H 1

#   include "ba0_common.h"

BEGIN_C_DECLS

extern BA0_DLL ba0_mint_hp ba0_largest_small_prime (
    void);

extern BA0_DLL ba0_mint_hp ba0_smallest_small_prime (
    void);

extern BA0_DLL ba0_mint_hp ba0_next_small_prime (
    ba0_mint_hp);

extern BA0_DLL ba0_mint_hp ba0_previous_small_prime (
    ba0_mint_hp);

END_C_DECLS
#endif /* !BA0_SMALL_P_H */
