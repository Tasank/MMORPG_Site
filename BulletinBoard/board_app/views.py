from django.shortcuts import render

# Create your views here.
def site1(request):
    return render(request, 'Site1/index.html')