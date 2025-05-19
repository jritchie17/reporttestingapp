-- Materialize the CTE into a temporary table
SELECT DISTINCT 
        CONCAT(RTRIM(b.ldr_entity_id), '-', RTRIM(b.am_location), ' ', ca.name) AS Center,
        CASE 
            WHEN CONCAT(b.am_account, '-', b.am_subaccount) = '7322-0000' 
                THEN '7322-0000 Contracted Anesthesia Services'
            ELSE ad.CAReportName 
        END AS CAReportName,
        CONCAT(a.am_account, '-', a.am_subaccount) AS FullAccount,
        b.am_account,
        b.amt_class_type,
        b.processing_yr,
        b.ldr_amt_1, b.ldr_amt_2, b.ldr_amt_3, b.ldr_amt_4, b.ldr_amt_5, b.ldr_amt_6,
        b.ldr_amt_11, b.ldr_amt_12   
INTO #HierarchyData
 FROM 
        CognosTesting.dbo.Nassql7_DBSglep_ldr_acct AS a
    INNER JOIN 
        CognosTesting.dbo.Nassql7_DBSglep_ldr_acct_bal AS b
        ON a.ldr_entity_id = b.ldr_entity_id
        AND a.am_location = b.am_location
        AND a.am_account = b.am_account
        AND a.am_subaccount = b.am_subaccount
    LEFT JOIN (
        SELECT JoinColumn, CAReportName, TopParent
        FROM CognosTesting.dbo.AccountDimension
        WHERE TopParent IN ('Statistical Accounts', 'Center Trend', 'Statement of Operations')
    ) ad
        ON ad.JoinColumn = CONCAT(b.am_account, '-', b.am_subaccount)
    INNER JOIN (
        SELECT DISTINCT Center, name 
        FROM CognosTesting.dbo.Cognos_FlatFile_CenterAttribute
    ) AS ca
        ON ca.Center = CONCAT(RTRIM(b.ldr_entity_id), '-', RTRIM(b.am_location))
    WHERE 
        b.processing_yr IN ('2024', '2025')
        AND ca.center IN ('2001-001', '2001-002', '2003-001', '2003-002', '2005-001', '2009-001', '2011-001', '2013-001', '2015-001', '2018-001')
        AND (
            CONCAT(a.am_account, '-', a.am_subaccount) LIKE 'R1%' 
            OR CONCAT(a.am_account, '-', a.am_subaccount) LIKE 'S1%'
			OR CONCAT(a.am_account, '-', a.am_subaccount) = 'S005-0000'
            OR CONCAT(a.am_account, '-', a.am_subaccount) IN (
                '1111-1102', '1111-1105', '1111-1139', '1111-1144', '1111-1147', '1112-1102', '1112-1105', 
                '1131-1102', '1134-1102', '5312-5303', '5322-5303', '6101-6001', '6103-6001', '6103-6060', 
                '6104-6001', '6109-6001', '6113-6001', '6115-6001', '6131-6001', '6137-6001', '6142-6001', 
                '6143-6001', '6144-6001', '6201-6001', '6203-6001', '6213-6001', '6301-6001', '6303-6001', 
                '6313-6001', '6501-6001', '7115-0000', '7115-7004', '7116-0000', '7117-0000', '7125-0000', 
                '7127-0000', '7129-0000', '7141-0000', '7141-7004', '7143-0000', '7145-0000', '7161-0000', 
                '7163-0000', '7165-0000', '7173-0000', '7201-0000', '7203-0000', '7205-0000', '7207-0000', 
                '7209-7005', '7209-7006', '7217-0000', '7223-0000', '7225-0000', '7301-0000', '7303-0000', 
                '7305-0000', '7306-0000', '7307-0000', '7309-0000', '7309-7001', '7311-0000', '7312-0000', 
                '7313-0000', '7317-0000', '7319-0000', '7321-0000', '7322-0000', '7323-0000', '7323-7001', 
                '7327-0000', '7329-0000', '7331-0000', '7333-0000', '7337-0000', '7338-0000', '7339-0000', 
                '7341-0000', '7343-0000', '7347-0000', '7349-0000', '7351-0000', '7353-0000', '7355-0000', 
                '7356-0000', '7357-0000', '7361-0000', '7363-0000', '7369-0000', '7370-0000', '7371-0000', 
                '7411-0000', '7412-0000', '7415-0000', '7416-0000', '7421-0000', '7422-0000', '7431-0000', 
                '7501-0000', '7505-0000', '7507-0000', '7509-0000', '7654-0000', '7655-0000', '7656-0000', 
                '7912-7011', '7912-7012', '8101-0000', '8102-0000', '8102-1202', '8104-0000', '8109-0000', 
                '8139-0000', '8143-0000', '8201-0000', '8211-0000', '8212-0000', '8213-0000', '8214-0000', 
                '8215-0000', '8221-0000', '8221-8201', 'S005-0000'
            )
        )

-- Main data rows
SELECT 
    h.Center,
    h.CAReportName,
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' THEN h.ldr_amt_11 ELSE 0 END), 2) AS DECIMAL(18,2)), 0) AS [Nov 2024],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' THEN h.ldr_amt_12 ELSE 0 END), 2) AS DECIMAL(18,2)), 0) AS [Dec 2024],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' THEN h.ldr_amt_1 ELSE 0 END), 2) AS DECIMAL(18,2)), 0) AS [Jan 2025],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' THEN h.ldr_amt_2 ELSE 0 END), 2) AS DECIMAL(18,2)), 0) AS [Feb 2025],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' THEN h.ldr_amt_3 ELSE 0 END), 2) AS DECIMAL(18,2)), 0) AS [Mar 2025],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' THEN h.ldr_amt_4 ELSE 0 END), 2) AS DECIMAL(18,2)), 0) AS [Apr 2025],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' THEN h.ldr_amt_5 ELSE 0 END), 2) AS DECIMAL(18,2)), 0) AS [May 2025],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' THEN h.ldr_amt_6 ELSE 0 END), 2) AS DECIMAL(18,2)), 0) AS [Jun 2025],
    ISNULL(CAST(ROUND(
        CASE
            WHEN (FullAccount IN ('1111-1102','1111-1105','5312-5303','5322-5303','6101-6001','6201-6001','8201-0000','8143-0000') OR FullAccount LIKE 'R1%' OR FullAccount LIKE 'S1%') THEN
                SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'Actual' THEN h.ldr_amt_5 ELSE 0 END)
                - SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'Budget' THEN h.ldr_amt_5 ELSE 0 END)
            ELSE
                SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'Budget' THEN h.ldr_amt_5 ELSE 0 END)
                - SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'Actual' THEN h.ldr_amt_5 ELSE 0 END)
        END
    , 2) AS DECIMAL(18,2)), 0) AS [Mo. Bdgt Var May 2025],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' THEN h.ldr_amt_5 ELSE 0 END), 2) AS DECIMAL(18,2)), 0) AS [Mo. Bdgt May 2025],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END), 2) AS DECIMAL(18,2)), 0) AS [YTD May 2025],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END), 2) AS DECIMAL(18,2)), 0) AS [YTD Bdgt May 2025],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END), 2) AS DECIMAL(18,2)), 0) AS [YTD May 2024]
FROM 
    #HierarchyData h
GROUP BY 
    h.Center, h.CAReportName, FullAccount

-- Total Procedures per center
UNION ALL
SELECT 
    h.Center,
    'Total Procedures',
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' THEN h.ldr_amt_11 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' THEN h.ldr_amt_12 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' THEN h.ldr_amt_1  ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' THEN h.ldr_amt_2 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' THEN h.ldr_amt_3 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' THEN h.ldr_amt_4 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' THEN h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' THEN h.ldr_amt_6 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' THEN h.ldr_amt_5 ELSE 0 END) - SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' THEN h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' THEN h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0)
FROM 
    #HierarchyData h
WHERE 
    h.FullAccount LIKE 'R1%'
GROUP BY 
    h.Center

-- Total Cases per center
UNION ALL
SELECT 
    h.Center,
    'Total Cases',
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' THEN h.ldr_amt_11 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' THEN h.ldr_amt_12 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' THEN h.ldr_amt_1  ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' THEN h.ldr_amt_2 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' THEN h.ldr_amt_3 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' THEN h.ldr_amt_4 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' THEN h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' THEN h.ldr_amt_6 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' THEN h.ldr_amt_5 ELSE 0 END) - SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' THEN h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' THEN h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0)
FROM 
    #HierarchyData h
WHERE 
    h.FullAccount LIKE 'S1%'
GROUP BY 
    h.Center

-- Compensation Total per center (FullAccount LIKE '71%')
UNION ALL
SELECT 
    h.Center,
    'Compensation Total',

    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_11 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_12 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1  ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_2 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_3 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_4 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_6 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),

    -- Mo. Bdgt Var May 2025
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END) -
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END)
    , 2) AS DECIMAL(18,2)), 0),

    -- Mo. Bdgt May 2025
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),

    -- YTD May 2025
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),

    -- YTD Bdgt May 2025
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),

    -- YTD May 2024
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0)

FROM #HierarchyData h
GROUP BY h.Center

-- Medical supplies & drugs Total  (FullAccount LIKE '72%')
UNION ALL
SELECT 
    h.Center,
    'Medical supplies & drugs Total',

    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_11 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_12 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1  ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_2 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_3 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_4 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_6 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),

    -- Mo. Bdgt Var May 2025
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END) -
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END)
    , 2) AS DECIMAL(18,2)), 0),

    -- Mo. Bdgt May 2025
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),

    -- YTD May 2025
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),

    -- YTD Bdgt May 2025
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),

    -- YTD May 2024
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0)

FROM #HierarchyData h
GROUP BY h.Center
-- Variable Expenses Total  (FullAccount LIKE '73%')
UNION ALL
SELECT 
    h.Center,
    'Variable Expenses Total',

    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_11 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_12 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_1 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_2 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_3 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_4 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_6 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),

    -- Mo. Bdgt Var May 2025
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_5 ELSE 0 END) -
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_5 ELSE 0 END)
    , 2) AS DECIMAL(18,2)), 0),

    -- Mo. Bdgt May 2025
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),

    -- YTD May 2025
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),

    -- YTD Bdgt May 2025
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),

    -- YTD May 2024
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0)

FROM #HierarchyData h
GROUP BY h.Center

