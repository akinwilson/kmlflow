from django import forms
from .models import Proposals

class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposals
        fields = [
            'research_paper_link',
            'research_paper_title',
            'title',
            'description',
            'proposal_goal',
            'trial_runs',
            'requested_gpus',
        ]
        widgets = {
            'research_paper_link': forms.URLInput(attrs={'class': 'form-control'}),
            'research_paper_title': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'proposal_goal': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'trial_runs': forms.URLInput(attrs={'class': 'form-control'}),
            'requested_gpus': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_requested_gpus(self):
        requested_gpus = self.cleaned_data['requested_gpus']
        if requested_gpus < 1:
            raise forms.ValidationError("Requested GPUs must be a whole number greater than 1.")
        return requested_gpus

# class ProposalForm(forms.ModelForm):
#     class Meta:
#         model = Proposal
#         fields = [
#             'research_paper_link',
#             'research_paper_title',
#             'title',
#             'description',
#             'proposal_goal',
#             'trial_runs',
#             'requested_gpus',
#         ]
#         widgets = {
#             'description': forms.Textarea(attrs={'rows': 4}),
#             'proposal_goal': forms.Textarea(attrs={'rows': 4}),
#         }

#     def clean_requested_gpus(self):
#         requested_gpus = self.cleaned_data['requested_gpus']
#         if requested_gpus < 1:
#             raise forms.ValidationError("Requested GPUs must be a whole number greater than 1.")
#         return requested_gpus


