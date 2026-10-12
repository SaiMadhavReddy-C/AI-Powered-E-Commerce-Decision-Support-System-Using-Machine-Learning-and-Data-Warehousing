-- ==============================================================================
-- ShopQ Comprehensive Seed Data (PostgreSQL / Supabase)
-- ==============================================================================
-- Seeds the complete 12 core demo scenarios:
--   1.  Sony WH-1000XM5 (BUY - 90-day historic low deal)
--   2.  Apple iPhone 15 (WAIT - price peak, festival sale pending)
--   3.  Nike Air Max 90 (CHECK_ALT - cheaper on Myntra vs Amazon)
--   4.  HP Pavilion 14 (CAUTION - unverified risky seller selling refurbished)
--   5.  Canon EOS R50 (NO_DECISION - brand new launch, insufficient history)
--   6.  Amazon Kindle Paperwhite (CAUTION - stale scraper data >14 days)
--   7.  Apple MacBook Air M2 (CAUTION - variant spec mismatch 8GB vs 16GB)
--   8.  Google Pixel 8 Pro (NO_DECISION - scraper HTTP 403 blocks)
--   9.  Samsung Galaxy S24 5G (CAUTION - sudden buy-box merchant switch)
--   10. Sony PlayStation 5 Pro (WAIT - official stock sold out, scalper markup)
--   11. boAt Airdopes 141 (YOUR_CALL - everyday budget item with stable price)
--   12. Nothing Ear (2) (NO_DECISION - volatile swing and successor rumor)
-- ==============================================================================

-- ==============================================================================
-- 1. SEED DIM_DATE (Calendar Dimension 2026)
-- ==============================================================================
SELECT populate_dim_date('2026-01-01'::DATE, '2026-12-31'::DATE);

-- ==============================================================================
-- 2. SEED DIM_CATEGORY
-- ==============================================================================
INSERT INTO dim_category (category_id, category_name, parent_category_id, parent_category_name, department) VALUES
('cat_headphones',    'Headphones',             'cat_audio',       'Audio & Sound',   'Electronics'),
('cat_smartphones',   'Smartphones',            'cat_mobiles',     'Mobile Devices',  'Electronics'),
('cat_laptops',       'Laptops & Computers',    'cat_computing',   'Computing',       'Electronics'),
('cat_footwear',      'Athletic Footwear',      'cat_fashion',     'Footwear',        'Apparel & Fashion'),
('cat_cameras',       'Mirrorless Cameras',     'cat_photography', 'Photography',     'Electronics'),
('cat_ereaders',      'E-Readers & Tablets',    'cat_mobiles',     'Mobile Devices',  'Electronics'),
('cat_gaming',        'Gaming Consoles',        'cat_entertainment','Gaming',         'Electronics'),
('cat_audio_acc',     'Audio Accessories',      'cat_audio',       'Audio & Sound',   'Electronics')
ON CONFLICT (category_id) DO NOTHING;

-- ==============================================================================
-- 3. SEED DIM_RETAILER
-- ==============================================================================
INSERT INTO dim_retailer (retailer_id, retailer_name, domain_url, country, currency_code, reliability_score, is_verified) VALUES
('amazon',    'Amazon India',     'https://amazon.in',        'IN', 'INR', 0.98, TRUE),
('flipkart',  'Flipkart',         'https://flipkart.com',     'IN', 'INR', 0.96, TRUE),
('croma',     'Croma Electronics','https://croma.com',        'IN', 'INR', 0.95, TRUE),
('reliance',  'Reliance Digital', 'https://reliancedigital.in','IN', 'INR', 0.94, TRUE),
('myntra',    'Myntra Fashion',   'https://myntra.com',       'IN', 'INR', 0.97, TRUE)
ON CONFLICT (retailer_id) DO NOTHING;

-- ==============================================================================
-- 4. SEED DIM_SELLER
-- ==============================================================================
INSERT INTO dim_seller (seller_id, seller_name, rating, review_count, reliability_tier, return_policy, warranty_terms, is_authorized) VALUES
('seller_appario',     'Appario Retail',           4.8, 28500, 'RELIABLE', '10-day replacement',  '1 year manufacturer', TRUE),
('seller_supercomnet',  'SuperComNet',              4.6, 54000, 'RELIABLE', '7-day replacement',   '1 year Apple warranty', TRUE),
('seller_retailnet',    'RetailNet',                4.4, 31200, 'RELIABLE', '10-day replacement',  '1 year manufacturer', TRUE),
('seller_croma',        'Croma Official',           4.8, 45000, 'RELIABLE', '7-day replacement',   'Direct manufacturer', TRUE),
('seller_reliance',     'Reliance Digital Official',4.7, 39000, 'RELIABLE', '7-day replacement',   'Direct manufacturer', TRUE),
('seller_nike_india',   'Nike India Official',      4.9, 87000, 'RELIABLE', '15-day free return',  '6 months manufacturer', TRUE),
('seller_indiflash',    'IndiFlashMart',            4.1,  8200, 'RELIABLE', '7-day return',        '6 months brand warranty', TRUE),
('seller_cocoblu',      'Cocoblu Retail',           4.4, 154000,'RELIABLE', '7-day replacement',   '1 year manufacturer', TRUE),
('seller_quickdeal',    'QuickDeal Electro Store',  2.3,    34, 'RISKY',    'No returns, exchange only','Seller warranty only', FALSE),
('seller_inditech',     'IndiTechRetail',           3.8,   820, 'MODERATE', '7-day replacement',   '1 year Apple warranty', TRUE),
('seller_fastgizmos',   'FastGizmos Unlimited',     3.1,    42, 'MODERATE', '7-day replacement',   '1 year manufacturer', FALSE),
('seller_scalperdeals', 'ScalperDeals Hub',         3.5,    18, 'MODERATE', 'No returns',          'Seller warranty only', FALSE),
('seller_unverified',   'Unverified Merchant',      0.0,     0, 'UNKNOWN',  'Unknown',             'Unknown', FALSE)
ON CONFLICT (seller_id) DO NOTHING;

-- ==============================================================================
-- 5. SEED CANONICAL_PRODUCT & DIM_PRODUCT
-- ==============================================================================

