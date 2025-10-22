#include "bad_reduction.h"
#include "bad_invert.h"
#include "bad_global.h"

/*
 * A0 and B0 are polynomials with leading derivative x.
 * The initial of B0 is nonzero mod C
 *
 * Computes U1, U2 and U3 such that U1 * A0 + U2 * B0 = U3 mod C
 *                                  U3 is a gcd (mod C) of A0 and B0
 *
 * (except that U2 is not computed and not returned).
 *
 * The ordering is assumed to be rearranged so that L >> N
 * where L = Leaders (C) and N = Non-Leaders (C, A0, B0)
 */

static void
bad_half_Euclid (
    struct bap_polynom_mpz *U1,
    struct bap_polynom_mpz *U3,
    struct bap_polynom_mpz *A0,
    struct bap_polynom_mpz *B0,
    struct bav_variable *x,
    struct bad_regchain *C)
{
  struct bap_tableof_polynom_mpz polys;
  struct bap_product_mpz *H;
  struct bap_polynom_mpz *U_1, *U_3, *V_1, *V_3, *Q, *R, *S;
  ba0_int_p counter;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  U_1 = bap_new_polynom_mpz ();
  V_1 = bap_new_polynom_mpz ();

  if (bap_degree_polynom_mpz (A0, x) >= bap_degree_polynom_mpz (B0, x))
    {
      bap_set_polynom_one_mpz (U_1);
      U_3 = A0;
      V_3 = B0;
    }
  else
    {
      bap_set_polynom_one_mpz (V_1);
      V_3 = A0;
      U_3 = B0;
    }

  Q = bap_new_polynom_mpz ();
  R = bap_new_polynom_mpz ();
  S = bap_new_polynom_mpz ();
  H = bap_new_product_mpz ();
/*
 * No need to realloc2
 */
  ba0_init_table ((struct ba0_table *) &polys);
  ba0_realloc_table ((struct ba0_table *) &polys, 2);

  counter = 0;
/*
 * Loop invariants:
 * U_1 * A0 + U_2 * B0 = U_3 mod C
 * V_1 * A0 + V_2 * B0 = V_3 mod C
 */
  while (!bap_is_zero_polynom_mpz (V_3))
    {
      baz_gcd_pseudo_division_polynom_mpz (Q, R, H, U_3, V_3, x);
      bad_reduce_easy_polynom_by_regchain (R, R, C, bad_algebraic_reduction);
      bad_reduce_easy_polynom_by_regchain (Q, Q, C, bad_algebraic_reduction);
      bad_ensure_nonzero_initial_mod_regchain (R, R, C,
          bad_algebraic_reduction);
/*
 * H * U_3 = Q * V_3 + R mod C
 */
      bap_mul_polynom_mpz (Q, Q, V_1);
      bap_mul_product_polynom_mpz (H, H, U_1, 1);
      bap_expand_product_mpz (S, H);
      bap_sub_polynom_mpz (S, S, Q);
/*
 * S = H * U_1 - Q * V_1 
 */
      polys.tab[0] = S;
      polys.tab[1] = R;
      polys.size = 2;
      baz_content_tableof_polynom_mpz (H, &polys, x, true);
      bap_expand_product_mpz (Q, H);
      if (!bap_is_one_polynom_mpz (Q))
        {
          bap_exquo_polynom_mpz (R, R, Q);
          bap_exquo_polynom_mpz (S, S, Q);
        }
/*
 * Q = the gcd of the coefficients (wrt x) of S and R together
 * S = S / Q
 * R = R / Q
 */
      BA0_SWAP (struct bap_polynom_mpz *,
          U_1,
          V_1);
      if (counter < 2)
        {
          U_3 = V_3;
          V_3 = bap_new_polynom_mpz ();
        }
      else
        BA0_SWAP (struct bap_polynom_mpz *,
            U_3,
            V_3);
/*
 * A bit complicated stuff in order not to override A0 and B0
 */
      BA0_SWAP (struct bap_polynom_mpz *,
          V_1,
          S);
      BA0_SWAP (struct bap_polynom_mpz *,
          V_3,
          R);
/*
 * U_1 = V_1
 * U_3 = V_3
 * V_1 = S
 * V_3 = R
 */
      counter += 1;
    }
  ba0_pull_stack ();
  if (U1 != U_1)
    bap_set_polynom_mpz (U1, U_1);
  if (U3 != U_3)
    bap_set_polynom_mpz (U3, U_3);
  ba0_restore (&M);
}

