#include "bap_itercoeff_mpq.h"

#define BAD_FLAG_mpq

/****************************************************************************
 ITERATORS OF ba0_mpqICIENTS
 ****************************************************************************/

static enum bap_rank_code
itercoeff_samerank_mpq (
    struct bav_term *R,
    struct bav_term *last_term,
    bav_Inumber last_number)
{
  enum ba0_compare_code code;
/*
 * Readonly static data
 */
  static enum bap_rank_code tab[] =
      { bap_rank_too_low, bap_rank_ok, bap_rank_ok,
    bap_rank_too_high
  };
/*
 * Compare the two terms up to the last variable with number >= last_number
 * last_number being the number of the last variable w.r.t. which
 * coefficients are taken
 */
  code = bav_compare_stripped_term (R, last_term, last_number);
  return tab[code];
}

/*
 * texinfo: bap_begin_itercoeff_mpq
 * Initialize the iterator on the first coefficient of @var{A} i.e.
 * the one with highest term, w.r.t. the lexicographic order induced
 * by the current ordering.
 * The variable @var{v} provides the lowest variable of the alphabet of 
 * the terms.
 */

BAP_DLL void
bap_begin_itercoeff_mpq (
    struct bap_itercoeff_mpq *I,
    struct bap_polynom_mpq *A,
    struct bav_variable *v)
{
  struct ba0_mark M;
  struct bav_term last_term;
  bav_Inumber last_number;

  I->poly = A;
  I->last_variable = v;

  if (bap_is_zero_polynom_mpq (A))
    {
      I->outof = true;
      return;
    }

  ba0_record (&M);

  bav_init_term (&last_term);
  last_number = v->number.tab[bav_current_ordering ()];
  bap_begin_itermon_mpq (&I->debut, A);
  bap_term_itermon_mpq (&last_term, &I->debut);
  bap_begin_itermon_mpq (&I->fin, A);
  bap_seeklast_itermon_mpq (&I->fin, &itercoeff_samerank_mpq, &last_term,
      last_number);
  I->outof = false;

  ba0_restore (&M);
}

/*
 * texinfo: bap_end_itercoeff_mpq
 * Initialize the iterator on the last coefficient of @var{A} i.e.
 * the one with lowest term, w.r.t. the lexicographic order induced
 * by the current ordering.
 * The variable @var{v} provides the lowest variable of the alphabet of 
 * the terms.
 */

BAP_DLL void
bap_end_itercoeff_mpq (
    struct bap_itercoeff_mpq *I,
    struct bap_polynom_mpq *A,
    struct bav_variable *v)
{
  struct ba0_mark M;
  struct bav_term last_term;
  bav_Inumber last_number;

  I->poly = A;
  I->last_variable = v;

  if (bap_is_zero_polynom_mpq (A))
    {
      I->outof = true;
      return;
    }

  ba0_record (&M);

  bav_init_term (&last_term);
  last_number = v->number.tab[bav_current_ordering ()];
  bap_end_itermon_mpq (&I->fin, A);
  bap_term_itermon_mpq (&last_term, &I->fin);
  bap_begin_itermon_mpq (&I->debut, A);
  bap_seekfirst_itermon_mpq (&I->debut, &itercoeff_samerank_mpq, &last_term,
      last_number);
  I->outof = false;

  ba0_restore (&M);
}

/*
 * texinfo: bap_outof_itercoeff_mpq
 * Return true if the iterator has exited from the polynomial.
 */

BAP_DLL bool
bap_outof_itercoeff_mpq (
    struct bap_itercoeff_mpq *I)
{
  return I->outof;
}

/*
 * texinfo: bap_next_itercoeff_mpq
 * Move the iterator to the next term.
 * Exception @code{BA0_ERRALG} is raised if the iterator is
 * outside the polynomial before the call.
 */

BAP_DLL void
bap_next_itercoeff_mpq (
    struct bap_itercoeff_mpq *I)
{
  struct ba0_mark M;
  struct bav_term last_term;
  bav_Inumber last_number;

  if (bap_outof_itercoeff_mpq (I))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_record (&M);

  last_number = I->last_variable->number.tab[bav_current_ordering ()];
  bav_init_term (&last_term);
  bap_set_itermon_mpq (&I->debut, &I->fin);
  bap_next_itermon_mpq (&I->debut);
  if (!bap_outof_itermon_mpq (&I->debut))
    {
      bap_term_itermon_mpq (&last_term, &I->debut);
      bap_seeklast_itermon_mpq (&I->fin, &itercoeff_samerank_mpq,
          &last_term, last_number);
    }
  else
    I->outof = true;

  ba0_restore (&M);
}

/*
 * texinfo: bap_prev_itercoeff_mpq
 * Move the iterator to the previous term.
 * Exception @code{BA0_ERRALG} is raised if the iterator is
 * outside the polynomial before the call.
 */

