# Credit Card Expense Tracker

A Python-based command-line application for tracking and managing credit card expenditures using PostgreSQL database and SQLAlchemy ORM.

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

## 🚀 Usage

### Starting the Application

```bash
cd src
python main.py
```

## 🏗 Architecture

### Design Patterns

- **MVC Pattern**: Separation of data (models), business logic (manager), and presentation (utils)
- **Repository Pattern**: Database operations abstracted through manager class
- **Context Manager**: Automatic connection management with `with` statements

## 👨‍💻 Author

### Ritankar Bhattacharjee

- Application Version: 1.1.0
- Last Updated: July 2025

---
