#include "bap_geobucket_mint_hp.h"
#include "bap_creator_mint_hp.h"
#include "bap_itermon_mint_hp.h"
#include "bap_polyspec_mint_hp.h"
#include "bap_itermon_mpz.h"
#include "bap_add_polynom_mint_hp.h"
#include "bap_mul_polynom_mint_hp.h"
#include "bap_prem_polynom_mint_hp.h"
#include "bap_invert_mint_hp.h"

/*
 * texinfo: bap_polynom_mpq_to_mint_hp
 * Assign @var{B} to @var{A} modulo @code{ba0_mint_hp_module}.
 */

BAP_DLL void
bap_polynom_mpq_to_mint_hp (
    struct bap_polynom_mint_hp *A,
    struct bap_polynom_mpq *B)
{
  A = (struct bap_polynom_mint_hp *) 0;
  B = (struct bap_polynom_mpq *) 0;
  BA0_RAISE_EXCEPTION (BA0_ERRNYP);
}

/*
 * texinfo: bap_polynom_mpz_to_mint_hp
 * Assign to @var{R} the polynomial @var{A} modulo 
 * @code{ba0_mint_hp_module}.
 */

BAP_DLL void
bap_polynom_mpz_to_mint_hp (
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mpz *A)
{
  struct bap_itermon_mpz iter;
  struct bap_creator_mint_hp crea;
  struct bap_polynom_mint_hp *P;
/*
    ba0_mpz_t bunk, module;
*/
  ba0_mint_hp c;
  struct bav_term T;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);

  bav_init_term (&T);
  bav_set_term (&T, &A->total_rank);
/*
    ba0_mpz_init_set_si (module, ba0_mint_hp_module);
    ba0_mpz_init (bunk);
*/
  P = bap_new_polynom_mint_hp ();
  bap_begin_creator_mint_hp (&crea, P, &T, bap_approx_total_rank,
      bap_nbmon_polynom_mpz (A));

  bap_begin_itermon_mpz (&iter, A);
  while (!bap_outof_itermon_mpz (&iter))
    {
/*
	mpz_mod (bunk, *bap_coeff_itermon_mpz (&iter), module);
	c = (ba0_mint_hp)mpz_get_ui (bunk);
*/
      c = (ba0_mint_hp) ba0_mpz_fdiv_ui (*bap_coeff_itermon_mpz (&iter),
          ba0_mint_hp_module);
      if (c != 0)
        {
          bap_term_itermon_mpz (&T, &iter);
          bap_write_creator_mint_hp (&crea, &T, c);
        }
      bap_next_itermon_mpz (&iter);
    }
  bap_close_creator_mint_hp (&crea);
  ba0_pull_stack ();
  bap_set_polynom_mint_hp (R, P);
  ba0_restore (&M);
}

/*-
\paragraph{void bap_random_eval_polynom_mpz_to_mint_hp 
	(struct bap_polynom_mint_hp * R, struct bap_polynom_mpz * A, ba0_unary_predicate* f)}
Sets
$R$ to $A \mod (p, x_k - \alpha_k)$ where~$p$ 
is {\em mint_hp_module}, the
$x_k$ are the the derivatives occurring in~$A$ which satisfy~$f$ and the
$\alpha_k = g (p, x_k)$ are ``random'' values which are functions of 
$p$ and $x_k$
-*/

/*
 * texinfo: bap_random_eval_polynom_mpz_to_mint_hp
 * Assign to @var{R} the polynomial @var{A} modulo 
 * @math{(p,\,x_1 - \alpha_1,\ldots,x_k - \alpha_k)} 
 * where @var{p} denotes @code{ba0_mint_hp_module},
 * the @math{x_k} denote the derivatives occurring in @var{A} which satisfy
 * @var{f} and the @math{\alpha_k = g (p, x_k)} are ``random'' values
 * which are actually functions of @var{p} and @math{x_k}.
 */