BAP_DLL void
bap_prev_itercoeff_mpq (
    struct bap_itercoeff_mpq *I)
{
  struct ba0_mark M;
  struct bav_term last_term;
  bav_Inumber last_number;

  if (bap_outof_itercoeff_mpq (I))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_record (&M);

  last_number = I->last_variable->number.tab[bav_current_ordering ()];
  bav_init_term (&last_term);
  bap_set_itermon_mpq (&I->fin, &I->debut);
  bap_prev_itermon_mpq (&I->fin);
  if (!bap_outof_itermon_mpq (&I->fin))
    {
      bap_term_itermon_mpq (&last_term, &I->fin);
      bap_seekfirst_itermon_mpq (&I->debut, &itercoeff_samerank_mpq,
          &last_term, last_number);
    }
  else
    I->outof = true;

  ba0_restore (&M);
}

/*
 * texinfo: bap_term_itercoeff_mpq
 * Assign to @var{T} the current term.
 * Exception @code{BA0_ERRALG} is raised if the iterator is
 * outside the polynomial before the call.
 */

BAP_DLL void
bap_term_itercoeff_mpq (
    struct bav_term *T,
    struct bap_itercoeff_mpq *I)
{
  if (bap_outof_itercoeff_mpq (I))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  bap_term_itermon_mpq (T, &I->debut);
  bav_strip_term (T, T, I->last_variable->number.tab[bav_current_ordering ()]);
}

/*
 * texinfo: bap_coeff_itercoeff_mpq
 * Assign to @var{A} the current coefficient in readonly mode.
 * Exception @code{BA0_ERRALG} is raised if the iterator is
 * outside the polynomial before the call.
 */

BAP_DLL void
bap_coeff_itercoeff_mpq (
    struct bap_polynom_mpq *A,
    struct bap_itercoeff_mpq *I)
{
  struct bav_term *T;
  bav_Inumber n;
  ba0_int_p j;

  if (bap_outof_itercoeff_mpq (I))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
/*
   Calcul des numeros de monomes
*/
  if (I->poly->access == bap_sequential_monom_access)
    {
      A->clot = I->poly->clot;
      A->access = bap_sequential_monom_access;
      A->seq.first = bap_number_itermon_clot_mpq (&I->debut.iter);
      A->seq.after = bap_number_itermon_clot_mpq (&I->fin.iter) + 1;
    }
  else
    {
      struct bap_creator_indexed_access crea;
      struct bap_iterator_indexed_access iter;
      ba0_int_p i, nbmon;

      A->clot = I->poly->clot;
      A->access = bap_indexed_monom_access;

      nbmon = I->fin.iter_ix.num.combined - I->debut.iter_ix.num.combined + 1;
      bap_realloc_indexed_access (&A->ind, nbmon);
      bap_begin_creator_indexed_access (&crea, &A->ind);

      bap_set_iterator_indexed_access (&iter, &I->debut.iter_ix);
      for (i = 0; i < nbmon; i++)
        bap_write_creator_indexed_access (&crea,
            bap_read_iterator_indexed_access (&iter));
      bap_close_creator_indexed_access (&crea);
    }
  bap_set_termstripper (&A->tstrip, &I->poly->tstrip);
/*
   Calcul de la struct bav_variable * maximale
*/
  T = &I->poly->total_rank;
  n = I->last_variable->number.tab[bav_current_ordering ()];
  j = 0;
  while (j < T->size && bav_variable_number (T->rg[j].var) >= n)
    j++;
  bap_change_variable_termstripper (&A->tstrip,
      j == T->size ? BAV_NOT_A_VARIABLE : T->rg[j].var);
/*
   Calcul du struct bav_rank total
*/
  bap_set_total_rank_polynom_mpq (A);
/*
   Calcul du booleen coeff
*/
  A->readonly = true;
}

/*
 * texinfo: bap_seek_coeff_itercoeff_mpq
 * Assign to @var{A}, as a readonly polynomial, the coefficient of the
 * term @var{T}. If @var{T} involves variables strictly less than the 
 * last variable of the alphabet of the terms, they are ignored.
 * Exception @code{BA0_ERRALG} is raised if the iterator is
 * outside the polynomial before the call.
 */

BAP_DLL void
bap_seek_coeff_itercoeff_mpq (
    struct bap_polynom_mpq *A,
    struct bap_itercoeff_mpq *I,
    struct bav_term *T)
{
  struct bav_term U;
  enum ba0_compare_code code;
  struct ba0_mark M;
  struct bav_term *last_term;
  bav_Inumber last_number;

  if (bap_outof_itercoeff_mpq (I))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  last_term = T;
  last_number = I->last_variable->number.tab[bav_current_ordering ()];

  bap_seekfirst_itermon_mpq (&I->debut, &itercoeff_samerank_mpq, last_term,
      last_number);

