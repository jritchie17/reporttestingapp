SELECT DISTINCT
    'Facility: ' +
	Case WHEN Element3 IN ('Bad debt expense - facility','Contractual adjustments - facility') THEN Element3
    ELSE Element3_CaReportName END AS 'CAReportName',
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Mar]
             WHEN Year = '2024' THEN [Mar] ELSE 0 END) AS [Mar 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Apr]
             WHEN Year = '2024' THEN [Apr] ELSE 0 END) AS [Apr 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [May]
             WHEN Year = '2024' THEN [May] ELSE 0 END) AS [May 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Jun]
             WHEN Year = '2024' THEN [Jun] ELSE 0 END) AS [Jun 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Jul]
             WHEN Year = '2024' THEN [Jul] ELSE 0 END) AS [Jul 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Aug]
             WHEN Year = '2024' THEN [Aug] ELSE 0 END) AS [Aug 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Sep]
             WHEN Year = '2024' THEN [Sep] ELSE 0 END) AS [Sep 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Oct]
             WHEN Year = '2024' THEN [Oct] ELSE 0 END) AS [Oct 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Nov]
             WHEN Year = '2024' THEN [Nov] ELSE 0 END) AS [Nov 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Dec]
             WHEN Year = '2024' THEN [Dec] ELSE 0 END) AS [Dec 2024],
    SUM(CASE WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Jan]
             WHEN Year = '2025' THEN [Jan] ELSE 0 END) AS [Jan 2025],
    SUM(CASE WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Feb]
             WHEN Year = '2025' THEN [Feb] ELSE 0 END) AS [Feb 2025],
    SUM(CASE WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Mar]
             WHEN Year = '2025' THEN [Mar] ELSE 0 END) AS [Mar 2025],
    SUM(CASE WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Apr]
             WHEN Year = '2025' THEN [Apr] ELSE 0 END) AS [Apr 2025],
    SUM(CASE WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [May]
             WHEN Year = '2025' THEN [May] ELSE 0 END) AS [May 2025],
	SUM(CASE WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN 
            -1 * ((Apr + Mar + Feb) / 3.0)
			 WHEN Year = '2025' THEN (Apr + Mar + Feb) / 3.0 ELSE 0 END ) AS [May 2025 T3],
	SUM(CASE WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN 
            -1 * (May - ((Apr + Mar + Feb) / 3.0))
			 WHEN Year = '2025' THEN (May - ((Apr + Mar + Feb) / 3.0)) ELSE 0 END ) AS [May 2025 Var],
	SUM(CASE WHEN Year = '2025' AND May = 0 THEN 0
			 WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN 
            -1 * ((May - ((Apr + Mar + Feb) / 3.0)) / NULLIF(May, 0))
			WHEN Year = '2025' THEN (May - ((Apr + Mar + Feb) / 3.0)) / NULLIF(May, 0) ELSE 0 END ) AS [May 2025 Var%],
	SUM(CASE WHEN Year = '2025' AND Element3_CAReportNAME IN('0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days', 'Credit Balances') THEN NULL
			 WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May 
			 ELSE NULL END) AS YTDMay2025Actual,
	SUM(CASE WHEN Year = '2024' AND Element3_CAReportNAME IN('0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days', 'Credit Balances') THEN NULL
			 WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May 
			 ELSE NULL END) AS YTDMay2025PY,
	CASE 
    WHEN 
        SUM(CASE WHEN Year = '2025' AND Element3_CAReportNAME IN ('0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days','Credit Balances') THEN NULL
                 WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May 
                 ELSE NULL END) IS NULL
     OR
        SUM(CASE WHEN Year = '2024' AND Element3_CAReportNAME IN ('0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days','Credit Balances') THEN NULL
                 WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May 
                 ELSE NULL END) IS NULL
    THEN NULL
    ELSE
        SUM(CASE WHEN Year = '2024' AND Element3_CAReportNAME IN ('0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days','Credit Balances') THEN NULL
                 WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May 
                 ELSE NULL END)
        -
        SUM(CASE WHEN Year = '2025' AND Element3_CAReportNAME IN ('0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days','Credit Balances') THEN NULL
                 WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May 
                 ELSE NULL END)
END AS YTDMay2025Var,
CASE 
    WHEN 
        SUM(CASE WHEN Year = '2025' AND Element3_CAReportNAME IN ('0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days','Credit Balances') THEN NULL
                 WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May 
                 ELSE NULL END) IS NULL
     OR
        SUM(CASE WHEN Year = '2024' AND Element3_CAReportNAME IN ('0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days','Credit Balances') THEN NULL
                 WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May 
                 ELSE NULL END) IS NULL
     OR
        ABS(SUM(CASE WHEN Year = '2024' AND Element3_CAReportNAME IN ('0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days','Credit Balances') THEN NULL
                     WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May 
                     ELSE NULL END)) = 0
    THEN NULL
    ELSE
        (
            SUM(CASE WHEN Year = '2025' AND Element3_CAReportNAME IN ('0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days','Credit Balances') THEN NULL
                     WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May 
                     ELSE NULL END)
            -
            SUM(CASE WHEN Year = '2024' AND Element3_CAReportNAME IN ('0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days','Credit Balances') THEN NULL
                     WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May 
                     ELSE NULL END)
        )
        /
        ABS(SUM(CASE WHEN Year = '2024' AND Element3_CAReportNAME IN ('0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days','Credit Balances') THEN NULL
                     WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May 
                     ELSE NULL END))
END AS YTDMay2025VarPct



FROM [CognosTesting].[dbo].[RawTestSet] r
INNER JOIN [CognosTesting].[dbo].[ReportingAccountHierarchy] rah
    ON r.accountnumber = rah.joincolumn
WHERE 
    rah.element1 = 'AR Reserve'
    AND AmountType = 'Actual'
    AND Year IN ('2024', '2025')
    AND CenterNumber NOT LIKE '2289%'
    AND Element2 <> 'Facility allowance'
    AND CenterNumber NOT IN ('M313-001', 'M232-001')
    AND Element3_CaReportName NOT LIKE '%anesthesia%'
    AND (
        Element3_CaReportName IN (
            '0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days',
            'Contractual write-offs','Credit balances','Non-aged balances','Total procedures', 'Bad debt write-offs, net of recoveries'
        )
        OR Element3 IN (
            'Bad debt expense - facility','Contractual adjustments - facility'
        )
    )
    AND AccountNumber NOT LIKE '%1202%'
GROUP BY Element3_CaReportName, Element3

