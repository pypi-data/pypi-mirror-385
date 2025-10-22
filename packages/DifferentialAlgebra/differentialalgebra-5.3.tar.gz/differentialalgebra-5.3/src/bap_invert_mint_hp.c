#include "bap_polynom_mint_hp.h"
#include "bap_add_polynom_mint_hp.h"
#include "bap_mul_polynom_mint_hp.h"
#include "bap_prem_polynom_mint_hp.h"
#include "bap_itermon_mint_hp.h"
#include "bap_creator_mint_hp.h"
#include "bap_invert_mint_hp.h"

#define BAD_FLAG_mint_hp

/*
	Polynomials with invertible numerical coefficients
*/

/* Makes $A$ numerically monic. Result in $R$. */

BAP_DLL void
bap_numeric_initial_one_polynom_mint_hp (
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A)
{
  ba0_mint_hp_t a;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mint_hp_init (a);
  ba0_mint_hp_invert (a, *bap_numeric_initial_polynom_mint_hp (A));
  ba0_pull_stack ();
  bap_mul_polynom_numeric_mint_hp (R, A, a);
  ba0_record (&M);
}

/*
 * Stores the quotient and the remainder of the Euclidean division
 * of $A$ by $B$ in $Q$ and $R$. The parameter $Q$ may be zero.
 * $A$ and $B$ are assumed to be univariate.
 */

BAP_DLL void
bap_Euclidean_division_polynom_mint_hp (
    struct bap_polynom_mint_hp *Q,
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mint_hp *A,
    struct bap_polynom_mint_hp *B)
{
  struct bap_creator_mint_hp crea;
  struct bap_itermon_mint_hp iterB, iterreste;
  struct bap_polynom_mint_hp reste;
  struct bap_polynom_mint_hp *quotient = (struct bap_polynom_mint_hp *) 0;
  ba0_mint_hp_t b, q;
  struct bav_term TB, TQ, Treste;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_mint_hp_init (b);
  bav_init_term (&TB);
/*
   Cas B = constante
*/
  bap_begin_itermon_mint_hp (&iterB, B);
  bap_term_itermon_mint_hp (&TB, &iterB);
  ba0_mint_hp_invert (b, *bap_coeff_itermon_mint_hp (&iterB));
  if (bav_is_one_term (&TB))
    {
      ba0_pull_stack ();
      if (Q != (struct bap_polynom_mint_hp *) 0)
        {
          if (ba0_mint_hp_is_one (b))
            {
              if (Q != A)
                bap_set_polynom_mint_hp (Q, A);
            }
          else
            bap_mul_polynom_numeric_mint_hp (Q, A, b);
        }
      bap_set_polynom_zero_mint_hp (R);
      ba0_restore (&M);
      return;
    }
/*
   Cas ou deg A < deg B
*/
  if (!bap_is_zero_polynom_mint_hp (A))
    {
      bap_begin_itermon_mint_hp (&iterreste, A);
      bav_init_term (&Treste);
      bap_term_itermon_mint_hp (&Treste, &iterreste);
      bav_init_term (&TQ);
    }
  if (bap_is_zero_polynom_mint_hp (A) || !bav_is_factor_term (&Treste, &TB, &TQ))
    {
      ba0_pull_stack ();
      if (Q != (struct bap_polynom_mint_hp *) 0)
        bap_set_polynom_zero_mint_hp (Q);
      if (R != A)
        bap_set_polynom_mint_hp (R, A);
      ba0_restore (&M);
      return;
    }
/*
   Cas general : deg A >= deg B > 0
*/
  if (Q != (struct bap_polynom_mint_hp *) 0)
    {
      quotient = bap_new_polynom_mint_hp ();
      bap_begin_creator_mint_hp (&crea, quotient, &TQ, bap_exact_total_rank,
          bap_nbmon_polynom_mint_hp (A));
    }
  ba0_mint_hp_init (q);
  ba0_mint_hp_mul (q, *bap_coeff_itermon_mint_hp (&iterreste), b);
  bap_init_polynom_mint_hp (&reste);
  bap_submulmon_polynom_mint_hp (&reste, A, B, &TQ, q);
  if (Q != (struct bap_polynom_mint_hp *) 0)
    bap_write_creator_mint_hp (&crea, &TQ, q);

  for (;;)
    {
      if (bap_is_zero_polynom_mint_hp (&reste))
        break;
      bap_begin_itermon_mint_hp (&iterreste, &reste);
      bap_term_itermon_mint_hp (&Treste, &iterreste);
      if (!bav_is_factor_term (&Treste, &TB, &TQ))
        break;
      ba0_mint_hp_mul (q, *bap_coeff_itermon_mint_hp (&iterreste), b);
      bap_submulmon_polynom_mint_hp (&reste, &reste, B, &TQ, q);
      if (Q != (struct bap_polynom_mint_hp *) 0)
        bap_write_creator_mint_hp (&crea, &TQ, q);
    }
  if (Q != (struct bap_polynom_mint_hp *) 0)
    bap_close_creator_mint_hp (&crea);
  ba0_pull_stack ();
  if (Q != (struct bap_polynom_mint_hp *) 0)
    bap_set_polynom_mint_hp (Q, quotient);
  bap_set_polynom_mint_hp (R, &reste);
  ba0_restore (&M);
}

