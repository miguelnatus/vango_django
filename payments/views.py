from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.db import transaction

from .models import Payment, PaymentMethod, Coupon, CouponUsage
from bookings.models import Booking
from .forms import PaymentMethodForm, CreditCardPaymentForm, PixPaymentForm, BankSlipPaymentForm

import json
import uuid
import requests
from decimal import Decimal

# Configurações de gateway de pagamento (em produção, use variáveis de ambiente)
PAYMENT_GATEWAY_API_KEY = getattr(settings, 'PAYMENT_GATEWAY_API_KEY', 'test_api_key')
PAYMENT_GATEWAY_URL = getattr(settings, 'PAYMENT_GATEWAY_URL', 'https://api.sandbox.gateway.com/v1')

@login_required
def payment_methods_list(request):
    """
    Lista os métodos de pagamento do usuário.
    """
    payment_methods = PaymentMethod.objects.filter(user=request.user)
    
    return render(request, 'payments/payment_methods_list.html', {
        'payment_methods': payment_methods
    })

@login_required
def payment_method_add(request):
    """
    Adiciona um novo método de pagamento.
    """
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            payment_method = form.save(commit=False)
            payment_method.user = request.user
            
            # Processar dados do cartão de forma segura
            if payment_method.type in ['credit_card', 'debit_card']:
                try:
                    # Em produção, use HTTPS e tokenização segura
                    card_number = form.cleaned_data.get('card_number')
                    card_cvv = form.cleaned_data.get('card_cvv')
                    
                    # Simular chamada para gateway de pagamento para tokenização
                    # Em produção, use uma biblioteca segura para isso
                    card_token = f"tok_{uuid.uuid4().hex}"
                    
                    # Armazenar apenas dados seguros
                    payment_method.card_token = card_token
                    payment_method.card_last_digits = card_number[-4:] if card_number else None
                    payment_method.card_brand = detect_card_brand(card_number)
                    
                    # Não armazenar número completo do cartão ou CVV
                except Exception as e:
                    messages.error(request, f"Erro ao processar o cartão: {str(e)}")
                    return render(request, 'payments/payment_method_add.html', {'form': form})
            
            payment_method.save()
            messages.success(request, "Método de pagamento adicionado com sucesso!")
            return redirect('payments:payment_methods_list')
    else:
        form = PaymentMethodForm()
    
    return render(request, 'payments/payment_method_add.html', {
        'form': form
    })

@login_required
def payment_method_delete(request, method_id):
    """
    Remove um método de pagamento.
    """
    payment_method = get_object_or_404(PaymentMethod, id=method_id, user=request.user)
    
    if request.method == 'POST':
        payment_method.delete()
        messages.success(request, "Método de pagamento removido com sucesso!")
        return redirect('payments:payment_methods_list')
    
    return render(request, 'payments/payment_method_delete.html', {
        'payment_method': payment_method
    })

@login_required
def payment_method_set_default(request, method_id):
    """
    Define um método de pagamento como padrão.
    """
    payment_method = get_object_or_404(PaymentMethod, id=method_id, user=request.user)
    
    # O método save() já cuida de remover o status de padrão de outros métodos
    payment_method.is_default = True
    payment_method.save()
    
    messages.success(request, "Método de pagamento definido como padrão!")
    return redirect('payments:payment_methods_list')

