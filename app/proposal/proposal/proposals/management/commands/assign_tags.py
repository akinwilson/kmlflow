from django.core.management.base import BaseCommand
from django.utils import timezone
from proposals.models import Proposals, Tags
import random

class Command(BaseCommand):
    help = 'Assigns 5 random tags to each Proposals object.'

    def handle(self, *args, **kwargs):
        # Fetch all tags from the database
        all_tags = list(Tags.objects.all())
        
        # Fetch all proposals
        proposals = Proposals.objects.all()

        # Assign 5 random tags to each proposal
        for proposal in proposals:
            # Randomly select 5 tags
            random_tags = random.sample(all_tags, 5)
            # Assign the tags to the proposal
            proposal.tags.set(random_tags)
            proposal.save()

        self.stdout.write(self.style.SUCCESS('Successfully assigned tags to all proposals.'))