#if !defined (BAD_CRITICAL_PAIR_H)
#   define BAD_CRITICAL_PAIR_H 1

#   include "bad_common.h"
#   include "bad_selection_strategy.h"

BEGIN_C_DECLS

/*
 * texinfo: bad_typeof_critical_pair
 * This data type permits to tag critical pairs in order to
 * process the most important ones before the other ones.
 * The default tag is @code{bad_normal_critical_pair}.
 * The tag @code{bad_rejected_easy_critical_pair} corresponds
 * to critical pairs @math{\{p_1, p_2\}} which are not reduction
 * critical pairs and such that neither @var{p_1} nor @var{p_2}
 * occurs in the field @code{A} of the current quadruple.
 */

enum bad_typeof_critical_pair
{
// default tag
  bad_normal_critical_pair,
// this tag indicates a lower priority
  bad_rejected_easy_critical_pair
};

/*
 * texinfo: bad_critical_pair
 * This data type implements critical pairs.
 * A pair @math{\{ p_1, p_2 \}} of differential polynomials is said to 
 * be a @dfn{critical pair} if the leaders of @math{p_1} and @math{p_2} 
 * are derivatives of some same differential indeterminate @math{u}.
 * Denote @math{\theta_1 u} the leading derivative of @math{p_1} and 
 *        @math{\theta_2 u} the one of @math{p_2}. 
 *
 * Denote @math{\theta_{12} = lcm{(\theta_1, \theta_2)}}. 
 *
 * If @math{\theta_{12} = \theta_1} or @math{\theta_{12} = \theta_2} 
 *      then the pair is called a @dfn{reduction critical pair}
 *      and the corresponding @math{\Delta}-polynomial is
 *      @math{\Delta (p_1, p_2) = prem (p_2, (\theta_{12}/{\theta_1}) p_1)}
 *
 * If the critical pair is not a reduction one then the
 *      corresponding @math{\Delta}-polynomial is
 *      @math{\Delta (p_1, p_2) = s_2 \, ({\theta_{12}}/{\theta_1}) p_1 
 *                              - s_1 \, ({\theta_{12}}/{\theta_2}) p_2}
 *      where @math{s_1} and @math{s_2} denote the separants of
 *      @math{p_1} and @math{p_2}.
 */

struct bad_critical_pair
{
  enum bad_typeof_critical_pair tag;
  struct bap_polynom_mpz p;
  struct bap_polynom_mpz q;
};


struct bad_listof_critical_pair
{
  struct bad_critical_pair *value;
  struct bad_listof_critical_pair *next;
};


extern BAD_DLL void bad_init_critical_pair (
    struct bad_critical_pair *);

extern BAD_DLL struct bad_critical_pair *bad_new_critical_pair (
    void);

extern BAD_DLL struct bad_critical_pair *bad_new_critical_pair_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAD_DLL void bad_set_critical_pair (
    struct bad_critical_pair *,
    struct bad_critical_pair *);

extern BAD_DLL void bad_set_critical_pair_polynom_mpz (
    struct bad_critical_pair *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAD_DLL void bad_delta_polynom_critical_pair (
    struct bap_polynom_mpz *,
    struct bad_critical_pair *);

extern BAD_DLL void bad_thetas_and_leaders_critical_pair (
    struct bav_tableof_term *,
    struct bav_tableof_variable *,
    struct bad_critical_pair *);

extern BAD_DLL bool bad_is_a_reduction_critical_pair (
    struct bad_critical_pair *,
    struct bav_variable **);

extern BAD_DLL bool bad_is_an_algebraic_critical_pair (
    struct bad_critical_pair *);

extern BAD_DLL bool bad_is_a_simpler_critical_pair (
    struct bad_critical_pair *,
    struct bad_critical_pair *,
    struct bad_selection_strategy *);

extern BAD_DLL bool bad_is_a_listof_rejected_critical_pair (
    struct bad_listof_critical_pair *);

extern BAD_DLL ba0_scanf_function bad_scanf_critical_pair;

extern BAD_DLL ba0_printf_function bad_printf_critical_pair;

extern BAD_DLL ba0_garbage1_function bad_garbage1_critical_pair;

extern BAD_DLL ba0_garbage2_function bad_garbage2_critical_pair;

extern BAD_DLL ba0_copy_function bad_copy_critical_pair;

END_C_DECLS
#endif /* !BAD_CRITICAL_PAIR_H */