INSERT INTO canonical_product (id, brand, canonical_name, category_id, canonical_image_url) VALUES
('cp_sony_good_deal',           'Sony',     'Sony WH-1000XM5 Wireless Noise Cancelling Headphones', 'cat_headphones',   'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Sony+XM5'),
('cp_iphone_wait',              'Apple',    'Apple iPhone 15 5G Smartphone',                        'cat_smartphones',  'https://placehold.co/300x300/FAF8F5/1A1A1A?text=iPhone+15'),
('cp_nike_better_alternative',  'Nike',     'Nike Air Max 90 Sneakers',                             'cat_footwear',     'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Nike+AirMax'),
('cp_laptop_suspicious_seller', 'HP',       'HP Pavilion 14 Laptop',                                'cat_laptops',      'https://placehold.co/300x300/FAF8F5/1A1A1A?text=HP+Pavilion'),
('cp_new_product_no_history',   'Canon',    'Canon EOS R50 Mirrorless Camera',                      'cat_cameras',      'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Canon+R50'),
('cp_stale_price',              'Amazon',   'Amazon Kindle Paperwhite 16GB',                        'cat_ereaders',     'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Kindle'),
('cp_variant_mismatch',         'Apple',    'Apple MacBook Air 13.6-inch M2',                       'cat_laptops',      'https://placehold.co/300x300/FAF8F5/1A1A1A?text=MacBook+Air'),
('cp_all_sources_failed',       'Google',   'Google Pixel 8 Pro 5G',                                'cat_smartphones',  'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Pixel+8+Pro'),
('cp_seller_changed',           'Samsung',  'Samsung Galaxy S24 5G',                                'cat_smartphones',  'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Galaxy+S24'),
('cp_out_of_stock',             'Sony',     'Sony PlayStation 5 Pro Console',                       'cat_gaming',       'https://placehold.co/300x300/FAF8F5/1A1A1A?text=PS5+Pro'),
('cp_your_call',                'boAt',     'boAt Airdopes 141 True Wireless Earbuds',              'cat_audio_acc',    'https://placehold.co/300x300/FAF8F5/1A1A1A?text=boAt+141'),
('cp_no_decision',              'Nothing',  'Nothing Ear (2) Wireless Earbuds',                     'cat_headphones',   'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Nothing+Ear2')
ON CONFLICT (id) DO NOTHING;

-- Populate conformed dim_product
INSERT INTO dim_product (product_id, brand, canonical_name, category_id, category_name, canonical_image_url) VALUES
('cp_sony_good_deal',           'Sony',     'Sony WH-1000XM5 Wireless Noise Cancelling Headphones', 'cat_headphones',   'Headphones',             'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Sony+XM5'),
('cp_iphone_wait',              'Apple',    'Apple iPhone 15 5G Smartphone',                        'cat_smartphones',  'Smartphones',            'https://placehold.co/300x300/FAF8F5/1A1A1A?text=iPhone+15'),
('cp_nike_better_alternative',  'Nike',     'Nike Air Max 90 Sneakers',                             'cat_footwear',     'Athletic Footwear',      'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Nike+AirMax'),
('cp_laptop_suspicious_seller', 'HP',       'HP Pavilion 14 Laptop',                                'cat_laptops',      'Laptops & Computers',    'https://placehold.co/300x300/FAF8F5/1A1A1A?text=HP+Pavilion'),
('cp_new_product_no_history',   'Canon',    'Canon EOS R50 Mirrorless Camera',                      'cat_cameras',      'Mirrorless Cameras',     'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Canon+R50'),
('cp_stale_price',              'Amazon',   'Amazon Kindle Paperwhite 16GB',                        'cat_ereaders',     'E-Readers & Tablets',    'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Kindle'),
('cp_variant_mismatch',         'Apple',    'Apple MacBook Air 13.6-inch M2',                       'cat_laptops',      'Laptops & Computers',    'https://placehold.co/300x300/FAF8F5/1A1A1A?text=MacBook+Air'),
('cp_all_sources_failed',       'Google',   'Google Pixel 8 Pro 5G',                                'cat_smartphones',  'Smartphones',            'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Pixel+8+Pro'),
('cp_seller_changed',           'Samsung',  'Samsung Galaxy S24 5G',                                'cat_smartphones',  'Smartphones',            'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Galaxy+S24'),
('cp_out_of_stock',             'Sony',     'Sony PlayStation 5 Pro Console',                       'cat_gaming',       'Gaming Consoles',        'https://placehold.co/300x300/FAF8F5/1A1A1A?text=PS5+Pro'),
('cp_your_call',                'boAt',     'boAt Airdopes 141 True Wireless Earbuds',              'cat_audio_acc',    'Audio Accessories',      'https://placehold.co/300x300/FAF8F5/1A1A1A?text=boAt+141'),
('cp_no_decision',              'Nothing',  'Nothing Ear (2) Wireless Earbuds',                     'cat_headphones',   'Headphones',             'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Nothing+Ear2')
ON CONFLICT (product_id) DO NOTHING;

-- ==============================================================================
-- 6. SEED CANONICAL_VARIANT & DIM_VARIANT
-- ==============================================================================

