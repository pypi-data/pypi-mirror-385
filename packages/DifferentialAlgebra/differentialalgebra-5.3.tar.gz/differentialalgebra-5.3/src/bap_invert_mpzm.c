#include "bap_polynom_mpzm.h"
#include "bap_add_polynom_mpzm.h"
#include "bap_mul_polynom_mpzm.h"
#include "bap_prem_polynom_mpzm.h"
#include "bap_itermon_mpzm.h"
#include "bap_creator_mpzm.h"
#include "bap_invert_mpzm.h"

#define BAD_FLAG_mpzm

/*
	Polynomials with invertible numerical coefficients
*/

/* Makes $A$ numerically monic. Result in $R$. */

BAP_DLL void
bap_numeric_initial_one_polynom_mpzm (
    struct bap_polynom_mpzm *R,
    struct bap_polynom_mpzm *A)
{
  ba0_mpzm_t a;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mpzm_init (a);
  ba0_mpzm_invert (a, *bap_numeric_initial_polynom_mpzm (A));
  ba0_pull_stack ();
  bap_mul_polynom_numeric_mpzm (R, A, a);
  ba0_record (&M);
}

/*
 * Stores the quotient and the remainder of the Euclidean division
 * of $A$ by $B$ in $Q$ and $R$. The parameter $Q$ may be zero.
 * $A$ and $B$ are assumed to be univariate.
 */

BAP_DLL void
bap_Euclidean_division_polynom_mpzm (
    struct bap_polynom_mpzm *Q,
    struct bap_polynom_mpzm *R,
    struct bap_polynom_mpzm *A,
    struct bap_polynom_mpzm *B)
{
  struct bap_creator_mpzm crea;
  struct bap_itermon_mpzm iterB, iterreste;
  struct bap_polynom_mpzm reste;
  struct bap_polynom_mpzm *quotient = (struct bap_polynom_mpzm *) 0;
  ba0_mpzm_t b, q;
  struct bav_term TB, TQ, Treste;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_mpzm_init (b);
  bav_init_term (&TB);
/*
   Cas B = constante
*/
  bap_begin_itermon_mpzm (&iterB, B);
  bap_term_itermon_mpzm (&TB, &iterB);
  ba0_mpzm_invert (b, *bap_coeff_itermon_mpzm (&iterB));
  if (bav_is_one_term (&TB))
    {
      ba0_pull_stack ();
      if (Q != (struct bap_polynom_mpzm *) 0)
        {
          if (ba0_mpzm_is_one (b))
            {
              if (Q != A)
                bap_set_polynom_mpzm (Q, A);
            }
          else
            bap_mul_polynom_numeric_mpzm (Q, A, b);
        }
      bap_set_polynom_zero_mpzm (R);
      ba0_restore (&M);
      return;
    }
/*
   Cas ou deg A < deg B
*/
  if (!bap_is_zero_polynom_mpzm (A))
    {
      bap_begin_itermon_mpzm (&iterreste, A);
      bav_init_term (&Treste);
      bap_term_itermon_mpzm (&Treste, &iterreste);
      bav_init_term (&TQ);
    }
  if (bap_is_zero_polynom_mpzm (A) || !bav_is_factor_term (&Treste, &TB, &TQ))
    {
      ba0_pull_stack ();
      if (Q != (struct bap_polynom_mpzm *) 0)
        bap_set_polynom_zero_mpzm (Q);
      if (R != A)
        bap_set_polynom_mpzm (R, A);
      ba0_restore (&M);
      return;
    }
/*
   Cas general : deg A >= deg B > 0
*/
  if (Q != (struct bap_polynom_mpzm *) 0)
    {
      quotient = bap_new_polynom_mpzm ();
      bap_begin_creator_mpzm (&crea, quotient, &TQ, bap_exact_total_rank,
          bap_nbmon_polynom_mpzm (A));
    }
  ba0_mpzm_init (q);
  ba0_mpzm_mul (q, *bap_coeff_itermon_mpzm (&iterreste), b);
  bap_init_polynom_mpzm (&reste);
  bap_submulmon_polynom_mpzm (&reste, A, B, &TQ, q);
  if (Q != (struct bap_polynom_mpzm *) 0)
    bap_write_creator_mpzm (&crea, &TQ, q);

  for (;;)
    {
      if (bap_is_zero_polynom_mpzm (&reste))
        break;
      bap_begin_itermon_mpzm (&iterreste, &reste);
      bap_term_itermon_mpzm (&Treste, &iterreste);
      if (!bav_is_factor_term (&Treste, &TB, &TQ))
        break;
      ba0_mpzm_mul (q, *bap_coeff_itermon_mpzm (&iterreste), b);
      bap_submulmon_polynom_mpzm (&reste, &reste, B, &TQ, q);
      if (Q != (struct bap_polynom_mpzm *) 0)
        bap_write_creator_mpzm (&crea, &TQ, q);
    }
  if (Q != (struct bap_polynom_mpzm *) 0)
    bap_close_creator_mpzm (&crea);
  ba0_pull_stack ();
  if (Q != (struct bap_polynom_mpzm *) 0)
    bap_set_polynom_mpzm (Q, quotient);
  bap_set_polynom_mpzm (R, &reste);
  ba0_restore (&M);
}

