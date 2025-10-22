#include "bad_quench_regchain.h"
#include "bad_reduction.h"
#include "bad_regularize.h"
#include "bad_invert.h"
#include "bad_global.h"

/*
 * texinfo: bad_set_settings_regularize
 * Set @code{bad_regularize_strategy} to @var{strategy}.
 * A zero value is replaced by the default value.
 */

BAD_DLL void
bad_set_settings_regularize (
    enum bad_typeof_regularize_strategy strategy)
{
  bad_initialized_global.regularize.strategy =
      strategy ? strategy : bad_subresultant_regularize_strategy;
}

/*
 * texinfo: bad_get_settings_regularize
 * Assign @code{bad_regularize_strategy} to *@var{strategy}.
 * The pointer may be zero.
 */

BAD_DLL void
bad_get_settings_regularize (
    enum bad_typeof_regularize_strategy *strategy)
{
  if (strategy)
    *strategy = bad_initialized_global.regularize.strategy;
}

/**********************************************************************
 CONTEXT FUNCTION FOR BAD_EUCLID
 **********************************************************************/

static enum bad_typeof_context
bad_context (
    struct bad_tableof_quadruple *tabG,
    struct bad_regchain *C)
{
  if (C != (struct bad_regchain *) 0)
    if (tabG != (struct bad_tableof_quadruple *) 0)
      return bad_pardi_context;
    else
      return bad_inverse_context;
  else
    return bad_rg_context;
}

typedef void bad_Euclid_function (
    struct bap_tableof_tableof_polynom_mpz *,
    struct bad_tableof_quadruple *,
    enum bad_typeof_Euclid,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *,
    bool,
    bool,
    struct bad_regchain *,
    struct bad_base_field *,
    struct bap_polynom_mpz * *);

/*****************************************************************************
 THE EUCLIDEAN ALGORITHM 

 It is performed with coefficients taken modulo an ideal.

 In the Rosenfeld-Groebner context, splitting cases may lead to
 recursive calls, through bad_ensure_regular_lcoeff.
 *****************************************************************************/

static bad_Euclid_function bad_Euclid_gcd_prem_and_factor_mod_regchain;
static bad_Euclid_function bad_Euclid_gcd_prem_mod_regchain;
static bad_Euclid_function bad_Euclid_subresultant_mod_regchain;

/*
 * texinfo: bad_Euclid_mod_regchain
 * This function essentially performs the Euclidean algorithm (possibly extended
 * or half-extended) over @var{A} and @var{B}, with coefficients taken
 * modulo some ideal @math{I}, which is precised below. 
 * 
 * It used to be called from different contexts but it is now only
 * called from @code{bad_pardi}.
 *
 * The polynomials are supposed to have coefficients in the field @var{K}.
 * 
 * The variable @var{v} is assumed to be greater than or equal to the leaders 
 * of these two polynomials. The booleans @var{reginitA} and @var{reginitB}
 * indicate if the leading coefficients of @var{A} and @var{B} are regular
 * modulo @math{I}. In some cases, exhibiting a zero divisor modulo @math{I}
 * raises the exception @code{BAD_EXRDDZ}. The zero divisor is then
 * stored in @var{ddz}.
 * 
 * The last entry of @var{tabV} receives an Euclidean relation.
 * If @var{type} is @code{bad_extended_Euclid} then triples
 * @math{(G, U, V)} such that @math{U \, A + V \, B = G} are
 * stored in @var{tabV}. 
 * If @var{type} is @code{bad_basic_Euclid} then only @var{G} is computed.
 * If @var{type} is @code{bad_half_extended_Euclid} then only @var{G} and
 * @var{U} are computed.
 * 
 * The parameter @var{tabV} is a table because the computation may lead
 * to splitting cases (in which case, new entries need to be appended) or to
 * some inconsistencies (in which case, entries need to be removed). 
 * Contexts are as follows.
 *
 * @itemize
 * @item When called from @code{bad_Rosenfeld_Groebner}, the parameter @var{C}
 * is zero and the table @var{tabG} is not zero. Then the ideal @math{I}
 * is the ideal associated to the last entry @var{G} of @var{tabG}. Booleans
 * @var{reginitA} and @var{reginitB} just indicate if the leading coefficients
 * of @var{A} and @var{B} are stored in the inequations list of @var{G}. 
 * Each step of the Euclidean algorithm normally leads to a splitting:
 * the leading coefficient of the current remainder is considered
 * as nonzero in the general branch; unless discarded by the
 * @code{bad_nonzero} function, it is also separately considered as zero,
 * producing another quadruple in @var{tabG} and another entry in @var{tabV}. 
 * All branches are processed up to the end. Some of them (possibly all) can 
 * be proven inconsistent. The corresponding entries of @var{tabG} and 
 * @var{tabV} are then removed.
 *
 * @item When called from @code{bad_pardi}, the parameters @var{C} and
 * @var{tabG} are nonzero.  The ideal @math{I} is the one defined by @var{C}.
 * It is assumed to be prime. The @code{bad_pardi} function only needs
 * one quadruple, which is the last entry of @var{tabG}. 
 * @item When called from @code{bad_invert_polynom_mod_regchain}, the
 * parameter @var{C} is nonzero while @var{tabG} is zero.
 * The ideal @math{I} is the one defined by @var{C}.
 * It does not need to be prime. The regularity tests may exhibit
 * some zero divisor. In such cases, the exception @code{BAD_EXRDDZ}
 * is raised and the zero divisor is stored in *@var{ddz}.
 * @end itemize
 */

BAD_DLL void
bad_Euclid_mod_regchain (
    struct bap_tableof_tableof_polynom_mpz *tabV,
    struct bad_tableof_quadruple *tabG,
    enum bad_typeof_Euclid type,
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *B,
    struct bav_variable *v,
    bool reginitA,
    bool reginitB,
    struct bad_regchain *C,
    struct bad_base_field *K,
    struct bap_polynom_mpz * *ddz)
{
  switch (bad_initialized_global.regularize.strategy)
    {
    case bad_subresultant_regularize_strategy:
      bad_Euclid_subresultant_mod_regchain (tabV, tabG, type, A, B, v, reginitA,
          reginitB, C, K, ddz);
      break;
    case bad_gcd_prem_regularize_strategy:
      bad_Euclid_gcd_prem_mod_regchain (tabV, tabG, type, A, B, v, reginitA,
          reginitB, C, K, ddz);
      break;
    case bad_gcd_prem_and_factor_regularize_strategy:
      bad_Euclid_gcd_prem_and_factor_mod_regchain (tabV, tabG, type, A, B, v,
          reginitA, reginitB, C, K, ddz);
      break;
    }
}

/*
   Subfunction of bad_Euclid_mod_regchain.
   Remove lcoeff (A, v) from A while this coefficient is zero mod C.
   At the end of the loop (i.e. when lcoeff (A, v) is non zero), checks
	that lcoeff (A, v) is regular mod C.
   If non regular, the exception BAD_EXRDDZ is raised and a divisor
	of some element of C is stored in *ddz (provided ddz is nonzero).
   The boolean *rankfall receives true if at least one of the lcoeff (A, v)
	is zero (so that the rank of A falls).

   Stores in P the coefficients which are zero mod C but not mod the
	component A of G.

   tabV and tabG lie in the current stack. They may be modified in rg context.
   B lies in the other stack. It may be modified in inverse and pardi contexts.
*/

static bool
bad_ensure_regular_lcoeff (
    struct bap_tableof_tableof_polynom_mpz *tabV,
    struct bad_tableof_quadruple *tabG,
    enum bad_typeof_Euclid type,
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *B,
    struct bav_variable *v,
    bool reginitA,
    struct bad_regchain *C,
    struct bad_base_field *K,
    struct bap_polynom_mpz * *ddz)
{
  struct bad_quadruple *G = (struct bad_quadruple *) 0, *H;
  enum bad_typeof_reduction type_red;
  enum bad_typeof_context context;
  bool *discarded_branch = 0;
  struct bap_tableof_polynom_mpz *V, *W;
  struct bap_polynom_mpz init, reductum;
  ba0_int_p index_G, index_V;
  bool consistent;

/*
   init and reductum are going to receive parts of B.
   They thus lie in the other stack.
   Actually, the stack changing operations are not necessary since the
	initial and reductum inst. are implemented with no memory allocation.
*/
  ba0_push_another_stack ();
  bap_init_readonly_polynom_mpz (&init);
  bap_init_readonly_polynom_mpz (&reductum);
  ba0_pull_stack ();

