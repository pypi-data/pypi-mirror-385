#include "bap_itermon_mpz.h"

#define BAD_FLAG_mpz

/****************************************************************************
 ITERATORS OF MONOMIALS
 ****************************************************************************/

/*
 * texinfo: bap_begin_itermon_mpz
 * Initialize the iterator @var{I} 
 * and set it on the first monomial of @var{A}.
 */

BAP_DLL void
bap_begin_itermon_mpz (
    struct bap_itermon_mpz *I,
    struct bap_polynom_mpz *A)
{
  I->poly = A;
  bap_begin_itermon_clot_mpz (&I->iter, I->poly->clot);
  if (!bap_is_zero_polynom_mpz (A))
    {
      if (I->poly->access == bap_sequential_monom_access)
        bap_goto_itermon_clot_mpz (&I->iter, I->poly->seq.first);
      else
        {
          bap_begin_iterator_indexed_access (&I->iter_ix, &I->poly->ind);
          bap_goto_itermon_clot_mpz (&I->iter,
              bap_index_iterator_indexed_access (&I->iter_ix));
        }
    }
  else if (I->poly->access == bap_indexed_monom_access)
    bap_begin_iterator_indexed_access (&I->iter_ix, &I->poly->ind);
}

/*
 * texinfo: bap_end_itermon_mpz
 * Initialize the iterator @var{I} and set it 
 * on the last  monomial of @var{A}.
 */

BAP_DLL void
bap_end_itermon_mpz (
    struct bap_itermon_mpz *I,
    struct bap_polynom_mpz *A)
{
  I->poly = A;
  bap_begin_itermon_clot_mpz (&I->iter, I->poly->clot);
  if (I->poly->access == bap_sequential_monom_access)
    bap_goto_itermon_clot_mpz (&I->iter, I->poly->seq.after - 1);
  else
    {
      bap_end_iterator_indexed_access (&I->iter_ix, &I->poly->ind);
      if (!bap_is_zero_polynom_mpz (A))
        bap_goto_itermon_clot_mpz (&I->iter,
            bap_index_iterator_indexed_access (&I->iter_ix));
    }
}

/*
 * texinfo: bap_set_itermon_mpz
 * Assign @var{J} to @var{I}.
 */

BAP_DLL void
bap_set_itermon_mpz (
    struct bap_itermon_mpz *I,
    struct bap_itermon_mpz *J)
{
  *I = *J;
}

/*
 * texinfo: bap_outof_itermon_mpz
 * Return true if the iterator is outside the polynomial.
 */

BAP_DLL bool
bap_outof_itermon_mpz (
    struct bap_itermon_mpz *I)
{
  if (I->poly->access == bap_sequential_monom_access)
    {
      ba0_int_p n = bap_number_itermon_clot_mpz (&I->iter);
      return n < I->poly->seq.first || n >= I->poly->seq.after;
    }
  else
    return bap_outof_iterator_indexed_access (&I->iter_ix);
}

/*
 * texinfo: bap_next_itermon_mpz
 * Move @var{I} to the next monomial.
 */

BAP_DLL void
bap_next_itermon_mpz (
    struct bap_itermon_mpz *I)
{
  if (I->poly->access == bap_sequential_monom_access)
    bap_next_itermon_clot_mpz (&I->iter);
  else
    {
      bap_next_iterator_indexed_access (&I->iter_ix);
      if (!bap_outof_iterator_indexed_access (&I->iter_ix))
        bap_goto_itermon_clot_mpz (&I->iter,
            bap_index_iterator_indexed_access (&I->iter_ix));
    }
}

/*
 * texinfo: bap_prev_itermon_mpz
 * Move @var{I} to the previous monomial.
 */

BAP_DLL void
bap_prev_itermon_mpz (
    struct bap_itermon_mpz *I)
{
  if (I->poly->access == bap_sequential_monom_access)
    bap_prev_itermon_clot_mpz (&I->iter);
  else
    {
      bap_prev_iterator_indexed_access (&I->iter_ix);
      if (!bap_outof_iterator_indexed_access (&I->iter_ix))
        bap_goto_itermon_clot_mpz (&I->iter,
            bap_index_iterator_indexed_access (&I->iter_ix));
    }
}

/*
 * texinfo: bap_goto_itermon_mpz
 * Move @var{I} on the monomial with number @var{n}.
 * Exception @code{BA0_ERRALG} is raised if @var{n} is not
 * a valid monomial number.
 */

