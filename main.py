from strategy_selector import get_strategy

def main(file_path):
    strategy = get_strategy(file_path)
    if not strategy:
        raise ValueError(f"No strategy found for file: {file_path}")
    
    result = strategy.run(file_path)
    return result


if __name__ == "__main__":
    file_path = "data/tipigo_system_data.xlsx"
    result = main(file_path)
    print(result)
