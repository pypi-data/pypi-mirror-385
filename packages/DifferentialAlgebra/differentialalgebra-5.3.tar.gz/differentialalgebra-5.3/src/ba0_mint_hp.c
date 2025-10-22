#include "ba0_exception.h"
#include "ba0_mint_hp.h"
#include "ba0_basic_io.h"
#include "ba0_analex.h"
#include "ba0_macros_mpq.h"
#include "ba0_global.h"

BA0_DLL void
ba0_reset_mint_hp_module (
    void)
{
  ba0_mint_hp_module_is_prime = false;
}

/*
 * texinfo: ba0_domain_mint_hp
 * Return @code{true} if the quotient ring is a domain (indeed a field).
 */

BA0_DLL bool
ba0_domain_mint_hp (
    void)
{
  return ba0_mint_hp_module_is_prime;
}

/*
 * texinfo: ba0_mint_hp_module_set
 * Give values to the two global variables.
 */

BA0_DLL void
ba0_mint_hp_module_set (
    ba0_mint_hp p,
    bool prime)
{
  ba0_mint_hp_module = p;
  ba0_mint_hp_module_is_prime = prime;
}

BA0_DLL ba0_mint_hp
ba0_pow_mint_hp (
    ba0_mint_hp a,
    ba0_int_p n)
{
  ba0_mint_hp e;
  ba0_int_p p;

  ba0_mint_hp_set_si (e, 1);
  if (n == 0)
    return e;
  for (p = n; p != 1; p /= 2)
    {
      if (p % 2 == 1)
        ba0_mint_hp_mul (e, e, a);
      ba0_mint_hp_mul (a, a, a);
    }
  ba0_mint_hp_mul (e, e, a);
  return e;
}

BA0_DLL void *
ba0_scanf_mint_hp (
    void *z)
{
  ba0_mint_hp *c;

  if (z == (void *) 0)
    c = (ba0_mint_hp *) ba0_alloc (sizeof (ba0_mint_hp));
  else
    c = (ba0_mint_hp *) z;

  if (ba0_type_token_analex () != ba0_integer_token)
    BA0_RAISE_EXCEPTION (BA0_ERRINT);

  *c = atoi (ba0_value_token_analex ());
  *c = *c % ba0_mint_hp_module;
  return c;
}

BA0_DLL void
ba0_printf_mint_hp (
    void *z)
{
  ba0_mint_hp *c = (ba0_mint_hp *) z;

  ba0_put_int_p ((ba0_int_p) * c);
}

/* 
  _a and _b are assumed nonzero.
*/

static ba0_int_hp
bingcdext (
    ba0_mint_hp _a,
    ba0_mint_hp _b,
    ba0_int_p *u,
    ba0_int_p *v)
{
  ba0_int_p a, b, k;
  ba0_int_p u1, u3, v1, v3, t1, t3;

  a = _a;
  b = _b;

  for (k = 0; (a % 2) == 0 && (b % 2) == 0; k++)
    {
      a /= 2;
      b /= 2;
    }
  if ((b % 2) == 0)
    {
      ba0_int_p zib;
      ba0_int_p *zob;

      zib = _a;
      _a = _b;
      _b = (ba0_int_hp) zib;
      zib = a;
      a = b;
      b = zib;
      zob = u;
      u = v;
      v = zob;
    }
/* Ici, a et b sont positifs et b est impair. */
  u1 = 1;
  u3 = a;
  v1 = 0;
  v3 = b;
  if ((u3 % 2) != 0)
    {
      t1 = -v1;
      t3 = -v3;
    }
  else if ((u1 % 2) == 0)
    {
      t1 = u1 / 2;
      t3 = u3 / 2;
    }
  else
    {
      t1 = (u1 - b) / 2;
      t3 = u3 / 2;
    }
  while (t3 != 0)
    {
      while ((t3 % 2) == 0)
        {
          if ((t1 % 2) == 0)
            t1 /= 2;
          else if (t1 > 0)
            t1 = (t1 - b) / 2;
          else
            t1 = (t1 + b) / 2;
          t3 /= 2;
        }
      if (t3 > 0)
        {
          u1 = t1;
          u3 = t3;
        }
      else
        {
          v1 = -t1;
          v3 = -t3;
        }
      t1 = u1 - v1;
      t3 = u3 - v3;
    }
  *u = (ba0_int_hp) u1;
  *v = (ba0_int_hp) (u3 - a * u1) / b;
  return (ba0_int_hp) (u3 << k);
}