BAP_DLL void
bap_goto_itermon_mpz (
    struct bap_itermon_mpz *I,
    ba0_int_p n)
{
  if (n < 0 || n >= bap_nbmon_polynom_mpz (I->poly))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  if (I->poly->access == bap_sequential_monom_access)
    bap_goto_itermon_clot_mpz (&I->iter, I->poly->seq.first + n);
  else
    {
      bap_goto_iterator_indexed_access (&I->iter_ix, n);
      bap_goto_itermon_clot_mpz (&I->iter,
          bap_index_iterator_indexed_access (&I->iter_ix));
    }
}

/*
 * texinfo: bap_coeff_itermon_mpz
 * Return the address of the coefficient of the current monomial.
 */

BAP_DLL ba0_mpz_t *
bap_coeff_itermon_mpz (
    struct bap_itermon_mpz *I)
{
  return bap_coeff_itermon_clot_mpz (&I->iter);
}

/*
 * texinfo: bap_term_itermon_mpz
 * Assign to @var{T} the term of the current monomial.
 */

BAP_DLL void
bap_term_itermon_mpz (
    struct bav_term *T,
    struct bap_itermon_mpz *I)
{
  if (bap_outof_itermon_mpz (I))
    BA0_RAISE_EXCEPTION (BA0_ERRALG);

  bap_term_itermon_clot_mpz (T, &I->iter);
  bap_strip_term_termstripper (T, I->poly->clot->ordering, &I->poly->tstrip);
}

/*
 * texinfo: bap_reductum_itermon_mpz
 * Assign to @var{A} the sum of all the monomials following the current monomial
 * (this one included). The result is readonly.
 */

BAP_DLL void
bap_reductum_itermon_mpz (
    struct bap_itermon_mpz *I,
    struct bap_polynom_mpz *A)
{
  if (bap_outof_itermon_mpz (I))
    bap_set_polynom_zero_mpz (A);
  else if (A != I->poly)
    {
      A->clot = I->poly->clot;
      if (I->poly->access == bap_sequential_monom_access)
        {
          A->access = bap_sequential_monom_access;
          A->seq.first = bap_number_itermon_clot_mpz (&I->iter);
          A->seq.after = I->poly->seq.after;
        }
      else
        {
          struct bap_creator_indexed_access crea;
          struct bap_iterator_indexed_access iter;
          ba0_int_p i, nbmon;

          A->access = bap_indexed_monom_access;
          bap_set_iterator_indexed_access (&iter, &I->iter_ix);
          nbmon = iter.ind->size - iter.num.combined;
          bap_realloc_indexed_access (&A->ind, nbmon);
          bap_begin_creator_indexed_access (&crea, &A->ind);
          for (i = 0; i < nbmon; i++)
            bap_write_creator_indexed_access (&crea,
                bap_read_iterator_indexed_access (&iter));
          bap_close_creator_indexed_access (&crea);
        }
      bap_set_termstripper (&A->tstrip, &I->poly->tstrip);
      bap_set_total_rank_polynom_mpz (A);
      A->readonly = true;
    }
  else
    {
      if (I->poly->access == bap_sequential_monom_access)
        {
          A->seq.first = bap_number_itermon_clot_mpz (&I->iter);
        }
      else
        {
          struct bap_creator_indexed_access crea;
          struct bap_iterator_indexed_access iter;
          ba0_int_p i, nbmon;

          bap_set_iterator_indexed_access (&iter, &I->iter_ix);
          nbmon = iter.ind->size - iter.num.combined;
          bap_begin_creator_indexed_access (&crea, &A->ind);
          for (i = 0; i < nbmon; i++)
            bap_write_creator_indexed_access (&crea,
                bap_read_iterator_indexed_access (&iter));
          bap_close_creator_indexed_access (&crea);
        }
      bap_set_total_rank_polynom_mpz (A);
      A->readonly = true;
    }
}

static void
seekfirst_sequential_itermon_poly_mpz (
    struct bap_itermon_mpz *I,
    enum bap_rank_code (*f) (struct bav_term *,
        struct bav_term *,
        bav_Inumber),
    struct bav_term *last_term,
    bav_Inumber last_number)
{
  ba0_int_p left, right, middle;
  enum bap_rank_code code;
  struct bav_term T;

  bav_init_term (&T);
  bap_term_itermon_mpz (&T, I);
  code = (*f) (&T, last_term, last_number);
  if (code == bap_rank_too_high)
    {
// look on the right
      left = bap_number_itermon_clot_mpz (&I->iter);
      right = I->poly->seq.after - 1;
    }
  else
    {
/*
   look on the left
*/
      left = I->poly->seq.first;
      right = bap_number_itermon_clot_mpz (&I->iter);
    }
  while (right - left > 1)
    {
      middle = (right + left) / 2;
      bap_goto_itermon_clot_mpz (&I->iter, middle);
      bap_term_itermon_mpz (&T, I);
      code = (*f) (&T, last_term, last_number);
      if (code == bap_rank_too_high)
        left = middle;
      else
        right = middle;
    }
/*
  When the two bounds are different, one considers the left one.
  If the rank is correct, one goes on it, else one goes to the right one.
*/
  if (left != right)
    {
      if (left != bap_number_itermon_clot_mpz (&I->iter))
        bap_prev_itermon_clot_mpz (&I->iter);
      bap_term_itermon_mpz (&T, I);
      code = (*f) (&T, last_term, last_number);
      if (code != bap_rank_ok)
        bap_next_itermon_clot_mpz (&I->iter);
    }
}

