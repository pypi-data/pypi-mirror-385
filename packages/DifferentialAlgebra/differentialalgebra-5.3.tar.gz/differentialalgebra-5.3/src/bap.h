#if !defined (BAP_COMMON_H)
#   define BAP_COMMON_H 1

#   include <bav.h>

/* 
 * The _MSC_VER flag is set if the code is compiled under WINDOWS
 * by using Microsoft Visual C (through Visual Studio 2008).
 *
 * In that case, some specific annotations must be added for DLL exports
 * Beware to the fact that this header file is going to be used either
 * for/while building BLAD or for using BLAD from an outer software.
 *
 * In the first case, functions are exported.
 * In the second one, they are imported.
 *
 * The flag BAP_BLAD_BUILDING must thus be set in the Makefile and passed
 * to the C preprocessor at BAP building time. Do not set it when using BAP.
 *
 * When compiling static libraries under Windows, set BA0_STATIC.
 */

#   if defined (_MSC_VER) && ! defined (BA0_STATIC)
#      if defined (BLAD_BUILDING) || defined (BAP_BLAD_BUILDING)
#         define BAP_DLL  __declspec(dllexport)
#      else
#         define BAP_DLL  __declspec(dllimport)
#      endif
#   else
#      define BAP_DLL
#   endif

/* #   include "bap_mesgerr.h" */

BEGIN_C_DECLS

/*
 * texinfo: bap_composite_number
 * This data structure aims at numbering elements which belong to
 * a sequence of elements implemented by means of tables of tables. 
 * Assume an element lies in @code{T->tab[i]->tab[j]}. Then 
 * @code{primary} is equal to @math{i}, 
 * @code{secondary} is equal to @math{j} and 
 * @code{combined}, the index of the element in the sequence, 
 * is equal to @math{j} plus the sum, for @math{0 \leq k < i} of 
 * @code{T->tab[k]->size}.
 */

struct bap_composite_number
{
  ba0_int_p primary;
  ba0_int_p secondary;
  ba0_int_p combined;
};

/*
 * texinfo: bap_typeof_monom_access
 * This data type permits to indicate the access which applies
 * to a polynomial.
 */

enum bap_typeof_monom_access
{
  bap_sequential_monom_access,
  bap_indexed_monom_access
};

/*
 * texinfo: bap_typeof_total_rank
 * This data type provides information on a @code{total_rank} field
 * while creating a polynomial, monomial per monomial.
 */

enum bap_typeof_total_rank
{
  bap_exact_total_rank,
  bap_approx_total_rank
};

/*
 * texinfo: bap_rank_code
 * This data type is used as return code for comparing ranks.
 */

enum bap_rank_code
{
  bap_rank_too_low,
  bap_rank_ok,
  bap_rank_too_high
};

extern BAP_DLL void bap_reset_all_settings (
    void);

extern BAP_DLL void bap_restart (
    ba0_int_p,
    ba0_int_p);

extern BAP_DLL void bap_terminate (
    enum ba0_restart_level);

extern BAP_DLL ba0_int_p bap_ceil_log2 (
    ba0_int_p);

END_C_DECLS
#endif /* !BAP_COMMON_H */
#if !defined (BAP_MESGERR_H)
#   define BAP_MESGERR_H 1

/* #   include "bap_common.h" */

BEGIN_C_DECLS

extern BAP_DLL char BAP_ERRNUL[];

extern BAP_DLL char BAP_ERRCST[];

extern BAP_DLL char BAP_ERRIND[];

extern BAP_DLL char BAP_ERRTGS[];

extern BAP_DLL char BAP_EXHNCP[];

END_C_DECLS
#endif /* !BAP_MESGERR_H */
#if !defined (BAP_TERMANAGER_H)
#   define BAP_TERMANAGER_H 1

/* #   include "bap_common.h" */

BEGIN_C_DECLS

/*
 * texinfo: bap_zipterm
 * If the term fits in a single @code{ba0_int_p} when compressed
 * then the corresponding @code{bap_zipterm} is the compressed form
 * of the term. If it does not, the corresponding @code{bap_zipterm}
 * is a pointer towards a sufficiently large array of @code{ba0_int_p}.
 */

typedef ba0_int_p bap_zipterm;

/*
 * texinfo: bap_termanager
 * This data type is designed to store the terms of a polynomial
 * (more precisely, of a clot in compressed form.
 */

struct bap_termanager
{
// the total rank of all terms of the clot
  struct bav_term total_rank;
  struct _zipping
  {
// number of ba0_int_p allocated to each zipterm
    ba0_int_p alloc;
// number of ba0_int_p used by each zipterm
    ba0_int_p size;
// the number of allocated entries of nbbits and mask
//      is equal to total_rank.alloc
// nbbits[i] = the number of bits needed to store the degree of 
//      the ith variable in total_rank in any zipterm
// mask[i]   = the binary mask needed to extract this degree
    unsigned char *nbbits;
    unsigned ba0_int_p *mask;
  } zipping;
};


extern BAP_DLL void bap_init_termanager (
    struct bap_termanager *,
    struct bav_term *);

extern BAP_DLL void bap_reset_termanager (
    struct bap_termanager *,
    struct bav_term *,
    bool *);

extern BAP_DLL bool bap_equal_termanager (
    struct bap_termanager *,
    struct bap_termanager *);

extern BAP_DLL void bap_init_set_termanager (
    struct bap_termanager *,
    struct bap_termanager *);

extern BAP_DLL void bap_init_zipterm_array_termanager (
    struct bap_termanager *,
    bap_zipterm *,
    ba0_int_p);

extern BAP_DLL void bap_set_zipterm_zipterm_termanager (
    struct bap_termanager *,
    bap_zipterm *,
    struct bap_termanager *,
    bap_zipterm);

extern BAP_DLL void bap_set_zipterm_term_termanager (
    struct bap_termanager *,
    bap_zipterm *,
    struct bav_term *);

extern BAP_DLL void bap_set_term_zipterm_termanager (
    struct bap_termanager *,
    struct bav_term *,
    bap_zipterm);

extern BAP_DLL ba0_garbage1_function bap_garbage1_termanager;

extern BAP_DLL ba0_garbage2_function bap_garbage2_termanager;

/* 
 * Should be garbage1 and garbage2 functions.
 */

extern BAP_DLL bool bap_worth_garbage_zipterm_termanager (
    struct bap_termanager *);

extern BAP_DLL ba0_int_p bap_garbage1_zipterm_termanager (
    struct bap_termanager *,
    bap_zipterm,
    enum ba0_garbage_code);

extern BAP_DLL bap_zipterm bap_garbage2_zipterm_termanager (
    struct bap_termanager *,
    bap_zipterm,
    enum ba0_garbage_code);

extern BAP_DLL void bap_switch_ring_termanager (
    struct bap_termanager *,
    struct bav_differential_ring *);

END_C_DECLS
#endif /* !BAP_TERMANAGER_H */
#if !defined (BAP_CLOT_mpz_H)
#   define BAP_CLOT_mpz_H 1

/* #   include "bap_common.h" */
/* #   include "bap_termanager.h" */

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
#if !defined (BAP_CLOT_mpzm_H)
#   define BAP_CLOT_mpzm_H 1

/* #   include "bap_common.h" */
/* #   include "bap_termanager.h" */

#   define BAD_FLAG_mpzm

BEGIN_C_DECLS

/*
 * texinfo: bap_table2of_monom_mpzm
 * This data type implements a contiguous linear combination
 * of zipterms. 
 */

struct bap_table2of_monom_mpzm
{
  ba0_int_p alloc;              // number of allocated entries for both arrays
  ba0_int_p size;               // number of used entries for both arrays
  bap_zipterm *zipterm;         // the array of zipterms
  ba0_mpzm_t *coeff;               // the array of coefficients
};


/*
 * texinfo: bap_tableof_table2of_monom_mpzm
 * This data type is a table of tables. 
 * However, if we forget technical details, it is a sequence of
 * pairs of the form (term, coefficient).
 * These pairs are called @dfn{monomials} in the documentation.
 */

struct bap_tableof_table2of_monom_mpzm
{
  ba0_int_p alloc;              // the number of allocated entries of tab
  ba0_int_p size;               // the number of used entries in tab
  struct bap_table2of_monom_mpzm **tab;
};


/*
 * texinfo: bap_clot_mpzm
 * This data type implements a clot i.e. a sequence of monomials
 * sorted in decreasing order w.r.t. the lexicographic ordering
 * induced by the current ordering.
 * The coefficients of monomials are nonzero.
 * Monomials are sometimes considered as numbered starting from @math{0}
 * in the documentation.
 */

struct bap_clot_mpzm
{
// the total number of allocated entries of (zipterm, coeff)
  ba0_int_p alloc;
// the total number of used entries i.e. of monomials
  ba0_int_p size;
// the termanager which handles zipterms
  struct bap_termanager tgest;
// the table of bap_table2of_monom_mpzm 
  struct bap_tableof_table2of_monom_mpzm tab;
// the ordering w.r.t. which zipterms are ordered
  bav_Iordering ordering;
};


extern BAP_DLL struct bap_clot_mpzm *bap_new_clot_mpzm (
    struct bav_term *);

extern BAP_DLL bool bap_is_zero_clot_mpzm (
    struct bap_clot_mpzm *);

extern BAP_DLL void bap_reverse_clot_mpzm (
    struct bap_clot_mpzm *);

extern BAP_DLL void bap_sort_clot_mpzm (
    struct bap_clot_mpzm *,
    ba0_int_p,
    ba0_int_p);

extern BAP_DLL void bap_change_ordering_clot_mpzm (
    struct bap_clot_mpzm *,
    bav_Iordering);

extern BAP_DLL ba0_garbage1_function bap_garbage1_clot_mpzm;

extern BAP_DLL ba0_garbage2_function bap_garbage2_clot_mpzm;

extern BAP_DLL ba0_copy_function bap_copy_clot_mpzm;

/*
 * texinfo: bap_itermon_clot_mpzm
 * This data type implements iterators of monomials over a clot.
 * In this context the monomial number @code{num.combined}
 * is located in @code{clot->tab[num.primary]->tab[num.secondary]}.
 * An iterator may be set outside a clot.
 */

struct bap_itermon_clot_mpzm
{
  struct bap_clot_mpzm *clot;
  struct bap_composite_number num;
};


extern BAP_DLL void bap_begin_itermon_clot_mpzm (
    struct bap_itermon_clot_mpzm *,
    struct bap_clot_mpzm *);

extern BAP_DLL void bap_end_itermon_clot_mpzm (
    struct bap_itermon_clot_mpzm *,
    struct bap_clot_mpzm *);

extern BAP_DLL bool bap_outof_itermon_clot_mpzm (
    struct bap_itermon_clot_mpzm *);

extern BAP_DLL void bap_next_itermon_clot_mpzm (
    struct bap_itermon_clot_mpzm *);

extern BAP_DLL void bap_prev_itermon_clot_mpzm (
    struct bap_itermon_clot_mpzm *);

extern BAP_DLL void bap_goto_itermon_clot_mpzm (
    struct bap_itermon_clot_mpzm *,
    ba0_int_p);

extern BAP_DLL ba0_int_p bap_number_itermon_clot_mpzm (
    struct bap_itermon_clot_mpzm *);

extern BAP_DLL void bap_term_itermon_clot_mpzm (
    struct bav_term *,
    struct bap_itermon_clot_mpzm *);

extern BAP_DLL ba0_mpzm_t *bap_coeff_itermon_clot_mpzm (
    struct bap_itermon_clot_mpzm *);

extern BAP_DLL void bap_swap_itermon_clot_mpzm (
    struct bap_itermon_clot_mpzm *,
    struct bap_itermon_clot_mpzm *);

/*
 * texinfo: bap_creator_clot_mpzm
 * This data type permits to create a clot monomial per monomial.
 * Monomials are stored in the clot by increasing number.
 * The creator permits to create clots whose monomials are not
 * sorted by decreasing order w.r.t. the lexicographic ordering
 * defined by the ranking. 
 * Creators rely on iterators of monomials over an already existing
 * clot which is then overwritten.
 */

struct bap_creator_clot_mpzm
{
  struct bap_itermon_clot_mpzm iter;
// the number of entries allocated to any new bap_table2of_monom_mpzm
  ba0_int_p table2of_monom_alloc;
};


extern BAP_DLL void bap_begin_creator_clot_mpzm (
    struct bap_creator_clot_mpzm *,
    struct bap_clot_mpzm *,
    struct bav_term *,
    ba0_int_p);

extern BAP_DLL void bap_append_creator_clot_mpzm (
    struct bap_creator_clot_mpzm *,
    struct bap_clot_mpzm *,
    ba0_int_p);

extern BAP_DLL void bap_write_creator_clot_mpzm (
    struct bap_creator_clot_mpzm *,
    struct bav_term *,
    ba0_mpzm_t);

extern BAP_DLL void bap_write_neg_creator_clot_mpzm (
    struct bap_creator_clot_mpzm *,
    struct bav_term *,
    ba0_mpzm_t);

extern BAP_DLL void bap_write_term_creator_clot_mpzm (
    struct bap_creator_clot_mpzm *,
    struct bav_term *);

extern BAP_DLL void bap_write_all_creator_clot_mpzm (
    struct bap_creator_clot_mpzm *,
    struct bap_clot_mpzm *,
    ba0_int_p,
    ba0_int_p);

extern BAP_DLL void bap_write_neg_all_creator_clot_mpzm (
    struct bap_creator_clot_mpzm *,
    struct bap_clot_mpzm *,
    ba0_int_p,
    ba0_int_p);

