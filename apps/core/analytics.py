"""ClickHouse-backed analytics with a Django fallback."""
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Count, Sum
from django.db.models.functions import TruncHour
from django.utils import timezone

from apps.ecommerce.models import Order, OrderItem, ProductVariant
from apps.logistics.models import Shipment


def _setting(name, default):
    return getattr(settings, name, default)


def _client():
    import clickhouse_connect

    return clickhouse_connect.get_client(
        host=_setting('CLICKHOUSE_HOST', 'localhost'),
        port=int(_setting('CLICKHOUSE_PORT', 8123)),
        username=_setting('CLICKHOUSE_USER', 'default'),
        password=_setting('CLICKHOUSE_PASSWORD', ''),
        database=_setting('CLICKHOUSE_DB', 'default'),
        connect_timeout=2,
        send_receive_timeout=2,
    )


def _ensure_table(client):
    client.command('''
        CREATE TABLE IF NOT EXISTS order_events (
            order_number String,
            created_at DateTime,
            updated_at DateTime,
            status LowCardinality(String),
            subtotal Decimal(18, 2),
            shipping_cost Decimal(18, 2),
            discount Decimal(18, 2),
            total Decimal(18, 2)
        ) ENGINE = ReplacingMergeTree(updated_at)
        ORDER BY order_number
    ''')


def _sync_orders(client):
    _ensure_table(client)
    result = client.query('SELECT max(updated_at) FROM order_events')
    last_updated = result.result_rows[0][0] if result.result_rows else None
    orders = Order.objects.all().order_by('updated_at')
    if last_updated:
        orders = orders.filter(updated_at__gt=last_updated)
    rows = [
        [
            order.order_number,
            order.created_at,
            order.updated_at,
            order.status,
            Decimal(order.subtotal),
            Decimal(order.shipping_cost),
            Decimal(order.discount),
            Decimal(order.total),
        ]
        for order in orders.iterator()
    ]
    if rows:
        client.insert(
            'order_events',
            rows,
            column_names=[
                'order_number', 'created_at', 'updated_at', 'status',
                'subtotal', 'shipping_cost', 'discount', 'total',
            ],
        )


def _clickhouse_sales(client, since):
    params = {'since': since}
    summary = client.query('''
        SELECT count(), coalesce(sum(total), 0),
               countIf(status IN ('pos_completed', 'delivered', 'confirmed', 'shipped'))
        FROM order_events FINAL
        WHERE created_at >= {since:DateTime}
    ''', parameters=params).result_rows[0]
    trend_rows = client.query('''
        SELECT toStartOfHour(created_at) AS bucket, count(), coalesce(sum(total), 0)
        FROM order_events FINAL
        WHERE created_at >= {since:DateTime}
        GROUP BY bucket ORDER BY bucket
    ''', parameters=params).result_rows
    return summary, trend_rows


def _django_sales(since):
    orders = Order.objects.filter(created_at__gte=since)
    summary = orders.aggregate(count=Count('id'), total=Sum('total'))
    paid = orders.filter(status__in=['pos_completed', 'delivered', 'confirmed', 'shipped']).count()
    trend_rows = orders.annotate(bucket=TruncHour('created_at')).values('bucket').annotate(
        count=Count('id'), total=Sum('total'),
    ).order_by('bucket')
    return (summary['count'] or 0, summary['total'] or Decimal('0'), paid), [
        (row['bucket'], row['count'], row['total'] or Decimal('0')) for row in trend_rows
    ]


def dashboard_snapshot():
    since = timezone.now() - timedelta(hours=24)
    source = 'django'
    try:
        client = _client()
        _sync_orders(client)
        summary, trend_rows = _clickhouse_sales(client, since)
        source = 'clickhouse'
    except Exception:
        summary, trend_rows = _django_sales(since)

    inventory = ProductVariant.objects.aggregate(
        units=Sum('stock'),
        low_stock=Count('id', filter=models.Q(stock__lte=models.F('min_stock'))),
    )
    shipment_counts = dict(
        Shipment.objects.values('status').annotate(count=Count('id')).values_list('status', 'count')
    )
    product_totals = {}
    for row in OrderItem.objects.filter(order__created_at__gte=since).values('product_name', 'price').annotate(
        quantity=Sum('quantity'),
    ):
        total = product_totals.setdefault(row['product_name'], {'quantity': 0, 'revenue': Decimal('0')})
        total['quantity'] += row['quantity'] or 0
        total['revenue'] += (row['price'] or Decimal('0')) * (row['quantity'] or 0)
    top_products = sorted(product_totals.items(), key=lambda item: item[1]['revenue'], reverse=True)[:5]

    return {
        'source': source,
        'updated_at': timezone.now().isoformat(),
        'period': '24h',
        'sales': {
            'orders': int(summary[0]),
            'revenue': float(summary[1]),
            'paid_orders': int(summary[2]),
            'trend': [
                {'time': bucket.isoformat(), 'orders': count, 'revenue': float(total)}
                for bucket, count, total in trend_rows
            ],
        },
        'inventory': {
            'units': int(inventory['units'] or 0),
            'low_stock': int(inventory['low_stock'] or 0),
        },
        'shipping': {
            'in_transit': int(shipment_counts.get('in_transit', 0)),
            'delivered': int(shipment_counts.get('delivered', 0)),
            'pending': int(shipment_counts.get('pending', 0)),
        },
        'top_products': [
            {'name': name, 'quantity': int(values['quantity']), 'revenue': float(values['revenue'])}
            for name, values in top_products
        ],
    }