#include "ba0_exception.h"
#include "ba0_stack.h"
#include "ba0_gmp.h"
#include "ba0_mpzm.h"
#include "ba0_basic_io.h"
#include "ba0_analex.h"
#include "ba0_garbage.h"
#include "ba0_macros_mpz.h"
#include "ba0_macros_mpzm.h"
#include "ba0_macros_mpq.h"
#include "ba0_global.h"

BA0_DLL void
ba0_init_mpzm_module (
    void)
{
  ba0_push_stack (&ba0_global.stack.quiet);
  ba0_mpz_init (ba0_mpzm_module);
  ba0_mpz_init (ba0_mpzm_half_module);
  ba0_mpz_init (ba0_mpzm_accum);
  ba0_pull_stack ();

}

BA0_DLL void
ba0_reset_mpzm_module (
    void)
{
  ba0_mpzm_module_is_prime = false;
}

/*
 * texinfo: ba0_domain_mpzm
 * Return @code{true} if the factor ring is a domain (a field).
 */

BA0_DLL bool
ba0_domain_mpzm (
    void)
{
  return ba0_mpzm_module_is_prime;
}

/*
 * texinfo: ba0_mpzm_module_set_ui
 * Assign the two parameters to the global variables.
 */

BA0_DLL void
ba0_mpzm_module_set_ui (
    unsigned ba0_int_p n,
    bool prime)
{
#if defined (BA0_MEMCHECK)
  if ((ba0_mpzm_module[0]._mp_alloc != 0
          && !ba0_in_stack (ba0_mpzm_module[0]._mp_d,
              &ba0_global.stack.quiet))
      || (ba0_mpzm_half_module[0]._mp_alloc != 0
          && !ba0_in_stack (ba0_mpzm_half_module[0]._mp_d,
              &ba0_global.stack.quiet))
      || (ba0_mpzm_accum[0]._mp_alloc != 0
          && !ba0_in_stack (ba0_mpzm_accum[0]._mp_d, &ba0_global.stack.quiet)))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
#endif
  ba0_push_stack (&ba0_global.stack.quiet);
  ba0_mpz_set_ui (ba0_mpzm_module, n);
  ba0_mpz_fdiv_q_2exp (ba0_mpzm_half_module, ba0_mpzm_module, 1);
  ba0_mpz_set_ui (ba0_mpzm_accum, 1);
  ba0_mpz_mul_2exp (ba0_mpzm_accum, ba0_mpzm_accum,
      (ba0_mpz_size (ba0_mpzm_module) + 1) * sizeof (ba0_mp_limb_t) * 16);
  ba0_pull_stack ();
  ba0_mpzm_module_is_prime = prime;
}

/*
 * texinfo: ba0_mpzm_module_set
 * Variant of the above function.
 */

BA0_DLL void
ba0_mpzm_module_set (
    ba0_mpz_t n,
    bool prime)
{
#if defined (BA0_MEMCHECK)
  if ((ba0_mpzm_module[0]._mp_alloc != 0
          && !ba0_in_stack (ba0_mpzm_module[0]._mp_d,
              &ba0_global.stack.quiet))
      || (ba0_mpzm_half_module[0]._mp_alloc != 0
          && !ba0_in_stack (ba0_mpzm_half_module[0]._mp_d,
              &ba0_global.stack.quiet))
      || (ba0_mpzm_accum[0]._mp_alloc != 0
          && !ba0_in_stack (ba0_mpzm_accum[0]._mp_d, &ba0_global.stack.quiet)))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
#endif
  ba0_push_stack (&ba0_global.stack.quiet);
  ba0_mpz_set (ba0_mpzm_module, n);
  ba0_mpz_fdiv_q_2exp (ba0_mpzm_half_module, ba0_mpzm_module, 1);
  ba0_mpz_set_ui (ba0_mpzm_accum, 1);
  ba0_mpz_mul_2exp (ba0_mpzm_accum, ba0_mpzm_accum,
      (ba0_mpz_size (ba0_mpzm_module) + 1) * sizeof (ba0_mp_limb_t) * 16);
  ba0_pull_stack ();
  ba0_mpzm_module_is_prime = prime;
}

/*
 * texinfo: ba0_mpzm_module_mul
 * Multiplie the modulus by n.
 */

BA0_DLL void
ba0_mpzm_module_mul (
    ba0_mpz_t n)
{
#if defined (BA0_MEMCHECK)
  if ((ba0_mpzm_module[0]._mp_alloc != 0
          && !ba0_in_stack (ba0_mpzm_module[0]._mp_d,
              &ba0_global.stack.quiet))
      || (ba0_mpzm_half_module[0]._mp_alloc != 0
          && !ba0_in_stack (ba0_mpzm_half_module[0]._mp_d,
              &ba0_global.stack.quiet))
      || (ba0_mpzm_accum[0]._mp_alloc != 0
          && !ba0_in_stack (ba0_mpzm_accum[0]._mp_d, &ba0_global.stack.quiet)))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
#endif
  ba0_push_stack (&ba0_global.stack.quiet);
  ba0_mpz_mul (ba0_mpzm_module, ba0_mpzm_module, n);
  ba0_mpz_fdiv_q_2exp (ba0_mpzm_half_module, ba0_mpzm_module, 1);
  ba0_mpz_set_ui (ba0_mpzm_accum, 1);
  ba0_mpz_mul_2exp (ba0_mpzm_accum, ba0_mpzm_accum,
      (ba0_mpz_size (ba0_mpzm_module) + 1) * sizeof (ba0_mp_limb_t) * 16);
  ba0_pull_stack ();
  ba0_mpzm_module_is_prime = false;
}

