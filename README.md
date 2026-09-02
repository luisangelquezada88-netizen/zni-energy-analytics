# GENERACIÓN ELÉCTRICA DE LAS ZONAS NO INTERCONECTADAS

Este repositorio constituye el desarrollo posterior de mi tesis de grado, el cual se enfocó en el uso de energías renovables en las Zonas No Interconectadas (ZNI) de Colombia: 

    Quezada, L. A. (2024). En camino a una transición energética justa : un análisis de gobernanza para las Zonas No Interconectadas. http://hdl.handle.net/10554/69107


El uso de herramientas de software e inteligencia artificial son de gran utilidad en la construcción de soluciones innovadoras a retos de gran complejidad como la transición energética. Por ende, además de la descripción tanto cuantitativa como cualitativa del fenómeno y la emisión de lineamientos de política (presentes en la investigación), en el presente repositorio se aumentan las capacidades de exploración estadística, se generan consultas SQL y se construye un algoritmo no supervisado de Machine Learning para la identificación del riesgo energético, insumos que alimentan la app que despliega el tablero de control de la investigación.

## ¿Qué son las Zonas No Interconectadas?

Las Zonas No Interconectadas son territorios que no hacen parte del Sistema Interconectado Nacional (SIN). Piensa en la electricidad que usas en tu hogar como una cadena de suministro: si vives en las principales ciudades de Colombia, la electricidad que consumes es generada en gran parte por hidroeléctricas, energía que luego es transmita y distribuida hasta la comodidad de tu hogar, constituyendo el SIN. 

En las Zonas No Interconectadas, la historia es diferente. Debido a características como su lejanía de centros urbanos, dificultades en el acceso, condiciones geográficas, presencia de ecosistemas y diversidad cultural, impiden su conexión al SIN. 

## ¿Por qué es importante este fenómeno de investigación? 

Las ZNI constituyen el 52% del territorio colombiano. Al no poder conectarse al SIN, miles de familias no cuentan con un suministro constante ni fiable de energía eléctrica, lo que, sumado a los bajos promedios diarios de disponibilidad del servicio, da como resultado duros escenarios de pobreza energética que impactan en la calidad de vida de sus habitantes.

A lo anterior se suma el contraste entre la potencialidad del territorio y su estado actual. A pesar de que las ZNI tienen gran potencial para la generación eléctrica con energías renovables, la matriz sigue siendo dominada por combustibles fósiles y problemas técnicos, jurídicos, económicos y socioculturales son frecuentes. 

El fenómeno de abordó desde la perspectiva de la justicia energética y la gobernanza. Para más información, consulte la investigación, adjuntada en el repositorio. 

## Datos utilizados

Se utilizan históricos extraídos del portal de Datos Abiertos de Colombia. Debido a que la plataforma limita la extracción de registros vía API a solo 1000 registros, se obta por descargar los archivos ``.csv`` y almacenarlos dentro del repositorio. 

| Nombre | Entidad | No. de registros (filas) | Fecha de actualización | Relevancia | Acceso |
|----------|-------------------|----------------------|----------------------|----------------------|----------|
| **Estado de la prestación del servicio de energía en Zonas No Interconectadas** | IPSE | 6.216 | 13/03/2026 | Permite caracterizar la prestación del servicio | [https://www.datos.gov.co/Minas-y-Energ-a/Estado-de-la-prestaci-n-del-servicio-de-energ-a-en/3ebi-d83g/about_data](https://www.datos.gov.co/Minas-y-Energ-a/Estado-de-la-prestaci-n-del-servicio-de-energ-a-en/3ebi-d83g/about_data) |
| **Superservicios - Registro de Generación Diaria - ZNI** | Superintendencia de Servicios Públicos | 2.222.487 | 24/05/2024 | Permite desagregar la matriz eléctrica | [https://www.datos.gov.co/Minas-y-Energ-a/Superservicios-Registro-de-Generacion-Diaria-ZNI/3a44-zwt6/about_data](https://www.datos.gov.co/Minas-y-Energ-a/Superservicios-Registro-de-Generacion-Diaria-ZNI/3a44-zwt6/about_data) |