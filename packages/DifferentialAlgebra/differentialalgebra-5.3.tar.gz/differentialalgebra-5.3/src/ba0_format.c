#include "ba0_exception.h"
#include "ba0_stack.h"
#include "ba0_format.h"
#include "ba0_global.h"

#define BA0_SUBFORMAT_REALLOC_VALUE	512

/*
 * texinfo: ba0_initialize_format
 * Initialize the table of the atomic formats and the H-table of formats.
 */

BA0_DLL void
ba0_initialize_format (
    void)
{
  ba0_int_p i;

  ba0_push_stack (&ba0_global.stack.format);

  ba0_init_table ((struct ba0_table *) &ba0_global.format.leaf_subformat);
  ba0_realloc_table
      ((struct ba0_table *) &ba0_global.format.leaf_subformat,
      BA0_SUBFORMAT_REALLOC_VALUE);

  ba0_init_table ((struct ba0_table *) &ba0_global.format.htable);
  ba0_realloc_table ((struct ba0_table *) &ba0_global.format.htable,
      BA0_SIZE_HTABLE_FORMAT);
  ba0_global.format.htable.size = ba0_global.format.htable.alloc;
  for (i = 0; i < ba0_global.format.htable.size; i++)
    ba0_global.format.htable.tab[i] = (struct ba0_pair *) 0;
  ba0_global.format.nbelem_htable = 0;

  ba0_pull_stack ();

  ba0_global.format.scanf_value_var = (ba0_scanf_function *) 0;
  ba0_global.format.printf_value_var = (ba0_printf_function *) 0;
}

static ba0_int_p
ba0_not_yet_implemented (
    void *objet,
    enum ba0_garbage_code code)
{
  objet = (void *) 0;
  code = ba0_isolated;

  BA0_RAISE_EXCEPTION (BA0_ERRNYP);
  return 0;                     /* to avoid an annoying warning */
}

BA0_DLL ba0_int_p
ba0_empty_garbage1 (
    void *objet,
    enum ba0_garbage_code code)
{
  objet = (void *) 0;
  code = ba0_isolated;

  return 0;                     /* to avoid an annoying warning */
}

BA0_DLL void *
ba0_empty_garbage2 (
    void *objet,
    enum ba0_garbage_code code)
{
  code = ba0_isolated;

  return objet;
}

static void *
identity (
    void *objet)
{
  return objet;
}

/*
 * texinfo: ba0_define_format
 * 
 * Create a new atomic format, identified by the special character @code{%}
 * followed by the string @var{id}. The five other parameters are pointers
 * to functions which permit to perform input, output, garbage collection
 * and copy.
 * 
 * Some pointers may be zero. In this case, the function is taken to
 * be the empty function. Some pointers may be minus one. In this case, 
 * the function raises the @code{BA0_ERRNYP} exception (not yet implemented)
 * when called.
 * 
 * Some exceptions may be raised: @code{BA0_ERRSYN} (syntax error), 
 * @code{BA0_ERRALG} (runtime error, in the case of a twice defined format).
 */

BA0_DLL void
ba0_define_format (
    char *id,
    ba0_scanf_function *s,
    ba0_printf_function *p,
    ba0_garbage1_function *g1,
    ba0_garbage2_function *g2,
    ba0_copy_function *c)
{
  ba0_define_format_with_sizelt (id, -1, s, p, g1, g2, c);
}

/*
 * texinfo: ba0_define_format_with_sizelt
 * 
 * Variant of the above function in the case the object identified by the
 * format is a pointer to some data structure. 
 * The parameter @var{sizelt} may then be @math{-1} or the size of the data 
 * structure the pointer points to. In the first case, arrays of data
 * structures are forbidden. In the second case, they are allowed.
 * 
 * The previous function is a particular case of this one 
 * with @math{sizelt = -1}.
 */

