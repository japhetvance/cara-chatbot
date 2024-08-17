import streamlit as st


st.set_page_config(layout='wide')

if "role" not in st.session_state:
    st.session_state.role = None

if "vote" not in st.session_state:
    st.session_state.vote = None
ROLES = ["Aviation Expert", "Aviation Enthusiast"]

@st.dialog("❗Key Reminder",width="large")
def vote(role):
    st.markdown("""While our app provides valuable information about aviation, it's important to understand that our dataset is specifically limited to the guidelines and regulations set forth by the Philippine Civil Aviation Regulation (PCAR) as of 08-17-2024. This means our coverage is restricted to the regulations within this jurisdiction and may not include broader or international aviation standards.
                <br><br>For comprehensive and up-to-date aviation regulations, please refer to our data sources listed here:""", unsafe_allow_html=True
               )
    col1, col2 = st.columns(2)
    col1.link_button("Civil Aviation Authority of the Philippines", "https://caap.gov.ph/", use_container_width = True)
    col2.link_button("Philippine Civil Aviation Regulation", "https://caap.gov.ph/civil-aviation-regulations/", use_container_width = True)
    
    agree = st.checkbox("I acknowledge that I understand the limitations of the model")
   
    if st.button("Try on CARA ChatBot ↗︎", type = "primary"):
        if agree:
            st.session_state.vote = {"role": role}
            st.rerun()
        else: 
            st.error("It is important to acknowledge the limitations of the model.")
            
def login():
    col1, col2, col3 = st.columns([1,3,1])
    
    col2.image('datas/cara.png')
    col1.image('datas/caragpt.png')

    col2.header("Hello, C.A.R.A!")
    content = """
    Welcome to C.A.R.A., your trusted aviation assistant designed to provide you with real-time insights and guidance on the regulations set by the Civil Aviation Authority of the Philippines. 
    AI at its core, C.A.R.A. ensures you have quick and easy access to essential aviation information whenever you need it. 
    Whether you're an aviation professional, student, or enthusiast, C.A.R.A. is here to support your journey with accurate and reliable answers, making your experience smoother and more informed.
    Discover a smarter way to navigate the skies with C.A.R.A. by your side.<br><br>

    """
    col2.markdown(content, unsafe_allow_html=True)

    col2.subheader("Begin Your Journey")
    col2.markdown("Choose your profile below to tailor your experience:")

    role = col2.radio("I am a ",ROLES, index = None, label_visibility = "collapsed",captions = ["Empowering you with comprehensive aviation knowledge, tools, and resources to excel in your career and stay informed on the latest regulations.", "Providing you with easy access to accurate aviation information, insights, and updates to fuel your passion for flying."] )
    # role = col2.selectbox("Choose your role", ROLES)
    if st.session_state.vote == None: 
        
        if col2.button("Next"):
            if role:
                vote(role)
            else:
                col2.error("Please Select Your Profile in order to proceed.")
    else:
        st.session_state.role = st.session_state.vote['role']

        st.rerun()
        
def logout():
    # st.session_state = None
    st.session_state.role = None
    st.session_state.vote = None
    st.rerun()
    
def contactus():
    col1, col2 = st.columns(2)
    col1.title('The team behind C.A.R.A.')
    col1.subheader("ABOUT US")
    contactinfo = """
    C.A.R.A. (Flying J's most advanced aviation assistant system) is your trusted digital companion in the aviation industry.
    We are committed to providing accurate, up-to-date information on Philippine Civil Aviation Regulations (PCAR) to aviation professionals, students, and enthusiasts alike.
    Our platform leverages advanced AI technology to deliver real-time insights and guidance, simplifying the complexities of aviation regulations and ensuring compliance and safety.
    At C.A.R.A., we believe in making aviation knowledge accessible and easy to understand, empowering you to excel in your aviation journey.
    Whether you’re navigating airworthiness standards or staying informed on personnel licensing requirements, C.A.R.A. is here to support you every step of the way.
    """
    col1.markdown(contactinfo, unsafe_allow_html=True)
    col1.subheader("MISSION")
    contactinfo = """
    To empower the aviation community by providing accurate, real-time information and guidance on Philippine Civil Aviation Regulations. 
    C.A.R.A. is dedicated to enhancing safety, compliance, and understanding within the industry, ensuring that every aviator, student, and enthusiast has the knowledge they need to navigate the skies with confidence.
    """
    col1.markdown(contactinfo, unsafe_allow_html=True)
    col1.subheader("VISION")
    contactinfo = """
    To be the leading digital assistant in aviation, setting the standard for accessibility and reliability in aviation information. C.A.R.A. envisions a future where every aviation professional and enthusiast is equipped with the tools and insights necessary to achieve excellence in their field, fostering a safer and more informed aviation community.
    """
    col1.markdown(contactinfo, unsafe_allow_html=True)
    
