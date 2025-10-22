#include "bap_polynom_mpq.h"
#include "bap_add_polynom_mpq.h"
#include "bap_mul_polynom_mpq.h"
#include "bap_prem_polynom_mpq.h"
#include "bap_itermon_mpq.h"
#include "bap_creator_mpq.h"
#include "bap_invert_mpq.h"

#define BAD_FLAG_mpq

/*
	Polynomials with invertible numerical coefficients
*/

/* Makes $A$ numerically monic. Result in $R$. */

BAP_DLL void
bap_numeric_initial_one_polynom_mpq (
    struct bap_polynom_mpq *R,
    struct bap_polynom_mpq *A)
{
  ba0_mpq_t a;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  ba0_mpq_init (a);
  ba0_mpq_invert (a, *bap_numeric_initial_polynom_mpq (A));
  ba0_pull_stack ();
  bap_mul_polynom_numeric_mpq (R, A, a);
  ba0_record (&M);
}

/*
 * Stores the quotient and the remainder of the Euclidean division
 * of $A$ by $B$ in $Q$ and $R$. The parameter $Q$ may be zero.
 * $A$ and $B$ are assumed to be univariate.
 */

BAP_DLL void
bap_Euclidean_division_polynom_mpq (
    struct bap_polynom_mpq *Q,
    struct bap_polynom_mpq *R,
    struct bap_polynom_mpq *A,
    struct bap_polynom_mpq *B)
{
  struct bap_creator_mpq crea;
  struct bap_itermon_mpq iterB, iterreste;
  struct bap_polynom_mpq reste;
  struct bap_polynom_mpq *quotient = (struct bap_polynom_mpq *) 0;
  ba0_mpq_t b, q;
  struct bav_term TB, TQ, Treste;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_mpq_init (b);
  bav_init_term (&TB);
/*
   Cas B = constante
*/
  bap_begin_itermon_mpq (&iterB, B);
  bap_term_itermon_mpq (&TB, &iterB);
  ba0_mpq_invert (b, *bap_coeff_itermon_mpq (&iterB));
  if (bav_is_one_term (&TB))
    {
      ba0_pull_stack ();
      if (Q != (struct bap_polynom_mpq *) 0)
        {
          if (ba0_mpq_is_one (b))
            {
              if (Q != A)
                bap_set_polynom_mpq (Q, A);
            }
          else
            bap_mul_polynom_numeric_mpq (Q, A, b);
        }
      bap_set_polynom_zero_mpq (R);
      ba0_restore (&M);
      return;
    }
/*
   Cas ou deg A < deg B
*/
  if (!bap_is_zero_polynom_mpq (A))
    {
      bap_begin_itermon_mpq (&iterreste, A);
      bav_init_term (&Treste);
      bap_term_itermon_mpq (&Treste, &iterreste);
      bav_init_term (&TQ);
    }
  if (bap_is_zero_polynom_mpq (A) || !bav_is_factor_term (&Treste, &TB, &TQ))
    {
      ba0_pull_stack ();
      if (Q != (struct bap_polynom_mpq *) 0)
        bap_set_polynom_zero_mpq (Q);
      if (R != A)
        bap_set_polynom_mpq (R, A);
      ba0_restore (&M);
      return;
    }
/*
   Cas general : deg A >= deg B > 0
*/
  if (Q != (struct bap_polynom_mpq *) 0)
    {
      quotient = bap_new_polynom_mpq ();
      bap_begin_creator_mpq (&crea, quotient, &TQ, bap_exact_total_rank,
          bap_nbmon_polynom_mpq (A));
    }
  ba0_mpq_init (q);
  ba0_mpq_mul (q, *bap_coeff_itermon_mpq (&iterreste), b);
  bap_init_polynom_mpq (&reste);
  bap_submulmon_polynom_mpq (&reste, A, B, &TQ, q);
  if (Q != (struct bap_polynom_mpq *) 0)
    bap_write_creator_mpq (&crea, &TQ, q);

  for (;;)
    {
      if (bap_is_zero_polynom_mpq (&reste))
        break;
      bap_begin_itermon_mpq (&iterreste, &reste);
      bap_term_itermon_mpq (&Treste, &iterreste);
      if (!bav_is_factor_term (&Treste, &TB, &TQ))
        break;
      ba0_mpq_mul (q, *bap_coeff_itermon_mpq (&iterreste), b);
      bap_submulmon_polynom_mpq (&reste, &reste, B, &TQ, q);
      if (Q != (struct bap_polynom_mpq *) 0)
        bap_write_creator_mpq (&crea, &TQ, q);
    }
  if (Q != (struct bap_polynom_mpq *) 0)
    bap_close_creator_mpq (&crea);
  ba0_pull_stack ();
  if (Q != (struct bap_polynom_mpq *) 0)
    bap_set_polynom_mpq (Q, quotient);
  bap_set_polynom_mpq (R, &reste);
  ba0_restore (&M);
}