-- Fixed Expenses Total per (FullAccount LIKE '74%')
UNION ALL
SELECT 
    h.Center,
    'Fixed Expenses Total',

    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_11 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_12 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_1 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_2 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_3 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_4 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_6 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),

    -- Mo. Bdgt Var May 2025
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_5 ELSE 0 END) -
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_5 ELSE 0 END)
    , 2) AS DECIMAL(18,2)), 0),

    -- Mo. Bdgt May 2025
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),

    -- YTD May 2025
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),

    -- YTD Bdgt May 2025
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0),

    -- YTD May 2024
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 End), 0) AS DECIMAL(18,2)), 0)

FROM #HierarchyData h
GROUP BY h.Center
-- Operating taxes and other Total per center (FullAccount LIKE '75%' but excluding 8221-0000 and 8143-0000)
UNION ALL
SELECT 
    h.Center,
    'Operating taxes and other Total',

    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_11 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_11 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_11 ELSE 0 END))* -1)
    , 2) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_12 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_12 ELSE 0 END)) -
        ((SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_12 ELSE 0 END))* -1)
    , 2) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_1 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_1 ELSE 0 END)) -
        ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_1 ELSE 0 END))* -1)
    , 2) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_2 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_2 ELSE 0 END)) -
        ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_2 ELSE 0 END)) * -1)
    , 2) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_3 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_3 ELSE 0 END)) -
        ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_3 ELSE 0 END))* -1)
    , 2) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_4 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_4 ELSE 0 END)) -
        ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_4 ELSE 0 END))* -1)
    , 2) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_5 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_5 ELSE 0 END)) -
        ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_5 ELSE 0 END))* -1)
    , 2) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_6 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_6 ELSE 0 END)) -
        ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_6 ELSE 0 END))* -1)
    , 2) AS DECIMAL(18,2)), 0),

    -- Mo. Bdgt Var May 2025
    ISNULL(CAST(ROUND((
        (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_5 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_5 ELSE 0 END)) -
        ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_5 ELSE 0 END))* -1)
        -
        (
            (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_5 ELSE 0 END) +
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_5 ELSE 0 END)) -
            ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_5 ELSE 0 END))* -1)
        )
    ), 2) AS DECIMAL(18,2)), 0),

    -- Mo. Bdgt May 2025
    ISNULL(CAST(ROUND(
       (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_5 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_5 ELSE 0 END)) -
        ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_5 ELSE 0 END))* -1)
    , 2) AS DECIMAL(18,2)), 0),

    -- YTD May 2025
    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)) -
        ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END))* -1)
    , 2) AS DECIMAL(18,2)), 0),

    -- YTD Bdgt May 2025
    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)) -
        ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END))* -1)
    , 2) AS DECIMAL(18,2)), 0),

    -- YTD May 2024
    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END))* -1)
    , 2) AS DECIMAL(18,2)), 0)

FROM #HierarchyData h
GROUP BY h.Center

-- Total Operating Expenses per center
--  = 71 %  + 72 %  + 73 %  + 74 %  + (75 % – 8221-0000 – ABS(8143-0000))
UNION ALL
SELECT
    h.Center,
    'Total Operating Expenses',
    -- Oct-24
    ISNULL(CAST(ROUND(
        ( SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_11 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_11 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_11 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_11 ELSE 0 END) +
          ((SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_11 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_11 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_11 ELSE 0 END))* -1)
          )
        )
    , 2) AS DECIMAL(18,2)), 0),
    -- Nov-24
    ISNULL(CAST(ROUND(
        ( SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_12 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_12 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_12 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_12 ELSE 0 END) +
          ((SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_12 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_12 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_12 ELSE 0 END))* -1)
          )
		  )
    , 2) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(
        ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_1 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_1 ELSE 0 END) +
          ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_1 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_1 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_1 ELSE 0 END))* -1)
          )
        )
    , 2) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(
        ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_2 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_2 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_2 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_2 ELSE 0 END) +
          ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_2 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_2 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_2 ELSE 0 END))* -1)
          )
        )
    , 2) AS DECIMAL(18,2)), 0),
    -- Feb-25
    ISNULL(CAST(ROUND(
        ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_3 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_3 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_3 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_3 ELSE 0 END) +
          ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_3 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_3 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_3 ELSE 0 END))* -1)
          )
        )
    , 2) AS DECIMAL(18,2)), 0),
    -- Mar-25
    ISNULL(CAST(ROUND(
        ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_4 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_4 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_4 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_4 ELSE 0 END) +
          ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_4 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_4 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_4 ELSE 0 END))* -1)
          )
        )
    , 2) AS DECIMAL(18,2)), 0),
    -- Apr-25
    ISNULL(CAST(ROUND(
        ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_5 ELSE 0 END) +
          ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_5 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_5 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_5 ELSE 0 END))* -1)
          )
        )
    , 2) AS DECIMAL(18,2)), 0),
    -- May-25
    ISNULL(CAST(ROUND(
        ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_6 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_6 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_6 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_6 ELSE 0 END) +
          ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_6 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_6 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_6 ELSE 0 END))* -1)
          )
        )
    , 2) AS DECIMAL(18,2)), 0),
    -- Mo. Bdgt Var Apr-25
    ISNULL(CAST(ROUND(
        ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_5 ELSE 0 END) +
          ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_5 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_5 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_5 ELSE 0 END))* -1)
          )
        ) -
        ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_5 ELSE 0 END) +
          ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_5 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_5 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_5 ELSE 0 END))* -1)
          )
        )
    , 2) AS DECIMAL(18,2)), 0),
    -- Mo. Bdgt Apr-25
    ISNULL(CAST(ROUND(
        ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_5 ELSE 0 END) +
          ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_5 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_5 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_5 ELSE 0 END))* -1)
          )
        )
    , 2) AS DECIMAL(18,2)), 0),
    -- YTD Apr-25 Actual
    ISNULL(CAST(ROUND(
        ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
          (  (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))* -1)
          )
        )
    , 2) AS DECIMAL(18,2)), 0),
    -- YTD Bdgt Apr-25
    ISNULL(CAST(ROUND(
        ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
          (  (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))* -1)
          )
        )
    , 2) AS DECIMAL(18,2)), 0),
    -- YTD Apr-24 Actual
    ISNULL(CAST(ROUND(
        ( SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
          (  (SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))* -1)
          )
        )
    , 2) AS DECIMAL(18,2)), 0)
FROM #HierarchyData h
GROUP BY h.Center

-- Operating Expenses per procedure  (Total Operating Expenses ÷ Total Procedures)
UNION ALL
SELECT
    h.Center,
    'Operating Expenses per procedure',

    /* ─────────── Monthly actuals ─────────── */
    /* Oct-24 */
    ISNULL(CAST(ROUND(
        (
          /* 71 % */ SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_11 ELSE 0 END) +
          /* 72 % */ SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_11 ELSE 0 END) +
          /* 73 % */ SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_11 ELSE 0 END) +
          /* 74 % */ SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_11 ELSE 0 END) +
          /* 75 % adj. */
          (  SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%'   THEN h.ldr_amt_11 ELSE 0 END)
           - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_11 ELSE 0 END)
           - ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_11 ELSE 0 END))
          )
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_11 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    /* Nov-24 */
    ISNULL(CAST(ROUND(
        (  SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_12 ELSE 0 END) +
           SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_12 ELSE 0 END) +
           SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_12 ELSE 0 END) +
           SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_12 ELSE 0 END) +
           (  SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%'   THEN h.ldr_amt_12 ELSE 0 END)
            - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_12 ELSE 0 END)
            - ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_12 ELSE 0 END))
           )
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_12 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    /* Dec-24 */
    ISNULL(CAST(ROUND(
        (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1  ELSE 0 END) +
           SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1  ELSE 0 END) +
           SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_1  ELSE 0 END) +
           SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_1  ELSE 0 END) +
           (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%'   THEN h.ldr_amt_1  ELSE 0 END)
            - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_1  ELSE 0 END)
            - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_1  ELSE 0 END))
           )
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1  ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    /* Jan-25 */
    ISNULL(CAST(ROUND(
        (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_2 ELSE 0 END) +
           SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_2 ELSE 0 END) +
           SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_2 ELSE 0 END) +
           SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_2 ELSE 0 END) +
           (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%'   THEN h.ldr_amt_2 ELSE 0 END)
            - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_2 ELSE 0 END)
            - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_2 ELSE 0 END))
           )
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_2 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    /* Feb-25 */
    ISNULL(CAST(ROUND(
        (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_3 ELSE 0 END) +
           SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_3 ELSE 0 END) +
           SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_3 ELSE 0 END) +
           SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_3 ELSE 0 END) +
           (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%'   THEN h.ldr_amt_3 ELSE 0 END)
            - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_3 ELSE 0 END)
            - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_3 ELSE 0 END))
           )
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_3 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    /* Mar-25 */
    ISNULL(CAST(ROUND(
        (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_4 ELSE 0 END) +
           SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_4 ELSE 0 END) +
           SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_4 ELSE 0 END) +
           SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_4 ELSE 0 END) +
           (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%'   THEN h.ldr_amt_4 ELSE 0 END)
            - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_4 ELSE 0 END)
            - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_4 ELSE 0 END))
           )
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_4 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    /* Apr-25 */
    ISNULL(CAST(ROUND(
        (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END) +
           SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END) +
           SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_5 ELSE 0 END) +
           SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_5 ELSE 0 END) +
           (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%'   THEN h.ldr_amt_5 ELSE 0 END)
            - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_5 ELSE 0 END)
            - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_5 ELSE 0 END))
           )
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    /* May-25 */
    ISNULL(CAST(ROUND(
        (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_6 ELSE 0 END) +
           SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_6 ELSE 0 END) +
           SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_6 ELSE 0 END) +
           SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_6 ELSE 0 END) +
           (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%'   THEN h.ldr_amt_6 ELSE 0 END)
            - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_6 ELSE 0 END)
            - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_6 ELSE 0 END))
           )
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_6 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    /* ─────────── Mo. budget variance & budget (Apr-25) ─────────── */
    /* Mo. Bdgt Var Apr-25 = (Actual OpEx/Proc) – (Budget OpEx/Proc) */
    ISNULL(CAST(ROUND(
        (
          /* actual numerator Apr-25 */
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END)+
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END)+
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_5 ELSE 0 END)+
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_5 ELSE 0 END)+
          (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%'   THEN h.ldr_amt_5 ELSE 0 END)
           - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8221-0000' THEN h.ldr_amt_5 ELSE 0 END)-
             ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8143-0000' THEN h.ldr_amt_5 ELSE 0 END))
          )
        -
          /* budget numerator Apr-25 */
          ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END)+
            SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END)+
            SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_5 ELSE 0 END)+
            SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_5 ELSE 0 END)+
            (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '75%'   THEN h.ldr_amt_5 ELSE 0 END)
             - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount='8221-0000' THEN h.ldr_amt_5 ELSE 0 END)-
               ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount='8143-0000' THEN h.ldr_amt_5 ELSE 0 END))
            )
          )
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    /* Mo. Bdgt Apr-25 (Budget OpEx ÷ Actual Procedures) */
    ISNULL(CAST(ROUND(
        (
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END)+
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END)+
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_5 ELSE 0 END)+
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_5 ELSE 0 END)+
          (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '75%'   THEN h.ldr_amt_5 ELSE 0 END)
           - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount='8221-0000' THEN h.ldr_amt_5 ELSE 0 END)-
             ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount='8143-0000' THEN h.ldr_amt_5 ELSE 0 END))
          )
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    /* ─────────── Year-to-date ratios ─────────── */
    /* YTD Apr-25 (Actual) */
    ISNULL(CAST(ROUND(
        (
          ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))-
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)-
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    /* YTD Bdgt Apr-25 */
    ISNULL(CAST(ROUND(
        (
          ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))-
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)-
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
		, 2) AS DECIMAL(18,2)), 0),

    /* YTD Apr-24 (Actual) */
    ISNULL(CAST(ROUND(
        (
          ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))-
          SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)-
          SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0)

