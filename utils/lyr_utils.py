from qgis import processing
from qgis.core import QgsVectorLayer

def layer_reproject(layer_in:QgsVectorLayer, crs_out:int) -> QgsVectorLayer:
    '''
        Função de apoio para execução de ferramenta de reprojeção do QGIS.
            Parameters:
                layer_in (QgsVectorLayer): Objeto QgsVectorLayer a ser reprojetado
                crs_out (int): Código EPSG do Sistema de referencia de saída

            Returns:
                Memory_out (QgsVectorLayer): Objeto QgsVectorLayer em memória do objeto reprojetado
    '''
    parameter = {'INPUT': layer_in,
                 'TARGET_CRS': f'EPSG:{crs_out}',
                 'OUTPUT': 'memory:'
                }
    lyr_reproj = processing.run('native:reprojectlayer', parameter)['OUTPUT']
    lyr_fixed = layer_fix_geometries(lyr_reproj)
    
    return lyr_fixed
    
def layer_fix_geometries(layer_in:QgsVectorLayer) -> QgsVectorLayer:
    '''
        Função de apoio para execução de ferramenta de correção de geometrias do QGIS.
            Parameters:
                layer_in (QgsVectorLayer): Objeto QgsVectorLayer a ser corrigido
                
            Returns:
                Memory_out (QgsVectorLayer): Objeto QgsVectorLayer em memória do objeto corrigido
    '''
    parameter = {'INPUT': layer_in,
                 'OUTPUT': 'memory:'
                }
    return processing.run('native:fixgeometries', parameter)['OUTPUT']