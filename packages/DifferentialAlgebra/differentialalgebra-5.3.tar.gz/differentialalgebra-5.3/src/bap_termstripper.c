#include "bap_termstripper.h"

/*
 * texinfo: bap_init_set_termstripper
 * Initialize @var{s} with @var{v} and @var{r}.
 */

BAP_DLL void
bap_init_set_termstripper (
    struct bap_termstripper *s,
    struct bav_variable *v,
    bav_Iordering r)
{
  memset (s, 0, sizeof (struct bap_termstripper));
  s->size = 1;
  s->tab[0].varmax = v;
  s->tab[0].ordering = r;
}

/*
 * texinfo: bap_set_termstripper
 * Assign @var{src} to @var{dst}.
 */

BAP_DLL void
bap_set_termstripper (
    struct bap_termstripper *dst,
    struct bap_termstripper *src)
{
  *dst = *src;
}

static bav_Iordering
bap_ordering_termstripper (
    struct bap_termstripper *s)
{
  return s->tab[s->size - 1].ordering;
}

/*
 * texinfo: bap_change_ordering_termstripper
 * Assign @var{r} to the ordering of the last recorded stripping operation.
 */

BAP_DLL void
bap_change_ordering_termstripper (
    struct bap_termstripper *s,
    bav_Iordering r)
{
  s->tab[s->size - 1].ordering = r;
}

/*
 * texinfo: bap_change_ordering_termstripper
 * Assign @var{v} to the variable of the last recorded stripping operation.
 */

BAP_DLL void
bap_change_variable_termstripper (
    struct bap_termstripper *s,
    struct bav_variable *v)
{
  s->tab[s->size - 1].varmax = v;
}

/*
 * texinfo: bap_append_termstripper
 * Record the new stripping operation defined by @var{r} and @var{v}.
 */

BAP_DLL void
bap_append_termstripper (
    struct bap_termstripper *s,
    struct bav_variable *v,
    bav_Iordering r)
{
  if (bap_ordering_termstripper (s) == r)
    {
      bap_change_variable_termstripper (s, v);
    }
  else
    {
      if (s->size == BAP_TERMSTRIPPER_SIZE)
        BA0_RAISE_EXCEPTION (BA0_ERRALG);
      s->tab[s->size].varmax = v;
      s->tab[s->size].ordering = r;
      s->size += 1;
    }
}

/*
 * texinfo: bap_strip_term_termstripper
 * Apply the stripping operations defined by @var{s} to the term @var{T}.
 * The result is in @var{T} and is sorted according to the ordering @var{r}.
 */

BAP_DLL void
bap_strip_term_termstripper (
    struct bav_term *T,
    bav_Iordering r,
    struct bap_termstripper *s)
{
  ba0_int_p i, j, n;
  bav_Iordering rr;
  bav_Inumber nx;

  for (n = 0; n < s->size; n++)
    {
      if (s->tab[n].varmax == BAV_NOT_A_VARIABLE)
        {
          bav_set_term_one (T);
          return;
        }
      else if (s->tab[n].varmax != (struct bav_variable *) -1)
        {
          rr = s->tab[n].ordering;
          nx = s->tab[n].varmax->number.tab[rr];
          for (i = j = 0; j < T->size; j++)
            if (T->rg[j].var->number.tab[rr] <= nx)
              T->rg[i++] = T->rg[j];
          T->size = i;
        }
    }
  rr = bap_ordering_termstripper (s);
  if (rr != r)
    {
      bav_push_ordering (rr);
      bav_sort_term (T);
      bav_pull_ordering ();
    }
}

/*
 * texinfo: bap_identity_termstripper
 * Return @code{true} if the stripping operations defined by @var{s}
 * are the identity.
 */

BAP_DLL bool
bap_identity_termstripper (
    struct bap_termstripper *s,
    bav_Iordering r)
{
  ba0_int_p i;

  if (r != bap_ordering_termstripper (s))
    return false;
  for (i = 0; i < s->size; i++)
    if (s->tab[i].varmax != (struct bav_variable *) -1)
      return false;
  return true;
}

/*
 * texinfo: bap_switch_ring_termstripper
 * Apply @code{bav_switch_ring_variable} to all variables in @var{s}.
 */

BAP_DLL void
bap_switch_ring_termstripper (
    struct bap_termstripper *s,
    struct bav_differential_ring *R)
{
  ba0_int_p i;

  for (i = 0; i < s->size; i++)
    if (s->tab[i].varmax != (struct bav_variable *) -1)
      s->tab[i].varmax = bav_switch_ring_variable (s->tab[i].varmax, R);
}