BA0_DLL void
ba0_define_format_with_sizelt (
    char *id,
    ba0_int_p sizelt,
    ba0_scanf_function *s,
    ba0_printf_function *p,
    ba0_garbage1_function *g1,
    ba0_garbage2_function *g2,
    ba0_copy_function *c)
{
  struct ba0_pair *pair;
  struct ba0_subformat *sf;
  ba0_int_p i;

  for (i = 0; i < ba0_global.format.leaf_subformat.size; i++)
    if (strcmp (id,
            ba0_global.format.leaf_subformat.tab[i]->identificateur) == 0)
      BA0_RAISE_EXCEPTION (BA0_ERRALG);

  ba0_push_stack (&ba0_global.stack.format);

  if (ba0_global.format.leaf_subformat.size ==
      ba0_global.format.leaf_subformat.alloc)
    ba0_realloc_table ((struct ba0_table *) &ba0_global.format.leaf_subformat,
        ba0_global.format.leaf_subformat.alloc + BA0_SUBFORMAT_REALLOC_VALUE);

  pair = (struct ba0_pair *) ba0_alloc (sizeof (struct ba0_pair));
  pair->identificateur = id;
  pair->value = sf =
      (struct ba0_subformat *) ba0_alloc (sizeof (struct ba0_subformat));

  sf->code = ba0_leaf_format;
  sf->u.leaf.sizelt = sizelt;

  if (s == (ba0_scanf_function *) - 1)
    sf->u.leaf.scanf = (ba0_scanf_function *) & ba0_not_yet_implemented;
  else
    sf->u.leaf.scanf = s;

  if (p == (ba0_printf_function *) - 1)
    sf->u.leaf.printf = (ba0_printf_function *) & ba0_not_yet_implemented;
  else
    sf->u.leaf.printf = p;

  if (g1 == (ba0_garbage1_function *) - 1)
    sf->u.leaf.garbage1 = (ba0_garbage1_function *) & ba0_not_yet_implemented;
  else if (g1 == (ba0_garbage1_function *) 0)
    sf->u.leaf.garbage1 = &ba0_empty_garbage1;
  else
    sf->u.leaf.garbage1 = g1;

  if (g2 == (ba0_garbage2_function *) - 1)
    sf->u.leaf.garbage2 = (ba0_garbage2_function *) & ba0_not_yet_implemented;
  else if (g2 == (ba0_garbage2_function *) 0)
    sf->u.leaf.garbage2 = &ba0_empty_garbage2;
  else
    sf->u.leaf.garbage2 = g2;

  if (c == (ba0_copy_function *) - 1)
    sf->u.leaf.copy = (ba0_copy_function *) & ba0_not_yet_implemented;
  else if (c == (ba0_copy_function *) 0)
    sf->u.leaf.copy = &identity;
  else
    sf->u.leaf.copy = c;

  ba0_global.format.leaf_subformat.tab[ba0_global.format.leaf_subformat.
      size++] = pair;

  ba0_pull_stack ();
}

/*****************************************************************************
 CONVERSION STRING -> FORMAT
 *****************************************************************************/

static bool
is_open (
    char c)
{
  return c == '(' || c == '[' || c == '{' || c == '<';
}

static bool
is_close (
    char c)
{
  return c == ')' || c == ']' || c == '}' || c == '>';
}

static char
matching_char (
    char c)
{
  switch (c)
    {
    case '(':
      return ')';
    case '[':
      return ']';
    case '{':
      return '}';
    case '<':
      return '>';
    default:
      return '\0';
    }
}

/* 
 * Extract the identifier which follows the next '%' in s, after index *index.
 * After the call, *index points to the last char of the identifier.
 *                 code contains the identifier
 */

static void
get_code (
    char *code,
    ba0_int_p buflen,
    char *s,
    ba0_int_p *index)
{
  ba0_int_p i, j;

  j = *index;
  if (s[j] == '%')
    j++;
  i = 0;
  while (i < buflen - 2 && (isalnum ((int) s[j]) || s[j] == '_'))
    code[i++] = s[j++];
  code[i] = '\0';
  *index = j - 1;
}

/* 
 * Extracts the next opening parenthesis in s, after index *index
 * After the call, *index points to this parenthesis.
 * A backslash backslashes the meaning of the parenthesis.
 */

static char
get_opening (
    char *s,
    ba0_int_p *index)
{
  bool backslash;
  ba0_int_p i;

  backslash = false;
  i = *index;
  while (s[i] && (backslash || !is_open (s[i])))
    {
      backslash = s[i] == '\\';
      i += 1;
    }
  if (s[i] == '\0')
    BA0_RAISE_EXCEPTION (BA0_ERRSYN);
  *index = i;
  return s[i];
}

/* 
 * Analyzes s and computes the length of the text field,
 * as well as the number of subformats. 
 * The stack (pile) contains '%' and opening parentheses.
 * number_of_ditto gives the number of '%' in pile.
 * The only stacked '%' are those which correspond to sub-ojects (%t, %l).
 * We are at top_level if number_of_ditto is zero.
 * All opening parentheses are stacked.
 * In the case of a string starting by an opening parenthesis, this one
 * is not taken into account.
 */

