#if !defined (BAD_SPLITTING_VERTEX_H)
#   define BAD_SPLITTING_VERTEX_H 1

#   include "bad_splitting_edge.h"

BEGIN_C_DECLS

/*
 * texinfo: bad_shapeof_splitting_vertex
 * This data type is a subtype of @code{bad_splitting_vertex}.
 * It permits to associate a @emph{shape} to a vertex.
 * @itemize
 * @item    parallelogram vertices correspond to vertices which
 * are rejected by means of a dimension argument
 * @item    triangle vertices correspond to vertices which are
 * discarded because a new equation is incompatible with some
 * existing inequation
 * @item    box vertices correspond to output regular differential chains
 * @item    hexagon vertices correspond to systems handled by the
 * @emph{regCharacteristic} algorithm
 * @item    ellipse vertices correspond to any other case.
 * @end itemize
 */

enum bad_shapeof_splitting_vertex
{
  bad_parallelogram_vertex,
  bad_triangle_vertex,
  bad_box_vertex,
  bad_ellipse_vertex,
  bad_hexagon_vertex
};

/*
 * texinfo: bad_splitting_vertex
 * This data type is a subtype of @code{bad_splitting_tree}.
 * It permits to describe one vertex of the tree.
 * Each vertex corresponds to a quadruple / regular chain, which
 * is identified by its @emph{number}.
 *
 * The field @code{number} contains the number of the vertex.
 *
 * The field @code{is_first} indicates if the vertex is a @dfn{first}
 * vertex. First vertices play a special role in elimination methods
 * for they provide bounds which permit to discard quadruples
 * by means of a dimension argument.
 *
 * The field @code{edges} contains the table of the edges starting
 * from the vertex towards other vertices of the splitting tree.
 * This table is sorted by increasing @code{dst} number.
 *
 * The field @code{shape} contains the shape of the vertex.
 *
 * The fields @code{thetas} and @code{leaders} are only meaningful
 * if the successors of the vertex in the splitting tree were
 * obtained by a process involving a differential reduction step.
 * In such a case, @code{leaders} contains the leaders of the
 * regular differential chain used to performed the reduction while
 * @code{thetas} contains the least common multiple of the derivative
 * operators applied to these regular differential chain elements
 * by the reduction. Both tables have the same size and there is a
 * one-to-one correspondence between there elements.
 *
 * The field @code{discarded_branch} indicates if a possible branch,
 * starting from the vertex, was discarded because of the presence
 * of differential inequations.
 */

struct bad_splitting_vertex
{
// the number of the vertex which is also the number of the quadruple
  ba0_int_p number;
// indicate if the vertex is a ``first'' vertex
  bool is_first;
// the shape of the vertex
  enum bad_shapeof_splitting_vertex shape;
// the edges towards the children of the vertex
  struct bad_tableof_splitting_edge edges;
// the derivative operators involved in a reduction process (if applicable)
  struct bav_tableof_term thetas;
// the leaders of the polynomials they have applied to (if applicable)
  struct bav_tableof_variable leaders;
};

struct bad_tableof_splitting_vertex
{
  ba0_int_p alloc;
  ba0_int_p size;
  struct bad_splitting_vertex **tab;
};

extern BAD_DLL void bad_init_splitting_vertex (
    struct bad_splitting_vertex *);

extern BAD_DLL struct bad_splitting_vertex *bad_new_splitting_vertex (
    void);

extern BAD_DLL void bad_reset_splitting_vertex (
    struct bad_splitting_vertex *,
    ba0_int_p);

extern BAD_DLL void bad_set_splitting_vertex (
    struct bad_splitting_vertex *,
    struct bad_splitting_vertex *);

extern BAD_DLL void bad_merge_thetas_leaders_splitting_vertex (
    struct bad_splitting_vertex *,
    struct bav_tableof_term *,
    struct bav_tableof_variable *);

extern BAD_DLL char *bad_shapeof_splitting_vertex_to_string (
    enum bad_shapeof_splitting_vertex);

extern BAD_DLL ba0_scanf_function bad_scanf_splitting_vertex;

extern BAD_DLL ba0_printf_function bad_printf_splitting_vertex;

extern BAD_DLL ba0_garbage1_function bad_garbage1_splitting_vertex;

extern BAD_DLL ba0_garbage2_function bad_garbage2_splitting_vertex;

extern BAD_DLL ba0_copy_function bad_copy_splitting_vertex;


END_C_DECLS
#endif /* !BAD_SPLITTING_VERTEX_H */