UNION ALL

  SELECT 
	  'Facility: ' +
	  element3_careportname AS CAReportName,
	  SUM(CASE WHEN Year = '2024' THEN beginningbalance + Jan + Feb + Mar END) AS [Mar 2024],
	  SUM(CASE WHEN Year = '2024' THEN beginningbalance + Jan + Feb + Mar + Apr END) AS [Apr 2024],
	  SUM(CASE WHEN Year = '2024' THEN beginningbalance + Jan + Feb + Mar + Apr + May END) AS [May 2024],
	  SUM(CASE WHEN Year = '2024' THEN beginningbalance + Jan + Feb + Mar + Apr + May + Jun END) AS [Jun 2024],
	  SUM(CASE WHEN Year = '2024' THEN beginningbalance + Jan + Feb + Mar + Apr + May + Jun + Jul END) AS [Jul 2024],
	  SUM(CASE WHEN Year = '2024' THEN beginningbalance + Jan + Feb + Mar + Apr + May + Jun + Jul + Aug END) AS [Aug 2024],
	  SUM(CASE WHEN Year = '2024' THEN beginningbalance + Jan + Feb + Mar + Apr + May + Jun + Jul + Aug + Sep END) AS [Sep 2024],
	  SUM(CASE WHEN Year = '2024' THEN beginningbalance + Jan + Feb + Mar + Apr + May + Jun + Jul + Aug + Sep + Oct END) AS [Oct 2024],
	  SUM(CASE WHEN Year = '2024' THEN beginningbalance + Jan + Feb + Mar + Apr + May + Jun + Jul + Aug + Sep + Oct + Nov END) AS [Nov 2024],
	  SUM(CASE WHEN Year = '2024' THEN beginningbalance + Jan + Feb + Mar + Apr + May + Jun + Jul + Aug + Sep + Oct + Nov + Dec END) AS [Dec 2024],
	  SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan END) AS [Jan 2025],
	  SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb END) AS [Feb 2025],
	  SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar END) AS [Mar 2025],
	  SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar + Apr END) AS [Apr 2025],
	  SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar + Apr + May END) AS [May 2025],
	  (SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb END) +  
      SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar END) +  
      SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar + Apr END)) / 3.0 AS [May 2025 T3],
	  (SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar + Apr + May END) -
      (SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb END) +  
        SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar END) +  
        SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar + Apr END)) / 3.0) AS [May 2025 Var],
		( CASE WHEN SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar + Apr + May END) = 0 THEN 0
        ELSE 
            (SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar + Apr + May END) - 
                (SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb END) +
                 SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar END) +
                 SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar + Apr END)) / 3.0
            ) / 
            NULLIF(SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar + Apr + May END), 0)END) AS [May 2025 Var%],
                NULL AS YTDMay2025Actual,
                NULL AS YTDMay2025PY,
                NULL AS YTDMay2025Var,
                NULL AS YTDMay2025VarPct
  FROM [CognosTesting].[dbo].[RawTestSet] r
INNER JOIN [CognosTesting].[dbo].[ReportingAccountHierarchy] rah
    ON r.accountnumber = rah.joincolumn

	WHERE element2_careportname = 'Accounts receivable, net'
	AND rah.element1 = 'AR Reserve'
    AND AmountType = 'Actual'
    AND Year IN ('2024', '2025')
    AND CenterNumber NOT LIKE '2289%'
    AND CenterNumber NOT IN ('M313-001', 'M232-001')
	AND BusinessLine <> 'NA'
	AND Element2 NOT LIKE '%Anesthesia%'
    AND AccountNumber NOT LIKE '%1202%'
  GROUP BY element3_careportname

  UNION ALL

  SELECT 
	  'Facility: ' +
	  element2_careportname AS CAReportName,
	  SUM(CASE WHEN Year = '2024' THEN beginningbalance + Jan + Feb + Mar END) AS [Mar 2024],
	  SUM(CASE WHEN Year = '2024' THEN beginningbalance + Jan + Feb + Mar + Apr END) AS [Apr 2024],
	  SUM(CASE WHEN Year = '2024' THEN beginningbalance + Jan + Feb + Mar + Apr + May END) AS [May 2024],
	  SUM(CASE WHEN Year = '2024' THEN beginningbalance + Jan + Feb + Mar + Apr + May + Jun END) AS [Jun 2024],
	  SUM(CASE WHEN Year = '2024' THEN beginningbalance + Jan + Feb + Mar + Apr + May + Jun + Jul END) AS [Jul 2024],
	  SUM(CASE WHEN Year = '2024' THEN beginningbalance + Jan + Feb + Mar + Apr + May + Jun + Jul + Aug END) AS [Aug 2024],
	  SUM(CASE WHEN Year = '2024' THEN beginningbalance + Jan + Feb + Mar + Apr + May + Jun + Jul + Aug + Sep END) AS [Sep 2024],
	  SUM(CASE WHEN Year = '2024' THEN beginningbalance + Jan + Feb + Mar + Apr + May + Jun + Jul + Aug + Sep + Oct END) AS [Oct 2024],
	  SUM(CASE WHEN Year = '2024' THEN beginningbalance + Jan + Feb + Mar + Apr + May + Jun + Jul + Aug + Sep + Oct + Nov END) AS [Nov 2024],
	  SUM(CASE WHEN Year = '2024' THEN beginningbalance + Jan + Feb + Mar + Apr + May + Jun + Jul + Aug + Sep + Oct + Nov + Dec END) AS [Dec 2024],
	  SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan END) AS [Jan 2025],
	  SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb END) AS [Feb 2025],
	  SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar END) AS [Mar 2025],
	  SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar + Apr END) AS [Apr 2025],
	  SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar + Apr + May END) AS [May 2025],
	  (SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb END) +  
      SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar END) +  
      SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar + Apr END)) / 3.0 AS [May 2025 T3],
	  (SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar + Apr + May END) -
      (SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb END) +  
        SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar END) +  
        SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar + Apr END)) / 3.0) AS [May 2025 Var],
		( CASE WHEN SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar + Apr + May END) = 0 THEN 0
        ELSE 
            (SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar + Apr + May END) - 
                (SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb END) +
                 SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar END) +
                 SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar + Apr END)) / 3.0
            ) / 
            NULLIF(SUM(CASE WHEN Year = '2025' THEN beginningbalance + Jan + Feb + Mar + Apr + May END), 0)END) AS [May 2025 Var%], 
                        NULL AS YTDMay2025Actual,
                        NULL AS YTDMay2025PY,
                        NULL AS YTDMay2025Var,
                        NULL AS YTDMay2025VarPct
	  
  FROM [CognosTesting].[dbo].[RawTestSet] r
INNER JOIN [CognosTesting].[dbo].[ReportingAccountHierarchy] rah
    ON r.accountnumber = rah.joincolumn

	WHERE element2_careportname = 'Accounts receivable, net'
	AND rah.element1 = 'AR Reserve'
    AND AmountType = 'Actual'
    AND Year IN ('2024', '2025')
    AND CenterNumber NOT LIKE '2289%'
    AND CenterNumber NOT IN ('M313-001', 'M232-001')
	AND BusinessLine <> 'NA'
	AND Element2 NOT LIKE '%Anesthesia%'
    AND AccountNumber NOT LIKE '%1202%'
  GROUP BY element2_careportname

  UNION ALL 

