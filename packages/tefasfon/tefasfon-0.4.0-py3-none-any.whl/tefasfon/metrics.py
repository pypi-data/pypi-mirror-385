import numpy as np
import pandas as pd

from .utils import (
    get_metric_labels,
    get_localized_message,
    normalize_lang,
    is_dayfirst,
    RET_NAME
)

_FREQ_TO_PPY = {"D": 252, "B": 252, "W": 52, "M": 12, "Q": 4, "A": 1, "Y": 1}

def _infer_ppy(freq: str | None) -> int:
    if not freq:
        return 252
    return _FREQ_TO_PPY.get(str(freq).upper()[0], 252)

def _prep_series(
    df: pd.DataFrame,
    price_col: str = "Fiyat",
    date_col: str = "Tarih",
    sort: bool = True,
    lang: str = "tr",
) -> pd.Series:
    lng = normalize_lang(lang)

    if date_col not in df.columns or price_col not in df.columns:
        raise ValueError(
            get_localized_message("required_columns_missing", lng, date_col, price_col)
        )

    s = df[[date_col, price_col]].copy()

    if not pd.api.types.is_datetime64_any_dtype(s[date_col]):
        s[date_col] = pd.to_datetime(
            s[date_col],
            dayfirst=is_dayfirst(lng),
            errors="coerce"
        )

    s[price_col] = pd.to_numeric(s[price_col], errors="coerce")

    s = s.dropna()

    if sort:
        s = s.sort_values(date_col)

    return pd.Series(
        s[price_col].values,
        index=pd.DatetimeIndex(s[date_col].values),
        name=price_col
    )

def compute_returns(
    df: pd.DataFrame,
    price_col: str = "Fiyat",
    date_col: str = "Tarih",
    freq: str | None = None,
    method: str = "simple",
    lang: str = "tr",
) -> pd.Series:
    prices = _prep_series(df, price_col=price_col, date_col=date_col, lang=lang)

    prices = prices[prices > 0]

    if freq:
        prices = prices.resample(freq).last().dropna()

    rets = np.log(prices / prices.shift(1)) if method.lower() == "log" else prices.pct_change()
    return rets.dropna().rename(RET_NAME[normalize_lang(lang)])

def cumulative_return(returns: pd.Series, method: str = "simple") -> float:
    r = returns.dropna()
    if r.empty:
        return float("nan")
    return float(np.exp(r.sum()) - 1.0) if method.lower() == "log" else float((1.0 + r).prod() - 1.0)

def annualized_return(
    returns: pd.Series,
    periods_per_year: int | None = None,
    method: str = "simple",
    freq: str | None = None,
) -> float:
    r = returns.dropna()
    if r.empty:
        return float("nan")
    ppy = _infer_ppy(freq) if periods_per_year is None else periods_per_year
    n = len(r)
    if n == 0:
        return float("nan")
    if method.lower() == "log":
        years = n / ppy
        return float(np.exp(r.sum() / years) - 1.0) if years else float("nan")
    growth = (1 + r).prod()
    years = n / ppy
    return float(growth ** (1 / years) - 1.0) if years else float("nan")

def annualized_volatility(
    returns: pd.Series,
    periods_per_year: int | None = None,
    freq: str | None = None,
) -> float:
    r = returns.dropna()
    if r.empty:
        return float("nan")
    ppy = _infer_ppy(freq) if periods_per_year is None else periods_per_year
    return float(r.std(ddof=1) * np.sqrt(ppy))

def sharpe_ratio(
    returns: pd.Series,
    risk_free_annual: float = 0.0,
    periods_per_year: int | None = None,
    freq: str | None = None,
    method: str = "simple",
) -> float:
    ppy = _infer_ppy(freq) if periods_per_year is None else periods_per_year
    ann_ret = annualized_return(returns, ppy, method=method, freq=freq)
    ann_vol = annualized_volatility(returns, ppy, freq=freq)
    if pd.isna(ann_vol) or ann_vol == 0:
        return float("nan")
    return float((ann_ret - risk_free_annual) / ann_vol)