  consistent = true;
  context = bad_context (tabG, C);
  switch (context)
    {
    case bad_rg_context:
      index_G = tabG->size - 1;
      index_V = tabV->size - 1;
      G = tabG->tab[index_G];
      V = tabV->tab[index_V];
/*
   A splitting is generated :
	H = G + initial, reductum = 0
	G = G + initial <> 0.
   About H. The initial goes in the P component. 
	    For the reductum, it depends on its degree in v. 
   If this degree is > 0 then 
	B degenerates to the reductum and a recursive call to bad_Euclid 
	is performed to handle that degenerated gcd computation. 
   If this degree is <= 0 then 
	the reductum is stored in the P component of H and, modulo the 
	equations present in P, the polynomial B degenerates to zero and 
	the gcd, which is A, is stored in W.
*/
      ba0_push_another_stack ();
      bap_initial_and_reductum2_polynom_mpz (&init, &reductum, B, v);
      ba0_pull_stack ();
      ba0_realloc2_table ((struct ba0_table *) tabG, tabG->size + 1,
          (ba0_new_function *) & bad_new_quadruple);
      ba0_realloc2_table ((struct ba0_table *) tabV, tabV->size + 1,
          (ba0_new_function *) & ba0_new_table);
      H = tabG->tab[tabG->size++];
      W = tabV->tab[tabV->size++];
      bad_set_quadruple (H, G);
/*
   If G + initial = 0 (possibly + reductum = 0) is inconsistent then
        the quadruple H is discarded.
*/
      if (!bad_simplify_and_store_in_P_quadruple (H, discarded_branch, &init,
              K))
        {
          tabG->size--;
          tabV->size--;
        }
      else
        {
          if (!bap_depend_polynom_mpz (&reductum, v))
            {
              if (!bad_simplify_and_store_in_P_quadruple (H, discarded_branch,
                      &reductum, K))
                {
                  tabG->size--;
                  tabV->size--;
                }
              else
                {
                  ba0_realloc2_table ((struct ba0_table *) W, 1,
                      (ba0_new_function *) & bap_new_polynom_mpz);
                  bap_set_polynom_mpz (W->tab[0], A);
                  W->size = 1;
                }
            }
          else
            bad_Euclid_mod_regchain (tabV, tabG, type, A, &reductum, v,
                reginitA, false, C, K, ddz);
/*
   The quadruple H and possibly many other ones, due to the recursive call
	to bad_Euclid are stored in tabG, above G (the corresponding gcds
	are stored in tabV, above V).
   I manage to put (G, V) at the top of the stacks tabG and tabV.
*/
          BA0_SWAP (struct bad_quadruple *,
              tabG->tab[tabG->size - 1],
              tabG->tab[index_G]);
          BA0_SWAP (struct bap_tableof_polynom_mpz *,
              tabV->tab[tabV->size - 1],
              tabV->tab[index_V]);
        }
      consistent =
          bad_simplify_and_store_in_S_quadruple (G, discarded_branch, &init, K);
      break;
    case bad_pardi_context:
      G = tabG->tab[tabG->size - 1];
    case bad_inverse_context:
      type_red =
          bad_defines_a_differential_ideal_regchain (C) ? bad_full_reduction :
          bad_algebraic_reduction;
/*
   If lcoeff (B) = 0 mod C then 
      B = reductum (B)
      in the pardi case: if lcoeff (B) <> 0 mod the component A of G then 
	this lcoeff is stored it is stored in the component P of G.
   If deg (B, v) = 0 then, 
      in the pardi case: B is necessarily zero mod C.
*/
      for (;;)
        {
          if (bap_is_zero_polynom_mpz (B))
            break;
          ba0_push_another_stack ();
          bap_initial2_polynom_mpz (&init, B, v);
          ba0_pull_stack ();
          if (bap_depend_polynom_mpz (B, v) || context == bad_inverse_context)
            {
              if (!bad_is_a_reduced_to_zero_polynom_by_regchain (&init, C,
                      type_red))
                break;
            }
          if (context == bad_pardi_context
              && !bad_is_a_reduced_to_zero_polynom_by_regchain (&init, &G->A,
                  type_red))
            bad_simplify_and_store_in_P_quadruple (G, discarded_branch, &init,
                K);
          ba0_push_another_stack ();
          bap_lcoeff_and_reductum_polynom_mpz (BAP_NOT_A_POLYNOM_mpz, B, B, v);
          ba0_pull_stack ();
        }
/*
   In the inverse context, we only know that the lcoeff of B is non zero.
   We need to make sure it is regular.
   The problem does not arise with pardi since the ideal is prime.
*/
      if (context == bad_inverse_context
          && !bad_defines_a_prime_ideal_regchain (C))
        {
          ba0_push_another_stack ();
          bap_initial2_polynom_mpz (&init, B, v);
          ba0_pull_stack ();
          bad_check_regularity_polynom_mod_regchain (&init, C, K, ddz);
        }
      break;
    }
  return consistent;
}

/*
  Subfunction of bad_Euclid_mod_regchain
  Computations are performed using subresultant sequences
*/

static bad_Euclid_function bad_basic_Euclid_subresultant_mod_regchain;
static bad_Euclid_function bad_extended_Euclid_subresultant_mod_regchain;

static void
bad_Euclid_subresultant_mod_regchain (
    struct bap_tableof_tableof_polynom_mpz *tabV,
    struct bad_tableof_quadruple *tabG,
    enum bad_typeof_Euclid type,
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *B,
    struct bav_variable *v,
    bool reginitA,
    bool reginitB,
    struct bad_regchain *C,
    struct bad_base_field *K,
    struct bap_polynom_mpz * *ddz)
{
  if (type == bad_basic_Euclid)
    bad_basic_Euclid_subresultant_mod_regchain (tabV, tabG, type, A, B, v,
        reginitA, reginitB, C, K, ddz);
  else
    bad_extended_Euclid_subresultant_mod_regchain (tabV, tabG, type, A, B, v,
        reginitA, reginitB, C, K, ddz);
}

/*
   Subfunction of bad_Euclid_subresultant_mod_regchain
   Only the last nonzero subresultant is required (not the Bezout identity)

   Stores in S the actual leading coefficients of the remainders (but not the
	leading coefficient of the first remainder).
   The function ensure_regular_lcoeff modifies P.
*/

static void
bad_basic_Euclid_subresultant_mod_regchain (
    struct bap_tableof_tableof_polynom_mpz *tabV,
    struct bad_tableof_quadruple *tabG,
    enum bad_typeof_Euclid type,
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *B,
    struct bav_variable *v,
    bool reginitA,
    bool reginitB,
    struct bad_regchain *C,
    struct bad_base_field *K,
    struct bap_polynom_mpz * *ddz)
{
  struct bad_quadruple *G = (struct bad_quadruple *) 0; /* to avoid a warning */
  enum bad_typeof_context context;
  bool *discarded_branch = 0;
  struct bap_tableof_polynom_mpz *V;
  struct bap_polynom_mpz *P, *Q, *Z;
  struct bap_polynom_mpz coeff, s;
  bav_Idegree d, delta;
  bool consistent, rankfall;
  struct ba0_mark M;

  P = (struct bap_polynom_mpz *) 0;
  Q = (struct bap_polynom_mpz *) 0;
  Z = (struct bap_polynom_mpz *) 0;

