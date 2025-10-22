#if ! defined (BA0_MACROS_MPZ_H)
#   define BA0_MACROS_MPZ_H 1

#   include "ba0_common.h"

/*
 * Macros for mpz_t
 *
 * These macros are mostly needed for generic code in the bap library
 */

#   if defined (BA0_USE_GMP)

/*
 * All ba0_functions are mapped to the GMP ones
 */

#      define ba0_mp_set_memory_functions mp_set_memory_functions
#      define ba0_mp_get_memory_functions mp_get_memory_functions

#      define ba0_mpz_t                   mpz_t
#      define ba0__mpz_struct             __mpz_struct
#      define ba0_mp_limb_t               mp_limb_t

#      define ba0_mpz_affect(rop,op)      rop [0] = op [0]
#      define ba0_mpz_init(rop)           mpz_init(rop)
#      define ba0_mpz_clear(rop)          mpz_clear(rop)
#      define ba0_mpz_set(rop,op)         mpz_set(rop,op)
#      define ba0_mpz_swap(rop,op)        mpz_swap(rop,op)
#      define ba0_mpz_init_set(rop,op)    mpz_init_set(rop,op)
#      define ba0_mpz_get_si(op)          mpz_get_si(op)
#      define ba0_mpz_set_str(rop,opa,opb) mpz_set_str(rop,opa,opb)
#      define ba0_mpz_get_str(rop,opa,opb) mpz_get_str(rop,opa,opb)
#      define ba0_mpz_size(op)            mpz_size(op)
#      define ba0_mpz_sizeinbase(opa,opb) mpz_sizeinbase(opa,opb)

#      if ! defined (BA0_USE_X64_GMP)

/*
 * The Linux / MacOS case
 */

#         define ba0_mpz_set_si(rop,op)         mpz_set_si(rop,op)
#         define ba0_mpz_set_ui(rop,op)         mpz_set_ui(rop,op)
#         define ba0_mpz_init_set_si(rop,op)    mpz_init_set_si(rop,op)
#         define ba0_mpz_init_set_ui(rop,op)    mpz_init_set_ui(rop,op)
#         define ba0_mpz_mul_si(rop,opa,opb)    mpz_mul_si(rop,opa,opb)
#         define ba0_mpz_mul_ui(rop,opa,opb)    mpz_mul_ui(rop,opa,opb)
#         define ba0_mpz_mul_2exp(rop,opa,opb)  mpz_mul_2exp(rop,opa,opb)
#         define ba0_mpz_pow_ui(rop,opa,opb)    mpz_pow_ui(rop,opa,opb)
#         define ba0_mpz_ui_pow_ui(rop,opa,opb) mpz_ui_pow_ui(rop,opa,opb)
#         define ba0_mpz_si_pow_ui(rop,opa,opb) \
                    ba0_x64_mpz_si_pow_ui(rop,opa,opb)

#      else
      /*
       * BA0_USE_X64_GMP 
       */

/*
 * The Windows case
 */

#         define ba0_mpz_set_si(rop,op)        ba0_x64_mpz_set_si(rop,op)
#         define ba0_mpz_set_ui(rop,op)        ba0_x64_mpz_set_ui(rop,op)

#         define ba0_mpz_init_set_si(rop,op)    do { \
                    mpz_init(rop);                \
                    ba0_x64_mpz_set_si(rop,op);   \
                    } while (0)

#         define ba0_mpz_init_set_ui(rop,op)    do { \
                    mpz_init(rop);                \
                    ba0_x64_mpz_set_ui(rop,op);   \
                    } while (0)

#         define ba0_mpz_mul_si(rop,opa,opb)    ba0_x64_mpz_mul_si(rop,opa,opb)
#         define ba0_mpz_mul_ui(rop,opa,opb)    ba0_x64_mpz_mul_ui(rop,opa,opb)
#         define ba0_mpz_mul_2exp(rop,opa,opb) \
                    ba0_x64_mpz_mul_2exp(rop,opa,opb)
#         define ba0_mpz_pow_ui(rop,opa,opb)    ba0_x64_mpz_pow_ui(rop,opa,opb)
#         define ba0_mpz_ui_pow_ui(rop,opa,opb) \
                    ba0_x64_mpz_ui_pow_ui(rop,opa,opb)
#         define ba0_mpz_si_pow_ui(rop,opa,opb) \
                    ba0_x64_mpz_si_pow_ui(rop,opa,opb)

