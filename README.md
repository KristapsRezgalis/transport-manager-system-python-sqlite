**Transport Management System (TMS)**

A desktop-based Transport Management System built with Python, SQLite, Pandas, and FreeSimpleGUI for managing transportation operations, forwarders, companies, contacts, and logistics statistics.
Designed to replace spreadsheet-based transport tracking with a centralized database solution.

**- Overview:**
The system provides a complete workflow for:
  Transport order management
  Forwarder database management
  Customer/company management
  Contact management
  Transportation cost analysis
  PDF transport order generation
  User administration
  Advanced filtering and searching
  Logistics reporting

**-- Features --**

**- Transport Orders:**
Manage transportation orders through a user-friendly interface.
> Functions:
  Create transport orders
  Edit existing orders
  Delete orders
  Search records
  Advanced filtering
  Sort by any column
  Calculate transport KPIs
> Stored information includes:
  SAP PO number
  Sender
  Delivery location
  Loading date
  Unloading date
  Pallet quantity
  Gross weight
  Forwarder
  Forwarder contact
  Transportation cost
  Customs status
  Temperature control requirements

**- Statistics & Analytics:**
> Built-in reporting module with:
  Cost analysis
  Pallet analysis
  Transport volume tracking
  Period-based reporting
  Diagram generation
> Dashboard KPIs:
  Total transports
  Total transportation cost
  Total pallets shipped
  Average cost per transport
  Average cost per pallet
  Average pallets per shipment

**- Company Management:**
Maintain a centralized customer/supplier database.
> Features:
  Create companies
  Edit company information
  Delete companies
  Search companies
  Company notes
  Product categories
  Contact management
  Address management
> Stored information:
  Company name
  Registration number
  VAT number
  Address
  Country
  Product type
  Internal notes

**- Forwarder Management:**
Manage logistics providers and carriers.
> Features:
  Create forwarders
  Edit forwarders
  Delete forwarders
  Search forwarders
  Payment terms management
> Stored information:
  Company details
  Registration numbers
  VAT numbers
  Address information
  Payment terms

**- Contact Management:**
> Separate contact management for:
  Companies
  Forwarders
> Stored information:
  Name
  Surname
  Position
  Phone number
  E-mail address

**- PDF Transport Orders:**
Generate professional transport order PDFs directly from transport records.
> Useful for:
  Carrier instructions
  Internal documentation

**- User Management:**
> Built-in authentication system:
  Login system
  User administration
  Multiple user roles
  Password management

> Stored information:
  Name
  Surname
  Role
  E-mail
  Phone
  Login credentials

**- Advanced Filtering by:**
  SAP PO range
  Sender
  Delivery location
  Loading dates
  Unloading dates
  Pallet count
  Gross weight
  Forwarder
  Forwarder contact
  Cost range
  Customs status
  Temperature control

**- Customizable UI:**
Supports multiple FreeSimpleGUI themes.
Users can dynamically switch between color themes without modifying the source code.

**- Technology Stack:**
Technology	Purpose
Python	Application Logic
SQLite	Database
Pandas	Data Processing
FreeSimpleGUI	User Interface
ReportLab/PDF Module	PDF Generation
Matplotlib	Statistics & Charts

**- Project Structure:**
project/
│
├── gui.py                # Main application
├── db.py                 # Database operations
├── company.py            # Company management
├── forwarder.py          # Forwarder management
├── pdf.py                # PDF generation
├── stats.py              # Statistics and diagrams
├── config.py             # Configuration and constants
│
├── database/
│   └── transport.db
│
├── pdf/
│   └── generated_orders/
│
└── assets/
    └── gemoss_logo.png

**- Installation:**
1. Clone Repository
git clone https://github.com/yourusername/gemoss-tms.git
cd gemoss-tms
2. Install Dependencies
pip install -r requirements.txt

**- Example requirements:**
FreeSimpleGUI
pandas
sqlite3
matplotlib
reportlab
3. Run Application
python gui.py

**- Database:**
The application uses SQLite.

**- Main tables:**
transport
user
t_company
t_company_contact
t_company_address
t_forwarder
t_fw_contact

**- Current Capabilities:**
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
✅ Responsive desktop interface

**- Planned Features:**
Email integration
Transport order status workflow
Invoice management
Document adding and saving
Automatic transport cost calculations
Export to Excel, CSV
Multi-language support
Role-based permissions
API integration with ERP systems

**- Purpose:**
This project was developed to streamline transport planning and logistics operations by replacing manual Excel-based workflows with a centralized Transport Management System.
The goal is to provide logistics coordinators and transport planners with a fast, reliable, and scalable tool for managing daily transportation activities.

**- License:**
This project is licensed under the MIT License.

**- Author:**
Kristaps Rezgalis
