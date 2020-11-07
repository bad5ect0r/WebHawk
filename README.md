# WebHawk [DEV]

An asset monitoring web application. A fun project of mine just to polish up on my Python/Django skills.
**The project is not complete yet so don't expect it to work.**

## How to

Ensure you have a virtual Python environment first.

```
$ python3 -m venv venv
$ source venv/bin/activate
```

Then you need to install all the requirements.

```
$ pip3 install -r requirements.txt
```

Next, you need to create a .env file. To do this, you can copy the .env.example file. **Make sure to update your `SECRET_KEY`!**

Finally, you need to run migrations by doing

```
$ python3 manage.py migrate
```

You should also add a new superuser:

```
$ python3 manage.py createsuperuser
```

To run the app, you need to do

```
$ python3 manage.py runserver
```

Let me know if you have any issues.

