1️⃣ Health Check (Sanity Test)

Method: GET
URL:

http://localhost:8000/health


✅ Confirms the API is running.
{
    "status": "healthy",
    "timestamp": "2025-12-15T17:39:23.775022",
    "version": "1.0.0"
}

2️⃣ Create Lesson Plan

Method: POST
URL:

http://localhost:8000/api/lesson-plans


Body (JSON):

{
  "user_id": "test_user_1",
  "subject": "Math",
  "topic": "Algebra",
  "level": "GCSE",
  "auto_approve": false
}


📌 Save from response:

lesson_plan_id

subtopics[].id

{
    "lesson_plan_id": "e24ed82118ce7c8de5fcd4be4df716907febc67b1027bcdbfcdf9faef815120c",
    "subject": "Math",
    "topic": "Algebra",
    "status": "draft",
    "subtopics": [
        {
            "id": "958d4516429e99ddc2d98eb642861a28405da0f5048bd85cacc645ce5fc0276f",
            "title": "1. Algebraic Notation and Basic Manipulation",
            "order": 1,
            "duration": 45,
            "concepts": [
                "Variables, constants and coefficients",
                "Terms, expressions, equations and identities",
                "Like and unlike terms",
                "Using correct algebraic notation (e.g. 3x not x3, multiplication implied, powers)",
                "Substitution into expressions",
                "Collecting like terms",
                "Using the four operations with algebraic terms"
            ]
        },
        {
            "id": "248f483557a5a966adc65b963e3d9f6be43802479f88b8f6e5cafbaff19ade68",
            "title": "2. Expanding and Factorising Single Brackets",
            "order": 2,
            "duration": 45,
            "concepts": [
                "The distributive law: a(b + c) = ab + ac",
                "Expanding a single bracket with positive and negative terms",
                "Simplifying expressions after expansion",
                "Common factors in algebraic terms",
                "Factorising expressions with a common factor",
                "Checking factorisation by re-expansion"
            ]
        },
        {
            "id": "67f4a067d1fc1439cc7c65de34f2a195e5307481571e16fa3d8afc77f92ab89f",
            "title": "3. Expanding and Factorising Quadratics (Non-Complex Cases)",
            "order": 3,
            "duration": 45,
            "concepts": [
                "Quadratic expressions (ax² + bx + c)",
                "Expanding double brackets (x + a)(x + b)",
                "Recognising patterns: (x + a)(x + b) → x² + (a + b)x + ab",
                "Factorising quadratics of the form x² + bx + c",
                "Using factor pairs of c that sum to b",
                "Special products: (x + a)² and (x − a)(x + a)"
            ]
        },
        {
            "id": "59b2477b9db7e7b1ccfdc0e659fc27103601a8d2ef9658f57900470849470005",
            "title": "4. Solving Linear Equations in One Variable",
            "order": 4,
            "duration": 45,
            "concepts": [
                "Equation as a balance idea",
                "Inverse operations",
                "Solving one-step and two-step equations",
                "Solving equations with unknowns on both sides",
                "Dealing with brackets in equations",
                "Checking solutions by substitution"
            ]
        },
        {
            "id": "d5cabd86471753104501b1669bec8fc7953c47593860242b11030569e585d469",
            "title": "5. Forming and Solving Linear Equations from Problems",
            "order": 5,
            "duration": 45,
            "concepts": [
                "Translating word problems into algebraic equations",
                "Using a variable to represent an unknown quantity",
                "Setting up equations from number puzzles and real contexts",
                "Perimeter and other geometric problems leading to equations",
                "Solving and interpreting solutions in context"
            ]
        },
        {
            "id": "b9bf103c08696c8be2e9af525114146587e3289a43ad2113f93131d4edd614c1",
            "title": "6. Inequalities and Number Lines",
            "order": 6,
            "duration": 30,
            "concepts": [
                "Inequality symbols: <, >, ≤, ≥",
                "Writing inequalities from statements",
                "Representing inequalities on a number line",
                "Solving simple linear inequalities",
                "Understanding solution sets of inequalities",
                "Comparing equations and inequalities"
            ]
        },
        {
            "id": "55d1caf15024bf7bd28332861c919f84324b31c0c3bc65eedf433e89ffe7ae76",
            "title": "7. Algebraic Substitution and Rearranging Formulae",
            "order": 7,
            "duration": 45,
            "concepts": [
                "Substituting values into expressions and formulae",
                "Using correct order of operations (BIDMAS) in substitution",
                "Rearranging simple formulae to change the subject",
                "Inverse operations in rearranging",
                "Rearranging in geometric and physics-type formulae (e.g. v = u + at, A = lw)"
            ]
        },
        {
            "id": "c43f3be7a522fa3993802cb555e8726b947b4425341dfa3f08e7c09fdfe405bd",
            "title": "8. Simultaneous Linear Equations (Two Variables)",
            "order": 8,
            "duration": 45,
            "concepts": [
                "Simultaneous equations meaning and graphical interpretation",
                "Solution as the point of intersection of two lines",
                "Solving by substitution method",
                "Solving by elimination method (when coefficients align)",
                "Interpreting solutions in worded contexts"
            ]
        }
    ],
    "progress_initialized": false
}

3️⃣ Approve Lesson Plan

Method: POST
URL:

http://localhost:8000/api/lesson-plans/approve


Body (JSON):

{
  "user_id": "test_user_1",
  "plan_id": "e24ed82118ce7c8de5fcd4be4df716907febc67b1027bcdbfcdf9faef815120c"
}


