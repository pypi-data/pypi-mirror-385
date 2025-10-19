import sf_quant.data as sfd
import datetime as dt
import polars as pl

assets = sfd.load_assets(
    start=dt.date(2025, 1, 1),
    end=dt.date(2025, 12, 31),
    columns=['date', 'barrid', 'ticker', 'in_universe'],
    in_universe=True
)

print(assets)