/*
 * Computes an inverse of A modulo C, i.e products U and G such that
 *
 *             U * A = G mod C (algebraically)
 *
 *             U in K [L, N] 
 *             G in K [N]
 *
 * By a well-known theorem, G is then not a zero divisor and 1/A = U/G mod C
 *
 * Any exhibited zerodivisor is returned through ddz.
 * The case A = 0 is handled.
 *
 * The ordering is assumed to be rearranged so that L >> N
 * where L = Leaders (C) and N = Non-Leaders (C, A)
 */

static void
bad_algebraic_invert_polynom_mod_regchain_zero_dimensional (
    struct bap_product_mpz *U,
    struct bap_polynom_mpz *G,
    struct bap_polynom_mpz *A,
    struct bad_regchain *C,
    struct bap_polynom_mpz *volatile *ddz)
{
  struct bad_regchain Cbar;
  struct bap_product_mpz *U1;
  struct bap_polynom_mpz *U1bar, *U3;
  struct bav_variable *x;
  ba0_int_p k;
  struct ba0_mark M;
/*
 * Cbar is a working copy of C.
 */
  Cbar = *C;

  ba0_push_another_stack ();
  ba0_record (&M);

  U1 = bap_new_product_mpz ();
  U3 = bap_new_polynom_mpz ();
  U1bar = bap_new_polynom_mpz ();

  bad_ensure_nonzero_initial_mod_regchain (U3, A, C, bad_algebraic_reduction);
  if (bap_is_zero_polynom_mpz (U3))
    BA0_RAISE_EXCEPTION (BAD_EXRNUL);
/*
 * Loop invariant: U1 * A = U3 mod C
 */
  for (;;)
    {
/*
 * Using bad_nonzero would change the behaviour of the function, in the
 * case of computations over base fields presented by non-trivial relations
 *
 * See tests/base_field2.c
 */
      if (bap_is_independent_polynom_mpz (U3))
        break;
      x = bap_leader_polynom_mpz (U3);
      if (!bad_is_leader_of_regchain (x, C, &k))
        break;
/*
 * Cbar = { C[0], ..., C[k-1] }. 
 * Reductions by Cbar will only apply to the coefficients of the polynomials.
 * Otherwise, the reduce_easy operation creates problems.
 */
      Cbar.decision_system.size = k;
      bad_half_Euclid (U1bar, U3, U3, C->decision_system.tab[k], x, &Cbar);
      if (bap_depend_polynom_mpz (U3, x))
        {
          if (ddz != (struct bap_polynom_mpz * volatile *) 0)
            {
              *ddz = U3;
              BA0_RAISE_EXCEPTION2 (BAD_EXRDDZ, "%Az", (void **) ddz);
            }
          else
            BA0_RAISE_EXCEPTION (BAD_EXRDDZ);
        }
      bap_mul_product_polynom_mpz (U1, U1, U1bar, 1);
    }
  if (bap_is_zero_polynom_mpz (U3))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  ba0_pull_stack ();
  bap_set_product_mpz (U, U1);
  bap_set_polynom_mpz (G, U3);
  ba0_restore (&M);
}

/*
 * Compute an inverse of A modulo C, i.e products U and G such that
 *
 *             U * A = G mod C (algebraically)
 *
 *             U in K [L, N] 
 *             G in K [N]
 *
 * By a well-known theorem, G is then not a zero divisor and 1/A = U/G mod C
 *
 * Any exhibited zerodivisor is returned through ddz.
 * The case A = 0 is handled.
 *
 * This function performs a temporary change of ordering.
 */

