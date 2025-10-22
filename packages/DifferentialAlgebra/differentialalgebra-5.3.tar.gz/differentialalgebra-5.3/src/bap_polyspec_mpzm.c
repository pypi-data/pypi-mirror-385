#include "bap_polynom_mpzm.h"
#include "bap_add_polynom_mpzm.h"
#include "bap_mul_polynom_mpzm.h"
#include "bap_prem_polynom_mpzm.h"
#include "bap_eval_polynom_mpzm.h"
#include "bap_creator_mpzm.h"
#include "bap_itermon_mpzm.h"
#include "bap_itercoeff_mpzm.h"
#include "bap_polyspec_mpzm.h"
#include "bap_invert_mpzm.h"
#include "bap_creator_mpz.h"
#include "bap_itermon_mpz.h"
#include "bap_add_polynom_mpz.h"
#include "bap_mul_polynom_mpz.h"
#include "bap_polynom_mpz.h"
#include "bap_polyspec_mpz.h"
#include "bap_polyspec_mpq.h"
#include "bap_itermon_mint_hp.h"
#include "bap_polyspec_mint_hp.h"


/*
 * They are polynomials with coefficients in $\Z/n\Z$ where $n$ is
 * given by the global variable {\tt ba0_mpzm_module}. Coefficients
 * are in positive representation. 
 */

/*-
 * Sets $A$ to $B \mod {(\mbox{\tt ba0_mpzm_module})}$.
 */

BAP_DLL void
bap_polynom_mpq_to_mpzm (
    struct bap_polynom_mpzm *A,
    struct bap_polynom_mpq *B)
{
  A = (struct bap_polynom_mpzm *) 0;
  B = (struct bap_polynom_mpq *) 0;
  BA0_RAISE_EXCEPTION (BA0_ERRNYP);
}

/*
 * Sets $R$ to $A \mod {(\mbox{\tt ba0_mpzm_module})}$.
 */

/*
 * texinfo: bap_polynom_mpz_to_mpzm
 * Assign to @var{R} the polynomial @var{A} modulo @code{ba0_mpzm_module}.
 */

BAP_DLL void
bap_polynom_mpz_to_mpzm (
    struct bap_polynom_mpzm *R,
    struct bap_polynom_mpz *A)
{
  struct bap_itermon_mpz iter;
  struct bap_creator_mpzm crea;
  struct bap_polynom_mpzm *P;
  ba0_mpz_t bunk;
  struct bav_term T;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&T);
  bav_set_term (&T, &A->total_rank);

  ba0_mpz_init (bunk);
  P = bap_new_polynom_mpzm ();
  bap_begin_creator_mpzm (&crea, P, &T, bap_approx_total_rank,
      bap_nbmon_polynom_mpz (A));

  bap_begin_itermon_mpz (&iter, A);
  while (!bap_outof_itermon_mpz (&iter))
    {
      ba0_mpz_mod (bunk, *bap_coeff_itermon_mpz (&iter), ba0_mpzm_module);
      if (ba0_mpz_sgn (bunk) != 0)
        {
          bap_term_itermon_mpz (&T, &iter);
          bap_write_creator_mpzm (&crea, &T, bunk);
        }
      bap_next_itermon_mpz (&iter);
    }
  bap_close_creator_mpzm (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mpzm (R, P);
  ba0_restore (&M);
}

/*
 * Sets $R$ to $A$.
 * Assumes {\tt ba0_mpzm_module} is a multiple of {\tt ba0_mint_hp_module}.
 */

/*
 * texinfo: bap_polynom_mint_hp_to_mpzm
 * Assign to @var{R} the polynomial @var{A}, assuming that 
 * @code{ba0_mpzm_module} is a multiple of @code{ba0_mint_hp_module}.
 */

BAP_DLL void
bap_polynom_mint_hp_to_mpzm (
    struct bap_polynom_mpzm *R,
    struct bap_polynom_mint_hp *A)
{
  struct bap_creator_mpzm crea;
  struct bap_itermon_mint_hp iter;
  struct bav_term T;
  ba0_mpz_t c;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
  bav_init_term (&T);
  bav_realloc_term (&T, A->total_rank.size);
  ba0_mpz_init (c);
  if (ba0_mpz_mod_ui (c, ba0_mpzm_module,
          (unsigned long int) ba0_mint_hp_module) != 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  ba0_pull_stack ();

  bap_begin_creator_mpzm (&crea, R, &A->total_rank, bap_exact_total_rank,
      bap_nbmon_polynom_mint_hp (A));
  bap_begin_itermon_mint_hp (&iter, A);
  while (!bap_outof_itermon_mint_hp (&iter))
    {
      bap_term_itermon_mint_hp (&T, &iter);
      ba0_mpz_set_ui (c, *bap_coeff_itermon_mint_hp (&iter));
      bap_write_creator_mpzm (&crea, &T, c);
      bap_next_itermon_mint_hp (&iter);
    }
  bap_close_creator_mpzm (&crea);
  ba0_restore (&M);
}

/* 
 * Sets $R$ to $A$, coefficients being interpreted as signed integers 
 * with absolute value less than one half of {\tt ba0_mpzm_module}.
 */

/*
 * texinfo: bap_mods_polynom_mpzm
 * Assign to @var{R} the polynomial @var{A}.
 * Maps the coefficients to the signed integers
 * with absolute value less than one half of @code{ba0_mpzm_module}.
 */

BAP_DLL void
bap_mods_polynom_mpzm (
    struct bap_polynom_mpz *R,
    struct bap_polynom_mpzm *A)
{
  struct bap_itermon_mpzm iter;
  ba0_mpz_t *lc;

