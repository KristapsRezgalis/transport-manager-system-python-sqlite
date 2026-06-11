Transport Management System (TMS)

A desktop-based Transport Management System built with Python, SQLite, Pandas, and FreeSimpleGUI for managing transportation operations, forwarders, companies, contacts, and logistics statistics.

Designed to replace spreadsheet-based transport tracking with a centralized database solution.

---

## Features

### Transport Orders
- Create, edit and delete transport orders
- Advanced filtering and search
- Column sorting
- Transport KPI calculations
- SAP PO tracking
- Loading and unloading date management
- Forwarder assignment
- Cost tracking
- Customs and temperature-control tracking

### Statistics & Analytics
- Transport cost analysis
- Pallet volume analysis
- Reporting by selected period
- Diagram generation
- Dashboard KPIs:
  - Total transports
  - Total cost
  - Total pallets
  - Cost per transport
  - Cost per pallet
  - Pallets per shipment

### Company Management
- Company database
- Company contacts
- Company addresses
- Product category tracking
- Internal notes

### Forwarder Management
- Forwarder database
- Payment terms
- Contact management
- Search and filtering

### User Management
- Login system
- User administration
- Role management
- Credential storage

### PDF Generation
Generate transport order PDFs directly from transport records.

### Customizable Interface
- Multiple GUI themes
- Dynamic theme switching
- Responsive desktop layout

---

## Technology Stack

- Python
- SQLite
- Pandas
- FreeSimpleGUI
- Matplotlib
- ReportLab

---

## Project Structure

```text
project/
│
├── gui.py
├── db.py
├── company.py
├── forwarder.py
├── pdf.py
├── stats.py
├── config.py
│
├── database/
│   └── transport.db
│
├── assets/
│   └── gemoss_logo.png
│
└── generated_pdfs/
```

---

## Database Tables

- transport
- user
- t_company
- t_company_contact
- t_company_address
- t_forwarder
- t_fw_contact

---

## Installation

### Clone Repository

```bash
git clone https://github.com/KristapsRezgalis/transport-manager-system-python-sqlite.git
cd transport-manager-system-python-sqlite
```

### Run

```bash
python gui.py
```

---

## Current Capabilities

✅ Transport order management

✅ Company management

✅ Forwarder management

✅ Contact management

✅ User administration

✅ PDF generation

✅ Advanced filtering

✅ Statistics dashboard

✅ Search functionality

✅ Dynamic table sorting

---

## Future Improvements

- Excel export
- Email integration
- Invoice management
- ERP integration
- Role-based permissions
- Multi-language support
- API integrations

---

## Purpose

This application was developed to streamline logistics and transportation operations by replacing manual spreadsheet workflows with a centralized Transport Management System.

---

## License
MIT License

---

## Author
**Kristaps Rezgalis**
