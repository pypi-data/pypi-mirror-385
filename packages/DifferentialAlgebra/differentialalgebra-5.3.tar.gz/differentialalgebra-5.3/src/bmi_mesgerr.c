#include "bmi_mesgerr.h"

/*
 * "This should not happen" errors
 */
char BMI_ERRNARGS[] = "blad_eval expects at least one parameter";
char BMI_ERROPTS[]  = "unknown BMI option";
char BMI_ERRFUN[]   = "unknown exported function";
char BMI_ERRNOPS[]  = "wrong number of parameters";
char BMI_ERRFILE[]  = "error while recording blad_eval command";
char BMI_ERRPARS[]  = "wrong list of parameters";
char BMI_ERRREGC[]  = "wrong regchain parameter";
char BMI_ERRDRNG[]  = "wrong differential ring parameter";
char BMI_ERRDLUP[]  = "wrong DLuple parameter";
/*
 * Error messages that might actually be produced
 */
char BMI_ERRMETH[]  = "Wrong reduction mode";
char BMI_ERRMODE[]  = "Wrong sorting mode";
char BMI_ERRCRIT[]  = "wrong criterion parameter";
char BMI_ERRNIL[]   = "empty list non expected";
char BMI_ERRCST[]   = "numeric polynomial non expected";
char BMI_ERRIND[]   = "independent polynomial non expected";
char BMI_ERRINDV[]  = "dependent variable expected";
char BMI_ERRCOEF[]  = "denominator with mixed variables non expected";
char BMI_ERRDER[]   = "independent variable expected";
char BMI_ERRROP[]   = "relational operator '==' or '!=' expected";

char BMI_ERRZSTR[]  = "wrong string format";

char BMI_ERRPRNK[]  = "wrong or incompatible ordering";
char BMI_ERRPARD[]  = "prime ideal expected";

char BMI_ERRLPT[] =
    "the conditions for applying the Low Power Theorem are not satisfied";
char BMI_ERRRBL[] =
    "independent rational fractions are incompatible with the iterated version of the algorithm";
