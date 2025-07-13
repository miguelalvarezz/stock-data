[//]: # (TeamName: StockData)
[//]: # (Member1: Victor Martin Alonso::v.martin.alonso@udc.es)
[//]: # (Member2: Miguel Álvarez González::miguel.alvarez.gonzalez@udc.es)
[//]: # (Teacher: AR)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=19113614&assignment_repo_type=AssignmentRepo)

# STOCKDATA
Plataforma de visualización y comparación de fondos de inversión y acciones de compañías

## Funcionalidades
### 1. Búsqueda de Fondos
- **Casos de uso**:
  - Búsqueda por símbolo exacto (ej: AAPL, TSLA, VTI)
  - Búsqueda por nombre parcial (ej: "Apple", "Tesla")
  - Visualización de resultados con información básica (precio, cambio %, volumen, sector)
  - Acceso a detalles completos de cada fondo
  - Recomendación de fondos similares del mismo sector

### 2. Comparación de Fondos
- **Casos de uso**:
  - Comparación de rentabilidad histórica
  - Análisis de volatilidad anual
  - Comparación de comisiones y gastos
  - Análisis de categoría/sector
  - Cálculo de rating basado en rentabilidad/riesgo

### 3. Página Principal
- **Casos de uso**:
  - Inicio de sesión y registro de usuarios
  - Personalización de perfil
  - Redireccionamiento a las demás funcionalidades

## Despliegue
### Opción 1
Ambos integrantes del grupo hemos realizado el despliegue mediante el comando "Dev Containers: Rebuild and Reopen in Container" de la librería Dev Containers. Una vez dentro del contenedor ejecutaremos los siguientes comandos: 
```bash
cd /stock-data
python manage.py runserver 0.0.0.0:800
```
Si fuera necesario realizar migraciones simplemente realizaremos el siguiente comando antes de correr el servidor:
```bash
python manage.py migrate
```

### Opción 2
Existe la posibilidad de realizar el despliegue de otra forma para el que nuestro proyecto está, también, preparado para ejecutar.  
Desde la terminal del proyecto ejecutaremos los siguiente comandos:
```bash
   cd .devcontainer
   docker-compose up --build
```
En una nueva terminal entraremos al contenedor:
```bash
   docker exec -it devcontainer-app-1 bash
```
Una vez dentro del contenedor ralizaremos los mismos comandos que en la opción 1:
```bash
   cd /workspace/stock-data
   python manage.py migrate
   python manage.py runserver 0.0.0.0:8000
```

## Cómo ejecutar
### Enlaces para probar el proyecto:
- http://localhost:8000/home/
- http://localhost:8000/searchFund/
- http://localhost:8000/compareFund/

### Símbolos de fondos y empresas con los que probar el código:
- IVV
- AMAZN
- TSLA
- OVV

### Consideraciones:
- A diferencia de la primera iteración, hemos implementado el poder buscar fondos sin introducir su símbolo concreto. Esto funcionará solo para las empresas y fondos más populares: Tesla, Amazon, S&P500...
- Como se puede ver en el código, contamos con dos aplicaciones que representan las funcionalidades principales: búsqueda y comparación de fondos. Además, como declaramos en el anteproyecto, contamos con dos casos de uso programados dentro de las aplicaciones de las dos funcionalidades principales. Estos son: visualización gráfica de un fondo y la sugerencia de fondos.
- Partes del código fueron generadas con ChatGPT, como los templates html. Además, se ha utilizado como apoyo en otras partes del código: creación de tests.

### Procedimiento:
- **Página de inicio**:
  - Nos encontraremos con los fondos de mayor actividad en el momento en que se entre a la plataforma. Estos fondos se pueden ordenar si presionamos sobre "Cambio %". Por defecto se mostrarán mezclados, si pulsamos una vez obtendremos los fondos con menor cambio y, si pulsamos de nuevo, los que mayor cambio porcentual han experimentado.
  - Por otro lado, dispondremos arriba la derecha de los botones de inicio de sesión y registro. El procedimiento es el típico en una plataforma como esta y, una vez logeados, podremos editar nuestro perfil presionando sobre nuestro nombre de usuario.
  - La página de inicio tiene una caja azul llamada "Buscar Fondos" que nos dirige directamente a la URL dedicada a esta función. También disponemos de un menú desplegable con el que podremos acceder directamente al resto de funcionalidades.

- **Búsqueda**:
  - Búsqueda por símbolo -> se realizará la búsqueda SOLO sobre el símbolo introducido y se mostrarán los detalles básicos sobre este.
  - Búsqueda general (nombres de empresas o fondos populares) -> se realizará primero una búsqueda sobre el nombre introducido y se mostrarán los fondos que tengan algún vínculo con la palabra introducida. En el listado que se imprima podremos seleccionar el que queramos (se imprimen un máximo de 5 fondos que cumplan con la característica).
  - En caso de querer obtener más información sobre el fondo buscado, pulsaremos en detalles y obtendremos información más profesional. Aquí podremos ver la ejecución de uno de los casos de uso secundarios: visualización de fondos.

- **Comparación**:
  - Una vez introducidos los dos símbolos, obtendremos distintos valores que nos facilitarán la comparación. Además, contamos de nuevo con la posibilidad de visualizar datos sobre los fondos.