FROM #HierarchyData h
GROUP BY h.Center

-- Compensation per procedure  (Compensation 71% ÷ Total Procedures R1%)
UNION ALL
SELECT
    h.Center,
    'Compensation per procedure',

    /* ───────── Monthly actual ratios ───────── */
    -- Oct-24
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_11 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_11 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    -- Nov-24
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_12 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_12 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    -- Dec-24
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1  ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1  ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    -- Jan-25
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_2 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_2 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    -- Feb-25
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_3 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_3 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    -- Mar-25
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_4 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_4 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    -- Apr-25
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    -- May-25
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_6 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_6 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    /* ───────── April-25 budget variance & budget ratios ───────── */
    -- Mo. Bdgt Var Apr-25  = (Actual comp – Budget comp) ÷ Actual procedures
    ISNULL(CAST(ROUND(
        (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END) -
           SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END)
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    -- Mo. Bdgt Apr-25  = Budget comp ÷ Actual procedures
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    /* ───────── Year-to-date ratios ───────── */
    -- YTD Apr-25 (Actual)
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    -- YTD Bdgt Apr-25
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    -- YTD Apr-24 (Actual)
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0)

FROM #HierarchyData h
GROUP BY h.Center
-- Medical supplies & drugs per procedure  (72 % ÷ R1 %)
UNION ALL
SELECT
    h.Center,
    'Medical supplies & drugs per procedure',

    /* ───────── Monthly actual ratios ───────── */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_11 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_11 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_12 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_12 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1  ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1  ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_2 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_2 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_3 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_3 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_4 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_4 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_6 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_6 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    /* ───────── April-25 budget variance & budget ratios ───────── */
    -- Mo. Bdgt Var Apr-25 = (Actual – Budget) ÷ Actual procedures
    ISNULL(CAST(ROUND(
        (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END) -
           SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END)
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    -- Mo. Bdgt Apr-25  = Budget supplies ÷ Actual procedures
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    /* ───────── Year-to-date ratios ───────── */
    -- YTD Apr-25 (Actual)
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    -- YTD Bdgt Apr-25
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0),

    -- YTD Apr-24 (Actual)
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0)

FROM #HierarchyData h
GROUP BY h.Center
-- Distributions per center (accounts 5312-5303 and 5322-5303)
UNION ALL
SELECT
    h.Center,
    'Distributions',

    /* ─────────────── Monthly actuals ─────────────── */
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_11 ELSE 0 End), 0) AS DECIMAL(18,2)), 0) AS [Nov 2024],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_12 ELSE 0 End), 0) AS DECIMAL(18,2)), 0) AS [Dec 2024],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_1  ELSE 0 End), 0) AS DECIMAL(18,2)), 0) AS [Jan 2025],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_2  ELSE 0 End), 0) AS DECIMAL(18,2)), 0) AS [Feb 2025],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_3  ELSE 0 End), 0) AS DECIMAL(18,2)), 0) AS [Mar 2025],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_4  ELSE 0 End), 0) AS DECIMAL(18,2)), 0) AS [Apr 2025],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_5  ELSE 0 End), 0) AS DECIMAL(18,2)), 0) AS [Apr 2025],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_6  ELSE 0 End), 0) AS DECIMAL(18,2)), 0) AS [Jun 2025],

    /* ─────────────── Mo. budget variance & budget (Apr-25) ─────────────── */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_5 ELSE 0 END) -
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_5 ELSE 0 END)
    , 2) AS DECIMAL(18,2)), 0)                                                     AS [Mo. Bdgt Var May 2025],

    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_5 ELSE 0 END)
    , 2) AS DECIMAL(18,2)), 0)                                                     AS [Mo. Bdgt May 2025],

    /* ─────────────── Year-to-date totals ─────────────── */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
    , 2) AS DECIMAL(18,2)), 0)                                                     AS [YTD May 2025],

    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
    , 2) AS DECIMAL(18,2)), 0)                                                     AS [YTD Bdgt May 2025],

    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
    , 2) AS DECIMAL(18,2)), 0)                                                     AS [YTD May 2024]

FROM #HierarchyData h
GROUP BY h.Center

