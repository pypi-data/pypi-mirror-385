#include "bav_parameters.h"
#include "bav_differential_ring.h"
#include "bav_global.h"

/*  
 * For dict - only non-plain range indexed strings are stored in dict
 */

static char *
bav_parameter_to_identifier (
    void *object)
{
  struct ba0_range_indexed_group *G = (struct ba0_range_indexed_group *) object;
  char *string;

  if (ba0_is_plain_string_range_indexed_group (G, &string))
    return "";
  else
    return string;
}

/*
 * texinfo: bav_init_parameters
 * Initialize @var{pars}.
 */

BAV_DLL void
bav_init_parameters (
    struct bav_parameters *pars)
{
  ba0_init_dictionary_string (&pars->dict, &bav_parameter_to_identifier, 8);
  ba0_init_table ((struct ba0_table *) &pars->pars);
}

/*
 * texinfo: bav_sizeof_parameters
 * Return the size needed to copy @var{pars}.
 * If @var{code} is @code{ba0_embedded} then @var{pars} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account.
 * If @var{strings_not_copied} then the strings occurring in @var{b}
 * are supposed not to be copied.
 */

BAV_DLL unsigned ba0_int_p
bav_sizeof_parameters (
    struct bav_parameters *pars,
    enum ba0_garbage_code code,
    bool strings_not_copied)
{
  unsigned ba0_int_p size;

  if (!strings_not_copied)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);

  if (code == ba0_isolated)
    size = ba0_allocated_size (sizeof (struct bav_parameters));
  else
    size = 0;
  size += ba0_sizeof_dictionary_string (&pars->dict, ba0_embedded);
  size += bav_sizeof_tableof_parameter (&pars->pars, ba0_embedded,
      strings_not_copied);
  return size;
}

/*
 * texinfo: bav_R_set_parameters
 * Copy @var{src} into @var{dst} without performing any string allocation.
 * The strings occurring in @var{src} are supposed to be present in @var{R}.
 * Each time a string has to be assigned, its copy in @var{R} is used.
 * The size needed for the copy is the one returned by
 * @code{bav_sizeof_parameters}.
 */

BAV_DLL void
bav_R_set_parameters (
    struct bav_parameters *dst,
    struct bav_parameters *src,
    struct bav_differential_ring *R)
{
  ba0_set_dictionary_string (&dst->dict, &src->dict);
  bav_set_tableof_parameter_with_tableof_string (&dst->pars, &src->pars,
      &R->dict_str_to_str, &R->strs);
}

/*
 * texinfo: bav_R_set_parameters_tableof_parameter
 * Fill @var{pars} with the content of @var{T}.
 * This function is called by the parser of orderings, in order
 * to fill the @code{pars} field of @code{bav_global.R}.
 */

BAV_DLL void
bav_R_set_parameters_tableof_parameter (
    struct bav_parameters *pars,
    struct bav_tableof_parameter *T)
{
  struct bav_parameter tmp;
  struct ba0_mark M;
  ba0_int_p i, j, k, n;
  char *string;

  if (pars != &bav_global.R.pars)
    BA0_RAISE_EXCEPTION (BA0_ERRNYP);
/*
 * tmp is a temporary parameter which permits to split a parameter
 *  containing a range indexed group in many different parameters
 *  containing range indexed strings
 */
  ba0_push_another_stack ();
  ba0_record (&M);
  bav_init_parameter (&tmp);
  ba0_pull_stack ();
/*
 * Everything is stored in the quiet stack
 */
  ba0_push_stack (&ba0_global.stack.quiet);
/*
 * Count the number of entries needed for pars and allocate
 */
  n = 0;
  for (i = 0; i < T->size; i++)
    if (ba0_is_plain_string_range_indexed_group (&T->tab[i]->rig, (char **) 0))
      n += 1;
    else
      {
        struct ba0_range_indexed_group *G = &T->tab[i]->rig;
        n += G->strs.size;
      }

  ba0_reset_table ((struct ba0_table *) &pars->pars);
  ba0_realloc2_table ((struct ba0_table *) &pars->pars, n,
      (ba0_new_function *) & bav_new_parameter);
  ba0_reset_dictionary_string (&pars->dict);
/*
 * Copy T in pars->pars and split range indexed groups
 */
  for (i = 0; i < T->size; i++)
    if (ba0_is_plain_string_range_indexed_group (&T->tab[i]->rig, &string))
      {
        struct bav_symbol *y = bav_R_string_to_existing_symbol (string);
        if (y == BAV_NOT_A_SYMBOL)
          BA0_RAISE_EXCEPTION (BA0_ERRALG);
/*
 * Plain string range indexed groups are not recorded in dict
 */
        j = pars->pars.size;

        y->index_in_pars = j;

        bav_set_parameter_with_tableof_string (pars->pars.tab[j], T->tab[i],
            &bav_global.R.dict_str_to_str, &bav_global.R.strs);

        pars->pars.size += 1;
      }
    else
      {
        struct ba0_range_indexed_group *G = &T->tab[i]->rig;

        ba0_push_another_stack ();
        bav_set_parameter (&tmp, T->tab[i]);
        tmp.rig.strs.size = 1;
        ba0_pull_stack ();

        for (j = 0; j < G->strs.size; j++)
          {
            tmp.rig.strs.tab[0] = G->strs.tab[j];

            k = pars->pars.size;

            ba0_add_dictionary_string (&pars->dict,
                (struct ba0_table *) &pars->pars, G->strs.tab[j], k);

            bav_set_parameter_with_tableof_string (pars->pars.tab[k],
                &tmp, &bav_global.R.dict_str_to_str, &bav_global.R.strs);

            pars->pars.size += 1;
          }
      }
/*
 * Some already created symbols might fit a range indexed string (case
 *      of varmax / varmin variables). Fix their index_in_pars field.
 */
  for (i = 0; i < bav_global.R.syms.size; i++)
    {
      struct bav_symbol *y = bav_global.R.syms.tab[i];

      if (y->index_in_rigs != BA0_NOT_AN_INDEX)
        {
          if (y->type != bav_dependent_symbol)
            BA0_RAISE_EXCEPTION (BA0_ERRALG);
          string = bav_global.R.rigs.tab[y->index_in_rigs]->strs.tab[0];
          j = ba0_get_dictionary_string (&pars->dict, (struct ba0_table *)
              &pars->pars, string);
          if (j != BA0_NOT_AN_INDEX)
            {
              struct ba0_range_indexed_group *rig;
              rig = &pars->pars.tab[j]->rig;
/*
 * The radical of y is the one of a parameter. 
 * We still need to check that the indices fit
 */
              if (ba0_fit_indices_range_indexed_group (rig, &y->subscripts))
                y->index_in_pars = j;
            }
        }
    }

  ba0_restore (&M);
  ba0_pull_stack ();
}
