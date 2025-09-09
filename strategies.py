from abc import ABC, abstractmethod
from Tipigo_Dashboard_Project.actions.interactive_actions import InteractiveActions
from Tipigo_Dashboard_Project.actions.tipigo_actions import TipigoActions
from Tipigo_Dashboard_Project.create_csv import create_csv_hapoalim, create_csv_interactive
from Tipigo_Dashboard_Project.create_pdf import create_pdf_hapoalim, create_pdf_interactive
from Tipigo_Dashboard_Project.split_system_data import take_stock_prices, take_benchmark
from Tipigo_Dashboard_Project.actions.hapoalim_actions import HapoalimActions


class DataProcessingStrategy(ABC):
    @abstractmethod
    def run(self, **kwargs):
        pass


class HapoalimStrategy(DataProcessingStrategy):
    def run(self, **kwargs):
        raw_data = kwargs.get("raw_data")
        system_file = kwargs.get("system_file")
        input_benchmarks = kwargs.get("input_benchmarks")
        initial_cash = kwargs.get("initial_cash")
        risk_free_rate_file = kwargs.get("risk_free_rate_file")

        hapoalim = HapoalimActions()
        raw = hapoalim.load(raw_data)
        mapped_data = hapoalim.map_to_uniform(raw)
        stock_prices = take_stock_prices(system_file)
        benchmark_data = take_benchmark(stock_prices, input_benchmarks)
        final_data, total_assets = hapoalim.pipeline(mapped_data, stock_prices, initial_cash, risk_free_rate_file)
        merged_data = final_data.merge(benchmark_data, on="Date", how="left")

        total_monthly = hapoalim.create_monthly(merged_data, input_benchmarks)
        create_pdf_hapoalim(merged_data, input_benchmarks)
        create_csv_hapoalim(merged_data, total_assets, total_monthly, input_benchmarks)

        return (merged_data, total_assets)


class InteractiveStrategy(DataProcessingStrategy):
    def run(self, **kwargs):
        risk_free_rate_file = kwargs.get("risk_free_rate_file")
        input_benchmarks = kwargs.get("input_benchmarks")
        initial_cash = kwargs.get("initial_cash")
        raw_data = kwargs.get("raw_data")
        interactive = InteractiveActions()

        total_assets_monthly = interactive.pipeline(raw_data, input_benchmarks, initial_cash, risk_free_rate_file)
        create_pdf_interactive(total_assets_monthly, input_benchmarks)
        create_csv_interactive(total_assets_monthly, input_benchmarks)

        return (total_assets_monthly)


class TipigoStrategy(DataProcessingStrategy):
    def run(self, **kwargs):
        raw_data = kwargs.get("raw_data")
        tipigo = TipigoActions()

        raw = tipigo.load(raw_data)
        final_data = tipigo.pipeline(raw)
        return (final_data)