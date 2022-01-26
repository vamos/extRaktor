# Author: libor@labavit.com
# Year: 2021
# Desc.: Gets input data from PDFs

import pandas as pd
import numpy as np
import pdftotext
import argparse
import pickle
import tabula
import nltk
import pdfplumber
import os


def arg_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Throw me some data^^')
    parser.add_argument('-f', "--file", required=True, help="input file", nargs='*')
    return parser.parse_args()


def get_filetype(files):
    """
    Determines imput file types.

    :param files: list of paths
    :return: dictionary {'file': 'type'}
    """
    filetypes_dict = {}
    for file in files:
        keywords_dict = {'Chromatogram': False,     # Shimadzu
                         'SPECORD': False,          # Specord
                         'Report': False}           # Other
        with open(file, "rb") as f:
            pdf = pdftotext.PDF(f)
        page0 = pdf[0]
        tokens = nltk.word_tokenize(page0)
        print(tokens)
        for key in keywords_dict:
            result = key in tokens
            if result:
                # dict with filename : type
                filetypes_dict[file] = key
                break

    # print(filetypes_dict)


def extract_spectrals(files) -> pd.DataFrame:
    """
    Extract all table data from '' filetypes.

    :param files:
    :return: dataframe
    """
    print(f'extract_spectrals')
    dff = pd.DataFrame()
    for file in files:
        print(f'extracting SPECORD file: {file}')
        # create list of pd.DataFrames from one file
        df_list = tabula.read_pdf(file, pages='all', multiple_tables=True)
        # from list make one pd.DataFrame
        df = pd.concat(df_list, axis=1)
        # make one column for each file
        df = df.stack(dropna=True).reset_index(drop=True).to_frame('Data').sort_values('Data')
        df = df.pop('Data').str.extractall(r'(\d+.\d+)')[0].unstack().astype('float')
        df['file'] = file
        dff = dff.append(df)
    return dff


def get_shimadzu_columns(file):
    columns = ['Area', 'Area%']
    return columns


def extract_shimadzu(files, column=None) -> (pd.DataFrame, list):
    """
    Extracts  specific column from tables in Shimadzu type files.


    :param files: list of file paths
    :param column:
    :return:dataframe with all tables from all files
    """

    dff = pd.DataFrame()
    for file in files:
        # check cache
        df = pd.DataFrame()
        df = cache(df, file + '.pkl')

        if df.empty:
            pdf_in = pdfplumber.open(file)
            page = pdf_in.pages[0]
            # if page.extract_table() is not None:
            # in case of empty page pdfplumber extract NoneType
            df_list = page.extract_table()
            df = pd.DataFrame(df_list)
            # create header and drop redundant rows
            columns = df.iloc[2]
            df.columns = columns
            df = df.drop([0, 1, 2])
            # drop last "total" row
            df = df.iloc[:-1]
            # concatenate table data from one file to dataframe
            # save relevant columns
            df = df[['Ret. Time', 'Area', 'Area%']].dropna()
            df = df.astype({"Area%": float, "Area": int, "Ret. Time": float})
            df['file'] = file
            df = cache(df, file + '.pkl')

        dff = dff.append(df)
    # select only relevant rows  and drop last row ( total + NaNs )
    if column is not None:
        print(f'in parser extracting column: {column}')
        dff = dff[['Ret. Time', column, 'file']].dropna()
    else:
        print(f'extracting column:area')
        dff = dff[['Ret. Time', 'Area', 'file']].dropna()
    print(f'dff: {dff}')
    dff['bins_RT'] = pd.cut(dff['Ret. Time'], 400).astype(str)
    dff = dff.pivot(index='file', columns='bins_RT', values=column)
    dff = dff.replace(np.nan, 0)
    # coly index 'file' to be represented in datatable
    dff.reset_index(level=0, inplace=True)

    return dff


def cache(df: pd.DataFrame, cache_file: str) -> pd.DataFrame:
    """
    Simple cache to speed up data extraction.

    :param df:
    :param cache_file:
    :return:
    """

    if os.path.exists(cache_file):
        # Load the cached data from the file.
        with open(cache_file, mode='rb') as file:
            df_cache = pickle.load(file)

        print("- Data loaded: " + cache_file)

    else:
        # The cache-file does not exist. Create cache file.
        if df.empty:
            # when checking cache dataframe should be empty
            # because it happens at the start of extract function
            # if its not empty -> create cache file
            return df
        else:
            with open(cache_file, mode='wb') as file:
                pickle.dump(df, file)
                df_cache = df
            print("+ Data saved: " + cache_file)

    return df_cache


if __name__ == '__main__':
    args = arg_parser()
    extract_shimadzu(['realdata/dalsi/D.pdf', 'realdata/dalsi/D copy.pdf', 'realdata/dalsi/D copy 2.pdf'])
