from ._anvil_designer import RowTemplate1Template
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class RowTemplate1(RowTemplate1Template):
  def __init__(self, **properties):
    self.init_components(**properties)
    
    self.label_6.text = self.item['brand']
    self.label_8.text = self.item['model']
    self.label_10.text = self.item['similarity']
    self.text_box_1.text = self.item['chemical_notes']
    
