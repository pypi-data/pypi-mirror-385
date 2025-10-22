#include "bap_polynom_mpq.h"
#include "bap_add_polynom_mpq.h"
#include "bap_mul_polynom_mpq.h"
#include "bap_prem_polynom_mpq.h"
#include "bap_Ducos_mpq.h"

#define BAD_FLAG_mpq

/*
   This a C translation of the AXIOM functions of Lionel Ducos
   (file {\tt prs.spad}). Functions suffixed by~$2$ compute single values.
   Functions suffixed by~$3$ apply to vectors.
*/

/*
 * texinfo: bap_nsr2_Ducos_polynom_mpq
 * Assign to @var{R} the next subresultant of @var{P} and @var{Q}
 * with respect to @var{v}.
 * The polynomial @var{P} has positive degree in @var{v} but @var{Q}
 * and @var{H} do not necessarily. The variable @var{v} must be greater 
 * than or equal to all the variables occurring in the polynomials.
 * Function @code{next_sousResultant2} of  Lionel Ducos.
 */

BAP_DLL void
bap_nsr2_Ducos_polynom_mpq (
    struct bap_polynom_mpq *R,
    struct bap_polynom_mpq *P,
    struct bap_polynom_mpq *Q,
    struct bap_polynom_mpq *H,
    struct bap_polynom_mpq *s,
    struct bav_variable *v)
{
  struct bap_polynom_mpq lcP, lcQ, lcH, PP, QQ, HH, A, coeff, reductum, bunk;
  bav_Idegree degP, degQ, i;
  struct bav_term T;
  struct bav_rank rg;
  struct ba0_mark M;
/*
>   next_sousResultant2(P : polR, Q : polR, Z : polR, s : R) : polR ==
    Z is denoted H here
*/
  ba0_push_another_stack ();
  ba0_record (&M);

  rg.var = v;
  rg.deg = 1;
  bav_init_term (&T);
  bav_set_term_rank (&T, &rg);

/*
>      (lcP, c, se) := (LC(P), LC(Q), LC(Z))
>      (d, e) := (degree(P), degree(Q))
>      (P, Q, H) := (reductum(P), reductum(Q), - reductum(Z))
>      A : polR := coefficient(P, e) * H
*/
  bap_init_readonly_polynom_mpq (&lcP);
  bap_init_readonly_polynom_mpq (&lcQ);
  bap_init_readonly_polynom_mpq (&lcH);

  bap_init_readonly_polynom_mpq (&PP);
  bap_init_readonly_polynom_mpq (&QQ);
  bap_init_polynom_mpq (&HH);

  bap_init_polynom_mpq (&A);
  bap_init_polynom_mpq (&bunk);
  bap_init_readonly_polynom_mpq (&coeff);
  bap_init_readonly_polynom_mpq (&reductum);

  bap_initial_and_reductum_polynom_mpq (&lcP, &PP, P);
  bap_initial_and_reductum2_polynom_mpq (&lcQ, &QQ, Q, v);
  bap_initial_and_reductum2_polynom_mpq (&lcH, &coeff, H, v);
  bap_neg_polynom_mpq (&HH, &coeff);

  degP = bap_leading_degree_polynom_mpq (P);
  degQ = bap_degree_polynom_mpq (Q, v);

