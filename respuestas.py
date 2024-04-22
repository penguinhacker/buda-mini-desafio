import requests
from functools import reduce

'''
Supuestos:
- No existen dos transacciones en exáctamente el mismo timestamp.
- Al decir ["1713825281517", "0.00028357", "63846000.0", "buy", 8017319] se entiende que se compraron
    0.00028357 BTC a un precio de 63846000 CLP, de acuerdo a las indicaciones del enunciado.
'''

# PREGUNTA 1 ----------------------------------------------------------------------------------------------
#1- ¿Cuánto dinero (en CLP) se transó durante el evento "Black Buda" BTC-CLP ? (truncar en 2 decimales)

'''
Concepto de la solución:
Tenemos una llamada a la API (GET markets/<market_id>/trades) la cual tiene un componente de tiempo en formato
*timestamp*, con esto podemos tomar la fecha de término del BlackBuda y hacer la consulta.

En los resultados, existe un valor que indica el trade más antiguo de la colección. Si este sigue en el intervalo
del BlackBuda, tenemos que volver a hacer una llamada hasta obtener todo el evento, acumulando todos los registros
que estén en dicho intervalo.
'''

# Gracias a internet, obtenemos los intervalos del BlackBuda en timestamp.
start_timestamp = 1709294400000 # 1 Marzo 12:00
end_timestamp = 1709298000000 # 1 Marzo 13:00

# Generamos una función del formato
# GetVolume: int int [string] -> int
# La cual entrega el volumen transado en CLP de un cierto rango
def GetVolume(initial_timestamp, final_timestamp, market_id = "btc-clp"):

    url = f'https://www.buda.com/api/v2/markets/{market_id}/trades'


    current_timestamp = final_timestamp #Este es el valor que usaremos como "pivote"
    results_list = []

    while True:

        response = requests.get(url, params={
            'timestamp': current_timestamp,
            'limit': 100,
        })

        json_response = response.json()
        oldest_timestamp = int(json_response["trades"]["last_timestamp"])

        # Dos casos: El valor está en el intervalo o no está
        # Si el valor está en medio del intervalo
        if oldest_timestamp > initial_timestamp:
            #Tenemos que guardar todos los elementos de "entries" y seguir.
            results_list += json_response["trades"]["entries"]
            current_timestamp = oldest_timestamp - 1 # El pivote actual será un instante antes de la transacción

        else:
            # Terminamos de hacer las consultas, debemos filtrar este último set de elementos.
            elements_in_range = [trade for trade in json_response["trades"]["entries"] if int(trade[0]) >= initial_timestamp]
            results_list += elements_in_range
            break

    return reduce(lambda x, y: x + float(y[2]), results_list, 0)


event_volume = GetVolume( start_timestamp, end_timestamp)
print("Respuesta Pregunta 1: ", event_volume)

#PREGUNTA 2 -----------------------------------------------------------------------------------------------------------
#2- En comparación con el mismo día del año anterior, ¿cuál fue el aumento porcentual en el volumen de transacciones (en BTC)? (truncar en 2 decimales)

# Ocuparemos la función de antes para poder obtener el mismo volumen del año pasado.
# Gracias a google obtenemos las fechas de antes

initial_last_year = 1677672000000
final_last_year = 1677675600000

ly_volume = GetVolume(initial_last_year,final_last_year)

# Con estos valores ahora podemos calcular el aumento porcentual, que es de la siguiente manera:
# aumento = ((valor_final - valor_inicial)/valor_inicial) * 100

aumento_porcentual = ((event_volume - ly_volume) / ly_volume) * 100

print("Aumento porcentual:", round(aumento_porcentual,2) )

# Pregunta 3 ----------------------------------------------------------------------------------------------------------------
#3- Considerando que la comisión normal corresponde a un 0.8% ¿Cuánto dinero (en CLP) se dejó de ganar debido a la liberación de comisiones durante el BlackBuda? (truncar en 2 decimales)

# En este caso solo queda comparar el volumen total de todo el evento y calcular su 0.8%, que es la ganancia
print("Total no ganado:",event_volume*0.008)
