from abc import ABC, abstractmethod
import pandas as pd

class MappingStrategy(ABC):
    @abstractmethod
    def map_to_uniform(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        pass

class BankAMapping(MappingStrategy):
    def map_to_uniform(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        column_mapping = {
            4: "Stock_symbol",        
            6: "Stock_full_name", 
            8: "Action",      
            9: "Date",       
            11: "Quantity",
            12: "Transaction_rate",
            13: "Gross_transaction_rate",
            16: "Net_transaction_amount",
            18: "Nominal_profit_ILS",
            25: "Real_profit_ILS",
            19: "Tax_ILS_amount",
            20: "Tax_used_amount",
            21: "Transaction_fee_ILS",
            22: "Exchange_rate",
            26: "Tax_ILS_percentage",
            27: "Tax_USD_percentage",
            28: "Percentage_transaction_fee",
            29: "Stock_exchange"
        }
        mapped_data = raw_data.rename(
            columns={raw_data.columns[i]: column_mapping[i] for i in column_mapping}
        )
        mapped_data = mapped_data[list(column_mapping.values())]
        action_mapping = {
            "קניה": "Buy",
            "מכירה": "Sell",
            "העברה לזכות הפקדון": "Transfer to deposit",
            "הטבה חלוקת מניות": "Stock distribution benefit",
            "דיבידנד בתשלום": "Dividend"
        }
        mapped_data["Action"] = mapped_data["Action"].map(action_mapping)
        return mapped_data


