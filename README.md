# Bankea 


### Prerequisites

You need to have Python & a Python environment
##### Python Environment Activate it in Windows
```
<path>/Script/activate
```

### Steps to run the bankea app

pip install -r requirements.txt
python manage.py migrate
python manage.py provision
python manage.py populate
python manage.py runserver
```

Starting development server at http://127.0.0.1:8000/ or `localhost:8000`

#### Users
You can use these credentials in order to login as customer:
```
name: victoria
pass: Famous12345

not able to get loan
name: mark
pass: Famous12345

```
To login as admin, do the following: 
```
python manage.py createsuperuser
http://127.0.0.1:8000/admin

```
Follow the steps and then use that to login
```
http://127.0.0.1:8000/api/v1
```
