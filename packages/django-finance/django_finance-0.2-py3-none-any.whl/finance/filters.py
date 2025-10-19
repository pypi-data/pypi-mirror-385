from django.db.models import Q
from searchkit.filters import SearchkitFilter as OriginalSearchkitFilter
from searchkit.models import Search


class SearchkitFilter(OriginalSearchkitFilter):
    """
    A searchkit filter that shows searches related to order accounts. If an the
    bankstatements are filtered by an order account, only those searches are
    shown that are related to that order account.
    """
    def lookups(self, request, model_admin):
        searches = Search.objects.filter(contenttype=self.searchkit_model).order_by('-created_date')
        order_account_id = request.GET.get('order_account__id__exact', None)
        if order_account_id:
            q = Q(searchtoaccount__order_account__id=order_account_id) | Q(searchtoaccount__isnull=True)
            searches = searches.filter(q)
        self.details = [None] + [obj.details for obj in searches]
        return [(str(obj.id), obj.name) for obj in searches]
