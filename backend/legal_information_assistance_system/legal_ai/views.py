from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from .services.rag_pipeline import ask_question

def query_view(request):
    query = request.GET.get("q")
    response = ask_question(query)

    return JsonResponse({"answer": response})