#include "ba0_exception.h"
#include "ba0_stack.h"
#include "ba0_string.h"
#include "ba0_basic_io.h"
#include "ba0_analex.h"
#include "ba0_garbage.h"
#include "ba0_gmp.h"
#include "ba0_scanf.h"
#include "ba0_printf.h"

/*
 * texinfo: ba0_not_a_string
 * Return @code{(char*)0}.
 */

BA0_DLL char *
ba0_not_a_string (
    void)
{
  return (char *) 0;
}

/*
 * texinfo: ba0_new_string
 * Return the empty string allocated in the current stack 
 * (not the @code{(char*)0} pointer, which is not a string).
 */

BA0_DLL char *
ba0_new_string (
    void)
{
  return ba0_strdup ("");
}

/*
 * texinfo: ba0_strdup
 * Return a copy of @var{s} in an area dynamically allocated in
 * the current stack.
 */

BA0_DLL char *
ba0_strdup (
    char *s)
{
  char *t;

  t = (char *) ba0_alloc (strlen (s) + 1);
  strcpy (t, s);
  return t;
}

/*
 * texinfo: ba0_strcat
 * Concatenate all the strings of @var{T} in a single, allocated, string
 * and return it.
 */

BA0_DLL char *
ba0_strcat (
    struct ba0_tableof_string *T)
{
  char *p, *q, *r;
  ba0_int_p l, i;

  l = 0;
  for (i = 0; i < T->size; i++)
    l += strlen (T->tab[i]);
  p = (char *) ba0_alloc (l + 1);
  q = p;
  for (i = 0; i < T->size; i++)
    {
      r = T->tab[i];
      while (*r)
        *q++ = *r++;
    }
  *q = '\0';
  return p;
}

/*
   Directly picked from the glibc since strcasecmp is actually not defined
   in the ANSI norm. Hence a bug on some architectures with the -ansi flag.
*/

/*
 * texinfo: ba0_strcasecmp
 * See the documentation of @code{strcasecmp} which is not always
 * available, depending on compiler options.
 */

BA0_DLL int
ba0_strcasecmp (
    char *s1,
    char *s2)
{
  const unsigned char *p1 = (const unsigned char *) s1;
  const unsigned char *p2 = (const unsigned char *) s2;
  int result;

  if (p1 == p2)
    return 0;

  while ((result = tolower (*p1) - tolower (*p2++)) == 0)
    if (*p1++ == '\0')
      break;

  return result;
}

/*
 * texinfo: ba0_strncasecmp
 * See the documentation of @code{strncasecmp} which is not always
 * available, depending on compiler options.
 */

BA0_DLL int
ba0_strncasecmp (
    char *s1,
    char *s2,
    size_t n)
{
  const unsigned char *p1 = (const unsigned char *) s1;
  const unsigned char *p2 = (const unsigned char *) s2;
  unsigned int i;
  int result = 0;

  if (p1 == p2)
    return 0;

  i = 0;
  while (i < n && (result = tolower (*p1) - tolower (*p2++)) == 0)
    {
      if (*p1++ == '\0')
        break;
      i++;
    }

  return result;
}

/*
 * texinfo: ba0_scanf_string
 * General parsing function for strings.
 * It can be called by @code{ba0_scanf/%s}.
 * It actually returns a copy (allocated by @code{ba0_alloc})
 * of the current token (see the lexical analyzer).
 */

BA0_DLL void *
ba0_scanf_string (
    void *z)
{
  char *s;

  if (z == (void *) 0)
    s = (char *) ba0_alloc (strlen (ba0_value_token_analex ()) + 1);
  else
    s = (char *) z;

  strcpy (s, ba0_value_token_analex ());
  return s;
}

/*
 * texinfo: ba0_printf_string
 * General printing function for strings.
 * It can be called using @code{ba0_printf/%s}.
 */

BA0_DLL void
ba0_printf_string (
    void *str)
{
  ba0_put_string ((char *) str);
}

/*
 * Readonly static data
 */

static char _string[] = "string";

BA0_DLL ba0_int_p
ba0_garbage1_string (
    void *str,
    enum ba0_garbage_code code)
{
  char *s = (char *) str;

  if (code == ba0_isolated)
    return ba0_new_gc_info (s, ba0_ceil_align (strlen (s) + 1), _string);
  else
    return 0;
}

BA0_DLL void *
ba0_garbage2_string (
    void *str,
    enum ba0_garbage_code code)
{
  if (code == ba0_isolated)
    return ba0_new_addr_gc_info (str, _string);
  else
    return str;
}

BA0_DLL void *
ba0_copy_string (
    void *str)
{
  char *s;

  s = (char *) ba0_alloc (strlen ((char *) str) + 1);
  strcpy (s, (char *) str);
  return s;
}

/*
 * texinfo: ba0_set_tableof_string
 * Assigns @var{src} to @var{dst}.
 * Strings are duplicated.
 */

BA0_DLL void
ba0_set_tableof_string (
    struct ba0_tableof_string *dst,
    struct ba0_tableof_string *src)
{
  ba0_int_p i;

  ba0_reset_table ((struct ba0_table *) dst);
  ba0_realloc_table ((struct ba0_table *) dst, src->size);
  for (i = 0; i < src->size; i++)
    dst->tab[i] = ba0_strdup (src->tab[i]);
  dst->size = src->size;
}

/*
 * texinfo: ba0_sizeof_tableof_string
 * Return the size needed to perform a copy of @var{T}, including
 * the strings themselves.
 * If @var{code} is @code{ba0_embedded} then @var{T} is supposed
 * to be embedded in a larger data structure so that its size is
 * not taken into account.
 */

BA0_DLL unsigned ba0_int_p
ba0_sizeof_tableof_string (
    struct ba0_tableof_string *T,
    enum ba0_garbage_code code)
{
  unsigned ba0_int_p size;
  ba0_int_p i;

  size = ba0_sizeof_table ((struct ba0_table *) T, code);
  for (i = 0; i < T->size; i++)
    size += ba0_allocated_size (strlen (T->tab[i]) + 1);
  return size;
}

/*
 * texinfo: ba0_member2_tableof_string
 * Return @code{true} if @var{string} belongs to @var{T},
 * else @code{false}. Comparisons are performed using @code{strcmp}.
 * If @var{index} is nonzero and @var{string} is found then
 * the index of @var{string} in @var{T} is assigned to *@var{index}.
 */

BA0_DLL bool
ba0_member2_tableof_string (
    char *string,
    struct ba0_tableof_string *T,
    ba0_int_p *index)
{
  bool found;
  ba0_int_p i;

  found = false;
  i = 0;
  while (i < T->size && !found)
    {
      if (strcmp (string, T->tab[i]) == 0)
        {
          found = true;
          if (index)
            *index = i;
        }
      else
        i += 1;
    }
  return found;
}
