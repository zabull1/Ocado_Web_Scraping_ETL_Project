SELECT count(*) FROM ocado;

-- The store manager believes that there is a relationship between the price of the product and the review the product get?
-- Is this so? What are the price of the first 10 product that have a review or 4.3 or above?

SELECT title,price, review FROM ocado
WHERE review >= 4.3
ORDER BY price DESC
LIMIT 10;

-- How many people have reviews the second worst product?

WITH CTE AS (SELECT title, review, review_count, row_number() OVER(ORDER BY review) AS rn FROM ocado
ORDER BY review ASc)
SELECT title, review, review_count FROM CTE  WHERE rn = 2;

-- What is the name, manufacturer and website of the 2nd most expensive product?
WITH CTE AS (SELECT title, manufacturer, link, CAST(price AS DECIMAL(4,1)) AS price,  row_number() OVER(ORDER BY price DESC) AS rn FROM ocado
ORDER BY price DESC)

SELECT title, manufacturer, link, price FROM CTE  WHERE rn = 2 ;

-- How many products cost £5 or more?
SELECT COUNT(*) FROM ocado WHERE price > 5 ;

-- How many products are in-house products (i.e., those WITH Ocado AS Brand names)?
SELECT COUNT(*) FROM ocado WHERE brand LIKE '%"Ocado"%';

-- Please classify the products AS suitable for vegans or not? How many product fall in both clASses?
SELECT COUNT(*) AS Vegans_count, (137 - Vegans_count) AS Non_vegans_count 
FROM ocado 
WHERE  information  LIKE '%Suitable for Vegetarians%' OR information  LIKE '%Suitable for Vegans%';

-- What are the id, url and price of the products that contain butter (see the DESCription column)?
SELECT id, link, price, DESCription, ingredient FROM ocado WHERE DESCription LIKE '%Butter%' OR ingredient LIKE '%Butter%';