# Dynamic Parallel Bitmap (DPB)

**Dynamic Parallel Bitmap** es un sistema optimizado para **búsquedas y deduplicación en mapas de bits segmentados**, con soporte de **IA** y procesamiento **paralelo**. Es ideal para manejar grandes volúmenes de datos en sistemas CRM, multiempresa o distribuidos.

---

## Características

- **Vectorizado** → Operaciones bit a bit altamente optimizadas usando **NumPy**  
- **Dinámico** → Soporta inserciones y eliminaciones de registros  
- **Paralelo** → Búsquedas y joins acelerados mediante **multiprocessing**  
- **Segmentado + IA** → Integración con **TensorFlow** para aprendizaje de patrones  
- **Escalable** → Maneja millones de registros sin degradar el rendimiento  
- **Aplicación típica** → Joins, deduplicación y sincronización de datos en CRM  

---

## DPB-NET-Q (Extensión experimental)

DPB-NET-Q introduce un **entrelazamiento lógico entre nodos de red** mediante **qbits lógicos**:  

- Cada nodo mantiene segmentos sincronizables y un vector de qbits asociados  
- Los valores de **score** y **confianza** evolucionan según la interacción de datos  
- Permite sincronizaciones inteligentes y medición de correlaciones entre nodos distribuidos  

Esta extensión es ideal para **redes de datos distribuidas** y entornos de alta complejidad.

---

## Instalación

Clonar el repositorio e instalar el paquete en modo editable:

```bash
git clone https://github.com/JesusDeg8061/Dynamic_bitmap.git
cd Dynamic_bitmap
pip install dynamic-bitmap
