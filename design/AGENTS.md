Actúa como un arquitecto de software senior con mas de 15 años de experiencia diseñando sistemas escalables.
Necesito que diseñes la arquitectura técnica completa para el siguiente proyecto:

## Proyecto
App web de un LLM chatbot que utiliza RAG (Retrieval Augmented Generation) para devolver respuestas razonadas en base a las fuentes que el usuario proporciona. La app permite su ejecución en dispositivos NVIDIA Jetson (ARM64 con GPUs) con máximo 8 Gigabytes de RAM.

## Problema a resolver
Este proyecto permite a los usuarios interactuar con un chatbot RAG en el que utilizan sus archivos de manera local, lo que otorga seguridad especialmente cuando se trata con documentos críticos para una empresa. El despliegue en sistemas NVIDIA Jetson permite mantener varios de los principios clave de este proyecto, que son el minimalismo y la eficiencia.

## Requisitos clave
- Usuarios esperados: 1
- Público objetivo: desarrolladores que quieran disponer de un servicio RAG completamente local.
- Tipo de aplicación: web.
- Restricciones técnicas: Python para el backend, NVIDIA Triton para ejecutar las inferencias del LLM y del modelo de embeddings, ambos modelos optimizados mediante NVIDIA TensorRT.
- La arquitectura debe de ser eficiente en el uso de la memoria RAM (sólo se disponen de 8 GB).
- Infraestructura: App desplegada en contenedores de Docker.

## Bocetos
El fichero prototypes/MAIN.png contiene un boceto de la página de inicio de la app. Se muestra la lista de cofres (se denomina cofre al conjunto de fuentes de información del usuario) ya creados por el usuario, al centrar el foco en uno de los elementos con el cursor o el teclado, se muestra un icono para eliminar el cofre. El texto "See all..." muestra todos los cofres creados por el usuario cuando se pulsa en este. Finalmente, el botón "Create new chest" permite crear un nuevo cofre.
Si se pulsa en uno de los elementos de la lista de cofres creados o se crea un nuevo cofre, la app pasa a una nueva vista. El fichero prototypes/CHAT.png contiene un boceto de dicha vista. A continuación te explico por puntos los aspectos de cada componente de la interfaz (no debes de seguirlos de forma estricta, tienes la libertad de adaptarlos según la tecnología de frontend que decidas escoger) y sus acciones:
- La barra superior de navegación contiene el nombre del cofre y un botón para crear un cofre (crea un conjunto vacío de fuentes, la página carga la información del nuevo conjunto vacío).
- El panel lateral izquierdo permite gestionar las fuentes del usuario. Contiene un botón para comprimir dicho panel, un botón para añadir nuevas fuentes (debe de permitir que el usuario añada una URL de una página web, texto plano o un fichero local y que quede registrado como una fuente) y una lista de widgets que representan las fuentes añadidas hasta el momento. Cada widget dispone de una check box que permite habilitar el uso de la fuente en las respuestas del LLM. Al enfocar un widget con el cursor o el teclado, se muestra un icono para elimina la fuente del cofre.
- Por último, el recuadro derecho es el propio chat en el que se muestran las preguntas y respuestas de la conversación. Simplemente debe otorga un recuadro para introducir las preguntas del usuario y un botón para enviarlas al LLM.

## Lo que necesito que entregues
1.Stack tecnológico recomendado: librería de Python que implemente RAG, frontend, base de datos para almacenar las fuentes de cada cofre y los embeddings de cada fuente, LLM como chatbot y modelo de embeddings para RAG. Se suele utilizar la librería LangChain para RAG, pero puedes utilizar otras si las consideras más eficientes.
Justifica cada elección en una línea, prioriza las tecnologías que mejor usen la memoria RAM.
2.Estructura de carpetas del proyecto: muestra el árbol de archivos inicial.
3.Modelo de datos: entidades principales, sus campos clave y relaciones.
4.Diagrama de flujo: describe paso a paso el flujo principal del usuario (de la forma: Paso 1 -> Paso 2 -> ...). La sección Bocetos de este fichero puede darte una base sólida.
5.Decisiones de diseño: lista las 3-5 decisiones arquitectónicas más importantes que has tomado y por qué.
6.Riesgos técnicos: identifica 2-3 posibles problemas y como mitigarlos.