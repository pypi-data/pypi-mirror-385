from spiral import _lib
from spiral.expressions.base import Expr, ExprLike


def get(expr: ExprLike) -> Expr:
    """Read data from object storage by the s3:// URL.

    Args:
        expr: URLs of the data that needs to be read from object storage.
    """
    from spiral import expressions as se

    expr = se.lift(expr)

    return Expr(_lib.expr.s3.get(expr.__expr__))
