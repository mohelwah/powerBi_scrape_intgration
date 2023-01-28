import pandas as pd

mast_df_link = 'https://raw.githubusercontent.com/mohelwah/powerBi_scrape_intgration/main/data/data-5-1-2023-23-1-2023.csv'
df  = pd.read_csv(mast_df_link)
df.head()