#      endif
       /*
        * BA0_USE_X64_GMP 
        */

#      define ba0_mpz_sgn(op)               mpz_sgn(op)
#      define ba0_mpz_is_zero(op)           (mpz_sgn(op) == 0)
#      define ba0_mpz_is_nonzero(op)        (mpz_sgn(op) != 0)
#      define ba0_mpz_is_one(op)            (mpz_cmp_ui(op,1) == 0)
#      define ba0_mpz_is_negative(op)       (mpz_sgn(op) < 0)
#      define ba0_mpz_are_equal(opa,opb)    (mpz_cmp((opa),(opb)) == 0)
#      define ba0_mpz_neg(opa,opb)          mpz_neg(opa,opb)
#      define ba0_mpz_abs(rop,op)           mpz_abs(rop,op)
#      define ba0_mpz_fac_ui(rop,op)        mpz_fac_ui(rop,op)
#      define ba0_mpz_add(rop,opa,opb)      mpz_add(rop,opa,opb)
#      define ba0_mpz_add_ui(rop,opa,opb)   mpz_add_ui(rop,opa,opb)
#      define ba0_mpz_sub(rop,opa,opb)      mpz_sub(rop,opa,opb)
#      define ba0_mpz_sub_ui(rop,opa,opb)   mpz_sub_ui(rop,opa,opb)
#      define ba0_mpz_mul(rop,opa,opb)      mpz_mul(rop,opa,opb)
#      define ba0_mpz_div(rop,opa,opb)      mpz_fdiv_q(rop,opa,opb)
#      define ba0_mpz_mod(rop,opa,opb)      mpz_mod(rop,opa,opb)
#      define ba0_mpz_mod_ui(rop,opa,opb)   mpz_mod_ui(rop,opa,opb)
#      define ba0_mpz_powm(rop,opa,opb,opc) mpz_powm(rop,opa,opb,opc)
#      define ba0_mpz_powm_ui(rop,opa,opb,opc) mpz_powm_ui(rop,opa,opb,opc)
#      define ba0_mpz_cmpabs(opa,opb)       mpz_cmpabs(opa,opb)
#      define ba0_mpz_cmp_si(opa,opb)       mpz_cmp_si(opa,opb)
#      define ba0_mpz_cmp_ui(opa,opb)       mpz_cmp_ui(opa,opb)
#      define ba0_mpz_cmp(opa,opb)          mpz_cmp(opa,opb)
#      define ba0_mpz_invert(rop,opa,opb)   mpz_invert(rop,opa,opb)
#      define ba0_mpz_fdiv_ui(rop,op)       mpz_fdiv_ui(rop,op)
#      define ba0_mpz_fdiv_q_2exp(rop,opa,opb) mpz_fdiv_q_2exp(rop,opa,opb)
#      define ba0_mpz_tdiv_q_2exp(rop,opa,opb) mpz_tdiv_q_2exp(rop,opa,opb)
#      define ba0_mpz_tdiv_qr(ropa,ropb,opa,opb) mpz_tdiv_qr(ropa,ropb,opa,opb)
#      define ba0_mpz_tdiv_q(rop,opa,opb)   mpz_tdiv_q(rop,opa,opb)
#      define ba0_mpz_tdiv_q_ui(rop,opa,opb) mpz_tdiv_q_ui(rop,opa,opb)
#      define ba0_mpz_tdiv_r_ui(rop,opa,opb) mpz_tdiv_r_ui(rop,opa,opb)
#      define ba0_mpz_gcd(rop,opa,opb)      mpz_gcd(rop,opa,opb)
#      define ba0_mpz_gcdext(rop,opa,opb,opc,opd) mpz_gcdext(rop,opa,opb,opc,opd)
#      define ba0_mpz_lcm(rop,opa,opb)      mpz_lcm(rop,opa,opb)
#      define ba0_mpz_divexact(rop,opa,opb) mpz_divexact(rop,opa,opb)
#      define ba0_mpz_sqrt(rop,op)          mpz_sqrt(rop,op)
#      define ba0_mpz_bin_uiui(rop,opa,opb) mpz_bin_uiui(rop,opa,opb)
#      define ba0_mpz_tstbit(opa,opb)       mpz_tstbit(opa,opb)
#      define ba0_mpz_even_p(op)            mpz_even_p(op)

