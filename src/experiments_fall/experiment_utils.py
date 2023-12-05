import pandas as pd
from sklearn.preprocessing import KBinsDiscretizer
from sklearn.model_selection import train_test_split

credit10k_translation_table = {
            'PaymentHistory': {'Without_Reference': 0, 'NoAceptable': 1, 'Aceptable': 2, 'Excellent': 3},
            'WorkHistory': {'Unjustified_no_work': 0, 'Unstable': 1, 'Justified_no_work': 2, 'Stable': 3},
            'Reliability': {'Unreliable': 0, 'Reliable': 1},
            'Debit': {'a0_11100': 0, 'a11101_25900': 1, 'a25901_more': 2},
            'Income': {'s0_30000': 0, 's30001_70000': 1, 's70001_more': 2},
            'RatioDebInc': {'Unfavorable': 0, 'Favorable': 1},
            'Assets': {'poor': 0, 'average': 1, 'wealthy': 2},
            'Worth': {'Low': 0, 'Medium': 1, 'High': 2},
            'Profession': {'Low_income_profession': 0, 'Medium_income_profession': 1, 'High_income_profession': 2},
            'FutureIncome': {'Not_promissing': 0, 'Promissing': 1},
            'Age': {'a16_21': 0, 'a22_65': 1, 'a66_up': 2},
            'CreditWorthiness': {'Negative': 0, 'Positive': 1}
        }

def prep_data(df: pd.DataFrame) -> pd.DataFrame:
    '''Preprocess data. Drop columns, convert detector to binary.'''
    columns_to_drop = ['Time', 'Reading ID']
    df = df.drop(columns_to_drop, axis='columns')
    df['Detector'] = df['Detector'].apply(lambda x: 1 if x == 'ON' else 0)
    df = df.drop(['Detector',], axis='columns')
    
    # Subtract lowest value from all values
    for col in df.columns:
        df[col] = df[col] - df[col].min()
    
    return df

def discretize_data(original_df: pd.DataFrame, 
                    df_to_discretize: pd.DataFrame, 
                    cols_to_discretize: list = ['Humidity', 'MQ139', 'TVOC', 'eCO2', 'Temperature'],
                    n_bins: list = [8,8,8,8,4],
                    strategy: str = 'kmeans'
                    ) -> pd.DataFrame:
    '''Discretize data. Returns a new DataFrame with discretized values.'''

    discretizer = KBinsDiscretizer(n_bins=n_bins, encode='ordinal', strategy=strategy, random_state=32)
    discretizer.fit(original_df[cols_to_discretize])
    
    df_to_discretize[cols_to_discretize] = discretizer.transform(df_to_discretize[cols_to_discretize])
    
    return df_to_discretize

def credit_pipeline(raw_data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    def encode_ordinal(df):
        df_encoded = df.copy()

        for feature, mapping in credit10k_translation_table.items():
            df_encoded[feature] = df_encoded[feature].map(mapping)

        return df_encoded
    
    raw_data = encode_ordinal(raw_data)
    
    train_df, test_df = train_test_split(raw_data, test_size=0.2, random_state=42)
    
    return train_df, test_df, 'CreditWorthiness'  

def fire_pipeline(train_filenames: list[str], test_filenames: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw_data = []
    for file in train_filenames:
        raw_data.append(pd.read_csv('data/' + file + '.csv'))
        
    raw_data = pd.concat(raw_data)
    
    
    test_data = []
    for file in test_filenames:
        test_data.append(pd.read_csv('data/' + file + '.csv'))
        
    test_data = pd.concat(test_data)
    
    raw_data = prep_data(raw_data)
    test_data = prep_data(test_data)
    
    raw_data = discretize_data(raw_data)
    test_data = discretize_data(test_data)
    
    for column in raw_data.columns:
        print(f'{column}: {raw_data[column].unique().shape[0]}')
    
    return raw_data, test_data