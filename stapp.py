import datetime
import time
from datetime import datetime
import numpy as np
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from dbmanager import DatabaseManager

# Today's Date:
today = datetime.today().strftime("%A : %d/%m/%y")

# This code will run only if the db Does not exist 🗃
weekly_audit_columns = ['priority', 'week', 'total_time_spent']
daily_audit_columns = ['priority', 'description', 'time_spent', 'start_time', 'end_time', "date"]
# Initialize the database manager with paths to your files
db_manager = DatabaseManager('prioritylist.txt', 'dailyaudits.csv', 'weeklyaudits.csv')
# Create empty audit files if they don't exist
db_manager.create_empty_audit_file('dailyaudits.csv', daily_audit_columns)
db_manager.create_empty_audit_file('weeklyaudits.csv', weekly_audit_columns)


def edit_priority_list():
    # Use session state to manage the priority list
    if "priority_list" not in st.session_state:
        st.session_state.priority_list = db_manager.read_priority_list()
        st.session_state.priority_list = list(set(st.session_state.priority_list))

    if st.session_state.priority_list:
        for item in st.session_state.priority_list:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"- *{item}*")
            with col2:
                if st.button("❌",key=item):
                    st.session_state.priority_list = list(set(st.session_state.priority_list))
                    st.session_state.priority_list.remove(item)
                    db_manager.delete_priority_item(item)
                    st.success(f"{item} deleted from the priority list.")
                    # Update the session state with the new list
                    st.session_state.priority_list = db_manager.read_priority_list()
                    # Reload the page to show the updated list
                    st.rerun()
    else:
        st.info("No items in the priority list.")

    # Placeholder for the new priority item
    new_priority_item = st.text_input("Add a new priority item:")
    if st.button("Add Item"):
        if new_priority_item and new_priority_item not in st.session_state.priority_list:
            db_manager.append_priority_item(new_priority_item)
            st.success(f"{new_priority_item} added to the priority list.")
            # Update the session state with the new list
            st.session_state.priority_list = db_manager.read_priority_list()
            # Reload the page to show the updated list
            st.rerun()
        else:
            st.warning("Please enter a unique priority item.")

def update_daily_audits():
    # Use session state to manage the daily audits list
    if "daily_audits_df" not in st.session_state:
        st.session_state.daily_audits_df = db_manager.read_daily_audits()

    # Fetch priorities from the priority list
    priority_list = db_manager.read_priority_list()
    priority_options = [''] + priority_list

    # Form for adding new audits
    with st.form(key='add_audit_form'):
        priority = st.selectbox("Select Priority", priority_options)
        description = st.text_input("Specify Task (Aspect)")
        start_button = st.form_submit_button("Start🚀")

        if start_button:
                # daily_audit_columns = ['priority_cat_str', 'description_str', 'time_spent_timestampsubstration', 'start_time', 'end_time', "date"]
                # Append the new audit to the daily audits DataFrame
                new_audit = {
                    'priority': priority, 'description': '"'+description+'"', 
                    'time_spent': "N0ne", 'start_time': time.time(),    # current timestamp
                    'end_time': "N0ne",
                    'date': pd.to_datetime('today').strftime('%Y-%m-%d')
                    }
                
                db_manager.write_daily_audits(new_audit)
                st.success("Audit added successfully.")
                # Update the session state with the new list
                st.session_state.daily_audits_df = db_manager.read_daily_audits()
                # Reload the page to show the updated list
                st.rerun() # REFRESEHs the page

    # Display existing audits
    if st.session_state.daily_audits_df.empty:
        st.info("No audits found.")
    else:   
        st.markdown("### Priority🧘‍♀️         Description📃             Time Spent ⏲")
        for index, row in st.session_state.daily_audits_df.iterrows():
            col1, col2, col3, col4 = st.columns([2,3,2,1])
            with col1:
                st.markdown(f"##### :violet[{row['priority']}]")
            with col2:
                st.markdown(f"##### :green[{row['description']}]")
            with col3:
                if row['end_time'] == "N0ne":
                    taskend = st.button("✅ :blue[**End Task**]", key=index)
                    if taskend:
                        st.session_state.daily_audits_df.loc[index, "end_time"] = time.time()
                        start_time = float(st.session_state.daily_audits_df.loc[index, "start_time"])
                        end_time = float(st.session_state.daily_audits_df.loc[index, "end_time"])
                        time_spent = round((end_time-start_time) / 3600,2)
                        # Update the session dataframe
                        st.session_state.daily_audits_df.loc[index, "time_spent"] = time_spent
                        db_manager.update_daily_audits(st.session_state.daily_audits_df.loc[index])
                        st.rerun()
                else:                    
                    st.markdown(f"##### :orange[{row['time_spent']} hours]")
            with col4:
                if st.button(f"❌", key=f"delete_audit_{index}"):
                    # Delete the audit from the DataFrame
                    start_time = float(st.session_state.daily_audits_df.loc[index, "start_time"])
                    st.session_state.daily_audits_df.drop(index, inplace=True)
                    db_manager.delete_audit_entry(start_time)    
                    st.success("Entry Deleted")
                    # Update the session state with the new list
                    st.session_state.daily_audits_df = db_manager.read_daily_audits()
                    # Reload the page to show the updated list
                    st.rerun()