  ba0_push_another_stack ();
  ba0_record (&M);
/*
   The result (the gcd of A and B) is stored in the V on the top of
	the stack tabV. 
   In the pardi and rg case, one also work with the G on the top of
	the stack tabG. In the rg case, it may happen that G gets
	inconsistent. It is then pulled out of the stack.
*/
  context = bad_context (tabG, C);
  switch (context)
    {
    case bad_rg_context:
    case bad_pardi_context:
      G = tabG->tab[tabG->size - 1];
      break;
    case bad_inverse_context:
      break;
    }
  V = tabV->tab[tabV->size - 1];
  if (bap_leading_degree_polynom_mpz (A) < bap_leading_degree_polynom_mpz (B))
    {
      BA0_SWAP (struct bap_polynom_mpz *,
          A,
          B);
      BA0_SWAP (bool,
          reginitA,
          reginitB);
    }
/*
   We make sure that the leading coefficient of the lower degree polynomial
	is regular.
*/
  consistent = true;
  if (!reginitB)
    {
      ba0_pull_stack ();
      switch (context)
        {
        case bad_inverse_context:
        case bad_pardi_context:
          bad_ensure_regular_lcoeff (tabV, tabG, type, A, B, v, reginitA, C, K,
              ddz);
          break;
        case bad_rg_context:
          consistent =
              bad_ensure_regular_lcoeff (tabV, tabG, type, A, B, v, reginitA, C,
              K, ddz);
          break;
        }
      ba0_push_another_stack ();
    }
  if (consistent)
    {
      bap_init_readonly_polynom_mpz (&coeff);
      bap_init_polynom_mpz (&s);

      P = bap_new_polynom_mpz ();
      Q = bap_new_polynom_mpz ();
      Z = bap_new_polynom_mpz ();
      bap_set_polynom_mpz (P, A);
      bap_set_polynom_mpz (Q, B);
    }
/*
   Result in P at the end of the loop (unless inconsistent)
*/
  while (consistent && !bap_is_zero_polynom_mpz (Q))
    {
/*
   (P, Q) = (Q, prem (P, Q)).
   The original code of Lionel Ducos takes prem (P, - Q).
*/
      if (bap_degree_polynom_mpz (Q, v) == 0)
        {
          BA0_SWAP (struct bap_polynom_mpz *,
              P,
              Q);
          bap_set_polynom_zero_mpz (Q);
        }
      else
        {
          bap_initial2_polynom_mpz (&coeff, Q, v);
          delta =
              bap_leading_degree_polynom_mpz (P) -
              bap_leading_degree_polynom_mpz (Q);
          bap_pow_polynom_mpz (&s, &coeff, delta);
          bap_prem_polynom_mpz (Z, (bav_Idegree *) 0, P, Q, v);
          BA0_SWAP (struct bap_polynom_mpz *,
              Z,
              Q);
          BA0_SWAP (struct bap_polynom_mpz *,
              Z,
              P);
        }
      rankfall = false;
      while (consistent && !bap_is_zero_polynom_mpz (Q) && !rankfall)
        {
          d = bap_degree_polynom_mpz (Q, v);
          ba0_pull_stack ();
          switch (context)
            {
            case bad_inverse_context:
            case bad_pardi_context:
              bad_ensure_regular_lcoeff (tabV, tabG, type, P, Q, v, true, C, K,
                  ddz);
              break;
            case bad_rg_context:
              if (bap_depend_polynom_mpz (Q, v))
                consistent =
                    bad_ensure_regular_lcoeff (tabV, tabG, type, P, Q, v, true,
                    C, K, ddz);
              else
                {
                  consistent =
                      bad_simplify_and_store_in_P_quadruple (G,
                      discarded_branch, Q, K);
                  bap_set_polynom_zero_mpz (Q);
                }
              break;
            }
          ba0_push_another_stack ();
          if (!consistent || bap_is_zero_polynom_mpz (Q))
            continue;
          rankfall = d != bap_degree_polynom_mpz (Q, v);
          if (rankfall)
            continue;
          bap_initial2_polynom_mpz (&coeff, Q, v);
          delta =
              bap_leading_degree_polynom_mpz (P) - bap_degree_polynom_mpz (Q,
              v);
          bap_muldiv2_Lazard_polynom_mpz (Z, Q, &coeff, &s, delta);
          bap_nsr2_Ducos_polynom_mpz (P, P, Q, Z, &s, v);
          BA0_SWAP (struct bap_polynom_mpz *,
              P,
              Q);
          bap_lcoeff_polynom_mpz (&s, Z, v);
        }
    }
  ba0_pull_stack ();
  if (!consistent)
    {
      tabG->size--;
      tabV->size--;
    }
  else
    {
      ba0_realloc2_table ((struct ba0_table *) V, 1,
          (ba0_new_function *) & bap_new_polynom_mpz);
      bap_set_polynom_mpz (V->tab[0], P);
      V->size = 1;
    }
  ba0_restore (&M);
}

/*
   Subfunction of bad_Euclid_subresultant_mod_regchain
   The table result is initialized.
   Its size gives the part of the Bezout identity which is desired.

   Stores in S the actual leading coefficients of the remainders (but not the
	first one).
   The function ensure_regular_lcoeff modifies P.
*/

static void
bad_extended_Euclid_subresultant_mod_regchain (
    struct bap_tableof_tableof_polynom_mpz *tabV,
    struct bad_tableof_quadruple *tabG,
    enum bad_typeof_Euclid type,
    struct bap_polynom_mpz *P,
    struct bap_polynom_mpz *Q,
    struct bav_variable *v,
    bool reginitP,
    bool reginitQ,
    struct bad_regchain *C,
    struct bad_base_field *K,
    struct bap_polynom_mpz * *ddz)
{
  struct bad_quadruple *G;
  enum bad_typeof_context context;
  struct bap_tableof_polynom_mpz *V, *VZ, *VP, *VQ;
  struct bap_polynom_mpz s, coeff, bunk;
  bav_Idegree degP, degQ, d;
  bool perm, rankfall, consistent;
  ba0_int_p i, n = 0;
  struct ba0_mark M;

  VP = (struct bap_tableof_polynom_mpz *) 0;
  VQ = (struct bap_tableof_polynom_mpz *) 0;
  VZ = (struct bap_tableof_polynom_mpz *) 0;

  context = bad_context (tabG, C);

