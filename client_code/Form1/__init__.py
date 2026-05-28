from ._anvil_designer import Form1Template
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Form1(Form1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    print(**properties)
    super().__init__(**properties)

    # Any code you write here will run before the form opens.
  @handle("outlined_button_1", "click")
  def outlined_button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.data_grid_1.visible = True