#define PILELEN 16              /* max number of imbricated %[...] */
#define CODELEN 64              /* max length of %something */

static void
first_analysis (
    ba0_int_p *stringlength,
    ba0_int_p *linknumber,
    char *s,
    ba0_int_p index)
{
  char pile[PILELEN], code[CODELEN];
  char chrin;
  ba0_int_p number_of_ditto = 0;
  ba0_int_p sp = -1;
  bool backslash;

  chrin = s[index];
  backslash = false;

  *stringlength = 0;
  *linknumber = 0;

  if (chrin == '\0')
    BA0_RAISE_EXCEPTION (BA0_ERRSYN);

  for (;;)
    {

/*
 * If chrin is a closing parenthesis, the opening one is pulled.
 * If the former stacked char is a '%', it is pulled and number_of_ditto
 * is decremented.
 * *stringlenth is never incremented.
 */
      if (chrin == '\0')
        {
          if (sp < 0)
            break;
          BA0_RAISE_EXCEPTION (BA0_ERRSYN);
        }
      else if (!backslash && is_close (chrin))
        {
          if (sp < 0)
            break;
          if (chrin != matching_char (pile[sp]))
            BA0_RAISE_EXCEPTION (BA0_ERRSYN);
          sp--;
          if (sp >= 0 && pile[sp] == '%')
            {
              sp--;
              number_of_ditto--;
            }
        }
      else if (!backslash && chrin == '%')
        {
/*
 * A '%' accounts for one char since the possible opening and closing
 * parentheses which come with it are stored outside text.
 *
 * *linknumber is incremented if we are at the top level.
 *
 * If the code is l or t, a '%' and the opening parenthesis are stacked
 * and number_of_ditto is incremented.
 */
          if (number_of_ditto == 0)
            {
              (*stringlength)++;
              (*linknumber)++;
            }
          get_code (code, CODELEN, s, &index);
          if (strcmp (code, "t") == 0 || strcmp (code, "l") == 0
              || strcmp (code, "m") == 0 || strcmp (code, "a") == 0
              || strcmp (code, "value") == 0 || strcmp (code, "point") == 0)
            {
              pile[++sp] = '%';
              pile[++sp] = get_opening (s, &index);
              number_of_ditto++;
            }
        }
      else if (!backslash && is_open (chrin))
        {
/*
 * chrin is an opening parenthesis which does not come with any '%'.
 * It is stacked. If number_of_ditto = 0, one counts also the 
 * matching closing parenthesis.
 */
          pile[++sp] = chrin;
          if (number_of_ditto == 0)
            *stringlength += 2;
        }
      else if (number_of_ditto == 0)

/* 
 * A tacky character is counted iff number_of_ditto = 0.
 */

        (*stringlength)++;
      backslash = chrin == '\\';
      chrin = s[++index];
    }
}

/*
 * The ba0_index variables points to the first character to analyze.
 * After the call, it points to the last analyzed one.
 *
 * The niveau variable provides the number of met opening parentheses.
 * One stops if niveau reaches -1.
 * It is pointless to do things more carefully.
 *
 * No need to use a stack because of recursive calls.
 */

