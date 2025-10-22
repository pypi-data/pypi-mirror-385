#if !defined (BA0_BASIC_IO_H)
#   define BA0_BASIC_IO_H 1

#   include "ba0_common.h"

BEGIN_C_DECLS

/*
 * texinfo: ba0_typeof_device
 * This data type permits to specify the device from/to which
 * the input is read of the output is written.
 */

enum ba0_typeof_device
{
  ba0_string_device,
  ba0_file_device,
  ba0_counter_device
};

/*
 * texinfo: ba0_output_device
 * This data type the device to which output is written.
 */

struct ba0_output_device
{
  enum ba0_typeof_device vers;
// if vers is equal to ba0_file_device
  FILE *file_flux;
// if vers is equal to ba0_string_device
  char *string_flux;
// index in string_flux
  ba0_int_p indice;
// if vers is equal to ba0_counter_device (number of output characters)
  ba0_int_p counter;
};

#   define BA0_DEFAULT_OUTPUT_LINE_LENGTH	80
#   define ba0_output_line_length ba0_global.basic_io.output_line_length

extern BA0_DLL void ba0_set_output_FILE (
    FILE *);

extern BA0_DLL void ba0_set_output_string (
    char *);

extern BA0_DLL void ba0_set_output_counter (
    void);

#   define BA0_BASIC_IO_SIZE_STACK 10

extern BA0_DLL void ba0_record_output (
    void);

extern BA0_DLL void ba0_restore_output (
    void);

extern BA0_DLL void ba0_reset_output (
    void);

extern BA0_DLL void ba0_put_char (
    char);

extern BA0_DLL void ba0_put_int_p (
    ba0_int_p);

extern BA0_DLL void ba0_put_hexint_p (
    ba0_int_p);

extern BA0_DLL ba0_printf_function ba0_put_string;

extern BA0_DLL ba0_int_p ba0_output_counter (
    void);

/*
 * texinfo: ba0_input_device
 * This data type the device from which input is read.
 */

struct ba0_input_device
{
  enum ba0_typeof_device from;
// if from == ba0_file_device
  FILE *file_flux;
// if from == ba0_string_device
  char *string_flux;
  ba0_int_p indice;
};

extern BA0_DLL void ba0_set_input_FILE (
    FILE *);

extern BA0_DLL void ba0_set_input_string (
    char *);

extern BA0_DLL bool ba0_isatty_input (
    void);

extern BA0_DLL void ba0_reset_input (
    void);

extern BA0_DLL void ba0_record_input (
    void);

extern BA0_DLL void ba0_restore_input (
    void);

extern BA0_DLL int ba0_get_char (
    void);

extern BA0_DLL void ba0_unget_char (
    int);

END_C_DECLS
#endif /* !BA0_BASIC_IO_H */
