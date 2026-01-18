import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random
import sqlite3
import os
from io import BytesIO

# Import utility modules
from utils.data_parser import LeadParser
from utils.dialer_simulator import DialerSimulator

# Page configuration
st.set_page_config(
    page_title="Auto Dialer Pro",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'contacts' not in st.session_state:
    st.session_state.contacts = pd.DataFrame()
if 'dialer' not in st.session_state:
    st.session_state.dialer = DialerSimulator()
if 'call_log' not in st.session_state:
    st.session_state.call_log = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'campaign_active' not in st.session_state:
    st.session_state.campaign_active = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = 'agent'  # 'agent' or 'admin'
if 'agents' not in st.session_state:
    st.session_state.agents = {
        'agent1': {'calls_today': 42, 'active': True, 'subscription': 'monthly'},
        'agent2': {'calls_today': 28, 'active': False, 'subscription': 'annual'},
        'agent3': {'calls_today': 15, 'active': True, 'subscription': 'monthly'}
    }

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #374151;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .call-status-box {
        background-color: #F3F4F6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #3B82F6;
        margin-bottom: 1rem;
    }
    .contact-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .stButton button {
        width: 100%;
        border-radius: 5px;
        font-weight: bold;
    }
    .dialing-animation {
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# Main Header
st.markdown('<h1 class="main-header">📞 Auto Dialer Pro</h1>', unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/phone.png", width=80)
    st.markdown("### Navigation")
    
    page = st.radio(
        "Go to",
        ["🏠 Dashboard", "📋 Contact Manager", "📞 Dialer Control", "📊 Admin Dashboard", "⚙️ Settings"]
    )
    
    # User role switcher (for demo)
    st.markdown("---")
    st.session_state.user_role = st.selectbox(
        "User Role (Demo)",
        ["agent", "admin"],
        index=0 if st.session_state.user_role == 'agent' else 1
    )
    
    # Campaign status
    st.markdown("---")
    status_color = "🟢" if st.session_state.campaign_active else "🔴"
    st.markdown(f"### Campaign Status: {status_color}")
    
    if st.session_state.campaign_active:
        if st.button("⏸️ Pause Campaign", use_container_width=True):
            st.session_state.campaign_active = False
            st.rerun()
    else:
        if st.button("▶️ Start Campaign", use_container_width=True) and len(st.session_state.contacts) > 0:
            st.session_state.campaign_active = True
            st.session_state.current_index = 0
            st.rerun()

# PAGE 1: Dashboard
if page == "🏠 Dashboard":
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Contacts", len(st.session_state.contacts))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        calls_today = len(st.session_state.dialer.call_history)
        st.metric("Calls Today", calls_today)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        if calls_today > 0:
            answered = len([c for c in st.session_state.dialer.call_history if c['answered']])
            success_rate = (answered / calls_today) * 100
        else:
            success_rate = 0
        st.metric("Answer Rate", f"{success_rate:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Active Campaign", "Running" if st.session_state.campaign_active else "Paused")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Call Statistics Chart
    st.markdown('<h3 class="sub-header">📈 Call Statistics</h3>', unsafe_allow_html=True)
    
    if st.session_state.dialer.call_history:
        # Create time-series data
        calls_by_hour = {}
        for call in st.session_state.dialer.call_history:
            hour = call['start_time'].strftime("%H:00")
            calls_by_hour[hour] = calls_by_hour.get(hour, 0) + 1
        
        # Create Plotly chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(calls_by_hour.keys()),
            y=list(calls_by_hour.values()),
            name="Calls per Hour",
            marker_color='#3B82F6'
        ))
        
        fig.update_layout(
            title="Call Volume by Hour",
            xaxis_title="Time of Day",
            yaxis_title="Number of Calls",
            template="plotly_white",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No call data yet. Start dialing to see statistics!")
    
    # Recent Activity
    st.markdown('<h3 class="sub-header">🕐 Recent Activity</h3>', unsafe_allow_html=True)
    
    if st.session_state.dialer.call_history:
        recent_calls = st.session_state.dialer.call_history[-5:]  # Last 5 calls
        for call in reversed(recent_calls):
            status = "✅ Answered" if call['answered'] else "❌ Not Answered"
            with st.expander(f"{call['contact'].get('name', 'Unknown')} - {call['contact']['phone']} - {status}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Time:** {call['start_time'].strftime('%I:%M %p')}")
                    st.write(f"**Duration:** {call['duration']:.1f}s")
                with col2:
                    st.write(f"**Attempts:** {len(call['attempts'])}")
                    st.write(f"**State:** {call['contact'].get('state', 'N/A')}")
    else:
        st.info("No recent calls. Start your campaign!")

# PAGE 2: Contact Manager
elif page == "📋 Contact Manager":
    st.markdown('<h2 class="sub-header">📥 Import Contacts</h2>', unsafe_allow_html=True)
    
    # File Upload Section
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file",
        type=['csv', 'xls', 'xlsx'],
        help="Upload your lead file. System will auto-detect columns."
    )
    
    if uploaded_file is not None:
        # Parse the uploaded file
        contacts_df, mapping = LeadParser.parse_uploaded_file(uploaded_file)
        
        if contacts_df is not None:
            st.success(f"✅ Successfully parsed {len(contacts_df)} contacts!")
            
            # Show detected mapping
            with st.expander("📊 Detected Field Mapping"):
                st.write("System detected these columns:")
                st.json(mapping)
            
            # Manual mapping override
            st.markdown("### 🔧 Manual Field Mapping (Optional)")
            col1, col2, col3 = st.columns(3)
            
            # You could add manual mapping controls here
            
            # Preview data
            st.markdown("### 👁️ Data Preview")
            st.dataframe(contacts_df[['id', 'name', 'phone', 'state']].head(10), use_container_width=True)
            
            # Save to session state
            if st.button("💾 Save to Campaign", type="primary"):
                st.session_state.contacts = contacts_df
                st.session_state.current_index = 0
                st.success(f"✅ {len(contacts_df)} contacts loaded for dialing!")
                st.rerun()
        else:
            st.error("Failed to parse the file. Please check the format.")
    
    # Current Contacts Management
    if not st.session_state.contacts.empty:
        st.markdown('<h2 class="sub-header">📋 Current Contact List</h2>', unsafe_allow_html=True)
        
        # Search and filter
        search_term = st.text_input("🔍 Search contacts by name or phone:")
        
        filtered_contacts = st.session_state.contacts
        if search_term:
            mask = (filtered_contacts['name'].str.contains(search_term, case=False)) | \
                   (filtered_contacts['phone'].str.contains(search_term, case=False))
            filtered_contacts = filtered_contacts[mask]
        
        # Show filtered contacts
        st.dataframe(
            filtered_contacts[['id', 'name', 'phone', 'state']],
            use_container_width=True,
            height=400
        )
        
        # Export option
        if st.button("📤 Export Contacts"):
            csv = filtered_contacts[['name', 'phone', 'state']].to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="contacts_export.csv",
                mime="text/csv"
            )

