# metro-travel-routes
Este programa permite a la agencia Metro Travel calcular la **ruta más barata** o la **ruta con menor cantidad de escalas** entre dos islas del Caribe, partiendo desde el aeropuerto de Maiquetía (CCS).

## ¿Qué hace el programa?
- Calcula rutas entre aeropuertos considerando precios y escalas.
- Permite al usuario elegir entre:
  - Minimizar **el costo** total del viaje.
  - Minimizar **el número de escalas**.
- Aplica **restricciones de visa**:
  - Si el pasajero no tiene visa, solo puede pasar por islas que **no la requieren**.
  - Si el destino o alguna escala requiere visa y el pasajero no la tiene, el viaje se bloquea.

## Archivos utilizados (NO hardcoded)
- `destinos.csv`: contiene los códigos de aeropuerto y si requieren visa.
- `tarifas.csv`: contiene los vuelos existentes y sus precios.

> Ambos archivos son leídos dinámicamente desde el disco al ejecutar el programa, cumpliendo con la norma del enunciado.