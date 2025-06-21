
from django.contrib import admin
from django.forms import ModelForm, ValidationError
from .models import PricingConfig, DayBasedPricing, TimeMultiplier, PricingConfigLog


class TimeMultiplierForm(ModelForm):
    class Meta:
        model = TimeMultiplier
        fields = '__all__'

    def clean(self):
        # Validate tier ordering
        tiers = TimeMultiplier.objects.filter(
            config=self.cleaned_data['config']
        ).exclude(id=self.instance.id).order_by('order')

        if tiers.exists() and self.cleaned_data['order'] > tiers.last().order + 1:
            raise ValidationError("Tiers must be in continuous order")
        return super().clean()


class TimeMultiplierInline(admin.TabularInline):
    model = TimeMultiplier
    form = TimeMultiplierForm
    extra = 1
    min_num = 1


class DayBasedPricingInline(admin.TabularInline):
    model = DayBasedPricing
    extra = 7
    max_num = 7


class PricingConfigAdmin(admin.ModelAdmin):
    inlines = [DayBasedPricingInline, TimeMultiplierInline]
    list_display = ('name', 'is_active', 'created_at')
    actions = ['activate_config']

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, (DayBasedPricing, TimeMultiplier)):
                instance.save()
        formset.save_m2m()

    def save_model(self, request, obj, form, change):
        action = 'create' if not change else 'update'
        obj.save()

        # Log changes
        PricingConfigLog.objects.create(
            config=obj,
            user=request.user,
            action=action,
            changes=str(form.changed_data)
        )

    def activate_config(self, request, queryset):
        queryset.update(is_active=True)
        PricingConfig.objects.exclude(pk__in=queryset).update(is_active=False)

    activate_config.short_description = "Activate selected configs"


admin.site.register(PricingConfig, PricingConfigAdmin)
admin.site.register(PricingConfigLog)

