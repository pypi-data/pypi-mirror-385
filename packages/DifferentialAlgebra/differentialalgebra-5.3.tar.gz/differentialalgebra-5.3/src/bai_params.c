#include "bai_params.h"
#include "bai_odex.h"

/*
 * BAI_PARAMETERS
 */

static void
bai_init_parameters (
    struct bai_parameters *params)
{
  params->values = (double *) 0;
  params->names = ba0_new_table ();
}

static void
bai_reset_parameters (
    struct bai_parameters *params)
{
  struct ba0_table *names = (struct ba0_table *) params->names;

  ba0_reset_table (names);
}

static void
bai_set_parameters (
    struct bai_parameters *P,
    struct bai_parameters *Q)
{
  struct ba0_table *Pnames, *Qnames;

  if (P != Q)
    {
      Pnames = (struct ba0_table *) P->names;
      Qnames = (struct ba0_table *) Q->names;
      if (Pnames->alloc < Qnames->alloc)
        {
          P->values = (double *) ba0_alloc (sizeof (double) * Qnames->alloc);
        }
      memcpy (P->values, Q->values, sizeof (double) * Qnames->size);
      ba0_set_table (Pnames, Qnames);
    }
}

/*
 * The issue consists in reallocating values together with names
 */

static void
bai_realloc_parameters (
    struct bai_parameters *params,
    ba0_int_p n)
{
  struct ba0_table *names;
  double *new_values;

  names = (struct ba0_table *) params->names;
  if (names->alloc < n)
    {
      new_values = (double *) ba0_alloc (sizeof (double) * n);
      if (params->values != (double *) 0)
        memcpy (new_values, params->values, sizeof (double) * names->size);
      params->values = new_values;
      ba0_realloc_table (names, n);
    }
}

/*
 * This function sets the names of the pameters.
 */

static void
bai_set_parameters_tableof_variable (
    struct bai_parameters *params,
    struct bav_tableof_variable *idents)
{
  bai_realloc_parameters (params, idents->size);
  ba0_set_table ((struct ba0_table *) params->names,
      (struct ba0_table *) idents);
}

/*
 * The parameter must be defined
 */

static void
bai_set_parameters_variable (
    struct bai_parameters *params,
    struct bav_variable *v,
    double d)
{
  struct ba0_table *names;
  ba0_int_p i;

  names = (struct ba0_table *) params->names;
  if (ba0_member2_table (v, names, &i))
    {
      params->values[i] = d;
    }
  else
    BA0_RAISE_EXCEPTION (BAI_ERRUNK);
}

/*
 * BAI_COMMANDS
 */

static void
bai_init_commands (
    struct bai_commands *commands)
{
  commands->fptrs = (bai_command_function **) 0;
  commands->names = ba0_new_table ();
}

static void
bai_reset_commands (
    struct bai_commands *commands)
{
  struct ba0_table *names = (struct ba0_table *) commands->names;

  ba0_reset_table (names);
}

static void
bai_set_commands (
    struct bai_commands *P,
    struct bai_commands *Q)
{
  struct ba0_table *Pnames, *Qnames;

  if (P != Q)
    {
      Pnames = (struct ba0_table *) P->names;
      Qnames = (struct ba0_table *) Q->names;
      if (Pnames->alloc < Qnames->alloc)
        {
          P->fptrs =
              (bai_command_function **) ba0_alloc (sizeof (bai_command_function
                  *) * Qnames->alloc);
        }
      memcpy (P->fptrs, Q->fptrs,
          sizeof (bai_command_function *) * Qnames->size);
      ba0_set_table (Pnames, Qnames);
    }
}

/*
 * The issue consists in reallocating the field fptrs together with names
 */

static void
bai_realloc_commands (
    struct bai_commands *commands,
    ba0_int_p n)
{
  struct ba0_table *names;
  bai_command_function **new_fptrs;

  names = (struct ba0_table *) commands->names;
  if (names->alloc < n)
    {
      new_fptrs =
          (bai_command_function **) ba0_alloc (sizeof (bai_command_function *) *
          n);
      if (commands->fptrs != (bai_command_function **) 0)
        memcpy (new_fptrs, commands->fptrs,
            sizeof (bai_command_function *) * names->size);
      commands->fptrs = new_fptrs;
      ba0_realloc_table (names, n);
    }
}