static void
bad_algebraic_invert_product_mod_regchain (
    struct bap_product_mpz *U,
    struct bap_product_mpz *G,
    struct bap_product_mpz *A,
    struct bad_regchain *C,
    struct bad_base_field *K,
    struct bap_polynom_mpz *volatile *ddz)
{
  struct bad_regchain Cbar;
  struct bap_product_mpz Abar, Ubar, Gbar, U1;
  struct bap_polynom_mpz U3;
  struct bap_polynom_mpz *volatile ddzbar;      // ddzbar is volatile
  bav_Iordering r;
  ba0_int_p i;
  struct ba0_mark M;
/*
 * Get rid of the case A is zero
 */
  if (bap_is_zero_product_mpz (A))
    BA0_RAISE_EXCEPTION (BAD_EXRNUL);

  ba0_push_another_stack ();
  ba0_record (&M);
/*
 * Old strategy which does not take the base field K into account
 * May lead to useless computations. Improve me.
 */
  r = bad_ordering_eliminating_leaders_of_regchain (C);
  bav_push_ordering (r);
/*
 * It is better to remove the differential property since r is not a ranking
 * Moreover, one may want to compute algebraic inverses of non partially
 * reduced polynomials, modulo regular differential chains.
 */
  bad_init_regchain (&Cbar);
  bad_sort_regchain (&Cbar, C);
  bad_clear_property_attchain (&Cbar.attrib, bad_differential_ideal_property);

  bap_init_product_mpz (&Abar);
  bap_sort_product_mpz (&Abar, A);

  bap_init_product_mpz (&U1);
  bap_init_polynom_mpz (&U3);

  bap_init_product_mpz (&Ubar);
  bap_init_product_mpz (&Gbar);
  bap_set_product_numeric_mpz (&Gbar, Abar.num_factor);
/*
 * Denote Abar = c * mul (Abar[k] ** d[k], k = 1 .. t)
 * Loop invariant: 
 *
 *      Ubar * Abar = Gbar * mul (Abar[k] ** d[k], k = i .. t) mod C
 *
 * Thus, initially Ubar = 1 and Gbar = c
 */
  for (i = 0; i < Abar.size; i++)
    {
      if (Abar.tab[i].exponent > 0)
        {
          BA0_TRY
          {
/*
 * The exception handling is needed for two reasons in the case
 *      the zero-divisor needs be returned
 * 1. the ordering of the zero-divisor should be the one of the 
 *      calling function ;
 * 2. the initial of the zero-divisor may not be regular and we want
 *      to ensure this.
 */
            if (ddz == (struct bap_polynom_mpz * volatile *) 0)
              bad_algebraic_invert_polynom_mod_regchain_zero_dimensional (&U1,
                  &U3, &Abar.tab[i].factor, &Cbar,
                  (struct bap_polynom_mpz * volatile *) 0);
            else
              bad_algebraic_invert_polynom_mod_regchain_zero_dimensional (&U1,
                  &U3, &Abar.tab[i].factor, &Cbar,
                  (struct bap_polynom_mpz * volatile *) &ddzbar);
          }
          BA0_CATCH
          {
/*
 * The ordering r will be freed by the next BA0_RAISE_EXCEPTION
 */
            if (ba0_global.exception.raised != BAD_EXRDDZ
                || ddz == (struct bap_polynom_mpz * volatile *) 0)
              BA0_RE_RAISE_EXCEPTION;
/*
 * Change of ranking over the exhibited zero divisor
 */
            bav_pull_ordering ();
            bap_sort_polynom_mpz ((struct bap_polynom_mpz *) ddzbar,
                (struct bap_polynom_mpz *) ddzbar);
/*
 * Make sure that the initial of the zero-divisor is regular
 * This test may itself raise an exception.
 */
            struct bap_polynom_mpz init_ddzbar;
            bap_init_readonly_polynom_mpz (&init_ddzbar);
            bap_initial_polynom_mpz (&init_ddzbar,
                (struct bap_polynom_mpz *) ddzbar);
            bad_check_regularity_polynom_mod_regchain (&init_ddzbar, C, K,
                (struct bap_polynom_mpz **) ddz);
/*
 * re-raise the BAD_EXRDDZ exception
 */
            *ddz = bap_new_polynom_mpz ();
            bap_set_polynom_mpz (*ddz, (struct bap_polynom_mpz *) ddzbar);
            BA0_RAISE_EXCEPTION2 (BAD_EXRDDZ, "%Az", (void **) ddz);
          }
          BA0_ENDTRY;
/*
 * We have computed U1 and U3 such that
 *
 *      U1 * Abar[i] = U3 mod C
 *
 * Thus
 *      Ubar = Ubar * U1 ** d[i]
 *      Gbar = Gbar * U3 ** d[i]
 */
          bap_pow_product_mpz (&U1, &U1, Abar.tab[i].exponent);
          bap_mul_product_mpz (&Ubar, &Ubar, &U1);
          bap_mul_product_polynom_mpz (&Gbar, &Gbar, &U3, Abar.tab[i].exponent);
        }
    }