INSERT INTO canonical_variant (id, product_id, model_number, variant_name, storage, color, size, attributes_json) VALUES
('cv_sony_good_deal',           'cp_sony_good_deal',           'WH1000XM5/B', 'Black',                       NULL,    'Black',       'Over-Ear', '{"anc": true, "battery_hours": 30, "driver_mm": 30}'::jsonb),
('cv_iphone_wait',              'cp_iphone_wait',              'A3090',       '128GB Blue',                  '128GB', 'Blue',        '6.1 inch', '{"display": "Super Retina XDR", "chip": "A16 Bionic"}'::jsonb),
('cv_nike_better_alternative',  'cp_nike_better_alternative',  'CN8490-100',  'White/Black, UK 9',           NULL,    'White/Black', 'UK 9',     '{"cushioning": "Max Air", "upper": "Mesh and Leather"}'::jsonb),
('cv_laptop_suspicious_seller', 'cp_laptop_suspicious_seller', '14-dv2053TU', 'i5 13th Gen, 16GB, 512GB SSD', '512GB', 'Silver',      '14 inch',  '{"ram": "16GB DDR4", "processor": "Intel i5-1335U"}'::jsonb),
('cv_new_product_no_history',   'cp_new_product_no_history',   '5811C002',    'Body Only, Black',            NULL,    'Black',       'Compact',  '{"sensor_mp": 24.2, "mount": "RF-S"}'::jsonb),
('cv_stale_price',              'cp_stale_price',              'B08N36XNTT',  '16GB, Black, 6.8 inch',       '16GB',  'Black',       '6.8 inch', '{"waterproof": "IPX8", "warm_light": true}'::jsonb),
('cv_variant_mismatch',         'cp_variant_mismatch',         'MLXY3HN/A',   '16GB RAM, 512GB SSD Space Grey','512GB','Space Grey', '13.6 inch','{"ram": "16GB", "storage": "512GB", "soc": "Apple M2"}'::jsonb),
('cv_all_sources_failed',       'cp_all_sources_failed',       'GC3VE',       '128GB, Obsidian',             '128GB', 'Obsidian',    '6.7 inch', '{"ram": "12GB", "display": "Super Actua OLED"}'::jsonb),
('cv_seller_changed',           'cp_seller_changed',           'SM-S921B',    '256GB, Onyx Black',           '256GB', 'Onyx Black',  '6.2 inch', '{"chipset": "Exynos 2400", "battery_mah": 4000}'::jsonb),
('cv_out_of_stock',             'cp_out_of_stock',             'CFI-7000B01', '2TB SSD, White',              '2TB',   'White',       'Standard', '{"gpu": "Enhanced RDNA", "resolution": "4K 60fps"}'::jsonb),
('cv_your_call',                'cp_your_call',                'AIRDOPES-141','Bold Black',                  NULL,    'Bold Black',  'In-Ear',   '{"playtime_hours": 42, "low_latency": true}'::jsonb),
('cv_no_decision',              'cp_no_decision',              'B155',        'White, Hi-Res Audio',         NULL,    'White',       'In-Ear',   '{"anc_db": 40, "codecs": ["LHDC 5.0", "AAC"]}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- Populate conformed dim_variant
INSERT INTO dim_variant (variant_id, product_id, model_number, variant_name, storage, color, size, attributes_json) VALUES
('cv_sony_good_deal',           'cp_sony_good_deal',           'WH1000XM5/B', 'Black',                       NULL,    'Black',       'Over-Ear', '{"anc": true, "battery_hours": 30, "driver_mm": 30}'::jsonb),
('cv_iphone_wait',              'cp_iphone_wait',              'A3090',       '128GB Blue',                  '128GB', 'Blue',        '6.1 inch', '{"display": "Super Retina XDR", "chip": "A16 Bionic"}'::jsonb),
('cv_nike_better_alternative',  'cp_nike_better_alternative',  'CN8490-100',  'White/Black, UK 9',           NULL,    'White/Black', 'UK 9',     '{"cushioning": "Max Air", "upper": "Mesh and Leather"}'::jsonb),
('cv_laptop_suspicious_seller', 'cp_laptop_suspicious_seller', '14-dv2053TU', 'i5 13th Gen, 16GB, 512GB SSD', '512GB', 'Silver',      '14 inch',  '{"ram": "16GB DDR4", "processor": "Intel i5-1335U"}'::jsonb),
('cv_new_product_no_history',   'cp_new_product_no_history',   '5811C002',    'Body Only, Black',            NULL,    'Black',       'Compact',  '{"sensor_mp": 24.2, "mount": "RF-S"}'::jsonb),
('cv_stale_price',              'cp_stale_price',              'B08N36XNTT',  '16GB, Black, 6.8 inch',       '16GB',  'Black',       '6.8 inch', '{"waterproof": "IPX8", "warm_light": true}'::jsonb),
('cv_variant_mismatch',         'cp_variant_mismatch',         'MLXY3HN/A',   '16GB RAM, 512GB SSD Space Grey','512GB','Space Grey', '13.6 inch','{"ram": "16GB", "storage": "512GB", "soc": "Apple M2"}'::jsonb),
('cv_all_sources_failed',       'cp_all_sources_failed',       'GC3VE',       '128GB, Obsidian',             '128GB', 'Obsidian',    '6.7 inch', '{"ram": "12GB", "display": "Super Actua OLED"}'::jsonb),
('cv_seller_changed',           'cp_seller_changed',           'SM-S921B',    '256GB, Onyx Black',           '256GB', 'Onyx Black',  '6.2 inch', '{"chipset": "Exynos 2400", "battery_mah": 4000}'::jsonb),
('cv_out_of_stock',             'cp_out_of_stock',             'CFI-7000B01', '2TB SSD, White',              '2TB',   'White',       'Standard', '{"gpu": "Enhanced RDNA", "resolution": "4K 60fps"}'::jsonb),
('cv_your_call',                'cp_your_call',                'AIRDOPES-141','Bold Black',                  NULL,    'Bold Black',  'In-Ear',   '{"playtime_hours": 42, "low_latency": true}'::jsonb),
('cv_no_decision',              'cp_no_decision',              'B155',        'White, Hi-Res Audio',         NULL,    'White',       'In-Ear',   '{"anc_db": 40, "codecs": ["LHDC 5.0", "AAC"]}'::jsonb)
ON CONFLICT (variant_id) DO NOTHING;

-- ==============================================================================
-- 7. SEED RETAILER_LISTING
-- ==============================================================================

INSERT INTO retailer_listing (id, variant_id, retailer_id, external_product_id, title, product_url, image_url, status) VALUES
-- Sony XM5 Listings
('rl_amazon_sony',    'cv_sony_good_deal',           'amazon',   'B09XS7JWHH', 'Sony WH-1000XM5 Wireless Active Noise Cancelling Headphones - Black', 'https://amazon.in/dp/B09XS7JWHH', 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Sony', 'ACTIVE'),
('rl_flipkart_sony',  'cv_sony_good_deal',           'flipkart', 'ITM19381711', 'SONY WH-1000XM5 Bluetooth Headset with Mic (Black)',                 'https://flipkart.com/p/itm19381711', 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Sony', 'ACTIVE'),
('rl_croma_sony',     'cv_sony_good_deal',           'croma',    '261893',     'Sony WH-1000XM5 Over-Ear Noise Cancellation Headphones (Black)',       'https://croma.com/p/261893', 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Sony', 'ACTIVE'),

-- iPhone 15 Listings
('rl_flipkart_iphone','cv_iphone_wait',              'flipkart', 'ITM89123841', 'Apple iPhone 15 (Blue, 128 GB)',                                      'https://flipkart.com/p/itm89123841', 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=iPhone', 'ACTIVE'),
('rl_amazon_iphone',  'cv_iphone_wait',              'amazon',   'B0CHX1W1XY', 'Apple iPhone 15 (128 GB) - Blue',                                      'https://amazon.in/dp/B0CHX1W1XY', 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=iPhone', 'ACTIVE'),
('rl_reliance_iphone','cv_iphone_wait',              'reliance', '493839210',  'Apple iPhone 15 128 GB Blue Smartphone',                              'https://reliancedigital.in/p/493839210', 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=iPhone', 'ACTIVE'),

-- Nike Air Max 90 Listings
('rl_amazon_nike',    'cv_nike_better_alternative',  'amazon',   'B08N8PQ8T1', 'Nike Mens Air Max 90 Running Shoe White/Black UK 9',                   'https://amazon.in/dp/B08N8PQ8T1', 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Nike', 'ACTIVE'),
('rl_myntra_nike',    'cv_nike_better_alternative',  'myntra',   '19284729',   'Nike Men White & Black Air Max 90 Leather Sneakers',                   'https://myntra.com/19284729', 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Nike', 'ACTIVE'),
('rl_flipkart_nike',  'cv_nike_better_alternative',  'flipkart', 'ITM82749102', 'NIKE Air Max 90 Sneakers For Men (White, Black)',                     'https://flipkart.com/p/itm82749102', 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Nike', 'ACTIVE'),

-- HP Pavilion 14 Listings
('rl_amazon_hp',      'cv_laptop_suspicious_seller', 'amazon',   'B09WQ9H5K1', 'HP Pavilion 14, 13th Gen Intel Core i5 (16GB RAM/512GB SSD)',          'https://amazon.in/dp/B09WQ9H5K1', 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=HP', 'ACTIVE'),
('rl_croma_hp',       'cv_laptop_suspicious_seller', 'croma',    '271923',     'HP Pavilion 14-dv2053TU Intel Core i5 13th Gen Laptop (16GB/512GB)',    'https://croma.com/p/271923', 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=HP', 'ACTIVE'),

-- Canon EOS R50 Listings
('rl_croma_canon',    'cv_new_product_no_history',   'croma',    '281923',     'Canon EOS R50 24.2 MP Mirrorless Camera (Body Only, Black)',           'https://croma.com/p/281923', 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Canon', 'ACTIVE'),

-- Kindle Paperwhite Listings
('rl_amazon_kindle',  'cv_stale_price',              'amazon',   'B08N36XNTT', 'All-new Kindle Paperwhite (16 GB) - 6.8 inch display, adjustable warm','https://amazon.in/dp/B08N36XNTT', 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Kindle', 'ACTIVE'),

-- MacBook Air M2 Listings
('rl_flipkart_macbook','cv_variant_mismatch',         'flipkart', 'ITM73819284', 'Apple MacBook Air M2 - (16 GB/512 GB SSD/macOS Monterey)',           'https://flipkart.com/p/itm73819284', 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=MacBook', 'ACTIVE'),
('rl_amazon_macbook',  'cv_variant_mismatch',         'amazon',   'B0B3C9L7B9', 'Apple 2022 MacBook Air Laptop with M2 chip (13.6-inch, 16GB, 512GB)', 'https://amazon.in/dp/B0B3C9L7B9', 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=MacBook', 'ACTIVE'),

-- Pixel 8 Pro Listings
('rl_flipkart_pixel', 'cv_all_sources_failed',       'flipkart', 'ITM58291039', 'Google Pixel 8 Pro (Obsidian, 128 GB)',                              'https://flipkart.com/p/itm58291039', 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Pixel', 'ACTIVE'),

-- Galaxy S24 Listings
('rl_amazon_samsung', 'cv_seller_changed',           'amazon',   'B0CQ1XT8H5', 'Samsung Galaxy S24 5G (Onyx Black, 8GB, 256GB Storage)',               'https://amazon.in/dp/B0CQ1XT8H5', 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Samsung', 'ACTIVE'),

-- PS5 Pro Listings
('rl_amazon_ps5',     'cv_out_of_stock',             'amazon',   'B0DF9X8C2J', 'Sony PlayStation 5 Pro Digital Edition Console 2TB SSD',               'https://amazon.in/dp/B0DF9X8C2J', 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=PS5', 'OUT_OF_STOCK'),

-- boAt Airdopes 141 Listings
('rl_amazon_boat',    'cv_your_call',                'amazon',   'B09N3ZNHTY', 'boAt Airdopes 141 True Wireless Earbuds with 42H Playtime',             'https://amazon.in/dp/B09N3ZNHTY', 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=boAt', 'ACTIVE'),

-- Nothing Ear (2) Listings
('rl_flipkart_nothing','cv_no_decision',             'flipkart', 'ITM93819284', 'Nothing Ear (2) Bluetooth Headset (White)',                          'https://flipkart.com/p/itm93819284', 'https://placehold.co/300x300/FAF8F5/1A1A1A?text=Nothing', 'ACTIVE')
ON CONFLICT (id) DO NOTHING;

-- ==============================================================================
-- 8. SEED SELLER_OFFER (Current Merchant Offers)
-- ==============================================================================

INSERT INTO seller_offer (id, listing_id, seller_id, price, shipping_cost, discount, currency, availability, observed_at, collected_at, source_type) VALUES
-- Sony XM5 (Current Best Buy Deal)
('so_sony_amazon_appario',    'rl_amazon_sony',    'seller_appario',    22499.00,   0.00, 7491.00, 'INR', 'IN_STOCK', '2026-10-07 10:00:00+05:30', '2026-10-07 10:02:00+05:30', 'SCRAPER'),
('so_sony_flipkart_retailnet','rl_flipkart_sony',  'seller_retailnet',  24999.00,   0.00, 4991.00, 'INR', 'IN_STOCK', '2026-10-07 09:30:00+05:30', '2026-10-07 09:32:00+05:30', 'SCRAPER'),
('so_sony_croma_official',    'rl_croma_sony',     'seller_croma',      26990.00,   0.00, 3000.00, 'INR', 'IN_STOCK', '2026-10-07 08:00:00+05:30', '2026-10-07 08:05:00+05:30', 'API'),

-- iPhone 15 (Inflated Price Peak)
('so_iphone_flipkart_supercom','rl_flipkart_iphone','seller_supercomnet',65999.00,  0.00, 3991.00, 'INR', 'IN_STOCK', '2026-10-07 11:00:00+05:30', '2026-10-07 11:02:00+05:30', 'SCRAPER'),
('so_iphone_amazon_appario',  'rl_amazon_iphone',  'seller_appario',    66490.00,   0.00, 3500.00, 'INR', 'IN_STOCK', '2026-10-07 10:45:00+05:30', '2026-10-07 10:48:00+05:30', 'SCRAPER'),
('so_iphone_reliance_official','rl_reliance_iphone','seller_reliance',  65900.00,   0.00, 4090.00, 'INR', 'IN_STOCK', '2026-10-07 09:15:00+05:30', '2026-10-07 09:20:00+05:30', 'SCRAPER'),

-- Nike Air Max 90 (Amazon vs Myntra Alternative)
('so_nike_amazon_retailnet',  'rl_amazon_nike',    'seller_retailnet',  11499.00,  99.00,  500.00, 'INR', 'IN_STOCK', '2026-10-07 10:30:00+05:30', '2026-10-07 10:32:00+05:30', 'SCRAPER'),
('so_nike_myntra_direct',     'rl_myntra_nike',    'seller_nike_india',  8999.00,   0.00, 3000.00, 'INR', 'IN_STOCK', '2026-10-07 10:15:00+05:30', '2026-10-07 10:18:00+05:30', 'SCRAPER'),

-- HP Pavilion 14 (Risky seller on Amazon vs Verified Croma)
('so_hp_amazon_quickdeal',    'rl_amazon_hp',      'seller_quickdeal',  46999.00, 150.00,12000.00, 'INR', 'IN_STOCK', '2026-10-07 09:00:00+05:30', '2026-10-07 09:02:00+05:30', 'SCRAPER'),
('so_hp_croma_official',      'rl_croma_hp',       'seller_croma',      51999.00,   0.00, 7000.00, 'INR', 'IN_STOCK', '2026-10-07 09:10:00+05:30', '2026-10-07 09:12:00+05:30', 'API'),

-- Canon EOS R50 (Brand new release)
('so_canon_croma_official',   'rl_croma_canon',    'seller_croma',      74999.00,   0.00,    0.00, 'INR', 'IN_STOCK', '2026-10-07 11:20:00+05:30', '2026-10-07 11:22:00+05:30', 'API'),

-- Kindle Paperwhite (Stale scraper cache)
('so_kindle_amazon_cocoblu',  'rl_amazon_kindle',  'seller_cocoblu',    14999.00,   0.00, 1000.00, 'INR', 'IN_STOCK', '2026-09-23 08:00:00+05:30', '2026-09-23 08:05:00+05:30', 'SCRAPER'),

-- MacBook Air M2 (Variant mismatch risk)
('so_macbook_flipkart_inditech','rl_flipkart_macbook','seller_inditech',79990.00,   0.00,20000.00, 'INR', 'IN_STOCK', '2026-10-07 08:45:00+05:30', '2026-10-07 08:48:00+05:30', 'SCRAPER'),
('so_macbook_amazon_appario', 'rl_amazon_macbook', 'seller_appario',    94990.00,   0.00, 5000.00, 'INR', 'IN_STOCK', '2026-10-07 08:50:00+05:30', '2026-10-07 08:52:00+05:30', 'SCRAPER'),

-- Pixel 8 Pro (Unknown/Scraper blocked)
('so_pixel_flipkart_unverified','rl_flipkart_pixel','seller_unverified',84999.00,   0.00,22000.00, 'INR', 'LIMITED_STOCK','2026-10-07 07:00:00+05:30','2026-10-07 07:02:00+05:30', 'SCRAPER'),

-- Samsung S24 (Unrated merchant buy-box hijack)
('so_samsung_amazon_fastgizmos','rl_amazon_samsung','seller_fastgizmos', 59999.00, 200.00,15000.00, 'INR', 'IN_STOCK', '2026-10-07 10:50:00+05:30', '2026-10-07 10:53:00+05:30', 'SCRAPER'),

-- PS5 Pro (Scalper markup, official out of stock)
('so_ps5_amazon_scalper',     'rl_amazon_ps5',     'seller_scalperdeals',79990.00, 450.00,    0.00, 'INR', 'OUT_OF_STOCK','2026-10-07 11:15:00+05:30','2026-10-07 11:18:00+05:30', 'SCRAPER'),

-- boAt Airdopes 141 (Everyday stable price)
('so_boat_amazon_cocoblu',    'rl_amazon_boat',    'seller_cocoblu',       999.00,   0.00, 3500.00, 'INR', 'IN_STOCK', '2026-10-07 11:30:00+05:30', '2026-10-07 11:32:00+05:30', 'SCRAPER'),

-- Nothing Ear (2) (Volatile price swings)
('so_nothing_flipkart_supercom','rl_flipkart_nothing','seller_supercomnet',7499.00,  0.00, 2500.00, 'INR', 'IN_STOCK', '2026-10-07 11:25:00+05:30', '2026-10-07 11:28:00+05:30', 'SCRAPER')
ON CONFLICT (id) DO NOTHING;

-- ==============================================================================
-- 9. SEED FACT_PRICE_HISTORY (Analytical Time-Series Facts)
-- Dense price history points for trending, lowest price computation, and charts.
-- ==============================================================================

-- 9.1 Sony WH-1000XM5: Price trend dropping from ₹27,999 to historical low of ₹22,499
INSERT INTO fact_price_history (variant_id, retailer_id, seller_id, observed_at, collected_at, price, currency, shipping_cost, discount, in_stock, availability_status, source_url, source_type, date_key) VALUES
('cv_sony_good_deal', 'amazon', 'seller_appario', '2026-07-15 10:00:00+05:30', '2026-07-15 10:02:00+05:30', 29990.00, 'INR', 0.00,    0.00, TRUE, 'IN_STOCK', 'https://amazon.in/dp/B09XS7JWHH', 'SCRAPER', 20260715),
('cv_sony_good_deal', 'amazon', 'seller_appario', '2026-08-01 10:00:00+05:30', '2026-08-01 10:02:00+05:30', 28990.00, 'INR', 0.00, 1000.00, TRUE, 'IN_STOCK', 'https://amazon.in/dp/B09XS7JWHH', 'SCRAPER', 20260801),
('cv_sony_good_deal', 'amazon', 'seller_appario', '2026-08-20 10:00:00+05:30', '2026-08-20 10:02:00+05:30', 27999.00, 'INR', 0.00, 1991.00, TRUE, 'IN_STOCK', 'https://amazon.in/dp/B09XS7JWHH', 'SCRAPER', 20260820),
('cv_sony_good_deal', 'amazon', 'seller_appario', '2026-09-05 10:00:00+05:30', '2026-09-05 10:02:00+05:30', 26490.00, 'INR', 0.00, 3500.00, TRUE, 'IN_STOCK', 'https://amazon.in/dp/B09XS7JWHH', 'SCRAPER', 20260905),
('cv_sony_good_deal', 'amazon', 'seller_appario', '2026-09-20 10:00:00+05:30', '2026-09-20 10:02:00+05:30', 25999.00, 'INR', 0.00, 3991.00, TRUE, 'IN_STOCK', 'https://amazon.in/dp/B09XS7JWHH', 'SCRAPER', 20260920),
('cv_sony_good_deal', 'amazon', 'seller_appario', '2026-10-01 10:00:00+05:30', '2026-10-01 10:02:00+05:30', 24999.00, 'INR', 0.00, 4991.00, TRUE, 'IN_STOCK', 'https://amazon.in/dp/B09XS7JWHH', 'SCRAPER', 20261001),
('cv_sony_good_deal', 'amazon', 'seller_appario', '2026-10-05 10:00:00+05:30', '2026-10-05 10:02:00+05:30', 23999.00, 'INR', 0.00, 5991.00, TRUE, 'IN_STOCK', 'https://amazon.in/dp/B09XS7JWHH', 'SCRAPER', 20261005),
('cv_sony_good_deal', 'amazon', 'seller_appario', '2026-10-07 10:00:00+05:30', '2026-10-07 10:02:00+05:30', 22499.00, 'INR', 0.00, 7491.00, TRUE, 'IN_STOCK', 'https://amazon.in/dp/B09XS7JWHH', 'SCRAPER', 20261007),
-- Sony XM5 Flipkart comparison points
('cv_sony_good_deal', 'flipkart','seller_retailnet','2026-10-05 09:30:00+05:30', '2026-10-05 09:32:00+05:30', 25999.00, 'INR', 0.00, 3991.00, TRUE, 'IN_STOCK', 'https://flipkart.com/p/itm19381711', 'SCRAPER', 20261005),
('cv_sony_good_deal', 'flipkart','seller_retailnet','2026-10-07 09:30:00+05:30', '2026-10-07 09:32:00+05:30', 24999.00, 'INR', 0.00, 4991.00, TRUE, 'IN_STOCK', 'https://flipkart.com/p/itm19381711', 'SCRAPER', 20261007);

-- 9.2 Apple iPhone 15: Price surging towards 90-day high (WAIT condition)
INSERT INTO fact_price_history (variant_id, retailer_id, seller_id, observed_at, collected_at, price, currency, shipping_cost, discount, in_stock, availability_status, source_url, source_type, date_key) VALUES
('cv_iphone_wait', 'flipkart', 'seller_supercomnet', '2026-07-20 11:00:00+05:30', '2026-07-20 11:02:00+05:30', 52999.00, 'INR', 0.00, 16991.00, TRUE, 'IN_STOCK', 'https://flipkart.com/p/itm89123841', 'SCRAPER', 20260720),
('cv_iphone_wait', 'flipkart', 'seller_supercomnet', '2026-08-15 11:00:00+05:30', '2026-08-15 11:02:00+05:30', 54999.00, 'INR', 0.00, 14991.00, TRUE, 'IN_STOCK', 'https://flipkart.com/p/itm89123841', 'SCRAPER', 20260815),
('cv_iphone_wait', 'flipkart', 'seller_supercomnet', '2026-09-10 11:00:00+05:30', '2026-09-10 11:02:00+05:30', 57999.00, 'INR', 0.00, 11991.00, TRUE, 'IN_STOCK', 'https://flipkart.com/p/itm89123841', 'SCRAPER', 20260910),
('cv_iphone_wait', 'flipkart', 'seller_supercomnet', '2026-09-25 11:00:00+05:30', '2026-09-25 11:02:00+05:30', 61999.00, 'INR', 0.00,  7991.00, TRUE, 'IN_STOCK', 'https://flipkart.com/p/itm89123841', 'SCRAPER', 20260925),
('cv_iphone_wait', 'flipkart', 'seller_supercomnet', '2026-10-01 11:00:00+05:30', '2026-10-01 11:02:00+05:30', 64499.00, 'INR', 0.00,  5491.00, TRUE, 'IN_STOCK', 'https://flipkart.com/p/itm89123841', 'SCRAPER', 20261001),
('cv_iphone_wait', 'flipkart', 'seller_supercomnet', '2026-10-07 11:00:00+05:30', '2026-10-07 11:02:00+05:30', 65999.00, 'INR', 0.00,  3991.00, TRUE, 'IN_STOCK', 'https://flipkart.com/p/itm89123841', 'SCRAPER', 20261007);

-- 9.3 Nike Air Max 90: Disparity between Amazon (₹11,499) and Myntra (₹8,999)
INSERT INTO fact_price_history (variant_id, retailer_id, seller_id, observed_at, collected_at, price, currency, shipping_cost, discount, in_stock, availability_status, source_url, source_type, date_key) VALUES
('cv_nike_better_alternative', 'amazon', 'seller_retailnet', '2026-10-05 10:30:00+05:30', '2026-10-05 10:32:00+05:30', 11499.00, 'INR', 99.00, 500.00, TRUE, 'IN_STOCK', 'https://amazon.in/dp/B08N8PQ8T1', 'SCRAPER', 20261005),
('cv_nike_better_alternative', 'amazon', 'seller_retailnet', '2026-10-07 10:30:00+05:30', '2026-10-07 10:32:00+05:30', 11499.00, 'INR', 99.00, 500.00, TRUE, 'IN_STOCK', 'https://amazon.in/dp/B08N8PQ8T1', 'SCRAPER', 20261007),
('cv_nike_better_alternative', 'myntra', 'seller_nike_india','2026-10-05 10:15:00+05:30', '2026-10-05 10:18:00+05:30',  8999.00, 'INR',  0.00,3000.00, TRUE, 'IN_STOCK', 'https://myntra.com/19284729', 'SCRAPER', 20261005),
('cv_nike_better_alternative', 'myntra', 'seller_nike_india','2026-10-07 10:15:00+05:30', '2026-10-07 10:18:00+05:30',  8999.00, 'INR',  0.00,3000.00, TRUE, 'IN_STOCK', 'https://myntra.com/19284729', 'SCRAPER', 20261007);

-- 9.4 Sony PS5 Pro: Out of stock event at official MSRP, markup to ₹79,990
INSERT INTO fact_price_history (variant_id, retailer_id, seller_id, observed_at, collected_at, price, currency, shipping_cost, discount, in_stock, availability_status, source_url, source_type, date_key) VALUES
('cv_out_of_stock', 'amazon', 'seller_appario',    '2026-09-01 11:15:00+05:30', '2026-09-01 11:18:00+05:30', 69990.00, 'INR', 0.00, 0.00, TRUE,  'IN_STOCK',     'https://amazon.in/dp/B0DF9X8C2J', 'SCRAPER', 20260901),
('cv_out_of_stock', 'amazon', 'seller_scalperdeals','2026-10-01 11:15:00+05:30', '2026-10-01 11:18:00+05:30', 79990.00, 'INR',450.00, 0.00, FALSE, 'OUT_OF_STOCK', 'https://amazon.in/dp/B0DF9X8C2J', 'SCRAPER', 20261001),
('cv_out_of_stock', 'amazon', 'seller_scalperdeals','2026-10-07 11:15:00+05:30', '2026-10-07 11:18:00+05:30', 79990.00, 'INR',450.00, 0.00, FALSE, 'OUT_OF_STOCK', 'https://amazon.in/dp/B0DF9X8C2J', 'SCRAPER', 20261007);

-- 9.5 boAt Airdopes 141: Extremely stable pricing around ₹999
INSERT INTO fact_price_history (variant_id, retailer_id, seller_id, observed_at, collected_at, price, currency, shipping_cost, discount, in_stock, availability_status, source_url, source_type, date_key) VALUES
('cv_your_call', 'amazon', 'seller_cocoblu', '2026-08-01 11:30:00+05:30', '2026-08-01 11:32:00+05:30', 999.00, 'INR', 0.00, 3500.00, TRUE, 'IN_STOCK', 'https://amazon.in/dp/B09N3ZNHTY', 'SCRAPER', 20260801),
('cv_your_call', 'amazon', 'seller_cocoblu', '2026-09-01 11:30:00+05:30', '2026-09-01 11:32:00+05:30', 899.00, 'INR', 0.00, 3600.00, TRUE, 'IN_STOCK', 'https://amazon.in/dp/B09N3ZNHTY', 'SCRAPER', 20260901),
('cv_your_call', 'amazon', 'seller_cocoblu', '2026-10-07 11:30:00+05:30', '2026-10-07 11:32:00+05:30', 999.00, 'INR', 0.00, 3500.00, TRUE, 'IN_STOCK', 'https://amazon.in/dp/B09N3ZNHTY', 'SCRAPER', 20261007);

-- ==============================================================================
-- 10. SEED FACT_RECOMMENDATION (Engine Decision Snapshots)
-- ==============================================================================

INSERT INTO fact_recommendation (
    recommendation_id, product_id, timestamp, decision, buy_point, model_version,
    matching_model_version, decision_rules_version, confidence_level, current_price,
    predicted_direction, primary_reason, data_freshness, data_coverage, date_key
) VALUES
-- 1. Sony XM5 (BUY)
('rec_sony_good_deal', 'cp_sony_good_deal', '2026-10-07 10:05:00+05:30', 'BUY', 23999.00,
 'v2.4.1-hybrid', 'match-bert-v3', 'rules-v1.8', 'HIGH', 22499.00, 'FALLING',
 'This is the lowest price recorded in 90 days. Backed by verified authorized merchant with full manufacturer warranty.',
 '3 mins ago', 0.98, 20261007),

-- 2. Apple iPhone 15 (WAIT)
('rec_iphone_wait', 'cp_iphone_wait', '2026-10-07 11:05:00+05:30', 'WAIT', 54999.00,
 'v2.4.1-hybrid', 'match-bert-v3', 'rules-v1.8', 'HIGH', 65999.00, 'RISING',
 'Prices recently surged to ₹65,999 near the 90-day peak. A festival sale is expected within 10 days where it often drops below ₹55,000.',
 '5 mins ago', 0.95, 20261007),

-- 3. Nike Air Max 90 (CHECK_ALT)
('rec_nike_alt', 'cp_nike_better_alternative', '2026-10-07 10:35:00+05:30', 'CHECK_ALT', 9200.00,
 'v2.4.1-hybrid', 'match-bert-v3', 'rules-v1.8', 'HIGH', 11499.00, 'STABLE',
 'The current Amazon price is ₹11,499, but Myntra currently has the exact same shoe for ₹8,999 directly from Nike India.',
 '2 mins ago', 0.92, 20261007),

-- 4. HP Pavilion 14 (CAUTION)
('rec_hp_caution', 'cp_laptop_suspicious_seller', '2026-10-07 09:05:00+05:30', 'CAUTION', 51999.00,
 'v2.4.1-hybrid', 'match-bert-v3', 'rules-v1.8', 'MEDIUM', 46999.00, 'STABLE',
 'The price is unusually low (₹46,999), but this merchant has a 2.3 rating with multiple reports of refurbished units sold as new.',
 '15 mins ago', 0.88, 20261007),

-- 5. Canon EOS R50 (NO_DECISION)
('rec_canon_no_dec', 'cp_new_product_no_history', '2026-10-07 11:25:00+05:30', 'NO_DECISION', NULL,
 'v2.4.1-hybrid', 'match-bert-v3', 'rules-v1.8', 'LOW', 74999.00, 'STABLE',
 'This camera was released only 3 days ago. There is not enough historical pricing data to predict whether a discount cycle will occur soon.',
 '8 mins ago', 0.40, 20261007),

-- 6. Kindle Paperwhite (CAUTION - Stale data)
('rec_kindle_stale', 'cp_stale_price', '2026-10-07 08:10:00+05:30', 'CAUTION', 13499.00,
 'v2.4.1-hybrid', 'match-bert-v3', 'rules-v1.8', 'LOW', 14999.00, 'STABLE',
 'This price was last recorded 14 days ago. Scraper connectivity was interrupted, so live checkout price and stock may differ.',
 '14 days ago', 0.20, 20261007),

-- 7. MacBook Air M2 (CAUTION - Variant mismatch)
('rec_macbook_mismatch', 'cp_variant_mismatch', '2026-10-07 08:55:00+05:30', 'CAUTION', 89900.00,
 'v2.4.1-hybrid', 'match-bert-v3', 'rules-v1.8', 'MEDIUM', 79990.00, 'STABLE',
 'Potential variant mismatch detected: The listing title states 16GB RAM / 512GB SSD, but the model number corresponds to 8GB RAM / 256GB SSD.',
 '6 mins ago', 0.90, 20261007),

-- 8. Pixel 8 Pro (NO_DECISION - Anti-bot blocks)
('rec_pixel_blocked', 'cp_all_sources_failed', '2026-10-07 07:10:00+05:30', 'NO_DECISION', NULL,
 'v2.4.1-hybrid', 'match-bert-v3', 'rules-v1.8', 'LOW', 84999.00, 'STABLE',
 'All retail scrapers timed out or returned HTTP 503 / 403 blocks. Live inventory could not be confirmed.',
 '60 mins ago', 0.15, 20261007),

-- 9. Samsung S24 (CAUTION - Seller changed)
('rec_samsung_changed', 'cp_seller_changed', '2026-10-07 10:55:00+05:30', 'CAUTION', 54999.00,
 'v2.4.1-hybrid', 'match-bert-v3', 'rules-v1.8', 'MEDIUM', 59999.00, 'STABLE',
 'The default Buy Box seller switched in the last 12 hours from verified direct retailer to an unrated third-party merchant.',
 '10 mins ago', 0.85, 20261007),

-- 10. PS5 Pro (WAIT - Scalper markup)
('rec_ps5_scalper', 'cp_out_of_stock', '2026-10-07 11:20:00+05:30', 'WAIT', 69990.00,
 'v2.4.1-hybrid', 'match-bert-v3', 'rules-v1.8', 'HIGH', 79990.00, 'RISING',
 'Official stock is currently sold out across all authorized retailers. Only third-party sellers are listing units with a ₹10,000+ markup.',
 '7 mins ago', 0.94, 20261007),

-- 11. boAt Airdopes 141 (YOUR_CALL)
('rec_boat_your_call', 'cp_your_call', '2026-10-07 11:35:00+05:30', 'YOUR_CALL', 999.00,
 'v2.4.1-hybrid', 'match-bert-v3', 'rules-v1.8', 'LOW', 999.00, 'STABLE',
 'This is an everyday value item at ₹999. Price fluctuation over the past 90 days has been under ₹100. If you need it today, go ahead.',
 '1 min ago', 0.97, 20261007),

-- 12. Nothing Ear (2) (NO_DECISION)
('rec_nothing_volatile', 'cp_no_decision', '2026-10-07 11:30:00+05:30', 'NO_DECISION', NULL,
 'v2.4.1-hybrid', 'match-bert-v3', 'rules-v1.8', 'LOW', 7499.00, 'VOLATILE',
 'Conflicting market signals: Prices have been volatile with frequent erratic swings, and rumors of a successor announcement make a firm call unreliable.',
 '4 mins ago', 0.89, 20261007)
ON CONFLICT (recommendation_id) DO NOTHING;

-- ==============================================================================
-- 11. SEED FACT_RECOMMENDATION_OUTCOME (Model Prediction Accuracy Audits)
-- ==============================================================================

INSERT INTO fact_recommendation_outcome (
    recommendation_id, observed_future_price, outcome_status, evaluated_at
) VALUES
-- Historical outcome for prior Sony XM5 recommendation (Validated savings)
('rec_sony_good_deal', 25999.00, 'VALIDATED', '2026-10-07 12:00:00+05:30'),

-- Historical outcome for iPhone 15 wait recommendation (Validated festival discount drop)
('rec_iphone_wait', 53999.00, 'ACCURATE', '2026-10-07 12:00:00+05:30'),

-- Alternative check validation (Customer saved ₹2,500 on Myntra)
('rec_nike_alt', 8999.00, 'ACCURATE', '2026-10-07 12:00:00+05:30'),

-- Caution outcome validation (Avoided refurbished unit complaints)
('rec_hp_caution', 46999.00, 'ACCURATE', '2026-10-07 12:00:00+05:30'),

-- Recent recommendation still pending future evaluation window
('rec_ps5_scalper', NULL, 'PENDING_EVALUATION', '2026-10-07 12:00:00+05:30'),
('rec_boat_your_call', 999.00, 'VALIDATED', '2026-10-07 12:00:00+05:30');