/*
 * Sets $G$ to the monic gcd of $A$ and $B$.
 * The computation is performed by the basic Euclidean algorithm.
 * Polynomials are assumed to be univariate.
 */

BAP_DLL void
bap_Euclid_polynom_mpq (
    struct bap_polynom_mpq *G,
    struct bap_polynom_mpq *A,
    struct bap_polynom_mpq *B)
{
  struct bap_polynom_mpq *U3, *V3, *T3;
  struct ba0_mark M;

  if (bap_lt_rank_polynom_mpq (A, B))
    BA0_SWAP (struct bap_polynom_mpq *,
        A,
        B);

  ba0_push_another_stack ();
  ba0_record (&M);

  U3 = bap_new_polynom_mpq ();
  V3 = bap_new_polynom_mpq ();
  T3 = bap_new_polynom_mpq ();

  if (bap_is_zero_polynom_mpq (B))
    bap_set_polynom_mpq (U3, A);
  else
    {
      bap_Euclidean_division_polynom_mpq ((struct bap_polynom_mpq *) 0, V3,
          A, B);
      bap_set_polynom_mpq (U3, B);
      while (!bap_is_zero_polynom_mpq (V3))
        {
          bap_set_polynom_mpq (T3, V3);
          bap_Euclidean_division_polynom_mpq ((struct bap_polynom_mpq *) 0,
              V3, U3, V3);
          BA0_SWAP (struct bap_polynom_mpq *,
              U3,
              T3);
        }
    }
  if (!bap_is_zero_polynom_mpq (U3))
    bap_numeric_initial_one_polynom_mpq (U3, U3);
  ba0_pull_stack ();
  bap_set_polynom_mpq (G, U3);
  ba0_restore (&M);
}

/*
 * Stores in $U$, $V$ and $G$ three polynomials such that
 * $U\,A + V\,B = G = A \wedge B$. The gcd $G$ is monic.
 * The extended Euclidean algorithm is applied.
 * Polynomials are assumed to be univariate.
 */

BAP_DLL void
bap_extended_Euclid_polynom_mpq (
    struct bap_polynom_mpq *U,
    struct bap_polynom_mpq *V,
    struct bap_polynom_mpq *G,
    struct bap_polynom_mpq *A,
    struct bap_polynom_mpq *B)
{
  struct bap_polynom_mpq *U1, *U3, *V1, *V3, *T1, *T3, *Q;
  ba0_mpq_t a;
  struct ba0_mark M;

  if (bap_lt_rank_polynom_mpq (A, B))
    {
      BA0_SWAP (struct bap_polynom_mpq *,
          A,
          B);
      BA0_SWAP (struct bap_polynom_mpq *,
          U,
          V);
    }

  ba0_push_another_stack ();
  ba0_record (&M);

  U1 = bap_new_polynom_one_mpq ();
  U3 = bap_new_polynom_mpq ();
  bap_set_polynom_mpq (U3, A);
  V1 = bap_new_polynom_mpq ();
  V3 = bap_new_polynom_mpq ();
  bap_set_polynom_mpq (V3, B);
  Q = bap_new_polynom_mpq ();
  T1 = bap_new_polynom_mpq ();
  T3 = bap_new_polynom_mpq ();
  while (!bap_is_zero_polynom_mpq (V3))
    {
      bap_set_polynom_mpq (T3, V3);
      bap_Euclidean_division_polynom_mpq (Q, V3, U3, V3);
      BA0_SWAP (struct bap_polynom_mpq *,
          U3,
          T3);
      bap_set_polynom_mpq (T1, V1);
      bap_mul_polynom_mpq (Q, Q, V1);
      bap_sub_polynom_mpq (V1, U1, Q);
      BA0_SWAP (struct bap_polynom_mpq *,
          U1,
          T1);
    }
  if (!bap_is_zero_polynom_mpq (U3))
    {
      ba0_mpq_init (a);
      ba0_mpq_invert (a, *bap_numeric_initial_polynom_mpq (U3));
      bap_mul_polynom_numeric_mpq (U3, U3, a);
      bap_mul_polynom_numeric_mpq (U1, U1, a);
    }
  bap_mul_polynom_mpq (T1, U1, A);
  bap_sub_polynom_mpq (T1, U3, T1);
  ba0_pull_stack ();
  bap_set_polynom_mpq (U, U1);
  bap_exquo_polynom_mpq (V, T1, B);
  bap_set_polynom_mpq (G, U3);
  ba0_restore (&M);
}

#undef BAD_FLAG_mpq
