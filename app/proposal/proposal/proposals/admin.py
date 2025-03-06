from django.contrib import admin
from .models import Proposals,Category, Tags

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(Proposals)
class ProposalAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'expected_compute_time',
        'requested_gpus',
        'upvotes',
        'predicted_cost',
        'repo_link',
    ]
    list_filter = ['expected_compute_time', 'requested_gpus', 'upvotes']
    search_fields = ['title', 'description']
    list_per_page = 20
    
    def save_model(self, request, obj, form, change):
        # Ensure validation is called when saving in the admin
        obj.full_clean()
        super().save_model(request, obj, form, change)