SELECT DISTINCT
    'Facility: ' +
    Element2_CaReportName AS 'CAReportName',
    SUM(CASE WHEN Year = '2024' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [Mar]
             WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Mar]
             WHEN Year = '2024' THEN [Mar] ELSE 0 END) AS [Mar 2024],
    SUM(CASE WHEN Year = '2024' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [Apr]
             WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Apr]
             WHEN Year = '2024' THEN [Apr] ELSE 0 END) AS [Apr 2024],
    SUM(CASE WHEN Year = '2024' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [May]
             WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [May]
             WHEN Year = '2024' THEN [May] ELSE 0 END) AS [May 2024],
    SUM(CASE WHEN Year = '2024' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [Jun]
             WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Jun]
             WHEN Year = '2024' THEN [Jun] ELSE 0 END) AS [Jun 2024],
    SUM(CASE WHEN Year = '2024' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [Jul]
             WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Jul]
             WHEN Year = '2024' THEN [Jul] ELSE 0 END) AS [Jul 2024],
    SUM(CASE WHEN Year = '2024' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [Aug]
             WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Aug]
             WHEN Year = '2024' THEN [Aug] ELSE 0 END) AS [Aug 2024],
    SUM(CASE WHEN Year = '2024' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [Sep]
             WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Sep]
             WHEN Year = '2024' THEN [Sep] ELSE 0 END) AS [Sep 2024],
    SUM(CASE WHEN Year = '2024' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [Oct]
             WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Oct]
             WHEN Year = '2024' THEN [Oct] ELSE 0 END) AS [Oct 2024],
    SUM(CASE WHEN Year = '2024' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [Nov]
             WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Nov]
             WHEN Year = '2024' THEN [Nov] ELSE 0 END) AS [Nov 2024],
    SUM(CASE WHEN Year = '2024' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [Dec]
             WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Dec]
             WHEN Year = '2024' THEN [Dec] ELSE 0 END) AS [Dec 2024],
    SUM(CASE WHEN Year = '2025' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [Jan]
             WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Jan]
             WHEN Year = '2025' THEN [Jan] ELSE 0 END) AS [Jan 2025],
    SUM(CASE WHEN Year = '2025' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [Feb]
             WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Feb]
             WHEN Year = '2025' THEN [Feb] ELSE 0 END) AS [Feb 2025],
    SUM(CASE WHEN Year = '2025' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [Mar]
             WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Mar]
             WHEN Year = '2025' THEN [Mar] ELSE 0 END) AS [Mar 2025],
    SUM(CASE WHEN Year = '2025' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [Apr]
             WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Apr]
             WHEN Year = '2025' THEN [Apr] ELSE 0 END) AS [Apr 2025],
    SUM(CASE WHEN Year = '2025' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [May]
             WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [May]
             WHEN Year = '2025' THEN [May] ELSE 0 END) AS [May 2025],
			 (
    SUM(
        CASE 
            WHEN Year = '2025' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [Feb]
            WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Feb]
            WHEN Year = '2025' THEN [Feb]
            ELSE 0 
        END
    ) +
    SUM(
        CASE 
            WHEN Year = '2025' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [Mar]
            WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Mar]
            WHEN Year = '2025' THEN [Mar]
            ELSE 0 
        END
    ) +
    SUM(
        CASE 
            WHEN Year = '2025' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [Apr]
            WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Apr]
            WHEN Year = '2025' THEN [Apr]
            ELSE 0 
        END
    )
) / 3.0 AS [May 2025 T3],
(
    SUM(
        CASE 
            WHEN Year = '2025' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [May]
            WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [May]
            WHEN Year = '2025' THEN [May]
            ELSE 0 
        END
    ) -
    (
        SUM(
            CASE 
                WHEN Year = '2025' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [Feb]
                WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Feb]
                WHEN Year = '2025' THEN [Feb]
                ELSE 0 
            END
        ) +
        SUM(
            CASE 
                WHEN Year = '2025' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [Mar]
                WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Mar]
                WHEN Year = '2025' THEN [Mar]
                ELSE 0 
            END
        ) +
        SUM(
            CASE 
                WHEN Year = '2025' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [Apr]
                WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Apr]
                WHEN Year = '2025' THEN [Apr]
                ELSE 0 
            END
        )
    ) / 3.0
) AS [May 2025 Var],
(
    CASE 
        WHEN 
            SUM(
                CASE 
                    WHEN Year = '2025' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [May]
                    WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [May]
                    WHEN Year = '2025' THEN [May]
                    ELSE 0 
                END
            ) = 0 
        THEN 0
        ELSE
            (
                SUM(
                    CASE 
                        WHEN Year = '2025' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [May]
                        WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [May]
                        WHEN Year = '2025' THEN [May]
                        ELSE 0 
                    END
                ) -
                (
                    SUM(
                        CASE 
                            WHEN Year = '2025' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [Feb]
                            WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Feb]
                            WHEN Year = '2025' THEN [Feb]
                            ELSE 0 
                        END
                    ) +
                    SUM(
                        CASE 
                            WHEN Year = '2025' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [Mar]
                            WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Mar]
                            WHEN Year = '2025' THEN [Mar]
                            ELSE 0 
                        END
                    ) +
                    SUM(
                        CASE 
                            WHEN Year = '2025' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [Apr]
                            WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [Apr]
                            WHEN Year = '2025' THEN [Apr]
                            ELSE 0 
                        END
                    )
                ) / 3.0
            ) / NULLIF(
                SUM(
                    CASE 
                        WHEN Year = '2025' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * [May]
                        WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * [May]
                        WHEN Year = '2025' THEN [May]
                        ELSE 0 
                    END
                ),
                0
            )
    END
) AS [May 2025 Var%],
SUM(
    CASE 
        WHEN Element2_CaReportName IN ('A211-0000 Gross days in AR', 'Accounts receivable greater than 90 days', 'Total accounts receivable aging') 
            THEN NULL
        WHEN Year = '2025' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' 
            THEN -1 * (Jan + Feb + Mar + Apr + May)
        WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') 
            THEN -1 * (Jan + Feb + Mar + Apr + May)
        WHEN Year = '2025' 
            THEN Jan + Feb + Mar + Apr + May
        ELSE NULL
    END
) AS YTDMay2025Actual
        ,SUM(
            CASE
                WHEN Element2_CaReportName IN ('A211-0000 Gross days in AR', 'Accounts receivable greater than 90 days', 'Total accounts receivable aging') THEN NULL
                WHEN Year = '2024' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * (Jan + Feb + Mar + Apr + May)
                WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * (Jan + Feb + Mar + Apr + May)
                WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May
                ELSE NULL
            END
        ) AS YTDMay2025PY,
        CASE
            WHEN
                SUM(CASE
                        WHEN Element2_CaReportName IN ('A211-0000 Gross days in AR', 'Accounts receivable greater than 90 days', 'Total accounts receivable aging') THEN NULL
                        WHEN Year = '2025' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * (Jan + Feb + Mar + Apr + May)
                        WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * (Jan + Feb + Mar + Apr + May)
                        WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May
                        ELSE NULL
                    END) IS NULL
             OR
                SUM(CASE
                        WHEN Element2_CaReportName IN ('A211-0000 Gross days in AR', 'Accounts receivable greater than 90 days', 'Total accounts receivable aging') THEN NULL
                        WHEN Year = '2024' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * (Jan + Feb + Mar + Apr + May)
                        WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * (Jan + Feb + Mar + Apr + May)
                        WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May
                        ELSE NULL
                    END) IS NULL
            THEN NULL
            ELSE
                SUM(CASE
                        WHEN Element2_CaReportName IN ('A211-0000 Gross days in AR', 'Accounts receivable greater than 90 days', 'Total accounts receivable aging') THEN NULL
                        WHEN Year = '2024' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * (Jan + Feb + Mar + Apr + May)
                        WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * (Jan + Feb + Mar + Apr + May)
                        WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May
                        ELSE NULL
                    END)
                -
                SUM(CASE
                        WHEN Element2_CaReportName IN ('A211-0000 Gross days in AR', 'Accounts receivable greater than 90 days', 'Total accounts receivable aging') THEN NULL
                        WHEN Year = '2025' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * (Jan + Feb + Mar + Apr + May)
                        WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * (Jan + Feb + Mar + Apr + May)
                        WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May
                        ELSE NULL
                    END)
        END AS YTDMay2025Var,
        CASE
            WHEN
                SUM(CASE
                        WHEN Element2_CaReportName IN ('A211-0000 Gross days in AR', 'Accounts receivable greater than 90 days', 'Total accounts receivable aging') THEN NULL
                        WHEN Year = '2025' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * (Jan + Feb + Mar + Apr + May)
                        WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * (Jan + Feb + Mar + Apr + May)
                        WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May
                        ELSE NULL
                    END) IS NULL
             OR
                SUM(CASE
                        WHEN Element2_CaReportName IN ('A211-0000 Gross days in AR', 'Accounts receivable greater than 90 days', 'Total accounts receivable aging') THEN NULL
                        WHEN Year = '2024' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * (Jan + Feb + Mar + Apr + May)
                        WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * (Jan + Feb + Mar + Apr + May)
                        WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May
                        ELSE NULL
                    END) IS NULL
             OR
                ABS(SUM(CASE
                        WHEN Element2_CaReportName IN ('A211-0000 Gross days in AR', 'Accounts receivable greater than 90 days', 'Total accounts receivable aging') THEN NULL
                        WHEN Year = '2024' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * (Jan + Feb + Mar + Apr + May)
                        WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * (Jan + Feb + Mar + Apr + May)
                        WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May
                        ELSE NULL
                    END)) = 0
            THEN NULL
            ELSE
                (
                    SUM(CASE
                            WHEN Element2_CaReportName IN ('A211-0000 Gross days in AR', 'Accounts receivable greater than 90 days', 'Total accounts receivable aging') THEN NULL
                            WHEN Year = '2025' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * (Jan + Feb + Mar + Apr + May)
                            WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * (Jan + Feb + Mar + Apr + May)
                            WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May
                            ELSE NULL
                        END)
                    -
                    SUM(CASE
                            WHEN Element2_CaReportName IN ('A211-0000 Gross days in AR', 'Accounts receivable greater than 90 days', 'Total accounts receivable aging') THEN NULL
                            WHEN Year = '2024' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * (Jan + Feb + Mar + Apr + May)
                            WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * (Jan + Feb + Mar + Apr + May)
                            WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May
                            ELSE NULL
                        END)
                )
                /
                ABS(SUM(CASE
                        WHEN Element2_CaReportName IN ('A211-0000 Gross days in AR', 'Accounts receivable greater than 90 days', 'Total accounts receivable aging') THEN NULL
                        WHEN Year = '2024' AND Element2_CaReportName = 'Visits' AND Element3 = 'S128-6022' THEN -1 * (Jan + Feb + Mar + Apr + May)
                        WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * (Jan + Feb + Mar + Apr + May)
                        WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May
                        ELSE NULL
                    END))
        END AS YTDMay2025VarPct


