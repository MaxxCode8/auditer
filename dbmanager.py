from datetime import datetime, timedelta
import os
import pandas as pd

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
        try:
            df = pd.read_csv(self.daily_audits_path)
            today_audits = df[df['date'] == pd.to_datetime('today').strftime('%Y-%m-%d')]
            return today_audits
        except Exception as e:
            print(f"Error reading daily audits: {e}")

    def write_daily_audits(self, new_audit):
        # APPEND the new audit directly to the CSV file
        with open(self.daily_audits_path, 'a') as file:
            file.write(f"{new_audit['priority']},{new_audit['description']},{new_audit['time_spent']},{new_audit['start_time']},{new_audit['end_time']},{new_audit['date']}\n")

    def update_daily_audits(self, audit):
        # Read the entire CSV file into a DataFrame
        df = pd.read_csv(self.daily_audits_path)
        # Update the specific row
        df.loc[(df['date'] == audit['date']) & (df['start_time'] == audit['start_time']), ['end_time', 'time_spent']] = [audit['end_time'], audit['time_spent']]
        # Write the updated DataFrame back to the CSV file
        df.to_csv(self.daily_audits_path, index=False)

    def delete_audit_entry(self, start_ts):
        df = pd.read_csv(self.daily_audits_path)
        df = df[df['start_time'] != start_ts]
        df.to_csv(self.daily_audits_path, index=False)
        
    ####################################################################################### Weekly Audits DB
    def fetch_last_seven(self):
        df = pd.read_csv(self.daily_audits_path)
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        seven_days_ago = datetime.now() - timedelta(days=7)
        filtered_df = df[df['date'] >= seven_days_ago]
        return filtered_df
    
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