extern BAP_DLL void bap_write_mul_all_creator_clot_mpzm (
    struct bap_creator_clot_mpzm *,
    struct bap_clot_mpzm *,
    ba0_mpzm_t,
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

extern BAP_DLL void bap_close_creator_clot_mpzm (
    struct bap_creator_clot_mpzm *);

extern BAP_DLL void bap_goto_creator_clot_mpzm (
    struct bap_creator_clot_mpzm *,
    ba0_int_p);

extern BAP_DLL void bap_switch_ring_clot_mpzm (
    struct bap_clot_mpzm *,
    struct bav_differential_ring *);

END_C_DECLS
#   undef BAD_FLAG_mpzm
#endif /* !BAP_CLOT_mpzm_H */
#if !defined (BAP_CLOT_mpq_H)
#   define BAP_CLOT_mpq_H 1

/* #   include "bap_common.h" */
/* #   include "bap_termanager.h" */

#   define BAD_FLAG_mpq

BEGIN_C_DECLS

/*
 * texinfo: bap_table2of_monom_mpq
 * This data type implements a contiguous linear combination
 * of zipterms. 
 */

struct bap_table2of_monom_mpq
{
  ba0_int_p alloc;              // number of allocated entries for both arrays
  ba0_int_p size;               // number of used entries for both arrays
  bap_zipterm *zipterm;         // the array of zipterms
  ba0_mpq_t *coeff;               // the array of coefficients
};


/*
 * texinfo: bap_tableof_table2of_monom_mpq
 * This data type is a table of tables. 
 * However, if we forget technical details, it is a sequence of
 * pairs of the form (term, coefficient).
 * These pairs are called @dfn{monomials} in the documentation.
 */

struct bap_tableof_table2of_monom_mpq
{
  ba0_int_p alloc;              // the number of allocated entries of tab
  ba0_int_p size;               // the number of used entries in tab
  struct bap_table2of_monom_mpq **tab;
};


/*
 * texinfo: bap_clot_mpq
 * This data type implements a clot i.e. a sequence of monomials
 * sorted in decreasing order w.r.t. the lexicographic ordering
 * induced by the current ordering.
 * The coefficients of monomials are nonzero.
 * Monomials are sometimes considered as numbered starting from @math{0}
 * in the documentation.
 */

struct bap_clot_mpq
{
// the total number of allocated entries of (zipterm, coeff)
  ba0_int_p alloc;
// the total number of used entries i.e. of monomials
  ba0_int_p size;
// the termanager which handles zipterms
  struct bap_termanager tgest;
// the table of bap_table2of_monom_mpq 
  struct bap_tableof_table2of_monom_mpq tab;
// the ordering w.r.t. which zipterms are ordered
  bav_Iordering ordering;
};


extern BAP_DLL struct bap_clot_mpq *bap_new_clot_mpq (
    struct bav_term *);

extern BAP_DLL bool bap_is_zero_clot_mpq (
    struct bap_clot_mpq *);

extern BAP_DLL void bap_reverse_clot_mpq (
    struct bap_clot_mpq *);

extern BAP_DLL void bap_sort_clot_mpq (
    struct bap_clot_mpq *,
    ba0_int_p,
    ba0_int_p);

extern BAP_DLL void bap_change_ordering_clot_mpq (
    struct bap_clot_mpq *,
    bav_Iordering);

extern BAP_DLL ba0_garbage1_function bap_garbage1_clot_mpq;

extern BAP_DLL ba0_garbage2_function bap_garbage2_clot_mpq;

extern BAP_DLL ba0_copy_function bap_copy_clot_mpq;

/*
 * texinfo: bap_itermon_clot_mpq
 * This data type implements iterators of monomials over a clot.
 * In this context the monomial number @code{num.combined}
 * is located in @code{clot->tab[num.primary]->tab[num.secondary]}.
 * An iterator may be set outside a clot.
 */

struct bap_itermon_clot_mpq
{
  struct bap_clot_mpq *clot;
  struct bap_composite_number num;
};


extern BAP_DLL void bap_begin_itermon_clot_mpq (
    struct bap_itermon_clot_mpq *,
    struct bap_clot_mpq *);

extern BAP_DLL void bap_end_itermon_clot_mpq (
    struct bap_itermon_clot_mpq *,
    struct bap_clot_mpq *);

extern BAP_DLL bool bap_outof_itermon_clot_mpq (
    struct bap_itermon_clot_mpq *);

extern BAP_DLL void bap_next_itermon_clot_mpq (
    struct bap_itermon_clot_mpq *);

extern BAP_DLL void bap_prev_itermon_clot_mpq (
    struct bap_itermon_clot_mpq *);

extern BAP_DLL void bap_goto_itermon_clot_mpq (
    struct bap_itermon_clot_mpq *,
    ba0_int_p);

extern BAP_DLL ba0_int_p bap_number_itermon_clot_mpq (
    struct bap_itermon_clot_mpq *);

extern BAP_DLL void bap_term_itermon_clot_mpq (
    struct bav_term *,
    struct bap_itermon_clot_mpq *);

extern BAP_DLL ba0_mpq_t *bap_coeff_itermon_clot_mpq (
    struct bap_itermon_clot_mpq *);

extern BAP_DLL void bap_swap_itermon_clot_mpq (
    struct bap_itermon_clot_mpq *,
    struct bap_itermon_clot_mpq *);

/*
 * texinfo: bap_creator_clot_mpq
 * This data type permits to create a clot monomial per monomial.
 * Monomials are stored in the clot by increasing number.
 * The creator permits to create clots whose monomials are not
 * sorted by decreasing order w.r.t. the lexicographic ordering
 * defined by the ranking. 
 * Creators rely on iterators of monomials over an already existing
 * clot which is then overwritten.
 */

struct bap_creator_clot_mpq
{
  struct bap_itermon_clot_mpq iter;
// the number of entries allocated to any new bap_table2of_monom_mpq
  ba0_int_p table2of_monom_alloc;
};


extern BAP_DLL void bap_begin_creator_clot_mpq (
    struct bap_creator_clot_mpq *,
    struct bap_clot_mpq *,
    struct bav_term *,
    ba0_int_p);

extern BAP_DLL void bap_append_creator_clot_mpq (
    struct bap_creator_clot_mpq *,
    struct bap_clot_mpq *,
    ba0_int_p);

extern BAP_DLL void bap_write_creator_clot_mpq (
    struct bap_creator_clot_mpq *,
    struct bav_term *,
    ba0_mpq_t);

extern BAP_DLL void bap_write_neg_creator_clot_mpq (
    struct bap_creator_clot_mpq *,
    struct bav_term *,
    ba0_mpq_t);

extern BAP_DLL void bap_write_term_creator_clot_mpq (
    struct bap_creator_clot_mpq *,
    struct bav_term *);

extern BAP_DLL void bap_write_all_creator_clot_mpq (
    struct bap_creator_clot_mpq *,
    struct bap_clot_mpq *,
    ba0_int_p,
    ba0_int_p);

extern BAP_DLL void bap_write_neg_all_creator_clot_mpq (
    struct bap_creator_clot_mpq *,
    struct bap_clot_mpq *,
    ba0_int_p,
    ba0_int_p);

extern BAP_DLL void bap_write_mul_all_creator_clot_mpq (
    struct bap_creator_clot_mpq *,
    struct bap_clot_mpq *,
    ba0_mpq_t,
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

extern BAP_DLL void bap_close_creator_clot_mpq (
    struct bap_creator_clot_mpq *);

extern BAP_DLL void bap_goto_creator_clot_mpq (
    struct bap_creator_clot_mpq *,
    ba0_int_p);

extern BAP_DLL void bap_switch_ring_clot_mpq (
    struct bap_clot_mpq *,
    struct bav_differential_ring *);

END_C_DECLS
#   undef BAD_FLAG_mpq
#endif /* !BAP_CLOT_mpq_H */
#if !defined (BAP_CLOT_mint_hp_H)
#   define BAP_CLOT_mint_hp_H 1

/* #   include "bap_common.h" */
/* #   include "bap_termanager.h" */

#   define BAD_FLAG_mint_hp

BEGIN_C_DECLS

/*
 * texinfo: bap_table2of_monom_mint_hp
 * This data type implements a contiguous linear combination
 * of zipterms. 
 */

struct bap_table2of_monom_mint_hp
{
  ba0_int_p alloc;              // number of allocated entries for both arrays
  ba0_int_p size;               // number of used entries for both arrays
  bap_zipterm *zipterm;         // the array of zipterms
  ba0_mint_hp_t *coeff;               // the array of coefficients
};


/*
 * texinfo: bap_tableof_table2of_monom_mint_hp
 * This data type is a table of tables. 
 * However, if we forget technical details, it is a sequence of
 * pairs of the form (term, coefficient).
 * These pairs are called @dfn{monomials} in the documentation.
 */

struct bap_tableof_table2of_monom_mint_hp
{
  ba0_int_p alloc;              // the number of allocated entries of tab
  ba0_int_p size;               // the number of used entries in tab
  struct bap_table2of_monom_mint_hp **tab;
};


/*
 * texinfo: bap_clot_mint_hp
 * This data type implements a clot i.e. a sequence of monomials
 * sorted in decreasing order w.r.t. the lexicographic ordering
 * induced by the current ordering.
 * The coefficients of monomials are nonzero.
 * Monomials are sometimes considered as numbered starting from @math{0}
 * in the documentation.
 */

struct bap_clot_mint_hp
{
// the total number of allocated entries of (zipterm, coeff)
  ba0_int_p alloc;
// the total number of used entries i.e. of monomials
  ba0_int_p size;
// the termanager which handles zipterms
  struct bap_termanager tgest;
// the table of bap_table2of_monom_mint_hp 
  struct bap_tableof_table2of_monom_mint_hp tab;
// the ordering w.r.t. which zipterms are ordered
  bav_Iordering ordering;
};


extern BAP_DLL struct bap_clot_mint_hp *bap_new_clot_mint_hp (
    struct bav_term *);

extern BAP_DLL bool bap_is_zero_clot_mint_hp (
    struct bap_clot_mint_hp *);

extern BAP_DLL void bap_reverse_clot_mint_hp (
    struct bap_clot_mint_hp *);

extern BAP_DLL void bap_sort_clot_mint_hp (
    struct bap_clot_mint_hp *,
    ba0_int_p,
    ba0_int_p);

extern BAP_DLL void bap_change_ordering_clot_mint_hp (
    struct bap_clot_mint_hp *,
    bav_Iordering);

extern BAP_DLL ba0_garbage1_function bap_garbage1_clot_mint_hp;

extern BAP_DLL ba0_garbage2_function bap_garbage2_clot_mint_hp;

extern BAP_DLL ba0_copy_function bap_copy_clot_mint_hp;

/*
 * texinfo: bap_itermon_clot_mint_hp
 * This data type implements iterators of monomials over a clot.
 * In this context the monomial number @code{num.combined}
 * is located in @code{clot->tab[num.primary]->tab[num.secondary]}.
 * An iterator may be set outside a clot.
 */

struct bap_itermon_clot_mint_hp
{
  struct bap_clot_mint_hp *clot;
  struct bap_composite_number num;
};


extern BAP_DLL void bap_begin_itermon_clot_mint_hp (
    struct bap_itermon_clot_mint_hp *,
    struct bap_clot_mint_hp *);

extern BAP_DLL void bap_end_itermon_clot_mint_hp (
    struct bap_itermon_clot_mint_hp *,
    struct bap_clot_mint_hp *);

extern BAP_DLL bool bap_outof_itermon_clot_mint_hp (
    struct bap_itermon_clot_mint_hp *);

extern BAP_DLL void bap_next_itermon_clot_mint_hp (
    struct bap_itermon_clot_mint_hp *);

extern BAP_DLL void bap_prev_itermon_clot_mint_hp (
    struct bap_itermon_clot_mint_hp *);

extern BAP_DLL void bap_goto_itermon_clot_mint_hp (
    struct bap_itermon_clot_mint_hp *,
    ba0_int_p);

extern BAP_DLL ba0_int_p bap_number_itermon_clot_mint_hp (
    struct bap_itermon_clot_mint_hp *);

extern BAP_DLL void bap_term_itermon_clot_mint_hp (
    struct bav_term *,
    struct bap_itermon_clot_mint_hp *);

extern BAP_DLL ba0_mint_hp_t *bap_coeff_itermon_clot_mint_hp (
    struct bap_itermon_clot_mint_hp *);

extern BAP_DLL void bap_swap_itermon_clot_mint_hp (
    struct bap_itermon_clot_mint_hp *,
    struct bap_itermon_clot_mint_hp *);

/*
 * texinfo: bap_creator_clot_mint_hp
 * This data type permits to create a clot monomial per monomial.
 * Monomials are stored in the clot by increasing number.
 * The creator permits to create clots whose monomials are not
 * sorted by decreasing order w.r.t. the lexicographic ordering
 * defined by the ranking. 
 * Creators rely on iterators of monomials over an already existing
 * clot which is then overwritten.
 */

struct bap_creator_clot_mint_hp
{
  struct bap_itermon_clot_mint_hp iter;
// the number of entries allocated to any new bap_table2of_monom_mint_hp
  ba0_int_p table2of_monom_alloc;
};


extern BAP_DLL void bap_begin_creator_clot_mint_hp (
    struct bap_creator_clot_mint_hp *,
    struct bap_clot_mint_hp *,
    struct bav_term *,
    ba0_int_p);

extern BAP_DLL void bap_append_creator_clot_mint_hp (
    struct bap_creator_clot_mint_hp *,
    struct bap_clot_mint_hp *,
    ba0_int_p);

extern BAP_DLL void bap_write_creator_clot_mint_hp (
    struct bap_creator_clot_mint_hp *,
    struct bav_term *,
    ba0_mint_hp_t);

extern BAP_DLL void bap_write_neg_creator_clot_mint_hp (
    struct bap_creator_clot_mint_hp *,
    struct bav_term *,
    ba0_mint_hp_t);

extern BAP_DLL void bap_write_term_creator_clot_mint_hp (
    struct bap_creator_clot_mint_hp *,
    struct bav_term *);

extern BAP_DLL void bap_write_all_creator_clot_mint_hp (
    struct bap_creator_clot_mint_hp *,
    struct bap_clot_mint_hp *,
    ba0_int_p,
    ba0_int_p);

extern BAP_DLL void bap_write_neg_all_creator_clot_mint_hp (
    struct bap_creator_clot_mint_hp *,
    struct bap_clot_mint_hp *,
    ba0_int_p,
    ba0_int_p);

extern BAP_DLL void bap_write_mul_all_creator_clot_mint_hp (
    struct bap_creator_clot_mint_hp *,
    struct bap_clot_mint_hp *,
    ba0_mint_hp_t,
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

extern BAP_DLL void bap_close_creator_clot_mint_hp (
    struct bap_creator_clot_mint_hp *);

extern BAP_DLL void bap_goto_creator_clot_mint_hp (
    struct bap_creator_clot_mint_hp *,
    ba0_int_p);

extern BAP_DLL void bap_switch_ring_clot_mint_hp (
    struct bap_clot_mint_hp *,
    struct bav_differential_ring *);

END_C_DECLS
#   undef BAD_FLAG_mint_hp
#endif /* !BAP_CLOT_mint_hp_H */
#if !defined (BAP_TERMSTRIPPER_H)
#   define BAP_TERMSTRIPPER_H 1

/* #   include "bap_common.h" */

#   define BAP_TERMSTRIPPER_SIZE 3

BEGIN_C_DECLS

/* 
 * texinfo: bap_termstripper
 * This data type is involved in the process of taking coefficients of 
 * polynomials w.r.t. any variable. 
 *
 * It aims at stripping terms i.e. at cutting, in terms, all ranks 
 * which depend on variables strictly greater than a given variable.
 * The ordering w.r.t. which variables are compared is often not
 * the ordering of the clot. A stripping operation is thus described
 * by a pair (@code{variable}, @code{ordering}).
 *
 * The variable is allowed to be @code{BAV_NOT_A_VARIABLE} (i.e. @math{0}).
 * In that case, all variables are cut.
 * It is allowed to be @math{-1}. In that case, no variables are cut.
 *
 * It happens that a polynomial is obtained by performing a sequence
 * of stripping operations. This sequence, which is necessary to
 * recover the right stripped terms, is recorded.
 */

struct bap_termstripper
{
// the number of stripping operations recorded in tab
  ba0_int_p size;
  struct _tab
  {
    bav_Iordering ordering;
    struct bav_variable *varmax;
  } tab[BAP_TERMSTRIPPER_SIZE];
};


extern BAP_DLL void bap_init_set_termstripper (
    struct bap_termstripper *,
    struct bav_variable *,
    bav_Iordering);

extern BAP_DLL void bap_set_termstripper (
    struct bap_termstripper *,
    struct bap_termstripper *);

extern BAP_DLL void bap_change_ordering_termstripper (
    struct bap_termstripper *,
    bav_Iordering);

extern BAP_DLL void bap_change_variable_termstripper (
    struct bap_termstripper *,
    struct bav_variable *);

extern BAP_DLL void bap_append_termstripper (
    struct bap_termstripper *,
    struct bav_variable *,
    bav_Iordering);

extern BAP_DLL bool bap_identity_termstripper (
    struct bap_termstripper *,
    bav_Iordering);

extern BAP_DLL void bap_strip_term_termstripper (
    struct bav_term *,
    bav_Iordering,
    struct bap_termstripper *);

extern BAP_DLL void bap_switch_ring_termstripper (
    struct bap_termstripper *,
    struct bav_differential_ring *);

END_C_DECLS
#endif /* !BAP_TERMSTRIPPER_H */
#if !defined (BAP_SEQUENTIAL_ACCESS_H)
#   define BAP_SEQUENTIAL_ACCESS_H 1

/* #   include "bap_common.h" */

BEGIN_C_DECLS

/*
 * texinfo: bap_sequential_access
 * This data type permits to define a subsequence of monomials in a clot. 
 */

struct bap_sequential_access
{
// the index of the first monomial of the subsequence
  ba0_int_p first;
// the index of the first monomial following the subsequence
  ba0_int_p after;
};


END_C_DECLS
#endif /* !BAP_SEQUENTIAL_ACCESS_H */
#if !defined (BAP_INDEXED_ACCESS_H)
#   define BAP_INDEXED_ACCESS_H 1

/* #   include "bap_common.h" */

BEGIN_C_DECLS

/*
 * texinfo: bap_indexed_access
 * This data type permits to define a sequence of non consecutive 
 * monomials in a clot or in a polynomial, in any order. 
 * It is a table of tables of monomial numbers.
 * From a logical point of view, it is a sequence of monomial numbers.
 */

struct bap_indexed_access
{
// the total number of entries allocated to tab
  ba0_int_p alloc;
// the total number of entries used in tab
  ba0_int_p size;
  struct ba0_tableof_tableof_int_p tab;
};


extern BAP_DLL void bap_init_indexed_access (
    struct bap_indexed_access *);

extern BAP_DLL void bap_realloc_indexed_access (
    struct bap_indexed_access *,
    ba0_int_p);

extern BAP_DLL void bap_reverse_indexed_access (
    struct bap_indexed_access *);

extern BAP_DLL ba0_garbage1_function bap_garbage1_indexed_access;

extern BAP_DLL ba0_garbage2_function bap_garbage2_indexed_access;

END_C_DECLS
#endif /* !BAP_INDEXED_ACCESS_H */
#if !defined (BAP_ITERATOR_INDEX_H)
#   define BAP_ITERATOR_INDEX_H 1

/* #   include "bap_common.h" */
/* #   include "bap_indexed_access.h" */

BEGIN_C_DECLS

/*
 * texinfo: bap_iterator_indexed_access
 * This data structure implements an iterator over 
 * a @code{bap_indexed_access} structure.
 */

struct bap_iterator_indexed_access
{
  struct bap_indexed_access *ind;       // the structure being read
  struct bap_composite_number num;      // the current index
};


extern BAP_DLL void bap_begin_iterator_indexed_access (
    struct bap_iterator_indexed_access *,
    struct bap_indexed_access *);

extern BAP_DLL void bap_end_iterator_indexed_access (
    struct bap_iterator_indexed_access *,
    struct bap_indexed_access *);

extern BAP_DLL bool bap_outof_iterator_indexed_access (
    struct bap_iterator_indexed_access *);

extern BAP_DLL void bap_next_iterator_indexed_access (
    struct bap_iterator_indexed_access *);

extern BAP_DLL void bap_prev_iterator_indexed_access (
    struct bap_iterator_indexed_access *);

extern BAP_DLL void bap_goto_iterator_indexed_access (
    struct bap_iterator_indexed_access *,
    ba0_int_p);

extern BAP_DLL ba0_int_p bap_index_iterator_indexed_access (
    struct bap_iterator_indexed_access *);

extern BAP_DLL ba0_int_p bap_read_iterator_indexed_access (
    struct bap_iterator_indexed_access *);

extern BAP_DLL void bap_swapindex_iterator_indexed_access (
    struct bap_iterator_indexed_access *,
    struct bap_iterator_indexed_access *);

extern BAP_DLL void bap_set_iterator_indexed_access (
    struct bap_iterator_indexed_access *,
    struct bap_iterator_indexed_access *);


/*
 * texinfo: bap_creator_indexed_access
 * This data structure permits to rewrite the content of a
 * @code{bap_indexed_access} structure, provided that the
 * already allocated tables are large enough.
 */

struct bap_creator_indexed_access
{
  struct bap_indexed_access *ind;       // the structure being rewritten
  struct bap_composite_number num;      // the current index
};


extern BAP_DLL void bap_begin_creator_indexed_access (
    struct bap_creator_indexed_access *,
    struct bap_indexed_access *);

extern BAP_DLL void bap_write_creator_indexed_access (
    struct bap_creator_indexed_access *,
    ba0_int_p);

extern BAP_DLL void bap_close_creator_indexed_access (
    struct bap_creator_indexed_access *);

END_C_DECLS
#endif /* !BAP_ITERATOR_INDEX_H */
#if !defined (BAP_POLYNOM_mpz_H)
#   define BAP_POLYNOM_mpz_H 1

/* #   include "bap_common.h" */
/* #   include "bap_clot_mpz.h" */
/* #   include "bap_sequential_access.h" */
/* #   include "bap_indexed_access.h" */
/* #   include "bap_termstripper.h" */

#   define BAD_FLAG_mpz

BEGIN_C_DECLS

/*
 * texinfo: bap_polynom_mpz
 * This data type implements polynomials.
 * Note that the @code{total_rank} field contains the exact
 * total rank of the polynomial while the @code{total_rank} field 
 * of the term manager of its clot only contains a multiple
 * of this total rank.
 */

struct bap_polynom_mpz
{
  struct bap_clot_mpz *clot;  // the underlying clot
  struct bav_term total_rank;   // the total rank of the polynomial
  bool readonly;                // true if modifications are forbidden
  enum bap_typeof_monom_access access;
  struct bap_sequential_access seq;     // in case of a sequential access
  struct bap_indexed_access ind;        // in case of an indexed access
  struct bap_termstripper tstrip;       // for stripping terms
};


#   define BAP_NOT_A_POLYNOM_mpz	(struct bap_polynom_mpz*)0

struct bap_tableof_polynom_mpz
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bap_polynom_mpz **tab;
};

struct bap_listof_polynom_mpz
{
  struct bap_polynom_mpz *value;
  struct bap_listof_polynom_mpz *next;
};

struct bap_tableof_tableof_polynom_mpz
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bap_tableof_polynom_mpz **tab;
};

struct bap_tableof_listof_polynom_mpz
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bap_listof_polynom_mpz **tab;
};

extern BAP_DLL void bap_init_polynom_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_init_readonly_polynom_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_init_polynom_one_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_init_polynom_crk_mpz (
    struct bap_polynom_mpz *,
    ba0_mpz_t,
    struct bav_rank *);

extern BAP_DLL struct bap_polynom_mpz *bap_new_polynom_mpz (
    void);

extern BAP_DLL struct bap_polynom_mpz *bap_new_readonly_polynom_mpz (
    void);

extern BAP_DLL struct bap_polynom_mpz *bap_new_polynom_one_mpz (
    void);

extern BAP_DLL struct bap_polynom_mpz *bap_new_polynom_crk_mpz (
    ba0_mpz_t,
    struct bav_rank *);

extern BAP_DLL void bap_set_polynom_zero_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_set_polynom_one_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_set_polynom_crk_mpz (
    struct bap_polynom_mpz *,
    ba0_mpz_t,
    struct bav_rank *);

extern BAP_DLL void bap_set_polynom_variable_mpz (
    struct bap_polynom_mpz *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_set_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_set_tableof_polynom_mpz (
    struct bap_tableof_polynom_mpz *,
    struct bap_tableof_polynom_mpz *);

extern BAP_DLL void bap_set_tableof_tableof_polynom_mpz (
    struct bap_tableof_tableof_polynom_mpz *,
    struct bap_tableof_tableof_polynom_mpz *);

extern BAP_DLL void bap_set_readonly_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_set_polynom_term_mpz (
    struct bap_polynom_mpz *,
    struct bav_term *);

extern BAP_DLL void bap_set_polynom_monom_mpz (
    struct bap_polynom_mpz *,
    ba0_mpz_t,
    struct bav_term *);

extern BAP_DLL void bap_set_total_rank_polynom_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL bool bap_is_zero_polynom_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL bool bap_is_one_polynom_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL bool bap_is_numeric_polynom_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL bool bap_is_univariate_polynom_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL bool bap_depend_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAP_DLL bool bap_depend_only_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bav_tableof_variable *);

extern BAP_DLL bool bap_is_variable_polynom_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL bool bap_is_solved_polynom_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL bool bap_is_derivative_minus_independent_polynom_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL bool bap_is_rank_minus_monom_polynom_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL bool bap_are_disjoint_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL enum ba0_compare_code bap_compare_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL bool bap_equal_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL ba0_cmp_function bap_gt_rank_polynom_mpz;

