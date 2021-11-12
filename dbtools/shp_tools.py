# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Prisma
                                 A QGIS plugin
 Plugin para fazer caracterização de imóveis
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-09-29
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Zago
        email                : guilherme.nascimento@economia.gov.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import geopandas as gpd

from qgis.core import QgsProject, QgsVectorLayer

from shapely.wkt import loads

from .pgtools import PgTools
import json
import numpy as np

class ShpTools():

    def __init__(self):
        pass

    def OverlayAnalisys(self, operation_data):
        self.operation_data = operation_data
        gdf_selected_shp = []

        # Leitura dos dados que serão utilizados para sobreposição de áreas
        input = gpd.read_file(self.operation_data['input'])
        input = input.to_crs(4674)

        # Cálculo do buffer de proximidade
        if 'aproximacao' in self.operation_data:
            buffer_length_in_meters = (5 * 1000) * 1.60934

            input['geometry'] = input['geometry'].buffer(buffer_length_in_meters)

        # Leitura de shapefiles com GeoPandas
        for shp in range(len(self.operation_data['shp'])):
            gdf_selected_shp.append(gpd.read_file(self.operation_data['shp'][shp]['diretorioLocal']))
            gdf_selected_shp[shp] = gdf_selected_shp[shp].to_crs(4674)

        # Comparação de sobreposição entre input e Shapefiles
        index = 0
        overlay_shp = input.copy()
        index_result = 0
        overlay_shp['sobreposicao'] = False
        for area in gdf_selected_shp:
            print(self.operation_data['shp'][index]['nome'])
            print(area.crs)
            for indexArea, rowArea in area.iterrows():
                for indexInput, rowInput in input.iterrows():
                    # overlay_shp.loc[index_result, 'areaLote'] = rowInput['geometry'].area
                    # overlay_shp.loc[index_result, 'ctr_lat'] = rowInput['geometry'].centroid.y
                    # overlay_shp.loc[index_result, 'ctr_long'] = rowInput['geometry'].centroid.x

                    if(rowArea['geometry'].intersection(rowInput['geometry'])):
                        overlay_shp.loc[index_result, self.operation_data['shp'][index]['nome']] = (rowArea['geometry'].intersection(rowInput['geometry'])).area
                        overlay_shp.loc[index_result, 'sobreposicao'] = True
                        # overlay_shp.loc[indexInput, self.operation_data['shp'][index]['nome']] = rowArea.loc[[indexArea], 'geometry']

                    index_result += 1
            index += 1

        # Configuração acesso banco de dados Postgis junto das camadas que serão utilizadas
        databases = []
        for db in self.operation_data['pg']:
            databases.append({'connection': PgTools(db['host'], db['porta'], db['baseDeDados'], db['usuario'], db['senha']),
                              'layers': db['tabelasCamadas']})

        # Comparação de sobreposição entre input e Postgis
        gdf_selected_db = []
        layers_db = []
        for database in databases:
            for layer in database['layers']:
                layers_db.append(gpd.GeoDataFrame.from_dict(database['connection'].CalculateIntersectGPD(input.to_dict(), layer,
                                                                         (str(input.crs)).replace('epsg:', ''))))

            gdf_selected_db.append(layers_db)

        index_db = 0
        index_layer = 0
        index_result = 0
        overlay_db = input.copy()
        overlay_db['sobreposicao'] = False
        for db in gdf_selected_db:
            for layer_db in db:
                layer_db.geometry = layer_db['geometry'].apply(loads)
                for indexArea, rowArea in layer_db.iterrows():
                    for indexInput, rowInput in input.iterrows():
                        # overlay_db.loc[index_result, 'areaLote'] = rowInput['geometry'].area
                        # overlay_db.loc[index_result, 'ctr_lat'] = rowInput['geometry'].centroid.y
                        # overlay_db.loc[index_result, 'ctr_long'] = rowInput['geometry'].centroid.x

                        if (rowArea['geometry'].intersection(rowInput['geometry'])):
                            overlay_db.loc[index_result, self.operation_data['pg'][index_db]['nomeFantasiaTabelasCamadas'][index_layer]] = (
                                rowArea['geometry'].intersection(rowInput['geometry'])).area
                            overlay_db.loc[index_result, 'sobreposicao'] = True
                            # overlay_db.loc[indexInput, self.operation_data['pg'][index]['tabelasCamadas']] = rowArea.loc[[indexArea], 'geometry']

                        index_result += 1

                index_layer += 1
            index_db += 1

        result = {'overlay_shp': overlay_shp, 'overlay_db': overlay_db, 'input': input,
                  'gdf_selected_shp': gdf_selected_shp, 'gdf_selected_db': gdf_selected_db}

        return result








