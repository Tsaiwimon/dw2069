(function () {
    const apiUrl = '/dashboard/test/api/';
    const createUrl = '/dashboard/test/api/create/';
    const money = new Intl.NumberFormat('th-TH', { style: 'currency', currency: 'THB', maximumFractionDigits: 2 });
    const form = document.getElementById('order-form');
    const message = document.getElementById('form-message');

    function renderOrders(orders) {
        const target = document.getElementById('recent-orders');
        target.innerHTML = orders.length ? orders.map((order) => `<div class="recent-row"><div><span class="order-number">${order.order_number}</span><span class="order-time">${new Date(order.created_at).toLocaleString('th-TH')}</span></div><span class="order-total">${money.format(order.total)}</span><span class="order-status">${order.status}</span></div>`).join('') : '<p class="empty-state">ยังไม่มีออเดอร์</p>';
    }
    const stream = new EventSource('/dashboard/test/stream/');
    stream.onmessage = (event) => renderOrders(JSON.parse(event.data));
    stream.onerror = () => {
        stream.close();
        document.getElementById('recent-orders').innerHTML = '<p class="empty-state">แสดงข้อมูลล่าสุด</p>';
    };
    form.addEventListener('submit', async function (event) {
        event.preventDefault(); form.querySelector('button').disabled = true; message.className = 'form-message'; message.textContent = 'กำลังบันทึก...';
        try { const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value; const response = await fetch(createUrl, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken }, body: JSON.stringify(Object.fromEntries(new FormData(form))) }); const data = await response.json(); if (!response.ok) throw new Error(data.error || 'บันทึกไม่สำเร็จ'); message.className = 'form-message success'; message.textContent = `บันทึกแล้ว ${data.order_number} ยอด ${money.format(data.total)}`; } catch (error) { message.className = 'form-message error'; message.textContent = error.message; } finally { form.querySelector('button').disabled = false; }
    });
}());