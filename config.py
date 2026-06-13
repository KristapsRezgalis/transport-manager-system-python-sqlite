import FreeSimpleGUI as sg

sg.theme("DarkAmber")

# table column names
ORDER_COLUMNS = ["ID", "SAP PO", "Sender", "Delivery", "Loading", "Unloading", "Pallets", "Weight", "Forwarder", "Contact", "Cost","Customs","REF"]
USER_COLUMNS = ["ID", "Name", "Surname", "Role", "E-mail","Phone","Login","Password",]
COMPANY_COLUMNS = ['ID', 'Name', 'Reg Nr', 'VAT Nr', 'Street', 'City', 'Post code', 'Country']
FORWARDER_COLUMNS = ['ID', 'Name', 'Reg Nr', 'VAT Nr', 'Street', 'City', 'Post code', 'Country', 'Payment days']
FORWARDER_CONTACT_COLUMNS = ['ID', 'Name', 'Surname', 'Position', 'Phone', 'Email']
FW_CONTACT_DB_COLUMNS = ["fw_contact_id","fw_c_name","fw_c_surname","fw_c_position","fw_c_phone","fw_c_email"]
TRANSPORT_ORDER_DB_COLUMNS = ["nr", "sap_po", "sender", "delivery", "loading", "unloading", "pallets", "weight", "forwarder", "cost", "customs","ref"]

# dropdown variables
user_roles = ['admin', 'user', 'spectator']
countries = ["Albania", "Andorra", "Austria", "Belarus", "Belgium", "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Latvia", "Liechtenstein", "Lithuania", "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro", "Netherlands", "North Macedonia", "Norway", "Poland", "Portugal", "Romania", "Russia", "San Marino", "Serbia", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Turkey", "Ukraine", "United Kingdom", "Vatican City"]
temperature_customs_options = ['Yes', '']
statistics_types = ['Cost per pallet', 'Cost per cargo', 'Total cost', 'Total cargos', 'Total pallets', 'Total weight', 'Pallets per cargo', 'Weight per pallet', 'Weight per cargo', 'Cargos per country', 'Cargos per forwarder', 'Cost per forwarder']
statistic_period = ['Per day', 'Per month', 'Per year']