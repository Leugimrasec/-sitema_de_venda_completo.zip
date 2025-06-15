from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from src.models.user import db
from src.models.vendas import Cliente, Pedido, Visitante, EventoSite
from datetime import datetime, timedelta
from sqlalchemy import func, desc

admin_bp = Blueprint('admin', __name__)

# Credenciais simples para o admin (em produção, use um sistema mais seguro)
ADMIN_USER = 'admin'
ADMIN_PASSWORD = 'admin123'

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login do administrador"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USER and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            return render_template('admin/login.html', error='Credenciais inválidas')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    """Logout do administrador"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))

def admin_required(f):
    """Decorator para verificar se o admin está logado"""
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Dashboard principal do administrador"""
    try:
        # Estatísticas gerais
        total_visitantes = Visitante.query.count()
        total_pedidos = Pedido.query.count()
        pedidos_pagos = Pedido.query.filter_by(status='PAGO').count()
        receita_total = db.session.query(func.sum(Pedido.valor)).filter_by(status='PAGO').scalar() or 0
        
        # Visitantes hoje
        hoje = datetime.utcnow().date()
        visitantes_hoje = Visitante.query.filter(
            func.date(Visitante.data_visita) == hoje
        ).count()
        
        # Pedidos hoje
        pedidos_hoje = Pedido.query.filter(
            func.date(Pedido.data_pedido) == hoje
        ).count()
        
        # Últimos visitantes
        ultimos_visitantes = Visitante.query.order_by(desc(Visitante.data_visita)).limit(10).all()
        
        # Últimos pedidos
        ultimos_pedidos = Pedido.query.order_by(desc(Pedido.data_pedido)).limit(10).all()
        
        estatisticas = {
            'total_visitantes': total_visitantes,
            'total_pedidos': total_pedidos,
            'pedidos_pagos': pedidos_pagos,
            'receita_total': float(receita_total),
            'visitantes_hoje': visitantes_hoje,
            'pedidos_hoje': pedidos_hoje,
            'taxa_conversao': round((pedidos_pagos / total_visitantes * 100), 2) if total_visitantes > 0 else 0
        }
        
        return render_template('admin/dashboard.html', 
                             estatisticas=estatisticas,
                             ultimos_visitantes=ultimos_visitantes,
                             ultimos_pedidos=ultimos_pedidos)
    except Exception as e:
        return f"Erro ao carregar dashboard: {str(e)}", 500

@admin_bp.route('/pedidos')
@admin_required
def pedidos():
    """Lista todos os pedidos"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        pedidos_query = Pedido.query.order_by(desc(Pedido.data_pedido))
        pedidos_paginados = pedidos_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('admin/pedidos.html', pedidos=pedidos_paginados)
    except Exception as e:
        return f"Erro ao carregar pedidos: {str(e)}", 500

@admin_bp.route('/pedido/<int:pedido_id>')
@admin_required
def pedido_detalhes(pedido_id):
    """Detalhes de um pedido específico"""
    try:
        pedido = Pedido.query.get_or_404(pedido_id)
        return render_template('admin/pedido_detalhes.html', pedido=pedido)
    except Exception as e:
        return f"Erro ao carregar detalhes do pedido: {str(e)}", 500

@admin_bp.route('/confirmar-pagamento/<int:pedido_id>', methods=['POST'])
@admin_required
def confirmar_pagamento_admin(pedido_id):
    """Confirma o pagamento de um pedido pelo admin"""
    try:
        pedido = Pedido.query.get_or_404(pedido_id)
        
        pedido.status = 'PAGO'
        pedido.data_pagamento = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Pagamento confirmado'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/marcar-planilha-enviada/<int:pedido_id>', methods=['POST'])
@admin_required
def marcar_planilha_enviada(pedido_id):
    """Marca que a planilha foi enviada para o cliente"""
    try:
        pedido = Pedido.query.get_or_404(pedido_id)
        
        pedido.planilha_enviada = True
        pedido.data_envio_planilha = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Planilha marcada como enviada'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/visitantes')
@admin_required
def visitantes():
    """Lista todos os visitantes"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 50
        
        visitantes_query = Visitante.query.order_by(desc(Visitante.data_visita))
        visitantes_paginados = visitantes_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('admin/visitantes.html', visitantes=visitantes_paginados)
    except Exception as e:
        return f"Erro ao carregar visitantes: {str(e)}", 500

@admin_bp.route('/eventos')
@admin_required
def eventos():
    """Lista todos os eventos do site"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 50
        
        eventos_query = EventoSite.query.order_by(desc(EventoSite.data_evento))
        eventos_paginados = eventos_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('admin/eventos.html', eventos=eventos_paginados)
    except Exception as e:
        return f"Erro ao carregar eventos: {str(e)}", 500

@admin_bp.route('/api/estatisticas')
@admin_required
def api_estatisticas():
    """API para obter estatísticas em tempo real"""
    try:
        # Estatísticas dos últimos 7 dias
        sete_dias_atras = datetime.utcnow() - timedelta(days=7)
        
        visitantes_7_dias = Visitante.query.filter(
            Visitante.data_visita >= sete_dias_atras
        ).count()
        
        pedidos_7_dias = Pedido.query.filter(
            Pedido.data_pedido >= sete_dias_atras
        ).count()
        
        # Estatísticas por dia (últimos 7 dias)
        estatisticas_diarias = []
        for i in range(7):
            data = datetime.utcnow().date() - timedelta(days=i)
            visitantes_dia = Visitante.query.filter(
                func.date(Visitante.data_visita) == data
            ).count()
            pedidos_dia = Pedido.query.filter(
                func.date(Pedido.data_pedido) == data
            ).count()
            
            estatisticas_diarias.append({
                'data': data.strftime('%d/%m'),
                'visitantes': visitantes_dia,
                'pedidos': pedidos_dia
            })
        
        return jsonify({
            'success': True,
            'visitantes_7_dias': visitantes_7_dias,
            'pedidos_7_dias': pedidos_7_dias,
            'estatisticas_diarias': list(reversed(estatisticas_diarias))
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