/*
 * texinfo: ba0_mpzm_module_pow_ui
 * Assign @math{n^d} to the modulus.
 * The boolean indicates if @var{n} is prime.
 */

BA0_DLL void
ba0_mpzm_module_pow_ui (
    ba0_mpz_t n,
    unsigned ba0_int_p d,
    bool prime)
{
#if defined (BA0_MEMCHECK)
  if ((ba0_mpzm_module[0]._mp_alloc != 0
          && !ba0_in_stack (ba0_mpzm_module[0]._mp_d,
              &ba0_global.stack.quiet))
      || (ba0_mpzm_half_module[0]._mp_alloc != 0
          && !ba0_in_stack (ba0_mpzm_half_module[0]._mp_d,
              &ba0_global.stack.quiet))
      || (ba0_mpzm_accum[0]._mp_alloc != 0
          && !ba0_in_stack (ba0_mpzm_accum[0]._mp_d, &ba0_global.stack.quiet)))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
#endif
  ba0_push_stack (&ba0_global.stack.quiet);
  ba0_mpz_pow_ui (ba0_mpzm_module, n, d);
  ba0_mpz_fdiv_q_2exp (ba0_mpzm_half_module, ba0_mpzm_module, 1);
  ba0_mpz_set_ui (ba0_mpzm_accum, 1);
  ba0_mpz_mul_2exp (ba0_mpzm_accum, ba0_mpzm_accum,
      (ba0_mpz_size (ba0_mpzm_module) + 1) * sizeof (ba0_mp_limb_t) * 16);
  ba0_pull_stack ();
  ba0_mpzm_module_is_prime = prime && d == 1;
}

/*
 * texinfo: ba0_new_mpzm
 * Return a @code{mpz_t} allocated on the current stack.
 */

BA0_DLL ba0__mpz_struct *
ba0_new_mpzm (
    void)
{
  return ba0_new_mpz ();
}

/*
 * texinfo: ba0_scanf_mpzm
 * The general parser for modular @code{ba0_mpz_t}.
 * It can be called through @code{ba0_scanf/%zm}.
 */

BA0_DLL void *
ba0_scanf_mpzm (
    void *z)
{
  ba0__mpz_struct *c;

  if (z == (void *) 0)
    c = ba0_new_mpzm ();
  else
    c = (ba0__mpz_struct *) z;
  ba0_scanf_mpz (z);
  ba0_mpz_mod (c, c, ba0_mpzm_module);
  return c;
}

/*
 * texinfo: ba0_printf_mpzm
 * The general parser for modular @code{ba0_mpz_t}.
 * It can be called through @code{ba0_printf/%zm}.
 */

BA0_DLL void
ba0_printf_mpzm (
    void *z)
{
  ba0__mpz_struct *c = (ba0__mpz_struct *) z;
  char *s;
  struct ba0_mark M;

  ba0_record (&M);
  s = ba0_mpz_get_str ((char *) 0, 10, c);
  ba0_put_string (s);
  ba0_restore (&M);
}

/*
 * Readonly static data
 */

static char mpzm_struct_[] = "__mpzm_struct";
static char mpzm_struct_mp_d_[] = "__mpzm_struct._mp_d";

BA0_DLL ba0_int_p
ba0_garbage1_mpzm (
    void *_c,
    enum ba0_garbage_code code)
{
  ba0__mpz_struct *c = (ba0__mpz_struct *) _c;
  ba0_int_p n = 0;

  if (code == ba0_isolated)
    n += ba0_new_gc_info (c, sizeof (ba0__mpz_struct), mpzm_struct_);

  if (c->_mp_alloc != 0)
    n += ba0_new_gc_info
        (c->_mp_d, c->_mp_alloc * sizeof (ba0_mp_limb_t), mpzm_struct_mp_d_);
  return n;
}

BA0_DLL void *
ba0_garbage2_mpzm (
    void *_c,
    enum ba0_garbage_code code)
{
  ba0__mpz_struct *c;

  if (code == ba0_isolated)
    c = (ba0__mpz_struct *) ba0_new_addr_gc_info (_c, mpzm_struct_);
  else
    c = (ba0__mpz_struct *) _c;

  if (c->_mp_alloc != 0)
    c->_mp_d = ba0_new_addr_gc_info (c->_mp_d, mpzm_struct_mp_d_);
  return c;
}

