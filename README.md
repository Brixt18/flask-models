This library was made for use in Python Flask (frameworks) projects.

The main function is to provide a model for the databases created in SQLAlchemy and thus facilitate some implementations of it.

The models include a ready-made CRUD and some other functions.

# Install

Due that the project is not on PyPI, the install must be done by github
```bash
pip install "git+https://www.github.com/brixt18/flask-models"
```

# How to use
Here a little sample of how to use the models in Python 3

```python
from flask import Flask
from flask_models.models import Model
from flask_models.const import db, COLUMN, STRING


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./database.db"

class User(Model):
    name = COLUMN(STRING(100))

def create_app():
    db.init_app(app)

    return app

if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        db.create_all()
    
    app.run()
```
## Considerations
- `db` must be imported from `flask_models.const` and then initalized by `db.init_app(app)`
- `flask_models.const` contains commons types of data 
- - `STRING`, `TEXT`, `INTEGER`, `FLOAT`, `DATETIME`, `BOOLEAN`,
- - Recommended use:
    ```python
    from flask_models.models import Model
    from flask_models.const import * #or import the ones to use

    class MyModel(Model):
        my_data = COLUMN(STRING(100))
        my_number = COLUMN(INTEGER)
        my_bool = COLUMN(BOOLEAN)
        ... # etc
    ```
- [Flask SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/) must be installed
- [Flask Login](https://flask-login.readthedocs.io/en/latest/) must be installed if you wants to use `check_auth` param.

# The Models
The models already have a CRUD (by using the class `CRUD` in `flask_models.models`) that includes most of common cases and uses for the databases such as:

```python
# Retrieves a record from the class's model by its primary key (db.Column(..., primary_key=True))
user = MyModel.get_by_id(my_id, or_404=False)

# get all
users = MyModel.get_all() #-> list of objects [MyModel(), ...]
users = MyModel.get_all(basequery=True) #-> the BaseQuery object
users = MyModel.get_all(limit=30) #-> set the limit of the query

# save data
new_user = MyModel(**{
    "name": "new",
    "surname": "user"
})
new_user.save()

# save multiple data by using bulk
data = [MyModel(...), MyModel(...), MyModel(...), ...]
MyModel.bulk_save(data)

# update data
user = MyModel.get_by_token(my_token)
user.update({
    "name": "other name"
})

# delete
user = MyModel.get_by_token(my_token)
user.delete()

# The models have a password_checker too
user = MyModel.get_by_id(my_id)

if user.check_password(request.form["password"]):
    ...
```

- `or_404` returns a `abort(404)` flask object if the ID does not exists. Default is True. Not all queries has `or_404`, read the docs.
- `check_auth` is in `save()`, `update()` and `delete()` methods. Default is True. 
- - If you are building a MVC app, this checks that the one who is doing the request is the same user or is a logged user.
- - If you are building an API, you must set this to `False` always, or build your own auth checker.

The model `Model` already includes `id`, `token`, `created_at`, `updated_at` and `is_active`, so it is not necesary to define them in your models. They will inherit them from the Model, and its CRUD methods as well.