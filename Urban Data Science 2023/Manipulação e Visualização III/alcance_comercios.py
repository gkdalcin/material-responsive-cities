from decimal import Decimal
from qgis import processing
from qgis.processing import alg
from qgis.PyQt.QtCore import QVariant
from qgis.core import (NULL, QgsProject, QgsGeometry, QgsVectorFileWriter, QgsDistanceArea, QgsPointXY, QgsField, QgsFields, QgsVectorDataProvider)

#itens que aparecerão na janela de parâmetros
@alg(name='Alcance_Comercios', label='Alcance_Comercios', group='Urban Data Science', group_label='Urban Data Science')
@alg.input(type=alg.VECTOR_LAYER, name='imoveis', label='Lançamentos Imobiliários', types=[0])
@alg.input(type=alg.VECTOR_LAYER, name='comercios', label='Comercios', types=[0])
@alg.input(type=alg.NUMBER, name='radius', label='Analysis Radius (0.0 = Global Analysis)')

#ui output definition (does nothing, it is here because qgis requires the declaration of at least one output)
@alg.output(type=alg.NUMBER, name='numoffeat', label='Number of Features Processed')

def computeMetrics(instance, parameters, context, feedback, inputs):
    """
     Computa a quantidade de comércios dentro de um raio próximo a um lançamento imobiliário
    """
    
    #salva inputs da janela de parâmetros em variáveis
    comercios = instance.parameterAsVectorLayer(parameters, 'comercios', context)
    imoveis = instance.parameterAsVectorLayer(parameters, 'imoveis', context)
    radius = instance.parameterAsDouble(parameters, 'radius', context) 
    
    #verifica distancias entre imoveis e comercios, salvando os resultados em listas
    resultados = []
    for imovel in imoveis.getFeatures():
        if imovel.id() % 10 == 0:
            feedback.pushInfo(f'Initializing Edge {imovel.id()}')
        comercios_proximos = 0
        for comercio in comercios.getFeatures():
            distancia = QgsDistanceArea().measureLine(imovel.geometry().asPoint(), comercio.geometry().asPoint())
            if distancia <= radius:
                comercios_proximos += 1
        resultados.append([imovel.id(), comercios_proximos])
            

    #cria nova coluna no shapefile
    imoveis.dataProvider().addAttributes([QgsField("Alcance",QVariant.Double)])
    imoveis.updateFields()
    alcIndex = imoveis.fields().indexFromName("Alcance")
    
    for imovel in resultados:
        metricsD = {}
        metricsD[alcIndex] = imovel[1]
        imoveis.dataProvider().changeAttributeValues({imovel[0] : metricsD})


    
