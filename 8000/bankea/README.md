
# Bankea App - Django


##### Activate it (Windows)
```
<path>/Script/activate
```


### Steps to run app

In the root directory of the project run:

```
pip install -r requirements.txt
python manage.py migrate
python manage.py provision
python manage.py populate
python manage.py runserver
```

Now you can defaultly access the `localhost:8000`

#### Users
You can use these credentials in order to login as customer:
```
name: julia
pass: mirror12
```
To login as admin, do the following: 
```
python manage.py createsuperuser
```
Follow the steps and then use that to login
