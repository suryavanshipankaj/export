import pandas as pd
import streamlit as st
from io import BytesIO
st.set_page_config(page_title="Network", page_icon="🥷", layout="wide")
st.title("Generate SQL Script from Excel or CSV File 📜")
#st.title("Generate SQL Script from Excel or CSV File")

# Upload Excel or CSV file
inputFile = st.sidebar.file_uploader("Upload Excel or CSV File", type=["xlsx", "xls", "csv"])

if inputFile is not None:
    try:
        # Determine the file type and read the uploaded file
        if inputFile.name.endswith('xlsx') or inputFile.name.endswith('xls'):
            df = pd.read_excel(inputFile)
        elif inputFile.name.endswith('csv'):
            df = pd.read_csv(inputFile)

        # Map pandas dtypes to MySQL data types
        dtype_mapping = {
            'object': 'VARCHAR(255)',
            'int64': 'INT',
            'float64': 'FLOAT',
            'datetime64[ns]': 'DATETIME',
            'bool': 'BOOLEAN'
        }

        # Generate the CREATE TABLE statement
        table_name = "table_name"
        columns_with_types = []
        for column, dtype in zip(df.columns, df.dtypes):
            sql_type = dtype_mapping.get(str(dtype), 'VARCHAR(255)')
            columns_with_types.append(f"{column} {sql_type}")
        create_table_statement = f"CREATE TABLE {table_name} (\n" + ",\n".join(columns_with_types) + "\n);"

        # Generate the INSERT INTO statement
        columns = ', '.join(df.columns)
        values_list = []
        for _, row in df.iterrows():
            values = ', '.join([f"'{value}'" for value in row.values])
            values_list.append(f"({values})")
        values_str = ',\n'.join(values_list)
        insert_statement = f"INSERT INTO {table_name} ({columns}) VALUES\n{values_str};"

        # Combine both statements
        sql_script = create_table_statement + "\n\n" + insert_statement

        # Display the generated SQL script
        st.code(sql_script)

        # Function to convert SQL content to a downloadable file
        def create_download_link(sql_content):
            b = BytesIO()
            b.write(sql_content.encode())
            b.seek(0)
            return b

        # Create a downloadable link for the SQL file
        b = create_download_link(sql_script)
        st.download_button(
            label="Download SQL File",
            data=b,
            file_name="script.sql",
            mime="text/sql"
        )
    except Exception as e:
        st.error(f"Error processing the file: {e}")

