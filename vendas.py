from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(14), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com pedidos
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome_completo': self.nome_completo,
            'cpf': self.cpf,
            'email': self.email,
            'telefone': self.telefone,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None
        }

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    forma_pagamento = db.Column(db.String(50), nullable=False)  # PIX, CREDITO, DEBITO, BOLETO
    valor = db.Column(db.Float, nullable=False, default=50.00)
    status = db.Column(db.String(50), nullable=False, default='PENDENTE')  # PENDENTE, PAGO, CANCELADO
    chave_pix = db.Column(db.String(500), nullable=True)  # Para armazenar chave PIX aleatória
    data_pedido = db.Column(db.DateTime, default=datetime.utcnow)
    data_pagamento = db.Column(db.DateTime, nullable=True)
    planilha_enviada = db.Column(db.Boolean, default=False)
    data_envio_planilha = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'forma_pagamento': self.forma_pagamento,
            'valor': float(self.valor),
            'status': self.status,
            'chave_pix': self.chave_pix,
            'data_pedido': self.data_pedido.isoformat() if self.data_pedido else None,
            'data_pagamento': self.data_pagamento.isoformat() if self.data_pagamento else None,
            'planilha_enviada': self.planilha_enviada,
            'data_envio_planilha': self.data_envio_planilha.isoformat() if self.data_envio_planilha else None,
            'cliente': self.cliente.to_dict() if self.cliente else None
        }

class Visitante(db.Model):
    __tablename__ = 'visitantes'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.Text, nullable=True)
    referrer = db.Column(db.String(500), nullable=True)
    pagina_visitada = db.Column(db.String(500), nullable=False)
    data_visita = db.Column(db.DateTime, default=datetime.utcnow)
    tempo_permanencia = db.Column(db.Integer, nullable=True)  # em segundos
    
    def to_dict(self):
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'referrer': self.referrer,
            'pagina_visitada': self.pagina_visitada,
            'data_visita': self.data_visita.isoformat() if self.data_visita else None,
            'tempo_permanencia': self.tempo_permanencia
        }

class EventoSite(db.Model):
    __tablename__ = 'eventos_site'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo_evento = db.Column(db.String(100), nullable=False)  # CLIQUE_COMPRAR, CLIQUE_PIX, CLIQUE_CREDITO, etc.
    ip_address = db.Column(db.String(45), nullable=False)
    dados_evento = db.Column(db.Text, nullable=True)  # JSON com dados adicionais
    data_evento = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo_evento': self.tipo_evento,
            'ip_address': self.ip_address,
            'dados_evento': self.dados_evento,
            'data_evento': self.data_evento.isoformat() if self.data_evento else None
        }

