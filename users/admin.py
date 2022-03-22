from django.contrib import admin
from .models import *
# Register your models here.
class UserDetailAdmin(admin.ModelAdmin):
    list_display = ("user", "uuid", "loan_amount", "account_type" )
    search_fields = ("uuid",)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(UserDetailAdmin, self).get_search_results(request, queryset, search_term)
        try:
            queryset |= self.model.objects.filter(uuid=search_term)
        except:
            pass
        return queryset, use_distinct

class IndividualAdmin(admin.ModelAdmin):
    search_fields = ('user', )

admin.site.register(UserDetails, UserDetailAdmin)
admin.site.register(Individual)
admin.site.register(Business)
admin.site.register(Director)
admin.site.register(Guarantor)
admin.site.register(Employee)
admin.site.register(NextOfKin)
admin.site.register(IndividualDocuments)
admin.site.register(BusinessDocument)