✅ Progress tracking is now initialized.
{
    "status": "approved",
    "lesson_plan_id": "e24ed82118ce7c8de5fcd4be4df716907febc67b1027bcdbfcdf9faef815120c",
    "message": "Lesson plan approved and progress initialized"
}

4️⃣ Get All Lesson Plans for User

Method: GET
URL:

http://localhost:8000/api/lesson-plans/test_user_1


Useful to confirm plan state and subtopic count.

[
    {
        "id": "e24ed82118ce7c8de5fcd4be4df716907febc67b1027bcdbfcdf9faef815120c",
        "subject": "Math",
        "topic": "Algebra",
        "status": "approved",
        "subtopic_count": 8,
        "created_at": "2025-12-15T17:40:09.641883"
    }
]

5️⃣ Start a Lesson (Pick One Subtopic)

Method: POST
URL:

http://localhost:8000/api/lessons/start


Body (JSON):

{
  "user_id": "test_user_1",
  "lesson_plan_id": "e24ed82118ce7c8de5fcd4be4df716907febc67b1027bcdbfcdf9faef815120c",
  "subtopic_id": "248f483557a5a966adc65b963e3d9f6be43802479f88b8f6e5cafbaff19ade68"
}


📌 Save from response:

lesson_id

sections[].section_id

