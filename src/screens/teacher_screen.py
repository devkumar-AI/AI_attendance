from unicodedata import name
from datetime import datetime
import numpy as np
import pandas as pd
import streamlit as st
from src.database.config import supabase
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.database.db import check_tecaher_exists, create_teacher, teacher_login, get_teacher_subjects
from src.components.dialog_create_subject import create_subject_dialog
from src.components.subject_card import subject_card
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photo_dialog
from src.pipelines.face_pipeline import predict_attendance
from src.components.dialog_attendance_results import attendance_result_dialog


def teacher_screen():

    style_background_dashboard()
    style_base_layout()


    if 'teacher_data' in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type == "login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()

def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    c1, c2 = st.columns(2, gap="xxlarge", vertical_alignment="center")
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""Welcome, {teacher_data['name']}""")
        if st.button("Logout", type="secondary",key="logoutbtn",shortcut="control+l"):
            st.session_state["is_logged_in"]=False
            del st.session_state.teacher_data
            st.rerun()

    st.space()
    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = "take_attendance"
    tab1, tab2, tab3 = st.columns(3)

    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == "take_attendance" else "tertiary"
        if st.button("Take Attendance", type=type1,width="stretch", icon=":material/ar_on_you:"):
            st.session_state.current_teacher_tab = "take_attendance"
            st.rerun()
    
    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == "manage_subjects" else "tertiary"
        if st.button("Manage Subjects", type=type2, width="stretch", icon=":material/book_ribbon:"):
            st.session_state.current_teacher_tab = "manage_subjects"
            st.rerun()
    
    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == "attendance_records" else "tertiary"
        if st.button("Attendance Records", type=type3, width="stretch", icon=":material/cards_stack:"):
            st.session_state.current_teacher_tab = "attendance_records"
            st.rerun()

    st.divider()

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    if st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    if st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()


    footer_dashboard()

def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data["teacher_id"]
    st.header("Take AI Attendence")

    if "attendance_image" not in st.session_state:
        st.session_state.attendance_image = []
    
    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.warning("You haven't created any subjects yet! Please create  one to begin !")
        return
    
    subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}

    col1, col2 = st.columns([3,1], vertical_alignment="bottom")

    with col1:
        selected_subjects_label = st.selectbox("Select Subject", options=list(subject_options.keys()))
    
    with col2:
        if st.button("Add Photos", type="primary", width="stretch", icon=":material/photo_prints:"):
            add_photo_dialog()

    selected_subjects_id = subject_options[selected_subjects_label]

    st.divider()

    if st.session_state.attendance_image:
        st.header("Added Photos")
        gallery_cols = st.columns(4)

        for idx, img in enumerate(st.session_state.attendance_image):
            with gallery_cols[idx % 4]:
                st.image(img, width="stretch", caption=f"Photo {idx+1}")
    has_photos = bool(st.session_state.attendance_image)   
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Clear all photos", width="stretch", type="tertiary", icon=":material/delete:", disabled=not has_photos):
            st.session_state.attendance_image = []
            st.rerun()
    
    with c2:
        has_photos = bool(st.session_state.attendance_image)
        if st.button("Run Face Analysis", width="stretch", type="secondary", icon=":material/analytics:", disabled=not has_photos):
            with st.spinner("Deep scanning classroom photos..."):
                all_detected_ids = {}

                for idx, img in enumerate(st.session_state.attendance_image):
                    img_np = np.array(img.convert("RGB"))

                    detected, _, _ = predict_attendance(img_np)

                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)
                            all_detected_ids.setdefault(student_id, []).append(f"Photo {idx+1}")
                
                enrolled_res = supabase.table("subject_students").select("*, students(*)").eq("subject_id", selected_subjects_id).execute()
                enrolled_students = enrolled_res.data

                if not enrolled_students:
                    st.warning("No student enrolled in this course")
                else:
                    results, attendance_to_log = [], []

                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                    for node in enrolled_students:
                        student = node["students"]
                        sources = all_detected_ids.get(int(student["student_id"]), [])
                        is_present =  len(sources) > 0

                        results.append({
                            "Name" : student['name'],
                            "ID" : student['student_id'],
                            "Source" : ", ".join(sources) if is_present else "-",
                            "Status" : "✅ Present" if is_present else "❌ Absent"
                        })

                        attendance_to_log.append({
                            "student_id" : student['student_id'],
                            "subject_id" : selected_subjects_id,
                            "timestamp" : current_timestamp,
                            "is_present" : bool(is_present)
                        })

                attendance_result_dialog(pd.DataFrame(results), attendance_to_log)

    with c3:
        if st.button("Use voice Attendance", type="primary", width="stretch", icon=":material/mic:"):
            voice_attendance_dialog(selected)



def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']
    col1, col2 = st.columns(2)
    with col1:
        st.header("Manage Subjects" ,width="stretch")
    
    with col2:
       if st.button('Create New Subject', width="stretch"):
           create_subject_dialog(teacher_id)

    # List all subjects
    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        for sub in subjects:
            stats = [
                ("🫂", "Students", sub["total_students"]),
                ("🕰️", "Classes", sub["total_classes"]),
            ]
            def share_btn(subject=sub):
                if st.button(f'Share Code: {sub["name"]}', key=f'share_{sub["subject_code"]}', icon=":material/share:"):
                    share_subject_dialog(sub["name"], sub["subject_code"])
            st.space()

            subject_card(
                name = sub["name"],
                code = sub["subject_code"],
                section = sub["section"],
                stats =  stats,
                footer_callback = share_btn
            )
    else:
        st.info("No Subject Found. Create one above")

def teacher_tab_attendance_records():
    st.header("Attendence Record")

def login_teacher(username, password):
    if not username or not password:
        return False
    
    teacher = teacher_login(username, password)
    if teacher:
        st.session_state.user_role = "teacher"
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    
    return False

def teacher_screen_login():
    c1, c2 = st.columns(2, gap="xxlarge", vertical_alignment="center")
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type="secondary",key="loginbackbtn",shortcut="control+b"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header("Login using password" , text_alignment="center")

    st.space()
    st.space()

    teacher_username = st.text_input("Enter username", placeholder="devkumar01", key="teacher_username")
    teacher_pass = st.text_input("Enter password", placeholder="Enter password", type="password", key="teacher_password")

    st.divider()

    btnc1, btnc2 = st.columns(2, gap="large", vertical_alignment="center")
    with btnc1:
        if st.button("Login",width="stretch", shortcut="enter" ,icon=":material/passkey:"):
            if login_teacher(teacher_username, teacher_pass):
                st.toast("Welcome back, " + st.session_state.teacher_data["name"] + "!", icon="👋")
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    with btnc2:
        if st.button("Register Instead", width="stretch", type="primary",icon=":material/app_registration:"):
            st.session_state.teacher_login_type = "register"
            st.rerun()


    footer_dashboard()

def register_teacher(teacher_username, teacher_pass, teacher_pass_confirm, teacher_name):
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "All fields are required"

    if check_tecaher_exists(teacher_username):
        return False, "Teacher with this username already exists"
    
    if teacher_pass != teacher_pass_confirm:
        return False, "Passwords do not match"
    
    try:
        create_teacher(teacher_username, teacher_pass, teacher_name)
        return True, "Teacher registered successfully"
    
    except Exception as e:
        return False, "Unexpected Error Occured !"


def teacher_screen_register():
    c1, c2 = st.columns(2, gap="xxlarge", vertical_alignment="center")
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type="secondary",key="loginbackbtn",shortcut="control+b"):
            st.session_state.teacher_login_type = "login"
            st.rerun()

    st.header("Register your teacher profile here!" , text_alignment="center")

    st.space()
    st.space()

    teacher_username = st.text_input("Enter username", placeholder="devkumar01", key="teacher_username")
    teacher_name = st.text_input("Enter full name", placeholder="Dev Kumar", key="teacher_name")
    teacher_pass = st.text_input("Enter password", placeholder="Enter password", type="password", key="teacher_password")
    teacher_pass_confirm = st.text_input("Confirm password", placeholder="Confirm password", type="password", key="teacher_password_confirm")

    st.divider()

    btnc1, btnc2 = st.columns(2, gap="large", vertical_alignment="center")
    with btnc1:
        if st.button("Register Now",width="stretch", key="teacherloginbtn",shortcut="enter" ,icon=":material/app_registration:"):
            success , message = register_teacher(teacher_username, teacher_pass, teacher_pass_confirm, teacher_name)
            if success:
                st.success(message)
                import time
                time.sleep(2)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)
            
    
    with btnc2:
        if st.button("login Instead", width="stretch", type="primary",icon=":material/passkey:"):
            st.session_state.teacher_login_type = "login"
            st.rerun()
    footer_dashboard()
