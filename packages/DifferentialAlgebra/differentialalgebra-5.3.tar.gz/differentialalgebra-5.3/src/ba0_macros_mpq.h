#if !defined (BA0_MACROS_MPQ_H)
#   define BA0_MACROS_MPQ_H 1

#   include "ba0_common.h"
#   include "ba0_macros_mpz.h"

/* 
 * Macros for mpq_t
 */

#   if defined (BA0_USE_GMP)

#      define ba0_mpq_t                            mpq_t
#      define ba0__mpq_struct                      __mpq_struct

#      define ba0_mpq_affect(rop,op)               rop [0] = op [0]
#      define ba0_mpq_init(rop)                    mpq_init(rop)
#      define ba0_mpq_clear(rop)                   mpq_clear(rop)
#      define ba0_mpq_set(rop,op)                  mpq_set(rop,op)
#      define ba0_mpq_swap(rop,op)                 mpq_swap(rop,op)

#      if ! defined (BA0_USE_X64_GMP)
/*
 * The Linux / Mac OS case
 */
#         define ba0_mpq_set_si(rop,op)            mpq_set_si(rop,op,1)
#         define ba0_mpq_set_si_si(rop,opa,opb)    mpq_set_si(rop,opa,opb)
#         define ba0_mpq_set_ui(rop,op)            mpq_set_ui(rop,op,1)

#      else
/*
 * The Windows case
 */
#         define ba0_mpq_set_si(rop,op)            ba0_x64_mpq_set_si(rop,op,1)
#         define ba0_mpq_set_si_si(rop,opa,opb)    ba0_x64_mpq_set_si(rop,opa,opb)
#         define ba0_mpq_set_ui(rop,op)            ba0_x64_mpq_set_ui(rop,op,1)

#      endif
       /*
        * BA0_USE_X64_GMP 
        */

#      define ba0_mpq_sgn(op)                      mpq_sgn(op)
#      define ba0_mpq_cmp(opa,opb)                 mpq_cmp(opa,opb)
#      define ba0_mpq_cmp_si(opa,opb,opc)          mpq_cmp_si((opa),(opb),(opc))
#      define ba0_mpq_is_zero(op)                  (mpq_cmp_ui((op),0,1) == 0)
#      define ba0_mpq_is_one(op)                   (mpq_cmp_ui((op),1,1) == 0)
#      define ba0_mpq_is_negative(op)              (mpq_cmp_ui((op),0,1) < 0)
#      define ba0_mpq_are_equal(opa,opb)           (mpq_cmp((opa),(opb)) == 0)
#      define ba0_mpq_neg(opa,opb)                 mpq_neg(opa,opb)
#      define ba0_mpq_add(rop,opa,opb)             mpq_add(rop,opa,opb)
#      define ba0_mpq_sub(rop,opa,opb)             mpq_sub(rop,opa,opb)
#      define ba0_mpq_mul(rop,opa,opb)             mpq_mul(rop,opa,opb)

#      define ba0_mpq_canonicalize(rop)            mpq_canonicalize(rop)
#      define ba0_mpq_numref(rop)                  mpq_numref(rop)
#      define ba0_mpq_denref(rop)                  mpq_denref(rop)
#      define ba0_mpq_get_d(rop)                   mpq_get_d(rop)
#      define ba0_mpq_set_d(rop,op)                mpq_set_d(rop,op)
#      define ba0_mpq_set_num(rop,op)              mpq_set_num(rop,op)
#      define ba0_mpq_set_den(rop,op)              mpq_set_den(rop,op)
#      define ba0_mpq_set_z(rop,op)                mpq_set_z(rop,op)

#      define ba0_mpq_div(rop,opa,opb)             mpq_div(rop,opa,opb)
#      define ba0_mpq_invert(rop,op)               mpq_inv(rop,op)

#   else
      /*
       * BA0_USE_GMP 
       */

#      define ba0_mpq_t                            bam_mpq_t
#      define ba0__mpq_struct                      bam__mpq_struct

#      define ba0_mpq_affect(rop,op)               rop [0] = op [0]
#      define ba0_mpq_init(rop)                    bam_mpq_init(rop)
#      define ba0_mpq_clear(rop)                   bam_mpq_clear(rop)
#      define ba0_mpq_set(rop,op)                  bam_mpq_set(rop,op)
#      define ba0_mpq_swap(rop,op)                 bam_mpq_swap(rop,op)

#      if ! defined (BA0_USE_X64_GMP)
/*
 * The Linux / Mac OS case
 */
