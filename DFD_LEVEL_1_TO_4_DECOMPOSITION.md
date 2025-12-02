# DATA FLOW DIAGRAM DECOMPOSITION
## Silay DRRMO Flood Monitoring System with GIS
### Level 1 to Level 4 Expansion (Admin Side)

---

## TABLE OF CONTENTS
1. [Context Diagram (Level 0)](#context-diagram-level-0)
2. [Level 1 DFD - System Overview](#level-1-dfd---system-overview)
3. [Level 2 DFD - Process Decomposition](#level-2-dfd---process-decomposition)
4. [Level 3 DFD - Detailed Sub-Processes](#level-3-dfd---detailed-sub-processes)
5. [Level 4 DFD - Atomic Processes](#level-4-dfd---atomic-processes)

---

## CONTEXT DIAGRAM (Level 0)

```
┌─────────────────┐
│   Admin User    │
│  (Regular User) │
└────────┬────────┘
         │
         │ Login credentials, commands, settings
         │
         ↓
    ┌────────────────────────────────────────────┐
    │                                            │
    │    0.0 Flood Risk Management &            │
    │        Monitoring System                   │
    │                                            │
    └─┬──────────────────────────────────────┬───┘
      │                                      │
      │ Dashboards, reports,                 │
      │ analytics, alerts                    │
      │                                      │
      ↓                                      ↓
┌──────────────┐                    ┌────────────────┐
│ Open-Meteo   │──Rainfall data────>│                │
│     API      │                    │                │
└──────────────┘                    │                │
                                    │                │
┌──────────────┐                    │                │
│ WorldTides   │──Tide level data──>│   EXTERNAL     │
│     API      │                    │     DATA       │
└──────────────┘                    │   SOURCES      │
                                    │                │
┌──────────────┐                    │                │
│  MGB GIS     │<──GIS requests─────│                │
│  Data Source │──Boundaries/maps──>│                │
└──────────────┘                    └────────────────┘
```

### External Entities:
- **Admin User / Regular User**: System operators and stakeholders
- **Open-Meteo API**: Weather and rainfall data provider
- **WorldTides API**: Tide level data provider
- **MGB GIS Data Source**: Geographic Information System data repository

---

## LEVEL 1 DFD - SYSTEM OVERVIEW

### Processes:
1. **1.0 Authenticate**
2. **2.0 Flood Risk Map Assessment**
3. **3.0 Generating Reports and Certifications**
4. **4.0 Flood Risk and Flood Record Monitoring**
5. **5.0 User Management**
6. **6.0 Users Activity History Management**
7. **7.0 Benchmark Settings Adjustment**

### Data Stores:
- **D1** Users
- **D2** Barangays
- **D3** Flood Susceptibilities
- **D4** Assessment Records
- **D5** Report Records
- **D6** Certificate Records
- **D7** Rainfall Data
- **D8** Weather Data
- **D9** Tide Level Data
- **D10** Flood Records
- **D11** Benchmark Settings
- **D12** User Activity Logs
- **D13** Login Attempts

### External Entities:
- Admin/User
- Open-Meteo API
- WorldTides API
- MGB GIS Layers

---

## LEVEL 2 DFD - PROCESS DECOMPOSITION

### 1.0 AUTHENTICATE

#### Sub-Processes:
- **1.1 Validate Login Credentials**
  - Input: Username, password, IP address
  - Output: Authentication token, user session
  - Data Stores: D1 Users, D13 Login Attempts
  
- **1.2 Manage User Session**
  - Input: Session token, user activity
  - Output: Session status, timeout signals
  - Data Stores: D1 Users
  
- **1.3 Track Login Attempts**
  - Input: Login attempt details, IP address
  - Output: Security alerts, lockout signals
  - Data Stores: D13 Login Attempts
  
- **1.4 Enforce Access Control**
  - Input: User role, requested resource
  - Output: Access granted/denied
  - Data Stores: D1 Users

---

### 2.0 FLOOD RISK MAP ASSESSMENT

#### Sub-Processes:
- **2.1 Load GIS Layers**
  - Input: Map viewport, zoom level
  - Output: Barangay boundaries, flood susceptibility polygons
  - Data Stores: D2 Barangays, D3 Flood Susceptibilities
  
- **2.2 Perform Spatial Query**
  - Input: Latitude, longitude coordinates
  - Output: Location details, intersecting features
  - Data Stores: D2 Barangays, D3 Flood Susceptibilities
  
- **2.3 Calculate Risk Assessment**
  - Input: Coordinates, flood susceptibility code
  - Output: Risk level, classification, recommendations
  - Data Stores: D3 Flood Susceptibilities
  
- **2.4 Record Assessment Activity**
  - Input: User ID, location, risk assessment results
  - Output: Assessment record ID
  - Data Stores: D4 Assessment Records, D12 User Activity Logs

---

### 3.0 GENERATING REPORTS AND CERTIFICATIONS

#### Sub-Processes:
- **3.1 Generate Flood Risk Report**
  - Input: Assessment data, barangay, coordinates
  - Output: PDF report with risk analysis
  - Data Stores: D4 Assessment Records, D5 Report Records
  
- **3.2 Generate Certificate of Flood Susceptibility**
  - Input: Establishment name, address, assessment data
  - Output: Official PDF certificate
  - Data Stores: D4 Assessment Records, D6 Certificate Records
  
- **3.3 Export Historical Records**
  - Input: Date range, filters (barangay, user, risk level)
  - Output: CSV/PDF export files
  - Data Stores: D4 Assessment Records, D5 Report Records, D6 Certificate Records
  
- **3.4 Log Report Generation**
  - Input: User ID, report type, parameters
  - Output: Activity log entry
  - Data Stores: D5 Report Records, D6 Certificate Records, D12 User Activity Logs

---

### 4.0 FLOOD RISK AND FLOOD RECORD MONITORING

#### Sub-Processes:
- **4.1 Fetch External API Data**
  - Input: Location coordinates, API keys
  - Output: Raw rainfall, weather, tide data
  - External: Open-Meteo API, WorldTides API
  
- **4.2 Process and Store Sensor Data**
  - Input: Raw API responses
  - Output: Normalized sensor readings
  - Data Stores: D7 Rainfall Data, D8 Weather Data, D9 Tide Level Data
  
- **4.3 Calculate Real-time Risk Levels**
  - Input: Current rainfall, tide levels, benchmark thresholds
  - Output: Combined risk assessment (Low/Moderate/High)
  - Data Stores: D7 Rainfall Data, D9 Tide Level Data, D11 Benchmark Settings
  
- **4.4 Manage Flood Event Records**
  - Input: Event details, casualties, damages
  - Output: Historical flood record
  - Data Stores: D10 Flood Records
  
- **4.5 Generate Monitoring Dashboard**
  - Input: Real-time data, historical trends
  - Output: Interactive visualizations, alerts
  - Data Stores: D7, D8, D9, D10 (All monitoring data)

---

### 5.0 USER MANAGEMENT

#### Sub-Processes:
- **5.1 Register New User**
  - Input: User details, registration form
  - Output: Pending user account, auto-generated Staff ID
  - Data Stores: D1 Users
  
- **5.2 Approve/Reject User Accounts**
  - Input: User ID, approval decision
  - Output: Activated/deleted user account
  - Data Stores: D1 Users, D12 User Activity Logs
  
- **5.3 Manage User Profiles**
  - Input: Profile data, image uploads
  - Output: Updated user information
  - Data Stores: D1 Users
  
- **5.4 Assign Roles and Permissions**
  - Input: User ID, role selection
  - Output: Updated user privileges
  - Data Stores: D1 Users

---

### 6.0 USERS ACTIVITY HISTORY MANAGEMENT

#### Sub-Processes:
- **6.1 Log User Activities**
  - Input: User actions, timestamps
  - Output: Activity log entries
  - Data Stores: D12 User Activity Logs
  
- **6.2 View Activity History**
  - Input: User ID, date range filters
  - Output: Filtered activity list
  - Data Stores: D12 User Activity Logs
  
- **6.3 Archive Historical Activities**
  - Input: Archive criteria, date threshold
  - Output: Archived activity records
  - Data Stores: D12 User Activity Logs
  
- **6.4 Export Activity Reports**
  - Input: Export format, filters
  - Output: CSV/PDF activity report
  - Data Stores: D12 User Activity Logs

---

### 7.0 BENCHMARK SETTINGS ADJUSTMENT

#### Sub-Processes:
- **7.1 View Current Benchmark Settings**
  - Input: Admin request
  - Output: Current threshold values
  - Data Stores: D11 Benchmark Settings
  
- **7.2 Modify Threshold Values**
  - Input: New rainfall/tide thresholds
  - Output: Updated benchmark settings
  - Data Stores: D11 Benchmark Settings
  
- **7.3 Select Risk Calculation Method**
  - Input: Method selection (max, equal, priority-based)
  - Output: Updated calculation algorithm
  - Data Stores: D11 Benchmark Settings
  
- **7.4 Log Configuration Changes**
  - Input: Admin ID, old values, new values
  - Output: Configuration audit trail
  - Data Stores: D11 Benchmark Settings, D12 User Activity Logs

---

## LEVEL 3 DFD - DETAILED SUB-PROCESSES

### 1.1 VALIDATE LOGIN CREDENTIALS

#### Atomic Processes:
- **1.1.1 Receive Login Request**
  - Input: Username, password, IP address
  - Output: Login attempt record
  
- **1.1.2 Query User Database**
  - Input: Username
  - Output: User record or "not found" error
  - Data Store: D1 Users
  
- **1.1.3 Verify Password Hash**
  - Input: Submitted password, stored hash
  - Output: Password match status (true/false)
  
- **1.1.4 Check Account Status**
  - Input: User record
  - Output: Active/inactive, approved/pending status
  - Data Store: D1 Users
  
- **1.1.5 Check Lockout Status**
  - Input: Username, IP address
  - Output: Account locked/unlocked status
  - Data Store: D13 Login Attempts
  
- **1.1.6 Generate Session Token**
  - Input: Validated user ID
  - Output: JWT token, session cookie
  
- **1.1.7 Record Login Attempt**
  - Input: Username, IP, success/failure
  - Output: Login attempt log entry
  - Data Store: D13 Login Attempts

---

### 1.2 MANAGE USER SESSION

#### Atomic Processes:
- **1.2.1 Validate Session Token**
  - Input: Session token from request header
  - Output: Valid/invalid/expired status
  
- **1.2.2 Refresh Session Expiry**
  - Input: User activity timestamp
  - Output: Extended session timeout
  
- **1.2.3 Load User Context**
  - Input: User ID from session
  - Output: User profile, permissions, preferences
  - Data Store: D1 Users
  
- **1.2.4 Destroy Session on Logout**
  - Input: Logout request
  - Output: Cleared session data, revoked token

---

### 2.1 LOAD GIS LAYERS

#### Atomic Processes:
- **2.1.1 Fetch Barangay Boundaries**
  - Input: Map bounds (lat/lon bbox)
  - Output: GeoJSON MultiPolygon features
  - Data Store: D2 Barangays
  
- **2.1.2 Fetch Flood Susceptibility Zones**
  - Input: Map bounds, filter criteria
  - Output: GeoJSON polygons with hazard codes (VHF, HF, MF, LF)
  - Data Store: D3 Flood Susceptibilities
  
- **2.1.3 Serialize Spatial Data**
  - Input: Database geometry objects
  - Output: GeoJSON formatted strings
  
- **2.1.4 Optimize Layer Rendering**
  - Input: Zoom level, viewport size
  - Output: Simplified geometries for performance

---

### 2.2 PERFORM SPATIAL QUERY

#### Atomic Processes:
- **2.2.1 Parse Coordinates**
  - Input: Latitude, longitude strings
  - Output: Validated decimal coordinate pairs
  
- **2.2.2 Create Point Geometry**
  - Input: Lat/lon coordinates
  - Output: PostGIS POINT geometry
  
- **2.2.3 Execute ST_Intersects Query**
  - Input: Point geometry, barangay layer
  - Output: Intersecting barangay record
  - Data Store: D2 Barangays
  
- **2.2.4 Execute ST_Intersects Query (Flood Layer)**
  - Input: Point geometry, flood susceptibility layer
  - Output: Intersecting flood zone record with hazard code
  - Data Store: D3 Flood Susceptibilities

---

### 2.3 CALCULATE RISK ASSESSMENT

#### Atomic Processes:
- **2.3.1 Map Hazard Code to Risk Level**
  - Input: Flood susceptibility code (VHF/HF/MF/LF)
  - Output: Risk classification and description
  
- **2.3.2 Retrieve Recommendation Text**
  - Input: Risk level
  - Output: MGB-standard recommendation and mitigation measures
  
- **2.3.3 Format Assessment Results**
  - Input: All assessment components
  - Output: Structured assessment object

---

### 3.1 GENERATE FLOOD RISK REPORT

#### Atomic Processes:
- **3.1.1 Retrieve Assessment Data**
  - Input: Assessment ID or coordinates
  - Output: Assessment details
  - Data Store: D4 Assessment Records
  
- **3.1.2 Load Report Template**
  - Input: Report type
  - Output: HTML template with placeholders
  
- **3.1.3 Populate Template with Data**
  - Input: Assessment data, user info, timestamp
  - Output: Rendered HTML document
  
- **3.1.4 Convert HTML to PDF**
  - Input: Rendered HTML
  - Output: PDF file with proper formatting
  
- **3.1.5 Save Report Record**
  - Input: User ID, report metadata
  - Output: Report record ID
  - Data Store: D5 Report Records

---

### 3.3 EXPORT HISTORICAL RECORDS

#### Atomic Processes:
- **3.3.1 Parse Export Parameters**
  - Input: Date range, filters, format
  - Output: Validated query parameters
  
- **3.3.2 Query Database Records**
  - Input: Filter criteria
  - Output: Filtered assessment/report records
  - Data Stores: D4, D5, D6
  
- **3.3.3 Format Data for CSV**
  - Input: Query results
  - Output: CSV rows with headers
  
- **3.3.4 Format Data for PDF**
  - Input: Query results
  - Output: PDF table with pagination
  
- **3.3.5 Generate Download Response**
  - Input: Formatted file
  - Output: HTTP response with file attachment

---

### 4.1 FETCH EXTERNAL API DATA

#### Atomic Processes:
- **4.1.1 Construct Open-Meteo API Request**
  - Input: Silay City coordinates, parameters
  - Output: API URL with query string
  
- **4.1.2 Send HTTP GET Request**
  - Input: API URL, timeout settings
  - Output: JSON response or error
  
- **4.1.3 Construct WorldTides API Request**
  - Input: Cebu coordinates, API key, date range
  - Output: API URL with authentication
  
- **4.1.4 Send Authenticated Request**
  - Input: WorldTides URL with API key
  - Output: JSON tide data or error
  
- **4.1.5 Handle API Errors**
  - Input: HTTP error responses
  - Output: Logged errors, retry logic

---

### 4.2 PROCESS AND STORE SENSOR DATA

#### Atomic Processes:
- **4.2.1 Parse JSON Response**
  - Input: Raw API JSON
  - Output: Extracted data fields
  
- **4.2.2 Validate Data Integrity**
  - Input: Parsed data values
  - Output: Validated/sanitized values
  
- **4.2.3 Convert Units**
  - Input: Raw measurements
  - Output: Standardized units (mm, m, °C, kph)
  
- **4.2.4 Create RainfallData Record**
  - Input: Rainfall value, timestamp, station
  - Output: Database record ID
  - Data Store: D7 Rainfall Data
  
- **4.2.5 Create WeatherData Record**
  - Input: Temperature, humidity, wind speed
  - Output: Database record ID
  - Data Store: D8 Weather Data
  
- **4.2.6 Create TideLevelData Record**
  - Input: Tide height, timestamp
  - Output: Database record ID
  - Data Store: D9 Tide Level Data

---

### 4.3 CALCULATE REAL-TIME RISK LEVELS

#### Atomic Processes:
- **4.3.1 Retrieve Latest Rainfall Data**
  - Input: Query timestamp
  - Output: Most recent rainfall value (mm)
  - Data Store: D7 Rainfall Data
  
- **4.3.2 Retrieve Latest Tide Data**
  - Input: Query timestamp
  - Output: Most recent tide level (m)
  - Data Store: D9 Tide Level Data
  
- **4.3.3 Load Benchmark Thresholds**
  - Input: Settings query
  - Output: Moderate and High thresholds for rainfall and tide
  - Data Store: D11 Benchmark Settings
  
- **4.3.4 Apply AND-Based Risk Logic**
  - Input: Rainfall value, tide value, thresholds
  - Output: Combined risk level (Low/Moderate/High)
  - Logic:
    - High: rainfall >= high_threshold AND tide >= high_threshold
    - Moderate: rainfall >= moderate_threshold AND tide >= moderate_threshold
    - Low: Otherwise
  
- **4.3.5 Determine Risk Color**
  - Input: Risk level
  - Output: Color code (red/orange/yellow)
  
- **4.3.6 Format Risk Output**
  - Input: Risk level, color, values
  - Output: Structured risk object for UI

---

### 4.4 MANAGE FLOOD EVENT RECORDS

#### Atomic Processes:
- **4.4.1 Validate Flood Event Form**
  - Input: Event form data
  - Output: Validated event details
  
- **4.4.2 Save Flood Record**
  - Input: Event name, date, affected barangays
  - Output: Flood record ID
  - Data Store: D10 Flood Records
  
- **4.4.3 Update Casualty Statistics**
  - Input: Dead, injured, missing counts
  - Output: Updated record
  - Data Store: D10 Flood Records
  
- **4.4.4 Calculate Total Damages**
  - Input: Infrastructure, agriculture, institutional, commercial damages
  - Output: Total damage value (PHP)
  - Data Store: D10 Flood Records

---

### 5.1 REGISTER NEW USER

#### Atomic Processes:
- **5.1.1 Validate Registration Form**
  - Input: Username, email, password, profile data
  - Output: Validation errors or success
  
- **5.1.2 Check Username Uniqueness**
  - Input: Username
  - Output: Available/taken status
  - Data Store: D1 Users
  
- **5.1.3 Validate Password Strength**
  - Input: Password string
  - Output: Strength score, validation result
  
- **5.1.4 Generate Staff ID**
  - Input: Current year
  - Output: Auto-generated staff ID (e.g., 20250001)
  - Logic: Query last staff ID for year, increment sequential number
  - Data Store: D1 Users
  
- **5.1.5 Hash Password**
  - Input: Plain text password
  - Output: Bcrypt/PBKDF2 hash
  
- **5.1.6 Create User Record**
  - Input: Validated user data, staff ID, password hash
  - Output: User ID
  - Attributes: is_active=False, is_approved=False
  - Data Store: D1 Users

---

### 5.2 APPROVE/REJECT USER ACCOUNTS

#### Atomic Processes:
- **5.2.1 Query Pending Users**
  - Input: Filter criteria (is_approved=False)
  - Output: List of pending user accounts
  - Data Store: D1 Users
  
- **5.2.2 Display Approval Queue**
  - Input: Pending users list
  - Output: Admin approval interface
  
- **5.2.3 Approve User Account**
  - Input: User ID, admin action
  - Output: Updated user record (is_active=True, is_approved=True)
  - Data Store: D1 Users
  
- **5.2.4 Delete Rejected User**
  - Input: User ID, rejection reason
  - Output: Deleted user record
  - Data Store: D1 Users
  
- **5.2.5 Log Approval/Rejection Action**
  - Input: Admin ID, action type, target user
  - Output: Activity log entry
  - Data Store: D12 User Activity Logs

---

### 5.3 MANAGE USER PROFILES

#### Atomic Processes:
- **5.3.1 Load Profile Form**
  - Input: User ID
  - Output: Pre-filled profile form
  - Data Store: D1 Users
  
- **5.3.2 Validate Profile Image**
  - Input: Uploaded image file
  - Output: Validated file (max 5MB, JPG/PNG/GIF)
  - Checks: File size, dimensions (max 4000x4000), extension
  
- **5.3.3 Upload Profile Image**
  - Input: Validated image
  - Output: Saved file path (profile_images/)
  
- **5.3.4 Update User Fields**
  - Input: Bio, contact number, emergency contact, DOB
  - Output: Updated user record
  - Data Store: D1 Users

---

### 6.1 LOG USER ACTIVITIES

#### Atomic Processes:
- **6.1.1 Capture Activity Event**
  - Input: User action trigger (e.g., assessment, report, approval)
  - Output: Activity description string
  
- **6.1.2 Generate Timestamp**
  - Input: System time
  - Output: ISO 8601 timestamp
  
- **6.1.3 Create UserLog Entry**
  - Input: User ID, action description, timestamp
  - Output: Log record ID
  - Data Store: D12 User Activity Logs

---

### 6.3 ARCHIVE HISTORICAL ACTIVITIES

#### Atomic Processes:
- **6.3.1 Query Old Activity Records**
  - Input: Archive threshold date
  - Output: Records older than threshold
  - Data Store: D12 User Activity Logs
  
- **6.3.2 Mark Records as Archived**
  - Input: Record IDs
  - Output: Updated records (is_archived=True, archived_at=timestamp)
  - Data Store: D12 User Activity Logs
  
- **6.3.3 Filter Active Records**
  - Input: User query
  - Output: Non-archived records only (is_archived=False)
  - Data Store: D12 User Activity Logs

---

### 7.1 VIEW CURRENT BENCHMARK SETTINGS

#### Atomic Processes:
- **7.1.1 Query Benchmark Settings**
  - Input: Settings ID (singleton, pk=1)
  - Output: Current threshold values
  - Data Store: D11 Benchmark Settings
  
- **7.1.2 Format Settings Display**
  - Input: Settings object
  - Output: Formatted UI with current values
  - Fields:
    - rainfall_moderate_threshold (default: 30mm)
    - tide_moderate_threshold (default: 1.0m)
    - rainfall_high_threshold (default: 50mm)
    - tide_high_threshold (default: 1.5m)
    - combined_risk_method (default: max)

---

### 7.2 MODIFY THRESHOLD VALUES

#### Atomic Processes:
- **7.2.1 Validate Threshold Inputs**
  - Input: New threshold values
  - Output: Validated numbers (positive, logical order)
  - Checks: Moderate < High, rainfall > 0, tide > 0
  
- **7.2.2 Update Settings Record**
  - Input: Validated thresholds
  - Output: Updated benchmark settings
  - Data Store: D11 Benchmark Settings
  
- **7.2.3 Record Updated By Admin**
  - Input: Admin username
  - Output: Updated updated_by field
  - Data Store: D11 Benchmark Settings

---

### 7.3 SELECT RISK CALCULATION METHOD

#### Atomic Processes:
- **7.3.1 Display Method Options**
  - Input: Available calculation methods
  - Output: Radio button selection UI
  - Options:
    - max (Maximum of both)
    - rainfall_priority (80% rainfall, 20% tide)
    - tide_priority (20% rainfall, 80% tide)
    - equal (50% rainfall, 50% tide)
  
- **7.3.2 Update Calculation Method**
  - Input: Selected method
  - Output: Updated combined_risk_method field
  - Data Store: D11 Benchmark Settings
  
- **7.3.3 Apply Method to Risk Calculations**
  - Input: Updated method
  - Output: Recalculated risk assessments using new method

---

## LEVEL 4 DFD - ATOMIC PROCESSES

### 1.1.2 QUERY USER DATABASE

#### Detailed Steps:
**Process**: Query User Database  
**Input**: Username (string)  
**Output**: User record object or None

**Steps**:
1. **Sanitize Input**
   - Remove leading/trailing whitespace
   - Convert to lowercase
   - Escape special SQL characters

2. **Execute Database Query**
   ```python
   SELECT * FROM users_customuser 
   WHERE LOWER(username) = %username%
   LIMIT 1
   ```

3. **Fetch Result**
   - If found: Return user object with fields:
     - id, username, password_hash, email
     - staff_id, is_active, is_approved, is_staff, is_superuser
     - position, contact_number, profile_image
     - date_joined, last_login
   - If not found: Return None

4. **Handle Database Errors**
   - Catch connection errors
   - Log error details
   - Return None on error

---

### 1.1.3 VERIFY PASSWORD HASH

#### Detailed Steps:
**Process**: Verify Password Hash  
**Input**: Submitted password (plain text), Stored hash (string)  
**Output**: Boolean (True/False)

**Steps**:
1. **Load Hash Algorithm**
   - Django uses PBKDF2 by default
   - Format: `algorithm$iterations$salt$hash`
   - Example: `pbkdf2_sha256$260000$xyz$abc...`

2. **Extract Hash Components**
   - Split hash string by `$` delimiter
   - Extract: algorithm, iterations, salt

3. **Hash Submitted Password**
   - Apply same algorithm with same salt
   - Use same iteration count

4. **Compare Hashes**
   - Use constant-time comparison to prevent timing attacks
   - Return True if match, False otherwise

---

### 2.3.1 MAP HAZARD CODE TO RISK LEVEL

#### Detailed Steps:
**Process**: Map Hazard Code to Risk Level  
**Input**: Flood susceptibility code (VHF/HF/MF/LF)  
**Output**: Risk classification object

**Steps**:
1. **Define Risk Mapping Dictionary**
   ```python
   risk_data = {
       'LF': {
           'label': 'Low Susceptibility',
           'description': 'less than 0.5 meters flood height and/or less than 1 day flooding',
           'class': 'risk-low',
           'color': 'green'
       },
       'MF': {
           'label': 'Moderate Susceptibility',
           'description': '0.5 to 1 meter flood height and/or 1 to 3 days flooding',
           'class': 'risk-moderate',
           'color': 'yellow'
       },
       'HF': {
           'label': 'High Susceptibility',
           'description': '1 to 2 meters flood height and/or more than 3 days flooding',
           'class': 'risk-high',
           'color': 'orange'
       },
       'VHF': {
           'label': 'Very High Susceptibility',
           'description': 'more than 2 meters flood height and/or more than 3 days flooding',
           'class': 'risk-very-high',
           'color': 'red'
       }
   }
   ```

2. **Lookup Risk Data**
   - Use hazard code as dictionary key
   - Retrieve corresponding risk object

3. **Handle Unknown Codes**
   - If code not found: Return default risk object
   - Default: 'Unknown Risk Level', no class, no color

4. **Return Risk Classification**
   - Return complete risk object with all fields

---

### 4.3.4 APPLY AND-BASED RISK LOGIC

#### Detailed Steps:
**Process**: Apply AND-Based Risk Logic  
**Input**: 
- rainfall_mm (float)
- tide_m (float)
- thresholds object (rainfall_moderate, rainfall_high, tide_moderate, tide_high)

**Output**: Risk level string (High Risk / Moderate Risk / Low Risk)

**Steps**:
1. **Load Threshold Values**
   ```python
   rainfall_moderate = thresholds.rainfall_moderate_threshold  # 30mm
   rainfall_high = thresholds.rainfall_high_threshold          # 50mm
   tide_moderate = thresholds.tide_moderate_threshold          # 1.0m
   tide_high = thresholds.tide_high_threshold                  # 1.5m
   ```

2. **Check HIGH RISK Condition**
   ```python
   if (rainfall_mm >= rainfall_high) AND (tide_m >= tide_high):
       return "High Risk"
   ```
   - Example: rainfall=52mm AND tide=1.6m → High Risk
   - Counter-example: rainfall=52mm AND tide=1.2m → NOT High Risk

3. **Check MODERATE RISK Condition**
   ```python
   elif (rainfall_mm >= rainfall_moderate) AND (tide_m >= tide_moderate):
       return "Moderate Risk"
   ```
   - Example: rainfall=35mm AND tide=1.1m → Moderate Risk
   - Counter-example: rainfall=35mm AND tide=0.8m → NOT Moderate Risk

4. **Default to LOW RISK**
   ```python
   else:
       return "Low Risk"
   ```
   - If neither High nor Moderate conditions met

5. **Return Result**
   - Return risk level string

---

### 5.1.4 GENERATE STAFF ID

#### Detailed Steps:
**Process**: Generate Staff ID  
**Input**: Current year (integer)  
**Output**: Staff ID string (e.g., "20250001")

**Steps**:
1. **Get Current Year**
   ```python
   import datetime
   current_year = datetime.datetime.now().year  # e.g., 2025
   ```

2. **Query Database for Last Staff ID**
   ```python
   SELECT staff_id FROM users_customuser
   WHERE staff_id LIKE '2025%'
   ORDER BY staff_id DESC
   LIMIT 1
   ```

3. **Extract Sequential Number**
   - If last_user found:
     - Extract last 4 digits: `last_user.staff_id[-4:]`
     - Convert to integer: `int('0001')` → 1
     - Increment: `new_number = last_number + 1` → 2
   - If no users found for this year:
     - Set `new_number = 1`

4. **Format Staff ID**
   ```python
   staff_id = f"{current_year}{new_number:04d}"
   ```
   - Example: `f"{2025}{2:04d}"` → "20250002"
   - Zero-padded to 4 digits

5. **Return Staff ID**
   - Return formatted string

---

### 3.1.4 CONVERT HTML TO PDF

#### Detailed Steps:
**Process**: Convert HTML to PDF  
**Input**: Rendered HTML string  
**Output**: PDF binary file

**Steps**:
1. **Import PDF Library**
   ```python
   from xhtml2pdf import pisa
   ```

2. **Create PDF Buffer**
   ```python
   import io
   pdf_buffer = io.BytesIO()
   ```

3. **Convert HTML to PDF**
   ```python
   pisa_status = pisa.CreatePDF(
       src=html_content,
       dest=pdf_buffer,
       encoding='UTF-8'
   )
   ```

4. **Check Conversion Status**
   - If pisa_status.err:
     - Log error details
     - Raise conversion exception
   - Else:
     - Continue to next step

5. **Retrieve PDF Bytes**
   ```python
   pdf_buffer.seek(0)
   pdf_bytes = pdf_buffer.read()
   ```

6. **Return PDF File**
   - Return PDF binary data

---

### 4.2.4 CREATE RAINFALLDATA RECORD

#### Detailed Steps:
**Process**: Create RainfallData Record  
**Input**: 
- value_mm (float)
- timestamp (datetime)
- station_name (string)

**Output**: Database record ID (integer)

**Steps**:
1. **Validate Input Data**
   - Check value_mm >= 0
   - Check timestamp is valid datetime
   - Check station_name is not empty

2. **Create Model Instance**
   ```python
   rainfall_record = RainfallData(
       value_mm=value_mm,
       timestamp=timestamp,
       station_name=station_name
   )
   ```

3. **Save to Database**
   ```python
   rainfall_record.save()
   ```
   - Executes INSERT query
   - Auto-generates primary key

4. **Retrieve Record ID**
   ```python
   record_id = rainfall_record.id
   ```

5. **Log Success**
   ```python
   logger.info(f"Saved rainfall data: {value_mm}mm at {timestamp}")
   ```

6. **Return Record ID**
   - Return integer ID

---

### 7.2.1 VALIDATE THRESHOLD INPUTS

#### Detailed Steps:
**Process**: Validate Threshold Inputs  
**Input**: 
- rainfall_moderate (float)
- rainfall_high (float)
- tide_moderate (float)
- tide_high (float)

**Output**: Validated values or validation errors

**Steps**:
1. **Check Non-Negative Values**
   ```python
   if rainfall_moderate < 0:
       raise ValidationError("Rainfall moderate threshold must be >= 0")
   if rainfall_high < 0:
       raise ValidationError("Rainfall high threshold must be >= 0")
   if tide_moderate < 0:
       raise ValidationError("Tide moderate threshold must be >= 0")
   if tide_high < 0:
       raise ValidationError("Tide high threshold must be >= 0")
   ```

2. **Check Logical Order (Moderate < High)**
   ```python
   if rainfall_moderate >= rainfall_high:
       raise ValidationError("Rainfall moderate must be less than high")
   if tide_moderate >= tide_high:
       raise ValidationError("Tide moderate must be less than high")
   ```

3. **Check Reasonable Ranges**
   ```python
   if rainfall_moderate > 200:
       raise ValidationError("Rainfall moderate threshold seems too high")
   if tide_moderate > 5.0:
       raise ValidationError("Tide moderate threshold seems too high")
   ```

4. **Return Validated Values**
   - If all checks pass: Return input values
   - If any check fails: Raise validation error

---

## DATA DICTIONARY

### D1 - Users (CustomUser)
| Field | Type | Description |
|-------|------|-------------|
| id | Integer PK | Unique user identifier |
| username | String(150) | Login username |
| password | String(128) | Hashed password |
| email | EmailField | User email address |
| staff_id | String(10) | Auto-generated staff ID (e.g., 20250001) |
| first_name | String(150) | User's first name |
| last_name | String(150) | User's last name |
| is_active | Boolean | Account activation status |
| is_approved | Boolean | Admin approval status |
| is_staff | Boolean | Staff member flag |
| is_superuser | Boolean | Superuser flag |
| position | String(50) | Job position (choices) |
| custom_position | String(100) | Custom position title |
| contact_number | String(11) | Phone number |
| emergency_contact | String(100) | Emergency contact name |
| emergency_number | String(11) | Emergency contact phone |
| profile_image | ImageField | Profile photo |
| bio | Text(500) | User biography |
| date_of_birth | Date | Birthdate |
| date_joined | DateTime | Registration timestamp |
| last_login | DateTime | Last login timestamp |

### D2 - Barangays
| Field | Type | Description |
|-------|------|-------------|
| id | String(9) PK | PSGC barangay code |
| name | String(100) | Barangay name |
| parent_id | String(8) | Parent municipality code |
| geometry | MultiPolygon | Barangay boundary geometry |

### D3 - Flood Susceptibilities
| Field | Type | Description |
|-------|------|-------------|
| id | Integer PK | Record identifier |
| lgu | String(20) | LGU name (Silay City) |
| psgc_lgu | String(8) | PSGC LGU code |
| haz_class | String(20) | Hazard class (Flooding) |
| haz_code | String(3) | Hazard code (VHF/HF/MF/LF) |
| haz_desc | String(30) | Hazard description |
| haz_area_ha | Decimal(15,8) | Hazard area in hectares |
| geometry | MultiPolygon | Flood zone boundary |

### D4 - Assessment Records
| Field | Type | Description |
|-------|------|-------------|
| id | Integer PK | Record identifier |
| user_id | ForeignKey | User who performed assessment |
| barangay | String(100) | Barangay name |
| latitude | Decimal(10,6) | Assessment latitude |
| longitude | Decimal(10,6) | Assessment longitude |
| flood_risk_code | String(3) | Risk code (VHF/HF/MF/LF) |
| flood_risk_description | String(100) | Risk description |
| timestamp | DateTime | Assessment timestamp |
| is_archived | Boolean | Archive status |
| archived_at | DateTime | Archive timestamp |

### D11 - Benchmark Settings
| Field | Type | Description |
|-------|------|-------------|
| id | Integer PK | Settings ID (always 1) |
| rainfall_moderate_threshold | Float | Moderate risk rainfall (mm) |
| rainfall_high_threshold | Float | High risk rainfall (mm) |
| tide_moderate_threshold | Float | Moderate risk tide (m) |
| tide_high_threshold | Float | High risk tide (m) |
| combined_risk_method | String(20) | Risk calculation method |
| created_at | DateTime | Settings creation timestamp |
| updated_at | DateTime | Last update timestamp |
| updated_by | String(100) | Admin who last updated |

### D12 - User Activity Logs
| Field | Type | Description |
|-------|------|-------------|
| id | Integer PK | Log entry identifier |
| user_id | ForeignKey | User who performed action |
| action | String(100) | Action description |
| timestamp | DateTime | Action timestamp |
| is_archived | Boolean | Archive status |
| archived_at | DateTime | Archive timestamp |

### D13 - Login Attempts
| Field | Type | Description |
|-------|------|-------------|
| id | Integer PK | Attempt identifier |
| username | String(150) | Username attempted |
| ip_address | GenericIPAddress | Source IP address |
| timestamp | DateTime | Attempt timestamp |
| success | Boolean | Success/failure status |

---

## SUMMARY

This comprehensive DFD decomposition breaks down the Silay DRRMO Flood Monitoring System into 4 hierarchical levels:

- **Level 1**: 7 major processes (Authenticate, Assessment, Reports, Monitoring, User Management, Activity History, Benchmark Settings)
- **Level 2**: 29 sub-processes with detailed inputs/outputs
- **Level 3**: 60+ atomic processes with specific data transformations
- **Level 4**: Detailed step-by-step implementations for critical processes

Each level provides increasing granularity, from high-level system functions down to individual database queries and calculations, enabling complete understanding of data flows and process logic.
