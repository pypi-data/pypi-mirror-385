========================
pip show pydeskpro
========================
Name: pydeskpro
Version: 1.0.0
Summary:
Home-page:
Author: SHAFIQUL ISLAM
Author-email: shafiqul.cmt@gmail.com
Requires: click, rich
Required-by:

===============================
Installation command:
===============================
pip install pydeskpro
==================================
============================================
Complete the installation go to your installed project folder and simply type this command
============================================
PS C:\> pydesk
============================================
You’ll see an interactive menu like this:

Welcome to PyDesk!
What's your name? shafiqul
Performing scheduled backup...
Backup created successfully: pydesk_backup.zip

You’ll see an interactive menu like this:
==============================
  Welcome back, shafiqul! 👋
==============================
Tasks: 0 | Notes: 0 | Total Spent: 0.00
Select an option below:

┌────┬──────────────────────────┐
│ 1. │ Tasks                    │
│ 2. │ Notes                    │
│ 3. │ Expenses                 │
│ 4. │ Backup & Restore         │
│ 5. │ Change Name              │
│ 6. │ Backup Interval Settings │
│ 7. │ Exit                     │
└────┴──────────────────────────┘

===================================== Tasks Section ======================================
=======================================
Select an option: 1
=======================================
-- Tasks Menu --
1. Add Task
2. View Tasks
3. Delete Task
4. Back
=======================================
Select an option: 1
Enter task: My First Task

Select an option: 2

        Tasks
┏━━━━┳━━━━━━━━━━━━━━━┓
┃ No ┃ Task          ┃
┡━━━━╇━━━━━━━━━━━━━━━┩
│ 1  │ My First Task │
└────┴───────────────┘
======================================
Select an option: 3
=====================================

Show List of Tasks:
1. My First Task

Delete task number: 1
Task deleted!

======================================
Select an option: 4  
=====================================
Back to the Main menu
======================================
┌────┬──────────────────────────┐
│ 1. │ Tasks                    │
│ 2. │ Notes                    │
│ 3. │ Expenses                 │
│ 4. │ Backup & Restore         │
│ 5. │ Change Name              │
│ 6. │ Backup Interval Settings │
│ 7. │ Exit                     │
└────┴──────────────────────────┘

===================================== Notes Section ======================================
=========================================
Select an option: 2
=========================================
-- Notes Menu --
1. Add Note
2. View Notes
3. Delete Note
4. Back

=======================================
Select an option: 1   
======================================
Title: My Note Title
Body: Note Body

=======================================
Select an option: 2
=======================================
              Notes
┏━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ No ┃ Title         ┃ Body      ┃
┡━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ 1  │ My Note Title │ Note Body │
└────┴───────────────┴───────────┘
======================================
Select an option: 3
=====================================

Show List of Notes:
1. My Note Title

Delete Note number: 1
Note deleted!

======================================
Select an option: 4  
=====================================
Back to the Main menu
======================================

┌────┬──────────────────────────┐
│ 1. │ Tasks                    │
│ 2. │ Notes                    │
│ 3. │ Expenses                 │
│ 4. │ Backup & Restore         │
│ 5. │ Change Name              │
│ 6. │ Backup Interval Settings │
│ 7. │ Exit                     │
└────┴──────────────────────────┘

===================================== Expense Section ======================================
=========================================
Select an option: 3
=========================================
-- Expenses Menu --
1. Add Expense
2. View Expenses
3. Delete Expense
4. Total
5. Back

=======================================
Select an option: 1   
======================================
Description: Food
Amount: 200
Expense added!

=======================================
Select an option: 2
=======================================
         Expenses
┏━━━━┳━━━━━━━━━━┳━━━━━━━━┓
┃ No ┃ Category ┃ Amount ┃
┡━━━━╇━━━━━━━━━━╇━━━━━━━━┩
│ 1  │ Food     │ 200.00 │
│ 2  │ Travel   │ 500.00 │
│ 3  │ Food     │ 600.00 │
└────┴──────────┴────────┘
Total: 1300.00

======================================
Select an option: 3
=====================================

Show List of Expenses:
1. Food (200.0)

Delete expense number: 1
Expense deleted!
======================================
Select an option: 4  
=====================================
Total Expenses: 200.00
======================================

======================================
Select an option: 5
=====================================  
Category-wise Expense Summary
===================================
Food                 : $800.0
Travel               : $500.0

======================================
Select an option: 4  
=====================================
Back to the Main menu
======================================
┌────┬──────────────────────────┐
│ 1. │ Tasks                    │
│ 2. │ Notes                    │
│ 3. │ Expenses                 │
│ 4. │ Backup & Restore         │
│ 5. │ Change Name              │
│ 6. │ Backup Interval Settings │
│ 7. │ Exit                     │
└────┴──────────────────────────┘

======================================
Select an option: 4  
=====================================
-- Backup & Restore --
1. Create Backup
2. Restore Backup
3. Back

======================================
Select an option: 5  
=====================================
Enter new name:


======================================
Select an option: 6  
=====================================
-- Backup Interval Settings --
1. Daily
2. Weekly
Select backup frequency:


======================================
Select an option: 7  
=====================================
Goodbye!
Backup created successfully: pydesk_backup.zip