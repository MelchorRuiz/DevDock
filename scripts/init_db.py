import json
from urllib.parse import urlparse
from app import create_app, db
from app.models import Category, Tag, Tool

app = create_app()


def build_favicon_url(url):
    """Build the favicon URL for a given website URL."""
    domain = urlparse(url).netloc
    return f'https://www.google.com/s2/favicons?domain={domain}&sz=64'


seed_data = {
    'Documentación': [
        {
            'name': 'MDN Web Docs',
            'description': 'Documentación de referencia para HTML, CSS, JavaScript y APIs web.',
            'url': 'https://developer.mozilla.org',
            'tags': ['Docs', 'Frontend', 'JavaScript']
        },
        {
            'name': 'DevDocs',
            'description': 'Consolida documentación técnica de múltiples tecnologías en una sola interfaz.',
            'url': 'https://devdocs.io',
            'tags': ['Docs', 'Referencia']
        },
        {
            'name': 'Documentación oficial de React',
            'description': 'Guía y referencia oficial del framework React.',
            'url': 'https://react.dev',
            'tags': ['Docs', 'React', 'Framework']
        },
    ],
    'Educación': [
        {
            'name': 'Platzi',
            'description': 'Plataforma de cursos para desarrollo, diseño y habilidades digitales.',
            'url': 'https://platzi.com',
            'tags': ['Cursos', 'Educación']
        },
        {
            'name': 'Udemy',
            'description': 'Marketplace de cursos para programación, diseño y tecnología.',
            'url': 'https://www.udemy.com',
            'tags': ['Cursos', 'Educación']
        },
    ],
    'Snippets & Componentes': [
        {
            'name': 'UI Labs',
            'description': 'Colección de interfaces y componentes UI inspiracionales.',
            'url': 'https://www.uilabs.dev',
            'tags': ['UI', 'Componentes', 'Snippets']
        },
        {
            'name': 'Tailwind UI',
            'description': 'Componentes listos para producción construidos con Tailwind CSS.',
            'url': 'https://tailwindui.com',
            'tags': ['Tailwind', 'UI', 'Componentes']
        },
        {
            'name': 'CSS Glass',
            'description': 'Generador de estilos Glassmorphism para interfaces modernas.',
            'url': 'https://css.glass',
            'tags': ['CSS', 'Glassmorphism', 'Generador']
        },
    ],
    'APIs & Testing': [
        {
            'name': 'JSONPlaceholder',
            'description': 'API REST falsa para prototipos y pruebas rápidas.',
            'url': 'https://jsonplaceholder.typicode.com',
            'tags': ['API', 'Mock', 'Testing']
        },
        {
            'name': 'Postman Web',
            'description': 'Prueba, documenta y automatiza APIs desde el navegador.',
            'url': 'https://web.postman.co',
            'tags': ['API', 'Testing', 'Postman']
        },
        {
            'name': 'OWASP ZAP',
            'description': 'Herramienta de inspección de seguridad para aplicaciones web.',
            'url': 'https://www.zaproxy.org',
            'tags': ['Seguridad', 'Testing', 'Inspección']
        },
    ],
    'Deployment & Backend': [
        {
            'name': 'Render',
            'description': 'Servicio PaaS para desplegar aplicaciones y APIs fácilmente.',
            'url': 'https://render.com',
            'tags': ['Deployment', 'PaaS', 'Backend']
        },
        {
            'name': 'Supabase',
            'description': 'Base de datos serverless y backend open-source sobre Postgres.',
            'url': 'https://supabase.com',
            'tags': ['Backend', 'Database', 'Serverless']
        },
        {
            'name': 'Logtail',
            'description': 'Herramienta de gestión y observabilidad de logs en la nube.',
            'url': 'https://logtail.com',
            'tags': ['Logs', 'Observabilidad', 'Backend']
        },
    ],
    'Iconografía': [
        {
            'name': 'Lucide',
            'description': 'Set de iconos open-source y personalizable para productos digitales.',
            'url': 'https://lucide.dev',
            'tags': ['Iconos', 'UI']
        },
        {
            'name': 'Font Awesome',
            'description': 'Biblioteca popular de iconos para web y aplicaciones.',
            'url': 'https://fontawesome.com',
            'tags': ['Iconos', 'UI']
        },
        {
            'name': 'Flaticon',
            'description': 'Repositorio de iconos en distintos estilos y formatos.',
            'url': 'https://www.flaticon.com',
            'tags': ['Iconos', 'Recursos']
        },
    ],
    'Ilustraciones & 3D': [
        {
            'name': 'unDraw',
            'description': 'Ilustraciones open-source con colores personalizables.',
            'url': 'https://undraw.co',
            'tags': ['Ilustraciones', 'Diseño']
        },
        {
            'name': 'Spline',
            'description': 'Diseño y publicación de escenas 3D interactivas para web.',
            'url': 'https://spline.design',
            'tags': ['3D', 'Diseño']
        },
        {
            'name': 'Humaans',
            'description': 'Biblioteca de ilustraciones de personas para proyectos digitales.',
            'url': 'https://www.humaaans.com',
            'tags': ['Ilustraciones', 'Recursos']
        },
    ],
    'Tipografía': [
        {
            'name': 'Google Fonts',
            'description': 'Catálogo de tipografías web gratuitas y optimizadas.',
            'url': 'https://fonts.google.com',
            'tags': ['Fuentes', 'Diseño']
        },
        {
            'name': 'Fontjoy',
            'description': 'Generador de combinaciones tipográficas para interfaces y branding.',
            'url': 'https://fontjoy.com',
            'tags': ['Fuentes', 'Combinaciones']
        },
    ],
    'Colores': [
        {
            'name': 'Adobe Color',
            'description': 'Herramienta para crear y explorar armonías y paletas de color.',
            'url': 'https://color.adobe.com',
            'tags': ['Color', 'Paletas']
        },
        {
            'name': 'Coolors',
            'description': 'Generador rápido de paletas y tendencias de color.',
            'url': 'https://coolors.co',
            'tags': ['Color', 'Paletas']
        },
        {
            'name': 'CSS Gradient',
            'description': 'Generador visual de gradientes CSS para fondos y UI.',
            'url': 'https://cssgradient.io',
            'tags': ['Color', 'Gradientes', 'CSS']
        },
    ],
    'Imagen': [
        {
            'name': 'Squoosh',
            'description': 'Compresión y comparación de imágenes con diferentes codecs.',
            'url': 'https://squoosh.app',
            'tags': ['Imagen', 'Optimización']
        },
        {
            'name': 'Remove.bg',
            'description': 'Elimina fondos de imágenes automáticamente con IA.',
            'url': 'https://www.remove.bg',
            'tags': ['Imagen', 'IA']
        },
        {
            'name': 'TinyPNG',
            'description': 'Compresión eficiente de PNG y JPEG para web.',
            'url': 'https://tinypng.com',
            'tags': ['Imagen', 'Optimización']
        },
        {
            'name': 'Photopea',
            'description': 'Editor online de imágenes compatible con PSD y otros formatos.',
            'url': 'https://www.photopea.com',
            'tags': ['Imagen', 'Editor']
        },
    ],
    'Video': [
        {
            'name': 'Clideo Compress Video',
            'description': 'Compresor online para reducir peso de videos.',
            'url': 'https://clideo.com/compress-video',
            'tags': ['Video', 'Compresión']
        },
        {
            'name': 'CloudConvert Video to GIF',
            'description': 'Conversión de video a GIF desde el navegador.',
            'url': 'https://cloudconvert.com/video-to-gif',
            'tags': ['Video', 'GIF', 'Conversión']
        },
        {
            'name': 'Loom',
            'description': 'Grabación de pantalla y cámara para documentación y feedback.',
            'url': 'https://www.loom.com',
            'tags': ['Video', 'Grabación']
        },
    ],
    'PDF': [
        {
            'name': 'iLovePDF',
            'description': 'Suite online para unir, dividir, comprimir y convertir PDFs.',
            'url': 'https://www.ilovepdf.com',
            'tags': ['PDF', 'Documentos']
        },
        {
            'name': 'Smallpdf',
            'description': 'Herramientas de edición, compresión y conversión de PDF.',
            'url': 'https://smallpdf.com',
            'tags': ['PDF', 'Documentos']
        },
        {
            'name': 'DocuSign',
            'description': 'Firma digital de documentos y flujos de aprobación.',
            'url': 'https://www.docusign.com',
            'tags': ['PDF', 'Firma digital']
        },
    ],
    'Planificación': [
        {
            'name': 'Excalidraw',
            'description': 'Pizarra colaborativa para diagramas y wireframes rápidos.',
            'url': 'https://excalidraw.com',
            'tags': ['Planificación', 'Diagramas']
        },
        {
            'name': 'Trello',
            'description': 'Gestión de tareas estilo Kanban para equipos y proyectos.',
            'url': 'https://trello.com',
            'tags': ['Planificación', 'Kanban']
        },
        {
            'name': 'Readme.so',
            'description': 'Generador visual de README para repositorios.',
            'url': 'https://readme.so',
            'tags': ['Planificación', 'README']
        },
    ],
    'IA Tools': [
        {
            'name': 'ChatGPT',
            'description': 'Asistente de IA para ideación, redacción y soporte técnico.',
            'url': 'https://chatgpt.com',
            'tags': ['IA', 'Asistente']
        },
        {
            'name': 'Claude',
            'description': 'Asistente de IA para análisis, escritura y programación.',
            'url': 'https://claude.ai',
            'tags': ['IA', 'Asistente']
        },
        {
            'name': 'Perplexity',
            'description': 'Motor de respuestas con IA y referencias web.',
            'url': 'https://www.perplexity.ai',
            'tags': ['IA', 'Búsqueda']
        },
        {
            'name': 'PromptHero',
            'description': 'Repositorio y generador de prompts para modelos generativos.',
            'url': 'https://prompthero.com',
            'tags': ['IA', 'Prompts']
        },
    ],
    'Utilidades OS': [
        {
            'name': 'WeTransfer',
            'description': 'Transferencia rápida de archivos grandes sin registro obligatorio.',
            'url': 'https://wetransfer.com',
            'tags': ['Utilidades', 'Archivos']
        },
        {
            'name': 'Bitwarden Password Generator',
            'description': 'Generador de contraseñas seguras desde el navegador.',
            'url': 'https://bitwarden.com/password-generator',
            'tags': ['Utilidades', 'Seguridad', 'Contraseñas']
        },
    ],
}

