#if ! defined (BA0_MACROS_INTERVAL_MPQ_H)
#   define BA0_MACROS_INTERVAL_MPQ_H 1

#   include "ba0_common.h"
#   include "ba0_interval_mpq.h"

/* 
 * Macros for ba0_interval_mpq 
 */

typedef struct ba0_interval_mpq ba0_interval_mpq_t[1];

#   define ba0_interval_mpq_affect(rop,op)      ba0_set_interval_mpq (rop, op)
#   define ba0_interval_mpq_init(rop)           ba0_init_interval_mpq (rop)
#   define ba0_interval_mpq_set(rop,op)         ba0_set_interval_mpq (rop, op)
#   define ba0_interval_mpq_swap(rop,op)        BA0_SWAP(struct ba0_interval_mpq,rop[0],op[0])
#   define ba0_interval_mpq_set_si(rop,op)      ba0_set_interval_mpq_si (rop, op)
#   define ba0_interval_mpq_set_ui(rop,op)      ba0_set_interval_mpq_ui (rop, op)
#   define ba0_interval_mpq_init_set(rop,op)    ba0_set_interval_mpq (rop, op)

#   define ba0_interval_mpq_init_set_si(rop,op) \
       do {                                     \
         ba0_interval_mpq_init(rop);            \
         ba0_set_interval_mpq_si (rop, op);     \
       } while (0)

#   define ba0_interval_mpq_init_set_ui(rop,op) \
       do {                                     \
         ba0_interval_mpq_init(rop);            \
         ba0_set_interval_mpq_ui (rop, op);     \
       } while (0)

#   define ba0_interval_mpq_is_zero(op)         ba0_is_zero_interval_mpq (op)
#   define ba0_interval_mpq_is_one(op)          ba0_is_one_interval_mpq (op)
#   define ba0_interval_mpq_is_negative(op)     ba0_is_negative_interval_mpq (op)
#   define ba0_interval_mpq_are_equal(opa,opb)  ba0_are_equal_interval_mpq (opa, opb)
#   define ba0_interval_mpq_neg(rop,op)         ba0_neg_interval_mpq (rop, op)
#   define ba0_interval_mpq_add(rop,opa,opb)    ba0_add_interval_mpq (rop, opa, opb)
#   define ba0_interval_mpq_sub(rop,opa,opb)    ba0_sub_interval_mpq (rop, opa, opb)
#   define ba0_interval_mpq_mul(rop,opa,opb)    ba0_mul_interval_mpq (rop, opa, opb)
#   define ba0_interval_mpq_mul_ui(rop,opa,opb) ba0_mul_interval_mpq_ui (rop, opa, opb)
#   define ba0_interval_mpq_mul_si(rop,opa,opb) ba0_mul_interval_mpq_si (rop, opa, opb)
#   define ba0_interval_mpq_pow_ui(rop,opa,opb) ba0_pow_interval_mpq (rop, opa, (ba0_int_p)opb)

#endif
