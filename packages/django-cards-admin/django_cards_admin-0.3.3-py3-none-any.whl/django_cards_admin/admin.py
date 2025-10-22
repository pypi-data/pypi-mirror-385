from django.contrib import admin
from django.contrib.admin.options import csrf_protect_m
from django.utils.translation import ugettext
from django.urls import reverse


class DjangoCardsAdminMixin(admin.ModelAdmin):
    result_cards_columns = 4 # how many columns
    max_result_cards_number = 10 # if the number of the results is more than max_cards_number, show list instead of cards
    result_card_body_height = 100 # card body height in px
    result_card_body_min_width = 200 # card body min-width in px
    result_card_title_template = "result-card-title.html" # card title template, smart select by app_label and model_name
    result_card_body_template = "result-card-body.html" # card body template, smart select by app_label and model_name
    result_card_footer_template = "result-card-footer.html" # card footer template, smart select by app_label and model_name

    class Media:
        css = {
            "all": [
                "admin/css/result-cards.css",
            ]
        }

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["result_list_show_in_cards_flag"] = True
        extra_context["title_template"] = ugettext("Select %s to view")
        extra_context["result_card_width_in_percent"] = 100.0 / self.result_cards_columns
        extra_context["result_card_body_min_width"] = self.result_card_body_min_width
        extra_context["result_card_modeladmin"] = self
        return super().changelist_view(request, extra_context)

    def result_card_link(self, item):
        url = reverse("admin:{}_{}_change".format(item._meta.app_label, item._meta.model_name), kwargs={"object_id": item.pk})
        return url
    
    def result_card_link_title(self, item):
        return ugettext("View")

    def result_card_link_target(self, item):
        return ""
