-- NYC Nonprofit Capstone SQL Queries

-- Query 1: Join + GROUP BY - nonprofit density by borough
SELECT
    n.borough,
    COUNT(*) AS nonprofit_count,
    p.total_population,
    p.poverty_rate,
    ROUND(COUNT(*) * 10000.0 / p.total_population, 2) AS nonprofits_per_10k
FROM nonprofits AS n
JOIN borough_poverty AS p
    ON n.borough = p.borough
GROUP BY n.borough, p.total_population, p.poverty_rate
ORDER BY nonprofits_per_10k DESC;

-- Query 2: Join + WHERE + GROUP BY - faith-based nonprofits by borough
SELECT
    n.borough,
    COUNT(*) AS faith_based_nonprofits,
    p.poverty_rate
FROM nonprofits AS n
JOIN borough_poverty AS p
    ON n.borough = p.borough
WHERE n.is_faith_based = 1
GROUP BY n.borough, p.poverty_rate
ORDER BY faith_based_nonprofits DESC;

-- Query 3: Join + WHERE + GROUP BY - Human Services (NTEE P) and community need
SELECT
    n.borough,
    COUNT(*) AS human_services_nonprofits,
    p.poverty_rate,
    ROUND(COUNT(*) * 10000.0 / p.total_population, 2) AS human_services_per_10k
FROM nonprofits AS n
JOIN borough_poverty AS p
    ON n.borough = p.borough
WHERE n.ntee_major = 'P'
GROUP BY n.borough, p.total_population, p.poverty_rate
ORDER BY p.poverty_rate DESC;

-- Query 4: Subquery - boroughs above the NYC borough-average poverty rate
SELECT
    borough,
    poverty_rate
FROM borough_poverty
WHERE poverty_rate > (SELECT AVG(poverty_rate) FROM borough_poverty)
ORDER BY poverty_rate DESC;
