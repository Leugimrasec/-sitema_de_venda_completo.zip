import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
import json

class NotificationService:
    def __init__(self):
        # Configurações de email (usando Gmail SMTP)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_user = "contatochavefinanceira@gmail.com"
        self.email_password = "(Ab2+jaconda1805)"  # Senha de app do Gmail configurada
        
        # WhatsApp API (simulado - pode ser integrado com serviços como Twilio)
        self.whatsapp_api_url = "https://api.whatsapp.com/send"
        
    def enviar_email_novo_pedido(self, cliente_dados, pedido_dados):
        """Envia email quando um novo pedido é criado"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = self.email_user  # Envia para o próprio email do vendedor
            msg['Subject'] = f"🔔 Novo Pedido - {cliente_dados['nome_completo']}"
            
            # Corpo do email
            corpo_email = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #1e40af; border-bottom: 2px solid #1e40af; padding-bottom: 10px;">
                        🎉 Novo Pedido Recebido!
                    </h2>
                    
                    <div style="background-color: #f8fafc; padding: 20px; border-radius: 10px; margin: 20px 0;">
                        <h3 style="color: #059669; margin-top: 0;">📋 Dados do Cliente</h3>
                        <p><strong>Nome:</strong> {cliente_dados['nome_completo']}</p>
                        <p><strong>CPF:</strong> {cliente_dados['cpf']}</p>
                        <p><strong>Email:</strong> {cliente_dados['email']}</p>
                        <p><strong>Telefone:</strong> {cliente_dados['telefone']}</p>
                    </div>
                    
                    <div style="background-color: #eff6ff; padding: 20px; border-radius: 10px; margin: 20px 0;">
                        <h3 style="color: #1e40af; margin-top: 0;">💰 Dados do Pedido</h3>
                        <p><strong>Pedido ID:</strong> #{pedido_dados['id']}</p>
                        <p><strong>Forma de Pagamento:</strong> {pedido_dados['forma_pagamento']}</p>
                        <p><strong>Valor:</strong> R$ {pedido_dados['valor']:.2f}</p>
                        <p><strong>Status:</strong> {pedido_dados['status']}</p>
                        <p><strong>Data:</strong> {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                    </div>
                    
                    {self._get_pix_info(pedido_dados) if pedido_dados['forma_pagamento'] == 'PIX' else ''}
                    
                    <div style="background-color: #fef3c7; padding: 20px; border-radius: 10px; margin: 20px 0;">
                        <h3 style="color: #d97706; margin-top: 0;">📱 Próximos Passos</h3>
                        <p>1. Aguarde o comprovante de pagamento via WhatsApp</p>
                        <p>2. Confirme o pagamento no painel administrativo</p>
                        <p>3. Envie a planilha para o email do cliente</p>
                        <p>
                            <a href="https://wa.me/55{cliente_dados['telefone'].replace('(', '').replace(')', '').replace(' ', '').replace('-', '')}" 
                               style="background-color: #25d366; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">
                                💬 Contatar via WhatsApp
                            </a>
                        </p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                        <p style="color: #6b7280; font-size: 14px;">
                            Este email foi gerado automaticamente pelo sistema de vendas da Planilha Financeira
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(corpo_email, 'html'))
            
            # Enviar email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_user, self.email_user, text)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Erro ao enviar email de novo pedido: {e}")
            return False
    
    def enviar_email_confirmacao_cliente(self, cliente_dados, pedido_dados):
        """Envia email de confirmação para o cliente"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = cliente_dados['email']
            msg['Subject'] = "✅ Pedido Confirmado - Planilha de Controle Financeiro"
            
            corpo_email = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #059669; border-bottom: 2px solid #059669; padding-bottom: 10px;">
                        ✅ Pedido Confirmado!
                    </h2>
                    
                    <p>Olá <strong>{cliente_dados['nome_completo']}</strong>,</p>
                    
                    <p>Seu pedido foi confirmado com sucesso! Aguarde que em breve enviaremos a planilha financeira para este email.</p>
                    
                    <div style="background-color: #f0fdf4; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #059669;">
                        <h3 style="color: #059669; margin-top: 0;">📋 Resumo do Pedido</h3>
                        <p><strong>Pedido:</strong> #{pedido_dados['id']}</p>
                        <p><strong>Produto:</strong> Planilha de Controle Financeiro</p>
                        <p><strong>Valor:</strong> R$ {pedido_dados['valor']:.2f}</p>
                        <p><strong>Forma de Pagamento:</strong> {pedido_dados['forma_pagamento']}</p>
                    </div>
                    
                    <div style="background-color: #eff6ff; padding: 20px; border-radius: 10px; margin: 20px 0;">
                        <h3 style="color: #1e40af; margin-top: 0;">📞 Suporte</h3>
                        <p>Se tiver alguma dúvida, entre em contato conosco:</p>
                        <p>📧 Email: {self.email_user}</p>
                        <p>📱 WhatsApp: (61) 99922-6353</p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <p style="color: #059669; font-weight: bold; font-size: 18px;">
                            Obrigado pela sua compra! 🎉
                        </p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                        <p style="color: #6b7280; font-size: 14px;">
                            Planilha de Controle Financeiro - Transforme sua vida financeira
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(corpo_email, 'html'))
            
            # Enviar email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_user, cliente_dados['email'], text)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Erro ao enviar email de confirmação para cliente: {e}")
            return False
    
    def enviar_email_notificacao_pagamento(self, cliente_dados, pedido_dados):
        """Envia email de notificação quando o cliente clica em 'Já Paguei'"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = self.email_user  # Envia para o próprio email do administrador
            msg['Subject'] = f"🔔 CLIENTE JÁ PAGOU - {cliente_dados['nome_completo']}"
            
            corpo_email = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #d97706; border-bottom: 2px solid #d97706; padding-bottom: 10px;">
                        ⚠️ Cliente Já Pagou - Verificação Necessária
                    </h2>
                    
                    <p style="font-size: 18px; font-weight: bold; color: #d97706;">
                        O cliente informou que já realizou o pagamento. Por favor, verifique se o dinheiro já caiu na sua conta ou verifique a conta de cartões.
                    </p>
                    
                    <div style="background-color: #f8fafc; padding: 20px; border-radius: 10px; margin: 20px 0;">
                        <h3 style="color: #059669; margin-top: 0;">📋 Dados do Cliente</h3>
                        <p><strong>Nome:</strong> {cliente_dados['nome_completo']}</p>
                        <p><strong>CPF:</strong> {cliente_dados['cpf']}</p>
                        <p><strong>Email:</strong> {cliente_dados['email']}</p>
                        <p><strong>Telefone:</strong> {cliente_dados['telefone']}</p>
                    </div>
                    
                    <div style="background-color: #eff6ff; padding: 20px; border-radius: 10px; margin: 20px 0;">
                        <h3 style="color: #1e40af; margin-top: 0;">💰 Dados do Pedido</h3>
                        <p><strong>Pedido ID:</strong> #{pedido_dados['id']}</p>
                        <p><strong>Forma de Pagamento:</strong> {pedido_dados['forma_pagamento']}</p>
                        <p><strong>Valor:</strong> R$ {pedido_dados['valor']:.2f}</p>
                        <p><strong>Status:</strong> Aguardando Confirmação</p>
                        <p><strong>Data:</strong> {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                    </div>
                    
                    <div style="background-color: #fef3c7; padding: 20px; border-radius: 10px; margin: 20px 0;">
                        <h3 style="color: #d97706; margin-top: 0;">📱 Próximos Passos</h3>
                        <p>1. Verifique se o pagamento foi recebido</p>
                        <p>2. Confirme o pagamento no painel administrativo</p>
                        <p>3. Envie a planilha para o email do cliente</p>
                        <p>
                            <a href="https://wa.me/55{cliente_dados['telefone'].replace('(', '').replace(')', '').replace(' ', '').replace('-', '')}" 
                               style="background-color: #25d366; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">
                                💬 Contatar Cliente via WhatsApp
                            </a>
                        </p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                        <p style="color: #6b7280; font-size: 14px;">
                            Este email foi gerado automaticamente pelo sistema de vendas da Planilha Financeira
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(corpo_email, 'html'))
            
            # Enviar email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_user, self.email_user, text)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Erro ao enviar email de notificação de pagamento: {e}")
            return False
    
    def enviar_notificacao_whatsapp(self, cliente_dados, pedido_dados):
        """Envia notificação básica via WhatsApp (simulado)"""
        try:
            # Esta é uma implementação simulada
            # Em produção, você usaria uma API como Twilio, WhatsApp Business API, etc.
            
            telefone = cliente_dados['telefone'].replace('(', '').replace(')', '').replace(' ', '').replace('-', '')
            mensagem = f"""🎉 Novo pedido recebido!
            
