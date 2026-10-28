// ==============================================================================
// SECTION 1: GLOBAL CART STATE & INITIALIZATION
// ==============================================================================

// Memory object storing selected items, quantities, and prices
const orderCart = {};

// ==============================================================================
// SECTION 2: REAL-TIME RUNNING CLOCK (TOP RIGHT CORNER)
// ==============================================================================

function startLiveClock() {
    function updateClock() {
        const now = new Date();
        
        // Format live calendar date: e.g., 28 Oct 2026
        const dateStr = now.toLocaleDateString('en-IN', {
            day: '2-digit',
            month: 'short',
            year: 'numeric'
        });
        
        // Format live digital clock with seconds: e.g., 07:15:30 PM
        const timeStr = now.toLocaleTimeString('en-IN', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true
        });

        document.getElementById('live-date').innerText = dateStr;
        document.getElementById('live-time').innerText = timeStr;
    }
    
    updateClock();
    // Refresh clock every second
    setInterval(updateClock, 1000);
}

// ==============================================================================
// SECTION 3: DAILY SALES & TOP DISH ANALYTICS LOADER
// ==============================================================================

async function fetchDailyAnalytics() {
    try {
        const response = await fetch('/api/analytics/daily-summary');
        const data = await response.json();
        
        if (data.status === 'success') {
            // Update today's total revenue badge
            document.getElementById('daily-sales-amount').innerText = `₹${parseFloat(data.total_sales).toFixed(2)}`;
            // Update most ordered dish badge
            document.getElementById('top-ordered-dish').innerText = data.top_selling_item;
        }
    } catch (err) {
        console.error("Failed to fetch analytics:", err);
    }
}

// ==============================================================================
// SECTION 4: MENU ITEMS RENDERER & CATEGORY FILTER
// ==============================================================================

async function loadDishes(category = 'all', tabElement = null) {
    // Highlight currently active category button
    if (tabElement) {
        document.querySelectorAll('.cat-tab').forEach(tab => tab.classList.remove('active'));
        tabElement.classList.add('active');
    }

    try {
        const response = await fetch(`/api/menu?category=${category}`);
        const dishes = await response.json();
        const grid = document.getElementById('menu-grid');
        grid.innerHTML = '';

        dishes.forEach(dish => {
            const currentQty = orderCart[dish.item_id] ? orderCart[dish.item_id].quantity : 0;
            const card = document.createElement('div');
            card.className = 'food-card';

            card.innerHTML = `
                <div class="image-wrapper">
                    <img src="${dish.image_url}" alt="${dish.item_name}" onerror="this.src='assets/images/logo.png'">
                    <span class="diet-tag ${dish.is_veg ? 'veg' : 'non-veg'}">${dish.is_veg ? '● Veg' : '● Non-Veg'}</span>
                </div>
                <div class="card-body">
                    <h3>${dish.item_name}</h3>
                    <p class="dish-price">₹${parseFloat(dish.price).toFixed(2)}</p>
                    <div id="btn-box-${dish.item_id}">
                        ${currentQty > 0 
                            ? `<div class="qty-control-box">
                                 <button class="qty-btn" onclick="updateItemQuantity('${dish.item_id}', '${dish.item_name}', ${dish.price}, -1)">-</button>
                                 <span class="qty-value">${currentQty}</span>
                                 <button class="qty-btn" onclick="updateItemQuantity('${dish.item_id}', '${dish.item_name}', ${dish.price}, 1)">+</button>
                               </div>`
                            : `<button class="add-order-btn" onclick="updateItemQuantity('${dish.item_id}', '${dish.item_name}', ${dish.price}, 1)">Add to Order</button>`
                        }
                    </div>
                </div>
            `;
            grid.appendChild(card);
        });
    } catch (err) {
        console.error("Failed to load dishes:", err);
    }
}

// ==============================================================================
// SECTION 5: DINING TABLE QUANTITY (+ / -) MODIFIER
// ==============================================================================

