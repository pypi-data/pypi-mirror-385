#if !defined (BA0_MACROS_MINT_HP_H)
#   define BA0_MACROS_MINT_HP_H 1

#   include "ba0_common.h"

/* Macros for ba0_mint_hp */

#   define ba0_mint_hp_t ba0_mint_hp
#   define ba0_mint_hp_init(rop)            rop = 0
#   define ba0_mint_hp_set(rop,op)          rop = op
#   define ba0_mint_hp_affect(rop,op)       rop = op
#   define ba0_mint_hp_swap(opa,opb)        BA0_SWAP (ba0_mint_hp, opa, opb)

#   define ba0_mint_hp_set_si(rop,op)                    \
    rop = op > 0 ? op % ba0_mint_hp_module :             \
            (op + ba0_mint_hp_module) % ba0_mint_hp_module    \

#   define ba0_mint_hp_set_ui(rop,op)       rop = op % ba0_mint_hp_module

#   define ba0_mint_hp_init_set(rop,op)     rop = op

#   define ba0_mint_hp_init_set_si(rop,op)               \
    rop = op > 0 ? op % ba0_mint_hp_module :             \
            (op + ba0_mint_hp_module) % ba0_mint_hp_module

#   define ba0_mint_hp_init_set_ui(rop,op) rop = op % ba0_mint_hp_module

#   define ba0_mint_hp_is_zero(op)          ((op) == 0)
#   define ba0_mint_hp_is_one(op)           ((op) == 1)

#   define ba0_mint_hp_is_negative(op)      ((op) < 0)
#   define ba0_mint_hp_are_equal(opa,opb)   ((opa) == (opb))

#   define ba0_mint_hp_neg(rop,op)          rop = ba0_mint_hp_module - op

#   define ba0_mint_hp_add(rop,opa,opb)                  \
    rop = (ba0_mint_hp)(((unsigned ba0_int_p)(opa) +     \
                (unsigned ba0_int_p)(opb))               \
                % (unsigned ba0_int_p)ba0_mint_hp_module)

#   define ba0_mint_hp_sub(rop,opa,opb)                  \
    rop = (ba0_mint_hp)(((unsigned ba0_int_p)ba0_mint_hp_module + \
                (unsigned ba0_int_p)(opa) -              \
                (unsigned ba0_int_p)(opb))               \
                % (unsigned ba0_int_p)ba0_mint_hp_module)

#   define ba0_mint_hp_mul(rop,opa,opb)                  \
    rop = (ba0_mint_hp)(((unsigned ba0_int_p)(opa)*      \
                (unsigned ba0_int_p)(opb))               \
                % (unsigned ba0_int_p)ba0_mint_hp_module)

#   define ba0_mint_hp_mul_ui(rop,opa,opb)               \
    rop = (ba0_mint_hp)(((unsigned ba0_int_p)(opa)*      \
                (unsigned ba0_int_p)(opb))               \
                % (unsigned ba0_int_p)ba0_mint_hp_module)

#   define ba0_mint_hp_mul_si(rop,opa,opb)               \
    rop = (ba0_mint_hp)(((ba0_int_p)(opa)*((opb) > 0 ? (opb) : \
            ba0_mint_hp_module - (opb)))                 \
            % (unsigned ba0_int_p)ba0_mint_hp_module)

#   define ba0_mint_hp_pow_ui(rop,opa,opb)    rop = ba0_pow_mint_hp(opa,opb)

#   define ba0_mint_hp_div(rop,opa,opb)                  \
    rop = (ba0_mint_hp)(((unsigned ba0_int_p)(opa)*      \
            (unsigned ba0_int_p)ba0_invert_mint_hp(opb)) \
            % (unsigned ba0_int_p)ba0_mint_hp_module)

#   define ba0_mint_hp_invert(rop,op)    rop = ba0_invert_mint_hp (op)

#endif /* !BA0_MACROS_MINT_HP_H */
