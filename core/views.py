from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse, HttpResponseBadRequest
import logging
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile, ChatMessage
from .services.gemini import call_gemini

logger = logging.getLogger(__name__)
import json


def index(request):
    """Simple index that redirects to chat if authenticated, otherwise shows landing."""
    if request.user.is_authenticated:
        return redirect('core:chat')
    return render(request, 'core/index.html', {})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('core:chat')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def profile(request):
    profile = request.user.userprofile
    messages = ChatMessage.objects.filter(user=request.user).order_by('-created_at')[:50]
    return render(request, 'core/profile.html', {'profile': profile, 'messages': messages})


@login_required
def chat_page(request):
    # Render the chat UI (React will handle dynamic messages)
    profile = request.user.userprofile
    return render(request, 'core/chat.html', {'profile': profile})


@login_required
@require_POST
def api_add_tokens(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        amount = int(data.get('amount', 0))
    except Exception:
        return HttpResponseBadRequest('Invalid payload')
    if amount <= 0:
        return JsonResponse({'ok': False, 'error': 'Amount must be positive'})
    profile = request.user.userprofile
    profile.add_tokens(amount)
    return JsonResponse({'ok': True, 'tokens': profile.tokens})


@login_required
def buy_tokens(request):
    """Simple mock purchase view to add tokens via POST form (no payment gateway)."""
    profile = request.user.userprofile
    if request.method == 'POST':
        try:
            amount = int(request.POST.get('amount', 0))
        except Exception:
            amount = 0
        if amount > 0:
            profile.add_tokens(amount)
            return redirect('core:profile')
    return render(request, 'core/buy.html', {'profile': profile})


@login_required
@require_POST
def api_chat(request):
    """Basic chat endpoint: consumes tokens and returns a simple bot reply.

    This is where Gemini integration will later be added.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        message = data.get('message', '').strip()
    except Exception:
        return HttpResponseBadRequest('Invalid payload')

    if not message:
        return JsonResponse({'ok': False, 'error': 'Empty message'})

    profile = request.user.userprofile
    # Simple cost model: 1 token per message
    if not profile.consume_token(1):
        return JsonResponse({'ok': False, 'error': 'Insufficient tokens', 'tokens': profile.tokens}, status=402)

    # Save user message
    ChatMessage.objects.create(user=request.user, role='user', content=message)

    # Try to call Gemini integration; fall back to simple bot if unavailable
    try:
        bot_response = call_gemini(message)
    except Exception as exc:
        # Log the error server-side (do not expose secrets to the client)
        logger.exception('Gemini call failed; falling back to simple bot')
        bot_response = simple_bot_response(message)

    # Save bot message
    ChatMessage.objects.create(user=request.user, role='bot', content=bot_response)

    return JsonResponse({'ok': True, 'reply': bot_response, 'tokens': profile.tokens})


@login_required
def api_messages(request):
    """Return recent messages for the authenticated user as JSON.

    Query params:
      - limit (int): how many messages to return (default 50)
    """
    try:
        limit = int(request.GET.get('limit', 50))
    except Exception:
        limit = 50
    qs = ChatMessage.objects.filter(user=request.user).order_by('-created_at')[:limit]
    # return in chronological order
    msgs = [
        {'role': m.role, 'content': m.content, 'created_at': m.created_at.isoformat()}
        for m in reversed(qs)
    ]
    return JsonResponse({'ok': True, 'messages': msgs})


def simple_bot_response(user_message: str) -> str:
    # Very basic echo + friendly text. Replace this with Gemini API integration later.
    return f"Echo: {user_message}"

