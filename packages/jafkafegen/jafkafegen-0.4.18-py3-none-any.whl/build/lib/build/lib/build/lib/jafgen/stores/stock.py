from typing import Any

from jafgen.stores.supply import StorageKeepingUnit as SKU
from jafgen.stores.supply import Supply, SupplyId


class Stock:
    stock: dict[SKU, list[Supply]] = {}

    @classmethod
    def update(cls, stock_list: list[Supply]):
        for supply in stock_list:
            skus = supply.skus
            for sku in skus:
                if sku not in cls.stock:
                    cls.stock[sku] = []
                cls.stock[sku].append(supply)

    @classmethod
    def to_dict(cls) -> list[dict[str, Any]]:
        all_items: list[dict[str, Any]] = []
        for key in cls.stock:
            all_items += [item.to_dict(key) for item in cls.stock[key]]
        return all_items

Stock.update(
    [
        Supply(
            id=SupplyId("SUP-001"),
            name="compostable cutlery - knife",
            cost=0.07,
            perishable=False,
            skus=[SKU("JAF-001"), SKU("JAF-002"), SKU("JAF-003"), SKU("JAF-004"), SKU("JAF-005")],
        ),
        Supply(
            id=SupplyId("SUP-002"),
            name="cutlery - fork",
            cost=0.07,
            perishable=False,
            skus=[SKU("JAF-001"), SKU("JAF-002"), SKU("JAF-003"), SKU("JAF-004"), SKU("JAF-005")],
        ),
        Supply(
            id=SupplyId("SUP-003"),
            name="serving boat",
            cost=0.11,
            perishable=False,
            skus=[SKU("JAF-001"), SKU("JAF-002"), SKU("JAF-003"), SKU("JAF-004"), SKU("JAF-005")],
        ),
        Supply(
            id=SupplyId("SUP-004"),
            name="napkin",
            cost=0.04,
            perishable=False,
            skus=[SKU("JAF-001"), SKU("JAF-002"), SKU("JAF-003"), SKU("JAF-004"), SKU("JAF-005")],
        ),
        Supply(
            id=SupplyId("SUP-005"),
            name="16oz compostable clear cup",
            cost=0.13,
            perishable=False,
            skus=[SKU("BEV-001"), SKU("BEV-002"), SKU("BEV-003"), SKU("BEV-004"), SKU("BEV-005")],
        ),
        Supply(
            id=SupplyId("SUP-006"),
            name="16oz compostable clear lid",
            cost=0.04,
            perishable=False,
            skus=[SKU("BEV-001"), SKU("BEV-002"), SKU("BEV-003"), SKU("BEV-004"), SKU("BEV-005")],
        ),
        Supply(
            id=SupplyId("SUP-007"),
            name="biodegradable straw",
            cost=0.13,
            perishable=False,
            skus=[SKU("BEV-001"), SKU("BEV-002"), SKU("BEV-003"), SKU("BEV-004"), SKU("BEV-005")],
        ),
        Supply(
            id=SupplyId("SUP-008"), name="chai mix", cost=0.98, perishable=True, skus=[SKU("BEV-002")]
        ),
        Supply(
            id=SupplyId("SUP-009"),
            name="bread",
            cost=0.33,
            perishable=True,
            skus=[SKU("JAF-001"), SKU("JAF-002"), SKU("JAF-003"), SKU("JAF-004"), SKU("JAF-005")],
        ),
        Supply(
            id=SupplyId("SUP-010"),
            name="cheese",
            cost=0.2,
            perishable=True,
            skus=[SKU("JAF-002"), SKU("JAF-003"), SKU("JAF-004"), SKU("JAF-005")],
        ),
        Supply(
            id=SupplyId("SUP-011"), name="nutella", cost=0.46, perishable=True, skus=[SKU("JAF-001")]
        ),
        Supply(
            id=SupplyId("SUP-012"), name="banana", cost=0.13, perishable=True, skus=[SKU("JAF-001")]
        ),
        Supply(
            id=SupplyId("SUP-013"), name="beef stew", cost=1.69, perishable=True, skus=[SKU("JAF-002")]
        ),
        Supply(
            id=SupplyId("SUP-014"),
            name="lamb and pork bratwurst",
            cost=2.34,
            perishable=True,
            skus=[SKU("JAF-003")],
        ),
        Supply(
            id=SupplyId("SUP-015"),
            name="house-pickled cabbage sauerkraut",
            cost=0.43,
            perishable=True,
            skus=[SKU("JAF-003")],
        ),
        Supply(
            id=SupplyId("SUP-016"), name="mustard", cost=0.07, perishable=True, skus=[SKU("JAF-003")]
        ),
        Supply(
            id=SupplyId("SUP-017"),
            name="pulled pork",
            cost=2.15,
            perishable=True,
            skus=[SKU("JAF-004")],
        ),
        Supply(
            id=SupplyId("SUP-018"), name="pineapple", cost=0.26, perishable=True, skus=[SKU("JAF-004")]
        ),
        Supply(
            id=SupplyId("SUP-019"), name="melon", cost=0.33, perishable=True, skus=[SKU("JAF-005")]
        ),
        Supply(
            id=SupplyId("SUP-020"),
            name="minced beef",
            cost=1.24,
            perishable=True,
            skus=[SKU("JAF-005")],
        ),
        Supply(
            id=SupplyId("SUP-021"),
            name="ghost pepper sauce",
            cost=0.2,
            perishable=True,
            skus=[SKU("JAF-004")],
        ),
        Supply(
            id=SupplyId("SUP-022"), name="mango", cost=0.32, perishable=True, skus=[SKU("BEV-001")]
        ),
        Supply(
            id=SupplyId("SUP-023"), name="tangerine", cost=0.2, perishable=True, skus=[SKU("BEV-001")]
        ),
        Supply(
            id=SupplyId("SUP-024"), name="oatmilk", cost=0.11, perishable=True, skus=[SKU("BEV-002")]
        ),
        Supply(
            id=SupplyId("SUP-025"),
            name="whey protein",
            cost=0.36,
            perishable=True,
            skus=[SKU("BEV-002")],
        ),
        Supply(
            id=SupplyId("SUP-026"),
            name="coffee",
            cost=0.52,
            perishable=True,
            skus=[SKU("BEV-003"), SKU("BEV-004")],
        ),
        Supply(
            id=SupplyId("SUP-027"),
            name="french vanilla syrup",
            cost=0.72,
            perishable=True,
            skus=[SKU("BEV-003")],
        ),
        Supply(id=SupplyId("SUP-028"), name="kiwi", cost=0.2, perishable=True, skus=[SKU("BEV-005")]),
        Supply(id=SupplyId("SUP-029"), name="lime", cost=0.13, perishable=True, skus=[SKU("BEV-005")]),
    ]
)
