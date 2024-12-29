import pandas as pd

# File paths
AMAZON_PATH = 'data/amazon-products.csv'
SHEIN_PATH = 'data/shein-products.csv'
CONSOLIDATED_PATH = 'data/consolidated-products.csv'

def preprocess_amazon(amazon_path):
    df = pd.read_csv(amazon_path)
    # Standardizza i campi rilevanti
    df_cleaned = df[['title', 'description', 'final_price', 'currency', 'brand', 'images']].copy()
    df_cleaned.rename(columns={
        'title': 'name',
        'final_price': 'price',
        'images': 'image'
    }, inplace=True)
    # Conversione prezzo
    df_cleaned['price'] = pd.to_numeric(df_cleaned['price'], errors='coerce')
    df_cleaned.dropna(subset=['price'], inplace=True)
    return df_cleaned

def preprocess_shein(shein_path):
    df = pd.read_csv(shein_path)
    # Standardizza i campi rilevanti
    df_cleaned = df[['product_name', 'description', 'final_price', 'currency', 'brand', 'main_image']].copy()
    df_cleaned.rename(columns={
        'product_name': 'name',
        'final_price': 'price',
        'main_image': 'image'
    }, inplace=True)
    # Conversione prezzo
    df_cleaned['price'] = pd.to_numeric(df_cleaned['price'], errors='coerce')
    df_cleaned.dropna(subset=['price'], inplace=True)
    return df_cleaned

def consolidate_datasets(amazon_df, shein_df, output_path):
    consolidated = pd.concat([amazon_df, shein_df], ignore_index=True)
    consolidated.to_csv(output_path, index=False)
    return consolidated

if __name__ == '__main__':
    print("Preprocessing Amazon dataset...")
    amazon_cleaned = preprocess_amazon(AMAZON_PATH)
    print("Amazon dataset cleaned!")

    print("Preprocessing SHEIN dataset...")
    shein_cleaned = preprocess_shein(SHEIN_PATH)
    print("SHEIN dataset cleaned!")

    print("Consolidating datasets...")
    consolidated = consolidate_datasets(amazon_cleaned, shein_cleaned, CONSOLIDATED_PATH)
    print(f"Datasets consolidated and saved to {CONSOLIDATED_PATH}")