  if (context != bad_inverse_context)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);
  if (bap_degree_polynom_mpz (P, v) <= 0 || bap_degree_polynom_mpz (Q, v) <= 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_another_stack ();
  ba0_record (&M);

  switch (context)
    {
    case bad_rg_context:
    case bad_pardi_context:
      G = tabG->tab[tabG->size - 1];
      break;
    case bad_inverse_context:
      break;
    }
  V = tabV->tab[tabV->size - 1];
  switch (type)
    {
    case bad_basic_Euclid:
      BA0_RAISE_EXCEPTION (BA0_ERRALG);
      break;
    case bad_half_extended_Euclid:
      n = 2;
      break;
    case bad_extended_Euclid:
      n = 3;
      break;
    }
  degP = bap_degree_polynom_mpz (P, v);
  degQ = bap_degree_polynom_mpz (Q, v);
  if (degP < degQ)
    {
      BA0_SWAP (struct bap_polynom_mpz *,
          P,
          Q);
      BA0_SWAP (bav_Idegree, degP, degQ);
      BA0_SWAP (bool,
          reginitP,
          reginitQ);
      perm = true;
    }
  else
    perm = false;

  consistent = true;
  if (!reginitQ)
    {
      ba0_pull_stack ();
      switch (context)
        {
        case bad_inverse_context:
        case bad_pardi_context:
          bad_ensure_regular_lcoeff (tabV, tabG, type, P, Q, v, reginitP, C, K,
              ddz);
          break;
        case bad_rg_context:
          consistent =
              bad_ensure_regular_lcoeff (tabV, tabG, type, P, Q, v, reginitP, C,
              K, ddz);
          break;
        }
      ba0_push_another_stack ();
    }
  if (consistent)
    {
      bap_init_polynom_mpz (&bunk);
      bap_init_readonly_polynom_mpz (&coeff);
      bap_init_polynom_mpz (&s);
      VP = (struct bap_tableof_polynom_mpz *) ba0_new_table ();
      VQ = (struct bap_tableof_polynom_mpz *) ba0_new_table ();
      VZ = (struct bap_tableof_polynom_mpz *) ba0_new_table ();
      ba0_realloc2_table ((struct ba0_table *) VP, n,
          (ba0_new_function *) & bap_new_polynom_mpz);
      ba0_realloc2_table ((struct ba0_table *) VQ, n,
          (ba0_new_function *) & bap_new_polynom_mpz);
      ba0_realloc2_table ((struct ba0_table *) VZ, n,
          (ba0_new_function *) & bap_new_polynom_mpz);
      VP->size = n;
      VQ->size = n;
      VZ->size = n;

      bap_initial2_polynom_mpz (&coeff, Q, v);

      bap_pow_polynom_mpz (&s, &coeff, degP - degQ);
      bap_set_polynom_mpz (VP->tab[0], Q);
      bap_set_polynom_mpz (VZ->tab[0], Q);
      if (n == 2)
        {
          if (perm)
            {
              bap_set_polynom_one_mpz (VP->tab[1]);
              bap_set_polynom_one_mpz (VZ->tab[1]);
            }
        }
      else if (n == 3)
        {
          if (perm)
            {
              bap_set_polynom_one_mpz (VP->tab[1]);
              bap_set_polynom_one_mpz (VZ->tab[1]);
            }
          else
            {
              bap_set_polynom_one_mpz (VP->tab[2]);
              bap_set_polynom_one_mpz (VZ->tab[2]);
            }
        }

      if (n == 1)
        bap_pseudo_division_polynom_mpz (BAP_NOT_A_POLYNOM_mpz, VQ->tab[0],
            (bav_Idegree *) 0, P, Q, v);
      else if (n == 2)
        {
          if (perm)
            {
              bap_pseudo_division_polynom_mpz (VQ->tab[1], VQ->tab[0],
                  (bav_Idegree *) 0, P, Q, v);
              bap_neg_polynom_mpz (VQ->tab[1], VQ->tab[1]);
            }
          else
            {
              bap_pseudo_division_polynom_mpz (BAP_NOT_A_POLYNOM_mpz,
                  VQ->tab[0], &d, P, Q, v);
              bap_initial2_polynom_mpz (&coeff, Q, v);
              bap_pow_polynom_mpz (VQ->tab[1], &coeff, d);
            }
        }
      else
        {
          if (perm)
            {
              bap_pseudo_division_polynom_mpz (VQ->tab[1], VQ->tab[0], &d, P, Q,
                  v);
              bap_neg_polynom_mpz (VQ->tab[1], VQ->tab[1]);
              bap_initial2_polynom_mpz (&coeff, Q, v);
              bap_pow_polynom_mpz (VQ->tab[2], &coeff, d);
            }
          else
            {
              bap_pseudo_division_polynom_mpz (VQ->tab[2], VQ->tab[0], &d, P, Q,
                  v);
              bap_neg_polynom_mpz (VQ->tab[2], VQ->tab[2]);
              bap_initial2_polynom_mpz (&coeff, Q, v);
              bap_pow_polynom_mpz (VQ->tab[1], &coeff, d);
            }
        }
    }
  while (consistent && !bap_is_zero_polynom_mpz (VQ->tab[0]))
    {
      d = bap_degree_polynom_mpz (VQ->tab[0], v);
      ba0_pull_stack ();
      switch (context)
        {
        case bad_inverse_context:
        case bad_pardi_context:
          bad_ensure_regular_lcoeff (tabV, tabG, type, VP->tab[0], VQ->tab[0],
              v, true, C, K, ddz);
          break;
        case bad_rg_context:
          consistent =
              bad_ensure_regular_lcoeff (tabV, tabG, type, VP->tab[0],
              VQ->tab[0], v, true, C, K, ddz);
          break;
        }
      ba0_push_another_stack ();
      if (!consistent)
        continue;
      rankfall = d != bap_degree_polynom_mpz (VQ->tab[0], v);
      if (rankfall)
        {
          degP = bap_degree_polynom_mpz (VZ->tab[0], v);
          degQ = bap_degree_polynom_mpz (VQ->tab[0], v);
          bap_initial2_polynom_mpz (&coeff, VQ->tab[0], v);
          bap_pow_polynom_mpz (&s, &coeff, degP - degQ);
          bap_set_polynom_mpz (&bunk, VZ->tab[0]);
          for (i = 0; i < n; i++)
            {
              bap_set_polynom_mpz (VP->tab[i], VQ->tab[i]);
              bap_set_polynom_mpz (VZ->tab[i], VQ->tab[i]);
            }
          if (n == 1)
            bap_pseudo_division_polynom_mpz (BAP_NOT_A_POLYNOM_mpz, VQ->tab[0],
                (bav_Idegree *) 0, &bunk, VQ->tab[0], v);
          else if (n == 2)
            {
              bap_pseudo_division_polynom_mpz (BAP_NOT_A_POLYNOM_mpz,
                  VQ->tab[0], &d, &bunk, VQ->tab[0], v);
              bap_initial2_polynom_mpz (&coeff, VQ->tab[0], v);
              bap_pow_polynom_mpz (VQ->tab[1], &coeff, d);
            }
          else
            {
              bap_pseudo_division_polynom_mpz (VQ->tab[2], VQ->tab[0], &d,
                  &bunk, VQ->tab[0], v);
              bap_neg_polynom_mpz (VQ->tab[2], VQ->tab[2]);
              bap_initial2_polynom_mpz (&coeff, VQ->tab[0], v);
              bap_pow_polynom_mpz (VQ->tab[1], &coeff, d);
            }
        }
      else
        {
          bap_initial2_polynom_mpz (&coeff, VQ->tab[0], v);
          degQ = bap_degree_polynom_mpz (VQ->tab[0], v);
          degP = bap_degree_polynom_mpz (VZ->tab[0], v);
          bap_muldiv3_Lazard_polynom_mpz (VZ, VQ, &coeff, &s, degP - degQ);
          bap_initial2_polynom_mpz (&coeff, VZ->tab[0], v);
          bap_nsr3_Ducos_polynom_mpz (VP, VP, VQ, &s, &coeff, v);
          BA0_SWAP (struct bap_tableof_polynom_mpz *,
              VP,
              VQ);
          bap_set_polynom_mpz (&s, &coeff);
        }
    }
  ba0_pull_stack ();
  if (!consistent)
    {
      tabG->size--;
      tabV->size--;
    }
  else
    {
      ba0_realloc2_table ((struct ba0_table *) V, n,
          (ba0_new_function *) bap_new_polynom_mpz);
      for (i = 0; i < n; i++)
        bap_set_polynom_mpz (V->tab[i], VZ->tab[i]);
      V->size = n;
    }
  ba0_restore (&M);
}

static void
bad_Euclid_gcd_prem_and_factor_mod_regchain (
    struct bap_tableof_tableof_polynom_mpz *tabV,
    struct bad_tableof_quadruple *G,
    enum bad_typeof_Euclid type,
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *B,
    struct bav_variable *v,
    bool reginitA,
    bool reginitB,
    struct bad_regchain *C,
    struct bad_base_field *K,
    struct bap_polynom_mpz * *ddz)
{
  tabV = (struct bap_tableof_tableof_polynom_mpz *) 0;
  G = (struct bad_tableof_quadruple *) 0;
  type = bad_half_extended_Euclid;
  A = (struct bap_polynom_mpz *) 0;
  B = (struct bap_polynom_mpz *) 0;
  v = (struct bav_variable *) 0;
  reginitA = true;
  reginitB = true;
  C = (struct bad_regchain *) 0;
  K = (struct bad_base_field *) 0;
  ddz = (struct bap_polynom_mpz * *) 0;

  BA0_RAISE_EXCEPTION (BA0_ERRNYP);
}

static void
bad_Euclid_gcd_prem_mod_regchain (
    struct bap_tableof_tableof_polynom_mpz *tabV,
    struct bad_tableof_quadruple *G,
    enum bad_typeof_Euclid type,
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *B,
    struct bav_variable *v,
    bool reginitA,
    bool reginitB,
    struct bad_regchain *C,
    struct bad_base_field *K,
    struct bap_polynom_mpz * *ddz)
{
  tabV = (struct bap_tableof_tableof_polynom_mpz *) 0;
  G = (struct bad_tableof_quadruple *) 0;
  type = bad_half_extended_Euclid;
  A = (struct bap_polynom_mpz *) 0;
  B = (struct bap_polynom_mpz *) 0;
  v = (struct bav_variable *) 0;
  reginitA = true;
  reginitB = true;
  C = (struct bad_regchain *) 0;
  K = (struct bad_base_field *) 0;
  ddz = (struct bap_polynom_mpz * *) 0;

