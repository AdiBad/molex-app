from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
from anvil.tables import app_tables


class Form1(Form1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    super().__init__(**properties)

    # Any code you write here will run before the form opens.
    #rows = app_tables.chemical_notes.search()

    # Create dropdown items
    #self.drop_down_1.items = set([
    #  row['brand'] for row in rows
    #])
    #self.drop_down_2.items = set([
    #  row['model'] for row in rows
    #])


    rows = anvil.server.call('fetch_perfumes')
    
    self.drop_down_1.items = sorted(set(
      row['perfume_brand'] for row in rows
    ))
    
    self.drop_down_2.items = sorted(set(
      row['perfume_name'] for row in rows
    ))
    self.repeating_panel_1.visible=False


  def clean_perfume_name(self, perfume:str)->str:
    return perfume.replace(' ', '').lower()


  @handle("drop_down_1", "change")
  def drop_down_1_change(self, **event_args):
    """This method is called when an item is selected"""
    selected_value = self.drop_down_1.selected_value
    rows = anvil.server.call('fetch_perfumes', selected_value)
    self.drop_down_2.items = sorted(set(
      row['perfume_name'] for row in rows
    ))

  @handle("outlined_button_1", "click")
  def outlined_button_1_click(self, **event_args):
    if self.drop_down_1.selected_value is None:
      perfume_key = 'orriswakan'
      alert("Using Orris Wakan as the default user choice")
    else:
      perfume_key = anvil.server.call('fetch_perfume_key', 
                                   self.drop_down_1.selected_value,
                                   self.drop_down_2.selected_value)
    matched_perfumes = anvil.server.call('dot_product_perfumes', perfume_key)
    top_perfume = matched_perfumes[0]['perfume_key']
    
    top_perfume_details = anvil.server.call('best_perfume_info', top_perfume)
    self.best_match_perfume.content = top_perfume_details['perfume_name']
    self.description.content = top_perfume_details['description']
    self.top_notes.content = top_perfume_details['top_notes']
    self.score.text = round(int(matched_perfumes[0]['score']),2)
    
    self.best_match_perfume.visible=True
    self.description.visible=True
    self.top_notes.visible=True    
    self.score.visible=True

    # More information tab
    results_list=[]
    for data in matched_perfumes[1:5]:
      perfume_details =  anvil.server.call('best_perfume_info', 
                                       data.get('perfume_key'))
      results_list.append({
        'brand': perfume_details['perfume_name'],
        'description': perfume_details['description'],
        'score': round(int(data.get('score')), 2),
      })
    results_list.sort(key=lambda x: x['score'], reverse=True)
    self.repeating_panel_1.items = results_list
    self.repeating_panel_1.visible=True

  """
  @handle("outlined_button_1", "click")
  def outlined_button_1_click(self, **event_args):
    perfume_name = self.drop_down_2.selected_value
    perfume_name = self.clean_perfume_name(perfume_name)

    chemical_notes = app_tables.chemical_notes.search()

    # Create a pure Python dictionary mapping the 'perfume_lower' column to the row contents
    embeddings = {row['perfume_lower']: dict(row) for row in chemical_notes}

    #user chooses
    # 1. Get the embedding vector for the target perfume
    target_perfume = embeddings.get(perfume_name)

    if target_perfume is None:
      # Fallback if selected perfume is missing from database
      self.best_match_perfume.content = f"Perfume {perfume_name} not found"
      self.best_match_perfume.visible=True
      return

    # Extract the numeric vector list from your target perfume row
    # (Replace 'embedding_vector' with your actual column name containing the numbers)
    target_vector = [float(x) for x in target_perfume['embedding'].split()]

    best_score = float('-inf')
    best_match_name = None
    best_match_data = None
    results_list=[]
    for name, data in embeddings.items():
      if name == perfume_name:
        continue  # Skip the selected perfume itself

        # Parse the text string for the current perfume in the loop
      current_text_vector = data['embedding']
      current_vector = [float(x) for x in current_text_vector.split()]
        
        # 3. Calculate dot product in pure Python
      dot_product = sum(a * b for a, b in zip(target_vector, current_vector))
      results_list.append({
        'brand': data.get('brand', ''),
        'model': data.get('model', ''),
        'score': round(dot_product, 2),
        'description': data.get('description', '')
      })
        
        # 4. Track the highest score
      if dot_product > best_score:
            best_score = dot_product
            best_match_name = name
            best_match_data = data

    # 5. Assign the results back to your UI elements
    if best_match_data is not None:
      # Use app_tables.your_table_name.get() to find the single matching row
      # Replace 'chemical_notes' with your actual app_tables name if it is different
      best_match = app_tables.chemical_notes.get(perfume_lower=best_match_name)

      # Check if a matching row was actually found to prevent errors
      if best_match is not None:
        # Access column values using dictionary-style bracket notation
        self.best_match_perfume.content = f"{best_match['brand']} {best_match['model']}"
        self.description.content = best_match['description']
        self.top_notes.content = best_match['chemical_notes']

    
    self.best_match_perfume.visible=True
    self.description.visible=True
    self.top_notes.visible = True

    # populate chemical notes
    
    self.repeating_panel_1.visible=True
    results_list.sort(key=lambda x: x['score'], reverse=True)
    self.repeating_panel_1.items = results_list
  """
  
    



