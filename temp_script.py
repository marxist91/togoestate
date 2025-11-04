from accounts.models import User
from saved_searches.models import SavedSearch

u = User.objects.filter(role='customer').first()
print('Customer user:', u)
if u:
    ss = SavedSearch.objects.filter(user=u)
    print('Saved searches for customer:', ss.count())
