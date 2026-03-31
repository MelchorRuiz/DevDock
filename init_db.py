import os
from app import create_app, db
from app.models import Category, Tag, Tool

app = create_app()

with app.app_context():
    # Eliminar todas las tablas
    db.drop_all()
    
    # Crear todas las tablas
    db.create_all()
    
    # Crear categorías
    categories = [
        Category(name='Documentación'),
        Category(name='Snippets & Componentes'),
        Category(name='APIs & Testing'),
        Category(name='Deployment & Backend'),
    ]
    
    for category in categories:
        db.session.add(category)
    
    db.session.commit()
    
    # Crear herramientas para la categoría de Documentación
    docs_tools = [
        Tool(
            name='Docker Compose Visualizer',
            description='Automatically generates real-time topology maps from complex YAML definitions. Identifies circular dependencies and bottlenecks in service-to-service communication.',
            url='https://www.docker.com',
            favicon_url='https://www.google.com/s2/favicons?domain=www.docker.com&sz=64',
            category_id=1
        ),
        Tool(
            name='SVG Sprite Optimizer',
            description='Minifies and packs vector icons into memory-efficient spritesheets with dynamic ID mapping.',
            url='https://www.svgo.dev',
            favicon_url='https://www.google.com/s2/favicons?domain=www.svgo.dev&sz=64',
            category_id=1
        ),
        Tool(
            name='WebP Batcher',
            description='AI-driven lossy compression that maintains visual fidelity while reducing payload by up to 80%.',
            url='https://developers.google.com/speed/webp',
            favicon_url='https://www.google.com/s2/favicons?domain=developers.google.com&sz=64',
            category_id=1
        ),
        Tool(
            name='GitHook Orchestrator',
            description='Centralized control for pre-commit linting, security scans, and automated branch protection rules across multiple repositories.',
            url='https://git-scm.com',
            favicon_url='https://www.google.com/s2/favicons?domain=git-scm.com&sz=64',
            category_id=1
        ),
        Tool(
            name='API Stub Engine',
            description='Instantly mock REST or GraphQL endpoints with intelligent data seeding and delay simulation.',
            url='https://www.mockito.org',
            favicon_url='https://www.google.com/s2/favicons?domain=www.mockito.org&sz=64',
            category_id=1
        ),
    ]
    
    for tool in docs_tools:
        db.session.add(tool)
    
    # Crear herramientas para la categoría Snippets & Componentes
    snippets_tools = [
        Tool(
            name='React Component Library',
            description='Pre-built React components with Tailwind CSS styling and TypeScript support.',
            url='https://react.dev',
            favicon_url='https://www.google.com/s2/favicons?domain=react.dev&sz=64',
            category_id=2
        ),
        Tool(
            name='Vue.js Code Snippets',
            description='Reusable Vue.js components and composables for rapid development.',
            url='https://vuejs.org',
            favicon_url='https://www.google.com/s2/favicons?domain=vuejs.org&sz=64',
            category_id=2
        ),
    ]
    
    for tool in snippets_tools:
        db.session.add(tool)
    
    # Crear herramientas para la categoría APIs & Testing
    api_tools = [
        Tool(
            name='Postman API Testing',
            description='Complete API development and testing platform with automated testing capabilities.',
            url='https://www.postman.com',
            favicon_url='https://www.google.com/s2/favicons?domain=www.postman.com&sz=64',
            category_id=3
        ),
        Tool(
            name='Jest Testing Framework',
            description='JavaScript testing framework with a focus on simplicity and speed.',
            url='https://jestjs.io',
            favicon_url='https://www.google.com/s2/favicons?domain=jestjs.io&sz=64',
            category_id=3
        ),
    ]
    
    for tool in api_tools:
        db.session.add(tool)
    
    # Crear herramientas para la categoría Deployment & Backend
    deployment_tools = [
        Tool(
            name='Kubernetes Orchestration',
            description='Container orchestration platform for managing containerized applications at scale.',
            url='https://kubernetes.io',
            favicon_url='https://www.google.com/s2/favicons?domain=kubernetes.io&sz=64',
            category_id=4
        ),
        Tool(
            name='Docker Container Platform',
            description='Leading containerization platform for packaging and deploying applications.',
            url='https://www.docker.com',
            favicon_url='https://www.google.com/s2/favicons?domain=www.docker.com&sz=64',
            category_id=4
        ),
    ]
    
    for tool in deployment_tools:
        db.session.add(tool)

    db.session.commit()

    tags_by_name = {}
    for name in [
        'Docker', 'Visualizer', 'SVG', 'Optimization', 'Images', 'Git',
        'Hooks', 'API', 'Mocking', 'React', 'Vue', 'Testing', 'Kubernetes',
        'Backend'
    ]:
        tag = Tag(name=name)
        db.session.add(tag)
        tags_by_name[name] = tag

    db.session.flush()

    tool_tag_map = {
        'Docker Compose Visualizer': ['Docker', 'Visualizer'],
        'SVG Sprite Optimizer': ['SVG', 'Optimization'],
        'WebP Batcher': ['Images', 'Optimization'],
        'GitHook Orchestrator': ['Git', 'Hooks'],
        'API Stub Engine': ['API', 'Mocking'],
        'React Component Library': ['React'],
        'Vue.js Code Snippets': ['Vue'],
        'Postman API Testing': ['API', 'Testing'],
        'Jest Testing Framework': ['Testing'],
        'Kubernetes Orchestration': ['Kubernetes', 'Backend'],
        'Docker Container Platform': ['Docker', 'Backend'],
    }

    tools = Tool.query.all()
    tools_by_name = {tool.name: tool for tool in tools}
    for tool_name, tag_names in tool_tag_map.items():
        tool = tools_by_name.get(tool_name)
        if not tool:
            continue
        for tag_name in tag_names:
            tag = tags_by_name.get(tag_name)
            if tag:
                tool.tags.append(tag)
    
    db.session.commit()
    
    print('✅ Database initialized successfully with sample data!')