FROM [CognosTesting].[dbo].[RawTestSet] r
INNER JOIN [CognosTesting].[dbo].[ReportingAccountHierarchy] rah
    ON r.accountnumber = rah.joincolumn
WHERE 
    rah.element1 = 'AR Reserve'
    AND AmountType = 'Actual'
    AND Year IN ('2024', '2025')
    AND CenterNumber NOT LIKE '2289%'
    AND CenterNumber NOT IN ('M313-001', 'M232-001')
    AND Element2_CaReportName NOT LIKE '%anesthesia%'
	AND Element2 NOT LIKE '%Anesthesia%'
    AND Element2_CaReportName IN (
        'A211-0000 Gross days in AR','Collections, net of refunds',
        'Accounts receivable greater than 90 days','Collections per visit and procedure',
        'Gross charge per visit and procedure','Gross charges - facility',
        'Net revenue - facility','Refunds - facility',
        'Total accounts receivable aging','Total cases','Total procedures',
        'Total write-offs','Units','Visits','Write-off percentage'
    )
    AND AccountNumber NOT LIKE '%1202%'
GROUP BY Element2_CaReportName

UNION ALL

SELECT DISTINCT
    'Anesthesia: ' +
	Case WHEN Element3 IN ('Bad debt expense - anesthesia','Contractual adjustments - anesthesia') THEN Element3
    ELSE Element3_CaReportName END AS 'CAReportName',
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Mar]
             WHEN Year = '2024' THEN [Mar] ELSE 0 END) AS [Mar 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Apr]
             WHEN Year = '2024' THEN [Apr] ELSE 0 END) AS [Apr 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [May]
             WHEN Year = '2024' THEN [May] ELSE 0 END) AS [May 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Jun]
             WHEN Year = '2024' THEN [Jun] ELSE 0 END) AS [Jun 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Jul]
             WHEN Year = '2024' THEN [Jul] ELSE 0 END) AS [Jun 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Aug]
             WHEN Year = '2024' THEN [Aug] ELSE 0 END) AS [Aug 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Sep]
             WHEN Year = '2024' THEN [Sep] ELSE 0 END) AS [Sep 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Oct]
             WHEN Year = '2024' THEN [Oct] ELSE 0 END) AS [Oct 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Nov]
             WHEN Year = '2024' THEN [Nov] ELSE 0 END) AS [Nov 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Dec]
             WHEN Year = '2024' THEN [Dec] ELSE 0 END) AS [Dec 2024],
    SUM(CASE WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Jan]
             WHEN Year = '2025' THEN [Jan] ELSE 0 END) AS [Jan 2025],
    SUM(CASE WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Feb]
             WHEN Year = '2025' THEN [Feb] ELSE 0 END) AS [Feb 2025],
    SUM(CASE WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Mar]
             WHEN Year = '2025' THEN [Mar] ELSE 0 END) AS [Mar 2025],
    SUM(CASE WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Apr]
             WHEN Year = '2025' THEN [Apr] ELSE 0 END) AS [Apr 2025],
    SUM(CASE WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [May]
             WHEN Year = '2025' THEN [May] ELSE 0 END) AS [May 2025],
			 (
    SUM(
        CASE 
            WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Feb]
            WHEN Year = '2025' THEN [Feb]
            ELSE 0 
        END
    ) +
    SUM(
        CASE 
            WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Mar]
            WHEN Year = '2025' THEN [Mar]
            ELSE 0 
        END
    ) +
    SUM(
        CASE 
            WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Apr]
            WHEN Year = '2025' THEN [Apr]
            ELSE 0 
        END
    )
) / 3.0 AS [May 2025 T3],
(
    SUM(
        CASE 
            WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [May]
            WHEN Year = '2025' THEN [May]
            ELSE 0 
        END
    ) -
    (
        SUM(
            CASE 
                WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Feb]
                WHEN Year = '2025' THEN [Feb]
                ELSE 0 
            END
        ) +
        SUM(
            CASE 
                WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Mar]
                WHEN Year = '2025' THEN [Mar]
                ELSE 0 
            END
        ) +
        SUM(
            CASE 
                WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Apr]
                WHEN Year = '2025' THEN [Apr]
                ELSE 0 
            END
        )
    ) / 3.0
) AS [May 2025 Var],
(
    CASE 
        WHEN 
            SUM(
                CASE 
                    WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [May]
                    WHEN Year = '2025' THEN [May]
                    ELSE 0 
                END
            ) = 0 
        THEN 0
        ELSE
            (
                SUM(
                    CASE 
                        WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [May]
                        WHEN Year = '2025' THEN [May]
                        ELSE 0 
                    END
                ) -
                (
                    SUM(
                        CASE 
                            WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Feb]
                            WHEN Year = '2025' THEN [Feb]
                            ELSE 0 
                        END
                    ) +
                    SUM(
                        CASE 
                            WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Mar]
                            WHEN Year = '2025' THEN [Mar]
                            ELSE 0 
                        END
                    ) +
                    SUM(
                        CASE 
                            WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Apr]
                            WHEN Year = '2025' THEN [Apr]
                            ELSE 0 
                        END
                    )
                ) / 3.0
            ) / NULLIF(
                SUM(
                    CASE 
                        WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [May]
                        WHEN Year = '2025' THEN [May]
                        ELSE 0 
                    END
                ),
                0
            )
    END
) AS [May 2025 Var%],
SUM(CASE WHEN Year = '2025' AND Element3_CAReportNAME IN('0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days', 'Credit Balances') THEN NULL
                         WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May
                         ELSE NULL END) AS YTDMay2025Actual,
        SUM(CASE WHEN Year = '2024' AND Element3_CAReportNAME IN('0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days', 'Credit Balances') THEN NULL
                         WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May
                         ELSE NULL END) AS YTDMay2025PY,
        CASE
    WHEN
        SUM(CASE WHEN Year = '2025' AND Element3_CAReportNAME IN('0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days', 'Credit Balances') THEN NULL
                 WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May
                 ELSE NULL END) IS NULL
     OR
        SUM(CASE WHEN Year = '2024' AND Element3_CAReportNAME IN('0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days', 'Credit Balances') THEN NULL
                 WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May
                 ELSE NULL END) IS NULL
    THEN NULL
    ELSE
        SUM(CASE WHEN Year = '2024' AND Element3_CAReportNAME IN('0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days', 'Credit Balances') THEN NULL
                 WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May
                 ELSE NULL END)
        -
        SUM(CASE WHEN Year = '2025' AND Element3_CAReportNAME IN('0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days', 'Credit Balances') THEN NULL
                 WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May
                 ELSE NULL END)