#         define ba0_mpq_set_si(rop,op)            bam_mpq_set_si(rop,op,1)
#         define ba0_mpq_set_si_si(rop,opa,opb)    bam_mpq_set_si(rop,opa,opb)
#         define ba0_mpq_set_ui(rop,op)            bam_mpq_set_ui(rop,op,1)

#      else
/*
 * The Windows case
 */
#         define ba0_mpq_set_si(rop,op)            ba0_x64_mpq_set_si(rop,op,1)
#         define ba0_mpq_set_si_si(rop,opa,opb)    ba0_x64_mpq_set_si(rop,opa,opb)
#         define ba0_mpq_set_ui(rop,op)            ba0_x64_mpq_set_ui(rop,op,1)

#      endif
       /*
        * BA0_USE_X64_GMP 
        */

#      define ba0_mpq_sgn(op)                      bam_mpq_sgn(op)
#      define ba0_mpq_cmp(opa,opb)                 bam_mpq_cmp(opa,opb)
#      define ba0_mpq_cmp_si(opa,opb,opc)          bam_mpq_cmp_si((opa),(opb),(opc))
#      define ba0_mpq_is_zero(op)                  (bam_mpq_cmp_ui((op),0,1) == 0)
#      define ba0_mpq_is_one(op)                   (bam_mpq_cmp_ui((op),1,1) == 0)
#      define ba0_mpq_is_negative(op)              (bam_mpq_cmp_ui((op),0,1) < 0)
#      define ba0_mpq_are_equal(opa,opb)           (bam_mpq_cmp((opa),(opb)) == 0)
#      define ba0_mpq_neg(opa,opb)                 bam_mpq_neg(opa,opb)
#      define ba0_mpq_add(rop,opa,opb)             bam_mpq_add(rop,opa,opb)
#      define ba0_mpq_sub(rop,opa,opb)             bam_mpq_sub(rop,opa,opb)
#      define ba0_mpq_mul(rop,opa,opb)             bam_mpq_mul(rop,opa,opb)

#      define ba0_mpq_canonicalize(rop)            bam_mpq_canonicalize(rop)
#      define ba0_mpq_numref(rop)                  bam_mpq_numref(rop)
#      define ba0_mpq_denref(rop)                  bam_mpq_denref(rop)
#      define ba0_mpq_get_d(rop)                   bam_mpq_get_d(rop)
#      define ba0_mpq_set_d(rop,op)                bam_mpq_set_d(rop,op)
#      define ba0_mpq_set_num(rop,op)              bam_mpq_set_num(rop,op)
#      define ba0_mpq_set_den(rop,op)              bam_mpq_set_den(rop,op)
#      define ba0_mpq_set_z(rop,op)                bam_mpq_set_z(rop,op)

#      define ba0_mpq_div(rop,opa,opb)             bam_mpq_div(rop,opa,opb)
#      define ba0_mpq_invert(rop,op)               bam_mpq_inv(rop,op)

#   endif
       /*
        * BA0_USE_GMP 
        */

/*
 * Generic macros
 */

#   define ba0_mpq_init_set(rop,op)             \
        do {                                    \
          ba0_mpq_init(rop);                    \
          ba0_mpq_set(rop,op);                  \
        } while (0)

#   define ba0_mpq_init_set_si(rop,op)          \
        do {                                    \
          ba0_mpq_init(rop);                    \
          ba0_mpq_set_si(rop,op);               \
        } while (0)

#   define ba0_mpq_init_set_ui(rop,op)          \
        do {                                    \
          ba0_mpq_init(rop);                    \
          ba0_mpq_set_ui(rop,op);               \
        } while (0)

#   define ba0_mpq_mul_ui(rop,opa,opb)          \
        do {                                    \
          ba0_mpq_set(rop,opa);                 \
          ba0_mpz_mul_ui(ba0_mpq_numref(rop),ba0_mpq_numref(opa),opb); \
          ba0_mpq_canonicalize(rop);            \
        } while (0)

#   define ba0_mpq_mul_si(rop,opa,opb)          \
        do {                                    \
          ba0_mpq_set(rop,opa);                 \
          ba0_mpz_mul_si(ba0_mpq_numref(rop),ba0_mpq_numref(rop),opb); \
          ba0_mpq_canonicalize(rop);            \
        } while (0)

#   define ba0_mpq_pow_ui(rop,opa,opb)          \
        do {                                    \
          ba0_mpz_pow_ui(ba0_mpq_numref(rop),ba0_mpq_numref(opa),opb); \
          ba0_mpz_pow_ui(ba0_mpq_denref(rop),ba0_mpq_denref(opa),opb); \
        } while (0)

#endif /* !BA0_MACROS_MPQ_H */
