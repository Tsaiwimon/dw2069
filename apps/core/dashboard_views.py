import asyncio
import json
import threading
import uuid
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.http import JsonResponse, StreamingHttpResponse
from django.views.generic import TemplateView, View

from apps.ecommerce.models import Order, OrderItem

from .analytics import dashboard_snapshot


_dashboard_subscribers = {}
_subscriber_lock = threading.Lock()


def _recent_orders():
    orders = Order.objects.order_by('-created_at')[:12]
    return [
        {
            'order_number': order.order_number,
            'status': order.get_status_display(),
            'total': float(order.total),
            'created_at': order.created_at.isoformat(),
        }
        for order in orders
    ]


def _dashboard_event():
    return {
        'dashboard': dashboard_snapshot(),
        'orders': _recent_orders(),
    }


def publish_dashboard_update():
    event = _dashboard_event()
    with _subscriber_lock:
        subscribers = list(_dashboard_subscribers.items())
    for subscriber, loop in subscribers:
        loop.call_soon_threadsafe(subscriber.put_nowait, event)


async def _event_stream(key):
    subscriber = asyncio.Queue()
    loop = asyncio.get_running_loop()
    with _subscriber_lock:
        _dashboard_subscribers[subscriber] = loop
    event = await asyncio.to_thread(_dashboard_event)
    try:
        yield f'data: {json.dumps(event[key], ensure_ascii=False)}\n\n'
        while True:
            payload = await subscriber.get()
            yield f'data: {json.dumps(payload[key], ensure_ascii=False)}\n\n'
    finally:
        with _subscriber_lock:
            _dashboard_subscribers.pop(subscriber, None)


class DashboardView(TemplateView):
    template_name = 'dashboard/home.html'


class DashboardDataView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse(dashboard_snapshot())


class DashboardStreamView(View):
    def get(self, request, *args, **kwargs):
        response = StreamingHttpResponse(_event_stream('dashboard'), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response


class RealtimeTestView(TemplateView):
    template_name = 'dashboard/realtime_test.html'


class RealtimeTestDataView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({'orders': _recent_orders()})


class RealtimeTestStreamView(View):
    def get(self, request, *args, **kwargs):
        response = StreamingHttpResponse(_event_stream('orders'), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response


class RealtimeTestCreateView(View):
    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body or '{}')
            total = Decimal(str(payload.get('total', '0')))
            quantity = int(payload.get('quantity', 1))
            price = Decimal(str(payload.get('price', total)))
            if total <= 0 or quantity <= 0 or price <= 0:
                raise ValueError
        except (InvalidOperation, TypeError, ValueError, json.JSONDecodeError):
            return JsonResponse({'error': 'กรุณากรอกยอด จำนวน และราคาที่มากกว่า 0'}, status=400)

        product_name = str(payload.get('product_name') or 'สินค้าทดสอบ')[:255]
        with transaction.atomic():
            order = Order.objects.create(
                order_number=f'TEST-{uuid.uuid4().hex[:10].upper()}',
                status=payload.get('status', 'pos_completed'),
                subtotal=total,
                shipping_cost=Decimal('0'),
                discount=Decimal('0'),
                total=total,
                notes='สร้างจากหน้า Realtime Test',
            )
            OrderItem.objects.create(
                order=order,
                product_name=product_name,
                quantity=quantity,
                price=price,
            )
        try:
            publish_dashboard_update()
        except Exception:
            pass
        return JsonResponse({
            'success': True,
            'order_number': order.order_number,
            'total': float(order.total),
        }, status=201)