# PAGE 3: Dialer Control
elif page == "📞 Dialer Control":
    st.markdown('<h2 class="sub-header">🎯 Dialer Control Panel</h2>', unsafe_allow_html=True)
    
    if st.session_state.contacts.empty:
        st.warning("⚠️ No contacts loaded. Please import contacts first!")
        st.stop()
    
    # Dialer Settings
    col1, col2, col3 = st.columns(3)
    
    with col1:
        max_redials = st.selectbox(
            "🔁 Redial Attempts",
            options=[0, 1, 2],
            index=2,
            format_func=lambda x: ["Single Dial", "Double Dial", "Triple Dial"][x],
            help="Number of redial attempts before moving to next contact"
        )
    
    with col2:
        dialing_mode = st.selectbox(
            "📱 Dialing Mode",
            options=["preview", "progressive", "predictive"],
            index=0,
            help="Preview: Agent clicks to dial each contact\nProgressive: Auto-dial with delay\nPredictive: Auto-dial based on availability"
        )
    
    with col3:
        call_delay = st.slider(
            "⏱️ Delay Between Calls (seconds)",
            min_value=1,
            max_value=60,
            value=5,
            help="Time to wait before dialing next contact"
        )
    
    # Current Contact Display
    current_contact = None
    if st.session_state.current_index < len(st.session_state.contacts):
        current_contact = st.session_state.contacts.iloc[st.session_state.current_index].to_dict()
    
    # Call Status Box
    st.markdown('<div class="call-status-box">', unsafe_allow_html=True)
    
    col_status1, col_status2 = st.columns([2, 1])
    
    with col_status1:
        if st.session_state.dialer.is_dialing:
            st.markdown(f"### 🔄 {st.session_state.dialer.current_call['status'].upper()}")
            
            if current_contact:
                st.markdown(f"**Contact:** {current_contact.get('name', 'Unknown')}")
                st.markdown(f"**Number:** {current_contact['phone']}")
                st.markdown(f"**State:** {current_contact.get('state', 'N/A')}")
                
                # Pre-dial announcement simulation
                with st.chat_message("assistant"):
                    st.write(f"*Pre-dial announcement:* Calling **{current_contact.get('name', 'Unknown')}** from **{current_contact.get('state', 'N/A')}**...")
        
        elif st.session_state.dialer.current_call and st.session_state.dialer.current_call['answered']:
            st.markdown("### ✅ CALL ANSWERED")
            st.markdown("### 📱 Screen Pop Active")
            
            # Screen Pop Simulation
            contact = st.session_state.dialer.current_call['contact']
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.info(f"**Name:** {contact.get('name', 'Unknown')}")
                st.info(f"**Phone:** {contact['phone']}")
            with col_info2:
                st.info(f"**State:** {contact.get('state', 'N/A')}")
                st.info(f"**Call Duration:** {st.session_state.dialer.current_call.get('duration', 0):.1f}s")
        
        elif current_contact:
            st.markdown("### ⏳ READY TO DIAL")
            st.markdown(f"**Next Contact:** {current_contact.get('name', 'Unknown')}")
            st.markdown(f"**Phone:** {current_contact['phone']}")
            st.markdown(f"**Progress:** {st.session_state.current_index + 1} of {len(st.session_state.contacts)}")
    
    with col_status2:
        # Progress circle
        if not st.session_state.contacts.empty:
            progress = (st.session_state.current_index + 1) / len(st.session_state.contacts)
            st.markdown(f"""
            <div style="text-align: center;">
                <div style="font-size: 2rem; font-weight: bold; color: #3B82F6;">
                    {st.session_state.current_index + 1}/{len(st.session_state.contacts)}
                </div>
                <div style="font-size: 0.9rem; color: #6B7280;">
                    Contacts
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.progress(progress)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Dialer Control Buttons
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
    
    with col_btn1:
        if st.button("📞 Dial Now", type="primary", use_container_width=True):
            if current_contact and not st.session_state.dialer.is_dialing:
                st.session_state.dialer.start_dialing(current_contact, max_redials)
                st.rerun()
    
    with col_btn2:
        if st.button("🔄 Redial", use_container_width=True, 
                    disabled=not (st.session_state.dialer.current_call and 
                                 st.session_state.dialer.current_call['status'] == 'failed')):
            if current_contact:
                st.session_state.dialer.start_dialing(current_contact, max_redials)
                st.rerun()
    
    with col_btn3:
        if st.button("⏭️ Skip", use_container_width=True):
            if st.session_state.current_index < len(st.session_state.contacts) - 1:
                st.session_state.current_index += 1
                st.session_state.dialer.reset()
                st.rerun()
    
    with col_btn4:
        if st.button("⏹️ End Call", use_container_width=True, 
                    disabled=not st.session_state.dialer.is_dialing):
            st.session_state.dialer.is_dialing = False
            st.session_state.dialer._log_call()
            st.rerun()
    
    # Campaign Auto-dialer
    st.markdown("---")
    st.markdown("###  Campaign Auto-Dialer")
    
    if st.session_state.campaign_active:
        st.warning("⚠️ Campaign is running in auto mode")
        
        # Simulate auto-dialing
        if not st.session_state.dialer.is_dialing:
            time.sleep(1)  # Simulate delay
            if st.session_state.current_index < len(st.session_state.contacts):
                current_contact = st.session_state.contacts.iloc[st.session_state.current_index].to_dict()
                st.session_state.dialer.start_dialing(current_contact, max_redials)
                
                # Check if call completed
                if not st.session_state.dialer.is_dialing:
                    st.session_state.current_index += 1
                    
                    # Check if campaign completed
                    if st.session_state.current_index >= len(st.session_state.contacts):
                        st.session_state.campaign_active = False
                        st.success("✅ Campaign completed all contacts!")
                
                st.rerun()
    else:
        if st.button("🚀 Start Auto Campaign", type="secondary", use_container_width=True):
            st.session_state.campaign_active = True
            st.session_state.current_index = 0
            st.rerun()

# PAGE 4: Admin Dashboard
elif page == "📊 Admin Dashboard":
    if st.session_state.user_role != 'admin':
        st.warning("🔒 Admin access required. Switch to admin role in sidebar.")
        st.stop()
    
    st.markdown('<h2 class="sub-header">👨‍💼 Admin Dashboard</h2>', unsafe_allow_html=True)
    
    # Agent Management
    st.markdown("### 👥 Agent Management")
    
    # Add new agent
    with st.expander("➕ Add New Agent"):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_agent_id = st.text_input("Agent ID")
        with col2:
            new_agent_subscription = st.selectbox("Subscription", ["monthly", "annual"])
        with col3:
            if st.button("Add Agent"):
                if new_agent_id:
                    st.session_state.agents[new_agent_id] = {
                        'calls_today': 0,
                        'active': True,
                        'subscription': new_agent_subscription
                    }
                    st.success(f"Agent {new_agent_id} added!")
                    st.rerun()
    
    # Display agents
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("**Active Agents**")
        for agent_id, agent_data in st.session_state.agents.items():
            status = "🟢" if agent_data['active'] else "🔴"
            with st.container():
                cols = st.columns([1, 2, 1, 1])
                cols[0].write(f"{status} {agent_id}")
                cols[1].write(f"Calls Today: {agent_data['calls_today']}")
                cols[2].write(f"Sub: {agent_data['subscription']}")
                with cols[3]:
                    if st.button("❌", key=f"del_{agent_id}"):
                        del st.session_state.agents[agent_id]
                        st.rerun()
    
    with col2:
        st.markdown("**Agent Stats**")
        st.metric("Total Agents", len(st.session_state.agents))
        active_agents = sum(1 for a in st.session_state.agents.values() if a['active'])
        st.metric("Active Now", active_agents)
        total_calls = sum(a['calls_today'] for a in st.session_state.agents.values())
        st.metric("Total Calls", total_calls)
    
    # Billing Overview
    st.markdown("### 💰 Billing Overview")
    
    col_b1, col_b2, col_b3 = st.columns(3)
    
    with col_b1:
        st.metric("Monthly Revenue", f"${len([a for a in st.session_state.agents.values() if a['subscription'] == 'monthly']) * 29.99:.2f}")
    
    with col_b2:
        st.metric("Annual Revenue", f"${len([a for a in st.session_state.agents.values() if a['subscription'] == 'annual']) * 299.99:.2f}")
    
    with col_b3:
        total_rev = (len([a for a in st.session_state.agents.values() if a['subscription'] == 'monthly']) * 29.99 +
                    len([a for a in st.session_state.agents.values() if a['subscription'] == 'annual']) * 299.99)
        st.metric("Total Revenue", f"${total_rev:.2f}")
    
    # Activity Log
    st.markdown("### 📋 Recent System Activity")
    
    # Simulated activity log
    activities = [
        {"time": "10:30 AM", "agent": "agent1", "action": "Started campaign", "details": "100 contacts"},
        {"time": "10:45 AM", "agent": "agent2", "action": "Uploaded leads", "details": "CSV file"},
        {"time": "11:15 AM", "agent": "agent1", "action": "Call answered", "details": "Duration: 45s"},
        {"time": "11:30 AM", "agent": "agent3", "action": "Subscription renewed", "details": "Annual plan"},
        {"time": "12:00 PM", "agent": "admin", "action": "Added new agent", "details": "agent4 added"},
    ]
    
    for activity in activities:
        with st.expander(f"{activity['time']} - {activity['agent']} - {activity['action']}"):
            st.write(f"**Details:** {activity['details']}")

# PAGE 5: Settings
elif page == "⚙️ Settings":
    st.markdown('<h2 class="sub-header">⚙️ System Settings</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Dialer Settings", "Billing", "Integration"])
    
    with tab1:
        st.markdown("### 📞 Dialer Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.number_input("Max Calls Per Hour", min_value=1, max_value=1000, value=100)
            st.number_input("Daily Call Limit", min_value=1, max_value=5000, value=1000)
            st.time_input("Start Time", value=datetime.strptime("09:00", "%H:%M").time())
            st.time_input("End Time", value=datetime.strptime("17:00", "%H:%M").time())
        
        with col2:
            st.checkbox("Enable Call Recording", value=False)
            st.checkbox("Auto-redial busy numbers", value=True)
            st.checkbox("Skip invalid numbers", value=True)
            st.checkbox("Require confirmation before dial", value=False)
    
    with tab2:
        st.markdown("### 💳 Billing Configuration")
        
        monthly_price = st.number_input("Monthly Subscription Price ($)", min_value=0.0, value=29.99, step=0.01)
        annual_price = st.number_input("Annual Subscription Price ($)", min_value=0.0, value=299.99, step=0.01)
        
        st.markdown("**Payment Processor**")
        payment_provider = st.selectbox("Select Provider", ["Stripe", "PayPal", "Authorize.net"])
        
        if payment_provider == "Stripe":
            st.info("Integration with Stripe API required. Webhooks for payment events.")
        
        st.checkbox("Auto-renew subscriptions", value=True)
        st.checkbox("Send payment reminders", value=True)
        st.checkbox("Pause service on payment failure", value=True)
    
    with tab3:
        st.markdown("### 🔗 VoIP Integration")
        
        voip_provider = st.selectbox(
            "VoIP Service Provider",
            ["Twilio", "Plivo", "Vonage", "Bandwidth.com", "Custom"]
        )
        
        if voip_provider:
            st.info(f"Selected: **{voip_provider}**")
            
            if voip_provider == "Twilio":
                st.text_input("Account SID", type="password")
                st.text_input("Auth Token", type="password")
                st.text_input("Twilio Phone Number")
            
            # Test connection
            if st.button("Test VoIP Connection", type="secondary"):
                st.success("✅ Connection test successful (simulated)")
        
        st.markdown("---")
        st.markdown("#### Webhook Configuration")
        st.text_input("Call Answer Webhook URL", value="https://your-domain.com/webhook/answer")
        st.text_input("Call Status Webhook URL", value="https://your-domain.com/webhook/status")

