from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tokens = models.PositiveIntegerField(default=100)

    def consume_token(self, amount=1):
        if self.tokens >= amount:
            self.tokens -= amount
            self.save()
            return True
        return False

    def add_tokens(self, amount):
        self.tokens += amount
        self.save()

    def __str__(self):
        return f"{self.user.username} profile (tokens={self.tokens})"


class ChatMessage(models.Model):
    ROLE_CHOICES = (('user', 'User'), ('bot', 'Bot'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f"{self.user.username} {self.role}: {self.content[:50]}"