-- Margin %  (EBITDA ÷ Net Revenue) expressed as percentage with 1-decimal
UNION ALL
SELECT
    h.Center,
    'Margin %',

    /* ───────── Monthly actual margins ───────── */
    /* Oct-24 */
    ISNULL(CAST(ROUND(
        CASE
            WHEN (   ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_11 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_11 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_11 ELSE 0 END)
                 ) = 0
            THEN 0
            ELSE (
                   /* EBITDA Oct-24 */
                   ( ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_11 ELSE 0 END))
                     - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_11 ELSE 0 END)
                     - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_11 ELSE 0 END)
                   )
                   -
                   ( SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_11 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_11 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_11 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_11 ELSE 0 END)
                     + (  SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_11 ELSE 0 END)
                        - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount='8221-0000' THEN h.ldr_amt_11 ELSE 0 END)
                        - ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount='8143-0000' THEN h.ldr_amt_11 ELSE 0 END))
                       )
                   )
                 ) 
                 /
                 ( ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_11 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_11 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_11 ELSE 0 END)
                 )
        END ,1) AS DECIMAL(18,2)), 0) AS [Nov 2024],

    /* Nov-24 */
    ISNULL(CAST(ROUND(
        CASE
            WHEN (   ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_12 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_12 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_12 ELSE 0 END)
                 ) = 0
            THEN 0
            ELSE (
                   ( ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_12 ELSE 0 END))
                     - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_12 ELSE 0 END)
                     - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_12 ELSE 0 END)
                   )
                   -
                   ( SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_12 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_12 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_12 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_12 ELSE 0 END)
                     + (  SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_12 ELSE 0 END)
                        - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount='8221-0000' THEN h.ldr_amt_12 ELSE 0 END)
                        - ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount='8143-0000' THEN h.ldr_amt_12 ELSE 0 END))
                       )
                   )
                 ) 
                 /
                 ( ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_12 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_12 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_12 ELSE 0 END)
                 )
        END ,1) AS DECIMAL(18,2)), 0) AS [Dec 2024],

    /* Dec-24 */
    ISNULL(CAST(ROUND(
        CASE
            WHEN (   ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1  ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1  ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1  ELSE 0 END)
                 ) = 0
            THEN 0
            ELSE (
                   ( ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1  ELSE 0 END))
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1  ELSE 0 END)
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1  ELSE 0 END)
                   )
                   -
                   ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1  ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1  ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_1  ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_1  ELSE 0 END)
                     + (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_1  ELSE 0 END)
                        - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8221-0000' THEN h.ldr_amt_1  ELSE 0 END)
                        - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8143-0000' THEN h.ldr_amt_1  ELSE 0 END))
                       )
                   )
                 ) 
                 /
                 ( ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1  ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1  ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1  ELSE 0 END)
                 )
        END ,1) AS DECIMAL(18,2)), 0) AS [Jan 2025],

    /* Jan-25 */
    ISNULL(CAST(ROUND(
        CASE
            WHEN (   ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_2 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_2 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_2 ELSE 0 END)
                 ) = 0
            THEN 0
            ELSE (
                   ( ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_2 ELSE 0 END))
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_2 ELSE 0 END)
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_2 ELSE 0 END)
                   )
                   -
                   ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_2 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_2 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_2 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_2 ELSE 0 END)
                     + (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_2 ELSE 0 END)
                        - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8221-0000' THEN h.ldr_amt_2 ELSE 0 END)
                        - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8143-0000' THEN h.ldr_amt_2 ELSE 0 END))
                       )
                   )
                 ) 
                 /
                 ( ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_2 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_2 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_2 ELSE 0 END)
                 )
        END ,1) AS DECIMAL(18,2)), 0) AS [Feb 2025],

    /* Feb-25 */
    ISNULL(CAST(ROUND(
        CASE
            WHEN (   ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_3 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_3 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_3 ELSE 0 END)
                 ) = 0
            THEN 0
            ELSE (
                   ( ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_3 ELSE 0 END))
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_3 ELSE 0 END)
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_3 ELSE 0 END)
                   )
                   -
                   ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_3 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_3 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_3 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_3 ELSE 0 END)
                     + (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_3 ELSE 0 END)
                        - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8221-0000' THEN h.ldr_amt_3 ELSE 0 END)
                        - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8143-0000' THEN h.ldr_amt_3 ELSE 0 END))
                       )
                   )
                 ) 
                 /
                 ( ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_3 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_3 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_3 ELSE 0 END)
                 )
        END ,1) AS DECIMAL(18,2)), 0) AS [Mar 2025],

    /* Mar-25 */
    ISNULL(CAST(ROUND(
        CASE
            WHEN (   ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_4 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_4 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_4 ELSE 0 END)
                 ) = 0
            THEN 0
            ELSE (
                   ( ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_4 ELSE 0 END))
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_4 ELSE 0 END)
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_4 ELSE 0 END)
                   )
                   -
                   ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_4 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_4 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_4 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_4 ELSE 0 END)
                     + (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_4 ELSE 0 END)
                        - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8221-0000' THEN h.ldr_amt_4 ELSE 0 END)
                        - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8143-0000' THEN h.ldr_amt_4 ELSE 0 END))
                       )
                   )
                 ) 
                 /
                 ( ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_4 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_4 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_4 ELSE 0 END)
                 )
        END ,1) AS DECIMAL(18,2)), 0) AS [Apr 2025],

    /* Apr-25 */
    ISNULL(CAST(ROUND(
        CASE
            WHEN (   ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
                 ) = 0
            THEN 0
            ELSE (
                   ( ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
                   )
                   -
                   ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_5 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_5 ELSE 0 END)
                     + (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_5 ELSE 0 END)
                        - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8221-0000' THEN h.ldr_amt_5 ELSE 0 END)
                        - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8143-0000' THEN h.ldr_amt_5 ELSE 0 END))
                       )
                   )
                 ) 
                 /
                 ( ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
                 )
        END ,1) AS DECIMAL(18,2)), 0) AS [Apr 2025],

    /* May-25 */
    ISNULL(CAST(ROUND(
        CASE
            WHEN (   ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_6 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_6 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_6 ELSE 0 END)
                 ) = 0
            THEN 0
            ELSE (
                   ( ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_6 ELSE 0 END))
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_6 ELSE 0 END)
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_6 ELSE 0 END)
                   )
                   -
                   ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_6 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_6 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_6 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_6 ELSE 0 END)
                     + (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_6 ELSE 0 END)
                        - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8221-0000' THEN h.ldr_amt_6 ELSE 0 END)
                        - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8143-0000' THEN h.ldr_amt_6 ELSE 0 END))
                       )
                   )
                 ) 
                 /
                 ( ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_6 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_6 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_6 ELSE 0 END)
                 )
        END ,1) AS DECIMAL(18,2)), 0) AS [Jun 2025],

    /* ───────── Mo. Bdgt Var (Apr-25) ───────── */
    ISNULL(CAST(ROUND(
        /* Actual Margin Apr-25 – Budget Margin Apr-25, already % forms */
        (
          /* Actual % Apr-25 */
          CASE
              WHEN (   ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
                   ) = 0
              THEN 0
              ELSE (
                     ( ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
                       - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
                       - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
                     )
                     -
                     ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END)
                       + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END)
                       + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_5 ELSE 0 END)
                       + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_5 ELSE 0 END)
                       + (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_5 ELSE 0 END)
                          - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8221-0000' THEN h.ldr_amt_5 ELSE 0 END)
                          - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8143-0000' THEN h.ldr_amt_5 ELSE 0 END))
                         )
                     )
                   ) 
                   /
                   ( ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
                   )
          END
        )
        -
        (
          /* Budget % Apr-25 */
          CASE
              WHEN (   ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
                   ) = 0
              THEN 0
              ELSE (
                     ( ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
                       - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
                       - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
                     )
                     -
                     ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END)
                       + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END)
                       + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_5 ELSE 0 END)
                       + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_5 ELSE 0 END)
                       + (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_5 ELSE 0 END)
                          - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount='8221-0000' THEN h.ldr_amt_5 ELSE 0 END)
                          - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount='8143-0000' THEN h.ldr_amt_5 ELSE 0 END))
                         )
                     )
                   ) 
                   /
                   ( ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
                   )
          END
        )
    ,1) AS DECIMAL(18,2)), 0) AS [Mo. Bdgt Var May 2025],

    /* Budget Margin Apr-25 */
    ISNULL(CAST(ROUND(
        CASE
            WHEN (   ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
                 ) = 0
            THEN 0
            ELSE (
                   ( ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
                   )
                   -
                   ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_5 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_5 ELSE 0 END)
                     + (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_5 ELSE 0 END)
                        - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount='8221-0000' THEN h.ldr_amt_5 ELSE 0 END)
                        - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount='8143-0000' THEN h.ldr_amt_5 ELSE 0 END))
                       )
                   )
                 ) 
                 /
                 ( ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
                 )
        END ,1) AS DECIMAL(18,2)), 0) AS [Mo. Bdgt May 2025],

    /* ───────── YTD Apr-25 Margin (Actual) ───────── */
    ISNULL(CAST(ROUND(
        CASE
            WHEN (   ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                 ) = 0
            THEN 0
            ELSE (
                   ( ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                   )
                   -
                   ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                     + (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                        - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8221-0000' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                        - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8143-0000' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))
                       )
                   )
                 ) 
                 /
                 ( ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                 )
        END ,1) AS DECIMAL(18,2)), 0) AS [YTD May 2025],

    /* YTD Bdgt Apr-25 Margin */
    ISNULL(CAST(ROUND(
        CASE
            WHEN (   ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                 ) = 0
            THEN 0
            ELSE (
                   ( ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                   )
                   -
                   ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                     + (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                        - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount='8221-0000' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                        - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount='8143-0000' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))
                       )
                   )
                 ) 
                 /
                 ( ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                 )
        END ,1) AS DECIMAL(18,2)), 0) AS [YTD Bdgt May 2025],

    /* YTD Apr-24 Margin (Actual) */
    ISNULL(CAST(ROUND(
        CASE
            WHEN (   ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                 ) = 0
            THEN 0
            ELSE (
                   ( ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))
                     - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                     - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                   )
                   -
                   ( SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                     + SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                     + (  SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                        - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount='8221-0000' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                        - ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount='8143-0000' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))
                       )
                   )
                 ) 
                 /
                 ( ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                 )
        END ,1) AS DECIMAL(18,2)), 0) AS [YTD May 2024]

FROM #HierarchyData h
GROUP BY h.Center



-- Contractual Adjustments per Procedure  (62% ÷ Total Procedures)
UNION ALL
SELECT
    h.Center,
    'Contractual Adjustments per Procedure',

    /* ───────── Monthly actual ratios ───────── */
    /* Oct-24 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_11 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_11 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Nov 2024],

    /* Nov-24 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_12 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_12 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Dec 2024],

    /* Dec-24 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1  ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1  ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Jan 2025],

    /* Jan-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_2 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_2 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Feb 2025],

    /* Feb-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_3 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_3 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Mar 2025],

    /* Mar-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_4 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_4 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Apr 2025],

    /* Apr-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Apr 2025],

    /* May-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_6 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_6 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Jun 2025],

    /* ───────── April-25 budget variance & budget ───────── */
    /* Mo. Bdgt Var = (Actual Apr-25 / Proc) − (Budget Apr-25 / Proc-actual) */
    ISNULL(CAST(ROUND(
        (
            SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
          - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
        )
        / NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Mo. Bdgt Var May 2025],

    /* Mo. Bdgt Apr-25 = budget numerator ÷ actual procedure count */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Mo. Bdgt May 2025],

    /* ───────── YTD totals ───────── */
    /* YTD Apr-25 (Actual) */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD May 2025],

    /* YTD Bdgt Apr-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD Bdgt May 2025],

    /* YTD Apr-24 (Actual) */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD May 2024]

FROM #HierarchyData h
GROUP BY h.Center
-- Linens per Procedure  (7301-0000 ÷ Total Procedures)
UNION ALL
SELECT
    h.Center,
    'Linens per Procedure',

    /* ───────── Monthly actual ratios ───────── */
    /* Oct-24 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount='7301-0000' THEN h.ldr_amt_11 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_11 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Nov 2024],

    /* Nov-24 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount='7301-0000' THEN h.ldr_amt_12 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_12 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Dec 2024],

    /* Dec-24 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='7301-0000' THEN h.ldr_amt_1  ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1  ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Jan 2025],

    /* Jan-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='7301-0000' THEN h.ldr_amt_2 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_2 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Feb 2025],

    /* Feb-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='7301-0000' THEN h.ldr_amt_3 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_3 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Mar 2025],

    /* Mar-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='7301-0000' THEN h.ldr_amt_4 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_4 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Apr 2025],

    /* Apr-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='7301-0000' THEN h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Apr 2025],

    /* May-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='7301-0000' THEN h.ldr_amt_6 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_6 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Jun 2025],

    /* ───────── April-25 budget variance & budget ───────── */
    /* Mo. Bdgt Var Apr-25 */
    ISNULL(CAST(ROUND(
        (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='7301-0000' THEN h.ldr_amt_5 ELSE 0 END)
         - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount='7301-0000' THEN h.ldr_amt_5 ELSE 0 END)
        )
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Mo. Bdgt Var May 2025],

    /* Mo. Bdgt Apr-25 (budget numerator ÷ actual procedures) */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount='7301-0000' THEN h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Mo. Bdgt May 2025],

    /* ───────── YTD ratios ───────── */
    /* YTD Apr-25 (Actual) */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='7301-0000' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD May 2025],

    /* YTD Bdgt Apr-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount='7301-0000' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD Bdgt May 2025],

    /* YTD Apr-24 (Actual) */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount='7301-0000' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD May 2024]

