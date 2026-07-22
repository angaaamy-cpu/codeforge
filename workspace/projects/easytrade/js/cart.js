/**
 * EasyTrade Cart Management
 * ========================
 * إدارة سلة التسوق باستخدام localStorage
 */

const CART_STORAGE_KEY = "easytrade_cart";

/**
 * الحصول على السلة من localStorage
 */
function getCart() {
    try {
        const cartData = localStorage.getItem(CART_STORAGE_KEY);
        if (!cartData) {
            return [];
        }
        const data = JSON.parse(cartData);
        return Array.isArray(data) ? data : [];
    } catch (e) {
        console.error("Error reading cart:", e);
        return [];
    }
}

/**
 * حفظ السلة في localStorage
 */
function saveCart(cart) {
    try {
        localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cart));
        updateCartBadge();
        return true;
    } catch (e) {
        console.error("Error saving cart:", e);
        return false;
    }
}

/**
 * إضافة منتج للسلة
 */
function addToCart(productId, quantity = 1) {
    const cart = getCart();
    const existingItem = cart.find(item => item.id === productId);
    
    if (existingItem) {
        existingItem.quantity += quantity;
    } else {
        cart.push({ id: productId, quantity: quantity });
    }
    
    saveCart(cart);
    return true;
}

/**
 * حذف منتج من السلة
 */
function removeFromCart(productId) {
    let cart = getCart();
    cart = cart.filter(item => item.id !== productId);
    saveCart(cart);
    return true;
}

/**
 * تحديث كمية منتج
 */
function updateQuantity(productId, quantity) {
    const cart = getCart();
    const item = cart.find(item => item.id === productId);
    
    if (!item) {
        return false;
    }
    
    if (quantity <= 0) {
        return removeFromCart(productId);
    }
    
    item.quantity = quantity;
    saveCart(cart);
    return true;
}

/**
 * الحصول على المجموع الكلي للسلة
 */
function getCartTotal() {
    const cart = getCart();
    let total = 0;
    
    cart.forEach(item => {
        const product = getProductById(item.id);
        if (product) {
            total += product.price * item.quantity;
        }
    });
    
    return total;
}

/**
 * الحصول على عدد العناصر في السلة
 */
function getCartCount() {
    const cart = getCart();
    return cart.reduce((sum, item) => sum + item.quantity, 0);
}

/**
 * الحصول على تفاصيل السلة مع معلومات المنتجات
 */
function getCartDetails() {
    const cart = getCart();
    const details = [];
    let subtotal = 0;
    
    cart.forEach(item => {
        const product = getProductById(item.id);
        if (product) {
            const itemTotal = product.price * item.quantity;
            details.push({
                id: product.id,
                name: product.name,
                price: product.price,
                quantity: item.quantity,
                image: product.image,
                itemTotal: itemTotal
            });
            subtotal += itemTotal;
        }
    });
    
    return {
        items: details,
        subtotal: subtotal,
        total: subtotal, // يمكن إضافة ضرائب ورسوم هنا
        itemCount: cart.reduce((sum, item) => sum + item.quantity, 0)
    };
}

/**
 * تفريغ السلة
 */
function clearCart() {
    saveCart([]);
    return true;
}

/**
 * تحديث شارة السلة في الهيدر
 */
function updateCartBadge() {
    const badge = document.getElementById("cart-badge");
    if (badge) {
        const count = getCartCount();
        badge.textContent = count;
        badge.style.display = count > 0 ? "inline-block" : "none";
    }
}

/**
 * إنشاء رقم طلب عشوائي
 */
function generateOrderNumber() {
    const timestamp = Date.now().toString(36).toUpperCase();
    const random = Math.random().toString(36).substring(2, 6).toUpperCase();
    return "ET-" + timestamp + "-" + random;
}

/**
 * التحقق من صحة المدخلات
 */
function sanitizeInput(input) {
    if (typeof input !== "string") {
        return "";
    }
    return input.replace(/[<>]/g, "").trim();
}

/**
 * التحقق من صحة الكمية
 */
function validateQuantity(quantity) {
    const num = parseInt(quantity, 10);
    return !isNaN(num) && num > 0 && num <= 99;
}