  if (R == (struct bap_polynom_mpz *) A)
    {
      bap_begin_itermon_mpzm (&iter, A);
      while (!bap_outof_itermon_mpzm (&iter))
        {
          lc = bap_coeff_itermon_mpzm (&iter);
          if (ba0_mpz_cmp (*lc, ba0_mpzm_half_module) > 0)
            ba0_mpz_sub (*lc, *lc, ba0_mpzm_module);
          bap_next_itermon_mpzm (&iter);
        }
    }
  else
    {
      struct bap_creator_mpz crea;
      struct bap_polynom_mpz *P;
      ba0_mpz_t bunk;
      struct bav_term T;
      struct ba0_mark M;

      ba0_push_another_stack ();
      ba0_record (&M);
      bav_init_term (&T);
      ba0_mpz_init (bunk);
      bav_set_term (&T, &A->total_rank);
      P = bap_new_polynom_mpz ();
      bap_begin_creator_mpz (&crea, P, &T, bap_exact_total_rank,
          bap_nbmon_polynom_mpzm (A));
      bap_begin_itermon_mpzm (&iter, A);
      while (!bap_outof_itermon_mpzm (&iter))
        {
          bap_term_itermon_mpzm (&T, &iter);
          lc = bap_coeff_itermon_mpzm (&iter);
          if (ba0_mpz_cmp (*lc, ba0_mpzm_half_module) > 0)
            {
              ba0_mpz_sub (bunk, *lc, ba0_mpzm_module);
              bap_write_creator_mpz (&crea, &T, bunk);
            }
          else
            bap_write_creator_mpz (&crea, &T, *lc);
          bap_next_itermon_mpzm (&iter);
        }
      bap_close_creator_mpz (&crea);
      ba0_pull_stack ();
      bap_set_polynom_mpz (R, P);
      ba0_restore (&M);
    }
}

/* 
 * Variant of the above function, for products.
 */

/*
 * texinfo: bap_mods_product_mpzm
 * Variant of the above function, for products.
 */

BAP_DLL void
bap_mods_product_mpzm (
    struct bap_product_mpz *P,
    struct bap_product_mpzm *Q)
{
  ba0_int_p i;

