# -*- coding: utf-8 -*-
import os

from qgis.PyQt.QtWidgets import QApplication
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsRasterLayer, QgsVectorLayer, QgsFillSymbol, \
    QgsLineSymbol, QgsMarkerSymbol, QgsRectangle, QgsMapSettings, QgsLayoutSize, QgsUnitTypes, QgsLayoutExporter, \
    QgsPrintLayout, QgsReadWriteContext, QgsPalLayerSettings, QgsTextFormat, QgsVectorLayerSimpleLabeling
from qgis.PyQt.QtXml import QDomDocument
from qgis.utils import iface
from PyQt5.QtCore import Qt

from ..utils.utils import Utils
from ..settings.env_tools import EnvTools
from ..analysis.overlay_analysis import OverlayAnalisys
from .memorial import gerardoc

import geopandas as gpd
from shapely.geometry import Polygon, Point, LineString
from PyPDF2 import PdfFileReader, PdfFileMerger
from datetime import datetime


class LinestringRequired():
    def __init__(self, operation_config):
        self.operation_config = operation_config

        self.layout = None
        self.atlas = None
        self.index_input = None

        self.gpd_area_homologada = []
        self.gpd_area_nao_homologada = []

        self.utils = Utils()
        self.time = None

        self.layers = []
        self.project_layers = []
        self.rect_main_map = None
        self.root = QgsProject.instance().layerTreeRoot()

        self.basemap_name, self.basemap_link = self.utils.get_active_basemap()

    def linestring_required_layers(self, input, input_standard, gdf_vertices, gpd_area_homologada, gpd_area_nao_homologada, project_layers, index_input, time, atlas, layout):
        self.gpd_area_homologada = gpd_area_homologada
        self.gpd_area_nao_homologada = gpd_area_nao_homologada
        self.time = time
        self.index_input = index_input
        self.atlas = atlas
        self.layout = layout
        self.project_layers = project_layers

        if len(input_standard) > 0:
            self.handle_layers(input.iloc[[0]], input_standard.iloc[[0]], gdf_vertices)
        else:
            self.handle_layers(input.iloc[[0]], input_standard, gdf_vertices)

    def handle_layers(self, feature_input_gdp, input_standard, gdf_vertices):
        """
        Carrega camadas j?? processadas no QGis para que posteriormente possam ser gerados os relat??rios no formato PDF. Ap??s gerar todas camadas necess??rias,
        est?? fun????o aciona outra fun????o (export_pdf), que ?? respons??vel por gerar o layout PDF a partir das fei????es carregadas nesta fun????o.

        @keyword feature_input_gdp: Fei????o que est?? sendo processada e ser?? carregada para o QGis.
        @keyword input_standard: Fei????o padr??o isto ??, sem zona de proximidade (caso necess??rio), que est?? sendo processada e ser?? carregada para o QGis.
        @keyword feature_area: Camada de compara????o que est?? sendo processada.
        @keyword feature_intersection: Camada de interse????o (caso exista) e ser?? carregada para o QGis.
        @keyword index_1: Vari??vel utilizada para pegar dados armazenados no arquivo Json, exemplo: pegar inform????es como estiliza????o ou nome da camada.
        @keyword index_2: Vari??vel utilizada para pegar dados armazenados no arquivo Json, exemplo: pegar inform????es como estiliza????o ou nome da camada.
        """
        crs = (feature_input_gdp.iloc[0]['crs_feature'])
        # Forma de contornar problema do QGis, que alterava o extent da camada de forma incorreta
        extent = feature_input_gdp.bounds

        # Altera o EPSG do projeto QGis
        QgsProject.instance().setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))
        QApplication.instance().processEvents()

        self.remove_layers()

        # Carrega as ??reas de intersec????o no Qgis
        if self.gpd_area_homologada is not None:
            if len(self.gpd_area_homologada) > 0:
                show_qgis_intersection = QgsVectorLayer(self.gpd_area_homologada.to_json(), "Sobreposi????o")
                show_qgis_intersection.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))

                show_qgis_intersection.loadSldStyle(self.operation_config['operation_config']['sld_default_layers']['overlay_input_line'])

                QgsProject.instance().addMapLayer(show_qgis_intersection, False)
                self.root.insertLayer(len(QgsProject.instance().layerTreeRoot().children()) - len(self.project_layers) - 2, show_qgis_intersection)

        # Carrega a ??rea padr??o no QGis, sem ??rea de aproxima????o (caso necess??rio)
        if 'aproximacao' in self.operation_config['operation_config']:
            # Carrega camada de input no QGis (Caso usu??rio tenha inserido como entrada, a ??rea de aproxima????o est?? nesta camada)
            show_qgis_input = QgsVectorLayer(feature_input_gdp.to_json(), "Fei????o de Estudo/Sobreposi????o")
            show_qgis_input.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))

            symbol = self.get_input_symbol(show_qgis_input.geometryType())
            show_qgis_input.renderer().setSymbol(symbol)
            QgsProject.instance().addMapLayer(show_qgis_input, False)
            self.root.insertLayer(len(QgsProject.instance().layerTreeRoot().children()) - len(self.project_layers) - 1, show_qgis_input)

            input_standard = input_standard.to_crs(crs)
            show_qgis_input_standard = QgsVectorLayer(input_standard.to_json(),
                                                      "Fei????o de Estudo/Sobreposi????o (padr??o)")
            show_qgis_input_standard.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))

            symbol = self.get_input_standard_symbol(show_qgis_input_standard.geometryType())
            show_qgis_input_standard.renderer().setSymbol(symbol)
            QgsProject.instance().addMapLayer(show_qgis_input_standard, False)
            self.root.insertLayer(len(QgsProject.instance().layerTreeRoot().children()) - len(self.project_layers) - 2, show_qgis_input_standard)
        else:
            # Carrega camada de input no QGis (Caso usu??rio tenha inserido como entrada, a ??rea de aproxima????o est?? nesta camada)
            show_qgis_input = QgsVectorLayer(feature_input_gdp.to_json(), "Fei????o de Estudo/Sobreposi????o")
            show_qgis_input.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))

            self.get_input_standard_symbol(show_qgis_input.geometryType(), show_qgis_input)

            QgsProject.instance().addMapLayer(show_qgis_input, False)
            self.root.insertLayer(len(QgsProject.instance().layerTreeRoot().children()) - len(self.project_layers) - 1, show_qgis_input)

        layers_localization_map = []
        layers_situation_map = []
        # Posiciona a tela do QGis no extent da ??rea de entrada
        for layer in QgsProject.instance().mapLayers().values():
            if layer.name() == 'Fei????o de Estudo/Sobreposi????o':
                rect = QgsRectangle(extent['minx'], extent['miny'], extent['maxx'], extent['maxy'])
                # Aqui est?? sendo contornado o erro de transforma????o, comentado no comeco desta fun????o
                layer.setExtent(rect)
                self.atlas.setEnabled(True)
                self.atlas.setCoverageLayer(layer)
                self.atlas.changed
                self.layers = layer

                layers_localization_map.append(layer)
                layers_situation_map.append(layer)

            elif layer.name() == 'LPM Homologada' or layer.name() == 'LTM Homologada' or layer.name() == 'LPM N??o Homologada' or layer.name() == 'LTM N??o Homologada':
                layers_situation_map.append(layer)

            elif layer.name() == self.basemap_name:
                layers_localization_map.append(layer)
                layers_situation_map.append(layer)

            elif layer.name() == 'V??rtices':
                qml_style_dir = os.path.join(os.path.dirname(__file__), 'static\Estilo_Vertice_P.qml')
                layer.loadNamedStyle(qml_style_dir)
                layer.triggerRepaint()

        # Configura????es no QGis para gerar os relat??rios PDF
        ms = QgsMapSettings()
        ms.setLayers([self.layers])
        rect = QgsRectangle(ms.fullExtent())

        main_map = self.layout.itemById('Planta_Principal')
        situation_map = self.layout.itemById('Planta_Situacao')
        localization_map = self.layout.itemById('Planta_Localizacao')

        situation_map.setLayers(layers_situation_map)
        localization_map.setLayers(layers_localization_map)
        situation_map.refresh()
        localization_map.refresh()

        ms.setExtent(rect)
        main_map.zoomToExtent(rect)
        iface.mapCanvas().refresh()
        main_map.refresh()
        QApplication.instance().processEvents()
        self.rect_main_map = main_map.extent()

        # Tamanho do mapa no layout
        main_map.attemptResize(QgsLayoutSize(390, 277, QgsUnitTypes.LayoutMillimeters))

        self.export_pdf(feature_input_gdp, gdf_vertices)

    def export_pdf(self, feature_input_gdp, gdf_vertices):
        """
        Fun????o respons??vel carregar o layout de impress??o e por gerar os arquivos PDF.

        @keyword feature_input_gdp: Fei????o de input comparada
        @keyword index_1: Vari??vel utilizada para pegar dados armazenados no arquivo Json, exemplo: pegar inform????es como estiliza????o ou nome da camada.
        @keyword index_2: Vari??vel utilizada para pegar dados armazenados no arquivo Json, exemplo: pegar inform????es como estiliza????o ou nome da camada.
        """
        # Manipula????o dos textos do layout
        self.handle_text(feature_input_gdp)

        if 'logradouro' not in feature_input_gdp:
            feature_input_gdp['logradouro'] = "Ponto por Endere??o ou Coordenada"

        pdf_name = str(feature_input_gdp.iloc[0]['logradouro']) + '_' + str(self.time) + '_AreasUniao.pdf'
        pdf_path = os.path.join(self.operation_config['path_output'], pdf_name)

        atlas = self.layout.atlas()
        """Armazena o atlas do layout de impress??o carregado no projeto."""
        map_atlas = atlas.layout()
        pdf_settings = QgsLayoutExporter(map_atlas).PdfExportSettings()
        pdf_settings.dpi = 300

        if atlas.enabled():
            pdf_settings.rasterizeWholeImage = True
            QgsLayoutExporter.exportToPdf(atlas, pdf_path,
                                          settings=pdf_settings)

        gerardoc(feature_input_gdp, gdf_vertices, pdf_name, pdf_path, self.layout, self.operation_config)
        self.merge_pdf(pdf_name)

    def merge_pdf(self, pdf_name):
        pdf_name = "_".join(pdf_name.split("_", 3)[:3])

        pdf_files = [f for f in os.listdir(self.operation_config['path_output']) if f.startswith(pdf_name) and f.endswith(".pdf")]
        merger = PdfFileMerger()

        for filename in pdf_files:
            merger.append(PdfFileReader(os.path.join(self.operation_config['path_output'], filename), "rb"))

        merger.write(os.path.join(self.operation_config['path_output'], pdf_name + ".pdf"))

        for filename in os.listdir(self.operation_config['path_output']):
            if pdf_name in filename and filename.count("_") > 2:
                os.remove(self.operation_config['path_output'] + "/" + filename)

    def handle_text(self, feature_input_gdp):
        """
        Faz a manipula????o de alguns dados textuais presentes no layout de impress??o.

        @keyword index_1: Vari??vel utilizada para pegar dados armazenados no arquivo Json, exemplo: pegar inform????es como estiliza????o ou nome da camada.
        @keyword index_2: Vari??vel utilizada para pegar dados armazenados no arquivo Json, exemplo: pegar inform????es como estiliza????o ou nome da camada.
        """
        et = EnvTools()
        headers = et.get_report_hearder()

        spu = self.layout.itemById('CD_UnidadeSPU')
        spu.setText(headers['superintendencia'])

        sector = self.layout.itemById('CD_SubUnidadeSPU')
        sector.setText(headers['setor'])

        title = self.layout.itemById('CD_Titulo')
        layer_name = "??reas da Uni??o"
        title.setText('Caracteriza????o: ' + layer_name)
        self.fill_observation(feature_input_gdp, layer_name)

        self.fill_data_source()

    def fill_data_source(self):
        prisma_layers = ['Fei????o de Estudo/Sobreposi????o (padr??o)', 'Fei????o de Estudo/Sobreposi????o', 'Sobreposi????o'] + self.project_layers
        field_data_source = self.layout.itemById('CD_FonteDados')

        all_layers = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
        print_layers = [value for value in all_layers if value not in prisma_layers]

        data_source = self.get_data_source(print_layers)

        text = ''
        for item in print_layers:
            if item != self.basemap_name:
                text_item = data_source[item][0] + " (" + data_source[item][1].split('/')[-1] + "), "
                if text_item not in text:
                    text += text_item

        text += self.basemap_name + " (2022)."
        self.rect_main_map = None

        field_data_source.setText(text)

    def get_data_source(self, layers_name):
        data_source = {}
        for name in layers_name:
            for x in self.operation_config['operation_config']['shp']:
                if name == x['nomeFantasiaCamada']:
                    data_source[str(name)] = [x['orgaoResponsavel'], x['periodosReferencia']]

            for x in self.operation_config['operation_config']['pg']:
                for x_layers in x['nomeFantasiaTabelasCamadas']:
                    if name == x_layers:
                        data_source[str(name)] = [x['orgaoResponsavel'], x['periodosReferencia']]

            for x in self.operation_config['operation_config']['required']:
                if 'nomeFantasiaCamada' in x:
                    if name == x['nomeFantasiaCamada']:
                        data_source[str(name)] = [x['orgaoResponsavel'], x['periodosReferencia']]
                else:
                    for x_layers in x['nomeFantasiaTabelasCamadas']:
                        if name == x_layers:
                            data_source[str(name)] = [x['orgaoResponsavel'], x['periodosReferencia']]

        return data_source

    def fill_observation(self, feature_input_gdp, layer_name):
        input = self.operation_config['input']

        overlay_area = self.layout.itemById('CD_Compl_Obs1')
        lot_area = self.layout.itemById('CD_Compl_Obs1')
        overlay_uniao = self.layout.itemById('CD_Compl_Obs2')
        overlay_uniao_area = self.layout.itemById('CD_Compl_Obs3')
        overlay_uniao_nao = self.layout.itemById('CD_Compl_Obs4')
        overlay_uniao_nao_area = self.layout.itemById('CD_Compl_Obs5')
        texto1 = self.layout.itemById('CD_Compl_Obs6')
        texto1.setText("")

        # ??rea da fei????o
        format_value = f'{feature_input_gdp["areaLote"][0]:_.2f}'
        format_value = format_value.replace('.', ',').replace('_', '.')
        lot_area.setText("Comprimento total da linha: " + str(format_value) + " metros em " + str(len(feature_input_gdp.explode())) + " segmentos.")

        # Sobreposi????o com ??rea da uni??o
        if '??rea Homologada' in input and input.iloc[self.index_input]['??rea Homologada'] > 0:
            overlay_uniao.setText("Lote sobrep??e ??rea Homologada da Uni??o.")
        else:
            overlay_uniao.setText("Lote n??o sobrep??e ??rea Homologada da Uni??o.")

        if '??rea Homologada' in feature_input_gdp:
            format_value = f'{feature_input_gdp.iloc[0]["??rea Homologada"]:_.2f}'
            format_value = format_value.replace('.', ',').replace('_', '.')

            if len(self.gpd_area_homologada) > 0:
                overlay_uniao_area.setText("Sobreposi????o ??rea Homologada: " + str(format_value) + " metros em " + str(
                    len(self.gpd_area_homologada.explode())) + " segmentos.")
            else:
                overlay_uniao_area.setText("Sobreposi????o ??rea Homologada: 0 metros em 0 segmentos.")

        # Sobreposi????o com ??rea da uni??o n??o homologada
        if '??rea N??o Homologada' in input and input.iloc[self.index_input]['??rea N??o Homologada'] > 0:
            overlay_uniao_nao.setText("Lote sobrep??e ??rea N??o Homologada da Uni??o.")
        else:
            overlay_uniao_nao.setText("Lote n??o sobrep??e ??rea N??o Homologada da Uni??o.")

        if '??rea N??o Homologada' in feature_input_gdp:
            format_value = f'{feature_input_gdp.iloc[0]["??rea N??o Homologada"]:_.2f}'
            format_value = format_value.replace('.', ',').replace('_', '.')

            if len(self.gpd_area_nao_homologada) > 0:
                overlay_uniao_nao_area.setText(
                    "Sobreposi????o ??rea N??o Homologada: " + str(format_value) + " metros em " + str(
                        len(self.gpd_area_nao_homologada.explode())) + " segmentos.")
            else:
                overlay_uniao_nao_area.setText("Sobreposi????o ??rea N??o Homologada: 0 metros em 0 segmentos.")


    def add_template_to_project(self, template_dir):
        """
        Adiciona o template do layout ao projeto atual.
        @keyword template_dir: Vari??vel armazena o local do layout.
        """
        project = QgsProject.instance()
        layout = QgsPrintLayout(project)
        document = QDomDocument()

        # Leitura do template
        template_file = open(template_dir)
        template_content = template_file.read()
        template_file.close()
        document.setContent(template_content)

        # Adi????o do template no projeto
        layout.loadFromTemplate(document, QgsReadWriteContext())
        project.layoutManager().addLayout(layout)

    def get_input_symbol(self, geometry_type):
        """
        Estiliza????o din??mica para diferentes tipos de geometrias (??rea de input).

        @keyword geometry_type: Tipo de geometria da ??rea de input (com ou se buffer de ??rea de aproxima????o).
        @return symbol: Retorna o objeto contendo a estiliza????o de uma determinada camada.
        """
        symbol = None

        # Point
        if geometry_type == 0:
            symbol = QgsMarkerSymbol.createSimple({'name': 'dot', 'color': '#616161'})
        # Line String
        if geometry_type == 1:
            symbol = QgsLineSymbol.createSimple({"line_color": "#616161", "line_style": "solid", "width": "0.35"})
        # Pol??gono
        elif geometry_type == 2:
            symbol = QgsFillSymbol.createSimple(
                {'line_style': 'solid', 'line_color': 'black', 'color': '#616161', 'width_border': '0,35',
                 'style': 'solid'})

        return symbol

    def get_input_standard_symbol(self, geometry_type, show_qgis_input):
        """
        Estiliza????o din??mica para diferentes tipos de geometrias (??rea de input sem o buffer de aproxima????o).

        @keyword geometry_type: Tipo de geometria da ??rea de input sem o buffer de aproxima????o.
        @return symbol: Retorna o objeto contendo a estiliza????o de uma determinada camada.
        """
        symbol = None

        # Point
        if geometry_type == 0:
            show_qgis_input.loadSldStyle(
                self.operation_config['operation_config']['sld_default_layers']['default_input_point'])
        # Line String
        if geometry_type == 1:
            show_qgis_input.loadSldStyle(
                self.operation_config['operation_config']['sld_default_layers']['default_input_line'])
        # Pol??gono
        elif geometry_type == 2:
            show_qgis_input.loadSldStyle(
                self.operation_config['operation_config']['sld_default_layers']['default_input_polygon'])

    def get_feature_symbol(self, geometry_type, style):
        """
        Estiliza????o din??mica para diferentes tipos de geometrias (??reas de compara????o).

        @keyword geometry_type: Tipo de geometria da ??rea de compara????o.
        @keyword style: Vari??vel armazena o estilo que ser?? usado para a proje????o de uma determinada camada. Este estilo ?? obtido atrav??s do arquivo JSON de configura????o.
        @return symbol: Retorna o objeto contendo a estiliza????o de uma determinada camada.
        """
        symbol = None

        # Point
        if geometry_type == 0 or geometry_type == 4:
            symbol = QgsMarkerSymbol.createSimple(style)
        # Line String
        elif geometry_type == 1 or geometry_type == 5:
            symbol = QgsLineSymbol.createSimple(style)
        # Pol??gono
        elif geometry_type == 2 or geometry_type == 6:
            symbol = QgsFillSymbol.createSimple(style)

        return symbol

    def remove_layers(self):
        list_required = ['LPM Homologada', 'LTM Homologada', 'LLTM Homologada', 'LMEO Homologada', '??rea Homologada',
                         'LPM N??o Homologada', 'LTM N??o Homologada', '??rea N??o Homologada', 'LLTM N??o Homologada', 'LMEO N??o Homologada',
                         self.basemap_name] + self.project_layers
        for layer in QgsProject.instance().mapLayers().values():
            if layer.name() not in list_required:
                QgsProject.instance().removeMapLayers([layer.id()])
