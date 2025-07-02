// JavaScript atualizado para o site da Chave Financeira Libertadora
// Inclui integração com WhatsApp, email e painel administrativo

document.addEventListener("DOMContentLoaded", function() {
    console.log("Site da Chave Financeira Libertadora carregado!");
    
    // Configurações
    const config = {
        whatsappNumber: "5561999226352",
        emailContato: "contatochavefinanceira@gmail.com",
        pixCode: "00020126880014br.gov.bcb.pix0136a5b7ad4f-5918-4fc1-aa7a-a631afa24c260226Planilha chave financeira 520400005303986540550.005802BR5924Miguel Cesar Fernandes F6008Brasilia62230519daqr2612692379253246304CA3B",
        getnetUrl: "https://pag.getnet.com.br/N-p06-imYx",
        backendUrl: "https://5002-ijsji8ctydf972e82yg20-73f4c340.manusvm.computer"
    };

    // Função para abrir modal de compra
    window.abrirModalCompra = function() {
        document.getElementById('modal-compra').style.display = 'block';
        registrarEvento('modal_compra_aberto');
    };

    // Função para abrir modal "Já Paguei"
    window.abrirModalJaPaguei = function() {
        document.getElementById('modal-ja-paguei').style.display = 'block';
        registrarEvento('modal_ja_paguei_aberto');
    };

    // Função para fechar modais
    window.fecharModal = function(modalId) {
        document.getElementById(modalId).style.display = 'none';
    };

    // Função para copiar código PIX
    window.copiarPix = function() {
        const codigoPix = document.getElementById('codigo-pix');
        codigoPix.select();
        codigoPix.setSelectionRange(0, 99999);
        document.execCommand('copy');
        
        // Feedback visual
        const btnCopiar = document.querySelector('.btn-copiar');
        const textoOriginal = btnCopiar.textContent;
        btnCopiar.textContent = 'Copiado!';
        btnCopiar.style.backgroundColor = '#27ae60';
        
        setTimeout(() => {
            btnCopiar.textContent = textoOriginal;
            btnCopiar.style.backgroundColor = '';
        }, 2000);

        registrarEvento('pix_copiado');
    };

    // Função para confirmar pagamento PIX
    window.confirmarPagamentoPix = function() {
        fecharModal('modal-pix');
        abrirModalJaPaguei();
        registrarEvento('confirmacao_pagamento_pix');
    };

    // Função para registrar eventos no backend
    function registrarEvento(evento, dados = {}) {
        const dadosEvento = {
            evento: evento,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            userAgent: navigator.userAgent,
            ...dados
        };

        fetch(`${config.backendUrl}/api/registrar-evento`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(dadosEvento)
        }).catch(error => {
            console.log('Erro ao registrar evento:', error);
        });
    }

    // Função para registrar cliente
    function registrarCliente(dadosCliente) {
        return fetch(`${config.backendUrl}/api/registrar-cliente`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(dadosCliente)
        }).catch(error => {
            console.log('Erro ao registrar cliente:', error);
            return { ok: false };
        });
    }

    // Função para enviar notificação por email
    function enviarNotificacaoEmail(dadosCliente, tipoPagamento) {
        const dadosEmail = {
            destinatario: config.emailContato,
            assunto: `Nova compra - Chave Financeira Libertadora`,
            corpo:                 Nova compra realizada:
                
                Nome: ${dadosCliente.nome}
                WhatsApp: ${dadosCliente.whatsapp}
                Forma de Pagamento: ${tipoPagamento}
                Data: ${new Date().toLocaleString(\'pt-BR\')}
                
                ${tipoPagamento === \'PIX\' ? \'Cliente solicitou confirmação de pagamento PIX. Por favor, envie seu e-mail para que possamos enviar a planilha.\' : \'Pagamento via cartão processado.\'}
            `   };

        fetch(`${config.backendUrl}/api/enviar-email`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(dadosEmail)
        }).catch(error => {
            console.log('Erro ao enviar email:', error);
        });
    }

    // Handler do formulário de compra
    const formCompra = document.getElementById('form-compra');
    if (formCompra) {
        formCompra.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(formCompra);
            const dadosCliente = {
                nome: formData.get('nome'),
                email: formData.get('email'),
                whatsapp: formData.get('whatsapp'),
                formaPagamento: formData.get('pagamento'),
                timestamp: new Date().toISOString()
            };

            // Validações
            if (!dadosCliente.nome || !dadosCliente.email || !dadosCliente.whatsapp || !dadosCliente.formaPagamento) {
                alert('Por favor, preencha todos os campos obrigatórios.');
                return;
            }

            // Registrar cliente no backend
            try {
                await registrarCliente(dadosCliente);
                registrarEvento('cliente_registrado', dadosCliente);
            } catch (error) {
                console.log('Erro ao registrar cliente:', error);
            }

            // Processar pagamento
            if (dadosCliente.formaPagamento === 'pix') {
                fecharModal('modal-compra');
                document.getElementById('modal-pix').style.display = 'block';
                registrarEvento('pagamento_pix_iniciado', dadosCliente);
                enviarNotificacaoEmail(dadosCliente, 'PIX');
            } else if (dadosCliente.formaPagamento === 'cartao') {
                // Redirecionar para Getnet
                registrarEvento('pagamento_cartao_iniciado', dadosCliente);
                enviarNotificacaoEmail(dadosCliente, 'Cartão');
                window.open(config.getnetUrl, '_blank');
                
                // Mostrar modal de sucesso
                fecharModal('modal-compra');
                document.getElementById('modal-sucesso').style.display = 'block';
            }
        });
    }

    // Smooth scroll para links internos
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Fechar modais clicando fora
    window.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });

    // Máscara para WhatsApp
    const whatsappInput = document.getElementById('whatsapp');
    if (whatsappInput) {
        whatsappInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 11) {
                value = value.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
            } else if (value.length >= 7) {
                value = value.replace(/(\d{2})(\d{4})(\d{0,4})/, '($1) $2-$3');
            } else if (value.length >= 3) {
                value = value.replace(/(\d{2})(\d{0,5})/, '($1) $2');
            }
            e.target.value = value;
        });
    }

    // Registrar visita à página
    registrarEvento('visita_pagina');

    // Registrar cliques nos botões principais
    document.querySelectorAll('.btn-primary, .btn-comprar-agora').forEach(btn => {
        btn.addEventListener('click', () => {
            registrarEvento('clique_botao_comprar');
        });
    });

    document.querySelectorAll('.btn-ja-paguei').forEach(btn => {
        btn.addEventListener('click', () => {
            registrarEvento('clique_botao_ja_paguei');
        });
    });

    // FAQ Toggle
    document.querySelectorAll('.faq-question').forEach(question => {
        question.addEventListener('click', function() {
            const faqItem = this.parentElement;
            const answer = faqItem.querySelector('.faq-answer');
            const icon = this.querySelector('i');
            
            faqItem.classList.toggle('active');
            
            if (faqItem.classList.contains('active')) {
                answer.style.maxHeight = answer.scrollHeight + 'px';
                icon.style.transform = 'rotate(180deg)';
            } else {
                answer.style.maxHeight = '0';
                icon.style.transform = 'rotate(0deg)';
            }
        });
    });

    console.log("Todas as funcionalidades carregadas com sucesso!");
});

