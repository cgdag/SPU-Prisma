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
        copyright            : (C) 2021 by Zago / SPU
        email                : vinirafaelsch@gmail.com; guilherme.nascimento@economia.gov.br; marcoaurelio.reliquias@gmail.com
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
"""Todas os metodos de percistencia do postgres vao aqui"""
import psycopg2

class DbConnection:
    """
    Classe responsável por realizar operações em um banco de dados PostgreSQL.

    Atributos:
        host (str): Endereço do host do banco de dados.
        port (str): Porta do banco de dados.
        db (str): Nome do banco de dados.
        user (str): Nome do usuário para conexão.
        password (str): Senha para conexão.
        conn: Objeto de conexão com o banco de dados.
    """

    def __init__(self, host, port, db, user, password):
        """
        Inicializa a conexão com o banco de dados.

        Args:
            host (str): Endereço do host do banco de dados.
            port (str): Porta do banco de dados.
            db (str): Nome do banco de dados.
            user (str): Nome do usuário para conexão.
            password (str): Senha para conexão.
        """
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.password = password

        self.conn = psycopg2.connect(" dbname=" + self.db + " user=" + self.user + " host=" + self.host+ " password=" + self.password + " port=" + self.port)

    def GETtForeignKeyRelationTable(self, tableName):
        """
        Retorna uma tabela com informações sobre as relações de chave estrangeira de uma tabela.

        Args:
            tableName (str): Nome da tabela.

        Returns:
            list: Lista de tuplas com informações sobre chaves estrangeiras.
        """

        sql='SELECT conrelid::regclass AS ' + '"FK_Table"'
        + ',CASE WHEN pg_get_constraintdef(c.oid) LIKE' + " 'FOREIGN KEY %' THEN substring(pg_get_constraintdef(c.oid), 14, position(')' in pg_get_constraintdef(c.oid))-14) END AS " +' "FK_Column"'
        +',CASE WHEN pg_get_constraintdef(c.oid) LIKE' + " 'FOREIGN KEY %' THEN substring(pg_get_constraintdef(c.oid), position(' REFERENCES ' in pg_get_constraintdef(c.oid))+12, position('(' in substring(pg_get_constraintdef(c.oid), 14))-position(' REFERENCES ' in pg_get_constraintdef(c.oid))+1) END AS " + '"PK_Table"'
        +',CASE WHEN pg_get_constraintdef(c.oid) LIKE' + " 'FOREIGN KEY %' THEN substring(pg_get_constraintdef(c.oid), position('(' in substring(pg_get_constraintdef(c.oid), 14))+14, position(')' in substring(pg_get_constraintdef(c.oid), position('(' in substring(pg_get_constraintdef(c.oid), 14))+14))-1) END AS" + '"PK_Column"'
        +"FROM   pg_constraint c"
        +"JOIN   pg_namespace n ON n.oid = c.connamespace"
        +"WHERE  contype IN ('f', 'p ')"
        +"AND pg_get_constraintdef(c.oid) LIKE 'FOREIGN KEY %' AND conrelid::regclass::text='" + tableName + "'"
        +"ORDER  BY pg_get_constraintdef(c.oid), conrelid::regclass::text, contype DESC;"

        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return rows

    def GEtSridTable(self, tableName):
        """
        Obtém o SRID de uma tabela que possui uma coluna geométrica.

        Args:
            tableName (str): Nome da tabela.

        Returns:
            int: SRID da tabela.
        """

        sql = "select ST_SRID(ta.geom) as srid from " + tableName +" as ta group by srid"
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        srid =''

        for row in rows:
            srid = row[0]

        return srid

    def GEtNumberLineOfTable(self, tableName):
        """
        Retorna o número de linhas de uma tabela.

        Args:
            tableName (str): Nome da tabela.

        Returns:
            int: Número de linhas na tabela.
        """
        sql = "select count(*) from " + tableName
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        numberLine=''

        for row in rows:
            numberLine = row[0]
        return numberLine

    def GEtAllTables(self, schemaName):
        """
        Retorna todas as tabelas de um esquema específico.

        Args:
            schemaName (str): Nome do esquema.

        Returns:
            list: Lista de nomes de tabelas no esquema.
        """
        sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='" + schemaName + "';"
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        geoTablesLis = []

        for r in rows:
            geoTablesLis.append(r[0])

        return geoTablesLis
        
    def GEtTablesGeo(self, schemaName):
        """
        Retorna todas as tabelas com colunas geométricas de um esquema.

        Args:
            schemaName (str): Nome do esquema.

        Returns:
            list: Lista de nomes de tabelas que possuem colunas geométricas.
        """
        sql = "SELECT * FROM  information_schema.columns where table_schema='" + schemaName + "' AND column_name='geom'"
        #sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='" + schemaName + "';"
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        geoTablesLis = []

        for r in rows:
            geoTablesLis.append(r[2])

        return geoTablesLis

    def CAlculateIntersect(self, polygono, tableName, sridLayer):
        """
        Retorna os registros de uma tabela que intersectam com um polígono específico.

        Args:
            polygono (str): Geometria do polígono no formato WKT.
            tableName (str): Nome da tabela.
            sridLayer (int): SRID da camada do polígono.

        Returns:
            list: Lista de registros que intersectam com o polígono.
        """
        t = []
        if self.GEtNumberLineOfTable(tableName) > 0:

            sridTable = self.GEtSridTable(tableName)

            sql = "select ST_AsText(geom) as wkt_geom, * from " + tableName + " as ta where ST_Intersects (ta.geom, " + " ST_Transform ( ST_GeomFromText('" + polygono + "'," + str(sridLayer) + ")," + str(sridTable) + " ))"

            cur = self.conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            # for r in rows:
            #     print (r[0])
            return rows
        else:
            return t

    def CAlculateIntersectByPoint(self, pointCoord, tableName, sridPoint, raio):
        """
        Retorna os registros de uma tabela que intersectam com um buffer circular de um ponto.

        Args:
            pointCoord (tuple): Coordenadas do ponto (x, y).
            tableName (str): Nome da tabela.
            sridPoint (int): SRID do ponto.
            raio (float): Raio do buffer.

        Returns:
            list: Lista de registros que intersectam com o buffer.
        """
        t = []
        if self.GEtNumberLineOfTable(tableName) > 0:
            sridTable = self.GEtSridTable(tableName)
            sql = "select *, ST_AsText(geom) as wkt_geom from " + tableName + " as ta where ST_Intersects (ta.geom, " + "ST_Buffer(ST_Transform ( ST_SetSRID (ST_Point(" + str(pointCoord[0]) + "," + str(pointCoord[1]) + ")," + str(sridPoint) + ")," + str(sridTable) + " )," + str(raio) +") )"

            print (sql)
            cur = self.conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            # for r in rows:
            #     print (r[0])
            #print(rows)
            return rows
        else:
            return t


    def CReatePoint(self, pointCoord, sridInit):
        #t = []

        #sridTable = self.getSridTable(tableName)
        sql = "select ST_AsText( ST_Transform (ST_SetSRID (ST_Point(" + str(pointCoord[0]) + "," + str(pointCoord[1]) + ")," + str(sridInit) + ")," + str(4674) + "))"

        print (sql)
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()

        return rows


    #return a array with columns names of a table.
    def GEtTableColum(self, tableName, schemaName):

        sql = "select column_name from INFORMATION_SCHEMA.columns where table_schema= '" + schemaName + "' and table_name= '" + tableName + "';"
        #sql = "select * from " + schemaName + "." + tableName +";"
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        columnsLis = []

        for r in rows:
            columnsLis.append(r[0])
        return columnsLis


    #return dicionario.
    def GEtTablesCollumnsAll(self, tablesList, schemaName):

        columnsList=[]
        tablesCollumnsDic={}

        for table in tablesList:
            columnsList = self.getTableColum(table, schemaName)
            tablesCollumnsDic.update({table:columnsList})

        return tablesCollumnsDic


    def GEtGeomTypeTable(self, tableName):
        pass
        #return self.dataGeomTypes[tableName]

    def GEtGeomTypeTable(self, schema ,tableName):
        sql = "SELECT ST_GeometryType(geom) FROM " + schema +"." + tableName + " limit 1"
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        r = ''
        for row in rows:
            r = str(row[0])
        return r


    def GEtDataTypeColumns(self, tableName):

        sql = "select column_name, data_type, character_maximum_length from information_schema.columns where table_name='" + tableName + "'"
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        typeCollumnsDic={}

        for row in rows:
            typeCollumnsDic.update({row[0]:(row[1],row[2])})

        return typeCollumnsDic

    def GEtAllTypeGeomOFGeomColum(self, schema):
        tables = self.GEtTablesGeo(schema)
        dataTypeDic = {}
        for table in tables:
            tp = self.GEtGeomTypeTable(schema, table)
            dataTypeDic[table] = tp

        return dataTypeDic

    def testConnection(self,):
        """
        Testa a conexão com o banco de dados.

        Returns:
            bool: Verdadeiro se a conexão for bem-sucedida, Falso caso contrário.
        """
        try:
            cur = self.conn.cursor()
            return True
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            return False
