from django.shortcuts import render, redirect
from .forms import ProposalForm

def create_proposal(request):
    if request.method == 'POST':
        form = ProposalForm(request.POST)
        if form.is_valid():
            proposal = form.save(commit=False)
            # Calculate expected_compute_time and predicted_cost
            proposal.expected_compute_time = proposal.requested_gpus * 3  # Example calculation
            proposal.predicted_cost = proposal.requested_gpus * 100  # Example calculation
            proposal.save()
            return redirect('proposal_list')  # Redirect to a list of proposals
    else:
        form = ProposalForm()
    
    return render(request, 'proposal/proposal.html', {'form': form})