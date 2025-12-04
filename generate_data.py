import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_ecommerce_search_logs(n_rows: int = 800, days_back: int = 30) -> pd.DataFrame:
    rng = np.random.default_rng(42)

    queries = [
        "running shoes", "sneakers", "winter jacket", "jeans", "t shirt",
        "lipstick", "moisturizer", "perfume",
        "gaming mouse", "wireless keyboard", "earbuds", "smart watch",
        "coffee maker", "blender", "vacuum cleaner",
        "dog food", "cat litter", "yoga mat"
    ]

    categories = {
        "running shoes": "Sportswear",
        "sneakers": "Footwear",
        "winter jacket": "Apparel",
        "jeans": "Apparel",
        "t shirt": "Apparel",
        "lipstick": "Beauty",
        "moisturizer": "Beauty",
        "perfume": "Beauty",
        "gaming mouse": "Electronics",
        "wireless keyboard": "Electronics",
        "earbuds": "Electronics",
        "smart watch": "Electronics",
        "coffee maker": "Home Appliances",
        "blender": "Home Appliances",
        "vacuum cleaner": "Home Appliances",
        "dog food": "Pet Supplies",
        "cat litter": "Pet Supplies",
        "yoga mat": "Sportswear",
    }

    price_ranges = {
        "Sportswear": (40, 180),
        "Footwear": (50, 200),
        "Apparel": (20, 150),
        "Beauty": (8, 80),
        "Electronics": (25, 250),
        "Home Appliances": (35, 300),
        "Pet Supplies": (10, 120),
    }

    base_time = datetime.now() - timedelta(days=days_back)

    records = []
    for i in range(n_rows):
        query = random.choice(queries)
        category = categories[query]

        # Some noisy variations of queries (simulating typos / variants)
        if random.random() < 0.1:
            noisy_variants = {
                "running shoes": "runing shoes",
                "sneakers": "sneeker",
                "winter jacket": "winter jaket",
                "t shirt": "t-shirt",
                "earbuds": "ear buds",
            }
            normalized_query = query
            query = noisy_variants.get(query, query)
        else:
            normalized_query = query

        timestamp = base_time + timedelta(
            days=random.randint(0, days_back),
            minutes=random.randint(0, 1440)
        )

        session_id = f"S{rng.integers(100000, 999999)}"
        user_id = rng.integers(1000, 5000)

        # Basic behavior model:
        # - higher click probability for electronics & beauty (better merchandising)
        base_click_prob = {
            "Electronics": 0.8,
            "Beauty": 0.75,
            "Sportswear": 0.7,
            "Footwear": 0.7,
            "Apparel": 0.65,
            "Home Appliances": 0.6,
            "Pet Supplies": 0.6,
        }[category]

        # Some queries are systematically worse (e.g., due to poor search config)
        bad_queries = ["t shirt", "blender", "cat litter"]
        if normalized_query in bad_queries:
            click_prob = base_click_prob - 0.2
        else:
            click_prob = base_click_prob

        clicked = rng.random() < max(min(click_prob, 0.95), 0.05)
        click_position = rng.integers(1, 10) if clicked else None

        # Purchase model: only if clicked
        if clicked:
            base_purchase_prob = 0.22
            # better converting categories
            if category in ["Beauty", "Pet Supplies"]:
                base_purchase_prob += 0.08
            purchased = rng.random() < base_purchase_prob
        else:
            purchased = False

        # Price & revenue
        price_low, price_high = price_ranges[category]
        price = round(rng.uniform(price_low, price_high), 2) if purchased else None
        revenue = price if purchased else 0.0

        # Sometimes zero-result searches (no_result = 1)
        no_result = 1 if rng.random() < 0.05 else 0
        if no_result:
            clicked = False
            purchased = False
            click_position = None
            revenue = 0.0
            price = None

        product_id = f"P{rng.integers(10_000, 99_999)}" if purchased else None

        records.append({
            "timestamp": timestamp,
            "session_id": session_id,
            "user_id": user_id,
            "query": query,
            "normalized_query": normalized_query,
            "category": category,
            "clicked": int(clicked),
            "click_position": click_position,
            "purchased": int(purchased),
            "product_id": product_id,
            "price": price,
            "revenue": revenue,
            "no_result": no_result,
        })

    df = pd.DataFrame(records)
    return df


if __name__ == "__main__":
    df = generate_ecommerce_search_logs()
    df.to_csv("ecommerce_search_logs.csv", index=False)
    print("Generated ecommerce_search_logs.csv with", len(df), "rows")