END AS YTDMay2025Var,
CASE
    WHEN
        SUM(CASE WHEN Year = '2025' AND Element3_CAReportNAME IN('0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days', 'Credit Balances') THEN NULL
                 WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May
                 ELSE NULL END) IS NULL
     OR
        SUM(CASE WHEN Year = '2024' AND Element3_CAReportNAME IN('0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days', 'Credit Balances') THEN NULL
                 WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May
                 ELSE NULL END) IS NULL
     OR
        ABS(SUM(CASE WHEN Year = '2024' AND Element3_CAReportNAME IN('0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days', 'Credit Balances') THEN NULL
                     WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May
                     ELSE NULL END)) = 0
    THEN NULL
    ELSE
        (
            SUM(CASE WHEN Year = '2025' AND Element3_CAReportNAME IN('0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days', 'Credit Balances') THEN NULL
                     WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May
                     ELSE NULL END)
            -
            SUM(CASE WHEN Year = '2024' AND Element3_CAReportNAME IN('0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days', 'Credit Balances') THEN NULL
                     WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May
                     ELSE NULL END)
        )
        /
        ABS(SUM(CASE WHEN Year = '2024' AND Element3_CAReportNAME IN('0 - 30 days','120+ days','31 - 60 days','61 - 90 days','91 - 120 days', 'Credit Balances') THEN NULL
                     WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May
                     ELSE NULL END))
END AS YTDMay2025VarPct


FROM [CognosTesting].[dbo].[RawTestSet] r
INNER JOIN [CognosTesting].[dbo].[ReportingAccountHierarchy] rah
    ON r.accountnumber = rah.joincolumn
WHERE 
    rah.element1 = 'AR Reserve'
    AND AmountType = 'Actual'
    AND Year IN ('2024', '2025')
    AND CenterNumber NOT LIKE '2289%'
    AND Element2 <> 'Facility allowance'
    AND CenterNumber NOT LIKE 'M%'
    AND Element2 NOT LIKE '%facility%'
    AND (
        Element3_CaReportName IN (
            '0 - 30 days','31 - 60 days','61 - 90 days','91 - 120 days','120+ days',
            'Contractual write-offs','Credit balances','Non-aged balances', 'Bad debt write-offs, net of recoveries'
        )
        OR Element3 IN (
            'Bad debt expense - anesthesia','Contractual adjustments - anesthesia'
        )
    )
GROUP BY Element3_CaReportName, Element3

UNION ALL