  bav_pull_ordering ();
  bap_sort_product_mpz (&Ubar, &Ubar);
  bap_sort_product_mpz (&Gbar, &Gbar);
  bav_R_free_ordering (r);

  ba0_pull_stack ();
  bap_set_product_mpz (U, &Ubar);
  bap_set_product_mpz (G, &Gbar);
  ba0_restore (&M);
}

/*
 * Computes an inverse of A modulo C, i.e products U and G such that
 *
 *             U * A = G mod C (differentially)
 *
 *             U in K [L, N] 
 *             G in K [N]
 *
 * By a well-known theorem, G is then not a zero divisor and 1/A = U/G mod C
 *
 * Any exhibited zerodivisor is returned through ddz.
 * The case A = 0 is handled.
 *
 * Here, L = leaders (C) and N = non-leaders (C, A)
 */

static void
bad_differential_invert_polynom_mod_regchain (
    struct bap_product_mpz *U,
    struct bap_product_mpz *G,
    struct bap_polynom_mpz *A,
    struct bad_regchain *C,
    struct bad_base_field *K,
    struct bap_polynom_mpz *volatile *ddz)
{
  struct bap_product_mpz P, H;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  bap_init_product_mpz (&H);
  bap_init_product_mpz (&P);

  bad_reduce_polynom_by_regchain (&P, &H, (struct bav_tableof_term *) 0, A, C,
      bad_full_reduction, bad_all_derivatives_to_reduce);

  ba0_pull_stack ();

  bad_algebraic_invert_product_mod_regchain (U, G, &P, C, K, ddz);
  bap_mul_product_mpz (U, U, &H);

  ba0_restore (&M);
}

/*
 * Computes an inverse of A modulo C, i.e products U and G such that
 *
 *             U * A = G mod C (differentially or algebraically)
 *
 *             U in K [L, N] 
 *             G in K [N]
 *
 * The choice differential vs algebraic depends on the attributes of C
 *
 * By a well-known theorem, G is then not a zero divisor and 1/A = U/G mod C
 *
 * Any exhibited zerodivisor is returned through ddz.
 * The case A = 0 is handled.
 * 
 * Here, L = leaders (C) and N = non-leaders (C, A)
 */

/*
 * texinfo: bad_invert_polynom_mod_regchain
 * Compute @var{U} and @var{G} such that a relation @math{U \, A = G} holds
 * modulo the ideal defined by @var{C}, over the base field @var{K}.
 * The fraction @math{U/G} may be viewed as an inverse of @var{A}
 *      modulo @var{C}. 
 * In particular, @var{G} is regular modulo @var{C}.
 *
 * Exception @code{BAD_EXRNUL} is raised if @var{A} is zero modulo @var{C}.
 *
 * Exception @code{BAD_EXRDDZ} is raised if a zerodivisor modulo @var{C}
 * is exhibited during the computation. This zerodivisor may be different
 * from @var{A}. In this case and if @var{ddz} is nonzero, then the
 * zerodivisor is returned in @var{ddz} and is guaranteed to have
 * a regular initial modulo @var{C}.
 */

BAD_DLL void
bad_invert_polynom_mod_regchain (
    struct bap_product_mpz *U,
    struct bap_product_mpz *G,
    struct bap_polynom_mpz *A,
    struct bad_regchain *C,
    struct bad_base_field *K,
    struct bap_polynom_mpz *volatile *ddz)
{
  struct bap_product_mpz P;
  struct ba0_tableof_bool keep;
  struct ba0_mark M;