{
    "lesson_id": "c0d45ada24971da763edd2c2f6dcd005335fdb40073e5b3b51d7343948d4fe01",
    "subject": "Math",
    "topic": "Algebra",
    "subtopic": "2. Expanding and Factorising Single Brackets",
    "introduction": "In this lesson you will learn how to expand and factorise expressions with a single bracket, such as 3(x + 4) or 5y(2y − 7). These skills are essential for solving equations, working with functions, and preparing for more advanced algebra. We will use the distributive law to expand, then reverse the process to factorise. You will also practise working carefully with negative signs and checking your answers by re‑expanding.",
    "sections": [
        {
            "sectionId": "cff8fc14b68a5c25b782f9ad30ba88da9f2f1aaaa2a70aee7c929ddf870672d4",
            "title": "1. The Distributive Law and Expanding Single Brackets",
            "content": "### a) The distributive law\nThe distributive law tells us how multiplication works with brackets:\n\n**a(b + c) = ab + ac**\n\nThis means:\n- Multiply **a** by **b**\n- Multiply **a** by **c**\n- Then add the results\n\nIt can also work with subtraction:\n- **a(b − c) = ab − ac**\n\nThink of it like sharing: if 3 bags each contain (2 apples + 1 banana), then the total is 3×2 apples + 3×1 banana.\n\n### b) Expanding simple single brackets\nTo **expand** means to remove the brackets by multiplying.\n\n**Example 1**\nExpand: 3(x + 4)\n- Multiply 3 by x → 3x\n- Multiply 3 by 4 → 12\n- Answer: **3(x + 4) = 3x + 12**\n\n**Example 2**\nExpand: 5(y − 2)\n- 5 × y = 5y\n- 5 × (−2) = −10\n- Answer: **5(y − 2) = 5y − 10**\n\n### c) Expanding with different types of terms\nYou can expand when the bracket contains letters, numbers, or both.\n\n**Example 3**\nExpand: 2(3x + 5)\n- 2 × 3x = 6x\n- 2 × 5 = 10\n- Answer: **2(3x + 5) = 6x + 10**\n\n**Example 4**\nExpand: 4x(y + 3)\n- 4x × y = 4xy\n- 4x × 3 = 12x\n- Answer: **4x(y + 3) = 4xy + 12x**\n\n### d) Quick practice\nExpand these (don’t simplify yet):\n1) 6(a + 2)  \n2) 3(2x − 5)  \n3) 7m(n + 4)\n\n**Answers**\n1) 6a + 12  \n2) 6x − 15  \n3) 7mn + 28m",
            "keyPoints": [
                "Distributive law: a(b + c) = ab + ac",
                "To expand, multiply the outside term by each term inside the bracket",
                "Works with addition and subtraction inside the bracket",
                "Careful multiplication of numbers and letters is essential"
            ],
            "expanded": null
        },
        {
            "sectionId": "f7988933a85c2b2390fa0bdd4183e892e868b3ceea2820daefdcbe9badd5284c",
            "title": "2. Expanding with Negatives and Simplifying After Expansion",
            "content": "### a) Expanding with negative signs\nBe especially careful with minus signs. Remember:\n- **−k(b + c) = −kb − kc**\n- **−k(b − c) = −kb + kc** (the second term changes sign)\n\n**Example 1**\nExpand: −3(x + 5)\n- −3 × x = −3x\n- −3 × 5 = −15\n- Answer: **−3(x + 5) = −3x − 15**\n\n**Example 2**\nExpand: −2(4y − 3)\n- −2 × 4y = −8y\n- −2 × (−3) = +6  (negative × negative = positive)\n- Answer: **−2(4y − 3) = −8y + 6**\n\n### b) Expanding expressions with more complicated terms\nSometimes the outside number is also negative, or includes a letter.\n\n**Example 3**\nExpand: −5x(2x + 1)\n- −5x × 2x = −10x²\n- −5x × 1 = −5x\n- Answer: **−5x(2x + 1) = −10x² − 5x**\n\n**Example 4**\nExpand: −4a(b − 3)\n- −4a × b = −4ab\n- −4a × (−3) = +12a\n- Answer: **−4a(b − 3) = −4ab + 12a**\n\n### c) Simplifying after expansion\nAfter expanding, you should **simplify** by collecting like terms (terms with the same letter pattern and power).\n\n**Example 5**\nSimplify: 3(x + 4) + 2x\n1) Expand 3(x + 4): 3x + 12\n2) Now the expression is 3x + 12 + 2x\n3) Collect like terms: 3x + 2x = 5x\n4) Final answer: **5x + 12**\n\n**Example 6**\nSimplify: 2(3y − 1) − y\n1) Expand: 2 × 3y = 6y, 2 × (−1) = −2 → 6y − 2\n2) Expression becomes: 6y − 2 − y\n3) Collect like terms: 6y − y = 5y\n4) Final answer: **5y − 2**\n\n### d) Common mistakes to avoid\n- Forgetting to multiply **both** terms inside the bracket.\n- Getting the sign wrong when multiplying by a negative.\n- Not simplifying at the end.\n\n### e) Quick practice\nSimplify fully:\n1) 4(p − 3) + p  \n2) −2(3x + 1) + x  \n3) 5(y − 2) − 3y\n\n**Answers**\n1) 4p − 12 + p = **5p − 12**  \n2) −6x − 2 + x = **−5x − 2**  \n3) 5y − 10 − 3y = **2y − 10**",
            "keyPoints": [
                "Negative signs must be handled carefully when expanding",
                "Multiply the outside term by every term inside the bracket, including signs",
                "After expansion, collect like terms to simplify",
                "Check signs particularly when multiplying by a negative number"
            ],
            "expanded": null
        },
        {
            "sectionId": "ab15a0b5fd0ca30cd367408ffbafe949d44ea22233eb199f7455ab2cb2f5e9d4",
            "title": "3. Common Factors in Algebraic Terms",
            "content": "Before we factorise, we need to understand **common factors**.\n\n### a) What is a factor?\nA **factor** of a number or term is something that divides it exactly.\n\n- Factors of 12: 1, 2, 3, 4, 6, 12\n- Factors of 6x: 1, 2, 3, 6, x, 2x, 3x, 6x\n\nA **common factor** is a factor shared by all the terms.\n\n**Example 1**\nFind a common factor of 6x and 9x.\n- Factors of 6x: 1, 2, 3, 6, x, 2x, 3x, 6x\n- Factors of 9x: 1, 3, 9, x, 3x, 9x\nCommon factors: 1, 3, x, 3x  \nA highest common factor is **3x**.\n\n### b) Finding common factors in algebra\nLook at:\n- The **numbers** (coefficients)\n- The **letters** and their powers\n\n**Example 2**\nFind the HCF of 8a and 12ab.\n- 8a = 2 × 2 × 2 × a\n- 12ab = 2 × 2 × 3 × a × b\nCommon factors: 2 × 2 × a = 4a  \nHCF = **4a**\n\n**Example 3**\nFind the HCF of 5x² and 15x.\n- Numbers: HCF of 5 and 15 is 5\n- Letters: x² and x → both have at least one x → x\nHCF = **5x**\n\n### c) Quick practice\nFind the highest common factor (HCF):\n1) 4y and 10y  \n2) 9a² and 6a  \n3) 14xy and 21x\n\n**Answers**\n1) 2y  \n2) 3a  \n3) 7x",
            "keyPoints": [
                "A factor divides a term exactly",
                "A common factor is shared by all terms",
                "To find the HCF, look at both numbers and letters",
                "You need the HCF to factorise expressions with a single bracket"
            ],
            "expanded": null
        },
        {
            "sectionId": "f5d9145926aa5f6ff94250ffff2af29fb74e15f196f4761d0b57da7b159e35e7",
            "title": "4. Factorising Single Brackets and Checking by Expansion",
            "content": "### a) What does factorising mean?\nTo **factorise** is to write an expression as a product (multiplication) of factors.  \nFor single brackets, this is the **reverse** of expanding.\n\n- Expanding: 3(x + 2) → 3x + 6  \n- Factorising: 3x + 6 → 3(x + 2)\n\n### b) Factorising with a common factor\nSteps to factorise an expression like 6x + 9:\n1) Find the HCF of the terms.  \n2) Write the HCF outside the bracket.  \n3) Work out what to put inside the bracket by dividing each term by the HCF.\n\n**Example 1**\nFactorise: 6x + 9\n1) HCF of 6x and 9 is 3\n2) Put 3 outside: 3(    )\n3) Divide each term by 3: 6x ÷ 3 = 2x, 9 ÷ 3 = 3\n4) Answer: **3(2x + 3)**\n\n**Example 2**\nFactorise: 8y − 4\n1) HCF of 8y and 4 is 4\n2) 4(    )\n3) 8y ÷ 4 = 2y, 4 ÷ 4 = 1\n4) Answer: **4(2y − 1)**\n\n### c) Factorising with letters\n**Example 3**\nFactorise: 5x² + 10x\n1) HCF of 5x² and 10x is 5x\n2) 5x(    )\n3) 5x² ÷ 5x = x, 10x ÷ 5x = 2\n4) Answer: **5x(x + 2)**\n\n**Example 4**\nFactorise: 9ab + 3a\n1) HCF of 9ab and 3a is 3a\n2) 3a(    )\n3) 9ab ÷ 3a = 3b, 3a ÷ 3a = 1\n4) Answer: **3a(3b + 1)**\n\n### d) Factorising with negative terms\nOften we choose to factor out a **positive** HCF, but sometimes it’s useful to factor out a **negative**.\n\n**Example 5**\nFactorise: −2x + 6\nOption 1: factor out **2**  \n1) HCF of −2x and 6 is 2\n2) 2(    )\n3) −2x ÷ 2 = −x, 6 ÷ 2 = 3\n4) Answer: **2(−x + 3)**\n\nOption 2: factor out **−2** (often neater)  \n1) HCF (including sign) is −2\n2) −2(    )\n3) −2x ÷ (−2) = x, 6 ÷ (−2) = −3\n4) Answer: **−2(x − 3)**\n\nBoth are correct, but **−2(x − 3)** usually looks nicer.\n\n**Example 6**\nFactorise: 4y − 12\n1) HCF is 4\n2) 4(    )\n3) 4y ÷ 4 = y, 12 ÷ 4 = 3\n4) Answer: **4(y − 3)**\n\n### e) Checking factorisation by re-expansion\nYou can always check your factorised answer by expanding it again:\n\n**Example 7**\nCheck: 5x(x − 4)\n- Expand: 5x × x = 5x², 5x × (−4) = −20x\n- Result: 5x² − 20x  \nSo factorisation is correct.\n\n**Example 8**\nFactorise and check: 7a + 14\n1) Factorise: HCF is 7 → 7(a + 2)\n2) Check: 7(a + 2) = 7a + 14 ✓\n\n### f) Quick practice\nFactorise fully:\n1) 10x + 5  \n2) 6y − 9y²  \n3) 12ab − 4a  \n4) −3x − 9\n\n**Answers**\n1) 5(2x + 1)  \n2) 3y(2 − 3y)  \n3) 4a(3b − 1)  \n4) −3(x + 3)",
            "keyPoints": [
                "Factorising is the reverse of expanding",
                "To factorise, find the highest common factor and put it outside a bracket",
                "Divide each term by the HCF to find what goes inside the bracket",
                "You can include a negative sign in the common factor to make the bracket neater",
                "Always check factorisation by re-expanding to see if you get the original expression"
            ],
            "expanded": null
        }
    ],
    "summary": "You have learned how to use the distributive law to expand single brackets, including those with negative signs, and then simplify expressions by collecting like terms. You practised finding common factors in algebraic terms and used them to factorise expressions, which is the reverse process of expanding. Finally, you saw how to check your factorised expressions by re-expanding them to ensure they match the original expression. These skills are a core part of GCSE algebra and are used often in solving equations and manipulating formulas.",
    "key_terms": [
        "Distributive law",
        "Expand",
        "Factorise",
        "Single bracket",
        "Common factor",
        "Highest common factor (HCF)",
        "Coefficient",
        "Like terms",
        "Negative sign",
        "Re-expansion"
    ],
    "status": "active"
}

