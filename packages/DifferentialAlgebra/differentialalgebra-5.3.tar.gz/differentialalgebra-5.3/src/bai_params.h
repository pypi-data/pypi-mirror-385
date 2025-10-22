#if !defined (BAI_PARAMETERS_H)
#   define BAI_PARAMETERS_H 1

#   include "bai_common.h"

BEGIN_C_DECLS
/* Keep it here */
#   include "bai_odex_function.h"
extern BAI_DLL void bai_init_params (
    struct bai_params *);

extern BAI_DLL void bai_reset_params (
    struct bai_params *);

extern BAI_DLL struct bai_params *bai_new_params (
    void);

extern BAI_DLL void bai_set_params (
    struct bai_params *,
    struct bai_params *);

struct bai_odex_system;

extern BAI_DLL void bai_set_params_odex_system (
    struct bai_params *,
    struct bai_odex_system *);

extern BAI_DLL void bai_set_params_parameter (
    struct bai_params *,
    struct bav_variable *,
    double);

extern BAI_DLL void bai_set_params_command (
    struct bai_params *,
    struct bav_variable *,
    bai_command_function *);

END_C_DECLS
#endif /* !BAI_PARAMETERS_H */