  BA0_RAISE_EXCEPTION (BA0_ERRNYP);
}

/****************************************************************************
 CHECK REGULARITY
 ****************************************************************************/

static void bad_check_algebraic_regularity_mod_regchain (
    struct bap_polynom_mpz *,
    struct bad_regchain *,
    struct bap_listof_polynom_mpz *,
    struct bad_base_field *,
    struct bap_polynom_mpz * *);

/*
 * texinfo: bad_check_regularity_polynom_mod_regchain
 * Return if @var{A} is regular modulo the ideal defined by @var{C}
 * over the base field @var{K}.
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
bad_check_regularity_polynom_mod_regchain (
    struct bap_polynom_mpz *A,
    struct bad_regchain *C,
    struct bad_base_field *K,
    struct bap_polynom_mpz * *ddz)
{
  enum bad_typeof_reduction type_red;
  struct bap_product_mpz P;
  struct ba0_mark M;
  ba0_int_p i;

  if (bap_is_zero_polynom_mpz (A))
    BA0_RAISE_EXCEPTION (BAD_EXRNUL);
  else if (bad_is_zero_regchain (C))
    return;
  else if (bad_defines_a_prime_ideal_regchain (C))
    {
      enum bad_typeof_reduction type_red;
/*
 * If the ideal is prime then the regularity test reduces to a non zero test
 */
      type_red =
          bad_defines_a_differential_ideal_regchain (C) ? bad_full_reduction :
          bad_algebraic_reduction;
      if (bad_is_a_reduced_to_zero_polynom_by_regchain (A, C, type_red))
        BA0_RAISE_EXCEPTION (BAD_EXRNUL);
      return;
    }
  else
    {
/*
 * The non prime ideal case.
 * One first reduces A, then applies the algebraic test.
 */
      ba0_record (&M);

      if (bad_defines_a_differential_ideal_regchain (C))
        type_red = bad_full_reduction;
      else
        type_red = bad_algebraic_reduction;

      bap_init_product_mpz (&P);
      bad_reduce_polynom_by_regchain (&P, (struct bap_product_mpz *) 0,
          (struct bav_tableof_term *) 0, A, C,
          type_red, bad_all_derivatives_to_reduce);
      if (bap_is_zero_product_mpz (&P))
        BA0_RAISE_EXCEPTION (BAD_EXRNUL);
/*
 * From now on, BAD_EXRNUL cannot be raised anymore.
 */
      for (i = 0; i < P.size; i++)
        bad_check_algebraic_regularity_mod_regchain (&P.tab[i].factor, C,
            (struct bap_listof_polynom_mpz *) 0, K, ddz);

      ba0_restore (&M);
    }
}

/*
 * Subfunction of bad_check_regularity_polynom_mod_regchain
 * Tests the regularity of A mod the algebraic ideal defined by C.
 *
 * A is nonzero modulo C.
 * The initial of A is nonzero modulo C.
 * C is not the zero regchain and should define a prime ideal.
 *
 * The function either returns or raises the exception BAD_EXRDDZ.
 * In the second case, a non-trivial divisor of some element of C
 * is returned in *ddz.
 *
 * S is a list of polynomials that might help factoring polynomials.
 */

static void bad_Euclid_check_algebraic_regularity_mod_regchain (
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *B,
    struct bav_variable *v,
    struct bad_regchain *C,
    struct bap_listof_polynom_mpz *S,
    struct bad_base_field *K,
    struct bap_polynom_mpz * *ddz);

static void
bad_check_algebraic_regularity_mod_regchain (
    struct bap_polynom_mpz *A,
    struct bad_regchain *C,
    struct bap_listof_polynom_mpz *S,
    struct bad_base_field *K,
    struct bap_polynom_mpz * *ddz)
{
  struct bap_polynom_mpz init;
  struct bav_variable *v;
  bav_Idegree dA, dk;
  ba0_int_p k;

  if (!bad_member_polynom_base_field (A, K))
    {
      v = bap_leader_polynom_mpz (A);
      bap_init_readonly_polynom_mpz (&init);
      bap_initial_polynom_mpz (&init, A);
      bad_check_algebraic_regularity_mod_regchain (&init, C, S, K, ddz);
      if (bad_is_leader_of_regchain (v, C, &k))
        {
          dA = bap_leading_degree_polynom_mpz (A);
          dk = bap_leading_degree_polynom_mpz (C->decision_system.tab[k]);
          if (dA < dk)
            bad_Euclid_check_algebraic_regularity_mod_regchain
                (C->decision_system.tab[k], A, v, C, S, K, ddz);
          else
            bad_Euclid_check_algebraic_regularity_mod_regchain (A,
                C->decision_system.tab[k], v, C, S, K, ddz);
        }
    }
}

/* 
 * Subfunction of bad_check_algebraic_regularity_mod_regchain
 * A and B depend on v, degree (A, v) > degree (B, v), and the initials 
 * of A and B are regular modulo the algebraic ideal defined by C.
 *
 * Either returns or raises BAD_EXRDDZ.
 *
 * Performs a variant of the Euclidean algorithm.
 */

static void
bad_Euclid_check_algebraic_regularity_mod_regchain (
    struct bap_polynom_mpz *A,
    struct bap_polynom_mpz *B,
    struct bav_variable *v,
    struct bad_regchain *C,
    struct bap_listof_polynom_mpz *S,
    struct bad_base_field *K,
    struct bap_polynom_mpz * *ddz)
{
  struct bap_product_mpz prod1, prod2;
  struct bap_polynom_mpz R, init;
  struct ba0_tableof_bool keep;
  struct ba0_mark M;
  ba0_int_p i, j;

  ba0_record (&M);

  bap_init_readonly_polynom_mpz (&init);
  bap_init_polynom_mpz (&R);
  bap_init_product_mpz (&prod1);
  bap_init_product_mpz (&prod2);
  ba0_init_table ((struct ba0_table *) &keep);

  baz_gcd_prem_polynom_mpz (&R, (struct bap_product_mpz *) 0, A, B, v);
  bad_reduce_easy_polynom_by_regchain (&R, &R, C, bad_algebraic_reduction);
  baz_factor_easy_polynom_mpz (&prod1, &keep, &R, S);

  if (bap_is_zero_product_mpz (&prod1))
    {
      if (ddz != (struct bap_polynom_mpz * *) 0)
        {
          *ddz = B;
          BA0_RAISE_EXCEPTION2 (BAD_EXRDDZ, "%Az", (void **) ddz);
        }
      else
        BA0_RAISE_EXCEPTION (BAD_EXRDDZ);
    }
/*
 * The remainder (prod1) of A by B seems not to be zero.
 */
  for (i = 0; i < prod1.size; i++)
    {
#define BAD_DO_REDUCE 1
#undef BAD_DO_REDUCE
#if defined BAD_DO_REDUCE
      bad_reduce_polynom_by_regchain (&prod2, (struct bap_product_mpz *) 0,
          (struct bav_tableof_term *) 0,
          &prod1.tab[i].factor, C, bad_algebraic_reduction,
          bad_all_derivatives_to_reduce);
#else
      if (bad_is_a_reduced_to_zero_polynom_by_regchain (&prod1.tab[i].factor, C,
              bad_algebraic_reduction))
        bap_set_product_zero_mpz (&prod2);
      else
        {
          bad_ensure_nonzero_initial_mod_regchain (&prod1.tab[i].factor,
              &prod1.tab[i].factor, C, bad_algebraic_reduction);
          bap_set_product_polynom_mpz (&prod2, &prod1.tab[i].factor, 1);
        }
#endif
/*
 * The above reduction is necessary. It may prove that the remainder is zero.
 * prod2 is a factorization of reduced prod1.
 */
      if (bap_is_zero_product_mpz (&prod2))
        {
          if (ddz != (struct bap_polynom_mpz * *) 0)
            {
              *ddz = B;
              BA0_RAISE_EXCEPTION2 (BAD_EXRDDZ, "%Az", (void **) ddz);
            }
          else
            BA0_RAISE_EXCEPTION (BAD_EXRDDZ);
        }
/*
 * At this stage, one makes sure that no factor of prod2 can be zero mod C.
 * Thus, one makes sure that B is not a gcd of C->decision_system.tab [k] and A.
 */
      for (j = 0; j < prod2.size; j++)
        {
          if (!bap_depend_polynom_mpz (&prod2.tab[j].factor, v))
            bad_check_algebraic_regularity_mod_regchain (&prod2.tab[j].factor,
                C, S, K, ddz);
          else
            {
              bap_initial_polynom_mpz (&init, &prod2.tab[j].factor);
              bad_check_algebraic_regularity_mod_regchain (&init, C, S, K, ddz);
              bad_Euclid_check_algebraic_regularity_mod_regchain (B,
                  &prod2.tab[j].factor, v, C, S, K, ddz);
            }
        }
    }
  ba0_restore (&M);
}