  bap_coeff2_polynom_mpq (&coeff, &PP, v, degQ);
  bap_mul_polynom_mpq (&A, &HH, &coeff);
/*
>      for i in e+1..d-1 repeat
>         H := if degree(H) = e-1 then
>                 X * reductum(H) - ((LC(H) * Q) exquo c)::polR
>              else
>                 X * H
>         -- H = s_e * X^i mod S_d-1
>         A := coefficient(P, i) * H + A
*/
  rg.deg = 1;
  for (i = degQ + 1; i < degP; i++)
    {
      if (bap_degree_polynom_mpq (&HH, v) == degQ - 1)
        {
          bap_initial_and_reductum2_polynom_mpq (&coeff, &reductum, &HH, v);
          bap_mul_polynom_mpq (&bunk, &QQ, &coeff);
          bap_exquo_polynom_mpq (&bunk, &bunk, &lcQ);
          bap_submulrk_polynom_mpq (&HH, &reductum, &rg, &bunk);
        }
      else
        bap_mul_polynom_term_mpq (&HH, &HH, &T);
      bap_coeff2_polynom_mpq (&coeff, &PP, v, i);
      bap_mul_polynom_mpq (&bunk, &HH, &coeff);
      bap_add_polynom_mpq (&A, &bunk, &A);
    }
/*
>      while degree(P) >= e repeat P := reductum(P)
*/
  while (bap_degree_polynom_mpq (&PP, v) >= degQ)
    bap_initial_and_reductum2_polynom_mpq ((struct bap_polynom_mpq *) 0,
        &PP, &PP, v);
/*
>      A := A + se * P            --  A = s_e * reductum(P_0)       mod S_d-1
>      A := (A exquo lcP)::polR   --  A = s_e * reductum(S_d) / s_d mod S_d-1
*/
  bap_mul_polynom_mpq (&bunk, &PP, &lcH);
  bap_add_polynom_mpq (&A, &A, &bunk);
  bap_exquo_polynom_mpq (&A, &A, &lcP);
/*
>      A := if degree(H) = e-1 then
>              c * (X * reductum(H) + A) - LC(H) * Q
>           else
>              c * (X * H + A)
>      A := (A exquo s)::polR                    -- A = +/- S_e-1
*/
  if (bap_degree_polynom_mpq (&HH, v) == degQ - 1)
    {
      bap_initial_and_reductum2_polynom_mpq (&coeff, &HH, &HH, v);
      bap_mul_polynom_mpq (&bunk, &QQ, &coeff);
      rg.deg = 1;
      bap_addmulrk_polynom_mpq (&A, &HH, &rg, &A);
      bap_mul_polynom_mpq (&A, &A, &lcQ);
      bap_sub_polynom_mpq (&A, &A, &bunk);
    }
  else
    {
      rg.deg = 1;
      bap_addmulrk_polynom_mpq (&A, &HH, &rg, &A);
      bap_mul_polynom_mpq (&A, &A, &lcQ);
    }
  bap_exquo_polynom_mpq (&A, &A, s);
  ba0_pull_stack ();
/*  
>     return (if odd?(d-e) then A else - A)
*/
  if ((degP - degQ) % 2 == 1)
    bap_set_polynom_mpq (R, &A);
  else
    bap_neg_polynom_mpq (R, &A);
  ba0_restore (&M);
}

/* Function {\tt next_sousResultant3} of Lionel Ducos. */

/*
 * texinfo: bap_nsr3_Ducos_polynom_mpq
 * Function @code{next_sousResultant3} of Lionel Ducos.
 */

BAP_DLL void
bap_nsr3_Ducos_polynom_mpq (
    struct bap_tableof_polynom_mpq *VR,
    struct bap_tableof_polynom_mpq *VP,
    struct bap_tableof_polynom_mpq *VQ,
    struct bap_polynom_mpq *s,
    struct bap_polynom_mpq *ss,
    struct bav_variable *v)
{
  struct bap_polynom_mpq lcP, lcQ, bunk, coeff, coegg, r, rr, quot;
  struct ba0_table VPP;
  struct bap_polynom_mpq *P, *Q;
  bav_Idegree e, delta;
  ba0_int_p i;
  struct bav_rank rg;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  rg.var = v;

  bap_init_polynom_mpq (&bunk);
  bap_init_readonly_polynom_mpq (&coeff);
  bap_init_readonly_polynom_mpq (&coegg);