extern BAP_DLL ba0_cmp_function bap_lt_rank_polynom_mpz;

extern BAP_DLL bool bap_equal_rank_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL int bap_compare_rank_polynom_mpz (
    const void *,
    const void *);

extern BAP_DLL void bap_reverse_polynom_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_mark_indets_polynom_mpz (
    struct bav_dictionary_variable *,
    struct bav_tableof_variable *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_mark_indets_tableof_polynom_mpz (
    struct bav_dictionary_variable *,
    struct bav_tableof_variable *,
    struct bap_tableof_polynom_mpz *);

extern BAP_DLL void bap_mark_indets_listof_polynom_mpz (
    struct bav_dictionary_variable *,
    struct bav_tableof_variable *,
    struct bap_listof_polynom_mpz *);

extern BAP_DLL void bap_mark_ranks_polynom_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_sort_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_physort_polynom_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL ba0_int_p bap_nbmon_polynom_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_minimal_total_rank_polynom_mpz (
    struct bav_term *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_leading_term_polynom_mpz (
    struct bav_term *,
    struct bap_polynom_mpz *);

extern BAP_DLL struct bav_variable *bap_leader_polynom_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL struct bav_rank bap_rank_polynom_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL bav_Idegree bap_leading_degree_polynom_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL bav_Idegree bap_degree_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAP_DLL bav_Idegree bap_total_degree_polynom_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL bav_Iorder bap_total_order_polynom_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL ba0_mpz_t *bap_numeric_initial_polynom_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_initial_and_reductum_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_initial_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_reductum_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_initial_and_reductum2_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAP_DLL void bap_initial2_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAP_DLL void bap_reductum2_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAP_DLL void bap_coeff2_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_lcoeff_and_reductum_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAP_DLL void bap_lcoeff_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAP_DLL void bap_coeff_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_coeff_and_reductum_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_replace_initial_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_separant_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_separant2_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAP_DLL void bap_sort_tableof_polynom_mpz (
    struct bap_tableof_polynom_mpz *,
    enum ba0_sort_mode);

extern BAP_DLL unsigned ba0_int_p bap_sizeof_polynom_mpz (
    struct bap_polynom_mpz *,
    enum ba0_garbage_code);

extern BAP_DLL void bap_switch_ring_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bav_differential_ring *);

extern BAP_DLL ba0_garbage1_function bap_garbage1_polynom_mpz;

extern BAP_DLL ba0_garbage2_function bap_garbage2_polynom_mpz;

extern BAP_DLL ba0_copy_function bap_copy_polynom_mpz;

END_C_DECLS
#   undef  BAD_FLAG_mpz
#endif /* !BAP_POLYNOM_mpz_H */
#if !defined (BAP_POLYNOM_mpzm_H)
#   define BAP_POLYNOM_mpzm_H 1

/* #   include "bap_common.h" */
/* #   include "bap_clot_mpzm.h" */
/* #   include "bap_sequential_access.h" */
/* #   include "bap_indexed_access.h" */
/* #   include "bap_termstripper.h" */

#   define BAD_FLAG_mpzm

BEGIN_C_DECLS

/*
 * texinfo: bap_polynom_mpzm
 * This data type implements polynomials.
 * Note that the @code{total_rank} field contains the exact
 * total rank of the polynomial while the @code{total_rank} field 
 * of the term manager of its clot only contains a multiple
 * of this total rank.
 */

struct bap_polynom_mpzm
{
  struct bap_clot_mpzm *clot;  // the underlying clot
  struct bav_term total_rank;   // the total rank of the polynomial
  bool readonly;                // true if modifications are forbidden
  enum bap_typeof_monom_access access;
  struct bap_sequential_access seq;     // in case of a sequential access
  struct bap_indexed_access ind;        // in case of an indexed access
  struct bap_termstripper tstrip;       // for stripping terms
};


#   define BAP_NOT_A_POLYNOM_mpzm	(struct bap_polynom_mpzm*)0

struct bap_tableof_polynom_mpzm
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bap_polynom_mpzm **tab;
};

struct bap_listof_polynom_mpzm
{
  struct bap_polynom_mpzm *value;
  struct bap_listof_polynom_mpzm *next;
};

struct bap_tableof_tableof_polynom_mpzm
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bap_tableof_polynom_mpzm **tab;
};

struct bap_tableof_listof_polynom_mpzm
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bap_listof_polynom_mpzm **tab;
};

extern BAP_DLL void bap_init_polynom_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_init_readonly_polynom_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_init_polynom_one_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_init_polynom_crk_mpzm (
    struct bap_polynom_mpzm *,
    ba0_mpzm_t,
    struct bav_rank *);

extern BAP_DLL struct bap_polynom_mpzm *bap_new_polynom_mpzm (
    void);

extern BAP_DLL struct bap_polynom_mpzm *bap_new_readonly_polynom_mpzm (
    void);

extern BAP_DLL struct bap_polynom_mpzm *bap_new_polynom_one_mpzm (
    void);

extern BAP_DLL struct bap_polynom_mpzm *bap_new_polynom_crk_mpzm (
    ba0_mpzm_t,
    struct bav_rank *);

extern BAP_DLL void bap_set_polynom_zero_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_set_polynom_one_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_set_polynom_crk_mpzm (
    struct bap_polynom_mpzm *,
    ba0_mpzm_t,
    struct bav_rank *);

extern BAP_DLL void bap_set_polynom_variable_mpzm (
    struct bap_polynom_mpzm *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_set_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_set_tableof_polynom_mpzm (
    struct bap_tableof_polynom_mpzm *,
    struct bap_tableof_polynom_mpzm *);

extern BAP_DLL void bap_set_tableof_tableof_polynom_mpzm (
    struct bap_tableof_tableof_polynom_mpzm *,
    struct bap_tableof_tableof_polynom_mpzm *);

extern BAP_DLL void bap_set_readonly_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_set_polynom_term_mpzm (
    struct bap_polynom_mpzm *,
    struct bav_term *);

extern BAP_DLL void bap_set_polynom_monom_mpzm (
    struct bap_polynom_mpzm *,
    ba0_mpzm_t,
    struct bav_term *);

extern BAP_DLL void bap_set_total_rank_polynom_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL bool bap_is_zero_polynom_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL bool bap_is_one_polynom_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL bool bap_is_numeric_polynom_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL bool bap_is_univariate_polynom_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL bool bap_depend_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bav_variable *);

extern BAP_DLL bool bap_depend_only_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bav_tableof_variable *);

extern BAP_DLL bool bap_is_variable_polynom_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL bool bap_is_solved_polynom_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL bool bap_is_derivative_minus_independent_polynom_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL bool bap_is_rank_minus_monom_polynom_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL bool bap_are_disjoint_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL enum ba0_compare_code bap_compare_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL bool bap_equal_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL ba0_cmp_function bap_gt_rank_polynom_mpzm;

extern BAP_DLL ba0_cmp_function bap_lt_rank_polynom_mpzm;

extern BAP_DLL bool bap_equal_rank_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL int bap_compare_rank_polynom_mpzm (
    const void *,
    const void *);

extern BAP_DLL void bap_reverse_polynom_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_mark_indets_polynom_mpzm (
    struct bav_dictionary_variable *,
    struct bav_tableof_variable *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_mark_indets_tableof_polynom_mpzm (
    struct bav_dictionary_variable *,
    struct bav_tableof_variable *,
    struct bap_tableof_polynom_mpzm *);

extern BAP_DLL void bap_mark_indets_listof_polynom_mpzm (
    struct bav_dictionary_variable *,
    struct bav_tableof_variable *,
    struct bap_listof_polynom_mpzm *);

extern BAP_DLL void bap_mark_ranks_polynom_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_sort_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_physort_polynom_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL ba0_int_p bap_nbmon_polynom_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_minimal_total_rank_polynom_mpzm (
    struct bav_term *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_leading_term_polynom_mpzm (
    struct bav_term *,
    struct bap_polynom_mpzm *);

extern BAP_DLL struct bav_variable *bap_leader_polynom_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL struct bav_rank bap_rank_polynom_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL bav_Idegree bap_leading_degree_polynom_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL bav_Idegree bap_degree_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bav_variable *);

extern BAP_DLL bav_Idegree bap_total_degree_polynom_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL bav_Iorder bap_total_order_polynom_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL ba0_mpzm_t *bap_numeric_initial_polynom_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_initial_and_reductum_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_initial_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_reductum_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_initial_and_reductum2_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *);

extern BAP_DLL void bap_initial2_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *);

extern BAP_DLL void bap_reductum2_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *);

extern BAP_DLL void bap_coeff2_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_lcoeff_and_reductum_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *);

extern BAP_DLL void bap_lcoeff_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *);

extern BAP_DLL void bap_coeff_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_coeff_and_reductum_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_replace_initial_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_separant_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_separant2_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *);

extern BAP_DLL void bap_sort_tableof_polynom_mpzm (
    struct bap_tableof_polynom_mpzm *,
    enum ba0_sort_mode);

extern BAP_DLL unsigned ba0_int_p bap_sizeof_polynom_mpzm (
    struct bap_polynom_mpzm *,
    enum ba0_garbage_code);

extern BAP_DLL void bap_switch_ring_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bav_differential_ring *);

extern BAP_DLL ba0_garbage1_function bap_garbage1_polynom_mpzm;

extern BAP_DLL ba0_garbage2_function bap_garbage2_polynom_mpzm;

extern BAP_DLL ba0_copy_function bap_copy_polynom_mpzm;

END_C_DECLS
#   undef  BAD_FLAG_mpzm
#endif /* !BAP_POLYNOM_mpzm_H */
#if !defined (BAP_POLYNOM_mpq_H)
#   define BAP_POLYNOM_mpq_H 1

/* #   include "bap_common.h" */
/* #   include "bap_clot_mpq.h" */
/* #   include "bap_sequential_access.h" */
/* #   include "bap_indexed_access.h" */
/* #   include "bap_termstripper.h" */

#   define BAD_FLAG_mpq

BEGIN_C_DECLS

/*
 * texinfo: bap_polynom_mpq
 * This data type implements polynomials.
 * Note that the @code{total_rank} field contains the exact
 * total rank of the polynomial while the @code{total_rank} field 
 * of the term manager of its clot only contains a multiple
 * of this total rank.
 */

struct bap_polynom_mpq
{
  struct bap_clot_mpq *clot;  // the underlying clot
  struct bav_term total_rank;   // the total rank of the polynomial
  bool readonly;                // true if modifications are forbidden
  enum bap_typeof_monom_access access;
  struct bap_sequential_access seq;     // in case of a sequential access
  struct bap_indexed_access ind;        // in case of an indexed access
  struct bap_termstripper tstrip;       // for stripping terms
};


#   define BAP_NOT_A_POLYNOM_mpq	(struct bap_polynom_mpq*)0

struct bap_tableof_polynom_mpq
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bap_polynom_mpq **tab;
};

struct bap_listof_polynom_mpq
{
  struct bap_polynom_mpq *value;
  struct bap_listof_polynom_mpq *next;
};

struct bap_tableof_tableof_polynom_mpq
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bap_tableof_polynom_mpq **tab;
};

struct bap_tableof_listof_polynom_mpq
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bap_listof_polynom_mpq **tab;
};

extern BAP_DLL void bap_init_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_init_readonly_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_init_polynom_one_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_init_polynom_crk_mpq (
    struct bap_polynom_mpq *,
    ba0_mpq_t,
    struct bav_rank *);

extern BAP_DLL struct bap_polynom_mpq *bap_new_polynom_mpq (
    void);

extern BAP_DLL struct bap_polynom_mpq *bap_new_readonly_polynom_mpq (
    void);

extern BAP_DLL struct bap_polynom_mpq *bap_new_polynom_one_mpq (
    void);

extern BAP_DLL struct bap_polynom_mpq *bap_new_polynom_crk_mpq (
    ba0_mpq_t,
    struct bav_rank *);

extern BAP_DLL void bap_set_polynom_zero_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_set_polynom_one_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_set_polynom_crk_mpq (
    struct bap_polynom_mpq *,
    ba0_mpq_t,
    struct bav_rank *);

extern BAP_DLL void bap_set_polynom_variable_mpq (
    struct bap_polynom_mpq *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_set_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_set_tableof_polynom_mpq (
    struct bap_tableof_polynom_mpq *,
    struct bap_tableof_polynom_mpq *);

extern BAP_DLL void bap_set_tableof_tableof_polynom_mpq (
    struct bap_tableof_tableof_polynom_mpq *,
    struct bap_tableof_tableof_polynom_mpq *);

extern BAP_DLL void bap_set_readonly_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_set_polynom_term_mpq (
    struct bap_polynom_mpq *,
    struct bav_term *);

extern BAP_DLL void bap_set_polynom_monom_mpq (
    struct bap_polynom_mpq *,
    ba0_mpq_t,
    struct bav_term *);

extern BAP_DLL void bap_set_total_rank_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL bool bap_is_zero_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL bool bap_is_one_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL bool bap_is_numeric_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL bool bap_is_univariate_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL bool bap_depend_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL bool bap_depend_only_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bav_tableof_variable *);

extern BAP_DLL bool bap_is_variable_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL bool bap_is_solved_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL bool bap_is_derivative_minus_independent_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL bool bap_is_rank_minus_monom_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL bool bap_are_disjoint_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL enum ba0_compare_code bap_compare_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL bool bap_equal_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL ba0_cmp_function bap_gt_rank_polynom_mpq;

extern BAP_DLL ba0_cmp_function bap_lt_rank_polynom_mpq;

extern BAP_DLL bool bap_equal_rank_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL int bap_compare_rank_polynom_mpq (
    const void *,
    const void *);

extern BAP_DLL void bap_reverse_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_mark_indets_polynom_mpq (
    struct bav_dictionary_variable *,
    struct bav_tableof_variable *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_mark_indets_tableof_polynom_mpq (
    struct bav_dictionary_variable *,
    struct bav_tableof_variable *,
    struct bap_tableof_polynom_mpq *);

extern BAP_DLL void bap_mark_indets_listof_polynom_mpq (
    struct bav_dictionary_variable *,
    struct bav_tableof_variable *,
    struct bap_listof_polynom_mpq *);

extern BAP_DLL void bap_mark_ranks_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_sort_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_physort_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL ba0_int_p bap_nbmon_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_minimal_total_rank_polynom_mpq (
    struct bav_term *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_leading_term_polynom_mpq (
    struct bav_term *,
    struct bap_polynom_mpq *);

extern BAP_DLL struct bav_variable *bap_leader_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL struct bav_rank bap_rank_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL bav_Idegree bap_leading_degree_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL bav_Idegree bap_degree_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL bav_Idegree bap_total_degree_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL bav_Iorder bap_total_order_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL ba0_mpq_t *bap_numeric_initial_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_initial_and_reductum_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_initial_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_reductum_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_initial_and_reductum2_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL void bap_initial2_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL void bap_reductum2_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL void bap_coeff2_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_lcoeff_and_reductum_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL void bap_lcoeff_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL void bap_coeff_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_coeff_and_reductum_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_replace_initial_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_separant_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_separant2_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL void bap_sort_tableof_polynom_mpq (
    struct bap_tableof_polynom_mpq *,
    enum ba0_sort_mode);

extern BAP_DLL unsigned ba0_int_p bap_sizeof_polynom_mpq (
    struct bap_polynom_mpq *,
    enum ba0_garbage_code);

extern BAP_DLL void bap_switch_ring_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bav_differential_ring *);

extern BAP_DLL ba0_garbage1_function bap_garbage1_polynom_mpq;

extern BAP_DLL ba0_garbage2_function bap_garbage2_polynom_mpq;

extern BAP_DLL ba0_copy_function bap_copy_polynom_mpq;

END_C_DECLS
#   undef  BAD_FLAG_mpq
#endif /* !BAP_POLYNOM_mpq_H */
#if !defined (BAP_POLYNOM_mint_hp_H)
#   define BAP_POLYNOM_mint_hp_H 1

/* #   include "bap_common.h" */
/* #   include "bap_clot_mint_hp.h" */
/* #   include "bap_sequential_access.h" */
/* #   include "bap_indexed_access.h" */
/* #   include "bap_termstripper.h" */

#   define BAD_FLAG_mint_hp

BEGIN_C_DECLS

/*
 * texinfo: bap_polynom_mint_hp
 * This data type implements polynomials.
 * Note that the @code{total_rank} field contains the exact
 * total rank of the polynomial while the @code{total_rank} field 
 * of the term manager of its clot only contains a multiple
 * of this total rank.
 */

struct bap_polynom_mint_hp
{
  struct bap_clot_mint_hp *clot;  // the underlying clot
  struct bav_term total_rank;   // the total rank of the polynomial
  bool readonly;                // true if modifications are forbidden
  enum bap_typeof_monom_access access;
  struct bap_sequential_access seq;     // in case of a sequential access
  struct bap_indexed_access ind;        // in case of an indexed access
  struct bap_termstripper tstrip;       // for stripping terms
};


#   define BAP_NOT_A_POLYNOM_mint_hp	(struct bap_polynom_mint_hp*)0

struct bap_tableof_polynom_mint_hp
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bap_polynom_mint_hp **tab;
};

struct bap_listof_polynom_mint_hp
{
  struct bap_polynom_mint_hp *value;
  struct bap_listof_polynom_mint_hp *next;
};

struct bap_tableof_tableof_polynom_mint_hp
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bap_tableof_polynom_mint_hp **tab;
};

struct bap_tableof_listof_polynom_mint_hp
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bap_listof_polynom_mint_hp **tab;
};

extern BAP_DLL void bap_init_polynom_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_init_readonly_polynom_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_init_polynom_one_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_init_polynom_crk_mint_hp (
    struct bap_polynom_mint_hp *,
    ba0_mint_hp_t,
    struct bav_rank *);

extern BAP_DLL struct bap_polynom_mint_hp *bap_new_polynom_mint_hp (
    void);

extern BAP_DLL struct bap_polynom_mint_hp *bap_new_readonly_polynom_mint_hp (
    void);

extern BAP_DLL struct bap_polynom_mint_hp *bap_new_polynom_one_mint_hp (
    void);

extern BAP_DLL struct bap_polynom_mint_hp *bap_new_polynom_crk_mint_hp (
    ba0_mint_hp_t,
    struct bav_rank *);

extern BAP_DLL void bap_set_polynom_zero_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_set_polynom_one_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_set_polynom_crk_mint_hp (
    struct bap_polynom_mint_hp *,
    ba0_mint_hp_t,
    struct bav_rank *);

extern BAP_DLL void bap_set_polynom_variable_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_set_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_set_tableof_polynom_mint_hp (
    struct bap_tableof_polynom_mint_hp *,
    struct bap_tableof_polynom_mint_hp *);

extern BAP_DLL void bap_set_tableof_tableof_polynom_mint_hp (
    struct bap_tableof_tableof_polynom_mint_hp *,
    struct bap_tableof_tableof_polynom_mint_hp *);

extern BAP_DLL void bap_set_readonly_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_set_polynom_term_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bav_term *);

extern BAP_DLL void bap_set_polynom_monom_mint_hp (
    struct bap_polynom_mint_hp *,
    ba0_mint_hp_t,
    struct bav_term *);

extern BAP_DLL void bap_set_total_rank_polynom_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL bool bap_is_zero_polynom_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL bool bap_is_one_polynom_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL bool bap_is_numeric_polynom_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL bool bap_is_univariate_polynom_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL bool bap_depend_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

extern BAP_DLL bool bap_depend_only_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bav_tableof_variable *);

extern BAP_DLL bool bap_is_variable_polynom_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL bool bap_is_solved_polynom_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL bool bap_is_derivative_minus_independent_polynom_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL bool bap_is_rank_minus_monom_polynom_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL bool bap_are_disjoint_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL enum ba0_compare_code bap_compare_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL bool bap_equal_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL ba0_cmp_function bap_gt_rank_polynom_mint_hp;

