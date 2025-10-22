#if !defined (BAS_DL_VERTEX_H)
#   define BAS_DL_VERTEX_H 1

#   include "bas_DL_edge.h"
#   include "bas_Zuple.h"

BEGIN_C_DECLS

/*
 * texinfo: bas_typeof_consistency_vertex
 * This data type is a subtype of @code{bas_DL_vertex}.
 * It determines the consistency information of one vertex
 * of a DL tree.
 */

enum bas_typeof_consistency_vertex
{
// the vertex is inconsistent
  bas_inconsistent_vertex,
// the vertex is rejected because kappa is exceeded
  bas_rejected_vertex,
// the consistency of the vertex is uncertain (at least when created)
  bas_uncertain_vertex,
// the vertex is consistent
  bas_consistent_vertex
};

/*
 * texinfo: bas_DL_vertex
 * This data type is a subtype of @code{bas_DL_tree}.
 * It permits to describe one vertex of the tree.
 * Each vertex corresponds to a Zuple @var{Z}, which
 * is identified by its @emph{number}.
 *
 * The field @code{number} contains the number of the vertex.
 *
 * The field @code{consistency} provides the consistency information
 * for the vertex. The default value is @code{bas_uncertain_vertex}.
 *
 * The field @code{edges} contains the table of the edges starting
 * from the vertex towards other vertices of the DL tree.
 *
 * The field @code{action} contains the action to be undertaken on the vertex.
 * The field @code{y} contains the differential indeterminate
 * with respect to which the action is undertaken. 
 * The fields @code{k}, @code{r} and @code{deg} contain the entries of the 
 * corresponding fields of @var{Z} which apply to @code{y}.
 */

struct bas_DL_vertex
{
// the number of the vertex which is also the number of the quadruple
  ba0_int_p number;
// the consistency information for the vertex
  enum bas_typeof_consistency_vertex consistency;
// the edges towards the children of the vertex
  struct bas_tableof_DL_edge edges;
// information of the process undertaken by the vertex
  enum bas_typeof_action_on_Zuple action;
  struct bav_symbol *y;
  ba0_int_p k;
  ba0_int_p r;
  ba0_int_p deg;
};

struct bas_tableof_DL_vertex
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bas_DL_vertex **tab;
};

extern BAS_DLL void bas_init_DL_vertex (
    struct bas_DL_vertex *);

extern BAS_DLL struct bas_DL_vertex *bas_new_DL_vertex (
    void);

extern BAS_DLL void bas_reset_DL_vertex (
    struct bas_DL_vertex *,
    ba0_int_p);

extern BAS_DLL void bas_set_DL_vertex (
    struct bas_DL_vertex *,
    struct bas_DL_vertex *);

extern BAS_DLL void bas_set_aykrd_DL_vertex (
    struct bas_DL_vertex *,
    enum bas_typeof_action_on_Zuple,
    struct bav_symbol *,
    ba0_int_p,
    ba0_int_p,
    ba0_int_p);

extern BAS_DLL ba0_scanf_function bas_scanf_DL_vertex;

extern BAS_DLL ba0_printf_function bas_printf_DL_vertex;

extern BAS_DLL ba0_garbage1_function bas_garbage1_DL_vertex;

extern BAS_DLL ba0_garbage2_function bas_garbage2_DL_vertex;

extern BAS_DLL ba0_copy_function bas_copy_DL_vertex;

END_C_DECLS
#endif /* !BAS_DL_VERTEX_H */