FROM #HierarchyData h
GROUP BY h.Center
-- Medical Supplies per Procedure  (7201-0000 + 7203-0000) ÷ Total Procedures
UNION ALL
SELECT
    h.Center,
    'Medical Supplies per Procedure',

    /* ───────── Monthly actual ratios ───────── */
    /* Oct-24 */
    ISNULL(CAST(ROUND(
        (   SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual'
                     AND h.FullAccount IN ('7201-0000','7203-0000') THEN h.ldr_amt_11 ELSE 0 END)
        )
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_11 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Nov 2024],

    /* Nov-24 */
    ISNULL(CAST(ROUND(
        (   SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual'
                     AND h.FullAccount IN ('7201-0000','7203-0000') THEN h.ldr_amt_12 ELSE 0 END)
        )
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_12 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Dec 2024],

    /* Dec-24 */
    ISNULL(CAST(ROUND(
        (   SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                     AND h.FullAccount IN ('7201-0000','7203-0000') THEN h.ldr_amt_1  ELSE 0 END)
        )
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1  ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Jan 2025],

    /* Jan-25 */
    ISNULL(CAST(ROUND(
        (   SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                     AND h.FullAccount IN ('7201-0000','7203-0000') THEN h.ldr_amt_2 ELSE 0 END)
        )
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_2 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Feb 2025],

    /* Feb-25 */
    ISNULL(CAST(ROUND(
        (   SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                     AND h.FullAccount IN ('7201-0000','7203-0000') THEN h.ldr_amt_3 ELSE 0 END)
        )
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_3 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Mar 2025],

    /* Mar-25 */
    ISNULL(CAST(ROUND(
        (   SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                     AND h.FullAccount IN ('7201-0000','7203-0000') THEN h.ldr_amt_4 ELSE 0 END)
        )
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_4 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Apr 2025],

    /* Apr-25 */
    ISNULL(CAST(ROUND(
        (   SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                     AND h.FullAccount IN ('7201-0000','7203-0000') THEN h.ldr_amt_5 ELSE 0 END)
        )
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Apr 2025],

    /* May-25 */
    ISNULL(CAST(ROUND(
        (   SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                     AND h.FullAccount IN ('7201-0000','7203-0000') THEN h.ldr_amt_6 ELSE 0 END)
        )
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_6 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Jun 2025],

    /* ───────── April-25 budget variance & budget ───────── */
    /* Mo. Bdgt Var May 2025 */
    ISNULL(CAST(ROUND(
        (   SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                     AND h.FullAccount IN ('7201-0000','7203-0000') THEN h.ldr_amt_5 ELSE 0 END)
          - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget'
                     AND h.FullAccount IN ('7201-0000','7203-0000') THEN h.ldr_amt_5 ELSE 0 END)
        )
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Mo. Bdgt Var May 2025],

    /* Mo. Bdgt May 2025 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget'
                 AND h.FullAccount IN ('7201-0000','7203-0000') THEN h.ldr_amt_5 ELSE 0 END)
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Mo. Bdgt May 2025],

    /* ───────── YTD ratios ───────── */
    /* YTD May 2025 (Actual) */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                 AND h.FullAccount IN ('7201-0000','7203-0000')
                 THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%'
                        THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD May 2025],

    /* YTD Bdgt May 2025 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget'
                 AND h.FullAccount IN ('7201-0000','7203-0000')
                 THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%'
                        THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD Bdgt May 2025],

    /* YTD May 2024 (Actual) */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual'
                 AND h.FullAccount IN ('7201-0000','7203-0000')
                 THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%'
                        THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD May 2024]

FROM #HierarchyData h
GROUP BY h.Center
-- Drugs per Procedure  (7205-0000 + 7207-0000) ÷ Total Procedures
UNION ALL
SELECT
    h.Center,
    'Drug supplies per Procedure',

    /* ───────── Monthly actual ratios ───────── */
    /* Oct-24 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual'
                 AND h.FullAccount IN ('7205-0000','7207-0000') THEN h.ldr_amt_11 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_11 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Nov 2024],

    /* Nov-24 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual'
                 AND h.FullAccount IN ('7205-0000','7207-0000') THEN h.ldr_amt_12 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_12 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Dec 2024],

    /* Dec-24 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                 AND h.FullAccount IN ('7205-0000','7207-0000') THEN h.ldr_amt_1  ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1  ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Jan 2025],

    /* Jan-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                 AND h.FullAccount IN ('7205-0000','7207-0000') THEN h.ldr_amt_2 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_2 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Feb 2025],

    /* Feb-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                 AND h.FullAccount IN ('7205-0000','7207-0000') THEN h.ldr_amt_3 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_3 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Mar 2025],

    /* Mar-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                 AND h.FullAccount IN ('7205-0000','7207-0000') THEN h.ldr_amt_4 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_4 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Apr 2025],

    /* Apr-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                 AND h.FullAccount IN ('7205-0000','7207-0000') THEN h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Apr 2025],

    /* May-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                 AND h.FullAccount IN ('7205-0000','7207-0000') THEN h.ldr_amt_6 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_6 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Jun 2025],

    /* ───────── April-25 budget variance & budget ───────── */
    /* Mo. Bdgt Var May 2025 */
    ISNULL(CAST(ROUND(
        (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                    AND h.FullAccount IN ('7205-0000','7207-0000') THEN h.ldr_amt_5 ELSE 0 END)
         - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget'
                    AND h.FullAccount IN ('7205-0000','7207-0000') THEN h.ldr_amt_5 ELSE 0 END)
        )
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Mo. Bdgt Var May 2025],

    /* Mo. Bdgt May 2025 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget'
                 AND h.FullAccount IN ('7205-0000','7207-0000') THEN h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Mo. Bdgt May 2025],

    /* ───────── YTD ratios ───────── */
    /* YTD May 2025 (Actual) */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                 AND h.FullAccount IN ('7205-0000','7207-0000')
                 THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%'
                        THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD May 2025],

    /* YTD Bdgt May 2025 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget'
                 AND h.FullAccount IN ('7205-0000','7207-0000')
                 THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%'
                        THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD Bdgt May 2025],

    /* YTD May 2024 (Actual) */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual'
                 AND h.FullAccount IN ('7205-0000','7207-0000')
                 THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%'
                        THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD May 2024]

FROM #HierarchyData h
GROUP BY h.Center

-- Bad Debt % of Net Revenue  (6301-6001 ÷ Net Revenue)
-- Bad Debt % of Net Revenue  (6301-6001 ÷ Net Revenue)  -- now returned as a fraction
UNION ALL
SELECT
    h.Center,
    'Bad Debt % of Net Revenue',

    /* ───────── Monthly actual ratios ───────── */
    /* Oct-24 */
    ISNULL(CAST(ROUND(
        CASE
            WHEN (
                     ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_11 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_11 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_11 ELSE 0 END)
                 ) = 0
            THEN 0
            ELSE
                 SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount='6301-6001' THEN h.ldr_amt_11 ELSE 0 END)
                 /
                 (  ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_11 ELSE 0 END))
                  - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_11 ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_11 ELSE 0 END)
                 )
        END,3) AS DECIMAL(18,2)), 0) AS [Nov 2024],

    /* Nov-24 */
    ISNULL(CAST(ROUND(
        CASE
            WHEN (
                     ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_12 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_12 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_12 ELSE 0 END)
                 ) = 0
            THEN 0
            ELSE
                 SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount='6301-6001' THEN h.ldr_amt_12 ELSE 0 END)
                 /
                 (  ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_12 ELSE 0 END))
                  - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_12 ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_12 ELSE 0 END)
                 )
        END,3) AS DECIMAL(18,2)), 0) AS [Dec 2024],

    /* Dec-24 */
    ISNULL(CAST(ROUND(
        CASE
            WHEN (
                     ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1  ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1  ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1  ELSE 0 END)
                 ) = 0
            THEN 0
            ELSE
                 SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='6301-6001' THEN h.ldr_amt_1  ELSE 0 END)
                 /
                 (  ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1  ELSE 0 END))
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1  ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1  ELSE 0 END)
                 )
        END,3) AS DECIMAL(18,2)), 0) AS [Jan 2025],

    /* Jan-25 */
    ISNULL(CAST(ROUND(
        CASE
            WHEN (
                     ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_2 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_2 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_2 ELSE 0 END)
                 ) = 0
            THEN 0
            ELSE
                 SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='6301-6001' THEN h.ldr_amt_2 ELSE 0 END)
                 /
                 (  ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_2 ELSE 0 END))
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_2 ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_2 ELSE 0 END)
                 )
        END,3) AS DECIMAL(18,2)), 0) AS [Feb 2025],

    /* Feb-25 */
    ISNULL(CAST(ROUND(
        CASE
            WHEN (
                     ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_3 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_3 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_3 ELSE 0 END)
                 ) = 0
            THEN 0
            ELSE
                 SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='6301-6001' THEN h.ldr_amt_3 ELSE 0 END)
                 /
                 (  ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_3 ELSE 0 END))
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_3 ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_3 ELSE 0 END)
                 )
        END,3) AS DECIMAL(18,2)), 0) AS [Mar 2025],

    /* Mar-25 */
    ISNULL(CAST(ROUND(
        CASE
            WHEN (
                     ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_4 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_4 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_4 ELSE 0 END)
                 ) = 0
            THEN 0
            ELSE
                 SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='6301-6001' THEN h.ldr_amt_4 ELSE 0 END)
                 /
                 (  ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_4 ELSE 0 END))
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_4 ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_4 ELSE 0 END)
                 )
        END,3) AS DECIMAL(18,2)), 0) AS [Apr 2025],

    /* Apr-25 */
    ISNULL(CAST(ROUND(
        CASE
            WHEN (
                     ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
                 ) = 0
            THEN 0
            ELSE
                 SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='6301-6001' THEN h.ldr_amt_5 ELSE 0 END)
                 /
                 (  ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
                 )
        END,3) AS DECIMAL(18,2)), 0) AS [Apr 2025],

    /* May-25 */
    ISNULL(CAST(ROUND(
        CASE
            WHEN (
                     ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_6 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_6 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_6 ELSE 0 END)
                 ) = 0
            THEN 0
            ELSE
                 SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='6301-6001' THEN h.ldr_amt_6 ELSE 0 END)
                 /
                 (  ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_6 ELSE 0 END))
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_6 ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_6 ELSE 0 END)
                 )
        END,3) AS DECIMAL(18,2)), 0) AS [Jun 2025],

    /* ───────── Mo. Bdgt Var & Budget Apr-25 ───────── */
    ISNULL(CAST(ROUND(
        (
          /* Actual ratio Apr-25 */
          CASE
              WHEN (
                     ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
                   ) = 0
              THEN 0
              ELSE
                   SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='6301-6001' THEN h.ldr_amt_5 ELSE 0 END)
                   /
                   (  ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
                    - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
                    - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
                   )
          END
          -
          /* Budget ratio Apr-25 */
          CASE
              WHEN (
                     ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
                   ) = 0
              THEN 0
              ELSE
                   SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount='6301-6001' THEN h.ldr_amt_5 ELSE 0 END)
                   /
                   (  ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
                    - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
                    - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
                   )
          END
        ),3) AS DECIMAL(18,2)), 0) AS [Mo. Bdgt Var May 2025],

    /* Mo. Bdgt Apr-25 */
    ISNULL(CAST(ROUND(
        CASE
            WHEN (
                     ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
                 ) = 0
            THEN 0
            ELSE
                 SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount='6301-6001' THEN h.ldr_amt_5 ELSE 0 END)
                 /
                 (  ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
                 )
        END,3) AS DECIMAL(18,2)), 0) AS [Mo. Bdgt May 2025],

    /* ───────── YTD ratios ───────── */
    /* YTD Apr-25 (Actual) */
    ISNULL(CAST(ROUND(
        CASE
            WHEN (
                     ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%'
                                  THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%'
                                  THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%'
                                  THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                 ) = 0
            THEN 0
            ELSE
                 SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='6301-6001'
                          THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                 /
                 (  ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%'
                                  THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%'
                                  THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%'
                                  THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                 )
        END,3) AS DECIMAL(18,2)), 0) AS [YTD May 2025],

    /* YTD Bdgt Apr-25 */
    ISNULL(CAST(ROUND(
        CASE
            WHEN (
                     ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '61%'
                                  THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '62%'
                                  THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '63%'
                                  THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                 ) = 0
            THEN 0
            ELSE
                 SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount='6301-6001'
                          THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                 /
                 (  ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '61%'
                                  THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '62%'
                                  THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '63%'
                                  THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                 )
        END,3) AS DECIMAL(18,2)), 0) AS [YTD Bdgt May 2025],

    /* YTD Apr-24 (Actual) */
    ISNULL(CAST(ROUND(
        CASE
            WHEN (
                     ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%'
                                  THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))
                   - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%'
                                  THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                   - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%'
                                  THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                 ) = 0
            THEN 0
            ELSE
                 SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount='6301-6001'
                          THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                 /
                 (  ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%'
                                  THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))
                  - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%'
                                  THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%'
                                  THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)
                 )
        END,3) AS DECIMAL(18,2)), 0) AS [YTD May 2024]