extern BAP_DLL ba0_cmp_function bap_lt_rank_polynom_mint_hp;

extern BAP_DLL bool bap_equal_rank_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL int bap_compare_rank_polynom_mint_hp (
    const void *,
    const void *);

extern BAP_DLL void bap_reverse_polynom_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_mark_indets_polynom_mint_hp (
    struct bav_dictionary_variable *,
    struct bav_tableof_variable *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_mark_indets_tableof_polynom_mint_hp (
    struct bav_dictionary_variable *,
    struct bav_tableof_variable *,
    struct bap_tableof_polynom_mint_hp *);

extern BAP_DLL void bap_mark_indets_listof_polynom_mint_hp (
    struct bav_dictionary_variable *,
    struct bav_tableof_variable *,
    struct bap_listof_polynom_mint_hp *);

extern BAP_DLL void bap_mark_ranks_polynom_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_sort_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_physort_polynom_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL ba0_int_p bap_nbmon_polynom_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_minimal_total_rank_polynom_mint_hp (
    struct bav_term *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_leading_term_polynom_mint_hp (
    struct bav_term *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL struct bav_variable *bap_leader_polynom_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL struct bav_rank bap_rank_polynom_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL bav_Idegree bap_leading_degree_polynom_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL bav_Idegree bap_degree_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

extern BAP_DLL bav_Idegree bap_total_degree_polynom_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL bav_Iorder bap_total_order_polynom_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL ba0_mint_hp_t *bap_numeric_initial_polynom_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_initial_and_reductum_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_initial_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_reductum_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_initial_and_reductum2_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

extern BAP_DLL void bap_initial2_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

extern BAP_DLL void bap_reductum2_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

extern BAP_DLL void bap_coeff2_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_lcoeff_and_reductum_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

extern BAP_DLL void bap_lcoeff_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

extern BAP_DLL void bap_coeff_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_coeff_and_reductum_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_replace_initial_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_separant_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_separant2_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

extern BAP_DLL void bap_sort_tableof_polynom_mint_hp (
    struct bap_tableof_polynom_mint_hp *,
    enum ba0_sort_mode);

extern BAP_DLL unsigned ba0_int_p bap_sizeof_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    enum ba0_garbage_code);

extern BAP_DLL void bap_switch_ring_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bav_differential_ring *);

extern BAP_DLL ba0_garbage1_function bap_garbage1_polynom_mint_hp;

extern BAP_DLL ba0_garbage2_function bap_garbage2_polynom_mint_hp;

extern BAP_DLL ba0_copy_function bap_copy_polynom_mint_hp;

END_C_DECLS
#   undef  BAD_FLAG_mint_hp
#endif /* !BAP_POLYNOM_mint_hp_H */
#if !defined (BAP__CHECK_mpz_H)
#   define BAP__CHECK_mpz_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mpz.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpz

extern BAP_DLL void bap__check_ordering_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL void bap__check_compatible_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

#   undef BAD_FLAG_mpz

END_C_DECLS
#endif /* !BAP__CHECK_mpz_H */
#if !defined (BAP__CHECK_mpzm_H)
#   define BAP__CHECK_mpzm_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mpzm.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpzm

extern BAP_DLL void bap__check_ordering_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap__check_compatible_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

#   undef BAD_FLAG_mpzm

END_C_DECLS
#endif /* !BAP__CHECK_mpzm_H */
#if !defined (BAP__CHECK_mpq_H)
#   define BAP__CHECK_mpq_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mpq.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpq

extern BAP_DLL void bap__check_ordering_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL void bap__check_compatible_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

#   undef BAD_FLAG_mpq

END_C_DECLS
#endif /* !BAP__CHECK_mpq_H */
#if !defined (BAP__CHECK_mint_hp_H)
#   define BAP__CHECK_mint_hp_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mint_hp.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mint_hp

extern BAP_DLL void bap__check_ordering_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap__check_compatible_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

#   undef BAD_FLAG_mint_hp

END_C_DECLS
#endif /* !BAP__CHECK_mint_hp_H */
#if !defined (BAP_ADD_POLYNOM_mpz_H)
#   define BAP_ADD_POLYNOM_mpz_H 1

/* #   include "bap_polynom_mpz.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpz

extern BAP_DLL void bap_add_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_add_polynom_numeric_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    ba0_mpz_t);

extern BAP_DLL void bap_sub_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_submulmon_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_term *,
    ba0_mpz_t);

extern BAP_DLL void bap_comblin_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    ba0_int_p,
    struct bap_polynom_mpz *,
    ba0_int_p);

extern BAP_DLL void bap_addmulrk_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_rank *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_submulrk_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_rank *,
    struct bap_polynom_mpz *);

#   undef  BAD_FLAG_mpz

END_C_DECLS
#endif /* !BAP_ADD_POLYNOM_mpz_H */
#if !defined (BAP_ADD_POLYNOM_mpzm_H)
#   define BAP_ADD_POLYNOM_mpzm_H 1

/* #   include "bap_polynom_mpzm.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpzm

extern BAP_DLL void bap_add_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_add_polynom_numeric_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    ba0_mpzm_t);

extern BAP_DLL void bap_sub_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_submulmon_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_term *,
    ba0_mpzm_t);

extern BAP_DLL void bap_comblin_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    ba0_int_p,
    struct bap_polynom_mpzm *,
    ba0_int_p);

extern BAP_DLL void bap_addmulrk_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_rank *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_submulrk_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_rank *,
    struct bap_polynom_mpzm *);

#   undef  BAD_FLAG_mpzm

END_C_DECLS
#endif /* !BAP_ADD_POLYNOM_mpzm_H */
#if !defined (BAP_ADD_POLYNOM_mpq_H)
#   define BAP_ADD_POLYNOM_mpq_H 1

/* #   include "bap_polynom_mpq.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpq

extern BAP_DLL void bap_add_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_add_polynom_numeric_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    ba0_mpq_t);

extern BAP_DLL void bap_sub_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_submulmon_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_term *,
    ba0_mpq_t);

extern BAP_DLL void bap_comblin_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    ba0_int_p,
    struct bap_polynom_mpq *,
    ba0_int_p);

extern BAP_DLL void bap_addmulrk_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_rank *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_submulrk_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_rank *,
    struct bap_polynom_mpq *);

#   undef  BAD_FLAG_mpq

END_C_DECLS
#endif /* !BAP_ADD_POLYNOM_mpq_H */
#if !defined (BAP_ADD_POLYNOM_mint_hp_H)
#   define BAP_ADD_POLYNOM_mint_hp_H 1

/* #   include "bap_polynom_mint_hp.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mint_hp

extern BAP_DLL void bap_add_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_add_polynom_numeric_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    ba0_mint_hp_t);

extern BAP_DLL void bap_sub_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_submulmon_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_term *,
    ba0_mint_hp_t);

extern BAP_DLL void bap_comblin_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    ba0_int_p,
    struct bap_polynom_mint_hp *,
    ba0_int_p);

extern BAP_DLL void bap_addmulrk_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_rank *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_submulrk_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_rank *,
    struct bap_polynom_mint_hp *);

#   undef  BAD_FLAG_mint_hp

END_C_DECLS
#endif /* !BAP_ADD_POLYNOM_mint_hp_H */
#if !defined (BAP_MUL_POLYNOM_mpz_H)
#   define BAP_MUL_POLYNOM_mpz_H 1

/* #   include "bap_polynom_mpz.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpz

extern BAP_DLL void bap_neg_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_mul_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_mul_polynom_variable_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_mul_polynom_term_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_term *);

extern BAP_DLL void bap_mul_polynom_monom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    ba0_mpz_t,
    struct bav_term *);

extern BAP_DLL void bap_mul_polynom_numeric_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    ba0_mpz_t);

extern BAP_DLL void bap_mul_polynom_value_int_p_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_value_int_p *);

extern BAP_DLL void bap_pow_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    bav_Idegree);

#   undef  BAD_FLAG_mpz

END_C_DECLS
#endif /* !BAP_MUL_POLYNOM_mpz_H */
#if !defined (BAP_MUL_POLYNOM_mpzm_H)
#   define BAP_MUL_POLYNOM_mpzm_H 1

/* #   include "bap_polynom_mpzm.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpzm

extern BAP_DLL void bap_neg_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_mul_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_mul_polynom_variable_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_mul_polynom_term_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_term *);

extern BAP_DLL void bap_mul_polynom_monom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    ba0_mpzm_t,
    struct bav_term *);

extern BAP_DLL void bap_mul_polynom_numeric_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    ba0_mpzm_t);

extern BAP_DLL void bap_mul_polynom_value_int_p_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_value_int_p *);

extern BAP_DLL void bap_pow_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    bav_Idegree);

#   undef  BAD_FLAG_mpzm

END_C_DECLS
#endif /* !BAP_MUL_POLYNOM_mpzm_H */
#if !defined (BAP_MUL_POLYNOM_mpq_H)
#   define BAP_MUL_POLYNOM_mpq_H 1

/* #   include "bap_polynom_mpq.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpq

extern BAP_DLL void bap_neg_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_mul_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_mul_polynom_variable_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_mul_polynom_term_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_term *);

extern BAP_DLL void bap_mul_polynom_monom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    ba0_mpq_t,
    struct bav_term *);

extern BAP_DLL void bap_mul_polynom_numeric_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    ba0_mpq_t);

extern BAP_DLL void bap_mul_polynom_value_int_p_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_value_int_p *);

extern BAP_DLL void bap_pow_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    bav_Idegree);

#   undef  BAD_FLAG_mpq

END_C_DECLS
#endif /* !BAP_MUL_POLYNOM_mpq_H */
#if !defined (BAP_MUL_POLYNOM_mint_hp_H)
#   define BAP_MUL_POLYNOM_mint_hp_H 1

/* #   include "bap_polynom_mint_hp.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mint_hp

extern BAP_DLL void bap_neg_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_mul_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_mul_polynom_variable_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *,
    bav_Idegree);

extern BAP_DLL void bap_mul_polynom_term_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_term *);

extern BAP_DLL void bap_mul_polynom_monom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    ba0_mint_hp_t,
    struct bav_term *);

extern BAP_DLL void bap_mul_polynom_numeric_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    ba0_mint_hp_t);

extern BAP_DLL void bap_mul_polynom_value_int_p_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_value_int_p *);

extern BAP_DLL void bap_pow_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    bav_Idegree);

#   undef  BAD_FLAG_mint_hp

END_C_DECLS
#endif /* !BAP_MUL_POLYNOM_mint_hp_H */
#if !defined (BAP_PREM_POLYNOM_mpz_H)
#   define BAP_PREM_POLYNOM_mpz_H 1

/* #   include "bap_polynom_mpz.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpz

extern BAP_DLL bool bap_is_numeric_factor_polynom_mpz (
    struct bap_polynom_mpz *,
    ba0_mpz_t,
    struct bap_polynom_mpz *);

extern BAP_DLL bool bap_is_variable_factor_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bav_variable *,
    bav_Idegree *);

extern BAP_DLL bool bap_is_factor_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL bool bap_is_factor_tableof_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_tableof_polynom_mpz *);

extern BAP_DLL void bap_exquo_polynom_term_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_term *);

extern BAP_DLL void bap_exquo_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

struct bap_product_mpz;

extern BAP_DLL void bap_exquo_polynom_product_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_product_mpz *);

extern BAP_DLL void bap_pseudo_division_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    bav_Idegree *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAP_DLL void bap_prem_polynom_mpz (
    struct bap_polynom_mpz *,
    bav_Idegree *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAP_DLL void bap_pquo_polynom_mpz (
    struct bap_polynom_mpz *,
    bav_Idegree *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAP_DLL void bap_rem_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

#   undef  BAD_FLAG_mpz

END_C_DECLS
#endif /* !BAP_PREM_POLYNOM_mpz_H */
#if !defined (BAP_PREM_POLYNOM_mpzm_H)
#   define BAP_PREM_POLYNOM_mpzm_H 1

/* #   include "bap_polynom_mpzm.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpzm

extern BAP_DLL bool bap_is_numeric_factor_polynom_mpzm (
    struct bap_polynom_mpzm *,
    ba0_mpzm_t,
    struct bap_polynom_mpzm *);

extern BAP_DLL bool bap_is_variable_factor_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bav_variable *,
    bav_Idegree *);

extern BAP_DLL bool bap_is_factor_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL bool bap_is_factor_tableof_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_tableof_polynom_mpzm *);

extern BAP_DLL void bap_exquo_polynom_term_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_term *);

extern BAP_DLL void bap_exquo_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

struct bap_product_mpzm;

extern BAP_DLL void bap_exquo_polynom_product_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_product_mpzm *);

extern BAP_DLL void bap_pseudo_division_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    bav_Idegree *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *);

extern BAP_DLL void bap_prem_polynom_mpzm (
    struct bap_polynom_mpzm *,
    bav_Idegree *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *);

extern BAP_DLL void bap_pquo_polynom_mpzm (
    struct bap_polynom_mpzm *,
    bav_Idegree *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *);

extern BAP_DLL void bap_rem_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *);

#   undef  BAD_FLAG_mpzm

END_C_DECLS
#endif /* !BAP_PREM_POLYNOM_mpzm_H */
#if !defined (BAP_PREM_POLYNOM_mpq_H)
#   define BAP_PREM_POLYNOM_mpq_H 1

/* #   include "bap_polynom_mpq.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpq

extern BAP_DLL bool bap_is_numeric_factor_polynom_mpq (
    struct bap_polynom_mpq *,
    ba0_mpq_t,
    struct bap_polynom_mpq *);

extern BAP_DLL bool bap_is_variable_factor_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bav_variable *,
    bav_Idegree *);

extern BAP_DLL bool bap_is_factor_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL bool bap_is_factor_tableof_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_tableof_polynom_mpq *);

extern BAP_DLL void bap_exquo_polynom_term_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_term *);

extern BAP_DLL void bap_exquo_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

struct bap_product_mpq;

extern BAP_DLL void bap_exquo_polynom_product_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_product_mpq *);

extern BAP_DLL void bap_pseudo_division_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    bav_Idegree *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL void bap_prem_polynom_mpq (
    struct bap_polynom_mpq *,
    bav_Idegree *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL void bap_pquo_polynom_mpq (
    struct bap_polynom_mpq *,
    bav_Idegree *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL void bap_rem_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

#   undef  BAD_FLAG_mpq

END_C_DECLS
#endif /* !BAP_PREM_POLYNOM_mpq_H */
#if !defined (BAP_PREM_POLYNOM_mint_hp_H)
#   define BAP_PREM_POLYNOM_mint_hp_H 1

/* #   include "bap_polynom_mint_hp.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mint_hp

extern BAP_DLL bool bap_is_numeric_factor_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    ba0_mint_hp_t,
    struct bap_polynom_mint_hp *);

extern BAP_DLL bool bap_is_variable_factor_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bav_variable *,
    bav_Idegree *);

extern BAP_DLL bool bap_is_factor_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL bool bap_is_factor_tableof_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_tableof_polynom_mint_hp *);

extern BAP_DLL void bap_exquo_polynom_term_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_term *);

extern BAP_DLL void bap_exquo_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

struct bap_product_mint_hp;

extern BAP_DLL void bap_exquo_polynom_product_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_product_mint_hp *);

extern BAP_DLL void bap_pseudo_division_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    bav_Idegree *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

extern BAP_DLL void bap_prem_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    bav_Idegree *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

extern BAP_DLL void bap_pquo_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    bav_Idegree *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

extern BAP_DLL void bap_rem_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

#   undef  BAD_FLAG_mint_hp

END_C_DECLS
#endif /* !BAP_PREM_POLYNOM_mint_hp_H */
#if !defined (BAP_PARSE_POLYNOM_mpz_H)
#   define BAP_PARSE_POLYNOM_mpz_H 1

/* #   include "bap_common.h" */
/* #   include "bap_clot_mpz.h" */
/* #   include "bap_sequential_access.h" */
/* #   include "bap_indexed_access.h" */
/* #   include "bap_termstripper.h" */
/* #   include "bap_polynom_mpz.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpz

extern BAP_DLL ba0_scanf_function bap_scanf_polynom_eqn_mpz;

extern BAP_DLL ba0_scanf_function bap_scanf_expanded_polynom_mpz;

extern BAP_DLL ba0_scanf_function bap_scanf_polynom_mpz;

extern BAP_DLL ba0_scanf_function bap_scanf_simplify_polynom_mpz;

extern BAP_DLL ba0_scanf_function bap_scanf_atomic_polynom_mpz;

extern BAP_DLL ba0_scanf_function bap_scanf_simplify_expanded_polynom_mpz;

extern BAP_DLL ba0_printf_function bap_printf_polynom_mpz;

extern BAP_DLL void bap_simplify_zero_derivatives_of_parameter_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

#   undef  BAD_FLAG_mpz

END_C_DECLS
#endif /* !BAP_PARSE_POLYNOM_mpz_H */
#if !defined (BAP_PARSE_POLYNOM_mpzm_H)
#   define BAP_PARSE_POLYNOM_mpzm_H 1

/* #   include "bap_common.h" */
/* #   include "bap_clot_mpzm.h" */
/* #   include "bap_sequential_access.h" */
/* #   include "bap_indexed_access.h" */
/* #   include "bap_termstripper.h" */
/* #   include "bap_polynom_mpzm.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpzm

extern BAP_DLL ba0_scanf_function bap_scanf_polynom_eqn_mpzm;

extern BAP_DLL ba0_scanf_function bap_scanf_expanded_polynom_mpzm;

extern BAP_DLL ba0_scanf_function bap_scanf_polynom_mpzm;

extern BAP_DLL ba0_scanf_function bap_scanf_simplify_polynom_mpzm;

extern BAP_DLL ba0_scanf_function bap_scanf_atomic_polynom_mpzm;

extern BAP_DLL ba0_scanf_function bap_scanf_simplify_expanded_polynom_mpzm;

extern BAP_DLL ba0_printf_function bap_printf_polynom_mpzm;

extern BAP_DLL void bap_simplify_zero_derivatives_of_parameter_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

#   undef  BAD_FLAG_mpzm

END_C_DECLS
#endif /* !BAP_PARSE_POLYNOM_mpzm_H */
#if !defined (BAP_PARSE_POLYNOM_mpq_H)
#   define BAP_PARSE_POLYNOM_mpq_H 1

/* #   include "bap_common.h" */
/* #   include "bap_clot_mpq.h" */
/* #   include "bap_sequential_access.h" */
/* #   include "bap_indexed_access.h" */
/* #   include "bap_termstripper.h" */
/* #   include "bap_polynom_mpq.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpq

extern BAP_DLL ba0_scanf_function bap_scanf_polynom_eqn_mpq;

extern BAP_DLL ba0_scanf_function bap_scanf_expanded_polynom_mpq;

extern BAP_DLL ba0_scanf_function bap_scanf_polynom_mpq;

extern BAP_DLL ba0_scanf_function bap_scanf_simplify_polynom_mpq;

extern BAP_DLL ba0_scanf_function bap_scanf_atomic_polynom_mpq;

extern BAP_DLL ba0_scanf_function bap_scanf_simplify_expanded_polynom_mpq;

extern BAP_DLL ba0_printf_function bap_printf_polynom_mpq;

extern BAP_DLL void bap_simplify_zero_derivatives_of_parameter_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

#   undef  BAD_FLAG_mpq

END_C_DECLS
#endif /* !BAP_PARSE_POLYNOM_mpq_H */
#if !defined (BAP_PARSE_POLYNOM_mint_hp_H)
#   define BAP_PARSE_POLYNOM_mint_hp_H 1

/* #   include "bap_common.h" */
/* #   include "bap_clot_mint_hp.h" */
/* #   include "bap_sequential_access.h" */
/* #   include "bap_indexed_access.h" */
/* #   include "bap_termstripper.h" */
/* #   include "bap_polynom_mint_hp.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mint_hp

extern BAP_DLL ba0_scanf_function bap_scanf_polynom_eqn_mint_hp;

extern BAP_DLL ba0_scanf_function bap_scanf_expanded_polynom_mint_hp;

extern BAP_DLL ba0_scanf_function bap_scanf_polynom_mint_hp;

extern BAP_DLL ba0_scanf_function bap_scanf_simplify_polynom_mint_hp;

extern BAP_DLL ba0_scanf_function bap_scanf_atomic_polynom_mint_hp;

extern BAP_DLL ba0_scanf_function bap_scanf_simplify_expanded_polynom_mint_hp;

extern BAP_DLL ba0_printf_function bap_printf_polynom_mint_hp;

extern BAP_DLL void bap_simplify_zero_derivatives_of_parameter_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

#   undef  BAD_FLAG_mint_hp

END_C_DECLS
#endif /* !BAP_PARSE_POLYNOM_mint_hp_H */
#if !defined (BAP_DUCOS_mpz_H)
#   define BAP_DUCOS_mpz_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mpz.h" */
/* #   include "bap_product_mpz.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpz

extern BAP_DLL void bap_muldiv_Lazard_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    bav_Idegree);

extern BAP_DLL void bap_muldiv2_Lazard_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    bav_Idegree);

extern BAP_DLL void bap_muldiv3_Lazard_polynom_mpz (
    struct bap_tableof_polynom_mpz *,
    struct bap_tableof_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    bav_Idegree);

extern BAP_DLL void bap_nsr2_Ducos_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAP_DLL void bap_nsr3_Ducos_polynom_mpz (
    struct bap_tableof_polynom_mpz *,
    struct bap_tableof_polynom_mpz *,
    struct bap_tableof_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAP_DLL void bap_resultant2_Ducos_polynom_mpz (
    struct bap_product_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAP_DLL void bap_lsr3_Ducos_polynom_mpz (
    struct bap_tableof_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

#   undef BAD_FLAG_mpz

END_C_DECLS
#endif /* !BAP_DUCOS_mpz_H */
#if !defined (BAP_DUCOS_mpzm_H)
#   define BAP_DUCOS_mpzm_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mpzm.h" */
/* #   include "bap_product_mpzm.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpzm

extern BAP_DLL void bap_muldiv_Lazard_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    bav_Idegree);

extern BAP_DLL void bap_muldiv2_Lazard_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    bav_Idegree);

extern BAP_DLL void bap_muldiv3_Lazard_polynom_mpzm (
    struct bap_tableof_polynom_mpzm *,
    struct bap_tableof_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    bav_Idegree);

extern BAP_DLL void bap_nsr2_Ducos_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *);

extern BAP_DLL void bap_nsr3_Ducos_polynom_mpzm (
    struct bap_tableof_polynom_mpzm *,
    struct bap_tableof_polynom_mpzm *,
    struct bap_tableof_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *);

extern BAP_DLL void bap_resultant2_Ducos_polynom_mpzm (
    struct bap_product_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *);

extern BAP_DLL void bap_lsr3_Ducos_polynom_mpzm (
    struct bap_tableof_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *);

#   undef BAD_FLAG_mpzm

END_C_DECLS
#endif /* !BAP_DUCOS_mpzm_H */
#if !defined (BAP_DUCOS_mpq_H)
#   define BAP_DUCOS_mpq_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mpq.h" */
/* #   include "bap_product_mpq.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpq

extern BAP_DLL void bap_muldiv_Lazard_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    bav_Idegree);

extern BAP_DLL void bap_muldiv2_Lazard_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    bav_Idegree);

extern BAP_DLL void bap_muldiv3_Lazard_polynom_mpq (
    struct bap_tableof_polynom_mpq *,
    struct bap_tableof_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    bav_Idegree);

extern BAP_DLL void bap_nsr2_Ducos_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL void bap_nsr3_Ducos_polynom_mpq (
    struct bap_tableof_polynom_mpq *,
    struct bap_tableof_polynom_mpq *,
    struct bap_tableof_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL void bap_resultant2_Ducos_polynom_mpq (
    struct bap_product_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL void bap_lsr3_Ducos_polynom_mpq (
    struct bap_tableof_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

#   undef BAD_FLAG_mpq

END_C_DECLS
#endif /* !BAP_DUCOS_mpq_H */
#if !defined (BAP_DUCOS_mint_hp_H)
#   define BAP_DUCOS_mint_hp_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mint_hp.h" */
/* #   include "bap_product_mint_hp.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mint_hp

extern BAP_DLL void bap_muldiv_Lazard_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    bav_Idegree);

extern BAP_DLL void bap_muldiv2_Lazard_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    bav_Idegree);

extern BAP_DLL void bap_muldiv3_Lazard_polynom_mint_hp (
    struct bap_tableof_polynom_mint_hp *,
    struct bap_tableof_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    bav_Idegree);

extern BAP_DLL void bap_nsr2_Ducos_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

extern BAP_DLL void bap_nsr3_Ducos_polynom_mint_hp (
    struct bap_tableof_polynom_mint_hp *,
    struct bap_tableof_polynom_mint_hp *,
    struct bap_tableof_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

extern BAP_DLL void bap_resultant2_Ducos_polynom_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

extern BAP_DLL void bap_lsr3_Ducos_polynom_mint_hp (
    struct bap_tableof_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

#   undef BAD_FLAG_mint_hp

END_C_DECLS
#endif /* !BAP_DUCOS_mint_hp_H */
#if !defined (BAP_EVAL_POLYNOM_mpz_H)
#   define BAP_EVAL_POLYNOM_mpz_H 1

/* #   include "bap_polynom_mpz.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpz
#   if defined (BAD_FLAG_mpz) || defined (BAD_FLAG_mpzm) || defined (BAD_FLAG_mpq)

extern BAP_DLL void bap_set_point_polynom_mpz (
    struct ba0_point *,
    struct bap_polynom_mpz *,
    bool);

extern BAP_DLL void bap_eval_to_polynom_at_numeric_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *,
    ba0_mpz_t);
#   endif

#   if defined (BAD_FLAG_mpz) || defined (BAD_FLAG_mpzm)
extern BAP_DLL void bap_eval_to_polynom_at_value_int_p_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_value_int_p *);

extern BAP_DLL void bap_eval_to_polynom_at_point_int_p_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_point_int_p *);

extern BAP_DLL void bap_eval_to_numeric_at_point_int_p_polynom_mpz (
    ba0_mpz_t *,
    struct bap_polynom_mpz *,
    struct bav_point_int_p *);

extern BAP_DLL void bap_evalcoeff_at_point_int_p_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_point_int_p *);
#   endif
#   undef  BAD_FLAG_mpz

END_C_DECLS
#endif /* !BAP_EVAL_POLYNOM_mpz_H */
#if !defined (BAP_EVAL_POLYNOM_mpzm_H)
#   define BAP_EVAL_POLYNOM_mpzm_H 1

/* #   include "bap_polynom_mpzm.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpzm
#   if defined (BAD_FLAG_mpz) || defined (BAD_FLAG_mpzm) || defined (BAD_FLAG_mpq)

extern BAP_DLL void bap_set_point_polynom_mpzm (
    struct ba0_point *,
    struct bap_polynom_mpzm *,
    bool);

extern BAP_DLL void bap_eval_to_polynom_at_numeric_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *,
    ba0_mpzm_t);
#   endif

#   if defined (BAD_FLAG_mpz) || defined (BAD_FLAG_mpzm)
extern BAP_DLL void bap_eval_to_polynom_at_value_int_p_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_value_int_p *);

extern BAP_DLL void bap_eval_to_polynom_at_point_int_p_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_point_int_p *);

extern BAP_DLL void bap_eval_to_numeric_at_point_int_p_polynom_mpzm (
    ba0_mpzm_t *,
    struct bap_polynom_mpzm *,
    struct bav_point_int_p *);

extern BAP_DLL void bap_evalcoeff_at_point_int_p_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_point_int_p *);
#   endif
#   undef  BAD_FLAG_mpzm

END_C_DECLS
#endif /* !BAP_EVAL_POLYNOM_mpzm_H */
#if !defined (BAP_EVAL_POLYNOM_mpq_H)
#   define BAP_EVAL_POLYNOM_mpq_H 1

/* #   include "bap_polynom_mpq.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpq
#   if defined (BAD_FLAG_mpz) || defined (BAD_FLAG_mpzm) || defined (BAD_FLAG_mpq)

extern BAP_DLL void bap_set_point_polynom_mpq (
    struct ba0_point *,
    struct bap_polynom_mpq *,
    bool);

extern BAP_DLL void bap_eval_to_polynom_at_numeric_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *,
    ba0_mpq_t);
#   endif

#   if defined (BAD_FLAG_mpz) || defined (BAD_FLAG_mpzm)
extern BAP_DLL void bap_eval_to_polynom_at_value_int_p_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_value_int_p *);

extern BAP_DLL void bap_eval_to_polynom_at_point_int_p_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_point_int_p *);

extern BAP_DLL void bap_eval_to_numeric_at_point_int_p_polynom_mpq (
    ba0_mpq_t *,
    struct bap_polynom_mpq *,
    struct bav_point_int_p *);

extern BAP_DLL void bap_evalcoeff_at_point_int_p_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_point_int_p *);
#   endif
#   undef  BAD_FLAG_mpq

END_C_DECLS
#endif /* !BAP_EVAL_POLYNOM_mpq_H */
#if !defined (BAP_EVAL_POLYNOM_mint_hp_H)
#   define BAP_EVAL_POLYNOM_mint_hp_H 1

/* #   include "bap_polynom_mint_hp.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mint_hp
#   if defined (BAD_FLAG_mpz) || defined (BAD_FLAG_mpzm) || defined (BAD_FLAG_mpq)

extern BAP_DLL void bap_set_point_polynom_mint_hp (
    struct ba0_point *,
    struct bap_polynom_mint_hp *,
    bool);

extern BAP_DLL void bap_eval_to_polynom_at_numeric_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *,
    ba0_mint_hp_t);
#   endif

#   if defined (BAD_FLAG_mpz) || defined (BAD_FLAG_mpzm)
extern BAP_DLL void bap_eval_to_polynom_at_value_int_p_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_value_int_p *);

extern BAP_DLL void bap_eval_to_polynom_at_point_int_p_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_point_int_p *);

extern BAP_DLL void bap_eval_to_numeric_at_point_int_p_polynom_mint_hp (
    ba0_mint_hp_t *,
    struct bap_polynom_mint_hp *,
    struct bav_point_int_p *);

extern BAP_DLL void bap_evalcoeff_at_point_int_p_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_point_int_p *);
#   endif
#   undef  BAD_FLAG_mint_hp

END_C_DECLS
#endif /* !BAP_EVAL_POLYNOM_mint_hp_H */
#if !defined (BAP_DIFF_POLYNOM_mpz_H)
#   define BAP_DIFF_POLYNOM_mpz_H 1

/* #   include "bap_common.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpz
extern BAP_DLL bool bap_is_constant_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bav_symbol *);

extern BAP_DLL bool bap_is_polynomial_with_constant_coefficients_mpz (
    struct bap_polynom_mpz *,
    struct bav_variable *,
    struct bav_symbol *);

extern BAP_DLL bool bap_is_independent_polynom_mpz (
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_diff_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_symbol *);

extern BAP_DLL void bap_diff2_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_term *);

extern BAP_DLL void bap_involved_derivations_polynom_mpz (
    struct bav_tableof_variable *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_involved_parameters_polynom_mpz (
    struct bav_dictionary_symbol *,
    struct bav_tableof_symbol *,
    struct bap_polynom_mpz *);

#   undef  BAD_FLAG_mpz

END_C_DECLS
#endif /* !BAP_DIFF_POLYNOM_mpz_H */
#if !defined (BAP_DIFF_POLYNOM_mpzm_H)
#   define BAP_DIFF_POLYNOM_mpzm_H 1

/* #   include "bap_common.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpzm
extern BAP_DLL bool bap_is_constant_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bav_symbol *);

extern BAP_DLL bool bap_is_polynomial_with_constant_coefficients_mpzm (
    struct bap_polynom_mpzm *,
    struct bav_variable *,
    struct bav_symbol *);

extern BAP_DLL bool bap_is_independent_polynom_mpzm (
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_diff_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_symbol *);

extern BAP_DLL void bap_diff2_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_term *);

extern BAP_DLL void bap_involved_derivations_polynom_mpzm (
    struct bav_tableof_variable *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_involved_parameters_polynom_mpzm (
    struct bav_dictionary_symbol *,
    struct bav_tableof_symbol *,
    struct bap_polynom_mpzm *);

#   undef  BAD_FLAG_mpzm

END_C_DECLS
#endif /* !BAP_DIFF_POLYNOM_mpzm_H */
#if !defined (BAP_DIFF_POLYNOM_mpq_H)
#   define BAP_DIFF_POLYNOM_mpq_H 1

/* #   include "bap_common.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpq
extern BAP_DLL bool bap_is_constant_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bav_symbol *);

extern BAP_DLL bool bap_is_polynomial_with_constant_coefficients_mpq (
    struct bap_polynom_mpq *,
    struct bav_variable *,
    struct bav_symbol *);

extern BAP_DLL bool bap_is_independent_polynom_mpq (
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_diff_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_symbol *);

extern BAP_DLL void bap_diff2_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_term *);

extern BAP_DLL void bap_involved_derivations_polynom_mpq (
    struct bav_tableof_variable *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_involved_parameters_polynom_mpq (
    struct bav_dictionary_symbol *,
    struct bav_tableof_symbol *,
    struct bap_polynom_mpq *);

#   undef  BAD_FLAG_mpq

END_C_DECLS
#endif /* !BAP_DIFF_POLYNOM_mpq_H */
#if !defined (BAP_DIFF_POLYNOM_mint_hp_H)
#   define BAP_DIFF_POLYNOM_mint_hp_H 1

/* #   include "bap_common.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mint_hp
extern BAP_DLL bool bap_is_constant_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bav_symbol *);

extern BAP_DLL bool bap_is_polynomial_with_constant_coefficients_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bav_variable *,
    struct bav_symbol *);

extern BAP_DLL bool bap_is_independent_polynom_mint_hp (
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_diff_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_symbol *);

extern BAP_DLL void bap_diff2_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_term *);

extern BAP_DLL void bap_involved_derivations_polynom_mint_hp (
    struct bav_tableof_variable *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_involved_parameters_polynom_mint_hp (
    struct bav_dictionary_symbol *,
    struct bav_tableof_symbol *,
    struct bap_polynom_mint_hp *);

#   undef  BAD_FLAG_mint_hp

END_C_DECLS
#endif /* !BAP_DIFF_POLYNOM_mint_hp_H */
#if !defined (BAP_INVERT_mpzm_H)
#   define BAP_INVERT_mpzm_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mpzm.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpzm

extern BAP_DLL void bap_numeric_initial_one_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_Euclidean_division_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_Euclid_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_extended_Euclid_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

#   undef BAD_FLAG_mpzm

END_C_DECLS
#endif /* !BAP_INVERT_mpzm_H */
#if !defined (BAP_INVERT_mpq_H)
#   define BAP_INVERT_mpq_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mpq.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpq

extern BAP_DLL void bap_numeric_initial_one_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_Euclidean_division_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_Euclid_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_extended_Euclid_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

#   undef BAD_FLAG_mpq

END_C_DECLS
#endif /* !BAP_INVERT_mpq_H */
#if !defined (BAP_INVERT_mint_hp_H)
#   define BAP_INVERT_mint_hp_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mint_hp.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mint_hp

extern BAP_DLL void bap_numeric_initial_one_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_Euclidean_division_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_Euclid_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_extended_Euclid_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *);