/*
 * Sets the names of the commands
 */

static void
bai_set_commands_tableof_variable (
    struct bai_commands *commands,
    struct bav_tableof_variable *idents)
{
  bai_realloc_commands (commands, idents->size);
  ba0_set_table ((struct ba0_table *) commands->names,
      (struct ba0_table *) idents);
}

/*
 * The command must be defined
 */

static void
bai_set_commands_variable (
    struct bai_commands *commands,
    struct bav_variable *v,
    bai_command_function *f)
{
  struct ba0_table *names;
  ba0_int_p i;

  names = (struct ba0_table *) commands->names;
  if (ba0_member2_table (v, names, &i))
    {
      commands->fptrs[i] = f;
    }
  else
    BA0_RAISE_EXCEPTION (BAI_ERRUNK);
}

/*
 * BAI_PARAMS
 */

/*
 * texinfo: bai_init_params
 * Initialize @var{p}.
 */

BAI_DLL void
bai_init_params (
    struct bai_params *p)
{
  bai_init_parameters (&p->pars);
  bai_init_commands (&p->cmds);
}

/*
 * texinfo: bai_reset_params
 * Reset to zero the sizes of the tables of @var{p}.
 */

BAI_DLL void
bai_reset_params (
    struct bai_params *p)
{
  bai_reset_parameters (&p->pars);
  bai_reset_commands (&p->cmds);
}

/*
 * texinfo: bai_new_params
 * Allocate a new structure, initialize it and return it.
 */

BAI_DLL struct bai_params *
bai_new_params (
    void)
{
  struct bai_params *p;

  p = (struct bai_params *) ba0_alloc (sizeof (struct bai_params));
  bai_init_params (p);
  return p;
}

/*
 * texinfo: bai_set_params
 * Assign @var{q} to @var{p}.
 */

BAI_DLL void
bai_set_params (
    struct bai_params *p,
    struct bai_params *q)
{
  bai_set_parameters (&p->pars, &q->pars);
  bai_set_commands (&p->cmds, &q->cmds);
  p->extra = q->extra;
}

/*
 * texinfo: bai_set_params_odex_system
 * Make a copy of the fields @code{params} and @code{commands} of @var{S}
 * in the subfields @code{pars.names} and @code{cmds.names} of @var{p}. 
 * The order of the tables @code{params} and @code{commands} are preserved.
 * This function must be called before setting any parameter or command value.
 */

BAI_DLL void
bai_set_params_odex_system (
    struct bai_params *p,
    struct bai_odex_system *S)
{
  bai_set_parameters_tableof_variable (&p->pars, &S->params);
  bai_set_commands_tableof_variable (&p->cmds, &S->commands);
}

/*
 * texinfo: bai_set_params_parameter
 * Assign @var{d} to the value of @var{v}. 
 * The parameter @var{v} must be already defined in the subfield 
 * @code{pars.names} of @var{p}. 
 * Exception @code{BAI_ERRUNK} is raised if @var{v} is not defined.
 */

BAI_DLL void
bai_set_params_parameter (
    struct bai_params *p,
    struct bav_variable *v,
    double d)
{
  bai_set_parameters_variable (&p->pars, v, d);
}

/*
 * texinfo: bai_set_params_command
 * Assign @var{f} to the function associated to the command  @var{v}. 
 * The command @var{v} must be already defined in the subfield 
 * @code{cmds.names} of @var{p}.
 * Exception @code{BAI_ERRUNK} is raised if @var{v} is not defined.
 */

BAI_DLL void
bai_set_params_command (
    struct bai_params *p,
    struct bav_variable *v,
    bai_command_function *f)
{
  bai_set_commands_variable (&p->cmds, v, f);
}