FROM #HierarchyData h
GROUP BY h.Center

-- Compensation per Day  (Total Compensation 71% ÷ S005-0000)
UNION ALL
SELECT
    h.Center,
    'Compensation per Day',

    /* ───────── Monthly actual values ───────── */
    /* Oct 2024 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_11 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount='S005-0000' THEN h.ldr_amt_11 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Nov 2024],

    /* Nov 2024 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_12 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount='S005-0000' THEN h.ldr_amt_12 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Dec 2024],

    /* Dec 2024 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1  ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='S005-0000' THEN h.ldr_amt_1  ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Jan 2025],

    /* Jan 2025 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_2 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='S005-0000' THEN h.ldr_amt_2 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Feb 2025],

    /* Feb 2025 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_3 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='S005-0000' THEN h.ldr_amt_3 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Mar 2025],

    /* Mar 2025 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_4 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='S005-0000' THEN h.ldr_amt_4 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Apr 2025],

    /* Apr 2025 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='S005-0000' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Apr 2025],

    /* May 2025 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_6 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='S005-0000' THEN h.ldr_amt_6 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Jun 2025],

    /* ───────── April-25 budget variance & budget ───────── */
    /* Mo. Bdgt Var May 2025 */
    ISNULL(CAST(ROUND(
        (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END)
         - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END)
        )
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='S005-0000' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Mo. Bdgt Var May 2025],

    /* Mo. Bdgt May 2025 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='S005-0000' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Mo. Bdgt May 2025],

    /* ───────── YTD ratios ───────── */
    /* YTD May 2025 (Actual) */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%'
                 THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='S005-0000'
                        THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD May 2025],

    /* YTD Bdgt May 2025 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '71%'
                 THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='S005-0000'
                        THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD Bdgt May 2025],

    /* YTD May 2024 (Actual) */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%'
                 THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount='S005-0000'
                        THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD May 2024]

FROM #HierarchyData h
GROUP BY h.Center
-- Procedures per Day  (Total Procedures R1% ÷ S005-0000)
UNION ALL
SELECT
    h.Center,
    'Procedures per Day',

    /* ───────── Monthly actual values ───────── */
    /* Oct-24 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual'
                 AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_11 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual'
                        AND h.FullAccount='S005-0000' THEN h.ldr_amt_11 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Nov 2024],

    /* Nov-24 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual'
                 AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_12 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual'
                        AND h.FullAccount='S005-0000' THEN h.ldr_amt_12 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Dec 2024],

    /* Dec-24 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                 AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1  ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount='S005-0000' THEN h.ldr_amt_1  ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Jan 2025],

    /* Jan-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                 AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_2 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount='S005-0000' THEN h.ldr_amt_2 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Feb 2025],

    /* Feb-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                 AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_3 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount='S005-0000' THEN h.ldr_amt_3 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Mar 2025],

    /* Mar-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                 AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_4 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount='S005-0000' THEN h.ldr_amt_4 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Apr 2025],

    /* Apr-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                 AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount='S005-0000' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Apr 2025],

    /* May-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                 AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_6 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount='S005-0000' THEN h.ldr_amt_6 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Jun 2025],

    /* ───────── April-25 budget variance & budget ───────── */
    /* Mo. Bdgt Var Apr-25 */
    ISNULL(CAST(ROUND(
        (  SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                    AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 END)
         - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget'
                    AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 END)
        )
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount='S005-0000' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Mo. Bdgt Var May 2025],

    /* Mo. Bdgt Apr-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget'
                 AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount='S005-0000' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Mo. Bdgt May 2025],

    /* ───────── YTD ratios ───────── */
    /* YTD Apr-25 (Actual) */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                 AND h.FullAccount LIKE 'R1%'
                 THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount='S005-0000'
                        THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD May 2025],

    /* YTD Bdgt Apr-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget'
                 AND h.FullAccount LIKE 'R1%'
                 THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount='S005-0000'
                        THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD Bdgt May 2025],

    /* YTD Apr-24 (Actual) */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual'
                 AND h.FullAccount LIKE 'R1%'
                 THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual'
                        AND h.FullAccount='S005-0000'
                        THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD May 2024]

FROM #HierarchyData h
GROUP BY h.Center
-- Gross revenue per Procedure  (ABS(61%) ÷ Total Procedures)
UNION ALL
SELECT
    h.Center,
    'Gross revenue per Procedure',

    /* ───────── Monthly actual values ───────── */
    /* Oct-24 */
    ISNULL(CAST(ROUND(
        ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual'
                     AND h.FullAccount LIKE '61%' THEN h.ldr_amt_11 ELSE 0 END))
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_11 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Nov 2024],

    /* Nov-24 */
    ISNULL(CAST(ROUND(
        ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual'
                     AND h.FullAccount LIKE '61%' THEN h.ldr_amt_12 ELSE 0 END))
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_12 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Dec 2024],

    /* Dec-24 */
    ISNULL(CAST(ROUND(
        ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                     AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1  ELSE 0 END))
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1  ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Jan 2025],

    /* Jan-25 */
    ISNULL(CAST(ROUND(
        ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                     AND h.FullAccount LIKE '61%' THEN h.ldr_amt_2 ELSE 0 END))
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_2 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Feb 2025],

    /* Feb-25 */
    ISNULL(CAST(ROUND(
        ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                     AND h.FullAccount LIKE '61%' THEN h.ldr_amt_3 ELSE 0 END))
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_3 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Mar 2025],

    /* Mar-25 */
    ISNULL(CAST(ROUND(
        ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                     AND h.FullAccount LIKE '61%' THEN h.ldr_amt_4 ELSE 0 END))
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_4 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Apr 2025],

    /* Apr-25 */
    ISNULL(CAST(ROUND(
        ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                     AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Apr 2025],

    /* May-25 */
    ISNULL(CAST(ROUND(
        ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                     AND h.FullAccount LIKE '61%' THEN h.ldr_amt_6 ELSE 0 END))
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_6 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Jun 2025],

    /* ───────── April-25 budget variance & budget ───────── */
    /* Mo. Bdgt Var May 2025 */
    ISNULL(CAST(ROUND(
        (  ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
         - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget'
                        AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
        )
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Mo. Bdgt Var May 2025],

    /* Mo. Bdgt May 2025 */
    ISNULL(CAST(ROUND(
        ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget'
                     AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 End), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Mo. Bdgt May 2025],

    /* ───────── YTD ratios ───────── */
    /* YTD May 2025 (Actual) */
    ISNULL(CAST(ROUND(
        ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                     AND h.FullAccount LIKE '61%'
                     THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%'
                        THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD May 2025],

    /* YTD Bdgt May 2025 */
    ISNULL(CAST(ROUND(
        ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget'
                     AND h.FullAccount LIKE '61%'
                     THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))
        /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual'
                        AND h.FullAccount LIKE 'R1%'
                        THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD Bdgt May 2025],

    /* YTD May 2024 (Actual) */

	ISNULL(CAST(ROUND(
		ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual'
                 AND h.FullAccount LIKE '61%'
                 THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END))
		/
		NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual'
                    AND h.FullAccount LIKE 'R1%'
                    THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END), 0)
	   , 2) AS DECIMAL(18,2)), 0) AS [YTD May 2024]

FROM #HierarchyData h
GROUP BY h.Center
-- Net Cash Collection per procedure (Cash collections 11% ÷ Total Procedures R1%)
UNION ALL
SELECT
    h.Center,
    'Net Cash Collection per procedure',
    /* Oct-24 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '11%' THEN h.ldr_amt_11 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_11 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0),
    /* Nov-24 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '11%' THEN h.ldr_amt_12 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_12 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0),
    /* Dec-24 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '11%' THEN h.ldr_amt_1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0),
    /* Jan-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '11%' THEN h.ldr_amt_2 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_2 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0),
    /* Feb-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '11%' THEN h.ldr_amt_3 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_3 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0),
    /* Mar-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '11%' THEN h.ldr_amt_4 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_4 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0),
    /* Apr-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '11%' THEN h.ldr_amt_5 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0),
    /* May-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '11%' THEN h.ldr_amt_6 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_6 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0),
    /* Mo. Bdgt Var Apr-25 */
    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '11%' THEN h.ldr_amt_5 ELSE 0 END)
         - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '11%' THEN h.ldr_amt_5 ELSE 0 END))
        / NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0),
    /* Mo. Bdgt Apr-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '11%' THEN h.ldr_amt_5 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0),
    /* YTD Apr-25 (Actual) */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '11%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0),
    /* YTD Bdgt Apr-25 */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '11%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0),
    /* YTD Apr-24 (Actual) */
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '11%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0)
FROM #HierarchyData h
GROUP BY h.Center

