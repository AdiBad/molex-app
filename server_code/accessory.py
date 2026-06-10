import anvil.files
from anvil.files import data_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

import pandas as pd

@anvil.server.callable
def fetch_perfumes(user_brand:str=None) -> pd.DataFrame():
  a = pd.read_csv(data_files['perfume_brand_model.csv'])
  if user_brand is not None:
    a = a[a['perfume_brand']==user_brand]
  return a.to_dict('records')


@anvil.server.callable
def fetch_perfume_key(perfume_brand:str, perfume_model:str) -> str:
  a = pd.read_csv(data_files['perfume_brand_model.csv'])
  return a[(a['perfume_brand']==perfume_brand) &
    (a['perfume_name']==perfume_model)]['fraterwork_ID'].iloc[0]

@anvil.server.callable
def dot_product_perfumes(user_perfume_key:str) -> pd.DataFrame():
  embedding = pd.read_csv(data_files['perfume_avg_embedding.csv'], 
                          index_col=0, header=None, encoding='utf-8')
  embedding.index.name='perfume'
  embedding = embedding.groupby('perfume').mean()
  user_choice = embedding.loc[user_perfume_key] 
  remaining_perfumes = embedding.drop(index=user_perfume_key)
  scores = remaining_perfumes.dot(user_choice).sort_values(ascending=False)
  result_df = scores.reset_index()
  result_df.columns = ["perfume_key", "score"]
  return result_df.to_dict("records")  

@anvil.server.callable
def best_perfume_info(top_perfume_key:str) -> pd.DataFrame():
  top_notes = pd.read_csv(data_files['perfume_top_notes.csv'], 
                          index_col=0, header=None)
  perfume_models = pd.read_csv(data_files['perfume_brand_model.csv'], 
                            index_col=0)
  return {
    'perfume_name': perfume_models.loc[top_perfume_key]['perfume_brand']+\
                    ' ' + perfume_models.loc[top_perfume_key]['perfume_name'],
    'description':  perfume_models.loc[top_perfume_key]['description'],
    'top_notes': top_notes.loc[top_perfume_key].dropna().to_list()[0],
    }