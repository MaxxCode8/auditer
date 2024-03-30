import datetime
import streamlit as st
from dbmanager import DatabaseManager
import pandas as pd
from datetime import datetime
import time
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
            # Sort the priority list
            st.session_state.priority_list.sort()
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
        description = st.text_input("Description")
        submit_button = st.form_submit_button("Start🚀")

        if submit_button:
            # daily_audit_columns = ['priority_cat_str', 'description_str', 'time_spent_timestampsubstration', 'start_time', 'end_time', "date"]
            # Append the new audit to the daily audits DataFrame
            new_audit = {
                'priority': priority, 'description': description, 
                'time_spent': "N0ne", 'start_time': time.time(),    # current timestamp
                'end_time': "N0ne",
                'date': pd.to_datetime('today').strftime('%Y-%m-%d')}

            new_audit_df = pd.DataFrame([new_audit])

            if st.session_state.daily_audits_df.empty:
                st.session_state.daily_audits_df = new_audit_df
            else:
                st.session_state.daily_audits_df = pd.concat([st.session_state.daily_audits_df, new_audit_df], ignore_index=True)

            db_manager.write_daily_audits(st.session_state.daily_audits_df)
            st.success("Audit added successfully.")
            # Update the session state with the new list
            st.session_state.daily_audits_df = db_manager.read_daily_audits()
            # Reload the page to show the updated list
            st.rerun() # REFRESEHs the page

    # Display existing audits
    if st.session_state.daily_audits_df.empty:
        st.info("No audits found.")
    else:   
        st.markdown("### Priority🧘‍♀️                  Description📃            Time Spent ⏲")
        for index, row in st.session_state.daily_audits_df.iterrows():
            col1, col2, col3, col4 = st.columns([2,3,2,1])
            with col1:
                st.markdown(f"##### :violet[{row['priority']}]")
            with col2:
                st.markdown(f"##### :green[{row['description']}]")
            with col3:
                # st.write(row['end_time'])
                if row['end_time'] == "N0ne":
                    taskend = st.button("✅ :blue[**End Task**]", key=index)
                    if taskend:
                        st.session_state.daily_audits_df.loc[index, "end_time"] = time.time()
                        start_time = float(st.session_state.daily_audits_df.loc[index, "start_time"])
                        end_time = float(st.session_state.daily_audits_df.loc[index, "end_time"])
                        time_spent = round((end_time-start_time) / 3600,2)
                        # Update the session dataframe
                        st.session_state.daily_audits_df.loc[index, "time_spent"] = time_spent
                        st.rerun()
                        # Session dataframe still not updated in the csv
                else:                    
                    st.markdown(f"##### :orange[{row['time_spent']} hours]")
            with col4:
                if st.button(f"❌", key=f"delete_audit_{index}"):
                    # Delete the audit from the DataFrame
                    st.session_state.daily_audits_df.drop(index, inplace=True)
                    db_manager.write_daily_audits(st.session_state.daily_audits_df)
                    st.success(f"Audit {index} deleted successfully.")
                    # Update the session state with the new list
                    st.session_state.daily_audits_df = db_manager.read_daily_audits()
                    # Reload the page to show the updated list
                    st.rerun()


# Function to display weekly audit report
def display_weekly_audit_report():
    # Example: Read the weekly audits and display them
    weekly_audits = db_manager.read_weekly_audits()
    st.write(weekly_audits)

# Main Streamlit app
def main():
    st.markdown("# Auditer...")
    st.markdown(f"#### :orange[*{today}*]")
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
