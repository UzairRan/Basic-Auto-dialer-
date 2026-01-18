import pandas as pd
import streamlit as st
from io import BytesIO
import re

class LeadParser:
    """Flexible CSV/Excel parser for multiple lead source formats"""
    
    # Common column name variations
    PHONE_VARIANTS = ['phone', 'Phone', 'PHONE', 'Phone Number', 'phone_number', 
                      'PhoneNumber', 'Phone No', 'phone_no', 'telephone', 'Tel', 
                      'cell', 'Cell', 'mobile', 'Mobile', 'contact', 'Contact']
    
    NAME_VARIANTS = ['name', 'Name', 'NAME', 'full_name', 'Full Name', 
                     'fullname', 'FullName', 'contact_name', 'Contact Name', 
                     'first_name', 'first name', 'First Name']
    
    STATE_VARIANTS = ['state', 'State', 'STATE', 'st', 'St', 'State Code', 
                      'state_code', 'location', 'Location', 'region', 'Region']
    
    @staticmethod
    def clean_phone_number(phone):
        """Clean and validate phone numbers"""
        if pd.isna(phone):
            return None
        
        # Convert to string and remove non-numeric
        phone_str = str(phone)
        digits = re.sub(r'\D', '', phone_str)
        
        # Handle US numbers (add +1 if missing)
        if len(digits) == 10:
            return f"+1{digits}"
        elif len(digits) == 11 and digits.startswith('1'):
            return f"+{digits}"
        elif digits.startswith('+'):
            return digits
        else:
            return f"+{digits}" if digits else None
    
    @staticmethod
    def detect_column_mapping(df):
        """Auto-detect column mappings based on common variants"""
        mapping = {'phone': None, 'name': None, 'state': None}
        
        for col in df.columns:
            col_lower = str(col).lower().replace(' ', '_').replace('-', '_')
            
            # Check phone variants
            for variant in LeadParser.PHONE_VARIANTS:
                if variant.lower() in col_lower:
                    mapping['phone'] = col
                    break
            
            # Check name variants
            for variant in LeadParser.NAME_VARIANTS:
                if variant.lower() in col_lower:
                    mapping['name'] = col
                    break
            
            # Check state variants
            for variant in LeadParser.STATE_VARIANTS:
                if variant.lower() in col_lower:
                    mapping['state'] = col
                    break
        
        return mapping
    
    @staticmethod
    def parse_uploaded_file(uploaded_file):
        """Parse uploaded CSV or Excel file with flexible mapping"""
        try:
            # Read file based on type
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(uploaded_file, engine='openpyxl')
            else:
                return None, "Unsupported file format"
            
            # Auto-detect column mapping
            mapping = LeadParser.detect_column_mapping(df)
            
            # Create standardized dataframe
            result_df = pd.DataFrame()
            
            # Map phone column
            if mapping['phone']:
                result_df['phone'] = df[mapping['phone']].apply(LeadParser.clean_phone_number)
            else:
                # Try to find any column that looks like phone numbers
                for col in df.columns:
                    sample_val = str(df[col].iloc[0]) if len(df) > 0 else ''
                    if any(char.isdigit() for char in sample_val) and len(str(sample_val)) >= 10:
                        result_df['phone'] = df[col].apply(LeadParser.clean_phone_number)
                        mapping['phone'] = col
                        break
            
            # Map name column
            if mapping['name']:
                result_df['name'] = df[mapping['name']].fillna('Unknown')
            else:
                result_df['name'] = 'Unknown'
            
            # Map state column
            if mapping['state']:
                result_df['state'] = df[mapping['state']].fillna('N/A')
            else:
                result_df['state'] = 'N/A'
            
            # Keep original data for reference
            result_df['original_data'] = df.apply(lambda row: row.to_dict(), axis=1)
            
            # Add unique ID
            result_df['id'] = range(1, len(result_df) + 1)
            
            # Filter out invalid phone numbers
            result_df = result_df[result_df['phone'].notna()]
            
            return result_df, mapping
            
        except Exception as e:
            return None, f"Error parsing file: {str(e)}" 