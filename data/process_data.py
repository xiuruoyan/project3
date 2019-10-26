import sys
import pandas as pd
from sqlalchemy import create_engine

def load_data(messages_filepath, categories_filepath):
    """
    Loads the messages and categories datasets from the specified filepaths
    Input:
        messages_filepath: filepath to the messages dataset
        categories_filepath: filepath to the categories dataset
    Output:
        df: Merged Pandas dataframe
    """
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)
    df = messages.merge(categories, on='id')
    return df


def clean_data(df):
    """
    Cleans dataset
    Input:
        df: Merged pd dataframe
    Output:
        df: Cleaned pd dataframe
    """
    categories = df['categories'].str.split(';',expand=True)
    row = categories[:1]
    category_colnames = row.apply(lambda x: x.str.split('-')[0][0], axis=0)
    categories.columns = category_colnames
    for i in categories:
        categories[i] = categories[i].apply(lambda x: x.split('-')[1] if int(x.split('-')[1]) < 2 else 1)
        categories[i] = categories[i].astype(int)

    df.drop('categories',axis=1,inplace=True)

    df = pd.concat([df,categories], axis=1)

    df = df.drop_duplicates(keep='first')

    return df


def save_data(df, database_filename):
    """
    Save clean dataset into sqlite database
    Input:
        df:  Cleaned pd dataframe
        database_filename: Name of the database file
    """

    engine = create_engine('sqlite:///'+ database_filename)
    df.to_sql('cleanedData', engine, index=False)  


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()
