# django-cards-admin

Show cards in changelist instead of table for django admin site.

## Install

```shell
pip install django-cards-admin
```

## Settings

**pro/settings.py**

```python
INSTALLED_APPS = [
    ...
    "django_simple_tags",
    "django_cards_admin",
    ...
]
```

## Usage

**app/admin.py**

```python
from django.contrib import admin
from django_cards_admin.admin import DjangoCardsAdminMixin
from .models import Book

class BookAdmin(DjangoCardsAdminMixin, admin.ModelAdmin):
    result_cards_columns = 5
    max_cards_number = 5
    result_card_body_height = 200
    list_display = ["title", "author", "isbn"]

admin.site.register(Book, BookAdmin)
```

## Configurations

- result_cards_columns = 4 # how many columns
- max_result_cards_number = 10 # if the number of the results is more than max_cards_number, show list instead of cards
- result_card_body_height = 100 # card body height in px
- result_card_body_min_width = 200 # card body min-width in px
- result_card_title_template = "result-card-title.html" # card title template, smart select by app_label and model_name
- result_card_body_template = "result-card-body.html" # card body template, smart select by app_label and model_name
- result_card_footer_template = "result-card-footer.html" # card footer template, smart select by app_label and model_name

## Release

### v0.1.0 2020/02/23

- First release.

### v0.2.0 2020/03/19

- Fix result-cards width problem in filtered changelist.

### v0.3.0 2020/03/21

- Add item link and link title override mechanism. Requires django-simple-tags>=0.4.0.

### v0.3.1 2020/04/28

- Remove print() statements in admin.py.

### v0.3.2 2023/09/15

- Doc update.

### v0.3.3 2025/10/21

- Doc update.

