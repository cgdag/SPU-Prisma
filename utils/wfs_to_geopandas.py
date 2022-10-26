import geopandas as gpd
import requests
from owslib.wfs import WebFeatureService
from qgis.core import QgsProject, QgsVectorLayer, QgsFillSymbol, QgsLineSymbol, QgsMarkerSymbol, QgsRasterLayer, QgsCoordinateReferenceSystem

class WfsOperations:

      def get_wfs_informations(self, link_wfs):

            wfs = WebFeatureService(url=link_wfs)

            layers = list(wfs.contents)

            data_wfs = []
            for data in layers:
                  data_wfs.append([data, wfs[data].title])

            return data_wfs

      def download_wfs_layer(self, link_wfs, layer):
            params = dict(SERVICE='WFS', VERSION="1.1.0", REQUEST='GetFeature',
                  TYPENAME=layer, OUTPUTFORMAT='geojson')

            url = requests.Request('GET', link_wfs, params=params).prepare().url
            response = requests.get(url)

            if response.ok:
                  print("response: ", response)
                  print(os.path.join(os.path.dirname(__file__)))

                  # open("instagram.ico", "wb").write(response.content)

                  return True
            return False

