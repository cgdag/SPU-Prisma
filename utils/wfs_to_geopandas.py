import os

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

      def download_wfs_layer(self, link_wfs, layer, base_name):
            params = dict(SERVICE='WFS', VERSION="1.1.0", REQUEST='GetFeature',
                  TYPENAME=layer, OUTPUTFORMAT='json')

            url = requests.Request('GET', link_wfs, params=params).prepare().url
            response = requests.get(url)

            if response.ok:
                  layer = layer\
                        .replace(':', '_')\
                        .replace('*', '_')\
                        .replace('/', '_')\
                        .replace('\\', '_')

                  dir = os.path.dirname(__file__) + '/../wfs_layers/' + str(base_name)
                  print(dir)
                  if not os.path.isdir(dir):
                        os.mkdir(dir)

                  file_path = dir + '/' + layer + ".geojson"
                  open(file_path, "wb").write(response.content)

                  return True
            return False

      def update_wfs_layer(self, link_wfs, layer, base_name):
            params = dict(SERVICE='WFS', VERSION="1.1.0", REQUEST='GetFeature',
                  TYPENAME=layer, OUTPUTFORMAT='json')

            url = requests.Request('GET', link_wfs, params=params).prepare().url
            response = requests.get(url)

            if response.ok:
                  layer = layer\
                        .replace(':', '_')\
                        .replace('*', '_')\
                        .replace('/', '_')\
                        .replace('\\', '_')

                  dir = os.path.dirname(__file__) + '/../wfs_layers/' + base_name + '/' + layer + ".geojson"

                  if os.path.isfile(dir):
                        os.remove(dir)

                  open(dir, "wb").write(response.content)
                  return True
            return False

