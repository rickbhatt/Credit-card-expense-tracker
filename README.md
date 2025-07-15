# Credit Card Expense Tracker

A Python-based command-line application for tracking and managing credit card expenditures using PostgreSQL database and SQLAlchemy ORM.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [File Structure](#file-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🔍 Overview

This application provides a simple yet powerful interface for tracking credit card transactions. Built with modern Python practices, it uses SQLAlchemy ORM for database operations and Rich library for beautiful console output.

### Key Highlights

- **Clean Architecture**: Separation of concerns with dedicated modules
- **User-Friendly Interface**: Serial number-based selection (no database IDs exposed)
- **Rich Console Output**: Beautiful tables with colored formatting
- **Robust Error Handling**: Comprehensive validation and error messages
- **Database Agnostic**: Easy to switch between database systems

## ✨ Features

### Core Functionality

- ✅ **Add Transactions**: Insert new credit card transactions with validation
- ✅ **View Transactions**: Display all transactions in a formatted table
- ✅ **Delete Transactions**: Remove transactions with confirmation
- ✅ **Update Transactions**: Update transactions with confirmation
- ✅ **Calculate Totals**: Automatic expenditure calculation
- ✅ **Data Validation**: Input validation for dates, amounts, and data types

### User Experience

- 🎨 **Rich Console Interface**: Colored tables and formatted output
- 🔢 **Serial Number Selection**: User-friendly record selection
- ⚠️ **Confirmation Dialogs**: Safety confirmations for destructive operations
- 📊 **Formatted Display**: Currency formatting and date localization

## 🛠 System Requirements

### Software Dependencies

- **Python**: 3.8 or higher
- **PostgreSQL**: 12 or higher
- **Operating System**: Windows, macOS, or Linux

## 📦 Installation

### 1. Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd credit-card-tracker

# Or download and extract the ZIP file
```

### 2. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 🗄️ Database Setup

### 1. Install PostgreSQL

- Download from [postgresql.org](https://www.postgresql.org/download/)
- Follow installation instructions for your operating system
- Remember the password you set for the `postgres` user

### 2. Create Database

```sql
-- Connect to PostgreSQL as postgres user
psql -U postgres

-- Create database
CREATE DATABASE cct_db;

-- Create user (optional)
CREATE USER your_username WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE cct_db TO your_username;

-- Exit psql
\q
```

### 3. Verify Connection

```bash
psql -U postgres -d cct_db -h localhost -p 5432
```

## ⚙️ Configuration

### 1. Environment Variables

Create a `.env` file in the `src` directory:

```env
# Database Configuration
DB_NAME=cct_db
DB_USER=postgres
DB_HOST=localhost
DB_PORT=5432
DB_PASSWORD=your_password_here

# Application Settings
CREATE_TABLES=false
```

### 2. Configuration Options

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DB_NAME` | Database name | - | Yes |
| `DB_USER` | Database username | - | Yes |
| `DB_HOST` | Database host | localhost | Yes |
| `DB_PORT` | Database port | 5432 | Yes |
| `DB_PASSWORD` | Database password | - | Yes |
| `CREATE_TABLES` | Auto-create tables | false | No |

### 3. First Run Setup

On first run with `CREATE_TABLES=true`, the application will automatically create the required database tables.

## 🚀 Usage

### Starting the Application

```bash
cd src
python main.py
```

### Main Menu Options

```
**************************************************
1. Press 1 to insert transaction details
2. Press 2 to see all transactions and total expenditure
3. Press 3 to delete a transaction
4. Press 4 to exit the program
**************************************************
```

### 1. Adding Transactions

1. Select option `1`
2. Enter transaction date in DD-MM-YYYY format (e.g., 25-12-2024)
3. Enter transaction details (e.g., "Coffee at Starbucks")
4. Enter amount (positive number, e.g., 45.50)
5. Enter remarks (optional)

**Example:**

```
Enter transaction date DD-MM-YYYY: 06-07-2025
Enter transaction details: Netflix Subscription
Enter amount: 199.00
Enter remarks (Optional): Monthly subscription
```

### 2. Viewing Transactions

Select option `2` to view all transactions in a formatted table with:

- Serial numbers (1, 2, 3...)
- Date in DD-MMM-YYYY format
- Transaction details
- Amount in ₹ currency format
- Remarks
- Total expenditure at the bottom

### 3. Deleting Transactions

1. Select option `3`
2. View the list of all transactions with serial numbers
3. Enter the serial number of the transaction to delete
4. Confirm deletion when prompted

**Safety Features:**

- Shows the transaction to be deleted before confirmation
- Requires explicit confirmation (y/yes)
- Can be cancelled at any time

## 🏗 Architecture

### Design Patterns

- **MVC Pattern**: Separation of data (models), business logic (manager), and presentation (utils)
- **Repository Pattern**: Database operations abstracted through manager class
- **Context Manager**: Automatic connection management with `with` statements

### Module Structure

```
src/
├── main.py              # Application entry point
├── .env                 # Environment configuration
├── requirements.txt     # Python dependencies
└── db/                  # Database package
    ├── __init__.py     # Package initialization
    ├── models.py       # SQLAlchemy models
    ├── manager.py      # Database operations
    └── utils.py        # Display utilities
```

### Data Flow

```
User Input → main.py → Database.manager → SQLAlchemy → PostgreSQL
                    ↓
              Rich Console ← utils.py ← DataFrame ← Database Response
```

## 📚 API Reference

### Database Class

#### Constructor

```python
Database()
```

Initializes database connection parameters from environment variables.

#### Methods

##### `connect() -> bool`

Establishes database connection and creates tables if configured.

**Returns:** `True` if successful, `False` otherwise

##### `insert_into_transaction_table(date_str, details, amount_str, remarks) -> int|None`

Inserts a new transaction record.

**Parameters:**

- `date_str` (str): Date in DD-MM-YYYY format
- `details` (str): Transaction description
- `amount_str` (str): Transaction amount
- `remarks` (str): Optional remarks

**Returns:** Transaction ID if successful, `None` otherwise

##### `display_transaction_and_total_expenditure() -> None`

Displays all transactions in a formatted table with total expenditure.

##### `delete_transaction_menu() -> bool`

Interactive menu for deleting transactions.

**Returns:** `True` if deletion successful, `False` otherwise

### Transaction Model

#### Fields

- `id` (Integer): Primary key, auto-increment
- `date` (Date): Transaction date
- `transaction_details` (String): Description of transaction
- `amount` (Numeric): Transaction amount with 2 decimal precision
- `remarks` (Text): Optional remarks

### Utility Functions

#### `display_transactions_in_table(df, total, table_title)`

Pure display function for showing transaction data.

#### `display_transactions_for_selection(df, table_title) -> dict`

Interactive display that returns ID mapping for user selection.

#### `display_single_transaction(df, table_title)`

Displays a single transaction (used for confirmations).

## 📁 File Structure

```
src/
├── main.py                 # Application entry point and CLI interface
├── .env                    # Environment configuration (not in git)
├── requirements.txt        # Python dependencies
│
└── db/                     # Database package
    ├── __init__.py        # Package initialization and metadata
    │                      # Exports: Database class
    │                      # Version: 1.1.0
    │                      # Author: Ritankar Bhattacharjee
    │
    ├── models.py          # SQLAlchemy ORM models
    │                      # - Transaction model with all fields
    │                      # - Base declarative class
    │                      # - Model relationships (future)
    │
    ├── manager.py         # Database operations and business logic
    │                      # - Database connection management
    │                      # - CRUD operations for transactions
    │                      # - Context manager implementation
    │                      # - Error handling and validation
    │
    └── utils.py           # Display utilities and console formatting
                           # - Rich table creation and formatting
                           # - Serial number to ID mapping
                           # - Separated display methods
```

### Key Files Description

#### `main.py`

- Application entry point
- CLI menu system
- User input validation
- Error handling for main operations

#### `db/models.py`

- SQLAlchemy ORM models
- Database table definitions
- Model methods and relationships

#### `db/manager.py`

- Database connection management
- Business logic for all operations
- Context manager for automatic cleanup
- Error handling and transaction management

#### `db/utils.py`

- Rich console formatting
- Table display utilities
- User interaction helpers
- Separation of display concerns

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection Failed

**Error:** `Unable to connect to the database`

**Solutions:**

- Verify PostgreSQL is running
- Check `.env` file configuration
- Ensure database exists
- Verify username/password
- Check firewall settings

#### 2. Module Import Errors

**Error:** `ModuleNotFoundError`

**Solutions:**

- Activate virtual environment
- Install requirements: `pip install -r requirements.txt`
- Check Python path

#### 3. Permission Denied

**Error:** `permission denied for database`

**Solutions:**

- Grant database privileges
- Check user permissions
- Use correct database user

#### 4. Table Does Not Exist

**Error:** `relation "transaction" does not exist`

**Solutions:**

- Set `CREATE_TABLES=true` in `.env`
- Run application once to create tables
- Manually create tables using SQL

### Debug Mode

Enable SQLAlchemy echo for debugging:

```python
# In manager.py, change:
self.engine = create_engine(db_url, echo=True)  # Shows SQL queries
```

### Logging

Add logging for better debugging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create virtual environment
3. Install dependencies
4. Make changes
5. Test thoroughly
6. Submit pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings for functions
- Maintain consistent naming conventions

### Testing

Before submitting changes:

- Test all CRUD operations
- Verify error handling
- Check edge cases
- Test with different data types

### Future Enhancements

Potential areas for improvement:

- 📅 Billing period management
- 📊 Expense categorization
- 📈 Reporting and analytics
- 🔍 Search and filtering
- 📱 GUI interface
- 🔐 User authentication
- 💾 Data export/import
- 📝 Budget tracking

---

## 📄 License

This project is created for personal use. Feel free to modify and distribute as needed.

## 👨‍💻 Author

**Ritankar Bhattacharjee**

- Application Version: 1.1.0
- Last Updated: July 2025

---

*For additional support or questions, please refer to the troubleshooting section or contact the author.*
