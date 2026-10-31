
from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
from anvil.files import data_files


class Form1(Form1Template):

  DEFAULT_PERFUME = "orriswakan"
  RESULTS_COUNT = 4

  def __init__(self, **properties):
    super().__init__(**properties)

    # Load perfume metadata only once
    self._perfumes = anvil.server.call('fetch_perfumes')

    # Precompute brand/model lookups
    self._brand_models = {}
    self._perfume_keys = {}

    for row in self._perfumes:
      brand = row['perfume_brand']
      model = row['perfume_name']
      key = str(row['fraterwork_ID'])

      self._brand_models.setdefault(brand, set()).add(model)
      self._perfume_keys[(brand, model)] = key

      # Populate brand dropdown
    self.drop_down_1.items = sorted(self._brand_models)

    # Initially show all perfume models
    self.drop_down_2.items = sorted({
      row['perfume_name'] for row in self._perfumes
    })

    # Hide results
    self.repeating_panel_1.visible = False
    self.xy_panel_1.visible = False
    self.content_panel_2.visible = False
    self.best_match_perfume.visible = False
    self.description.visible = False
    self.top_notes.visible = False
    self.score.visible = False

    # --------------------------------------------------------
    # BRAND SELECTION
    # --------------------------------------------------------

  @handle("drop_down_1", "change")
  def drop_down_1_change(self, **event_args):

    brand = self.drop_down_1.selected_value

    if brand is None:
      models = {
        row['perfume_name'] for row in self._perfumes
      }
    else:
      models = self._brand_models.get(brand, set())

    self.drop_down_2.items = sorted(models)
    self.drop_down_2.selected_value = None

    self._hide_results()

    # --------------------------------------------------------
    # HIDE PREVIOUS RESULTS
    # --------------------------------------------------------

  def _hide_results(self):

    self.repeating_panel_1.visible = False
    self.xy_panel_1.visible = False
    self.content_panel_2.visible = False
    self.best_match_perfume.visible = False
    self.description.visible = False
    self.top_notes.visible = False
    self.score.visible = False

    # --------------------------------------------------------
    # PERFUME SIMILARITY SEARCH
    # --------------------------------------------------------

  @handle("outlined_button_1", "click")
  def outlined_button_1_click(self, **event_args):

    brand = self.drop_down_1.selected_value
    model = self.drop_down_2.selected_value

    # Validate selection
    if brand is None and model is None:
      perfume_key = self.DEFAULT_PERFUME
      alert("Using Orris Wakan as the default fragrance.")

    elif brand is None or model is None:
      alert("Please select both a brand and a fragrance.")
      return

    else:
      perfume_key = self._perfume_keys.get((brand, model))

      if perfume_key is None:
        alert("Fragrance not found.")
        return

    self._hide_results()

    search_button = self.outlined_button_1
    search_button.enabled = False
    search_button.text = "Analyzing fragrance profile…"

    try:
      # Request only the five highest-scoring matches
      matched_perfumes = anvil.server.call(
        'dot_product_perfumes',
        perfume_key,
        self.RESULTS_COUNT
      )

      if not matched_perfumes:
        alert("No similar fragrances found.")
        return

        # Fetch all displayed fragrance information in ONE call
      perfume_keys = [
        item['perfume_key'] for item in matched_perfumes
      ]

      details = anvil.server.call(
        'best_perfume_info_batch',
        perfume_keys
      )

      # Best match
      best = matched_perfumes[0]
      best_info = details[best['perfume_key']]

      self.best_match_perfume.content = best_info['perfume_name']
      self.description.content = best_info['description']
      self.top_notes.content = best_info['top_notes']
      self.score.text = f"{float(best['score']):.2f}"
      self.best_match_image.source = data_files['']
      self.best_match_image.visible = True
      self.best_match_perfume.visible = True
      self.description.visible = True
      self.top_notes.visible = True
      self.score.visible = True
      self.xy_panel_1.visible = True

      # Remaining four recommendations
      self.repeating_panel_1.items = [
        {
          'brand': details[item['perfume_key']]['perfume_name'],
          'description': details[item['perfume_key']]['description'],
          'score': f"{float(item['score']):.2f}"
        }
        for item in matched_perfumes[1:]
      ]

      self.repeating_panel_1.visible = True
      self.content_panel_2.visible = True

    except Exception as e:
      alert(
        f"Unable to retrieve fragrance recommendations: {e}"
      )
    finally:
      search_button.enabled = True
      search_button.text = "Find similar fragrances"