  if (P == (struct bap_product_mpz *) Q)
    {
      if (ba0_mpz_cmp (Q->num_factor, ba0_mpzm_half_module) > 0)
        ba0_mpz_sub (P->num_factor, Q->num_factor, ba0_mpzm_module);
      for (i = 0; i < Q->size; i++)
        bap_mods_polynom_mpzm (&P->tab[i].factor, &Q->tab[i].factor);
    }
  else
    {
      if (ba0_mpz_cmp (Q->num_factor, ba0_mpzm_half_module) > 0)
        ba0_mpz_sub (P->num_factor, Q->num_factor, ba0_mpzm_module);
      else
        ba0_mpz_set (P->num_factor, Q->num_factor);
      P->size = 0;
      bap_realloc_product_mpz (P, Q->size);
      for (i = 0; i < Q->size; i++)
        bap_mods_polynom_mpzm (&P->tab[i].factor, &Q->tab[i].factor);
      P->size = Q->size;
    }
}

/* 
 * Sets to $U$, $V$ and $G$ polynomials such that
 * $A\,U + B\,V = G = A \wedge B \mod {(p^k)}$.
 * The global variable {\tt ba0_mpzm_module} is changed. 
 * Exception BAP_EXHNCP is raised if the computation failed.
 */

/*
   Function EEAlift page 271
*/

#if defined (BA0_HEAVY_DEBUG)
static void
verifie_Bezout (
    struct bap_polynom_mpzm *U,
    struct bap_polynom_mpzm *V,
    struct bap_polynom_mpzm *G,
    struct bap_polynom_mpzm *A,
    struct bap_polynom_mpzm *B,
    ba0_mpz_t p,
    bav_Idegree k)
{
  struct bap_polynom_mpzm *E, F;
  ba0_mpz_t modulus;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_mpz_init_set (modulus, p);
  ba0_mpz_pow_ui (modulus, modulus, k);
  ba0_mpzm_module_set (modulus, k == 1);

  E = bap_new_polynom_mpzm ();
  F = bap_new_polynom_mpzm ();
  bap_mul_polynom_mpzm (E, A, U);
  bap_mul_polynom_mpzm (F, B, V);
  bap_add_polynom_mpzm (E, E, F);
  bap_sub_polynom_mpzm (E, E, G);
  if (!bap_is_zero_polynom_mpzm (E))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_pull_stack ();
  ba0_restore (&M);
}
#endif

/*
 * texinfo: bap_Bezout_polynom_mpzm
 * Assign to @var{U}, @var{V} and @var{G} polynomials such that
 * @var{G} is the gcd of @var{A} and @var{B} and @math{A\,U + B\,V = G}
 * modulo @math{p^k}. 
 * The global variable @code{ba0_mpzm_module} is changed.
 * Exception @code{BAP_EXHNCP} is raised if the computation failed.
 */

BAP_DLL void
bap_Bezout_polynom_mpzm (
    struct bap_polynom_mpzm *U,
    struct bap_polynom_mpzm *V,
    struct bap_polynom_mpzm *G,
    struct bap_polynom_mpzm *A,
    struct bap_polynom_mpzm *B,
    ba0_mpz_t p,
    bav_Idegree k)
{
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_mpzm_module_set (p, true);

  if (k == 1)
    {
      ba0_pull_stack ();
      bap_extended_Euclid_polynom_mpzm (U, V, G, A, B);
    }
  else
    {
      struct bap_polynom_mpzm *A_mod_p, *B_mod_p, *U_mod_p, *V_mod_p, *G_mod_p,
          *Q, *Uhat, *Vhat, *newU, *newV;
      struct bap_polynom_mpz *E, *F;
      bav_Idegree j;

      BA0_RAISE_EXCEPTION (BA0_ERRNYP);

/*
   Bug a cause d'un probleme de representation signee qui est necessaire
   avec un Hensel lifting numerique
*/
      A_mod_p = bap_new_polynom_mpzm ();
      B_mod_p = bap_new_polynom_mpzm ();
      bap_polynom_mpz_to_mpzm (A_mod_p, (struct bap_polynom_mpz *) A);
      bap_polynom_mpz_to_mpzm (B_mod_p, (struct bap_polynom_mpz *) B);
      U_mod_p = bap_new_polynom_mpzm ();
      V_mod_p = bap_new_polynom_mpzm ();
      G_mod_p = bap_new_polynom_mpzm ();
      bap_extended_Euclid_polynom_mpzm (U_mod_p, V_mod_p, G_mod_p, A_mod_p,
          B_mod_p);
      if (!bap_is_one_polynom_mpzm (G_mod_p))
        BA0_RAISE_EXCEPTION (BAP_EXHNCP);
      newU = bap_new_polynom_mpzm ();
      newV = bap_new_polynom_mpzm ();
      bap_set_polynom_mpzm (newU, U_mod_p);
      bap_set_polynom_mpzm (newV, V_mod_p);
      E = bap_new_polynom_mpz ();
      F = bap_new_polynom_mpz ();
      Uhat = bap_new_polynom_mpzm ();
      Vhat = bap_new_polynom_mpzm ();
      Q = bap_new_polynom_mpzm ();
      for (j = 1; j <= k - 1; j++)
        {
          bap_set_polynom_one_mpz (E);
          bap_mul_polynom_mpz (F, (struct bap_polynom_mpz *) newU,
              (struct bap_polynom_mpz *) A);
          bap_sub_polynom_mpz (E, E, F);
          bap_mul_polynom_mpz (F, (struct bap_polynom_mpz *) newV,
              (struct bap_polynom_mpz *) B);
          bap_sub_polynom_mpz (E, E, F);
          bap_exquo_polynom_numeric_mpz (E, E, ba0_mpzm_module);
/*
   On pourrait prendre mod p plutot que mod p^j
*/
          bap_polynom_mpz_to_mpzm ((struct bap_polynom_mpzm *) E, E);

          bap_mul_polynom_mpzm (Uhat, U_mod_p, (struct bap_polynom_mpzm *) E);
          bap_mul_polynom_mpzm (Vhat, V_mod_p, (struct bap_polynom_mpzm *) E);
          bap_Euclidean_division_polynom_mpzm (Q, Uhat, Uhat, B_mod_p);
          bap_mul_polynom_mpzm (Q, Q, A_mod_p);
          bap_add_polynom_mpzm (Vhat, Vhat, Q);
          bap_mul_polynom_numeric_mpz ((struct bap_polynom_mpz *) Uhat,
              (struct bap_polynom_mpz *) Uhat, ba0_mpzm_module);
          bap_mul_polynom_numeric_mpz ((struct bap_polynom_mpz *) Vhat,
              (struct bap_polynom_mpz *) Vhat, ba0_mpzm_module);
          bap_add_polynom_mpz ((struct bap_polynom_mpz *) newU,
              (struct bap_polynom_mpz *) newU, (struct bap_polynom_mpz *) Uhat);
          bap_add_polynom_mpz ((struct bap_polynom_mpz *) newV,
              (struct bap_polynom_mpz *) newV, (struct bap_polynom_mpz *) Vhat);
          ba0_mpzm_module_mul (p);
        }
      ba0_pull_stack ();
      bap_set_polynom_mpzm (U, newU);
      bap_set_polynom_mpzm (V, newV);
      bap_set_polynom_one_mpzm (G);
    }
  ba0_restore (&M);
#if defined (BA0_HEAVY_DEBUG)
  verifie_Bezout (U, V, G, A, B, p, k);
#endif
}

/* 
 * Sets $R$ to the coefficient of $(x - \alpha)^k$ in the Taylor expansion 
 * of $A$ in $\mbox{\em val} = (x, \alpha)$.
 */

/*
 * texinfo: bap_coeftayl_polynom_mpzm
 * Assign to @var{R} the coefficient of @math{(x - \alpha)} 
 * in the Taylor expansion of @math{A} at @math{@emph{val} = (x,\,\alpha)}.
 */

BAP_DLL void
bap_coeftayl_polynom_mpzm (
    struct bap_polynom_mpzm *R,
    struct bap_polynom_mpzm *A,
    struct bav_value_int_p *val,
    bav_Idegree k)
{
  struct bap_itercoeff_mpzm iter;
  struct bav_term T;
  struct bap_polynom_mpzm B, C, D;
  struct bap_polynom_mpzm *AA;
  bav_Iordering r = 0;
  bav_Idegree d;
  ba0_mpz_t c, binomial;
  struct ba0_mark M;

  d = bav_degree_term (&A->total_rank, val->var);
  if (d < k)
    {
      bap_set_polynom_zero_mpzm (R);
      return;
    }

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&T);
  ba0_mpz_init (c);
  ba0_mpz_init (binomial);

  if (val->var != bap_leader_polynom_mpzm (A))
    {
      r = bav_R_copy_ordering (bav_current_ordering ());
      bav_push_ordering (r);
      bav_R_set_maximal_variable (val->var);
      AA = bap_new_polynom_mpzm ();
      bap_sort_polynom_mpzm (AA, A);
    }
  else
    AA = A;

  bap_init_polynom_mpzm (&B);
  bap_init_polynom_mpzm (&C);
  bap_init_polynom_mpzm (&D);
  bap_begin_itercoeff_mpzm (&iter, AA, val->var);
  if (!bap_outof_itercoeff_mpzm (&iter))
    bap_term_itercoeff_mpzm (&T, &iter);
  d = bav_degree_term (&T, val->var);
  while (!bap_outof_itercoeff_mpzm (&iter) && d >= k)
    {
      bap_coeff_itercoeff_mpzm (&C, &iter);
/*
ba0_printf ("C = %Azm\n", &C);
*/
      ba0_mpz_si_pow_ui (c, val->value, d - k);
/*
 * Cast for Windows 64 bits, Visual Studio 2008.
 * It is unlikely that d or k >= ULONG_MAX :-)
 */
      ba0_mpz_bin_uiui (binomial, (unsigned long) d, (unsigned long) k);
      ba0_mpz_mul (c, c, binomial);
      ba0_mpz_mod (c, c, ba0_mpzm_module);
      if (ba0_mpz_sgn (c) != 0)
        {
          bap_mul_polynom_numeric_mpzm (&D, &C, c);
          bap_add_polynom_mpzm (&B, &B, &D);
/*
ba0_printf ("B = %Azm\n", &B);
*/
        }
      bap_next_itercoeff_mpzm (&iter);
      if (!bap_outof_itercoeff_mpzm (&iter))
        bap_term_itercoeff_mpzm (&T, &iter);
      d = bav_degree_term (&T, val->var);
    }

