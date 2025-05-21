from abc import ABC, abstractmethod
import pandas as pd

class MappingStrategy(ABC):
    @abstractmethod
    def run(self, file_path: str) -> pd.DataFrame:
        """Handles the full process for this strategy."""
        pass

    @abstractmethod
    def load(self, file_path: str) -> pd.DataFrame:
        """Reads file into a DataFrame."""
        pass

    def map_to_uniform(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Optional: only used by strategies that require mapping."""
        return raw_data

    @abstractmethod
    def pipeline(self, data: pd.DataFrame) -> pd.DataFrame:
        """Final transformation step applied to mapped or raw data."""
        pass
