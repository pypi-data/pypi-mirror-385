#include "bai_odex.h"
#include "bai_global.h"

/*
 * texinfo: bai_init_odex_system
 * Initialize @var{S}.
 */

BAI_DLL void
bai_init_odex_system (
    struct bai_odex_system *S)
{
  S->t = BAV_NOT_A_VARIABLE;
  ba0_init_table ((struct ba0_table *) &S->lhs);
  ba0_init_table ((struct ba0_table *) &S->rhs);
  ba0_init_table ((struct ba0_table *) &S->params);
  ba0_init_table ((struct ba0_table *) &S->commands);
}

/*
 * texinfo: bai_reset_odex_system
 * Reset to zero the sizes of all fields of @var{S}.
 */

BAI_DLL void
bai_reset_odex_system (
    struct bai_odex_system *S)
{
  S->t = BAV_NOT_A_VARIABLE;
  ba0_reset_table ((struct ba0_table *) &S->lhs);
  ba0_reset_table ((struct ba0_table *) &S->rhs);
  ba0_reset_table ((struct ba0_table *) &S->params);
  ba0_reset_table ((struct ba0_table *) &S->commands);
}

/*
 * texinfo: bai_new_odex_system
 * Allocate a new differential system, initialize it and return it.
 */

BAI_DLL struct bai_odex_system *
bai_new_odex_system (
    void)
{
  struct bai_odex_system *S;

  S = (struct bai_odex_system *) ba0_alloc (sizeof (struct bai_odex_system));
  bai_init_odex_system (S);
  return S;
}

/*
 * texinfo: bai_set_odex_system
 * Assign @var{src} to @var{dst}.
 */

BAI_DLL void
bai_set_odex_system (
    struct bai_odex_system *dst,
    struct bai_odex_system *src)
{
  ba0_int_p i;

  if (dst != src)
    {
      dst->t = src->t;
      ba0_set_table ((struct ba0_table *) &dst->lhs,
          (struct ba0_table *) &src->lhs);
      dst->rhs.size = 0;
      ba0_realloc2_table ((struct ba0_table *) &dst->rhs, src->rhs.size,
          (ba0_new_function *) & baz_new_ratfrac);
      for (i = 0; i < src->rhs.size; i++)
        {
          baz_set_ratfrac (dst->rhs.tab[dst->rhs.size++], src->rhs.tab[i]);
        }
      ba0_set_table ((struct ba0_table *) &dst->params,
          (struct ba0_table *) &src->params);
      ba0_set_table ((struct ba0_table *) &dst->commands,
          (struct ba0_table *) &src->commands);
    }
}

/*
 * texinfo: bai_set_odex_system_tables
 * Assign to @var{S} the ODE system defined by the other parameters.
 * The variable @var{t} must be independent.
 * The parameter @var{params} contains the system parameters.
 * The parameter @var{commands} contains the system commands.
 * The parameter @var{depvars} contains the system dependent variables (they
 * must have order zero). 
 * The parameter @var{rhs} contains the righthand sides of the system
 * differential equations. There must be one righthand side per dependent
 * variable. The righthand sides must only depend on the system parameters,
 * commands and dependent variables.
 * The function raises the exception @code{BAI_ERROXS} if the system
 * is inconsistent.
 */

BAI_DLL void
bai_set_odex_system_tables (
    struct bai_odex_system *S,
    struct bav_variable *t,
    struct bav_tableof_variable *params,
    struct bav_tableof_variable *commands,
    struct bav_tableof_variable *depvars,
    struct baz_tableof_ratfrac *rhs)
{
  struct bav_dictionary_variable dict;
  struct bav_tableof_variable vars;
  struct ba0_mark M;
  ba0_int_p i;

  if (bav_symbol_type_variable (t) != bav_independent_symbol)
    BA0_RAISE_EXCEPTION (BAI_ERROXS);

  if (depvars->size != rhs->size)
    BA0_RAISE_EXCEPTION (BAI_ERROXS);

