-- Clean insert for full menu items catalog
DELETE FROM menu_items;

INSERT INTO menu_items (item_id, item_name, category, cuisine, price, is_veg, is_available, image_url) VALUES
-- ================= STARTERS & APPETIZERS =================
('STA-001', 'Madurai Mutton Elumbu Saru', 'starters', 'madurai', 160.00, 0, 1, 'assets/images/mutton-soup.jpg'),
('STA-002', 'Murungai Keerai Saaru', 'starters', 'chettinad', 90.00, 1, 1, 'assets/images/murungai-keerai-soup.jpg'),
('STA-003', 'Classic Sweet Corn Veg Soup', 'starters', 'north_indian', 110.00, 1, 1, 'assets/images/sweet-corn-soup.jpg'),
('STA-004', 'Chicken Manchow Soup', 'starters', 'north_indian', 145.00, 0, 1, 'assets/images/chicken-manchow-soup.jpg'),
('STA-005', 'South Indian Kosumalli Salad', 'starters', 'chettinad', 95.00, 1, 1, 'assets/images/kosumalli-salad.jpg'),
('STA-006', 'Crispy Gobi 65', 'starters', 'madurai', 140.00, 1, 1, 'assets/images/gobi-65.jpg'),
('STA-007', 'Vazhaipoo Vadai (4 pcs)', 'starters', 'chettinad', 120.00, 1, 1, 'assets/images/vazhaipoo-vadai.jpg'),
('STA-008', 'Paneer Tikka Angaara', 'starters', 'north_indian', 230.00, 1, 1, 'assets/images/punner-tikka.jpg'),
('STA-009', 'Madurai Mutton Chukka', 'starters', 'madurai', 290.00, 0, 1, 'assets/images/mutton-chukka.jpg'),
('STA-010', 'Kozhi Chinthamani', 'starters', 'kongu', 250.00, 0, 1, 'assets/images/kozhi-chinthamani.jpg'),
('STA-011', 'Andhra Royyala Vepudu (Prawn)', 'starters', 'andhra', 320.00, 0, 1, 'assets/images/andhra-prawn-fry.jpg'),
('STA-012', 'Amritsari Fish Tikka', 'starters', 'north_indian', 310.00, 0, 1, 'assets/images/amritsari-fish.jpg'),
('STA-013', 'Tandoori Murgh Roast', 'starters', 'north_indian', 240.00, 0, 1, 'assets/images/tandoori-chicken.jpg'),
('STA-014', 'Signature Charcoal Grilled Chicken', 'starters', 'north_indian', 220.00, 0, 1, 'assets/images/grill-chicken.jpg'),

-- ================= MAIN COURSE =================
('MC-001', 'Madurai Malli Poo Idli (4 pcs)', 'main_course', 'madurai', 80.00, 1, 1, 'assets/images/malli-poo-idly.jpg'),
('MC-002', 'Madurai Kari Dosa (Mutton)', 'main_course', 'madurai', 240.00, 0, 1, 'assets/images/kari-dosa.jpg'),
('MC-003', 'Ghee Podi Roast Dosa', 'main_course', 'madurai', 110.00, 1, 1, 'assets/images/ghee-podi-roast.jpg'),
('MC-004', 'Kerala Appam with Chicken Stew', 'main_course', 'kerala', 180.00, 0, 1, 'assets/images/appam-chicken-stew.jpg'),
('MC-005', 'Idiyappam with Kadala Curry', 'main_course', 'kerala', 110.00, 1, 1, 'assets/images/idiyappam-kadala.jpg'),
('MC-006', 'Kerala Puttu with Kadala', 'main_course', 'kerala', 105.00, 1, 1, 'assets/images/kerala-puttu.jpg'),
('MC-007', 'Malabar Egg Roast with Porotta', 'main_course', 'kerala', 140.00, 0, 1, 'assets/images/malabar-egg-roast.jpg'),
('MC-008', 'Chettinad Special Non-Veg Meals', 'main_course', 'chettinad', 320.00, 0, 1, 'assets/images/chettinad-nonveg-meals.jpg'),
('MC-009', 'Traditional Tamil Nadu Veg Meals', 'main_course', 'madurai', 160.00, 1, 1, 'assets/images/tamil-veg-meals.jpg'),
('MC-010', 'Authentic Andhra Bhojanam Meals', 'main_course', 'andhra', 220.00, 1, 1, 'assets/images/andhra-meals.jpg'),
('MC-011', 'Thalappakatti Mutton Biryani', 'main_course', 'chettinad', 310.00, 0, 1, 'assets/images/mutton-briyani.jpg'),
('MC-012', 'Hyderabadi Dum Chicken Biryani', 'main_course', 'andhra', 260.00, 0, 1, 'assets/images/hyderabad-chicken-briyani.jpg'),
('MC-013', 'Andhra Gongura Mutton Biryani', 'main_course', 'andhra', 330.00, 0, 1, 'assets/images/gongura-mutton-briyani.jpg'),
('MC-014', 'Butter Chicken (Murgh Makhani)', 'main_course', 'north_indian', 270.00, 0, 1, 'assets/images/butter-chicken.jpg'),
('MC-015', 'Paneer Butter Masala', 'main_course', 'north_indian', 220.00, 1, 1, 'assets/images/punner-butter-masala.jpg'),
('MC-016', 'Dal Makhani', 'main_course', 'north_indian', 190.00, 1, 1, 'assets/images/dal-makhani.jpg'),
('MC-017', 'Butter Naan / Garlic Naan', 'main_course', 'north_indian', 45.00, 1, 1, 'assets/images/butter-naan.jpg'),

