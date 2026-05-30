from ._anvil_designer import Form1Template
from anvil import *
from anvil.tables import app_tables


class Form1(Form1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    super().__init__(**properties)

    # Any code you write here will run before the form opens.
    rows = app_tables.perfumes.search()

    # Create dropdown items
    self.drop_down_1.items = [
      (row['brand'], row) for row in rows
    ]
    self.drop_down_2.items = [
      (row['model'], row) for row in rows
    ]
    self.repeating_panel_1.visible=False


  def clean_perfume_name(self, perfume:str)->str:
    return perfume.replace(' ', '').lower()

  @handle("outlined_button_1", "click")
  def outlined_button_1_click(self, **event_args):
    perfume_name = f'{self.drop_down_1.selected_value}{self.drop_down_2.selected_value}'
    perfume_name = self.clean_perfume_name(perfume_name)

    chemical_notes = app_tables.chemical_notes.search()

    # Create a pure Python dictionary mapping the 'perfume_lower' column to the row contents
    embeddings = {row['perfume_lower']: dict(row) for row in chemical_notes}

    #user chooses
    # 1. Get the embedding vector for the target perfume
    target_perfume = embeddings.get(perfume_name)

    if target_perfume is None:
      # Fallback if selected perfume is missing from database
      self.best_match_perfume.content = "Perfume not found"
      self.best_match_perfume.visible=True
      return

    # Extract the numeric vector list from your target perfume row
    # (Replace 'embedding_vector' with your actual column name containing the numbers)
    target_vector = [float(x) for x in target_perfume['embedding'].split()]

    best_score = float('-inf')
    best_match_name = None
    best_match_data = None

    for name, data in embeddings.items():
      if name == perfume_name:
        continue  # Skip the selected perfume itself

        # Parse the text string for the current perfume in the loop
      current_text_vector = data['embedding_vector']
      current_vector = [float(x) for x in current_text_vector.split()]
        
        # 3. Calculate dot product in pure Python
      dot_product = sum(a * b for a, b in zip(target_vector, current_vector))
        
        # 4. Track the highest score
      if dot_product > best_score:
            best_score = dot_product
            best_match_name = name
            best_match_data = data

    # 5. Assign the results back to your UI elements
    if best_match_data is not None:
        self.best_match_perfume.content = best_match_name
        self.description.content = best_match_data.get(
          'Description', 'No description available')
        self.top_notes.content = ''

    
    self.best_match_perfume.visible=True
    self.description.visible=True
    self.top_notes.visible = True

    # populate chemical notes
    
    """
    top_notes = pd.read_csv('perfume_top_notes.csv', index_col=0, 
                            header=None, encoding='utf-8')
    self.repeating_panel_1.visible=True
    self.repeating_panel_1.items = app_tables.chemical_notes.search()
    """