6️⃣ Expand a Lesson Section

Method: POST
URL:

http://localhost:8000/api/lessons/expand-section


Body (JSON):

{
  "user_id": "test_user_1",
  "lesson_id": "c0d45ada24971da763edd2c2f6dcd005335fdb40073e5b3b51d7343948d4fe01",
  "section_id": "f7988933a85c2b2390fa0bdd4183e892e868b3ceea2820daefdcbe9badd5284c"
}


✅ Returns expanded explanation for that section only.
{
    "section_id": "f7988933a85c2b2390fa0bdd4183e892e868b3ceea2820daefdcbe9badd5284c",
    "expanded_content": "## 2. Expanding with Negatives and Simplifying After Expansion\n\nWhen you expand brackets, you’re distributing the number (or letter) outside the bracket to **every term inside**. When negatives are involved, the main challenge is keeping track of the signs.\n\n---\n\n### a) Expanding with negative signs\n\nThink of a minus sign as “the opposite of.”  \nSo:\n\n- **−k(b + c)** means “the opposite of (k(b + c))”\n- **−k(b − c)** means “the opposite of (k(b − c))”\n\nAlgebraically:\n\n- **−k(b + c) = −kb − kc**\n- **−k(b − c) = −kb + kc**\n\nNotice in the second one, the sign of the second term changes.\n\n#### Why does the sign change?\n\nStart with:\n\n- \\( k(b - c) = kb - kc \\)\n\nNow take the opposite (multiply everything by −1):\n\n- \\( -k(b - c) = -(kb - kc) \\)\n\nDistribute the negative sign:\n\n- \\( -(kb - kc) = -kb + kc \\)\n\nSo the minus in front of the bracket flips the signs of **every** term inside.\n\n---\n\n#### Example 1: Negative times a sum\n\nExpand:  \n\\[\n-3(x + 5)\n\\]\n\nStep-by-step:\n\n1. Distribute −3 to each term inside the bracket:\n   - −3 × x = −3x  \n   - −3 × 5 = −15\n2. Put the results together:\n   - −3x − 15\n\n**Answer:**  \n\\[\n-3(x + 5) = -3x - 15\n\\]\n\n---\n\n#### Example 2: Negative times a difference\n\nExpand:  \n\\[\n-2(4y - 3)\n\\]\n\nStep-by-step:\n\n1. Distribute −2:\n   - −2 × 4y = −8y  \n   - −2 × (−3) = +6  (negative × negative = positive)\n2. Combine:\n   - −8y + 6\n\n**Answer:**  \n\\[\n-2(4y - 3) = -8y + 6\n\\]\n\n---\n\n#### Extra Example 1: Minus sign in front of a bracket\n\nExpand:  \n\\[\n-(x - 7)\n\\]\n\nYou can think of this as −1 × (x − 7).\n\n1. Multiply each term by −1:\n   - −1 × x = −x  \n   - −1 × (−7) = +7\n2. Combine:\n   - −x + 7\n\n**Answer:**  \n\\[\n-(x - 7) = -x + 7\n\\]\n\n---\n\n#### Extra Example 2: Plus and minus together\n\nExpand:  \n\\[\n5 - 2(x + 3)\n\\]\n\nHere, only the **−2** is multiplied by the bracket. The 5 is separate.\n\n1. Expand −2(x + 3):\n   - −2 × x = −2x  \n   - −2 × 3 = −6  \n   So −2(x + 3) = −2x − 6\n2. Now rewrite the expression:\n   - 5 − 2(x + 3) = 5 + (−2x − 6)\n   - = 5 − 2x − 6\n3. Simplify (combine numbers):\n   - 5 − 6 = −1  \n   So: −2x − 1\n\n**Answer:**  \n\\[\n5 - 2(x + 3) = -2x - 1\n\\]\n\n---\n\n### b) Expanding expressions with more complicated terms\n\nSometimes the number outside the bracket is not just a number; it can be:\n\n- Negative\n- A letter (like x, a, k)\n- A combination (like −5x, 3ab, etc.)\n\nThe rule is the same: **multiply the outside term by each term inside the bracket**.\n\n---\n\n#### Example 3: Negative with a variable outside\n\nExpand:  \n\\[\n-5x(2x + 1)\n\\]\n\nStep-by-step:\n\n1. Multiply −5x by 2x:\n   - −5x × 2x = −10x²  \n     (5 × 2 = 10, and x × x = x²)\n2. Multiply −5x by 1:\n   - −5x × 1 = −5x\n3. Combine:\n   - −10x² − 5x\n\n**Answer:**  \n\\[\n-5x(2x + 1) = -10x^2 - 5x\n\\]\n\n---\n\n#### Example 4: Negative letter outside with a difference inside\n\nExpand:  \n\\[\n-4a(b - 3)\n\\]\n\nStep-by-step:\n\n1. Multiply −4a by b:\n   - −4a × b = −4ab\n2. Multiply −4a by −3:\n   - −4a × (−3) = +12a  (negative × negative = positive)\n3. Combine:\n   - −4ab + 12a\n\n**Answer:**  \n\\[\n-4a(b - 3) = -4ab + 12a\n\\]\n\n---\n\n#### Extra Example 3: Two variables outside\n\nExpand:  \n\\[\n3m(2n - 5)\n\\]\n\n1. Multiply 3m by 2n:\n   - 3m × 2n = 6mn\n2. Multiply 3m by −5:\n   - 3m × (−5) = −15m\n3. Combine:\n   - 6mn − 15m\n\n**Answer:**  \n\\[\n3m(2n - 5) = 6mn - 15m\n\\]\n\n---\n\n#### Extra Example 4: Negative variable outside, both terms inside negative/positive\n\nExpand:  \n\\[\n-2k(3k - 4)\n\\]\n\n1. Multiply −2k by 3k:\n   - −2k × 3k = −6k²\n2. Multiply −2k by −4:\n   - −2k × (−4) = +8k\n3. Combine:\n   - −6k² + 8k\n\n**Answer:**  \n\\[\n-2k(3k - 4) = -6k^2 + 8k\n\\]\n\n---\n\n### c) Simplifying after expansion\n\nAfter expanding, your expression might have several terms. You should **simplify** it by:\n\n1. **Collecting like terms**  \n   Like terms have:\n   - The same letters\n   - The same powers  \n   Examples:\n   - 3x and −5x are like terms\n   - 2y² and 7y² are like terms\n   - 4ab and −ab are like terms  \n   But:\n   - x and x² are **not** like terms\n   - y and y² are **not** like terms\n\n2. **Adding or subtracting the coefficients** of like terms.\n\n---\n\n#### Example 5\n\nSimplify:  \n\\[\n3(x + 4) + 2x\n\\]\n\n1. Expand 3(x + 4):\n   - 3 × x = 3x  \n   - 3 × 4 = 12  \n   So 3(x + 4) = 3x + 12\n2. Rewrite the whole expression:\n   - 3x + 12 + 2x\n3. Collect like terms (3x and 2x):\n   - 3x + 2x = 5x\n4. Final answer:\n   - 5x + 12\n\n**Answer:**  \n\\[\n3(x + 4) + 2x = 5x + 12\n\\]\n\n---\n\n#### Example 6\n\nSimplify:  \n\\[\n2(3y - 1) - y\n\\]\n\n1. Expand 2(3y − 1):\n   - 2 × 3y = 6y  \n   - 2 × (−1) = −2  \n   So 2(3y − 1) = 6y − 2\n2. Rewrite the expression:\n   - 6y − 2 − y\n3. Collect like terms (6y and −y):\n   - 6y − y = 5y\n4. Final answer:\n   - 5y − 2\n\n**Answer:**  \n\\[\n2(3y - 1) - y = 5y - 2\n\\]\n\n---\n\n#### Extra Example 5: Negative outside and like terms inside\n\nSimplify:  \n\\[\n-4(x - 2) + 3x\n\\]\n\n1. Expand −4(x − 2):\n   - −4 × x = −4x  \n   - −4 × (−2) = +8  \n   So −4(x − 2) = −4x + 8\n2. Rewrite the expression:\n   - −4x + 8 + 3x\n3. Collect like terms (−4x and +3x):\n   - −4x + 3x = −x\n4. Final answer:\n   - −x + 8\n\n**Answer:**  \n\\[\n-4(x - 2) + 3x = -x + 8\n\\]\n\n---\n\n#### Extra Example 6: Two brackets and a negative\n\nSimplify:  \n\\[\n5(y - 1) - 2(y + 3)\n\\]\n\n1. Expand 5(y − 1):\n   - 5 × y = 5y  \n   - 5 × (−1) = −5  \n   So 5(y − 1) = 5y − 5\n2. Expand −2(y + 3):\n   - −2 × y = −2y  \n   - −2 × 3 = −6  \n   So −2(y + 3) = −2y − 6\n3. Combine all terms:\n   - 5y − 5 − 2y − 6\n4. Collect like terms:\n   - 5y − 2y = 3y  \n   - −5 − 6 = −11\n5. Final answer:\n   - 3y − 11\n\n**Answer:**  \n\\[\n5(y - 1) - 2(y + 3) = 3y - 11\n\\]\n\n---\n\n### d) Common mistakes to avoid\n\n1. **Forgetting to multiply every term inside the bracket**\n\n   Incorrect:\n   - −3(x + 4) = −3x + 4  ✗  \n   (Only x was multiplied by −3; the 4 was left alone.)\n\n   Correct:\n   - −3(x + 4) = −3x − 12 ✓  \n   (Both x and 4 were multiplied by −3.)\n\n2. **Getting the sign wrong when multiplying by a negative**\n\n   Remember:\n   - positive × positive = positive\n   - positive × negative = negative\n   - negative × positive = negative\n   - negative × negative = positive\n\n   Example:\n   - −2(5 − 3)  \n     −2 × 5 = −10  \n     −2 × (−3) = +6  \n     So −10 + 6 = −4\n\n3. **Not simplifying at the end**\n\n   If you stop at:\n   - 3x + 2x + 5  \n\n   You haven’t finished. Combine like terms:\n   - 3x + 2x = 5x  \n   Final: 5x + 5\n\n4. **Dropping the minus sign in front of a bracket**\n\n   Example:\n   - −(x − 2) is **not** the same as x − 2  \n   Instead:\n   - −(x − 2) = −x + 2\n\n---\n\n### e) Real-world analogies\n\n1. **Money / debt**\n\n   Think of negatives as debts:\n\n   - x = £x you have  \n   - −x = £x you owe\n\n   If you have −2(x + 5), you’re saying:\n   - “I owe 2 times everything in (x + 5).”  \n   So you owe 2x and you owe 10: −2x − 10.\n\n2. **Temperature change**\n\n   Suppose:\n   - x = current temperature  \n   - (x + 3) = temperature after rising 3 degrees\n\n   Then −2(x + 3) could represent “twice the *drop* from that warmer temperature,” leading to negative values (colder).\n\n3. **Reversing direction**\n\n   A minus sign can mean “reverse direction”:\n\n   - If (b − c) is “go forward b, then back c,”  \n   - Then −(b − c) is “reverse that whole journey,”  \n     so you go back b, then forward c → −b + c.\n\n---\n\n### f) Quick practice\n\nSimplify fully:\n\n1) \\(4(p - 3) + p\\)  \n2) \\(-2(3x + 1) + x\\)  \n3) \\(5(y - 2) - 3y\\)\n\n**Step-by-step:**\n\n1) \\(4(p - 3) + p\\)  \n   - 4 × p = 4p  \n   - 4 × (−3) = −12 → 4p − 12  \n   - Now: 4p − 12 + p = (4p + p) − 12 = 5p − 12  \n   **Answer:** 5p − 12\n\n2) \\(-2(3x + 1) + x\\)  \n   - −2 × 3x = −6x  \n   - −2 × 1 = −2 → −6x − 2  \n   - Now: −6x − 2 + x = (−6x + x) − 2 = −5x − 2  \n   **Answer:** −5x − 2\n\n3) \\(5(y - 2) - 3y\\)  \n   - 5 × y = 5y  \n   - 5 × (−2) = −10 → 5y − 10  \n   - Now: 5y − 10 − 3y = (5y − 3y) − 10 = 2y − 10  \n   **Answer:** 2y − 10\n\n---\n\nIf you’d like, I can give you a short “sign rules checklist” or more practice problems with mixed positives and negatives."
}