  if (val->var != bap_leader_polynom_mpzm (A))
    {
      bav_pull_ordering ();
      bav_R_free_ordering (r);
      bap_change_ordering_termstripper (&B.tstrip, bav_current_ordering ());
    }
  ba0_pull_stack ();
  bap_set_polynom_mpzm (R, &B);
  ba0_restore (&M);
}

#if defined (BA0_HEAVY_DEBUG)
static void
verifie_quorem (
    struct bap_polynom_mpzm *Q,
    struct bap_polynom_mpzm *R,
    struct bav_rank *rg,
    struct bap_polynom_mpzm *A,
    struct bap_polynom_mpzm *B)
{
  struct bav_rank rgR, rgB;
  struct bap_polynom_mpzm *E, F;
  struct bav_term T;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  rgR = bap_rank_polynom_mpzm (R);
  rgB = bap_rank_polynom_mpzm (B);
  if (rgR.deg >= rgB.deg)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  bav_init_term (&T);
  bav_set_term_rank (&T, rg);
  E = bap_new_polynom_mpzm ();
  bap_mul_polynom_term_mpzm (E, A, &T);
  F = bap_new_polynom_mpzm ();
  bap_mul_polynom_mpzm (F, B, Q);
  bap_add_polynom_mpzm (F, F, R);
  bap_sub_polynom_mpzm (E, E, F);
  if (!bap_is_zero_polynom_mpzm (E))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  ba0_pull_stack ();
  ba0_restore (&M);
}
#endif

/* 
 * Sets $Q$ and $R$ to polynomials such that $\mbox{\em rg}\,A = B\,Q + R$ 
 * with $\deg R < \deg B$. Assumes $\deg A < \deg B$.
 */

/*
 * texinfo: bap_quorem_polynom_mpzm
 * Assign to @var{R} and @var{Q} polynomials such that 
 * @math{@emph{rg}\,A = B\,Q + R} with @math{\deg R < \deg B}.
 * Assumes @math{\deg A < \deg B}.
 */

BAP_DLL void
bap_quorem_polynom_mpzm (
    struct bap_polynom_mpzm *Q,
    struct bap_polynom_mpzm *R,
    struct bav_rank *rg,
    struct bap_polynom_mpzm *A,
    struct bap_polynom_mpzm *B)
{
  struct bav_term T;
  struct bav_variable *x;
  struct bav_rank rk;
  bav_Idegree m, d, e;
  ba0_mpz_t c, inv_lcB;
  struct ba0_mark M;

  if (Q == B || R == B)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  x = rg->var;
  m = rg->deg;
  d = bap_degree_polynom_mpzm (B, x) - bap_degree_polynom_mpzm (A, x) - 1;
  d = BA0_MIN (d, m);

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&T);
  rk.var = x;
  rk.deg = d;
  bav_set_term_rank (&T, &rk);

  ba0_mpz_init (c);
  ba0_mpz_init (inv_lcB);
  ba0_mpzm_invert (inv_lcB, *bap_numeric_initial_polynom_mpzm (B));

  ba0_pull_stack ();

  bap_mul_polynom_term_mpzm (R, A, &T);
  bap_set_polynom_zero_mpzm (Q);

  while (d < m)
    {
      e = bap_degree_polynom_mpzm (B, x) - bap_degree_polynom_mpzm (R, x) - 1;
      if (e > 0)
        {
          rk.deg = BA0_MIN (e, m);
          bav_set_term_rank (&T, &rk);
          bap_mul_polynom_term_mpzm (Q, Q, &T);
          bap_mul_polynom_term_mpzm (R, R, &T);
          d += e;
        }
      else
        {
          ba0_mpzm_mul (c, *bap_numeric_initial_polynom_mpzm (R), inv_lcB);
          rk.deg = 1;
          bav_set_term_rank (&T, &rk);

          bap_mul_polynom_term_mpzm (Q, Q, &T);
          bap_add_polynom_numeric_mpzm (Q, Q, c);

          bap_mul_polynom_term_mpzm (R, R, &T);
          bav_set_term_one (&T);
          bap_submulmon_polynom_mpzm (R, R, B, &T, c);
          d += 1;
        }
    }
  ba0_restore (&M);
#if defined (BA0_HEAVY_DEBUG)
  verifie_quorem (Q, R, rg, A, B);
#endif
}

