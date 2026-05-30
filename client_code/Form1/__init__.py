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

    

  @handle("outlined_button_1", "click")
  def outlined_button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.rich_text_2.visible=True
    self.rich_text_3.visible=True
    self.repeating_panel_1.visible=True
    self.repeating_panel_1.items = app_tables.chemical_notes.search()
    


