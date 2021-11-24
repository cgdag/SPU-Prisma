from qgis.PyQt.QtWidgets import QApplication
from qgis.core import QgsProject, QgsVectorLayer, QgsFillSymbol, QgsRasterLayer, QgsCoordinateReferenceSystem
from qgis.utils import iface

import geopandas as gpd

class MapCanvas():
    def __init__(self):
        pass

    def print_overlay_qgis(self, result):
        input = result['input']

        gdf_selected_shp = result['gdf_selected_shp']
        gdf_selected_db = result['gdf_selected_db']

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
                show_qgis_areas = QgsVectorLayer(gdf_area.to_json(), result['operation_config']['shp'][index]['nomeFantasiaCamada'])

                symbol = QgsFillSymbol.createSimple(result['operation_config']['shp'][index]['estiloCamadas'][0])
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
                                                     result['operation_config']['pg'][index_db][
                                                         'nomeFantasiaTabelasCamadas'][index_layer])
                    # symbol = QgsFillSymbol.createSimple(
                    #     result['operation_config']['pg'][index_db]['estiloTabelasCamadas'][index_layer])
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