/* 
 * Affecte \`a~$Q$ et \`a~$R$ des polyn\^omes tels que
 * $\mbox{\em rg}\,A = B\,Q + R$ avec $\deg R < \deg B$.
 * Suppose que $\deg A < \deg B$.

BAP_DLL void bap_quorem_polynom_mpzm 
		(struct bap_polynom_mpzm * Q, struct bap_polynom_mpzm * R, 
		 struct bav_rank * rg, struct bap_polynom_mpzm * A, struct bap_polynom_mpzm * B)
{   struct bav_rank rgA, rgB, rgbar;
    struct bap_polynom_mpzm * newQ, newR, C;
    struct bav_term T;
    ba0_mpz_t c;
    struct ba0_mark M;

    ba0_push_another_stack ();
    ba0_record (&M);
    bav_init_term (&T);

    rgA = bap_rank_polynom_mpzm (A);
    rgB = bap_rank_polynom_mpzm (B);

    newQ = bap_new_polynom_mpzm ();
    newR = bap_new_polynom_mpzm ();

    if (rgA.deg >= rgB.deg)
	BA0_RAISE_EXCEPTION (BA0_ERRALG);

    if (rg.deg + rgA.deg < rgB.deg)
    {   bav_set_term_rank (&T, &rg);
	bap_mul_polynom_term_mpzm (newR, A, &T);
    } else
    {   rgbar.var = rg.var;
	rgbar.deg = rg.deg - 1;
	bap_quorem_polynom_mpzm (newQ, newR, &rgbar, A, B);
	rgbar = bap_rank_polynom_mpzm (newR);
	if (rgbar.deg < rgB.deg - 1)
	{   rgbar.var = rg.var;
	    rgbar.deg = 1;
	    bav_set_term_rank (&T, &rgbar);

	    bap_mul_polynom_term_mpzm (newQ, newQ, &T);
	    bap_mul_polynom_term_mpzm (newR, newR, &T);
	} else
	{   ba0_mpzm_init_set (c, *bap_numeric_initial_polynom_mpzm (newR));
	    ba0_mpzm_div (c, c, *bap_numeric_initial_polynom_mpzm (B));
	    rgbar.var = rg.var;
	    rgbar.deg = 1;
	    bav_set_term_rank (&T, &rgbar);

	    bap_mul_polynom_term_mpzm (newQ, newQ, &T);
	    bap_add_polynom_numeric_mpzm (newQ, newQ, c);
	    bap_mul_polynom_term_mpzm (newR, newR, &T);
	    C = bap_new_polynom_mpzm ();
	    bap_mul_polynom_numeric_mpzm (C, B, c);
	    bap_sub_polynom_mpzm (newR, newR, C);
	}
    }
    ba0_pull_stack ();
    bap_set_polynom_mpzm (Q, newQ);
    bap_set_polynom_mpzm (R, newR);
    ba0_restore (&M);
#if defined (BA0_HEAVY_DEBUG)
    verifie_quorem (Q, R, rg, A, B);
#endif
}
*/

#if defined (BA0_HEAVY_DEBUG)
static void
verifie_univariate_diophante_poly_mpzm (
    struct bap_polynom_mpzm *sigma,
    struct bap_product_mpzm *prod,
    struct bav_rank *rg,
    ba0_mpz_t p,
    bav_Idegree k)
{
  ba0_int_p i, r;
  struct bap_polynom_mpzm A, Z, *B;
  struct bav_variable *v;
  ba0_mpz_t un;
  struct ba0_mark M;

  ba0_record (&M);
/*
ba0_put_string ("verifie univariate diophante\n");
if (rg.var != BAV_NOT_A_VARIABLE)
{ ba0_printf ("struct bav_rank * = %v", rg->var);
  printf ("^%d\n", rg->deg);
}
ba0_printf ("p = %z\n", p);
*/
  v = bap_leader_polynom_mpzm (&prod->tab[0].factor);
  ba0_mpzm_module_pow_ui (p, k, true);

/*
if (k != 1) 
{ printf ("p^%d = ", k);
  ba0_printf ("%z\n", ba0_mpzm_module);
}
*/
  r = prod->size;
  for (i = 0; i < r; i++)
    {
/*
	printf ("sigma [%d] = \n", i);
	ba0_printf ("%Azm\n", &sigma [i]);
	printf ("a [%d] = \n", i);
	ba0_printf ("%Azm\n", &prod->tab [i].factor);
*/
/*
   Je ne teste pas la condition sur les degres qui est trop stricte

	if (! bap_is_numeric_polynom_mpzm (&sigma [i]) &&
		bap_degree_polynom_mpzm (&sigma [i], v) >= 
		    bap_leading_degree_polynom_mpzm (&prod->tab [i].factor))
	    BA0_RAISE_EXCEPTION (BA0_ERRALG);
*/
    }
  bap_init_polynom_mpzm (&A);
  bap_expand_product_mpzm (&A, prod);
  B = (struct bap_polynom_mpzm *) ba0_alloc (sizeof (struct bap_polynom_mpzm) *
      r);
  for (i = 0; i < r; i++)
    {
      bap_init_polynom_mpzm (&B[i]);
      bap_exquo_polynom_mpzm (&B[i], &A, &prod->tab[i].factor);
    }
  ba0_mpz_init_set_si (un, 1);
  bap_set_polynom_crk_mpzm (&A, un, rg);
  bap_init_polynom_mpzm (&Z);
  for (i = 0; i < r; i++)
    {
      bap_mul_polynom_mpzm (&Z, &B[i], &sigma[i]);
      bap_sub_polynom_mpzm (&A, &A, &Z);
    }
/*
ba0_printf ("resultat : %Azm\n", &A);
ba0_put_string ("=============================\n");
*/
  if (!bap_is_zero_polynom_mpzm (&A))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_restore (&M);
}
#endif

/* 
 * Denote $\mbox{\em prod} = a_1 \cdots a_r$ and 
 * $b_i = a_1 \cdots a_{i-1}\,a_{i+1} \cdots a_r$.
 * Sets {\em sigma} to the unique solution of the Diophantine polynomial
 * equation in $\Z/p^k\Z [x]$
 *
 * $$\sigma_1 \, b_1 + \cdots + \sigma_r\,b_r = \mbox{\em rg} \mod {(p^k)}$$
 *
 * such that $\deg \sigma_i < \deg a_i$.
 * Assumes $\mbox{\tt ba0_mpzm_module} = p^k$, that $p$ does not divide
 * any initial of the $a_i$ and that the $a_i$ are relatively prime modulo~$p$.
 */

/*
 * texinfo: bap_uni_Diophante_polynom_mpzm
 * Denote @math{@emph{prod} = a_1 \cdot a_r} and
 * @math{b_i = a_1 \cdots a_{i-1}\,a_{i+1} \cdots a_r}.
 * Assigns to @var{sigma} the unique solution of the Diophantine polynomial
 * equation in @math{(Z/p^kZ)[x]} 
 * @math{\sigma_1 \, b_1 + \cdots + \sigma_r\,b_r = @emph{rg}} modulo @math{p^k}
 * such that @math{\deg \sigma_i < \deg a_i}. Assumes 
 * @code{ba0_mpzm_module} is @math{p^k}, that @var{p} does not divide
 * any initial of the @math{a_i} and that the @math{a_i} are relatively
 * prime modulo @var{p}.
 */