  if (!ba0_is_unique_table ((struct ba0_table *) params)
      || !ba0_is_unique_table ((struct ba0_table *) commands)
      || !ba0_is_unique_table ((struct ba0_table *) depvars))
    BA0_RAISE_EXCEPTION (BAI_ERROXS);
/*
 * The elements of depvars must have order zero and not belong to 
 * params or commands
 */
  for (i = 0; i < depvars->size; i++)
    {
      if (bav_total_order_variable (depvars->tab[i]) != 0)
        BA0_RAISE_EXCEPTION (BAI_ERROXS);
      if (ba0_member_table (depvars->tab[i], (struct ba0_table *) params)
          || ba0_member_table (depvars->tab[i], (struct ba0_table *) commands))
        BA0_RAISE_EXCEPTION (BAI_ERROXS);
    }
/*
 * Elements of params must be distinct from elements of commands.
 */
  for (i = 0; i < params->size; i++)
    {
      if (ba0_member_table (params->tab[i], (struct ba0_table *) commands))
        BA0_RAISE_EXCEPTION (BAI_ERROXS);
    }
/*
 * Righthand sides elements of ODE must only depend on depvars, params
 * and commands.
 */
  ba0_record (&M);

  bav_init_dictionary_variable (&dict, 1);
  ba0_init_table ((struct ba0_table *)&vars);
  ba0_realloc_table ((struct ba0_table *)&vars, 2);

//  bav_R_mark_variables (false);
  for (i = 0; i < rhs->size; i++)
    {
      bap_mark_indets_polynom_mpz (&dict, &vars, &rhs->tab[i]->numer);
      bap_mark_indets_polynom_mpz (&dict, &vars, &rhs->tab[i]->denom);
    }

//  bav_R_marked_variables (&T, true);
  for (i = 0; i < vars.size; i++)
    {
      if (!ba0_member_table (vars.tab[i], (struct ba0_table *) params)
          && !ba0_member_table (vars.tab[i], (struct ba0_table *) commands)
          && !ba0_member_table (vars.tab[i], (struct ba0_table *) depvars))
        BA0_RAISE_EXCEPTION (BAI_ERROXS);
    }

  ba0_restore (&M);
/*
 * Setting
 */
  S->t = t;
  ba0_set_table ((struct ba0_table *) &S->params, (struct ba0_table *) params);
  ba0_set_table ((struct ba0_table *) &S->commands,
      (struct ba0_table *) commands);
  ba0_set_table ((struct ba0_table *) &S->lhs, (struct ba0_table *) depvars);
/*
 * Differentiate once dependent variables for lhs
 */
  for (i = 0; i < S->lhs.size; i++)
    S->lhs.tab[i] = bav_diff_variable (S->lhs.tab[i], t->root);
  S->rhs.size = 0;
  ba0_realloc2_table ((struct ba0_table *) &S->rhs, rhs->size,
      (ba0_new_function *) & baz_new_ratfrac);
  for (i = 0; i < rhs->size; i++)
    {
      baz_set_ratfrac (S->rhs.tab[S->rhs.size], rhs->tab[i]);
      S->rhs.size += 1;
    }
}

/*
 * texinfo: bai_set_odex_system_regchain
 * Variant of @code{bai_set_odex_system_tables} 
 * where the righthand side are computed from
 * @var{C} by taking the normal forms of the first derivatives w.r.t. @code{t}
 * of the dependent variables. In addition to @code{BAI_ERROXS}, the function
 * may thus in principle raise the exceptions @code{BAD_EXRNUL} and 
 * @code{BAD_EXRDDZ}.
 */

BAI_DLL void
bai_set_odex_system_regchain (
    struct bai_odex_system *S,
    struct bav_variable *t,
    struct bav_tableof_variable *params,
    struct bav_tableof_variable *commands,
    struct bav_tableof_variable *depvars,
    struct bad_regchain *C)
{
  struct baz_tableof_ratfrac rhs;
  struct bap_polynom_mpz leader;
  struct ba0_mark M;
  ba0_int_p i;