static void
seekfirst_indexed_itermon_poly_mpz (
    struct bap_itermon_mpz *I,
    enum bap_rank_code (*f) (struct bav_term *,
        struct bav_term *,
        bav_Inumber),
    struct bav_term *last_term,
    bav_Inumber last_number)
{
  ba0_int_p left, right, middle;
  enum bap_rank_code code;
  struct bav_term T;

  bav_init_term (&T);
  bap_term_itermon_mpz (&T, I);
  code = (*f) (&T, last_term, last_number);
  if (code == bap_rank_too_high)
    {
/*
   look on the right
*/
      left = I->iter_ix.num.combined;
      right = I->poly->ind.size - 1;
    }
  else
    {
/*
   look on the left
*/
      left = 0;
      right = I->iter_ix.num.combined;
    }
  while (right - left > 1)
    {
      middle = (right + left) / 2;
      bap_goto_iterator_indexed_access (&I->iter_ix, middle);
      bap_goto_itermon_clot_mpz (&I->iter,
          bap_index_iterator_indexed_access (&I->iter_ix));
      bap_term_itermon_mpz (&T, I);
      code = (*f) (&T, last_term, last_number);
      if (code == bap_rank_too_high)
        left = middle;
      else
        right = middle;
    }
/*
  When the two bounds are different, one considers the left one.
  If the rank is correct, one goes on it, else one goes to the right one.
*/
  if (left != right)
    {
      if (left != I->iter_ix.num.combined)
        {
          bap_prev_iterator_indexed_access (&I->iter_ix);
          bap_goto_itermon_clot_mpz (&I->iter,
              bap_index_iterator_indexed_access (&I->iter_ix));
        }
      bap_term_itermon_mpz (&T, I);
      code = (*f) (&T, last_term, last_number);
      if (code != bap_rank_ok)
        {
          bap_next_iterator_indexed_access (&I->iter_ix);
          bap_goto_itermon_clot_mpz (&I->iter,
              bap_index_iterator_indexed_access (&I->iter_ix));
        }
    }
}

/*
 * texinfo: bap_seekfirst_itermon_mpz
 * Move the iterator @var{I} to the first monomial such that
 * @math{f(T)} returns @code{bap_rank_ok}, where @var{T} denotes
 * the term of the monomial. 
 * Arguments @var{last_term} and @var{last_number} are extra arguments
 * passed to @var{f}.
 * The monomial is obtained by dichotomic search.
 */

BAP_DLL void
bap_seekfirst_itermon_mpz (
    struct bap_itermon_mpz *I,
    enum bap_rank_code (*f) (struct bav_term *,
        struct bav_term *,
        bav_Inumber),
    struct bav_term *last_term,
    bav_Inumber last_number)
{
  struct ba0_mark M;

  if (bap_is_zero_polynom_mpz (I->poly))
    BA0_RAISE_EXCEPTION (BAP_ERRNUL);
  ba0_record (&M);
  if (bap_outof_itermon_mpz (I))
    bap_begin_itermon_mpz (I, I->poly);
  if (I->poly->access == bap_sequential_monom_access)
    seekfirst_sequential_itermon_poly_mpz (I, f, last_term, last_number);
  else
    seekfirst_indexed_itermon_poly_mpz (I, f, last_term, last_number);
  ba0_restore (&M);
}

