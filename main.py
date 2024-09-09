import pandas as pd
import gnrl_database_con as db
import os
import statistics


def df_toFloat(dataframe):
    row_list = []
    for row in dataframe.values:
        new_line = []
        for value in row:
            if not type(new_line) == str:
                new_line.append(float(value))
        new_series = pd.Series(new_line, index=df.columns)
        row_list.append(new_series)

    return pd.DataFrame(row_list, columns=df.columns)


if __name__ == "__main__":
    database = db.Database()

    tables = database.show_tables()
    print(tables)
    seriesList = []
    analysis_results_heads = ['id', 'feret_mean', 'feret_median', 'feret_stddev', 'feret_sum']
    for table in tables:
        if not table[0] == 'analysis_results':

            # create a DF from table (probably filled with text values)
            df = database.table_into_DF(table[0])

            # Beginning of DF filtration
            df = df_toFloat(df)

            col_idx = df.columns.tolist()
            if 'Round' not in col_idx:
                continue
            col_idx = col_idx.index('Round')  # Column by which filtration is performed
            filtrated_rows_idx = []
            i = 0
            for row in df.values:
                if row[col_idx] > 0.3:  # Filtrating expression
                    filtrated_rows_idx.append(i)
                i += 1

            df.drop(filtrated_rows_idx, axis=0, inplace=True)  # Returned filtrated DF
            # print(df)

            # Data analysis
            analyzed_column = df['Feret']
            if len(analyzed_column) > 1:
                feret_mean = statistics.mean(analyzed_column)
                feret_median = statistics.median(analyzed_column)
                feret_stdDev = statistics.stdev(analyzed_column)
                feret_sum = sum(analyzed_column)
                feret_series = pd.Series([table[0], feret_mean, feret_median, feret_stdDev, feret_sum],
                                         index=analysis_results_heads)
                seriesList.append(feret_series)
            else:
                feret_mean = statistics.mean(analyzed_column)
                feret_median = 0
                feret_stdDev = 0
                feret_sum = sum(analyzed_column)
                feret_series = pd.Series([table[0], feret_mean, feret_median, feret_stdDev, feret_sum],
                                         index=analysis_results_heads)
                seriesList.append(feret_series)


    # Analysis results
    analysis_result_df = pd.DataFrame(seriesList, columns=analysis_results_heads)

    #write to excel
    analysis_result_df.to_excel(fr"Desktop\analysis_results.xlsx")

    # Send to database
    database_columns = database.get_columns_names('analysis_results')
    if not database.is_table('analysis_results'):
        database.create_table('analysis_results', analysis_results_heads)
        for row in analysis_result_df.values:
            print(f"Row {row}, to list {row.tolist()}")
            database.insert('analysis_results', row.tolist())
    elif len(database_columns) != len(analysis_results_heads):
        new_headers = []

        for column in analysis_results_heads:
            if not column in database_columns:
                new_headers.append(column)
        for header in new_headers:
            values = analysis_result_df[header].tolist()
            database.add_column('analysis_results', header, 'VARCHAR(50)', values)

