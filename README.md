# drone-flight-planner
A Django REST Framework (DRF) based web application for generating optimized drone flight paths using polygon coordinates. Users can create polygons via an API, customize image overlap percentages, and receive an XML file with waypoints. Features robust error handling and efficient flight path algorithms.

# Prerequisite:
    
    Python, Postman, and Git are installed into the system and Twilio account (This will be used as an OTP sending service).

    **Note:** Use Python> 3.9, In this project, we used 3.10

# Setup

   1. Clone the repository:

          git clone https://github.com/akashrajk54/DroneFlightPlanner.git
      
   3. Navigate to the project directory:

          cd DroneFlightPlanner

          git checkout development

   5. Create a virtual environment (optional but recommended):

           python -m venv venv

   6. To activate the virtual environment run the below command and choose as per your os:

      a). Windows:

          venv\Scripts\activate

      b). Linux/macOS:

          source venv/bin/activate

   8. Install dependencies:

          pip install -r requirements.txt

   9. Set up environment variables by creating a .env file then add the key values:

       Generate a New Django Secret Key:

           Into your terminal type "python" and hit enter it will open the python console then run the below code:

           from django.core.management.utils import get_random_secret_key

           print(get_random_secret_key())

       You can use the above-printed key as your secret key for the below variable.

       Then type "exit()" to exit the Python console.

       Create a database in Postgres and add its details (DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD) below.

       Go into your Twilio account, get the information (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER), and add the details below. If you are using a free Twilio account, make sure you use the same number to log in to DroneFlightPlanner using the sign-up/login API, as Twilio provides only one number that can receive OTPs during the free account period.

       ## Below key-value pairs add into the .env file. For database use PostgreSQL

           SECRET_KEY=''

           DATABASE_NAME=''

           DATABASE_USER=''

           DATABASE_PASSWORD=''

           DATABASE_HOST='localhost'

           DATABASE_PORT='5432'

           MAX_TIME_LIMIT_TO_VERIFY_OTP='3'

           TWILIO_ACCOUNT_SID=''

           TWILIO_AUTH_TOKEN=''

           TWILIO_PHONE_NUMBER=''

           Debug = True

       **Note:** There should be no spaces around the "=" sign in to .env file

   10. Create a folder with the name "logs" inside DroneFlightPlanner/

               mkdir logs

   12. Run migrations to create the database schema:
       
              python manage.py makemigrations accounts_engine
      
              python manage.py makemigrations waypoint_generator
      
              python manage.py migrate

   13. Create a superuser (admin) account:
       
       **Note:** Put a phone number with a country code like +91 for IN.

               python manage.py createsuperuser

   15. Run the development server:

              python manage.py runserver
      
       **Note:** By default, it will use **8000** port



# Functionality:
The backend provides comprehensive functionality for managing Flight path, including user authentication, waypoint generation. Each API endpoint is designed to fulfill specific requirements, ensuring that users can perform desired actions efficiently and effectively.

# Code Quality:
The backend codebase adheres to best practices for clean, maintainable, and well-documented code. It follows the Django framework conventions, utilizes descriptive variable and function names, and includes comments and docstrings to explain the purpose and usage of different components.
# User Experience:
The backend aims to deliver a smooth and intuitive user experience by offering a straightforward API interface with clear and consistent endpoint naming and request/response formats. Error messages are informative and user-friendly, guiding users on how to rectify issues or provide necessary input.

# Problem Solving:
The backend effectively handles potential issues such as API errors and load performance through robust error handling mechanisms and optimization techniques. Error responses are properly formatted with appropriate HTTP status codes and error messages, enabling clients to identify and address issues promptly.

