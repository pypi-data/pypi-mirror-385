from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
import time
import pandas as pd
import re
from datetime import timedelta
from io import StringIO
from rich.console import Console

from .setup_webdriver import setup_webdriver
from .utils import (
    FUND_TYPE_CODES,
    TAB_CODES,
    get_localized_message,
    parse_and_validate_dates,
    print_rich_panel,
    fix_date
)

def _safe_click(driver, element):
    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)

def _click_if_present(wait, by, locator):
    try:
        elem = wait.until(EC.element_to_be_clickable((by, locator)))
        _safe_click(elem._parent, elem)
        return True
    except Exception:
        return False

def fetch_tefas_data(
    fund_type_code: int,
    tab_code: int,
    start_date: str,
    end_date: str,
    fund_codes: list = None,
    fund_title_contains: list = None,
    lang: str = "tr",
    save_to_excel: bool = False,
    wait_seconds: int = 2,
    headless: bool = True,
) -> pd.DataFrame:
    console = Console()

    if fund_type_code not in FUND_TYPE_CODES:
        raise ValueError(get_localized_message("invalid_fund_type", lang, fund_type_code, list(FUND_TYPE_CODES.keys())))
    if tab_code not in TAB_CODES:
        raise ValueError(get_localized_message("invalid_tab_type", lang, tab_code, list(TAB_CODES.keys())))

    fund_type_label = FUND_TYPE_CODES[fund_type_code]
    tab_label = TAB_CODES[tab_code]

    start_date_dt, end_date_dt = parse_and_validate_dates(start_date, end_date, lang)
    start_date_filename = start_date_dt.strftime("%Y%m%d")
    end_date_filename = end_date_dt.strftime("%Y%m%d")
    excel_filename = f"tefas_{fund_type_label}_{tab_label}_{start_date_filename}_{end_date_filename}.xlsx"

    driver = setup_webdriver(lang, headless=headless)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get("https://www.tefas.gov.tr/TarihselVeriler.aspx")

        for by, loc in [
            (By.ID, "cookieAccept"),
            (By.CSS_SELECTOR, "button[aria-label='Kapat']"),
            (By.CSS_SELECTOR, "button#onetrust-accept-btn-handler"),
        ]:
            _click_if_present(wait, by, loc)

        tab_dropdown_table_map = {
            "general_information": {
                "tab_button_id": "ui-id-1",
                "table_id": "table_general_info",
                "next_button_id": "table_general_info_next",
                "dropdown_name": "table_general_info_length"
            },
            "portfolio_breakdown": {
                "tab_button_id": "ui-id-2",
                "table_id": "table_allocation",
                "next_button_id": "table_allocation_next",
                "dropdown_name": "table_allocation_length"
            }
        }
        tab_params = tab_dropdown_table_map[tab_label]

        tab_button = wait.until(EC.element_to_be_clickable((By.ID, tab_params["tab_button_id"])))
        _safe_click(driver, tab_button)

        all_rows = []
        columns = None
        current_date = start_date_dt

        start_date_input = wait.until(EC.presence_of_element_located((By.ID, "TextBoxStartDate")))
        end_date_input = wait.until(EC.presence_of_element_located((By.ID, "TextBoxEndDate")))
        view_button = wait.until(EC.element_to_be_clickable((By.ID, "ButtonSearchDates")))

        while current_date <= end_date_dt:
            date_str = current_date.strftime("%d.%m.%Y")

            print_rich_panel(
                console,
                get_localized_message("processing_date", lang, date_str),
                lang,
                style="bold yellow"
            )

            start_date_input.clear()
            start_date_input.send_keys(date_str)
            end_date_input.clear()
            end_date_input.send_keys(date_str)
            _safe_click(driver, view_button)

            try:
                table_element = wait.until(EC.presence_of_element_located((By.ID, tab_params["table_id"])))
            except TimeoutException:
                time.sleep(wait_seconds)
                try:
                    table_element = wait.until(EC.presence_of_element_located((By.ID, tab_params["table_id"])))
                except TimeoutException:
                    print_rich_panel(
                        console,
                        get_localized_message("date_skipped", lang, date_str),
                        lang,
                        style="magenta"
                    )
                    current_date += timedelta(days=1)
                    continue

            try:
                select_element = wait.until(EC.presence_of_element_located((By.NAME, tab_params["dropdown_name"])))
                select_box = Select(select_element)
                nums = [int(o.text) for o in select_box.options if o.text.isdigit()]
                if nums:
                    select_box.select_by_visible_text(str(max(nums)))
                    time.sleep(wait_seconds)
            except Exception as e:
                pass

            while True:
                table_element = wait.until(EC.presence_of_element_located((By.ID, tab_params["table_id"])))
                table_html = table_element.get_attribute("outerHTML")

                if ("dataTables_empty" in table_html) or ("Tabloda herhangi bir veri mevcut değil" in table_html):
                    print_rich_panel(
                        console,
                        get_localized_message("date_skipped", lang, date_str),
                        lang,
                        style="magenta"
                    )
                    break

                page_df = pd.read_html(StringIO(table_html), decimal=',', thousands='.')[0]

                if "Tarih" in page_df.columns:
                    page_df["Tarih"] = page_df["Tarih"].apply(fix_date)

                if columns is None:
                    columns = page_df.columns.tolist()

                all_rows.extend(page_df.values.tolist())

                try:
                    next_button = driver.find_element(By.ID, tab_params["next_button_id"])
                except Exception:
                    break

                if "disabled" in next_button.get_attribute("class"):
                    break
                if not (next_button.is_displayed() and next_button.is_enabled()):
                    break

                try:
                    _safe_click(driver, next_button)
                    time.sleep(wait_seconds)
                except ElementClickInterceptedException:
                    break

            print_rich_panel(
                console,
                get_localized_message("date_done", lang, date_str),
                lang,
                style="green"
            )
            current_date += timedelta(days=1)

        if not all_rows or columns is None:
            final_df = pd.DataFrame()
        else:
            final_df = pd.DataFrame(all_rows, columns=columns)

        if fund_codes and not final_df.empty:
            possible_cols = [c for c in final_df.columns if ("fon kodu" in c.lower())]
            if possible_cols:
                fund_col = possible_cols[0]
                final_df = final_df[final_df[fund_col].isin(fund_codes)]

        if fund_title_contains and not final_df.empty:
            possible_title_cols = [c for c in final_df.columns if ("fon adı" in c.lower()) or ("fon adi" in c.lower())]
            if possible_title_cols:
                title_col = possible_title_cols[0]
                s = final_df[title_col].astype(str).str.strip()

                mask = pd.Series(False, index=final_df.index)
                for term in fund_title_contains:
                    t = (str(term) if term is not None else "").strip()
                    if not t:
                        continue
                    pattern = fr"(?<!\w){re.escape(t)}(?!\w)"
                    mask |= s.str.contains(pattern, case=False, regex=True, na=False)

                final_df = final_df[mask]

        print_rich_panel(console, get_localized_message("rows_fetched", lang, final_df.shape[0]), lang, style="green")

        if save_to_excel and not final_df.empty:
            final_df.to_excel(excel_filename, index=False)
            print_rich_panel(console, get_localized_message("saved_excel", lang, excel_filename), lang, style="bold cyan")

        print_rich_panel(console, get_localized_message("all_done", lang), lang, style="bold green")
        return final_df

    finally:
        try:
            driver.quit()
        except Exception:
            pass