static void
seeklast_sequential_itermon_poly_mpz (
    struct bap_itermon_mpz *I,
    enum bap_rank_code (*f) (struct bav_term *,
        struct bav_term *,
        bav_Inumber),
    struct bav_term *last_term,
    bav_Inumber last_number)
{
  ba0_int_p left, right, middle;
  enum bap_rank_code code;
  struct bav_term T;

  bav_init_term (&T);
  bap_term_itermon_mpz (&T, I);
  code = (*f) (&T, last_term, last_number);
  if (code == bap_rank_too_low)
    {
/*
   look on the left
*/
      left = I->poly->seq.first;
      right = bap_number_itermon_clot_mpz (&I->iter);
    }
  else
    {
/*
   look on the right
*/
      left = bap_number_itermon_clot_mpz (&I->iter);
      right = I->poly->seq.after - 1;
    }
  while (right - left > 1)
    {
      middle = (right + left) / 2;
      bap_goto_itermon_clot_mpz (&I->iter, middle);
      bap_term_itermon_mpz (&T, I);
      code = (*f) (&T, last_term, last_number);
      if (code == bap_rank_too_low)
        right = middle;
      else
        left = middle;
    }
/*
   If the two bounds are different, one considers the right one.
   If the rank is correct then one goes on it else one goes to the left one.
*/
  if (left != right)
    {
      if (right != bap_number_itermon_clot_mpz (&I->iter))
        bap_next_itermon_clot_mpz (&I->iter);
      bap_term_itermon_mpz (&T, I);
      code = (*f) (&T, last_term, last_number);
      if (code != bap_rank_ok)
        bap_prev_itermon_clot_mpz (&I->iter);
    }
}

static void
seeklast_indexed_itermon_poly_mpz (
    struct bap_itermon_mpz *I,
    enum bap_rank_code (*f) (struct bav_term *,
        struct bav_term *,
        bav_Inumber),
    struct bav_term *last_term,
    bav_Inumber last_number)
{
  ba0_int_p left, right, middle;
  enum bap_rank_code code;
  struct bav_term T;

  bav_init_term (&T);
  bap_term_itermon_mpz (&T, I);
  code = (*f) (&T, last_term, last_number);
  if (code == bap_rank_too_low)
    {
/*
   look on the left
*/
      left = 0;
      right = I->iter_ix.num.combined;
    }
  else
    {
/*
   look on the right
*/
      left = I->iter_ix.num.combined;
      right = I->poly->ind.size - 1;
    }
  while (right - left > 1)
    {
      middle = (right + left) / 2;
      bap_goto_iterator_indexed_access (&I->iter_ix, middle);
      bap_goto_itermon_clot_mpz (&I->iter,
          bap_index_iterator_indexed_access (&I->iter_ix));
      bap_term_itermon_mpz (&T, I);
      code = (*f) (&T, last_term, last_number);
      if (code == bap_rank_too_low)
        right = middle;
      else
        left = middle;
    }
/*
   If the two bounds are different, one considers the right one.
   If the rank is correct then one goes on it else one goes to the left one.
*/
  if (left != right)
    {
      if (right != I->iter_ix.num.combined)
        {
          bap_next_iterator_indexed_access (&I->iter_ix);
          bap_goto_itermon_clot_mpz (&I->iter,
              bap_index_iterator_indexed_access (&I->iter_ix));
        }
      bap_term_itermon_mpz (&T, I);
      code = (*f) (&T, last_term, last_number);
      if (code != bap_rank_ok)
        {
          bap_prev_iterator_indexed_access (&I->iter_ix);
          bap_goto_itermon_clot_mpz (&I->iter,
              bap_index_iterator_indexed_access (&I->iter_ix));
        }
    }
}

/*
 * texinfo: bap_seeklast_itermon_mpz
 * Move the iterator @var{I} to the last monomial such that
 * @math{f(T)} returns @code{bap_rank_ok}, where @var{T} denotes
 * the term of the monomial. 
 * Arguments @var{last_term} and @var{last_number} are extra arguments
 * passed to @var{f}.
 * The monomial is obtained by dichotomic search.
 */

BAP_DLL void
bap_seeklast_itermon_mpz (
    struct bap_itermon_mpz *I,
    enum bap_rank_code (*f) (struct bav_term *,
        struct bav_term *,
        bav_Inumber),
    struct bav_term *last_term,
    bav_Inumber last_number)
{
  struct ba0_mark M;

  if (bap_is_zero_polynom_mpz (I->poly))
    BA0_RAISE_EXCEPTION (BAP_ERRNUL);
  ba0_record (&M);
  if (bap_outof_itermon_mpz (I))
    bap_begin_itermon_mpz (I, I->poly);
  if (I->poly->access == bap_sequential_monom_access)
    seeklast_sequential_itermon_poly_mpz (I, f, last_term, last_number);
  else
    seeklast_indexed_itermon_poly_mpz (I, f, last_term, last_number);
  ba0_restore (&M);
}

/*
 * texinfo: bap_close_itermon_mpz
 * Close the iterator. 
 */

BAP_DLL void
bap_close_itermon_mpz (
    struct bap_itermon_mpz *iter)
{
  iter = (struct bap_itermon_mpz *) 0;
}

#undef BAD_FLAG_mpz
