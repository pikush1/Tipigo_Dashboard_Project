from strategies.hapoalim_Strategy import BankAStrategy
from strategies.tipigo_Strategy import BankBStrategy

def MappingStrategy(file_path):
    filename = file_path.lower()
    if "hapoalim" in filename:
        return BankAStrategy()
    elif "interactive" in filename:
        return "interactive"
    else:
        return None