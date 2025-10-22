#if !defined (BAP_EVAL_POLYNOM_mint_hp_H)
#   define BAP_EVAL_POLYNOM_mint_hp_H 1

#   include "bap_polynom_mint_hp.h"

BEGIN_C_DECLS

#   define BAD_FLAG_mint_hp
#   if defined (BAD_FLAG_mpz) || defined (BAD_FLAG_mpzm) || defined (BAD_FLAG_mpq)

extern BAP_DLL void bap_set_point_polynom_mint_hp (
    struct ba0_point *,
    struct bap_polynom_mint_hp *,
    bool);

extern BAP_DLL void bap_eval_to_polynom_at_numeric_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *,
    ba0_mint_hp_t);
#   endif

#   if defined (BAD_FLAG_mpz) || defined (BAD_FLAG_mpzm)
extern BAP_DLL void bap_eval_to_polynom_at_value_int_p_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_value_int_p *);

extern BAP_DLL void bap_eval_to_polynom_at_point_int_p_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_point_int_p *);

extern BAP_DLL void bap_eval_to_numeric_at_point_int_p_polynom_mint_hp (
    ba0_mint_hp_t *,
    struct bap_polynom_mint_hp *,
    struct bav_point_int_p *);

extern BAP_DLL void bap_evalcoeff_at_point_int_p_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_point_int_p *);
#   endif
#   undef  BAD_FLAG_mint_hp

END_C_DECLS
#endif /* !BAP_EVAL_POLYNOM_mint_hp_H */
