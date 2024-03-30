import pandas as pd
import os

class DatabaseManager:
    
    def __init__(self, priority_list_path, daily_audits_path, weekly_audits_path):
        self.priority_list_path = priority_list_path
        self.daily_audits_path = daily_audits_path
        self.weekly_audits_path = weekly_audits_path

    ####################################################################################### Priority List DB
    
    def read_priority_list(self):
        if not os.path.exists(self.priority_list_path):
            # Optionally, create the file if it's supposed to exist
            with open(self.priority_list_path, 'w') as file:
                file.write("") # Write a header if your file format includes one
            return [] # Return an empty list if the file does not exist
        with open(self.priority_list_path, 'r') as file:
            priority_list = file.read().split(',')
        # Remove any empty strings from the list
        priority_list = [item.strip() for item in priority_list if item.strip()]
        return priority_list
    
    def delete_priority_item(self, item):
        priority_list = self.read_priority_list()
        priority_list.remove(item)
        self.write_priority_list(priority_list)

    def write_priority_list(self, priority_list):
        with open(self.priority_list_path, 'w') as file:
            for item in priority_list:
                file.writelines(f"{item},\n")
    
    def append_priority_item(self, item):
        with open(self.priority_list_path, 'a') as file:
            file.write(f"{item},\n")

    ####################################################################################### Daily Audits DB
    
    def read_daily_audits(self):
        if not os.path.exists(self.daily_audits_path):
            self.create_empty_audit_file(self.daily_audits_path)
        return pd.read_csv(self.daily_audits_path)

    def write_daily_audits(self, df):
        df.to_csv(self.daily_audits_path, index=False)

    ####################################################################################### Weekly Audits DB

    def read_weekly_audits(self):
        if not os.path.exists(self.weekly_audits_path):
            self.create_empty_audit_file(self.weekly_audits_path)
        return pd.read_csv(self.weekly_audits_path)

    def write_weekly_audits(self, df):
        df.to_csv(self.weekly_audits_path, index=False)

    ####################################################################################### Emtpy Audit Initialization

    def create_empty_audit_file(self, file_path, column_list):
        # Check if the file already exists
        if not os.path.exists(file_path):
            empty_df = pd.DataFrame(columns=column_list)
            empty_df.to_csv(file_path, index=False)
            # print(f"db Log: Empty file created at {file_path}")
        else:
            # print(f"db Log: File already exists at {file_path}. No new file created.")
            pass