/*
 * Returns $1/c$ modulo {\tt ba0_mint_hp_module}.
 * Raises exception BA0_ERRIVZ if $c = 0$ or BA0_ERRDDZ if $c$ is not
 * relativaly prime to the module.
 */

BA0_DLL ba0_mint_hp
ba0_invert_mint_hp (
    ba0_mint_hp c)
{
  ba0_int_p u, v;

  if (c == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRIVZ);
  if (bingcdext (c, ba0_mint_hp_module, &u, &v) != 1)
    BA0_RAISE_EXCEPTION (BA0_ERRDDZ);
  return u > 0 ? (ba0_mint_hp) u : (ba0_mint_hp) (ba0_mint_hp_module + u);
}

/*
 * texinfo: ba0_wang_mint_hp
 * Applie the Paul Shyh-Horng Wang algorithm to convert a modular number to a 
 * rational. Denote @var{n} the modulus. Assigns to @var{rat} the unique rational
 * number @math{p/q} such that @math{|p|,\, |q| < \sqrt{n / 2}}.
 * Returns @code{ba0_rational_found} if the rational exists.
 * Returns @code{ba0_zero_divisor} if a rational is found with a denominator
 * not relatively prime to @var{n}. In this case, *@var{ddz} receives
 * @math{q \wedge n} if @var{ddz} is not the zero pointer. 
 * Returns @code{ba0_rational_not_found} the rational does not exist.
 */

BA0_DLL enum ba0_wang_code
ba0_wang_mint_hp (
    ba0_mpq_t rat,
    ba0_mint_hp a,
    ba0_int_hp *ddz)
{
  bool opp = false;
  ba0_int_p u1, u3, v1, v3, t1, t3, q;

  u1 = 0;
  u3 = ba0_mint_hp_module;
  v1 = 1;
  v3 = a;

  if (a == 0)
    {
      ba0_mpq_set_si (rat, 0);
      return ba0_rational_found;
    }

  if (2 * v3 >= ba0_mint_hp_module)
    {
      v3 = ba0_mint_hp_module - v3;
      opp = !opp;
    }

  for (;;)
    {
      if ((unsigned ba0_int_p) (u1 * u1) >=
          (unsigned ba0_int_p) ba0_mint_hp_module / 2)
        return ba0_rational_not_found;
/*
	    BA0_RAISE_EXCEPTION (BA0_EXWRNT);
*/
      if ((unsigned ba0_int_p) (u3 * u3) <
          (unsigned ba0_int_p) ba0_mint_hp_module / 2)
        {
          ba0_int_p s, t;
          if (u1 > 0)
            {
              q = bingcdext ((ba0_mint_hp) u1, ba0_mint_hp_module, &s, &t);
              if (q != 1)
                {
                  if (ddz != (ba0_int_hp *) 0)
                    *ddz = (ba0_int_hp) q;
                  return ba0_zero_divisor;
/*
		    BA0_RAISE_EXCEPTION (BA0_EXWDDZ);
*/
                }
              ba0_mpq_set_si_si (rat, opp ? -u3 : u3, u1);
              return ba0_rational_found;
            }
          else
            {
              q = bingcdext ((ba0_int_hp) - u1, ba0_mint_hp_module, &s, &t);
              if (q != 1)
                {
                  if (ddz != (ba0_int_hp *) 0)
                    *ddz = (ba0_int_hp) q;
                  return ba0_zero_divisor;
/*
		    BA0_RAISE_EXCEPTION (BA0_EXWDDZ);
*/
                }
              ba0_mpq_set_si_si (rat, opp ? u3 : -u3, -u1);
              return ba0_rational_found;
            }
        }
      if (v3 == 0)
        return ba0_rational_not_found;
/*
	    BA0_RAISE_EXCEPTION (BA0_EXWRNT);
*/
      q = u3 / v3;
      t1 = v1;
      v1 = u1 - q * v1;
      u1 = t1;
      t3 = v3;
      v3 = u3 - q * v3;
      u3 = t3;
    }
  return ba0_rational_found;    /* to avoid annoying warnings */
}