BAP_DLL void
bap_uni_Diophante_polynom_mpzm (
    struct bap_polynom_mpzm *sigma,
    struct bap_product_mpzm *prod,
    struct bav_rank *rg,
    ba0_mpz_t p,
    bav_Idegree k)
{
  ba0_int_p nb_f;
  struct bap_polynom_mpzm *Q, *R;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
/*
ba0_put_string ("----- debut univariate_diophante -----\n");
ba0_printf ("prod = %Pzm\n", prod);
if (rg.var != BAV_NOT_A_VARIABLE)
{ ba0_printf ("struct bav_rank * = %v", rg->var);
  printf ("^%d\n", rg->deg);
}
ba0_printf ("p = %z\n", p);
*/
  Q = bap_new_polynom_mpzm ();
  R = bap_new_polynom_mpzm ();

  nb_f = prod->size;

  if (nb_f > 2)
    {
      struct bap_polynom_mpzm *B, *gamma;
      struct bav_point_int_p point;
      struct bap_product_mpzm temp_prod;
      ba0_int_p j;
/*
   B [k] = A [k + 1] * ... * A [nb_f - 1]  pour k = 0 .. nb_f - 2
*/
      B = (struct bap_polynom_mpzm *) ba0_alloc (sizeof (struct
              bap_polynom_mpzm) * nb_f);
      bap_init_polynom_mpzm (&B[nb_f - 2]);
      bap_set_polynom_mpzm (&B[nb_f - 2], &prod->tab[nb_f - 1].factor);
/*
printf ("B [%d] = \n", nb_f - 2);
ba0_printf ("%Azm\n", &B [nb_f - 2]);
*/
      for (j = nb_f - 3; j >= 0; j--)
        {
          bap_init_polynom_mpzm (&B[j]);
          bap_mul_polynom_mpzm (&B[j], &prod->tab[j + 1].factor, &B[j + 1]);
/*
printf ("B [%d] = \n", j);
ba0_printf ("%Azm\n", &B [j]);
*/
        }
/*
   gamma et temp_prod sont des zone de communication avec multivariate_diop.
*/
      gamma =
          (struct bap_polynom_mpzm *) ba0_alloc (sizeof (struct
              bap_polynom_mpzm) * 2);
      bap_init_polynom_mpzm (&gamma[0]);
      bap_init_polynom_mpzm (&gamma[1]);

      bap_init_product_mpzm (&temp_prod);
      bap_realloc_product_mpzm (&temp_prod, 2);
      temp_prod.size = 2;

      ba0_init_table ((struct ba0_table *) &point);
/*
   B [nb_f - 1] = the beta variable
   B [k] = s [k] for k = 0 .. nb_f - 1
*/
      bap_init_polynom_one_mpzm (&B[nb_f - 1]);
      for (j = 0; j < nb_f - 1; j++)
        {
          temp_prod.tab[0].factor = B[j];
          temp_prod.tab[1].factor = prod->tab[j].factor;
          bap_multi_Diophante_polynom_mpzm (gamma, &temp_prod, &B[nb_f - 1],
              &point, 0, p, k);
          bap_set_polynom_mpzm (&B[nb_f - 1], &gamma[0]);
          bap_set_polynom_mpzm (&B[j], &gamma[1]);
/*
ba0_printf ("beta = %Azm\n", &B [nb_f - 1]);
printf ("B [%d] = \n", j);
ba0_printf ("%Azm\n", &B [j]);
*/
        }
      for (j = 0; j < nb_f; j++)
        {
          bap_quorem_polynom_mpzm (Q, R, rg, &B[j], &prod->tab[j].factor);
          ba0_pull_stack ();
          bap_set_polynom_mpzm (&sigma[j], R);
/*
printf ("sigma [%d] = \n", j);
ba0_printf ("%Azm\n", &sigma [j]);
*/
          ba0_push_another_stack ();
        }
      ba0_pull_stack ();
    }
  else
    {
      struct bap_polynom_mpzm *U, *V, *G;
      ba0_mpz_t svg_mpzm_module;
      bool svg_mpzm_module_is_prime;
      struct bav_term T;

      U = bap_new_polynom_mpzm ();
      V = bap_new_polynom_mpzm ();
      G = bap_new_polynom_mpzm ();
      ba0_mpz_init_set (svg_mpzm_module, ba0_mpzm_module);
      svg_mpzm_module_is_prime = ba0_mpzm_module_is_prime;
      bap_Bezout_polynom_mpzm (U, V, G, &prod->tab[1].factor,
          &prod->tab[0].factor, p, k);
      ba0_mpzm_module_set (svg_mpzm_module, svg_mpzm_module_is_prime);
      bap_quorem_polynom_mpzm (Q, R, rg, U, &prod->tab[0].factor);
      bav_init_term (&T);
      bav_set_term_rank (&T, rg);
      bap_mul_polynom_term_mpzm (V, V, &T);
      bap_mul_polynom_mpzm (Q, &prod->tab[1].factor, Q);
      bap_add_polynom_mpzm (Q, Q, V);

      ba0_pull_stack ();
      bap_set_polynom_mpzm (&sigma[0], R);
      bap_set_polynom_mpzm (&sigma[1], Q);
    }
/*
{ ba0_int_p j;
  ba0_put_string ("------ fin univariate diophante ------\n");
  for (j = 0; j < prod->size; j++)
     ba0_printf ("%Azm\n", &sigma [j]);
}
*/
#if defined (BA0_HEAVY_DEBUG)
  verifie_univariate_diophante_poly_mpzm (sigma, prod, rg, p, k);
#endif
  ba0_restore (&M);
}

