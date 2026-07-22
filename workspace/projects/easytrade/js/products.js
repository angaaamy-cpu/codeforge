/**
 * EasyTrade Products Data
 * ======================
 * بيانات المنتجات الثابتة
 */

const PRODUCTS = [
    {
        id: 1,
        name: "هاتف ذكي X",
        nameEn: "Smart Phone X",
        description: "هاتف ذكي بأحدث التقنيات، شاشة 6.7 بوصة، كاميرا 108 ميجابيكسل",
        price: 299,
        category: "electronics",
        categoryName: "إلكترونيات",
        image: "📱"
    },
    {
        id: 2,
        name: "لابتوب برو",
        nameEn: "Pro Laptop",
        description: "لابتوب قوي للمطورين والمصممين، 16GB RAM، 512GB SSD",
        price: 799,
        category: "electronics",
        categoryName: "إلكترونيات",
        image: "💻"
    },
    {
        id: 3,
        name: "سماعات لاسلكية",
        nameEn: "Wireless Headphones",
        description: "سماعات بلوتوث عالية الجودة، عمر بطارية 30 ساعة",
        price: 89,
        category: "electronics",
        categoryName: "إلكترونيات",
        image: "🎧"
    },
    {
        id: 4,
        name: "ساعة ذكية",
        nameEn: "Smart Watch",
        description: "ساعة ذكية مع تتبع اللياقة والقلب، مقاومة للماء",
        price: 199,
        category: "electronics",
        categoryName: "إلكترونيات",
        image: "⌚"
    },
    {
        id: 5,
        name: "قميص كاجوال",
        nameEn: "Casual Shirt",
        description: "قميص قطن عالي الجودة، مريح للارتداء اليومي",
        price: 49,
        category: "clothing",
        categoryName: "ملابس",
        image: "👕"
    },
    {
        id: 6,
        name: "حذاء رياضي",
        nameEn: "Sports Shoes",
        description: "حذاء خفيف ومريح للرياضة والمشي",
        price: 129,
        category: "shoes",
        categoryName: "أحذية",
        image: "👟"
    },
    {
        id: 7,
        name: "حقيبة ظهر",
        nameEn: "Backpack",
        description: "حقيبة ظهر متعددة الأقسام، مثالية للدراسة والسفر",
        price: 79,
        category: "accessories",
        categoryName: "إكسسوارات",
        image: "🎒"
    },
    {
        id: 8,
        name: "نظارات شمسية",
        nameEn: "Sunglasses",
        description: "نظارات شمسية أنيقة تحجب 100% من الأشعة فوق البنفسجية",
        price: 59,
        category: "accessories",
        categoryName: "إكسسوارات",
        image: "🕶️"
    },
    {
        id: 9,
        name: "كاميرا رقمية",
        nameEn: "Digital Camera",
        description: "كاميرا 24 ميجابيكسل مع عدسة 18-55mm",
        price: 449,
        category: "electronics",
        categoryName: "إلكترونيات",
        image: "📷"
    },
    {
        id: 10,
        name: "لوحة رسم",
        nameEn: "Drawing Tablet",
        description: "لوحة رسم رقمية للرسامين والمصممين",
        price: 159,
        category: "electronics",
        categoryName: "إلكترونيات",
        image: "🎨"
    }
];

const CATEGORIES = [
    { id: "all", name: "الكل", nameEn: "All" },
    { id: "electronics", name: "إلكترونيات", nameEn: "Electronics" },
    { id: "clothing", name: "ملابس", nameEn: "Clothing" },
    { id: "shoes", name: "أحذية", nameEn: "Shoes" },
    { id: "accessories", name: "إكسسوارات", nameEn: "Accessories" }
];

/**
 * الحصول على منتج بالـ ID
 */
function getProductById(id) {
    const numId = parseInt(id, 10);
    return PRODUCTS.find(p => p.id === numId);
}

/**
 * البحث في المنتجات
 */
function searchProducts(query) {
    if (!query || query.trim() === "") {
        return PRODUCTS;
    }
    
    const q = query.toLowerCase().trim();
    return PRODUCTS.filter(p => 
        p.name.toLowerCase().includes(q) ||
        p.nameEn.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q)
    );
}

/**
 * تصفية حسب الفئة
 */
function filterByCategory(categoryId) {
    if (categoryId === "all") {
        return PRODUCTS;
    }
    return PRODUCTS.filter(p => p.category === categoryId);
}

/**
 * الحصول على سعر الصرف (للعرض)
 */
function formatPrice(price) {
    return price.toFixed(2) + " $";
}