function updateItemQuantity(itemId, itemName, price, delta) {
    if (!orderCart[itemId]) {
        orderCart[itemId] = { name: itemName, price: price, quantity: 0 };
    }

    orderCart[itemId].quantity += delta;
    const btnContainer = document.getElementById(`btn-box-${itemId}`);

    // If quantity hits 0, remove item and show Add to Order button
    if (orderCart[itemId].quantity <= 0) {
        delete orderCart[itemId];
        if (btnContainer) {
            btnContainer.innerHTML = `<button class="add-order-btn" onclick="updateItemQuantity('${itemId}', '${itemName}', ${price}, 1)">Add to Order</button>`;
        }
    } else {
        // If quantity > 0, show interactive [-] count [+] control
        if (btnContainer) {
            btnContainer.innerHTML = `
                <div class="qty-control-box">
                    <button class="qty-btn" onclick="updateItemQuantity('${itemId}', '${itemName}', ${price}, -1)">-</button>
                    <span class="qty-value">${orderCart[itemId].quantity}</span>
                    <button class="qty-btn" onclick="updateItemQuantity('${itemId}', '${itemName}', ${price}, 1)">+</button>
                </div>
            `;
        }
    }

    updateOrderSummary();
}

function updateOrderSummary() {
    let totalItems = 0;
    let totalPrice = 0;

    for (const id in orderCart) {
        totalItems += orderCart[id].quantity;
        totalPrice += orderCart[id].quantity * orderCart[id].price;
    }

    document.getElementById('tray-total-items').innerText = `${totalItems} Items`;
    document.getElementById('tray-total-price').innerText = `₹${totalPrice.toFixed(2)}`;
}

// ==============================================================================
// SECTION 6: GST BILL CALCULATION & MODAL OPEN/CLOSE
// ==============================================================================

function openBillModal() {
    let subtotal = 0;
    const itemsListContainer = document.getElementById('bill-items-list');
    itemsListContainer.innerHTML = '';

    const items = [];
    for (const id in orderCart) {
        const item = orderCart[id];
        subtotal += item.price * item.quantity;
        items.push({ id: id, name: item.name, price: item.price, qty: item.quantity });

        const row = document.createElement('div');
        row.className = 'receipt-info-row';
        row.innerHTML = `<span>${item.name} (x${item.quantity})</span><span>₹${(item.price * item.quantity).toFixed(2)}</span>`;
        itemsListContainer.appendChild(row);
    }

    if (items.length === 0) {
        alert("Please add dishes to your order first!");
        return;
    }

    // Indian GST Breakdown: 2.5% CGST + 2.5% SGST = 5.0% Grand Tax
    const cgst = subtotal * 0.025;
    const sgst = subtotal * 0.025;
    const grandTotal = subtotal + cgst + sgst;

    document.getElementById('bill-timestamp').innerText = new Date().toLocaleString('en-IN');
    document.getElementById('bill-subtotal').innerText = `₹${subtotal.toFixed(2)}`;
    document.getElementById('bill-cgst').innerText = `₹${cgst.toFixed(2)}`;
    document.getElementById('bill-sgst').innerText = `₹${sgst.toFixed(2)}`;
    document.getElementById('bill-grand-total').innerText = `₹${grandTotal.toFixed(2)}`;

    document.getElementById('bill-modal').style.display = 'flex';
}

function closeBillModal() {
    document.getElementById('bill-modal').style.display = 'none';
}

// ==============================================================================
// SECTION 7: BILL PAYMENT & KAFKA EVENT TRIGGER
// ==============================================================================

async function submitBillPayment() {
    let subtotal = 0;
    const items = [];
    for (const id in orderCart) {
        const item = orderCart[id];
        subtotal += item.price * item.quantity;
        items.push({ id: id, name: item.name, price: item.price, qty: item.quantity });
    }

    try {
        const res = await fetch('/api/orders/pay', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                table_number: 1,
                items: items,
                subtotal: subtotal,
                payment_method: 'UPI'
            })
        });

        const result = await res.json();
        if (result.status === 'success') {
            alert(`Payment Successful! Order #${result.bill_details.order_id} stored in Database and published to Kafka!`);
            
            // Clear dining table cart
            for (const key in orderCart) delete orderCart[key];
            updateOrderSummary();
            loadDishes('all');
            closeBillModal();
            fetchDailyAnalytics();
        } else {
            alert("Payment failed: " + result.message);
        }
    } catch (err) {
        console.error("Payment error:", err);
        alert("Error connecting to server for payment.");
    }
}

// ==============================================================================
// SECTION 8: DOM STARTUP LISTENER
// ==============================================================================

document.addEventListener('DOMContentLoaded', () => {
    startLiveClock();
    fetchDailyAnalytics();
    loadDishes('all');
    // Refresh sales analytics every 60 seconds
    setInterval(fetchDailyAnalytics, 60000);
});