from django.db import models




class Proposals(models.Model):
    research_paper_link = models.URLField(verbose_name="Research Paper Link", blank=True, null=True)
    research_paper_title = models.CharField(max_length=200, verbose_name="Research Paper Title")
    title = models.CharField(max_length=200, verbose_name="Proposal Title")
    description = models.TextField(verbose_name="Proposal Description")
    proposal_goal = models.TextField(verbose_name="Proposal Goal")
    trial_runs = models.URLField(verbose_name="Trial Runs Link", blank=True, null=True)
    requested_gpus = models.PositiveIntegerField(verbose_name="Requested GPUs")
    upvotes = models.PositiveIntegerField(verbose_name="Upvotes", default=0)
    expected_compute_time = models.PositiveIntegerField(verbose_name="Expected Compute Time (hours)", blank=True, null=True)
    predicted_cost = models.PositiveIntegerField(verbose_name="Predicted Cost (W8S)", blank=True, null=True)
    repo_link = models.URLField(max_length=500)  # <--- Ensure this exists
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    tags = models.ManyToManyField('Tags', verbose_name="Tags", blank=True, related_name="proposals")
    def __str__(self):
        return self.title
    def clean(self):
        # Ensure exactly 5 tags are associated with a proposal
        if self.tags.count() != 5:
            raise ValidationError("A proposal must have exactly 5 tags.")
    class Meta:
        
        db_table = 'proposals'
        verbose_name_plural = "proposali"  # pseudo-Latin plural of proposals 
        ordering = ['-created_at']

class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name="Category Name")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'categories'
        verbose_name_plural = "Categories"


class Tags(models.Model):
    name = models.CharField(max_length=200, verbose_name="Tag Subject")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="tags")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'tags'
        verbose_name_plural = "Tags"