# Function to display weekly audit report
def display_weekly_audit_report():

    # if st.button("Give Me Last 7 Day Audit 🧮"):
    #     df7 = db_manager.fetch_last_seven()
    #     grouped_df = df7.groupby('priority')['time_spent'].sum()

    #     # Sort the data by total time spent
    #     sorted_df = grouped_df.sort_values(ascending=True)

    #     # Create a figure and a set of subplots
    #     fig, ax = plt.subplots(figsize=(16, 12))

    #     # Define a list of colors for each bar
    #     colors = plt.cm.viridis(np.linspace(0, 1, len(sorted_df)))

    #     # Plot the horizontal histogram on the first subplot
    #     bars = ax.barh(sorted_df.index, sorted_df.values, color=colors)

    #     # Display the total time spent on top of each bar in "X hrs : Y min" format
    #     for bar in bars:
    #         width = bar.get_width()
    #         hours = int(width)
    #         minutes = int((width - hours) * 60)
    #         ax.text(width, bar.get_y() + bar.get_height()/2, f'{hours} hrs : {minutes} min', va='center', ha='left',
    #                 fontsize=15, fontweight='bold', color='white', bbox=dict(facecolor='black', alpha=0.8, boxstyle='round,pad=0.3'))

    #     ax.set_ylabel('Priority', fontsize=15, fontweight='bold')
    #     ax.set_xlabel('Total Time Spent', fontsize=15, fontweight='bold')
    #     ax.set_title('Total Time Spent per Priority', fontsize=16, fontweight='bold')
    #     ax.set_yticklabels(sorted_df.index, fontsize=15) # Adjust y-axis labels for better readability

    #     # Set a gradient background
    #     ax.set_facecolor('lightgray')
    #     ax.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.5)

    #     # Display the figure in Streamlit
    #     st.pyplot(fig)
        

    if st.button("Give Me Last 7 Day Audit 🧮"):
        df7 = db_manager.fetch_last_seven()
        grouped_df = df7.groupby('priority')['time_spent'].sum()

        # Sort the data by total time spent
        sorted_df = grouped_df.sort_values(ascending=False)

        # Create a figure and a set of subplots
        fig, ax = plt.subplots(figsize=(15, 11))

        # Define a list of colors for each bar
        colors = plt.cm.viridis(np.linspace(0, 1, len(sorted_df)))

        # Plot the histogram on the first subplot
        bars = ax.bar(sorted_df.index, sorted_df.values, color=colors)

        # Display the total time spent on top of each bar in "X hrs : Y min" format
        for bar in bars:
            height = bar.get_height()
            hours = int(height)
            minutes = int((height - hours) * 60)
            ax.text(bar.get_x() + bar.get_width()/2, height, f'{hours} hrs : {minutes} min', ha='center', va='bottom',
                    fontsize=15, fontweight='bold', color='white', bbox=dict(facecolor='black', alpha=0.8, boxstyle='round,pad=0.5'))

        ax.set_xlabel('Priority', fontsize=15, fontweight='bold')
        ax.set_ylabel('Total Time Spent', fontsize=15, fontweight='bold')
        ax.set_title('Total Time Spent per Priority', fontsize=20, fontweight='bold')
        
        # Set the x-ticks to match the number of labels
        ax.set_xticks(range(len(sorted_df.index)))
        ax.set_xticklabels(sorted_df.index, rotation=35, fontsize=14, fontweight='bold') # Rotate x-axis labels for better readability

        # Set a gradient background
        ax.set_facecolor('lightgray')
        ax.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.5)

        # Display the figure in Streamlit
        st.pyplot(fig)



        @st.cache_data
        def convert_df(df):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_csv().encode('utf-8')

        csv = convert_df(pd.read_csv('dailyaudits.csv'))

        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f'daily_audits_till_{datetime.today().strftime("%y-%m-%d")}.csv',
            mime='text/csv',
        )

# Main Streamlit app
def main():
    st.markdown("# Self Audit is Self Transformation")
    st.markdown(f"#### :orange[*{today}*]")
    st.write("")
    st.write("")
    st.write("")
    tab1, tab2, tab3 = st.tabs(["Edit Priority List", "Daily Audits", "Weekly Audit Report"])
    with tab1:
        edit_priority_list()

    with tab2:
        update_daily_audits()

    with tab3:
        display_weekly_audit_report()

if __name__ == "__main__":
    main()


# - Manully set Start and End Task Time ⭐⭐⭐⭐⭐
# - Specific Entry Deletion ISSUE 🔴 : Deletes Entire Database 