  if (bad_defines_a_differential_ideal_regchain (C))
    bad_differential_invert_polynom_mod_regchain (U, G, A, C, K, ddz);
  else
    {
      if (bad_is_a_reduced_to_zero_polynom_by_regchain (A, C,
              bad_algebraic_reduction))
        BA0_RAISE_EXCEPTION (BAD_EXRNUL);

      ba0_push_another_stack ();
      ba0_record (&M);
      bap_init_product_mpz (&P);
      ba0_init_table ((struct ba0_table *) &keep);
      baz_factor_easy_polynom_mpz (&P, &keep, A,
          (struct bap_listof_polynom_mpz *) 0);
      ba0_pull_stack ();
      bad_algebraic_invert_product_mod_regchain (U, G, &P, C, K, ddz);
      ba0_restore (&M);
    }
  baz_gcd_product_mpz ((struct bap_product_mpz *) 0, U, G, U, G);

#if defined (BA0_HEAVY_DEBUG)
  ba0_record (&M);
  struct bap_polynom_mpz tmp1;
  bap_init_polynom_mpz (&tmp1);
  bap_expand_product_mpz (&tmp1, U);
  bap_mul_polynom_mpz (&tmp1, &tmp1, A);
  struct bap_polynom_mpz tmp2;
  bap_init_polynom_mpz (&tmp2);
  bap_expand_product_mpz (&tmp2, G);
  bap_sub_polynom_mpz (&tmp1, &tmp1, &tmp2);
  enum bad_typeof_reduction type_red;
  if (bad_defines_a_differential_ideal_regchain (C))
    type_red = bad_full_reduction;
  else
    type_red = bad_algebraic_reduction;
  if (!bad_is_a_reduced_to_zero_polynom_by_regchain (&tmp1, C, type_red))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  ba0_restore (&M);
#endif
}

/*
 * texinfo: bad_invert_product_mod_regchain
 * Variant of @code{bad_invert_polynom_mod_regchain} for products.
 * The inverses are computed factorwise.
 */

BAD_DLL void
bad_invert_product_mod_regchain (
    struct bap_product_mpz *U,
    struct bap_product_mpz *G,
    struct bap_product_mpz *A,
    struct bad_regchain *C,
    struct bad_base_field *K,
    struct bap_polynom_mpz *volatile *ddz)
{
  struct bap_product_mpz Uhat, Ghat, Ubar, Gbar;
  ba0_int_p i;
  struct ba0_mark M;

  if (bap_is_zero_product_mpz (A))
    BA0_RAISE_EXCEPTION (BAD_EXRNUL);

  bap_set_product_one_mpz (U);
  bap_set_product_numeric_mpz (G, A->num_factor);
  bap_realloc_product_mpz (U, A->size);
  bap_realloc_product_mpz (G, A->size);

  ba0_push_another_stack ();
  ba0_record (&M);

  bap_init_product_mpz (&Ubar);
  bap_init_product_mpz (&Gbar);
  bap_set_product_numeric_mpz (&Gbar, A->num_factor);

  bap_init_product_mpz (&Uhat);
  bap_init_product_mpz (&Ghat);
/*
 * Denote A = c * mul (A[k] ** d[k], k = 1 .. t)
 * Loop invariant: 
 *
 *      Ubar * A = Gbar * mul (A[k] ** d[k], k = i .. t) mod C
 *
 * Thus, initially Ubar = 1 and Gbar = c
 */
  for (i = 0; i < A->size; i++)
    {
      if (A->tab[i].exponent > 0)
        {
          bad_invert_polynom_mod_regchain (&Uhat, &Ghat, &A->tab[i].factor, C,
              K, ddz);
          bap_pow_product_mpz (&Uhat, &Uhat, A->tab[i].exponent);
          bap_pow_product_mpz (&Ghat, &Ghat, A->tab[i].exponent);

          bap_mul_product_mpz (&Ubar, &Ubar, &Uhat);
          bap_mul_product_mpz (&Gbar, &Gbar, &Ghat);
        }
    }

  ba0_pull_stack ();
  bap_set_product_mpz (U, &Ubar);
  bap_set_product_mpz (G, &Gbar);
  ba0_restore (&M);
}