/*
 * Sets $G$ to the monic gcd of $A$ and $B$.
 * The computation is performed by the basic Euclidean algorithm.
 * Polynomials are assumed to be univariate.
 */

BAP_DLL void
bap_Euclid_polynom_mpzm (
    struct bap_polynom_mpzm *G,
    struct bap_polynom_mpzm *A,
    struct bap_polynom_mpzm *B)
{
  struct bap_polynom_mpzm *U3, *V3, *T3;
  struct ba0_mark M;

  if (bap_lt_rank_polynom_mpzm (A, B))
    BA0_SWAP (struct bap_polynom_mpzm *,
        A,
        B);

  ba0_push_another_stack ();
  ba0_record (&M);

  U3 = bap_new_polynom_mpzm ();
  V3 = bap_new_polynom_mpzm ();
  T3 = bap_new_polynom_mpzm ();

  if (bap_is_zero_polynom_mpzm (B))
    bap_set_polynom_mpzm (U3, A);
  else
    {
      bap_Euclidean_division_polynom_mpzm ((struct bap_polynom_mpzm *) 0, V3,
          A, B);
      bap_set_polynom_mpzm (U3, B);
      while (!bap_is_zero_polynom_mpzm (V3))
        {
          bap_set_polynom_mpzm (T3, V3);
          bap_Euclidean_division_polynom_mpzm ((struct bap_polynom_mpzm *) 0,
              V3, U3, V3);
          BA0_SWAP (struct bap_polynom_mpzm *,
              U3,
              T3);
        }
    }
  if (!bap_is_zero_polynom_mpzm (U3))
    bap_numeric_initial_one_polynom_mpzm (U3, U3);
  ba0_pull_stack ();
  bap_set_polynom_mpzm (G, U3);
  ba0_restore (&M);
}

/*
 * Stores in $U$, $V$ and $G$ three polynomials such that
 * $U\,A + V\,B = G = A \wedge B$. The gcd $G$ is monic.
 * The extended Euclidean algorithm is applied.
 * Polynomials are assumed to be univariate.
 */

BAP_DLL void
bap_extended_Euclid_polynom_mpzm (
    struct bap_polynom_mpzm *U,
    struct bap_polynom_mpzm *V,
    struct bap_polynom_mpzm *G,
    struct bap_polynom_mpzm *A,
    struct bap_polynom_mpzm *B)
{
  struct bap_polynom_mpzm *U1, *U3, *V1, *V3, *T1, *T3, *Q;
  ba0_mpzm_t a;
  struct ba0_mark M;

  if (bap_lt_rank_polynom_mpzm (A, B))
    {
      BA0_SWAP (struct bap_polynom_mpzm *,
          A,
          B);
      BA0_SWAP (struct bap_polynom_mpzm *,
          U,
          V);
    }

  ba0_push_another_stack ();
  ba0_record (&M);

  U1 = bap_new_polynom_one_mpzm ();
  U3 = bap_new_polynom_mpzm ();
  bap_set_polynom_mpzm (U3, A);
  V1 = bap_new_polynom_mpzm ();
  V3 = bap_new_polynom_mpzm ();
  bap_set_polynom_mpzm (V3, B);
  Q = bap_new_polynom_mpzm ();
  T1 = bap_new_polynom_mpzm ();
  T3 = bap_new_polynom_mpzm ();
  while (!bap_is_zero_polynom_mpzm (V3))
    {
      bap_set_polynom_mpzm (T3, V3);
      bap_Euclidean_division_polynom_mpzm (Q, V3, U3, V3);
      BA0_SWAP (struct bap_polynom_mpzm *,
          U3,
          T3);
      bap_set_polynom_mpzm (T1, V1);
      bap_mul_polynom_mpzm (Q, Q, V1);
      bap_sub_polynom_mpzm (V1, U1, Q);
      BA0_SWAP (struct bap_polynom_mpzm *,
          U1,
          T1);
    }
  if (!bap_is_zero_polynom_mpzm (U3))
    {
      ba0_mpzm_init (a);
      ba0_mpzm_invert (a, *bap_numeric_initial_polynom_mpzm (U3));
      bap_mul_polynom_numeric_mpzm (U3, U3, a);
      bap_mul_polynom_numeric_mpzm (U1, U1, a);
    }
  bap_mul_polynom_mpzm (T1, U1, A);
  bap_sub_polynom_mpzm (T1, U3, T1);
  ba0_pull_stack ();
  bap_set_polynom_mpzm (U, U1);
  bap_exquo_polynom_mpzm (V, T1, B);
  bap_set_polynom_mpzm (G, U3);
  ba0_restore (&M);
}

#undef BAD_FLAG_mpzm
