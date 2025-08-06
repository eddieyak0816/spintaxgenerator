## Internal Linking Formulas for Google Sheets

### Parent Page Selection

**Link to First Child (one cell to the right and one cell down):**

```
=IF(INDIRECT(ADDRESS(ROW()+1, COLUMN()+1))="", "", "<a href='/" & LOWER(SUBSTITUTE(INDIRECT(ADDRESS(ROW()+1, COLUMN()+1)), " ", "-")) & "'>" & INDIRECT(ADDRESS(ROW()+1, COLUMN()+1)) & "</a>")
```

This formula dynamically links to the first child page by referencing the cell one row down and one column to the right. Use this if the dropdown selection is "Parent".

---

### Sibling Page Selection

**Link to Parent (closest non-empty cell above in the column to the left):**

```
=IFERROR("<a href='/'"&SUBSTITUTE(LOWER(INDEX(FILTER(INDIRECT(CHAR(COLUMN()-1+64)&"1:"&CHAR(COLUMN()-1+64)&ROW()-1),INDIRECT(CHAR(COLUMN()-1+64)&"1:"&CHAR(COLUMN()-1+64)&ROW()-1)<>""),ROWS(FILTER(INDIRECT(CHAR(COLUMN()-1+64)&"1:"&CHAR(COLUMN()-1+64)&ROW()-1),INDIRECT(CHAR(COLUMN()-1+64)&"1:"&CHAR(COLUMN()-1+64)&ROW()-1)<>""))))," ","-")&"'>"&INDEX(FILTER(INDIRECT(CHAR(COLUMN()-1+64)&"1:"&CHAR(COLUMN()-1+64)&ROW()-1),INDIRECT(CHAR(COLUMN()-1+64)&"1:"&CHAR(COLUMN()-1+64)&ROW()-1)<>""),ROWS(FILTER(INDIRECT(CHAR(COLUMN()-1+64)&"1:"&CHAR(COLUMN()-1+64)&ROW()-1),INDIRECT(CHAR(COLUMN()-1+64)&"1:"&CHAR(COLUMN()-1+64)&ROW()-1)<>"")))&"</a>","")
```

This formula dynamically finds the closest non-empty cell above in the column to the left and creates a hyperlink using its value. Use this if the dropdown selection is "Sibling".

---

**Link to Next Sibling (one cell below in the same column):**

```
=IF(INDIRECT(ADDRESS(ROW()+1, COLUMN()))="", "", "<a href='/" & LOWER(SUBSTITUTE(INDIRECT(ADDRESS(ROW()+1, COLUMN())), " ", "-")) & "'>" & INDIRECT(ADDRESS(ROW()+1, COLUMN())) & "</a>")
```

This formula dynamically links from a sibling page to the next sibling (the cell directly below in the same column). Use this if the dropdown selection is "Sibling".
