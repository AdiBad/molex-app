from anvil import *

from ._anvil_designer import RowTemplate1Template


class RowTemplate1(RowTemplate1Template):
  def __init__(self, **properties):
    self.init_components(**properties)
    
    self.label_6.text = self.item['brand']
    self.label_10.text = self.item['score']
    self.text_box_1.text = self.item['description']
    