  if (bav_symbol_type_variable (t) != bav_independent_symbol)
    BA0_RAISE_EXCEPTION (BAI_ERROXS);

  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_init_table ((struct ba0_table *) &rhs);
  ba0_realloc2_table ((struct ba0_table *) &rhs, depvars->size,
      (ba0_new_function *) & baz_new_ratfrac);
  bap_init_polynom_mpz (&leader);
  for (i = 0; i < depvars->size; i++)
    {
      if (bav_symbol_type_variable (depvars->tab[i]) != bav_dependent_symbol
          || bav_total_order_variable (depvars->tab[i]) > 0)
        BA0_RAISE_EXCEPTION (BAI_ERROXS);

      ba0_scanf_printf ("%Az", "%v[%v]", &leader, depvars->tab[i], t);

      bad_normal_form_polynom_mod_regchain (rhs.tab[rhs.size], &leader, C,
          (struct bap_polynom_mpz * *) 0);
      rhs.size += 1;
    }

  ba0_pull_stack ();
  bai_set_odex_system_tables (S, t, params, commands, depvars, &rhs);
  ba0_restore (&M);
}

/*
 * texinfo: bai_odex_is_lhs
 * Return @code{true} if  @var{v} is the order zero variable corresponding
 * to some lefthand side variable of @var{S} and @code{false} otherwise. 
 * If @code{true} and if @var{index} is nonzero then @var{index} receives the 
 * index of @var{v} in the table @code{lhs} of @var{S}.
 */

BAI_DLL bool
bai_odex_is_lhs (
    struct bav_variable *v,
    struct bai_odex_system *S,
    ba0_int_p *index)
{
  ba0_int_p i;

  for (i = 0; i < S->lhs.size; i++)
    if (S->lhs.tab[i] != BAV_NOT_A_VARIABLE
        && v == bav_order_zero_variable (S->lhs.tab[i]))
      {
        if (index)
          *index = i;
        return true;
      }
  return false;
}

/*
 * texinfo: bai_scanf_odex_system
 * The parsing function for explicit ODE systems.
 * It is called by @code{ba0_scanf/%odex}.
 * The expected format is 
 * @code{odex (indep = %v, params = %t[%v], commands = %t[%v], eqns = [%v = %Qz])}.
 */