7️⃣ Complete Lesson

Method: POST
URL:

http://localhost:8000/api/lessons/complete


Body (JSON):

{
  "user_id": "test_user_1",
  "lesson_id": "PASTE_LESSON_ID_HERE",
  "study_time": 20
}

response:
{
    "lesson_completed": true,
    "next_action": "quiz",
    "progress": {
        "percentComplete": 0,
        "totalStudyTime": 20
    }
}

📌 Look for next_action → usually "quiz"

8️⃣ Start Quiz

Method: POST
URL:

http://localhost:8000/api/quizzes/start


Body (JSON):

{
  "user_id": "test_user_1",
  "lesson_id": "c0d45ada24971da763edd2c2f6dcd005335fdb40073e5b3b51d7343948d4fe01",
  "subtopic_id": "248f483557a5a966adc65b963e3d9f6be43802479f88b8f6e5cafbaff19ade68",
  "difficulty": "mixed",
  "question_count": 3
}


📌 Save from response:

quiz_id

questions[].question_id

{
    "quiz_id": "8acc16d9-9e90-4356-aa81-b779c96ce830",
    "questions": [
        {
            "questionId": "q1",
            "type": "multiple_choice",
            "question": "Which expression is the correct expansion of −3(2x − 5)?",
            "options": [
                "−6x − 15",
                "−6x + 15",
                "6x − 15",
                "6x + 15"
            ],
            "difficulty": "medium"
        },
        {
            "questionId": "q2",
            "type": "short_answer",
            "question": "Factorise fully: 9x² + 6x",
            "options": null,
            "difficulty": "medium"
        },
        {
            "questionId": "q3",
            "type": "long_answer",
            "question": "Explain how you would simplify the expression 4(2y − 3) + 5y. Show your working and give the final answer in its simplest form.",
            "options": null,
            "difficulty": "hard"
        }
    ],
    "total_questions": 3
}

