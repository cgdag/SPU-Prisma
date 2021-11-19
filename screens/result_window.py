import sys
import os.path

from qgis.PyQt.QtWidgets import QAction, QFileDialog, QApplication

from qgis.core import QgsProject, QgsVectorLayer, QgsFillSymbol, QgsRasterLayer, QgsMapSettings, QgsCoordinateReferenceSystem, QgsRectangle
from qgis.gui import QgsMapCanvas
from qgis.utils import iface

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

from ..settings.json_tools import JsonTools
from ..layout.layout_manager import LayoutManager

from shapely.wkt import loads
from shapely.geometry import Point, LineString, Polygon, MultiPolygon

import geopandas as gpd

class ResultWindow (QtWidgets.QDialog):
    cancel_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()

    def __init__(self, result):
        self.result = result
        super(ResultWindow, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'result_window.ui'), self)

        self.btn_output.clicked.connect(self.handle_output)
        self.btn_print_overlay_qgis.clicked.connect(self.print_overlay_qgis)
        self.btn_cancel.clicked.connect(self.cancel)
        self.btn_continuar.clicked.connect(self.next)

        self.show_result()

    # Exibe em uma lista a quantidade de sobreposições que se teve com determinada área
    def show_result(self):
        if(self.result['operation'] == 'shapefile'):
            input = self.result['input']

            gdf_result_shp = gpd.GeoDataFrame.from_dict(self.result['overlay_shp'])
            gdf_result_db = gpd.GeoDataFrame.from_dict(self.result['overlay_db'])

            # show_result_shp = gdf_result_shp.query('sobreposicao == True').reset_index()
            # show_result_db = gdf_result_db.query('sobreposicao == True').reset_index()

            layers_bd = 0
            for i in self.result['operation_data']['pg']:
                layers_bd += len(i['tabelasCamadas'])

            # Configura quantidade de linhas e as colunas da tabela de resultados
            self.tbl_result.setColumnCount(3)
            self.tbl_result.setRowCount(len(self.result['operation_data']['shp']) + layers_bd)
            self.tbl_result.setHorizontalHeaderLabels(['Camada', 'Feições camada de input', 'Sobreposições'])

            self.tbl_result.horizontalHeader().setStretchLastSection(True)
            self.tbl_result.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

            row_control = 0
            # Faz a contagem de quantas sobreposições aconteceram com as áreas de shapefile selecionadas
            # e realiza a inserção deste valor na tabela
            for i in self.result['operation_data']['shp']:
                cont = 0
                for rowIndex, row in gdf_result_shp.iterrows():
                    if str(i['nome']) in gdf_result_shp and row[str(i['nome'])] == True:
                        cont += 1

                cellName = QtWidgets.QTableWidgetItem(str(i['nome']))
                self.tbl_result.setItem(row_control, 0, cellName)

                cellName = QtWidgets.QTableWidgetItem(str(len(input)))
                self.tbl_result.setItem(row_control, 1, cellName)

                cellValue = QtWidgets.QTableWidgetItem(str(cont))
                self.tbl_result.setItem(row_control, 2, cellValue)

                row_control += 1

            # Faz a contagem de quantas sobreposições aconteceram com as áreas de banco de dados selecionados
            # e realiza a inserção deste valor na tabela
            for bd in self.result['operation_data']['pg']:
                cont = 0
                for layer in bd['nomeFantasiaTabelasCamadas']:
                    for rowIndex, row in gdf_result_db.iterrows():
                        if row[str(layer)]:
                            cont += 1

                        # if str(layer) in gdf_result_db and row[str(layer)] > 0:
                        #     cont += 1

                    cellName = QtWidgets.QTableWidgetItem(str(layer))
                    self.tbl_result.setItem(row_control, 0, cellName)

                    cellName = QtWidgets.QTableWidgetItem(str(len(input)))
                    self.tbl_result.setItem(row_control, 1, cellName)

                    cellValue = QtWidgets.QTableWidgetItem(str(cont))
                    self.tbl_result.setItem(row_control, 2, cellValue)

                    row_control += 1

    def handle_output(self):
        self.output = QFileDialog.getExistingDirectory(self, "Selecione a pasta de saída")
        self.txt_output.setText(self.output)

    def print_overlay_qgis(self):
        input = self.result['input']

        gdf_selected_shp = self.result['gdf_selected_shp']
        gdf_selected_db = self.result['gdf_selected_db']

        # Carrega camada mundial do OpenStreetMap
        tms = 'type=xyz&url=http://a.tile.openstreetmap.org/{z}/{x}/{y}.png'
        layer = QgsRasterLayer(tms, 'OpenStreetMap', 'wms')

        QgsProject.instance().addMapLayer(layer)
        QApplication.instance().processEvents()
        QgsProject.instance().setCrs(QgsCoordinateReferenceSystem("EPSG:4674"))

        # Exibe de sobreposição entre input e Shapefiles
        index = -1
        index_show_overlay = 0
        gdf_input = gpd.GeoDataFrame(columns = input.columns)
        print_input = False
        input = input.to_crs(epsg='4674')
        for area in gdf_selected_shp:
            area = area.to_crs(epsg='4674')
            index += 1
            gdf_area = gpd.GeoDataFrame(columns = area.columns)
            for indexArea, rowArea in area.iterrows():
                for indexInput, rowInput in input.iterrows():
                    if (rowArea['geometry'].intersection(rowInput['geometry'])):
                        gdf_input.loc[index_show_overlay] = rowInput
                        gdf_area.loc[index_show_overlay] = rowArea
                        index_show_overlay += 1

            if len(gdf_area) > 0:
                print_input = True

                gdf_area = gdf_area.drop_duplicates()
                show_qgis_areas = QgsVectorLayer(gdf_area.to_json(), self.result['operation_data']['shp'][index]['nomeFantasiaCamada'])

                symbol = QgsFillSymbol.createSimple(self.result['operation_data']['shp'][index]['estiloCamadas'][0])
                show_qgis_areas.renderer().setSymbol(symbol)
                QgsProject.instance().addMapLayer(show_qgis_areas)

        # Exibe de sobreposição entre input e Postgis
        index_db = 0
        for db in gdf_selected_db:
            index_layer = 0
            for area in db:
                area.crs = {'init':'epsg:4674'}
                gdf_area = gpd.GeoDataFrame(columns=area.columns)
                for indexArea, rowArea in area.iterrows():
                    for indexInput, rowInput in input.iterrows():
                        if (rowArea['geometry'].intersection(rowInput['geometry'])):
                            gdf_input.loc[index_show_overlay] = rowInput
                            gdf_area.loc[index_show_overlay] = rowArea
                            index_show_overlay += 1

                if len(gdf_area) > 0:
                    print_input = True

                    # gdf_area['geometry'] = gdf_area['geometry'].apply(lambda x: x.wkt).values
                    # print(gdf_area['geometry'])

                    if 'geom' in gdf_area:
                        gdf_area = gdf_area.drop(columns=['geom'])

                    gdf_area = gdf_area.drop_duplicates()

                    show_qgis_areas = QgsVectorLayer(gdf_area.to_json(),
                                                     self.result['operation_data']['pg'][index_db][
                                                         'nomeFantasiaTabelasCamadas'][index_layer])
                    # symbol = QgsFillSymbol.createSimple(
                    #     self.result['operation_data']['pg'][index_db]['estiloTabelasCamadas'][index_layer])
                    # show_qgis_areas.renderer().setSymbol(symbol)
                    QgsProject.instance().addMapLayer(show_qgis_areas)


                index_layer += 1
            index_db += 1

        if print_input:
            gdf_input = gdf_input.drop_duplicates()

            show_qgis_input = QgsVectorLayer(gdf_input.to_json(), "input")

            symbol = QgsFillSymbol.createSimple({'line_style': 'solid', 'line_color': 'black', 'color': 'gray', 'width_border': '0,35', 'style': 'solid'})
            show_qgis_input.renderer().setSymbol(symbol)

            QgsProject.instance().addMapLayer(show_qgis_input)

            # Repaint the canvas map
            iface.mapCanvas().refresh()
            # Da zoom na camada de input
            iface.zoomToActiveLayer()

    def cancel(self):
        self.hide()
        self.cancel_window.emit()

    def next(self):
        LayoutManager()
        

        self.hide()
        self.continue_window.emit()