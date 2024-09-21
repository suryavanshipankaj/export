import pandas as pd
import streamlit as st
from io import BytesIO

# Set up the page configuration
st.set_page_config(page_title="SQL Script Generator", page_icon="🥷", layout="wide")

# Page title and description
st.title("Generate SQL Script from Excel or CSV File 📜")
st.write("Upload an Excel or CSV file and generate a SQL `CREATE TABLE` and `INSERT INTO` script automatically.")

# Sidebar for file upload
st.sidebar.header("Upload your file 📂")
inputFile = st.sidebar.file_uploader("Upload Excel or CSV File", type=["xlsx", "xls", "csv"])

# Custom table name input
table_name = st.sidebar.text_input("Enter Table Name", value="table_name")

# Check if a file has been uploaded
if inputFile is not None:
    try:
        # Display file info and loading spinner
        with st.spinner("Processing the file..."):
            # Determine file type and read the file
            if inputFile.name.endswith(('xlsx', 'xls')):
                df = pd.read_excel(inputFile)
            elif inputFile.name.endswith('csv'):
                df = pd.read_csv(inputFile)

        # Display a preview of the uploaded data
        st.subheader("Preview of Uploaded Data 📊")
        st.dataframe(df.head(10))  # Show the first 10 rows for preview
        
        # Add a checkbox to allow users to show the entire dataset
        if st.checkbox("Show Full Dataset"):
            st.dataframe(df)

        # Map pandas dtypes to MySQL data types
        dtype_mapping = {
            'object': 'VARCHAR(255)',
            'int64': 'INT',
            'float64': 'FLOAT',
            'datetime64[ns]': 'DATETIME',
            'bool': 'BOOLEAN'
        }

        # Generate the CREATE TABLE statement
        columns_with_types = []
        for column, dtype in zip(df.columns, df.dtypes):
            sql_type = dtype_mapping.get(str(dtype), 'VARCHAR(255)')
            columns_with_types.append(f"`{column}` {sql_type}")
        create_table_statement = f"CREATE TABLE `{table_name}` (\n" + ",\n".join(columns_with_types) + "\n);"

        # Generate the INSERT INTO statement
        columns = ', '.join([f"`{col}`" for col in df.columns])
        values_list = []
        for _, row in df.iterrows():
            values = ', '.join([f"'{value}'" if pd.notna(value) else "NULL" for value in row.values])
            values_list.append(f"({values})")
        values_str = ',\n'.join(values_list)
        insert_statement = f"INSERT INTO `{table_name}` ({columns}) VALUES\n{values_str};"

        # Combine the SQL statements
        sql_script = create_table_statement + "\n\n" + insert_statement

        # Display the generated SQL script
        st.subheader("Generated SQL Script 🧾")
        st.code(sql_script, language="sql")

        # Function to convert SQL content to a downloadable file
        def create_download_link(sql_content):
            b = BytesIO()
            b.write(sql_content.encode())
            b.seek(0)
            return b

        # Create a downloadable link for the SQL file
        b = create_download_link(sql_script)
        st.download_button(
            label="Download SQL File 📥",
            data=b,
            file_name=f"{table_name}.sql",
            mime="text/sql"
        )

    except Exception as e:
        # Display error message if something goes wrong
        st.error(f"Error processing the file: {e}")
else:
    st.info("Please upload an Excel or CSV file to get started.")

