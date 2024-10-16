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
from shapely.wkt import loads

import psycopg2

class DbConnection:

    def __init__(self, host, port, db, user, password):
        """Constructor."""

        #QDialog.__init__(self)
        #self.setupUi(self)
        #self.iface = iface
        #super(DbTools, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        #self.dataGeomTypes = {"trecho_rodoviario":"LineString", "trecho_ferroviario":"LineString", "area_politico_adminitrativo":"Polygon", "unidade_federacao":"Polygon", "municipio": "Polygon", "municipio":"Polygon", "terreno_sujeito_inundacao":"Polygon","faixa_dominio":"Polygon", "parcela":"Polygon", "terra_originalmente_uniao":"Polygon","trecho_terreno_marginal":"Polygon", "trecho_terreno_marginal":"Polygon","trecho_area_indubitavel":"Polygon", "terras_interiores":"Polygon", "faixa_dominio":"Polygon", "area_especial":"Polygon", "massa_dagua":"Polygon"}
        #self.nameConect = ConfigurationDialog.getLastNameConnection(self)
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.password = password

        #try:
        #print (self.nameConect)
        print (self.host,self.port, self.db, self.user, self.password)

        self.conn = psycopg2.connect(" dbname=" + self.db + " user=" + self.user + " host=" + self.host+ " password=" + self.password + " port=" + self.port)


    # def GEtRefSys(self):
    #     con = sqlite3.connect('C:/Users/guibo/spatialite.db')
    #     print("lido")
    #     cur = con.cursor()
    #     cur.execute('select auth_name, auth_srid, ref_sys_name from spatial_ref_sys order by srid')
    #     rows = cur.fetchall()
    #     return rows

    #Return a table with relation "FOREIGN KEY". The format of table is: FK_Table | FK_Column | PK_Table | PK_Column
    def GETtForeignKeyRelationTable(self, tableName):

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


    #Return a RSID of the table. Return a table
    def GEtSridTable(self, tableName):

        sql = "select ST_SRID(ta.geom) as srid from " + tableName +" as ta group by srid"
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        srid =''

        for row in rows:
            srid = row[0]

        return srid


    def GEtNumberLineOfTable(self, tableName):

        sql = "select count(*) from " + tableName
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        numberLine=''

        for row in rows:
            numberLine = row[0]
        return numberLine


    #return all table of a schema. Return a list of strings
    def GEtAllTables(self, schemaName):

        sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='" + schemaName + "';"
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        geoTablesLis = []

        for r in rows:
            geoTablesLis.append(r[0])

        return geoTablesLis
        #SELECT * FROM information_schema.tables WHERE table_schema='public' AND table_type = 'BASE TABLE' AND table_name<>'spatial_ref_sys'
        #SELECT * FROM  information_schema.columns where table_schema='public' AND column_name='geom'


    #return all table with geometry. Return a list of strings
    def GEtTablesGeo(self, schemaName):

        sql = "SELECT * FROM  information_schema.columns where table_schema='" + schemaName + "' AND column_name='geom'"
        #sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='" + schemaName + "';"
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        geoTablesLis = []

        for r in rows:
            geoTablesLis.append(r[2])

        return geoTablesLis

    #return a table with intersects with  polygono
    def CAlculateIntersect(self, polygono, tableName, sridLayer):

        t = []
        if self.GEtNumberLineOfTable(tableName) > 0:

            sridTable = self.GEtSridTable(tableName)

            # sql = "select * from " + tableName + " as ta where ST_Intersects (ta.geom, " + " ST_Transform ( ST_GeomFromText('" + polygono + "'," + str(
            #     sridLayer) + ")," + str(sridTable) + " ))"

            sql = "select ST_AsText(geom) as wkt_geom, * from " + tableName + " as ta where ST_Intersects (ta.geom, " + " ST_Transform ( ST_GeomFromText('" + polygono + "'," + str(sridLayer) + ")," + str(sridTable) + " ))"
            #sql = "select *, ST_AsText(geom) as wkt_geom from " + tableName + " as ta where ST_Intersects (ta.geom, " + "ST_GeogFromText('SRID=" + str(sridTable) + ";" + polygono + "'))"
            #print (sql)



            cur = self.conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            # for r in rows:
            #     print (r[0])
            return rows
        else:
            return t

    def CAlculateIntersectByPoint(self, pointCoord, tableName, sridPoint, raio):
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
        try:
            cur = self.conn.cursor()
            return True
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            return False



    # def GETtStatesName(self):
    #     sql = "SELECT nome_valor FROM dominio.sigla_uf ORDER BY id_codigo ASC "
    #     cur = self.conn.cursor()
    #     cur.execute(sql)
    #     rows = cur.fetchall()
    #
    #     return rows
