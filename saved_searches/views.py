from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
import json
from .models import SavedSearch, SearchHistory


@login_required
@require_POST
def save_search(request):
    try:
        data = json.loads(request.body)
        query = data.get('query', '')
        name = data.get('name', '')

        if not query:
            return JsonResponse({'error': 'Query is required'}, status=400)

        saved_search, created = SavedSearch.objects.get_or_create(
            user=request.user,
            query=query,
            defaults={'name': name}
        )

        if not created:
            saved_search.name = name
            saved_search.save()

        return JsonResponse({
            'status': 'saved',
            'message': 'Recherche sauvegardée',
            'id': saved_search.id
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@login_required
def saved_searches_list(request):
    searches = SavedSearch.objects.filter(user=request.user)
    return JsonResponse({
        'searches': [
            {
                'id': search.id,
                'name': search.name,
                'query': search.query,
                'created_at': search.created_at.isoformat(),
                'updated_at': search.updated_at.isoformat()
            }
            for search in searches
        ]
    })


@login_required
@require_POST
def delete_saved_search(request, search_id):
    try:
        search = SavedSearch.objects.get(id=search_id, user=request.user)
        search.delete()
        return JsonResponse({'status': 'deleted', 'message': 'Recherche supprimée'})
    except SavedSearch.DoesNotExist:
        return JsonResponse({'error': 'Recherche non trouvée'}, status=404)


@login_required
def search_history(request):
    history = SearchHistory.objects.filter(user=request.user)[:20]  # Last 20 searches
    return JsonResponse({
        'history': [
            {
                'id': item.id,
                'query': item.query,
                'results_count': item.results_count,
                'searched_at': item.searched_at.isoformat()
            }
            for item in history
        ]
    })


@login_required
@require_POST
def record_search(request):
    try:
        data = json.loads(request.body)
        query = data.get('query', '')
        results_count = data.get('results_count', 0)

        if query:
            SearchHistory.objects.create(
                user=request.user,
                query=query,
                results_count=results_count
            )

        return JsonResponse({'status': 'recorded'})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