@login_required
def checkout(request, booking_id):
    """
    Página de checkout para uma reserva.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Verificar se a reserva já foi paga
    if hasattr(booking, 'payment') and booking.payment.is_paid:
        messages.info(request, "Esta reserva já foi paga.")
        return redirect('bookings:detail', booking_id=booking.id)
    
    # Verificar se a reserva está pendente
    if booking.status != 'pending':
        messages.error(request, "Esta reserva não está disponível para pagamento.")
        return redirect('bookings:detail', booking_id=booking.id)
    
    # Obter métodos de pagamento do usuário
    payment_methods = PaymentMethod.objects.filter(user=request.user)
    default_payment_method = payment_methods.filter(is_default=True).first()
    
    # Verificar cupom aplicado
    applied_coupon = None
    discount_amount = Decimal('0.00')
    
    if 'coupon_code' in request.session:
        coupon_code = request.session['coupon_code']
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_valid:
                # Verificar se é primeira compra (se necessário)
                if coupon.is_first_purchase_only and Payment.objects.filter(user=request.user, status='approved').exists():
                    messages.warning(request, "Este cupom é válido apenas para primeira compra.")
                else:
                    # Verificar se a rota é elegível (se aplicável)
                    if coupon.applicable_routes.exists() and not coupon.applicable_routes.filter(id=booking.route.id).exists():
                        messages.warning(request, "Este cupom não é válido para esta rota.")
                    else:
                        applied_coupon = coupon
                        discount_amount = coupon.calculate_discount(booking.total_price)
        except Coupon.DoesNotExist:
            pass
    
    # Calcular valor final
    final_amount = booking.total_price - discount_amount
    if final_amount < 0:
        final_amount = Decimal('0.00')
    
    # Formulários de pagamento
    credit_card_form = CreditCardPaymentForm()
    pix_form = PixPaymentForm()
    bank_slip_form = BankSlipPaymentForm()
    
    if request.method == 'POST':
        payment_method_type = request.POST.get('payment_method_type')
        
        # Processar pagamento com base no método escolhido
        if payment_method_type == 'saved_card' and request.POST.get('payment_method_id'):
            # Pagamento com cartão salvo
            payment_method_id = request.POST.get('payment_method_id')
            payment_method = get_object_or_404(PaymentMethod, id=payment_method_id, user=request.user)
            
            # Criar pagamento
            payment = create_payment(
                booking=booking,
                user=request.user,
                amount=final_amount,
                payment_method='credit_card' if payment_method.type == 'credit_card' else 'debit_card',
                card_token=payment_method.card_token,
                card_last_digits=payment_method.card_last_digits,
                card_brand=payment_method.card_brand
            )
            
            # Aplicar cupom, se houver
            if applied_coupon:
                apply_coupon(booking, applied_coupon, discount_amount)
                del request.session['coupon_code']
            
            # Redirecionar para página de confirmação
            return redirect('payments:payment_confirmation', payment_id=payment.id)
            
        elif payment_method_type == 'new_card':
            # Pagamento com novo cartão
            form = CreditCardPaymentForm(request.POST)
            if form.is_valid():
                # Processar dados do cartão de forma segura
                try:
                    card_number = form.cleaned_data.get('card_number')
                    card_holder = form.cleaned_data.get('card_holder')
                    card_expiry_month = form.cleaned_data.get('card_expiry_month')
                    card_expiry_year = form.cleaned_data.get('card_expiry_year')
                    card_cvv = form.cleaned_data.get('card_cvv')
                    save_card = form.cleaned_data.get('save_card')
                    
                    # Simular chamada para gateway de pagamento para tokenização
                    card_token = f"tok_{uuid.uuid4().hex}"
                    card_last_digits = card_number[-4:] if card_number else None
                    card_brand = detect_card_brand(card_number)
                    
                    # Salvar cartão se solicitado
                    if save_card:
                        payment_method = PaymentMethod(
                            user=request.user,
                            type='credit_card',
                            card_token=card_token,
                            card_last_digits=card_last_digits,
                            card_brand=card_brand,
                            card_holder_name=card_holder,
                            card_expiry_month=card_expiry_month,
                            card_expiry_year=card_expiry_year
                        )
                        payment_method.save()
                    
                    # Criar pagamento
                    payment = create_payment(
                        booking=booking,
                        user=request.user,
                        amount=final_amount,
                        payment_method='credit_card',
                        card_token=card_token,
                        card_last_digits=card_last_digits,
                        card_brand=card_brand
                    )
                    
                    # Aplicar cupom, se houver
                    if applied_coupon:
                        apply_coupon(booking, applied_coupon, discount_amount)
                        del request.session['coupon_code']
                    
                    # Redirecionar para página de confirmação
                    return redirect('payments:payment_confirmation', payment_id=payment.id)
                    
                except Exception as e:
                    messages.error(request, f"Erro ao processar o pagamento: {str(e)}")
            else:
                credit_card_form = form
                
        elif payment_method_type == 'pix':
            # Pagamento com PIX
            form = PixPaymentForm(request.POST)
            if form.is_valid():
                # Criar pagamento
                payment = create_payment(
                    booking=booking,
                    user=request.user,
                    amount=final_amount,
                    payment_method='pix'
                )
                
                # Gerar QR code do PIX (simulação)
                pix_qr_code = f"00020126330014BR.GOV.BCB.PIX0111{uuid.uuid4().hex}5204000053039865802BR5913VanGo Turismo6008Sao Paulo62070503***63041234"
                pix_expiration = timezone.now() + timezone.timedelta(hours=24)
                
                payment.pix_qr_code = pix_qr_code
                payment.pix_expiration = pix_expiration
                payment.save()
                
                # Aplicar cupom, se houver
                if applied_coupon:
                    apply_coupon(booking, applied_coupon, discount_amount)
                    del request.session['coupon_code']
                
                # Redirecionar para página de confirmação
                return redirect('payments:payment_confirmation', payment_id=payment.id)
            else:
                pix_form = form
                
        elif payment_method_type == 'bank_slip':
            # Pagamento com boleto
            form = BankSlipPaymentForm(request.POST)
            if form.is_valid():
                # Criar pagamento
                payment = create_payment(
                    booking=booking,
                    user=request.user,
                    amount=final_amount,
                    payment_method='bank_slip'
                )
                
                # Gerar boleto (simulação)
                bank_slip_url = f"https://api.sandbox.gateway.com/boletos/{uuid.uuid4().hex}"
                bank_slip_expiration = timezone.now() + timezone.timedelta(days=3)
                
                payment.bank_slip_url = bank_slip_url
                payment.bank_slip_expiration = bank_slip_expiration
                payment.save()
                
                # Aplicar cupom, se houver
                if applied_coupon:
                    apply_coupon(booking, applied_coupon, discount_amount)
                    del request.session['coupon_code']
                
                # Redirecionar para página de confirmação
                return redirect('payments:payment_confirmation', payment_id=payment.id)
            else:
                bank_slip_form = form
    
    return render(request, 'payments/checkout.html', {
        'booking': booking,
        'payment_methods': payment_methods,
        'default_payment_method': default_payment_method,
        'applied_coupon': applied_coupon,
        'discount_amount': discount_amount,
        'final_amount': final_amount,
        'credit_card_form': credit_card_form,
        'pix_form': pix_form,
        'bank_slip_form': bank_slip_form
    })

@login_required
def apply_coupon(request, booking_id):
    """
    Aplica um cupom de desconto a uma reserva.
    """
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        
        if not coupon_code:
            return JsonResponse({'success': False, 'message': 'Código de cupom inválido.'})
        
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            
            if not coupon.is_valid:
                return JsonResponse({'success': False, 'message': 'Este cupom expirou ou atingiu o limite de uso.'})
            
            # Verificar se é primeira compra (se necessário)
            if coupon.is_first_purchase_only and Payment.objects.filter(user=request.user, status='approved').exists():
                return JsonResponse({'success': False, 'message': 'Este cupom é válido apenas para primeira compra.'})
            
            booking = get_object_or_404(Booking, id=booking_id, user=request.user)
            
            # Verificar se a rota é elegível (se aplicável)
            if coupon.applicable_routes.exists() and not coupon.applicable_routes.filter(id=booking.route.id).exists():
                return JsonResponse({'success': False, 'message': 'Este cupom não é válido para esta rota.'})
            
            # Calcular desconto
            discount_amount = coupon.calculate_discount(booking.total_price)
            
            # Armazenar cupom na sessão
            request.session['coupon_code'] = coupon_code
            
            return JsonResponse({
                'success': True,
                'message': 'Cupom aplicado com sucesso!',
                'discount_amount': float(discount_amount),
                'final_amount': float(booking.total_price - discount_amount)
            })
            
        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Cupom não encontrado.'})
    
    return JsonResponse({'success': False, 'message': 'Método não permitido.'})

@login_required
def remove_coupon(request, booking_id):
    """
    Remove um cupom de desconto aplicado.
    """
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
    
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    return JsonResponse({
        'success': True,
        'message': 'Cupom removido com sucesso!',
        'final_amount': float(booking.total_price)
    })

@login_required
def payment_confirmation(request, payment_id):
    """
    Página de confirmação de pagamento.
    """
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    return render(request, 'payments/payment_confirmation.html', {
        'payment': payment,
        'booking': payment.booking
    })

@login_required
def payment_webhook(request):
    """
    Webhook para receber notificações de pagamento do gateway.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método não permitido.'})
    
    # Verificar assinatura do webhook (em produção)
    # ...
    
    try:
        data = json.loads(request.body)
        transaction_id = data.get('transaction_id')
        status = data.get('status')
        
        payment = Payment.objects.get(transaction_id=transaction_id)
        
        if status == 'approved':
            payment.approve(gateway_response=data)
        elif status == 'declined':
            payment.decline(gateway_response=data)
        elif status == 'refunded':
            payment.refund(gateway_response=data)
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
def payment_history(request):
    """
    Histórico de pagamentos do usuário.
    """
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'payments/payment_history.html', {
        'payments': payments
    })

