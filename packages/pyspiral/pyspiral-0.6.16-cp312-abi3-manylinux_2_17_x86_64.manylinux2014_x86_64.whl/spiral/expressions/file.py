from spiral import _lib
from spiral.expressions.base import Expr, ExprLike


def get(expr: ExprLike) -> Expr:
    """Read data from the local filesystem by the file:// URL.

    Args:
        expr: URLs of the data that needs to be read.
    """
    from spiral import expressions as se

    expr = se.lift(expr)

    # This just works :)
    return Expr(_lib.expr.s3.get(expr.__expr__))
