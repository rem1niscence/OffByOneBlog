from django import forms
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie


class ColorizedErrorFormMixin(forms.ModelForm):
    error_css_class = 'is-danger'

    def is_valid(self):
        valid = super(ColorizedErrorFormMixin, self).is_valid()
        self.add_error_css_class()
        return valid

    def add_error_css_class(self):
        for field in self.errors:
            self.fields[field].widget.attrs.update(
                {'class': self.fields[field].widget.attrs.get('class', '') +
                 f' {self.error_css_class}'})


class CacheVaryOnCookieMixin:
    """ Mixin caching a single page,

        Subclasses can provide these attribute:
        `timeout` - cache timeout for this
    """

    @classmethod
    def get_timeout(cls):
        if hasattr(cls, 'timeout'):
            return cls.timeout
        return settings.CACHE_TTL

    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super().as_view(*args, **kwargs)
        view = vary_on_cookie(view)
        view = cache_page(timeout=cls.get_timeout())(view)
        return view
