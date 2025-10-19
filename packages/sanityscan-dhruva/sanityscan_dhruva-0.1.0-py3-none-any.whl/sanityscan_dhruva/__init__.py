
from typing import Optional
import os, pandas as pd
from sklearn.model_selection import train_test_split

def report(csv_path: str, target: Optional[str] = None, n: int = 5) -> None:
    df = pd.read_csv(csv_path)
    print(f"Rows: {len(df)}  Cols: {df.shape[1]}")
    print(df.head(n))
    if target and target in df:
        vc = df[target].value_counts(dropna=False)
        print("Class balance:", (vc/len(df)).round(3).to_dict())

def _can_stratify(series: pd.Series, frac: float) -> bool:
    """True if every class would contribute at least 1 sample to a split of size `frac`."""
    if series is None or frac <= 0:
        return False
    vc = series.value_counts(dropna=False)
    return (vc.min() * frac) >= 1.0

def split_csv(csv_path: str, out: str = "splits", target: Optional[str] = None,
              test_size: float = 0.2, val_size: float = 0.1, random_state: int = 42) -> None:
    os.makedirs(out, exist_ok=True)
    df = pd.read_csv(csv_path)

    # Decide stratification for TEST
    strat_test = None
    if target and target in df and df[target].nunique() <= 50 and _can_stratify(df[target], test_size):
        strat_test = df[target]

    train, test = train_test_split(
        df, test_size=test_size, random_state=random_state, stratify=strat_test
    )

    # Decide stratification for VAL (fraction relative to TRAIN)
    rel_val = val_size / (1 - test_size)
    strat_val = None
    if target and target in train and train[target].nunique() <= 50 and _can_stratify(train[target], rel_val):
        strat_val = train[target]

    train, val = train_test_split(
        train, test_size=rel_val, random_state=random_state, stratify=strat_val
    )

    train.to_csv(f"{out}/train.csv", index=False)
    val.to_csv(f"{out}/val.csv", index=False)
    test.to_csv(f"{out}/test.csv", index=False)
    print(f"Wrote {out}/train.csv, {out}/val.csv, {out}/test.csv")
