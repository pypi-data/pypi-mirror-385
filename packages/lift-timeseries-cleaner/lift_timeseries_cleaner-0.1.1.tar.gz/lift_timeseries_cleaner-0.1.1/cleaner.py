import pandas as pd
import os
df= pd.ExcelFile('Dataset_kenya/Income Report - Mon Apr 3 2023.xlsx')
df_demo = pd.read_excel(df, sheet_name='Demographics')
df_src = pd.read_excel(df, sheet_name='Income Sources')
df_report = pd.read_excel(df, sheet_name='Income Reports')
dt = df_report[['Respondent ID', 'Gender', 'Age', 'Number of children',
       'Marital Status', 'Country of Residence','Income report amount','Income report date created']]
dt.columns = ['id', 'gender', 'age', 'children', 'marital', 'country', 'amount', 'date']
dt['date'] = pd.to_datetime(dt['date'])
dt.set_index('date', inplace=True)
dt['week'] = dt.index.strftime('%m%Y')
dt = dt.sort_values(by='week')
# Pivot the dataframe: one row per id, weeks as columns (amount values), retain other columns
df_pivot = dt.reset_index().pivot_table(
    index=['id', 'gender', 'age', 'children', 'marital', 'country'],
    columns='week',
    values='amount',
    aggfunc='sum',
    fill_value=0
)
# Flatten columns
df_pivot.columns = [str(col) for col in df_pivot.columns]
df_pivot = df_pivot.reset_index()
print(df_pivot.head())
# print(f"Number of variables: {df_pivot.shape[1]}")

# # ML data generator class
# class MLDataGenerator:
#     def __init__(self, df, covariates, week_columns):
#         self.df = df
#         self.covariates = covariates
#         self.week_columns = sorted(week_columns, key=lambda x: pd.to_datetime('01'+x, format='%d%m%Y'))

#     def generate(self, n=6):
#         data = []
#         for _, row in self.df.iterrows():
#             covs = row[self.covariates].values.tolist()
#             weeks = [row[w] for w in self.week_columns]
#             for i in range(len(weeks) - n):
#                 X = covs + weeks[i:i+n]
#                 y = weeks[i+n]
#                 data.append(X + [y])
#         columns = self.covariates + [f'week_{i+1}' for i in range(n)] + ['y']
#         return pd.DataFrame(data, columns=columns)

# # Usage example
# covariates = ['gender', 'age', 'children', 'marital', 'country']
# week_columns = [col for col in df_pivot.columns if col not in ['id'] + covariates]
# week_columns = [col for col in week_columns if int(col) >= 12022]
# if '012022' not in week_columns:
#     week_columns = ['012022'] + week_columns
# mlgen = MLDataGenerator(df_pivot, covariates, week_columns)
# ml_df = mlgen.generate(n=6)
# ml_df['id'] = df_pivot['id'].repeat(len(ml_df) // len(df_pivot)).reset_index(drop=True)
# ml_df = ml_df.fillna(0)
# print(ml_df.head())
# print(f"ML dataframe shape: {ml_df.shape}")
# ml_df.to_csv('outputs/model_data.csv', index=False)
# df_pivot.to_csv('outputs/df_pivot.csv', index=False)

# Save all trained models in 'models/' directory (add this to your notebook after training)
# import os
# os.makedirs('models', exist_ok=True)
# for name, model in trainer.models.items():
#     joblib.dump(model, f"models/{name.replace(' ', '_').lower()}_model.pkl")
#     print(f"Saved {name} as models/{name.replace(' ', '_').lower()}_model.pkl")