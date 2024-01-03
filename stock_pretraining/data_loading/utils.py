

def set_stock_data():
     response = httpx.get(f"https://api.tiingo.com/tiingo/{interval}/{ticker}/prices?startDate={start_date}&endDate={end_date}&format=csv", headers=headers)
    if response.is_error:
        if debug:
            print(f'Failed to retrieve data for {ticker} with the following response: "{response.text}".')

        continue
    df = pd.read_csv(StringIO(response.text), sep=",")
    df = df.rename(columns={
        'date': 'stock_datetime',
        'adjVolume': 'stock_adj_volume',
        'adjClose': 'stock_adj_close',
        'adjHigh': 'stock_adj_high',
        'adjLow': 'stock_adj_low',
        'adjOpen': 'stock_adj_open',
    })
    df['ticker'] = ticker
    df['stock_interval'] = interval
    df['id'] = [uuid.uuid4() for _ in range(len(df))]
    df = df[['id', 'ticker', 'stock_interval', 'stock_datetime', 'stock_adj_volume', 'stock_adj_open', 'stock_adj_close', 'stock_adj_high', 'stock_adj_low']]
    df.to_sql("stock_data", self.engine, if_exists='append', index=False)