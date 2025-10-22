#include "baz_factor_polynom_mpq.h"
#include "baz_factor_polynom_mpz.h"

/*
 * texinfo: baz_factor_polynom_mpq
 * Assign to @var{R} the complete factorization of @var{A}
 * over the ring of integer numbers.
 */

BAZ_DLL void
baz_factor_polynom_mpq (
    struct bap_product_mpq *R,
    struct bap_polynom_mpq *A)
{
  struct bap_product_mpz P;
  struct bap_polynom_mpz numer;
  ba0_mpz_t denom;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  bap_init_polynom_mpz (&numer);
  bap_init_product_mpz (&P);
  ba0_mpz_init (denom);

  bap_numer_polynom_mpq (&numer, denom, A);
  baz_factor_polynom_mpz (&P, &numer);

  ba0_pull_stack ();

  bap_product_mpz_to_mpq (R, &P);
  ba0_mpz_mul (ba0_mpq_denref (R->num_factor), ba0_mpq_denref (R->num_factor),
      denom);
  ba0_mpq_canonicalize (R->num_factor);

  ba0_restore (&M);
}
