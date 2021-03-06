import sys
import pandas as pd
from sqlalchemy import create_engine 


def load_data(messages_filepath: str, categories_filepath: str) -> pd.DataFrame:
    """
    Read and merge messages and categories.
    
    :param messages_filepath: file path of message data
    :param categories_filepath: file path of category data
    :return: merged message and category data
    """
    messages = pd.read_csv(messages_filepath) 
    categories = pd.read_csv(categories_filepath)
    df = pd.merge(messages, categories, on=["id"], how="inner")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the merged message and category data.
    
    :param df: merged message and category data
    :return: cleaned message and category data
    """
    # create a dataframe of the 36 individual category columns
    categories = df["categories"].str.split(";", expand=True)
    
    # rename the columns of categories by extracting from the values, e.g. 'related-1'
    row = categories.loc[0, :]
    category_colnames = [c.split("-")[0] for c in row]
    categories.columns = category_colnames
    
    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].str[-1].astype(int)

        # make all columns binary (a few values, e.g. in "related", are higher than 1)
        categories[column] = categories[column].map(lambda x: 1 if x == 2 else x)

        # convert column from string to numeric
        categories[column] = pd.to_numeric(categories[column])
        
    df = df.drop(columns=["categories"])
    df = pd.concat([df, categories], axis=1)
    
    # drop duplicates
    df = df.drop_duplicates()
    return df

def save_data(df: pd.DataFrame, database_filename: str) -> None:
    """
    Saves the cleaned message and category data to a database.
    
    :param df: cleaned message and category data
    :param database_filename: file name of the database
    :return: data saved to database
    """
    engine = create_engine(f'sqlite:///{database_filename}')
    df.to_sql("DisasterResponse", engine, index=False, if_exists="replace")  


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
