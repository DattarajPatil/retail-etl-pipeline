"""Generates the 5 retail source files: 2 CSV, 2 Parquet, 1 pipe-delimited TXT.
Some rows are deliberately dirty (duplicates, bad dates, blanks, odd casing) so the
refined layer rules have something to catch.
Run: pip install pandas pyarrow ; python generate_sample_data.py"""
import random, pathlib
from datetime import date, timedelta
import pandas as pd

random.seed(2026)
out = pathlib.Path(__file__).parent / "sample"
for d in ("sales", "customers", "products", "stores", "inventory"):
    (out / d).mkdir(parents=True, exist_ok=True)

# ---------------- STORES (parquet) ----------------
S = [("S01","Pune Central","Pune","Maharashtra","West","2018-04-12"),
     ("S02","Mumbai Andheri","Mumbai","Maharashtra","West","2017-09-03"),
     ("S03","Nagpur Civil Lines","Nagpur","Maharashtra","West","2020-01-15"),
     ("S04","Delhi Saket","Delhi","Delhi","North","2019-06-21"),
     ("S05","Gurugram Sector 29","Gurugram","Haryana","North","2021-03-10"),
     ("S06","Bengaluru Indiranagar","Bengaluru","Karnataka","South","2016-11-20"),
     ("S07","Hyderabad Madhapur","Hyderabad","Telangana","South","2019-12-05"),
     ("S08","Chennai T Nagar","Chennai","Tamil Nadu","South","2018-08-30"),
     ("S09","Kolkata Salt Lake","Kolkata","West Bengal","East","2022-02-14"),
     ("S10","Ahmedabad Navrangpura","Ahmedabad","Gujarat","West","2021-10-01")]
stores = pd.DataFrame(S, columns=["store_id","store_name","city","state","region","open_date"])
stores["open_date"] = pd.to_datetime(stores["open_date"]).dt.date
stores.to_parquet(out / "stores/stores.parquet", index=False)

# ---------------- PRODUCTS (parquet) ----------------
P = [("Basmati Rice 5kg","Grocery","India Gate",420),("Toor Dal 1kg","Grocery","Tata Sampann",160),
     ("Aashirvaad Atta 10kg","Grocery","Aashirvaad",470),("Sunflower Oil 1L","Grocery","Fortune",150),
     ("Sugar 1kg","Grocery","Madhur",48),("Iodised Salt 1kg","Grocery","Tata",28),
     ("Turmeric Powder 200g","Grocery","Everest",72),("Red Chilli Powder 200g","Grocery","MDH",85),
     ("Tea Leaves 500g","Beverages","Tata Tea",255),("Instant Coffee 100g","Beverages","Nescafe",310),
     ("Mango Juice 1L","Beverages","Real",110),("Cola 2L","Beverages","Thums Up",95),
     ("Packaged Water 1L","Beverages","Bisleri",20),("Energy Drink 250ml","Beverages","Red Bull",125),
     ("Bath Soap 4pk","Personal Care","Dove",190),("Shampoo 340ml","Personal Care","Clinic Plus",245),
     ("Toothpaste 200g","Personal Care","Colgate",110),("Face Wash 100ml","Personal Care","Himalaya",150),
     ("Deodorant 150ml","Personal Care","Fogg",199),("Hand Wash 750ml","Personal Care","Dettol",135),
     ("Detergent Powder 2kg","Household","Surf Excel",385),("Dish Wash Liquid 750ml","Household","Vim",185),
     ("Floor Cleaner 1L","Household","Lizol",210),("Toilet Cleaner 500ml","Household","Harpic",99),
     ("Garbage Bags 30pk","Household","Scotch-Brite",120),("Tissue Roll 4pk","Household","Origami",140),
     ("Chips 150g","Snacks","Lays",50),("Namkeen 400g","Snacks","Haldirams",120),
     ("Biscuits 600g","Snacks","Parle-G",65),("Chocolate Bar 55g","Snacks","Cadbury",60),
     ("Instant Noodles 4pk","Snacks","Maggi",56),("Cornflakes 475g","Snacks","Kelloggs",215),
     ("Full Cream Milk 1L","Dairy","Amul",68),("Butter 500g","Dairy","Amul",285),
     ("Cheese Slices 200g","Dairy","Britannia",130),("Curd 400g","Dairy","Mother Dairy",45),
     ("Paneer 200g","Dairy","Amul",95),("Eggs 12pk","Dairy","Keggs",84),
     ("Notebook 6pk","Stationery","Classmate",270),("Ball Pens 10pk","Stationery","Cello",90)]
rows = []
for i, (name, cat, brand, mrp) in enumerate(P, 1):
    mrp = float(mrp); cost = round(mrp * random.uniform(0.68, 0.85), 2)
    rows.append((f"P{i:03d}", f"SKU-{cat[:3].upper()}-{i:04d}", name, cat, brand, cost, mrp))
products = pd.DataFrame(rows, columns=["product_id","sku","product_name","category","brand","cost_price","mrp"])
# dirty rows for the refined layer: duplicate product, mrp below cost, lowercase category
products = pd.concat([products,
    products.iloc[[2]],
    pd.DataFrame([("P041","SKU-TST-0041","Test Item Bad Price","grocery","acme",100.0,80.0)], columns=products.columns)],
    ignore_index=True)
