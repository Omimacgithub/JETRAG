Actúa como un desarrollador senior especializado en FastAPI con Svelte y ChromaDB.

IMPORTANTE: si ves que algún aspecto que se comenta no coincide con lo que se dice en el resto de ficheros .md que se mencionan en este AGENTS.md, pausa el desarrollo, coméntame las incoherencias que hayas encontrado y espera a mi confirmación antes de continuar.

## Contexto del proyecto
JETRAG es una aplicación WEB que permite a los usuarios interactuar con un chatbot RAG en el que utilizan cofres (concepto que me he inventado para denominar a conjuntos de fuentes de información como texto plano, URLs o ficheros) de manera local, lo que otorga seguridad especialmente cuando se trata con documentos críticos para una empresa.

JETRAG debe permitir su despliegue en sistemas NVIDIA Jetson con 8 GB de RAM, por lo que su diseño e implementación debe ser lo más simple y eficiente posible. Todo el código debe de ejecutarse encima de contenedores de Docker, el contenedor de backend (el que ejecuta las inferencias de la LLM y el modelo de embeddings para RAG) debe de tener acceso directo a la GPU de NVIDIA de la Jetson.

JETRAG es una aplicación WEB que mediante una API REST realiza una gestión de los cofres y sus fuentes (almacenados en una VectorDB).

Necesito que implementes lo siguiente:

## Funcionalidad
La app (JETRAG) se compone de dos ventanas, el flujo de cada ventana y entre ventanas se muestra en la sección "Flujo Principal: Crear Cofre y Chatear" del fichero APPFLOW.md. El fichero ../design/prototypes/MAIN.png muestra un boceto de la ventana del PASO 1 (el boceto es meramente orientativo, puedes adaptar el frontend acorde a tus preferencias), dicha ventana muestra la lista de cofres creados recuperados de la db de SQLite mediante un GET y muestra un botón para crear nuevos cofres, que se registran en la db de SQLite mediante un POST y que hace que la app cambie a la ventana del PASO 2. Cada cofre de la lista de cofres creados es un widget, que al enfocarse con el cursor o teclado permite eliminarlo de la db de SQLite mediante un DELETE o modificar su nombre mediante un PATCH. Si se pulsa en uno de los widgets, se realiza un GET para recuperar la lista de fuentes de la db de SQLite del cofre del widget y la app cambia a la ventana del PASO 2.

El fichero ../design/prototypes/CHAT.png muestra un boceto de la ventana del PASO 2 (el boceto es meramente orientativo, puedes adaptar el frontend acorde a tus preferencias). Dicha ventana contiene un botón para crear un cofre, si se pulsa, envía un POST para crear un nuevo cofre en la db de SQLite y actualiza la ventana con la lista de fuentes del nuevo cofre (inicialmente vacía). El panel lateral izquierdo permite gestionar las fuentes del cofre, contiene un botón para comprimir dicho panel y un botón para añadir nuevas fuentes, que muestra una ventana emergente que lleva al PASO 3 del diagrama de flujo. En dicha ventana, el usuario puede añadir varias fuentes de información en forma de texto plano, URLs o ficheros (el usuario mediante un botón puede ir subiendo fuentes, que se almacenen en un localstorage de JavaScript). Finalmente, la ventana contiene un botón de confirmación, si el usuario lo pulsa, la lista de fuentes del localstorage de Javascript se lleva al backend para ser procesada en los pasos del PASO 3, como el proceso puede llevar varios segundos, se debe de mostrar un círculo de carga que indique al usuario que se está procesando la información. Tras finalizar los pasos del PASO 3, la app vuelve a la ventana del PASO 2 realizando un GET de la lista de fuentes del cofre para reflejar la lista actualizada. Justo debajo del botón de añadir fuentes, se muestra la lista de fuentes, cada fuente es un widget que al enfocarse con el cursor o teclado permite eliminarlo de la db de SQLite mediante un DELETE, modificar su nombre mediante un PATCH o habilitar su uso en la respuesta del LLM por medio de una check box. El área principal muestra la conversación, el usuario envía una pregunta y se ejecutan los pasos del PASO 4 (que son los pasos de un sistema RAG convencional). Finalmente, se llega al PASO 5, que representa la respuesta del LLM.

El software debe de ejecutarse encima de contenedores de Docker, el fichero DOCKERARCH.md especifica los contenedores en los que se divide la aplicación, cómo se conectan entre sí y los volúmenes a crear que se explican a continuación:
- ./data/sqlite/jetrag.db: db de SQLite (esquema del fichero SQLSCHEMA.md).
- ./data/chroma/: base de datos vectorial de ChromaDB.
- ./triton/models/: modelos en su versión optimizada mediante TensorRT.
Para crear el fichero docker-compose.yml, puedes seguir la configuración que se muestra en la sección "Fichero docker-compose.yml" del fichero DOCKERARCH.md.


## Contexto técnico
- Stack tecnológico: puedes verlo en el fichero STACK.md.
- Base de datos: puedes ver el esquema en el fichero SQLSCHEMA.md.
- Convenciones del proyecto: Usa convenciones estándar.

## Requisitos del código
1.Código listo para producción, no ejemplos simplificados.
2.Incluir validación de inputs y manejo de errores completo.
3.Aplicar el principio de responsabilidad única.
4.Añadir tipos/interfaces cuando el lenguaje lo permita.
5.Incluir comentarios SÓLO donde la lógica no sea obvia.
6.Si necesitas alguna dependencia externa, indícala al inicio con el comando de instalación.
7.Los ficheros Dockerfile que consideres crear deben de reducir lo máximo posible el tamaño de la imagen resultante.

## Formato de entrega
Entrega el código en bloques separados por archivo, en el fichero TREE.md tienes un ejemplo de árbol de ficheros que puedes utilizar COMO BASE. Indica la ruta de cada archivo como encabezado. Al final, incluye una sección breve "Como probarlo" con los pasos exactos. También indica los comandos que se deben de ejecutar para compilar los modelos de LLM y de embeddings en una versión optimizada de TensorRT.