9️⃣ Submit Quiz (Mixed Answer Types)

Method: POST
URL:

http://localhost:8000/api/quizzes/submit


Body (JSON):

{
  "user_id": "test_user_1",
  "quiz_id": "8acc16d9-9e90-4356-aa81-b779c96ce830",
  "responses": [
    {
      "questionId": "q1",
      "userAnswer": "4xy and −7xy"
    },
    {
      "questionId": "q2",
      "userAnswer": "3(2x − 5) = 6x − 15"
    },
    {
      "questionId": "q3",
      "userBulletPoints": [
        "Represent unknown values",
        "3(x + 2) = 3x + 6” or “2(x − 5) = 2x − 10",
        "Used in expressions"
      ]
    }
  ]
}


📌 Watch for:

score.percentage

trigger_tutor

{
    "attempt_id": "3b2e3636-e5cd-4157-973e-50fbc737823b",
    "score": {
        "percentage": 31.25,
        "marksAwarded": 5,
        "maxMarks": 16
    },
    "responses": [
        {
            "questionId": "q1",
            "isCorrect": false,
            "marksAwarded": 0.0,
            "maxMarks": 1.0,
            "feedback": "The correct answer is −6x + 15",
            "aiGeneratedAnswer": null
        },
        {
            "questionId": "q2",
            "isCorrect": null,
            "marksAwarded": 0.0,
            "maxMarks": 3.0,
            "feedback": "You haven’t yet factorised the expression 9x² + 6x.\n\nWhat you did:\n- You wrote 3(2x − 5) = 6x − 15. This is correct algebra in itself (it does expand to 6x − 15), but it has nothing to do with the original expression 9x² + 6x.\n\nWhat was needed for the marks:\n1. First, spot the highest common factor of 9x² and 6x, which is **3x**. That would earn 1 mark.\n2. Then write 9x² + 6x = 3x(3x + 2). The bracket **(3x + 2)** would earn the second mark.\n3. Any equivalent factorisation (like (3x + 2)·3x) that expands back to 9x² + 6x is acceptable.\n\nTo improve, always start by looking for a common factor in all terms (numbers and variables), factor it out, and check by expanding that you get back to the original expression.",
            "aiGeneratedAnswer": null
        },
        {
            "questionId": "q3",
            "isCorrect": null,
            "marksAwarded": 5.0,
            "maxMarks": 12.0,
            "feedback": "Marks: 5/5.\n\n• Method – 2 marks\n  - Correctly expanded 4(2y − 3) to 8y − 12. (1 mark)\n  - Correctly wrote the full expression after expansion as 8y − 12 + 5y. (1 mark)\n\n• Simplifying – 2 marks\n  - Correctly collected like terms: 8y + 5y = 13y. (1 mark)\n  - Correct final simplified expression: 13y − 12. (1 mark)\n\n• Explanation/communication – 1 mark\n  - Very clear explanation using the distributive property and then collecting like terms, with well-structured working. (1 mark)\n\nFeedback:\nYour answer is complete, clear, and fully correct. You showed each step: expanding the bracket accurately, writing the full expression, collecting the like terms correctly, and presenting the final answer in simplest form. Your explanation of the distributive property and the examples you gave show strong understanding and excellent communication. Nothing is missing or incorrect for the marks available.",
            "aiGeneratedAnswer": "To simplify the expression \\(4(2y - 3) + 5y\\), start by expanding the brackets using the distributive property. This means you multiply the number outside the bracket by each term inside the bracket, just as in examples like \\(3(x + 2) = 3x + 6\\) or \\(2(x - 5) = 2x - 10\\).\n\nSo:\n\\[\n4(2y - 3) + 5y = 4 \\cdot 2y - 4 \\cdot 3 + 5y = 8y - 12 + 5y\n\\]\n\nNow collect like terms. The terms \\(8y\\) and \\(5y\\) both involve the unknown \\(y\\), so add them:\n\\[\n8y + 5y = 13y\n\\]\n\nSo the expression becomes:\n\\[\n13y - 12\n\\]\n\nFinal answer in simplest form: \\(\\boxed{13y - 12}\\)."
        }
    ],
    "mastery_level": "beginner",
    "next_action": "tutor",
    "trigger_tutor": true,
    "weak_concepts": [
        "Which expression is the correct expansion of −3(2x",
        "Factorise fully: 9x² + 6x",
        "Explain how you would simplify the expression 4(2y"
    ]
}