products.to_parquet(out / "products/products.parquet", index=False)
good = products[(products.mrp >= products.cost_price)].drop_duplicates("product_id")
price = dict(zip(good.product_id, good.mrp))

# ---------------- CUSTOMERS (csv) ----------------
first = ["Aarav","Vivaan","Aditya","Sai","Arjun","Rohan","Ishaan","Kabir","Rahul","Amit","Priya","Ananya",
         "Diya","Isha","Kavya","Meera","Neha","Pooja","Riya","Sneha","Shruti","Tanvi","Vikram","Suresh","Nikhil"]
last = ["Patil","Sharma","Deshmukh","Kulkarni","Joshi","Gupta","Reddy","Iyer","Nair","Singh","Khan","Mehta",
        "Shah","Banerjee","Das","Chavan","Jadhav","Pawar","More","Kale"]
cities = stores[["city","state"]].values.tolist()
cust = []
for i in range(1, 301):
    f, l = random.choice(first), random.choice(last)
    c, st = random.choice(cities)
    d = date(2022, 1, 1) + timedelta(days=random.randint(0, 1400))
    cust.append([f"C{i:04d}", f, l, f"{f}.{l}{random.randint(1,99)}@example.com".lower(),
                 f"+91-{random.randint(70000,99999)}{random.randint(10000,99999)}", c, st, d.isoformat()])
cust = pd.DataFrame(cust, columns=["customer_id","first_name","last_name","email","phone","city","state","signup_date"])
# dirty rows
cust.loc[3, "email"] = "not-an-email"
cust.loc[7, "email"] = ""
cust.loc[11, "first_name"] = "  rahul "; cust.loc[11, "last_name"] = "SHARMA"
cust.loc[15, "phone"] = "(020) 2567 1234"
cust.loc[19, "city"] = "PUNE"
cust = pd.concat([cust, cust.iloc[[20, 21]]], ignore_index=True)   # duplicates
cust.to_csv(out / "customers/customers.csv", index=False)
cust_ids = [f"C{i:04d}" for i in range(1, 301)]

# ---------------- SALES (csv) ----------------
pids = list(price)
sids = stores.store_id.tolist()
sales = []
t = 1
start, end = date(2026, 9, 1), date(2026, 11, 16)
ndays = (end - start).days
for _ in range(6000):
    d = start + timedelta(days=random.randint(0, ndays))
    wk = 1.3 if d.weekday() >= 5 else 1.0
    for _ in range(random.choice([1, 1, 2, 3])):          # 1-3 lines per bill
        pid = random.choice(pids)
        qty = max(1, int(random.choice([1,1,1,2,2,3,4,5]) * wk))
        up = round(price[pid] * random.uniform(0.92, 1.0), 2)
        disc = random.choice(["", "", "0", "0", str(round(up*qty*0.05, 2)), str(round(up*qty*0.10, 2))])
        sales.append([f"T{t:06d}", d.isoformat(), random.choice(sids), random.choice(cust_ids), pid,
                      qty, up, disc, random.choice(["UPI","UPI","CARD","CASH","WALLET"])])
        t += 1
sales = pd.DataFrame(sales, columns=["txn_id","txn_date","store_id","customer_id","product_id","qty","unit_price","discount","payment_mode"])
n = len(sales)
idx = random.sample(range(n), 120)
sales.loc[idx[:30], "store_id"]    = sales.loc[idx[:30], "store_id"].str.lower()          # casing
sales.loc[idx[30:50], "product_id"] = " " + sales.loc[idx[30:50], "product_id"] + " "    # whitespace
sales.loc[idx[50:60], "payment_mode"] = sales.loc[idx[50:60], "payment_mode"].str.lower()
sales.loc[idx[60:70], "qty"] = 0                                                         # invalid qty
sales.loc[idx[70:75], "qty"] = -1
sales.loc[idx[75:80], "unit_price"] = -10                                                # invalid price
sales.loc[idx[80:90], "txn_date"] = sales.loc[idx[80:90], "txn_date"].str.replace("-", "/")  # bad date format
sales.loc[idx[90:95], "txn_id"] = ""                                                     # missing key
sales = pd.concat([sales, sales.sample(60, random_state=1)], ignore_index=True)          # duplicate txns
sales.to_csv(out / "sales/sales_transactions.csv", index=False)

# ---------------- STORE INVENTORY (pipe-delimited txt) ----------------
inv = []
for snap in ("2026-11-09", "2026-11-16"):
    for s in sids:
        for p in good.product_id:
            inv.append([s, p, random.choice([0, 3, 8, 15, 40, 90, 150, 250, 400]), snap])
inv = pd.DataFrame(inv, columns=["store_id","product_id","stock_qty","snapshot_date"])
inv.loc[5, "stock_qty"] = -4                                                              # invalid
inv = pd.concat([inv, inv.iloc[[10, 11, 12]]], ignore_index=True)                         # duplicates
inv.to_csv(out / "inventory/store_inventory.txt", sep="|", index=False)

for name, df in [("stores", stores), ("products", products), ("customers", cust), ("sales", sales), ("inventory", inv)]:
    print(f"{name:10s} {len(df):6d} rows")
