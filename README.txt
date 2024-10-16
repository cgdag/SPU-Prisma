# SPU-Prisma

O SPU-Prisma (ou simplesmente Prisma), deve ser considerado como um complemento do QGIS para Caracterização em massa de imóveis (lote, terreno) em geral. Em particular, esse complemento auxilia no estudo de sobreposição do imóvel bem como sua identificação no espaço.

Dado um polígono, linha, ponto ou endereço de entrada o complemento realiza a consulta de sobreposição nas bases de dados da SPU e em bases locais na máquina. Basicamente, o complemento testa se o imóvel sobrepõe ou não outros imóveis da União, bem como, levanta todas as suas características espaciais em relação aos imóveis da União.

O Prisma gera documentos em formato PDF com o resultado da caracterização. Tais documentos são compostos por mapas, tabela de coordenadas, informações sobre os imóveis que estão se sobrepondo entre outras informações sobre a sobreposição, como por exemplo o tamanho da área sobreposta.


## O que não é o Prisma

O prisma NÃO pode ser confundido com:

* Um complemento para desenhar polígonos, pontos e linhas.

* Um complemento para atualização de geometria ou qualquer outra informação de bancos de dados geográficos ou de um conjunto de shapefile (SHP).

* Um complemento para fazer cadastro de imóveis.

* Um complemento para criar geometrias.

## Tipos de entradas de dados que o Prisma aceita

O Prisma aceita as seguintes entradas vindas do usuário:

* Um endereço de um imóvel que será geocodificado e transformado em um ponto especializado.
* Uma Feição selecionada de uma camada aberta no QGIS que pode ser de um dos tipos: camada de polígonos, camada de linhas, camada de ponto e camada de Multipolígonos
* De um shapeFile com uma ou mais feições, que pode ser: Pontos, Linha, Polígonos e Multipolígonos.


## Tipos bases de dados que o Prisma Consome

O Prisma também irá precisar de consumir internamente pelo menos um dos seguintes tipos de bases de dados:

* Banco de dados Postgres/Postgis.

* Um diretório na máquina do usuário com Shapefiles.

Essas bases devem vir de um processo de curadoria feito pelos técnicos da SPU. E deverão ser cadastradas no próprio complemento dentro da janela de configurações.

Ao cadastrar as bases no plugin será gerado um JSON de curadoria e pré configuração das bases de dados. Tal JSON poderá ser compartilhado entre os usuários da SPU facilitando a disseminação das bases dados de consulta, garantindo que sejam utilizadas bases de dados confiáveis.

## Contato dos Desenvolvedores (contact)

* Vinicius Rafael Schneider (vinirafaelsch@gmail.com)
* Guilherme Henrique (guilherme.nascimento@economia.gov.br)