static void
bad_iterated_lsr3_polynom_mod_regchain_zero_dimensional (
    struct bap_product_mpz *U,
    struct bap_polynom_mpz *G,
    struct bap_polynom_mpz *A,
    struct bad_regchain *C)
{
  struct bap_tableof_polynom_mpz T;
  struct bap_product_mpz Ubar;
  struct bap_polynom_mpz *Gbar, *Ci;
  struct bav_variable *v;
  struct ba0_mark M;
  ba0_int_p i;
  bool first;

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_init_table ((struct ba0_table *) &T);
  ba0_realloc2_table ((struct ba0_table *) &T, 2,
      (ba0_new_function *) & bap_new_polynom_mpz);
  T.size = 2;

  Gbar = bap_new_polynom_mpz ();
  bap_init_product_mpz (&Ubar);
  first = true;

  for (i = C->decision_system.size - 1; i >= 0; i--)
    {
      Ci = C->decision_system.tab[i];
      v = bap_leader_polynom_mpz (Ci);
      if (bap_depend_polynom_mpz (first ? A : Gbar, v))
        {
          bap_lsr3_Ducos_polynom_mpz (&T, first ? A : Gbar, Ci, v);
          first = false;
          BA0_SWAP (struct bap_polynom_mpz *,
              T.tab[0],
              Gbar);
          bap_mul_product_polynom_mpz (&Ubar, &Ubar, T.tab[1], 1);
        }
    }

  ba0_pull_stack ();
  bap_set_product_mpz (U, &Ubar);
  bap_set_polynom_mpz (G, first ? A : Gbar);
  ba0_restore (&M);
}

BAD_DLL void
bad_iterated_lsr3_product_mod_regchain (
    struct bap_product_mpz *U,
    struct bap_product_mpz *G,
    struct bap_product_mpz *A,
    struct bad_regchain *C)
{
  struct bad_regchain Cbar;
  struct bap_product_mpz Abar, Ubar, Gbar, U1;
  struct bap_polynom_mpz U3;
  bav_Iordering r;
  struct ba0_mark M;
  ba0_int_p i;

  ba0_push_another_stack ();
  ba0_record (&M);

  r = bad_ordering_eliminating_leaders_of_regchain (C);
  bav_push_ordering (r);
/*
 * It is better to remove the differential property since r is not a ranking
 */
  bad_init_regchain (&Cbar);
  bad_sort_regchain (&Cbar, C);
  bad_clear_property_attchain (&Cbar.attrib, bad_differential_ideal_property);
  bap_init_product_mpz (&Abar);
  bap_sort_product_mpz (&Abar, A);

  bap_init_product_mpz (&U1);
  bap_init_polynom_mpz (&U3);

  bap_init_product_mpz (&Ubar);
  bap_init_product_mpz (&Gbar);
  bap_set_product_numeric_mpz (&Gbar, Abar.num_factor);
/*
 * Denote Abar = c * mul (Abar[k] ** d[k], k = 1 .. t)
 * Loop invariant:
 *
 *      Ubar * Abar = Gbar * mul (Abar[k] ** d[k], k = 1 .. t) mod C
 *
 * Thus initially, Ubar = 1 and Gbar = c
 */
  for (i = 0; i < Abar.size; i++)
    {
      if (Abar.tab[i].exponent > 0)
        {
          bad_iterated_lsr3_polynom_mod_regchain_zero_dimensional (&U1, &U3,
              &Abar.tab[i].factor, &Cbar);
/*
 * We have U1 and U3 such that
 * 
 *      U1 * Abar[i] = U3 mod C
 * 
 * Thus
 *      Ubar = Ubar * U1 ** d[i]
 *      Gbar = Gbar * U3 ** d[i]
 */
          bap_pow_product_mpz (&U1, &U1, Abar.tab[i].exponent);
          bap_mul_product_mpz (&Ubar, &Ubar, &U1);
          bap_mul_product_polynom_mpz (&Gbar, &Gbar, &U3, Abar.tab[i].exponent);
        }
    }

  bav_pull_ordering ();
  bap_sort_product_mpz (&Ubar, &Ubar);
  bap_sort_product_mpz (&Gbar, &Gbar);
  bav_R_free_ordering (r);

  ba0_pull_stack ();
  bap_set_product_mpz (U, &Ubar);
  bap_set_product_mpz (G, &Gbar);
  ba0_restore (&M);
}