BAI_DLL void *
bai_scanf_odex_system (
    void *S0)
{
  struct bai_odex_system *S = (struct bai_odex_system *) S0;
  struct baz_tableof_ratfrac Trhs;
  struct bav_tableof_variable Tdepvars, Tparams, Tcommands;
  struct bav_variable *t, *v;
  struct ba0_mark M;
  ba0_int_p i;
  bool indep, params, commands, eqns;
  char buffer[64];

  if (S == (struct bai_odex_system *) 0)
    S = bai_new_odex_system ();
/*
 * odex (indep = %v, params = %t[%v], commands = %t[%v], eqns = %t[%v = %Qz])
 * - some fields may be omitted
 * - the fields may occur in any order
 * - the independent variable may be omitted if clear from the context
 */
  ba0_push_another_stack ();
  ba0_record (&M);

  ba0_init_table ((struct ba0_table *) &Tparams);
  ba0_init_table ((struct ba0_table *) &Tcommands);
  ba0_init_table ((struct ba0_table *) &Tdepvars);
  ba0_init_table ((struct ba0_table *) &Trhs);

  if (ba0_type_token_analex () != ba0_string_token
      || strcmp (ba0_value_token_analex (), "odex") != 0)
    BA0_RAISE_EXCEPTION (BA0_ERRSYN);

  ba0_get_token_analex ();
  if (!ba0_sign_token_analex ("("))
    BA0_RAISE_EXCEPTION (BA0_ERRSYN);

  indep = false;
  params = false;
  commands = false;
  eqns = false;

  ba0_get_token_analex ();
  for (;;)
    {
      ba0_scanf ("%s = ", buffer);
      if (strcmp (buffer, "indep") == 0 && !indep)
        {
          ba0_get_token_analex ();
          ba0_scanf ("%v", &t);
          indep = true;
        }
      else if (strcmp (buffer, "params") == 0 && !params)
        {
          ba0_get_token_analex ();
          ba0_scanf ("%t[%v]", &Tparams);
          params = true;
        }
      else if (strcmp (buffer, "commands") == 0 && !commands)
        {
          ba0_get_token_analex ();
          ba0_scanf ("%t[%v]", &Tcommands);
          commands = true;
        }
      else if (strcmp (buffer, "eqns") == 0 && !eqns)
        {
          ba0_get_token_analex ();
          if (!ba0_sign_token_analex ("["))
            BA0_RAISE_EXCEPTION (BA0_ERRSYN);

          ba0_get_token_analex ();
          for (;;)
            {
              if (Tdepvars.size == Tdepvars.alloc)
                ba0_realloc_table ((struct ba0_table *) &Tdepvars,
                    2 * Tdepvars.size + 1);
              if (Trhs.size == Trhs.alloc)
                ba0_realloc2_table ((struct ba0_table *) &Trhs,
                    2 * Trhs.size + 1, (ba0_new_function *) & baz_new_ratfrac);
/*
 * Temporarily, the Tdepvars elements are not forced to order zero.
 */
              ba0_scanf ("%v = %Qz", &Tdepvars.tab[Tdepvars.size],
                  Trhs.tab[Trhs.size]);
              Tdepvars.size += 1;
              Trhs.size += 1;
              ba0_get_token_analex ();
              if (!ba0_sign_token_analex (","))
                break;
              ba0_get_token_analex ();
            }
          if (!ba0_sign_token_analex ("]"))
            BA0_RAISE_EXCEPTION (BA0_ERRSYN);
          eqns = true;
        }
      ba0_get_token_analex ();
      if (!ba0_sign_token_analex (","))
        break;
      ba0_get_token_analex ();
    }
  if (!ba0_sign_token_analex (")"))
    BA0_RAISE_EXCEPTION (BA0_ERRSYN);
/*
 * If not given, the independent variable must be clear from the context
 */
  if (!indep)
    {
      if (bav_global.R.ders.size == 1)
        t = bav_derivation_index_to_derivation (0);
      else
        BA0_RAISE_EXCEPTION (BAI_ERROXS);
    }
/*
 * Check the depvars now (since t is known). Force order zero.
 */
  for (i = 0; i < Tdepvars.size; i++)
    {
      v = bav_order_zero_variable (Tdepvars.tab[i]);
      if (Tdepvars.tab[i] != bav_diff_variable (v, t->root))
        BA0_RAISE_EXCEPTION (BAI_ERROXS);
      Tdepvars.tab[i] = v;
    }
/*
 * The remaining consistency checking is performed by the function call below
 */
  ba0_pull_stack ();
  bai_set_odex_system_tables (S, t, &Tparams, &Tcommands, &Tdepvars, &Trhs);
  ba0_restore (&M);
  return S;
}

/*
 * texinfo: bai_printf_odex_system
 * The printing function for explicit ODE systems.
 * It is called by @code{ba0_printf/%odex}.
 */

BAI_DLL void
bai_printf_odex_system (
    void *S0)
{
  struct bai_odex_system *S = (struct bai_odex_system *) S0;
  ba0_int_p i;
  bool b;

  ba0_printf ("odex %s", "(");
  b = false;
  if (S->params.size > 0)
    {
      b = true;
      ba0_printf ("params = %t[%v]", &S->params);
    }
  if (S->commands.size > 0)
    {
      if (b)
        ba0_printf (", ");
      b = true;
      ba0_printf ("commands = %t[%v]", &S->commands);
    }
  if (S->rhs.size > 0)
    {
      if (b)
        ba0_printf (", ");
      b = true;
      ba0_printf ("eqns = %s", "[");
      for (i = 0; i < S->lhs.size - 1; i++)
        ba0_printf ("%v = %Qz, ", S->lhs.tab[i], S->rhs.tab[i]);
      ba0_printf ("%v = %Qz%s", S->lhs.tab[S->lhs.size - 1],
          S->rhs.tab[S->rhs.size - 1], "])");
    }
}

