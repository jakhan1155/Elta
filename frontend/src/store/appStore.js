// Состояние витрины: каталог, выбранная категория, поиск, бренд, открытые страницы
let DATA = { products: [], categories: [] };
let byId = {};
let cat = "all", query = "", brand = "all";

const stack = [];   // открытые страницы поверх витрины