#   undef BAD_FLAG_mint_hp

END_C_DECLS
#endif /* !BAP_INVERT_mint_hp_H */
#if !defined (BAP_CREATOR_mpz_H)
#   define BAP_CREATOR_mpz_H 1

/* #   include "bap_common.h" */
/* #   include "bap_clot_mpz.h" */
/* #   include "bap_polynom_mpz.h" */

#   define BAD_FLAG_mpz

BEGIN_C_DECLS

/*
 * texinfo: bap_creator_mpz
 * This data type permits to create a polynomial from scratch
 * by giving, in decreasing order, its terms and numerical
 * coefficients.
 */

struct bap_creator_mpz
{
// the polynomial to create
  struct bap_polynom_mpz *poly;
// a creator for the clot of the polynomial
  struct bap_creator_clot_mpz crea;
// the type of the total rank provided when initializing the process
  enum bap_typeof_total_rank type;
};


extern BAP_DLL void bap_begin_creator_mpz (
    struct bap_creator_mpz *,
    struct bap_polynom_mpz *,
    struct bav_term *,
    enum bap_typeof_total_rank,
    ba0_int_p);

extern BAP_DLL void bap_append_creator_mpz (
    struct bap_creator_mpz *,
    struct bap_polynom_mpz *,
    ba0_int_p);

extern BAP_DLL void bap_write_creator_mpz (
    struct bap_creator_mpz *,
    struct bav_term *,
    ba0_mpz_t);

extern BAP_DLL void bap_write_neg_creator_mpz (
    struct bap_creator_mpz *,
    struct bav_term *,
    ba0_mpz_t);