/*
 * Readonly static data
 */

static char _odex[] = "struct bai_odex_system";

BAI_DLL ba0_int_p
bai_garbage1_odex_system (
    void *S0,
    enum ba0_garbage_code code)
{
  struct bai_odex_system *S = (struct bai_odex_system *) S0;
  ba0_int_p n;

  n = 0;
  if (code == ba0_isolated)
    {
      ba0_new_gc_info (S, sizeof (struct bai_odex_system), _odex);
      n += 1;
    }

  n += ba0_garbage1 ("%t[%v]", &S->lhs, ba0_embedded);
  n += ba0_garbage1 ("%t[%Qz]", &S->rhs, ba0_embedded);
  n += ba0_garbage1 ("%t[%v]", &S->params, ba0_embedded);
  n += ba0_garbage1 ("%t[%v]", &S->commands, ba0_embedded);
  return n;
}

BAI_DLL void *
bai_garbage2_odex_system (
    void *S0,
    enum ba0_garbage_code code)
{
  struct bai_odex_system *S;

  if (code == ba0_isolated)
    S = (struct bai_odex_system *) ba0_new_addr_gc_info (S0, _odex);
  else
    S = (struct bai_odex_system *) S0;

  ba0_garbage2 ("%t[%v]", &S->lhs, ba0_embedded);
  ba0_garbage2 ("%t[%Qz]", &S->rhs, ba0_embedded);
  ba0_garbage2 ("%t[%v]", &S->params, ba0_embedded);
  ba0_garbage2 ("%t[%v]", &S->commands, ba0_embedded);
  return S;
}

BAI_DLL void *
bai_copy_odex_system (
    void *S0)
{
  struct bai_odex_system *S;

  S = (struct bai_odex_system *) ba0_alloc (sizeof (struct bai_odex_system));
  bai_init_odex_system (S);
  bai_set_odex_system (S, (struct bai_odex_system *) S0);
  return S;
}

/*
 * Code generation
 */

#define the_system	bai_global.odex.system

static void
bai_printf_variable (
    void *z)
{
  struct bav_variable *v = (struct bav_variable *) z;
  ba0_int_p k;

  if (bav_symbol_type_variable (v) == bav_independent_symbol)
    ba0_printf ("t");
  else if (bai_odex_is_lhs (v, the_system, &k))
    ba0_printf ("x[%d]", k);
  else if (ba0_member2_table (v, (struct ba0_table *) &the_system->params, &k))
    ba0_printf ("p[%d]", k);
  else if (ba0_member2_table (v, (struct ba0_table *) &the_system->commands,
          &k))
    ba0_printf ("c[%d] (t, params)", k);
  else
    BA0_RAISE_EXCEPTION (BAI_ERRUNK);
}

static void
bai_printf_rank (
    void *z)
{
  struct bav_rank *rg = (struct bav_rank *) z;

  if (rg->deg == 0)
    ba0_printf ("1.");
  else if (rg->deg == 1)
    ba0_printf ("%v", rg->var);
  else if (rg->deg == 2)
    ba0_printf ("%v*%v", rg->var, rg->var);
  else
    ba0_printf ("pow (%v, (double)%d)", rg->var, rg->deg);
}

/*
 * Insert some (double) casts to avoid expressions such as 1/3
 */

static void
bai_fprintf_ratfrac_mpz (
    FILE *f,
    struct baz_ratfrac *A)
{
  if (baz_is_zero_ratfrac (A))
    ba0_fprintf (f, "(double)0");
  else if (bap_is_one_polynom_mpz (&A->denom))
    {
      if (bap_is_numeric_polynom_mpz (&A->numer))
        ba0_fprintf (f, "(double)");
      ba0_fprintf (f, "%Az", &A->numer);
    }
  else
    {
      ba0_fprintf (f, "%s", "(");
      if (bap_is_numeric_polynom_mpz (&A->numer))
        ba0_fprintf (f, "(double)");
      ba0_fprintf (f, "%Az", &A->numer);
      ba0_fprintf (f, "%s", ")/(");
      if (bap_is_numeric_polynom_mpz (&A->denom))
        ba0_fprintf (f, "(double)");
      ba0_fprintf (f, "%Az", &A->denom);
      ba0_fprintf (f, "%s", ")");
    }
  ba0_fprintf (f, ";\n");
}

