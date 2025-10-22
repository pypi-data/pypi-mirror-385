#if !defined (BAV_PARAMETERS_H)
#   define BAV_PARAMETERS_H

#   include "bav_parameter.h"

BEGIN_C_DECLS

/*
 * texinfo: bav_parameters
 * This data type is only used to form the field @code{pars}
 * of the @code{bav_differential_ring} structure. It handles
 * the parameters of the differential ring.
 *
 * The field @code{pars} contains the table of all parameters.
 * Each range indexed group occurring in any element of the
 * table actually is a range indexed string i.e. has a single radical.
 *
 * The field @code{dict} maps strings to non-plain parameters in @code{pars}. 
 * The keys are the radicals of the range indexed strings. 
 * The dictionary does not contain any entry corresponding to plain parameters.
 */

struct bav_parameters
{
// maps strings to radicals of range indexed strings for non-plain parameters
  struct ba0_dictionary_string dict;
// the table of parameters - range indexed groups are range indexed strings
  struct bav_tableof_parameter pars;
};

extern BAV_DLL void bav_init_parameters (
    struct bav_parameters *);

extern BAV_DLL unsigned ba0_int_p bav_sizeof_parameters (
    struct bav_parameters *,
    enum ba0_garbage_code,
    bool);

extern BAV_DLL void bav_R_set_parameters (
    struct bav_parameters *,
    struct bav_parameters *,
    struct bav_differential_ring *);

extern BAV_DLL void bav_R_set_parameters_tableof_parameter (
    struct bav_parameters *,
    struct bav_tableof_parameter *);

END_C_DECLS
#endif /* !BAV_PARAMETERS_H */
