from strategies.Bank_A_Strategy import BankAStrategy
from strategies.Bank_B_Strategy import BankBStrategy

def get_strategy(file_path):
    filename = file_path.lower()
    if "hapoalim" in filename:
        return BankAStrategy()
    elif "tipigo" in filename:
        return BankBStrategy()
    else:
        return None