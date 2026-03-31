from app import db

tool_tags = db.Table(
    'tool_tags',
    db.Column('tool_id', db.Integer, db.ForeignKey('tool.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Tool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(255), nullable=False)
    favicon_url = db.Column(db.String(255), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    embedding = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    category = db.relationship('Category', back_populates='tools')
    tags = db.relationship('Tag', secondary=tool_tags, back_populates='tools')
    
    
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    tools = db.relationship('Tool', back_populates='category')
    
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    tools = db.relationship('Tool', secondary=tool_tags, back_populates='tags')

class Suggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    raw_url = db.Column(db.String(255), nullable=False)
    suggested_by = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    ai_analysis = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