🔟 Start Tutor Session (Optional)

Method: POST
URL:

http://localhost:8000/api/tutor/start


Body (JSON):

{
  "user_id": "test_user_1",
  "trigger": "manual",
  "lesson_id": "c0d45ada24971da763edd2c2f6dcd005335fdb40073e5b3b51d7343948d4fe01",
  "concept": "variables",
  "initial_message": "I'm still confused about variables"
}


📌 Save session_id

{
    "session_id": "e601f0c6-07b5-47c7-ae64-748cf7056563",
    "message": "",
    "context": {
        "lessonId": "c0d45ada24971da763edd2c2f6dcd005335fdb40073e5b3b51d7343948d4fe01",
        "subtopicId": null,
        "questionId": null,
        "concept": "variables"
    }
}

1️⃣1️⃣ Send Message to Tutor

Method: POST
URL:

http://localhost:8000/api/tutor/message


Body (JSON):

{
  "user_id": "test_user_1",
  "session_id": "e601f0c6-07b5-47c7-ae64-748cf7056563",
  "message": "Can you give me a simple example?"
}

1️⃣2️⃣ End Tutor Session

Method: POST
URL:

http://localhost:8000/api/tutor/end/test_user_1/e601f0c6-07b5-47c7-ae64-748cf7056563

