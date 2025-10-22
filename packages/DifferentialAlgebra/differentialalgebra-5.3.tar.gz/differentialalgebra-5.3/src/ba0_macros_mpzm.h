#if !defined (BA0_MACROS_MPZM_H)
#   define BA0_MACROS_MPZM_H 1

#   include "ba0_common.h"
#   include "ba0_macros_mpz.h"

/* 
 * Macros for ba0_mpzm
 */

#   define ba0_mpzm_t                           ba0_mpz_t
#   define ba0_mpzm_module                      ba0_global.mpzm.module
#   define ba0_mpzm_init(rop)                   ba0_mpz_init(rop)
#   define ba0_mpzm_set(rop,op)                 ba0_mpz_set(rop,op)
#   define ba0_mpzm_affect(rop,op)              rop [0] = op [0]
#   define ba0_mpzm_swap(opa,opb)               ba0_mpz_swap(opa,opb)

#   define ba0_mpzm_set_si(rop,op)              \
        do {                                    \
          ba0_mpz_set_si(rop,op);               \
          ba0_mpz_mod(rop,rop,ba0_mpzm_module); \
        } while (0)

#   define ba0_mpzm_init_set(rop,op)    ba0_mpz_init_set(rop,op)

#   define ba0_mpzm_init_set_si(rop,op)         \
        do {                                    \
          ba0_mpz_init_set_si(rop,op);          \
          ba0_mpz_mod(rop,rop,ba0_mpzm_module); \
        } while (0)

#   define ba0_mpzm_init_set_ui(rop,op)         \
        do {                                    \
          ba0_mpz_init_set_ui(rop,op);          \
          ba0_mpz_mod(rop,rop,ba0_mpzm_module); \
        } while (0)

#   define ba0_mpzm_is_zero(op)                 (ba0_mpz_cmp_ui((op),0) == 0)
#   define ba0_mpzm_is_one(op)                  (ba0_mpz_cmp_ui((op),1) == 0)
#   define ba0_mpzm_is_negative(op)             false
#   define ba0_mpzm_are_equal(opa,opb)          (ba0_mpz_cmp((opa),(opb)) == 0)

#   define ba0_mpzm_neg(rop,op)                 \
        do {                                    \
          ba0_mpz_neg(rop,op);                  \
          ba0_mpz_mod(rop,rop,ba0_mpzm_module); \
        } while (0)

#   define ba0_mpzm_add(rop,opa,opb)            \
        do {                                    \
          ba0_mpz_add(rop,opa,opb);             \
          ba0_mpz_mod(rop,rop,ba0_mpzm_module); \
        } while (0)

#   define ba0_mpzm_sub(rop,opa,opb)            \
        do {                                    \
          ba0_mpz_sub(rop,opa,opb);             \
          ba0_mpz_mod(rop,rop,ba0_mpzm_module); \
        } while (0)

#   define ba0_mpzm_mul(rop,opa,opb)            \
        do {                                    \
          ba0_push_stack (&ba0_global.stack.quiet); \
          ba0_mpz_mul(ba0_mpzm_accum,opa,opb);  \
          ba0_pull_stack ();                    \
          ba0_mpz_mod(rop,ba0_mpzm_accum,ba0_mpzm_module); \
        } while (0)

#   define ba0_mpzm_mul_ui(rop,opa,opb)         \
        do {                                    \
          ba0_push_stack (&ba0_global.stack.quiet); \
          ba0_mpz_mul_ui(ba0_mpzm_accum,opa,opb);   \
          ba0_pull_stack ();                    \
          ba0_mpz_mod(rop,ba0_mpzm_accum,ba0_mpzm_module); \
        } while (0)

#   define ba0_mpzm_mul_si(rop,opa,opb)         \
        do {                                    \
          ba0_mpz_mul_si(rop,opa,opb);          \
          ba0_mpz_mod(rop,rop,ba0_mpzm_module); \
        } while (0)

#   if ! defined (BA0_USE_X64_GMP)
/*
 * The Linux / Mac OS Case
 */
#      define ba0_mpzm_pow_ui(rop,opa,opb)      \
        ba0_mpz_powm_ui(rop,opa,opb,ba0_mpzm_module)
#   else
/*
 * The Windows case
 */
#      define ba0_mpzm_pow_ui(rop,opa,opb)      \
        do {                                    \
          ba0_mpz_t bunk;                       \
          ba0_push_another_stack ();            \
          ba0_mpz_set_ui(bunk,opb);             \
          ba0_pull_stack ();                    \
          ba0_mpz_powm(rop,opa,bunk,ba0_mpzm_module); \
        } while (0)
#   endif

#   define ba0_mpzm_div(rop,opa,opb)            \
        do {                                    \
          ba0_push_stack (&ba0_global.stack.quiet);           \
          ba0_mpz_invert(ba0_mpzm_accum,opb,ba0_mpzm_module); \
          ba0_mpz_mul(ba0_mpzm_accum,ba0_mpzm_accum,opa);     \
          ba0_pull_stack ();                    \
          ba0_mpz_mod(rop,ba0_mpzm_accum,ba0_mpzm_module);    \
        } while (0)

#   define ba0_mpzm_invert(rop,op)              \
      ba0_mpz_invert(rop,op,ba0_mpzm_module)

#endif /* !BA0_MACROS_MPZM_H */