@login_required
def payment_detail(request, payment_id):
    """
    Detalhes de um pagamento.
    """
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    return render(request, 'payments/payment_detail.html', {
        'payment': payment,
        'booking': payment.booking
    })

# Funções auxiliares

def create_payment(booking, user, amount, payment_method, card_token=None, card_last_digits=None, card_brand=None):
    """
    Cria um novo pagamento e processa através do gateway.
    """
    with transaction.atomic():
        # Criar pagamento no banco de dados
        payment = Payment(
            user=user,
            booking=booking,
            amount=amount,
            status='processing',
            payment_method=payment_method,
            card_last_digits=card_last_digits,
            card_brand=card_brand
        )
        payment.save()
        
        # Processar pagamento no gateway (simulação)
        try:
            # Em produção, use uma biblioteca segura para isso
            payload = {
                'amount': float(amount),
                'currency': 'BRL',
                'payment_method': payment_method,
                'description': f'Reserva #{booking.id} - VanGo',
                'customer': {
                    'name': user.get_full_name(),
                    'email': user.email
                }
            }
            
            if payment_method in ['credit_card', 'debit_card'] and card_token:
                payload['card'] = {
                    'token': card_token
                }
            
            # Simular resposta do gateway
            transaction_id = f"txn_{uuid.uuid4().hex}"
            gateway_response = {
                'id': transaction_id,
                'status': 'approved',  # Em produção, isso viria do gateway
                'amount': float(amount),
                'currency': 'BRL',
                'created_at': timezone.now().isoformat()
            }
            
            # Atualizar pagamento com resposta do gateway
            payment.transaction_id = transaction_id
            payment.gateway_response = gateway_response
            
            # Em produção, o status seria atualizado pelo webhook
            # Para fins de demonstração, vamos aprovar automaticamente
            payment.approve(transaction_id=transaction_id, gateway_response=gateway_response)
            
            return payment
            
        except Exception as e:
            # Em caso de erro, marcar pagamento como recusado
            payment.status = 'declined'
            payment.gateway_response = {'error': str(e)}
            payment.save()
            raise

def apply_coupon(booking, coupon, discount_amount):
    """
    Aplica um cupom a uma reserva.
    """
    with transaction.atomic():
        # Registrar uso do cupom
        coupon_usage = CouponUsage(
            coupon=coupon,
            user=booking.user,
            booking=booking,
            discount_amount=discount_amount
        )
        coupon_usage.save()
        
        # Incrementar contador de uso do cupom
        coupon.use()

def detect_card_brand(card_number):
    """
    Detecta a bandeira do cartão com base no número.
    """
    if not card_number:
        return None
        
    # Simplificado para demonstração
    if card_number.startswith('4'):
        return 'Visa'
    elif card_number.startswith('5'):
        return 'Mastercard'
    elif card_number.startswith('3'):
        return 'American Express'
    elif card_number.startswith('6'):
        return 'Discover'
    else:
        return 'Outra'
