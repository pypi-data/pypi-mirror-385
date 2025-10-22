#if !defined (BAP_CLOT_mpz_H)
#   define BAP_CLOT_mpz_H 1

#   include "bap_common.h"
#   include "bap_termanager.h"

#   define BAD_FLAG_mpz

BEGIN_C_DECLS

/*
 * texinfo: bap_table2of_monom_mpz
 * This data type implements a contiguous linear combination
 * of zipterms. 
 */

struct bap_table2of_monom_mpz
{
  ba0_int_p alloc;              // number of allocated entries for both arrays
  ba0_int_p size;               // number of used entries for both arrays
  bap_zipterm *zipterm;         // the array of zipterms
  ba0_mpz_t *coeff;               // the array of coefficients
};


/*
 * texinfo: bap_tableof_table2of_monom_mpz
 * This data type is a table of tables. 
 * However, if we forget technical details, it is a sequence of
 * pairs of the form (term, coefficient).
 * These pairs are called @dfn{monomials} in the documentation.
 */

struct bap_tableof_table2of_monom_mpz
{
  ba0_int_p alloc;              // the number of allocated entries of tab
  ba0_int_p size;               // the number of used entries in tab
  struct bap_table2of_monom_mpz **tab;
};


/*
 * texinfo: bap_clot_mpz
 * This data type implements a clot i.e. a sequence of monomials
 * sorted in decreasing order w.r.t. the lexicographic ordering
 * induced by the current ordering.
 * The coefficients of monomials are nonzero.
 * Monomials are sometimes considered as numbered starting from @math{0}
 * in the documentation.
 */

struct bap_clot_mpz
{
// the total number of allocated entries of (zipterm, coeff)
  ba0_int_p alloc;
// the total number of used entries i.e. of monomials
  ba0_int_p size;
// the termanager which handles zipterms
  struct bap_termanager tgest;
// the table of bap_table2of_monom_mpz 
  struct bap_tableof_table2of_monom_mpz tab;
// the ordering w.r.t. which zipterms are ordered
  bav_Iordering ordering;
};


extern BAP_DLL struct bap_clot_mpz *bap_new_clot_mpz (
    struct bav_term *);

extern BAP_DLL bool bap_is_zero_clot_mpz (
    struct bap_clot_mpz *);

extern BAP_DLL void bap_reverse_clot_mpz (
    struct bap_clot_mpz *);

extern BAP_DLL void bap_sort_clot_mpz (
    struct bap_clot_mpz *,
    ba0_int_p,
    ba0_int_p);

extern BAP_DLL void bap_change_ordering_clot_mpz (
    struct bap_clot_mpz *,
    bav_Iordering);

extern BAP_DLL ba0_garbage1_function bap_garbage1_clot_mpz;

extern BAP_DLL ba0_garbage2_function bap_garbage2_clot_mpz;

extern BAP_DLL ba0_copy_function bap_copy_clot_mpz;

/*
 * texinfo: bap_itermon_clot_mpz
 * This data type implements iterators of monomials over a clot.
 * In this context the monomial number @code{num.combined}
 * is located in @code{clot->tab[num.primary]->tab[num.secondary]}.
 * An iterator may be set outside a clot.
 */

struct bap_itermon_clot_mpz
{
  struct bap_clot_mpz *clot;
  struct bap_composite_number num;
};


extern BAP_DLL void bap_begin_itermon_clot_mpz (
    struct bap_itermon_clot_mpz *,
    struct bap_clot_mpz *);

extern BAP_DLL void bap_end_itermon_clot_mpz (
    struct bap_itermon_clot_mpz *,
    struct bap_clot_mpz *);

extern BAP_DLL bool bap_outof_itermon_clot_mpz (
    struct bap_itermon_clot_mpz *);

extern BAP_DLL void bap_next_itermon_clot_mpz (
    struct bap_itermon_clot_mpz *);

extern BAP_DLL void bap_prev_itermon_clot_mpz (
    struct bap_itermon_clot_mpz *);

extern BAP_DLL void bap_goto_itermon_clot_mpz (
    struct bap_itermon_clot_mpz *,
    ba0_int_p);

extern BAP_DLL ba0_int_p bap_number_itermon_clot_mpz (
    struct bap_itermon_clot_mpz *);

extern BAP_DLL void bap_term_itermon_clot_mpz (
    struct bav_term *,
    struct bap_itermon_clot_mpz *);

extern BAP_DLL ba0_mpz_t *bap_coeff_itermon_clot_mpz (
    struct bap_itermon_clot_mpz *);

extern BAP_DLL void bap_swap_itermon_clot_mpz (
    struct bap_itermon_clot_mpz *,
    struct bap_itermon_clot_mpz *);

/*
 * texinfo: bap_creator_clot_mpz
 * This data type permits to create a clot monomial per monomial.
 * Monomials are stored in the clot by increasing number.
 * The creator permits to create clots whose monomials are not
 * sorted by decreasing order w.r.t. the lexicographic ordering
 * defined by the ranking. 
 * Creators rely on iterators of monomials over an already existing
 * clot which is then overwritten.
 */

struct bap_creator_clot_mpz
{
  struct bap_itermon_clot_mpz iter;
// the number of entries allocated to any new bap_table2of_monom_mpz
  ba0_int_p table2of_monom_alloc;
};


extern BAP_DLL void bap_begin_creator_clot_mpz (
    struct bap_creator_clot_mpz *,
    struct bap_clot_mpz *,
    struct bav_term *,
    ba0_int_p);

extern BAP_DLL void bap_append_creator_clot_mpz (
    struct bap_creator_clot_mpz *,
    struct bap_clot_mpz *,
    ba0_int_p);

extern BAP_DLL void bap_write_creator_clot_mpz (
    struct bap_creator_clot_mpz *,
    struct bav_term *,
    ba0_mpz_t);

extern BAP_DLL void bap_write_neg_creator_clot_mpz (
    struct bap_creator_clot_mpz *,
    struct bav_term *,
    ba0_mpz_t);

extern BAP_DLL void bap_write_term_creator_clot_mpz (
    struct bap_creator_clot_mpz *,
    struct bav_term *);

extern BAP_DLL void bap_write_all_creator_clot_mpz (
    struct bap_creator_clot_mpz *,
    struct bap_clot_mpz *,
    ba0_int_p,
    ba0_int_p);

extern BAP_DLL void bap_write_neg_all_creator_clot_mpz (
    struct bap_creator_clot_mpz *,
    struct bap_clot_mpz *,
    ba0_int_p,
    ba0_int_p);

extern BAP_DLL void bap_write_mul_all_creator_clot_mpz (
    struct bap_creator_clot_mpz *,
    struct bap_clot_mpz *,
    ba0_mpz_t,
    ba0_int_p,
    ba0_int_p);

#   if defined BAD_FLAG_mpz

extern BAP_DLL void bap_write_exquo_all_creator_clot_mpz (
    struct bap_creator_clot_mpz *,
    struct bap_clot_mpz *,
    ba0_mpz_t,
    ba0_int_p,
    ba0_int_p);

#   endif

extern BAP_DLL void bap_close_creator_clot_mpz (
    struct bap_creator_clot_mpz *);

extern BAP_DLL void bap_goto_creator_clot_mpz (
    struct bap_creator_clot_mpz *,
    ba0_int_p);

extern BAP_DLL void bap_switch_ring_clot_mpz (
    struct bap_clot_mpz *,
    struct bav_differential_ring *);

END_C_DECLS
#   undef BAD_FLAG_mpz
#endif /* !BAP_CLOT_mpz_H */
