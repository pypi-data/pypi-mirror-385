import csv
import os
from typing import Any
from datetime import time
from rich.progress import track
from loguru import logger
from jafgen.customers.customers import Customer, CustomerId
from jafgen.customers.order import Order
from jafgen.customers.tweet import Tweet
from jafgen.stores.inventory import Inventory
from jafgen.stores.market import Market
from jafgen.stores.stock import Stock
from jafgen.stores.store import Store
from jafgen.time import (
    Day,
    DayHoursOfOperation,
    WeekHoursOfOperation,
)

T_OPEN_WD = time(hour=15)
T_CLOSE_WD = time(hour=21)
T_OPEN_WE = time(hour=14)
T_CLOSE_WE = time(hour=22)

class Simulation:
    def __init__(self, years: int, days: int, prefix: str):
        logger.info(f"Starting simulation for {years} years and {days} days")
        self.years = years
        self.days = days
        self.scale = 1000
        self.prefix = prefix
        self.stores = [
            # name | popularity | opened | TAM | tax
            ("Philadelphia", 0.85, 0, 9 * self.scale, 0.06),
            ("Brooklyn", 0.95, 192, 14 * self.scale, 0.04),
            ("Chicago", 0.92, 605, 12 * self.scale, 0.0625),
            ("San Francisco", 0.87, 615, 11 * self.scale, 0.075),
            ("New Orleans", 0.92, 920, 8 * self.scale, 0.04),
            ("Los Angeles", 0.87, 1107, 8 * self.scale, 0.08),
            ("Alingsås", 0.9, 100, 8 * self.scale, 0.08),
            ("Borås", 0.75, 200, 15 * self.scale, 0.08),
            ("Malmö", 0.99, 250, 20 * self.scale, 0.08),
            ("Göteborg", 0.8, 120, 50 * self.scale, 0.08),
            ("Värnamo", 0.5, 120, 20 * self.scale, 0.08),
            ("Stockholm", 0.8, 0, 100 * self.scale, 0.08),
            ("Leipzig", 0.9, 100, 120 * self.scale, 0.08),
            ("Madrid", 0.9, 100, 210 * self.scale, 0.08),
            ("Berlin", 0.8, 200, 190 * self.scale, 0.08),
        ]
        self.markets: list[Market] = []
        self.customers: dict[CustomerId, Customer] = {}
        self.orders: list[Order] = []
        self.tweets: list[Tweet] = []
        self.sim_days = 365 * self.years + self.days


    def init_markets(self):
        logger.info(f"Simulating {len(self.stores)} stores")
        for store_name, popularity, opened_date, market_size, tax in self.stores:
            logger.info(f"Creating store {store_name} opened {opened_date} with TAM {market_size}")
            m = Market(
                Store(
                    name=store_name,
                    base_popularity=popularity,
                    hours_of_operation=WeekHoursOfOperation(
                        week_days=DayHoursOfOperation(opens_at=T_OPEN_WD, closes_at=T_CLOSE_WD),
                        weekends=DayHoursOfOperation(opens_at=T_OPEN_WE, closes_at=T_CLOSE_WE),
                    ),
                    opened_day=Day(opened_date),
                    tax_rate=tax,
                ),
                num_customers=market_size,
            )
            self.markets.append(m)

    def run_simulation(self):
        self.init_markets()
        for i in track(
            range(self.sim_days), description=f"🥪 Pressing {self.sim_days} days of fresh jaffles..."
        ):
            for market in self.markets:
                day = Day(i)
                for order, tweet in market.sim_day(day):
                    if order:
                        self.orders.append(order)
                        if order.customer.id not in self.customers:
                            self.customers[order.customer.id] = order.customer
                    if tweet:
                        self.tweets.append(tweet)

    def save_results(self) -> None:
        stock: Stock = Stock()
        inventory: Inventory = Inventory()
        entities: dict[str, list[dict[str, Any]]] = {
            "customers": [customer.to_dict() for customer in self.customers.values()],
            "orders": [order.to_dict() for order in self.orders],
            "items": [item.to_dict() for order in self.orders for item in order.items],
            "stores": [market.store.to_dict() for market in self.markets],
            "supplies": stock.to_dict(),
            "products": inventory.to_dict(),
            "tweets": [tweet.to_dict() for tweet in self.tweets],
        }

        if not os.path.exists("./jaffle-data"):
            os.makedirs("./jaffle-data")
        for entity, data in track(
            entities.items(), description="🚚 Delivering jaffles..."
        ):
            if data:
                file = f"./jaffle-data/{self.prefix}_{entity}.csv"
                writer = csv.DictWriter(open(file, "w", newline=""), fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
