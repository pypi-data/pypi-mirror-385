#if !defined (BAP_POLYSPEC_MINT_HP_H)
#   define BAP_POLYSPEC_MINT_HP_H 1

#   include "bap_common.h"
#   include "bap_polynom_mpz.h"
#   include "bap_polynom_mpzm.h"
#   include "bap_polynom_mpq.h"
#   include "bap_polynom_mint_hp.h"
#   include "bap_product_mint_hp.h"

BEGIN_C_DECLS
/* 
 * Polynomials with coefficients in Z/nZ where n is a small integer.
 * Precisely, polynomials with coefficients
 * 
 * ba0_mint_hp modulo ba0_mint_hp_module */
extern BAP_DLL void bap_polynom_mpq_to_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_polynom_mpz_to_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_random_eval_polynom_mpz_to_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mpz *,
    ba0_unary_predicate *);

extern BAP_DLL void bap_Berlekamp_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_polynom_mint_hp *);

END_C_DECLS
#endif /* !BAP_POLYSPEC_MINT_HP_H */