/**********************************************************************
 REG CHARACTERISTIC
 **********************************************************************/

/*
 * texinfo: bad_reg_characteristic_regchain
 * Denote @math{J} the unit ideal if @var{ideal} is zero and the ideal
 * defined by @var{ideal} otherwise. Denote @math{C} the last element 
 * of @var{tabC}. 
 *
 * Let us first consider the differential context. It is assumed that
 * @math{[C] : H_C^\infty \subset [C] : S^\infty} and that the elements 
 * of @math{S} are partially reduced with respect to @math{C}. 
 * This function stores 
 * in @var{tabC}, at indices greater than or equal to that of @math{C}, 
 * regular chains @math{A_1, \ldots, A_t} such that
 * @math{[C] : H_C^\infty \subset [C] : S^\infty 
 *      \subset [A_1] : H_{A_1}^\infty \cap \cdots \cap 
 *              [A_t] : H_{A_t}^\infty \subset J}.
 *
 * In the algebraic context, the function stores in @var{tabC},
 * at indices greater than or equal to that of @math{C}, regular chains
 * @math{A_1, \ldots, A_t} such that
 * @math{(C) : I_C^\infty \subset (C) : S^\infty 
 *      \subset (A_1) : I_{A_1}^\infty \cap \cdots \cap 
 *              (A_t) : I_{A_t}^\infty \subset J}.
 *
 * In the case @math{J} is a prime ideal then only one regular 
 * chain is computed. 
 *
 * If moreover @math{J} is minimal over the ideal defined by @math{C} 
 * then the resulting regular chain is a characteristic set of @math{J}.
 *
 * Polynomials are supposed to have coefficients in @var{K}.
 */

BAD_DLL void
bad_reg_characteristic_regchain (
    struct bad_intersectof_regchain *tabC,
    struct bap_listof_polynom_mpz *S0,
    struct bad_regchain *ideal,
    struct bad_base_field *K)
{
  struct bad_intersectof_regchain todoC;
  struct bad_quench_map map;
  struct bap_tableof_listof_polynom_mpz todoS;
  struct bap_polynom_mpz *volatile g;
  struct bap_polynom_mpz *h, *r;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  g = BAP_NOT_A_POLYNOM_mpz;    /* to avoid a warning */
  h = bap_new_polynom_mpz ();
  r = bap_new_polynom_mpz ();
/*
 * C is popped from tabC. 
 * Initialize the two stacks todoC, todoS and push the pair (C, S0)
 */
  bad_init_intersectof_regchain (&todoC);
  tabC->inter.size -= 1;
  bad_set_intersectof_regchain_regchain (&todoC,
      tabC->inter.tab[tabC->inter.size]);

  ba0_init_table ((struct ba0_table *) &todoS);
  ba0_realloc_table ((struct ba0_table *) &todoS, 1);
  todoS.tab[todoS.size++] = S0;

  bad_init_quench_map (&map, todoC.inter.tab[0]);

  while (todoC.inter.size > 0)
    {
      struct bad_regchain *C = todoC.inter.tab[todoC.inter.size - 1];
      struct bap_listof_polynom_mpz *S = todoS.tab[todoS.size - 1];

      if (todoC.inter.size != todoS.size)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
/*
 * (C, S) are the top elements of todoC, todoS
 */
      if (S == (struct bap_listof_polynom_mpz *) 0)
        {
          int old_size = todoC.inter.size;
          int n;

          if (bad_has_property_regchain (C, bad_normalized_property))
            {
/*
 * Final normalization step. It may create new regular chains or discard C
 */
              bad_set_all_properties_quench_map (&map, true);
              bad_set_property_quench_map (&map.normalized, false);
              bad_quench_and_handle_exceptions_regchain (&todoC, &map,
                  (struct bav_tableof_term *) 0, (bool *) 0, ideal, K);
            }
/*
 * n = the number of regular chains to be appended to tabC (possibly 0)
 */
          n = todoC.inter.size - old_size + 1;
          ba0_pull_stack ();
          ba0_realloc2_table ((struct ba0_table *) &tabC->inter,
              tabC->inter.size + n, (ba0_new_function *) & bad_new_regchain);
          for (int k = 0; k < n; k++)
            {
              bad_set_regchain (tabC->inter.tab[tabC->inter.size],
                  todoC.inter.tab[old_size + k - 1]);
              tabC->inter.size += 1;
            }
          ba0_push_another_stack ();
/*
 * Pop the n regular chains from todoC and 1 element from todoS
 */
          todoC.inter.size -= n;
          todoS.size -= 1;
        }
      else
        {
/*
 * Process the current inequation
 */
          BA0_TRY
          {
            bad_check_regularity_polynom_mod_regchain (S->value, C, K,
                (struct bap_polynom_mpz **) &g);
/*
 * The current inequation is regular. Next inequation
 */
            todoS.tab[todoS.size - 1] = S->next;
          }
          BA0_CATCH
          {
            struct bad_regchain *D;
            enum bad_typeof_reduction type_red;
            struct bav_variable *vg, *vh;
            ba0_int_p k;
            bool b, consider_g, consider_h;

            if (ba0_global.exception.raised == BAD_EXRNUL)
              {
/*
 * Inconsistent pair (C, S)
 */
                todoC.inter.size -= 1;
                todoS.size -= 1;
              }
            else if (ba0_global.exception.raised != BAD_EXRDDZ)
              BA0_RE_RAISE_EXCEPTION;
            else
              {
/*
 * Handle exception BAD_EXRDDZ
 */
                vg = bap_leader_polynom_mpz ((struct bap_polynom_mpz *) g);
                b = bad_is_leader_of_regchain (vg, C, &k);
                if (!b)
                  BA0_RAISE_EXCEPTION (BA0_ERRALG);

                type_red =
                    bad_defines_a_differential_ideal_regchain (C) ?
                    bad_full_reduction : bad_algebraic_reduction;

                bap_pquo_polynom_mpz (h, (bav_Idegree *) 0,
                    C->decision_system.tab[k], (struct bap_polynom_mpz *) g,
                    vg);
/*
 * consider_g means that the branch g = 0 must be considered
 * consider_h means that the branch h = 0 must be considered
 */
                if (ideal != (struct bad_regchain *) 0)
                  consider_g =
                      bad_is_a_reduced_to_zero_polynom_by_regchain ((struct
                          bap_polynom_mpz *) g, ideal, type_red);
                else if (vg == bap_leader_polynom_mpz (S->value))
                  {
                    bap_prem_polynom_mpz (r, (bav_Idegree *) 0, S->value,
                        (struct bap_polynom_mpz *) g, vg);
                    consider_g = !bap_is_zero_polynom_mpz (r);
                  }
                else
                  consider_g = true;

                vh = bap_leader_polynom_mpz (h);
                if (ideal != (struct bad_regchain *) 0)
                  consider_h =
                      bad_is_a_reduced_to_zero_polynom_by_regchain (h, ideal,
                      type_red);
                else if (vh == bap_leader_polynom_mpz (S->value))
                  {
                    bap_prem_polynom_mpz (r, (bav_Idegree *) 0, S->value, h,
                        vh);
                    consider_h = !bap_is_zero_polynom_mpz (r);
                  }
                else
                  consider_h = true;
/* 
 * Avoid the case h = 0 must be considered and g = 0 must not.
 */
                if (consider_h && !consider_g)
                  {
                    struct bap_polynom_mpz *tmp = (struct bap_polynom_mpz *) g;
                    g = h;
                    h = tmp;
                    BA0_SWAP (bool,
                        consider_g,
                        consider_h);
                  }
/* 
 * If both branches must be considered, D = a copy of C before modification
 */
                if (consider_h)
                  D = (struct bad_regchain *) bad_copy_regchain (C);

                if (consider_g)
                  {
                    int old_size = todoC.inter.size;
                    int n;
/*
 * Recall (C, S) is the top pair of (todoC, todoS)
 */
                    bap_set_polynom_mpz (C->decision_system.tab[k],
                        (struct bap_polynom_mpz *) g);

                    bad_set_all_properties_quench_map (&map, true);
                    bad_inactivate_property_quench_map (&map.normalized);
                    bad_pseudo_divided_polynom_quench_map (&map, k);

                    bad_quench_and_handle_exceptions_regchain (&todoC, &map,
                        (struct bav_tableof_term *) 0, (bool *) 0, ideal, K);
/*
 * n = the number of regular chains appended to todoC (= -1 if C is removed)
 *
 * For each of these chains, the list of inequations to process is S
 */
                    n = todoC.inter.size - old_size;
                    ba0_realloc_table ((struct ba0_table *) &todoS,
                        todoS.size + n);
                    for (int k = 0; k < n; k++)
                      todoS.tab[todoS.size + k] = S;
                    todoS.size += n;
                  }

                if (consider_h)
                  {
                    int old_size, n;
/*
 * Same as above with (D, h) instead of (C, g)
 * todoC may moreover need tp be reallocated
 */
                    ba0_realloc_table ((struct ba0_table *) &todoC.inter,
                        todoC.inter.size + 1);
                    todoC.inter.tab[todoC.inter.size++] = D;
                    bap_set_polynom_mpz (D->decision_system.tab[k], h);

                    old_size = todoC.inter.size;

                    bad_set_all_properties_quench_map (&map, true);
                    bad_inactivate_property_quench_map (&map.normalized);
                    bad_pseudo_divided_polynom_quench_map (&map, k);

                    bad_quench_and_handle_exceptions_regchain (&todoC, &map,
                        (struct bav_tableof_term *) 0, (bool *) 0, ideal, K);
/*
 * n = the number of regular chains appended to todoC (= -1 if D is removed)
 *      plus 1 because D has been appended to todoC (hence 0 if D is removed)
 *
 * For each of these chains, the list of inequations to process is S
 */
                    n = todoC.inter.size - old_size + 1;
                    ba0_realloc_table ((struct ba0_table *) &todoS,
                        todoS.size + n);
                    for (int k = 0; k < n; k++)
                      todoS.tab[todoS.size + k] = S;
                    todoS.size += n;
                  }
              }
          }
          BA0_ENDTRY;
        }
    }