#if defined (BA0_HEAVY_DEBUG)
static void
verifie_multivariate_diophante_poly_mpzm (
    struct bap_polynom_mpzm *sigma,
    struct bap_product_mpzm *prod,
    struct bap_polynom_mpzm *C,
    struct bav_point_int_p *point,
    bav_Idegree maxdeg,
    ba0_mpz_t p,
    bav_Idegree k)
{
  ba0_int_p i, r;
  struct bap_polynom_mpzm A, Z, *B;
  struct bav_variable *v;
  struct ba0_mark M;

  ba0_record (&M);
/*
ba0_put_string ("verifie multivariate diophante\n");
ba0_printf ("C = %Azm\n", C);
ba0_printf ("p = %z\n", p);
*/
  v = bap_leader_polynom_mpzm (&prod->tab[0].factor);
  ba0_mpzm_module_pow_ui (p, k, true);

/*
if (k != 1) 
{ printf ("p^%d = ", k);
  ba0_printf ("%z\n", ba0_mpzm_module);
}
bav_printf_point_int_p (point);
printf (", maxdeg = %d\n", maxdeg);
*/
  r = prod->size;
  for (i = 0; i < r; i++)
    {
/*
	printf ("sigma [%d] = \n", i);
	ba0_printf ("%Azm\n", &sigma [i]);
	printf ("a [%d] = \n", i);
	ba0_printf ("%Azm\n", &prod->tab [i].factor);

	if (! bap_is_numeric_polynom_mpzm (&sigma [i]) &&
		bap_degree_polynom_mpzm (&sigma [i], v) >= 
		    bap_leading_degree_polynom_mpzm (&prod->tab [i].factor))
	    BA0_RAISE_EXCEPTION (BA0_ERRALG);
*/
    }
  bap_init_polynom_mpzm (&A);
  bap_expand_product_mpzm (&A, prod);
  B = (struct bap_polynom_mpzm *) ba0_alloc (sizeof (struct bap_polynom_mpzm) *
      r);
  for (i = 0; i < r; i++)
    {
      bap_init_polynom_mpzm (&B[i]);
      bap_exquo_polynom_mpzm (&B[i], &A, &prod->tab[i].factor);
    }
  bap_set_polynom_mpzm (&A, C);
  bap_init_polynom_mpzm (&Z);
  for (i = 0; i < r; i++)
    {
      bap_mul_polynom_mpzm (&Z, &B[i], &sigma[i]);
      bap_sub_polynom_mpzm (&A, &A, &Z);
    }
/*
ba0_printf ("resultat : %Azm\n", &A);
ba0_put_string ("=============================\n");
*/
  bap_evalcoeff_at_point_int_p_polynom_mpzm (&A, &A, point);
  if (!bap_is_zero_polynom_mpzm (&A))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_restore (&M);
}
#endif

/* Denote $\mbox{\em prod} = a_1 \cdots a_r$ and
 * $b_i = a_1 \cdots a_{i-1}\,a_{i+1} \cdots a_r$.
 *
 * Sets {\em sigma} to the unique Diophantine polynomial equation in
 * $\Z/p^k\Z [x,y_1,\ldots,y_t]$
 *
 * $$\sigma_1 \, b_1 + \cdots + \sigma_r\,b_r = C
 *		 \mod {(\mbox{\em point}^{\mbox{\em maxdeg}}, p^k)}$$
 *
 * such that $\deg (\sigma_i,x) < \deg (a_i,x)$.
 *
 * Assumes $\mbox{\tt ba0_mpzm_module} = p^k$, that $p$ does not divide
 * any initial of the $a_i$ modulo {\em point} and that the $a_i$ are 
 * relatively prime modulo~$(\mbox{\em point}, p)$.
 */

/*
 * texinfo: bap_multi_Diophante_polynom_mpzm
 * Denote @math{@emph{prod} = a_1 \cdot a_r} and
 * @math{b_i = a_1 \cdots a_{i-1}\,a_{i+1} \cdots a_r}.
 * Assigns to @var{sigma} the unique solution in @math{Z [x,\, y_1,\ldots,y_t]}
 * of the Diophantine polynomial equation
 * @math{\sigma_1 \, b_1 + \cdots + \sigma_r\,b_r = C}
 * modulo @math{({point}^{maxdeg},\,p^k)}
 * such that
 * @math{\deg (\sigma_i,x) < \deg (a_i,x)}.
 * Assumes that @code{ba0_mpzm_module} is @math{p^k}, that @var{p} does not divide
 * any initial of the @math{a_i} modulo @var{point} and that the @math{a_i} 
 * are relatively prime modulo @math{(@emph{point},\,p^k)}.
 */

