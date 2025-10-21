import pandas as pd
import yfinance as yf
from tqdm import tqdm
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import time
import json

def load_smc_levels(filename: str = "analysis/smc_analysis_levels.csv"):
    try:
        return pd.read_csv(filename)
    except Exception as e:
        print(f"Error loading levels: {e}")
        return None

def load_smc_summaries(filename: str = "analysis/smc_analysis_summaries.csv"):
    try:
        return pd.read_csv(filename)
    except Exception as e:
        print(f"Error loading summaries: {e}")
        return None

def get_current_price(stock_code: str):
    try:
        ticker = yf.Ticker(stock_code)
        data = ticker.history(period="1d", interval="1d")
        if not data.empty:
            return round(data['Close'].iloc[-1], 2)
        return None
    except Exception as e:
        print(f"Error fetching current price for {stock_code}: {e}")
        return None

def screen_stocks_near_levels(levels_df, summaries_df, proximity_percentage: float = 1.0):
    if levels_df is None:
        print("No levels data available for screening.")
        return pd.DataFrame()
    if summaries_df is None:
        print("No summaries data available for screening.")
        return pd.DataFrame()
    
    results = []
    unique_stocks = levels_df['Stock_Code'].unique()
    
    for stock in tqdm(unique_stocks, desc="Screening stocks"):
        current_price = get_current_price(stock)
        if current_price is None:
            continue
        stock_levels = levels_df[levels_df['Stock_Code'] == stock]
        stock_summary = summaries_df[summaries_df['Stock_Code'] == stock]
        
        swing_trend = stock_summary['Swing_Trend'].iloc[0] if not stock_summary.empty else "Unknown"
        internal_trend = stock_summary['Internal_Trend'].iloc[0] if not stock_summary.empty else "Unknown"
        current_zone = stock_summary['Current_Zone'].iloc[0] if not stock_summary.empty else "Unknown"
        
        for _, level in stock_levels.iterrows():
            midpoint = level['Midpoint']
            level_type = level['Level_Type']
            
            threshold = midpoint * (proximity_percentage / 100)
            distance = abs(current_price - midpoint)
            distance_percent = (distance / midpoint) * 100 if midpoint else None
            
            if distance <= threshold:
                results.append({
                    'Stock_Code': stock,
                    'Current_Price': current_price,
                    'Swing_Trend': swing_trend,
                    'Internal_Trend': internal_trend,
                    'Current_Zone': current_zone,
                    'Level_Type': level_type,
                    'Top': level['Top'],
                    'Bottom': level['Bottom'],
                    'Midpoint': midpoint,
                    'Top_Distance_Percent': round(level['Top Distance_Percent'], 2) if 'Top Distance_Percent' in level else None,
                    'Bottom_Distance_Percent': round(level['Bottom Distance_Percent'], 2) if 'Bottom Distance_Percent' in level else None,
                    'Midpoint_Distance_Percent': round(distance_percent, 2) if distance_percent is not None else None,
                    'Time': level['Time']
                })
    
    results_df = pd.DataFrame(results)
    if not results_df.empty:
        results_df = results_df.sort_values(by=['Stock_Code', 'Midpoint_Distance_Percent'])
    return results_df

def main(
    proximity_percentage: float = 2.0,
    output_csv: str = "screener_results.csv",
    spreadsheet_id: str = None,
    output_format: str = "csv",
    clear: bool = False,
    print_details: bool = False,  # Added for debugging
    use_colab: bool = False       # 👈 Added Colab toggle
):
    levels_df = load_smc_levels()
    summaries_df = load_smc_summaries()
    if levels_df is None or summaries_df is None:
        print("No SMC levels or summaries data found.")
        return

    if print_details:
        print(f"Loaded {len(levels_df)} levels rows for {len(levels_df['Stock_Code'].unique())} unique stocks")
        print(f"Loaded {len(summaries_df)} summaries rows for {len(summaries_df['Stock_Code'].unique())} unique stocks")

    screener_results = screen_stocks_near_levels(levels_df, summaries_df, proximity_percentage)
    if screener_results.empty:
        print("No stocks found near SMC levels.")
        return

    # ---------------- Google Sheets setup ----------------
    gspread_client = None
    screener_worksheet = None
    spreadsheet_url = None
    if output_format in ["google_sheets", "both"] and spreadsheet_id:
        try:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = None
            if use_colab:
                try:
                    from google.colab import userdata
                    SERVICE_ACCOUNT_CREDS = userdata.get("SERVICE_ACCOUNT_CREDS")
                    if SERVICE_ACCOUNT_CREDS:
                        SERVICE_ACCOUNT_CREDS = json.loads(SERVICE_ACCOUNT_CREDS)
                        from google.oauth2.service_account import Credentials
                        creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_CREDS, scopes=scope)
                    else:
                        print("⚠️ SERVICE_ACCOUNT_CREDS not found in Colab. Falling back to CSV output.")
                        output_format = "csv"
                except ImportError:
                    print("⚠️ Not running in Colab. Falling back to local credentials.")
            if creds is None:
                local_cred_path = "Credentials/credentials.json"
                if os.path.exists(local_cred_path):
                    creds = ServiceAccountCredentials.from_json_keyfile_name(local_cred_path, scope)
                else:
                    print(f"⚠️ Local credentials.json not found at {local_cred_path}. Falling back to CSV output.")
                    output_format = "csv"

            if creds:
                gspread_client = gspread.authorize(creds)
                spreadsheet = gspread_client.open_by_key(spreadsheet_id)
                spreadsheet_url = spreadsheet.url
                try:
                    screener_worksheet = spreadsheet.worksheet("Screener_Results")
                except gspread.exceptions.WorksheetNotFound:
                    screener_worksheet = spreadsheet.add_worksheet(title="Screener_Results", rows=1000, cols=20)
                if clear:
                    screener_worksheet.clear()

        except Exception as e:
            print(f"Failed to initialize Google Sheets: {e}")
            if output_format == "google_sheets":
                return
            output_format = "csv"

    # ---------------- Save CSV ----------------
    if output_format in ["csv", "both"]:
        if clear and os.path.exists(output_csv):
            os.remove(output_csv)
        screener_results.to_csv(output_csv, index=False)
        print(f"\nScreener results saved to {output_csv}")

    # ---------------- Save Google Sheets ----------------
    if output_format in ["google_sheets", "both"] and gspread_client and screener_worksheet:
        try:
            results_rows = [list(screener_results.columns)]
            for _, row in screener_results.iterrows():
                normalized_row = [str(val) if pd.notnull(val) else "" for val in row]
                results_rows.append(normalized_row)
            if len(results_rows) > 1:
                screener_worksheet.update(range_name="A1", values=results_rows)
                if print_details:
                    print(f"Updated Screener_Results worksheet with {len(results_rows)-1} rows")
            time.sleep(1)
        except Exception as e:
            print(f"Error updating Google Sheets: {e}")

    # ---------------- Print results ----------------
    print("\nStocks with Current Price Near SMC Levels:")
    print(screener_results.to_string(index=False))
    if output_format in ["google_sheets", "both"] and spreadsheet_url:
        print(f"\nData saved to Google Sheets: {spreadsheet_url}")