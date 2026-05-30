from ._anvil_designer import Form1Template
from anvil import *
from anvil.tables import app_tables
import pandas as pd

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
    return perfume.replace((' ', '')).lower()

  @handle("outlined_button_1", "click")
  def outlined_button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    perfume_name = f'{self.drop_down_1.selected_value}{self.drop_down_2.selected_value}'
    perfume_name = self.clean_perfume_name(perfume_name)

    chemical_notes = app_tables.chemical_notes.search()
    list_of_dicts = [dict(row) for row in chemical_notes]
    embeddings = pd.DataFrame.from_records(
      list_of_dicts).set_index('perfume_lower')

    #user chooses
    remaining_perfumes = embeddings[~embeddings.index.isin([perfume_name])]
    best_matches = remaining_perfumes.dot(
      perfume_name).sort_values(ascending=False)
    best_match = best_matches.iloc[0]
    self.best_match_perfume.content = best_match.index[0]
    self.description.content = best_match['Description']
    self.top_notes.content = ''

    
    self.rich_text_2.visible=True
    self.rich_text_3.visible=True

    # populate chemical notes
    
    """
    top_notes = pd.read_csv('perfume_top_notes.csv', index_col=0, 
                            header=None, encoding='utf-8')
    self.repeating_panel_1.visible=True
    self.repeating_panel_1.items = app_tables.chemical_notes.search()
    """
    


