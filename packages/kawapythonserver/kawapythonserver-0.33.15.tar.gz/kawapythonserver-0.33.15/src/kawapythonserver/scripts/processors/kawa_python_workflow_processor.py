import pandas as pd
import pyarrow as pa

from .kawa_action_processor import ActionProcessor
from ...server.kawa_directory_manager import KawaDirectoryManager
from ...server.kawa_metadata import Metadata


class PythonWorkflowProcessor(ActionProcessor):
    def __init__(self,
                 job_id: str,
                 dataset_count: int,
                 kawa_directory_manager: KawaDirectoryManager,
                 metadata: Metadata):
        self.job_id = job_id
        self.metadata = metadata
        self.dataset_count = dataset_count
        self.kawa_directory_manager: KawaDirectoryManager = kawa_directory_manager

    def retrieve_data(self) -> list[pd.DataFrame]:
        dataframes: list[pd.DataFrame] = []
        for dataset_index in range(0, self.dataset_count):
            arrow_table = self.kawa_directory_manager.read_table(self.job_id, dataset_index)
            dataframes.append(arrow_table.to_pandas())
        return dataframes

    def load(self, df: pd.DataFrame = pd.DataFrame(), json: str = '{}'):
        arrow_table = pa.Table.from_pandas(df)
        self.kawa_directory_manager.write_output(self.job_id, arrow_table)

    def need_defined_outputs(self) -> bool:
        return self.metadata.outputs