BA0_DLL void *
ba0_copy_mpzm (
    void *z)
{
  ba0__mpz_struct *c;

  c = ba0_new_mpzm ();
  ba0_mpz_init_set (c, (ba0__mpz_struct *) z);
  return c;
}

/*
 * texinfo: ba0_wang_mpzm
 * Applie the Paul Shyh-Horng Wang algorithm to convert a modular number to a 
 * rational. Denote @var{n} the modulus. Assigns to @var{rat} the unique rational
 * number @math{p/q} such that @math{|p|,\, |q| < \sqrt{n / 2}}.
 * Returns @code{ba0_rational_found} if the rational exists.
 * Returns @code{ba0_zero_divisor} if a rational is found with a denominator
 * not relatively prime to @var{n}. In this case, @var{ddz} receives
 * @math{q \wedge n} if @var{ddz} is not the zero pointer. 
 * Returns @code{ba0_rational_not_found} the rational does not exist.
 */

BA0_DLL enum ba0_wang_code
ba0_wang_mpzm (
    ba0_mpq_t rat,
    ba0_mpz_t a,
    ba0_mpz_t ddz)
{
  bool opp = false;
  int sign;
  ba0_mpz_t u1, u3, v1, v3, bunk, q;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_mpz_init (u1);
  ba0_mpz_init_set (u3, ba0_mpzm_module);
  ba0_mpz_init_set_si (v1, 1);
  ba0_mpz_init_set (v3, a);
  ba0_mpz_init (bunk);
  ba0_mpz_init (q);

  sign = ba0_mpz_sgn (a);

  if (sign == 0)
    {
      ba0_pull_stack ();
      ba0_mpq_set_si (rat, 0);
      ba0_restore (&M);
      return ba0_rational_found;
    }
  if (sign < 0)
    {
      ba0_mpz_neg (v3, a);
      opp = !opp;
    }
  ba0_mpz_mul_2exp (bunk, v3, 1);
  if (ba0_mpz_cmp (bunk, ba0_mpzm_module) >= 0)
    {
      ba0_mpz_sub (v3, ba0_mpzm_module, v3);
      opp = !opp;
    }

  for (;;)
    {
      ba0_mpz_mul (bunk, u1, u1);
      ba0_mpz_mul_2exp (bunk, bunk, 1);
      if (ba0_mpz_cmp (bunk, ba0_mpzm_module) >= 0)
        {
          ba0_pull_stack ();
          ba0_restore (&M);
          return ba0_rational_not_found;
        }
      ba0_mpz_mul (bunk, u3, u3);
      ba0_mpz_mul_2exp (bunk, bunk, 1);
      if (ba0_mpz_cmp (bunk, ba0_mpzm_module) < 0)
        {
          if (ba0_mpz_sgn (u1) > 0)
            {
              ba0_mpz_gcd (bunk, u1, ba0_mpzm_module);
              if (ba0_mpz_cmp_si (bunk, 1) != 0)
                {
                  ba0_pull_stack ();
                  if (ddz != (ba0__mpz_struct *) 0)
                    ba0_mpz_set (ddz, bunk);
                  ba0_restore (&M);
                  return ba0_zero_divisor;
                }
              if (opp)
                ba0_mpz_neg (u3, u3);
              ba0_pull_stack ();
              ba0_mpq_set_num (rat, u3);
              ba0_mpq_set_den (rat, u1);
              ba0_restore (&M);
              return ba0_rational_found;
            }
          else
            {
              ba0_mpz_neg (u1, u1);
              ba0_mpz_gcd (bunk, u1, ba0_mpzm_module);
              if (ba0_mpz_cmp_si (bunk, 1) != 0)
                {
                  ba0_pull_stack ();
                  if (ddz != (ba0__mpz_struct *) 0)
                    ba0_mpz_set (ddz, bunk);
                  ba0_restore (&M);
                  return ba0_zero_divisor;
                }
              if (!opp)
                ba0_mpz_neg (u3, u3);
              ba0_pull_stack ();
              ba0_mpq_set_num (rat, u3);
              ba0_mpq_set_den (rat, u1);
              ba0_restore (&M);
              return ba0_rational_found;
            }
        }
      if (ba0_mpz_sgn (v3) == 0)
        {
          ba0_pull_stack ();
          ba0_restore (&M);
          return ba0_rational_not_found;
/*
	    BA0_RAISE_EXCEPTION (BA0_EXWRNT);
*/
        }
      ba0_mpz_set (bunk, v3);
      ba0_mpz_tdiv_qr (q, v3, u3, v3);
      ba0_mpz_set (u3, bunk);
      ba0_mpz_set (bunk, v1);
      ba0_mpz_set (v1, u1);
      ba0_mpz_mul (u1, bunk, q);
      ba0_mpz_sub (v1, v1, u1);
      ba0_mpz_set (u1, bunk);
    }
  return ba0_rational_found;    /* to avoid annoying warnings */
}