-- ================= SNACKS & EVENING SPECIALS =================
('SNA-001', 'Madurai Bun Parotta with Salna', 'snacks', 'madurai', 70.00, 1, 1, 'assets/images/bun-parotta.jpg'),
('SNA-002', 'Madurai Chicken Kothu Parotta', 'snacks', 'madurai', 180.00, 0, 1, 'assets/images/chicken-kothu-parotta.jpg'),
('SNA-003', 'Madurai Mutton Kothu Parotta', 'snacks', 'madurai', 250.00, 0, 1, 'assets/images/mutton-kothu-parotta.jpg'),
('SNA-004', 'Ceylon Egg Veechu Parotta', 'snacks', 'madurai', 95.00, 0, 1, 'assets/images/veechu-parotta.jpg'),

-- ================= BEVERAGES & DESSERTS =================
('BEV-001', 'Kumbakonam Traditional Filter Coffee', 'beverages', 'south_indian', 35.00, 1, 1, 'assets/images/filter-coffee.jpg'),
('BEV-002', 'Madurai Famous Jigarthanda', 'beverages', 'madurai', 90.00, 1, 1, 'assets/images/jigarthanda.jpg'),
('BEV-003', 'Elaneer Payasam', 'beverages', 'kerala', 120.00, 1, 1, 'assets/images/elaneer-payasam.jpg'),
('BEV-004', 'Bira 91 White Craft Beer', 'beverages', 'beverages', 240.00, 1, 1, 'assets/images/bira-white.jpg'),
('BEV-005', 'Sula Sauvignon Blanc (Glass)', 'beverages', 'beverages', 320.00, 1, 1, 'assets/images/white-wine.jpg');


USE restaurant_db;

-- Table to store finalized bill transactions and GST tax audit
CREATE TABLE IF NOT EXISTS payments (
    -- Unique transaction sequence identifier
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    -- Reference link to the parent order
    order_id INT NOT NULL,
    -- Dining table number
    table_number INT NOT NULL,
    -- Food items subtotal amount before taxes
    subtotal DECIMAL(10, 2) NOT NULL,
    -- Central GST amount (2.5%)
    cgst DECIMAL(10, 2) NOT NULL,
    -- State GST amount (2.5%)
    sgst DECIMAL(10, 2) NOT NULL,
    -- Final payable bill amount with 5% GST
    grand_total DECIMAL(10, 2) NOT NULL,
    -- Payment mode used (UPI, CASH, CARD)
    payment_method VARCHAR(30) NOT NULL DEFAULT 'UPI',
    -- Final payment status
    payment_status VARCHAR(20) NOT NULL DEFAULT 'PAID',
    -- Exact payment completion date and time
    paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Cascade deletion if parent order record is deleted
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);