/*
 * texinfo: bai_odex_generate_rhs_C_code
 * Write in @var{f} (which must be open in write mode) the C code of a
 * function which evaluates the righthand sides of @var{S}. The identifier
 * of the generated C function is given in @var{ident}.
 * The generated C function has a @code{bai_odex_integrated_function} signature.
 */

BAI_DLL void
bai_odex_generate_rhs_C_code (
    FILE *f,
    char *ident,
    struct bai_odex_system *S)
{
  ba0_printf_function *printf_variable, *printf_rank;
  ba0_int_p i;

  ba0_fprintf (f, "%s", "#include <math.h>\n\n");
  ba0_fprintf (f, "%s", "#ifdef _MSC_VER\n");
  ba0_fprintf (f, "%s", "#    include <float.h>\n");
  ba0_fprintf (f, "%s", "#else\n");
  ba0_fprintf (f, "%s", "#    if HAVE_IEEEFP_H\n");
  ba0_fprintf (f, "%s", "#        include <ieeefp.h>\n");
  ba0_fprintf (f, "%s", "#    endif\n");
  ba0_fprintf (f, "%s", "#endif\n\n");

  ba0_fprintf (f, "%s", "struct bai_parameters {\n");
  ba0_fprintf (f, "%s", "    double* values;\n");
  ba0_fprintf (f, "%s", "    void* names;\n");
  ba0_fprintf (f, "%s", "};\n\n");

  ba0_fprintf (f, "typedef double bai_command_function (double, void*);\n\n");

  ba0_fprintf (f, "%s", "struct bai_commands {\n");
  ba0_fprintf (f, "%s", "    bai_command_function** fptrs;\n");
  ba0_fprintf (f, "%s", "    void* names;\n");
  ba0_fprintf (f, "%s", "};\n\n");

  ba0_fprintf (f, "%s", "struct bai_params {\n");
  ba0_fprintf (f, "%s", "    struct bai_parameters pars;\n");
  ba0_fprintf (f, "%s", "    struct bai_commands cmds;\n");
  ba0_fprintf (f, "%s", "    void* extra;\n");
  ba0_fprintf (f, "%s", "};\n\n");

  ba0_fprintf (f, "%s",
      "enum bai_odex_exit_code { bai_odex_success = 0, bai_odex_non_finite = 1 };\n\n");

  ba0_fprintf (f, "enum bai_odex_exit_code %s\n\t", ident);
  ba0_fprintf (f, "(double t, double* x, double* f, void* params)\n");
  ba0_fprintf (f, "%s", "{   double* p;\n");
  ba0_fprintf (f, "%s", "    bai_command_function** c;\n\n");

  ba0_fprintf (f, "%s", "    p = ((struct bai_params*)params)->pars.values;\n");
  ba0_fprintf (f, "%s",
      "    c = ((struct bai_params*)params)->cmds.fptrs;\n\n");

  bav_get_settings_variable (0, &printf_variable, 0, 0, 0);
  bav_get_settings_rank (&printf_rank);

  BA0_TRY
  {
    bav_set_settings_variable (0, &bai_printf_variable, 0, 0, 0);
    bav_set_settings_rank (&bai_printf_rank);

    the_system = S;

    for (i = 0; i < the_system->rhs.size; i++)
      {
        ba0_fprintf (f, "    f[%d] = ", i);
        bai_fprintf_ratfrac_mpz (f, the_system->rhs.tab[i]);

        ba0_fprintf (f, "    if (! isfinite (f[%d]))\n", i);
        ba0_fprintf (f, "        return bai_odex_non_finite;\n");
      }

    ba0_fprintf (f, "%s", "    return bai_odex_success;\n");
    ba0_fprintf (f, "%s", "}\n\n");

    bav_set_settings_variable (0, printf_variable, 0, 0, 0);
    bav_set_settings_rank (printf_rank);
  }
  BA0_CATCH
  {
    bav_set_settings_variable (0, printf_variable, 0, 0, 0);
    bav_set_settings_rank (printf_rank);
    BA0_RE_RAISE_EXCEPTION;
  }
  BA0_ENDTRY;
}

