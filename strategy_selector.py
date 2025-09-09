from strategies import HapoalimStrategy, InteractiveStrategy, TipigoStrategy


def StrategySelector(file_path):
    filename = file_path.lower()
    if "hapoalim" in filename:
        return HapoalimStrategy()
    elif "interactive" in filename:
        return InteractiveStrategy()
    elif "tipigo" in filename:
        return TipigoStrategy()
    else:
        return None