BAP_DLL void
bap_multi_Diophante_polynom_mpzm (
    struct bap_polynom_mpzm *sigma,
    struct bap_product_mpzm *prod,
    struct bap_polynom_mpzm *C,
    struct bav_point_int_p *point,
    bav_Idegree maxdeg,
    ba0_mpz_t p,
    bav_Idegree k)
{
  ba0_int_p nb_f, nb_x, j;
  struct bap_polynom_mpzm *gamma, *delta;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  nb_f = prod->size;
  nb_x = point->size;

/* 
   gamma va recevoir le resultat qui sera finalement affecte a sigma.
*/
  gamma =
      (struct bap_polynom_mpzm *) ba0_alloc (sizeof (struct bap_polynom_mpzm) *
      nb_f);
  delta =
      (struct bap_polynom_mpzm *) ba0_alloc (sizeof (struct bap_polynom_mpzm) *
      nb_f);
  for (j = 0; j < nb_f; j++)
    {
      bap_init_polynom_mpzm (&gamma[j]);
      bap_init_polynom_mpzm (&delta[j]);
    }

  if (nb_x > 0)
    {
      bav_Idegree m;
      struct bap_polynom_mpzm *A, *monome;
      struct bap_polynom_mpzm *E, *F, *new_C;
      struct bap_polynom_mpzm *B;
      struct bav_point_int_p new_point;
      struct bap_product_mpzm new_prod;
      struct ba0_mark M2;
/*
   A = produit (prod->tab [j].factor)
*/
      ba0_push_another_stack ();
      ba0_record (&M2);
      A = bap_new_polynom_mpzm ();
      bap_expand_product_mpzm (A, prod);
      ba0_pull_stack ();
/*
   Initialisation du struct ba0_table * B.
   B [j] = A / prod->tab [j].factor
*/
      B = (struct bap_polynom_mpzm *) ba0_alloc (sizeof (struct
              bap_polynom_mpzm) * nb_f);
      for (j = 0; j < nb_f; j++)
        {
          bap_init_polynom_mpzm (&B[j]);
/*
   Bug possible a cause d'bap_exquo_polynom_mpzm
*/
          bap_exquo_polynom_mpzm (&B[j], A, &prod->tab[j].factor);
        }
/*
   Recuperation de l'emplacement de A
*/
      ba0_restore (&M2);
/*
   Si point = (x1 = a1, ..., x{nb_x-1} = a{nb_x-1})
   alors new_point = (x1 = a1, ..., x{nb_x-2} = a{nb_x-2}) et
	 
   new_prod = prod 	(mod (x{nb_x-1} - a{nb_x-1}))
   new_C = C 		(mod (x{nb_x-1} - a{nb_x-1}))
 
   L'appel recursif 
	bap_multi_Diophante_polynom_mpzm 
				(gamma, new_prod, new_c, new_point, maxdeg)
   donne des values a gamma.
*/
      ba0_init_point ((struct ba0_point *) &new_point);
      point->size--;
      ba0_set_point ((struct ba0_point *) &new_point,
          (struct ba0_point *) point);
      point->size++;

      bap_init_product_mpzm (&new_prod);
      bap_realloc_product_mpzm (&new_prod, nb_f);

      for (j = 0; j < nb_f; j++)
        {
          bap_eval_to_polynom_at_value_int_p_polynom_mpzm (&new_prod.
              tab[j].factor, &prod->tab[j].factor, point->tab[point->size - 1]);
        }
      new_prod.size = prod->size;

      new_C = bap_new_polynom_mpzm ();
      bap_eval_to_polynom_at_value_int_p_polynom_mpzm (new_C, C,
          point->tab[point->size - 1]);

      bap_multi_Diophante_polynom_mpzm (gamma, &new_prod, new_C, &new_point,
          maxdeg, p, k);
/*
   E = C - somme (gamma [j] * B [j]) mod ba0_mpzm_module
*/
      E = bap_new_polynom_mpzm ();
      bap_set_polynom_mpzm (E, C);
      F = new_C;
      for (j = 0; j < nb_f; j++)
        {
          bap_mul_polynom_mpzm (F, &gamma[j], &B[j]);
          bap_sub_polynom_mpzm (E, E, F);
        }

      monome = bap_new_polynom_mpzm ();
      bap_set_polynom_one_mpzm (monome);
      for (m = 1; m <= maxdeg && !bap_is_zero_polynom_mpzm (E); m++)
        {
          bap_mul_polynom_value_int_p_mpzm (monome, monome,
              point->tab[point->size - 1]);
          bap_coeftayl_polynom_mpzm (new_C, E, point->tab[point->size - 1], m);
          if (!bap_is_zero_polynom_mpzm (new_C))
            {
/*
   new_C = coeftayl etc ...
   L'appel recursif
	bap_multi_Diophante_polynom_mpzm 
				(delta, new_prod, new_C, new_point, maxdeg)
   donne des values a delta.
*/
              bap_multi_Diophante_polynom_mpzm (delta, &new_prod, new_C,
                  &new_point, maxdeg, p, k);
/*
   gamma [j] = gamma [j] + delta [j] * monome
*/
              for (j = 0; j < nb_f; j++)
                {
                  bap_mul_polynom_mpzm (&delta[j], &delta[j], monome);
                  bap_add_polynom_mpzm (&gamma[j], &gamma[j], &delta[j]);
                }
/*
   E = E - somme (delta [j] * B [j]) mod ba0_mpzm_module
*/
              for (j = 0; j < nb_f; j++)
                {
                  bap_mul_polynom_mpzm (F, &delta[j], &B[j]);
                  bap_sub_polynom_mpzm (E, E, F);
                }
            }
        }
    }
  else
    {
      struct bav_dictionary_variable dict;
      struct bav_tableof_variable vars;
      struct bav_term T;
      struct bap_itermon_mpzm iter;
      ba0_mpz_t *lc;
      struct bav_rank rg;

      bav_init_dictionary_variable (&dict, 6);
      ba0_init_table ((struct ba0_table *) &vars);
      ba0_realloc_table ((struct ba0_table *) &vars, 64);

      bap_mark_indets_polynom_mpzm (&dict, &vars, C);
      for (j = 0; j < nb_f; j++)
        bap_mark_indets_polynom_mpzm (&dict, &vars, &prod->tab[j].factor);
 
      if (vars.size != 1)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);

      rg.var = vars.tab[0];

      bav_init_term (&T);
      bap_begin_itermon_mpzm (&iter, C);
      while (!bap_outof_itermon_mpzm (&iter))
        {
          bap_term_itermon_mpzm (&T, &iter);
          lc = bap_coeff_itermon_mpzm (&iter);
          if (bav_is_one_term (&T))
            rg.deg = 0;
          else
            rg.deg = T.rg[0].deg;
          bap_uni_Diophante_polynom_mpzm (delta, prod, &rg, p, k);
          for (j = 0; j < nb_f; j++)
            {
              bap_mul_polynom_numeric_mpzm (&delta[j], &delta[j], *lc);
              bap_add_polynom_mpzm (&gamma[j], &gamma[j], &delta[j]);
            }
          bap_next_itermon_mpzm (&iter);
        }
    }
/*
ba0_put_string ("-------- ba0_output de multivariate_diophante ---------\n");
*/
  ba0_pull_stack ();
  for (j = 0; j < nb_f; j++)
    {
      bap_set_polynom_mpzm (&sigma[j], &gamma[j]);
/*
	ba0_printf ("%Azm\n", &sigma [j]);
*/
    }

  ba0_restore (&M);

#if defined (BA0_HEAVY_DEBUG)
  verifie_multivariate_diophante_poly_mpzm (sigma, prod, C, point, maxdeg, p,
      k);
#endif
}
