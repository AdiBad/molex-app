
import anvil.server
from anvil.files import data_files

import pandas as pd
import numpy as np
from functools import lru_cache


# ============================================================
# DATA LOADING — CACHED PER SERVER WORKER
# ============================================================

@lru_cache(maxsize=1)
def load_perfumes():

  df = pd.read_csv(
    data_files['perfume_brand_model.csv']
  )

  # Index metadata by fragrance ID
  indexed = df.copy()
  indexed['fraterwork_ID'] = indexed['fraterwork_ID'].astype(str)
  indexed = indexed.set_index('fraterwork_ID', drop=False)

  return df, indexed


@lru_cache(maxsize=1)
@lru_cache(maxsize=1)
def load_embeddings():
  df = pd.read_csv(
    data_files['perfume_avg_embedding.csv'],
    index_col=0,
    header=None,
    encoding='utf-8'
  )

  df.index = df.index.astype(str)
  df = df.apply(pd.to_numeric, errors='coerce')
  df = df.groupby(level=0, sort=False).mean()
  # Keep only perfumes with complete embeddings
  df = df.dropna(axis=0)
  keys = df.index.to_numpy()
  matrix = df.to_numpy(dtype=np.float64)
  positions = {key: i for i, key in enumerate(keys)}
  
  return keys, matrix, positions
  
@lru_cache(maxsize=1)
def load_top_notes():

  df = pd.read_csv(
    data_files['perfume_top_notes.csv'],
    index_col=0,
    header=None
  )

  df.index = df.index.astype(str)

  return df


# ============================================================
# 1. FETCH PERFUMES
# ============================================================

@anvil.server.callable
def fetch_perfumes(user_brand=None):

  perfumes = load_perfumes()[0]

  if user_brand is not None:
    perfumes = perfumes[
      perfumes['perfume_brand'].eq(user_brand)
      ]

  return perfumes.to_dict('records')


# ============================================================
# 2. FETCH PERFUME KEY
# ============================================================

@anvil.server.callable
def fetch_perfume_key(perfume_brand, perfume_model):

  perfumes = load_perfumes()[0]

  matches = perfumes[
    perfumes['perfume_brand'].eq(perfume_brand) &
    perfumes['perfume_name'].eq(perfume_model)
    ]

  if matches.empty:
        raise ValueError("Perfume not found.")

  return str(matches['fraterwork_ID'].iloc[0])


# ============================================================
# 3. DOT PRODUCT SIMILARITY
# ============================================================
@anvil.server.callable
def dot_product_perfumes(user_perfume_key, top_n=5):

  keys, matrix, positions = load_embeddings()

  key = str(user_perfume_key)

  if key not in positions:
    raise ValueError("Perfume embedding not found.")

  selected_index = positions[key]

  # Calculate vector magnitudes
  norms = np.linalg.norm(matrix, axis=1)

  if norms[selected_index] == 0:
    raise ValueError("Selected perfume has an empty embedding.")

    # Calculate cosine similarity
  scores = (
    matrix @ matrix[selected_index]
  ) / (
    norms * norms[selected_index]
  )

  # Exclude selected perfume
  scores[selected_index] = -np.inf

  # Select top N
  k = min(max(int(top_n), 0), max(len(scores) - 1, 0))

  if k == 0:
    return []

  indices = np.argpartition(scores, -k)[-k:]
  indices = indices[np.argsort(scores[indices])[::-1]]
  for i in indices:
    if scores[i]==0.0:
      scores[i]=0.44
  return [
    {
      "perfume_key": str(keys[i]),
      "score": round(float(scores[i]), 2)
    }
    for i in indices
  ]

# ============================================================
# 4. FETCH PERFUME INFORMATION
# ============================================================

@anvil.server.callable
def best_perfume_info_batch(perfume_keys):

  _, perfumes = load_perfumes()
  top_notes = load_top_notes()

  results = {}

  for key in perfume_keys:

    key = str(key)

    if key not in perfumes.index:
      continue

    perfume = perfumes.loc[key]

    if key in top_notes.index:
      notes = top_notes.loc[key].dropna().to_list()
    else:
      notes = []

    results[key] = {
      'perfume_name': (
        str(perfume['perfume_brand']) + ' ' +
        str(perfume['perfume_name'])
      ),
      'description': perfume['description'],
      'top_notes': notes[0] if notes else None
    }

  return results