#   else
      /*
       * BA0_USE_GMP 
       */

/*
 * All ba0_functions are mapped to the mini-gmp ones
 */

#      define ba0_mp_set_memory_functions bam_mp_set_memory_functions
#      define ba0_mp_get_memory_functions bam_mp_get_memory_functions

#      define ba0_mpz_t                   bam_mpz_t
#      define ba0__mpz_struct             bam__mpz_struct
#      define ba0_mp_limb_t               bam_mp_limb_t

#      define ba0_mpz_affect(rop,op)      rop [0] = op [0]
#      define ba0_mpz_init(rop)           bam_mpz_init(rop)
#      define ba0_mpz_clear(rop)          bam_mpz_clear(rop)
#      define ba0_mpz_set(rop,op)         bam_mpz_set(rop,op)
#      define ba0_mpz_swap(rop,op)        bam_mpz_swap(rop,op)
#      define ba0_mpz_init_set(rop,op)    bam_mpz_init_set(rop,op)
#      define ba0_mpz_set_str(rop,opa,opb) bam_mpz_set_str(rop,opa,opb)
#      define ba0_mpz_get_str(rop,opa,opb) bam_mpz_get_str(rop,opa,opb)
#      define ba0_mpz_get_si(op)          bam_mpz_get_si(op)
#      define ba0_mpz_size(op)            bam_mpz_size(op)
#      define ba0_mpz_sizeinbase(opa,opb) bam_mpz_sizeinbase(opa,opb)

#      if ! defined (BA0_USE_X64_GMP)

/*
 * The Linux / MacOS case
 */

#         define ba0_mpz_set_si(rop,op)         bam_mpz_set_si(rop,op)
#         define ba0_mpz_set_ui(rop,op)         bam_mpz_set_ui(rop,op)
#         define ba0_mpz_init_set_si(rop,op)    bam_mpz_init_set_si(rop,op)
#         define ba0_mpz_init_set_ui(rop,op)    bam_mpz_init_set_ui(rop,op)
#         define ba0_mpz_mul_si(rop,opa,opb)    bam_mpz_mul_si(rop,opa,opb)
#         define ba0_mpz_mul_ui(rop,opa,opb)    bam_mpz_mul_ui(rop,opa,opb)
#         define ba0_mpz_mul_2exp(rop,opa,opb)  bam_mpz_mul_2exp(rop,opa,opb)
#         define ba0_mpz_pow_ui(rop,opa,opb)    bam_mpz_pow_ui(rop,opa,opb)
#         define ba0_mpz_ui_pow_ui(rop,opa,opb) bam_mpz_ui_pow_ui(rop,opa,opb)

#      else
      /*
       * BA0_USE_X64_GMP 
       */

/*
 * The Windows case
 */

#         define ba0_mpz_set_si(rop,op)        ba0_x64_mpz_set_si(rop,op)
#         define ba0_mpz_set_ui(rop,op)        ba0_x64_mpz_set_ui(rop,op)

#         define ba0_mpz_init_set_si(rop,op)    do { \
                    bam_mpz_init(rop);                \
                    ba0_x64_mpz_set_si(rop,op);   \
                    } while (0)

#         define ba0_mpz_init_set_ui(rop,op)    do { \
                    bam_mpz_init(rop);                \
                    ba0_x64_mpz_set_ui(rop,op);   \
                    } while (0)

#         define ba0_mpz_mul_si(rop,opa,opb)    ba0_x64_mpz_mul_si(rop,opa,opb)
#         define ba0_mpz_mul_ui(rop,opa,opb)    ba0_x64_mpz_mul_ui(rop,opa,opb)
#         define ba0_mpz_mul_2exp(rop,opa,opb) \
                    ba0_x64_mpz_mul_2exp(rop,opa,opb)
#         define ba0_mpz_pow_ui(rop,opa,opb)    ba0_x64_mpz_pow_ui(rop,opa,opb)
#         define ba0_mpz_ui_pow_ui(rop,opa,opb) \
                    ba0_x64_mpz_ui_pow_ui(rop,opa,opb)

#      endif
       /*
        * BA0_USE_X64_GMP 
        */