BAP_DLL void
bap_random_eval_polynom_mpz_to_mint_hp (
    struct bap_polynom_mint_hp *R,
    struct bap_polynom_mpz *A,
    ba0_unary_predicate *f)
{
  struct bap_itermon_mpz iter;
  struct bap_geobucket_mint_hp geo;
  struct bap_polynom_mint_hp monome;
  bool *evaluer;
  ba0_mint_hp *value;
  struct bav_term T;
  struct bav_variable *u;
  ba0_mpz_t bunk, *lc;
  ba0_int_p i, j;
  ba0_mint_hp c;
  struct ba0_mark M;

  ba0_push_another_stack ();
  ba0_record (&M);
/*
   evaluer [i] indicates if the variable with index i gets a value
   value [i] gives the value for the variable with index i
*/
  evaluer = (bool *) ba0_alloc (sizeof (bool) * bav_global.R.vars.size);
  value =
      (ba0_mint_hp *) ba0_alloc (sizeof (ba0_mint_hp) * bav_global.R.vars.size);
  for (i = 0; i < A->total_rank.size; i++)
    {
      u = A->total_rank.rg[i].var;
      evaluer[u->index_in_vars] = (*f) (u);
      if (evaluer[u->index_in_vars])
        value[u->index_in_vars] = bav_random_eval_variable_to_mint_hp (u);
    }

  ba0_mpz_init (bunk);
  bav_init_term (&T);
  bap_init_polynom_mint_hp (&monome);
  bap_init_geobucket_mint_hp (&geo);
  bap_begin_itermon_mpz (&iter, A);
  while (!bap_outof_itermon_mpz (&iter))
    {
      lc = bap_coeff_itermon_mpz (&iter);
      bap_term_itermon_mpz (&T, &iter);
      c = (ba0_mint_hp) ba0_mpz_mod_ui (bunk, *lc, ba0_mint_hp_module);
      j = 0;
      for (i = 0; i < T.size; i++)
        {
          u = T.rg[i].var;
          if (evaluer[u->index_in_vars])
            {
              ba0_mint_hp d =
                  ba0_pow_mint_hp (value[u->index_in_vars], T.rg[i].deg);
              ba0_mint_hp_mul (c, c, d);
            }
          else
            T.rg[j++] = T.rg[i];
        }
      T.size = j;
      bap_set_polynom_monom_mint_hp (&monome, c, &T);
      bap_add_geobucket_mint_hp (&geo, &monome);
      bap_next_itermon_mpz (&iter);
    }
  ba0_pull_stack ();
  bap_set_polynom_geobucket_mint_hp (R, &geo);
  ba0_restore (&M);
}

/*-
\paragraph{void bap_Berlekamp_mint_hp (struct bap_product_mint_hp * prod, struct bap_polynom_mint_hp * P)}
Denote $n$ the module {\tt ba0_mint_hp_module}.
Sets {\em prod} to the factorization 
$$\frac{1}{i_P} P =  F_1 \cdots F_r \mod n$$ where the $F_i$ are
irreductible modulo~$n$. The input polynomial $P$ is assumed to
be non constant and squarefree.
-*/

/*
 * texinfo: bap_Berlekamp_mint_hp
 * Denote @var{n} the module @code{ba0_mint_hp_module}.
 * Assigns to @var{prod} the factorization
 * @math{1/i_P\,P = F_1 \cdots F_r} modulo @var{n} where the @math{F_i}
 * are irreducible modulo @var{n}. The input polynomial @var{P} is assumed
 * to be nonconstant and squarefree.
 */

BAP_DLL void
bap_Berlekamp_mint_hp (
    struct bap_product_mint_hp *prod,
    struct bap_polynom_mint_hp *P)
{
  bav_Idegree d;
  ba0_int_p i, j, k, l, r, *C, module, found;
  ba0_int_hp *A, *U, *Q;
  struct bap_itermon_mint_hp iter;
  struct bav_term term;
  struct bap_polynom_mint_hp *F = (struct bap_polynom_mint_hp *) 0, B, G;
  struct ba0_mark M;

  module = (ba0_int_p) ba0_mint_hp_module;

  ba0_push_another_stack ();
  ba0_record (&M);

