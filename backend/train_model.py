import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
import sys
import os
import tldextract
from concurrent.futures import ProcessPoolExecutor
from functools import partial

# To run this from the backend directory:
# python train_model.py

# Add current directory to path if needed for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from features import url_features_extraction

def process_urls_chunk(urls):
    return [url_features_extraction(url) for url in urls]

def load_and_prepare_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.dirname(current_dir) # project root, where CSVs are
    data_frames = []
    
    # 1. Dataset: phishing_url_dataset_unique.csv (RAW URLs)
    print("Loading phishing_url_dataset_unique.csv...")
    df_unique = pd.read_csv(os.path.join(data_dir, 'phishing_url_dataset_unique.csv'))
    urls = df_unique['url'].astype(str).tolist()
    labels = df_unique['label'].tolist()
    
    print(f"Extracting features from {len(urls)} URLs (this might take a moment)...")
    # Using small chunks for progress visibility if we were interactive, 
    # but here we'll just do it. Using multiprocessing to speed up.
    with ProcessPoolExecutor() as executor:
        # Split URLs into chunks for the executor
        chunk_size = 5000
        chunks = [urls[i:i + chunk_size] for i in range(0, len(urls), chunk_size)]
        results = list(executor.map(process_urls_chunk, chunks))
    
    features_unique = [item for sublist in results for item in sublist]
    df1 = pd.DataFrame(features_unique)
    df1['label'] = labels
    data_frames.append(df1)
    print(f"Processed df1: {df1.shape}")

    # 2. Dataset: web-page-phishing.csv (PRE-EXTRACTED)
    # Columns: url_length,n_dots,n_hypens,n_underline,n_slash,n_questionmark,n_equal,n_at,n_and,n_exclamation,n_space,n_tilde,n_comma,n_plus,n_asterisk,n_hastag,n_dollar,n_percent,n_redirection,phishing
    print("Loading web-page-phishing.csv...")
    df_web = pd.read_csv(os.path.join(data_dir, 'web-page-phishing.csv'))
    
    # Map to our 23 features
    # Our order: url_length(0), n_dots(1), n_hyphens(2), n_underline(3), n_slash(4), n_questionmark(5), n_equal(6), n_at(7), n_and(8), n_exclamation(9), n_space(10), n_tilde(11), n_comma(12), n_plus(13), n_asterisk(14), n_hastag(15), n_dollar(16), n_percent(17), n_redirection(18), is_https(19), is_shortened(20), having_ip(21), subdomain_count(22)
    
    df2 = pd.DataFrame()
    df2[0] = df_web['url_length']
    df2[1] = df_web['n_dots']
    df2[2] = df_web['n_hypens']
    df2[3] = df_web['n_underline']
    df2[4] = df_web['n_slash']
    df2[5] = df_web['n_questionmark']
    df2[6] = df_web['n_equal']
    df2[7] = df_web['n_at']
    df2[8] = df_web['n_and']
    df2[9] = df_web['n_exclamation']
    df2[10] = df_web['n_space']
    df2[11] = df_web['n_tilde']
    df2[12] = df_web['n_comma']
    df2[13] = df_web['n_plus']
    df2[14] = df_web['n_asterisk']
    df2[15] = df_web['n_hastag']
    df2[16] = df_web['n_dollar']
    df2[17] = df_web['n_percent']
    df2[18] = df_web['n_redirection']
    
    # Missing features in this dataset, fill with 0 (neutral/unknown)
    df2[19] = 0 # is_https
    df2[20] = 0 # is_shortened
    df2[21] = 0 # having_ip
    df2[22] = 0 # subdomain_count
    
    df2['label'] = df_web['phishing']
    data_frames.append(df2)
    print(f"Processed df2: {df2.shape}")

    # 3. Dataset: phishing_url_dataset.csv (PRE-EXTRACTED)
    # url_length,valid_url,at_symbol,sensitive_words_count,path_length,isHttps,nb_dots,nb_hyphens,nb_and,nb_or,nb_www,nb_com,nb_underscore,target
    print("Loading phishing_url_dataset.csv...")
    df_phish = pd.read_csv(os.path.join(data_dir, 'phishing_url_dataset.csv'))
    
    df3 = pd.DataFrame()
    df3[0] = df_phish['url_length']
    df3[1] = df_phish['nb_dots']
    df3[2] = df_phish['nb_hyphens']
    df3[3] = df_phish['nb_underscore']
    df3[4] = 0 # slash missing
    df3[5] = 0 # questionmark missing
    df3[6] = 0 # equal missing
    df3[7] = df_phish['at_symbol']
    df3[8] = df_phish['nb_and']
    df3[9] = 0 # exclamation missing
    df3[10] = 0 # space missing
    df3[11] = 0 # tilde missing
    df3[12] = 0 # comma missing
    df3[13] = 0 # plus missing
    df3[14] = 0 # asterisk missing
    df3[15] = 0 # hastag missing
    df3[16] = 0 # dollar missing
    df3[17] = 0 # percent missing
    df3[18] = 0 # redirection missing
    df3[19] = df_phish['isHttps']
    df3[20] = 0 # is_shortened missing
    df3[21] = 0 # having_ip missing
    df3[22] = 0 # subdomain_count missing
    
    df3['label'] = df_phish['target']
    data_frames.append(df3)
    print(f"Processed df3: {df3.shape}")

    # Combine all
    print("Combining datasets...")
    final_df = pd.concat(data_frames, ignore_index=True)
    print(f"Final dataset size: {final_df.shape}")
    
    return final_df

def train():
    df = load_and_prepare_data()
    
    X = df.drop(columns=['label'])
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Training Random Forest model on {len(X_train)} samples...")
    # Use n_jobs=-1 for efficiency
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model trained with accuracy: {accuracy * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save the model
    model_path = os.path.join(os.path.dirname(__file__), 'phishing_model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"Model saved to {model_path}")
    
    # Save the feature column names to ensure consistency in main.py if needed
    # But we use fixed order in features.py so it's fine.

if __name__ == "__main__":
    # Workaround for multiprocessing on Windows if needed
    train()