def medinfohubplus():
    st.markdown(f"<h1 style='text-align: center;'>Greetings from C.A.R.A, {role} 👨‍✈️</h1>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<h4 style='text-align: center;color: #75C2F6;'><b><i>C.A.R.A</b></i><i> is your ultimate resource for accessible, reliable, and comprehensive aviation information. Our platform is designed to enhance your understanding of aviation regulations, support industry compliance, and simplify complex guidelines. With real-time insights and guidance, C.A.R.A. ensures you stay informed and up-to-date with the latest aviation standards.</i></h4>", unsafe_allow_html=True)
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💬CARA ChatBot")
        st.markdown("***Empowering You with Reliable Aviation Information***")
        st.markdown("C.A.R.A. leverages advanced AI to deliver accurate and easy-to-understand aviation guidelines and regulations. Our goal is to make aviation information accessible to everyone, enhancing your understanding and supporting informed decision-making. By providing real-time insights tailored to your needs, C.A.R.A. ensures you stay updated with the latest industry standards. Trust C.A.R.A. to be your guide in navigating the complexities of aviation regulations with confidence.")
        

    with col2:
        st.subheader("✈️Philippine Civil Aviation Regulation")
        st.markdown("***Providing Comprehensive Guidelines and Regulations for Philippine Aviation***")
        st.markdown("The Civil Aviation Regulations (CAR) outline the regulatory requirements for aviation safety, including aircraft operations, airworthiness, and personnel licensing. These regulations are organized into various Parts, each addressing specific aspects of aviation safety and compliance. Each Part is designed to ensure that all operational, maintenance, and personnel standards are met, providing a comprehensive framework for safe and efficient aviation practices.")
        
    col3, col4 = st.columns(2)
    if col3.button('Try on CARA Chatbot ↗︎', type = "primary", use_container_width = True):
        st.switch_page("chatbot/cara.py")
    col4.link_button("Explore the data source here 🛪", "https://caap.gov.ph/civil-aviation-regulations/", use_container_width = True)

role = st.session_state.role

logout_page = st.Page(logout, title="End Session", icon=":material/logout:")
about_us = st.Page(contactus, title="About Us", icon="✉️")
medinfohubplus_info = st.Page(medinfohubplus, title="About Our Data App", icon="📱", default=(role == role))

chatbot = st.Page(
    "chatbot/cara.py",
    title="Chat with C.A.R.A",
    icon="💬",
)
about_us_pages = [medinfohubplus_info,about_us]
account_pages = [logout_page]
data_apps = [chatbot]

st.logo(
    "datas/everyday.png",
    icon_image= "datas/cara-logo.png",
)

page_dict = {}
if st.session_state.role in ["Aviation Expert", "Aviation Enthusiast", "Neither"]:
    page_dict["Application"] = data_apps
if st.session_state.role in ["Aviation Expert", "Aviation Enthusiast", "Neither"]:
    page_dict["The Team"] = about_us_pages

if len(page_dict) > 0:
    pg = st.navigation(page_dict | {"Session": data_apps})
else:
    pg = st.navigation([st.Page(login)]) #defaults to login page if no acceptable role is selected

pg.run()