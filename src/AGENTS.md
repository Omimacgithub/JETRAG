Actúa como un desarrollador senior especializado en FastAPI con Svelte y ChromaDB.

## Contexto rápido
JETRAG es una aplicación WEB que permite a los usuarios interactuar con un chatbot RAG en el que utilizan cofres (concepto que me he inventado para denominar a conjuntos de fuentes de información como texto plano, URLs o ficheros) de manera local, lo que otorga seguridad especialmente cuando se trata con documentos críticos para una empresa. 

JETRAG debe permitir su despliegue en sistemas NVIDIA Jetson con 8 GB de RAM, por lo que su diseño e implementación debe de ser lo más simple y eficiente posible.

JETRAG es una aplicación WEB que mediante APIs de REST realiza una gestión de los cofres y sus fuentes (almacenados en una VectorDB).

Necesito que implementes lo siguiente:

## Funcionalidad
La app (JETRAG) se compone de dos pestañas, el flujo de cada pestaña y entre pestañas se muestra en la sección "Flujo Principal: Crear Cofre y Chatear" del fichero APPFLOW.md. El fichero ../design/prototypes/MAIN.png muestra un boceto de la pestaña del PASO 1 (el boceto es meramente orientativo), dicha pestaña muestra la lista de cofres creados recuperados de la VectorDB mediante un GET y muestra un botón para crear nuevos cofres, que se registran en la VectorDB mediante un POST y que hace que la app cambie a la pestaña del PASO 2. Cada cofre de la lista de cofres creados es un widget, que al enfocarse con el cursor o teclado permite eliminarlo de la VectorDB mediante un DELETE o modificar su nombre mediante un PATCH. Si se pulsa en uno de los widgets, se realiza un GET para recuperar la lista de fuentes de la VectorDB del cofre del widget y la app cambia a la pestaña del PASO 2.

El fichero ../design/prototypes/CHAT.png muestra un boceto de la pestaña del PASO 2 (el boceto es meramente orientativo). El panel lateral izquierdo permite gestionar las fuentes del cofre, contiene un botón para comprimir dicho panel y un botón para añadir nuevas fuentes, que muestra una ventana emergente que lleva al PASO 3 del diagrama de flujo. En dicha ventana, el usuario puede añadir varias fuentes de información en forma de texto plano, URLs o ficheros. Tras insertar y confirmar las fuentes, se recuperan en el backend mediante un POST para ser procesadas en los pasos del PASO 3, como el proceso puede llevar varios segundos, se debe de mostrar algún componente que indique al usuario que se está procesando la información. Tras finalizar los pasos del PASO 3, la app vuelve a la ventana del PASO 2 realizando un GET de la lista de fuentes del cofre para reflejar la lista actualizada. Justo debajo del botón de añadir fuentes, se muestra la lista de fuentes, cada fuente es un widget que al enfocarse con el cursor o teclado permite eliminarlo de la VectorDB mediante un DELETE o modificar su nombre mediante un PATCH

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

## Formato de entrega
Entrega el código en bloques separados por archivo, en el fichero TREE.md tienes un ejemplo de árbol de ficheros que puedes utilizar COMO BASE. Indica la ruta de cada archivo como
encabezado. Al final, incluye una sección breve "Como probarlo" con los pasos exactos.

(Es el PASO 3) Te dejo a tu elección cuando realizar la división de la información en chunks y su transformación en embeddings cuando el usuario añada una fuente. Para no dejar la interfaz congelada, implementa un aviso al usuario de que espere el tiempo necesario a que dichas operaciones se completen.