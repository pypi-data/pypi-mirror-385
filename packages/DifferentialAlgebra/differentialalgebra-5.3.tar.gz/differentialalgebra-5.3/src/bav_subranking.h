#if !defined (BAV_SUBRANKING_H)
#   define BAV_SUBRANKING_H 1

#   include "bav_common.h"
#   include "bav_variable.h"
#   include "bav_typed_ident.h"


BEGIN_C_DECLS

/*
 * texinfo: bav_subranking
 * This data type implements subrankings.
 * A @dfn{subranking} permits to
 * compare derivatives of differential indeterminates.
 * Subrankings form a subtype of the @code{bav_block} data type.
 *
 * There are five predefined subrankings:
 * @code{lex}, @code{grlexA}, @code{grlexB}, @code{degrevlexA}
 * and @code{degrevlexB}.
 * The difference between them is actually only meaningful in the case of
 * partial derivatives.
 * Consider two different derivatives @math{u = \theta\,y} and 
 * @math{v = \phi\,z} to be compared.
 * View the @dfn{derivative operators} @math{\theta,\phi} as power products 
 * of derivations. 
 *
 * Among themselves, differential indeterminates are ordered by their
 * order of appearance in the block.
 * Among themselves, derivations are ordered by their order of
 * appearance in the derivation list:
 * this permits to compare derivative operators.
 * For details, see the @code{bav_ordering} data structure.
 *
 * In the @code{lex} ordering, derivative operators 
 * are first compared with respect to the lexicographic order; in case
 * of equality, differential indeterminates are compared.
 *
 * In all other subrankings, derivative operators are first compared
 * with respect to their total order. In the sequel, it is assumed
 * that @math{\theta} and @math{\phi} have the same total order.
 *
 * In the @code{grlexA} and @code{degrevlexA} subrankings, 
 * the second comparison criterion is given by the differential 
 * indeterminates i.e. @math{u > v} if @math{y > z}.
 * In the case of equality, the derivative operators are compared
 * either with respect to the lexicographic ordering (@code{grlexA})
 * or with respect to the reverse lexicographic ordering (@code{degrevlexA}).
 *
 * In the @code{grlexB} and @code{degrevlexB} subrankings, 
 * the second comparison criterion is given by the derivative operators,
 * which are compared either with respect to the lexicographic ordering 
 * (@code{grlexB}) or with respect to the reverse lexicographic ordering 
 * (@code{degrevlexB}). In the case of equality, the differential 
 * indeterminates are compared.
 *
 * To each subranking, a comparison function @code{inf} is associated.
 * This function is called when a new ordering or a new variable are
 * created. It is involved in the comparison process of two variables,
 * in order to determine their numbers, with respect to some ordering
 * @var{ord}.
 *
 * This function takes as input two different variables @var{v} and @var{w}
 * belonging to some same block of @var{ord}, their typed ident
 * @var{tid_v} and @var{tid_w}, picked 
 * from the @code{typed_idents} field of @var{ord} and the address
 * of the @code{ders} field of @var{ord}. It returns @code{true} if 
 * @math{v < w} with respect to the subranking (hence the ordering),
 * @code{false} otherwise.
 */

struct bav_typed_ident;

struct bav_subranking
{
// The identifier of the subranking (grlexA, degrevlexB, ...)
// This identifier is a readonly global string.
  char *ident;
  bool (
      *inf) (
      struct bav_variable * v,
      struct bav_variable * w,
      struct bav_typed_ident * tid_v,
      struct bav_typed_ident * tid_w,
      struct bav_tableof_symbol * ders);
};

extern BAV_DLL bool bav_is_subranking (
    char *,
    struct bav_subranking **);

END_C_DECLS
#endif /* !BAV_SUBRANKING_H */