static struct ba0_format *
_formate (
    char *s,
    ba0_int_p *index)
{
  ba0_int_p textlen, linknmb;
  ba0_int_p itext, ilink;
  struct ba0_format *f;
  ba0_int_p niveau;
  char chrin;
  bool backslash;

  first_analysis (&textlen, &linknmb, s, *index);

  f = (struct ba0_format *) ba0_alloc (sizeof (struct ba0_format));
  f->text = (char *) ba0_alloc (textlen + 1);
  f->link =
      (struct ba0_subformat * *) ba0_alloc (sizeof (struct ba0_subformat *) *
      linknmb);
  f->linknmb = linknmb;
  itext = 0;
  ilink = 0;

  niveau = 0;
  chrin = s[*index];
  backslash = false;
  for (;;)
    {
      if (!backslash && is_open (chrin))
        niveau++;
      else if (chrin == '\0' || (!backslash && is_close (chrin)))
        {
          if (--niveau < 0)
            break;
        }
      else if (!backslash && chrin == '%')
        {
          bool predefined;
          char code[CODELEN];
          enum ba0_typeof_format c;

          get_code (code, CODELEN, s, index);
          if (strcmp (code, "t") == 0)
            {
              c = ba0_table_format;
              predefined = true;
            }
          else if (strcmp (code, "a") == 0)
            {
              c = ba0_array_format;
              predefined = true;
            }
          else if (strcmp (code, "l") == 0)
            {
              c = ba0_list_format;
              predefined = true;
            }
          else if (strcmp (code, "m") == 0)
            {
              c = ba0_matrix_format;
              predefined = true;
            }
          else if (strcmp (code, "value") == 0)
            {
              c = ba0_value_format;
              predefined = true;
            }
          else if (strcmp (code, "point") == 0)
            {
              c = ba0_point_format;
              predefined = true;
            }
          else
            predefined = false;
          if (predefined)
            {
              struct ba0_subformat *l =
                  (struct ba0_subformat *) ba0_alloc (sizeof (struct
                      ba0_subformat));
              f->link[ilink++] = l;
              l->u.node.po = get_opening (s, index);
              l->u.node.pf = matching_char (l->u.node.po);
              (*index)++;
              l->u.node.op = _formate (s, index);
              l->code = c;
              if (l->u.node.op->linknmb != 1)
                BA0_RAISE_EXCEPTION (BA0_ERRSYN);
              if (c == ba0_array_format &&
                  l->u.node.op->link[0]->u.leaf.sizelt < 0)
                BA0_RAISE_EXCEPTION (BA0_ERRSYN);
            }
          else
            {
              ba0_int_p i;
              bool found = false;
              struct ba0_pair *pair;

              for (i = 0; i < ba0_global.format.leaf_subformat.size && !found;
                  i++)
                {
                  pair = ba0_global.format.leaf_subformat.tab[i];
                  if (strcmp (pair->identificateur, code) == 0)
                    {
                      f->link[ilink++] = (struct ba0_subformat *) pair->value;
                      found = true;
                    }
                }
              if (!found)
                BA0_RAISE_EXCEPTION (BA0_ERRSYN);
            }
        }
      f->text[itext++] = chrin;
      backslash = chrin == '\\';
      chrin = s[++(*index)];
    }
  f->text[itext] = '\0';
  return f;
}

/**********************************************************************
 HASH-TABLE MANAGEMENT
 **********************************************************************/

static ba0_int_p
primary_key (
    char *s)
{
  unsigned ba0_int_p t;

  t = (unsigned ba0_int_p) (void *) s;
  t /= BA0_ALIGN;
  t %= ba0_global.format.htable.size;
  return (ba0_int_p) t;
}

static ba0_int_p
secondary_key (
    char *s)
{
  unsigned ba0_int_p t;

  t = (unsigned ba0_int_p) (void *) s;
  t ^= -1;
  t /= BA0_ALIGN;
  t %= ba0_global.format.htable.size;
  if (t == 0)
    t = 1;                      /* to avoid infinite loops */
  return (ba0_int_p) t;
}

/*
 * texinfo: ba0_get_format
 * Transform the string @var{s} to a format and return it. 
 * There are restrictions on the strings. 
 * In particular, parentheses must be paired. 
 * The format corresponding to a given string is only computed once. 
 * Exception @code{BA0_ERROOM} is raised if the H-table is full.
 */

BA0_DLL struct ba0_format *
ba0_get_format (
    char *s)
{
  ba0_int_p i, j, index;
  struct ba0_pair *pair;

  i = primary_key (s);
  j = secondary_key (s);
  pair = ba0_global.format.htable.tab[i];
  while (pair != (struct ba0_pair *) 0 && pair->identificateur != s)
    {
      i = (i + j) % ba0_global.format.htable.size;
      pair = ba0_global.format.htable.tab[i];
    }

  if (pair == (struct ba0_pair *) 0)
    {
      if (++ba0_global.format.nbelem_htable > ba0_global.format.htable.size / 3)
        BA0_RAISE_EXCEPTION (BA0_ERROOM);
      ba0_push_stack (&ba0_global.stack.format);
      pair = (struct ba0_pair *) ba0_alloc (sizeof (struct ba0_pair));
      ba0_global.format.htable.tab[i] = pair;
      pair->identificateur = s;
      index = 0;
      pair->value = _formate (s, &index);
      ba0_pull_stack ();
    }

  return (struct ba0_format *) pair->value;
}