  ba0_init_table (&VPP);
  ba0_realloc2_table ((struct ba0_table *) &VPP, VP->size,
      (ba0_new_function *) & bap_new_polynom_mpq);
  VPP.size = VP->size;
/*
    next_sousResultant3(VP : Vector(polR), VQ : Vector(polR), s : R, ss : R) :
                                                      Vector(polR) ==
    -- P ~ S_d,  Q = S_d-1,  s = lc(S_d),  ss = lc(S_e)
       (P, Q) := (VP.1, VQ.1)
*/
  P = VP->tab[0];
  Q = VQ->tab[0];
/*
       (lcP, c) := (LC(P), LC(Q))
       ici c est nomme lcQ.
*/
  bap_init_readonly_polynom_mpq (&lcP);
  bap_init_readonly_polynom_mpq (&lcQ);
  bap_initial2_polynom_mpq (&lcP, P, v);
  bap_initial2_polynom_mpq (&lcQ, Q, v);
/*
       e : NNI := degree(Q)
       if one?(delta := degree(P) - e) then
*/
  e = bap_degree_polynom_mpq (Q, v);
  delta = bap_degree_polynom_mpq (P, v) - e;
  if (delta == 1)
    {
      bap_coeff2_polynom_mpq (&coeff, P, v, e);
      bap_coeff2_polynom_mpq (&coegg, Q, v, e - 1);
      for (i = 0; i < VP->size; i++)
        {
/*
         VP := c * VP - coefficient(P, e) * VQ
*/
          bap_mul_polynom_mpq (&bunk, &coeff, VQ->tab[i]);
          bap_mul_polynom_mpq (VPP.tab[i], VP->tab[i], &lcQ);
          bap_sub_polynom_mpq (VPP.tab[i], VPP.tab[i], &bunk);
/*
         VP := VP exquo lcP
*/
          bap_exquo_polynom_mpq (VPP.tab[i], VPP.tab[i], &lcP);
/*
	         VP := c * (VP - X * VQ) + coefficient(Q, (e-1)::NNI) * VQ
*/
          rg.deg = 1;
          bap_submulrk_polynom_mpq (VPP.tab[i], VQ->tab[i], &rg, VPP.tab[i]);
          bap_mul_polynom_mpq (VPP.tab[i], VPP.tab[i], &lcQ);
          bap_mul_polynom_mpq (&bunk, VQ->tab[i], &coegg);
          bap_sub_polynom_mpq (VPP.tab[i], &bunk, VPP.tab[i]);
/*
         VP := VP exquo s
*/
          bap_exquo_polynom_mpq (VPP.tab[i], VPP.tab[i], s);
        }
    }
  else
    {
/*
       else                                    -- algorithm of Lickteig - Roy
         (r, rr) := (s * lcP, ss * c)
*/
      bap_init_polynom_mpq (&r);
      bap_init_polynom_mpq (&rr);
      bap_mul_polynom_mpq (&r, s, &lcP);
      bap_mul_polynom_mpq (&rr, ss, &lcQ);
/*
         divid := divide(rr * P, Q)
*/
      bap_mul_polynom_mpq (&bunk, &rr, P);
      bap_init_polynom_mpq (&quot);
      bap_rem_polynom_mpq (&quot, VPP.tab[0], &bunk, Q, v);
/*
         VP.1 := (divid.remainder exquo r)::polR
*/
      bap_exquo_polynom_mpq (VPP.tab[0], VPP.tab[0], &r);
/*
         for i in 2..#VP repeat
*/
      for (i = 1; i < VP->size; i++)
        {
/*
           VP.i := rr * VP.i - VQ.i * divid.quotient
*/
          bap_mul_polynom_mpq (VPP.tab[i], &rr, VP->tab[i]);
          bap_mul_polynom_mpq (&bunk, VQ->tab[i], &quot);
          bap_sub_polynom_mpq (VPP.tab[i], VPP.tab[i], &bunk);
/*
           VP.i := (VP.i exquo r)::polR
*/
          bap_exquo_polynom_mpq (VPP.tab[i], VPP.tab[i], &r);
        }
    }
  ba0_pull_stack ();
  for (i = 0; i < VR->size; i++)
    bap_set_polynom_mpq (VR->tab[i], VPP.tab[i]);
  ba0_restore (&M);
}

/*
 * Function {\tt Lazard} of Lionel Ducos.
 *
 * R := x^n/y^(n-1)
 *
 * Alternating multiplications and divisions.
 */

/*
 * texinfo: bap_muldiv_Lazard_polynom_mpq
 * Function @code{Lazard} of Lionel Ducos.
 * Assign @math{x^n / y^{(n-1)}} to @var{R} by alternating
 * multiplications and divisions.
 */

