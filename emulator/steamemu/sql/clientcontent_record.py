def main():
    # ... (Other parts of the main() function as before) ...

    if fetched_row:
        # ... (Other parts of the main() function as before) ...

        # Format the columns in the desired format
        client_bootstrap_version = format_hex_column(fetched_row[3])
        linux_client_app_version = format_hex_column(fetched_row[4])
        linux_hlds_update_tool_version = format_hex_column(fetched_row[5])
        beta_client_bootstrap_version = format_hex_column(fetched_row[6])
        beta_client_app_package_version = format_hex_column(fetched_row[8])
        beta_linux_hlds_update_tool_version = format_hex_column(
            fetched_row[12])
        cafe_administration_client_version = format_hex_column(fetched_row[14])
        cafe_administration_server_version = format_hex_column(fetched_row[15])
        custom_package_version = format_hex_column(fetched_row[16])

        # Append '\x00' to the specified columns
        beta_client_bootstrap_password = fetched_row[7] + '\x00'
        beta_client_app_package_password = fetched_row[9] + '\x00'
        beta_win32_hlds_update_tool_version = fetched_row[10] + '\x00'
        beta_win32_hlds_update_tool_password = fetched_row[11] + '\x00'
        beta_linux_hlds_update_tool_password = fetched_row[13] + '\x00'

        # ... (Print statements for other columns as before) ...
    else:
        print("No rows found for the specified date:",
              date_to_search.strftime('%Y-%m-%d'))

    mysql_db.disconnect()
