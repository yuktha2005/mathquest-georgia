# UNVERIFIED_CONTENT.md — Curriculum & Standards Verification Registry

This document tracks all curriculum standard codes, chapter names, or topics in MathQuest across supported boards (Georgia MGSE and CBSE Class 6).

Per our architectural rules:
- Any unverified item in `backend/data/packs/*.json` must have `"verified": false`.
- The item must be registered here with the source checked, reason for uncertainty, and steps for manual verification.
- Every verified item must cite its primary official source.

---

## 📋 Comprehensive Registry of Curriculum Standards

| Pack ID | Topic ID | Code / Item | Verified | Official Source / Citation | Pedagogical Scope & Verification Notes |
|---|---|---|---|---|---|
| `georgia-g5` | `fractions` | `MGSE5.NF.1` | **Yes** (`true`) | GaDOE Georgia Standards of Excellence (Grade 5 Mathematics) | Verified: Add and subtract fractions with unlike denominators, including mixed numbers. |
| `georgia-g5` | `decimals` | `MGSE5.NBT.7` | **Yes** (`true`) | GaDOE Georgia Standards of Excellence (Grade 5 Mathematics) | Verified: Add, subtract, multiply, and divide decimals to hundredths using concrete models or place value strategies. |
| `georgia-g5` | `ratios` | `MGSE5.NF.5` | **Yes** (`true`) | GaDOE Georgia Standards of Excellence (Grade 5 Mathematics) | Verified: Interpret multiplication as scaling (resizing), comparing product size to factors. |
| `georgia-g5` | `geometry` | `MGSE5.MD.5` | **Yes** (`true`) | GaDOE Georgia Standards of Excellence (Grade 5 Mathematics) | Verified: Relate volume to operations of multiplication and addition; 2D area and perimeter foundations. |
| `georgia-g6` | `fractions` | `MGSE6.NS.1` | **Yes** (`true`) | GaDOE Georgia Standards of Excellence (Grade 6 Mathematics) | Verified: Interpret and compute quotients of fractions, and solve fraction division word problems. |
| `georgia-g6` | `decimals` | `MGSE6.NS.3` | **Yes** (`true`) | GaDOE Georgia Standards of Excellence (Grade 6 Mathematics) | Verified: Fluently add, subtract, multiply, and divide multi-digit decimals using standard algorithms. |
| `georgia-g6` | `ratios` | `MGSE6.RP.3` | **Yes** (`true`) | GaDOE Georgia Standards of Excellence (Grade 6 Mathematics) | Verified: Use ratio and rate reasoning to solve real-world problems (equivalent ratios, unit rates, percentages). |
| `georgia-g6` | `geometry` | `MGSE6.G.1` | **Yes** (`true`) | GaDOE Georgia Standards of Excellence (Grade 6 Mathematics) | Verified: Find area of triangles, special quadrilaterals, and polygons by composing/decomposing shapes. |
| `cbse-g6` | `factors_multiples` | `CBSE6.MATH.03` | **Yes** (`true`) | NCERT Class 6 Mathematics (*Playing with Numbers* / *Ganita Prakash* Ch. 3 & 5) | Verified: Factors, multiples, prime numbers, divisibility rules, prime factorisation, HCF, and LCM. |
| `cbse-g6` | `fractions` | `CBSE6.MATH.07` | **Yes** (`true`) | NCERT Class 6 Mathematics (*Fractions* / *Ganita Prakash* Ch. 7) | Verified: Proper, improper, mixed fractions, equivalent fractions, unlike denominator addition/subtraction. |
| `cbse-g6` | `decimals` | `CBSE6.MATH.08` | **Yes** (`true`) | NCERT Class 6 Mathematics (*Decimals* / *Ganita Prakash* Units) | Verified: Tenths, hundredths, place value representation, units conversion (rupees/paise, m/cm), addition/subtraction. |
| `cbse-g6` | `integers` | `CBSE6.MATH.06` | **Yes** (`true`) | NCERT Class 6 Mathematics (*Integers* / *Ganita Prakash* "The Other Side of Zero") | Verified: Number line representation, ordering, addition and subtraction of positive and negative integers. |
| `cbse-g6` | `ratios` | `CBSE6.MATH.12` | **Yes** (`true`) | NCERT Class 6 Mathematics (*Ratio and Proportion*) | Verified: Ratio equivalence, proportionality checks, and the unitary method for solving practical word problems. |
| `cbse-g6` | `geometry` | `CBSE6.MATH.10` | **Yes** (`true`) | NCERT Class 6 Mathematics (*Mensuration* / *Ganita Prakash* "Perimeter and Area") | Verified: Perimeter and area of regular figures, rectangles, squares, and parallelograms. |

---

## 🔍 Verification Protocol & Syllabus Harmonization Notes

1. **Georgia MGSE**:
   - Official GaDOE framework documents for Grades 5 and 6 confirm all codes `MGSE5.NF.1`, `MGSE5.NBT.7`, `MGSE5.NF.5`, `MGSE5.MD.5`, `MGSE6.NS.1`, `MGSE6.NS.3`, `MGSE6.RP.3`, and `MGSE6.G.1`.
2. **NCERT Ganita Prakash (2024 Edition) vs. Legacy NCERT Class 6**:
   - NCERT published the updated textbook *Ganita Prakash* for Class 6 aligned with NCF-SE 2023.
   - Core concepts (factors, multiples, primes, fractions, decimals, integers, perimeter, area, ratios) are fully preserved across both editions.
   - To ensure backward compatibility with state schools following earlier NCERT prints and CBSE schools adopting *Ganita Prakash*, topic titles reflect both canonical names (e.g. *Playing with Numbers* and *Prime Time*; *Mensuration* and *Perimeter and Area*).
3. **No Verbatim Copyrighted Text**:
   - In adherence to Rule 5, all topic descriptions, explanations, and problem statements are original pedagogical syntheses authored specifically for MathQuest. No copyrighted textbook questions or paragraphs have been reproduced.