/*
 * texinfo: bai_odex_generate_jacobianof_rhs_C_code
 * Write in @var{f} (which must be open in write mode) the C code of a
 * function which evaluates the Jacobian matrix of @var{S}. The identifier
 * of the generated C function is given in @var{ident}.
 * The generated C function has a
 * @code{bai_odex_jacobianof_integrated_function} signature.
 * This function should always be called after @code{bai_odex_generate_rhs_C_code}
 * for the generated code makes use of the type declarations written
 * by the above function.
 */

BAI_DLL void
bai_odex_generate_jacobianof_rhs_C_code (
    FILE *f,
    char *ident,
    struct bai_odex_system *S)
{
  struct baz_ratfrac R;
  struct bav_variable *v;
  ba0_printf_function *printf_variable, *printf_rank;
  struct ba0_mark M;
  ba0_int_p i, lig, col;

  ba0_record (&M);

  ba0_fprintf (f, "enum bai_odex_exit_code %s\n\t", ident);
  ba0_fprintf (f,
      "(double t, double* x, double* J, double* dfdt, void* params)\n");
  ba0_fprintf (f, "%s", "{   double* p;\n");
  ba0_fprintf (f, "%s", "    bai_command_function** c;\n\n");

  ba0_fprintf (f, "%s", "    p = ((struct bai_params*)params)->pars.values;\n");
  ba0_fprintf (f, "%s",
      "    c = ((struct bai_params*)params)->cmds.fptrs;\n\n");

  bav_get_settings_variable (0, &printf_variable, 0, 0, 0);
  bav_get_settings_rank (&printf_rank);

  BA0_TRY
  {
    bav_set_settings_variable (0, &bai_printf_variable, 0, 0, 0);
    bav_set_settings_rank (&bai_printf_rank);

    the_system = S;

    baz_init_ratfrac (&R);
    for (lig = 0; lig < S->lhs.size; lig++)
      {
        for (col = 0; col < S->lhs.size; col++)
          {
            v = bav_order_zero_variable (S->lhs.tab[col]);
            baz_separant2_ratfrac (&R, S->rhs.tab[lig], v);
            i = lig * S->lhs.size + col;
            ba0_fprintf (f, "    J[%d] = ", i);
            bai_fprintf_ratfrac_mpz (f, &R);
            ba0_fprintf (f, "    if (! isfinite (J[%d]))\n", i);
            ba0_fprintf (f, "        return bai_odex_non_finite;\n");
          }
      }

    ba0_fprintf (f, "\n");

    for (i = 0; i < S->lhs.size; i++)
      {
        baz_separant2_ratfrac (&R, S->rhs.tab[i], S->t);
        ba0_fprintf (f, "    dfdt[%d] = ", i);
        bai_fprintf_ratfrac_mpz (f, &R);
        ba0_fprintf (f, "    if (! isfinite (dfdt[%d]))\n", i);
        ba0_fprintf (f, "        return bai_odex_non_finite;\n");
      }

    ba0_fprintf (f, "\n");
    ba0_fprintf (f, "%s", "    return bai_odex_success;\n");
    ba0_fprintf (f, "%s", "}\n\n");

    bav_set_settings_variable (0, printf_variable, 0, 0, 0);
    bav_set_settings_rank (printf_rank);
  }
  BA0_CATCH
  {
    bav_set_settings_variable (0, printf_variable, 0, 0, 0);
    bav_set_settings_rank (printf_rank);
    BA0_RE_RAISE_EXCEPTION;
  }
  BA0_ENDTRY;
  ba0_restore (&M);
}
