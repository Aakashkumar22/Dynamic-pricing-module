from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class PricingConfig(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=False)
    waiting_charge = models.DecimalField(max_digits=5, decimal_places=2)
    waiting_time_threshold = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class DayBasedPricing(models.Model):
    DAY_CHOICES = [
        (0, 'Sunday'),
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
    ]

    config = models.ForeignKey(PricingConfig, on_delete=models.CASCADE, related_name='day_pricing')
    day = models.IntegerField(choices=DAY_CHOICES)
    base_distance = models.DecimalField(max_digits=5, decimal_places=2)
    base_price = models.DecimalField(max_digits=8, decimal_places=2)
    additional_price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        unique_together = ('config', 'day')

    def __str__(self):
        return f"{self.get_day_display()} pricing"


class TimeMultiplier(models.Model):
    config = models.ForeignKey(PricingConfig, on_delete=models.CASCADE, related_name='time_multipliers')
    duration_upper_bound = models.PositiveIntegerField(help_text="Duration in minutes")
    multiplier = models.DecimalField(max_digits=5, decimal_places=2)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']
        unique_together = ('config', 'duration_upper_bound')

    def __str__(self):
        return f"<{self.duration_upper_bound}min: {self.multiplier}x"


class PricingConfigLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
    ]

    config = models.ForeignKey(PricingConfig, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    changes = models.TextField()

    def __str__(self):
        return f"{self.get_action_display()} by {self.user} at {self.timestamp}"

