#include "ba0_exception.h"
#include "ba0_small_p.h"

/*
 * Returns the largest small prime
 */

BA0_DLL ba0_mint_hp
ba0_largest_small_prime (
    void)
{
/*
 * Specific hack to handle APPLE_UNIVERSAL_OSX code
 */
#if defined (BA0_APPLE_UNIVERSAL_OSX)
  if (sizeof (ba0_int_p) == 4)
    return BA0_MAX_PRIME_16BITS;
  else
    return BA0_MAX_PRIME_32BITS;
#else
  return BA0_MAX_PRIME_MINT_HP;
#endif
}

BA0_DLL ba0_mint_hp
ba0_smallest_small_prime (
    void)
{
  return 3;
}

static bool
is_a_small_prime (
    ba0_mint_hp a)
{
  static unsigned ba0_int_p t[] = { 4, 2, 4, 2, 4, 6, 2, 6 };
  unsigned ba0_int_p c, n = (unsigned ba0_int_p) a;
  ba0_mint_hp i;

  if (n == 2 || n == 3 || n == 5)
    return true;
  if (n % 2 == 0 || n % 3 == 0 || n % 5 == 0)
    return false;
  for (c = 7, i = 0; c * c <= n; c += t[i], i = (i + 1) % 8)
    if (n % c == 0)
      return false;
  return true;
}

BA0_DLL ba0_mint_hp
ba0_previous_small_prime (
    ba0_mint_hp n)
{
  ba0_mint_hp p;

  if (n <= 3)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  p = n % 2 == 0 ? n - 1 : n - 2;
  while (p > 2 && !is_a_small_prime (p))
    p -= 2;
  if (p <= 2)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  return p;
}

BA0_DLL ba0_mint_hp
ba0_next_small_prime (
    ba0_mint_hp n)
{
  ba0_mint_hp p, bound;

  bound = ba0_largest_small_prime ();
  if (n >= bound)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  p = n % 2 == 0 ? n + 1 : n + 2;
  while (p <= bound && !is_a_small_prime (p))
    p += 2;
  if (p > bound)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  return p;
}