-- Center EBITDA per Procedure (EBITDA ÷ Total Procedures)
UNION ALL
SELECT
    h.Center,
    'Center EBITDA per Procedure',
    /* Oct-24 */
    ISNULL(CAST(ROUND(
        (
            (ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_11 ELSE 0 END))
             - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_11 ELSE 0 END)
             - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_11 ELSE 0 END))
            - (SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_11 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_11 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_11 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_11 ELSE 0 END)
               + (SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_11 ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount='8221-0000' THEN h.ldr_amt_11 ELSE 0 END)
                  - ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount='8143-0000' THEN h.ldr_amt_11 ELSE 0 END))))
        )
        / NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_11 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Nov 2024],
    /* Nov-24 */
    ISNULL(CAST(ROUND(
        (
            (ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_12 ELSE 0 END))
             - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_12 ELSE 0 END)
             - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_12 ELSE 0 END))
            - (SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_12 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_12 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_12 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_12 ELSE 0 END)
               + (SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_12 ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount='8221-0000' THEN h.ldr_amt_12 ELSE 0 END)
                  - ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount='8143-0000' THEN h.ldr_amt_12 ELSE 0 END))))
        )
        / NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_12 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Dec 2024],
    /* Dec-24 */
    ISNULL(CAST(ROUND(
        (
            (ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1 ELSE 0 END))
             - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1 ELSE 0 END)
             - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1 ELSE 0 END))
            - (SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_1 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_1 ELSE 0 END)
               + (SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_1 ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8221-0000' THEN h.ldr_amt_1 ELSE 0 END)
                  - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8143-0000' THEN h.ldr_amt_1 ELSE 0 END))))
        )
        / NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Jan 2025],
    /* Jan-25 */
    ISNULL(CAST(ROUND(
        (
            (ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_2 ELSE 0 END))
             - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_2 ELSE 0 END)
             - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_2 ELSE 0 END))
            - (SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_2 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_2 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_2 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_2 ELSE 0 END)
               + (SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_2 ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8221-0000' THEN h.ldr_amt_2 ELSE 0 END)
                  - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8143-0000' THEN h.ldr_amt_2 ELSE 0 END))))
        )
        / NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_2 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Feb 2025],
    /* Feb-25 */
    ISNULL(CAST(ROUND(
        (
            (ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_3 ELSE 0 END))
             - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_3 ELSE 0 END)
             - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_3 ELSE 0 END))
            - (SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_3 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_3 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_3 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_3 ELSE 0 END)
               + (SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_3 ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8221-0000' THEN h.ldr_amt_3 ELSE 0 END)
                  - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8143-0000' THEN h.ldr_amt_3 ELSE 0 END))))
        )
        / NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_3 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Mar 2025],
    /* Mar-25 */
    ISNULL(CAST(ROUND(
        (
            (ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_4 ELSE 0 END))
             - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_4 ELSE 0 END)
             - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_4 ELSE 0 END))
            - (SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_4 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_4 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_4 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_4 ELSE 0 END)
               + (SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_4 ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8221-0000' THEN h.ldr_amt_4 ELSE 0 END)
                  - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8143-0000' THEN h.ldr_amt_4 ELSE 0 END))))
        )
        / NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_4 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Apr 2025],
    /* Apr-25 */
    ISNULL(CAST(ROUND(
        (
            (ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
             - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
             - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END))
            - (SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_5 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_5 ELSE 0 END)
               + (SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_5 ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8221-0000' THEN h.ldr_amt_5 ELSE 0 END)
                  - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8143-0000' THEN h.ldr_amt_5 ELSE 0 END))))
        )
        / NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Apr 2025],
    /* May-25 */
    ISNULL(CAST(ROUND(
        (
            (ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_6 ELSE 0 END))
             - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_6 ELSE 0 END)
             - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_6 ELSE 0 END))
            - (SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_6 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_6 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_6 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_6 ELSE 0 END)
               + (SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_6 ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8221-0000' THEN h.ldr_amt_6 ELSE 0 END)
                  - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8143-0000' THEN h.ldr_amt_6 ELSE 0 END))))
        )
        / NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_6 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Jun 2025],
    /* Mo. Bdgt Var Apr-25 */
    ISNULL(CAST(ROUND(
        (
            (ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
             - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
             - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END))
            - (SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_5 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_5 ELSE 0 END)
               + (SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_5 ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8221-0000' THEN h.ldr_amt_5 ELSE 0 END)
                  - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8143-0000' THEN h.ldr_amt_5 ELSE 0 END))))
            - ((ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
                - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
                - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END))
               - (SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END)
                  + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END)
                  + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_5 ELSE 0 END)
                  + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_5 ELSE 0 END)
                  + (SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_5 ELSE 0 END)
                     - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount='8221-0000' THEN h.ldr_amt_5 ELSE 0 END)
                     - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount='8143-0000' THEN h.ldr_amt_5 ELSE 0 END)))))
        )
        / NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Mo. Bdgt Var May 2025],
    /* Mo. Bdgt Apr-25 */
    ISNULL(CAST(ROUND(
        (
            (ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END))
             - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END)
             - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END))
            - (SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_5 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_5 ELSE 0 END)
               + (SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_5 ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount='8221-0000' THEN h.ldr_amt_5 ELSE 0 END)
                  - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount='8143-0000' THEN h.ldr_amt_5 ELSE 0 END))))
        )
        / NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [Mo. Bdgt May 2025],
    /* YTD Apr-25 (Actual) */
    ISNULL(CAST(ROUND(
        (
            (ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END))
             - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
             - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END))
            - (SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
               + (SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8221-0000' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
                  - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount='8143-0000' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END))))
        )
        / NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD May 2025],
    /* YTD Bdgt Apr-25 */
    ISNULL(CAST(ROUND(
        (
            (ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END))
             - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
             - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END))
            - (SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
               + (SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount='8221-0000' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
                  - ABS(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount='8143-0000' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END))))
        )
        / NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD Bdgt May 2025],
    /* YTD Apr-24 Actual */
    ISNULL(CAST(ROUND(
        (
            (ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END))
             - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
             - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END))
            - (SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
               + SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
               + (SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
                  - SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount='8221-0000' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
                  - ABS(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount='8143-0000' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END))))
        )
        / NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD May 2024]
FROM #HierarchyData h
GROUP BY h.Center

-- Distributions per center (accounts 5312-5303 and 5322-5303)
UNION ALL
SELECT
    h.Center,
    'Distributions',
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_11 ELSE 0 END), 0) AS DECIMAL(18,2)), 0) AS [Nov 2024],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_12 ELSE 0 END), 0) AS DECIMAL(18,2)), 0) AS [Dec 2024],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_1 ELSE 0 END), 0) AS DECIMAL(18,2)), 0) AS [Jan 2025],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_2 ELSE 0 END), 0) AS DECIMAL(18,2)), 0) AS [Feb 2025],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_3 ELSE 0 END), 0) AS DECIMAL(18,2)), 0) AS [Mar 2025],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_4 ELSE 0 END), 0) AS DECIMAL(18,2)), 0) AS [Apr 2025],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_5 ELSE 0 END), 0) AS DECIMAL(18,2)), 0) AS [May 2025],
    ISNULL(CAST(ROUND(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_6 ELSE 0 END), 0) AS DECIMAL(18,2)), 0) AS [Jun 2025],
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_5 ELSE 0 END)
        - SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_5 ELSE 0 END)
    , 2) AS DECIMAL(18,2)), 0) AS [Mo. Bdgt Var May 2025],
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_5 ELSE 0 END)
    , 2) AS DECIMAL(18,2)), 0) AS [Mo. Bdgt May 2025],
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD May 2025],
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD Bdgt May 2025],
    ISNULL(CAST(ROUND(
        SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount IN ('5312-5303','5322-5303') THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END)
    , 2) AS DECIMAL(18,2)), 0) AS [YTD May 2024]
FROM #HierarchyData h
GROUP BY h.Center