  ba0_pull_stack ();
  ba0_restore (&M);
}

/*****************************************************************************
 NORMAL FORM
 *****************************************************************************/

/*
 * texinfo: bad_normal_form_polynom_mod_regchain
 * Assign to @var{NF} the normal form of @math{A} modulo the ideal 
 * @math{I} defined by @math{C} or raise an exception. 
 * The function calls @code{bad_invert_polynom_mod_regchain}. It may thus
 * fail and raise the exceptions @code{BAD_EXRNUL} or @code{BAD_EXRDDZ}.
 */

BAD_DLL void
bad_normal_form_polynom_mod_regchain (
    struct baz_ratfrac *NF,
    struct bap_polynom_mpz *A,
    struct bad_regchain *C,
    struct bap_polynom_mpz * *ddz)
{
  struct bap_product_mpz Pbar, Qbar, H, R, U, G;
  struct bad_base_field K;
  enum bad_typeof_reduction type_red;
  struct ba0_mark M;
  ba0_mpz_t *lc;

  ba0_push_another_stack ();
  ba0_record (&M);

  type_red =
      bad_defines_a_differential_ideal_regchain (C) ? bad_full_reduction :
      bad_algebraic_reduction;
/*
 * Normal forms could have been defined over a base field but not yet
 */
  bad_init_base_field (&K);
  bap_init_product_mpz (&Pbar);
  bap_init_product_mpz (&Qbar);
  bap_init_product_mpz (&R);
  bap_init_product_mpz (&H);
  bap_init_product_mpz (&U);
  bap_init_product_mpz (&G);

  bap_set_product_polynom_mpz (&Pbar, A, 1);

  while (bad_is_a_reducible_product_by_regchain (&Pbar, C, type_red,
          bad_all_derivatives_to_reduce, (ba0_int_p *) 0))
    {
      bad_reduce_product_by_regchain (&R, &H, (struct bav_tableof_term *) 0,
          &Pbar, C, type_red, bad_all_derivatives_to_reduce);
      bad_invert_product_mod_regchain (&U, &G, &H, C, &K, ddz);

      bap_mul_product_mpz (&Pbar, &U, &R);
      bap_mul_product_mpz (&Qbar, &Qbar, &G);
    }

  baz_gcd_product_mpz ((struct bap_product_mpz *) 0, &Pbar, &Qbar, &Pbar,
      &Qbar);
  ba0_pull_stack ();
  bap_expand_product_mpz (&NF->numer, &Pbar);
  bap_expand_product_mpz (&NF->denom, &Qbar);
/*
 * The next line fixes a bug. See bad/tests/nf11.c
 */
  baz_reduce_ratfrac (NF, NF);
  lc = bap_numeric_initial_polynom_mpz (&NF->denom);
  if (ba0_mpz_sgn (*lc) < 0)
    {
      bap_neg_polynom_mpz (&NF->numer, &NF->numer);
      bap_neg_polynom_mpz (&NF->denom, &NF->denom);
    }
  ba0_restore (&M);
}

/*
 * texinfo: bad_normal_form_ratfrac_mod_regchain
 * Variant of @code{bad_reduced_form_polynom_mod_regchain}
 * for rational fractions.
 */

BAD_DLL void
bad_normal_form_ratfrac_mod_regchain (
    struct baz_ratfrac *NF,
    struct baz_ratfrac *A,
    struct bad_regchain *C,
    struct bap_polynom_mpz * *ddz)
{
  struct bad_base_field K;
  struct bap_product_mpz Pbar, Qbar, H, R, U, G;
  enum bad_typeof_reduction type_red;
  struct ba0_mark M;
  ba0_mpz_t *lc;

  ba0_push_another_stack ();
  ba0_record (&M);

  type_red =
      bad_defines_a_differential_ideal_regchain (C) ? bad_full_reduction :
      bad_algebraic_reduction;
/*
 * Normal forms could have been defined over a base field but not yet
 */
  bad_init_base_field (&K);
  bap_init_product_mpz (&Pbar);
  bap_init_product_mpz (&Qbar);
  bap_init_product_mpz (&R);
  bap_init_product_mpz (&H);
  bap_init_product_mpz (&U);
  bap_init_product_mpz (&G);

  bad_invert_polynom_mod_regchain (&Pbar, &Qbar, &A->denom, C, &K, ddz);
/*
 * Then: Pbar * A.denom = Qbar mod I
 */
  bap_mul_product_polynom_mpz (&Pbar, &Pbar, &A->numer, 1);
/*
 * Pbar := Pbar * A.numer, thus, Pbar * A.denom = Qbar * A.numer mod I
 *
 * Loop invariant: Pbar * A.denom = Qbar * A.numer mod I
 */
  while (bad_is_a_reducible_product_by_regchain (&Pbar, C, type_red,
          bad_all_derivatives_to_reduce, (ba0_int_p *) 0))
    {
      bad_reduce_product_by_regchain (&R, &H, (struct bav_tableof_term *) 0,
          &Pbar, C, type_red, bad_all_derivatives_to_reduce);
      bad_invert_product_mod_regchain (&U, &G, &H, C, &K, ddz);
/*
 * H * Pbar = R mod I
 * U * H    = G mod I
 *
 * Thus U * H * Pbar = G * Pbar = U * R
 */
      bap_mul_product_mpz (&Pbar, &U, &R);
      bap_mul_product_mpz (&Qbar, &Qbar, &G);
/*
 * Then Pbar := U * R
 *      Qbar := Qbar * G
 */
    }