{
    "status": "resolved",
    "session_id": "e601f0c6-07b5-47c7-ae64-748cf7056563",
    "message": "Tutor session ended successfully"
}

1️⃣3️⃣ View Dashboard

Method: GET
URL:

http://localhost:8000/api/dashboard/test_user_1


Shows:

Overall progress

Lesson plans

Recommendations

{
    "user": {
        "totalStudyTime": 20,
        "overallProgress": 0.0,
        "averageScore": 31.25
    },
    "lesson_plans": [
        {
            "id": "e24ed82118ce7c8de5fcd4be4df716907febc67b1027bcdbfcdf9faef815120c",
            "subject": "Math",
            "topic": "Algebra",
            "status": "approved",
            "subtopicCount": 8,
            "progress": {
                "lessonPlanId": "e24ed82118ce7c8de5fcd4be4df716907febc67b1027bcdbfcdf9faef815120c",
                "subject": "Math",
                "topic": "Algebra",
                "percentComplete": 0,
                "averageScore": 31.25,
                "totalSubtopics": 8,
                "completedSubtopics": 0
            }
        }
    ],
    "active_tutor_sessions": 4,
    "recommendations": [
        "Continue Math - Algebra (0% complete)",
        "Review Math - Algebra (average score: 31%)"
    ]
}

1️⃣4️⃣ View Lesson Plan Progress

Method: GET
URL:

http://localhost:8000/api/progress/test_user_1/e24ed82118ce7c8de5fcd4be4df716907febc67b1027bcdbfcdf9faef815120c

{
    "lesson_plan_id": "e24ed82118ce7c8de5fcd4be4df716907febc67b1027bcdbfcdf9faef815120c",
    "subtopic_progress": {
        "958d4516429e99ddc2d98eb642861a28405da0f5048bd85cacc645ce5fc0276f": {
            "status": "not_started",
            "lessonCompleted": false,
            "quizAttempts": 0,
            "bestScore": 0,
            "averageScore": 0,
            "masteryLevel": "not_started",
            "weakConcepts": [],
            "lastAttemptAt": null
        },
        "248f483557a5a966adc65b963e3d9f6be43802479f88b8f6e5cafbaff19ade68": {
            "status": "in_progress",
            "lessonCompleted": true,
            "quizAttempts": 1,
            "bestScore": 31.25,
            "averageScore": 31.25,
            "masteryLevel": "beginner",
            "weakConcepts": [
                "Which expression is the correct expansion of −3(2x",
                "Factorise fully: 9x² + 6x",
                "Explain how you would simplify the expression 4(2y"
            ],
            "lastAttemptAt": "2025-12-15T17:50:42.293696"
        },
        "67f4a067d1fc1439cc7c65de34f2a195e5307481571e16fa3d8afc77f92ab89f": {
            "status": "not_started",
            "lessonCompleted": false,
            "quizAttempts": 0,
            "bestScore": 0,
            "averageScore": 0,
            "masteryLevel": "not_started",
            "weakConcepts": [],
            "lastAttemptAt": null
        },
        "59b2477b9db7e7b1ccfdc0e659fc27103601a8d2ef9658f57900470849470005": {
            "status": "not_started",
            "lessonCompleted": false,
            "quizAttempts": 0,
            "bestScore": 0,
            "averageScore": 0,
            "masteryLevel": "not_started",
            "weakConcepts": [],
            "lastAttemptAt": null
        },
        "d5cabd86471753104501b1669bec8fc7953c47593860242b11030569e585d469": {
            "status": "not_started",
            "lessonCompleted": false,
            "quizAttempts": 0,
            "bestScore": 0,
            "averageScore": 0,
            "masteryLevel": "not_started",
            "weakConcepts": [],
            "lastAttemptAt": null
        },
        "b9bf103c08696c8be2e9af525114146587e3289a43ad2113f93131d4edd614c1": {
            "status": "not_started",
            "lessonCompleted": false,
            "quizAttempts": 0,
            "bestScore": 0,
            "averageScore": 0,
            "masteryLevel": "not_started",
            "weakConcepts": [],
            "lastAttemptAt": null
        },
        "55d1caf15024bf7bd28332861c919f84324b31c0c3bc65eedf433e89ffe7ae76": {
            "status": "not_started",
            "lessonCompleted": false,
            "quizAttempts": 0,
            "bestScore": 0,
            "averageScore": 0,
            "masteryLevel": "not_started",
            "weakConcepts": [],
            "lastAttemptAt": null
        },
        "c43f3be7a522fa3993802cb555e8726b947b4425341dfa3f08e7c09fdfe405bd": {
            "status": "not_started",
            "lessonCompleted": false,
            "quizAttempts": 0,
            "bestScore": 0,
            "averageScore": 0,
            "masteryLevel": "not_started",
            "weakConcepts": [],
            "lastAttemptAt": null
        }
    },
    "overall_progress": {
        "totalSubtopics": 8,
        "completedSubtopics": 0,
        "percentComplete": 0,
        "totalStudyTime": 20,
        "averageScore": 31.25
    },
    "updated_at": "2025-12-15T17:50:42.750264"
}