-- Net revenue per procedure (corrected YTD calculations as an example)
UNION ALL
SELECT
    h.Center,
    'Net revenue per procedure',
    /* Oct-24 */
    ISNULL(CAST(ROUND(
        (
            (SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_11 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr= '2024' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_11 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_11 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_11 ELSE 0 END)
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_11 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0),
    /* Nov-24 */
    ISNULL(CAST(ROUND(
        (
            (SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_12 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr= '2024' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_12 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_12 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_12 ELSE 0 END)
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_12 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0),
    /* Dec-24 */
    ISNULL(CAST(ROUND(
        (
            (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr= '2025' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_1 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1 ELSE 0 END)
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0),
    /* Jan-25 */
    ISNULL(CAST(ROUND(
        (
            (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_2 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr= '2025' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_2 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_2 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_2 ELSE 0 END)
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_2 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0),
    /* Feb-25 */
    ISNULL(CAST(ROUND(
        (
            (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_3 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr='2025' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_3 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_3 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_3 ELSE 0 END)
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_3 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0),
    /* Mar-25 */
    ISNULL(CAST(ROUND(
        (
            (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_4 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr='2025' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_4 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_4 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_4 ELSE 0 END)
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_4 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0),
    /* Apr-25 */
    ISNULL(CAST(ROUND(
        (
            (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr='2025' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_5 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END) 
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0),
    /* May-25 */
    ISNULL(CAST(ROUND(
        (
            (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_6 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr='2025' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_6 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_6 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_6 ELSE 0 END)
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_6 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0),
    /* Mo. Bdgt Var Apr-25 */
    ISNULL(CAST(ROUND(
        (
            (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr='2025' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_5 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END) 
        ) -
        (
            (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr= '2025' and h.amt_class_type= 'budget' and h.FullAccount = '8109-0000' THEN h.ldr_amt_5 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0),
    /* Mo. Bdgt Apr-25 */
    ISNULL(CAST(ROUND(
        (
           (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END) * -1) +
           (SUM(Case WHEN h.processing_yr= '2025' and h.amt_class_type= 'budget' and h.FullAccount = '8109-0000' THEN h.ldr_amt_5 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_5 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0),
    /* YTD Apr-25 (Actual) */
    ISNULL(CAST(ROUND(
        (
            ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) * -1) -
		(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8109-0000' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) * -1)) -
            (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END))
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0),
    /* YTD Bdgt Apr-25 */
    ISNULL(CAST(ROUND(
        (
            ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) * -1) -
		(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount = '8109-0000' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) * -1)) -
            (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END))
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0),
    /* YTD Apr-24 (Actual) */
    ISNULL(CAST(ROUND(
        (
            ((SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) * -1) -
		(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount = '8109-0000' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) * -1)) -
        (SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) -
        SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END))
        ) /
        NULLIF(SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE 'R1%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END), 0)
    , 2) AS DECIMAL(18,2)), 0)
FROM #HierarchyData h
GROUP BY h.Center

-- Center Level EBITDA per center  (Net Revenue – Total Operating Expenses)
UNION ALL
SELECT
    h.Center,
    'Center Level EBITDA',

    /* ─────────── Monthly actuals ─────────── */
    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_11 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr= '2024' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_11 ELSE 0 END) * -1) -
			SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_11 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_11 ELSE 0 END)
        -
        ( SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_11 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_11 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_11 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_11 ELSE 0 END) +
          ((SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_11 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_11 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_11 ELSE 0 END))* -1)
          )
        )
    , 2) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_12 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr= '2024' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_12 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_12 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_12 ELSE 0 END)
        -
        ( SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_12 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_12 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_12 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_12 ELSE 0 END) +
          (  (SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_12 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_12 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_12 ELSE 0 END))* -1)
          )
        )
    , 2) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr= '2025' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_1 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1 ELSE 0 END)
        -
        ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1  ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1  ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_1  ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_1  ELSE 0 END) +
          (  (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_1 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_1 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_1 ELSE 0 END))* -1)
          )
        )
    , 2) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_2 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr= '2025' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_2 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_2 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_2 ELSE 0 END)
        -
        ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_2 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_2 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_2 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_2 ELSE 0 END) +
          (  (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_2 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_2 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_2 ELSE 0 END))* -1)
          )
        )
    , 2) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_3 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr= '2025' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_3 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_3 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_3 ELSE 0 END)
        -
        ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_3 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_3 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_3 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_3 ELSE 0 END) +
          (  (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_3 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_3 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_3 ELSE 0 END))* -1)
          )
        )
    , 2) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_4 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr= '2025' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_4 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_4 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_4 ELSE 0 END)
        -
        ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_4 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_4 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_4 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_4 ELSE 0 END) +
          (  (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_4 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_4 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_4 ELSE 0 END))* -1)
          )
        )
    , 2) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr= '2025' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_5 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
        -
        ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_5 ELSE 0 END) +
          (  (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_5 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_5 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_5 ELSE 0 END))* -1)
          )
        )
    , 2) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_6 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr= '2025' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_6 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_6 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_6 ELSE 0 END)
        -
        (SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_6 ELSE 0 END) +
         SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_6 ELSE 0 END) +
         SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_6 ELSE 0 END) +
         SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_6 ELSE 0 END) +
         ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_6 ELSE 0 END) +
         SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_6 ELSE 0 END)) -
         ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_6 ELSE 0 END))* -1)
          )
        )
    , 2) AS DECIMAL(18,2)), 0),

    /* ─────────── Mo. budget variance & budget (Apr-25) ─────────── */
    -- Mo. Bdgt Var Apr-25 = Actual EBITDA − Budget EBITDA
    ISNULL(CAST(ROUND(
        (
          /* Actual EBITDA Apr-25 */
          (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr='2025' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_5 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END) 
			-
          ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END) +
            SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END) +
            SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_5 ELSE 0 END) +
            SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_5 ELSE 0 END) +
            (  (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_5 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_5 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_5 ELSE 0 END))* -1)
          )
          )
        ) -
        (
          /* Budget EBITDA Apr-25 */
          (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr= '2025' and h.amt_class_type= 'budget' and h.FullAccount = '8109-0000' THEN h.ldr_amt_5 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
			-
          ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END) +
            SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END) +
            SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_5 ELSE 0 END) +
            SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_5 ELSE 0 END) +
            (  (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_5 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_5 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_5 ELSE 0 END))* -1)
          )
          )
        )
    , 2) AS DECIMAL(18,2)), 0),

    -- Mo. Bdgt Apr-25 (Budget EBITDA)
    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END) * -1) +
           (SUM(Case WHEN h.processing_yr= '2025' and h.amt_class_type= 'budget' and h.FullAccount = '8109-0000' THEN h.ldr_amt_5 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END)
		-
        ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_5 ELSE 0 END) +
          (  (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_5 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_5 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_5 ELSE 0 END))* -1)
          )
        )
    , 2) AS DECIMAL(18,2)), 0),

    /* ─────────── Year-to-date totals ─────────── */
    ISNULL(CAST(ROUND(
        ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) * -1) -
		(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8109-0000' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) * -1)) -
            (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END))
		-
        ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
          (  (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))* -1)
          )
        )
    , 2) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(
        ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) * -1) -
		(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount = '8109-0000' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) * -1)) -
            (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END))
		-
        ( SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2025' AND h.amt_class_type='budget' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
          (  (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))* -1)
          )
        )
    , 2) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(
        ((SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) * -1) -
		(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount = '8109-0000' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) * -1)) -
        (SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) -
        SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END))
	-
        ( SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '71%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '72%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '73%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
          SUM(CASE WHEN h.processing_yr='2024' AND h.amt_class_type='actual' AND h.FullAccount LIKE '74%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
          (  (SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '75%' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END) +
        SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount = '8221-0000' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END)) -
       ((SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount = '8143-0000' THEN h.ldr_amt_1+h.ldr_amt_3+h.ldr_amt_4+h.ldr_amt_5 ELSE 0 END))* -1)
          )
        )
    , 2) AS DECIMAL(18,2)), 0)

FROM #HierarchyData h
GROUP BY h.Center

-- Net Revenue per center: ABS(61%) - 62% - 63%
UNION ALL
SELECT 
    h.Center,
    'Net Revenue',
    
    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_11 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr= '2024' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_11 ELSE 0 END) * -1)+
            (SUM(Case WHEN h.processing_yr= '2024' and h.amt_class_type='actual' and h.FullAccount = '8104-0000' THEN h.ldr_amt_11 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_11 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_11 ELSE 0 END) 			
    , 2) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_12 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr= '2024' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_12 ELSE 0 END) * -1)+
            (SUM(Case WHEN h.processing_yr= '2024' and h.amt_class_type='actual' and h.FullAccount = '8104-0000' THEN h.ldr_amt_12 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_12 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_12 ELSE 0 END) 			
    , 2) AS DECIMAL(18,2)), 0),

    
    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr= '2025' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_1 ELSE 0 END) * -1)+
            (SUM(Case WHEN h.processing_yr= '2025' and h.amt_class_type='actual' and h.FullAccount = '8104-0000' THEN h.ldr_amt_1 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1 ELSE 0 END) 			
    , 2) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_2 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr= '2025' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_2 ELSE 0 END) * -1)+
            (SUM(Case WHEN h.processing_yr= '2025' and h.amt_class_type='actual' and h.FullAccount = '8104-0000' THEN h.ldr_amt_2 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_2 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_2 ELSE 0 END) 			
    , 2) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_3 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr='2025' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_3 ELSE 0 END) * -1)+
            (SUM(Case WHEN h.processing_yr='2025' and h.amt_class_type='actual' and h.FullAccount = '8104-0000' THEN h.ldr_amt_3 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_3 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_3 ELSE 0 END) 			
    , 2) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_4 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr='2025' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_4 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr='2025' and h.amt_class_type='actual' and h.FullAccount = '8104-0000' THEN h.ldr_amt_4 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_4 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_4 ELSE 0 END) 			
    , 2) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr='2025' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_5 ELSE 0 END) * -1)+
            (SUM(Case WHEN h.processing_yr='2025' and h.amt_class_type='actual' and h.FullAccount = '8104-0000' THEN h.ldr_amt_5 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END) 			
    , 2) AS DECIMAL(18,2)), 0),

    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_6 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr='2025' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_6 ELSE 0 END) * -1)+
            (SUM(Case WHEN h.processing_yr='2025' and h.amt_class_type='actual' and h.FullAccount = '8104-0000' THEN h.ldr_amt_6 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_6 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_6 ELSE 0 END) 			
    , 2) AS DECIMAL(18,2)), 0),

    -- Mo. Bdgt Var May 2025
    ISNULL(CAST(ROUND(
        (
            (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr='2025' and h.amt_class_type='actual' and h.FullAccount = '8109-0000' THEN h.ldr_amt_5 ELSE 0 END) * -1)+
            (SUM(Case WHEN h.processing_yr='2025' and h.amt_class_type='actual' and h.FullAccount = '8104-0000' THEN h.ldr_amt_5 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END) 
        ) -
        (
            (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END) * -1) +
            (SUM(Case WHEN h.processing_yr= '2025' and h.amt_class_type= 'budget' and h.FullAccount = '8109-0000' THEN h.ldr_amt_5 ELSE 0 END) * -1)+
            (SUM(Case WHEN h.processing_yr= '2025' and h.amt_class_type= 'budget' and h.FullAccount = '8104-0000' THEN h.ldr_amt_5 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END) 
        )
    , 2) AS DECIMAL(18,2)), 0),

    -- Mo. Bdgt May 2025
    ISNULL(CAST(ROUND(
        (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_5 ELSE 0 END) * -1) +
           (SUM(Case WHEN h.processing_yr= '2025' and h.amt_class_type= 'budget' and h.FullAccount = '8109-0000' THEN h.ldr_amt_5 ELSE 0 END) * -1)+
           (SUM(Case WHEN h.processing_yr= '2025' and h.amt_class_type= 'budget' and h.FullAccount = '8104-0000' THEN h.ldr_amt_5 ELSE 0 END) * -1)-
			SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_5 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_5 ELSE 0 END) 
    , 2) AS DECIMAL(18,2)), 0),

    -- YTD Actual May 2025
    ISNULL(CAST(ROUND(
        ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) * -1) +
		(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8109-0000' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) * -1)+
		(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount = '8104-0000' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) * -1)) -
            (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END))
    , 2) AS DECIMAL(18,2)), 0),

    -- YTD Bdgt May 2025
    ISNULL(CAST(ROUND(
        ((SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) * -1) +
		(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount = '8109-0000' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) * -1)+
		(SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount = '8104-0000' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) * -1)) -
            (SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) -
            SUM(CASE WHEN h.processing_yr = '2025' AND h.amt_class_type = 'budget' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END))
    , 2) AS DECIMAL(18,2)), 0),

    -- YTD Actual May 2024
    ISNULL(CAST(ROUND(
        ((SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '61%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) * -1) +
		(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount = '8109-0000' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) * -1)+
		(SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount = '8104-0000' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) * -1)) -
        (SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '62%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END) -
        SUM(CASE WHEN h.processing_yr = '2024' AND h.amt_class_type = 'actual' AND h.FullAccount LIKE '63%' THEN h.ldr_amt_1 + h.ldr_amt_2 + h.ldr_amt_3 + h.ldr_amt_4 + h.ldr_amt_5 ELSE 0 END))
    , 2) AS DECIMAL(18,2)), 0)

FROM #HierarchyData h
GROUP BY h.Center;

DROP TABLE #HierarchyData;