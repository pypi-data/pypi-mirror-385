import dataclasses
import logging
from functools import partial
from typing import TYPE_CHECKING, Optional

from spiral.core.client import Shard
from spiral.core.table.spec import Operation
from spiral.expressions import Expr

if TYPE_CHECKING:
    from spiral import KeySpaceIndex, Table

logger = logging.getLogger(__name__)


class Enrichment:
    """
    An enrichment is used to derive new columns from the existing once, such as fetching data from object storage
    with `se.s3.get` or compute embeddings. With column groups design supporting 100s of thousands of columns,
    horizontally expanding tables are a powerful primitive.

    NOTE: Spiral aims to optimize enrichments where source and destination table are the same.
    """

    def __init__(
        self,
        table: "Table",
        projection: Expr,
        where: Expr | None,
    ):
        self._table = table
        self._projection = projection
        self._where = where

    @property
    def table(self) -> "Table":
        """The table to write back into."""
        return self._table

    @property
    def projection(self) -> Expr:
        """The projection expression."""
        return self._projection

    @property
    def where(self) -> Expr | None:
        """The filter expression."""
        return self._where

    def apply(self, *, batch_readahead: int | None = None, partition_size_bytes: int | None = None) -> None:
        """Apply the enrichment onto the table in a streaming fashion.

        For large tables, consider using `apply_dask` for distributed execution.
        """
        scan = self._table.spiral.scan(self._projection, where=self._where)

        with self._table.txn() as txn:
            txn.writeback(
                scan,
                partition_size_bytes=partition_size_bytes,
                batch_readahead=batch_readahead,
            )

    # TODO(marko): Need to figure out this sharding with key space index in places.
    #   We could compute on-demand instead of requiring a resource.
    def apply_dask(
        self, *, index: Optional["KeySpaceIndex"] = None, partition_size_bytes: int | None = None, **kwargs
    ) -> None:
        """Use distributed Dask to apply the enrichment. Requires `dask[distributed]` to be installed.

        If "address" of an existing Dask cluster is not provided in `kwargs`, a local cluster will be created.

        IMPORTANT: Dask execution has some limitations, e.g. UDFs are not currently supported. These limitations
        usually manifest as serialization errors when Dask workers attempt to serialize the state. If you are
        encountering such issues, consider splitting the enrichment into UDF-only derivation that will be
        executed in a streaming fashion, followed by a Dask enrichment for the rest of the computation.
        If that is not possible, please reach out to the support for assistance.

        Args:
            index: Optional key space index to use for sharding the enrichment.
                If not provided, the table's default sharding will be used.
            **kwargs: Additional keyword arguments to pass to `dask.distributed.Client`
                such as `address` to connect to an existing cluster.
        """
        try:
            from dask.distributed import Client
        except ImportError:
            raise ImportError("dask is not installed, please install dask[distributed] to use this feature.")

        # Connect before doing any work.
        dask_client = Client(**kwargs)

        # Start a transaction BEFORE the planning scan.
        tx = self._table.txn()
        plan_scan = self._table.spiral.scan(self._projection, where=self._where)

        # Determine the "tasks". Use the index if provided.
        shards = plan_scan.shards()
        if index is not None:
            # TODO(marko): This will use index's asof automatically.
            shards = self._table.spiral.internal.compute_shards(index.core)

        # Partially bind the enrichment function.
        _compute = partial(
            _enrichment_task,
            settings_dict=self._table.spiral.config.model_dump(),
            state_json=plan_scan.core.scan_state().to_json(),
            output_table_id=self._table.table_id,
            partition_size_bytes=partition_size_bytes,
        )
        enrichments = dask_client.map(_compute, shards)

        logger.info(f"Applying enrichment with {len(shards)} shards. Follow progress at {dask_client.dashboard_link}")
        for result in dask_client.gather(enrichments):
            result: EnrichmentTaskResult
            tx.include(result.ops)

        if tx.is_empty():
            logger.warning("Transaction not committed. No rows were read for enrichment.")
            return

        tx.commit()


@dataclasses.dataclass
class EnrichmentTaskResult:
    ops: list[Operation]

    def __getstate__(self):
        return {"ops": [op.to_json() for op in self.ops]}

    def __setstate__(self, state):
        self.ops = [Operation.from_json(op_json) for op_json in state["ops"]]


# NOTE(marko): This function must be picklable!
def _enrichment_task(
    shard: Shard, *, settings_dict, state_json, output_table_id, partition_size_bytes: int | None
) -> EnrichmentTaskResult:
    # Returns operations that can be included in a transaction.
    from spiral import Scan, Spiral
    from spiral.core.table import ScanState
    from spiral.settings import Settings

    settings: Settings = Settings.model_validate(settings_dict)
    sp = Spiral(config=settings)
    state = ScanState.from_json(state_json)
    task_scan = Scan(sp, sp.core.load_scan(state))
    table = sp.table(output_table_id)

    task_tx = table.txn()
    task_tx.writeback(task_scan, key_range=shard.key_range, partition_size_bytes=partition_size_bytes)
    return EnrichmentTaskResult(ops=task_tx.take())
