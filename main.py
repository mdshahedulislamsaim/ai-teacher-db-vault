# =====================================================================
# File: main.py
# Purpose: Manages student registration and mastery tracking in Supabase.
# =====================================================================

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables (secrets) from the .env file
load_dotenv()

# Extract database connection details from environment variables
# Note: Ensure SUPABASE_URL does not include '/rest/v1/'
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize the Supabase Client with our credentials
# This object 'supabase' is now our bridge to the PostgreSQL database
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def register_student(name: str, email: str, grade: int):
    """
    Registers a new student by inserting a record into the 'students' table.
    
    Logic:
    1. Prepare a dictionary (JSON) with student data.
    2. Execute the insert command on the 'students' table.
    3. Return the newly generated unique student ID for future reference.
    """
    response = supabase.table("students").insert({
        "name": name,
        "email": email,
        "grade_level": grade
    }).execute()
    
    # Access the first item in the returned data list
    student = response.data[0]
    print(f"✅ Student Registered: {student['name']} (ID: {student['id']})")
    
    # Return the ID so we can associate mastery logs with this specific student
    return student['id']

def initialize_student_mastery(student_id: str, topic_id: int):
    """
    Creates an initial mastery entry for a student in a specific topic.
    
    Logic:
    - We default the mastery_score to 10.0 (baseline).
    - We set the Bloom Level to 1 (the lowest level: 'Remember').
    """
    response = supabase.table("student_mastery").insert({
        "student_id": student_id,
        "topic_id": topic_id,
        "mastery_score": 10.0,
        "blooms_level": 1,
        "avg_latency_ms": 0,
        "total_attempts": 0
    }).execute()
    
    print(f"📊 Mastery initialized for Topic ID {topic_id}")

def get_student_profile(student_id: str):
    """
    Fetches the full profile for a student, including their linked mastery logs.
    
    Logic:
    1. Query the 'students' table to get the user's name and grade.
    2. Query 'student_mastery' and join it with 'topics' to get readable titles.
    """
    # Fetch user data
    student = supabase.table("students").select("*").eq("id", student_id).execute()
    
    # Fetch mastery data (joins automatically because we defined foreign keys in SQL)
    mastery = supabase.table("student_mastery").select("*, topics(title)").eq("student_id", student_id).execute()
    
    # Print the findings to the console
    print("\n--- 🎓 STUDENT PROFILE ---")
    print(f"Name: {student.data[0]['name']}")
    print(f"Grade: {student.data[0]['grade_level']}")
    print("Mastery Status:")
    
    # Loop through all mastery records linked to this student
    for record in mastery.data:
        topic_title = record['topics']['title']
        print(f"  - Topic: {topic_title} | Score: {record['mastery_score']}% | Bloom Level: {record['blooms_level']}")

# --- MAIN EXECUTION BLOCK ---
# This block runs only if this script is executed directly (e.g., via 'python main.py')
if __name__ == "__main__":
    
    # Generate a unique email address to avoid database conflicts during testing
    test_email = f"student_{os.urandom(3).hex()}@test.com"
    
    # STEP 1: Add the student to the database
    new_student_id = register_student("Rahim Ahmed", test_email, 10)
    
    # STEP 2: Assign the student to a default topic (Topic 1: Quadratic Equations)
    initialize_student_mastery(new_student_id, 1)
    
    # STEP 3: Display the saved profile
    get_student_profile(new_student_id)