  baz_gcd_product_mpz ((struct bap_product_mpz *) 0, &Pbar, &Qbar, &Pbar,
      &Qbar);
  ba0_pull_stack ();
  bap_expand_product_mpz (&NF->numer, &Pbar);
  bap_expand_product_mpz (&NF->denom, &Qbar);
/*
 * The next line fixes a bug. See bad/tests/nf11.c
 */
  baz_reduce_ratfrac (NF, NF);
  lc = bap_numeric_initial_polynom_mpz (&NF->denom);
  if (ba0_mpz_sgn (*lc) < 0)
    {
      bap_neg_polynom_mpz (&NF->numer, &NF->numer);
      bap_neg_polynom_mpz (&NF->denom, &NF->denom);
    }
  ba0_restore (&M);
}

/*
 * texinfo: bad_normal_form_ratfrac_mod_intersectof_regchain
 * Compute one normal form of @var{A} for each regchain in @var{tabC} 
 * Append the normal forms to @var{tabNF}.
 */

BAD_DLL void
bad_normal_form_ratfrac_mod_intersectof_regchain (
    struct baz_tableof_ratfrac *tabNF,
    struct baz_ratfrac *A,
    struct bad_intersectof_regchain *tabC,
    struct bap_polynom_mpz * *ddz)
{
  ba0_int_p i;

  ba0_realloc2_table ((struct ba0_table *) tabNF,
      tabNF->size + tabC->inter.size, (ba0_new_function *) & baz_new_ratfrac);
  for (i = 0; i < tabC->inter.size; i++)
    {
      bad_normal_form_ratfrac_mod_regchain (tabNF->tab[tabNF->size], A,
          tabC->inter.tab[i], ddz);
      tabNF->size += 1;
    }
}

/*
 * texinfo: bad_normal_form_handling_exceptions_ratfrac_mod_regchain
 * Denote @var{C} the regular chain on the top of @var{tabC}.
 * Compute the normal form of @var{A} modulo @var{C}.
 * In most cases, the computation is successful and the resulting normal
 * form is just stored on the top of @var{tabNF}.
 * 
 * In some cases however, the computation may raise one of the exceptions
 * @code{BAD_EXRNUL} or @code{BAD_EXRDDZ}, leading to splitting cases. 
 * The regular chains produced by the splittings are stored either on
 * the top of @var{tabC} (starting from the index of @var{C}, since this
 * chain is removed in the case of splittings) or on the top of @var{tabNUL}.
 * The chains which are stored in @var{tabC} are those with respect to which normal
 * forms can eventually be computed. The chains which are stored in @var{tabNUL}
 * are those with respect to which the denominator of @var{A} is zero. 
 * 
 * At the end of the process, the radical of the ideal defined by @var{C} 
 * is equal to the radical of the ideals defined by the chains stored in
 * @var{tabC} and @var{tabNUL}.
 * 
 * For each regular chain stored in @var{tabC}, the normal form
 * of @var{A} is stored in @var{tabNF}.
 * 
 * Exceptions are handled as follows.
 * If @code{BAD_EXRNUL} is raised then the denominator of @var{A} is zero
 * modulo the current chain. This chain is stored in @var{tabNUL}.
 * If @code{BAD_EXRDDZ} is raised then 
 * @code{bad_handle_splitting_exceptions_regchain} is called in order to
 * split the current chain and the normal form computations are restarted 
 * modulo the new regular chains. 
 * The corresponding normal forms of @var{A} are stored 
 * on the top of @var{tabNF}.
 */

BAD_DLL void
bad_normal_form_handling_exceptions_ratfrac_mod_regchain (
    struct baz_tableof_ratfrac *tabNF,
    struct bad_intersectof_regchain *tabC,
    struct bad_intersectof_regchain *tabNUL,
    struct baz_ratfrac *A)
{
  struct bad_intersectof_regchain S;
  struct bad_regchain *volatile C;      /* volatile needed here */
  struct baz_ratfrac NF;
  struct bad_base_field K;
  struct bap_polynom_mpz *volatile ddz = BAP_NOT_A_POLYNOM_mpz; /* to avoid a warning */
  struct ba0_mark M;

  ba0_realloc2_table ((struct ba0_table *) tabNF, tabNF->size + 1,
      (ba0_new_function *) & baz_new_ratfrac);
/*
 * The first case is handled separately to avoid copying regchains
 */
  C = tabC->inter.tab[tabC->inter.size - 1];

  BA0_TRY
  {
    bad_normal_form_ratfrac_mod_regchain (tabNF->tab[tabNF->size], A,
        (struct bad_regchain *) C, (struct bap_polynom_mpz * *) &ddz);
    tabNF->size += 1;

    BA0_CANCEL_EXCEPTION;

    return;
  }
  BA0_CATCH
  {
    if (ba0_global.exception.raised == BAD_EXRNUL)
      {
        if (tabNUL != (struct bad_intersectof_regchain *) 0)
          bad_append_intersectof_regchain_regchain (tabNUL,
              (struct bad_regchain *) C);
        tabC->inter.size -= 1;
/*
 * Case of a prime ideal with respect to which the normal form does not exist
 * In such a case, the regular chain is moved to tabNUL
 */
        if (tabC->inter.size == 0)
          bad_clear_property_attchain (&tabC->attrib, bad_prime_ideal_property);

        return;
      }
    else if (ba0_global.exception.raised != BAD_EXRDDZ)
      BA0_RE_RAISE_EXCEPTION;
  }
  BA0_ENDTRY;
/*
 * The above computation has raised BAD_EXRDDZ
 */
  ba0_push_another_stack ();
  ba0_record (&M);

  bad_init_base_field (&K);
  bad_init_intersectof_regchain (&S);
  C = tabC->inter.tab[tabC->inter.size - 1];
  tabC->inter.size -= 1;
  bad_set_intersectof_regchain_regchain (&S, (struct bad_regchain *) C);
  baz_init_ratfrac (&NF);

  bad_handle_splitting_exceptions_regchain (&S, (struct bad_quench_map *) 0,
      (struct bav_tableof_term *) 0, (bool *) 0, (struct bap_polynom_mpz *) ddz,
      (struct bad_regchain *) 0, BAD_EXRDDZ, &K);

  while (S.inter.size > 0)
    {
      BA0_TRY
      {
        C = S.inter.tab[S.inter.size - 1];
        bad_normal_form_ratfrac_mod_regchain (&NF, A, (struct bad_regchain *) C,
            (struct bap_polynom_mpz * *) &ddz);

        BA0_CANCEL_EXCEPTION;

        ba0_pull_stack ();
        bad_append_intersectof_regchain_regchain (tabC,
            (struct bad_regchain *) C);
        ba0_realloc2_table ((struct ba0_table *) tabNF,
            tabNF->size + S.inter.size, (ba0_new_function *) & baz_new_ratfrac);
        baz_set_ratfrac (tabNF->tab[tabNF->size++], &NF);
        ba0_push_another_stack ();

        S.inter.size -= 1;
      }
      BA0_CATCH
      {
        if (ba0_global.exception.raised == BAD_EXRNUL)
          {
            if (tabNUL != (struct bad_intersectof_regchain *) 0)
              {
                ba0_pull_stack ();
                bad_append_intersectof_regchain_regchain (tabNUL,
                    (struct bad_regchain *) C);
                ba0_push_another_stack ();
              }

            S.inter.size -= 1;
          }
        else if (ba0_global.exception.raised == BAD_EXRDDZ)
          {
            bad_handle_splitting_exceptions_regchain (&S,
                (struct bad_quench_map *) 0, (struct bav_tableof_term *) 0,
                (bool *) 0, (struct bap_polynom_mpz *) ddz,
                (struct bad_regchain *) 0, BAD_EXRDDZ, &K);
          }
        else
          BA0_RE_RAISE_EXCEPTION;
      }
      BA0_ENDTRY;
    }

  ba0_pull_stack ();
  ba0_restore (&M);
}