/*
 * Sets $G$ to the monic gcd of $A$ and $B$.
 * The computation is performed by the basic Euclidean algorithm.
 * Polynomials are assumed to be univariate.
 */

BAP_DLL void
bap_Euclid_polynom_mint_hp (
    struct bap_polynom_mint_hp *G,
    struct bap_polynom_mint_hp *A,
    struct bap_polynom_mint_hp *B)
{
  struct bap_polynom_mint_hp *U3, *V3, *T3;
  struct ba0_mark M;

  if (bap_lt_rank_polynom_mint_hp (A, B))
    BA0_SWAP (struct bap_polynom_mint_hp *,
        A,
        B);

  ba0_push_another_stack ();
  ba0_record (&M);

  U3 = bap_new_polynom_mint_hp ();
  V3 = bap_new_polynom_mint_hp ();
  T3 = bap_new_polynom_mint_hp ();

  if (bap_is_zero_polynom_mint_hp (B))
    bap_set_polynom_mint_hp (U3, A);
  else
    {
      bap_Euclidean_division_polynom_mint_hp ((struct bap_polynom_mint_hp *) 0, V3,
          A, B);
      bap_set_polynom_mint_hp (U3, B);
      while (!bap_is_zero_polynom_mint_hp (V3))
        {
          bap_set_polynom_mint_hp (T3, V3);
          bap_Euclidean_division_polynom_mint_hp ((struct bap_polynom_mint_hp *) 0,
              V3, U3, V3);
          BA0_SWAP (struct bap_polynom_mint_hp *,
              U3,
              T3);
        }
    }
  if (!bap_is_zero_polynom_mint_hp (U3))
    bap_numeric_initial_one_polynom_mint_hp (U3, U3);
  ba0_pull_stack ();
  bap_set_polynom_mint_hp (G, U3);
  ba0_restore (&M);
}

/*
 * Stores in $U$, $V$ and $G$ three polynomials such that
 * $U\,A + V\,B = G = A \wedge B$. The gcd $G$ is monic.
 * The extended Euclidean algorithm is applied.
 * Polynomials are assumed to be univariate.
 */

BAP_DLL void
bap_extended_Euclid_polynom_mint_hp (
    struct bap_polynom_mint_hp *U,
    struct bap_polynom_mint_hp *V,
    struct bap_polynom_mint_hp *G,
    struct bap_polynom_mint_hp *A,
    struct bap_polynom_mint_hp *B)
{
  struct bap_polynom_mint_hp *U1, *U3, *V1, *V3, *T1, *T3, *Q;
  ba0_mint_hp_t a;
  struct ba0_mark M;

  if (bap_lt_rank_polynom_mint_hp (A, B))
    {
      BA0_SWAP (struct bap_polynom_mint_hp *,
          A,
          B);
      BA0_SWAP (struct bap_polynom_mint_hp *,
          U,
          V);
    }

  ba0_push_another_stack ();
  ba0_record (&M);

  U1 = bap_new_polynom_one_mint_hp ();
  U3 = bap_new_polynom_mint_hp ();
  bap_set_polynom_mint_hp (U3, A);
  V1 = bap_new_polynom_mint_hp ();
  V3 = bap_new_polynom_mint_hp ();
  bap_set_polynom_mint_hp (V3, B);
  Q = bap_new_polynom_mint_hp ();
  T1 = bap_new_polynom_mint_hp ();
  T3 = bap_new_polynom_mint_hp ();
  while (!bap_is_zero_polynom_mint_hp (V3))
    {
      bap_set_polynom_mint_hp (T3, V3);
      bap_Euclidean_division_polynom_mint_hp (Q, V3, U3, V3);
      BA0_SWAP (struct bap_polynom_mint_hp *,
          U3,
          T3);
      bap_set_polynom_mint_hp (T1, V1);
      bap_mul_polynom_mint_hp (Q, Q, V1);
      bap_sub_polynom_mint_hp (V1, U1, Q);
      BA0_SWAP (struct bap_polynom_mint_hp *,
          U1,
          T1);
    }
  if (!bap_is_zero_polynom_mint_hp (U3))
    {
      ba0_mint_hp_init (a);
      ba0_mint_hp_invert (a, *bap_numeric_initial_polynom_mint_hp (U3));
      bap_mul_polynom_numeric_mint_hp (U3, U3, a);
      bap_mul_polynom_numeric_mint_hp (U1, U1, a);
    }
  bap_mul_polynom_mint_hp (T1, U1, A);
  bap_sub_polynom_mint_hp (T1, U3, T1);
  ba0_pull_stack ();
  bap_set_polynom_mint_hp (U, U1);
  bap_exquo_polynom_mint_hp (V, T1, B);
  bap_set_polynom_mint_hp (G, U3);
  ba0_restore (&M);
}

#undef BAD_FLAG_mint_hp