SELECT DISTINCT
    'Anesthesia: ' +
    Element2_CaReportName AS 'CAReportName',
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Mar]
             WHEN Year = '2024' THEN [Mar] ELSE 0 END) AS [Mar 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Apr]
             WHEN Year = '2024' THEN [Apr] ELSE 0 END) AS [Apr 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [May]
             WHEN Year = '2024' THEN [May] ELSE 0 END) AS [May 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Jun]
             WHEN Year = '2024' THEN [Jun] ELSE 0 END) AS [Jun 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Jul]
             WHEN Year = '2024' THEN [Jul] ELSE 0 END) AS [Jul 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Aug]
             WHEN Year = '2024' THEN [Aug] ELSE 0 END) AS [Aug 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Sep]
             WHEN Year = '2024' THEN [Sep] ELSE 0 END) AS [Sep 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Oct]
             WHEN Year = '2024' THEN [Oct] ELSE 0 END) AS [Oct 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Nov]
             WHEN Year = '2024' THEN [Nov] ELSE 0 END) AS [Nov 2024],
    SUM(CASE WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Dec]
             WHEN Year = '2024' THEN [Dec] ELSE 0 END) AS [Dec 2024],
    SUM(CASE WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Jan]
             WHEN Year = '2025' THEN [Jan] ELSE 0 END) AS [Jan 2025],
    SUM(CASE WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Feb]
             WHEN Year = '2025' THEN [Feb] ELSE 0 END) AS [Feb 2025],
    SUM(CASE WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Mar]
             WHEN Year = '2025' THEN [Mar] ELSE 0 END) AS [Mar 2025],
    SUM(CASE WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Apr]
             WHEN Year = '2025' THEN [Apr] ELSE 0 END) AS [Apr 2025],
    SUM(CASE WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [May]
             WHEN Year = '2025' THEN [May] ELSE 0 END) AS [May 2025],
			 (
    SUM(
        CASE 
            WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Feb]
            WHEN Year = '2025' THEN [Feb]
            ELSE 0 
        END
    ) +
    SUM(
        CASE 
            WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Mar]
            WHEN Year = '2025' THEN [Mar]
            ELSE 0 
        END
    ) +
    SUM(
        CASE 
            WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Apr]
            WHEN Year = '2025' THEN [Apr]
            ELSE 0 
        END
    )
) / 3.0 AS [May 2025 T3],
(
    SUM(
        CASE 
            WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [May]
            WHEN Year = '2025' THEN [May]
            ELSE 0 
        END
    ) -
    (
        SUM(
            CASE 
                WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Feb]
                WHEN Year = '2025' THEN [Feb]
                ELSE 0 
            END
        ) +
        SUM(
            CASE 
                WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Mar]
                WHEN Year = '2025' THEN [Mar]
                ELSE 0 
            END
        ) +
        SUM(
            CASE 
                WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Apr]
                WHEN Year = '2025' THEN [Apr]
                ELSE 0 
            END
        )
    ) / 3.0
) AS [May 2025 Var],
(
    CASE 
        WHEN 
            SUM(
                CASE 
                    WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [May]
                    WHEN Year = '2025' THEN [May]
                    ELSE 0 
                END
            ) = 0 
        THEN 0
        ELSE
            (
                SUM(
                    CASE 
                        WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [May]
                        WHEN Year = '2025' THEN [May]
                        ELSE 0 
                    END
                ) -
                (
                    SUM(
                        CASE 
                            WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Feb]
                            WHEN Year = '2025' THEN [Feb]
                            ELSE 0 
                        END
                    ) +
                    SUM(
                        CASE 
                            WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Mar]
                            WHEN Year = '2025' THEN [Mar]
                            ELSE 0 
                        END
                    ) +
                    SUM(
                        CASE 
                            WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [Apr]
                            WHEN Year = '2025' THEN [Apr]
                            ELSE 0 
                        END
                    )
                ) / 3.0
            ) / NULLIF(
                SUM(
                    CASE 
                        WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - anesthesia', 'Bad debt expense - anesthesia') THEN -1 * [May]
                        WHEN Year = '2025' THEN [May]
                        ELSE 0 
                    END
                ),
                0
            )
    END
) AS [May 2025 Var%],
SUM(
    CASE 
        WHEN Element2_CaReportName IN ('A211-0000 Gross days in AR', 'Accounts receivable greater than 90 days') 
            THEN NULL
        WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') 
            THEN -1 * (Jan + Feb + Mar + Apr + May)
        WHEN Year = '2025' 
            THEN Jan + Feb + Mar + Apr + May
        ELSE NULL
    END
) AS [YTDMay2025Actual]
        ,SUM(
            CASE
                WHEN Element2_CaReportName IN ('A211-0000 Gross days in AR', 'Accounts receivable greater than 90 days') THEN NULL
                WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * (Jan + Feb + Mar + Apr + May)
                WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May
                ELSE NULL
            END
        ) AS YTDMay2025PY,
        CASE
    WHEN
        SUM(CASE WHEN Element2_CaReportName IN ('A211-0000 Gross days in AR', 'Accounts receivable greater than 90 days') THEN NULL
                 WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * (Jan + Feb + Mar + Apr + May)
                 WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May
                 ELSE NULL END) IS NULL
     OR
        SUM(CASE WHEN Element2_CaReportName IN ('A211-0000 Gross days in AR', 'Accounts receivable greater than 90 days') THEN NULL
                 WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * (Jan + Feb + Mar + Apr + May)
                 WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May
                 ELSE NULL END) IS NULL
    THEN NULL
    ELSE
        SUM(CASE WHEN Element2_CaReportName IN ('A211-0000 Gross days in AR', 'Accounts receivable greater than 90 days') THEN NULL
                 WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * (Jan + Feb + Mar + Apr + May)
                 WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May
                 ELSE NULL END)
        -
        SUM(CASE WHEN Element2_CaReportName IN ('A211-0000 Gross days in AR', 'Accounts receivable greater than 90 days') THEN NULL
                 WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * (Jan + Feb + Mar + Apr + May)
                 WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May
                 ELSE NULL END)
END AS YTDMay2025Var,
CASE
    WHEN
        SUM(CASE WHEN Element2_CaReportName IN ('A211-0000 Gross days in AR', 'Accounts receivable greater than 90 days') THEN NULL
                 WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * (Jan + Feb + Mar + Apr + May)
                 WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May
                 ELSE NULL END) IS NULL
     OR
        SUM(CASE WHEN Element2_CaReportName IN ('A211-0000 Gross days in AR', 'Accounts receivable greater than 90 days') THEN NULL
                 WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * (Jan + Feb + Mar + Apr + May)
                 WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May
                 ELSE NULL END) IS NULL
     OR
        ABS(SUM(CASE WHEN Element2_CaReportName IN ('A211-0000 Gross days in AR', 'Accounts receivable greater than 90 days') THEN NULL
                     WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * (Jan + Feb + Mar + Apr + May)
                     WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May
                     ELSE NULL END)) = 0
    THEN NULL
    ELSE
        (
            SUM(CASE WHEN Element2_CaReportName IN ('A211-0000 Gross days in AR', 'Accounts receivable greater than 90 days') THEN NULL
                     WHEN Year = '2025' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * (Jan + Feb + Mar + Apr + May)
                     WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May
                     ELSE NULL END)
            -
            SUM(CASE WHEN Element2_CaReportName IN ('A211-0000 Gross days in AR', 'Accounts receivable greater than 90 days') THEN NULL
                     WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * (Jan + Feb + Mar + Apr + May)
                     WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May
                     ELSE NULL END)
        )
        /
        ABS(SUM(CASE WHEN Element2_CaReportName IN ('A211-0000 Gross days in AR', 'Accounts receivable greater than 90 days') THEN NULL
                     WHEN Year = '2024' AND Element3 IN ('Contractual adjustments - facility', 'Bad debt expense - facility') THEN -1 * (Jan + Feb + Mar + Apr + May)
                     WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May
                     ELSE NULL END))
END AS YTDMay2025VarPct

FROM [CognosTesting].[dbo].[RawTestSet] r
INNER JOIN [CognosTesting].[dbo].[ReportingAccountHierarchy] rah
    ON r.accountnumber = rah.joincolumn
WHERE 
    rah.element1 = 'AR Reserve'
    AND AmountType = 'Actual'
    AND Year IN ('2024', '2025')
    AND CenterNumber NOT LIKE '2289%'
    AND Element2 <> 'Facility allowance'
    AND CenterNumber NOT LIKE 'M%'
    AND Element2 NOT LIKE '%facility%'
    AND Element2_CaReportName IN (
        'A211-0000 Gross days in AR','Collections, net of refunds',
        'Accounts receivable greater than 90 days','Collections per visit and procedure',
        'Gross charge per visit and procedure','Gross charges - anesthesia',
        'Net revenue - facility','Refunds - anesthesia',
        'Total accounts receivable aging', 'Total write-offs','Write-off percentage', 'S007 Anesthesia cases',
		'S006 Anesthesia base units'
    )
    AND AccountNumber NOT LIKE '%1202%'
GROUP BY Element2_CaReportName

UNION ALL

