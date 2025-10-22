from spiral.core.table import KeyRange
from spiral.core.table import Transaction as CoreTransaction
from spiral.core.table.spec import Operation
from spiral.expressions.base import ExprLike
from spiral.scan import Scan


class Transaction:
    """Spiral table transaction.

    IMPORTANT: While transaction can be used to atomically write data to the table,
            it is important that the primary key columns are unique within the transaction.
    """

    def __init__(self, core: CoreTransaction):
        self._core = core

    @property
    def status(self) -> str:
        """The status of the transaction."""
        return self._core.status

    def is_empty(self) -> bool:
        """Check if the transaction has no operations."""
        return self._core.is_empty()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self._core.commit()
        else:
            self._core.abort()

    def write(self, expr: ExprLike, *, partition_size_bytes: int | None = None):
        """Write an item to the table inside a single transaction.

        :param expr: The expression to write. Must evaluate to a struct array.
        :param partition_size_bytes: The maximum partition size in bytes.
            If not provided, the default partition size is used.
        """
        from spiral import expressions as se

        record_batches = se.evaluate(expr)

        self._core.write(record_batches, partition_size_bytes=partition_size_bytes)

    def writeback(
        self,
        scan: Scan,
        *,
        key_range: KeyRange | None = None,
        partition_size_bytes: int | None = None,
        batch_readahead: int | None = None,
    ):
        """Write back the results of a scan to the table.

        :param scan: The scan to write back.
            The scan does NOT need to be over the same table as transaction,
            but it does need to have the same key schema.
        :param key_range: Optional key range to limit the writeback to.
        :param partition_size_bytes: The maximum partition size in bytes.
        :param batch_readahead: The number of batches to read ahead when evaluating the scan.
        """
        self._core.writeback(
            scan.core, key_range=key_range, partition_size_bytes=partition_size_bytes, batch_readahead=batch_readahead
        )

    def drop_columns(self, column_paths: list[str]):
        """
        Drops the specified columns from the table.


        :param column_paths: Fully qualified column names. (e.g., "column_name" or "nested.field").
            All columns must exist, if a column doesn't exist the function will return an error.
        """
        self._core.drop_columns(column_paths)

    def take(self) -> list[Operation]:
        """Take the operations from the transaction

        Transaction can no longer be committed or aborted after calling this method.
        ."""
        return self._core.take()

    def include(self, ops: list[Operation]):
        """Include the given operations in the transaction.

        Checks for conflicts between the included operations and any existing operations.
        """
        self._core.include(ops)

    def commit(self):
        """Commit the transaction."""
        self._core.commit()

    def abort(self):
        """Abort the transaction."""
        self._core.abort()
