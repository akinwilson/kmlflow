import json
from django.core.management.base import BaseCommand
from proposals.models import Category, Tags 
from pathlib import Path 



class Command(BaseCommand):
    help = 'Load categories and tags from a JSON fixture file into the database'

    def handle(self, *args, **kwargs):
        json_file_path = Path(__file__).parent.parent.parent / "fixtures/tags.json"

        # Load the JSON data
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        # Iterate over each category and its tags
        for category_name, tags in data.items():
            # Create or get the category
            category, created = Category.objects.get_or_create(name=category_name)
            self.stdout.write(self.style.SUCCESS(f'Category: {category.name}'))

            # Add tags to the category
            for tag_name in tags:
                tag, created = Tags.objects.get_or_create(name=tag_name, category=category)
                self.stdout.write(self.style.SUCCESS(f'Tag: {tag.name}'))

        self.stdout.write(self.style.SUCCESS('Data loaded successfully!'))