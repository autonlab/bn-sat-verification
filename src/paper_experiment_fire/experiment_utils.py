import pandas as pd
from sklearn.preprocessing import KBinsDiscretizer

def prep_data(df: pd.DataFrame) -> pd.DataFrame:
    '''Preprocess data. Drop columns, convert detector to binary.'''
    columns_to_drop = ['Time', 'Reading ID']
    df = df.drop(columns_to_drop, axis='columns')
    df['Detector'] = df['Detector'].apply(lambda x: 1 if x == 'ON' else 0)
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