extern BAP_DLL bool bap_is_write_allable_creator_mpz (
    struct bap_creator_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_write_all_creator_mpz (
    struct bap_creator_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_write_neg_all_creator_mpz (
    struct bap_creator_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_write_mul_all_creator_mpz (
    struct bap_creator_mpz *,
    struct bap_polynom_mpz *,
    ba0_mpz_t);

#   if defined BAD_FLAG_mpz

extern BAP_DLL void bap_write_exquo_all_creator_mpz (
    struct bap_creator_mpz *,
    struct bap_polynom_mpz *,
    ba0_mpz_t);

#   endif

extern BAP_DLL void bap_close_creator_mpz (
    struct bap_creator_mpz *);

END_C_DECLS
#   undef  BAD_FLAG_mpz
#endif /* !BAP_CREATOR_mpz_H */
#if !defined (BAP_CREATOR_mpzm_H)
#   define BAP_CREATOR_mpzm_H 1

/* #   include "bap_common.h" */
/* #   include "bap_clot_mpzm.h" */
/* #   include "bap_polynom_mpzm.h" */

#   define BAD_FLAG_mpzm

BEGIN_C_DECLS

/*
 * texinfo: bap_creator_mpzm
 * This data type permits to create a polynomial from scratch
 * by giving, in decreasing order, its terms and numerical
 * coefficients.
 */

struct bap_creator_mpzm
{
// the polynomial to create
  struct bap_polynom_mpzm *poly;
// a creator for the clot of the polynomial
  struct bap_creator_clot_mpzm crea;
// the type of the total rank provided when initializing the process
  enum bap_typeof_total_rank type;
};


extern BAP_DLL void bap_begin_creator_mpzm (
    struct bap_creator_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_term *,
    enum bap_typeof_total_rank,
    ba0_int_p);

extern BAP_DLL void bap_append_creator_mpzm (
    struct bap_creator_mpzm *,
    struct bap_polynom_mpzm *,
    ba0_int_p);

extern BAP_DLL void bap_write_creator_mpzm (
    struct bap_creator_mpzm *,
    struct bav_term *,
    ba0_mpzm_t);

extern BAP_DLL void bap_write_neg_creator_mpzm (
    struct bap_creator_mpzm *,
    struct bav_term *,
    ba0_mpzm_t);

extern BAP_DLL bool bap_is_write_allable_creator_mpzm (
    struct bap_creator_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_write_all_creator_mpzm (
    struct bap_creator_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_write_neg_all_creator_mpzm (
    struct bap_creator_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_write_mul_all_creator_mpzm (
    struct bap_creator_mpzm *,
    struct bap_polynom_mpzm *,
    ba0_mpzm_t);

#   if defined BAD_FLAG_mpz

extern BAP_DLL void bap_write_exquo_all_creator_mpz (
    struct bap_creator_mpz *,
    struct bap_polynom_mpz *,
    ba0_mpz_t);

#   endif

extern BAP_DLL void bap_close_creator_mpzm (
    struct bap_creator_mpzm *);

END_C_DECLS
#   undef  BAD_FLAG_mpzm
#endif /* !BAP_CREATOR_mpzm_H */
#if !defined (BAP_CREATOR_mpq_H)
#   define BAP_CREATOR_mpq_H 1

/* #   include "bap_common.h" */
/* #   include "bap_clot_mpq.h" */
/* #   include "bap_polynom_mpq.h" */

#   define BAD_FLAG_mpq

BEGIN_C_DECLS

/*
 * texinfo: bap_creator_mpq
 * This data type permits to create a polynomial from scratch
 * by giving, in decreasing order, its terms and numerical
 * coefficients.
 */

struct bap_creator_mpq
{
// the polynomial to create
  struct bap_polynom_mpq *poly;
// a creator for the clot of the polynomial
  struct bap_creator_clot_mpq crea;
// the type of the total rank provided when initializing the process
  enum bap_typeof_total_rank type;
};


extern BAP_DLL void bap_begin_creator_mpq (
    struct bap_creator_mpq *,
    struct bap_polynom_mpq *,
    struct bav_term *,
    enum bap_typeof_total_rank,
    ba0_int_p);

extern BAP_DLL void bap_append_creator_mpq (
    struct bap_creator_mpq *,
    struct bap_polynom_mpq *,
    ba0_int_p);

extern BAP_DLL void bap_write_creator_mpq (
    struct bap_creator_mpq *,
    struct bav_term *,
    ba0_mpq_t);

extern BAP_DLL void bap_write_neg_creator_mpq (
    struct bap_creator_mpq *,
    struct bav_term *,
    ba0_mpq_t);

extern BAP_DLL bool bap_is_write_allable_creator_mpq (
    struct bap_creator_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_write_all_creator_mpq (
    struct bap_creator_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_write_neg_all_creator_mpq (
    struct bap_creator_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_write_mul_all_creator_mpq (
    struct bap_creator_mpq *,
    struct bap_polynom_mpq *,
    ba0_mpq_t);

#   if defined BAD_FLAG_mpz

extern BAP_DLL void bap_write_exquo_all_creator_mpz (
    struct bap_creator_mpz *,
    struct bap_polynom_mpz *,
    ba0_mpz_t);

#   endif

extern BAP_DLL void bap_close_creator_mpq (
    struct bap_creator_mpq *);

END_C_DECLS
#   undef  BAD_FLAG_mpq
#endif /* !BAP_CREATOR_mpq_H */
#if !defined (BAP_CREATOR_mint_hp_H)
#   define BAP_CREATOR_mint_hp_H 1

/* #   include "bap_common.h" */
/* #   include "bap_clot_mint_hp.h" */
/* #   include "bap_polynom_mint_hp.h" */

#   define BAD_FLAG_mint_hp

BEGIN_C_DECLS

/*
 * texinfo: bap_creator_mint_hp
 * This data type permits to create a polynomial from scratch
 * by giving, in decreasing order, its terms and numerical
 * coefficients.
 */

struct bap_creator_mint_hp
{
// the polynomial to create
  struct bap_polynom_mint_hp *poly;
// a creator for the clot of the polynomial
  struct bap_creator_clot_mint_hp crea;
// the type of the total rank provided when initializing the process
  enum bap_typeof_total_rank type;
};


extern BAP_DLL void bap_begin_creator_mint_hp (
    struct bap_creator_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_term *,
    enum bap_typeof_total_rank,
    ba0_int_p);

extern BAP_DLL void bap_append_creator_mint_hp (
    struct bap_creator_mint_hp *,
    struct bap_polynom_mint_hp *,
    ba0_int_p);

extern BAP_DLL void bap_write_creator_mint_hp (
    struct bap_creator_mint_hp *,
    struct bav_term *,
    ba0_mint_hp_t);

extern BAP_DLL void bap_write_neg_creator_mint_hp (
    struct bap_creator_mint_hp *,
    struct bav_term *,
    ba0_mint_hp_t);

extern BAP_DLL bool bap_is_write_allable_creator_mint_hp (
    struct bap_creator_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_write_all_creator_mint_hp (
    struct bap_creator_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_write_neg_all_creator_mint_hp (
    struct bap_creator_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_write_mul_all_creator_mint_hp (
    struct bap_creator_mint_hp *,
    struct bap_polynom_mint_hp *,
    ba0_mint_hp_t);

#   if defined BAD_FLAG_mpz

extern BAP_DLL void bap_write_exquo_all_creator_mpz (
    struct bap_creator_mpz *,
    struct bap_polynom_mpz *,
    ba0_mpz_t);

#   endif

extern BAP_DLL void bap_close_creator_mint_hp (
    struct bap_creator_mint_hp *);

END_C_DECLS
#   undef  BAD_FLAG_mint_hp
#endif /* !BAP_CREATOR_mint_hp_H */
#if !defined (BAP_ITERMON_mpz_H)
#   define BAP_ITERMON_mpz_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mpz.h" */
/* #   include "bap_iterator_indexed_access.h" */

#   define BAD_FLAG_mpz

BEGIN_C_DECLS

/*
 * texinfo: bap_itermon_mpz
 * This data type implements an iterator of monomials of a
 * differential polynomials, viewed as multivariate polynomial
 * over the numerical coefficients.
 * The monomials of the polynomial may be accessed either in
 * sequential access as in indexed access.
 */

struct bap_itermon_mpz
{
  struct bap_polynom_mpz *poly;       // the polynomial
// an iterator of monomials of poly->clot
  struct bap_itermon_clot_mpz iter;
// an auxiliary data structure if access is indexed
// it provides the current index in poly->ind.tab
  struct bap_iterator_indexed_access iter_ix;
};


extern BAP_DLL void bap_begin_itermon_mpz (
    struct bap_itermon_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_end_itermon_mpz (
    struct bap_itermon_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_close_itermon_mpz (
    struct bap_itermon_mpz *);

extern BAP_DLL void bap_set_itermon_mpz (
    struct bap_itermon_mpz *,
    struct bap_itermon_mpz *);

extern BAP_DLL bool bap_outof_itermon_mpz (
    struct bap_itermon_mpz *);

extern BAP_DLL void bap_next_itermon_mpz (
    struct bap_itermon_mpz *);

extern BAP_DLL void bap_prev_itermon_mpz (
    struct bap_itermon_mpz *);

extern BAP_DLL void bap_goto_itermon_mpz (
    struct bap_itermon_mpz *,
    ba0_int_p);

extern BAP_DLL ba0_mpz_t *bap_coeff_itermon_mpz (
    struct bap_itermon_mpz *);

extern BAP_DLL void bap_term_itermon_mpz (
    struct bav_term *,
    struct bap_itermon_mpz *);

extern BAP_DLL void bap_reductum_itermon_mpz (
    struct bap_itermon_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_seekfirst_itermon_mpz (
    struct bap_itermon_mpz *,
    enum bap_rank_code (*)(struct bav_term *,
        struct bav_term *,
        bav_Inumber),
    struct bav_term *,
    bav_Inumber);

extern BAP_DLL void bap_seeklast_itermon_mpz (
    struct bap_itermon_mpz *,
    enum bap_rank_code (*)(struct bav_term *,
        struct bav_term *,
        bav_Inumber),
    struct bav_term *,
    bav_Inumber);

END_C_DECLS
#   undef  BAD_FLAG_mpz
#endif /* !BAP_ITERMON_mpz_H */
#if !defined (BAP_ITERMON_mpzm_H)
#   define BAP_ITERMON_mpzm_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mpzm.h" */
/* #   include "bap_iterator_indexed_access.h" */

#   define BAD_FLAG_mpzm

BEGIN_C_DECLS

/*
 * texinfo: bap_itermon_mpzm
 * This data type implements an iterator of monomials of a
 * differential polynomials, viewed as multivariate polynomial
 * over the numerical coefficients.
 * The monomials of the polynomial may be accessed either in
 * sequential access as in indexed access.
 */

struct bap_itermon_mpzm
{
  struct bap_polynom_mpzm *poly;       // the polynomial
// an iterator of monomials of poly->clot
  struct bap_itermon_clot_mpzm iter;
// an auxiliary data structure if access is indexed
// it provides the current index in poly->ind.tab
  struct bap_iterator_indexed_access iter_ix;
};


extern BAP_DLL void bap_begin_itermon_mpzm (
    struct bap_itermon_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_end_itermon_mpzm (
    struct bap_itermon_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_close_itermon_mpzm (
    struct bap_itermon_mpzm *);

extern BAP_DLL void bap_set_itermon_mpzm (
    struct bap_itermon_mpzm *,
    struct bap_itermon_mpzm *);

extern BAP_DLL bool bap_outof_itermon_mpzm (
    struct bap_itermon_mpzm *);

extern BAP_DLL void bap_next_itermon_mpzm (
    struct bap_itermon_mpzm *);

extern BAP_DLL void bap_prev_itermon_mpzm (
    struct bap_itermon_mpzm *);

extern BAP_DLL void bap_goto_itermon_mpzm (
    struct bap_itermon_mpzm *,
    ba0_int_p);

extern BAP_DLL ba0_mpzm_t *bap_coeff_itermon_mpzm (
    struct bap_itermon_mpzm *);

extern BAP_DLL void bap_term_itermon_mpzm (
    struct bav_term *,
    struct bap_itermon_mpzm *);

extern BAP_DLL void bap_reductum_itermon_mpzm (
    struct bap_itermon_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_seekfirst_itermon_mpzm (
    struct bap_itermon_mpzm *,
    enum bap_rank_code (*)(struct bav_term *,
        struct bav_term *,
        bav_Inumber),
    struct bav_term *,
    bav_Inumber);

extern BAP_DLL void bap_seeklast_itermon_mpzm (
    struct bap_itermon_mpzm *,
    enum bap_rank_code (*)(struct bav_term *,
        struct bav_term *,
        bav_Inumber),
    struct bav_term *,
    bav_Inumber);

END_C_DECLS
#   undef  BAD_FLAG_mpzm
#endif /* !BAP_ITERMON_mpzm_H */
#if !defined (BAP_ITERMON_mpq_H)
#   define BAP_ITERMON_mpq_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mpq.h" */
/* #   include "bap_iterator_indexed_access.h" */

#   define BAD_FLAG_mpq

BEGIN_C_DECLS

/*
 * texinfo: bap_itermon_mpq
 * This data type implements an iterator of monomials of a
 * differential polynomials, viewed as multivariate polynomial
 * over the numerical coefficients.
 * The monomials of the polynomial may be accessed either in
 * sequential access as in indexed access.
 */

struct bap_itermon_mpq
{
  struct bap_polynom_mpq *poly;       // the polynomial
// an iterator of monomials of poly->clot
  struct bap_itermon_clot_mpq iter;
// an auxiliary data structure if access is indexed
// it provides the current index in poly->ind.tab
  struct bap_iterator_indexed_access iter_ix;
};


extern BAP_DLL void bap_begin_itermon_mpq (
    struct bap_itermon_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_end_itermon_mpq (
    struct bap_itermon_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_close_itermon_mpq (
    struct bap_itermon_mpq *);

extern BAP_DLL void bap_set_itermon_mpq (
    struct bap_itermon_mpq *,
    struct bap_itermon_mpq *);

extern BAP_DLL bool bap_outof_itermon_mpq (
    struct bap_itermon_mpq *);

extern BAP_DLL void bap_next_itermon_mpq (
    struct bap_itermon_mpq *);

extern BAP_DLL void bap_prev_itermon_mpq (
    struct bap_itermon_mpq *);

extern BAP_DLL void bap_goto_itermon_mpq (
    struct bap_itermon_mpq *,
    ba0_int_p);

extern BAP_DLL ba0_mpq_t *bap_coeff_itermon_mpq (
    struct bap_itermon_mpq *);

extern BAP_DLL void bap_term_itermon_mpq (
    struct bav_term *,
    struct bap_itermon_mpq *);

extern BAP_DLL void bap_reductum_itermon_mpq (
    struct bap_itermon_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_seekfirst_itermon_mpq (
    struct bap_itermon_mpq *,
    enum bap_rank_code (*)(struct bav_term *,
        struct bav_term *,
        bav_Inumber),
    struct bav_term *,
    bav_Inumber);

extern BAP_DLL void bap_seeklast_itermon_mpq (
    struct bap_itermon_mpq *,
    enum bap_rank_code (*)(struct bav_term *,
        struct bav_term *,
        bav_Inumber),
    struct bav_term *,
    bav_Inumber);

END_C_DECLS
#   undef  BAD_FLAG_mpq
#endif /* !BAP_ITERMON_mpq_H */
#if !defined (BAP_ITERMON_mint_hp_H)
#   define BAP_ITERMON_mint_hp_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mint_hp.h" */
/* #   include "bap_iterator_indexed_access.h" */

#   define BAD_FLAG_mint_hp

BEGIN_C_DECLS

/*
 * texinfo: bap_itermon_mint_hp
 * This data type implements an iterator of monomials of a
 * differential polynomials, viewed as multivariate polynomial
 * over the numerical coefficients.
 * The monomials of the polynomial may be accessed either in
 * sequential access as in indexed access.
 */

struct bap_itermon_mint_hp
{
  struct bap_polynom_mint_hp *poly;       // the polynomial
// an iterator of monomials of poly->clot
  struct bap_itermon_clot_mint_hp iter;
// an auxiliary data structure if access is indexed
// it provides the current index in poly->ind.tab
  struct bap_iterator_indexed_access iter_ix;
};


extern BAP_DLL void bap_begin_itermon_mint_hp (
    struct bap_itermon_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_end_itermon_mint_hp (
    struct bap_itermon_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_close_itermon_mint_hp (
    struct bap_itermon_mint_hp *);

extern BAP_DLL void bap_set_itermon_mint_hp (
    struct bap_itermon_mint_hp *,
    struct bap_itermon_mint_hp *);

extern BAP_DLL bool bap_outof_itermon_mint_hp (
    struct bap_itermon_mint_hp *);

extern BAP_DLL void bap_next_itermon_mint_hp (
    struct bap_itermon_mint_hp *);

extern BAP_DLL void bap_prev_itermon_mint_hp (
    struct bap_itermon_mint_hp *);

extern BAP_DLL void bap_goto_itermon_mint_hp (
    struct bap_itermon_mint_hp *,
    ba0_int_p);

extern BAP_DLL ba0_mint_hp_t *bap_coeff_itermon_mint_hp (
    struct bap_itermon_mint_hp *);

extern BAP_DLL void bap_term_itermon_mint_hp (
    struct bav_term *,
    struct bap_itermon_mint_hp *);

extern BAP_DLL void bap_reductum_itermon_mint_hp (
    struct bap_itermon_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_seekfirst_itermon_mint_hp (
    struct bap_itermon_mint_hp *,
    enum bap_rank_code (*)(struct bav_term *,
        struct bav_term *,
        bav_Inumber),
    struct bav_term *,
    bav_Inumber);

extern BAP_DLL void bap_seeklast_itermon_mint_hp (
    struct bap_itermon_mint_hp *,
    enum bap_rank_code (*)(struct bav_term *,
        struct bav_term *,
        bav_Inumber),
    struct bav_term *,
    bav_Inumber);

END_C_DECLS
#   undef  BAD_FLAG_mint_hp
#endif /* !BAP_ITERMON_mint_hp_H */
#if !defined (BAP_ITERKOEFF_mpz_H)
#   define BAP_ITERKOEFF_mpz_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mpz.h" */
/* #   include "bap_itermon_mpz.h" */

#   define BAD_FLAG_mpz

BEGIN_C_DECLS

/*
 * texinfo: bap_itercoeff_mpz
 * This data type implements an iterator of coefficients of a 
 * differential polynomials, with respect to a given variable.
 * Let @var{A} be a polynomial and @math{X = x_1 < \cdots < x_n} be 
 * the alphabet of the variables it depends on. 
 * Let @math{1 \leq i \leq n} be an index.
 * The iterator permits to extract the coefficients of @var{A}, viewed as 
 * a polynomial over the alphabet @math{x_i, \ldots, x_n}, with 
 * coefficients in the ring of the polynomials over the alphabet 
 * @math{x_1, \ldots, x_{i-1}}.
 */

struct bap_itercoeff_mpz
{
  struct bap_polynom_mpz *poly;       // the polynomial
  struct bav_variable *last_variable;   // the lowest variable among the terms
// debut is set on the first monomial of the current coefficient
  struct bap_itermon_mpz debut;
// fin is set on the last monomial of the current coefficient
  struct bap_itermon_mpz fin;
  bool outof;                   // true if the iterator is outside the polynomial
};


extern BAP_DLL void bap_begin_itercoeff_mpz (
    struct bap_itercoeff_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAP_DLL void bap_end_itercoeff_mpz (
    struct bap_itercoeff_mpz *,
    struct bap_polynom_mpz *,
    struct bav_variable *);

extern BAP_DLL bool bap_outof_itercoeff_mpz (
    struct bap_itercoeff_mpz *);

extern BAP_DLL void bap_close_itercoeff_mpz (
    struct bap_itercoeff_mpz *);

extern BAP_DLL void bap_next_itercoeff_mpz (
    struct bap_itercoeff_mpz *);

extern BAP_DLL void bap_prev_itercoeff_mpz (
    struct bap_itercoeff_mpz *);

extern BAP_DLL void bap_term_itercoeff_mpz (
    struct bav_term *,
    struct bap_itercoeff_mpz *);

extern BAP_DLL void bap_coeff_itercoeff_mpz (
    struct bap_polynom_mpz *,
    struct bap_itercoeff_mpz *);

extern BAP_DLL void bap_seek_coeff_itercoeff_mpz (
    struct bap_polynom_mpz *,
    struct bap_itercoeff_mpz *,
    struct bav_term *);

extern BAP_DLL void bap_split_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bav_term *);

END_C_DECLS
#   undef  BAD_FLAG_mpz
#endif /* !BAP_ITERKOEFF_mpz_H */
#if !defined (BAP_ITERKOEFF_mpzm_H)
#   define BAP_ITERKOEFF_mpzm_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mpzm.h" */
/* #   include "bap_itermon_mpzm.h" */

#   define BAD_FLAG_mpzm

BEGIN_C_DECLS

/*
 * texinfo: bap_itercoeff_mpzm
 * This data type implements an iterator of coefficients of a 
 * differential polynomials, with respect to a given variable.
 * Let @var{A} be a polynomial and @math{X = x_1 < \cdots < x_n} be 
 * the alphabet of the variables it depends on. 
 * Let @math{1 \leq i \leq n} be an index.
 * The iterator permits to extract the coefficients of @var{A}, viewed as 
 * a polynomial over the alphabet @math{x_i, \ldots, x_n}, with 
 * coefficients in the ring of the polynomials over the alphabet 
 * @math{x_1, \ldots, x_{i-1}}.
 */

struct bap_itercoeff_mpzm
{
  struct bap_polynom_mpzm *poly;       // the polynomial
  struct bav_variable *last_variable;   // the lowest variable among the terms
// debut is set on the first monomial of the current coefficient
  struct bap_itermon_mpzm debut;
// fin is set on the last monomial of the current coefficient
  struct bap_itermon_mpzm fin;
  bool outof;                   // true if the iterator is outside the polynomial
};


extern BAP_DLL void bap_begin_itercoeff_mpzm (
    struct bap_itercoeff_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *);

extern BAP_DLL void bap_end_itercoeff_mpzm (
    struct bap_itercoeff_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_variable *);

extern BAP_DLL bool bap_outof_itercoeff_mpzm (
    struct bap_itercoeff_mpzm *);

extern BAP_DLL void bap_close_itercoeff_mpzm (
    struct bap_itercoeff_mpzm *);

extern BAP_DLL void bap_next_itercoeff_mpzm (
    struct bap_itercoeff_mpzm *);

extern BAP_DLL void bap_prev_itercoeff_mpzm (
    struct bap_itercoeff_mpzm *);

extern BAP_DLL void bap_term_itercoeff_mpzm (
    struct bav_term *,
    struct bap_itercoeff_mpzm *);

extern BAP_DLL void bap_coeff_itercoeff_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_itercoeff_mpzm *);

extern BAP_DLL void bap_seek_coeff_itercoeff_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_itercoeff_mpzm *,
    struct bav_term *);

extern BAP_DLL void bap_split_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_term *);

END_C_DECLS
#   undef  BAD_FLAG_mpzm
#endif /* !BAP_ITERKOEFF_mpzm_H */
#if !defined (BAP_ITERKOEFF_mpq_H)
#   define BAP_ITERKOEFF_mpq_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mpq.h" */
/* #   include "bap_itermon_mpq.h" */

#   define BAD_FLAG_mpq

BEGIN_C_DECLS

/*
 * texinfo: bap_itercoeff_mpq
 * This data type implements an iterator of coefficients of a 
 * differential polynomials, with respect to a given variable.
 * Let @var{A} be a polynomial and @math{X = x_1 < \cdots < x_n} be 
 * the alphabet of the variables it depends on. 
 * Let @math{1 \leq i \leq n} be an index.
 * The iterator permits to extract the coefficients of @var{A}, viewed as 
 * a polynomial over the alphabet @math{x_i, \ldots, x_n}, with 
 * coefficients in the ring of the polynomials over the alphabet 
 * @math{x_1, \ldots, x_{i-1}}.
 */

struct bap_itercoeff_mpq
{
  struct bap_polynom_mpq *poly;       // the polynomial
  struct bav_variable *last_variable;   // the lowest variable among the terms
// debut is set on the first monomial of the current coefficient
  struct bap_itermon_mpq debut;
// fin is set on the last monomial of the current coefficient
  struct bap_itermon_mpq fin;
  bool outof;                   // true if the iterator is outside the polynomial
};


extern BAP_DLL void bap_begin_itercoeff_mpq (
    struct bap_itercoeff_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL void bap_end_itercoeff_mpq (
    struct bap_itercoeff_mpq *,
    struct bap_polynom_mpq *,
    struct bav_variable *);

extern BAP_DLL bool bap_outof_itercoeff_mpq (
    struct bap_itercoeff_mpq *);

extern BAP_DLL void bap_close_itercoeff_mpq (
    struct bap_itercoeff_mpq *);

extern BAP_DLL void bap_next_itercoeff_mpq (
    struct bap_itercoeff_mpq *);

extern BAP_DLL void bap_prev_itercoeff_mpq (
    struct bap_itercoeff_mpq *);

extern BAP_DLL void bap_term_itercoeff_mpq (
    struct bav_term *,
    struct bap_itercoeff_mpq *);

extern BAP_DLL void bap_coeff_itercoeff_mpq (
    struct bap_polynom_mpq *,
    struct bap_itercoeff_mpq *);

extern BAP_DLL void bap_seek_coeff_itercoeff_mpq (
    struct bap_polynom_mpq *,
    struct bap_itercoeff_mpq *,
    struct bav_term *);

extern BAP_DLL void bap_split_polynom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *,
    struct bav_term *);

END_C_DECLS
#   undef  BAD_FLAG_mpq
#endif /* !BAP_ITERKOEFF_mpq_H */
#if !defined (BAP_ITERKOEFF_mint_hp_H)
#   define BAP_ITERKOEFF_mint_hp_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mint_hp.h" */
/* #   include "bap_itermon_mint_hp.h" */

#   define BAD_FLAG_mint_hp

BEGIN_C_DECLS

/*
 * texinfo: bap_itercoeff_mint_hp
 * This data type implements an iterator of coefficients of a 
 * differential polynomials, with respect to a given variable.
 * Let @var{A} be a polynomial and @math{X = x_1 < \cdots < x_n} be 
 * the alphabet of the variables it depends on. 
 * Let @math{1 \leq i \leq n} be an index.
 * The iterator permits to extract the coefficients of @var{A}, viewed as 
 * a polynomial over the alphabet @math{x_i, \ldots, x_n}, with 
 * coefficients in the ring of the polynomials over the alphabet 
 * @math{x_1, \ldots, x_{i-1}}.
 */

struct bap_itercoeff_mint_hp
{
  struct bap_polynom_mint_hp *poly;       // the polynomial
  struct bav_variable *last_variable;   // the lowest variable among the terms
// debut is set on the first monomial of the current coefficient
  struct bap_itermon_mint_hp debut;
// fin is set on the last monomial of the current coefficient
  struct bap_itermon_mint_hp fin;
  bool outof;                   // true if the iterator is outside the polynomial
};


extern BAP_DLL void bap_begin_itercoeff_mint_hp (
    struct bap_itercoeff_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

extern BAP_DLL void bap_end_itercoeff_mint_hp (
    struct bap_itercoeff_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_variable *);

extern BAP_DLL bool bap_outof_itercoeff_mint_hp (
    struct bap_itercoeff_mint_hp *);

extern BAP_DLL void bap_close_itercoeff_mint_hp (
    struct bap_itercoeff_mint_hp *);

extern BAP_DLL void bap_next_itercoeff_mint_hp (
    struct bap_itercoeff_mint_hp *);

extern BAP_DLL void bap_prev_itercoeff_mint_hp (
    struct bap_itercoeff_mint_hp *);

extern BAP_DLL void bap_term_itercoeff_mint_hp (
    struct bav_term *,
    struct bap_itercoeff_mint_hp *);

extern BAP_DLL void bap_coeff_itercoeff_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_itercoeff_mint_hp *);

extern BAP_DLL void bap_seek_coeff_itercoeff_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_itercoeff_mint_hp *,
    struct bav_term *);

extern BAP_DLL void bap_split_polynom_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mint_hp *,
    struct bav_term *);

END_C_DECLS
#   undef  BAD_FLAG_mint_hp
#endif /* !BAP_ITERKOEFF_mint_hp_H */
#if !defined (BAP_PRODUCT_mpz_H)
#   define BAP_PRODUCT_mpz_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mpz.h" */

#   define BAD_FLAG_mpz

BEGIN_C_DECLS

/*
 * texinfo: bap_power_mpz
 * This data type implements a polynomial raised to some power.
 */

struct bap_power_mpz
{
  struct bap_polynom_mpz factor;
  bav_Idegree exponent;
};


/*
 * texinfo: bap_product_mpz
 * This data type implements products of polynomials of the form
 * @math{c \, f_1^{a_1} \cdots f_t^{a_t}}
 * where @var{c} is the @dfn{numerical factor} of the product, 
 * the @math{f_i} are non numerical polynomials, not necessarily 
 * irreducible and not even necessarily pairwise distinct. 
 * The exponents @math{a_i} are allowed to be zero. 
 * The product one is coded by @math{c = 1} and @math{t = 0}. 
 * The product zero is coded by @math{c = 0}.  
 * Observe that in the context of rings which are not domains, 
 * zero and one are not necessarily automatically recognized.
 */

struct bap_product_mpz
{
// the numerical factor
  ba0_mpz_t num_factor;
// the number of allocated entries of tab
  ba0_int_p alloc;
// the number of used entries
  ba0_int_p size;
// the array of bap_power_mpz
  struct bap_power_mpz *tab;
};

struct bap_tableof_product_mpz
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bap_product_mpz **tab;
};

extern BAP_DLL void bap_init_power_mpz (
    struct bap_power_mpz *);

extern BAP_DLL struct bap_power_mpz *bap_new_power_mpz (
    void);

extern BAP_DLL void bap_set_power_mpz (
    struct bap_power_mpz *,
    struct bap_power_mpz *);

extern BAP_DLL void bap_set_power_polynom_mpz (
    struct bap_power_mpz *,
    struct bap_polynom_mpz *,
    bav_Idegree);

extern BAP_DLL void bap_pow_power_mpz (
    struct bap_power_mpz *,
    struct bap_power_mpz *,
    bav_Idegree);

extern BAP_DLL void bap_init_product_mpz (
    struct bap_product_mpz *);

extern BAP_DLL void bap_init_product_zero_mpz (
    struct bap_product_mpz *);

extern BAP_DLL void bap_realloc_product_mpz (
    struct bap_product_mpz *,
    ba0_int_p);

extern BAP_DLL struct bap_product_mpz *bap_new_product_mpz (
    void);

extern BAP_DLL struct bap_product_mpz *bap_new_product_zero_mpz (
    void);

extern BAP_DLL bool bap_is_zero_product_mpz (
    struct bap_product_mpz *);

extern BAP_DLL bool bap_is_one_product_mpz (
    struct bap_product_mpz *);

extern BAP_DLL bool bap_is_numeric_product_mpz (
    struct bap_product_mpz *);

extern BAP_DLL struct bav_variable * bap_leader_product_mpz (
    struct bap_product_mpz *);

extern BAP_DLL void bap_set_product_zero_mpz (
    struct bap_product_mpz *);

extern BAP_DLL void bap_set_product_one_mpz (
    struct bap_product_mpz *);

extern BAP_DLL void bap_set_product_numeric_mpz (
    struct bap_product_mpz *,
    ba0_mpz_t);

extern BAP_DLL void bap_set_product_polynom_mpz (
    struct bap_product_mpz *,
    struct bap_polynom_mpz *,
    bav_Idegree);

extern BAP_DLL void bap_set_product_mpz (
    struct bap_product_mpz *,
    struct bap_product_mpz *);

extern BAP_DLL void bap_expand_product_mpz (
    struct bap_polynom_mpz *,
    struct bap_product_mpz *);

extern BAP_DLL void bap_mul_product_polynom_mpz (
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bap_polynom_mpz *,
    bav_Idegree);

extern BAP_DLL void bap_neg_product_mpz (
    struct bap_product_mpz *,
    struct bap_product_mpz *);

extern BAP_DLL void bap_mul_product_numeric_mpz (
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    ba0_mpz_t);

extern BAP_DLL void bap_mul_product_term_mpz (
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bav_term *);

extern BAP_DLL void bap_mul_product_mpz (
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bap_product_mpz *);

extern BAP_DLL void bap_pow_product_mpz (
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    bav_Idegree);

extern BAP_DLL void bap_exquo_product_polynom_mpz (
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bap_polynom_mpz *,
    bav_Idegree);

extern BAP_DLL bav_Idegree bap_exponent_product_mpz (
    struct bap_product_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_sort_product_mpz (
    struct bap_product_mpz *,
    struct bap_product_mpz *);

extern BAP_DLL void bap_physort_product_mpz (
    struct bap_product_mpz *);

extern BAP_DLL ba0_scanf_function bap_scanf_product_mpz;

extern BAP_DLL ba0_printf_function bap_printf_product_mpz;

extern BAP_DLL ba0_garbage1_function bap_garbage1_product_mpz;

extern BAP_DLL ba0_garbage2_function bap_garbage2_product_mpz;

extern BAP_DLL ba0_copy_function bap_copy_product_mpz;

END_C_DECLS
#   undef BAD_FLAG_mpz
#endif /* !BAP_PRODUCT_mpz_H */
#if !defined (BAP_PRODUCT_mpzm_H)
#   define BAP_PRODUCT_mpzm_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mpzm.h" */

#   define BAD_FLAG_mpzm

BEGIN_C_DECLS

/*
 * texinfo: bap_power_mpzm
 * This data type implements a polynomial raised to some power.
 */

struct bap_power_mpzm
{
  struct bap_polynom_mpzm factor;
  bav_Idegree exponent;
};


/*
 * texinfo: bap_product_mpzm
 * This data type implements products of polynomials of the form
 * @math{c \, f_1^{a_1} \cdots f_t^{a_t}}
 * where @var{c} is the @dfn{numerical factor} of the product, 
 * the @math{f_i} are non numerical polynomials, not necessarily 
 * irreducible and not even necessarily pairwise distinct. 
 * The exponents @math{a_i} are allowed to be zero. 
 * The product one is coded by @math{c = 1} and @math{t = 0}. 
 * The product zero is coded by @math{c = 0}.  
 * Observe that in the context of rings which are not domains, 
 * zero and one are not necessarily automatically recognized.
 */

struct bap_product_mpzm
{
// the numerical factor
  ba0_mpzm_t num_factor;
// the number of allocated entries of tab
  ba0_int_p alloc;
// the number of used entries
  ba0_int_p size;
// the array of bap_power_mpzm
  struct bap_power_mpzm *tab;
};

struct bap_tableof_product_mpzm
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bap_product_mpzm **tab;
};

extern BAP_DLL void bap_init_power_mpzm (
    struct bap_power_mpzm *);

extern BAP_DLL struct bap_power_mpzm *bap_new_power_mpzm (
    void);

extern BAP_DLL void bap_set_power_mpzm (
    struct bap_power_mpzm *,
    struct bap_power_mpzm *);

extern BAP_DLL void bap_set_power_polynom_mpzm (
    struct bap_power_mpzm *,
    struct bap_polynom_mpzm *,
    bav_Idegree);

extern BAP_DLL void bap_pow_power_mpzm (
    struct bap_power_mpzm *,
    struct bap_power_mpzm *,
    bav_Idegree);

extern BAP_DLL void bap_init_product_mpzm (
    struct bap_product_mpzm *);

extern BAP_DLL void bap_init_product_zero_mpzm (
    struct bap_product_mpzm *);

extern BAP_DLL void bap_realloc_product_mpzm (
    struct bap_product_mpzm *,
    ba0_int_p);

extern BAP_DLL struct bap_product_mpzm *bap_new_product_mpzm (
    void);

extern BAP_DLL struct bap_product_mpzm *bap_new_product_zero_mpzm (
    void);

extern BAP_DLL bool bap_is_zero_product_mpzm (
    struct bap_product_mpzm *);

extern BAP_DLL bool bap_is_one_product_mpzm (
    struct bap_product_mpzm *);

extern BAP_DLL bool bap_is_numeric_product_mpzm (
    struct bap_product_mpzm *);

extern BAP_DLL struct bav_variable * bap_leader_product_mpzm (
    struct bap_product_mpzm *);

extern BAP_DLL void bap_set_product_zero_mpzm (
    struct bap_product_mpzm *);

extern BAP_DLL void bap_set_product_one_mpzm (
    struct bap_product_mpzm *);

extern BAP_DLL void bap_set_product_numeric_mpzm (
    struct bap_product_mpzm *,
    ba0_mpzm_t);

extern BAP_DLL void bap_set_product_polynom_mpzm (
    struct bap_product_mpzm *,
    struct bap_polynom_mpzm *,
    bav_Idegree);

extern BAP_DLL void bap_set_product_mpzm (
    struct bap_product_mpzm *,
    struct bap_product_mpzm *);

extern BAP_DLL void bap_expand_product_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_product_mpzm *);

extern BAP_DLL void bap_mul_product_polynom_mpzm (
    struct bap_product_mpzm *,
    struct bap_product_mpzm *,
    struct bap_polynom_mpzm *,
    bav_Idegree);

extern BAP_DLL void bap_neg_product_mpzm (
    struct bap_product_mpzm *,
    struct bap_product_mpzm *);

extern BAP_DLL void bap_mul_product_numeric_mpzm (
    struct bap_product_mpzm *,
    struct bap_product_mpzm *,
    ba0_mpzm_t);

extern BAP_DLL void bap_mul_product_term_mpzm (
    struct bap_product_mpzm *,
    struct bap_product_mpzm *,
    struct bav_term *);

extern BAP_DLL void bap_mul_product_mpzm (
    struct bap_product_mpzm *,
    struct bap_product_mpzm *,
    struct bap_product_mpzm *);

extern BAP_DLL void bap_pow_product_mpzm (
    struct bap_product_mpzm *,
    struct bap_product_mpzm *,
    bav_Idegree);

extern BAP_DLL void bap_exquo_product_polynom_mpzm (
    struct bap_product_mpzm *,
    struct bap_product_mpzm *,
    struct bap_polynom_mpzm *,
    bav_Idegree);

extern BAP_DLL bav_Idegree bap_exponent_product_mpzm (
    struct bap_product_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_sort_product_mpzm (
    struct bap_product_mpzm *,
    struct bap_product_mpzm *);

extern BAP_DLL void bap_physort_product_mpzm (
    struct bap_product_mpzm *);

extern BAP_DLL ba0_scanf_function bap_scanf_product_mpzm;

extern BAP_DLL ba0_printf_function bap_printf_product_mpzm;

extern BAP_DLL ba0_garbage1_function bap_garbage1_product_mpzm;

extern BAP_DLL ba0_garbage2_function bap_garbage2_product_mpzm;

extern BAP_DLL ba0_copy_function bap_copy_product_mpzm;

END_C_DECLS
#   undef BAD_FLAG_mpzm
#endif /* !BAP_PRODUCT_mpzm_H */
#if !defined (BAP_PRODUCT_mpq_H)
#   define BAP_PRODUCT_mpq_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mpq.h" */

#   define BAD_FLAG_mpq

BEGIN_C_DECLS

/*
 * texinfo: bap_power_mpq
 * This data type implements a polynomial raised to some power.
 */

struct bap_power_mpq
{
  struct bap_polynom_mpq factor;
  bav_Idegree exponent;
};


/*
 * texinfo: bap_product_mpq
 * This data type implements products of polynomials of the form
 * @math{c \, f_1^{a_1} \cdots f_t^{a_t}}
 * where @var{c} is the @dfn{numerical factor} of the product, 
 * the @math{f_i} are non numerical polynomials, not necessarily 
 * irreducible and not even necessarily pairwise distinct. 
 * The exponents @math{a_i} are allowed to be zero. 
 * The product one is coded by @math{c = 1} and @math{t = 0}. 
 * The product zero is coded by @math{c = 0}.  
 * Observe that in the context of rings which are not domains, 
 * zero and one are not necessarily automatically recognized.
 */

struct bap_product_mpq
{
// the numerical factor
  ba0_mpq_t num_factor;
// the number of allocated entries of tab
  ba0_int_p alloc;
// the number of used entries
  ba0_int_p size;
// the array of bap_power_mpq
  struct bap_power_mpq *tab;
};

struct bap_tableof_product_mpq
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bap_product_mpq **tab;
};

extern BAP_DLL void bap_init_power_mpq (
    struct bap_power_mpq *);

extern BAP_DLL struct bap_power_mpq *bap_new_power_mpq (
    void);

extern BAP_DLL void bap_set_power_mpq (
    struct bap_power_mpq *,
    struct bap_power_mpq *);

extern BAP_DLL void bap_set_power_polynom_mpq (
    struct bap_power_mpq *,
    struct bap_polynom_mpq *,
    bav_Idegree);

extern BAP_DLL void bap_pow_power_mpq (
    struct bap_power_mpq *,
    struct bap_power_mpq *,
    bav_Idegree);

extern BAP_DLL void bap_init_product_mpq (
    struct bap_product_mpq *);

extern BAP_DLL void bap_init_product_zero_mpq (
    struct bap_product_mpq *);

extern BAP_DLL void bap_realloc_product_mpq (
    struct bap_product_mpq *,
    ba0_int_p);

extern BAP_DLL struct bap_product_mpq *bap_new_product_mpq (
    void);

extern BAP_DLL struct bap_product_mpq *bap_new_product_zero_mpq (
    void);

extern BAP_DLL bool bap_is_zero_product_mpq (
    struct bap_product_mpq *);

extern BAP_DLL bool bap_is_one_product_mpq (
    struct bap_product_mpq *);

extern BAP_DLL bool bap_is_numeric_product_mpq (
    struct bap_product_mpq *);

extern BAP_DLL struct bav_variable * bap_leader_product_mpq (
    struct bap_product_mpq *);

extern BAP_DLL void bap_set_product_zero_mpq (
    struct bap_product_mpq *);

extern BAP_DLL void bap_set_product_one_mpq (
    struct bap_product_mpq *);

extern BAP_DLL void bap_set_product_numeric_mpq (
    struct bap_product_mpq *,
    ba0_mpq_t);

extern BAP_DLL void bap_set_product_polynom_mpq (
    struct bap_product_mpq *,
    struct bap_polynom_mpq *,
    bav_Idegree);

extern BAP_DLL void bap_set_product_mpq (
    struct bap_product_mpq *,
    struct bap_product_mpq *);

extern BAP_DLL void bap_expand_product_mpq (
    struct bap_polynom_mpq *,
    struct bap_product_mpq *);

extern BAP_DLL void bap_mul_product_polynom_mpq (
    struct bap_product_mpq *,
    struct bap_product_mpq *,
    struct bap_polynom_mpq *,
    bav_Idegree);

extern BAP_DLL void bap_neg_product_mpq (
    struct bap_product_mpq *,
    struct bap_product_mpq *);

extern BAP_DLL void bap_mul_product_numeric_mpq (
    struct bap_product_mpq *,
    struct bap_product_mpq *,
    ba0_mpq_t);

extern BAP_DLL void bap_mul_product_term_mpq (
    struct bap_product_mpq *,
    struct bap_product_mpq *,
    struct bav_term *);

extern BAP_DLL void bap_mul_product_mpq (
    struct bap_product_mpq *,
    struct bap_product_mpq *,
    struct bap_product_mpq *);

extern BAP_DLL void bap_pow_product_mpq (
    struct bap_product_mpq *,
    struct bap_product_mpq *,
    bav_Idegree);

extern BAP_DLL void bap_exquo_product_polynom_mpq (
    struct bap_product_mpq *,
    struct bap_product_mpq *,
    struct bap_polynom_mpq *,
    bav_Idegree);

extern BAP_DLL bav_Idegree bap_exponent_product_mpq (
    struct bap_product_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_sort_product_mpq (
    struct bap_product_mpq *,
    struct bap_product_mpq *);

extern BAP_DLL void bap_physort_product_mpq (
    struct bap_product_mpq *);

extern BAP_DLL ba0_scanf_function bap_scanf_product_mpq;

extern BAP_DLL ba0_printf_function bap_printf_product_mpq;

extern BAP_DLL ba0_garbage1_function bap_garbage1_product_mpq;

extern BAP_DLL ba0_garbage2_function bap_garbage2_product_mpq;

extern BAP_DLL ba0_copy_function bap_copy_product_mpq;

END_C_DECLS
#   undef BAD_FLAG_mpq
#endif /* !BAP_PRODUCT_mpq_H */
#if !defined (BAP_PRODUCT_mint_hp_H)
#   define BAP_PRODUCT_mint_hp_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mint_hp.h" */

#   define BAD_FLAG_mint_hp

BEGIN_C_DECLS

/*
 * texinfo: bap_power_mint_hp
 * This data type implements a polynomial raised to some power.
 */

struct bap_power_mint_hp
{
  struct bap_polynom_mint_hp factor;
  bav_Idegree exponent;
};


/*
 * texinfo: bap_product_mint_hp
 * This data type implements products of polynomials of the form
 * @math{c \, f_1^{a_1} \cdots f_t^{a_t}}
 * where @var{c} is the @dfn{numerical factor} of the product, 
 * the @math{f_i} are non numerical polynomials, not necessarily 
 * irreducible and not even necessarily pairwise distinct. 
 * The exponents @math{a_i} are allowed to be zero. 
 * The product one is coded by @math{c = 1} and @math{t = 0}. 
 * The product zero is coded by @math{c = 0}.  
 * Observe that in the context of rings which are not domains, 
 * zero and one are not necessarily automatically recognized.
 */

struct bap_product_mint_hp
{
// the numerical factor
  ba0_mint_hp_t num_factor;
// the number of allocated entries of tab
  ba0_int_p alloc;
// the number of used entries
  ba0_int_p size;
// the array of bap_power_mint_hp
  struct bap_power_mint_hp *tab;
};

struct bap_tableof_product_mint_hp
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bap_product_mint_hp **tab;
};

extern BAP_DLL void bap_init_power_mint_hp (
    struct bap_power_mint_hp *);

extern BAP_DLL struct bap_power_mint_hp *bap_new_power_mint_hp (
    void);

extern BAP_DLL void bap_set_power_mint_hp (
    struct bap_power_mint_hp *,
    struct bap_power_mint_hp *);

extern BAP_DLL void bap_set_power_polynom_mint_hp (
    struct bap_power_mint_hp *,
    struct bap_polynom_mint_hp *,
    bav_Idegree);

extern BAP_DLL void bap_pow_power_mint_hp (
    struct bap_power_mint_hp *,
    struct bap_power_mint_hp *,
    bav_Idegree);

extern BAP_DLL void bap_init_product_mint_hp (
    struct bap_product_mint_hp *);

extern BAP_DLL void bap_init_product_zero_mint_hp (
    struct bap_product_mint_hp *);

extern BAP_DLL void bap_realloc_product_mint_hp (
    struct bap_product_mint_hp *,
    ba0_int_p);

extern BAP_DLL struct bap_product_mint_hp *bap_new_product_mint_hp (
    void);

extern BAP_DLL struct bap_product_mint_hp *bap_new_product_zero_mint_hp (
    void);

extern BAP_DLL bool bap_is_zero_product_mint_hp (
    struct bap_product_mint_hp *);

extern BAP_DLL bool bap_is_one_product_mint_hp (
    struct bap_product_mint_hp *);

extern BAP_DLL bool bap_is_numeric_product_mint_hp (
    struct bap_product_mint_hp *);

extern BAP_DLL struct bav_variable * bap_leader_product_mint_hp (
    struct bap_product_mint_hp *);

extern BAP_DLL void bap_set_product_zero_mint_hp (
    struct bap_product_mint_hp *);

extern BAP_DLL void bap_set_product_one_mint_hp (
    struct bap_product_mint_hp *);

extern BAP_DLL void bap_set_product_numeric_mint_hp (
    struct bap_product_mint_hp *,
    ba0_mint_hp_t);

extern BAP_DLL void bap_set_product_polynom_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_polynom_mint_hp *,
    bav_Idegree);

extern BAP_DLL void bap_set_product_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_product_mint_hp *);

extern BAP_DLL void bap_expand_product_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_product_mint_hp *);

extern BAP_DLL void bap_mul_product_polynom_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_product_mint_hp *,
    struct bap_polynom_mint_hp *,
    bav_Idegree);

extern BAP_DLL void bap_neg_product_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_product_mint_hp *);

extern BAP_DLL void bap_mul_product_numeric_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_product_mint_hp *,
    ba0_mint_hp_t);

extern BAP_DLL void bap_mul_product_term_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_product_mint_hp *,
    struct bav_term *);

extern BAP_DLL void bap_mul_product_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_product_mint_hp *,
    struct bap_product_mint_hp *);

extern BAP_DLL void bap_pow_product_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_product_mint_hp *,
    bav_Idegree);

extern BAP_DLL void bap_exquo_product_polynom_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_product_mint_hp *,
    struct bap_polynom_mint_hp *,
    bav_Idegree);

extern BAP_DLL bav_Idegree bap_exponent_product_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_sort_product_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_product_mint_hp *);

extern BAP_DLL void bap_physort_product_mint_hp (
    struct bap_product_mint_hp *);

extern BAP_DLL ba0_scanf_function bap_scanf_product_mint_hp;

extern BAP_DLL ba0_printf_function bap_printf_product_mint_hp;

extern BAP_DLL ba0_garbage1_function bap_garbage1_product_mint_hp;

extern BAP_DLL ba0_garbage2_function bap_garbage2_product_mint_hp;

extern BAP_DLL ba0_copy_function bap_copy_product_mint_hp;

END_C_DECLS
#   undef BAD_FLAG_mint_hp
#endif /* !BAP_PRODUCT_mint_hp_H */
#if !defined (BAP_GEOBUCKET_mpz_H)
#   define BAP_GEOBUCKET_mpz_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mpz.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpz

/*
 * texinfo: bap_geobucket_mpz
 * A geobucket (JSC (1998) 25, 285-293, Thomas Yan) is a table of polynomials
 * representing the sum of these polynomials. This data structure
 * permits to improve the complexity of the sum of many different
 * polynomials.
 * The polynomial at index @var{i} is a sum of at most @var{2^i} 
 * monomials.
 * The data structure is a duplicate of @code{bap_tableof_polynomial}.
 */

struct bap_geobucket_mpz
{
// number of allocated entries
  ba0_int_p alloc;
// number of used entries
  ba0_int_p size;
// the array
  struct bap_polynom_mpz **tab;
};



extern BAP_DLL void bap_init_geobucket_mpz (
    struct bap_geobucket_mpz *);

extern BAP_DLL void bap_reset_geobucket_mpz (
    struct bap_geobucket_mpz *);

extern BAP_DLL void bap_mul_geobucket_mpz (
    struct bap_geobucket_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_mul_geobucket_numeric_mpz (
    struct bap_geobucket_mpz *,
    ba0_mpz_t);

extern BAP_DLL void bap_add_geobucket_mpz (
    struct bap_geobucket_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_sub_geobucket_mpz (
    struct bap_geobucket_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_set_polynom_geobucket_mpz (
    struct bap_polynom_mpz *,
    struct bap_geobucket_mpz *);

#   undef BAD_FLAG_mpz

END_C_DECLS
#endif /* !BAP_GEOBUCKET_mpz_H */
#if !defined (BAP_GEOBUCKET_mpzm_H)
#   define BAP_GEOBUCKET_mpzm_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mpzm.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpzm

/*
 * texinfo: bap_geobucket_mpzm
 * A geobucket (JSC (1998) 25, 285-293, Thomas Yan) is a table of polynomials
 * representing the sum of these polynomials. This data structure
 * permits to improve the complexity of the sum of many different
 * polynomials.
 * The polynomial at index @var{i} is a sum of at most @var{2^i} 
 * monomials.
 * The data structure is a duplicate of @code{bap_tableof_polynomial}.
 */

struct bap_geobucket_mpzm
{
// number of allocated entries
  ba0_int_p alloc;
// number of used entries
  ba0_int_p size;
// the array
  struct bap_polynom_mpzm **tab;
};



extern BAP_DLL void bap_init_geobucket_mpzm (
    struct bap_geobucket_mpzm *);

extern BAP_DLL void bap_reset_geobucket_mpzm (
    struct bap_geobucket_mpzm *);

extern BAP_DLL void bap_mul_geobucket_mpzm (
    struct bap_geobucket_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_mul_geobucket_numeric_mpzm (
    struct bap_geobucket_mpzm *,
    ba0_mpzm_t);

extern BAP_DLL void bap_add_geobucket_mpzm (
    struct bap_geobucket_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_sub_geobucket_mpzm (
    struct bap_geobucket_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_set_polynom_geobucket_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_geobucket_mpzm *);

#   undef BAD_FLAG_mpzm

END_C_DECLS
#endif /* !BAP_GEOBUCKET_mpzm_H */
#if !defined (BAP_GEOBUCKET_mpq_H)
#   define BAP_GEOBUCKET_mpq_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mpq.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mpq

/*
 * texinfo: bap_geobucket_mpq
 * A geobucket (JSC (1998) 25, 285-293, Thomas Yan) is a table of polynomials
 * representing the sum of these polynomials. This data structure
 * permits to improve the complexity of the sum of many different
 * polynomials.
 * The polynomial at index @var{i} is a sum of at most @var{2^i} 
 * monomials.
 * The data structure is a duplicate of @code{bap_tableof_polynomial}.
 */

struct bap_geobucket_mpq
{
// number of allocated entries
  ba0_int_p alloc;
// number of used entries
  ba0_int_p size;
// the array
  struct bap_polynom_mpq **tab;
};



extern BAP_DLL void bap_init_geobucket_mpq (
    struct bap_geobucket_mpq *);

extern BAP_DLL void bap_reset_geobucket_mpq (
    struct bap_geobucket_mpq *);

extern BAP_DLL void bap_mul_geobucket_mpq (
    struct bap_geobucket_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_mul_geobucket_numeric_mpq (
    struct bap_geobucket_mpq *,
    ba0_mpq_t);

extern BAP_DLL void bap_add_geobucket_mpq (
    struct bap_geobucket_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_sub_geobucket_mpq (
    struct bap_geobucket_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_set_polynom_geobucket_mpq (
    struct bap_polynom_mpq *,
    struct bap_geobucket_mpq *);

#   undef BAD_FLAG_mpq

END_C_DECLS
#endif /* !BAP_GEOBUCKET_mpq_H */
#if !defined (BAP_GEOBUCKET_mint_hp_H)
#   define BAP_GEOBUCKET_mint_hp_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mint_hp.h" */

BEGIN_C_DECLS

#   define BAD_FLAG_mint_hp

/*
 * texinfo: bap_geobucket_mint_hp
 * A geobucket (JSC (1998) 25, 285-293, Thomas Yan) is a table of polynomials
 * representing the sum of these polynomials. This data structure
 * permits to improve the complexity of the sum of many different
 * polynomials.
 * The polynomial at index @var{i} is a sum of at most @var{2^i} 
 * monomials.
 * The data structure is a duplicate of @code{bap_tableof_polynomial}.
 */

struct bap_geobucket_mint_hp
{
// number of allocated entries
  ba0_int_p alloc;
// number of used entries
  ba0_int_p size;
// the array
  struct bap_polynom_mint_hp **tab;
};



extern BAP_DLL void bap_init_geobucket_mint_hp (
    struct bap_geobucket_mint_hp *);

extern BAP_DLL void bap_reset_geobucket_mint_hp (
    struct bap_geobucket_mint_hp *);

extern BAP_DLL void bap_mul_geobucket_mint_hp (
    struct bap_geobucket_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_mul_geobucket_numeric_mint_hp (
    struct bap_geobucket_mint_hp *,
    ba0_mint_hp_t);

extern BAP_DLL void bap_add_geobucket_mint_hp (
    struct bap_geobucket_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_sub_geobucket_mint_hp (
    struct bap_geobucket_mint_hp *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_set_polynom_geobucket_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_geobucket_mint_hp *);

#   undef BAD_FLAG_mint_hp

END_C_DECLS
#endif /* !BAP_GEOBUCKET_mint_hp_H */
#if !defined (BAP_POLYSPEC_MPZ_H)
#   define BAP_POLYSPEC_MPZ_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mpz.h" */
/* #   include "bap_product_mpz.h" */
/* #   include "bap_polynom_mpzm.h" */
/* #   include "bap_product_mpzm.h" */
/* #   include "bap_polynom_mpq.h" */

BEGIN_C_DECLS

extern BAP_DLL void bap_polynom_mpq_to_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_maxnorm_polynom_mpz (
    ba0_mpz_t,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_normal_sign_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_numeric_content_polynom_mpz (
    ba0_mpz_t,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_signed_numeric_content_polynom_mpz (
    ba0_mpz_t,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_numeric_primpart_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_normal_numeric_primpart_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_exquo_polynom_numeric_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    ba0_mpz_t);

extern BAP_DLL bool bap_is_numeric_factor_polynom_mpz (
    struct bap_polynom_mpz *,
    ba0_mpz_t,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_replace_initial2_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_product_mpz *,
    struct bap_product_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_separant_and_sepuctum_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_sepuctum_polynom_mpz (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpz *);

END_C_DECLS
#endif /* !BAP_POLYSPEC_MPZ_H */
#if !defined (BAP_POLYSPEC_MPZM_H)
#   define BAP_POLYSPEC_MPZM_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mpz.h" */
/* #   include "bap_polynom_mpzm.h" */
/* #   include "bap_polynom_mpq.h" */
/* #   include "bap_polynom_mint_hp.h" */
/* #   include "bap_product_mpz.h" */
/* #   include "bap_product_mpzm.h" */

BEGIN_C_DECLS

extern BAP_DLL void bap_polynom_mpq_to_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_polynom_mpz_to_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_polynom_mint_hp_to_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mint_hp *);

extern BAP_DLL void bap_mods_polynom_mpzm (
    struct bap_polynom_mpz *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_mods_product_mpzm (
    struct bap_product_mpz *,
    struct bap_product_mpzm *);

extern BAP_DLL void bap_Bezout_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    ba0_mpz_t,
    bav_Idegree);

extern BAP_DLL void bap_coeftayl_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_value_int_p *,
    bav_Idegree);

extern BAP_DLL void bap_quorem_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_rank *,
    struct bap_polynom_mpzm *,
    struct bap_polynom_mpzm *);

extern BAP_DLL void bap_uni_Diophante_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_product_mpzm *,
    struct bav_rank *,
    ba0_mpz_t,
    bav_Idegree);

extern BAP_DLL void bap_multi_Diophante_polynom_mpzm (
    struct bap_polynom_mpzm *,
    struct bap_product_mpzm *,
    struct bap_polynom_mpzm *,
    struct bav_point_int_p *,
    bav_Idegree,
    ba0_mpz_t,
    bav_Idegree);

END_C_DECLS
#endif /* !BAP_POLYSPEC_MPZM_H */
#if !defined (BAP_POLYSPEC_MPQ_H)
#   define BAP_POLYSPEC_MPQ_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mpq.h" */
/* #   include "bap_polynom_mpz.h" */
/* #   include "bap_product_mpq.h" */

BEGIN_C_DECLS

extern BAP_DLL void bap_polynom_mpq_to_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_polynom_mpz_to_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_set_polynom_numer_denom_mpq (
    struct bap_polynom_mpq *,
    struct bap_polynom_mpz *,
    ba0_mpz_t);

extern BAP_DLL void bap_product_mpz_to_mpq (
    struct bap_product_mpq *,
    struct bap_product_mpz *);

extern BAP_DLL void bap_numer_polynom_mpq (
    struct bap_polynom_mpz *,
    ba0_mpz_t,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_denom_polynom_mpq (
    ba0_mpz_t,
    struct bap_polynom_mpq *);

END_C_DECLS
#endif /* !BAP_POLYSPEC_MPQ_H */
#if !defined (BAP_POLYSPEC_MINT_HP_H)
#   define BAP_POLYSPEC_MINT_HP_H 1

/* #   include "bap_common.h" */
/* #   include "bap_polynom_mpz.h" */
/* #   include "bap_polynom_mpzm.h" */
/* #   include "bap_polynom_mpq.h" */
/* #   include "bap_polynom_mint_hp.h" */
/* #   include "bap_product_mint_hp.h" */

BEGIN_C_DECLS
/* 
 * Polynomials with coefficients in Z/nZ where n is a small integer.
 * Precisely, polynomials with coefficients
 * 
 * ba0_mint_hp modulo ba0_mint_hp_module */
extern BAP_DLL void bap_polynom_mpq_to_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mpq *);

extern BAP_DLL void bap_polynom_mpz_to_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mpz *);

extern BAP_DLL void bap_random_eval_polynom_mpz_to_mint_hp (
    struct bap_polynom_mint_hp *,
    struct bap_polynom_mpz *,
    ba0_unary_predicate *);

extern BAP_DLL void bap_Berlekamp_mint_hp (
    struct bap_product_mint_hp *,
    struct bap_polynom_mint_hp *);

END_C_DECLS
#endif /* !BAP_POLYSPEC_MINT_HP_H */
