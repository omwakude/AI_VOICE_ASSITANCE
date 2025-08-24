from django.shortcuts import render

# Create your views here.
# chatbot/views.py
from django.shortcuts import render
from .intent_model import model_clf, execute_command

def index(request):
    response = ""
    if request.method == "POST":
        user_input = request.POST.get("user_input")
        intent = model_clf.predict([user_input])[0]
        result = execute_command(intent)
        response = f"Detected intent: {intent} | {result}"
    return render(request, "chatbot/index.html", {"response": response})