SELECT DISTINCT
    'Calculations: ' +
	Element3_CaReportName AS 'CAReportName',
    SUM(CASE WHEN Year = '2024' THEN [Mar] END) AS [Mar 2024],
    SUM(CASE WHEN Year = '2024' THEN [Apr] END) AS [Apr 2024],
    SUM(CASE WHEN Year = '2024' THEN [May] END) AS [May 2024],
    SUM(CASE WHEN Year = '2024' THEN [Jun] END) AS [Jun 2024],
    SUM(CASE WHEN Year = '2024' THEN [Jul] END) AS [Jul 2024],
    SUM(CASE WHEN Year = '2024' THEN [Aug] END) AS [Aug 2024],
    SUM(CASE WHEN Year = '2024' THEN [Sep] END) AS [Sep 2024],
    SUM(CASE WHEN Year = '2024' THEN [Oct] END) AS [Oct 2024],
    SUM(CASE WHEN Year = '2024' THEN [Nov] END) AS [Nov 2024],
    SUM(CASE WHEN Year = '2024' THEN [Dec] END) AS [Dec 2024],
    SUM(CASE WHEN Year = '2025' THEN [Jan] END) AS [Jan 2025],
    SUM(CASE WHEN Year = '2025' THEN [Feb] END) AS [Feb 2025],
    SUM(CASE WHEN Year = '2025' THEN [Mar] END) AS [Mar 2025],
    SUM(CASE WHEN Year = '2025' THEN [Apr] END) AS [Apr 2025],
    SUM(CASE WHEN Year = '2025' THEN [May] END) AS [May 2025],
	SUM(CASE WHEN Year = '2025' THEN (Apr + Mar + Feb) / 3.0 END ) AS [May 2025 T3],
	SUM(CASE WHEN Year = '2025' THEN (May - ((Apr + Mar + Feb) / 3.0)) END ) AS [May 2025 Var],
	SUM(CASE WHEN Year = '2025' AND May = 0 THEN 0
			 WHEN Year = '2025' THEN (May - ((Apr + Mar + Feb) / 3.0)) / NULLIF(May, 0) END ) AS [May 2025 Var%],
        SUM(Jan + Feb + Mar + Apr + May) AS YTDMay2025Actual,
        SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) AS YTDMay2025PY,
        CASE
            WHEN SUM(CASE WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May END) IS NULL
                 OR SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) IS NULL
            THEN NULL
            ELSE SUM(CASE WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May END) -
                 SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END)
        END AS YTDMay2025Var,
        CASE
            WHEN SUM(CASE WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May END) IS NULL
                 OR SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) IS NULL
                 OR ABS(SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END)) = 0
            THEN NULL
            ELSE (SUM(CASE WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May END) -
                  SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END)) /
                 ABS(SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END))
        END AS YTDMay2025VarPct

FROM [CognosTesting].[dbo].[RawTestSet] r
INNER JOIN [CognosTesting].[dbo].[ReportingAccountHierarchy] rah
    ON r.accountnumber = rah.joincolumn
WHERE 
    rah.element1 = 'AR Reserve'
    AND AmountType = 'Actual'
    AND Year IN ('2024', '2025')
    AND CenterNumber NOT LIKE '2289%'
    AND Element2 <> 'Facility allowance'
    AND CenterNumber NOT IN ('M313-001', 'M232-001')
    AND Element3_CaReportName NOT LIKE '%anesthesia%'
    AND Element2_CaReportName IN ('Total procedures', 'Gross Charges', 'Total implant revenue', 'Total billable drug revenue')
    AND AccountNumber NOT LIKE '%1202%'
GROUP BY Element3_CaReportName

UNION ALL

SELECT DISTINCT
    'Calculations: ' +
	Element3_CaReportName AS 'CAReportName',
    SUM(CASE WHEN Year = '2024' THEN [Mar] END) AS [Mar 2024],
    SUM(CASE WHEN Year = '2024' THEN [Apr] END) AS [Apr 2024],
    SUM(CASE WHEN Year = '2024' THEN [May] END) AS [May 2024],
    SUM(CASE WHEN Year = '2024' THEN [Jun] END) AS [Jun 2024],
    SUM(CASE WHEN Year = '2024' THEN [Jul] END) AS [Jul 2024],
    SUM(CASE WHEN Year = '2024' THEN [Aug] END) AS [Aug 2024],
    SUM(CASE WHEN Year = '2024' THEN [Sep] END) AS [Sep 2024],
    SUM(CASE WHEN Year = '2024' THEN [Oct] END) AS [Oct 2024],
    SUM(CASE WHEN Year = '2024' THEN [Nov] END) AS [Nov 2024],
    SUM(CASE WHEN Year = '2024' THEN [Dec] END) AS [Dec 2024],
    SUM(CASE WHEN Year = '2025' THEN [Jan] END) AS [Jan 2025],
    SUM(CASE WHEN Year = '2025' THEN [Feb] END) AS [Feb 2025],
    SUM(CASE WHEN Year = '2025' THEN [Mar] END) AS [Mar 2025],
    SUM(CASE WHEN Year = '2025' THEN [Apr] END) AS [Apr 2025],
    SUM(CASE WHEN Year = '2025' THEN [May] END) AS [May 2025],
	SUM(CASE WHEN Year = '2025' THEN (Apr + Mar + Feb) / 3.0 END ) AS [May 2025 T3],
        SUM(CASE WHEN Year = '2025' THEN (May - ((Apr + Mar + Feb) / 3.0)) END ) AS [May 2025 Var],
        SUM(CASE WHEN Year = '2025' AND May = 0 THEN 0
                         WHEN Year = '2025' THEN (May - ((Apr + Mar + Feb) / 3.0)) / NULLIF(May, 0) END ) AS [May 2025 Var%]
        ,SUM(Jan + Feb + Mar + Apr + May) AS YTDMay2025Actual,
        SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) AS YTDMay2025PY,
        CASE
            WHEN SUM(CASE WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May END) IS NULL
                 OR SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) IS NULL
            THEN NULL
            ELSE SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) -
                 SUM(CASE WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May END)
        END AS YTDMay2025Var,
        CASE
            WHEN SUM(CASE WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May END) IS NULL
                 OR SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) IS NULL
                 OR ABS(SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END)) = 0
            THEN NULL
            ELSE (SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) -
                  SUM(CASE WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May END)) /
                 ABS(SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END))
        END AS YTDMay2025VarPct
        ,SUM(Jan + Feb + Mar + Apr + May) AS YTDMay2025Actual,
        SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) AS YTDMay2025PY,
        CASE
            WHEN SUM(CASE WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May END) IS NULL
                 OR SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) IS NULL
            THEN NULL
            ELSE SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) -
                 SUM(CASE WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May END)
        END AS YTDMay2025Var,
        CASE
            WHEN SUM(CASE WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May END) IS NULL
                 OR SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) IS NULL
                 OR ABS(SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END)) = 0
            THEN NULL
            ELSE (SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) -
                  SUM(CASE WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May END)) /
                 ABS(SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END))
        END AS YTDMay2025VarPct
        ,SUM(Jan + Feb + Mar + Apr + May) AS YTDMay2025Actual,
        SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) AS YTDMay2025PY,
        CASE
            WHEN SUM(CASE WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May END) IS NULL
                 OR SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) IS NULL
            THEN NULL
            ELSE SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) -
                 SUM(CASE WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May END)
        END AS YTDMay2025Var,
        CASE
            WHEN SUM(CASE WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May END) IS NULL
                 OR SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) IS NULL
                 OR ABS(SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END)) = 0
            THEN NULL
            ELSE (SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) -
                  SUM(CASE WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May END)) /
                 ABS(SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END))
        END AS YTDMay2025VarPct
        ,SUM(Jan + Feb + Mar + Apr + May) AS YTDMay2025Actual,
        SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) AS YTDMay2025PY,
        CASE
            WHEN SUM(CASE WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May END) IS NULL
                 OR SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) IS NULL
            THEN NULL
            ELSE SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) -
                 SUM(CASE WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May END)
        END AS YTDMay2025Var,
        CASE
            WHEN SUM(CASE WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May END) IS NULL
                 OR SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) IS NULL
                 OR ABS(SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END)) = 0
            THEN NULL
            ELSE (SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) -
                  SUM(CASE WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May END)) /
                 ABS(SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END))
        END AS YTDMay2025VarPct
        ,SUM(Jan + Feb + Mar + Apr + May) AS YTDMay2025Actual,
        SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) AS YTDMay2025PY,
        CASE
            WHEN SUM(CASE WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May END) IS NULL
                 OR SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) IS NULL
            THEN NULL
            ELSE SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) -
                 SUM(CASE WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May END)
        END AS YTDMay2025Var,
        CASE
            WHEN SUM(CASE WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May END) IS NULL
                 OR SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) IS NULL
                 OR ABS(SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END)) = 0
            THEN NULL
            ELSE (SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END) -
                  SUM(CASE WHEN Year = '2025' THEN Jan + Feb + Mar + Apr + May END)) /
                 ABS(SUM(CASE WHEN Year = '2024' THEN Jan + Feb + Mar + Apr + May END))
        END AS YTDMay2025VarPct

