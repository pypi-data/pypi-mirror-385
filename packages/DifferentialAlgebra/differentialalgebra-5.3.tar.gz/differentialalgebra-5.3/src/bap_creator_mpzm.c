#include "bap_creator_mpzm.h"

#define BAD_FLAG_mpzm

/****************************************************************************
 CREATORS OF MONOMIALS

 They permit us to create polynomials monomials by monomials.
 ****************************************************************************/

/*
 * texinfo: bap_begin_creator_mpzm
 * Initialize the creator @var{crea} at the beginning of @var{A}.
 * The polynomial @var{A} is going to be overwritten.
 * If allocating some @code{bap_mont_mpzm} in the clot of @var{A}
 * is necessary they will be allocated @var{nbmon_par_mont} monomials.
 * The parameter @var{type} indicates if @var{T} is the exact total
 * rank of the resulting polynomial or a mere upper bound.
 */

BAP_DLL void
bap_begin_creator_mpzm (
    struct bap_creator_mpzm *crea,
    struct bap_polynom_mpzm *A,
    struct bav_term *T,
    enum bap_typeof_total_rank type,
    ba0_int_p table2of_monom_alloc)
{
  if (A == (struct bap_polynom_mpzm *) 0 || A->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  bap_begin_creator_clot_mpzm (&crea->crea, A->clot, T, table2of_monom_alloc);
  if (type == bap_exact_total_rank)
    bav_set_term (&A->total_rank, T);
  crea->poly = A;
  crea->type = type;
}

/*
 * texinfo: bap_append_creator_mpzm
 * Initialize the creator @var{crea} at the end of the polynomial @var{A}
 * (further monomials are going to be appended to the ones of @var{A}).
 * If allocating some @code{bap_mont_mpzm} in the clot of @var{A}
 * is necessary they will be allocated @var{nbmon_par_mont} monomials.
 */

BAP_DLL void
bap_append_creator_mpzm (
    struct bap_creator_mpzm *crea,
    struct bap_polynom_mpzm *A,
    ba0_int_p table2of_monom_alloc)
{
  if (A == (struct bap_polynom_mpzm *) 0)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  if (A->readonly)
    BA0_RAISE_EXCEPTION (BA0_ERRALG);
  bap_append_creator_clot_mpzm (&crea->crea, A->clot, table2of_monom_alloc);
  crea->poly = A;
  crea->type = bap_exact_total_rank;
}

/*
 * texinfo: bap_write_creator_mpzm
 * Write @math{c\,T} on the creator @var{crea}.
 * The coefficient may be zero.
 */

BAP_DLL void
bap_write_creator_mpzm (
    struct bap_creator_mpzm *crea,
    struct bav_term *T,
    ba0_mpzm_t c)
{
  bap_write_creator_clot_mpzm (&crea->crea, T, c);
}

/* Writes - c*T on crea.  The coefficient c may be zero. */

/*
 * texinfo: bap_write_neg_creator_mpzm
 * Write @math{- c\,T} on the creator.
 * The coefficient may be zero.
 */

BAP_DLL void
bap_write_neg_creator_mpzm (
    struct bap_creator_mpzm *crea,
    struct bav_term *T,
    ba0_mpzm_t c)
{
  bap_write_neg_creator_clot_mpzm (&crea->crea, T, c);
}

/*
 * texinfo: bap_is_write_allable_creator_mpzm
 * Return @code{true} if the function @code{bap_write_all_creator_mpzm}
 * can be applied to @var{crea} and @var{A}.
 */

BAP_DLL bool
bap_is_write_allable_creator_mpzm (
    struct bap_creator_mpzm *crea,
    struct bap_polynom_mpzm *A)
{
  return crea->poly->clot->ordering == A->clot->ordering
      && bap_are_disjoint_polynom_mpzm (crea->poly, A)
      && bap_equal_termanager (&crea->poly->clot->tgest, &A->clot->tgest)
      && A->access == bap_sequential_monom_access
      && bap_identity_termstripper (&A->tstrip, A->clot->ordering);
}

/*
 * texinfo: bap_write_all_creator_mpzm
 * Write all monomials of @var{A} on the creator @var{crea} efficiently.
 * This function only applies in restricted cases.
 * In particular, it is required that the term managers of @var{A}
 * and of the @code{poly} field of @var{crea} are compatible.
 */

BAP_DLL void
bap_write_all_creator_mpzm (
    struct bap_creator_mpzm *crea,
    struct bap_polynom_mpzm *A)
{
  bap_write_all_creator_clot_mpzm (&crea->crea, A->clot, A->seq.first,
      A->seq.after);
}

/*
 * texinfo: bap_write_neg_all_creator_mpzm
 * Write all monomials of @math{- A} on the creator @var{crea} efficiently.
 * This function only applies in restricted cases.
 * In particular, it is required that the term managers of @var{A}
 * and of the @code{poly} field of @var{crea} are compatible.
 */

BAP_DLL void
bap_write_neg_all_creator_mpzm (
    struct bap_creator_mpzm *crea,
    struct bap_polynom_mpzm *A)
{
  bap_write_neg_all_creator_clot_mpzm (&crea->crea, A->clot, A->seq.first,
      A->seq.after);
}

/*
 * texinfo: bap_write_mul_all_creator_mpzm
 * Write all monomials of @math{c\,A} on the creator @var{crea} efficiently.
 * This function only applies in restricted cases.
 * In particular, it is required that the term managers of @var{A}
 * and of the @code{poly} field of @var{crea} are compatible.
 */

BAP_DLL void
bap_write_mul_all_creator_mpzm (
    struct bap_creator_mpzm *crea,
    struct bap_polynom_mpzm *A,
    ba0_mpzm_t c)
{
  bap_write_mul_all_creator_clot_mpzm (&crea->crea, A->clot, c, A->seq.first,
      A->seq.after);
}

#if defined (BAD_FLAG_mpz)

/*
 * texinfo: bap_write_exquo_all_creator_mpz
 * This function is only available for polynomials with @code{ba0_mpz_t}
 * coefficients.
 * Write all monomials of @math{A / c} on the creator @var{crea} efficiently.
 * The division of the coefficients of @var{A} by @var{c} must be exact.
 * This function only applies in restricted cases.
 * In particular, it is required that the term managers of @var{A}
 * and of the @code{poly} field of @var{crea} are compatible.
 */

BAP_DLL void
bap_write_exquo_all_creator_mpz (
    struct bap_creator_mpz *crea,
    struct bap_polynom_mpz *A,
    ba0_mpz_t c)
{
  bap_write_exquo_all_creator_clot_mpzm (&crea->crea, A->clot, c, A->seq.first,
      A->seq.after);
}

#endif

/*
 * texinfo: bap_close_creator_mpzm
 * Complete the construction of the @code{poly} field of @var{crea}.
 * If @code{type} is @code{bap_approx_total_rank} then the @code{total_rank}
 * field of @var{A} is recomputed.
 */

BAP_DLL void
bap_close_creator_mpzm (
    struct bap_creator_mpzm *crea)
{
  struct bap_polynom_mpzm *A;

  bap_close_creator_clot_mpzm (&crea->crea);

  A = crea->poly;

  A->access = bap_sequential_monom_access;
  A->seq.first = 0;
  A->seq.after = A->clot->size;

  if (crea->type == bap_approx_total_rank)
    bap_set_total_rank_polynom_mpzm (A);

  bap_init_set_termstripper (&A->tstrip, (struct bav_variable *) -1,
      A->clot->ordering);
}

#undef BAD_FLAG_mpzm
