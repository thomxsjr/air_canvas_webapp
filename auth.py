import pyrebase

config = {
'apiKey': "AIzaSyDivnkmsK4dBJpSDI2Le_Nl6oL9vqJwmMY",
'authDomain': "aircanvasflaskapp.firebaseapp.com",
'projectId': "aircanvasflaskapp",
'storageBucket': "aircanvasflaskapp.appspot.com",
'messagingSenderId': "930383551956",
'appId': "1:930383551956:web:c79ea45ebd49f808ec8a41"
};

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

email = 'test@gmail.com'
password = '123456'

user = auth.create_user_with_email_and_password(email, password)