with app.app_context():
    # Delete existing tables and data
    db.drop_all()
    
    # Create tables based on the models
    db.create_all()
    
    # Create categories first to establish relationships with tools
    categories_by_name = {}
    for category_name in seed_data:
        category = Category(name=category_name)
        db.session.add(category)
        categories_by_name[category_name] = category

    db.session.flush()

    # Create tools and associate them with categories and tags
    tags_by_name = {}
    for category_name, tools in seed_data.items():
        category = categories_by_name[category_name]
        for tool_data in tools:
            tool = Tool(
                name=tool_data['name'],
                description=tool_data['description'],
                url=tool_data['url'],
                favicon_url=build_favicon_url(tool_data['url']),
                category_id=category.id,
            )
            db.session.add(tool)

            for tag_name in tool_data.get('tags', []):
                tag = tags_by_name.get(tag_name)
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                    tags_by_name[tag_name] = tag
                tool.tags.append(tag)
    
    db.session.commit()
    
    print('✅ Database initialized with seed data successfully!')
    
    # Generate embeddings for all tools after they have been created
    print('\n📊 Generate embeddings for all tools...')
    tools = Tool.query.all()
    for tool in tools:
        if tool.generate_embedding():
            print(f'  ✓ Embedding generated for: {tool.name}')
        else:
            print(f'  ✗ Error generating embedding for {tool.name}')
    
    db.session.commit()
    print('✅ All embeddings generated and saved successfully!')
