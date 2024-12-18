from qgis.core import QgsField, QgsFeatureRequest
from PyQt5.QtCore import QVariant

from ..databases.handle_selections import HandleSelections
from .utils import Utils
from .lyr_utils import *

from ..environment import NOME_CAMADA_ENTRADA, NOME_CAMADA_ENTRADA_BUFFER, CRS_PADRAO

class DataProcessing():
    """
    Classe responsável por realizar o pré-processamento de dados geoespaciais para operações específicas.

    Essa classe manipula camadas de entrada, aplica buffers, insere campos para análise de sobreposição,
    e prepara as camadas necessárias para as operações de geoprocessamento.

    Atributos:
        handle_selections (HandleSelections): Classe auxiliar para manipular seleções de camadas.
        utils (Utils): Classe auxiliar para funções utilitárias.
    """
    def __init__(self):
        """
        Método construtor da classe `DataProcessing`.

        Inicializa os atributos `handle_selections` e `utils` para auxiliar nas operações de manipulação de camadas e utilidades.
        """
        self.handle_selections = HandleSelections()
        self.utils = Utils()

    def data_preprocessing(self, operation_config):
        """
        Realiza o pré-processamento de dados geoespaciais com base nas configurações da operação.

        Lê a camada de entrada, aplica transformações como buffer e CRS, 
        e prepara as camadas obrigatórias e opcionais (WFS, SHP, PostgreSQL) para as operações.

        Args:
            operation_config (dict): Configurações da operação, contendo camadas de entrada, aproximações (buffers),
                                    e camadas de comparação.

        Returns:
            dict: Dicionário contendo as camadas processadas, incluindo a camada de entrada, buffers, 
                e camadas obrigatórias ou opcionais.
        """
        # Leitura do shapefile de input
        lyr_input = operation_config['input']['layer']
        lyr_input.setName(NOME_CAMADA_ENTRADA)
        lyr_input = lyr_process(lyr_input, operation_config, CRS_PADRAO)
        input_buffer = operation_config['input'].get('aproximacao', {})

        # Leitura de itens de comparação
        dic_lyr_retorno = {}
  
        list_required, operation_config = self.handle_selections.read_required_layers(operation_config['obrigatorio'], operation_config)
        list_selected_shp, operation_config = self.handle_selections.read_selected_shp(operation_config['shp'], operation_config)
        list_selected_wfs, operation_config = self.handle_selections.read_selected_wfs(operation_config['wfs'], operation_config)
        list_selected_db, operation_config = self.handle_selections.read_selected_db(operation_config['pg'], operation_config)

        for layer in list_selected_shp:
            # Criar campo com o nome da camada de comparação
            lyr_input = self.init_field_layer_name(lyr_input, layer.name())
            # Adiciona buffer nas camadas de comparação
            if operation_config.get('aproximacao') and operation_config['aproximacao'].get(layer.name()):
                layer = insert_buffer(layer, operation_config['aproximacao'][layer.name()])

        for layer in list_selected_wfs:
            # Criar campo com o nome da camada de comparação
            lyr_input = self.init_field_layer_name(lyr_input, layer.name())
            # Adiciona buffer nas camadas de comparação
            if operation_config.get('aproximacao') and operation_config['aproximacao'].get(layer.name()):
                layer = insert_buffer(layer, operation_config['aproximacao'][layer.name()])

        for layer in list_selected_db:
            # Criar campo com o nome da camada de comparação
            lyr_input = self.init_field_layer_name(lyr_input, layer.name())
            # Adiciona buffer nas camadas de comparação
            if operation_config.get('aproximacao') and operation_config['aproximacao'].get(layer.name()):
                layer = insert_buffer(layer, operation_config['aproximacao'][layer.name()])

        for layer in list_required:
            # Criar campo com o nome da camada de comparação
            lyr_input = self.init_field_layer_name(lyr_input, layer.name())
            # Adiciona buffer nas camadas de comparação
            if operation_config.get('aproximacao') and operation_config['aproximacao'].get(layer.name()):
                layer = insert_buffer(layer, operation_config['aproximacao'][layer.name()])

        lyr_input.updateFields()
        dic_lyr_retorno = {'input': lyr_input, 'required': list_required, 'db': list_selected_db, 'shp': list_selected_shp, 'wfs': list_selected_wfs}
        
        # Trata o retorno da função caso usuário tenha inserido buffer na camada de entrada
        if input_buffer:
            lyr_input_buffer = insert_buffer(lyr_input, input_buffer)
            lyr_input_buffer.setName(NOME_CAMADA_ENTRADA_BUFFER)
            lyr_input_buffer = lyr_process(lyr_input_buffer, operation_config, CRS_PADRAO)
            dic_lyr_retorno.update(input_buffer = lyr_input_buffer)

        return dic_lyr_retorno
    
    def init_field_layer_name(self, layer, field_name):
        """
        Adiciona um novo campo a uma camada geoespacial para armazenar informações de sobreposição.

        Esse campo é usado para registrar se há sobreposição entre feições da camada de entrada
        e camadas de comparação.

        Args:
            layer (QgsVectorLayer): Camada de entrada.
            field_name (str): Nome do campo a ser adicionado.

        Returns:
            QgsVectorLayer: Camada atualizada com o novo campo.
        """
        layer_provider = layer.dataProvider()
        # Adiciona um novo campo ao layer
        layer_provider.addAttributes([QgsField(field_name, QVariant.Bool)])

        # Atualiza os campos
        layer.updateFields()

        # Obtém o índice do novo campo
        field_index = layer.fields().indexFromName(field_name)

        # Cria um objeto QgsFeatureRequest para selecionar todos os recursos da camada
        request = QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry)

        # Loop sobre todos os recursos da camada e atualiza o novo campo com o valor padrão
        for feat in layer.getFeatures(request):
            layer.changeAttributeValue(feat.id(), field_index, False)

        return layer