Cliente: {cliente_dados['nome_completo']}
Pedido: #{pedido_dados['id']}
Valor: R$ {pedido_dados['valor']:.2f}
Pagamento: {pedido_dados['forma_pagamento']}

Aguardando comprovante de pagamento."""
            
            # Log da notificação (em produção, enviaria via API)
            print(f"[WHATSAPP SIMULADO] Para: {telefone}")
            print(f"[WHATSAPP SIMULADO] Mensagem: {mensagem}")
            
            return True
            
        except Exception as e:
            print(f"Erro ao enviar notificação WhatsApp: {e}")
            return False
    
    def _get_pix_info(self, pedido_dados):
        """Retorna informações do PIX se aplicável"""
        if pedido_dados.get('chave_pix'):
            return f"""
            <div style="background-color: #fef3c7; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h3 style="color: #d97706; margin-top: 0;">🔑 Chave PIX Gerada</h3>
                <p><strong>Chave PIX:</strong></p>
                <div style="background-color: white; padding: 10px; border-radius: 5px; font-family: monospace; word-break: break-all; border: 1px solid #d1d5db;">
                    {pedido_dados['chave_pix']}
                </div>
                <p style="margin-top: 10px; color: #d97706; font-size: 14px;">
                    ⚠️ Esta chave PIX foi gerada especificamente para este pedido
                </p>
            </div>
            """
        return ""

# Instância global do serviço de notificações
notification_service = NotificationService()
