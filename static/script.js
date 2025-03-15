// Login Page
function toggleForm() {
    const loginBox = document.getElementById("login-box");
    const registerBox = document.getElementById("register-box");
    
    if (loginBox.classList.contains("active")) {
        loginBox.classList.remove("active");
        registerBox.classList.add("active");
    } else {
        registerBox.classList.remove("active");
        loginBox.classList.add("active");
    }
}

// Home Page
document.addEventListener("DOMContentLoaded", function () {
    const menuBtn = document.getElementById("menu-btn");
    const closeBtn = document.getElementById("close-btn");
    const navLinks = document.querySelector(".nav-links");

    menuBtn.addEventListener("click", function () {
        navLinks.classList.add("active");
    });

    closeBtn.addEventListener("click", function () {
        navLinks.classList.remove("active");
    });
});

// Admin Page
document.addEventListener("DOMContentLoaded", fetchItems);

// Fetch items from the database
function fetchItems() {
    fetch('/get_items')
        .then(response => response.json())
        .then(data => {
            console.log("Fetched items:", data);  // Debug: Log fetched items
            let table = document.getElementById('inventory-table');
            if (table) {
                table.innerHTML = "";
                data.forEach(item => {
                    let row = `<tr>
                        <td>${item.name}</td>
                        <td>${item.category}</td>
                        <td>$${item.price}</td>
                        <td>${item.quantity}</td>
                        <td>
                            <button onclick="deleteItem(${item.id})">Remove</button>
                        </td>
                    </tr>`;
                    table.innerHTML += row;
                });
            }

            // Update the menu on home.html
            let menuGrid = document.getElementById('menu-grid');
            if (menuGrid) {
                menuGrid.innerHTML = "";
                data.forEach(item => {
                    let card = `<div class="card" data-name="${item.name.toLowerCase()}" data-category="${item.category}">
                        <img src="${item.image}" alt="${item.name}">
                        <div class="title">${item.name}</div>
                        <div class="description">${item.category}</div>
                        <div class="price">$${item.price}</div>
                        <input type="number" class="quantity" min="1" value="1" id="qty-${item.name}">
                        <button class="btn" onclick="addToCart('${item.name}', ${item.price})">Add to Cart</button>
                    </div>`;
                    menuGrid.innerHTML += card;
                });
            }
        })
        .catch(error => {
            console.error('Error fetching items:', error);  // Debug: Log fetch errors
        });
}

// Add a new item
function addItem() {
    let name = document.getElementById('item-name').value;
    let category = document.getElementById('item-category').value;
    let price = document.getElementById('item-price').value;
    let quantity = document.getElementById('item-quantity').value;
    let image = document.getElementById('item-image').value;

    console.log("Sending data:", { name, category, price, quantity, image });  // Debug: Log data being sent

    fetch('/add_item', {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ name, category, price, quantity, image })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Response from server:", data);  // Debug: Log server response
        if (data.message) {
            alert(data.message);  // Show success message
            fetchItems();  // Refresh the item list
        } else if (data.error) {
            alert(data.error);  // Show error message
        }
    })
    .catch(error => {
        console.error('Error:', error);  // Debug: Log any fetch errors
        alert('An error occurred while adding the item.');
    });
}

document.querySelectorAll(".faq-item").forEach((item) => {
    item.addEventListener("click", () => {
        item.classList.toggle("active");
    });
});

// Delete an item
function deleteItem(id) {
    fetch('/delete_item', {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ id })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Response from server:", data);  // Debug: Log server response
        if (data.message) {
            alert(data.message);  // Show success message
            fetchItems();  // Refresh the item list
        } else if (data.error) {
            alert(data.error);  // Show error message
        }
    })
    .catch(error => {
        console.error('Error:', error);  // Debug: Log any fetch errors
        alert('An error occurred while deleting the item.');
    });
}

// Menu Page
let cart = [];

// Filter the menu
function filterMenu() {
    const searchValue = document.getElementById("search-bar").value.toLowerCase();
    const filterValue = document.getElementById("filter-category").value;

    document.querySelectorAll(".card").forEach(card => {
        const itemName = card.getAttribute("data-name").toLowerCase();
        const itemCategory = card.getAttribute("data-category");

        const matchesSearch = itemName.includes(searchValue);
        const matchesCategory = filterValue === "all" || itemCategory === filterValue;

        if (matchesSearch && matchesCategory) {
            card.style.display = "block";
        } else {
            card.style.display = "none";
        }
    });
}

// Add an item to the cart
function addToCart(name, price) {
    const quantity = document.getElementById(`qty-${name}`).value;
    cart.push({ name, price, quantity });
    updateCart();
}

// Update the cart display
function updateCart() {
    const cartList = document.getElementById("cart-list");
    cartList.innerHTML = cart.map(item => `<li>${item.name} x${item.quantity} - $${(item.price * item.quantity).toFixed(2)}</li>`).join("");
    document.getElementById("cart-total").textContent = `$${cart.reduce((total, item) => total + item.price * item.quantity, 0).toFixed(2)}`;
}

// Handle checkout
function checkout() {
    const cartData = {
        items: cart,
        total_price: cart.reduce((total, item) => total + item.price * item.quantity, 0)
    };

    fetch('/checkout', {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(cartData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);  // Show success message
            clearCart();  // Clear the cart after successful checkout
        } else if (data.error) {
            alert(data.error);  // Show error message
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while placing the order.');
    });
}

// Clear the cart
function clearCart() {
    cart = [];
    updateCart();
}

// FAQ Toggle Function
function toggleAnswer(question) {
    const answer = question.nextElementSibling; // Get the next sibling element (the answer)
    if (answer.style.display === "block") {
        answer.style.display = "none"; // Hide the answer if it's already visible
    } else {
        answer.style.display = "block"; // Show the answer if it's hidden
    }
}

// Initialize the menu when the page loads
document.addEventListener("DOMContentLoaded", function () {
    fetchItems();  // Fetch and render the menu
});