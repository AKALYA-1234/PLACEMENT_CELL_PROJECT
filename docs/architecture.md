# System Architecture & Core Concepts

## Overview

The Placement Management & Analytics Portal is designed to digest heterogeneous company placement spreadsheets, extract register numbers, normalize rounds, update student placement statuses, and serve real-time placement analytics to college administrators.

```
+-------------------------------------------------------------+
|                      ADMIN USER                             |
+-------------------------------------------------------------+
                              |
                              v
                      [ Admin Login ]
                              |
                              v
                     [ Upload Workbook ]
                              |
                              v
                 +--------------------------+
                 |    Excel Parser Module   |
                 | - Sheet Detection        |
                 | - Column Detection       |
                 | - Register No. Matcher   |
                 | - Stage Normalizer       |
                 +--------------------------+
                              |
                              v
                   [ Preview & Validation ]
                              |
                              v
                   [ Admin Confirmation ]
                              |
                              v
                 +--------------------------+
                 |  Transactional Database  |
                 |       (PostgreSQL)       |
                 +--------------------------+
                              |
                              v
                    [ Live Analytics ]
```

## Normalization Taxonomy

Every round in an Excel workbook is mapped to one of three categories:

1. `REGISTERED` — Initial registration or round 1 participation.
2. `PROGRESSION` — Movement to intermediate rounds (Aptitude, Technical, HR, Interview).
3. `PLACED` — Final selection or job offer. (Sheets named `OFFER`, `OFFERED`, `SELECTED`, `FINAL PLACED` map to `PLACED`).