BAP_DLL void
bap_muldiv_Lazard_polynom_mpq (
    struct bap_polynom_mpq *R,
    struct bap_polynom_mpq *x,
    struct bap_polynom_mpq *y,
    bav_Idegree n)
{
  struct bap_polynom_mpq c;
  bav_Idegree a;
  struct ba0_mark M;
/*
>   Lazard(x : R, y : R, n : NNI) : R ==
>      zero?(n) => error("Lazard$PRS : n = 0")
>      one?(n) => x
*/
  if (n == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  if (n == 1)
    {
      if (R != x)
        bap_set_polynom_mpq (R, x);
    }
  else
    {
/*
>      a : NNI := 1
>      while n >= (b := 2*a) repeat a := b
*/
      ba0_push_another_stack ();
      ba0_record (&M);

      for (a = 1; n >= 2 * a; a *= 2);
/*
   Comme n >= 2, on est sur que a > 1 et donc qu'on entre une fois
   dans la boucle. J'ai deplie la premiere iteration.
>      c : R := x
>      n := (n - a)::NNI
>      repeat                    --  c = x**i / y**(i-1),  i=n_0 quo a,  a=2**?
>         one?(a) => return c
>         a := a quo 2
>         c := ((c * c) exquo y)::R
>         if n >= a then ( c := ((c * x) exquo y)::R ; n := (n - a)::NNI )
*/
      n = n - a;
      a /= 2;
      bap_init_polynom_mpq (&c);
      bap_mul_polynom_mpq (&c, x, x);
      bap_exquo_polynom_mpq (&c, &c, y);
      if (n >= a)
        {
          bap_mul_polynom_mpq (&c, &c, x);
          bap_exquo_polynom_mpq (&c, &c, y);
          n = n - a;
        }
      while (a != 1)
        {
          a /= 2;
          bap_mul_polynom_mpq (&c, &c, &c);
          bap_exquo_polynom_mpq (&c, &c, y);
          if (n >= a)
            {
              bap_mul_polynom_mpq (&c, &c, x);
              bap_exquo_polynom_mpq (&c, &c, y);
              n = n - a;
            }
        }
      ba0_pull_stack ();
      bap_set_polynom_mpq (R, &c);
      ba0_restore (&M);
    }
}

/*
 * Function {\tt Lazard2} of Lionel Ducos.
 * Set $R$ to $\displaystyle{F\,\left(\frac x y\right)^{(n-1)}}$.
 */

/*
 * texinfo: bap_muldiv2_Lazard_polynom_mpq
 * Function @code{Lazard2} of Lionel Ducos.
 * Assign @math{F\,(x/y)^{(n-1)}} to @math{R}.
 */

BAP_DLL void
bap_muldiv2_Lazard_polynom_mpq (
    struct bap_polynom_mpq *R,
    struct bap_polynom_mpq *F,
    struct bap_polynom_mpq *x,
    struct bap_polynom_mpq *y,
    bav_Idegree n)
{
  struct bap_polynom_mpq A;
  struct ba0_mark M;
/*
>   Lazard2(F : polR, x : R, y : R, n : NNI) : polR ==
>      zero?(n) => error("Lazard2$PRS : n = 0")
>      one?(n) => F
*/
  if (n == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  if (n == 1)
    {
      if (R != F)
        bap_set_polynom_mpq (R, F);
    }
  else
    {
/*
>      x := Lazard(x, y, (n-1)::NNI)
>      return ((x * F) exquo y)::polR
*/
      ba0_push_another_stack ();
      ba0_record (&M);
      bap_init_polynom_mpq (&A);
      bap_muldiv_Lazard_polynom_mpq (&A, x, y, n - 1);
      bap_mul_polynom_mpq (&A, &A, F);
      ba0_pull_stack ();
      bap_exquo_polynom_mpq (R, &A, y);
      ba0_restore (&M);
    }
}

/*
 * VR := VP * (x/y)^(n-1)
 */

/*
 * texinfo: bap_muldiv3_Lazard_polynom_mpq
 * Assign the array 
 * @math{x^{(n-1)}\,VP\,y^{(n-1)}} 
 * to @var{VR}.
 */

BAP_DLL void
bap_muldiv3_Lazard_polynom_mpq (
    struct bap_tableof_polynom_mpq *VR,
    struct bap_tableof_polynom_mpq *VP,
    struct bap_polynom_mpq *x,
    struct bap_polynom_mpq *y,
    bav_Idegree n)
{
  struct bap_polynom_mpq z, t;
  ba0_int_p i;
  struct ba0_mark M;
/*
    Lazard3(V : Vector(polR), x : R, y : R, n : NNI) : Vector(polR) ==
    -- computes x**(n-1) * V / y**(n-1)
       zero?(n) => error("Lazard2$prs : n = 0")
       one?(n) => V
       x := Lazard(x, y, (n-1)::NNI)
       return ((x * V) exquo y)
*/
  if (n == 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  if (n == 1)
    {
      if (VR != VP)
        {
          for (i = 0; i < VR->size; i++)
            bap_set_polynom_mpq (VR->tab[i], VP->tab[i]);
        }
    }
  else
    {
      ba0_push_another_stack ();
      ba0_record (&M);
      bap_init_polynom_mpq (&z);
      bap_init_polynom_mpq (&t);
      bap_muldiv_Lazard_polynom_mpq (&z, x, y, n - 1);
      for (i = 0; i < VR->size; i++)
        {
          bap_mul_polynom_mpq (&t, &z, VP->tab[i]);
          ba0_pull_stack ();
          bap_exquo_polynom_mpq (VR->tab[i], &t, y);
          ba0_push_another_stack ();
        }
      ba0_pull_stack ();
      ba0_restore (&M);
    }
}


/*
 * Function algo_new of Lionel Ducos
 * Polynomials P and Q have nonzero degree in v
 * v is their leading variable
 */

static void
algo_new_mpq (
    struct bap_polynom_mpq *R,
    struct bap_polynom_mpq *P,
    struct bap_polynom_mpq *Q,
    struct bav_variable *v)
{
  struct bap_polynom_mpq coeff, s, Z;
  struct bap_polynom_mpq *A, *B;
  bav_Idegree delta;
  struct ba0_mark M;

  if (!bap_depend_polynom_mpq (P, v) || !bap_depend_polynom_mpq (Q, v))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
/*
>   algo_new(P : polR, Q : polR) : R ==
>      delta : NNI := (degree(P) - degree(Q))::NNI
>      s : R := LC(Q)**delta
>      (P, Q) := (Q, pseudoRemainder(P, -Q))
*/
  ba0_push_another_stack ();
  ba0_record (&M);

  bap_init_readonly_polynom_mpq (&coeff);
  bap_init_polynom_mpq (&s);
  bap_init_polynom_mpq (&Z);

  bap_initial2_polynom_mpq (&coeff, Q, v);
  delta =
      bap_leading_degree_polynom_mpq (P) - bap_degree_polynom_mpq (Q, v);
  bap_pow_polynom_mpq (&s, &coeff, delta);

  A = bap_new_polynom_mpq ();
  B = bap_new_polynom_mpq ();

  bap_set_polynom_mpq (A, Q);

  bap_prem_polynom_mpq (B, (bav_Idegree *) 0, P, Q, v);
  bap_neg_polynom_mpq (B, B);
/*
>      repeat
>         -- P = S_c-1 (except the first turn : P ~ S_c-1),
>         -- Q = S_d-1,  s = lc(S_d)
>         zero?(Q) => return 0
>         delta := (degree(P) - degree(Q))::NNI
>         Z : polR := Lazard2(Q, LC(Q), s, delta)
>         -- Z = S_e ~ S_d-1
>         zero?(degree(Z)) => return LC(Z)
>         (P, Q) := (Q, next_sousResultant2(P, Q, Z, s))
>         s := LC(Z)
*/
  for (;;)
    {
      if (bap_is_zero_polynom_mpq (B))
        {
          ba0_pull_stack ();
          bap_set_polynom_zero_mpq (R);
          break;
        }
/*
   Beware to B which may possibly not depend on v
*/
      delta =
          bap_leading_degree_polynom_mpq (A) - bap_degree_polynom_mpq (B,
          v);
      bap_initial2_polynom_mpq (&coeff, B, v);
      bap_muldiv2_Lazard_polynom_mpq (&Z, B, &coeff, &s, delta);
      if (!bap_depend_polynom_mpq (&Z, v))
        {
          ba0_pull_stack ();
          bap_set_polynom_mpq (R, &Z);
          break;
        }
      bap_nsr2_Ducos_polynom_mpq (A, A, B, &Z, &s, v);
      BA0_SWAP (struct bap_polynom_mpq *,
          A,
          B);
      bap_lcoeff_polynom_mpq (&s, &Z, v);
    }
  ba0_restore (&M);
}

/*
 * texinfo: bap_resultant2_Ducos_polynom_mpq
 * Assign to @var{R} the resultant w.r.t. @var{v} of @var{P} and @var{Q}.
 * Function @code{resultant} of Lionel Ducos.
 */

BAP_DLL void
bap_resultant2_Ducos_polynom_mpq (
    struct bap_product_mpq *R,
    struct bap_polynom_mpq *P,
    struct bap_polynom_mpq *Q,
    struct bav_variable *v)
{
  if (bap_is_zero_polynom_mpq (P) || bap_is_zero_polynom_mpq (Q))
    bap_set_product_zero_mpq (R);
  else
    {
      struct bap_polynom_mpq *pmQ;
      bav_Idegree degP, degQ;
      struct ba0_mark M;

      ba0_push_another_stack ();
      ba0_record (&M);

      degP = bap_degree_polynom_mpq (P, v);
      degQ = bap_degree_polynom_mpq (Q, v);

      if (degP < degQ)
        {
          BA0_SWAP (struct bap_polynom_mpq *,
              P,
              Q);
          BA0_SWAP (bav_Idegree, degP, degQ);
          if (degP % 2 == 1 && degQ % 2 == 1)
            {
              pmQ = bap_new_polynom_mpq ();
              bap_neg_polynom_mpq (pmQ, Q);
            }
          else
            pmQ = Q;
        }
      if (degQ == 0)
        {
          ba0_pull_stack ();
          bap_set_product_polynom_mpq (R, pmQ, degP);
        }
      else
        {
          struct bap_polynom_mpq tmp;

          bap_init_polynom_mpq (&tmp);
          algo_new_mpq (&tmp, P, Q, v);

          ba0_pull_stack ();
          bap_set_product_polynom_mpq (R, &tmp, 1);
        }
      ba0_restore (&M);
    }
}

/*
 * Variant of {\tt lastSubResultantEuclidean} of Lionel Ducos.
 * The array $\mbox{\em VR}$ has size between $1$ and $3$.
 * In the case the size is $3$, sets $\mbox{\em VR}$ to the array
 * $(G,\,U,\,V)$ where $G$ is the last nonzero subresultant of $P$ and $Q$
 * and where $U$ and $V$ satisfy 
 * $$G = P\,U + Q\,V.$$
 * If the size is $2$, only computes $(G,\,U)$. 
 * If the size is $1$ only computes $(G)$.
 */

/*
 * texinfo: bap_lsr3_Ducos_polynom_mpq
 * Variant of @code{lastSubResultantEuclidean} of Lionel Ducos.
 * The array @var{VR}  has size between @math{1} and @math{3}.
 * In the case the size is @math{3} assigns to @var{VR} the array
 * @math{(G,\,U,\,V)} where @math{G} is the last nonzero subresultant of 
 * @var{P} and @var{Q} and where @var{U} and @var{V} satisfy
 * @math{G = P\,U + Q\,V}.
 * If the size is @math{2} only computes @math{(G,\,U)}.
 * If the size is @math{1} only computes @math{(G)}.
 */

BAP_DLL void
bap_lsr3_Ducos_polynom_mpq (
    struct bap_tableof_polynom_mpq *VR,
    struct bap_polynom_mpq *P,
    struct bap_polynom_mpq *Q,
    struct bav_variable *v)
{
  struct bap_tableof_polynom_mpq VZ;
  struct bap_tableof_polynom_mpq *VP, *VQ;
  struct bap_polynom_mpq s, coeff;
  bav_Idegree degP, degQ, degZ;
  bool b, perm;
  ba0_int_p i;
  struct ba0_mark M;

/*
    lastSubResultantEuclidean(P : polR, Q : polR) :
                    Record(coef1 : polR, coef2 : polR, subResultant : polR) ==
       zero?(Q) or zero?(P) => construct(0::polR, 0::polR, 0::polR)
*/
  if (bap_is_zero_polynom_mpq (P) || bap_is_zero_polynom_mpq (Q))
    {
      for (i = 0; i < VR->size; i++)
        bap_set_polynom_zero_mpq (VR->tab[i]);
      return;
    }
/*
       if degree(P) < degree(Q) then
          l := lastSubResultantEuclidean(Q, P)
          return construct(l.coef2, l.coef1, l.subResultant)
*/
  degP = bap_degree_polynom_mpq (P, v);
  degQ = bap_degree_polynom_mpq (Q, v);
  if (degP < degQ)
    {
      BA0_SWAP (struct bap_polynom_mpq *,
          P,
          Q);
      BA0_SWAP (bav_Idegree, degP, degQ);
      perm = true;
    }
  else
    perm = false;
/*
       if zero?(degree(Q)) then
          degP : NNI := degree(P)
          zero?(degP) =>
              error("lastSubResultantEuclidean$PRS : bav_constant_symbol polynomials")
          s : R := LC(Q)**(degP-1)::NNI
          return construct(0::polR, s::polR, s * Q)
*/
  if (degQ == 0)
    {
      if (degP == 0)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
      if (VR->size == 1)
        bap_pow_polynom_mpq (VR->tab[0], Q, degP);
      else if (VR->size == 2)
        {
          bap_pow_polynom_mpq (VR->tab[0], Q, degP);
          if (perm)
            bap_pow_polynom_mpq (VR->tab[1], Q, degP - 1);
          else
            bap_set_polynom_zero_mpq (VR->tab[1]);
        }
      else
        {
          if (perm)
            {
              bap_pow_polynom_mpq (VR->tab[1], Q, degP - 1);
              bap_mul_polynom_mpq (VR->tab[0], VR->tab[1], Q);
              bap_set_polynom_zero_mpq (VR->tab[2]);
            }
          else
            {
              bap_pow_polynom_mpq (VR->tab[2], Q, degP - 1);
              bap_mul_polynom_mpq (VR->tab[0], VR->tab[2], Q);
              bap_set_polynom_zero_mpq (VR->tab[1]);
            }
        }
      return;
    }
/*
       s : R := LC(Q)**(degree(P) - degree(Q))::NNI
       VP : Vector(polR) := [Q, 0::polR, 1::polR]
       pdiv := pseudoDivide(P, -Q)
       VQ : Vector(polR) := [pdiv.remainder, pdiv.coef::polR, pdiv.quotient]
       VZ : Vector(polR) := copy(VP)
*/
  ba0_push_another_stack ();
  ba0_record (&M);

  bap_init_readonly_polynom_mpq (&coeff);
  bap_init_polynom_mpq (&s);
  VP = (struct bap_tableof_polynom_mpq *) ba0_new_table ();
  VQ = (struct bap_tableof_polynom_mpq *) ba0_new_table ();
  ba0_init_table ((struct ba0_table *) &VZ);
  ba0_realloc2_table ((struct ba0_table *) VP, VR->size,
      (ba0_new_function *) & bap_new_polynom_mpq);
  ba0_realloc2_table ((struct ba0_table *) VQ, VR->size,
      (ba0_new_function *) & bap_new_polynom_mpq);
  ba0_realloc2_table ((struct ba0_table *) &VZ, VR->size,
      (ba0_new_function *) & bap_new_polynom_mpq);
  VP->size = VR->size;
  VQ->size = VR->size;
  VZ.size = VR->size;

  bap_initial2_polynom_mpq (&coeff, Q, v);
  bap_pow_polynom_mpq (&s, &coeff, degP - degQ);
  bap_set_polynom_mpq (VP->tab[0], Q);
  bap_set_polynom_mpq (VZ.tab[0], Q);
  if (VP->size == 2)
    {
      if (perm)
        {
          bap_set_polynom_one_mpq (VP->tab[1]);
          bap_set_polynom_one_mpq (VZ.tab[1]);
        }
    }
  else if (VP->size == 3)
    {
      if (perm)
        {
          bap_set_polynom_one_mpq (VP->tab[1]);
          bap_set_polynom_one_mpq (VZ.tab[1]);
        }
      else
        {
          bap_set_polynom_one_mpq (VP->tab[2]);
          bap_set_polynom_one_mpq (VZ.tab[2]);
        }
    }

  b = Q->readonly;
  Q->readonly = false;
  bap_neg_polynom_mpq (Q, Q);
  if (VQ->size == 1)
    bap_pseudo_division_polynom_mpq ((struct bap_polynom_mpq *) 0,
        VQ->tab[0], (bav_Idegree *) 0, P, Q, v);
  else if (VQ->size == 2)
    {
      if (perm)
        {
          bap_pseudo_division_polynom_mpq (VQ->tab[1], VQ->tab[0],
              (bav_Idegree *) 0, P, Q, v);
        }
      else
        {
          bav_Idegree e;

          bap_pseudo_division_polynom_mpq ((struct bap_polynom_mpq *) 0,
              VQ->tab[0], &e, P, Q, v);
          bap_initial2_polynom_mpq (&coeff, Q, v);
          bap_pow_polynom_mpq (VQ->tab[1], &coeff, e);
        }
    }
  else
    {
      bav_Idegree e;

      if (perm)
        {
          bap_pseudo_division_polynom_mpq (VQ->tab[1], VQ->tab[0], &e, P, Q,
              v);
          bap_initial2_polynom_mpq (&coeff, Q, v);
          bap_pow_polynom_mpq (VQ->tab[2], &coeff, e);
        }
      else
        {
          bap_pseudo_division_polynom_mpq (VQ->tab[2], VQ->tab[0], &e, P, Q,
              v);
          bap_initial2_polynom_mpq (&coeff, Q, v);
          bap_pow_polynom_mpq (VQ->tab[1], &coeff, e);
        }
    }
  bap_neg_polynom_mpq (Q, Q);
  Q->readonly = b;
/*
       repeat
          --  VZ.1 = S_d,  VP.1 = S_{c-1},  VQ.1 = S_{d-1},  s = lc(S_d)
          --  S_{c-1} = VP.2 P_0 + VP.3 Q_0
          --  S_{d-1} = VQ.2 P_0 + VQ.3 Q_0
          --  S_d     = VZ.2 P_0 + VZ.3 Q_0
          (Q, Z) := (VQ.1, VZ.1)
          zero?(Q) => return construct(VZ.2, VZ.3, VZ.1)
          VZ := Lazard3(VQ, LC(Q), s, (degree(Z) - degree(Q))::NNI)
          zero?(degree(Q)) => return construct(VZ.2, VZ.3, VZ.1)
          ss : R := LC(VZ.1)
          (VP, VQ) := (VQ, next_sousResultant3(VP, VQ, s, ss))
          s := ss
*/
  for (;;)
    {
      if (bap_is_zero_polynom_mpq (VQ->tab[0]))
        break;
      bap_initial2_polynom_mpq (&coeff, VQ->tab[0], v);
      degQ = bap_degree_polynom_mpq (VQ->tab[0], v);
      degZ = bap_degree_polynom_mpq (VZ.tab[0], v);
      bap_muldiv3_Lazard_polynom_mpq (&VZ, VQ, &coeff, &s, degZ - degQ);
      if (degQ == 0)
        break;
      bap_initial2_polynom_mpq (&coeff, VZ.tab[0], v);
      bap_nsr3_Ducos_polynom_mpq (VP, VP, VQ, &s, &coeff, v);
      BA0_SWAP (struct bap_tableof_polynom_mpq *,
          VP,
          VQ);
      bap_set_polynom_mpq (&s, &coeff);
    }
  ba0_pull_stack ();
  for (i = 0; i < VR->size; i++)
    bap_set_polynom_mpq (VR->tab[i], VZ.tab[i]);
  ba0_restore (&M);
  return;
}

#undef BAD_FLAG_mpq
