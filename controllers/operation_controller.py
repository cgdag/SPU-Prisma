from ..settings.json_tools import JsonTools
from ..settings.env_tools import EnvTools

from PyQt5.QtCore import QVariant


class OperationController:
    """
    Classe utilizada para criar um dicionário com especificações da operação que será feita.
    Dentre as especificações estão: tipo de operação (shapefile, ponto, endereço, feição selecionada),
    arquivos shapefile e bases de dados de bancos de dados selecionados para comparação.

    @ivar data_bd: Armazena bases de dados de banco de dados vindos do arquivo de configuração JSON.
    @ivar data_shp: Armazena bases de dados de shapefiles vindos do arquivo de configuração JSON.
    @ivar json_tools: Classe para leitura de arquivos JSON. comoposwmoa
    """
    def __init__(self):
        """
        Método de inicialização da classe.
        """
        self.json_tools = JsonTools()
        self.data_bd = self.json_tools.get_config_database()
        self.data_shp = self.json_tools.get_config_shapefile()
        self.data_required = self.json_tools.get_config_required()

    def get_operation(self, operation_config, selected_items_shp, selected_items_bd):
        """
        Função que gera as configurações/especificações da busca de sobreposição que irá acontecer. Aqui é armazenado, em formado de dicionário, quais bases de dados serão de dados serão
        utilizadas para a busca de sobreposição

        @keyword operation_config: Dicionário contendo configurações/especificações de busca.
        @keyword selected_items_bd: Vetor com bases de dados vindos de banco de dados que foram selecionados para comparação.
        @keyword selected_items_shp: Vetor com bases de dados vindos de shapefiles que foram selecionados para comparação.
        @return operation_config: Dicionário contendo configurações/especificações de busca.
        """
        if (operation_config['operation'] == 'shapefile'):
            operation_config = self.create_operation_config(operation_config, selected_items_bd, selected_items_shp)

        elif (operation_config['operation'] == 'feature'):
            operation_config = self.create_operation_config(operation_config, selected_items_bd, selected_items_shp)

            # Quando uma camada é pega do QGis, alguns campos são retornados em formato de objeto QVariant
            # Esses dados sempre são nulos e podem ser apagados, que é oq está sendo feito
            # Veja: https://github.com/geopandas/geopandas/issues/2269
            input = operation_config['input']
            columns = list(input)

            for i in range(len(input)):
                for column in columns:
                    if column in input:
                        if type(input.iloc[i][column]) == QVariant:
                            input = input.drop(column, axis=1)

            operation_config['input'] = input

        elif (operation_config['operation'] == 'coordinate'):
            operation_config = self.create_operation_config(operation_config, selected_items_bd, selected_items_shp)


        return operation_config

    def create_operation_config(self, operation_config, selected_items_bd, selected_items_shp):
        """
        Monta uma lista de configurações para operação que será realizada.

        @keyword operation_config: Dicionário contendo configurações/especificações de busca.
        @keyword selected_items_bd: Vetor com bases de dados vindos de banco de dados que foram selecionados para comparação.
        @keyword selected_items_shp: Vetor com bases de dados vindos de shapefiles que foram selecionados para comparação.
        @return operation_config: Dicionário contendo configurações/especificações de busca.
        """
        operation_config['shp'] = []
        for i in self.data_shp:
            if(i['nome'] in selected_items_shp):
                operation_config['shp'].append(i)

        operation_config['pg'] = []

        handled_items_db = []
        for value in selected_items_bd:
            handled_value = value.replace(')', '').split(' (')
            handled_items_db.append(handled_value)

        for i in self.data_bd:
            et = EnvTools()
            login = et.get_credentials(i['id'])

            i['usuario'] = login[0]
            i['senha'] = login[1]

            for key, layer in enumerate(i['nomeFantasiaTabelasCamadas']):
                for layer_req in handled_items_db:
                    if i['nome'] == layer_req[1] and layer == layer_req[0]:
                        operation_config['pg'].append(dict(i))
                        print(operation_config['pg'][-1])
                        operation_config['pg'][-1]['nomeFantasiaTabelasCamadas'] = [layer]
                        operation_config['pg'][-1]['tabelasCamadas'] = [i['tabelasCamadas'][key]]
                        operation_config['pg'][-1]['estiloTabelasCamadas'] = [i['estiloTabelasCamadas'][key]]

        for i in self.data_required:
            if i['tipo'] == 'pg':
                for x in self.data_bd:
                    if i['id'] == x['id']:
                        et = EnvTools()
                        login = et.get_credentials(i['id'])

                        i['usuario'] = login[0]
                        i['senha'] = login[1]

        operation_config['required'] = self.data_required

        return operation_config