FROM [CognosTesting].[dbo].[RawTestSet] r
INNER JOIN [CognosTesting].[dbo].[ReportingAccountHierarchy] rah
    ON r.accountnumber = rah.joincolumn
WHERE 
    rah.element1 = 'AR Reserve'
    AND AmountType = 'Actual'
    AND Year IN ('2024', '2025')
    AND CenterNumber NOT LIKE '2289%'
    AND Element2 <> 'Facility allowance'
    AND CenterNumber NOT IN ('M313-001', 'M232-001')
    AND Element3_CaReportName NOT LIKE '%anesthesia%'
    AND Element2_CaReportName ='Gross Charges', 'Total implant revenue', 'Total billable drug revenue')
    AND AccountNumber NOT LIKE '%1202%'
GROUP BY Element3_CaReportName

UNION ALL

SELECT DISTINCT
    'Calculations: ' +
	Element3_CaReportName AS 'CAReportName',
    SUM(CASE WHEN Year = '2024' THEN [Mar] END) AS [Mar 2024],
    SUM(CASE WHEN Year = '2024' THEN [Apr] END) AS [Apr 2024],
    SUM(CASE WHEN Year = '2024' THEN [May] END) AS [May 2024],
    SUM(CASE WHEN Year = '2024' THEN [Jun] END) AS [Jun 2024],
    SUM(CASE WHEN Year = '2024' THEN [Jul] END) AS [Jul 2024],
    SUM(CASE WHEN Year = '2024' THEN [Aug] END) AS [Aug 2024],
    SUM(CASE WHEN Year = '2024' THEN [Sep] END) AS [Sep 2024],
    SUM(CASE WHEN Year = '2024' THEN [Oct] END) AS [Oct 2024],
    SUM(CASE WHEN Year = '2024' THEN [Nov] END) AS [Nov 2024],
    SUM(CASE WHEN Year = '2024' THEN [Dec] END) AS [Dec 2024],
    SUM(CASE WHEN Year = '2025' THEN [Jan] END) AS [Jan 2025],
    SUM(CASE WHEN Year = '2025' THEN [Feb] END) AS [Feb 2025],
    SUM(CASE WHEN Year = '2025' THEN [Mar] END) AS [Mar 2025],
    SUM(CASE WHEN Year = '2025' THEN [Apr] END) AS [Apr 2025],
    SUM(CASE WHEN Year = '2025' THEN [May] END) AS [May 2025],
	SUM(CASE WHEN Year = '2025' THEN (Apr + Mar + Feb) / 3.0 END ) AS [May 2025 T3],
	SUM(CASE WHEN Year = '2025' THEN (May - ((Apr + Mar + Feb) / 3.0)) END ) AS [May 2025 Var],
	SUM(CASE WHEN Year = '2025' AND May = 0 THEN 0
			 WHEN Year = '2025' THEN (May - ((Apr + Mar + Feb) / 3.0)) / NULLIF(May, 0) END ) AS [May 2025 Var%]

FROM [CognosTesting].[dbo].[RawTestSet] r
INNER JOIN [CognosTesting].[dbo].[ReportingAccountHierarchy] rah
    ON r.accountnumber = rah.joincolumn
WHERE 
    rah.element1 = 'AR Reserve'
    AND AmountType = 'Actual'
    AND Year IN ('2024', '2025')
    AND CenterNumber NOT LIKE '2289%'
    AND Element2 <> 'Facility allowance'
    AND CenterNumber NOT IN ('M313-001', 'M232-001')
    AND Element3_CaReportName NOT LIKE '%anesthesia%'
    AND Element2_CaReportName ='Total implant revenue', 'Total billable drug revenue')
    AND AccountNumber NOT LIKE '%1202%'
GROUP BY Element3_CaReportName

UNION ALL

SELECT DISTINCT
    'Calculations: ' +
	Element3_CaReportName AS 'CAReportName',
    SUM(CASE WHEN Year = '2024' THEN [Mar] END) AS [Mar 2024],
    SUM(CASE WHEN Year = '2024' THEN [Apr] END) AS [Apr 2024],
    SUM(CASE WHEN Year = '2024' THEN [May] END) AS [May 2024],
    SUM(CASE WHEN Year = '2024' THEN [Jun] END) AS [Jun 2024],
    SUM(CASE WHEN Year = '2024' THEN [Jul] END) AS [Jul 2024],
    SUM(CASE WHEN Year = '2024' THEN [Aug] END) AS [Aug 2024],
    SUM(CASE WHEN Year = '2024' THEN [Sep] END) AS [Sep 2024],
    SUM(CASE WHEN Year = '2024' THEN [Oct] END) AS [Oct 2024],
    SUM(CASE WHEN Year = '2024' THEN [Nov] END) AS [Nov 2024],
    SUM(CASE WHEN Year = '2024' THEN [Dec] END) AS [Dec 2024],
    SUM(CASE WHEN Year = '2025' THEN [Jan] END) AS [Jan 2025],
    SUM(CASE WHEN Year = '2025' THEN [Feb] END) AS [Feb 2025],
    SUM(CASE WHEN Year = '2025' THEN [Mar] END) AS [Mar 2025],
    SUM(CASE WHEN Year = '2025' THEN [Apr] END) AS [Apr 2025],
    SUM(CASE WHEN Year = '2025' THEN [May] END) AS [May 2025],
	SUM(CASE WHEN Year = '2025' THEN (Apr + Mar + Feb) / 3.0 END ) AS [May 2025 T3],
	SUM(CASE WHEN Year = '2025' THEN (May - ((Apr + Mar + Feb) / 3.0)) END ) AS [May 2025 Var],
	SUM(CASE WHEN Year = '2025' AND May = 0 THEN 0
			 WHEN Year = '2025' THEN (May - ((Apr + Mar + Feb) / 3.0)) / NULLIF(May, 0) END ) AS [May 2025 Var%]

FROM [CognosTesting].[dbo].[RawTestSet] r
INNER JOIN [CognosTesting].[dbo].[ReportingAccountHierarchy] rah
    ON r.accountnumber = rah.joincolumn
WHERE 
    rah.element1 = 'AR Reserve'
    AND AmountType = 'Actual'
    AND Year IN ('2024', '2025')
    AND CenterNumber NOT LIKE '2289%'
    AND Element2 <> 'Facility allowance'
    AND CenterNumber NOT IN ('M313-001', 'M232-001')
    AND Element3_CaReportName NOT LIKE '%anesthesia%'
    AND Element2_CaReportName ='Total billable drug revenue'
    AND AccountNumber NOT LIKE '%1202%'
GROUP BY Element3_CaReportName