  ba0_record (&M);
  bav_init_term (&U);
  bap_term_itermon_mpq (&U, &I->debut);
  code = bav_compare_stripped_term (T, &U, last_number);
  ba0_restore (&M);

  if (code != ba0_eq)
    bap_set_polynom_zero_mpq (A);
  else
    {
      bap_seeklast_itermon_mpq (&I->fin, &itercoeff_samerank_mpq, last_term,
          last_number);
      bap_coeff_itercoeff_mpq (A, I);
    }
}

/*
 * Stores in A the monomials between I->debut and I->fin.
 */

static void
bap_set_polynom_itercoeff_mpq (
    struct bap_polynom_mpq *A,
    struct bap_itercoeff_mpq *I)
{
  struct bap_creator_indexed_access crea;
  struct bap_iterator_indexed_access iter;
  ba0_int_p i, nbmon;
/*
   Calcul des numeros de monomes
 */
  if (I->poly->access == bap_sequential_monom_access)
    {
      A->clot = I->poly->clot;
      A->access = bap_sequential_monom_access;
      A->seq.first = bap_number_itermon_clot_mpq (&I->debut.iter);
      A->seq.after = bap_number_itermon_clot_mpq (&I->fin.iter);
    }
  else
    {
      A->clot = I->poly->clot;
      A->access = bap_indexed_monom_access;

      nbmon = I->fin.iter_ix.num.combined - I->debut.iter_ix.num.combined;
      bap_realloc_indexed_access (&A->ind, nbmon);
      bap_begin_creator_indexed_access (&crea, &A->ind);

      bap_set_iterator_indexed_access (&iter, &I->debut.iter_ix);
      for (i = 0; i < nbmon; i++)
        bap_write_creator_indexed_access (&crea,
            bap_read_iterator_indexed_access (&iter));
      bap_close_creator_indexed_access (&crea);
    }
  bap_set_termstripper (&A->tstrip, &I->poly->tstrip);
/*
   Calcul du struct bav_rank total
 */
  bap_set_total_rank_polynom_mpq (A);
/*
   Calcul du booleen coeff
 */
  A->readonly = true;
}

/*
 * texinfo: bap_split_polynom_mpq
 * Split @var{R} into two parts.
 * Assign to @var{A}, as a readonly polynomial, the sum of all the
 * monomials which are greater than or equal to @var{T}. 
 * Assign to @var{B} the sum of the remaining monomials.
 */

BAP_DLL void
bap_split_polynom_mpq (
    struct bap_polynom_mpq *A,
    struct bap_polynom_mpq *B,
    struct bap_polynom_mpq *R,
    struct bav_term *T)
{
  struct bap_itercoeff_mpq iter;
  struct bav_term U;
  struct ba0_mark M;
  enum ba0_compare_code code;
  struct bav_term *last_term;
  bav_Inumber last_number;

  if ((R == A && B != BAP_NOT_A_POLYNOM_mpq) || (R == B
          && A != BAP_NOT_A_POLYNOM_mpq))
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  if (T->size == 0)
    {
      if (A != BAP_NOT_A_POLYNOM_mpq && A != R)
        bap_set_readonly_polynom_mpq (A, R);
      if (B != BAP_NOT_A_POLYNOM_mpq && B != R)
        bap_set_polynom_zero_mpq (B);
      return;
    }
  else
    bap_begin_itercoeff_mpq (&iter, R, T->rg[T->size - 1].var);

  bap_begin_itermon_mpq (&iter.debut, R);

  last_term = T;
  last_number = iter.last_variable->number.tab[bav_current_ordering ()];

  ba0_push_another_stack ();
  ba0_record (&M);
  bav_init_term (&U);
  bap_term_itermon_mpq (&U, &iter.debut);
  ba0_pull_stack ();

  code = bav_compare_stripped_term (T, &U, last_number);
  if (code == ba0_gt)
    bap_set_itermon_mpq (&iter.fin, &iter.debut);
  else
    {
      bap_seeklast_itermon_mpq (&iter.fin, &itercoeff_samerank_mpq,
          last_term, last_number);
      bap_next_itermon_mpq (&iter.fin);
    }
  ba0_restore (&M);

  if (A != BAP_NOT_A_POLYNOM_mpq)
    {
      bap_set_polynom_itercoeff_mpq (A, &iter);
    }
  if (B != BAP_NOT_A_POLYNOM_mpq)
    {
      bap_set_itermon_mpq (&iter.debut, &iter.fin);
      bap_end_itermon_mpq (&iter.fin, R);
      bap_next_itermon_mpq (&iter.fin);
      bap_set_polynom_itercoeff_mpq (B, &iter);
    }
}

/*
 * texinfo: bap_close_itercoeff_mpq
 * Close the iterator. 
 */

BAP_DLL void
bap_close_itercoeff_mpq (
    struct bap_itercoeff_mpq *iter)
{
  iter = (struct bap_itercoeff_mpq *) 0;
}

#undef BAD_FLAG_mpq