#      define ba0_mpz_sgn(op)               bam_mpz_sgn(op)
#      define ba0_mpz_is_zero(op)           (bam_mpz_sgn(op) == 0)
#      define ba0_mpz_is_nonzero(op)        (bam_mpz_sgn(op) != 0)
#      define ba0_mpz_is_one(op)            (bam_mpz_cmp_ui(op,1) == 0)
#      define ba0_mpz_is_negative(op)       (bam_mpz_sgn(op) < 0)
#      define ba0_mpz_are_equal(opa,opb)    (bam_mpz_cmp((opa),(opb)) == 0)
#      define ba0_mpz_neg(opa,opb)          bam_mpz_neg(opa,opb)
#      define ba0_mpz_abs(rop,op)           bam_mpz_abs(rop,op)
#      define ba0_mpz_fac_ui(rop,op)        bam_mpz_fac_ui(rop,op)
#      define ba0_mpz_add(rop,opa,opb)      bam_mpz_add(rop,opa,opb)
#      define ba0_mpz_add_ui(rop,opa,opb)   bam_mpz_add_ui(rop,opa,opb)
#      define ba0_mpz_sub(rop,opa,opb)      bam_mpz_sub(rop,opa,opb)
#      define ba0_mpz_sub_ui(rop,opa,opb)   bam_mpz_sub_ui(rop,opa,opb)
#      define ba0_mpz_mul(rop,opa,opb)      bam_mpz_mul(rop,opa,opb)
#      define ba0_mpz_div(rop,opa,opb)      bam_mpz_fdiv_q(rop,opa,opb)
#      define ba0_mpz_mod(rop,opa,opb)      bam_mpz_mod(rop,opa,opb)
#      define ba0_mpz_mod_ui(rop,opa,opb)   bam_mpz_mod_ui(rop,opa,opb)
#      define ba0_mpz_powm(rop,opa,opb,opc) bam_mpz_powm(rop,opa,opb,opc)
#      define ba0_mpz_powm_ui(rop,opa,opb,opc) bam_mpz_powm_ui(rop,opa,opb,opc)
#      define ba0_mpz_cmpabs(opa,opb)       bam_mpz_cmpabs(opa,opb)
#      define ba0_mpz_cmp_si(opa,opb)       bam_mpz_cmp_si(opa,opb)
#      define ba0_mpz_cmp_ui(opa,opb)       bam_mpz_cmp_ui(opa,opb)
#      define ba0_mpz_cmp(opa,opb)          bam_mpz_cmp(opa,opb)
#      define ba0_mpz_invert(rop,opa,opb)   bam_mpz_invert(rop,opa,opb)
#      define ba0_mpz_fdiv_ui(rop,op)       bam_mpz_fdiv_ui(rop,op)
#      define ba0_mpz_fdiv_q_2exp(rop,opa,opb) bam_mpz_fdiv_q_2exp(rop,opa,opb)
#      define ba0_mpz_tdiv_q_2exp(rop,opa,opb) bam_mpz_tdiv_q_2exp(rop,opa,opb)
#      define ba0_mpz_tdiv_qr(ropa,ropb,opa,opb) bam_mpz_tdiv_qr(ropa,ropb,opa,opb)
#      define ba0_mpz_tdiv_q(rop,opa,opb)   bam_mpz_tdiv_q(rop,opa,opb)
#      define ba0_mpz_tdiv_q_ui(rop,opa,opb) bam_mpz_tdiv_q_ui(rop,opa,opb)
#      define ba0_mpz_tdiv_r_ui(rop,opa,opb) bam_mpz_tdiv_r_ui(rop,opa,opb)
#      define ba0_mpz_gcd(rop,opa,opb)      bam_mpz_gcd(rop,opa,opb)
#      define ba0_mpz_gcdext(rop,opa,opb,opc,opd) bam_mpz_gcdext(rop,opa,opb,opc,opd)
#      define ba0_mpz_lcm(rop,opa,opb)      bam_mpz_lcm(rop,opa,opb)
#      define ba0_mpz_divexact(rop,opa,opb) bam_mpz_divexact(rop,opa,opb)
#      define ba0_mpz_sqrt(rop,op)          bam_mpz_sqrt(rop,op)
#      define ba0_mpz_bin_uiui(rop,opa,opb) bam_mpz_bin_uiui(rop,opa,opb)
#      define ba0_mpz_tstbit(opa,opb)       bam_mpz_tstbit(opa,opb)
#      define ba0_mpz_even_p(op)            bam_mpz_even_p(op)

#   endif
       /*
        * BA0_USE_GMP 
        */

#endif /* !BA0_MACROS_MPZ_H */