def compute_metrics(
    df: pd.DataFrame,
    price_col: str = "Fiyat",
    date_col: str = "Tarih",
    freq: str = "D",
    risk_free_annual: float = 0.0,
    periods_per_year: int | None = None,
    method: str = "simple",
    lang: str = "tr",
) -> pd.DataFrame:
    lng = normalize_lang(lang)
    labels = get_metric_labels(lng)

    rets = compute_returns(df, price_col=price_col, date_col=date_col, freq=freq, method=method, lang=lng)
    ppy = _infer_ppy(freq) if periods_per_year is None else periods_per_year

    return pd.DataFrame([{
        labels["obs"]: len(rets),
        labels["cumulative_return"]: cumulative_return(rets, method=method),
        labels["annualized_return"]: annualized_return(rets, ppy, method=method, freq=freq),
        labels["annualized_volatility"]: annualized_volatility(rets, ppy, freq=freq),
        labels["sharpe_ratio"]: sharpe_ratio(rets, risk_free_annual, ppy, freq=freq, method=method),
    }])

def analyze_funds(
    df: pd.DataFrame,
    price_col: str = "Fiyat",
    fund_code_col: str = "Fon Kodu",
    fund_title_col: str = "Fon Adı",
    date_col: str = "Tarih",
    freq: str = "D",
    risk_free_annual: float = 0.0,
    periods_per_year: int | None = None,
    method: str = "simple",
    drop_empty: bool = True,
    lang: str = "tr",
) -> pd.DataFrame:
    lng = normalize_lang(lang)
    labels = get_metric_labels(lng)

    required = [price_col, fund_code_col, date_col]
    if df is None or df.empty or any(col not in df.columns for col in required):
        return pd.DataFrame(columns=[
            "Fon Kodu" if lng=="tr" else "Fund Code",
            "Fon Adı" if lng=="tr" else "Fund Name",
            labels["obs"],
            labels["cumulative_return"], labels["annualized_return"],
            labels["annualized_volatility"], labels["sharpe_ratio"]
        ])

    work = df.dropna(subset=required).copy()
    work[date_col] = pd.to_datetime(work[date_col], format="%d.%m.%Y", errors="coerce")
    work[price_col] = pd.to_numeric(work[price_col], errors="coerce")
    work = work.dropna(subset=[date_col, price_col]).sort_values([fund_code_col, date_col])

    out_rows = []
    for code, g in work.groupby(fund_code_col, dropna=True):
        try:
            m = compute_metrics(
                g, price_col=price_col, date_col=date_col, freq=freq,
                risk_free_annual=risk_free_annual, periods_per_year=periods_per_year,
                method=method, lang=lng
            ).iloc[0].to_dict()

            name_val = g.sort_values(date_col).iloc[-1][fund_title_col] if fund_title_col in g.columns else None
            row = {
                ("Fon Kodu" if lng=="tr" else "Fund Code"): code,
                ("Fon Adı" if lng=="tr" else "Fund Name"): name_val,
                labels["obs"]: m[labels["obs"]],
                labels["cumulative_return"]: m[labels["cumulative_return"]],
                labels["annualized_return"]: m[labels["annualized_return"]],
                labels["annualized_volatility"]: m[labels["annualized_volatility"]],
                labels["sharpe_ratio"]: m[labels["sharpe_ratio"]],
            }
            out_rows.append(row)
        except Exception:
            if not drop_empty:
                out_rows.append({
                    ("Fon Kodu" if lng=="tr" else "Fund Code"): code,
                    ("Fon Adı"  if lng=="tr" else "Fund Name"): None,
                    labels["obs"]: 0,
                    labels["cumulative_return"]: None,
                    labels["annualized_return"]: None,
                    labels["annualized_volatility"]: None,
                    labels["sharpe_ratio"]: None,
                })

    out = pd.DataFrame(out_rows)
    if out.empty:
        return out

    return out.sort_values(
        by=[labels["sharpe_ratio"], labels["annualized_return"]],
        ascending=[False, False],
        na_position="last"
    ).reset_index(drop=True)