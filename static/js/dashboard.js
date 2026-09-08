(function () {
    const apiUrl = '/dashboard/api/';
    const money = new Intl.NumberFormat('th-TH', { style: 'currency', currency: 'THB', maximumFractionDigits: 0 });
    const number = new Intl.NumberFormat('th-TH');
    const $ = (id) => document.getElementById(id);

    function renderChart(points) {
        const chart = $('sales-chart');
        if (!points.length) { chart.innerHTML = '<div class="empty-state">ยังไม่มียอดขายในช่วงนี้</div>'; return; }
        const max = Math.max(...points.map((point) => point.revenue), 1);
        chart.innerHTML = points.slice(-24).map((point) => {
            const hour = new Date(point.time).toLocaleTimeString('th-TH', { hour: '2-digit' });
            return `<div class="bar-wrap" title="${hour}: ${money.format(point.revenue)}"><div class="bar" style="height:${Math.max(4, point.revenue / max * 100)}%"></div><span class="bar-label">${hour}</span></div>`;
        }).join('');
    }

    function renderProducts(products) {
        $('top-products').innerHTML = products.length ? products.map((product, index) => `<div class="product-row"><span class="rank">0${index + 1}</span><div class="product-info"><span class="product-name">${product.name}</span><span class="product-qty">ขายแล้ว ${number.format(product.quantity)} ชิ้น</span></div><span class="product-revenue">${money.format(product.revenue)}</span></div>`).join('') : '<div class="empty-state">ยังไม่มีข้อมูลสินค้า</div>';
    }

    function render(data) {
        $('revenue').textContent = money.format(data.sales.revenue);
        $('orders').textContent = `${number.format(data.sales.orders)} ออเดอร์`;
        $('paid-orders').textContent = number.format(data.sales.paid_orders);
        $('stock-units').textContent = number.format(data.inventory.units);
        $('low-stock').textContent = `${number.format(data.inventory.low_stock)} รายการใกล้หมด`;
        $('in-transit').textContent = number.format(data.shipping.in_transit);
        $('shipping-summary').textContent = `ส่งแล้ว ${number.format(data.shipping.delivered)} / รอดำเนินการ ${number.format(data.shipping.pending)}`;
        $('updated-at').textContent = `อัปเดต ${new Date(data.updated_at).toLocaleTimeString('th-TH')}`;
        $('connection-status').innerHTML = `<span></span> ${data.source === 'clickhouse' ? 'ClickHouse สด' : 'โหมดสำรอง Django'}`;
        $('connection-status').classList.toggle('is-error', data.source !== 'clickhouse');
        renderChart(data.sales.trend); renderProducts(data.top_products);
    }

    const stream = new EventSource('/dashboard/stream/');
    stream.onopen = () => $('connection-status').classList.remove('is-error');
    stream.onmessage = (event) => {
        render(JSON.parse(event.data));
        $('connection-status').innerHTML = '<span></span> เชื่อมต่อแบบสด';
    };
    stream.onerror = () => {
        stream.close();
        $('connection-status').innerHTML = '<span></span> แสดงข้อมูลล่าสุด';
        $('connection-status').classList.add('is-error');
    };
}());