#if !defined (BA0_ANALEX_H)
#   define BA0_ANALEX_H 1

/* 
 * Lexical analyzer.
 */

#   include "ba0_common.h"
#   include "ba0_string.h"
#   include "ba0_dictionary_string.h"

BEGIN_C_DECLS

/*
 * texinfo: ba0_typeof_token
 * This data type permits to assign a type to a token.
 */

enum ba0_typeof_token
{
// Special value
  ba0_no_token,
// The token is an integer starting with a digit (unsigned)
  ba0_integer_token,
// The token is a sign. Signs are single characters
  ba0_sign_token,
// The token is a string. 
// Any sequence of characters delimited by quotes is a string
  ba0_string_token
};

/* 
 * texinfo: ba0_token
 * This data type permits to store one token.
 */

struct ba0_token
{
// The type of the token
  enum ba0_typeof_token type;
// At least one space was present before the first token character
  bool spaces_before;
// The value of the token, stored in the analex stack.
  char *value;
};

/* 
 * texinfo: ba0_analex_token_fifo
 * This data type describes a FIFO of tokens implemented as a
 * circular array.
 * The only variables of this type are fields of @code{ba0_global}.
 */

struct ba0_analex_token_fifo
{
// The array of token containing the FIFO.
// Its length is stored in ba0_initialized_global.analex.nb_tokens
  struct ba0_token *fifo;
// The index of the first token in the FIFO i.e the current token
  ba0_int_p first;
// The index of the last token present in the FIFO
// It is usually equal to first unless a token has been "ungot"
  ba0_int_p last;
// The number of calls to ba0_get_token_analex since the last reset
  ba0_int_p counter;
};

/* 
 * The default max length of the FIFO
 * The characters that can be used for quoting
 */

#   define BA0_NBTOKENS    20
#   define BA0_QUOTES      "'\""

/* 
 * The length of the error context string (see ba0_global)
 */

#   define BA0_CONTEXT_LMAX 60

/*
 * The size of the substitution dictionary stack (see ba0_global)
 */

#   define BA0_SIZE_SUBS_DICT_STACK 4

extern BA0_DLL void ba0_set_settings_analex (
    ba0_int_p,
    char *);

extern BA0_DLL void ba0_get_settings_analex (
    ba0_int_p *,
    char **);

extern BA0_DLL char *ba0_get_context_analex (
    void);

extern BA0_DLL void ba0_write_context_analex (
    void);

extern BA0_DLL void ba0_init_analex (
    void);

extern BA0_DLL void ba0_clear_analex (
    void);

extern BA0_DLL void ba0_reset_analex (
    void);

extern BA0_DLL void ba0_record_analex (
    void);

extern BA0_DLL void ba0_restore_analex (
    void);

extern BA0_DLL void ba0_reset_subs_dict_analex (
    void);

extern BA0_DLL void ba0_push_subs_dict_analex (
    struct ba0_dictionary_string *,
    struct ba0_tableof_string *,
    struct ba0_tableof_string *);

extern BA0_DLL void ba0_pull_subs_dict_analex (
    void);

extern BA0_DLL void ba0_set_analex_FILE (
    FILE *);

extern BA0_DLL void ba0_set_analex_string (
    char *);

extern BA0_DLL ba0_int_p ba0_get_counter_analex (
    void);

extern BA0_DLL void ba0_get_token_analex (
    void);

extern BA0_DLL void ba0_unget_token_analex (
    ba0_int_p);

extern BA0_DLL void ba0_unget_given_token_analex (
    char *,
    enum ba0_typeof_token,
    bool);

extern BA0_DLL bool ba0_sign_token_analex (
    char *);

extern BA0_DLL bool ba0_spaces_before_token_analex (
    void);

extern BA0_DLL enum ba0_typeof_token ba0_type_token_analex (
    void);

extern BA0_DLL char *ba0_value_token_analex (
    void);

END_C_DECLS
#endif /* !BA0_ANALEX_H */