  d = bap_leading_degree_polynom_mint_hp (P);
  if (d == 1)
    {
      r = 0;
      goto fin;
    }
/*
   Tableau U des coefficients de P.
*/
  U = (ba0_int_hp *) ba0_alloc (sizeof (ba0_int_hp) * (d + 1));
  for (i = 0; i <= d; i++)
    U[i] = 0;
  bap_begin_itermon_mint_hp (&iter, P);
  bav_init_term (&term);
  while (!bap_outof_itermon_mint_hp (&iter))
    {
      bap_term_itermon_mint_hp (&term, &iter);
      i = term.size == 0 ? 0 : term.rg[0].deg;
      U[i] = (ba0_int_hp) * bap_coeff_itermon_mint_hp (&iter);
      bap_next_itermon_mint_hp (&iter);
    }
/*
   A zone intermediaire pour faire les elevations a la puissance mod P.
*/
  A = (ba0_int_hp *) ba0_alloc (sizeof (ba0_int_hp) * d);
  A[0] = 1;
  for (i = 1; i < d; i++)
    A[i] = 0;
/*
  Matrice Q = matrice de l'application 
			F -> F^ba0_mint_hp_module (mod P, ba0_mint_hp_module)
	      moins la matrice identite.
  La premiere ligne est omise.
*/
  Q = (ba0_int_hp *) ba0_alloc (sizeof (ba0_int_hp) * d * d);
  for (k = 1; k < d; k++)
    {
      for (j = 0; j < ba0_mint_hp_module; j++)
        {
          ba0_int_p t = (ba0_int_p) A[d - 1];
          for (i = d - 1; i > 0; i--)
            A[i] =
                (ba0_int_hp) (((ba0_int_p) A[i - 1] -
                    t * (ba0_int_p) U[i]) % module);
          A[0] = (ba0_int_hp) ((-t * (ba0_int_p) U[0]) % module);
        }
      for (j = 0; j < d; j++)
        Q[d * k + j] = A[j];
      Q[d * k + k] = (Q[d * k + k] - 1) % (ba0_int_hp) module;
    }
/*
printf ("matrice Q\n");
for (k = 1; k < d; k++)
{   for (j = 0; j < d; j++)
	ba0_printf ("%d\t", (int)Q [d * k + j]);
    ba0_printf ("\n");
}
*/

/*
  Recherche du noyau
*/
  C = (ba0_int_p *) ba0_alloc (sizeof (ba0_int_p) * d);
  for (i = 0; i < d; i++)
    C[i] = -1;
  r = 0;
  for (k = 1; k < d; k++)
    {
      j = 0;
      while (j < d && (Q[d * k + j] == 0 || C[j] >= 0))
        j++;
      if (j < d)
        {
          ba0_int_p t;
/*
   t = -1 / Q [k, j] mod p
*/
          t = Q[d * k + j] > 0 ? Q[d * k + j] : module + Q[d * k + j];
          t = module - (ba0_int_p) ba0_invert_mint_hp ((ba0_int_hp) t);
          Q[d * k + j] = -1;
          if (t != 1)
            {
              for (i = k + 1; i < d; i++)
                Q[d * i + j] =
                    (ba0_int_hp) ((t * (ba0_int_p) Q[d * i + j]) % module);
            }
          for (l = 0; l < d; l++)
            {
              if (l != j && Q[d * k + l] != 0)
                {
                  t = (ba0_int_p) Q[d * k + l];
                  Q[d * k + l] = 0;
                  for (i = k + 1; i < d; i++)
                    Q[d * i + l] =
                        (ba0_int_hp) (((ba0_int_p) Q[d * i + l] +
                            t * (ba0_int_p) Q[d * i + j]) % module);
                }
            }
          C[j] = k;
        }
      else
        {
          r = r + 1;
          for (i = 0; i < d; i++)
            Q[d * r + i] = 0;
          for (i = 0; i < d; i++)
            {
              if (C[i] >= 0)
                Q[d * r + C[i]] = Q[d * k + i];
            }
          Q[d * r + k] = 1;
        }
    }
/*
    ba0_printf ("nombre de factors = %d\n", r + 1);
*/
  if (r == 0)
    goto fin;
/*
   F = les factors
   Initialement, il faut factoriser le polynome P.
*/
  F = (struct bap_polynom_mint_hp *) ba0_alloc (sizeof (struct
          bap_polynom_mint_hp) * (r + 1));
  bap_init_polynom_mint_hp (&F[0]);
  bap_set_polynom_mint_hp (&F[0], P);
  found = 1;
  bap_init_polynom_mint_hp (&B);
  bap_init_polynom_mint_hp (&G);

  for (k = 1; k <= r && found <= r; k++)
    {
      struct bap_creator_mint_hp crea;
      struct bav_rank rg;
/*
   Creation du k-eme element B de la base du noyau
*/
      i = d - 1;
      while (Q[d * k + i] == 0)
        i--;
      rg.var = bap_leader_polynom_mint_hp (P);
      rg.deg = i;
      bav_set_term_rank (&term, &rg);
      bap_begin_creator_mint_hp (&crea, &B, &term, bap_exact_total_rank, i + 1);
      while (i >= 0)
        {
          if (Q[d * k + i] != 0)
            {
              if (i > 0)
                term.rg[0].deg = i;
              else
                term.size = 0;
              bap_write_creator_mint_hp (&crea, &term,
                  Q[d * k + i] >
                  0 ? Q[d * k + i] : (ba0_int_hp) module + Q[d * k + i]);
            }
          i -= 1;
        }
      bap_close_creator_mint_hp (&crea);
      for (j = 0; j < module - 1 && found <= r; j++)
        {
          ba0_int_p old_found;
          if (j > 0)
            bap_add_polynom_numeric_mint_hp (&B, &B, ba0_mint_hp_module - 1);
          old_found = found;
          for (i = 0; i < old_found && found <= r; i++)
            {
              bap_Euclid_polynom_mint_hp (&G, &B, &F[i]);
              if (!bap_is_numeric_polynom_mint_hp (&G)
                  && bap_leading_degree_polynom_mint_hp (&G) <
                  bap_leading_degree_polynom_mint_hp (&F[i]))
                {
                  bap_init_polynom_mint_hp (&F[found]);
                  bap_exquo_polynom_mint_hp (&F[found], &F[i], &G);
                  bap_set_polynom_mint_hp (&F[i], &G);
                  found++;
                }
            }
        }
    }
fin:
  ba0_pull_stack ();
  bap_set_product_one_mint_hp (prod);
  bap_realloc_product_mint_hp (prod, r + 1);
  prod->size = r + 1;
  if (r == 0)
    bap_set_polynom_mint_hp (&prod->tab[0].factor, P);
  else
    {
      for (i = 0; i <= r; i++)
        bap_set_polynom_mint_hp (&prod->tab[i].factor, &F[i]);
    }
  ba0_restore (&M);
}
